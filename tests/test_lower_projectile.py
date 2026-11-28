"""Backend v1: the generic projectile lowering (Fighter recompiler plan, milestone 2)."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import components
from mkmszr.fighter_import import lower_projectile as lp
from mkmszr.fighter_import.body_build import Donor
from mkmszr.fighter_import.mips import Assembler

CLEAN, MKT = os.environ.get("MKMSZR_CLEAN_ROM"), os.environ.get("MKMSZR_MKT_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")
needs_roms = pytest.mark.skipif(
    not (CLEAN and MKT), reason="needs MKMSZR_CLEAN_ROM and MKMSZR_MKT_ROM"
)
PROOFS = Path(__file__).resolve().parents[1] / "Experimental" / "FighterRecompilerProofs"
# Runtime-confirmed bounded (owner, 2026-11-11): generic projectile proof v06.
V06_SHA256 = "49799d3a34fe510cbc86172cca5bf6679aa91318c6eef3ca3daaca736996c340"


def _forceball() -> dict:  # type: ignore[type-arg]
    moves, _ = components.load_programs("reptile")
    (m,) = [m for m in moves if m.name == "forceball_fast"]
    return next(s for s in m.steps if s["op"] == "projectile")


def test_strike_record_from_the_move_program() -> None:
    record = lp.strike_record(_forceball()["strike"], 0x2B)
    assert record.hex() == "0063002c002f003d" + "2b05" + "1202" + "00010000"


def test_knockback_arc_conversion() -> None:
    # MKT (0x2CCCC toward, -0x6CCCC, 0x5199) through the standard-jump calibration
    assert lp.arc("knockback_arc") == (-0x3B73B, -0x90623, 0x5A3C)


def test_process_emits_and_links() -> None:
    art = lp.ArtLayout(0x459E0, 0x0D, 0x12, 21, 100, 88)
    p = lp.Lowered(art, 0x77776, -60, -72, bytes(16), (0,) * 4, 335, 3, 336)
    a = Assembler(0xA01AF420)
    lp.emit_spawn(a)
    lp.emit_process(a, p)
    from mkmszr.fighter_import import host

    host.emit_sound_player(a)
    lp.emit_data(a, p, 0xA01AF420)
    code = a.link()
    assert a.labels["record"] % 16 == 0 and len(code) < 0x800


@needs_mkt
def test_donor_parts_of_the_forceball() -> None:
    donor = Donor(Path(MKT).read_bytes(), 19)  # type: ignore[arg-type]
    step = _forceball()
    flight = lp.donor_part(donor, step["art"])
    assert (
        flight.frames == (0x3078, 0x308C, 0x30A0, 0x308C)
        and flight.loops
        and flight.palette is None
    )
    impact = lp.donor_part(donor, step["impact"]["anim"])
    assert impact.frames[0] == 0x30B4 and len(impact.frames) == 7 and not impact.loops
    assert impact.palette == 0x800BEBD0  # bound by token 13


@needs_roms
def test_backend_reproduces_the_runtime_confirmed_proof(monkeypatch: pytest.MonkeyPatch) -> None:
    # v06 predates the knockback reaction's victim morphs (composition v03); without them the
    # backend still reproduces it byte for byte.
    spec_v06 = {k: v for k, v in lp.REACTION_LOWERING["knockback_arc"].items() if k != "morph"}
    monkeypatch.setitem(lp.REACTION_LOWERING, "knockback_arc", spec_v06)
    spec = importlib.util.spec_from_file_location(
        "v07", PROOFS / "MKMSZR_build_generic-projectile_proof_v07.py"
    )
    assert spec and spec.loader
    v07 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v07)
    rom, _ = v07.build(Path(CLEAN).read_bytes(), Path(MKT).read_bytes())  # type: ignore[arg-type]
    assert hashlib.sha256(rom).hexdigest() == V06_SHA256


@pytest.mark.skipif(not os.environ.get("MKMSZR_MKT_ROM"), reason="needs MKMSZR_MKT_ROM")
def test_reptile_forceball_helper() -> None:
    from mkmszr.fighter_import.body_build import Donor

    donor = Donor(Path(os.environ["MKMSZR_MKT_ROM"]).read_bytes(), 19)
    helper = lp.donor_helper(donor, {"table": 1, "slot": 5})
    # Token 11 creates it from 0x2FD4 with the second body pose; tokens 12 step it.
    assert helper == lp.Helper((0x2FD4, 0x3000, 0x3028, 0x3050), 1)
    assert lp.donor_helper(donor, {"table": 1, "slot": 2}) is None  # the slide has none


def test_phase_end_pace_matches_the_host() -> None:
    # 0x80031070: an odd rate of 2 or more sleeps rate - 1 between frames.
    assert [lp.phase_end_ticks(r) for r in (1, 2, 3, 4, 5)] == [1, 2, 2, 4, 4]


def test_acid_stagger_push_is_scaled_from_the_rocket() -> None:
    # MKT acid 0x26666 against MKT rocket 0x33333, whose host stumble push 0x56666 was accepted.
    assert lp.stumble_push("acid_stagger") == 0x40CCC
    assert lp.REACTION_LOWERING["acid_stagger"]["kind"] == "stumble"


@pytest.mark.skipif(not os.environ.get("MKMSZR_CLEAN_ROM"), reason="needs MKMSZR_CLEAN_ROM")
def test_acid_stagger_lift() -> None:
    from mkmszr.fighter_import.mipsdis import decode

    clean = Path(os.environ["MKMSZR_CLEAN_ROM"]).read_bytes()
    dst = 0xA01B0000
    code = lp.lift_stumble(clean, "acid_stagger", dst)
    word = lambda i: int.from_bytes(code[4 * i : 4 * i + 4], "big")
    assert word(38) == 0  # the trap's 8-tick hit pause is gone
    assert (word(46), word(48)) == (0x3C020004, 0x34420CCC)  # +0x40CCC
    assert (word(49), word(50)) == (0x3C02FFFB, 0x3442F334)  # -0x40CCC
    assert decode(word(17), dst + 4 * 17).text == f"j 0x{dst + 4 * 33:X}"  # internal jump moved


@pytest.mark.skipif(not os.environ.get("MKMSZR_MKT_ROM"), reason="needs MKMSZR_MKT_ROM")
def test_virtual_art_entries() -> None:
    mkt = Path(os.environ["MKMSZR_MKT_ROM"]).read_bytes()
    moves, _ = components.load_programs("reptile")
    acid = next(s for s in next(m for m in moves if m.name == "acid_spit").steps if s["op"] == "projectile")
    file87 = bytearray(b"\xff" * 0x40000)
    art = lp.place_art(file87, mkt, 19, acid, None, 0x40000, at=0x20000)
    assert art.virtual and art.impact_slot is not None
    for index, at in ((art.flight_slot, art.flight_at), (art.impact_slot, art.impact_at)):
        assert int.from_bytes(file87[0x104 + 4 * index : 0x108 + 4 * index], "big") == at


def test_process_alive_word_and_unmirrored_impact() -> None:
    import dataclasses

    from mkmszr.fighter_import import host
    from mkmszr.fighter_import.mipsdis import decode

    art = lp.ArtLayout(0x459E0, 0x0D, 0x12, 21, 100, 88)
    p = lp.Lowered(art, 0x77776, -60, -72, bytes(16), (0,) * 4, None, 3, None,
                   impact_at_opponent=True)  # fmt: skip
    texts = {}
    for flip in (True, False):
        a = Assembler(0xA01AF420)
        lp.emit_spawn(a)
        lp.emit_process(a, dataclasses.replace(p, impact_flip=flip), alive="alive")
        host.emit_sound_player(a)
        lp.emit_data(a, p, 0xA01AF420)
        a.label("alive")
        a.raw(0)
        code = a.link()
        texts[flip] = [decode(int.from_bytes(code[i : i + 4], "big"), 0xA01AF420 + i).text
                       for i in range(0, len(code), 4)]  # fmt: skip
    assert any(t.startswith("xor t1, t1, t2") for t in texts[True])
    assert not any(t.startswith("xor t1, t1, t2") for t in texts[False])
    sets = [t for t in texts[False] if t.startswith("sw t1, 0(t0)")]
    clears = [t for t in texts[False] if t.startswith("sw zero, 0(t0)")]
    assert sets and clears  # set while alive, cleared before the process exits


def test_impact_keeps_the_projectile_height() -> None:
    from mkmszr.fighter_import import host
    from mkmszr.fighter_import.mipsdis import decode

    art = lp.ArtLayout(0x459E0, 0x0D, 0x12, 21, 100, 88)
    stores = {}
    for keep in (False, True):
        p = lp.Lowered(art, 0x77776, -60, -72, bytes(16), (0,) * 4, None, 3, None,
                       impact_at_opponent=True, impact_keep_y=keep)  # fmt: skip
        a = Assembler(0xA01AF420)
        lp.emit_spawn(a)
        lp.emit_process(a, p)
        host.emit_sound_player(a)
        lp.emit_data(a, p, 0xA01AF420)
        code = a.link()
        text = [decode(int.from_bytes(code[i : i + 4], "big"), 0).text for i in range(0, len(code), 4)]
        stores[keep] = sum(t == f"sw t1, {host.ACTOR_Y}(s1)" for t in text)
    assert stores[False] == stores[True] + 1  # only the opponent's y copy goes


@needs_mkt
def test_acid_box_is_centred_on_the_drawn_spit() -> None:
    mkt = Path(os.environ["MKMSZR_MKT_ROM"]).read_bytes()
    moves, _ = components.load_programs("reptile")
    acid = next(s for s in next(m for m in moves if m.name == "acid_spit").steps if s["op"] == "projectile")
    donor = Donor(mkt, 19)
    top, bottom = lp.drawn_band(donor, acid["art"])
    assert (round(top), round(bottom)) == (92, 97)  # flight rows -25..-21 px
    out = lp.centre_on_art(donor, acid)
    assert out["strike"]["box"] == [193, 88, 64, 12]  # MKT's 27 moved by +61
    assert [c["box"][1] for c in out["checks"]] == [84, 84]
    assert acid["strike"]["box"][1] == 27  # the move program is unchanged


@pytest.mark.skipif(not CLEAN, reason="needs MKMSZR_CLEAN_ROM")
def test_knockback_reaction_morphs_the_victim_first() -> None:
    # Composition v02 crash: host reaction 0x25 plays shared root 0x1E without the stock
    # morphs, so a Temple MONK3 (type 2, sparse file) read an unfilled root and crashed.
    clean = Path(CLEAN).read_bytes()  # type: ignore[arg-type]
    words = lp.lifted_reaction(clean, "knockback_arc")
    stock = [int.from_bytes(clean[0x58814 + 4 * i : 0x58818 + 4 * i], "big") for i in range(0x110 // 4)]
    assert words[:2] == stock[:2]
    assert words[2:12] == [0x3C02802F, 0x8C42CE20, 0x8C4406E0, 0x0C015CB1, 0,
                           0x3C02802F, 0x8C42CE20, 0x8C4406E0, 0x0C015D1E, 0]  # fmt: skip
    assert len(words) == len(stock) + 10
    # the same sequence as the stock launch reaction 0x0C (0x80052898)
    launch = clean[0x534E4 : 0x534E4 + 20]
    assert launch.hex() == "3c02802f8c42ce208c4406e00c015cb100000000"


def test_host_kind_reaction_uses_the_stock_entry() -> None:
    # Rayden's lightning stand-in: the stock roundhouse launch, no payload reaction code.
    assert lp.host_reaction("launch") == 0x0C
    assert lp.host_reaction("knockback_arc") is None


def test_homing_hunt_and_direction_match_the_legacy_model() -> None:
    """The generic homing flight's steering and direction code (SMRE's constants, Sektor proof
    v14) against the runtime-confirmed legacy model (actions.robo_tracker: rocket_hunt and
    point_rocket, proofs v42-v46), run on the MIPS evaluator over many positions and speeds."""

    import random

    from mips_eval import Machine

    from mkmszr.fighter_import import lower_projectile as lp
    from mkmszr.fighter_import.actions import robo_tracker as trk
    from mkmszr.fighter_import.mips import REG, Assembler

    h = lp.Homing(((8, 0), (16, 0x8800)), trk.AIM_Y, trk.DETONATE_PX, trk.STEER, trk.HUNT_SPEED, 4,
                  0x80, trk.START_SPEED, 3, ())  # fmt: skip
    a = Assembler(0xA0100000)
    lp._emit_hunt(a, h, "hunt")
    lp._emit_direction(a, "dir")
    code = a.link()
    rnd = random.Random(14)
    ctrl, target, rocket, sp = 0x80200000, 0x80201000, 0x80202000, 0x80203000
    for _ in range(300):
        vx, vy = rnd.randint(-0x60000, 0x60000), rnd.randint(-0x60000, 0x60000)
        rx, ry = rnd.randint(-40000, 40000) << 8, rnd.randint(-8000, 8000) << 8
        tx, ty = rx + (rnd.randint(-600, 600) << 8), ry + (rnd.randint(-300, 300) << 8)
        sum_x, sum_y = vx + rnd.randint(-0x40000, 0x40000), vy + rnd.randint(-0x40000, 0x40000)
        m = Machine(code, 0xA0100000)
        m.store(ctrl + 0x6E0, target)
        for base, x, y in ((target, tx, ty), (rocket, rx, ry)):
            m.store(base + 0x2C, x)
            m.store(base + 0x30, y)
        m.store(sp + lp.SUM_X_SP, sum_x)
        m.store(sp + lp.SUM_Y_SP, sum_y)
        m.regs[REG["s1"]], m.regs[REG["s7"]], m.regs[REG["sp"]] = rocket, ctrl, sp
        m.regs[REG["s2"]], m.regs[REG["s3"]] = vx & 0xFFFFFFFF, vy & 0xFFFFFFFF
        m.regs[REG["ra"]] = 0x80000010
        stop = m.run(a.labels["hunt"])
        assert stop.kind == "return"
        dx = ((tx - rx) >> 9) - ((sum_x - vx) >> 16)
        dy = ((ty - ry) >> 9) - ((sum_y - vy) >> 16) + trk.AIM_Y
        s32 = lambda v: v - (1 << 32) if v & 0x80000000 else v
        if trk.near(dx, dy):
            assert m.regs[REG["v0"]] == 1
        else:
            assert m.regs[REG["v0"]] == 0
            assert (s32(m.regs[REG["s2"]]), s32(m.regs[REG["s3"]])) == trk.hunt(vx, vy, dx, dy)
        m.regs[REG["a0"]], m.regs[REG["a1"]] = vx & 0xFFFFFFFF, vy & 0xFFFFFFFF
        m.regs[REG["ra"]] = 0x80000010
        assert m.run(a.labels["dir"]).kind == "return"
        assert m.regs[REG["v0"]] == trk.direction(vx, vy)


@needs_mkt
def test_tether_render_offset_changes_only_the_flight_anchor() -> None:
    from mkmszr.fighter_import import generate

    mkt = Path(MKT).read_bytes()
    program, result, _ = generate.Generator(mkt, 14).program("spear", 0x800ABFB8)
    assert not result.unknown
    step = next(s for s in program["steps"] if s["op"] == "projectile")

    original = bytearray()
    lowered = bytearray()
    art = lp.place_art(original, mkt, 14, step, None, 0x10000)
    moved = lp.place_art(lowered, mkt, 14, step, None, 0x10000, render_dy_px=10)
    assert art == moved

    def word_at(at: int) -> int:
        return int.from_bytes(original[at:at + 4], "big")

    descriptor = word_at(word_at(art.flight_at))
    anchor_y = descriptor + 10
    assert original[anchor_y:anchor_y + 2] == bytes(2)
    assert lowered[anchor_y:anchor_y + 2] == (-10).to_bytes(2, "big", signed=True)
    lowered[anchor_y:anchor_y + 2] = original[anchor_y:anchor_y + 2]
    assert lowered == original
