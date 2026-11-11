"""Generic body builder (Fighter recompiler plan, milestone 1).

Builds an imported fighter's body into the host fighter file 0x87 from a fighter description
(``description.py``): donor frames, the 16-colour reduction, the shared Type-5 entropy table,
the frame packer, the translated body scripts (host slot *i* takes MKT table 0 index *i*),
Run and Push, the fallback for every other stock frame reference, and an independent decode
check of every emitted frame.

Fighter-specific choices come from the description. Frozen legacy (plan rule 4) plugs in
through :class:`Extras`: frames a fighter's moves need (named frame sets with their entropy
groups) and script edits applied before the fallback. Ported from ``sektor_build.py`` (Sektor
build v61) and checked byte for byte against it (``tests/test_fighter_swap.py``).
"""

from __future__ import annotations

import bisect
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache

from .description import FighterDescription
from .mkt_fighter import MktRom
from .script import MKMSZ, MKT

MKT_FLIPPED = 0x47  # MKT table-0 slot whose first phase is the fighter's flip poses
# Per-fighter palette record pointers (count, RGBA5551 words), indexed by MKT fighter id. It
# matches the palette every fighter with its own art binds in its first frame; fighters that
# share art (the ninjas, the robots) get their costume recolour in the shared layout (Reptile
# 0x800BE864, green). 0x800A1738 is not indexed by fighter id past 16 (entries 17+ are the
# alternates of fighters 0+); reading it gave Reptile another fighter's palette (body proofs
# v01-v02, owner: "as if the palette was mapped wrongly").
MKT_PALETTE_TABLE = 0x800A3660

# Host fighter file 0x87 (MKMSZ USA Rev. 0): Static-confirmed layout.
FILE87_ROM = 0x748920
FILE87_SIZE = 0x459E0
TYPE_START = 0x14AC
TYPE_END = 0x41684
PALETTE_OFF = 0x4584C
FILE_TABLE_87 = 0xA5664  # file 0x87's (start, end) entry in the file table
SCRIPT_REF_START = 0x1B0
SAFE_END = 0x4E544  # v49 budget: the largest file the runtime-confirmed placement allowed
RUN_RATE_ROM = 0x2F7A0  # ordinary Run setup: addiu a0, zero, 2
RUN_RATE_STOCK = 0x24040002
PUSH_TARGET, RUN_TARGET = 0x1B0, 0xEE8
ZERO_BLOCK = b"\0" * 8
MODEL_COUNT_MAX = 64


def be16(b, o):
    return int.from_bytes(b[o : o + 2], "big")


def be32(b, o):
    return int.from_bytes(b[o : o + 4], "big")


def put32(b, o, v):
    b[o : o + 4] = int(v & 0xFFFFFFFF).to_bytes(4, "big")


def s16(v):
    return v - 0x10000 if v & 0x8000 else v


def s32(v):
    return v - 0x100000000 if v & 0x80000000 else v


def align4(v):
    return (v + 3) & ~3


def align2(v):
    return (v + 1) & ~1


class BitReader:
    def __init__(self, data):
        self.data = data
        self.bit = 0

    def read(self, n):
        v = 0
        for _ in range(n):
            byte = self.data[self.bit >> 3]
            sh = 7 - (self.bit & 7)
            self.bit += 1
            v = (v << 1) | ((byte >> sh) & 1)
        return v


class BitWriter:
    def __init__(self):
        self.out = bytearray()
        self.cur = 0
        self.n = 0
        self.bits = 0

    def write(self, v, n):
        assert n >= 0 and (n == 0 or 0 <= v < (1 << n))
        self.bits += n
        for sh in range(n - 1, -1, -1):
            self.cur = (self.cur << 1) | ((v >> sh) & 1)
            self.n += 1
            if self.n == 8:
                self.out.append(self.cur)
                self.cur = 0
                self.n = 0

    def finish(self):
        if self.n:
            self.out.append(self.cur << (8 - self.n))
            self.cur = 0
            self.n = 0
        return bytes(self.out)


# -- donor image codecs (MKT image dispatcher 0x80081C4C) --------------------------------------


def dec_15(src):
    n = int.from_bytes(src[:4], "big") & 0xFFFFFF
    p = 4
    out = bytearray()
    while len(out) < n:
        ch = src[p]
        p += 1
        if ch & 0x80:
            out += bytes((0,)) * ((ch & 0x7F) + 1)
        elif ch & 0x40:
            out.append((ch >> 3) & 7)
            if len(out) < n:
                out.append(ch & 7)
        else:
            pix = ch & 7
            if pix == 0:
                pix = (ch >> 3) & 7
                cnt = src[p]
                p += 1
                out += bytes((pix,)) * cnt
            else:
                cnt = ((ch >> 3) & 7) + 3
                out += bytes((pix,)) * cnt
    assert len(out) == n
    return bytes(out)


def dec_22_24(src, dictb):
    typ = src[0]
    n = int.from_bytes(src[:4], "big") & 0xFFFFFF
    if typ == 24:
        top = src[4:8]
        fp = 8
        mini = None
    elif typ == 23:
        top = None
        mini = src[4]
        fp = 5
    elif typ == 22:
        top = None
        mini = 0
        fp = 4
    else:
        raise ValueError(typ)
    flip_len = src[fp]
    fp += 1
    if flip_len & 0x80:
        flip_len = ((flip_len & 0x7F) << 8) | src[fp]
        fp += 1
    flip_data = src[fp:]
    sp = fp + flip_len
    bit_count = 8
    fi = 0
    flip = flip_data[fi] if flip_data else 0
    fi += 1 if flip_data else 0
    out = bytearray()
    while len(out) < n:
        ch = src[sp]
        sp += 1
        if ch & 0x80:
            idx = (ch & 0x7F) << 1
            if flip & 0x80:
                out.extend((dictb[idx + 1], dictb[idx]))
            else:
                out.extend((dictb[idx], dictb[idx + 1]))
            bit_count -= 1
            if bit_count == 0:
                flip = flip_data[fi]
                fi += 1
                bit_count = 8
            else:
                flip = (flip << 1) & 0xFF
        else:
            sw = ch >> 5
            ch &= 0x1F
            if sw == 3:
                cnt = src[sp]
                sp += 1
                out += bytes((ch,)) * cnt
            elif sw == 2:
                if top is None:
                    cnt = ch + 3
                    pix = mini
                else:
                    cnt = (ch & 7) + 3
                    pix = top[(ch >> 3) & 3]
                out += bytes((pix,)) * cnt
            elif sw == 1:
                out.append(ch)
                out.append(ch)
            else:
                out.append(ch)
    assert len(out) == n
    return bytes(out)


def make_blocks(padded, stride, eh):
    assert stride % 4 == 0 and eh % 2 == 0
    out = []
    for by in range(0, eh, 2):
        for bx in range(0, stride, 4):
            out.append(
                padded[by * stride + bx : by * stride + bx + 4]
                + padded[(by + 1) * stride + bx : (by + 1) * stride + bx + 4]
            )
    return out


def visible_rows(fr):
    return [fr["padded"][y * fr["stride"] : y * fr["stride"] + fr["w"]] for y in range(fr["h"])]


