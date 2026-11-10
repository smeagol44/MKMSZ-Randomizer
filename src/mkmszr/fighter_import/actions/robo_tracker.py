"""Sektor's heat-seeking rocket (MKT ``do_robo_zap2`` / ``rocket2_proc``) on the MKMSZ host.

Donor, MKT USA Rev. 2 N64 (checked against the arcade MK3 ``MKZAP.ASM`` lineage):

* ``do_robo_zap2`` ``0x8007BF38``: special init, ``ochar_sound 0x0C`` (target sound), then
  the straight rocket's own launcher ``0x8007C068`` (chest open, placement, sitting duck,
  ``sleep 0x20``, chest close) with ``rocket2_proc`` ``0x8007C25C`` instead of ``rocket1_proc``.
* ``rocket2_proc``: ``ochar_sound 4`` (cruise rocket), timeout ``0x80`` ticks, speed
  ``0x4CCCC`` at anirate 3, strike ``0x12``, and a crosshair object (robot secondary
  animation 5, heap descriptor ``0x2C64``, palette ``0x800BC3D0``) kept on the opponent at
  (−12, +27) px, in front of the players. Then per tick: crosshair update, sleep 1,
  ``point_rocket`` (``0x8007CA34``: one of eight direction animations from the velocity, flipped
  by its x sign), ``rocket_smoke`` (direction-dependent puff placement) and the phase table
  ``0x800AB220``: 8 ticks straight, 16 ticks climbing (``vy -= 0x8800``), then
  ``rocket_hunt`` ``0x8007C4AC``.
* ``rocket_hunt`` per tick: aim at the opponent + ``0x36`` px down; explode within 6 px
  (rough distance); unit vector ``× 0x33333``; ``v = v + u − v/16``; renormalise ``v`` to
  5 px/tick. Distances are MKT's rough hypotenuse ``0x8006C9C0`` (``max + min/2``).
  Explodes on timeout. The strike is checked only at the explosion.

Host: the HP command shares the straight rocket's whole launch (the lifted Ice root, see
:mod:`.robo_zap`); a payload flag set by each command's callback stub selects the launch
sound and start speed and, in the flight child, the homing flight. The flight runs in the
stock projectile loop ``0x8004CC50`` with a per-tick callback that runs two donor ticks,
so the stock collision ends it on contact. A follower effect process carries the crosshair
and removes itself when the rocket's heartbeat stops.

Target (proof v45): not the controller's last-opponent link ``+0x640`` (after a kill it
still names the dead enemy, which the v44 rocket and crosshair chased into a pit) but the
nearest living enemy as for the teleport: classes 2-4, health ``+0x654`` non-zero, on the
player's path and within the teleport's square range of the player. The HP condition
refuses the move when there is none. The flight keeps that target while it lives and is
present, otherwise takes the next one the same way, or flies on unguided without a
crosshair.

Proximity (proof v43): each donor hunt step measures from the rocket's position at that
donor tick (actor position plus the earlier steps of the host tick) and applies the donor
6-px test. Within it, the rocket is placed on the aim point and stops, so the stock strike
right after the callback resolves the hit there (MKT checks the strike only at the
explosion). If that strike does not connect (e.g. an invulnerable target), the next call
explodes the rocket without a strike and ends it through the loop's own exit
``0x8004CDF8``. Proof v42 had no proximity test: a rocket whose box missed the target
circled through it.

Recorded differences from MKT: the stock per-tick collision still runs during the whole
flight (so a contact during the first 24 donor ticks also hits); the stock loop deletes an
off-screen rocket (MKT keeps it); a timeout explodes without a strike.
"""

from __future__ import annotations

from collections.abc import Callable

from .. import effects, host
from ..host import UNITS_PER_TEXEL, hi, lo
from ..mips import Assembler
from . import robo_zap

# ---- donor facts ----------------------------------------------------------------------
TARGET_SOUND_OCHAR, CRUISE_SOUND_OCHAR = 0x0C, 4
START_SPEED = 0x4CCCC
PHASE_TICKS = (8, 16)  # straight, climb; then hunt until it ends
CLIMB = 0x8800
AIM_Y = 0x36  # px below the opponent's reference
STEER = 0x33333
HUNT_SPEED = 5
DETONATE_PX = 6  # rocket_hunt: explode when the rough distance to the aim point is below
TIMEOUT_TICKS = 0x80  # donor ticks (= the stock loop's 0x40 host iterations)
ROCKET_ANIMATION = 0x1300  # robot heap: eight two-frame parts, 0x14 bytes apart
DIRECTION_PARTS = 8  # 12, 1, 2, 3, 6, 5, 4, 3 o'clock
TARGET_DESCRIPTOR, TARGET_PALETTE = 0x2C64, 0x800BC3D0
TARGET_OFFSET = (-12, 27)  # px from the opponent (lineup + multi_adjust)
SMOKE_PLACEMENT = ((0, 20), (-6, 13), (-12, 6), (5, 0), (0, -20), (-6, -13), (-12, -6), (5, 0))
SMOKE_X_SHIFT = -0x18  # rocket_puff: x - 0x18

