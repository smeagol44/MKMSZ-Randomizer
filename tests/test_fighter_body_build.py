"""Generic body builder (Fighter recompiler plan, milestone 1).

The byte-identity gate (generic builder + Sektor's description == the pinned Sektor build)
is ``tests/test_fighter_swap.py::test_sektor_build_matches_the_proof_line`` (ROM-backed).
"""

from __future__ import annotations

import io
import os
import re
import tokenize
from pathlib import Path

import pytest

from mkmszr.fighter_import import body_build as bb
from mkmszr.fighter_import import description as fd

GENERIC = Path("src/mkmszr/fighter_import/body_build.py").read_text(encoding="utf-8")

# Sektor-only items from Wiki Fighter-Recompiler-Inventory that must not appear in generic code.
SEKTOR_ONLY = {
    "robot heap": "0x8881C0", "robot dictionary": "0x906A90", "staging RR": "0xF40000",
    "stance frame": "0x1768", "Run pose": "0x2708", "elbow combo": "0x1C0C", "shoulder": "0x22EC",
    "arm pose": "0x2318", "teleport pose": "0x2F08", "combo script": "0x5E0", "throw script": "0x8F8",
    "late knee": "0x6A0", "relocated place": "0x798",
}  # fmt: skip


def _code_tokens() -> tuple[set[int], set[str]]:
    numbers, names = set(), set()
    for tok in tokenize.generate_tokens(io.StringIO(GENERIC).readline):
        if tok.type == tokenize.NUMBER:
            numbers.add(int(tok.string, 0))
        elif tok.type == tokenize.NAME:
            names.add(tok.string.lower())
    return numbers, names


def test_no_sektor_constants_in_generic_code() -> None:
    numbers, names = _code_tokens()
    for what, literal in SEKTOR_ONLY.items():
        assert int(literal.rstrip(","), 0) not in numbers, what
    assert not {n for n in names if re.search(r"sektor|robo|mecarm|knee|elbow|throw", n)}


def test_split_even_and_blocks() -> None:
    assert bb.split_even(list(range(10)), 4) == [[0, 1], [2, 3, 4], [5, 6], [7, 8, 9]]
    assert bb.split_even([1, 2], 4) == [[1], [2]]
    padded = bytes(range(16))
    assert bb.make_blocks(padded, 4, 4) == [bytes([0, 1, 2, 3, 4, 5, 6, 7]), bytes(range(8, 16))]


def test_encode_round_trips_through_the_independent_decoder() -> None:
    import random

    rng = random.Random(7)
    frames = {}
    for k in range(6):
        w, h = 8 + 4 * (k % 3), 6 + 2 * (k % 2)
        padded = bytes(rng.choice([0, 0, 0, 1, 5, 9, 15]) for _ in range(w * h))
        frames[k] = {"w": w, "h": h, "x": 0, "y": 0, "stride": w, "eh": h, "padded": padded, "blocks": bb.make_blocks(padded, w, h)}
    groups = [[0, 1, 2], [3, 4], [5]]
    enc = bb.encode(frames, groups, [2, 1, 0])
    file87 = bytearray(b"\xff" * bb.TYPE_START) + enc.table
    shapes = {}
    for k, fr in frames.items():
        shape = (len(file87) + 3) & ~3
        file87 += b"\xff" * (shape - len(file87))
        sub, image = shape + 8, shape + 20
        rec = bytearray(20 + len(enc.streams[k]))
        rec[0:4] = sub.to_bytes(4, "big")
        rec[8:12] = image.to_bytes(4, "big")
        rec[12:14], rec[14:16] = fr["w"].to_bytes(2, "big"), fr["h"].to_bytes(2, "big")
        file87 += rec
        file87[image : image + 4] = b"\x05\0\0\0"
        file87[image + 4 : image + 8] = ((bb.TYPE_START - image) & 0xFFFFFFFF).to_bytes(4, "big")
        file87[image + 8 : image + 12] = ((fr["eh"] << 16) | fr["stride"]).to_bytes(4, "big")
        file87[image + 12 : image + 12 + len(enc.streams[k])] = enc.streams[k]
        shapes[k] = shape
    for k, fr in frames.items():
        pixels, model, w, h = bb.decode_type5(bytes(file87) + bytes(64), shapes[k], len(groups))
        assert (pixels, model, w, h) == (fr["padded"], enc.frame_model[k], fr["stride"], fr["eh"])