def composite(body, part, remap=None, codec="flattened"):
    """Flatten a multi-part donor frame: nonzero ``part`` pixels (optionally remapped) over ``body``,
    both placed by their actor-relative anchors."""

    bx0, by0 = -body["x"], -body["y"]
    ax0, ay0 = -part["x"], -part["y"]
    minx = min(bx0, ax0)
    miny = min(by0, ay0)
    maxx = max(bx0 + body["w"], ax0 + part["w"])
    maxy = max(by0 + body["h"], ay0 + part["h"])
    w = maxx - minx
    h = maxy - miny
    stride = align4(w)
    eh = align2(h)
    out = bytearray(stride * eh)

    def blit(fr, x0, y0, rm=None):
        ox = x0 - minx
        oy = y0 - miny
        for yy, row in enumerate(visible_rows(fr)):
            dst = (oy + yy) * stride + ox
            for xx, p in enumerate(row):
                if p:
                    out[dst + xx] = rm[p] if rm is not None else p

    blit(body, bx0, by0)
    blit(part, ax0, ay0, remap)
    raw = bytes(out)
    return {"w": w, "h": h, "x": -minx, "y": -miny, "stride": stride, "eh": eh, "padded": raw,
                "blocks": make_blocks(raw, stride, eh), "codec": codec}  # fmt: skip


class Donor:
    """One MKT fighter's heap: script words and decoded frames (heap-relative offsets)."""

    def __init__(self, mkt: bytes, fighter_id: int) -> None:
        reader = MktRom(mkt)
        self.mkt = mkt
        self.fighter_id = fighter_id
        self.base = reader.heap(fighter_id)[0]
        start, end = reader.dictionary(fighter_id)
        self.dictionary = mkt[start:end]
        self.table0 = reader.table0(fighter_id)

    def m32(self, rel):
        return be32(self.mkt, self.base + rel)

    def is_shape(self, rel):
        """A single-part frame record: ``[rel + 8, 0]`` then its descriptor."""

        return (isinstance(rel, int) and rel > 0 and self.base + rel + 8 <= len(self.mkt)
                and self.m32(rel) == rel + 8 and self.m32(rel + 4) == 0)  # fmt: skip

    def parts(self, rel):
        """Descriptor offsets of a frame record (zero-terminated pointer list), or None."""

        if not (isinstance(rel, int) and 0 < rel and self.base + rel + 8 <= len(self.mkt)):
            return None
        out, p = [], rel
        while len(out) < 8:
            d = self.m32(p)
            if d == 0:
                break
            if not (0 < d < len(self.mkt) - self.base and d % 4 == 0):
                return None
            out.append(d)
            p += 4
        return out if 0 < len(out) < 8 else None

    def is_frame(self, rel):
        parts = self.parts(rel)
        if not parts:
            return False
        try:
            self.frame(rel)
        except (ValueError, AssertionError, IndexError):
            return False
        return True

    def descriptor_frame(self, sub, rel):
        image_rel = be32(self.mkt, self.base + sub)
        packed = be32(self.mkt, self.base + sub + 4)
        anchor = be32(self.mkt, self.base + sub + 8)
        h = (packed >> 16) & 0xFFFF
        w = packed & 0xFFFF
        x = s16((anchor >> 16) & 0xFFFF)
        y = s16(anchor & 0xFFFF)
        src = self.mkt[self.base + image_rel :]
        typ = src[0]
        stride = align4(w)
        eh = align2(h)
        if typ == 15:
            raw = dec_15(src)
        elif typ in (22, 23, 24):
            raw = dec_22_24(src, self.dictionary)
        elif typ == 16:
            from .projectile import decode_mkt_codec16

            raw = decode_mkt_codec16(src)[0]
        else:
            raise ValueError((hex(rel), typ, hex(image_rel)))
        # Some images store the even (padded) height: stride * align2(h) bytes.
        if len(raw) == eh * stride and eh > h:
            raw = raw[: h * stride]
        assert len(raw) == h * stride, (hex(rel), typ, w, h, len(raw))
        if eh > h:
            raw += bytes(stride * (eh - h))
        return {"w": w, "h": h, "x": x, "y": y, "stride": stride, "eh": eh, "padded": raw,
                "blocks": make_blocks(raw, stride, eh), "codec": typ, "donor": rel}  # fmt: skip

    def frame(self, rel):
        """Decode frame record ``rel``; a multi-part record is flattened onto its first part."""

        if self.is_shape(rel):
            return self.descriptor_frame(rel + 8, rel)
        parts = self.parts(rel)
        if not parts:
            raise ValueError(f"0x{rel:X} is not a frame record")
        out = self.descriptor_frame(parts[0], rel)
        for sub in parts[1:]:
            out = composite(out, self.descriptor_frame(sub, rel), codec="flattened")
        out["donor"] = rel
        return out

    def palette(self):
        """The fighter's MKT palette as RGBA5551 words (index 0 transparent)."""

        va = be32(self.mkt, MKT_PALETTE_TABLE - 0x80000000 + 4 * self.fighter_id)
        o = va - 0x80000000
        n = be32(self.mkt, o)
        if not 0 < n <= 256:
            raise ValueError(f"bad palette record at 0x{va:08X}")
        return [be16(self.mkt, o + 4 + 2 * i) for i in range(n)]

    def phase(self, slot):
        """Frames of the first phase of MKT table 0 ``slot``."""

        root, out = self.table0[slot], []
        while self.m32(root + 4 * len(out)):
            out.append(self.m32(root + 4 * len(out)))
        return out

    def frames(self, slot):
        """Frame words of MKT table 0 ``slot``'s script, tokens skipped, up to its jump or end."""

        p, out = self.table0[slot], []
        while True:
            v = self.m32(p)
            if v == 0 or v == 1:
                return out
            if MKT.is_token(v):
                p += 4 * (1 + len(MKT.operands[v]))
                continue
            out.append(v)
            p += 4

    def script(self, rel, n):
        return [self.m32(rel + 4 * i) for i in range(n)]


# -- Type-5 encoder -------------------------------------------------------------------------------

ZERO_BITS, ZERO_BASES = (2, 2, 3), (0, 4, 8)


