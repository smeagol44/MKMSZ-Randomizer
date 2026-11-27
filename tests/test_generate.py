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


@needs_mkt
def test_the_grab_rule_reads_the_shocker(mkt: bytes) -> None:
    """HP release (quick special 0x1D -> 0x80073228), SMRE step 2: grab_refused, then |dx| < 0x37
    with the opponent settled, else the miss routine; the hit path damages (0x20), holds and
    releases the opponent (0x800734CC: shock_hold). One unblockable one-tick strike reaching 55 px,
    the hit path as on_hit, the miss after it; nothing unknown."""

    g = gen.Generator(mkt, 24).move(0x8004EBA0)
    assert g.unknown == [] and g.grab
    strike = next(s for s in g.steps if s["op"] == "strike")
    assert strike["strike"] == {"box": [0x37, 0, 0x37, gen.GRAB_BOX_HEIGHT], "damage": 0x20, "block_damage": 0,
                                "reaction": "shock_hold", "blocked_reaction": "blocked", "unblockable": True}  # fmt: skip
    assert strike["ticks"] == 1 and strike["only_if"] == "opponent_settled"
    assert [s["op"] for s in strike["on_hit"]] == ["sound", "pose", "sleep", "repeat", "end"]
    shocks = strike["on_hit"][3]
    assert shocks["count"] == 8 and [s["op"] for s in shocks["steps"]] == ["next_frame", "sleep"] * 4
    after = [s["op"] for s in g.steps[g.steps.index(strike) + 1 :]]
    assert after == ["pose", "repeat", "sleep", "pose", "end"]  # MKT's miss: 15 frames at 3 ticks


# ---- SMRE: whole programs from the command records (2026-11-27) ---------------------------------
@needs_mkt
@pytest.mark.parametrize("fighter", ["rayden", "reptile"])
def test_smre_writes_the_stored_programs_exactly(mkt: bytes, fighter: str) -> None:
    """Every move the fighter description lists under ``smre`` is written by the Special Move
    Recompile Engine from its MKT command record (command block, conditions, steps, provenance,
    the movement flag); the stored program is exactly that output, kept as the reference."""

    from mkmszr.fighter_import import description as fd

    d = fd.load(fighter)
    doc = json.loads(resources.files("mkmszr.fighters.moves").joinpath(f"{fighter}.json").read_text("utf-8"))
    stored = {m["name"]: m for m in doc["moves"]}
    g = gen.Generator(mkt, d.donor_fighter_id)
    for move, record in d.smre.items():
        prog, _, _ = g.program(move, record)
        if stored[move].get("grab"):
            prog["grab"] = True
        assert prog == stored[move], move


@needs_mkt
def test_smre_reads_commands_and_conditions(mkt: bytes) -> None:
    """Buttons come from the input events that hold the record (Reptile's forceball sits in the
    High Punch and Low Punch tables: 0x90; Rayden's Lightning record has masks 0xFC but sits only
    in Low Punch: 0x80); the release grid gives ``release``; ``ticks_since`` on the High Punch
    press stamp is ``held_for``, on any other stamp a ``cooldown``; guards the build does not
    lower are notes, not conditions."""

    ray, rep = gen.Generator(mkt, 24), gen.Generator(mkt, 19)
    cmd, _ = ray.command(0x800ABA54)
    assert (cmd["buttons"], cmd["tokens"], cmd["window"]) == ("0x80", [9, 7], 16)
    cmd, notes = ray.command(0x800AB9F4)  # the Shocker
    assert cmd["release"] is True and cmd["conditions"] == [{"kind": "held_for", "ticks": 0x38, "src": "MKT 0x80051008"}]
    assert any("opponent's action" in n for n in notes)
    cmd, _ = ray.command(0x800AB968)  # the teleport
    assert cmd["buttons"] == "stick" and cmd["conditions"][0]["kind"] == "cooldown" and cmd["conditions"][0]["ticks"] == 0x40
    cmd, notes = rep.command(0x800AC810)  # the fast forceball, through forceball_cooldown(0x80156BA0)
    assert cmd["buttons"] == "0x90"
    assert [(c["kind"], c.get("key") or c.get("mask")) for c in cmd["conditions"]] == [("cooldown", "0x80156BA0"), ("buttons_held", "0x90")]
    assert len(notes) == 2  # the opponent's fighter id and reaction state
    with pytest.raises(ValueError, match="not one of fighter"):
        ray.command(0x800AC810)


