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


def test_invisibility_stealth_and_timer() -> None:
    moves, _ = components.load_programs("reptile")
    inv = next(m for m in moves if m.name == "invisibility")
    a = Assembler(BASE, cached_calls=True)
    ls.emit_gate_condition(a, "cond", ls.GATES["freeze_on_contact"], ls.COSTS["freeze_on_contact"],
                           refuse_if=(ls.CTRL_STEALTH, ls.STEALTH_BIT))  # fmt: skip
    ls.emit_action(a, "root", inv.steps, cost=0x80, animations={(1, 1): ("at", 0x100)}, face=False,
                   donor_ticks=2, sounds={9: 175}, stealth="timer", skip=frozenset({"effect"}))  # fmt: skip
    a.label("play")
    ls.emit_stealth_timer(a, "timer", 3, 1)
    code = a.link()
    text = " ".join(_text(code))
    assert "andi t4, t4, 0x1000" in text  # refused while already stealthed
    assert "addiu a0, zero, 175" in text
    assert "lhu t0, 1622(a0)" in text and "slti t1, t0, 1" in text  # Ice drained each period
    assert "addiu t9, t9, 9604" in text  # 0x80072584, the Eye's effect
    assert "andi t1, t1, 0xFFFE" in text  # the Inventory's timer request is cleared
    # The generation word follows jr ra and its delay slot, so it is never executed.
    gen = a.labels["timer_gen"] - BASE
    assert code[gen - 8 : gen] == bytes.fromhex("03e0000800000000")
    with pytest.raises(ValueError, match="not ported"):
        ls.emit_action(Assembler(BASE), "x", inv.steps, cost=0, animations={(1, 1): ("at", 0)},
                       sounds={9: 175}, stealth="timer")  # fmt: skip


@pytest.mark.skipif(not os.environ.get("MKMSZR_MKT_ROM"), reason="needs MKMSZR_MKT_ROM")
def test_invisibility_fire_effect() -> None:
    from mkmszr.fighter_import import effects

    mkt = Path(os.environ["MKMSZR_MKT_ROM"]).read_bytes()
    fire = effects.mkt_animation_art(mkt, 0x800CC77C, 0x800CCA88)
    assert len(fire.frames) == 9 and fire.slot_size == (100, 137) and len(fire.palette) == 32
    moves, _ = components.load_programs("reptile")
    inv = next(m for m in moves if m.name == "invisibility")
    a = Assembler(BASE, cached_calls=True)
    ls.emit_action(a, "root", inv.steps, cost=0x40, animations={(1, 1): ("at", 0x100)}, face=False,
                   donor_ticks=2, sounds={9: 175}, stealth="timer", effects={30: ("fx_fire", 0)})  # fmt: skip
    for name in ("play", "timer", "timer_gen", "timer_undo", "fx_fire", "fx_spawn_xy"):
        a.label(name)
    text = " ".join(_text(a.link()))
    assert "ori a3, a3, 0xFFFF" in text  # drawn in front (sub-layer 0xFFFF)
    assert "addiu t1, t1, -64" in text  # Ice 0x40 (owner: half of Freeze on Contact's)


def test_airborne_gate_skips_the_floor_checks() -> None:
    # Rayden's torpedo (owner): it may start in the air.
    from mkmszr.fighter_import.mips import Assembler

    def words(airborne: bool) -> list[int]:
        a = Assembler(0xA01AF420)
        ls.emit_gate_condition(a, "g", ls.GATES["ice_clone"], 0x60, airborne=airborne)
        return a.link()

    grounded, air = words(False), words(True)
    assert len(air) < len(grounded)
    ground_check = 0x8D6E06B4  # lw t6, 0x6B4(t3): the floor read
    assert ground_check in [int.from_bytes(grounded[i:i + 4], "big") for i in range(0, len(grounded), 4)]
    assert ground_check not in [int.from_bytes(air[i:i + 4], "big") for i in range(0, len(air), 4)]


def test_hover_and_jump_ops_lower() -> None:
    from mkmszr.fighter_import.mips import Assembler

    a = Assembler(0xA01AF420, cached_calls=True)
    steps = [{"op": "hover"}, {"op": "jump", "x": "0", "y": "0xD999", "gravity": "0x6CCC", "until": "landing"},
             {"op": "end"}]  # fmt: skip
    ls.emit_action(a, "t", steps, cost=0, animations={})
    code = a.link()
    ws = [int.from_bytes(code[i:i + 4], "big") for i in range(0, len(code), 4)]
    assert 0x3C198003 in ws and 0x273921D0 in ws  # lui/addiu t9 -> 0x800321D0
    # sw zero, 0x70C(s0) before the call: the stock jump calls a non-zero +0x70C every air tick
    # (Rayden specials proof v02 hang); every stock caller clears it.
    call = ws.index(0x273921D0)
    assert ws.index(0xAE00070C) < call


def test_air_control_installs_the_air_map_before_the_jump() -> None:
    from mkmszr.fighter_import.mips import Assembler

    steps = [{"op": "jump", "x": "0", "y": "0xD999", "gravity": "0x6CCC", "until": "landing"}, {"op": "end"}]
    words = {}
    for flag in (False, True):
        a = Assembler(0xA01AF420, cached_calls=True)
        ls.emit_action(a, "t", steps, cost=0, animations={}, air_control=flag)
        code = a.link()
        words[flag] = [int.from_bytes(code[i:i + 4], "big") for i in range(0, len(code), 4)]
    input_map = 0x2739B05C  # addiu t9, t9, lo(0x8002B05C)
    jump = 0x273921D0
    assert input_map not in words[False]
    w = words[True]
    assert input_map in w and w.index(input_map) < w.index(jump)
    assert 0x3405FA00 in w or 0x34A5FA00 in w  # ori a1, lo(0x8009FA00): the straight-air map