def test_knapsack_fills_the_capacity_best() -> None:
    sizes = {"a": 12, "b": 8, "c": 20, "d": 4}
    packed = bb.knapsack(list(sizes), sizes, 24)
    assert sum(sizes[k] for k in packed) == 24


def test_reduce_palette_is_deterministic_and_keeps_transparency() -> None:
    from collections import Counter

    palette = [0x07C0] + [((i * 7 % 32) << 11) | ((i * 13 % 32) << 6) | ((i * 3 % 32) << 1) | 1 for i in range(1, 32)]
    usage = Counter({i: (i * 37) % 101 + 1 for i in range(32)})
    usage[5] = 0
    index_map, words = bb.reduce_palette(palette, usage)
    assert (index_map, words) == bb.reduce_palette(palette, Counter(dict(reversed(list(usage.items())))))
    assert index_map[0] == 0 and all(1 <= index_map[i] <= 15 for i in range(1, 32))
    assert len(words) == 16 and words[0] == 0 and all(w & 0x8000 for w in words[1:])


def test_reduce_palette_keeps_ramps_apart() -> None:
    from collections import Counter

    def mkt(r, g, b):
        return (r << 11) | (g << 6) | (b << 1) | 1

    # Reptile-like: 11 greys down to black, 7 greens, 13 browns; the darkest green is heavily
    # used and median cut used to merge it with black.
    greys = [mkt(v, v, v) for v in (29, 24, 20, 16, 12, 10, 8, 6, 4, 2, 0)]
    greens = [mkt(1, g, 1) for g in (13, 12, 10, 9, 7, 5, 3)]
    browns = [mkt(26 - 2 * k, max(0, 20 - 2 * k), max(0, 16 - 2 * k)) for k in range(13)]
    palette = [0x07C0, *greys, *greens, *browns]
    assert [len(r) for r in bb.palette_ramps(palette)] == [11, 7, 13]
    usage = Counter({i: 1000 for i in range(1, 32)})
    usage[18] = 100000
    index_map, words = bb.reduce_palette(palette, usage)
    ramp_of = {i: 0 if i <= 11 else 1 if i <= 18 else 2 for i in range(1, 32)}
    for i in range(1, 32):
        for j in range(1, 32):
            if index_map[i] == index_map[j]:
                assert ramp_of[i] == ramp_of[j], (i, j)
    w = words[index_map[11]]
    assert w & 31 == (w >> 5) & 31 == (w >> 10) & 31 <= 2  # black stays a neutral near-black


def test_lying_landing_keeps_the_last_landing_frame() -> None:
    f = [("frame", r) for r in range(6)]
    assert bb.lying_landing([*f[:3], 0, f[3], f[4], 0]) == [*f[:3], 0, f[4], 0]
    assert bb.lying_landing([*f[:3], 0, f[3], 0]) == [*f[:3], 0, f[3], 0]
    assert bb.lying_landing([*f[:2], 1, ("jump", 0)]) == [*f[:2], 1, ("jump", 0)]


# ---------------------------------------------------------------- ROM-backed

