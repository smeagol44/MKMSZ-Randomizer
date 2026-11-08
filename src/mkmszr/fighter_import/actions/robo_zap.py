"""Sektor's straight rocket (MKT ``do_robo_zap`` / ``rocket1_proc``) on the MKMSZ host.

The rocket is built by re-hosting stock Ice Blast and swapping donor behaviour in one
piece at a time (Wiki ``MKT-Adapter-Primitives``, "Importer direction"). The host is a
lifted copy of the stock Ice root (:mod:`..lifter`); every behavioural change is a
declared word patch on that copy, checked against the stock word it replaces, so the
stock root (still used by Sub-Zero's up/down Ice) is never touched.

Donor facts are MKT USA Rev. 2 N64 retail values (not the arcade source lineage).
"""

from __future__ import annotations

from .. import host, physics
from ..host import F_OFFSET, UNITS_PER_TEXEL, hi, lo
from ..lifter import LiftError, LiftResult
from ..mips import REG, Assembler

# Stock MKMSZ Ice host (USA Rev. 0)
ICE_CALLBACK_SRC, ICE_CALLBACK_END = 0x80049C34, 0x80049C84  # LP record action
ICE_CALLBACK_GROUND_SELECTOR = 0x80049C70  # 'move a0, zero' -> transfer selector
ICE_ROOT_SRC, ICE_ROOT_END = 0x8004AB84, 0x8004B1D0  # transfer selector 0 (all Ice modes)

# Donor: retail placement of the rocket relative to Sektor, in sprite pixels (source
# adjust_xy_a5(SCX(7), SCY(45))). The host helper takes world units: x UNITS_PER_TEXEL.
# (v72/v24 passed the pixel values unscaled: half the distance, too high and inward.)
PLACEMENT = (5, 38)
# Runtime-observed correction (user frame-by-frame MKT vs MKMSZ captures, proof v27): at
# the start of its trajectory MKT's flat rocket sits 3-4 px further out than the derived
# placement, with no flame visible behind Sektor. MKT first shows a vertical rocket frame
# (a donor glitch, not reproduced); anchor arithmetic does not explain the offset (a
# top-left-preserving frame switch would give 21 px), so the observed value is used.
LAUNCH_CORRECTION = (4, 0)


def _addiu(rt: str, imm: int) -> int:
    return (0x09 << 26) | (REG[rt] << 16) | (imm & 0xFFFF)


def _jal(target: int) -> int:
    return (3 << 26) | ((target >> 2) & 0x03FFFFFF)


# Stock words at the root's projectile placement call:
#   0x80031208(+0x648 actor, (s16)s2, (s16)s3), s2/s3 = per-mode stock offsets.
PLACEMENT_SITE = {
    0x8004AFF0: 0x00122C00,  # sll a1, s2, 16
    0x8004AFF4: 0x00052C03,  # sra a1, a1, 16
    0x8004AFFC: 0x00133400,  # sll a2, s3, 16
    0x8004B000: _jal(F_OFFSET),
    0x8004B004: 0x00063403,  # sra a2, a2, 16 (delay slot)
}


def placement_patches(dx: int = PLACEMENT[0], dy: int = PLACEMENT[1]) -> dict[int, int]:
    """Root patches: place the projectile at donor pixel offset ``(dx, dy)``.

    Converted to host world units; the host helper applies facing.
    """

    dx, dy = (
        (dx + LAUNCH_CORRECTION[0]) * UNITS_PER_TEXEL,
        (dy + LAUNCH_CORRECTION[1]) * UNITS_PER_TEXEL,
    )
    for value in (dx, dy):
        if not -0x8000 <= value < 0x8000:
            raise ValueError("placement offsets are signed 16-bit whole units")
    return {
        0x8004AFF0: _addiu("a1", dx),
        0x8004AFF4: 0,
        0x8004AFFC: _addiu("a2", dy),
        0x8004B004: 0,
    }


