"""Special-move actions and conditions on the host (milestone 4 step 3, reusable).

A special replaces a Sub-Zero power (the fighter description's ``commands``): its command
record keeps the donor input (``fighter_import.commands``) and gets

* a **condition** (:func:`emit_gate_condition`): the logic of Sektor's runtime-accepted missile
  conditions (``actions/sektor_tiers.py``, proofs v54+), generic: ground only, not grabbed,
  not busy, no live projectile (class ``0x700``), no special lock, the replaced power's Ice cost
  available and its tier reached. The tier is read at run time from the replaced power's stock
  gate instruction (``slti v0, v0, N``), so the power-order shuffle still applies;
* an **action** (:func:`emit_action`), entered through the Ice-root selector table
  (``0x8004AA4C``, :func:`host.emit_transfer_thunk`), that runs the move program's steps.

Supported steps: ``stamp`` (MKT cooldown key; not lowered yet), ``begin``, ``animate`` (a donor
animation the description copied into a host secondary slot, ``body.secondary_scripts``;
``until`` ``phase_end`` or ``manual``), ``pose``, ``next_frame``, ``velocity``, ``stop``,
``face``, ``shake``, ``repeat``, ``strike`` (a hit window with ``on_hit`` / ``on_block`` branches),
``pass_through`` (see :func:`emit_action`), ``projectile`` (a child built by
``lower_projectile``), ``sleep``, ``finish`` and ``end``.

**Timing.** MKT runs its game logic at 60 ticks a second, the host at 30
(``physics.DONOR_HZ`` / ``HOST_HZ``). With ``donor_ticks=2`` donor tick counts (sleeps, strike
windows, repeat counts, animation rates) are halved, and an advance done every donor tick is
done twice per host tick, so a move keeps MKT's real-time length and distance. The accepted
forceballs keep donor counts (``donor_ticks=1``); the owner halved Acid Spit's recovery by hand
(specials proof v11).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import host, physics
from . import lower_projectile as lp
from .host import hi, lo
from .mips import Assembler

PLAYER_ACTOR = 0x802E73DC
PLAYER_CTRL = 0x802C1AC0
SPECIAL_FLAG = 0x802E7DE8  # stock conditions refuse while it is set
F_FIND_CLASS = 0x80028510
F_TIER = 0x80074FBC  # tier count 0..9 from current XP
F_SLEEP = 0x80028794
F_PROCESS_CREATE = 0x8002830C  # (id, entry) -> controller or 0
F_PROCESS_EXIT = 0x80028564
F_TO_PHASE_END = 0x80031070  # (ticks per frame): animate to the end of the phase
CURRENT_XP = 0x8011200C
FALL_SPEED_LIMIT = 0xB4782  # stock LP condition: refuse while actor +0x18 exceeds it
BUSY_ACTION = 0x1A
CTRL_ICE = 0x656  # Ice meter (halfword)
ICE_ACTION_ID = 0x603  # stock special action id (teleport and projectile proofs)

# Stock tier gates (``slti v0, v0, N`` after the tier evaluator), per Sub-Zero power, and the
# Ice each power costs (Wiki Player-Actions-and-Special-Moves, stock reconciliation).
GATES = {
    "ice_blast_air": 0x8004A3BC,
    "directional_ice_down": 0x8004A4F4,
    "directional_ice_up": 0x8004A484,
    "ice_clone": 0x8004A2A8,
    "freeze_on_contact": 0x8005A9DC,
    "polar_blast": 0x8004A6B4,
    "ice_shatter": 0x800509A0,  # first of its two contextual sites (power_order sets both alike)
}
# Ground Ice Blast's tier is a bgtz tail (tier >= 1) at ROM 0x4B018; the product's power-order
# shuffle rewrites it to ``slti t0, v0, N`` (patches/power_order.build_ice_ground_tail).
ICE_BLAST_GATE, ICE_BLAST_STOCK_TIER = 0x8004A418, 1
SLTI_T0_V0 = 0x2848
COSTS = {
    "ice_blast": 0x20,
    "ice_blast_air": 0x20,  # the same LP condition as Ice Blast (0x8004A304: meter < 0x20 refuses)
    "directional_ice_up": 0x20,
    "directional_ice_down": 0x60,
    "ice_clone": 0x60,
    "freeze_on_contact": 0x80,
    "polar_blast": 0xA6,
    "ice_shatter": 0,  # contextual, no Ice cost
}
# Per-thousand random gate (Wiki Function-Registry): 0x8000 when a native random value modulo
# 1000 is below a0. A sound step with ``random: k`` picks one of k donor sounds evenly (MKT
# ``ft_sound(randu(k) + n)``, Rayden's torpedo start).
F_RANDPER = 0x80016008
F_TURN = 0x8003188C  # (actor): turn it around (face_opponent 0x80031EF0 calls it when needed)
MOVEMENT_COST = 0  # movement abilities cost no Ice (owner rule, 2026-11-24; move program "movement")
GRAB_COST = 2 * COSTS["ice_blast"]  # grabs cost twice Ice Blast's (owner rule, 2026-11-26; "grab")
BLOCKED_FLAG = 0x802ECD88  # halfword: the collision core sets it on a blocked contact
F_SET_XVEL = 0x8002B1EC  # (actor, x speed): actor +0x14 and +0x58
FACING_BIT = 0x10
# Host victim reactions by strike meaning: a stock entry, or None for one the builder supplies
# in a spare reaction-table entry (``reactions`` argument of emit_action).
# ``launch``: the stock roundhouse's reaction (player strike index 0x0D, record 0x800AF5E4; owner,
# specials proof v15: "the roundhouse kick one, not the uppercut"). ``uppercut``: 0x800507D0,
# Runtime-confirmed (Sektor teleport).
STOCK_REACTIONS = {"launch": 0x0C, "uppercut": 0x08}
# actor +0x8C: the draw takes the actor's colours from the stage lighting while it is set
# (0x800188B4 -> 0x80024F74); Freeze on Contact clears it while it runs (0x80034740 / 0x80034658).
# Named LIT_BIT until specials proof v17: the pass-through does not depend on it.
LIT_BIT = 0x1000


def emit_gate_condition(a: Assembler, label: str, gate_va: int, cost: int,
                        default: int | None = None, alive: tuple[str, ...] = (),
                        refuse_if: tuple[int, int] | None = None, airborne: bool = False,
                        cooldown: tuple[str, int] | None = None, target_range: int | None = None,
                        held: tuple[str, int] | None = None) -> None:  # fmt: skip
    """``label() -> 0x8000 / 0x4000`` (see the module notes). With ``default``, the gate word
    is used only when it is ``slti t0, v0, N`` (Ice Blast's rewritten tail), else ``default``.
    With ``alive`` (labels of words that projectiles set while they live,
    ``lower_projectile.emit_process``), only those projectiles block it instead of any live one
    (Reptile: one fast and one slow forceball may coexist, owner 2026-11-11). Set words with no
    live projectile process are stale (a process ended by something else) and are cleared.
    ``refuse_if`` (controller offset, mask): refuse while that halfword of the player's
    controller has a bit of the mask set (Invisibility: already stealthed). ``airborne``: also
    accept in the air (no fall-speed or floor check; Rayden's torpedo, owner 2026-11-24).
    ``cooldown`` (stamp label, ticks): refuse until that many clock ticks (``host.VI_CLOCK``,
    60 Hz, as MKT's) have passed since the move's ``stamp`` (MKT's ticks_since condition).
    ``target_range``: refuse unless an enemy is within that range on the player's path (as
    Sektor's teleport condition, which avoids a teleport with nobody to reach). ``held`` (stamp
    label, ticks): refuse unless the High Punch press stamp (``commands``) is at least that old
    at the release (MKT ``ticks_since`` on the press stamp: Rayden's Shocker). Both are
    timestamps since v30: v25-v29 used a counter process with a running flag and a timer
    process, which a stock process kill could leave stuck until the next stage load."""

    a.label(label)
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x1C, "sp")
    if target_range is not None:  # find_target uses s1 / s4
        a.sw("s1", 0x18, "sp")
        a.sw("s4", 0x14, "sp")
    if cooldown is not None:  # refuse until the cooldown has passed since the move's stamp
        host.emit_since(a, cooldown[0], cooldown[1], label + "_no", unset_refuses=False)
    if held is not None:  # refuse unless High Punch was pressed that long before its release
        host.emit_since(a, held[0], held[1], label + "_no", unset_refuses=True)
    a.lui("t0", hi(PLAYER_ACTOR))
    a.lw("t0", lo(PLAYER_ACTOR), "t0")
    if not airborne:
        a.lw("t1", 0x18, "t0")
        a.li("t2", FALL_SPEED_LIMIT)
        a.slt("t2", "t2", "t1")
        a.bnez("t2", label + "_no")
    a.lui("t3", hi(PLAYER_CTRL))
    a.lw("t3", lo(PLAYER_CTRL), "t3")
    a.lh("t4", 0x6B0, "t3")
    a.bnez("t4", label + "_no")
    a.lw("t5", 0x6E0, "t3")
    a.lw("t4", 0xDC, "t5")
    a.bnez("t4", label + "_no")
    if refuse_if is not None:
        a.lhu("t4", refuse_if[0], "t3")
        a.andi("t4", "t4", refuse_if[1])
        a.bnez("t4", label + "_no")
    a.lhu("t4", CTRL_ICE, "t3")
    a.slti("t4", "t4", cost)  # meter is a small positive halfword
    a.bnez("t4", label + "_no")
    if not airborne:
        a.lw("t4", 0x30, "t5")
        a.lw("t6", 0x6B4, "t3")
        a.slt("t4", "t4", "t6")
        a.bnez("t4", label + "_no")  # airborne
    a.lui("t6", hi(host.CURRENT_CTRL))
    a.lw("t6", lo(host.CURRENT_CTRL), "t6")
    a.lhu("t7", 0x6AA, "t6")
    a.li("t8", BUSY_ACTION)
    a.beq("t7", "t8", label + "_no")
    if alive:
        a.move("t1", "zero")
        for word in alive:
            a.la("t0", word)
            a.lw("t2", 0, "t0")
            a.or_("t1", "t1", "t2")
        a.beqz("t1", label + "_free")
    a.li("a0", lp.PROJECTILE_CLASS)
    a.li("a1", 0xFFFF)
    a.jal(F_FIND_CLASS)
    a.bnez("v0", label + "_no")
    if alive:
        for word in alive:  # stale: no projectile process left
            a.la("t0", word)
            a.sw("zero", 0, "t0")
        a.label(label + "_free")
    a.lui("t0", hi(SPECIAL_FLAG))
    a.lh("t0", lo(SPECIAL_FLAG), "t0")
    a.bnez("t0", label + "_no")
    a.lui("a0", hi(CURRENT_XP))
    a.lw("a0", lo(CURRENT_XP), "a0")
    a.jal(F_TIER)
    if default is not None:
        a.lui("t1", hi(gate_va))
        a.lhu("t1", lo(gate_va), "t1")
        a.li("t2", SLTI_T0_V0)
        a.li("t0", default)
        a.bne("t1", "t2", label + "_gate")
    a.lui("t0", hi(gate_va + 2))
    a.lh("t0", lo(gate_va + 2), "t0")  # the slot's threshold N
    if default is not None:
        a.label(label + "_gate")
    a.slt("t1", "v0", "t0")
    a.bnez("t1", label + "_no")
    if target_range is not None:
        a.lui("t0", hi(PLAYER_CTRL))
        a.lw("t0", lo(PLAYER_CTRL), "t0")
        a.lw("s1", host.CTRL_ACTOR, "t0")
        host.find_target(a, label + "_no", target_range)
    a.li("v0", 0x8000)
    a.beq("zero", "zero", label + "_ret")
    a.label(label + "_no")
    a.li("v0", 0x4000)
    a.label(label + "_ret")
    a.lw("ra", 0x1C, "sp")
    if target_range is not None:
        a.lw("s1", 0x18, "sp")
        a.lw("s4", 0x14, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)


# ---- cooldowns (MKT stamp_tick + ticks_since) ---------------------------------------------------
def emit_stamp(a: Assembler, cooldown: str, skip: str) -> None:
    """In the move: stamp the clock in the cooldown word (its condition compares the time)."""

    host.emit_stamp_now(a, cooldown)
    a.label(skip)
    host.load_controller(a)


# ---- relocation (MKT match_me_to_opponent + multi_adjust_xy; Sektor's teleport reposition) -----
RELOCATE_RANGE = 592  # 0.925 x the 640-unit visible ground width at camera depth 0x200 (Sektor)
RELOCATE_WALL_MARGIN = 4
RELOCATE_MIN_SEPARATION = 16
RELOCATE_FLOOR_BOUND = 0x20000
RELOCATE_SNAP = 0x40


def emit_relocate_routine(a: Assembler, label: str = "relocate") -> None:
    """Subroutine ``relocate(a0 = distance in world units) -> v0`` (1 placed, 0 no enemy): the
    player goes past the nearest enemy in range by ``a0`` (less when a wall is nearer), on the
    enemy's floor, snapped onto the nearest probed floor; on the near side when the far one
    has no floor, else at the enemy's x; a cornered enemy is nudged out; then he faces it. It
    is Sektor's runtime-confirmed teleport reposition (``actions/robo_teleport``, production
    settings: on the floor, own-floor fallback, floor probe, snap), as a subroutine any move can
    call. MKT picks the side by the arena's edges; the host has no arena, so by the room."""

    from .actions import robo_teleport as rt

    a.label(label)
    a.addiu("sp", "sp", -0x40)
    a.sw("ra", 0x3C, "sp")
    for k, r in enumerate(("s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7")):
        a.sw(r, 0x1C + 4 * k, "sp")
    a.move("s7", "a0")
    host.load_controller(a)
    host.find_target(a, label + "_none", RELOCATE_RANGE)
    a.lw("t0", host.CTRL_GROUND, "v0")  # the enemy's floor, before any call
    a.sw("t0", 0x10, "sp")
    host.face_opponent(a)
    host.load_controller(a)
    a.lw("t0", host.ACTOR_X, "s4")
    a.lw("t1", host.ACTOR_X, "s1")
    a.slt("s6", "t0", "t1")  # 1: the enemy is on the player's -x side
    a.lw("t0", 0x10, "sp")  # y: the enemy's floor if usable, else the player's, else its height
    a.lw("t1", host.ACTOR_Y, "s4")
    a.sw("t1", 0x14, "sp")
    a.subu("t2", "t0", "t1")
    a.bltz("t2", label + "_own")
    a.li("t3", RELOCATE_FLOOR_BOUND)
    a.slt("t3", "t3", "t2")
    a.bnez("t3", label + "_own")
    a.sw("t0", 0x14, "sp")
    a.beq("zero", "zero", label + "_yset")
    a.label(label + "_own")
    a.lw("t0", host.CTRL_GROUND, "s0")
    a.subu("t2", "t0", "t1")
    a.bltz("t2", label + "_yset")
    a.li("t3", 0x7FBC00)
    a.beq("t0", "t3", label + "_yset")  # no floor
    a.sw("t0", 0x14, "sp")
    a.label(label + "_yset")
    for field in (host.ACTOR_PATH_PARAM, host.ACTOR_X, host.ACTOR_Z):
        a.lw("t0", field, "s4")
        a.sw("t0", field, "s1")
    a.lw("t0", 0x14, "sp")
    a.sw("t0", host.ACTOR_Y, "s1")
    a.move("a0", "s4")
    a.addiu("a1", "sp", 0x10)
    a.addiu("a2", "sp", 0x14)
    a.jal(host.F_WALL_DISTANCE)
    a.lw("t0", 0x14, "sp")
    a.beqz("s6", label + "_far")
    a.lw("t0", 0x10, "sp")  # the wall room on the far side
    a.label(label + "_far")
    a.addiu("s5", "t0", -RELOCATE_WALL_MARGIN)
    a.slt("t2", "s7", "s5")
    a.beqz("t2", label + "_le")
    a.move("s5", "s7")  # min(distance, room)
    a.label(label + "_le")
    a.bgez("s5", label + "_pos")
    a.li("s5", 0)
    a.label(label + "_pos")
    host.offset_actor(a, "s1", "s5")
    a.li("t1", RELOCATE_MIN_SEPARATION)
    a.slt("t2", "s5", "t1")
    a.beqz("t2", label + "_placed")
    a.li("t1", RELOCATE_MIN_SEPARATION)
    a.subu("s2", "t1", "s5")  # cornered: nudge the enemy out
    a.lw("s3", host.ACTOR_X, "s4")
    host.offset_actor(a, "s4", "s2")
    a.lw("t0", host.ACTOR_X, "s4")
    a.slt("t1", "s3", "t0")
    a.beq("t1", "s6", label + "_placed")
    a.move("a0", "s4")
    a.subu("a1", "zero", "s2")
    a.sll("a1", "a1", 1)
    a.move("a2", "zero")
    a.jal(host.F_OFFSET)
    a.label(label + "_placed")

    def probe() -> None:
        a.lw("a0", host.ACTOR_X, "s1")
        a.sra("a0", "a0", 8)
        a.lw("a1", host.ACTOR_Z, "s1")
        a.sra("a1", "a1", 8)
        a.lw("a2", host.ACTOR_Y, "s1")
        a.jal_label(label + "_floor_probe")

    probe()
    a.bnez("v0", label + "_spot")
    a.lw("t0", host.ACTOR_X, "s4")  # near side: mirrored around the enemy
    a.sll("t0", "t0", 1)
    a.lw("t1", host.ACTOR_X, "s1")
    a.subu("t0", "t0", "t1")
    a.sw("t0", host.ACTOR_X, "s1")
    probe()
    a.bnez("v0", label + "_spot")
    a.lw("t0", host.ACTOR_X, "s4")  # the enemy's own x
    a.sw("t0", host.ACTOR_X, "s1")
    probe()
    a.beqz("v0", label + "_kept")
    a.label(label + "_spot")
    a.sw("v1", host.ACTOR_Y, "s1")  # on the probed floor
    a.label(label + "_kept")
    host.face_opponent(a)
    a.li("v0", 1)
    a.beq("zero", "zero", label + "_ret")
    a.label(label + "_none")
    a.move("v0", "zero")
    a.label(label + "_ret")
    a.lw("ra", 0x3C, "sp")
    for k, r in enumerate(("s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7")):
        a.lw(r, 0x1C + 4 * k, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x40)
    rt.emit_floor_probe(a, label + "_floor_probe", nearest=RELOCATE_SNAP)


def emit_charge(a: Assembler, amount: int) -> None:
    """Take ``amount`` from the current controller's Ice meter (t0, t1)."""

    a.lui("t0", hi(host.CURRENT_CTRL))
    a.lw("t0", lo(host.CURRENT_CTRL), "t0")
    a.lhu("t1", CTRL_ICE, "t0")
    a.addiu("t1", "t1", -amount)
    a.sh("t1", CTRL_ICE, "t0")


# The stock jump (Wiki Player-Actions-and-Special-Moves, "Integrator and gravity", "Airborne
# counter"): 0x800321D0(actor, x vel, y vel, gravity, [sp+0x10] rate, [sp+0x14] root). 13 keeps a
# velocity or the rate, a negative root keeps the animation. It counts the airborne ticks in
# controller +0x6B2, sleeps until the actor lands and clears the counter.
F_JUMP, JUMP_KEEP = 0x800321D0, 13
# Controller +0x70C: the stock jump copies it to +0x68C at entry and calls it every air tick when
# non-zero. Every stock caller clears it first (0x8004F40C, 0x80057CEC, ...); the field is shared
# with other uses, and a stale value is called as code (Rayden specials proof v02 save state: TLB
# miss at 0x801125A0 called from 0x80032448 after a torpedo hit up close).
CTRL_JUMP_CALLBACK = 0x70C
# Air control in the stock jump: each air tick 0x800321D0 adds +-0x8000 to the player's x speed
# from the held Left/Right (pad +0x638 bits 0x8000/0x2000, clamped), unless the player's input map
# 0x802E7DFC is the busy map 0x8009F988 (0x8003237C..0x80032400), which an uncancellable special
# holds. ``air_control`` installs the stock straight-air map first (0x8002B05C); the special lock
# 0x800BF308 stays set, so the input dispatcher 0x800157E0 still starts no air attack (owner,
# Rayden specials proof v07: "I have no air control ... unlike when you jump").
AIR_MAP = 0x8009FA00


def _scale(n: int, donor_ticks: int) -> int:
    return max(1, -(-n // donor_ticks))


def _timed_repeat(step: dict[str, Any], donor_ticks: int) -> tuple[int, list[list[dict[str, Any]]]] | None:
    """A ``repeat`` whose body sleeps at least one host tick (Rayden's Shocker: 32 x [sleep 3,
    next_frame] at 2 donor ticks per host tick): MKT's iteration count and its total time. The
    body is emitted ``k`` times per loop pass (``k`` = the passes after which the donor time is
    whole host ticks again), its sleeps rounded on the running total (3, 3 -> 2, 1 host ticks),
    so 32 frames take 48 host ticks; scaling the count instead showed 16 frames in 32 ticks. Its
    ``next_frame`` steps are MKT's own frame steps: one frame each (a per-tick loop's advance by
    the donor ticks it stands for landed on the same frame of a two-frame loop every time).
    None for a per-tick loop (a body shorter than a host tick), whose count scales."""

    from math import gcd

    body = step["steps"]
    if donor_ticks <= 1 or any(s["op"] == "repeat" for s in body):
        return None
    sleeps = [int(s["ticks"]) for s in body if s["op"] == "sleep"]
    total = sum(sleeps)
    if total < donor_ticks:
        return None
    k = donor_ticks // gcd(total, donor_ticks)
    count = int(step["count"])
    if count % k:
        return None
    bodies, donor, host_done = [], 0, 0
    for _ in range(k):
        out = []
        for s in body:
            if s["op"] == "sleep":
                donor += int(s["ticks"])
                end = -(-donor // donor_ticks)
                s = {**s, "_host_ticks": max(1, end - host_done)}
                host_done = end
            elif s["op"] == "next_frame":  # MKT's own frame step: one frame (v29; v25-v28 two)
                s = {**s, "_times": 1}
            out.append(s)
        bodies.append(out)
    return count // k, bodies


INSTANT_OPS = {"pose", "next_frame", "sound", "face", "flip"}


def _sleep_runs(steps: list[dict[str, Any]], donor_ticks: int) -> list[dict[str, Any]]:
    """Sleeps with only instant steps between them, rounded on their running total (as
    :func:`_timed_repeat` does within a repeat): Sektor's landing, two frames of 3 donor ticks
    each, takes 3 host ticks (MKT's 0.1 s), not 2 + 2 (proof v07; the owner's LK after the
    uppercut). A lone sleep keeps its own rounding."""

    if donor_ticks <= 1:
        return steps
    out = list(steps)
    run: list[int] = []

    def close() -> None:
        if len(run) > 1:
            donor = done = 0
            for i in run:
                donor += int(out[i]["ticks"])
                end = (2 * donor + donor_ticks) // (2 * donor_ticks)  # nearest, halves up
                out[i] = {**out[i], "_host_ticks": max(1, end - done)}
                done = end
        run.clear()

    for k, s in enumerate(out):
        if s["op"] == "sleep" and "_host_ticks" not in s:
            run.append(k)
        elif s["op"] not in INSTANT_OPS:
            close()
    close()
    return out


@dataclass(frozen=True)
class Motion:
    """A ``jump`` step that sinks below the screen or rises to the floor, as an alias script: one
    frame per host tick (``steps``), the fighter's pose moved down by the donor curve's depth
    (``fighter_build.motion_scripts``). ``near_from``: the first step within the strike's reach
    of the floor (a rise); ``surface_velocity``: MKT's y velocity when the rise reaches the
    floor (donor units), the flight's start."""

    script: int
    steps: int
    near_from: int | None = None
    surface_velocity: int | None = None


def _emit_fall_then_sink(a: Assembler, motion: Motion, y: int, gravity: int, tag: str) -> None:
    """A sink that may start in the air: while above his floor the fighter falls on the sink's
    own curve (MKT's velocity and gravity, converted), showing its first frame, counting ticks
    (``s7``); then the alias script goes on from that tick (capped at its last frame)."""

    host.set_cursor(a, motion.script)
    host.advance_animation(a)
    a.move("s7", "zero")
    a.lw("t0", host.ACTOR_Y, "s1")
    a.lw("t1", host.CTRL_GROUND, "s0")
    a.slt("t2", "t0", "t1")  # y grows downward: above the floor
    a.beqz("t2", tag + "_grounded")
    a.li("t0", physics.convert_velocity(y))
    a.sw("t0", host.ACTOR_YVEL, "s1")
    a.li("t0", physics.convert_acceleration(gravity))
    a.sw("t0", host.ACTOR_GRAVITY, "s1")
    a.li("s2", 60)  # at most 2 s
    a.label(tag)
    host.sleep_tick(a)
    host.load_controller(a)
    a.addiu("s7", "s7", 1)
    a.lw("t0", host.ACTOR_Y, "s1")
    a.lw("t1", host.CTRL_GROUND, "s0")
    a.slt("t2", "t0", "t1")
    a.beqz("t2", tag + "_fallen")
    a.addiu("s2", "s2", -1)
    a.bnez("s2", tag)
    a.label(tag + "_fallen")
    host.stop(a)
    a.sw("zero", host.ACTOR_GRAVITY, "s1")
    a.sw("zero", host.ACTOR_YVEL, "s1")
    a.sh("zero", host.CTRL_AIRBORNE, "s0")
    a.label(tag + "_grounded")
    a.li("t0", motion.steps - 1)
    a.slt("t1", "t0", "s7")
    a.beqz("t1", tag + "_index")
    a.move("s7", "t0")  # capped at the last frame
    a.label(tag + "_index")
    a.lw("t0", host.ACTOR_FILE_BASE, "s1")  # the cursor on frame s7 of the script
    a.sll("t1", "s7", 2)
    a.addu("t0", "t0", "t1")
    a.li("t1", motion.script)
    a.addu("t0", "t0", "t1")
    a.sw("t0", host.CTRL_SCRIPT_CURSOR, "s0")
    host.advance_animation(a)
    a.li("s2", motion.steps - 1)
    a.subu("s2", "s2", "s7")  # the ticks left
    a.beqz("s2", tag + "_done")
    a.label(tag + "_sink")
    host.sleep_tick(a)
    host.load_controller(a)
    host.advance_animation(a)
    a.addiu("s2", "s2", -1)
    a.bnez("s2", tag + "_sink")
    a.label(tag + "_done")
    host.load_controller(a)


def _emit_strike_once(a: Assembler, label: str, record: str, hit_word: str) -> None:
    """``label()``: the strike against every enemy unless it already connected (``hit_word``);
    on contact sets ``hit_word`` (1 clean, 2 blocked). Saves what it uses."""

    done = label + "_done"
    a.label(label)
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x1C, "sp")
    a.la("t0", hit_word)
    a.lw("t0", 0, "t0")
    a.bnez("t0", done)
    a.la("a0", record)
    a.lui("t0", lp.KSEG1_TO_KSEG0 >> 16)
    a.subu("a0", "a0", "t0")  # KSEG0 alias: the collision core rejects other records
    a.move("a1", "zero")
    a.jal(host.F_STRIKE)
    a.andi("v0", "v0", 0xFFFF)
    a.li("t0", 0x8000)
    a.bne("v0", "t0", done)
    a.lui("t0", hi(BLOCKED_FLAG))
    a.lhu("t0", lo(BLOCKED_FLAG), "t0")
    a.li("t1", 1)
    a.beqz("t0", label + "_clean")
    a.li("t1", 2)
    a.label(label + "_clean")
    a.la("t0", hit_word)
    a.sw("t1", 0, "t0")
    a.label(done)
    a.lw("ra", 0x1C, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)


def _emit_rising_strike(a: Assembler, label: str, strike_once: str, hit_word: str,
                        blocked_gravity: int | None) -> None:  # fmt: skip
    """The stock jump's per-tick callback (controller ``+0x70C``, MKT process ``+0x438``): the
    strike while the fighter rises (actor y velocity < 0); a blocked strike switches the gravity
    (MKT ``0xB000``)."""

    a.label(label)
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x1C, "sp")
    a.sw("s1", 0x18, "sp")
    a.sw("s0", 0x14, "sp")
    host.load_controller(a)
    a.lw("t0", host.ACTOR_YVEL, "s1")
    a.bgez("t0", label + "_done")
    a.jal_label(strike_once)
    if blocked_gravity is not None:
        a.la("t0", hit_word)
        a.lw("t0", 0, "t0")
        a.li("t1", 2)
        a.bne("t0", "t1", label + "_done")
        host.load_controller(a)
        a.li("t0", blocked_gravity)
        a.sw("t0", host.ACTOR_GRAVITY, "s1")
    a.label(label + "_done")
    a.lw("s0", 0x14, "sp")
    a.lw("s1", 0x18, "sp")
    a.lw("ra", 0x1C, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)


def emit_action(a: Assembler, label: str, steps: list[dict[str, Any]], *, cost: int,
                animations: dict[tuple[int, int], int | tuple[str, int]], child: str | None = None,
                helper: str | None = None, sounds: dict[int, int] | None = None,
                face: bool | None = None, donor_ticks: int = 1,
                reactions: dict[str, int] | None = None,
                speed: Callable[[int], int] | None = None,
                footsteps: dict[tuple[int, int], Footsteps] | None = None,
                stealth: str | None = None,
                effects: dict[int, tuple[str, int]] | None = None,
                skip: frozenset[str] = frozenset(),
                carry: str | None = None, air_control: bool = False,
                cooldown: str | None = None, afterimage: str | None = None,
                motions: dict[int, Motion] | None = None,
                primary_scripts: dict[int, int] | None = None,
                air_start: bool = False) -> list[tuple[str, bytes]]:  # fmt: skip
    """The action root for a move program (never returns). ``animations``: donor animation
    (table, slot) -> host secondary slot holding it, or ``("at", offset)`` for a body script
    without a table entry (selected by setting the cursor); ``child``: the projectile process
    label; ``helper``: the throw helper's process label (``lower_projectile.emit_helper``),
    started with the throw animation; ``sounds``: donor fighter sound -> host event, for
    ``sound`` steps (needs ``host.emit_sound_player``); ``face``: overrides the program's
    ``begin.face`` (MKT turns to its one opponent; the host may not want that);
    ``donor_ticks``: donor ticks per host tick (module notes); ``reactions``: strike meaning ->
    host reaction index (else :data:`STOCK_REACTIONS`); ``speed``: donor x speed -> host speed;
    ``footsteps``: a manually advanced animation -> its donor footstep frames
    (:func:`donor_footsteps`) and the host events to alternate (needs ``host.emit_sound_player``);
    ``stealth``: the label of the timer process (:func:`emit_stealth_timer`) for ``stealth``
    steps; ``effects``: MKT effect index -> (``effects.emit_descriptor`` label, dy in whole units)
    for ``effect`` steps, started at the fighter in front of him through ``fx_spawn_xy``
    (``effects.emit_spawn``); ``skip``: step ops left out on purpose; ``carry``: the label of
    the word a ``carry`` step shares with the victim's ``torpedo_carry`` reaction
    (:func:`emit_carry_reaction`); ``air_control``: ``jump`` steps let the player steer (see
    :data:`AIR_MAP`); ``cooldown``: the label of the move's cooldown process
    (the clock stamp its ``stamp`` step writes, :func:`emit_stamp`); ``afterimage``: the label of the
    afterimage process (``lower_projectile.emit_afterimage_process``) for ``afterimage`` steps;
    ``relocate`` steps call the ``relocate`` subroutine (:func:`emit_relocate_routine`);
    ``motions``: ``id(step)`` -> :class:`Motion`, the alias scripts of the ``jump`` steps that
    sink below the screen or rise to the floor (``fighter_build.motion_scripts``);
    ``primary_scripts``: host primary slot -> its script's file offset (a pose with an offset
    in a body slot: Sektor's landing); ``air_start``: the move may start in the air (MKT's
    command has no ground check), so a sink first falls on its own curve to the floor and goes
    on from the curve tick it reached (Sektor's legacy teleport, runtime-confirmed v08).

    Returns the strike records ``(label, 16 bytes)`` to place with :func:`emit_strike_data`.

    ``pass_through`` (MKT ``sans_repell_3``, no fighter repulsion; the host's fighter
    separation is not located). Specials proof v15 stopped at the victim. From v16 each
    pass-through tick clears actor ``+0x8C`` bit ``0x1000`` as stock Freeze on Contact does while
    Sub-Zero runs through enemies, and re-applies the move's last speed (kept in ``s5``); ``end``
    sets the bit again (Runtime-confirmed together, Reptile v16). The bit's only reader is the
    draw's stage lighting (:data:`LIT_BIT`), so the speed is what lets him through (inference)."""

    records: list[tuple[str, bytes]] = []
    shakers: list[tuple[str, dict[str, Any]]] = []
    counter = [0]

    def ops(steps: list[dict[str, Any]]) -> set[str]:
        found = set()
        for s in steps:
            found.add(s["op"])
            for key in ("steps", "every_tick", "on_hit", "on_block"):
                found |= ops(s.get(key, []))
        return found

    used = ops(steps)
    moves = "velocity" in used
    passes = "pass_through" in used

    def fresh(tag: str) -> str:
        counter[0] += 1
        return f"{label}_{tag}{counter[0]}"

    def anim_at(anim: dict[str, Any], reverse: bool = False) -> int | tuple[str, int]:
        key: tuple = (int(anim["table"]), int(anim["slot"]))
        if reverse:  # its frames backwards (body.secondary_scripts ``:reverse``)
            key = (*key, "reverse")
        if key not in animations:
            raise ValueError(f"{label}: animation {key} has no host slot")
        return animations[key]

    def select(where: int | tuple[str, int], offset: int = 0) -> None:
        if isinstance(where, tuple) and where[0] == "primary" and offset:  # by its script offset
            if not primary_scripts or where[1] not in primary_scripts:
                raise ValueError(f"{label}: a pose offset needs a script offset")
            host.load_controller(a)
            host.set_cursor(a, primary_scripts[where[1]] + 4 * offset)
        elif isinstance(where, tuple) and where[0] == "primary":  # a body slot (Rayden's getup)
            a.move("a0", "zero")
            a.li("a1", where[1])
            a.jal(lp.F_SELECT)
        elif isinstance(where, tuple):
            host.load_controller(a)
            host.set_cursor(a, where[1] + 4 * offset)
        else:
            if offset:
                raise ValueError(f"{label}: a pose offset needs a script offset")
            a.li("a0", 1)
            a.li("a1", where)
            a.jal(lp.F_SELECT)

    stepping: list[Footsteps | None] = [None]  # the manual animation's footsteps, if any
    running: list[int | None] = [None]  # the rate of an ``animate ... running`` animation
    rise: list[Motion | None] = [None]  # the last rise: a jump without y goes on from it
    hit_word = f"{label}_struck"  # a motion's strike connected (once per move)
    motion_strike: list[str | None] = [None]  # its record label
    callbacks: list[tuple[str, str, int | None]] = []  # (label, record, blocked gravity)

    def advance(times: int = 1) -> None:
        for _ in range(times):
            host.load_controller(a)
            host.advance_animation(a)
            steps_now = stepping[0]
            if steps_now is not None:  # s6: frame index in the cycle, s7: which step sound
                a.addiu("s6", "s6", 1)
                wrap = fresh("cycle")
                a.slti("t0", "s6", steps_now.cycle)
                a.bnez("t0", wrap)
                a.move("s6", "zero")
                a.label(wrap)
                for frame in steps_now.frames:
                    skip = fresh("nostep")
                    a.li("t0", frame)
                    a.bne("s6", "t0", skip)
                    other = fresh("step")
                    done = fresh("stepped")
                    a.bnez("s7", other)
                    host.play_sound(a, steps_now.events[0])
                    a.beq("zero", "zero", done)
                    a.label(other)
                    host.play_sound(a, steps_now.events[-1])
                    a.label(done)
                    a.li("t0", 1)
                    a.xor("s7", "s7", "t0")
                    a.label(skip)
        host.load_controller(a)

    def sleep(ticks: int, host_ticks: int | None = None) -> None:
        n = _scale(ticks, donor_ticks) if host_ticks is None else host_ticks
        host.sleep_ticks(a, n, fresh("sleep"))
        host.load_controller(a)

    def emit(steps: list[dict[str, Any]], after: str | None) -> None:
        for step in _sleep_runs(steps, donor_ticks):
            op = step["op"]
            if op in skip:
                continue
            if op == "stamp":
                if cooldown is not None:
                    emit_stamp(a, cooldown, fresh("stamped"))
                continue  # else not lowered (projectiles: the host one-projectile rule instead)
            elif op == "afterimage":
                if afterimage is None:
                    raise ValueError(f"{label}: afterimage step without its process")
                lp.emit_afterimage_spawn(a, afterimage, fresh("afterimage"))
                host.load_controller(a)
            elif op == "relocate":
                a.li("a0", int(step["dx"]) * lp.UNITS_PER_PX)
                a.jal_label("relocate")
                host.load_controller(a)
            elif op == "begin":
                host.set_special_lock(a)
                host.set_action_id(a, ICE_ACTION_ID)
                turn = step.get("face", True) if face is None else face
                host.special_begin(a, face=turn)  # stop, (face), busy input map
                host.load_controller(a)
                emit_charge(a, cost)
            elif op == "animate":
                where = anim_at(step["anim"], bool(step.get("reverse")))
                until = step.get("until")
                if until == "running":  # rate-stepped by the motion that follows (MKT next_anirate)
                    select(where)
                    a.li("a0", _scale(int(step["rate"]), donor_ticks))
                    a.jal(host.F_RATE_INIT)
                    running[0] = _scale(int(step["rate"]), donor_ticks)
                    host.load_controller(a)
                    continue
                if until not in ("phase_end", "manual"):
                    raise ValueError(f"{label}: animation end {until!r} is not lowered yet")
                if helper is not None and until == "phase_end":
                    lp.emit_spawn(a, helper, after=fresh("helper"))
                key = (int(step["anim"]["table"]), int(step["anim"]["slot"]))
                stepping[0] = (footsteps or {}).get(key) if until == "manual" else None
                if stepping[0] is not None:
                    a.move("s6", "zero")
                    a.move("s7", "zero")
                select(where)
                if until == "phase_end":
                    if "rate_reacting" in step:  # MKT: faster while the opponent is in a reaction
                        quick = fresh("quick")
                        host.load_controller(a)
                        host.opponent_reacting(a, "s0", "t8", quick + "_read")
                        a.li("a0", _scale(int(step["rate"]), donor_ticks))
                        a.beqz("t8", quick)
                        a.li("a0", _scale(int(step["rate_reacting"]), donor_ticks))
                        a.label(quick)
                    else:
                        a.li("a0", _scale(int(step["rate"]), donor_ticks))
                    a.jal(F_TO_PHASE_END)
                    host.load_controller(a)
                else:  # show the first frame (index 0); next_frame steps advance it
                    held, stepping[0] = stepping[0], None
                    advance()
                    stepping[0] = held
            elif op == "pose":
                select(anim_at(step["anim"]), int(step["anim"].get("offset", 0)))
                advance()
            elif op == "next_frame":  # a per-tick loop advances once per donor tick it stands for
                advance(step.get("_times", donor_ticks))
            elif op == "pass_through":  # see the docstring
                host.load_controller(a)
                a.lhu("t0", lp.ACTOR_FLAGS, "s1")
                a.andi("t0", "t0", 0xFFFF ^ LIT_BIT)
                a.sh("t0", lp.ACTOR_FLAGS, "s1")
                if moves:
                    a.move("a0", "s1")
                    a.move("a1", "s5")
                    a.jal(F_SET_XVEL)
                    host.load_controller(a)
            elif op == "velocity":
                if speed is None:
                    raise ValueError(f"{label}: velocity needs a speed conversion")
                host.load_controller(a)
                a.li("a1", speed(lp._int(step["x"])))
                a.lhu("t0", lp.ACTOR_FLAGS, "s1")
                a.andi("t0", "t0", FACING_BIT)
                ahead = fresh("ahead")
                a.beqz("t0", ahead)
                a.subu("a1", "zero", "a1")  # facing left: negative x
                a.label(ahead)
                a.move("s5", "a1")  # pass_through re-applies it
                a.move("a0", "s1")
                a.jal(F_SET_XVEL)
                host.load_controller(a)
            elif op == "stop":
                host.load_controller(a)
                host.stop(a)
                host.load_controller(a)
            elif op == "hover":  # level flight: no gravity, no y motion, airborne counter kept
                # The counter counts every tick, also at floor height: with it at zero the
                # per-tick floor check 0x80024BA8 installs the stock fall where no floor region
                # matches (a ground torpedo over a ledge). It also keeps him from landing (only
                # by crossing); the closing ``jump`` clears it.
                host.load_controller(a)
                a.sw("zero", host.ACTOR_GRAVITY, "s1")
                a.sw("zero", host.ACTOR_YVEL, "s1")
                a.lhu("t0", host.CTRL_AIRBORNE, "s0")
                a.addiu("t0", "t0", 1)
                a.sh("t0", host.CTRL_AIRBORNE, "s0")
            elif op == "carry":  # see emit_carry_reaction
                if carry is None:
                    raise ValueError(f"{label}: carry step without a carry word")
                loop, out = fresh("carry"), fresh("carried")
                a.la("t0", carry)
                a.li("t1", 1)
                a.sw("t1", 0, "t0")
                a.li("s3", _scale(int(step["ticks"]), donor_ticks))
                a.label(loop)
                emit(step.get("every_tick", []), None)
                a.la("t0", carry)
                a.lw("t1", 0, "t0")
                a.beqz("t1", out)  # the victim reached a wall
                host.load_controller(a)
                host.sleep_tick(a)
                host.load_controller(a)
                a.addiu("s3", "s3", -1)
                a.bnez("s3", loop)
                a.label(out)
                a.la("t0", carry)
                a.sw("zero", 0, "t0")  # release
                host.load_controller(a)
            elif op == "jump" and step["until"] in ("below_screen", "surface"):
                motion = (motions or {}).get(id(step))
                if motion is None:
                    raise ValueError(f"{label}: jump {step['until']} has no alias script")
                strike_at = None
                if "strike" in step:
                    strike_at = motion.near_from
                    record_for(step["strike"])  # the record the strike routine checks
                    a.la("t0", hit_word)
                    a.sw("zero", 0, "t0")
                if step["until"] == "surface":
                    rise[0] = motion
                host.load_controller(a)
                if step["until"] == "below_screen" and air_start:
                    _emit_fall_then_sink(a, motion, lp._int(step["y"]), lp._int(step["gravity"]), fresh("fall"))
                    continue
                host.set_cursor(a, motion.script)
                host.advance_animation(a)
                a.li("s2", motion.steps - 1)
                tick = fresh("motion")
                a.label(tick)
                host.sleep_tick(a)
                host.load_controller(a)
                host.advance_animation(a)
                if strike_at is not None:  # the last ``steps - near_from`` ticks: near the floor
                    far = fresh("far")
                    a.slti("t0", "s2", motion.steps - strike_at + 1)
                    a.beqz("t0", far)
                    a.jal_label(f"{label}_strike_once")
                    a.label(far)
                    host.load_controller(a)
                a.addiu("s2", "s2", -1)
                a.bnez("s2", tick)
                host.load_controller(a)
            elif op == "jump" and "y" not in step:  # on from the motion's velocity (a rise)
                motion = rise[0]
                if motion is None or motion.surface_velocity is None:
                    raise ValueError(f"{label}: a jump without y follows no rise")
                cb = None
                if "strike" in step:
                    cb = fresh("callback")
                    blocked = physics.convert_acceleration(lp._int(step["gravity_on_block"])) if "gravity_on_block" in step else None
                    callbacks.append((cb, record_for(step["strike"]), blocked))
                host.load_controller(a)
                if cb is not None:
                    a.la("t0", cb)
                    a.sw("t0", CTRL_JUMP_CALLBACK, "s0")  # the stock jump calls it each air tick
                a.move("a0", "s1")
                a.li("a1", physics.convert_velocity(lp._int(step.get("x", 0))))
                a.li("a2", physics.convert_velocity(motion.surface_velocity))
                a.li("a3", physics.convert_acceleration(lp._int(step["gravity"])))
                a.li("t0", running[0] if running[0] is not None else JUMP_KEEP)
                a.sw("t0", 0x10, "sp")
                a.li("t0", -1)
                a.sw("t0", 0x14, "sp")  # root: keep the current animation
                if cb is None:
                    a.sw("zero", CTRL_JUMP_CALLBACK, "s0")
                a.jal(F_JUMP)
                host.load_controller(a)
                a.sw("zero", CTRL_JUMP_CALLBACK, "s0")
            elif op == "jump":  # the stock jump/fall to the floor (returns on landing)
                host.load_controller(a)
                if air_control:
                    a.move("a0", "s1")
                    a.li("a1", AIR_MAP)
                    a.jal(host.F_INPUT_MAP)
                    host.load_controller(a)
                x, y, g = (lp._int(step.get(k, 0)) for k in ("x", "y", "gravity"))
                a.move("a0", "s1")
                a.li("a1", physics.convert_velocity(x))
                a.li("a2", physics.convert_velocity(y))
                a.li("a3", physics.convert_acceleration(g))
                # rate: the stock jump steps the current animation at it each air tick
                # (0x80031724 / 0x8003174C); 13 keeps the animation as it is
                rate = _scale(int(step["rate"]), donor_ticks) if "rate" in step else JUMP_KEEP
                a.li("t0", rate)
                a.sw("t0", 0x10, "sp")
                a.li("t0", -1)
                a.sw("t0", 0x14, "sp")  # root: keep the current animation
                a.sw("zero", CTRL_JUMP_CALLBACK, "s0")  # no per-tick callback (see above)
                a.jal(F_JUMP)
                host.load_controller(a)
            elif op == "face":
                host.load_controller(a)
                host.face_opponent(a)
                host.load_controller(a)
            elif op == "flip":  # turn around: the host's own turn (0x80031EF0 calls it)
                host.load_controller(a)
                a.move("a0", "s1")
                a.jal(F_TURN)
                host.load_controller(a)
            elif op == "shake_screen":
                shaker = fresh("shaker")
                shakers.append((shaker, step))
                a.li("a0", SHAKE_PROCESS_ID)
                a.la("a1", shaker)
                a.jal(F_PROCESS_CREATE)  # no process left: no shake
                host.load_controller(a)
            elif op == "shake":
                dx = int(step["dx"]) * lp.UNITS_PER_PX
                dy = int(step.get("dy", 0)) * lp.UNITS_PER_PX
                for _ in range(int(step["count"])):
                    for sign in (1, -1):
                        host.load_controller(a)
                        a.move("a0", "s1")
                        a.li("a1", sign * dx)
                        a.li("a2", sign * dy)
                        a.jal(host.F_OFFSET)
                        sleep(int(step["ticks"]))
            elif op == "repeat":
                timed = _timed_repeat(step, donor_ticks)
                loop = fresh("repeat")
                if timed is None:  # a per-tick loop: the count scales with the ticks
                    a.li("s4", _scale(int(step["count"]), donor_ticks))
                    a.label(loop)
                    emit(step["steps"], None)
                else:  # MKT's count, the sleeps spread so the total time is MKT's (see below)
                    count, bodies = timed
                    a.li("s4", count)
                    a.label(loop)
                    for body in bodies:
                        emit(body, None)
                a.addiu("s4", "s4", -1)
                a.bnez("s4", loop)
            elif op == "strike":
                _emit_strike(step)
            elif op == "sound":
                fighter = int(step["sound"]["fighter"])
                choices = [fighter + k for k in range(int(step["sound"].get("random", 1)))]
                if not sounds or any(n not in sounds for n in choices):
                    raise ValueError(f"{label}: fighter sound {choices} has no host event")
                played = fresh("played")
                for k, n in enumerate(choices[:-1]):  # one of k..: a per-thousand gate each
                    other = fresh("other")
                    a.li("a0", 1000 // (len(choices) - k))
                    a.jal(F_RANDPER)
                    a.andi("v0", "v0", 0xFFFF)
                    a.li("t0", 0x8000)
                    a.bne("v0", "t0", other)
                    host.play_sound(a, sounds[n])
                    a.beq("zero", "zero", played)
                    a.label(other)
                host.play_sound(a, sounds[choices[-1]])
                a.label(played)
                host.load_controller(a)
            elif op == "projectile":
                if child is None:
                    raise ValueError(f"{label}: projectile step without a child process")
                if helper is not None:  # the helper goes first: one type-4 object at a time
                    lp.emit_helper_handover(a, helper, fresh("handover"))
                    host.load_controller(a)
                lp.emit_spawn(a, child, after=fresh("spawned"))
            elif op == "sleep":
                sleep(int(step["ticks"]), step.get("_host_ticks"))
            elif op == "finish":
                a.li("a0", _scale(int(step["rate"]), donor_ticks))
                a.jal(F_TO_PHASE_END)
                host.load_controller(a)
            elif op == "effect":
                fx = int(step["effect"]["mkt_fx"])
                if not effects or fx not in effects:
                    raise ValueError(f"{label}: MKT effect {fx} is not ported")
                descriptor, dy = effects[fx]
                host.load_controller(a)
                a.move("a0", "s1")
                a.la("a1", descriptor)
                a.li("a2", (dy & 0xFFFF) << 16)
                a.li("a3", FRONT_SUBLAYER)
                a.jal_label("fx_spawn_xy")
                host.load_controller(a)
            elif op == "stealth":
                if stealth is None:
                    raise ValueError(f"{label}: stealth step without a timer process")
                emit_stealth_start(a, stealth, fresh("stealth"))
                host.load_controller(a)
            elif op == "end":
                if passes:
                    host.load_controller(a)
                    a.lhu("t0", lp.ACTOR_FLAGS, "s1")
                    a.ori("t0", "t0", LIT_BIT)
                    a.sh("t0", lp.ACTOR_FLAGS, "s1")
                if moves:  # MKT's reaction_exit leaves no motion behind
                    host.load_controller(a)
                    host.stop(a)
                    host.load_controller(a)
                host.exit_action(a, hang=fresh("hang"))
            else:
                raise ValueError(f"{label}: step {op!r} is not lowered yet")
        if after is not None:
            a.beq("zero", "zero", after)

    def record_for(strike: dict[str, Any]) -> str:
        """The move's one motion strike record (a rise and its flight check the same strike)."""

        if motion_strike[0] is None:
            meaning = strike["reaction"]
            table = {**STOCK_REACTIONS, **(reactions or {})}
            if meaning not in table:
                raise ValueError(f"{label}: strike reaction {meaning!r} has no host reaction")
            motion_strike[0] = fresh("record")
            records.append((motion_strike[0], lp.strike_record(strike, table[meaning])))
        return motion_strike[0]

    def _emit_strike(step: dict[str, Any]) -> None:
        strike = step["strike"]
        meaning = strike["reaction"]
        table = {**STOCK_REACTIONS, **(reactions or {})}
        if meaning not in table:
            raise ValueError(f"{label}: strike reaction {meaning!r} has no host reaction")
        rec = fresh("record")
        records.append((rec, lp.strike_record(strike, table[meaning])))
        loop, miss, hit, block, done = (fresh(t) for t in ("window", "miss", "hit", "block", "after"))
        a.li("s3", _scale(int(step["ticks"]), donor_ticks))
        a.label(loop)
        emit(step.get("every_tick", []), None)
        # only_if "opponent_settled" (MKT q_his_react_flag_set) is not lowered: the collision
        # core scans every enemy, and the window ends at the first contact.
        a.la("a0", rec)
        a.lui("t0", lp.KSEG1_TO_KSEG0 >> 16)
        a.subu("a0", "a0", "t0")  # KSEG0 alias: the collision core rejects other records
        a.move("a1", "zero")
        a.jal(host.F_STRIKE)
        a.andi("v0", "v0", 0xFFFF)
        a.li("t0", 0x8000)
        a.bne("v0", "t0", miss)
        a.lui("t0", hi(BLOCKED_FLAG))
        a.lhu("t0", lo(BLOCKED_FLAG), "t0")
        a.bnez("t0", block)
        a.beq("zero", "zero", hit)
        a.label(miss)
        host.load_controller(a)
        host.sleep_tick(a)
        host.load_controller(a)
        a.addiu("s3", "s3", -1)
        a.bnez("s3", loop)
        a.beq("zero", "zero", done)
        a.label(hit)
        host.load_controller(a)
        emit(step.get("on_hit", []), done)
        a.label(block)
        host.load_controller(a)
        emit(step.get("on_block", []), done)
        a.label(done)
        host.load_controller(a)

    a.label(label)
    host.enter_action(a, host.Frame(size=0x40, strike_offset=0x30), ())
    host.load_controller(a)
    emit(steps, None)
    if motion_strike[0] is not None:  # after the action root, which never returns
        _emit_strike_once(a, f"{label}_strike_once", motion_strike[0], hit_word)
        for cb, rec, blocked in callbacks:
            _emit_rising_strike(a, cb, f"{label}_strike_once", hit_word, blocked)
        while a.pc() & 3:
            a.nop()
        a.label(hit_word)
        a.raw(0)
    for shaker, step in shakers:  # after the action root, which never returns
        emit_screen_shake(a, shaker, int(step["amplitude"]) * lp.UNITS_PER_PX, int(step["count"]),
                          _scale(int(step["ticks"]), donor_ticks))  # fmt: skip
    return records


@dataclass(frozen=True)
class Footsteps:
    cycle: int  # frames in the looping animation
    frames: tuple[int, ...]  # frame indices reached right after a donor footstep callback
    events: tuple[int, ...]  # host sound events, alternated


MKT_FOOTSTEP_CALLBACK = 8  # token 6 operand: 0x8000518C, random of group 0x800A1A3C (Wiki)
MKT_FOOTSTEP_GROUP = 0x800A1A3C  # four u16 MKT sound events
MKT_TOKEN_CALLBACK = 6


def donor_footsteps(donor: Any, slot: int) -> tuple[int, tuple[int, ...]]:
    """(frame count, frames reached right after each footstep callback) of a looping MKT
    table-0 animation (e.g. the Run, slot 0x4A: callback 8 before frames 3 and 7 of 9)."""

    p, frames, steps = donor.m32(4 * slot), 0, []
    while True:
        v = donor.m32(p)
        if v in (0, 1):
            break
        if v == MKT_TOKEN_CALLBACK:
            if donor.m32(p + 4) == MKT_FOOTSTEP_CALLBACK:
                steps.append(frames)
            p += 8
            continue
        if v < 0x20:
            raise ValueError(f"MKT token {v} in a footstep animation is not supported")
        frames += 1
        p += 4
    return frames, tuple(s % frames for s in steps)


def emit_strike_data(a: Assembler, records: list[tuple[str, bytes]], base: int) -> None:
    """The strike records, 16-aligned (read through their KSEG0 alias)."""

    for name, record in records:
        while (a.pc() - base) % 16:
            a.nop()
        a.label(name)
        for i in range(0, 16, 4):
            a.raw(int.from_bytes(record[i : i + 4], "big"))


# MKT reaction 0x74 (``r_reptile_dash``): a grounded victim stands still for 20 donor ticks,
# then exits; it selects no animation. Host: the stock hit reaction 0x10 (``0x80054B20``) without
# its two hit voices and its flinch: preamble (with its airborne handler), stop, a still hold in
# the victim's current frame, exit. Specials proof v15 also showed the first hit pose (slot
# 0x1C); the owner saw a hit, not a hold. ``0x800504C4`` starts the hit (blood) effect at the
# victim: dropped from v17 (owner: "a blood effect ... shouldn't be there").
HOLD_DONOR_TICKS = 20
F_REACT_A, F_REACT_B = 0x800504C4, 0x800556A4  # stock reaction 0x10 preamble: hit effect, 0x103
F_REACT_PREAMBLE, AIRBORNE_HANDLER = 0x80053028, 0x800532F8
HIT_SLOT = 0x1C  # victim primary slot of the stock hit flinch


def emit_hold_reaction(a: Assembler, label: str, donor_ticks: int = 1, pose: bool = False,
                       blood: bool = False) -> None:  # fmt: skip
    """Victim reaction ``elbow_hold`` (installed by the collision core as the victim's callback)."""

    a.label(label)
    a.addiu("sp", "sp", -0x30)
    a.sw("ra", 0x28, "sp")
    for k, reg in enumerate(("s0", "s1", "s2")):
        a.sw(reg, 0x18 + 4 * k, "sp")
    if blood:  # specials proofs v15-v16
        a.jal(F_REACT_A)
    a.jal(F_REACT_B)
    a.move("a0", "zero")
    a.li("a1", AIRBORNE_HANDLER)
    a.move("a2", "zero")
    a.move("a3", "zero")
    a.jal(F_REACT_PREAMBLE)
    host.load_controller(a)
    host.stop(a)
    host.load_controller(a)
    a.lw("t0", 0x64, "s1")
    a.ori("t0", "t0", 4)
    a.sw("t0", 0x64, "s1")
    if pose:  # specials proof v15
        a.move("a0", "zero")
        a.li("a1", HIT_SLOT)
        a.jal(lp.F_SELECT)
        host.load_controller(a)
        host.advance_animation(a)
    host.sleep_ticks(a, _scale(HOLD_DONOR_TICKS, donor_ticks), label + "_hold")
    host.load_controller(a)
    a.move("a0", "s1")
    a.jal(host.F_EXIT)
    for k, reg in enumerate(("s0", "s1", "s2")):
        a.lw(reg, 0x18 + 4 * k, "sp")
    a.lw("ra", 0x28, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x30)


# MKT torpedo carry (Rayden, 0x800452C4): on a hit the torpedo takes the victim along. Rayden keeps
# flying for up to 0x20 donor ticks (both objects share one velocity) unless a wall stops them; then
# the screen shakes, his sound 13 plays and the victim's process restarts at 0x8004558C: his
# table-0 slot 0x1A pose, do_jump(0x33333, -0x6CCCD, 0x5199), landing. Host (specials proof v03):
# the victim reaction below holds the victim at a grab point in front of the player each tick, in
# the first frame of root 0x1E, while the attacker's ``carry`` step keeps the shared word set; it
# clears the word itself when the victim's room to the wall ahead runs out, then
# tail-calls the lifted knockback ``torpedo_carry_release`` (``lower_projectile``), which plays
# the throw from its own start. The victim morphs first, as the stock launch does, because root
# 0x1E is a shared root (Wiki Fighter-Recompiler-Components, "knockback morph").
CARRY_ROOT = 0x1E
CARRY_WALL_MARGIN = 40  # whole units (20 px) of room left ahead of the victim
CARRY_TIMEOUT_TICKS = 24  # host ticks: past the attacker's 16 (0x20 donor ticks at 2 per tick)
# The grab point (specials proof v04; owner on v03: Rayden's hands should hold the victim's waist,
# and an airborne torpedo must not carry the victim along the ground or off a ledge). x: in front
# of the player's anchor, toward his facing; y: from the player's y (actor y grows downward). The
# flat frame 0x2100 reaches 66 px in front of his anchor (136 px wide, anchor at 70); a ground
# carry at the same y looked right (owner, v03).
CARRY_DX_PX, CARRY_DY_PX = 72, 0  # the v04-v08 calibration; dropped in v09 (owner: pure MKT)
ACTOR_PREV_Y = 0x3C  # floor landing is by crossing from the previous y (0x80025ED4)


def emit_carry_reaction(a: Assembler, label: str, word: str, release: str,
                        morphs: tuple[int, ...], dx_px: int | None = None,
                        dy_px: int | None = None) -> None:  # fmt: skip
    """Victim reaction ``torpedo_carry`` (see the notes above); ``word``: the attacker's carry
    word, ``release``: the lifted knockback's label, ``morphs``: the victim morph routines;
    ``dx_px``, ``dy_px``: a grab point (an owner calibration, specials proof v04-v08); without
    them the victim keeps its contact distance and its own height, as MKT's shared velocity does.
    While held it has no gravity or vertical speed and its airborne counter counts (as ``hover``),
    so it neither falls nor lands on a floor or a ledge before the release."""

    frame = 0x30
    a.label(label)
    a.addiu("sp", "sp", -frame)
    a.sw("ra", 0x28, "sp")
    for k, reg in enumerate(("s0", "s1", "s2", "s3")):
        a.sw(reg, 0x18 + 4 * k, "sp")
    for target in morphs:
        host.load_controller(a)
        a.move("a0", "s1")
        a.jal(target)
    host.load_controller(a)
    host.stop(a)
    a.move("a0", "zero")
    a.li("a1", CARRY_ROOT)
    a.jal(lp.F_SELECT)
    host.load_controller(a)
    host.advance_animation(a)

    def player_actor(reg: str) -> None:
        a.lui(reg, hi(host.PLAYER_CTRL))
        a.lw(reg, lo(host.PLAYER_CTRL), reg)
        a.lw(reg, host.CTRL_ACTOR, reg)

    if dx_px is None:  # MKT: the contact distance, kept (signed, so no facing test)
        host.load_controller(a)
        player_actor("t0")
        a.lw("t1", host.ACTOR_X, "t0")
        a.lw("t2", host.ACTOR_X, "s1")
        a.subu("s2", "t2", "t1")
    else:
        a.li("s2", dx_px * lp.UNITS_PER_PX << 8)  # actor x is whole units << 8
    a.li("s3", CARRY_TIMEOUT_TICKS)
    a.label(label + "_loop")
    a.la("t0", word)
    a.lw("t1", 0, "t0")
    a.beqz("t1", label + "_out")  # the attacker let go
    host.load_controller(a)
    a.move("a0", "s1")
    a.addiu("a1", "sp", 0x10)
    a.addiu("a2", "sp", 0x14)
    a.jal(host.F_WALL_DISTANCE)
    player_actor("t0")
    a.lhu("t1", lp.ACTOR_FLAGS, "t0")
    a.andi("t1", "t1", lp.FACING_BIT)
    a.lw("t2", 0x14, "sp")  # carried right: the room on the right
    a.beqz("t1", label + "_room")
    a.lw("t2", 0x10, "sp")  # facing left: the room on the left
    a.label(label + "_room")
    a.slti("t3", "t2", CARRY_WALL_MARGIN)
    a.bnez("t3", label + "_wall")
    host.load_controller(a)
    player_actor("t0")
    a.move("t2", "s2")
    if dx_px is not None:
        a.lhu("t1", lp.ACTOR_FLAGS, "t0")
        a.andi("t1", "t1", lp.FACING_BIT)
        a.beqz("t1", label + "_ahead")
        a.subu("t2", "zero", "s2")  # he faces left: the grab point is to his left
        a.label(label + "_ahead")
    a.lw("t1", host.ACTOR_X, "t0")
    a.addu("t1", "t1", "t2")
    a.sw("t1", host.ACTOR_X, "s1")
    if dy_px is not None:
        a.lw("t1", host.ACTOR_Y, "t0")
        a.li("t2", dy_px * lp.UNITS_PER_PX << 8)
        a.addu("t1", "t1", "t2")
    else:
        a.lw("t1", host.ACTOR_Y, "s1")  # its own height, held
    a.sw("t1", host.ACTOR_Y, "s1")
    a.sw("t1", ACTOR_PREV_Y, "s1")  # moved, not falling: no landing by crossing
    a.sw("zero", host.ACTOR_GRAVITY, "s1")
    a.sw("zero", host.ACTOR_YVEL, "s1")
    # Every tick, also at floor height: the per-tick floor check 0x80024BA8 also runs for
    # enemies (classes 2-3) and installs the stock fall when no floor region matches and +0x6B0
    # is zero, i.e. at a ledge during a ground carry (v04: counted only above the floor).
    a.lhu("t1", host.CTRL_AIRBORNE, "s0")
    a.addiu("t1", "t1", 1)
    a.sh("t1", host.CTRL_AIRBORNE, "s0")
    host.sleep_tick(a)
    a.addiu("s3", "s3", -1)
    a.bnez("s3", label + "_loop")
    a.label(label + "_wall")
    a.la("t0", word)
    a.sw("zero", 0, "t0")
    a.label(label + "_out")
    for k, reg in enumerate(("s0", "s1", "s2", "s3")):
        a.lw(reg, 0x18 + 4 * k, "sp")
    a.lw("ra", 0x28, "sp")
    a.addiu("sp", "sp", frame)
    a.j_label(release)  # the throw, as the reaction itself (same sp and ra)


# Shock hold (Rayden's Shocker, MKT 0x80073228 on a grab): the victim gets a waiting routine
# (0x8005A1B8), is posed in its slot 0x20 at his hands (0x800733F8, per-fighter offsets) and, 8
# times, its shock palette goes on and off (0x8000FD28 / 0x8000F9B0, the cyan palette reaction 0x80
# uses) while it is moved 4 px and back every 3 donor ticks (0x800735BC); then it drops and lands
# knocked down (0x800734CC -> 0x80058728). The host: the victim stops, shows its root 0x20 and
# turns to face him; each tick it is held at his hands (the grab point below; no gravity, its
# airborne counter counting, as the carry), moved 4 px down and back every ``every`` ticks, and
# blinks cyan (the lightning's blink helper), then falls into the torpedo victim's release (the
# lifted knockback with no push). Specials proof v25-v26 held it where the strike found it.
SHOCK_ROOT = 0x20
# MKT: after the grab he shows his pose and sleeps 3 (0x80073314), then 8 shocks, each 2 halves of
# 2 x 3 donor ticks (0x80073378(8)); the victim is released after both (SMRE step 2: the hold
# ends with his shaking; specials proofs v25-v30 held it 96 donor ticks, without the first 3).
SHOCK_HOLD_DONOR_TICKS = 3 + 8 * 2 * 6
SHOCK_JIGGLE_DONOR_TICKS = 3
SHOCK_JIGGLE_PX = 4
# MKT 0x800733F8: match_ani_points(him, victim) gives the victim his position, flip_single turns
# it to face him, then multi_adjust_xy(victim, dx, dy - 8) from the per-victim table 0x800AAF8C
# (6 bytes: frame, dx, dy). Its common entry (16 of 28 fighters: the ninjas, Cage, Baraka, ...)
# is dx -44, dy -13; dx runs along the victim's facing, toward him, so the victim's anchor is
# 44 px in front of his and 21 px up (Static-confirmed reading). Host enemies are not MKT
# fighters: the common entry for all.
SHOCK_GRAB_DX_PX = 44
SHOCK_GRAB_DY_PX = -13 - 8


def emit_shock_hold_reaction(a: Assembler, label: str, release: str, morphs: tuple[int, ...],
                             ticks: int, every: int, blink: str) -> None:  # fmt: skip
    """Victim reaction ``shock_hold`` (see the notes above); ``ticks``, ``every`` in host ticks;
    ``blink``: the label of its blink process (``lower_projectile.emit_blink``)."""

    frame = 0x30
    a.label(label)
    a.addiu("sp", "sp", -frame)
    a.sw("ra", 0x28, "sp")
    for k, reg in enumerate(("s0", "s1", "s2", "s3")):
        a.sw(reg, 0x18 + 4 * k, "sp")
    for target in morphs:
        host.load_controller(a)
        a.move("a0", "s1")
        a.jal(target)
    host.load_controller(a)
    host.stop(a)
    a.move("a0", "zero")
    a.li("a1", SHOCK_ROOT)
    a.jal(lp.F_SELECT)
    host.load_controller(a)
    host.advance_animation(a)
    a.li("a0", lp.BLINK_PROCESS_ID)  # the cyan blink, with this controller as its argument
    a.la("a1", blink)
    a.jal(lp.F_CLONE)
    a.beqz("v0", label + "_noblink")
    a.sw("s0", 0x6F4, "v0")
    a.label(label + "_noblink")

    def player_actor(reg: str) -> None:
        a.lui(reg, hi(host.PLAYER_CTRL))
        a.lw(reg, lo(host.PLAYER_CTRL), reg)
        a.lw(reg, host.CTRL_ACTOR, reg)

    host.load_controller(a)  # it faces him (MKT flip_single after match_ani_points)
    player_actor("t0")
    a.lhu("t1", lp.ACTOR_FLAGS, "t0")
    a.lhu("t2", lp.ACTOR_FLAGS, "s1")
    a.xor("t1", "t1", "t2")
    a.andi("t1", "t1", lp.FACING_BIT)
    a.bnez("t1", label + "_faced")  # (the assembler fills branch delay slots)
    a.move("a0", "s1")
    a.jal(F_TURN)
    a.label(label + "_faced")
    a.li("s2", ticks)
    a.label(label + "_loop")
    host.load_controller(a)
    player_actor("t0")  # at his hands: his position plus the grab offset along his facing
    a.li("t2", SHOCK_GRAB_DX_PX * lp.UNITS_PER_PX << 8)  # actor x is whole units << 8
    a.lhu("t1", lp.ACTOR_FLAGS, "t0")
    a.andi("t1", "t1", lp.FACING_BIT)
    a.beqz("t1", label + "_ahead")
    a.subu("t2", "zero", "t2")  # he faces left: the grab point is to his left
    a.label(label + "_ahead")
    a.lw("t1", host.ACTOR_X, "t0")
    a.addu("t1", "t1", "t2")
    a.sw("t1", host.ACTOR_X, "s1")
    a.lw("s3", host.ACTOR_Y, "t0")
    a.li("t2", SHOCK_GRAB_DY_PX * lp.UNITS_PER_PX << 8)  # y grows downward: negative is up
    a.addu("s3", "s3", "t2")
    a.li("t0", every)  # down 4 px on every other ``every`` ticks
    a.div("s2", "t0")
    a.mflo("t1")
    a.nop()
    a.nop()
    a.andi("t1", "t1", 1)
    a.li("t2", SHOCK_JIGGLE_PX * lp.UNITS_PER_PX << 8)
    a.mult("t1", "t2")
    a.mflo("t1")
    a.nop()
    a.nop()
    a.addu("t1", "t1", "s3")
    a.sw("t1", host.ACTOR_Y, "s1")
    a.sw("t1", ACTOR_PREV_Y, "s1")
    a.sw("zero", host.ACTOR_GRAVITY, "s1")
    a.sw("zero", host.ACTOR_YVEL, "s1")
    a.lhu("t1", host.CTRL_AIRBORNE, "s0")
    a.addiu("t1", "t1", 1)
    a.sh("t1", host.CTRL_AIRBORNE, "s0")
    host.sleep_tick(a)
    a.addiu("s2", "s2", -1)
    a.bnez("s2", label + "_loop")
    host.load_controller(a)
    a.sw("s3", host.ACTOR_Y, "s1")  # at the grab height: the drop falls from his hands
    a.sw("s3", ACTOR_PREV_Y, "s1")
    for k, reg in enumerate(("s0", "s1", "s2", "s3")):
        a.lw(reg, 0x18 + 4 * k, "sp")
    a.lw("ra", 0x28, "sp")
    a.addiu("sp", "sp", frame)
    a.j_label(release)  # the drop, as the reaction itself (same sp and ra)


# Screen shake (MKT 0x8002A750(amplitude, count): a process that, every 3 ticks, moves the
# camera's vertical offset by the amplitude and flips its sign, count times). The host keeps
# camera shake offsets at 0x8009A928 (vertical) and 0x8009A92C (horizontal): the camera update
# adds them (0x800132A4: camera 0x8009A944 = [0x8009A928] - target y; 0x8009A948 = [0x8009A92C]
# + 160 - target x), its own shake process 0x80037A24 (process 0x15 at 0x80037CA0, used across
# the stages) writes them from a 16-step table and zeroes them at the end. Its shortest run is
# 16 steps; MKT's is 6, so the move runs MKT's algorithm on the same offset and zeroes it.
SHAKE_PROCESS_ID = 0x15  # as the host's shakes
SHAKE_VERTICAL = 0x8009A928


def emit_screen_shake(a: Assembler, label: str, amplitude: int, count: int, ticks: int) -> None:
    """Process ``label``: MKT's screen shake on the host's vertical camera offset
    (``amplitude`` in world units), then the offset back to 0 and exit."""

    a.label(label)
    a.li("s0", count)
    a.li("s1", amplitude)
    a.label(label + "_step")
    a.lui("t0", hi(SHAKE_VERTICAL))
    a.lw("t1", lo(SHAKE_VERTICAL), "t0")
    a.subu("t1", "t1", "s1")
    a.sw("t1", lo(SHAKE_VERTICAL), "t0")
    a.subu("s1", "zero", "s1")
    a.li("a0", ticks)
    a.jal(F_SLEEP)
    a.addiu("s0", "s0", -1)
    a.bnez("s0", label + "_step")
    a.lui("t0", hi(SHAKE_VERTICAL))
    a.sw("zero", lo(SHAKE_VERTICAL), "t0")
    a.jal(F_PROCESS_EXIT)


# Victim reactions the builder supplies as payload routines (strike meanings that are not
# STOCK_REACTIONS and not lifted projectile reactions), each in a spare reaction-table entry.
# One table instead of a builder branch per reaction: a new reaction is a row here.
@dataclass(frozen=True)
class ReactionContext:
    tune: dict[str, Any]  # the move's ``specials`` tuning
    donor_ticks: int
    clean: bytes


@dataclass(frozen=True)
class VictimReaction:
    suffix: str  # routine label: "<move>_<suffix>"
    emit: Callable[[Assembler, str, ReactionContext], None]
    word: bool = False  # the attacker's steps share "<label>_word" with it (``carry``)


def _emit_hold(a: Assembler, label: str, ctx: ReactionContext) -> None:
    emit_hold_reaction(a, label, ctx.donor_ticks)


def _emit_carry(a: Assembler, label: str, ctx: ReactionContext) -> None:
    grab = ctx.tune.get("carry", {})  # specials.<move>.carry: a grab point, in px (owner)
    release = label + "_release"
    emit_carry_reaction(a, label, label + "_word", release,
                        lp.REACTION_LOWERING["torpedo_carry_release"]["morph"],
                        dx_px=lp._int(grab["dx_px"]) if "dx_px" in grab else None,
                        dy_px=lp._int(grab["dy_px"]) if "dy_px" in grab else None)  # fmt: skip
    a.label(release)
    for w in lp.lifted_reaction(ctx.clean, "torpedo_carry_release"):
        a.raw(w)
    a.label(label + "_word")
    a.raw(0)


def _emit_shock_hold(a: Assembler, label: str, ctx: ReactionContext) -> None:
    ticks = _scale(SHOCK_HOLD_DONOR_TICKS, ctx.donor_ticks)
    every = _scale(SHOCK_JIGGLE_DONOR_TICKS, ctx.donor_ticks)
    release, blink = label + "_release", label + "_blink"
    emit_shock_hold_reaction(a, label, release, lp.REACTION_LOWERING["torpedo_carry_release"]["morph"],
                             ticks, every, blink)  # fmt: skip
    a.label(release)
    for w in lp.lifted_reaction(ctx.clean, "torpedo_carry_release"):
        a.raw(w)
    # the palette goes on and off once per 6-donor-tick half (0x800735BC), 8 times each
    lp.emit_blink(a, blink, (0x20, 0xFF, 0xFF), 16, _scale(2 * SHOCK_JIGGLE_DONOR_TICKS, ctx.donor_ticks))


VICTIM_REACTIONS: dict[str, VictimReaction] = {
    "elbow_hold": VictimReaction("hold", _emit_hold),
    "torpedo_carry": VictimReaction("carry", _emit_carry, word=True),
    "shock_hold": VictimReaction("shock", _emit_shock_hold),
}


# Stealth (Reptile's Invisibility): the Eye item's effect (Wiki Fighter-Recompiler-Components,
# "Eye item"). 0x80072584 sets it on the player: controller +0x6BC |= 0x1000 (enemy AI
# idles), actor +0x8C |= 0x4000, +0x64 |= 0x2000, colour +0xFC/+0xFE/+0x100 = 32 (also on the
# attached actor +0x650), 0x800A5FA0 |= 1, and the request bit 0x802ECCC6 |= 1, which the
# Inventory turns into its 1200-tick timer 0x80072644 when it closes (0x80073BD0..0x80073C04).
# A special clears the request itself (or the next Inventory visit would start a stray timer)
# and runs its own timer, which undoes the effect only if no newer stealth started since: a hit
# ends stealth early (0x80053594..0x800535F8), so a recast must not be cut short by an older
# timer.
F_EYE_USE = 0x80072584
EYE_REQUEST = 0x802ECCC6  # halfword, bit 0
EYE_EFFECT = 0x800A5FA0  # halfword, bit 0
STEALTH_BIT = 0x1000  # player controller +0x6BC
CTRL_STEALTH = 0x6BC
STEALTH_ACTOR_FLAG = 0x4000  # actor +0x8C
STEALTH_ACTOR_64 = 0x2000  # actor +0x64
NORMAL_COLOUR = 0x80
CTRL_ARG = 0x6F4  # a new process's argument word (written after creation, as effects do)
FRONT_SUBLAYER = 0xFFFF  # effects drawn in front (stock Ice helper value)
TIMER_PROCESS_ID = 0x100  # as the Eye timer


def emit_stealth_start(a: Assembler, timer: str, tag: str) -> None:
    """Start stealth and its timer process ``timer`` (generation in ``timer_gen``)."""

    a.jal(F_EYE_USE)
    a.lui("t0", hi(EYE_REQUEST))
    a.lhu("t1", lo(EYE_REQUEST), "t0")
    a.andi("t1", "t1", 0xFFFE)
    a.sh("t1", lo(EYE_REQUEST), "t0")
    a.la("t0", timer + "_gen")
    a.lw("t1", 0, "t0")
    a.addiu("t1", "t1", 1)
    a.sw("t1", 0, "t0")
    a.li("a0", TIMER_PROCESS_ID)
    a.la("a1", timer)
    a.jal(F_PROCESS_CREATE)
    a.bnez("v0", tag + "_timed")
    a.jal_label(timer + "_undo")  # no process left: no stealth rather than endless stealth
    a.beq("zero", "zero", tag + "_done")
    a.label(tag + "_timed")
    a.la("t0", timer + "_gen")
    a.lw("t1", 0, "t0")
    a.sw("t1", CTRL_ARG, "v0")
    a.label(tag + "_done")


def emit_stealth_timer(a: Assembler, label: str, period: int, drain: int) -> None:
    """The stealth process (entered with its own controller current), its undo subroutine (the
    stock timer's tail, ``0x80072654..0x800726BC``) and its generation word.

    Owner (specials proof v18): stealth lasts while it is paid for, not a fixed time. Every
    ``period`` ticks it takes ``drain`` Ice (controller ``+0x656``; the meter refills 1 every 5
    ticks up to ``0xA6``, ``0x8005C3A4..0x8005C3D4``); when the meter cannot pay, stealth ends.
    It stops without undoing when a hit (``0x80053594``) or a newer stealth already ended it."""

    a.label(label)
    host.load_controller(a)
    a.lw("s2", CTRL_ARG, "s0")  # the generation it was started for
    a.label(label + "_tick")
    a.li("a0", period)
    a.jal(F_SLEEP)
    a.la("t0", label + "_gen")
    a.lw("t1", 0, "t0")
    a.bne("t1", "s2", label + "_exit")  # a newer stealth owns the effect
    a.lui("a0", hi(PLAYER_CTRL))
    a.lw("a0", lo(PLAYER_CTRL), "a0")
    a.lhu("t0", CTRL_STEALTH, "a0")
    a.andi("t0", "t0", STEALTH_BIT)
    a.beqz("t0", label + "_exit")  # already ended (a hit)
    a.lhu("t0", CTRL_ICE, "a0")
    a.slti("t1", "t0", drain)
    a.bnez("t1", label + "_end")
    a.addiu("t0", "t0", -drain)
    a.sh("t0", CTRL_ICE, "a0")
    a.beq("zero", "zero", label + "_tick")
    a.label(label + "_end")
    a.jal_label(label + "_undo")
    a.label(label + "_exit")
    a.jal(F_PROCESS_EXIT)
    a.label(label + "_hang")
    a.beq("zero", "zero", label + "_hang")
    a.label(label + "_undo")
    a.lui("a0", hi(PLAYER_CTRL))
    a.lw("a0", lo(PLAYER_CTRL), "a0")
    a.lhu("t0", CTRL_STEALTH, "a0")
    a.andi("t0", "t0", 0xFFFF ^ STEALTH_BIT)
    a.sh("t0", CTRL_STEALTH, "a0")
    a.lw("t1", host.CTRL_ACTOR, "a0")
    a.lhu("t0", lp.ACTOR_FLAGS, "t1")
    a.andi("t0", "t0", 0xFFFF ^ STEALTH_ACTOR_FLAG)
    a.sh("t0", lp.ACTOR_FLAGS, "t1")
    a.lw("t0", 0x64, "t1")
    a.li("t2", ~STEALTH_ACTOR_64 & 0xFFFFFFFF)
    a.and_("t0", "t0", "t2")
    a.sw("t0", 0x64, "t1")
    a.li("t0", NORMAL_COLOUR)
    for off in (0xFC, 0xFE, 0x100):
        a.sh("t0", off, "t1")
    a.lui("t0", hi(EYE_EFFECT))
    a.lhu("t2", lo(EYE_EFFECT), "t0")
    a.andi("t2", "t2", 0xFFFE)
    a.sh("t2", lo(EYE_EFFECT), "t0")
    a.jr_ra()
    a.nop()
    a.label(label + "_gen")
    a.raw(0)
