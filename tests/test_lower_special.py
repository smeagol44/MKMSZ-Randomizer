"""Special-move actions and conditions (fighter_import.lower_special), milestone 4 step 3."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import components
from mkmszr.fighter_import import lower_special as ls
from mkmszr.fighter_import.mips import Assembler
from mkmszr.fighter_import.mipsdis import decode

CLEAN = os.environ.get("MKMSZR_CLEAN_ROM")
needs_clean = pytest.mark.skipif(not CLEAN, reason="needs MKMSZR_CLEAN_ROM")
BASE = 0xA01AF520


def _text(code: bytes) -> list[str]:
    return [decode(int.from_bytes(code[i : i + 4], "big"), BASE + i).text for i in range(0, len(code), 4)]


@needs_clean
def test_gates_are_stock_tier_compares() -> None:
    clean = Path(CLEAN).read_bytes()
    for name, va in ls.GATES.items():
        word = int.from_bytes(clean[va - 0x7FFFF400 : va - 0x7FFFF400 + 4], "big")
        assert word >> 16 == 0x2842, name  # slti v0, v0, N
        prev = int.from_bytes(clean[va - 0x7FFFF400 - 8 : va - 0x7FFFF400 - 4], "big")
        assert prev == 0x0C01D3EF, name  # jal 0x80074FBC (tier evaluator)


def test_condition_reads_the_gate_and_checks_the_cost() -> None:
    a = Assembler(BASE, cached_calls=True)
    ls.emit_gate_condition(a, "cond", ls.GATES["ice_clone"], ls.COSTS["ice_clone"])
    text = " ".join(_text(a.link()))
    assert "lh t0, -23894(t0)" in text  # 0x8004A2AA: the gate's immediate, read at run time
    assert "slti t4, t4, 96" in text and "addiu a0, zero, 1792" in text  # Ice 0x60, class 0x700


def test_forceball_action_follows_the_move_program() -> None:
    moves, _ = components.load_programs("reptile")
    (fast,) = [m for m in moves if m.name == "forceball_fast"]
    a = Assembler(BASE, cached_calls=True)
    ls.emit_action(a, "root", fast.steps, cost=0x60, animations={(1, 5): 0x25}, child="ball")
    a.label("ball")
    text = _text(a.link())
    calls = [t for t in text if t.startswith("addiu t9, t9")]
    joined = " ".join(text)
    assert "addiu a1, zero, 37" in joined and "addiu t1, t1, -96" in joined  # S25, Ice 0x60
    assert len(calls) >= 5  # special begin, select, phase end, spawn, sleeps, phase end, exit
    with pytest.raises(ValueError):
        ls.emit_action(Assembler(BASE), "x", fast.steps, cost=0, animations={}, child="ball")


def test_per_move_limit_checks_only_its_own_words() -> None:
    a = Assembler(BASE, cached_calls=True)
    ls.emit_gate_condition(a, "cond", ls.GATES["ice_clone"], ls.COSTS["ice_clone"], alive=("mine", "acid"))
    a.label("mine")
    a.raw(0)
    a.label("acid")
    a.raw(0)
    code = a.link()
    text = _text(code)
    words = {a.labels["mine"], a.labels["acid"]}
    stores = [t for t in text if t.startswith("sw zero, 0(t0)")]
    assert len(stores) == 2  # stale words cleared when no projectile process is left
    loads = [i for i, t in enumerate(text) if t.startswith("lui t0") and text[i + 1].startswith("ori t0")]
    pointed = {(int(text[i].split(", ")[1], 0) << 16) | int(text[i + 1].split(", ")[2], 0) for i in loads}
    assert words <= pointed
    free = a.labels["cond_free"]
    find = next(i for i, t in enumerate(text) if t.startswith("addiu a0, zero, 1792"))
    assert BASE + 4 * find < free  # the class scan runs only when a word is set


def test_begin_without_turning() -> None:
    moves, _ = components.load_programs("reptile")
    acid = next(m for m in moves if m.name == "acid_spit")
    texts = {}
    for face in (True, False):
        a = Assembler(BASE, cached_calls=False)
        ls.emit_action(a, "root", acid.steps, cost=0x20, animations={(1, 6): ("at", 0x100)},
                       child="ball", sounds={8: 1}, face=face)  # fmt: skip
        a.label("ball")
        a.label("play")
        texts[face] = " ".join(_text(a.link()))
    on, off = texts[True].lower(), texts[False].lower()  # jal targets print in the KSEG1 segment
    assert "0049f90" in on and "0049f90" not in off  # stock special begin (it faces)
    assert "002b74c" in off and "002b05c" in off and "0031ef0" not in off  # its steps, no face


def test_elbow_dash_lowering() -> None:
    from mkmszr.fighter_import import lower_projectile as lp
    from mkmszr.fighter_import import physics

    moves, _ = components.load_programs("reptile")
    elbow = next(m for m in moves if m.name == "elbow_dash")
    a = Assembler(BASE, cached_calls=True)
    records = ls.emit_action(
        a, "root", elbow.steps, cost=0, animations={(0, 0x4A): ("at", 0xEE8), (1, 0x0B): ("at", 0x5000)},
        face=False, donor_ticks=2, reactions={"elbow_hold": 0x4C},
        speed=lambda v: physics.fold_donor_speeds(v, v, lambda d: d, lp.UNITS_PER_PX)[0],
    )
    ls.emit_hold_reaction(a, "hold", 2)
    ls.emit_strike_data(a, records, BASE)
    text = " ".join(_text(a.link()))
    # Two strikes: the hold (reaction 0x4C, no damage) and the return hit (roundhouse 0x0C, 13/3).
    assert [r[8:12].hex() for _, r in records] == ["4c050000", "0c050d03"]  # launch: roundhouse 0x0C
    assert all(a.labels[name] % 16 == BASE % 16 for name, _ in records)
    assert "lui a1, 0xD" in text and "ori a1, a1, 0xDDDD" in text  # MKT 0xA6666 -> host 0xDDDDD
    assert "addiu s3, zero, 8" in text and "addiu s3, zero, 10" in text  # windows: MKT 16 and 20
    assert "addiu s4, zero, 7" in text  # pass-through dash: MKT 14 ticks
    assert "0049f90" not in text.lower()  # no turning at the start
    assert "addiu s2, zero, 10" in text  # the hold: MKT 20 ticks
    assert "andi t0, t0, 0xEFFF" in text and "ori t0, t0, 0x1000" in text  # pass-through bit
    assert "addiu a1, zero, 28" not in text  # the hold keeps the victim's frame (no hit pose)
    with pytest.raises(ValueError, match="reaction"):
        ls.emit_action(Assembler(BASE), "x", elbow.steps, cost=0,
                       animations={(0, 0x4A): ("at", 0), (1, 0x0B): ("at", 0)}, speed=lambda v: v)  # fmt: skip


@pytest.mark.skipif(not os.environ.get("MKMSZR_MKT_ROM"), reason="needs MKMSZR_MKT_ROM")
def test_footsteps_follow_the_donor_run() -> None:
    from mkmszr.fighter_import.body_build import Donor

    mkt = Path(os.environ["MKMSZR_MKT_ROM"]).read_bytes()
    assert ls.donor_footsteps(Donor(mkt, 19), 0x4A) == (9, (3, 7))  # callback 8 before frames 3, 7
    moves, _ = components.load_programs("reptile")
    elbow = next(m for m in moves if m.name == "elbow_dash")
    a = Assembler(BASE, cached_calls=True)
    records = ls.emit_action(
        a, "root", elbow.steps, cost=0, animations={(0, 0x4A): ("at", 0xEE8), (1, 0x0B): ("at", 0)},
        donor_ticks=2, reactions={"elbow_hold": 0x4C}, speed=lambda v: v,
        footsteps={(0, 0x4A): ls.Footsteps(9, (3, 7), (459, 478))},
    )
    a.label("play")
    ls.emit_strike_data(a, records, BASE)
    text = " ".join(_text(a.link()))
    assert "addiu a0, zero, 459" in text and "addiu a0, zero, 478" in text
    assert "slti t0, s6, 9" in text
    hold = Assembler(BASE, cached_calls=True)
    ls.emit_hold_reaction(hold, "hold", 2)
    calls = " ".join(_text(hold.link()))
    assert "addiu t9, t9, 1220" not in calls  # no stock hit effect 0x800504C4 (v17)
    assert "addiu t9, t9, 22180" in calls  # 0x800556A4 stays