# Every stock word a rocket patch may replace, by VA (lifted callback and root).
STOCK_WORDS = {ICE_CALLBACK_GROUND_SELECTOR: 0x00002021, **PLACEMENT_SITE}  # move a0, zero


def check_stock(result: LiftResult) -> None:
    """Each patch in a lift report must replace a documented stock word, unchanged."""

    for va, (old, _new) in result.patched.items():
        if va not in STOCK_WORDS:
            raise LiftError(f"undocumented rocket patch site {va:#x}")
        if old != STOCK_WORDS[va]:
            raise LiftError(
                f"stock word at {va:#x} is {old:#010x}, expected {STOCK_WORDS[va]:#010x}"
            )


# ---- Chest open / hold / close (MKZAP.ASM robo_open_chest_fast, sleep 0x20, robo_close_chest)
# Donor robot secondary animation slot 0: RBCHEST1, RBCHEST2. MKT (60 Hz): open with
# mframew 4 ticks/frame (2 if the opponent is reacting: not modelled yet), rocket created,
# hold 0x20, close with backwards_ani 4 ticks/frame, then the action ends.
CHEST_FRAMES = (0x29A0, 0x29B4)  # robot heap offsets: RBCHEST1, RBCHEST2

# Stock Zap script (fighter file 0x87, animation slot 0x24) as the lifted root plays it on
# the parent (host ticks): phase 1 (+0xDA0..+0xDB0) at 2 ticks/frame via 0x80030E98(3);
# sleep 2; token 0x0B (+0xDB8, constructor +0xDBC) creates the projectile; sleep 2 in
# 0x8004B584; the projectile process starts; recovery frames +0xDCC..+0xDE0 with sleeps
# 2, 2, 3, 4, 5, 5 (root 0x8004B108..0x8004B1A0, or 0x8004B650.. on a point-blank hit).
ZAP_SCRIPT = 0xDA0
ZAP_TOKEN = 0xDB8
ZAP_RECOVERY = (0xDCC, 0xDD0, 0xDD4, 0xDD8, 0xDDC, 0xDE0)


def chest_script_words(open1: int, open2: int) -> dict[int, int]:
    """Zap script words (file offset -> word) for the chest open, hold and close.

    Phase 1 becomes RBCHEST1, RBCHEST2 (2 + 2 ticks, donor 4 + 4 at 60 Hz), then jumps
    to the unchanged token so the projectile hooks keep their offsets. From projectile
    creation RBCHEST2 holds 2 + 2 + 2 + 3 + 4 + 5 = 18 ticks (donor 32 + 4) and the last
    recovery frame shows RBCHEST1 (closing).
    """

    words = {
        ZAP_SCRIPT: open1,
        ZAP_SCRIPT + 4: open2,
        ZAP_SCRIPT + 8: 0,  # end of phase 1
        ZAP_SCRIPT + 0xC: 1,  # jump
        ZAP_SCRIPT + 0x10: ZAP_TOKEN,
        ZAP_SCRIPT + 0x14: 0,  # unreachable
    }
    for pos in ZAP_RECOVERY[:-1]:
        words[pos] = open2
    words[ZAP_RECOVERY[-1]] = open1
    return words


# Root patch: the last recovery frame (RBCHEST1, closing) holds 2 ticks (donor 4), not 5.
CLOSE_HOLD_SITE = {0x8004B1A0: 0x24040005}  # addiu a0, zero, 5 (sleep delay slot)


def close_patches(ticks: int = 2) -> dict[int, int]:
    return {0x8004B1A0: _addiu("a0", ticks)}


STOCK_WORDS.update(CLOSE_HOLD_SITE)


