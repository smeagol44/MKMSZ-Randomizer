"""Generic body builder (Fighter recompiler plan, milestone 1).

The byte-identity gate (generic builder + Sektor's description == the pinned Sektor build)
is ``tests/test_fighter_swap.py::test_sektor_build_matches_the_proof_line`` (ROM-backed).
"""

from __future__ import annotations

import io
import re
import tokenize
from pathlib import Path

from mkmszr.fighter_import import body_build as bb

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