# ---- host -----------------------------------------------------------------------------
HP_RECORD_ROM = 0xB1C80  # 0x800B1080: stock Freeze on Contact (D,F,F + HP), tier 8
COMMAND_RIGHT, COMMAND_LEFT = (8, 7, 9), (9, 7, 8)  # F,D,B newest first (7 Down, 8/9 L/R)
COMMAND_WINDOW = 0x3C  # stock three-input HP window
HP_MASK = 0x10
LP_ICE_CONDITION = 0x8004A304  # tier >= 1 and Ice cost, as the straight rocket
# Straight rocket: the stock LP Ice Blast record (0x800B0F38, D,F + LP) -> MKT's F,F + LP.
LP_RECORD_ROM = 0xB1B38
LP_MASK = 0x80
STRAIGHT_RIGHT, STRAIGHT_LEFT = (9, 9), (8, 8)  # F,F (9/8 = forward facing right/left)
STRAIGHT_WINDOW = 0x18  # as the F,F + LK teleport record
# Double Missile (MKT special 51, B,B,F + LP): replaces the stock Ice Clone record
# (0x800B0F0C, D,B + LP; user choice, proof v46); straight rocket condition.
DOUBLE_RECORD_ROM = 0xB1B0C
DOUBLE_RIGHT, DOUBLE_LEFT = (9, 8, 8), (8, 9, 9)  # B,B,F newest first
F_FLIP = 0x8003188C
F_FIND_CLASS = 0x80028510  # (class, mask) -> first other process with +0x6D8 & mask == class
ENEMY_CLASSES = (2, 3, 4)  # ordinary enemy spawn slots 0x71..0x73 (the strike's victim scan)
CTRL_HEALTH = 0x654  # zero once dead (the strike's victim scan skips it)
TARGET_RANGE = 592  # world units, square, as the F,F + LK teleport (robo_teleport)
F_FLIGHT_END = 0x8004CDF8  # (actor): the stock loop's exit (unlink, process exit); no return
# Rocket process controller fields (free during the flight: only 0x8002830C copies them).
VX, VY, PHASE, DIR, TICKS = 0x6F4, 0x6F8, 0x6FC, 0x700, 0x704
LOOP_CALLS = 0x41  # the stock loop calls the callback 0x41 times, then deletes the rocket
DETONATE = 3  # PHASE high half after the proximity test fired


def rough(x: int, y: int) -> int:
    """MKT ``0x8006C9C0``: ``max(|x|,|y|) + min(|x|,|y|) / 2`` (arithmetic shifts)."""

    a, b = abs(x), abs(y)
    return (b >> 1) + a if b < a else (a >> 1) + b


def _div(n: int, d: int) -> int:
    q = abs(n) // abs(d)
    return q if (n < 0) == (d < 0) else -q


def _s32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - (1 << 32) if v & 0x80000000 else v


def hunt(vx: int, vy: int, dx: int, dy: int) -> tuple[int, int]:
    """One donor ``rocket_hunt`` step; ``(dx, dy)`` px to the aim point (``dy`` incl. AIM_Y)."""

    ux, uy = _s32(dx * STEER), _s32(dy * STEER)
    n = max(rough(ux, uy) >> 16, 1)
    ux, uy = _div(ux, n), _div(uy, n)
    vx, vy = _s32(vx + ux - (vx >> 4)), _s32(vy + uy - (vy >> 4))
    n = max(rough(vx, vy) >> 16, 1)
    return _s32(_div(vx, n) * HUNT_SPEED), _s32(_div(vy, n) * HUNT_SPEED)


def near(dx: int, dy: int) -> bool:
    """``rocket_hunt``'s explosion test, ``(dx, dy)`` px to the aim point."""

    return rough(dx, dy) < DETONATE_PX


def direction(vx: int, vy: int) -> int:
    """``point_rocket``: 0 = up … 3 = level; +4 when moving down."""

    ax, ay = abs(vx), abs(vy)
    if ay >= (7 * ax) >> 1:
        d = 0
    elif ay >= ax:
        d = 1
    elif ax <= (7 * ay) >> 1:
        d = 2
    else:
        d = 3
    return d + 4 if vy > 0 else d


def host_velocity(donor_sum: int) -> int:
    """Two donor ticks' displacement (16.16 px) -> host +0x14/+0x18 (as robo_zap)."""

    return _div(2 * donor_sum, 3)


def smoke_offsets() -> list[int]:
    """Per direction: ``dy << 16 | dx`` whole units, for an unflipped rocket."""

    out = []
    for x, y in SMOKE_PLACEMENT:
        dx, dy = (x + SMOKE_X_SHIFT) * UNITS_PER_TEXEL, y * UNITS_PER_TEXEL
        out.append(((dy & 0xFFFF) << 16) | (dx & 0xFFFF))
    return out


