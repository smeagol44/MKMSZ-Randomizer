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
    projectile.emit_preupload_hook(a, "u", 0x45DD0, art)
    w = words(a)
    assert w[8] == 0x08000000 | (projectile.F_PALETTE_BIND >> 2) & 0x03FFFFFF  # j 0x8001C528
    assert w[-2] == 0x08000000 | (projectile.F_ACTOR_INSERT >> 2) & 0x03FFFFFF  # j 0x80024650
    assert art.stride == 40 and len(art.palette_record()) == 4 + 128
    # v23: no allocating slot initializer; stock deferred upload done early.
    assert 0x0C000000 | (projectile.F_TEXTURE_SLOT_LOAD >> 2) & 0x03FFFFFF not in w
    queue = w.index(0x0C000000 | (projectile.F_UPLOAD_QUEUE >> 2) & 0x03FFFFFF)
    assert w[queue + 2 : queue + 4] == [
        0x24040001,
        0x0C000000 | (projectile.F_UPLOAD_DRAIN >> 2) & 0x03FFFFFF,
    ]
    assert 0xAFA90010 in w[:queue]  # height at sp+0x10


# ---------------------------------------------------------------- robo zap (straight rocket)
def test_robo_zap_placement_patches_lifted_root() -> None:
    from mkmszr.fighter_import import lifter
    from mkmszr.fighter_import.actions import robo_zap

    src = robo_zap.ICE_ROOT_SRC
    words = [0] * ((robo_zap.ICE_ROOT_END - src) // 4)
    for va, word in robo_zap.PLACEMENT_SITE.items():
        words[(va - src) // 4] = word
    code = b"".join(w.to_bytes(4, "big") for w in words)
    patches = robo_zap.placement_patches()
    out = lifter.lift(code, src, 0xA01AFBA8, patches=patches)
    lifter.verify(code, out)
    robo_zap.check_stock(out)
    w = [int.from_bytes(out.code[i : i + 4], "big") for i in range(0, len(out.code), 4)]
    assert w[(0x8004AFF0 - src) // 4] == 0x24050012  # addiu a1, zero, 18 ((5 + 4) px)
    assert w[(0x8004AFFC - src) // 4] == 0x2406004C  # addiu a2, zero, 76 (38 px)
    assert w[(0x8004B000 - src) // 4] == 0x0C00C482  # jal 0x80031208 kept
    bad = lifter.lift(code, src, 0xA01AFBA8, patches={0x8004AF00: 0})
    with pytest.raises(lifter.LiftError):
        robo_zap.check_stock(bad)
    with pytest.raises(ValueError):
        robo_zap.placement_patches(0x8000, 0)


def test_projectile_behind_owner_sublayer() -> None:
    from mkmszr.fighter_import import projectile

    art = projectile.ProjectileArt(39, 9, 26, 3, bytes(360), (0,) * 16)
    plain, behind = Assembler(0x8009A1E0), Assembler(0x8009A1E0)
    projectile.emit_preupload_hook(plain, "u", 0x45DD0, art)
    projectile.emit_preupload_hook(behind, "u", 0x45DD0, art, behind_owner=True)
    w = words(behind)
    assert w[7:10] == [0x964800EC, 0x25080001, 0xA60800EC]  # lhu/addiu/sh +0xEC: parent + 1
    assert len(w) == len(words(plain)) + 3


def test_teleport_emerge_on_floor_is_opt_in() -> None:
    from dataclasses import replace

    from mkmszr.fighter_import.actions import robo_teleport as rt

    scripts = rt.TeleportScripts(0x100, 0x200, 0x300, 0x310, 4, 6)
    base = rt.TeleportParams(scripts, (1, 2, 3, 4), 400)
    old = words(rt.assemble(0xA01AF420, base))
    new = words(rt.assemble(0xA01AF420, replace(base, emerge_on_floor=True)))
    assert 0x8C4806B4 not in old and 0x8C4806B4 in new  # lw t0, 0x6B4(v0): target floor
    i = new.index(0x8C4806B4)
    assert new[i + 1] == 0xAFA8001C  # saved at once: the next call clobbers v0
    assert new[i - 1] == 0 and new[i - 2] >> 26 == 0x05  # right after find_target (bnez; nop)
    j = new.index(0x8FA8001C)  # lw t0, 0x1C(sp)
    assert new[j + 1] == 0x8E890030  # lw t1, 0x30(s4): target y (fallback)


def test_robo_zap_chest_choreography() -> None:
    from mkmszr.fighter_import.actions import robo_zap

    w = robo_zap.chest_script_words(0x111, 0x222)
    assert [w[robo_zap.ZAP_SCRIPT + 4 * i] for i in range(6)] == [0x111, 0x222, 0, 1, 0xDB8, 0]
    assert [w[p] for p in robo_zap.ZAP_RECOVERY] == [0x222] * 5 + [0x111]
    assert robo_zap.ZAP_TOKEN not in w and 0xDBC not in w  # token and hook offsets untouched
    assert robo_zap.close_patches() == {0x8004B1A0: 0x24040002}
    assert robo_zap.STOCK_WORDS[0x8004B1A0] == 0x24040005


# ---------------------------------------------------------------- rocket flight
def test_fold_donor_speeds_and_frame_cycle() -> None:
    from itertools import pairwise

    from mkmszr.fighter_import import physics
    from mkmszr.fighter_import.actions import robo_zap

    normal = robo_zap.host_speeds(robo_zap.SPEED_NORMAL)
    reacting = robo_zap.host_speeds(robo_zap.SPEED_REACTING)
    # v75's runtime-accepted start/cap, now derived: 2 units/px * (d0 + d1) / 3.
    assert normal[0] == 0x46666 and normal[-1] == reacting[-1] == 0xEEEEE
    assert reacting[0] == 2 * (0x59999 + 0x59999 + (0x59999 >> 4)) // 3
    assert all(b > a for a, b in pairwise(normal))
    table = robo_zap.speed_table()
    assert table == normal + [0] + reacting + [0]
    assert physics.resample_frame_cycle([1, 2], 3) == [1, 1, 2, 1, 2, 2]
    assert physics.resample_frame_cycle([1, 2], 2) == [1, 2]


def test_robo_zap_flight_child_and_callback_execute() -> None:
    from mips_eval import Machine

    from mkmszr.fighter_import import host
    from mkmszr.fighter_import.actions import robo_zap

    base = 0xA01AF000
    a = Assembler(base)
    robo_zap.emit_flight(a, 0x46000)
    robo_zap.emit_speed_table(a, "zap_speeds")
    m = Machine(a.link(), base)
    ctrl, actor = 0x80300000, 0x80310000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + host.CTRL_ACTOR, actor)
    m.store(robo_zap.FILE87_BASE_PTR, 0x80400000)

    def callback(v: int) -> int:
        m.store(actor + host.ACTOR_XVEL, v)
        m.regs[31] = 0x8004CD00
        assert m.run(a.labels["zap_callback"]).target == 0x8004CD00
        out = m.load(actor + host.ACTOR_XVEL)
        return out - (1 << 32) if out & 0x80000000 else out

    for start in (robo_zap.SPEED_NORMAL, robo_zap.SPEED_REACTING):
        seq = robo_zap.host_speeds(start)
        for sign in (1, -1):
            v, got = sign * seq[0], []
            for _ in range(len(seq) + 1):
                v = callback(v)
                got.append(v)
            assert got == [sign * x for x in seq[1:]] + [sign * seq[-1]] * 2
    assert callback(0) == 0 and callback(12345) == 12345  # unknown speeds are left alone

    seq = robo_zap.host_speeds(robo_zap.SPEED_NORMAL)
    m.store(actor + host.ACTOR_XVEL, (-seq[0]) & 0xFFFFFFFF)  # set at creation, facing left
    stop = m.run(a.labels["zap_child"])
    assert (
        stop.kind == "call" and stop.target & 0x1FFFFFFF == robo_zap.F_PROJECTILE_SETUP & 0x1FFFFFFF
    )
    assert m.regs[4:7] == [actor, seq[robo_zap.CHILD_START_TICKS], 1]
    assert m.load(ctrl + host.CTRL_SCRIPT_CURSOR) == 0x80446000
    stop = m.run(stop.resume)
    assert stop.kind == "return" and stop.target == robo_zap.FLIGHT_TAIL  # cached stock tail
    assert m.regs[4:6] == [actor, robo_zap.FLIGHT_STRIKE_SELECTOR]
    assert m.load(ctrl + 0x70C) == a.labels["zap_callback"]


def test_robo_zap_initial_speed_reacting_and_facing() -> None:
    from mips_eval import Machine

    from mkmszr.fighter_import import host
    from mkmszr.fighter_import.actions import robo_zap

    a = Assembler(0x8009A1E0)
    robo_zap.emit_initial_speed(a)
    a.jr_ra()
    a.nop()
    normal = robo_zap.host_speeds(robo_zap.SPEED_NORMAL)[0]
    reacting = robo_zap.host_speeds(robo_zap.SPEED_REACTING)[0]
    ctrl, opp, actor = 0x80300000, 0x80320000, 0x80310000
    for opponent, flags, facing, want in (
        (0, 0, 0, normal),
        (opp, 0, 0, normal),
        (opp, 0x04, 0, reacting),
        (opp, 0x04, 0x10, -reacting),
        (0, 0x04, 0x10, -normal),
    ):
        m = Machine(a.link(), 0x8009A1E0)
        m.store(host.CURRENT_CTRL, ctrl)
        m.store(ctrl + host.CTRL_OPPONENT, opponent)
        m.store(opp + 0x6BC, flags)  # +0x6BE is the low halfword of word +0x6BC
        m.store(actor + 0x8C, facing << 16)  # +0x8C halfword
        m.regs[16] = actor  # s0
        m.regs[31] = 0x80030AC8
        m.run(0x8009A1E0)
        assert m.load(actor + host.ACTOR_XVEL) == want & 0xFFFFFFFF, (opponent, flags, facing)


def test_robo_zap_child_patch_and_stock_words() -> None:
    from mkmszr.fighter_import.actions import robo_zap

    assert robo_zap.child_patches(0xA01AFF00) == {0x8004B0D8: 0x3C04A01B, 0x8004B0DC: 0x2484FF00}
    assert robo_zap.STOCK_WORDS[0x8004B0D8] == 0x3C048005  # lui a0, 0x8005 (0x8004B82C)


def test_bind_after_creation_routine_executes() -> None:
    from mips_eval import Machine

    from mkmszr.fighter_import import host, projectile
    from mkmszr.fighter_import.actions import robo_zap

    art = projectile.ProjectileArt(39, 9, 26, 3, bytes(360), (0,) * 16)
    base = 0xA01B0000
    a = Assembler(base)
    projectile.emit_bind_after_creation(
        a,
        "bind",
        0x45D50,
        art,
        on_create=robo_zap.emit_initial_speed,
        epilogue=robo_zap.emit_mode_reload,
    )
    m = Machine(a.link(), base)
    ctrl, actor, owner, fbase, render = 0x80300000, 0x80310000, 0x80330000, 0x80400000, 0x80310108
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + 0x714, actor)
    m.store(ctrl + host.CTRL_ACTOR, owner)
    m.store(actor + 0x98, fbase)
    m.store(actor + 0x74, fbase + 0x45DD0)
    m.store(actor + 0x7C, render)
    m.store(render, fbase + 0x45BE0)
    m.store(actor + 0x9C, 0x00240000)  # +0x9C slot 0x24, +0x9E selector
    m.store(owner + 0xEC, 0x00010000)
    m.store(0x80111F98, 0x00000000)  # mode 0 (halfword at +0x1F98)
    m.regs[29], m.regs[31], m.regs[16], m.regs[18] = 0x80200000, 0x8004AEEC, 0x1111, 0x2222
    calls = []
    stop = m.run(base)
    while stop.kind == "call":
        f = stop.target & 0x1FFFFFFF
        calls.append((f, m.regs[4:8]))
        if f == projectile.F_PALETTE_BIND & 0x1FFFFFFF:
            m.regs[2] = 0xC5  # handle
        stop = m.run(stop.resume)
    assert stop.target == 0x8004AEEC and m.regs[29] == 0x80200000
    assert m.regs[16] == 0x1111 and m.regs[18] == 0x2222  # s0/s2 restored
    assert [c[0] for c in calls] == [
        projectile.F_PALETTE_BIND & 0x1FFFFFFF,
        projectile.F_FRAME_SETUP & 0x1FFFFFFF,
        projectile.F_UPLOAD_QUEUE & 0x1FFFFFFF,
        projectile.F_UPLOAD_DRAIN & 0x1FFFFFFF,
    ]
    assert calls[0][1][:3] == [fbase + 0x45D50, 0x100, 0]
    assert calls[2][1] == [1, fbase + 0x45BE4, 0x24, 40] and m.load(0x80200000 - 0x28 + 0x10) == 9
    assert m.load(actor + 0x9C) & 0xFFFF == 0xC5 - 0x80  # selector = handle - 0x80
    assert m.load(actor + 0xEC) >> 16 == 2  # owner sub-layer + 1
    assert m.load(actor + host.ACTOR_XVEL) == robo_zap.host_speeds(robo_zap.SPEED_NORMAL)[0]
    assert m.regs[3] == 0  # v1 = mode, reloaded for the root


def test_post_token_patch() -> None:
    from mkmszr.fighter_import.actions import robo_zap

    assert robo_zap.post_token_patches(0xA01AF800) == {0x8004AEE4: 0x0C06BE00, 0x8004AEE8: 0}


def test_sound_install_rewrites_one_isolated_chain() -> None:
    from mkmszr.fighter_import import sound

    chain = sound.HostChain(event=173, patch=330, subpatch=173, wave=163)
    clean = bytearray(b"\xff" * 0x9C0000)
    d = sound.MSZ_EVENT_DEFS + chain.event * 16
    clean[d + 4 : d + 12] = (0x20).to_bytes(4, "big") + (0x100).to_bytes(4, "big")
    track = sound.MSZ_TRACKS + 0x100
    clean[track : track + 0x20] = chain.patch.to_bytes(4, "big") + bytes(0x1C)
    p = sound.MSZ_PATCHES + chain.patch * 4
    clean[p : p + 4] = bytes([1, 0]) + chain.subpatch.to_bytes(2, "big")
    s = sound.MSZ_SUBPATCHES + chain.subpatch * 20
    clean[s : s + 20] = bytes(10) + chain.wave.to_bytes(2, "big") + bytes(8)
    donor = sound.DonorSound(
        0x108, (102).to_bytes(4, "big") + b"T" * 0x1C, b"S" * 20, b"W" * 24, b"B" * 264, b"x" * 100
    )
    rom = bytearray(clean)
    nxt = sound.install(rom, bytes(clean), donor, chain, 0x9B8000)
    assert nxt == 0x9B8070
    assert rom[track : track + 4] == chain.patch.to_bytes(4, "big")  # host patch kept
    assert rom[track + 4 : track + 0x20] == b"T" * 0x1C
    assert rom[s + 10 : s + 12] == chain.wave.to_bytes(2, "big")  # host waveform kept
    w = sound.MSZ_WAVES + chain.wave * 24
    assert rom[w : w + 4] == (0x9B8000 - sound.MSZ_TBL).to_bytes(4, "big")
    assert rom[0x9B8000:0x9B8064] == b"x" * 100
    with pytest.raises(ValueError):  # a chain may be hosted only once
        sound.install(rom, bytes(clean), donor, chain, 0x9B8080)


def test_robo_zap_flight_hands_hits_to_the_imported_hit_child() -> None:
    from mips_eval import Machine

    from mkmszr.fighter_import import host
    from mkmszr.fighter_import.actions import robo_zap

    base = 0xA01AF000
    a = Assembler(base)
    robo_zap.emit_flight(a, 0x46000, hit_child=0xA01B1234)
    robo_zap.emit_speed_table(a, "zap_speeds")
    m = Machine(a.link(), base)
    ctrl, actor = 0x80300000, 0x80310000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + host.CTRL_ACTOR, actor)
    m.regs[29] = 0x80200000
    stop = m.run(a.labels["zap_child"])  # -> 0x8004CC14 setup
    stop = m.run(stop.resume)
    assert stop.kind == "call" and stop.target == robo_zap.F_FLIGHT_LOOP  # cached (KSEG0)
    assert m.regs[4:6] == [actor, robo_zap.FLIGHT_STRIKE_SELECTOR]
    stop = m.run(stop.resume)  # loop returned: contact
    assert stop.kind == "call" and stop.target & 0x1FFFFFFF == host.F_CONTEXT_SWITCH & 0x1FFFFFFF
    assert m.regs[4] == ctrl + 8
    assert m.load(ctrl + host.CTRL_CALLBACK) == m.load(ctrl + 8) == 0xA01B1234
    assert m.load(ctrl + 0xC) == m.load(ctrl + 0x10) == ctrl + 0x620


def test_robo_zap_sound_wrappers_and_patches() -> None:
    from mips_eval import Machine

    from mkmszr.fighter_import import host
    from mkmszr.fighter_import.actions import robo_zap

    base = 0xA01AF000
    a = Assembler(base)
    host.emit_sound_player(a)
    robo_zap.emit_sound_wrappers(a, chest_event=173, boom_event=177)
    m = Machine(a.link(), base)
    m.regs[29], m.regs[31], m.regs[4], m.regs[5] = 0x80200000, 0x8004AD40, 3, 0x24
    events = []
    stop = m.run(a.labels["zap_chest_open"])
    while stop.kind == "call":
        if stop.target & 0x1FFFFFFF == host.F_RAW_SOUND & 0x1FFFFFFF:
            events.append(m.regs[4])
        stop = m.run(stop.resume)
    # tail-jumps into the stock open phase with the root's arguments and return address
    assert stop.target == 0x80030E98 and m.regs[4:6] == [3, 0x24]
    assert m.regs[31] == 0x8004AD40 and m.regs[29] == 0x80200000 and events == [173]
    assert robo_zap.root_sound_patches(0xA01AF100) == {
        0x8004AD38: 0x0C06BC40,
        0x8004AD58: 0x1000000F,  # b 0x8004AD98: skip the Ice launch sound block
    }
    assert robo_zap.hit_child_patches(0xA01AF200) == {0x8004BB94: 0x0C06BC80}
    assert robo_zap.straight_patches(0xA01B0000) == {0x8004B62C: 0x3C04A01B, 0x8004B630: 0x24840000}


def test_robo_zap_strike_record() -> None:
    from mkmszr.fighter_import.actions import robo_zap

    rec = robo_zap.strike_record()
    assert rec.hex() == "0010fff10023001f2305140200010000"
    assert rec[:8] == robo_zap.DONOR_STRIKE[:8] and rec[10:] == robo_zap.DONOR_STRIKE[10:]
    a = Assembler(0xA01AF420)
    robo_zap.emit_strike_record(a)
    assert a.link() == rec


def test_robo_zap_point_blank_uses_rocket_record() -> None:
    from mkmszr.fighter_import.actions import robo_zap

    assert robo_zap.point_blank_strike_patch() == {0x8004B5D4: 0x8C44004C}
    assert robo_zap.STOCK_WORDS[0x8004B5D4] == 0x8C440060


def test_robo_zap_trap_stumble_without_pause() -> None:
    from mkmszr.fighter_import.actions import robo_zap

    assert robo_zap.trap_stumble_patches() == {0x80051318: 0}
    assert robo_zap.STOCK_WORDS[0x80051318] == 0x0C00A1E5  # jal 0x80028794 (sleep)


def test_robo_zap_smoke_and_explosion_spawns() -> None:
    from mips_eval import Machine

    from mkmszr.fighter_import import effects, host
    from mkmszr.fighter_import.actions import robo_zap

    base = 0xA01AF000
    a = Assembler(base)
    host.emit_sound_player(a)
    robo_zap.emit_sound_wrappers(a, chest_event=173, boom_event=177, explosion="fx_expl")
    robo_zap.emit_flight(a, 0x46000, smoke="fx_smoke")
    robo_zap.emit_speed_table(a, "zap_speeds")
    a.label("fx_spawn")
    a.jr_ra()
    a.nop()
    a.label("fx_smoke")
    a.label("fx_expl")
    m = Machine(a.link(), base)
    ctrl, actor = 0x80300000, 0x80310000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + host.CTRL_ACTOR, actor)
    m.store(actor + 0xEC, 0x00040000)  # sub-layer 4
    speed = robo_zap.host_speeds(robo_zap.SPEED_NORMAL)[0]

    def args_at_spawn(entry: str, facing: int, xvel: int) -> list[int]:
        m.store(actor + 0x8C, facing << 16)
        m.store(actor + host.ACTOR_XVEL, xvel & 0xFFFFFFFF)
        m.regs[29], m.regs[31] = 0x80200000, 0x8004CD18
        m.store(a.labels["fx_spawn"], 0x0000000D)  # 'break' stops the evaluator at the call
        try:
            stop = m.run(a.labels[entry])
            while stop.kind == "call":
                stop = m.run(stop.resume)
        except NotImplementedError:
            return m.regs[4:8]
        raise AssertionError("fx_spawn not reached")

    assert args_at_spawn("zap_callback", 0, speed) == [actor, a.labels["fx_smoke"], 0xFFFFFFDA, 5]
    assert args_at_spawn("zap_callback", 0x10, -speed)[2] == 38
    assert args_at_spawn("zap_boom", 0, 0) == [
        actor,
        a.labels["fx_expl"],
        0,
        effects.FRONT_SUBLAYER,
    ]
    m.store(a.labels["fx_spawn"], 0x03E00008)  # jr ra: the callback returns to the loop
    m.store(actor + host.ACTOR_XVEL, speed)
    m.regs[29], m.regs[31] = 0x80200000, 0x8004CD18
    stop = m.run(a.labels["zap_callback"])
    assert stop.target == 0x8004CD18 and m.regs[29] == 0x80200000

    patches = robo_zap.hit_child_patches(0xA01AF200, explosion=True)
    assert patches == {0x8004BB94: 0x0C06BC80, 0x8004BCB4: 0, 0x8004BCD0: 0}
    for va in patches:
        assert va in robo_zap.STOCK_WORDS
