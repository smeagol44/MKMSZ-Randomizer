"""Reading aid for MKT moves (Fighter recompiler plan, milestone 3)."""

from __future__ import annotations

import os
import struct
from pathlib import Path

import pytest

from mkmszr.fighter_import import reading
from mkmszr.fighter_import.mipsdis import decode
from mkmszr.fighter_import.mkt_registry import REGISTRY

MKT = os.environ.get("MKMSZR_MKT_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")


@pytest.mark.parametrize(
    ("word", "pc", "text"),
    [
        (0x27BDFFE8, 0x80000000, "addiu sp, sp, -24"),
        (0x0C01DBDC, 0x8004F9AC, "jal 0x80076F70"),
        (0x03E00008, 0, "jr ra"),
        (0x3C048015, 0, "lui a0, 0x8015"),
        (0x34849999, 0, "ori a0, a0, 0x9999"),
        (0x56220032, 0x8004BEE0, "bnel s1, v0, 0x8004BFAC"),
        (0x8FBF0014, 0, "lw ra, 20(sp)"),
        (0x0040F809, 0, "jalr ra, v0"),
        (0x00057403, 0, "sra t6, a1, 16"),
        (0x46062000, 0, "add.s f0, f4, f6"),
        (0x00000000, 0, "nop"),
    ],
)
def test_decode(word: int, pc: int, text: str) -> None:
    assert decode(word, pc).text == text


def _image(code: dict[int, list[int]], words: dict[int, int] | None = None) -> bytes:
    data = bytearray(0xAB200)
    for va, insns in code.items():
        for i, w in enumerate(insns):
            struct.pack_into(">I", data, va - 0x80000000 + 4 * i, w)
    for va, w in (words or {}).items():
        struct.pack_into(">I", data, va - 0x80000000, w)
    return bytes(data)


def test_constants_reach_call_arguments_through_delay_slots_and_merges() -> None:
    entry = 0x80001000
    code = [
        0x3C048015,  # lui a0, 0x8015
        0x10A00002,  # beq a1, zero, +2  (-> 0x8000100C)
        0x24060007,  # addiu a2, zero, 7   (delay slot: both paths)
        0x24070001,  # addiu a3, zero, 1   (fall-through only)
        0x0C000800,  # jal 0x80002000      (merge point)
        0x24846BA0,  # addiu a0, a0, 0x6BA0 (delay slot)
        0x03E00008,  # jr ra
        0x00000000,
    ]
    r = reading.read(_image({entry: code}), entry)
    assert [i.pc for i in r.insns][-1] == entry + 4 * 7
    (call,) = r.calls
    assert call.target == 0x80002000
    assert call.args == (0x80156BA0, None, 7, None)  # a3 differs on the two paths
    assert call.name is None and r.unknown_calls == [call]


def test_dispatcher_entries_and_routine_arguments_are_followed() -> None:
    entry, special, child = 0x80001000, 0x80003000, 0x80004000
    image = _image(
        {
            entry: [0x0C01DBDC, 0x24040005, 0x03E00008, 0],  # do_special(5)
            special: [0x3C048000, 0x0C01FC05, 0x24844000, 0x03E00008, 0],  # proj_process(child)
            child: [0x03E00008, 0],
        },
        {0x800AB140 + 4 * 5: special},
    )
    first = reading.read(image, entry)
    assert first.calls[0].name == "do_special"
    assert "special 0x5 = 0x80003000" in first.notes[entry]
    assert reading.callees(image, first) == [0x80076F70, special]
    tree = reading.call_tree(image, entry, depth=3)
    assert set(tree) == {entry, special, child}
    assert child in tree[special].code_refs


def test_registry_entries() -> None:
    names = [r.name for r in REGISTRY.values()]
    assert len(names) == len(set(names))
    for va, r in REGISTRY.items():
        assert r.kind in ("engine", "move", "global"), hex(va)
        assert r.effect and r.evidence, hex(va)
        if r.kind != "global":
            assert reading.CODE_START <= va < reading.CODE_END and va % 4 == 0, hex(va)


# Reptile (MKT fighter 19): every own command, with the routines its reading must reach.
REPTILE = {
    0x8004F9A4: {0x80079A5C, 0x80079B0C, 0x80079B68, 0x80079C30, 0x800527D4},  # forceball (fast)
    0x8004F8E4: {0x80079AB4, 0x80079B0C, 0x80079B68, 0x80079C30, 0x800527F8},  # forceball (slow)
    0x8004F904: {0x80079800, 0x80079880, 0x800799C8, 0x80079920},  # acid spit
    0x8004EC20: {0x80073918},  # invisibility
    0x8004F260: {0x8004A294, 0x80052938},  # slide
    0x8004F2C0: {0x800467D0},  # elbow dash
}
SEKTOR = {0x8007BF38, 0x8007BF84, 0x8007BFC8, 0x80048368}


@needs_mkt
def test_reptile_specials_read_completely() -> None:
    mkt = Path(MKT).read_bytes()  # type: ignore[arg-type]
    moves = [m for m in reading.fighter_moves(mkt, 19) if not m.shared]
    assert {m.action for m in moves} == set(REPTILE)
    for m in moves:
        assert REPTILE[m.action] <= set(m.tree), hex(m.action)
        assert m.unknown_calls == [], [(hex(v), hex(c.target or 0)) for v, c in m.unknown_calls]


@needs_mkt
def test_sektor_specials_read_completely() -> None:
    mkt = Path(MKT).read_bytes()  # type: ignore[arg-type]
    moves = [m for m in reading.fighter_moves(mkt, 7) if not m.shared]
    assert {m.action for m in moves} == SEKTOR
    for m in moves:
        assert m.unknown_calls == [], hex(m.action)