def _record(
    mask: int, selector: int, action: int, window: int, right: tuple[int, ...],
    left: tuple[int, ...], condition: int = LP_ICE_CONDITION,
) -> bytes:  # fmt: skip
    """A special-move record (``0x2C`` bytes): masks, selector, condition, action,
    window, then up to six command tokens per facing, newest first."""

    rec = bytearray(0x2C)
    rec[0:2] = mask.to_bytes(2, "big")
    rec[2:4] = mask.to_bytes(2, "big")
    rec[4:8] = selector.to_bytes(4, "big")
    rec[8:12] = condition.to_bytes(4, "big")
    rec[12:16] = action.to_bytes(4, "big")
    rec[16:18] = window.to_bytes(2, "big")
    for i, tok in enumerate(right):
        rec[0x12 + 2 * i : 0x14 + 2 * i] = tok.to_bytes(2, "big")
    for i, tok in enumerate(left):
        rec[0x1E + 2 * i : 0x20 + 2 * i] = tok.to_bytes(2, "big")
    return bytes(rec)


def double_record(action: int, condition: int = LP_ICE_CONDITION) -> bytes:
    """The LP record for the Double Missile on ``B,B,F + LP`` (three inputs: the stock
    three-input window). R4: ``condition`` = :mod:`.sektor_tiers` ``tier_double``."""

    return _record(LP_MASK, 1, action, COMMAND_WINDOW, DOUBLE_RIGHT, DOUBLE_LEFT, condition)


def descriptor_record(action: int, condition: int = LP_ICE_CONDITION) -> bytes:
    """The HP special-move record for ``F,D,B + HP`` (selector 0 refuses an airborne
    start); ``condition`` is ``trk_cond`` in the proofs (v45)."""

    return _record(HP_MASK, 0, action, COMMAND_WINDOW, COMMAND_RIGHT, COMMAND_LEFT, condition)


def straight_record(action: int, condition: int = LP_ICE_CONDITION) -> bytes:
    """The LP record for the straight rocket on ``F,F + LP`` (the stock record's mask,
    selector 1 and condition; R4: ``tier_straight``, which refuses an airborne start)."""

    return _record(LP_MASK, 1, action, STRAIGHT_WINDOW, STRAIGHT_RIGHT, STRAIGHT_LEFT, condition)


# ---- donor art --------------------------------------------------------------------------
def direction_frames(heap: bytes, dictionary: bytes) -> list[tuple[effects.EffectFrame, ...]]:
    """The two frames of each of the eight direction parts of the rocket animation."""

    word = lambda o: int.from_bytes(heap[o : o + 4], "big")
    parts = []
    for k in range(DIRECTION_PARTS):
        base = ROCKET_ANIMATION + 0x14 * k
        if word(base + 8) != 1 or word(base + 12) != base:
            raise ValueError(f"rocket part {k + 1} is not a two-frame loop")
        parts.append(
            tuple(
                effects.heap_descriptor_frame(heap, word(word(base + 4 * i)), dictionary)
                for i in range(2)
            )
        )
    return parts


def target_art(mkt: bytes, heap: bytes, dictionary: bytes) -> effects.EffectArt:
    frame = effects.heap_descriptor_frame(heap, TARGET_DESCRIPTOR, dictionary)
    return effects.EffectArt((frame,), effects.mkt_palette(mkt, TARGET_PALETTE))


# ---- payload code -------------------------------------------------------------------------
def _emit_abs(a: Assembler, out: str, src: str, tmp: str) -> None:
    a.sra(tmp, src, 31)
    a.xor(out, src, tmp)
    a.subu(out, out, tmp)


def _emit_rough(a: Assembler, out: str, x: str, y: str, ta: str, tb: str, tag: str) -> None:
    _emit_abs(a, ta, x, out)
    _emit_abs(a, tb, y, out)
    a.slt(out, tb, ta)
    a.beqz(out, tag + "_ymax")
    a.sra(out, tb, 1)
    a.addu(out, out, ta)
    a.beq("zero", "zero", tag + "_done")
    a.label(tag + "_ymax")
    a.sra(out, ta, 1)
    a.addu(out, out, tb)
    a.label(tag + "_done")


def _emit_at_least_one(a: Assembler, reg: str, tag: str) -> None:
    """``reg = max(reg, 1)`` for ``reg >= 0`` (a rough distance >> 16)."""

    a.bnez(reg, tag + "_nz")
    a.li(reg, 1)
    a.label(tag + "_nz")


def emit_data(a: Assembler, loops: list[int], prefix: str = "trk") -> None:
    """Flag, heartbeat, followed controller, target, direction loops, smoke offsets."""

    if len(loops) != DIRECTION_PARTS:
        raise ValueError("one loop per direction")
    a.label(prefix + "_flag")
    a.raw(0)
    a.label(prefix + "_heartbeat")
    a.raw(0)
    a.label(prefix + "_follow")
    a.raw(0)
    a.label(prefix + "_aim")
    a.raw(0)
    a.label(prefix + "_double")  # robo_zap.emit_double_launch state
    a.raw(0)
    a.label(prefix + "_loops")
    for off in loops:
        a.raw(off)
    a.label(prefix + "_smoke_offsets")
    for word in smoke_offsets():
        a.raw(word)


