"""Move components, move programs and host readings (Fighter recompiler plan, milestone 2)."""

from __future__ import annotations

import copy
import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import components as cp
from mkmszr.fighter_import import reading
from mkmszr.fighter_import.mipsdis import decode
from mkmszr.fighter_import.mkmsz_registry import MKMSZ

CLEAN = os.environ.get("MKMSZR_CLEAN_ROM")
needs_clean = pytest.mark.skipif(not CLEAN, reason="needs MKMSZR_CLEAN_ROM")


@pytest.mark.parametrize("fighter", ["reptile", "sektor"])
def test_programs_validate_and_list_gaps(fighter: str) -> None:
    moves, gaps = cp.load_programs(fighter)
    assert moves and gaps
    assert cp.components_used(moves) <= set(cp.COMPONENTS)


def test_reptile_has_every_special() -> None:
    moves, _ = cp.load_programs("reptile")
    assert {m.name for m in moves} == {
        "forceball_fast", "forceball_slow", "acid_spit", "invisibility", "slide", "elbow_dash"}  # fmt: skip


def _doc() -> dict:
    return {
        "format": 1,
        "moves": [
            {
                "name": "t",
                "command": {
                    "buttons": "0x10",
                    "tokens": [9, 9],
                    "window": 18,
                    "src": "MKT 0x800AC83C",
                },
                "steps": [
                    {"op": "sleep", "ticks": 8, "src": {"ticks": "MKT 0x80079B34"}},
                    {"op": "end"},
                ],
            }
        ],
    }


def test_validator_accepts_minimal_program() -> None:
    assert [m.name for m in cp.validate_programs(_doc())] == ["t"]


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda d: d["moves"][0]["steps"][0].pop("src"), "missing or malformed src"),
        (lambda d: d["moves"][0]["steps"][0]["src"].update(ticks="MKT 80079B34"), "malformed src"),
        (lambda d: d["moves"][0]["steps"].append({"op": "teleport_magic"}), "unknown component"),
        (lambda d: d["moves"][0]["steps"][0].update(speed=3), "unknown parameter speed"),
        (lambda d: d["moves"][0]["steps"][0].update(ticks="soon"), "expected an integer"),
        (lambda d: d["moves"][0]["command"].pop("src"), "command needs src"),
        (
            lambda d: d["moves"][0]["command"].update(conditions=[{"kind": "moon_phase"}]),
            "unknown condition",
        ),
    ],
)
def test_validator_rejects(edit, message: str) -> None:  # type: ignore[no-untyped-def]
    doc = copy.deepcopy(_doc())
    edit(doc)
    with pytest.raises(cp.ProgramError, match=message):
        cp.validate_programs(doc)


def test_strike_reaction_must_be_a_known_meaning() -> None:
    moves, _ = cp.load_programs("reptile")
    raw = copy.deepcopy(
        {
            "format": 1,
            "moves": [{"name": m.name, "command": m.command, "steps": m.steps} for m in moves],
        }
    )
    projectile = next(s for s in raw["moves"][0]["steps"] if s["op"] == "projectile")
    projectile["strike"]["reaction"] = "explode_into_confetti"
    with pytest.raises(cp.ProgramError, match="unknown reaction"):
        cp.validate_programs(raw)


# -- host (MKMSZ) readings --------------------------------------------------------------------

HOST_ROUTINES = (0x800498A8, 0x80049668, 0x80047160, 0x80046F74, 0x80072584, 0x80072644)


@needs_clean
def test_host_reference_routines_read_completely() -> None:
    rom = Path(CLEAN).read_bytes()  # type: ignore[arg-type]
    for va in HOST_ROUTINES:
        r = reading.read(rom, va, engine=MKMSZ)
        assert r.unknown_calls == [], (hex(va), [hex(c.target or 0) for c in r.unknown_calls])
    proj = reading.read(rom, 0x80049668, engine=MKMSZ)
    names = [c.name for c in proj.calls]
    assert {
        "projectile_build",
        "projectile_collision_dispatch",
        "actor_offscreen",
        "process_exit",
    } <= set(names)


@needs_clean
def test_player_entry_of_the_type_file_table() -> None:
    """Type 4 (player) has no fighter-file entry, and projectile_actor_build is the table's only
    reader: the generic projectile's guarded edit (milestone 2 backend) rests on this."""

    rom = Path(CLEAN).read_bytes()  # type: ignore[arg-type]
    table = 0x800A0324
    assert MKMSZ.word(rom, table + 4 * 4) == 0
    hi, lo = (table + 0x8000) >> 16, table & 0xFFFF
    readers = []
    for va in range(0x80000400, 0x800A0000, 4):
        ins = decode(MKMSZ.word(rom, va), va)
        if ins.op == "lui" and ins.imm == hi:
            for k in range(1, 16):
                nxt = decode(MKMSZ.word(rom, va + 4 * k), va + 4 * k)
                if nxt.rs == ins.rt and (nxt.imm & 0xFFFF) == lo and nxt.op in ("addiu", "lw"):
                    readers.append(nxt.pc)
                    break
    assert readers == [0x80046FCC]