def test_carry_op_and_reaction_share_the_word() -> None:
    from mkmszr.fighter_import.mips import Assembler

    a = Assembler(0xA01AF420, cached_calls=True)
    steps = [{"op": "carry", "ticks": 32, "every_tick": [{"op": "hover"}]}, {"op": "end"}]
    ls.emit_action(a, "t", steps, cost=0, animations={}, donor_ticks=2, carry="word")
    ls.emit_carry_reaction(a, "carry", "word", "release", (0x800572C4, 0x80057478))
    a.label("release")
    a.jr_ra()
    a.nop()
    a.label("word")
    a.raw(0)
    code = a.link()
    ws = [int.from_bytes(code[i:i + 4], "big") for i in range(0, len(code), 4)]
    word = a.labels["word"]
    la = [i for i, w in enumerate(ws) if w == (0x3C080000 | word >> 16)
          and ws[i + 1] == (0x35080000 | word & 0xFFFF)]  # fmt: skip
    assert len(la) >= 5  # set, test and clear (attacker); test and clear (victim)
    assert 0x24130010 in ws  # 32 donor ticks at 2 per host tick
    reaction = (a.labels["carry"] - a.base) // 4
    assert 0x24050000 | ls.CARRY_ROOT in ws[reaction:]  # root 0x1E selected for the pose
    j = 0x08000000 | (a.labels["release"] >> 2) & 0x03FFFFFF
    assert j in ws[reaction:]  # tail call into the throw
    # MKT (v09, owner: pure MKT): the contact distance (victim x - player x, kept) and the
    # victim's own height, held: no gravity or y speed, the previous y moved too
    held = ws[reaction:]
    assert 0x01499023 in held  # subu s2, t2, t1: the contact distance
    assert 0x8E290030 in held  # lw t1, +0x30(s1): its own y
    for sw in (0xAE290030, 0xAE29003C, 0xAE200010, 0xAE200018):  # y, previous y, gravity, y speed
        assert sw in held
    assert 0xA6090000 | 0x6B2 in held  # sh t1, +0x6B2(s0): the airborne counter
    # counted every tick, not only above the floor (v04: a ground carry fell at a ledge)
    assert 0x8E0906B4 not in held  # lw t1, +0x6B4(s0): no floor comparison


def test_carry_grab_point_is_an_owner_option() -> None:
    """The v04-v08 grab point (72 px ahead at the player's y) stays available as tuning."""

    a = Assembler(0xA01AF420, cached_calls=True)
    ls.emit_carry_reaction(a, "carry", "word", "release", (), dx_px=72, dy_px=0)
    a.label("release")
    a.label("word")
    a.raw(0)
    code = a.link()
    ws = [int.from_bytes(code[i:i + 4], "big") for i in range(0, len(code), 4)]
    assert 0x34129000 in ws or 0x36529000 in ws  # ori s2, 0x9000: 72 px = 144 units << 8
    assert 0x01499023 not in ws


def test_shake_screen_runs_mkt_algorithm_on_the_camera_offset() -> None:
    a = Assembler(0xA01AF420, cached_calls=True)
    steps = [{"op": "shake_screen", "amplitude": 6, "count": 6, "ticks": 3}, {"op": "end"}]
    ls.emit_action(a, "t", steps, cost=0, animations={}, donor_ticks=2)
    code = a.link()
    ws = [int.from_bytes(code[i:i + 4], "big") for i in range(0, len(code), 4)]
    assert 0x24040015 in ws  # the process id of the host's shakes
    shaker = next(v for k, v in a.labels.items() if "shaker" in k and not k.endswith("_step"))
    tail = ws[(shaker - a.base) // 4 :]
    assert tail[:2] == [0x24100006, 0x2411000C]  # 6 steps of 6 px (12 world units)
    assert 0x24040002 in tail  # 3 donor ticks at 2 per host tick
    assert 0xAD00A928 in tail or 0xAD00A928 - 0x10000 in tail or any(
        (w & 0xFFFF) == 0xA928 and (w >> 26) == 0x2B and (w >> 16) & 0x1F == 0 for w in tail)  # fmt: skip


def test_jump_rate_animates_the_selection() -> None:
    a = Assembler(0xA01AF420, cached_calls=True)
    steps = [{"op": "jump", "x": "0x33333", "y": "-0x6CCCC", "gravity": "0x5199", "until": "landing",
              "rate": 3}, {"op": "end"}]  # fmt: skip
    ls.emit_action(a, "t", steps, cost=0, animations={}, donor_ticks=2)
    code = a.link()
    ws = [int.from_bytes(code[i:i + 4], "big") for i in range(0, len(code), 4)]
    assert 0x24080002 in ws and 0x2408000D not in ws  # rate 2, not "keep" (13)


def test_movement_moves_are_marked() -> None:
    moves = {m.name: m for m in components.load_programs("rayden")[0]}
    assert moves["torpedo"].movement and not moves["lightning"].movement
    assert {m.name for m in components.load_programs("reptile")[0] if m.movement} == {"elbow_dash"}
    with pytest.raises(components.ProgramError, match="movement"):
        components.validate_programs({"format": 1, "moves": [
            {"name": "x", "movement": "yes", "command": {"buttons": 0, "tokens": [], "window": 1,
             "src": "owner"}, "steps": [{"op": "end"}]}]})  # fmt: skip


def test_carry_step_needs_its_word() -> None:
    from mkmszr.fighter_import.mips import Assembler

    with pytest.raises(ValueError, match="carry word"):
        ls.emit_action(Assembler(0xA01AF420), "t", [{"op": "carry", "ticks": 4}], cost=0, animations={})
