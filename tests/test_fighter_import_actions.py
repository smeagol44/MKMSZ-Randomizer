"""Tests for the importer's MIPS assembler, host primitives and imported actions.

No ROM is needed: the teleport action is checked against the payload of the
Runtime-confirmed Sektor teleport proof v18 (SHA-256 of the assembled bytes).
"""

from __future__ import annotations

import hashlib

import pytest

from mkmszr.fighter_import import host, physics
from mkmszr.fighter_import.actions import robo_teleport
from mkmszr.fighter_import.mips import Assembler


def words(a: Assembler) -> list[int]:
    blob = a.link()
    return [int.from_bytes(blob[i : i + 4], "big") for i in range(0, len(blob), 4)]


def test_encodings() -> None:
    a = Assembler(0x80000000)
    a.addiu("sp", "sp", -0x40)
    a.lui("t0", 0x802F)
    a.lw("s0", -0x31E0, "t0")
    a.sh("zero", 0x6B2, "s0")
    a.sra("t9", "t0", 31)
    a.slt("t2", "t1", "t0")
    a.li("t0", 0x8000)  # does not fit a signed addiu: lui/ori, as the proven builders emit
    a.li("t1", -1)  # fits addiu
    assert words(a) == [
        0x27BDFFC0,
        0x3C08802F,
        0x8D10CE20,
        0xA60006B2,
        0x0008CFC3,
        0x0128502A,
        0x3C080000,
        0x35088000,
        0x2409FFFF,
    ]


def test_branches_calls_and_labels() -> None:
    a = Assembler(0xA01AF420)
    a.label("top")
    a.beqz("v0", "end")  # +2 instructions (with its delay slot)
    a.jal(0x80049F90)
    a.jal_label("top")
    a.label("end")
    a.bgez("s5", "top")
    w = words(a)
    assert w[0] == 0x10400005  # beq v0, zero, end
    assert w[2] == 0x0C0127E4  # jal 0x80049F90
    assert w[4] == 0x0C06BD08  # jal 0xA01AF420 (KSEG1 segment kept)
    assert w[6] == 0x06A1FFF9  # bgez s5, top
    with pytest.raises(ValueError):
        a.label("top")


def test_cross_segment_jump_rejected() -> None:
    a = Assembler(0x80000000)
    a.jal_label("far")
    a.code.extend([0] * 2)
    a.labels["far"] = 0xA0000000
    with pytest.raises(ValueError):
        a.link()


def test_hi_lo() -> None:
    assert (host.hi(0x802ECE20), host.lo(0x802ECE20)) == (0x802F, -0x31E0)
    assert (host.hi(0x802C1AC0), host.lo(0x802C1AC0)) == (0x802C, 0x1AC0)


def test_jump_calibration_and_teleport_motion() -> None:
    assert physics.convert_velocity(physics.DONOR_JUMP_VEL) == physics.HOST_JUMP_VEL
    m = robo_teleport.motion()
    # Runtime-confirmed v11-v18 values.
    assert (m.fall_velocity, m.fall_gravity) == (0x7E55F, 0xA56F)
    assert (m.emerge_velocity, m.gravity_nohit, m.gravity_hit) == (-0xFFEB3, 0x13594, 0xE306)


def test_teleport_action_matches_runtime_confirmed_v18_payload() -> None:
    params = robo_teleport.TeleportParams(
        scripts=robo_teleport.TeleportScripts(
            sink=0x45B48,
            drop=0x45B88,
            land_a=0x45BC8,
            land_b=0x45BD4,
            sink_steps=13,
            emerge_steps=6,
        ),
        strike_words=(0x0049FFF7, 0x00490057, 0x08021803, 0x00010E02),
        sound_event=335,
    )
    a = robo_teleport.assemble(0xA01AF420, params)
    blob = a.link()
    assert a.labels["cond"] == 0xA01AFA48
    assert hashlib.sha256(blob).hexdigest() == (
        "edb5cf64258208677ebf0f2ad276ac4a664b75e264f808ae53381bbdc8ea19ba"
    )