def emit_command_stubs(
    a: Assembler, ice_callback: int, target_event: int, player: str = "play",
    extra_costs: dict[str, int] | None = None,
) -> None:  # fmt: skip
    """``trk_cb_straight`` (F,F + LP), ``trk_cb_double`` (B,B,F + LP) and
    ``trk_cb_homing`` (F,D,B + HP) record actions: set the homing flag and the double
    state, then continue in the lifted Ice callback with ``ra`` unchanged.

    ``extra_costs`` (R4, :data:`.sektor_tiers.EXTRA_COST`): Ice taken by the double and
    homing stubs on top of the root's own ``0x20``; None reproduces v42-v53."""

    from . import sektor_tiers

    costs = extra_costs or {}
    a.label("trk_cb_double")
    if costs.get("double"):
        sektor_tiers.emit_charge(a, costs["double"])
    a.la("t0", "trk_double")
    a.li("t1", robo_zap.DOUBLE_REQUESTED)
    a.beq("zero", "zero", "trk_cb_flat")
    a.label("trk_cb_straight")
    a.la("t0", "trk_double")
    a.move("t1", "zero")
    a.label("trk_cb_flat")
    a.sw("t1", 0, "t0")
    a.la("t0", "trk_flag")
    a.sw("zero", 0, "t0")
    a.lui("t9", hi(ice_callback))
    a.addiu("t9", "t9", lo(ice_callback))
    a.jr("t9")
    a.nop()

    a.label("trk_cb_homing")
    if costs.get("homing"):
        sektor_tiers.emit_charge(a, costs["homing"])
    a.la("t0", "trk_double")
    a.sw("zero", 0, "t0")
    a.la("t0", "trk_flag")
    a.li("t1", 1)
    a.sw("t1", 0, "t0")
    a.addiu("sp", "sp", -0x18)
    a.sw("ra", 0x14, "sp")
    host.play_sound(a, target_event, player)
    a.lw("ra", 0x14, "sp")
    a.addiu("sp", "sp", 0x18)
    a.lui("t9", hi(ice_callback))
    a.addiu("t9", "t9", lo(ice_callback))
    a.jr("t9")
    a.nop()


def on_create(straight_launch: int, homing_launch: int) -> Callable[[Assembler], None]:
    """Creation code (``s0`` = rocket actor): straight as :func:`robo_zap.on_create`;
    homing: the folded donor start speed (facing-signed) and the cruise sound."""

    straight = robo_zap.on_create(straight_launch)

    def emit(a: Assembler) -> None:
        a.la("t0", "trk_flag")
        a.lw("t0", 0, "t0")
        a.bnez("t0", "trk_create_homing")
        straight(a)
        a.beq("zero", "zero", "trk_create_done")
        a.label("trk_create_homing")
        a.li("t0", host_velocity(2 * START_SPEED))
        a.lhu("t1", 0x8C, "s0")
        a.andi("t1", "t1", 0x10)
        a.beqz("t1", "trk_create_v")
        a.subu("t0", "zero", "t0")
        a.label("trk_create_v")
        a.sw("t0", host.ACTOR_XVEL, "s0")
        host.play_sound(a, homing_launch)
        a.label("trk_create_done")

    return emit


