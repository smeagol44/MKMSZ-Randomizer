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
def test_backend_reproduces_the_runtime_confirmed_proof() -> None:
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
