"""Move-program generator (fighter_import.decompile / generate): owner decision 2026-11-25.

The accepted hand-written programs are the expected outputs. A move the generator reproduces is
pinned as identical; for the others the remaining difference is pinned, so every change to it is
deliberate (a new rule, or a decided MKT-vs-accepted difference)."""

from __future__ import annotations

import json
import os
from importlib import resources
from pathlib import Path

import pytest

from mkmszr.fighter_import import decompile as dc
from mkmszr.fighter_import import generate as gen

MKT = os.environ.get("MKMSZR_MKT_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")


@pytest.fixture(scope="module")
def mkt() -> bytes:
    return Path(MKT).read_bytes()


def accepted(fighter: str, move: str) -> list[dict]:
    doc = json.loads(resources.files("mkmszr.fighters.moves").joinpath(f"{fighter}.json").read_text("utf-8"))
    return next(m for m in doc["moves"] if m["name"] == move)["steps"]


def changed(diff: list[str]) -> list[str]:
    return [line for line in diff[2:] if line[:1] in "+-"]


@needs_mkt
def test_decompile_structures_the_torpedo(mkt: bytes) -> None:
    stmts = dc.decompile(mkt, 0x800450D4)
    loops = [s for s in stmts if s.kind == "loop"]
    assert len(loops) == 1
    window = loops[0]
    assert "proc+0x444" in str(window.cond)  # counted down from 0x1A
    calls = [s.target for s in window.body if s.kind == "call"]
    assert calls[:2] == [0x8005A88C, 0x8003E620]  # sleep 1, strike_check_a0
    hit = next(s for s in window.body if s.kind == "if")
    assert [s.target for s in hit.then if s.kind == "call"] == [0x800452C4]  # the carry


@needs_mkt
def test_decompile_folds_a_known_argument(mkt: bytes) -> None:
    """Rayden's lightning routine serves both commands: argument 0 (D,F) and 1 (D,B)."""

    for arg, action in ((0, 0x2B), (1, 0x31)):
        stmts = dc.decompile(mkt, 0x80077DF8, (arg,))
        first = stmts[0]
        assert first.kind == "if" and first.cond.const() == arg
        branch = first.then if arg else first.other
        assert branch[0].kind == "call" and branch[0].args[1].const() == action


@needs_mkt
@pytest.mark.parametrize(
    ("fighter", "fid", "move", "entry", "args"),
    [("reptile", 19, "elbow_dash", 0x800467D0, ()),
     ("reptile", 19, "acid_spit", 0x8004F904, ()),  # its command's entry (do_special 0x23)
     # the speed reaches the process through the parent's +0x440; the hum is its flight
     # callback; the owner's spawn offset is in the description since generator step 4
     ("reptile", 19, "forceball_fast", 0x8004F9A4, ()),
     ("reptile", 19, "forceball_slow", 0x8004F8E4, ()),
     # MKT's flag 0x20 has no timer: the stealth length is the description's (step 4)
     ("reptile", 19, "invisibility", 0x80073918, ()),
     # generator step 5: the first program written by the generator, not by hand (2026-11-26)
     ("rayden", 24, "reversed_lightning", 0x8004FA64, ()),
     ("rayden", 24, "teleport", 0x8004F3F8, ())],
)
def test_generated_equals_accepted(mkt: bytes, fighter: str, fid: int, move: str, entry: int, args: tuple) -> None:
    g = gen.Generator(mkt, fid).move(entry, args)
    assert gen.compare(g.steps, accepted(fighter, move)) == []
    assert g.unknown == []


def projectile_of(steps: list[dict]) -> dict:
    return next(s for s in steps if s["op"] == "projectile")