def split_even(seq, n):
    total = len(seq)
    return [seq[(i * total) // n : ((i + 1) * total) // n] for i in range(n) if (i * total) // n < ((i + 1) * total) // n]


@dataclass
class Encoded:
    streams: dict
    frame_model: dict
    table: bytes
    patterns: int
    stream_bytes: int


def encode(frame_cache: dict, groups: list[list], order: list[int]) -> Encoded:
    """Shared-dictionary Type-5 encoding: one 13-class model per group over one pattern array
    sorted by the group frequencies in ``order``."""

    freqs = []
    for g in groups:
        c = Counter()
        for k in g:
            c.update(p for p in frame_cache[k]["blocks"] if p != ZERO_BLOCK)
        freqs.append(c)
    all_patterns = set().union(*(set(c) for c in freqs))
    patterns = sorted(all_patterns, key=lambda p: tuple(-freqs[i].get(p, 0) for i in order) + (p,))
    pidx = {p: i for i, p in enumerate(patterns)}

    def best_partition(mf, classes=13):
        used = sorted((pidx[p], w, p) for p, w in mf.items())
        idx = [x[0] for x in used]
        wt = [x[1] for x in used]
        pref = [0]
        for w in wt:
            pref.append(pref[-1] + w)
        n = len(used)

        @lru_cache(None)
        def dp(pos, k):
            if pos >= n:
                return (0, ())
            if k == 0:
                return (10**30, None)
            base = idx[pos]
            best = (10**30, None)
            for bits in range(1, 17):  # native decoder safety: never emit a 0-bit normal class
                q = bisect.bisect_left(idx, base + (1 << bits), pos, n)
                if q == pos:
                    continue
                rc, rp = dp(q, k - 1)
                cost = bits * (pref[q] - pref[pos]) + rc
                if rp is not None and cost < best[0]:
                    best = (cost, ((base, bits, pos, q),) + rp)
            return best

        _cost, plan = dp(0, classes)
        assert plan is not None
        if len(plan) < classes:
            base = plan[-1][0] if plan else 0
            plan = plan + tuple((base, 1, n, n) for _ in range(classes - len(plan)))
        cmap = {}
        for ci, (base, bits, a, q) in enumerate(plan):
            for j in range(a, q):
                ix, _w, p = used[j]
                cmap[p] = (ci, ix - base, bits)
        assert len(cmap) == len(mf) and len(plan) == 13 and all(x[1] >= 1 for x in plan)
        return plan, cmap

    model_plans, model_maps = [], []
    for mf in freqs:
        pl, cm = best_partition(mf)
        model_plans.append(pl)
        model_maps.append(cm)

    @lru_cache(None)
    def zero_plan(n):
        if n == 0:
            return (0, ())
        best = (10**9, None)
        for zi, (bits, base) in enumerate(zip(ZERO_BITS, ZERO_BASES, strict=True)):
            for extra in range(1 << bits):
                cnt = base + extra + 1
                if cnt <= n:
                    pc, pp = zero_plan(n - cnt)
                    cost = pc + 4 + bits
                    if cost < best[0]:
                        best = (cost, pp + ((13 + zi, extra, bits, cnt),))
        return best

    streams, frame_model = {}, {}
    for mid, g in enumerate(groups):
        cm = model_maps[mid]
        for k in g:
            bl = frame_cache[k]["blocks"]
            bw = BitWriter()
            bw.write(mid, 6)
            i = 0
            while i < len(bl):
                if bl[i] == ZERO_BLOCK:
                    j = i + 1
                    while j < len(bl) and bl[j] == ZERO_BLOCK:
                        j += 1
                    _, zp = zero_plan(j - i)
                    for sym, extra, bits, _ in zp:
                        bw.write(sym, 4)
                        bw.write(extra, bits)
                    i = j
                else:
                    ci, extra, bits = cm[bl[i]]
                    bw.write(ci, 4)
                    bw.write(extra, bits)
                    i += 1
            stream = bw.finish()
            while len(stream) & 3:
                stream += b"\0"
            streams[k] = stream
            frame_model[k] = mid

    def pack_pattern(block):
        bw = BitWriter()
        for px in block:
            assert 0 <= px < 16
            bw.write(px, 4)
        out = bw.finish()
        assert len(out) == 4
        return out

    table = bytearray((2).to_bytes(2, "big") + len(groups).to_bytes(2, "big"))
    for pl in model_plans:
        rec = bytearray(104)
        rec[0:4] = (0).to_bytes(4, "big")
        rec[4:6] = (4).to_bytes(2, "big")
        for i, (_base, bits, _a, _q) in enumerate(pl):
            rec[6 + i * 2 : 8 + i * 2] = bits.to_bytes(2, "big")
        for i, bits in enumerate(ZERO_BITS):
            rec[32 + i * 2 : 34 + i * 2] = bits.to_bytes(2, "big")
        for i, (base, _bits, _a, _q) in enumerate(pl):
            rec[40 + i * 4 : 44 + i * 4] = base.to_bytes(4, "big")
        for i, base in enumerate(ZERO_BASES):
            rec[92 + i * 4 : 96 + i * 4] = base.to_bytes(4, "big")
        table += rec
    for p in patterns:
        table += pack_pattern(p)
    return Encoded(streams, frame_model, bytes(table), len(patterns), sum(map(len, streams.values())))


def decode_type5(file87, shape_off, models):
    """Independent decoder for an emitted Type-5 frame: (pixels, model, width, height)."""

    assert be32(file87, shape_off) == shape_off + 8 and be32(file87, shape_off + 4) == 0
    sub = shape_off + 8
    image = be32(file87, sub)
    assert bytes(file87[image : image + 4]) == b"\x05\0\0\0"
    table_off = image + s32(be32(file87, image + 4))
    assert table_off == TYPE_START
    dims = be32(file87, image + 8)
    height = (dims >> 16) & 0xFFFF
    width = dims & 0xFFFF
    rows = be16(file87, table_off)
    mc = be16(file87, table_off + 2)
    assert rows == 2 and mc == models
    pbase = table_off + 4 + 104 * mc
    br = BitReader(bytes(file87[image + 12 :]))
    mid = br.read(6)
    assert mid < mc
    mo = table_off + 4 + 104 * mid
    prel = be32(file87, mo)
    bpp = be16(file87, mo + 4)
    assert bpp == 4 and prel == 0
    nbits = [be16(file87, mo + 6 + i * 2) for i in range(13)]
    zbits = [be16(file87, mo + 32 + i * 2) for i in range(3)]
    bases = [be32(file87, mo + 40 + i * 4) for i in range(13)]
    zbases = [be32(file87, mo + 92 + i * 4) for i in range(3)]
    out = bytearray(width * height)
    bw = width // 4
    total = bw * (height // rows)
    bi = 0
    while bi < total:
        code = br.read(4)
        if code < 13:
            pi = bases[code] + br.read(nbits[code])
            po = pbase + prel + pi * 4
            pbr = BitReader(bytes(file87[po : po + 4]))
            vals = [pbr.read(4) for _ in range(8)]
            by, bx = divmod(bi, bw)
            for ry in range(2):
                dst = (by * 2 + ry) * width + bx * 4
                out[dst : dst + 4] = bytes(vals[ry * 4 : ry * 4 + 4])
            bi += 1
        else:
            zi = code - 13
            bi += zbases[zi] + br.read(zbits[zi]) + 1
            assert bi <= total
    return bytes(out), mid, width, height


def knapsack(items: list, sizes: dict, capacity: int) -> set:
    """The subset of ``items`` with the largest total size that fits ``capacity`` (bytes, 4-aligned)."""

    capu = capacity // 4
    reachable = [False] * (capu + 1)
    parent = [None] * (capu + 1)
    reachable[0] = True
    for ii, k in enumerate(items):
        u = sizes[k] // 4
        assert sizes[k] % 4 == 0
        for s in range(capu - u, -1, -1):
            if reachable[s] and not reachable[s + u]:
                reachable[s + u] = True
                parent[s + u] = (s, ii)
    best = max(i for i, v in enumerate(reachable) if v)
    packed, cur = set(), best
    while cur:
        prev, ii = parent[cur]
        packed.add(items[ii])
        cur = prev
    assert sum(sizes[k] for k in packed) == best * 4
    return packed


# -- the body build -------------------------------------------------------------------------------


@dataclass
class Extras:
    """What a fighter's moves add to the body build (frozen legacy for Sektor).

    ``frames``: key -> decoded frame (dict as :meth:`Donor.frame`), in key order.
    ``sets``: ordered named key lists; ``groups`` lists, per extra entropy group, the set names it
    holds (in order). ``key_order`` is the order the set names take in the frame key list.
    ``script_hooks`` run after the generic scripts and before the fallback; each gets the
    :class:`Body` and returns ``{file offset: word}`` (the offsets become owned).
    """

    frames: dict = field(default_factory=dict)
    sets: dict = field(default_factory=dict)
    key_order: list = field(default_factory=list)
    groups: list = field(default_factory=list)
    script_hooks: list[Callable[[Body], dict]] = field(default_factory=list)


@dataclass
class Body:
    file: bytearray  # the built file 0x87 image (stock size)
    clean_file: bytes
    shape_map: dict
    inherited: list  # body-slot frames, in slot order
    flipped: list
    frame_cache: dict
    frame_model: dict
    all_keys: list
    groups: list
    slot_cfg: dict
    translated: dict
    script_targets: dict
    item_offsets: dict
    stock_shape_set: set
    owned: set
    fallback: int
    fallback_positions: list
    chain_start: int
    new_end: int
    run_words: list
    push_words: list
    encoded: Encoded
    log: list
    report: dict = field(default_factory=dict)

    def f32(self, off):
        return be32(self.clean_file, off)


# Computed layout (fighters without an explicit layout): token policy for copied MKT body scripts.
# Tokens 1-5, 9, 12, 14 share the MKMSZ grammar; callbacks 1, 18 and 19 are the ones Sektor's
# runtime-accepted body copies unchanged; donor sound/palette tokens are dropped (MKMSZ ignores
# them); fighter-ID branches (8) are folded for the donor; partner/helper tokens need adapters.
KEPT_TOKENS = {1, 2, 3, 4, 5, 9, 12, 14}
KEPT_CALLBACKS = {1, 18, 19}
DROPPED_TOKENS = {7, 13, 15}
MAX_SCRIPT_WORDS = 64


class LayoutError(ValueError):
    pass


def linearise(donor: Donor, slot: int, starts: set[int], root: int | None = None) -> list:
    """MKT table 0 ``slot``'s script (or the script at ``root``) as host words: ints,
    ``("frame", rel)`` and ``("jump", index)``."""

    out: list = []
    at: dict[int, int] = {}
    pos = donor.table0[slot] if root is None else root
    jumps = []
    while True:
        if len(out) > MAX_SCRIPT_WORDS:
            raise LayoutError(f"slot 0x{slot:02X}: script longer than {MAX_SCRIPT_WORDS} words")
        at.setdefault(pos, len(out))
        v = donor.m32(pos)
        if v == 0:
            out.append(0)
            pos += 4
            if pos in starts:
                break
            continue
        if not MKT.is_token(v):
            if not donor.is_frame(v):
                raise LayoutError(f"slot 0x{slot:02X}: word 0x{v:X} at 0x{pos:X} is not a frame")
            out.append(("frame", v))
            pos += 4
            continue
        ops = [donor.m32(pos + 4 + 4 * k) for k in range(len(MKT.operands[v]))]
        if v == 1:
            out.append(1)
            jumps.append(len(out))
            out.append(ops[0])
            break
        if v == 8:  # fighter-ID branch: taken only for the donor itself
            pos = ops[1] if ops[0] == donor.fighter_id else pos + 12
            continue
        if v in DROPPED_TOKENS:
            pos += 4 * (1 + len(ops))
            continue
        if v == 6 and ops[0] not in KEPT_CALLBACKS:
            raise LayoutError(f"slot 0x{slot:02X}: callback {ops[0]} at 0x{pos:X} has no rule")
        if v not in KEPT_TOKENS and v != 6:
            raise LayoutError(f"slot 0x{slot:02X}: token {v} at 0x{pos:X} needs an adapter")
        out.append(v)
        for kind, op in zip(MKT.operands[v], ops, strict=True):
            out.append(("frame", op) if kind == "frame" else op)
        pos += 4 * (1 + len(ops))
    for j in jumps:
        target = out[j]
        if target not in at:
            raise LayoutError(f"slot 0x{slot:02X}: jump to 0x{target:X} outside the copied script")
        out[j] = ("jump", at[target])
    return out


def _host_layout(clean_file: bytes):
    """Logical spans of the host primary scripts and the table entries that alias into them."""

    primary = sorted({be32(clean_file, 4 * i) for i in range(0x41)} - {0})
    entries = [(4 * i, be32(clean_file, 4 * i)) for i in range(0x41)]
    entries += [(0x104 + 4 * i, be32(clean_file, 0x104 + 4 * i)) for i in range(0x2B)]
    return primary, [(o, v) for o, v in entries if v]


def lying_landing(words: list) -> list:
    """The knockdown's landing phase reduced to its last frame, the lying pose.

    The host shows only the first frame of the knockdown's second phase on some routes
    (``0x8005AC00``: select phase 2 of primary 0x1E, one ``animation_advance``), and secondary 9
    (the lying pose) points at that phase; stock Sub-Zero's phase is that single pose. MKT
    landings can open with a bounce (Reptile ``0x27C8``, legs up) before the lying frame
    (``0x27DC``), which the host would then hold (Reptile body proof v01, owner: "dead
    animation is not the lying flat")."""

    if any(isinstance(w, tuple) and w[0] == "jump" for w in words) or words.count(0) < 2:
        return words
    a = words.index(0) + 1
    b = words.index(0, a)
    frames = [w for w in words[a:b] if isinstance(w, tuple) and w[0] == "frame"]
    if len(frames) < 2 or len(frames) != b - a:
        return words
    return [*words[:a], frames[-1], *words[b:]]


KNOCKDOWN_SLOT = 0x1E


def phase_slot_frames(donor: Donor, slots) -> dict[int, list[list[int]]]:
    """Per phase slot, the donor table-0 script's frames grouped by phase."""

    if not slots:
        return {}
    starts = set(donor.table0) | set(MktRom(donor.mkt).table1(donor.fighter_id))
    out = {}
    for slot in slots:
        phases: list[list[int]] = [[]]
        for w in linearise(donor, slot, starts):
            if w == 0:
                phases.append([])
            elif isinstance(w, tuple) and w[0] == "frame" and donor.is_shape(w[1]):
                phases[-1].append(w[1])
        out[slot] = [p for p in phases if p]
    return out


def phase_fill(clean_file: bytes, slot: int, phases: list[list[int]], mode: str = "phases",
               stance: int | None = None) -> dict[int, int]:  # fmt: skip
    """Host frame positions of primary ``slot``'s stock script -> donor frames.

    ``phases``: phase *k* takes donor phase *k* (the last donor phase for later ones), scaled by
    position, end points kept. ``shift:N`` (signed): host position *p*, counted over all
    phases, shows frame *p + N* of the donor's phases but the last (its retract) in order;
    before them ``stance``, after them the retract scaled over the remaining positions.
    Sektor's accepted throw (proof v55) has its visuals two places late (``shift:-2``);
    Reptile's MKT throw lands right one place early (owner, inputs proofs v01-v02)."""

    root = be32(clean_file, 4 * slot)
    _, entries = _host_layout(clean_file)  # every table entry starts a script (the throw ends at +0x928)
    end = min((v for _, v in entries if v > root), default=TYPE_START)
    host: list[list[int]] = [[]]
    for p, v, kind in _host_items(clean_file, root, end):
        if kind == "end":
            host.append([])
        elif kind == "token" and v in (1, 2):
            break
        elif kind == "frame":
            host[-1].append(p)
    if mode.startswith("shift:"):
        shift = int(mode[6:])
        frames = [r for p in (phases[:-1] if len(phases) > 1 else phases) for r in p]
        retract = phases[-1] if len(phases) > 1 else frames[-1:]
        positions = [p for ph in host for p in ph]
        if stance is None and shift < 0:
            raise LayoutError(f"slot 0x{slot:02X}: a negative shift needs the stance pose")
        after = [p for p in range(len(positions)) if p + shift >= len(frames)]
        seq = []
        for p in range(len(positions)):
            if p + shift < 0:
                seq.append(stance)
            elif p + shift < len(frames):
                seq.append(frames[p + shift])
            else:
                k, n = after.index(p), len(after)
                seq.append(retract[0] if n == 1 else retract[round(k * (len(retract) - 1) / (n - 1))])
        return dict(zip(positions, seq, strict=True))
    out = {}
    for k, positions in enumerate(p for p in host if p):
        src = phases[min(k, len(phases) - 1)]
        n = len(positions)
        for i, pos in enumerate(positions):
            out[pos] = src[0] if n == 1 else src[round(i * (len(src) - 1) / (n - 1))]
    return out


def _host_items(data: bytes, start: int, end: int) -> list[tuple[int, int, str]]:
    """(offset, word, kind) of the host script words in ``[start, end)``; kind is ``frame``,
    ``end``, ``token`` or ``operand``."""

    out, p = [], start
    while p < end:
        v = be32(data, p)
        if v == 0 or not MKMSZ.is_token(v):
            out.append((p, v, "frame" if v else "end"))
            p += 4
            continue
        n = len(MKMSZ.operands[v]) + (MKMSZ.callback_extra_words.get(be32(data, p + 4), 0) if v == 6 else 0)
        out.append((p, v, "token"))
        out += [(p + 4 * k, be32(data, p + 4 * k), "operand") for k in range(1, 1 + n)]
        p += 4 * (1 + n)
    return out


def stock_tails(clean_file: bytes, slot_cfg: dict, translated: dict, stock_shapes: set[int],
                new_shapes: set[int]) -> tuple[dict, list]:  # fmt: skip
    """The host-only phases after a computed in-place script's loop, kept and translated.

    Some stock scripts carry phases after their own loop that the host reaches by phase or by
    jump: the punches (primary 0x0E/0x0F) retract, and switch from one punch to the other
    through a frame of each and a jump into the other punch's script (stock 0x0E: ``f4,
    0x0F-phase-2-frame-3, jump 0x58C``). MKT scripts end at the loop, so the computed layout
    left these phases empty and switching punches showed nothing (Reptile body proof v01,
    owner). When the imported script has the stock shape up to the loop (frames where stock
    has frames, the same tokens and operands elsewhere), its tail keeps the stock tokens,
    operands and jumps, and each stock frame becomes the imported frame that holds the same
    place in the imported scripts (the slot's own first). Returns (file offset -> word, log)."""

    matched = {}
    for slot, cfg in sorted(slot_cfg.items()):
        if not cfg.get("computed") or cfg["mode"] != "inplace":
            continue
        root, vals = cfg["target"], translated[slot]
        items = _host_items(clean_file, root, root + 4 * cfg["capacity"])
        loop = next((i for i, (_, v, kind) in enumerate(items) if kind == "token" and v in (1, 2)), None)
        if loop is None:
            continue
        main = (items[loop][0] - root) // 4 + (2 if items[loop][1] == 1 else 1)
        if main != len(vals) or main >= cfg["capacity"]:
            continue
        head = [(p, v, kind) for p, v, kind in items if p < root + 4 * main]
        if all(vals[(p - root) // 4] in new_shapes if kind == "frame" else vals[(p - root) // 4] == v
               for p, v, kind in head):  # fmt: skip
            matched[slot] = (root, main, items)
    own: dict = {}
    anywhere: dict = {}
    for slot, (root, main, items) in matched.items():
        for p, v, kind in items:
            if kind == "frame" and p < root + 4 * main:
                own.setdefault((slot, v), translated[slot][(p - root) // 4])
                anywhere.setdefault(v, translated[slot][(p - root) // 4])
    heads = [(r, r + 4 * m) for r, m, _ in matched.values()]
    writes, log = {}, []
    for slot, (root, main, items) in matched.items():
        span_end = root + 4 * slot_cfg[slot]["capacity"]
        out: dict | None = {}
        prev = None
        for p, v, kind in items:
            if p < root + 4 * main:
                prev = (v, kind)
                continue
            if kind == "frame":
                role = own.get((slot, v), anywhere.get(v))
                if v not in stock_shapes or role is None:
                    out = None
                    break
                out[p] = role
            elif kind == "operand" and prev == (1, "token") and not (
                any(lo <= v < hi for lo, hi in heads) or root + 4 * main <= v < span_end
            ):
                out = None  # a jump outside the kept scripts
                break
            else:
                out[p] = v
            prev = (v, kind)
        if out is None:
            log.append(f"TAIL slot 0x{slot:02X}: stock tail left empty (a frame or jump has no place)")
            continue
        writes.update(out)
        log.append(f"TAIL slot 0x{slot:02X}: {len(out)} stock tail words kept")
    return writes, log


def _computed_cfg(description, donor: Donor, clean_file: bytes) -> dict:
    reader = MktRom(donor.mkt)
    table1 = reader.table1(donor.fighter_id)
    starts = set(donor.table0) | set(table1)
    primary, entries = _host_layout(clean_file)
    cfg = {}
    for slot in description.body.slots:
        table, index = description.body.sources.get(slot, (0, slot))
        source = (donor.table0 if table == 0 else table1)[index]
        words = linearise(donor, slot, starts, source)
        if slot == KNOCKDOWN_SLOT:
            words = lying_landing(words)
        root = be32(clean_file, 4 * slot)
        end = next((r for r in primary if r > root), TYPE_START)
        capacity = (end - root) // 4
        aliases = []
        for off, v in entries:
            if off != 4 * slot and root < v < end:
                stock_phase = sum(1 for p in range(root, v, 4) if be32(clean_file, p) == 0)
                aliases.append((off, stock_phase))
        mode = "inplace" if len(words) <= capacity else "packed"
        cfg[slot] = {"donor": source, "mode": mode, "computed": True, "words": words,
                     "n": len(words), "target": root, "capacity": capacity, "aliases": aliases,
                     "shapes": [w[1] for w in words if isinstance(w, tuple) and w[0] == "frame"]}  # fmt: skip
    return cfg


def _slot_cfg(description: FighterDescription, donor: Donor, clean_file: bytes) -> dict:
    layout = description.body.layout
    if layout is None:
        return _computed_cfg(description, donor, clean_file)
    cfg = {}
    for slot in description.body.slots:
        entry = layout.slots.get(slot)
        donor_root = donor.table0[slot]
        host_root = be32(clean_file, 4 * slot)
        c = {"donor": donor_root, "mode": entry.mode, "hybrid": entry.hybrid, "capacity": entry.capacity,
             "place": entry.place}
        if entry.mode == "inplace":
            c["target"] = host_root
        if entry.words is not None:
            c["words"] = list(entry.words)
            c["n"] = len(c["words"])
        else:
            c["n"] = entry.n
            c["words"] = donor.script(donor_root, entry.n)
        c["shapes"] = [v for v in c["words"] if donor.is_shape(v)]
        cfg[slot] = c
    return cfg


def _rgb(w: int) -> tuple[int, int, int]:
    return ((w >> 11) & 31, (w >> 6) & 31, (w >> 1) & 31)


def palette_ramps(donor_palette: list[int]) -> list[list[int]]:
    """Donor palette indices 1.. split into ramps: runs that go from light to dark in one hue.

    MKT fighter palettes are laid out as ramps (Reptile: 11 greys down to black, 7 greens, 13
    browns). A ramp ends where brightness rises or where two coloured entries change hue."""

    ramps: list[list[int]] = []
    cur: list[int] = []
    prev = None
    for i in range(1, len(donor_palette)):
        c = _rgb(donor_palette[i])
        if prev is not None:
            rise = sum(c) > sum(prev) + 1
            hue = (max(c) - min(c) >= 3 and max(prev) - min(prev) >= 3
                   and c.index(max(c)) != prev.index(max(prev)))  # fmt: skip
            if rise or hue:
                ramps.append(cur)
                cur = []
        cur.append(i)
        prev = c
    if cur:
        ramps.append(cur)
    return ramps


def _ramp_reduction(donor_palette: list[int], usage: Counter, budget: int):
    """Contiguous segments of each ramp, ``budget`` in all, with the least usage-weighted
    squared error (exact arithmetic); None when the used ramps outnumber the budget."""

    ramps = palette_ramps(donor_palette)
    used = [any(usage.get(i) for i in r) for r in ramps]
    if sum(used) > budget:
        return None
    # Unused entries weigh 1 against 2**20 per pixel: they get a centre without moving it.
    weight = {i: (usage.get(i, 0) << 20) + 1 for i in range(len(donor_palette))}

    def cost(idx):
        w = sum(weight[i] for i in idx)
        sq = sum(weight[i] * sum(v * v for v in _rgb(donor_palette[i])) for i in idx)
        lin = [sum(weight[i] * _rgb(donor_palette[i])[a] for i in idx) for a in range(3)]
        return Fraction(sq * w - sum(v * v for v in lin), w)

    def split(r):  # best[k] and the k segments, by dynamic programming over cut points
        n = len(r)
        best: list[list[Fraction | None]] = [[None] * (n + 1) for _ in range(n + 1)]
        cut = [[0] * (n + 1) for _ in range(n + 1)]
        best[0][0] = Fraction(0)
        for k in range(1, n + 1):
            for j in range(k, n + 1):
                for i in range(k - 1, j):
                    prev = best[k - 1][i]
                    if prev is None:
                        continue
                    v = prev + cost(r[i:j])
                    if best[k][j] is None or v < best[k][j]:
                        best[k][j], cut[k][j] = v, i
        segs = {}
        for k in range(1, n + 1):
            out, j = [], n
            for kk in range(k, 0, -1):
                out.append(r[cut[kk][j] : j])
                j = cut[kk][j]
            segs[k] = out[::-1]
        return best, segs

    tables = [split(r) for r in ramps]
    dp: dict[int, tuple[Fraction, list[int]]] = {0: (Fraction(0), [])}
    for (best, _), r, u in zip(tables, ramps, used, strict=True):
        nxt: dict[int, tuple[Fraction, list[int]]] = {}
        for spent, (c, choice) in sorted(dp.items()):
            for k in range(1, len(r) + 1) if u else (0,):
                if spent + k > budget:
                    break
                v = c + (best[k][len(r)] if k else 0)
                if spent + k not in nxt or v < nxt[spent + k][0]:
                    nxt[spent + k] = (v, [*choice, k])
        dp = nxt
    spent = min(dp, key=lambda s: (dp[s][0], s))
    boxes = []
    for (_, segs), k in zip(tables, dp[spent][1], strict=True):
        if k:
            boxes += segs[k]
    return boxes, weight


def _median_cut(donor_palette: list[int], usage: Counter, budget: int):
    rgb = _rgb
    used = [i for i in range(1, len(donor_palette)) if usage.get(i)]
    boxes = [used] if used else []
    while len(boxes) < budget:
        best, axis, best_key = None, 0, (-1,)
        for bi, box in enumerate(boxes):
            if len(box) < 2:
                continue
            for ax in range(3):
                vals = [rgb(donor_palette[i])[ax] for i in box]
                key = ((max(vals) - min(vals)) * sum(usage[i] for i in box), -bi, -ax)
                if key > best_key:
                    best, axis, best_key = bi, ax, key
        if best is None:
            break
        box = sorted(boxes[best], key=lambda i: (rgb(donor_palette[i])[axis], i))
        total, run, cut = sum(usage[i] for i in box), 0, 1
        for k, i in enumerate(box[:-1], 1):
            run += usage[i]
            cut = k
            if 2 * run >= total:
                break
        boxes[best:best + 1] = [box[:cut], box[cut:]]
    return boxes, usage


def reduce_palette(donor_palette: list[int], usage: Counter, colours: int = 16) -> tuple[list[int], list[int]]:
    """The donor palette reduced to ``colours`` entries (entry 0 transparent).

    Each ramp of the donor palette (:func:`palette_ramps`) keeps its own colours, merged only
    with its neighbours in the ramp, so black never becomes a dark green and greys never take
    a skin tone (Reptile body proof v01, owner: "colors are messed up"). A palette that is not
    laid out as ramps falls back to a weighted median cut.

    Returns (index map for every donor index, host BGR555 words for the reduced entries)."""

    from .projectile import mkt_color_to_host

    rgb = _rgb
    reduced = _ramp_reduction(donor_palette, usage, colours - 1)
    boxes, weight_of = reduced if reduced is not None else _median_cut(donor_palette, usage, colours - 1)
    centres = []
    for box in boxes:
        weight = sum(weight_of[i] for i in box)
        centres.append(tuple(round(sum(rgb(donor_palette[i])[a] * weight_of[i] for i in box) / weight) for a in range(3)))
    index_map = [0] * len(donor_palette)
    for k, box in enumerate(boxes, 1):
        for i in box:
            index_map[i] = k
    for i in range(1, len(donor_palette)):
        if not usage.get(i) and centres:
            c = rgb(donor_palette[i])
            index_map[i] = 1 + min(range(len(centres)), key=lambda k: (sum((a - b) ** 2 for a, b in zip(c, centres[k], strict=True)), k))
    words = [0] + [mkt_color_to_host((r << 11) | (g << 6) | (b << 1) | 1) for r, g, b in centres]
    words += [0] * (colours - len(words))
    return index_map, words


def build_body(description: FighterDescription, clean: bytes, mkt: bytes, extras: Extras,
               rom: bytearray | None = None) -> Body:  # fmt: skip
    """Build the fighter body. When ``rom`` is given (the clean 16 MiB image being built), the
    Run-rate edit is applied to it; the file image is returned in :class:`Body`."""

    body_d = description.body
    layout = body_d.layout
    log: list[str] = []
    donor = Donor(mkt, description.donor_fighter_id)
    clean_file = bytes(clean[FILE87_ROM : FILE87_ROM + FILE87_SIZE])

    def f32(off):
        return be32(clean_file, off)

    slot_cfg = _slot_cfg(description, donor, clean_file)
    old_shapes = []
    for slot in sorted(slot_cfg):
        for rel in slot_cfg[slot]["shapes"]:
            if rel not in old_shapes:
                old_shapes.append(rel)
    phase_sources = phase_slot_frames(donor, body_d.phase_slots)
    for phases in phase_sources.values():
        for rel in (r for p in phases for r in p):
            if rel not in old_shapes:
                old_shapes.append(rel)
    run_rels = donor.frames(body_d.run_slot) if layout is None or layout.run_frames is None else list(layout.run_frames)
    frame_cache = {rel: donor.frame(rel) for rel in old_shapes}
    for r in run_rels:
        frame_cache[r] = donor.frame(r)
    sets = dict(extras.sets)
    key_order, extra_group_names = list(extras.key_order), [list(g) for g in extras.groups]
    if "flipped" not in key_order:  # the generic grabbed recipe needs the flip poses
        key_order.append("flipped")
        extra_group_names.append(["flipped"])
    sets.setdefault("flipped", donor.phase(MKT_FLIPPED))
    for r in sets["flipped"]:
        frame_cache[r] = donor.frame(r)
    frame_cache.update(extras.frames)

    colour = body_d.colour
    index_map, palette = colour.index_map, colour.palette
    if colour.method == "auto":
        usage = Counter()
        for fr in frame_cache.values():
            usage.update(fr["padded"])
        donor_palette = donor.palette()
        index_map, words16 = reduce_palette(donor_palette, usage)
        if max(usage) >= len(index_map):
            raise ValueError(f"frames use palette index {max(usage)} beyond the donor palette")
        palette = b"".join(w.to_bytes(2, "big") for w in words16) + clean_file[PALETTE_OFF + 32 : PALETTE_OFF + 64]
        log.append(f"COLOUR auto: {sum(1 for c in usage if c)} donor indices used -> 15 colours")
    for k in list(frame_cache):
        fr = dict(frame_cache[k])
        fr["padded"] = bytes(index_map[p] for p in fr["padded"])
        fr["blocks"] = make_blocks(fr["padded"], fr["stride"], fr["eh"])
        frame_cache[k] = fr
        assert max(fr["padded"]) < 16

    inherited_groups = layout.inherited_groups if layout else min(56, max(1, len(old_shapes) // 3))
    run_groups_n = layout.run_groups if layout else min(4, len(run_rels))
    old_groups = split_even(old_shapes, inherited_groups)
    run_groups = split_even(run_rels, run_groups_n)
    extra_groups = [[k for name in names for k in sets[name]] for names in extra_group_names]
    groups = old_groups + run_groups + extra_groups
    all_keys = old_shapes + run_rels + [k for name in key_order for k in sets[name]]
    assert len(groups) <= MODEL_COUNT_MAX and sorted(map(repr, all_keys)) == sorted(map(repr, (k for g in groups for k in g)))
    n_old, n_run = len(old_groups), len(run_groups)
    # Pattern priority: extra groups (last first), then Run, then the inherited body.
    order = list(range(len(groups) - 1, n_old + n_run - 1, -1)) + list(range(n_old, n_old + n_run)) + list(range(n_old))
    enc = encode(frame_cache, groups, order)

    file87 = bytearray(clean_file)
    file87[PALETTE_OFF : PALETTE_OFF + 64] = palette

    stock_shapes = []
    for off in range(TYPE_START, TYPE_END, 4):
        if off + 20 <= FILE87_SIZE and f32(off) == off + 8 and f32(off + 4) == 0:
            image = f32(off + 8)
            if 0 <= image < FILE87_SIZE and clean_file[image : image + 4] == b"\x05\0\0\0":
                stock_shapes.append(off)
    stock_shape_set = set(stock_shapes)
    stock_ref_positions = [off for off in range(SCRIPT_REF_START, TYPE_START, 4) if f32(off) in stock_shape_set]

    # Dead stock script regions reused by relocated scripts: nothing outside a region may point
    # into it except the redirected slot roots.
    redirect_slots = {s for s, c in slot_cfg.items() if c["mode"] != "inplace"}
    for lo, hi in layout.dead_regions if layout else ():
        for p in range(0, TYPE_START, 4):
            v = f32(p)
            if lo <= v < hi and not (lo <= p < hi) and not (p < 0x104 and p // 4 in redirect_slots):
                raise ValueError(("external dead-script reference", hex(p), hex(v), hex(lo), hex(hi)))

    file87[TYPE_START:TYPE_END] = b"\xff" * (TYPE_END - TYPE_START)
    file87[TYPE_START : TYPE_START + len(enc.table)] = enc.table
    reclaim_cursor = align4(TYPE_START + len(enc.table))

    item_sizes = {k: 32 + len(enc.streams[k]) for k in all_keys}
    script_items = [("script", s) for s, c in sorted(slot_cfg.items()) if c["mode"] == "packed"]
    for it in script_items:
        item_sizes[it] = 4 * slot_cfg[it[1]]["n"]
    items = list(all_keys) + script_items
    cap = TYPE_END - reclaim_cursor
    packed = knapsack(items, item_sizes, cap)
    item_offsets = {}
    append_cursor = align4(FILE87_SIZE)
    for k in items:
        if k in packed:
            off = reclaim_cursor
            reclaim_cursor += item_sizes[k]
        else:
            off = append_cursor
            append_cursor += item_sizes[k]
        item_offsets[k] = off
    assert reclaim_cursor <= TYPE_END
    new_end = append_cursor
    chain_start = align4(reclaim_cursor)
    if new_end > len(file87):
        file87 += b"\xff" * (new_end - len(file87))
    if new_end >= SAFE_END:
        raise ValueError(f"fighter file 0x{new_end:X} exceeds the budget 0x{SAFE_END:X}")
    log.append(f"RECLAIM_PACK_USED {hex(sum(item_sizes[k] for k in packed))} RECLAIM_CAP {hex(cap)} "
               f"SLACK {hex(cap - sum(item_sizes[k] for k in packed))}")  # fmt: skip
    log.append(f"APPENDED_ITEMS {sum(1 for k in items if k not in packed)} "
               f"APPENDED_BYTES {hex(sum(item_sizes[k] for k in items if k not in packed))}")  # fmt: skip

    shape_map = {}
    for k in all_keys:
        fr = frame_cache[k]
        shape = item_offsets[k]
        stream = enc.streams[k]
        sub = shape + 8
        image = sub + 12
        shape_map[k] = shape
        put32(file87, shape, sub)
        put32(file87, shape + 4, 0)
        put32(file87, sub, image)
        file87[sub + 4 : sub + 6] = fr["w"].to_bytes(2, "big")
        file87[sub + 6 : sub + 8] = fr["h"].to_bytes(2, "big")
        file87[sub + 8 : sub + 10] = (fr["x"] & 0xFFFF).to_bytes(2, "big")
        file87[sub + 10 : sub + 12] = (fr["y"] & 0xFFFF).to_bytes(2, "big")
        file87[image : image + 4] = b"\x05\0\0\0"
        put32(file87, image + 4, TYPE_START - image)
        put32(file87, image + 8, (fr["eh"] << 16) | fr["stride"])
        file87[image + 12 : image + 12 + len(stream)] = stream

    # Body scripts.
    script_targets = {s: (item_offsets[("script", s)] if c["mode"] == "packed" else c["place"])
                      for s, c in slot_cfg.items() if c["mode"] != "inplace"}  # fmt: skip
    owned, translated = set(), {}
    for slot, cfg in slot_cfg.items():
        target = script_targets.get(slot, cfg.get("target"))
        donor_words = cfg["words"]
        if cfg.get("computed"):
            vals = [shape_map[w[1]] if isinstance(w, tuple) and w[0] == "frame"
                    else target + 4 * w[1] if isinstance(w, tuple) else w for w in donor_words]  # fmt: skip
        elif cfg["hybrid"]:
            stock_words = [f32(cfg["target"] + 4 * i) for i in range(cfg["n"])]
            vals = [shape_map[v] if donor.is_shape(v) else stock_words[i] for i, v in enumerate(donor_words)]
        else:
            vals = []
            for value in donor_words:
                if donor.is_shape(value):
                    vals.append(shape_map[value])
                elif cfg["donor"] <= value < cfg["donor"] + cfg["n"] * 4 and (value - cfg["donor"]) % 4 == 0:
                    vals.append(target + (value - cfg["donor"]))
                else:
                    vals.append(value)
        if slot in script_targets:
            put32(file87, slot * 4, target)
            for i, v in enumerate(vals):
                put32(file87, target + 4 * i, v)
                owned.add(target + 4 * i)
        else:
            capw = cfg["capacity"]
            assert len(vals) <= capw
            for i in range(capw):
                put32(file87, target + 4 * i, vals[i] if i < len(vals) else 0)
                owned.add(target + 4 * i)
        translated[slot] = vals
        if cfg.get("computed"):
            phase_starts = [0] + [i + 1 for i, v in enumerate(vals[:-1]) if v == 0]
            for off, phase in cfg["aliases"]:
                put32(file87, off, target + 4 * phase_starts[min(phase, len(phase_starts) - 1)])
                log.append(f"ALIAS table 0x{off:X} -> slot 0x{slot:02X} phase {phase}")

    stance_rel = translated_first_frame(slot_cfg, donor)
    for slot, phases in phase_sources.items():
        mode = body_d.phase_slots[slot]
        for pos, rel in phase_fill(clean_file, slot, phases, mode, stance_rel).items():
            put32(file87, pos, shape_map[rel])
            owned.add(pos)
        log.append(f"PHASES slot 0x{slot:02X}: host script kept, donor frames ({mode})")
    tails, tail_log = stock_tails(clean_file, slot_cfg, translated, stock_shape_set, set(shape_map.values()))
    for pos, word in tails.items():
        put32(file87, pos, word)
        owned.add(pos)
    log += tail_log

    # Push (MKMSZ only): the Run poses over the seven native Push ticks.
    clean_push = [f32(PUSH_TARGET + 4 * i) for i in range(9)]
    assert clean_push[7:] == [1, PUSH_TARGET + 4]
    push_visual = [run_rels[i % len(run_rels)] for i in range(6)] + [run_rels[0]]
    push_words = [shape_map[x] for x in push_visual] + clean_push[7:]
    for i, v in enumerate(push_words):
        put32(file87, PUSH_TARGET + 4 * i, v)
        owned.add(PUSH_TARGET + 4 * i)

    # Run: exactly the donor poses, then the native loop to the Run root.
    assert [f32(RUN_TARGET + 4 * i) for i in range(14)][12:] == [1, RUN_TARGET]
    run_words = [shape_map[x] for x in run_rels] + [1, RUN_TARGET]
    for i, v in enumerate(run_words):
        put32(file87, RUN_TARGET + 4 * i, v)
        owned.add(RUN_TARGET + 4 * i)

    body = Body(file87, clean_file, shape_map, old_shapes, [shape_map[r] for r in sets["flipped"]], frame_cache, enc.frame_model, all_keys, groups, slot_cfg,
                translated, script_targets, item_offsets, stock_shape_set, owned, 0, [], chain_start,
                new_end, run_words, push_words, enc, log)  # fmt: skip

    # Description script edits (positions -> donor frames), then the moves' hooks.
    for pos, rel in (layout.frame_edits if layout else {}).items():
        assert f32(pos) in stock_shape_set, (hex(pos), hex(f32(pos)))
        put32(file87, pos, shape_map[rel])
        owned.add(pos)
    for hook in extras.script_hooks:
        for pos, word in hook(body).items():
            put32(file87, pos, word)
            owned.add(pos)

    # Every remaining direct stock frame reference -> the first stance frame.
    fallback = shape_map[translated_first_frame(slot_cfg, donor)]
    fallback_positions = []
    for pos in stock_ref_positions:
        if pos in owned:
            continue
        put32(file87, pos, fallback)
        fallback_positions.append(pos)
    body.fallback, body.fallback_positions = fallback, fallback_positions

    body.report = {
        "frames": len(all_keys), "inherited": len(old_shapes), "run": len(run_rels),
        "table_bytes": len(enc.table), "stream_bytes": enc.stream_bytes,
        "reclaim_capacity": cap, "reclaim_used": sum(item_sizes[k] for k in packed),
        "appended_items": sum(1 for k in items if k not in packed),
        "appended_bytes": sum(item_sizes[k] for k in items if k not in packed),
        "file_end": new_end, "file_budget": SAFE_END, "chain_start": chain_start,
        "chain_free": TYPE_END - chain_start,
        "packed_scripts": [s for s, c in slot_cfg.items() if c["mode"] == "packed"],
    }  # fmt: skip
    for k in all_keys:
        dec, mid, w, h = decode_type5(file87, shape_map[k], len(groups))
        fr = frame_cache[k]
        assert mid == enc.frame_model[k] and w == fr["stride"] and h == fr["eh"] and dec == fr["padded"]

    if rom is not None:
        rate = body_d.run_rate
        assert be32(rom, RUN_RATE_ROM) == RUN_RATE_STOCK
        put32(rom, RUN_RATE_ROM, (RUN_RATE_STOCK & ~0xFFFF) | rate)
    return body


def translated_first_frame(slot_cfg: dict, donor: Donor):
    """The stance's first donor frame (the fallback for unmapped stock references)."""

    for v in slot_cfg[0x00]["words"]:
        if isinstance(v, tuple) and v[0] == "frame":
            return v[1]
        if isinstance(v, int) and donor.is_shape(v):
            return v
    raise ValueError("the stance script has no frame")