@needs_mkt
def test_smre_reads_inline_commands(mkt: bytes) -> None:
    """Sektor's specials are inline matcher calls in imperative handlers (SMRE step 3): buttons
    from the handler's event within the matcher's mask, tokens and window from the compact
    table, and the guards between the matcher and the transfer: ``process_exist`` on his
    projectile process (0x705/0x805) is ``projectiles_below`` 1; the Homing Missile's count of
    processes 0x704/0x804 (< 3) and the teleport's opponent guards are notes. The action is the
    transfer's wrapper (Sektor's teleport uppercut: ``do_body_propell(8)``)."""

    sek = gen.Generator(mkt, 7)
    cmd, notes = sek.command(0x800AB250)  # straight missile, F,F + LP
    assert cmd == {"buttons": "0x80", "tokens": [9, 9], "window": 32, "src": "MKT 0x800AB250",
                   "conditions": [{"kind": "projectiles_below", "count": 1, "src": "MKT 0x8004E73C"}]}  # fmt: skip
    assert notes == []
    cmd, notes = sek.command(0x800AB26C)  # double missile, B,B,F + LP
    assert (cmd["tokens"], cmd["conditions"][0]["kind"]) == ([9, 8, 8], "projectiles_below")
    cmd, notes = sek.command(0x800AB288)  # homing missile, F,D,B + HP
    assert (cmd["buttons"], cmd["tokens"], cmd["window"], "conditions" in cmd) == ("0x10", [8, 7, 9], 22, False)
    assert notes == ["0x8004E7EC: fewer than 3 live processes with ids 0x704, 0x804 (not lowered)"]
    cmd, notes = sek.command(0x800AB2C0)  # teleport uppercut, F,F + LK
    assert (cmd["buttons"], cmd["tokens"], cmd["window"]) == ("0x40", [9, 9], 24) and len(notes) == 2
    prog, _, _ = sek.program("teleport_uppercut", 0x800AB2C0)
    assert prog["steps"][0]["action_mkt"] == "0x208" and prog["steps"][1]["sound"] == {"fighter": 7}


@needs_mkt
def test_smre_reads_the_teleport_uppercut(mkt: bytes) -> None:
    """Sektor's teleport uppercut (F,F + LK -> do_body_propell(8) -> 0x80048368), nothing unknown:
    the last frame of slot 0x0D; a sink (y 0x5F333, gravity 0x9599) until past the screen's
    bottom line; behind the opponent (dx 12, MKT's velocity lead noted); the rise (table 1 slot 3
    at rate 5; y -0x7A666, gravity -0x5199) to the floor, striking within 41 px of it; the flight
    on from that velocity (gravity 0xF000, 0xB000 after a hit), striking while rising; the
    landing (slot 0x16 from its second frame, 3 ticks a frame)."""

    prog, g, _ = gen.Generator(mkt, 7).program("teleport_uppercut", 0x800AB2C0)
    assert g.unknown == [] and prog["movement"]
    steps = [{k: v for k, v in s.items() if k != "src"} for s in prog["steps"]]
    strike = {"box": [73, -9, 73, 87], "damage": 16, "block_damage": 2, "reaction": "uppercut",
              "blocked_reaction": "blocked"}  # fmt: skip
    assert steps == [
        {"op": "begin", "face": True, "stop": True, "action_mkt": "0x208"},
        {"op": "sound", "sound": {"fighter": 7}},
        {"op": "pose", "anim": {"table": 0, "slot": 13, "offset": 5}},
        {"op": "jump", "x": "0x0", "y": "0x5f333", "gravity": "0x9599", "until": "below_screen"},
        {"op": "relocate", "to": "behind_opponent", "dx": 12},
        {"op": "face"},
        {"op": "animate", "anim": {"table": 1, "slot": 3}, "rate": 5, "until": "running"},
        {"op": "jump", "x": "0x0", "y": "-0x7a666", "gravity": "-0x5199", "until": "surface",
         "strike": strike, "strike_near_px": 41},
        {"op": "jump", "x": "0x0", "gravity": "0xf000", "until": "landing", "gravity_on_hit": "0xb000",
         "strike": strike, "strike_while": "rising"},
        {"op": "pose", "anim": {"table": 0, "slot": 22, "offset": 1}},
        {"op": "sleep", "ticks": 3}, {"op": "next_frame"}, {"op": "sleep", "ticks": 3}, {"op": "end"},
    ]  # fmt: skip