CLEAN, MKT = os.environ.get("MKMSZR_CLEAN_ROM"), os.environ.get("MKMSZR_MKT_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")
needs_roms = pytest.mark.skipif(not (CLEAN and MKT), reason="needs MKMSZR_CLEAN_ROM and MKMSZR_MKT_ROM")
BODY_SLOTS = [i for i in range(0x23) if i not in (0x0D, 0x10)] + [0x4A, bb.MKT_FLIPPED]
# Documented exceptions (Wiki MKT-Fighter-Asset-Translation): Sonya's MKT slot 0x15 holds bare
# object descriptors with their own palette pointer, not fighter frame records.
NOT_FRAME_RECORDS = {(1, 0x15)}
# Fighter 24 binds 0x800BB7EC but its table entry 0x800B9AAC has another layout (Pending).
UNEXPLAINED_PALETTES = {24}


@needs_mkt
def test_every_body_frame_of_the_roster_decodes() -> None:
    from mkmszr.fighter_import.script import MKT as DIALECT

    mkt = Path(MKT).read_bytes()
    for fighter in range(26):  # ids 26-30 repeat KHAMELEON over other fighters' banks
        donor = bb.Donor(mkt, fighter)
        for slot in BODY_SLOTS:
            if (fighter, slot) in NOT_FRAME_RECORDS:
                continue
            p, ends = donor.table0[slot], 0
            for _ in range(80):
                v = donor.m32(p)
                if v == 0:
                    ends += 1
                    p += 4
                    if ends >= 8:
                        break
                    continue
                if v == 1:
                    break
                if DIALECT.is_token(v):
                    p += 4 * (1 + len(DIALECT.operands[v]))
                    continue
                assert donor.is_frame(v), (fighter, hex(slot), hex(v))
                p += 4


@needs_mkt
def test_computed_layout_folds_the_donor_branch() -> None:
    mkt = Path(MKT).read_bytes()
    from mkmszr.fighter_import.mkt_fighter import MktRom

    donor = bb.Donor(mkt, 19)  # Reptile: idle opens with "8, 0x13, 0x2B8" (branch taken for 0x13)
    starts = set(donor.table0) | set(MktRom(mkt).table1(19))
    words = bb.linearise(donor, 0x00, starts)
    assert 8 not in words and all(isinstance(w, tuple) and w[0] == "frame" for w in words[:2])
    assert words[-2] == 1 and words[-1][0] == "jump"


@needs_roms
def test_reptile_body_builds_and_fits() -> None:
    from mkmszr.fighter_import import common_moves as cm
    from mkmszr.fighter_import import description as fd

    body = bb.build_body(fd.load("reptile"), Path(CLEAN).read_bytes(), Path(MKT).read_bytes(), bb.Extras())
    r = body.report
    assert r["appended_items"] == 0 and r["file_end"] == bb.FILE87_SIZE  # stock-size file
    assert r["chain_free"] >= 0x10000  # room left for his moves
    # 155 + combo 12 + throw 8 + slide 2 + forceball 5 + acid 3 + invisibility 3 (the elbow's
    # frames were already in the body)
    assert (r["frames"], r["run"]) == (188, 9)
    out = cm.apply(bytes(body.file), stock=body.clean_file, flipped=body.flipped, slide=False)
    # Reptile's own MKT slide (table-1 slot 2) on host secondary 2 (body.secondary_slots).
    assert cm.frames(out, cm.SLIDE) == [body.shape_map[r] for r in (0x1E54, 0x2F94, 0x2FA8)]
    assert len(cm.frames(out, cm.PICKUP)) == 5 and len(set(cm.frames(out, cm.LONG_FALL))) == 1
    # The lying pose (S09, the knockdown's phase 2) is one frame: the donor landing's last.
    lying = body.shape_map[0x27DC]
    assert cm.frames(out, (1, 9)) == [lying] == cm.phase_frames(out, cm.KNOCKDOWN, 2)[-1:]
    assert cm.frames(out, cm.DEATH)[-1] == lying
    # The punches keep the host's retract and switch phases (stock tail after the loop).
    assert any("TAIL slot 0x0E: 16" in line for line in body.log)
    assert any("TAIL slot 0x0F: 15" in line for line in body.log)
    for slot in (0x0E, 0x0F):
        root = bb.be32(out, 4 * slot)
        stock = [bb.be32(body.clean_file, root + 4 * i) for i in range(28 if slot == 0x0E else 27)]
        now = [bb.be32(out, root + 4 * i) for i in range(len(stock))]
        assert [w for w in now if w not in body.shape_map.values()] == [
            w for w in stock if w not in body.stock_shape_set
        ]  # tokens, operands, phase ends and jumps are stock
        assert all(w in body.shape_map.values() for w, s in zip(now, stock) if s in body.stock_shape_set)
    # Combo animation (host primary 0x10) from MKT table-1 slot 0; throw (0x23) by phase.
    assert body.slot_cfg[0x10]["donor"] == bb.MktRom(Path(MKT).read_bytes()).table1(19)[0]
    throw = cm.frames(out, (0, 0x23))
    # shift:+1 (owner): MKT phases 1-2 (2 + 6 frames) one place early, then the retract's ends.
    grab = [0x29E4, 0x29F8, 0x2A0C, 0x2A20, 0x2A34, 0x2A48, 0x2A5C, 0x2A5C, 0x29E4]
    assert throw == [body.shape_map[r] for r in grab]