def emit_child(a: Assembler, hit_child: int, target_desc: str, spawn: str = "trk_spawn") -> None:
    """``trk_child``: the flight child when the flag is set (entered from ``zap_child``)."""

    a.label("trk_child")
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x18, "sp")
    a.sw("s0", 0x14, "sp")
    a.sw("s1", 0x10, "sp")
    a.lui("s0", hi(host.CURRENT_CTRL))
    a.lw("s0", lo(host.CURRENT_CTRL), "s0")
    a.lw("s1", host.CTRL_ACTOR, "s0")
    a.li("t1", 0x100)
    a.sw("t1", 0x69C, "s0")  # as the stock child
    a.la("t0", "trk_loops")
    a.lw("t0", 4 * 3, "t0")  # level flight
    a.lui("t1", hi(robo_zap.FILE87_BASE_PTR))
    a.lw("t1", lo(robo_zap.FILE87_BASE_PTR), "t1")
    a.addu("t0", "t0", "t1")
    a.sw("t0", host.CTRL_SCRIPT_CURSOR, "s0")
    a.li("t0", START_SPEED)
    a.lhu("t1", 0x8C, "s1")
    a.andi("t1", "t1", 0x10)
    a.beqz("t1", "trk_child_v")
    a.subu("t0", "zero", "t0")
    a.label("trk_child_v")
    a.sw("t0", VX, "s0")
    a.sw("zero", VY, "s0")
    a.li("t0", PHASE_TICKS[0] - 2 * robo_zap.CHILD_START_TICKS)  # donor ticks already flown
    a.sw("t0", PHASE, "s0")
    a.li("t0", 3)
    a.sw("t0", DIR, "s0")
    a.sw("zero", TICKS, "s0")
    a.la("t0", "trk_heartbeat")
    a.lw("t1", 0, "t0")
    a.addiu("t1", "t1", 1)
    a.sw("t1", 0, "t0")
    a.jal_label("trk_check")  # target controller (also trk_follow) or 0
    a.beqz("v0", "trk_child_fly")
    a.lw("a0", host.CTRL_ACTOR, "v0")
    a.beqz("a0", "trk_child_fly")
    a.la("a1", target_desc)
    a.move("a2", "zero")
    a.li("a3", effects.FRONT_SUBLAYER)
    a.jal_label(spawn)
    a.label("trk_child_fly")
    a.move("a0", "s1")
    a.li("a1", host_velocity(2 * START_SPEED))
    a.li("a2", 1)
    a.jal(robo_zap.F_PROJECTILE_SETUP)
    a.la("t1", "trk_callback")
    a.sw("t1", 0x70C, "s0")
    a.move("a0", "s1")
    a.li("a1", robo_zap.FLIGHT_STRIKE_SELECTOR)
    a.lui("t9", hi(robo_zap.F_FLIGHT_LOOP))
    a.addiu("t9", "t9", lo(robo_zap.F_FLIGHT_LOOP))
    a.jalr("t9")
    # contact: the stock tail's switch to the hit process, with the imported hit child
    a.lui("t0", hi(host.CURRENT_CTRL))
    a.lw("t0", lo(host.CURRENT_CTRL), "t0")
    a.li("a1", hit_child)
    a.addiu("a0", "t0", 8)
    a.addiu("v1", "t0", 0x620)
    a.sw("a1", host.CTRL_CALLBACK, "t0")
    a.sw("v1", 0xC, "t0")
    a.sw("v1", 0x10, "t0")
    a.sw("a1", 8, "t0")
    a.jal(host.F_CONTEXT_SWITCH)
    a.lw("ra", 0x18, "sp")
    a.lw("s0", 0x14, "sp")
    a.lw("s1", 0x10, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)


def _abs_over(a: Assembler, field: int, ref: str, cand: str, limit: int, fail: str) -> None:
    """``t0 = |cand.field - ref.field|``; branch to ``fail`` when above ``limit`` units."""

    a.lw("t0", field, cand)
    a.lw("t1", field, ref)
    a.subu("t0", "t0", "t1")
    _emit_abs(a, "t0", "t0", "t9")
    a.li("t1", limit << 8)
    a.slt("t2", "t1", "t0")
    a.bnez("t2", fail)


def emit_targeting(a: Assembler, range_units: int = TARGET_RANGE) -> None:
    """``trk_pick() -> v0``: the nearest (x) living enemy controller on the player's path
    within ``range_units`` (square) of the player, or 0. ``trk_check() -> v0``: keep
    ``trk_aim`` while it is a present, living enemy, else ``trk_pick``; stores the
    result in ``trk_aim`` and ``trk_follow``. Both preserve s0-s7."""

    a.label("trk_pick")
    a.addiu("sp", "sp", -0x28)
    a.sw("ra", 0x24, "sp")
    a.sw("s0", 0x20, "sp")
    a.sw("s1", 0x1C, "sp")
    a.sw("s2", 0x18, "sp")
    a.sw("s3", 0x14, "sp")
    a.lui("s3", hi(host.PLAYER_CTRL))
    a.lw("s3", lo(host.PLAYER_CTRL), "s3")
    a.move("s1", "zero")
    a.beqz("s3", "trk_pick_done")
    a.lw("s3", host.CTRL_ACTOR, "s3")
    a.beqz("s3", "trk_pick_done")
    a.lui("s2", 0x7FFF)
    a.li("s0", ENEMY_CLASSES[0])
    a.label("trk_pick_loop")
    a.move("a0", "s0")
    a.li("a1", 0xFFFF)
    a.jal(F_FIND_CLASS)
    a.beqz("v0", "trk_pick_next")
    a.lhu("t0", CTRL_HEALTH, "v0")
    a.beqz("t0", "trk_pick_next")
    a.lw("t3", host.CTRL_ACTOR, "v0")
    a.beqz("t3", "trk_pick_next")
    a.lw("t0", host.ACTOR_PATH, "t3")
    a.lw("t1", host.ACTOR_PATH, "s3")
    a.bne("t0", "t1", "trk_pick_next")
    _abs_over(a, host.ACTOR_Y, "s3", "t3", range_units, "trk_pick_next")
    _abs_over(a, host.ACTOR_X, "s3", "t3", range_units, "trk_pick_next")
    a.slt("t2", "t0", "s2")
    a.beqz("t2", "trk_pick_next")
    a.move("s2", "t0")
    a.move("s1", "v0")
    a.label("trk_pick_next")
    a.addiu("s0", "s0", 1)
    a.slti("t0", "s0", ENEMY_CLASSES[-1] + 1)
    a.bnez("t0", "trk_pick_loop")
    a.label("trk_pick_done")
    a.move("v0", "s1")
    a.lw("ra", 0x24, "sp")
    a.lw("s0", 0x20, "sp")
    a.lw("s1", 0x1C, "sp")
    a.lw("s2", 0x18, "sp")
    a.lw("s3", 0x14, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x28)

    a.label("trk_check")
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x1C, "sp")
    a.sw("s0", 0x18, "sp")
    a.sw("s1", 0x14, "sp")
    a.la("t0", "trk_aim")
    a.lw("s0", 0, "t0")
    a.beqz("s0", "trk_check_pick")
    a.li("s1", ENEMY_CLASSES[0])
    a.label("trk_check_loop")  # still a present enemy process?
    a.move("a0", "s1")
    a.li("a1", 0xFFFF)
    a.jal(F_FIND_CLASS)
    a.beq("v0", "s0", "trk_check_alive")
    a.addiu("s1", "s1", 1)
    a.slti("t0", "s1", ENEMY_CLASSES[-1] + 1)
    a.bnez("t0", "trk_check_loop")
    a.beq("zero", "zero", "trk_check_pick")
    a.label("trk_check_alive")
    a.lhu("t0", CTRL_HEALTH, "s0")
    a.beqz("t0", "trk_check_pick")
    a.lw("t0", host.CTRL_ACTOR, "s0")
    a.bnez("t0", "trk_check_store")
    a.label("trk_check_pick")
    a.jal_label("trk_pick")
    a.move("s0", "v0")
    a.label("trk_check_store")
    a.la("t0", "trk_aim")
    a.sw("s0", 0, "t0")
    a.la("t0", "trk_follow")
    a.sw("s0", 0, "t0")
    a.move("v0", "s0")
    a.lw("ra", 0x1C, "sp")
    a.lw("s0", 0x18, "sp")
    a.lw("s1", 0x14, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)