# ---- Flight (rocket1_proc / rocket1_flight_call) ------------------------------------
# Donor retail N64 (rocket1_proc 0x8007C100): flat-rocket loop = robot frames ROCKETD1,
# ROCKETD2 at anirate 3; start speed 0x33333, or 0x59999 if the opponent is reacting;
# every donor tick v += v >> 4, capped at 0xB3333. The rocket flies from its creation.
ROCKET_FRAMES = (0x2668, 0x267C)  # robot heap offsets: ROCKETD1, ROCKETD2
ROCKET_ANIRATE = 3  # donor ticks per frame
SPEED_NORMAL, SPEED_REACTING, SPEED_CAP = 0x33333, 0x59999, 0xB3333


def donor_speed_step(d: int) -> int:
    return d + (d >> 4)


def host_speeds(start: int) -> list[int]:
    """Host per-tick speeds (world units, actor +0x14 magnitude); last entry = cap."""

    return physics.fold_donor_speeds(start, SPEED_CAP, donor_speed_step, UNITS_PER_TEXEL)


def speed_table() -> list[int]:
    """Normal then reacting sequence, each ended by 0: a speed's successor is the next word."""

    normal, reacting = host_speeds(SPEED_NORMAL), host_speeds(SPEED_REACTING)
    if set(normal) & set(reacting) != {normal[-1]} or normal[-1] != reacting[-1]:
        raise AssertionError("speed sequences must share only the cap")
    return normal + [0] + reacting + [0]


def flight_frame_cycle(shapes: tuple[int, int]) -> list[int]:
    return physics.resample_frame_cycle(shapes, ROCKET_ANIRATE)


# Stock Ice host: the straight branch creates the flight child 0x8004B82C here, after
# 0x8004B584 has slept 2 ticks past the projectile's creation.
CHILD_SITE = {0x8004B0D8: 0x3C048005, 0x8004B0DC: 0x2484B82C}  # a0 = 0x8004B82C
CHILD_START_TICKS = 2  # host ticks from creation to the child's first flight tick
STOCK_WORDS.update(CHILD_SITE)
FLIGHT_TAIL = 0x8004B9C4  # stock child tail: 0x8004CC50(actor, selector) and cleanup
FLIGHT_STRIKE_SELECTOR = 0x13  # stock straight-Ice selector (strike step pending)
F_PROJECTILE_SETUP = 0x8004CC14  # (actor, magnitude, rate): facing-signed +0x14, anim rate
FILE87_BASE_PTR = 0x80291C10  # resident fighter file 0x87 base


def child_patches(child_va: int) -> dict[int, int]:
    return {
        0x8004B0D8: (0x0F << 26) | (REG["a0"] << 16) | hi(child_va),
        0x8004B0DC: (0x09 << 26) | (REG["a0"] << 21) | (REG["a0"] << 16) | (lo(child_va) & 0xFFFF),
    }


def _emit_next_speed(a: Assembler, table: str, label: str = "zap_next") -> None:
    """Leaf subroutine: ``t2`` = successor of ``t2`` in the speed table (unchanged if
    none or zero). Uses t3-t5."""

    a.label(label)
    a.beqz("t2", label + "_done")  # never match a separator
    a.la("t3", table)
    a.label(label + "_scan")
    a.lw("t4", 0, "t3")
    a.bne("t4", "t2", label + "_next")
    a.lw("t4", 4, "t3")
    a.beqz("t4", label + "_done")
    a.move("t2", "t4")
    a.beq("zero", "zero", label + "_done")
    a.label(label + "_next")
    a.li("t5", -1)  # end marker
    a.beq("t4", "t5", label + "_done")
    a.addiu("t3", "t3", 4)
    a.beq("zero", "zero", label + "_scan")
    a.label(label + "_done")
    a.jr_ra()
    a.nop()


def emit_speed_table(a: Assembler, label: str) -> None:
    a.label(label)
    for word in speed_table():
        a.raw(word)
    a.raw(0xFFFFFFFF)


