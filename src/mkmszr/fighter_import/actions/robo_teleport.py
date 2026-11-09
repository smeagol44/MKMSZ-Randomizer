"""MKT robot teleport uppercut (``do_body_propell(8)`` -> donor ``0x80048368``) for MKMSZ.

Runtime-confirmed as Sektor teleport proofs v08-v18 (Wiki ``Sektor-Takeover-Proof-
History`` and ``MKT-Adapter-Primitives#sektor-teleport-uppercut-translation``). This
module is the same action expressed through the host primitive library; with the
v18 parameters it assembles byte-for-byte to the v18 payload.

Donor phases: sink off-screen (velocity 0x5F333, gravity 0x9599), reposition past
the target and face it, rise from the screen bottom (surface speed 0xC6666), then
an uppercut arc (gravity 0xF000, or 0xB000 after a hit) and a landing hold.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import host, physics
from ..mips import Assembler

# Donor constants (MKT Rev. 2, 0x80048368 and its flight; surface speed derived in proof v04).
DONOR_SINK_VEL = 0x5F333
DONOR_SINK_GRAV = 0x9599
DONOR_SURFACE_VEL = 0xC6666
DONOR_GRAV_NOHIT = 0xF000
DONOR_GRAV_HIT = 0xB000

HOP_VELOCITY_SCALE = 0.9  # v05: user apex captures (v04 ~1.04 enemy heights vs MKT ~0.92)
STOCK_LK_CONDITION = 0x8004A4A4  # the replaced stock Low Kick record's condition
UPPERCUT_ACTION_ID = 0x603  # stock uppercut action id (0x800337E0)


@dataclass(frozen=True)
class Motion:
    fall_velocity: int
    fall_gravity: int
    emerge_velocity: int  # negative = up
    gravity_nohit: int
    gravity_hit: int


def motion() -> Motion:
    """Jump-calibrated donor motion, retimed so the post-hit airtime matches MKT (v11)."""

    v10_velocity = int(physics.convert_velocity(DONOR_SURFACE_VEL) * HOP_VELOCITY_SCALE)
    v10_gravity_hit = physics.convert_acceleration(DONOR_GRAV_HIT)
    scale = physics.donor_airtime_seconds(
        DONOR_SURFACE_VEL, DONOR_GRAV_HIT
    ) / physics.host_airtime_seconds(v10_velocity, v10_gravity_hit)
    if not 0.9 < scale < 0.95:
        raise AssertionError(scale)
    return Motion(
        fall_velocity=physics.convert_velocity(DONOR_SINK_VEL),
        fall_gravity=physics.convert_acceleration(DONOR_SINK_GRAV),
        emerge_velocity=-int(v10_velocity / scale),
        gravity_nohit=int(physics.convert_acceleration(DONOR_GRAV_NOHIT) / scale**2),
        gravity_hit=int(v10_gravity_hit / scale**2),
    )


@dataclass(frozen=True)
class TeleportScripts:
    """Fighter-file offsets of the teleport animation scripts."""

    sink: int
    drop: int
    land_a: int
    land_b: int
    sink_steps: int  # pose + cropped/aliased sink frames before the transparent frame
    emerge_steps: int


@dataclass(frozen=True)
class TeleportParams:
    scripts: TeleportScripts
    strike_words: tuple[int, int, int, int]
    sound_event: int
    range_units: int = 592  # 0.925 x the 640-unit visible ground width (camera depth 0x200)
    behind: int = 40  # emerge this far past the target (donor: behind it, then face it)
    wall_margin: int = 4
    min_separation: int = 16
    hidden_ticks: int = 1
    air_cap: int = 60
    fall_cap: int = 45
    landing_ticks: tuple[int, int] = (2, 1)  # donor 0x80076E48 holds 2 x 3 ticks at 60 Hz
    # v25: reappear on the target's floor (its controller +0x6B4), not at its current
    # height; MKT always rises from the floor. False reproduces v08-v24.
    emerge_on_floor: bool = False
    floor_bound: int = 0x20000  # accept the floor only within 512 units below the target
    # v40: when the target's floor is not usable (e.g. 0x7FBC00, "no floor below", set by
    # 0x80024BA8 while it is knocked/flying high), use Sektor's own floor (he is grounded
    # by then) if it is below the target, before falling back to the target's height.
    # False reproduces v25-v39 (an airborne target made Sektor reappear in mid-air).
    own_floor_fallback: bool = False


FRAME = host.Frame()


def emit_action(a: Assembler, p: TeleportParams) -> None:
    m = motion()
    s = p.scripts
    host.enter_action(a, FRAME, p.strike_words)
    a.li("s6", 0)
    host.load_controller(a)
    host.set_special_lock(a)
    host.set_action_id(a, UPPERCUT_ACTION_ID)
    host.special_begin(a)
    host.play_sound(a, p.sound_event)
    host.find_target(a, "exit", p.range_units)
    host.start_animation(a, s.sink, 1)

    # Airborne start: fall on the donor sink curve first; s7 = curve index reached.
    a.li("s7", 0)
    a.lw("t0", host.ACTOR_Y, "s1")
    a.lw("t1", host.CTRL_GROUND, "s0")
    a.slt("t2", "t0", "t1")
    a.beqz("t2", "grounded")
    a.li("t0", m.fall_velocity)
    a.sw("t0", host.ACTOR_YVEL, "s1")
    a.li("t0", m.fall_gravity)
    a.sw("t0", host.ACTOR_GRAVITY, "s1")
    a.li("s2", p.fall_cap)
    a.label("fall")
    host.sleep_tick(a)
    a.addiu("s7", "s7", 1)
    a.lw("t0", host.ACTOR_Y, "s1")
    a.lw("t1", host.CTRL_GROUND, "s0")
    a.slt("t2", "t0", "t1")
    a.beqz("t2", "fallen")
    a.addiu("s2", "s2", -1)
    a.bnez("s2", "fall")
    a.label("fallen")
    host.stop(a)
    a.sw("zero", host.ACTOR_GRAVITY, "s1")
    a.sw("zero", host.ACTOR_YVEL, "s1")
    a.sh("zero", host.CTRL_AIRBORNE, "s0")
    a.label("grounded")

    # Continue the sink from the curve index already reached (capped at the last pose).
    a.li("t0", s.sink_steps - 1)
    a.slt("t1", "t0", "s7")
    a.beqz("t1", "kok")
    a.move("s7", "t0")
    a.label("kok")
    a.sll("t0", "s7", 2)
    a.lw("t1", host.ACTOR_FILE_BASE, "s1")
    a.addu("t0", "t0", "t1")
    a.li("t1", s.sink)
    a.addu("t0", "t0", "t1")
    a.sw("t0", host.CTRL_SCRIPT_CURSOR, "s0")
    host.advance_animation(a)
    a.li("s2", s.sink_steps)
    a.subu("s2", "s2", "s7")
    a.label("sink")
    host.sleep_tick(a)
    host.rate_step(a)
    a.addiu("s2", "s2", -1)
    a.bnez("s2", "sink")

    _emit_reposition(a, p)

    a.label("emerge")
    host.sleep_ticks(a, p.hidden_ticks, "hidden")
    a.lw("s7", host.ACTOR_Y, "s1")  # own ground reference for landing
    a.li("s3", 0)  # s3 = strike connected
    host.start_animation(a, s.drop, 1)
    a.li("s2", s.emerge_steps)
    a.label("emg")
    host.sleep_tick(a)
    host.rate_step(a)
    a.addiu("s2", "s2", -1)
    a.bnez("s2", "emg")

    _emit_air_arc(a, p, m)

    a.label("landed")
    host.stop(a)
    a.sw("zero", host.ACTOR_GRAVITY, "s1")
    a.sw("zero", host.ACTOR_YVEL, "s1")
    a.sh("zero", host.CTRL_AIRBORNE, "s0")
    host.set_cursor(a, s.land_a)
    host.advance_animation(a)
    host.sleep_ticks(a, p.landing_ticks[0], "la")
    host.set_cursor(a, s.land_b)
    host.advance_animation(a)
    host.sleep_ticks(a, p.landing_ticks[1], "lb")
    a.label("exit")
    host.exit_action(a)


def _emit_reposition(a: Assembler, p: TeleportParams) -> None:
    """Past the target on the far side, wall-aware; nudge a cornered target; face it.

    Far-side placement makes the uppercut knock the target away from the wall, which
    avoids the stock corner pushback 0x80052EA8 (proof v08).
    """

    host.find_target(a, "emerge", p.range_units)
    if p.emerge_on_floor:
        a.lw("t0", host.CTRL_GROUND, "v0")  # v0 = target controller, before any call
        a.sw("t0", 0x1C, "sp")
    host.face_opponent(a)  # forward = toward the target
    a.lw("t0", host.ACTOR_X, "s4")
    a.lw("t1", host.ACTOR_X, "s1")
    a.slt("s6", "t0", "t1")  # s6 = 1: target is on Sektor's -x side
    if p.emerge_on_floor:
        # Target floor saved at 0x1C. y grows downward; airborne y < floor.
        a.lw("t0", 0x1C, "sp")
        a.lw("t1", host.ACTOR_Y, "s4")
        a.sw("t1", 0x18, "sp")  # fallback: the target's own height (v08-v24)
        a.subu("t2", "t0", "t1")
        a.bltz("t2", "floor_own" if p.own_floor_fallback else "floor_set")
        a.li("t3", p.floor_bound)
        a.slt("t3", "t3", "t2")
        a.bnez("t3", "floor_own" if p.own_floor_fallback else "floor_set")
        a.sw("t0", 0x18, "sp")
        if p.own_floor_fallback:
            a.beq("zero", "zero", "floor_set")
            a.label("floor_own")
            a.lw("t0", host.CTRL_GROUND, "s0")
            a.subu("t2", "t0", "t1")
            a.bltz("t2", "floor_set")  # own floor above the target: keep its height
            a.li("t3", 0x7FBC00)
            a.beq("t0", "t3", "floor_set")  # no floor
            a.sw("t0", 0x18, "sp")
        a.label("floor_set")
        fields: tuple[int, ...] = (host.ACTOR_PATH_PARAM, host.ACTOR_X, host.ACTOR_Z)
    else:
        fields = (host.ACTOR_PATH_PARAM, host.ACTOR_X, host.ACTOR_Y, host.ACTOR_Z)
    for field in fields:
        a.lw("t0", field, "s4")
        a.sw("t0", field, "s1")
    if p.emerge_on_floor:
        a.lw("t0", 0x18, "sp")
        a.sw("t0", host.ACTOR_Y, "s1")
    a.move("a0", "s4")
    a.addiu("a1", "sp", 0x10)
    a.addiu("a2", "sp", 0x14)
    a.jal(host.F_WALL_DISTANCE)
    a.lw("t0", 0x14, "sp")
    a.beqz("s6", "far_ok")
    a.lw("t0", 0x10, "sp")  # wall room on the far side
    a.label("far_ok")
    a.addiu("s5", "t0", -p.wall_margin)
    a.li("t1", p.behind)
    a.slt("t2", "t1", "s5")
    a.beqz("t2", "r_le")
    a.move("s5", "t1")  # s5 = min(behind, room)
    a.label("r_le")
    a.bgez("s5", "r_pos")
    a.li("s5", 0)
    a.label("r_pos")
    host.offset_actor(a, "s1", "s5")
    a.li("t1", p.min_separation)
    a.slt("t2", "s5", "t1")
    a.beqz("t2", "placed")
    a.li("t1", p.min_separation)
    a.subu("s2", "t1", "s5")  # cornered: nudge the target out
    a.lw("s3", host.ACTOR_X, "s4")
    host.offset_actor(a, "s4", "s2")
    a.lw("t0", host.ACTOR_X, "s4")
    a.slt("t1", "s3", "t0")
    a.beq("t1", "s6", "placed")  # moved toward Sektor's start side?
    a.move("a0", "s4")
    a.subu("a1", "zero", "s2")
    a.sll("a1", "a1", 1)
    a.move("a2", "zero")
    a.jal(host.F_OFFSET)
    a.label("placed")
    host.face_opponent(a)  # turn around to face the target


def _emit_air_arc(a: Assembler, p: TeleportParams, m: Motion) -> None:
    """Uppercut arc integrated by the action itself (engine-equivalent), strike while rising.

    v += 2g (0x80024F3C), y += (v>>8)+(v>>7) (0x80018080); velocity/gravity fields kept 0;
    +0xF0 re-set every tick; the airborne counter +0x6B2 kept counting (v07) so the per-tick
    floor check 0x80024BA8 does not install the stock fall routine.
    """

    a.li("s5", m.emerge_velocity)
    a.sw("zero", host.ACTOR_YVEL, "s1")
    a.sw("zero", host.ACTOR_GRAVITY, "s1")
    a.sw("zero", host.ACTOR_XVEL, "s1")
    a.sw("zero", host.ACTOR_ZVEL, "s1")
    a.li("s2", p.air_cap)
    a.label("air")
    a.lhu("t0", host.CTRL_AIRBORNE, "s0")
    a.addiu("t0", "t0", 1)
    a.sh("t0", host.CTRL_AIRBORNE, "s0")
    host.sleep_tick(a)
    host.rate_step(a)
    a.li("t0", 1)
    a.sw("t0", host.ACTOR_NO_GROUND_STICK, "s1")
    a.li("t1", m.gravity_nohit)
    a.beqz("s3", "g_ok")
    a.li("t1", m.gravity_hit)
    a.label("g_ok")
    a.sll("t1", "t1", 1)
    a.addu("s5", "s5", "t1")
    a.sra("t0", "s5", 8)
    a.sra("t1", "s5", 7)
    a.addu("t0", "t0", "t1")
    a.lw("t1", host.ACTOR_Y, "s1")
    a.addu("t1", "t1", "t0")
    a.sw("t1", host.ACTOR_Y, "s1")
    a.sw("zero", host.ACTOR_YVEL, "s1")
    a.sw("zero", host.ACTOR_GRAVITY, "s1")
    a.bgez("s5", "landcheck")
    a.bnez("s3", "landcheck")
    host.strike(a, FRAME, "landcheck")
    a.li("s3", 1)
    a.label("landcheck")
    a.bltz("s5", "airnext")
    a.lw("t0", host.ACTOR_Y, "s1")
    a.slt("t2", "t0", "s7")
    a.beqz("t2", "snap")
    a.label("airnext")
    a.addiu("s2", "s2", -1)
    a.bnez("s2", "air")
    a.label("snap")
    a.sw("s7", host.ACTOR_Y, "s1")
    a.sw("zero", host.ACTOR_NO_GROUND_STICK, "s1")


def emit_condition(a: Assembler, p: TeleportParams, label: str = "cond") -> None:
    """Descriptor condition: stock LK condition, no special in progress, a target in range.

    Returns 0x8000 (accept) or 0x4000 (reject); the parser 0x8004A0E0 stops on 0x4000.
    Rejecting up front avoids an airborne start with no target (proof v05).
    """

    a.label(label)
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x1C, "sp")
    a.sw("s1", 0x18, "sp")
    a.sw("s4", 0x14, "sp")
    a.jal(STOCK_LK_CONDITION)
    a.andi("v0", "v0", 0xFFFF)
    a.li("t0", 0x4000)
    a.beq("v0", "t0", "c_rej")
    a.lui("t0", host.hi(host.SPECIAL_LOCK))
    a.lh("t1", host.lo(host.SPECIAL_LOCK), "t0")
    a.bnez("t1", "c_rej")
    a.lui("t0", host.hi(host.PLAYER_CTRL))
    a.lw("t0", host.lo(host.PLAYER_CTRL), "t0")
    a.lw("s1", host.CTRL_ACTOR, "t0")
    host.find_target(a, "c_rej", p.range_units)
    a.li("v0", 0x8000)
    a.beq("zero", "zero", "c_ret")
    a.label("c_rej")
    a.li("v0", 0x4000)
    a.label("c_ret")
    a.lw("ra", 0x1C, "sp")
    a.lw("s1", 0x18, "sp")
    a.lw("s4", 0x14, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)


def assemble(base: int, p: TeleportParams) -> Assembler:
    """Action, sound player and descriptor condition, in the proven payload order."""

    a = Assembler(base)
    emit_action(a, p)
    host.emit_sound_player(a)
    emit_condition(a, p)
    return a