def emit_condition(a: Assembler, label: str = "trk_cond", base: str | None = None) -> None:
    """HP record condition: the stock LP Ice condition (R4: the payload condition ``base``,
    :mod:`.sektor_tiers` ``tier_homing``), then a target (``trk_pick``, stored in
    ``trk_aim``); 0x8000 accept, 0x4000 refuse (no target: no move)."""

    a.label(label)
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x1C, "sp")
    if base is None:
        a.lui("t9", hi(LP_ICE_CONDITION))
        a.addiu("t9", "t9", lo(LP_ICE_CONDITION))
        a.jalr("t9")
    else:
        a.jal_label(base)
    a.andi("v0", "v0", 0xFFFF)
    a.li("t0", 0x4000)
    a.beq("v0", "t0", label + "_ret")
    a.jal_label("trk_pick")
    a.la("t0", "trk_aim")
    a.sw("v0", 0, "t0")
    a.beqz("v0", label + "_refuse")
    a.li("v0", 0x8000)
    a.beq("zero", "zero", label + "_ret")
    a.label(label + "_refuse")
    a.li("v0", 0x4000)
    a.label(label + "_ret")
    a.lw("ra", 0x1C, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)


def emit_hunt(a: Assembler) -> None:
    """``trk_hunt``: one donor hunt step on the state at ``s0`` (rocket controller),
    rocket actor ``s1``; ``s2``/``s3`` hold this host tick's displacement sums including
    the current step's velocity, so ``s2 - VX`` is how far the earlier steps moved.

    Returns ``v0 = 1`` (``v1`` = opponent actor) when the rocket is within the donor
    explosion distance of the aim point, without steering; otherwise ``v0 = 0``.
    Leaf; uses t0-t9."""

    a.label("trk_hunt")
    a.move("v0", "zero")
    a.la("t0", "trk_aim")
    a.lw("t0", 0, "t0")
    a.beqz("t0", "trk_hunt_done")
    a.lw("t0", host.CTRL_ACTOR, "t0")
    a.beqz("t0", "trk_hunt_done")
    a.lw("t1", host.ACTOR_X, "t0")
    a.lw("t2", host.ACTOR_X, "s1")
    a.subu("t1", "t1", "t2")
    a.sra("t1", "t1", 9)  # 24.8 units -> px (2 units per px)
    a.lw("t3", VX, "s0")
    a.subu("t3", "s2", "t3")
    a.sra("t3", "t3", 16)  # px the earlier steps of this tick moved
    a.subu("t1", "t1", "t3")
    a.lw("t2", host.ACTOR_Y, "t0")
    a.lw("t3", host.ACTOR_Y, "s1")
    a.subu("t2", "t2", "t3")
    a.sra("t2", "t2", 9)
    a.lw("t3", VY, "s0")
    a.subu("t3", "s3", "t3")
    a.sra("t3", "t3", 16)
    a.subu("t2", "t2", "t3")
    a.addiu("t2", "t2", AIM_Y)
    _emit_rough(a, "t4", "t1", "t2", "t5", "t6", "trk_r0")
    a.slti("t4", "t4", DETONATE_PX)
    a.beqz("t4", "trk_hunt_steer")
    a.move("v1", "t0")
    a.jr_ra()
    a.li("v0", 1)
    a.label("trk_hunt_steer")
    a.li("t3", STEER)
    a.mult("t1", "t3")
    a.mflo("t1")
    a.mult("t2", "t3")
    a.mflo("t2")
    _emit_rough(a, "t4", "t1", "t2", "t5", "t6", "trk_r1")
    a.sra("t4", "t4", 16)
    _emit_at_least_one(a, "t4", "trk_n1")
    a.div("t1", "t4")
    a.mflo("t1")
    a.div("t2", "t4")
    a.mflo("t2")
    a.lw("t3", VX, "s0")
    a.sra("t5", "t3", 4)
    a.addu("t3", "t3", "t1")
    a.subu("t3", "t3", "t5")
    a.lw("t4", VY, "s0")
    a.sra("t5", "t4", 4)
    a.addu("t4", "t4", "t2")
    a.subu("t4", "t4", "t5")
    _emit_rough(a, "t5", "t3", "t4", "t6", "t7", "trk_r2")
    a.sra("t5", "t5", 16)
    _emit_at_least_one(a, "t5", "trk_n2")
    a.li("t6", HUNT_SPEED)
    a.div("t3", "t5")
    a.mflo("t3")
    a.mult("t3", "t6")
    a.mflo("t3")
    a.div("t4", "t5")
    a.mflo("t4")
    a.mult("t4", "t6")
    a.mflo("t4")
    a.sw("t3", VX, "s0")
    a.sw("t4", VY, "s0")
    a.label("trk_hunt_done")
    a.jr_ra()
    a.nop()