@needs_mkt
def test_lightning_equals_the_accepted_program(mkt: bytes) -> None:
    """Projectile rules (generator step 3): the bolt process folds on the lightning's argument
    (0 for D,F, handed to the child in +0x440); MKT checks close range with strike 0x10 twice
    before the flight (0x80078230); the owner had them added (2026-11-26, specials proof v19)."""

    g = gen.Generator(mkt, 24).move(0x8004FA44)  # the command's own entry (do_special 0x2E)
    made = projectile_of(g.steps)
    assert made["checks"] == [{"box": [101, 36, 64, 16], "after": 1}, {"box": [101, 36, 64, 16], "after": 2}]
    assert gen.compare(g.steps, accepted("rayden", "lightning")) == []  # owner: add them (specials v19)
    assert g.unknown == []




@needs_mkt
def test_torpedo_equals_the_accepted_program(mkt: bytes) -> None:
    """The owner switched the torpedo to MKT's version (2026-11-25): a random start sound 10-12,
    the speed from the lean, and Rayden's bounce back after the carry or a block. The victim's
    positioning routines that MKT also runs stay unknown (the host victim reaction plays them)."""

    g = gen.Generator(mkt, 24).move(0x8004F3A0)
    assert gen.compare(g.steps, accepted("rayden", "torpedo")) == []
    assert all(u.split(":")[0] in ("0x800453B4", "0x800453DC", "0x8004552C") for u in g.unknown)


def test_canonical_ignores_provenance_and_number_spelling() -> None:
    a = [{"op": "sleep", "ticks": 36, "src": {"ticks": "MKT 0x80077F08"}}]
    b = [{"op": "sleep", "ticks": "0x24"}]
    assert gen.compare(a, b) == []


@needs_mkt
def test_a_known_process_field_folds_the_bolt(mkt: bytes) -> None:
    """The decompiler takes known process fields: Rayden's bolt with +0x442 = 0 (D,F) uses strike
    0x11 and checks 0x10; with 1 (D,B), 0x13 and 0x12."""

    for flag, strike, check in ((0, 0x11, 0x10), (1, 0x13, 0x12)):
        stmts = dc.decompile(mkt, 0x80077F2C, (), {(0x442, 2): flag})
        calls = [s for s in stmts if s.kind == "call"]
        assert calls[0].args[0].const() == strike  # proj_set_strike
        assert [c.args[0].const() for c in calls if c.target == 0x80078230] == [check, check]


@needs_mkt
def test_reversed_lightning_reads_the_wrap_and_the_turn(mkt: bytes) -> None:
    """D,B + LP (0x80077DF8(1)): MKT turns Rayden around (flip_single), the bolt's flight
    callback 0x80078070 wraps it once at the screen edge (10 ticks), its strikes use reaction
    0x81 (pushed towards the attacker), and he faces the opponent at the end."""

    g = gen.Generator(mkt, 24).move(0x8004FA64)
    ops = [s["op"] for s in g.steps]
    assert ops == ["begin", "flip", "sound", "animate", "projectile", "sleep", "face", "end"]
    made = projectile_of(g.steps)
    assert made["wrap"] == {"cooldown": 10}
    assert made["strike"]["reaction"] == "shock_stagger_toward"
    assert all(s.get("src") for s in g.steps if len(s) > 1)  # provenance on every parameter


@needs_mkt
def test_teleport_reads_the_afterimage_and_the_relocation(mkt: bytes) -> None:
    """D,U (propell 0x1D -> 0x80045624): a copy of Rayden playing table-1 slot 1 stays behind
    (new_object + a process animating it), he is placed 67 px by the opponent (the side chosen by
    the arena edges: the decompiler keeps both constants, -0x43 | 0x43), faces him and plays his
    reappear (slot 0x22); Rayden's own branch of 0x80053AE8 folds by the fighter id."""

    g = gen.Generator(mkt, 24).move(0x8004F3F8)
    ops = [s["op"] for s in g.steps]
    assert ops == ["begin", "stamp", "sound", "afterimage", "relocate", "face", "sound", "animate",
                   "pose", "sleep", "end"]  # fmt: skip
    assert g.steps[3]["anim"] == {"table": 1, "slot": 1} and g.steps[3]["rate"] == 2
    assert g.steps[4]["dx"] == 67 and g.steps[6]["sound"] == {"fighter": 7}
    assert g.unknown == []
