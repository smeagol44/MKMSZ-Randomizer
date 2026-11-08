"""Projectile components: donor projectile art/palette and the host projectile seams.

MKMSZ creates a projectile actor from an animation token (``0x0B``, handler
``0x80030974``): it constructs the actor from the fighter file, binds the fixed Ice
palette record ``0x800B1A24`` through ``0x8001C528`` and publishes the actor with
``0x80024650``. Imported projectiles keep that native construction and add two
narrowly scoped hooks, Runtime-confirmed in Sektor missile proofs v87/v89:

* palette: when the token is the imported projectile's, bind the donor palette record
  instead of the Ice palette;
* pre-publication texture: load the projectile's raw image into its finalized texture
  slot (``0x8001BF70``) and refresh the frame (``0x8001BDA0``) before publication, so
  the first visible frame is not the slot's previous contents (v88 failure).

Both hooks fall through to the stock calls for any other token-``0x0B`` actor.
Hook context (stock handler): ``a3`` current controller, ``s0`` new actor, ``s2``
parent actor; ``+0x6E4`` already points past the token at the palette call.
"""

from __future__ import annotations

from dataclasses import dataclass

from .mips import Assembler

F_PALETTE_BIND = 0x8001C528
F_TEXTURE_SLOT_LOAD = 0x8001BF70  # synchronous: installs slot metadata, queues and drains
F_FRAME_SETUP = 0x8001BDA0
F_ACTOR_INSERT = 0x80024650
ACTOR_LIST_HEAD = 0x80111C98
TOKEN_0B_RETURN = 0x80030AD0  # stock return point after the insert call

TOKEN_PALETTE_CALL_ROM = 0x000315C8  # jal 0x8001C528 (delay: sw v0, 0x6E4(a3))
TOKEN_INSERT_CALL_ROM = 0x000316C8  # jal 0x80024650 (delay: sh v0, 0xAE(a0))
STOCK_PALETTE_JAL = 0x0C00714A
STOCK_INSERT_JAL = 0x0C009194


def decode_mkt_codec16(stream: bytes) -> tuple[bytes, int]:
    """MKT codec 16 (4-bit indices, RLE): returns (one index per byte, bytes consumed)."""

    if stream[0] != 16:
        raise ValueError("not a codec-16 image")
    size = int.from_bytes(stream[:4], "big") & 0x00FFFFFF
    pos = 4
    out = bytearray()
    while len(out) < size:
        ch = stream[pos]
        pos += 1
        if ch & 0x80:
            out += bytes((ch & 0x7F) + 7)
            continue
        high, pixel = ch >> 4, ch & 0x0F
        if high == 0:
            out += bytes((pixel,)) * stream[pos]
            pos += 1
        elif high <= 6:
            out += bytes((pixel,)) * high
        else:
            count = pixel + 3
            while count:
                byte = stream[pos]
                pos += 1
                out.append(byte >> 4)
                count -= 1
                if count:
                    out.append(byte & 0x0F)
                    count -= 1
    if len(out) != size:
        raise ValueError("codec-16 size mismatch")
    return bytes(out), pos


def mkt_color_to_host(value: int) -> int:
    """MKT RGBA5551 -> MKMSZ BGR555 with the opaque bit (transparent -> 0)."""

    if not value & 1:
        return 0
    r, g, b = (value >> 11) & 31, (value >> 6) & 31, (value >> 1) & 31
    return 0x8000 | (b << 10) | (g << 5) | r


@dataclass(frozen=True)
class ProjectileArt:
    """Raw (type-0) projectile image and its dedicated 64-entry palette record."""

    width: int
    height: int
    anchor_x: int
    anchor_y: int
    indices: bytes  # height * align4(width), one palette index per byte
    palette: tuple[int, ...]  # host colours, up to 64

    @property
    def stride(self) -> int:
        return (self.width + 3) & ~3

    def raw_image(self) -> bytes:
        return b"\0\0\0\0" + self.indices  # native raw/type-0 wrapper

    def palette_record(self) -> bytes:
        colours = list(self.palette) + [0] * (64 - len(self.palette))
        return (64).to_bytes(4, "big") + b"".join(c.to_bytes(2, "big") for c in colours)


def emit_palette_hook(a: Assembler, label: str, cursor_offset: int, palette_offset: int) -> None:
    """Token palette call: donor palette when the cursor is just past the projectile token.

    ``cursor_offset`` is the fighter-file offset the cursor holds after the token;
    ``palette_offset`` is the file offset passed instead of the Ice record.
    """

    a.label(label)
    a.lw("t0", 0x6E4, "a3")
    a.addiu("t0", "t0", -cursor_offset)
    a.lw("t1", 0x98, "s0")
    a.bne("t0", "t1", label + "_stock")
    a.lui("at", (palette_offset >> 16) & 0xFFFF)
    a.ori("at", "at", palette_offset & 0xFFFF)
    a.addu("a0", "t1", "at")
    a.label(label + "_stock")
    a.j(F_PALETTE_BIND)


def emit_preupload_hook(a: Assembler, label: str, shape_offset: int, art: ProjectileArt) -> None:
    """Token insert call: for the imported projectile only, load its texture slot first."""

    a.label(label)
    a.lw("t0", 0x98, "s0")
    a.li("t1", shape_offset)
    a.addu("t0", "t0", "t1")
    a.lw("t2", 0x74, "s0")
    a.bne("t0", "t2", label + "_publish")
    a.lw("t1", 0x7C, "s0")  # render record
    a.lw("a0", 0, "t1")  # raw/type-0 wrapper pointer
    a.addiu("a0", "a0", 4)
    a.li("a1", art.stride)
    a.li("a2", art.height)
    a.lhu("a3", 0x9C, "s0")  # finalized texture slot
    a.jal(F_TEXTURE_SLOT_LOAD)
    a.move("a0", "s0")
    a.lw("a1", 0x74, "s0")
    a.jal(F_FRAME_SETUP)
    a.label(label + "_publish")
    a.move("a0", "s0")
    a.lui("a1", (ACTOR_LIST_HEAD + 0x8000) >> 16)
    a.addiu("a1", "a1", (ACTOR_LIST_HEAD & 0xFFFF) - (0x10000 if ACTOR_LIST_HEAD & 0x8000 else 0))
    a.lui("ra", TOKEN_0B_RETURN >> 16)
    a.ori("ra", "ra", TOKEN_0B_RETURN & 0xFFFF)
    a.j(F_ACTOR_INSERT)
