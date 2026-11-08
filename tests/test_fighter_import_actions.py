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


# ---------------------------------------------------------------- lifter


def _code(*values: int) -> bytes:
    return b"".join(v.to_bytes(4, "big") for v in values)


def test_lifter_relocates_internal_jumps_only() -> None:
    from mkmszr.fighter_import import lifter

    src = 0x8004AB84
    code = _code(
        0x10400002,  # beqz v0, +2 (internal, PC-relative)
        0x08000000 | ((src + 0x10) >> 2) & 0x03FFFFFF,  # j src+0x10 (internal)
        0x0C00A1E5,  # jal 0x80028794 (external)
        0x00000000,
        0x03E00008,  # jr ra
        0x00000000,
    )
    out = lifter.lift(code, src, 0xA01AFBA8, patches={src + 0x0C: 0x24040004})
    lifter.verify(code, out)
    words = [int.from_bytes(out.code[i : i + 4], "big") for i in range(0, len(out.code), 4)]
    assert words[0] == 0x10400002 and words[2] == 0x0C00A1E5
    assert words[1] == 0x08000000 | ((0xA01AFBA8 + 0x10) >> 2) & 0x03FFFFFF
    assert out.relocated == [src + 4] and words[3] == 0x24040004


def test_lifter_rejects_non_self_contained_code() -> None:
    from mkmszr.fighter_import import lifter

    src = 0x80049C34
    with pytest.raises(lifter.LiftError):  # branch leaving the routine
        lifter.lift(_code(0x10400010, 0, 0x03E00008, 0), src, 0xA01AF000)
    with pytest.raises(lifter.LiftError):  # computed jump
        lifter.lift(_code(0x03200008, 0), src, 0xA01AF000)
    with pytest.raises(lifter.LiftError):  # address constant inside the routine (lui/addiu)
        lifter.lift(_code(0x3C058005, 0x24A59C38, 0x03E00008, 0), src, 0xA01AF000)


def test_transfer_thunk_enters_kseg0() -> None:
    a = Assembler(0xA01AFB48)
    host.emit_transfer_thunk(a, "t", 3)
    assert words(a) == [
        0x3C198005,
        0x2739AA4C,
        0x03200008,
        0x24040003,
    ]  # lui/addiu 0x8004AA4C, jr t9


# ---------------------------------------------------------------- projectile


def test_codec16_and_colours() -> None:
    from mkmszr.fighter_import import projectile

    # size 8: run of 3 x idx1 (high nibble 3), literal pair run (0x70 -> 3 nibbles), 2 zeros via 0x00/len
    stream = bytes([16, 0, 0, 8, 0x31, 0x70, 0x23, 0x40, 0x05, 0x02])
    indices, used = projectile.decode_mkt_codec16(stream)
    assert indices == bytes([1, 1, 1, 2, 3, 4, 5, 5]) and used == len(stream)
    assert projectile.mkt_color_to_host(0xF7BD) == 0xFBDE  # opaque light grey, RGBA5551 -> BGR555
    assert projectile.mkt_color_to_host(0x07C0) == 0  # ROCKET_P entry 0: alpha clear = transparent


def test_projectile_hooks_fall_through_to_stock_calls() -> None:
    from mkmszr.fighter_import import projectile

    art = projectile.ProjectileArt(39, 9, 26, 3, bytes(360), (0,) * 16)
    a = Assembler(0x8009A1E0)
    projectile.emit_palette_hook(a, "p", 0xDC0, 0x45D50)
    projectile.emit_preupload_hook(a, "u", 0x45DD0, art, 0x801B0200)
    w = words(a)
    assert w[8] == 0x08000000 | (projectile.F_PALETTE_BIND >> 2) & 0x03FFFFFF  # j 0x8001C528
    assert w[-2] == 0x08000000 | (projectile.F_ACTOR_INSERT >> 2) & 0x03FFFFFF  # j 0x80024650
    assert art.stride == 40 and len(art.palette_record()) == 4 + 128
    # v22: the slot load borrows the shared texture-storage pointer and gives it back.
    load = w.index(0x0C000000 | (projectile.F_TEXTURE_SLOT_LOAD >> 2) & 0x03FFFFFF)
    bump_sw = 0xAF380000 | (projectile.TEXTURE_BUMP & 0xFFFF)  # sw t8, %lo(bump)(t9)
    assert w[load - 1] == bump_sw and w[load + 4] == bump_sw
    assert w[load - 3 : load - 1] == [0x3C18801B, 0x37180200]  # t8 = backing
    with pytest.raises(ValueError):
        projectile.emit_preupload_hook(Assembler(0x8009A1E0), "x", 0x45DD0, art, 0x801B0204)
