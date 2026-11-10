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
from functools import lru_cache

from .description import FighterDescription
from .mkt_fighter import MktRom
from .script import MKT

MKT_FLIPPED = 0x47  # MKT table-0 slot whose first phase is the fighter's flip poses

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
        return (isinstance(rel, int) and rel > 0 and self.base + rel + 8 <= len(self.mkt)
                and self.m32(rel) == rel + 8 and self.m32(rel + 4) == 0)  # fmt: skip

    def frame(self, rel):
        o = self.base + rel
        assert be32(self.mkt, o) == rel + 8 and be32(self.mkt, o + 4) == 0, hex(rel)
        sub = o + 8
        image_rel = be32(self.mkt, sub)
        packed = be32(self.mkt, sub + 4)
        anchor = be32(self.mkt, sub + 8)
        h = (packed >> 16) & 0xFFFF
        w = packed & 0xFFFF
        x = s16((anchor >> 16) & 0xFFFF)
        y = s16(anchor & 0xFFFF)
        src = self.mkt[self.base + image_rel :]
        typ = src[0]
        if typ == 15:
            raw = dec_15(src)
        elif typ in (22, 23, 24):
            raw = dec_22_24(src, self.dictionary)
        else:
            raise ValueError((hex(rel), typ, hex(image_rel)))
        stride = align4(w)
        assert len(raw) == h * stride, (hex(rel), typ, w, h, len(raw))
        eh = align2(h)
        if eh > h:
            raw += bytes(stride * (eh - h))
        return {"w": w, "h": h, "x": x, "y": y, "stride": stride, "eh": eh, "padded": raw,
                    "blocks": make_blocks(raw, stride, eh), "codec": typ, "donor": rel}  # fmt: skip

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

    def f32(self, off):
        return be32(self.clean_file, off)


def _slot_cfg(description: FighterDescription, donor: Donor, clean_file: bytes) -> dict:
    layout = description.body.layout
    cfg = {}
    for slot in description.body.slots:
        entry = layout.slots.get(slot) if layout else None
        donor_root = donor.table0[slot]
        host_root = be32(clean_file, 4 * slot)
        if entry is None:
            raise NotImplementedError(f"computed layout for slot 0x{slot:02X} (milestone 1, PR 3)")
        c = {"donor": donor_root, "mode": entry.mode}
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


def build_body(description: FighterDescription, clean: bytes, mkt: bytes, extras: Extras,
               rom: bytearray | None = None) -> Body:  # fmt: skip
    """Build the fighter body. When ``rom`` is given (the clean 16 MiB image being built), the
    Run-rate edit is applied to it; the file image is returned in :class:`Body`."""

    body_d = description.body
    layout = body_d.layout
    if layout is None:
        raise NotImplementedError("computed layout (milestone 1, PR 3)")
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
    run_rels = donor.frames(body_d.run_slot) if layout.run_frames is None else list(layout.run_frames)
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
    for k in list(frame_cache):
        fr = dict(frame_cache[k])
        fr["padded"] = bytes(colour.index_map[p] for p in fr["padded"])
        fr["blocks"] = make_blocks(fr["padded"], fr["stride"], fr["eh"])
        frame_cache[k] = fr
        assert max(fr["padded"]) < 16

    old_groups = split_even(old_shapes, layout.inherited_groups)
    run_groups = split_even(run_rels, layout.run_groups)
    extra_groups = [[k for name in names for k in sets[name]] for names in extra_group_names]
    groups = old_groups + run_groups + extra_groups
    all_keys = old_shapes + run_rels + [k for name in key_order for k in sets[name]]
    assert len(groups) <= MODEL_COUNT_MAX and sorted(map(repr, all_keys)) == sorted(map(repr, (k for g in groups for k in g)))
    n_old, n_run = len(old_groups), len(run_groups)
    # Pattern priority: extra groups (last first), then Run, then the inherited body.
    order = list(range(len(groups) - 1, n_old + n_run - 1, -1)) + list(range(n_old, n_old + n_run)) + list(range(n_old))
    enc = encode(frame_cache, groups, order)

    file87 = bytearray(clean_file)
    file87[PALETTE_OFF : PALETTE_OFF + 64] = colour.palette

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
    for lo, hi in layout.dead_regions:
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
    script_targets = {s: (item_offsets[("script", s)] if c["mode"] == "packed" else layout.slots[s].place)
                      for s, c in slot_cfg.items() if c["mode"] != "inplace"}  # fmt: skip
    owned, translated = set(), {}
    for slot, cfg in slot_cfg.items():
        target = script_targets.get(slot, cfg.get("target"))
        donor_words = cfg["words"]
        if layout.slots[slot].hybrid:
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
            capw = layout.slots[slot].capacity
            assert len(vals) <= capw
            for i in range(capw):
                put32(file87, target + 4 * i, vals[i] if i < len(vals) else 0)
                owned.add(target + 4 * i)
        translated[slot] = vals

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
    for pos, rel in layout.frame_edits.items():
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

    return next(v for v in slot_cfg[0x00]["words"] if donor.is_shape(v))