def emit_direction(a: Assembler) -> None:
    """``trk_direction(a0 = vx, a1 = vy) -> v0``: ``point_rocket``'s choice. Leaf."""

    a.label("trk_direction")
    _emit_abs(a, "t0", "a0", "t2")
    _emit_abs(a, "t1", "a1", "t2")
    a.move("v0", "zero")
    a.sll("t2", "t0", 3)
    a.subu("t2", "t2", "t0")
    a.srl("t2", "t2", 1)  # 3.5 |vx|
    a.sltu("t3", "t1", "t2")
    a.beqz("t3", "trk_dir_down")
    a.li("v0", 1)
    a.sltu("t3", "t1", "t0")
    a.beqz("t3", "trk_dir_down")
    a.li("v0", 2)
    a.sll("t2", "t1", 3)
    a.subu("t2", "t2", "t1")
    a.srl("t2", "t2", 1)  # 3.5 |vy|
    a.sltu("t3", "t2", "t0")
    a.beqz("t3", "trk_dir_down")
    a.li("v0", 3)
    a.label("trk_dir_down")
    a.blez("a1", "trk_dir_done")
    a.addiu("v0", "v0", 4)
    a.label("trk_dir_done")
    a.jr_ra()
    a.nop()


def _emit_explode(a: Assembler, explosion: str, boom_event: int, spawn: str, player: str) -> None:
    host.play_sound(a, boom_event, player)
    a.move("a0", "s1")
    a.la("a1", explosion)
    a.move("a2", "zero")
    a.li("a3", effects.FRONT_SUBLAYER)
    a.jal_label(spawn)