def emit_initial_speed(a: Assembler, actor: str = "s0") -> None:
    """At creation (parent context): actor +0x14 = facing-signed donor start speed."""

    a.lui("t7", hi(host.CURRENT_CTRL))
    a.lw("t7", lo(host.CURRENT_CTRL), "t7")
    host.opponent_reacting(a, "t7", "t8", "zap_v0_react")
    a.li("t0", host_speeds(SPEED_NORMAL)[0])
    a.beqz("t8", "zap_v0_sel")
    a.li("t0", host_speeds(SPEED_REACTING)[0])
    a.label("zap_v0_sel")
    a.lhu("t1", 0x8C, actor)
    a.andi("t1", "t1", 0x10)  # facing flag, as 0x8004CC14
    a.beqz("t1", "zap_v0_set")
    a.subu("t0", "zero", "t0")
    a.label("zap_v0_set")
    a.sw("t0", host.ACTOR_XVEL, actor)


def emit_flight(a: Assembler, loop_offset: int, table: str = "zap_speeds") -> None:
    """Flight child (process entry, replaces 0x8004B82C) and its per-tick callback.

    The child points the animation at the resampled ROCKETD1/ROCKETD2 loop (phase
    CHILD_START_TICKS), advances the speed CHILD_START_TICKS steps past the creation
    speed, installs the callback and enters the stock flight loop (cached, via jr).
    The callback advances the speed one host tick (two donor ticks) per iteration.
    """

    a.label("zap_child")
    a.addiu("sp", "sp", -0x18)
    a.sw("ra", 0x10, "sp")
    a.lui("t0", hi(host.CURRENT_CTRL))
    a.lw("t0", lo(host.CURRENT_CTRL), "t0")
    a.li("t1", 0x100)
    a.sw("t1", 0x69C, "t0")  # as the stock child
    a.lui("t1", hi(FILE87_BASE_PTR))
    a.lw("t1", lo(FILE87_BASE_PTR), "t1")
    a.li("t2", loop_offset)
    a.addu("t1", "t1", "t2")
    a.sw("t1", host.CTRL_SCRIPT_CURSOR, "t0")
    a.lw("t1", host.CTRL_ACTOR, "t0")
    a.lw("t2", host.ACTOR_XVEL, "t1")
    a.sra("t6", "t2", 31)
    a.xor("t2", "t2", "t6")
    a.subu("t2", "t2", "t6")
    for _ in range(CHILD_START_TICKS):
        a.jal_label("zap_next")
    a.move("a0", "t1")
    a.move("a1", "t2")
    a.li("a2", 1)  # one frame per host tick: the loop is pre-resampled
    a.jal(F_PROJECTILE_SETUP)
    a.lui("t0", hi(host.CURRENT_CTRL))
    a.lw("t0", lo(host.CURRENT_CTRL), "t0")
    a.la("t1", "zap_callback")
    a.sw("t1", 0x70C, "t0")
    a.lw("a0", host.CTRL_ACTOR, "t0")
    a.li("a1", FLIGHT_STRIKE_SELECTOR)
    a.lui("t9", hi(FLIGHT_TAIL))
    a.addiu("t9", "t9", lo(FLIGHT_TAIL))
    a.jr("t9")
    a.nop()

    a.label("zap_callback")
    a.lui("t0", hi(host.CURRENT_CTRL))
    a.lw("t0", lo(host.CURRENT_CTRL), "t0")
    a.lw("t1", host.CTRL_ACTOR, "t0")
    a.lw("t2", host.ACTOR_XVEL, "t1")
    a.sra("t6", "t2", 31)
    a.xor("t2", "t2", "t6")
    a.subu("t2", "t2", "t6")
    a.move("t7", "ra")
    a.jal_label("zap_next")
    a.xor("t2", "t2", "t6")
    a.subu("t2", "t2", "t6")
    a.sw("t2", host.ACTOR_XVEL, "t1")
    a.jr("t7")
    a.nop()

    _emit_next_speed(a, table)