@needs_mkt
def test_palette_table_is_indexed_by_fighter_id() -> None:
    mkt = Path(MKT).read_bytes()

    def bound(fighter):  # the palette the fighter's first frame binds
        donor = bb.Donor(mkt, fighter)
        first = donor.frames(0)[0]
        return donor.m32((first + 8 if donor.is_shape(first) else donor.parts(first)[0]) + 12)

    binds = {f: bound(f) for f in range(26)}
    for fighter, palette in binds.items():
        table = bb.be32(mkt, bb.MKT_PALETTE_TABLE - 0x80000000 + 4 * fighter)
        if table == palette or fighter in UNEXPLAINED_PALETTES:
            continue
        # Shared art (ninjas, robots): the table holds the costume recolour of a palette that
        # another fighter's art binds too.
        assert sum(1 for p in binds.values() if p == palette) > 1, fighter
    assert sum(1 for f, p in binds.items() if p == bb.be32(mkt, bb.MKT_PALETTE_TABLE - 0x80000000 + 4 * f)) >= 14
    reptile = bb.Donor(mkt, 19).palette()
    assert len(reptile) == 32
    assert all(((w >> 6) & 31) > ((w >> 11) & 31) for w in reptile[17:30])  # green ramp


@needs_roms
def test_rayden_body_builds() -> None:
    # Rayden's sweep getup (slot 0x22) jumps into his getup script (copied inline), frame
    # 0x15DC holds one more row than its descriptor shows (cropped, as MKT draws it), his
    # palette ramps rise, and his codec-15 silhouettes use their own palette 0x800B9AF0; his
    # throw (phase_slots) skips draw-order callback 37, and his getup scripts start with the
    # script sound (callback 2, spare descriptor 0x2A).
    body = bb.build_body(fd.load("rayden"), Path(CLEAN).read_bytes(), Path(MKT).read_bytes(),
                         bb.Extras(), rom=bytearray(Path(CLEAN).read_bytes()))  # fmt: skip
    assert body.report["frames"] == 148 and body.report["file_end"] <= body.report["file_budget"]


@needs_roms
def test_palette_ramps_either_direction() -> None:
    mkt = Path(MKT).read_bytes()
    rayden = bb.palette_ramps(bb.Donor(mkt, 24).palette())
    assert [len(r) for r in rayden] == [11, 2, 3, 2, 13]  # black up to cyan, ..., greys up to white
    reptile = bb.palette_ramps(bb.Donor(mkt, 19).palette())
    assert [len(r) for r in reptile] == [8, 8, 15]  # light-to-dark ramps split as before
