"""Effect components: donor (MKT) effect animations as native MKMSZ effect actors.

Host model (stock Ice helper ``0x80060A3C``, Wiki ``Player-Actions-and-Special-Moves``):
an effect is its own class-``0x100`` process that

1. takes a dynamic texture slot ``0x8001C2B4(w, h)`` (slots ``0x200..0x2FF``; a freed
   slot with enough capacity is reused, otherwise storage is taken top-down from
   ``0x800BF2FC`` above the texture bump ``0x801AE478``; ``-1`` when full),
2. binds a palette record ``0x8001C528(record, 0x100, 0)`` (cached by source address),
3. constructs an actor ``0x800281A0(script, 0, file base, 1)`` (zeroed object from the
   free list ``0x802D0E34``; controller ``+0x6E0``),
4. inserts it in the movement/render list ``0x80111C98`` (``0x80024650``), advances its
   frame script through ``0x800304C0`` with a fixed sleep per frame until the script
   word is ``0``, then removes it (``0x80024B00``), sleeps 2 ticks, releases the
   slot (``0x8001C424``) and exits (``0x80028564``).

The stock helper additionally builds a mirror actor (the blue Sub-Zero "ghost"); the
component does not. Frame pixels reach the slot through the render pass's deferred
decode/upload (``0x800185B8``: ``+0xFA`` -> ``0x8000322C`` -> ``0x8001D6EC``), so a frame
image may be raw (type 0) or compressed (type 4, decoded into the per-frame scratch).

Spawning (:func:`emit_spawn`) copies the source actor's position, rotation and layer
into the new process's controller (``+0x6F4..+0x70C``, written after ``0x8002830C``
returns, so nothing is read from the source later) and refuses when fewer than the
descriptor's reserve of free processes (``0x80111DC8``) or free objects
(``0x802D0E34``) remain: stock spawners do not check either pool.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..resource_materialization import decode_type4
from .host import CURRENT_CTRL, F_OFFSET, F_SLEEP, hi, lo
from .mips import Assembler
from .projectile import F_ACTOR_INSERT, F_PALETTE_BIND, mkt_color_to_host

F_SLOT_ACQUIRE = 0x8001C2B4  # (w, h) -> dynamic texture slot or -1
F_SLOT_RELEASE = 0x8001C424  # (slot)
F_ACTOR_CONSTRUCT = 0x800281A0  # (script word ptr, 0, file base, flags) -> actor
F_ACTOR_REMOVE = 0x80024B00  # (actor, list)
F_ANIM_ADVANCE = 0x800304C0  # (actor): next frame-script word
F_PROCESS_CREATE = 0x8002830C  # (id, entry) -> controller or 0
F_PROCESS_EXIT = 0x80028564
ACTOR_LIST = 0x80111C98
PROCESS_FREE_LIST = 0x80111DC8
OBJECT_FREE_LIST = 0x802D0E34
FILE87_BASE_PTR = 0x80291C10
EFFECT_PROCESS_ID = 0x100  # as the stock Ice helper
FRONT_SUBLAYER = 0xFFFF  # stock helper value: drawn in front of its layer

# Controller fields of an effect process (copied from the spawner by 0x8002830C, then
# overwritten by emit_spawn before the process first runs).
FX_X, FX_Y, FX_Z = 0x6F4, 0x6F8, 0x6FC
FX_DESCRIPTOR = 0x700
FX_ROT_AC_AE = 0x704  # rotation +0xAC (high) / +0xAE (low)
FX_ROT_B0_LAYER = 0x708  # rotation +0xB0 (high) / priority +0x5C (low)
FX_SUBLAYER_DX = 0x70C  # sub-layer +0xEC (high) / local x offset, whole units (low, signed)


# ---- donor (MKT USA Rev. 2) images ------------------------------------------------------
def decode_mkt_codec15(stream: bytes) -> bytes:
    """MKT codec 15 (3-bit indices, RLE)."""

    size = int.from_bytes(stream[:4], "big") & 0xFFFFFF
    pos, out = 4, bytearray()
    while len(out) < size:
        ch = stream[pos]
        pos += 1
        if ch & 0x80:
            out += bytes((ch & 0x7F) + 1)
        elif ch & 0x40:
            out.append((ch >> 3) & 7)
            if len(out) < size:
                out.append(ch & 7)
        elif ch & 7 == 0:
            out += bytes(((ch >> 3) & 7,)) * stream[pos]
            pos += 1
        else:
            out += bytes((ch & 7,)) * (((ch >> 3) & 7) + 3)
    if len(out) != size:
        raise ValueError("codec-15 size mismatch")
    return bytes(out)


def decode_mkt_codec14_19(stream: bytes, dictionary: bytes) -> bytes:
    """MKT codecs 14/19 (decoder ``0x80082594``): 5-bit runs plus dictionary pairs.

    Codec 19 carries a fill index at ``+4`` (codec 14: fill 0). A byte with bit 7 set is
    dictionary pair ``(c & 0x7F) * 2``; otherwise ``k = c >> 5``, ``v = c & 0x1F``: 0 one
    ``v``, 1 two ``v``, 2 ``v + 3`` fills, 3 ``v`` repeated by the next byte.
    """

    size = int.from_bytes(stream[:4], "big") & 0xFFFFFF
    codec = stream[0] & 0x3F
    if codec not in (14, 19):
        raise ValueError(f"not a codec-14/19 image ({codec})")
    fill, pos = (stream[4], 5) if codec == 19 else (0, 4)
    out = bytearray()
    while len(out) < size:
        c = stream[pos]
        pos += 1
        if c & 0x80:
            i = (c & 0x7F) * 2
            out += dictionary[i : i + 2]
            continue
        k, v = c >> 5, c & 0x1F
        if k == 0:
            out.append(v)
        elif k == 1:
            out += bytes((v, v))
        elif k == 2:
            out += bytes((fill,)) * (v + 3)
        else:
            out += bytes((v,)) * stream[pos]
            pos += 1
    return bytes(out[:size])


@dataclass(frozen=True)
class EffectFrame:
    width: int
    height: int
    anchor_x: int
    anchor_y: int
    indices: bytes  # height * stride, one palette index per byte

    @property
    def stride(self) -> int:
        return (self.width + 3) & ~3


def pad_to_stride(frame: EffectFrame) -> EffectFrame:
    """Widen a frame to its 4-aligned row stride (transparent columns on the right,
    same anchor). The pixels already carry the stride, so only the width changes."""

    return EffectFrame(frame.stride, frame.height, frame.anchor_x, frame.anchor_y, frame.indices)


def _mkt_u32(mkt: bytes, va: int) -> int:
    return int.from_bytes(mkt[va - 0x80000000 : va - 0x80000000 + 4], "big")


def _mkt_s16(mkt: bytes, va: int) -> int:
    return int.from_bytes(mkt[va - 0x80000000 : va - 0x80000000 + 2], "big", signed=True)


def mkt_frame(mkt: bytes, descriptor: int, dictionary: bytes) -> EffectFrame:
    """MKT image descriptor ``{image, h << 16 | w, anchor x, anchor y}`` -> host indices."""

    from .projectile import decode_mkt_codec16

    image = _mkt_u32(mkt, descriptor)
    dims = _mkt_u32(mkt, descriptor + 4)
    width, height = dims & 0xFFFF, dims >> 16
    stream = mkt[image - 0x80000000 :]
    codec = stream[0] & 0x3F
    if codec == 16:
        indices = decode_mkt_codec16(stream)[0]
    elif codec == 15:
        indices = decode_mkt_codec15(stream)
    elif codec in (14, 19):
        indices = decode_mkt_codec14_19(stream, dictionary)
    else:
        raise ValueError(f"unsupported MKT effect codec {codec}")
    frame = EffectFrame(
        width, height, _mkt_s16(mkt, descriptor + 8), _mkt_s16(mkt, descriptor + 10), indices
    )
    if len(indices) != height * frame.stride:
        raise ValueError(f"MKT image {image:#x}: {len(indices)} indices for {width}x{height}")
    return frame


def mkt_palette(mkt: bytes, va: int) -> tuple[int, ...]:
    count = _mkt_u32(mkt, va)
    base = va - 0x80000000 + 4
    return tuple(
        mkt_color_to_host(int.from_bytes(mkt[base + 2 * i : base + 2 * i + 2], "big"))
        for i in range(count)
    )


# ---- host type-4 images ------------------------------------------------------------------
def encode_type4(raw: bytes) -> bytes:
    """Self-contained MKMSZ type-4 (``0x80003428``) block with back-references.

    The decoder's 1024-byte ring (``0x802E7E20``) is not cleared between images and
    output byte ``k`` lands at ring index ``(1 + k) & 0x3FF``. References therefore only
    reach bytes of this image (distance <= 1024) and never use ring index 0 (the end
    token), so the result does not depend on earlier images. Counts are 2..65.
    """

    n = len(raw)
    controls: list[int] = []
    tokens = bytearray()
    chains: dict[bytes, list[int]] = {}
    i = 0
    while i < n:
        best_len, best_src = 0, 0
        if i + 2 <= n:
            for s in reversed(chains.get(raw[i : i + 2], ())):
                if i - s > 1024:
                    break
                if (1 + s) & 0x3FF == 0:
                    continue
                length = 0
                while length < 65 and i + length < n and raw[s + length] == raw[i + length]:
                    length += 1
                if length > best_len:
                    best_len, best_src = length, s
                    if length == 65:
                        break
        step = best_len if best_len >= 3 else 1
        if step == 1:
            controls.append(1)
            tokens.append(raw[i])
        else:
            index = (1 + best_src) & 0x3FF
            controls.append(0)
            tokens += bytes((index >> 2, ((index & 3) << 6) | (best_len - 2)))
        for k in range(i, i + step):
            if k + 2 <= n:
                chains.setdefault(raw[k : k + 2], []).append(k)
        i += step
    controls.append(0)
    tokens += b"\0\0"  # end token: ring index 0
    control_bytes = bytearray((len(controls) + 7) // 8)
    for k, bit in enumerate(controls):
        if bit:
            control_bytes[k // 8] |= 0x80 >> (k % 8)
    size = 8 + len(control_bytes) + len(tokens)
    if size > 0xFFFFFF:
        raise ValueError("type-4 image exceeds the 24-bit size field")
    block = (
        bytes((size & 0xFF, (size >> 8) & 0xFF, size >> 16, 4))
        + (4 + len(control_bytes)).to_bytes(4, "little")
        + bytes(control_bytes)
        + bytes(tokens)
    )
    if decode_type4(block) != raw:
        raise AssertionError("type-4 round trip failed")
    return block


# ---- an effect in the fighter file -------------------------------------------------------
@dataclass(frozen=True)
class EffectArt:
    frames: tuple[EffectFrame, ...]
    palette: tuple[int, ...]  # host colours, up to 64
    compressed: bool = False  # type-4 images (decoded per frame) instead of raw type 0

    @property
    def slot_size(self) -> tuple[int, int]:
        return max(f.width for f in self.frames), max(f.height for f in self.frames)

    def image(self, frame: EffectFrame) -> bytes:
        return encode_type4(frame.indices) if self.compressed else b"\0\0\0\0" + frame.indices

    def palette_record(self) -> bytes:
        if len(self.palette) > 64:
            raise ValueError("palette record holds at most 64 colours")
        colours = list(self.palette) + [0] * (64 - len(self.palette))
        return (64).to_bytes(4, "big") + b"".join(c.to_bytes(2, "big") for c in colours)


@dataclass(frozen=True)
class EffectLayout:
    data: bytes  # placed at file offset ``offset``
    offset: int
    palette: int  # file offset of the palette record
    script: int  # file offset of the frame script (shape offsets, then 0)

    @property
    def end(self) -> int:
        return self.offset + len(self.data)


def layout(art: EffectArt, offset: int) -> EffectLayout:
    """Palette record, then per frame an image, a descriptor and a one-part shape, then
    the script; every record 4-aligned (fighter-file shapes must be)."""

    if offset & 3:
        raise ValueError("effect data must start 4-aligned")
    out = bytearray()

    def put(blob: bytes) -> int:
        at = offset + len(out)
        out.extend(blob)
        out.extend(bytes(-len(out) & 3))
        return at

    palette = put(art.palette_record())
    shapes = []
    for frame in art.frames:
        image = put(art.image(frame))
        desc = put(
            image.to_bytes(4, "big")
            + ((frame.width << 16) | frame.height).to_bytes(4, "big")
            + (((frame.anchor_x & 0xFFFF) << 16) | (frame.anchor_y & 0xFFFF)).to_bytes(4, "big")
        )
        shapes.append(put(desc.to_bytes(4, "big") + bytes(4)))
    script = put(b"".join(s.to_bytes(4, "big") for s in shapes) + bytes(4))
    return EffectLayout(bytes(out), offset, palette, script)


# ---- payload code -----------------------------------------------------------------------
def emit_descriptor(
    a: Assembler,
    label: str,
    placed: EffectLayout,
    art: EffectArt,
    ticks_per_frame: int,
    reserve: int,
) -> None:
    """``{script, palette, slot w << 16 | h, ticks per frame, pool reserve}``."""

    if a.pc() & 3:
        raise ValueError("effect descriptor must be word aligned")
    w, h = art.slot_size
    a.label(label)
    for word in (placed.script, placed.palette, (w << 16) | h, ticks_per_frame, reserve):
        a.raw(word)


def _emit_free_at_least(a: Assembler, head: int, count: str, fail: str, tag: str) -> None:
    """Branch to ``fail`` unless the free list at ``head`` has ``count`` (>= 1) nodes."""

    a.lui("t1", hi(head))
    a.lw("t1", lo(head), "t1")
    a.move("t2", count)
    a.label(tag)
    a.beqz("t1", fail)
    a.addiu("t2", "t2", -1)
    a.blez("t2", tag + "_ok")
    a.lw("t1", 0, "t1")
    a.beq("zero", "zero", tag)
    a.label(tag + "_ok")


def emit_spawn(a: Assembler, label: str = "fx_spawn", process: str = "fx_process") -> None:
    """``fx_spawn(a0 = source actor, a1 = descriptor, a2 = local dx, a3 = sub-layer)``.

    Starts an effect process at the source actor's position (offset by ``a2`` whole
    units along the source's local x), rotation and priority, drawn at sub-layer ``a3``.
    Does nothing when a pool is short or no process is available.
    """

    a.label(label)
    a.addiu("sp", "sp", -0x28)
    a.sw("ra", 0x24, "sp")
    a.sw("s0", 0x20, "sp")
    a.sw("s1", 0x1C, "sp")
    a.sw("s2", 0x18, "sp")
    a.sw("s3", 0x14, "sp")
    a.move("s0", "a0")
    a.move("s1", "a1")
    a.move("s2", "a2")
    a.move("s3", "a3")
    a.lw("t0", 0x10, "s1")
    _emit_free_at_least(a, PROCESS_FREE_LIST, "t0", label + "_done", label + "_proc")
    _emit_free_at_least(a, OBJECT_FREE_LIST, "t0", label + "_done", label + "_obj")
    a.li("a0", EFFECT_PROCESS_ID)
    a.la("a1", process)
    a.jal(F_PROCESS_CREATE)
    a.beqz("v0", label + "_done")
    for src, dst in ((0x2C, FX_X), (0x30, FX_Y), (0x34, FX_Z)):
        a.lw("t0", src, "s0")
        a.sw("t0", dst, "v0")
    a.sw("s1", FX_DESCRIPTOR, "v0")
    for high, low, dst in ((0xAC, 0xAE, FX_ROT_AC_AE), (0xB0, 0x5C, FX_ROT_B0_LAYER)):
        a.lhu("t0", high, "s0")
        a.sll("t0", "t0", 16)
        a.lhu("t1", low, "s0")
        a.addu("t0", "t0", "t1")
        a.sw("t0", dst, "v0")
    a.sll("t0", "s3", 16)
    a.andi("t1", "s2", 0xFFFF)
    a.addu("t0", "t0", "t1")
    a.sw("t0", FX_SUBLAYER_DX, "v0")
    a.label(label + "_done")
    a.lw("ra", 0x24, "sp")
    a.lw("s0", 0x20, "sp")
    a.lw("s1", 0x1C, "sp")
    a.lw("s2", 0x18, "sp")
    a.lw("s3", 0x14, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x28)


def emit_process(a: Assembler, label: str = "fx_process") -> None:
    """The effect process entry (never returns). ``s0`` slot, ``s1`` controller,
    ``s2`` actor, ``s3`` file base, ``s4`` descriptor."""

    a.label(label)
    a.addiu("sp", "sp", -0x20)
    a.lui("s1", hi(CURRENT_CTRL))
    a.lw("s1", lo(CURRENT_CTRL), "s1")
    a.lui("s3", hi(FILE87_BASE_PTR))
    a.lw("s3", lo(FILE87_BASE_PTR), "s3")
    a.lw("s4", FX_DESCRIPTOR, "s1")
    a.lhu("a0", 8, "s4")
    a.lhu("a1", 0xA, "s4")
    a.jal(F_SLOT_ACQUIRE)
    a.bltz("v0", label + "_exit")
    a.move("s0", "v0")
    a.lw("a0", 4, "s4")
    a.addu("a0", "a0", "s3")
    a.li("a1", 0x100)
    a.move("a2", "zero")
    a.jal(F_PALETTE_BIND)
    a.bltz("v0", label + "_release")
    a.addiu("s5", "v0", -0x80)
    a.lw("a0", 0, "s4")
    a.addu("a0", "a0", "s3")
    a.move("a1", "zero")
    a.move("a2", "s3")
    a.li("a3", 1)
    a.jal(F_ACTOR_CONSTRUCT)
    a.beqz("v0", label + "_release")
    a.move("s2", "v0")
    a.sh("s0", 0x9C, "s2")
    a.sh("s5", 0x9E, "s2")
    for src, dst in ((FX_X, 0x2C), (FX_Y, 0x30), (FX_Z, 0x34)):
        a.lw("t0", src, "s1")
        a.sw("t0", dst, "s2")
    for src, high, low in ((FX_ROT_AC_AE, 0xAC, 0xAE), (FX_ROT_B0_LAYER, 0xB0, 0x5C)):
        a.lw("t0", src, "s1")
        a.sh("t0", low, "s2")
        a.sra("t0", "t0", 16)
        a.sh("t0", high, "s2")
    a.lw("t0", FX_SUBLAYER_DX, "s1")
    a.sra("t0", "t0", 16)
    a.sh("t0", 0xEC, "s2")
    a.li("t0", 0x2002)  # as the stock helper
    a.sw("t0", 0x64, "s2")
    a.li("t0", 0x6C)
    a.sw("t0", 0xD8, "s2")
    a.li("t0", 0xE000)
    a.sw("t0", 0x6B4, "s1")
    a.lh("a1", FX_SUBLAYER_DX + 2, "s1")
    a.beqz("a1", label + "_placed")
    a.move("a0", "s2")
    a.move("a2", "zero")
    a.jal(F_OFFSET)  # facing bit clear here: a1 is along the copied rotation's +x
    a.label(label + "_placed")
    a.li("t0", 0x40)  # bind requests a texture decode (+0xFA)
    a.sh("t0", 0x8C, "s2")
    a.lw("t0", 0, "s4")
    a.addu("t0", "t0", "s3")
    a.sw("t0", 0x6E4, "s1")
    a.move("a0", "s2")
    a.lui("a1", hi(ACTOR_LIST))
    a.addiu("a1", "a1", lo(ACTOR_LIST))
    a.jal(F_ACTOR_INSERT)
    a.label(label + "_frame")
    a.move("a0", "s2")
    a.jal(F_ANIM_ADVANCE)
    a.lw("a0", 0xC, "s4")
    a.jal(F_SLEEP)
    a.lui("t0", hi(CURRENT_CTRL))
    a.lw("t0", lo(CURRENT_CTRL), "t0")
    a.lw("t0", 0x6E4, "t0")
    a.lw("t0", 0, "t0")
    a.bnez("t0", label + "_frame")
    a.move("a0", "s2")
    a.lui("a1", hi(ACTOR_LIST))
    a.addiu("a1", "a1", lo(ACTOR_LIST))
    a.jal(F_ACTOR_REMOVE)
    a.li("a0", 2)
    a.jal(F_SLEEP)
    a.label(label + "_release")
    a.move("a0", "s0")
    a.jal(F_SLOT_RELEASE)
    a.label(label + "_exit")
    a.jal(F_PROCESS_EXIT)
    a.beq("zero", "zero", label + "_exit")