def emit_callback(
    a: Assembler,
    smoke: str,
    explosion: str,
    boom_event: int,
    spawn: str = "fx_spawn",
    player: str = "play",
) -> None:
    """``trk_callback``: per host tick (two donor ticks) from the stock loop's ``jalr``."""

    a.label("trk_callback")
    a.addiu("sp", "sp", -0x30)
    a.sw("ra", 0x2C, "sp")
    a.sw("s0", 0x28, "sp")
    a.sw("s1", 0x24, "sp")
    a.sw("s2", 0x20, "sp")
    a.sw("s3", 0x1C, "sp")
    a.sw("s4", 0x18, "sp")
    a.lui("s0", hi(host.CURRENT_CTRL))
    a.lw("s0", lo(host.CURRENT_CTRL), "s0")
    a.lw("s1", host.CTRL_ACTOR, "s0")
    a.la("t0", "trk_heartbeat")
    a.lw("t1", 0, "t0")
    a.addiu("t1", "t1", 1)
    a.sw("t1", 0, "t0")
    a.lw("t1", PHASE, "s0")
    a.srl("t1", "t1", 16)
    a.li("t2", DETONATE)
    a.beq("t1", "t2", "trk_detonate")
    a.lw("t1", TICKS, "s0")
    a.addiu("t1", "t1", 1)
    a.sw("t1", TICKS, "s0")
    a.li("t2", LOOP_CALLS)
    a.bne("t1", "t2", "trk_steps")
    # timeout (the loop deletes the rocket next): explode where it is
    _emit_explode(a, explosion, boom_event, spawn, player)
    a.beq("zero", "zero", "trk_steps")
    # the proximity strike did not connect: explode without a strike and end the rocket
    a.label("trk_detonate")
    _emit_explode(a, explosion, boom_event, spawn, player)
    a.move("a0", "s1")
    a.jal(F_FLIGHT_END)  # does not return
    a.label("trk_steps")
    a.jal_label("trk_check")
    a.move("s2", "zero")
    a.move("s3", "zero")
    a.li("s4", 2)
    a.label("trk_step")
    a.lw("t0", VX, "s0")
    a.lw("t1", VY, "s0")
    a.addu("s2", "s2", "t0")
    a.addu("s3", "s3", "t1")
    a.lw("t2", PHASE, "s0")
    a.srl("t3", "t2", 16)
    a.li("t4", 2)
    a.bne("t3", "t4", "trk_timed")
    a.jal_label("trk_hunt")
    a.bnez("v0", "trk_near")
    a.beq("zero", "zero", "trk_next")
    a.label("trk_timed")
    a.li("t4", 1)
    a.bne("t3", "t4", "trk_count")
    a.li("t5", CLIMB)
    a.subu("t1", "t1", "t5")
    a.sw("t1", VY, "s0")
    a.label("trk_count")
    a.andi("t4", "t2", 0xFFFF)
    a.addiu("t4", "t4", -1)
    a.bnez("t4", "trk_store")
    a.addiu("t3", "t3", 1)  # next phase
    a.li("t4", PHASE_TICKS[1])
    a.li("t5", 1)
    a.beq("t3", "t5", "trk_store")
    a.move("t4", "zero")  # hunt: no count
    a.label("trk_store")
    a.sll("t3", "t3", 16)
    a.addu("t2", "t3", "t4")
    a.sw("t2", PHASE, "s0")
    a.label("trk_next")
    a.addiu("s4", "s4", -1)
    a.bnez("s4", "trk_step")
    a.li("t1", 3)
    a.sll("t0", "s2", 1)
    a.div("t0", "t1")
    a.mflo("t0")
    a.sw("t0", host.ACTOR_XVEL, "s1")
    a.sll("t0", "s3", 1)
    a.div("t0", "t1")
    a.mflo("t0")
    a.sw("t0", host.ACTOR_YVEL, "s1")
    # direction frames
    a.lw("a0", VX, "s0")
    a.lw("a1", VY, "s0")
    a.jal_label("trk_direction")
    a.lw("t0", DIR, "s0")
    a.beq("v0", "t0", "trk_facing")
    a.sw("v0", DIR, "s0")
    a.sll("t1", "v0", 2)
    a.la("t2", "trk_loops")
    a.addu("t2", "t2", "t1")
    a.lw("t2", 0, "t2")
    a.lui("t3", hi(robo_zap.FILE87_BASE_PTR))
    a.lw("t3", lo(robo_zap.FILE87_BASE_PTR), "t3")
    a.addu("t2", "t2", "t3")
    a.sw("t2", host.CTRL_SCRIPT_CURSOR, "s0")
    a.label("trk_facing")
    a.lw("t0", VX, "s0")
    a.slt("t0", "t0", "zero")
    a.sll("t0", "t0", 4)  # 0x10 when flying towards -x
    a.lhu("t1", 0x8C, "s1")
    a.andi("t1", "t1", 0x10)
    a.beq("t0", "t1", "trk_smoke")
    a.move("a0", "s1")
    a.jal(F_FLIP)
    a.label("trk_smoke")
    a.lw("t0", DIR, "s0")
    a.sll("t0", "t0", 2)
    a.la("t1", "trk_smoke_offsets")
    a.addu("t1", "t1", "t0")
    a.lw("a2", 0, "t1")
    a.lhu("t3", 0x8C, "s1")
    a.andi("t3", "t3", 0x10)
    a.beqz("t3", "trk_smoke_go")
    a.sll("t4", "a2", 16)  # flipped: negate dx (low half)
    a.sra("t4", "t4", 16)
    a.subu("t4", "zero", "t4")
    a.andi("t4", "t4", 0xFFFF)
    a.srl("t5", "a2", 16)
    a.sll("t5", "t5", 16)
    a.addu("a2", "t5", "t4")
    a.label("trk_smoke_go")
    a.move("a0", "s1")
    a.la("a1", smoke)
    a.lhu("a3", 0xEC, "s1")
    a.addiu("a3", "a3", 1)
    a.jal_label(spawn + "_xy")
    a.label("trk_return")
    a.lw("ra", 0x2C, "sp")
    a.lw("s0", 0x28, "sp")
    a.lw("s1", 0x24, "sp")
    a.lw("s2", 0x20, "sp")
    a.lw("s3", 0x1C, "sp")
    a.lw("s4", 0x18, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x30)
    # proximity: onto the aim point and stop; the stock strike follows this call
    a.label("trk_near")
    a.lw("t0", host.ACTOR_X, "v1")
    a.sw("t0", host.ACTOR_X, "s1")
    a.lw("t0", host.ACTOR_Y, "v1")
    a.li("t1", AIM_Y << 9)
    a.addu("t0", "t0", "t1")
    a.sw("t0", host.ACTOR_Y, "s1")
    a.sw("zero", host.ACTOR_XVEL, "s1")
    a.sw("zero", host.ACTOR_YVEL, "s1")
    a.li("t0", DETONATE << 16)
    a.sw("t0", PHASE, "s0")
    a.beq("zero", "zero", "trk_return")
