"""Sektor's power tiers and Ice costs on Sub-Zero's progression (R4, user decisions 2026-11-09).

Sub-Zero's nine Power Up slots keep their native thresholds, order and shuffle; each Sektor
move takes the tier of one slot by reading the gate instruction that slot's stock power uses
(``slti v0,v0,N`` after the tier evaluator ``0x80074FBC``; the power-order shuffle rewrites
only ``N``). Mapping:

====  ===================  ======================================  ==========
Slot  Sub-Zero power       Sektor                                   Ice cost
====  ===================  ======================================  ==========
1     Ice Blast            Straight Missile (``F,F + LP``)          ``0x20``
2     Slide                Slide (kept)                             stock
3     Directional Ice      Teleport Uppercut (``F,F + LK``)         free
4     Air Ice Blast        Homing Missile (``F,D,B + HP``)          ``0x40``
5     Ice Clone            empty                                    -
6     Ice Shatter          Double Missile (``B,B,F + LP``)          ``0x30``
7     Super Slide          empty                                    -
8     Freeze on Contact    Super Slide (kept)                       stock
9     Polar Blast          Polar Blast (kept)                       stock
====  ===================  ======================================  ==========

Removed for Sektor: Directional Ice up (its HK table is emptied), Air Ice Blast (the LP
missile conditions refuse an airborne start; the stock LP callback would run the air root),
Ice Shatter (the two contextual paths skip it, their gates stay readable), Ice Clone and
Freeze on Contact (their records carry the Double and Homing Missiles). The teleport keeps
the stock down-Ice LK condition (Directional Ice slot) and costs nothing; the three missiles
share the lifted Ice root, which takes ``0x20`` at launch, so the Double and Homing stubs take
the rest (:data:`EXTRA_COST`).
"""

from __future__ import annotations

from ..host import hi, lo
from ..mips import Assembler

# ---- stock facts (clean MKMSZ, Static-confirmed) ---------------------------------------
LP_ICE_CONDITION = 0x8004A304  # ground: Ice Blast tier, airborne: tier >= 4 (Air Ice Blast)
PLAYER_ACTOR = 0x802E73DC
PLAYER_CTRL = 0x802C1AC0
CURRENT_CTRL = 0x802ECE20
SPECIAL_FLAG = 0x802E7DE8  # stock conditions refuse while it is set
F_FIND_CLASS = 0x80028510
F_TIER = 0x80074FBC  # tier count 0..9 from current XP
CURRENT_XP = 0x8011200C
FALL_SPEED_LIMIT = 0xB4782  # stock LP condition: refuse while actor +0x18 exceeds it
BUSY_ACTION = 0x1A
PROJECTILE_CLASS = 0x700  # one live projectile at a time (stock)
CTRL_ICE = 0x656  # Ice meter (halfword)
ROOT_COST = 0x20  # taken by the (lifted) Ice root at launch, mode 0 (0x8004AC70)

# Gate instructions (VA of ``slti v0,v0,N``), one per slot Sektor reads at run time.
AIR_ICE_GATE = 0x8004A3BC  # ROM 0x4AFBC, slot 4
SHATTER_GATE = 0x800509A0  # ROM 0x515A0, slot 6 (first of its two sites)

COSTS = {"straight": 0x20, "double": 0x30, "homing": 0x40}  # homing lowered by the user (2026-11-10)
COSTS_V54 = {"straight": 0x20, "double": 0x30, "homing": 0x60}  # Sektor builders v54-v57


def extra_costs(costs: dict[str, int] = COSTS) -> dict[str, int]:
    """Ice the double/homing stubs take on top of the root's own ``0x20``."""

    return {name: cost - ROOT_COST for name, cost in costs.items() if cost > ROOT_COST}


EXTRA_COST = extra_costs()

# ---- stock edits (ROM offset -> (clean word, Sektor word)) -----------------------------
HK_RECORD_ROM = 0xB1B98  # 0x800B0F98: the only HK record, Directional Ice up
SHATTER_BRANCHES = (0x515A4, 0x535C8)  # ``bnez v0,+6`` after each Shatter gate -> ``b +6``
BNEZ_V0_6, BRANCH_6 = 0x14400006, 0x10000006
SUPER_SLIDE_GATE_ROM = 0x3D728  # 0x8003CB28 ``slti v0,v0,7``
FREEZE_GATE_ROM = 0x5B5DC  # 0x8005A9DC ``slti v0,v0,8``
SLTI_V0 = 0x28420000


def _gate(word: int) -> int:
    if word & 0xFFFF0000 != SLTI_V0:
        raise ValueError(f"not a tier gate: {word:#010x}")
    return word & 0xFFFF


def stock_edits(rom: bytes) -> dict[int, tuple[int, int]]:
    """The guarded stock words Sektor changes, computed from ``rom`` (clean or after the
    power-order shuffle): HK table emptied, Ice Shatter skipped, Super Slide on the Freeze on
    Contact slot's tier."""

    word = lambda off: int.from_bytes(rom[off : off + 4], "big")
    edits = {HK_RECORD_ROM: (word(HK_RECORD_ROM), word(HK_RECORD_ROM) & 0xFFFF)}
    if word(HK_RECORD_ROM) >> 16 != 0x0020:
        raise ValueError("unexpected HK record")
    for off in SHATTER_BRANCHES:
        if word(off) != BNEZ_V0_6:
            raise ValueError(f"unexpected Ice Shatter site {off:#x}")
        _gate(word(off - 4))
        edits[off] = (BNEZ_V0_6, BRANCH_6)
    slide = word(SUPER_SLIDE_GATE_ROM)
    _gate(slide)
    edits[SUPER_SLIDE_GATE_ROM] = (slide, SLTI_V0 | _gate(word(FREEZE_GATE_ROM)))
    return edits


# ---- payload conditions --------------------------------------------------------------
def emit_ground_condition(a: Assembler, label: str = "tier_straight") -> None:
    """Straight Missile: refuse an airborne start (that branch of the stock LP condition is
    Air Ice Blast), else the stock LP condition with ``ra`` unchanged (Ice Blast slot,
    ``0x20``)."""

    a.label(label)
    a.lui("t0", hi(PLAYER_CTRL))
    a.lw("t0", lo(PLAYER_CTRL), "t0")
    a.lw("t1", 0x6E0, "t0")
    a.lw("t1", 0x30, "t1")
    a.lw("t2", 0x6B4, "t0")
    a.slt("t1", "t1", "t2")  # y above the floor (y grows downward): airborne
    a.beqz("t1", label + "_stock")
    a.jr_ra()
    a.li("v0", 0x4000)
    a.label(label + "_stock")
    a.lui("t9", hi(LP_ICE_CONDITION))
    a.addiu("t9", "t9", lo(LP_ICE_CONDITION))
    a.jr("t9")
    a.nop()


def emit_gate_condition(a: Assembler, label: str, gate_va: int, cost: int) -> None:
    """``label() -> 0x8000 / 0x4000``: the stock LP condition's ground path with the Ice cost
    ``cost`` and the tier of the slot whose gate instruction is at ``gate_va`` (read at run
    time); airborne refused."""

    a.label(label)
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x1C, "sp")
    a.lui("t0", hi(PLAYER_ACTOR))
    a.lw("t0", lo(PLAYER_ACTOR), "t0")
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
    a.lhu("t4", CTRL_ICE, "t3")
    a.slti("t4", "t4", cost)  # meter is a small positive halfword
    a.bnez("t4", label + "_no")
    a.lw("t4", 0x30, "t5")
    a.lw("t6", 0x6B4, "t3")
    a.slt("t4", "t4", "t6")
    a.bnez("t4", label + "_no")  # airborne
    a.lui("t6", hi(CURRENT_CTRL))
    a.lw("t6", lo(CURRENT_CTRL), "t6")
    a.lhu("t7", 0x6AA, "t6")
    a.li("t8", BUSY_ACTION)
    a.beq("t7", "t8", label + "_no")
    a.li("a0", PROJECTILE_CLASS)
    a.li("a1", 0xFFFF)
    a.jal(F_FIND_CLASS)
    a.bnez("v0", label + "_no")
    a.lui("t0", hi(SPECIAL_FLAG))
    a.lh("t0", lo(SPECIAL_FLAG), "t0")
    a.bnez("t0", label + "_no")
    a.lui("a0", hi(CURRENT_XP))
    a.lw("a0", lo(CURRENT_XP), "a0")
    a.jal(F_TIER)
    a.lui("t0", hi(gate_va + 2))
    a.lh("t0", lo(gate_va + 2), "t0")  # the slot's threshold N
    a.slt("t1", "v0", "t0")
    a.bnez("t1", label + "_no")
    a.li("v0", 0x8000)
    a.beq("zero", "zero", label + "_ret")
    a.label(label + "_no")
    a.li("v0", 0x4000)
    a.label(label + "_ret")
    a.lw("ra", 0x1C, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)


def emit_charge(a: Assembler, amount: int) -> None:
    """Take ``amount`` from the current controller's Ice meter (t0, t1)."""

    a.lui("t0", hi(CURRENT_CTRL))
    a.lw("t0", lo(CURRENT_CTRL), "t0")
    a.lhu("t1", CTRL_ICE, "t0")
    a.addiu("t1", "t1", -amount)
    a.sh("t1", CTRL_ICE, "t0")


def emit_conditions(a: Assembler, costs: dict[str, int] = COSTS) -> dict[str, str]:
    """The three missile conditions; returns record name -> label."""

    emit_ground_condition(a, "tier_straight")
    emit_gate_condition(a, "tier_double", SHATTER_GATE, costs["double"])
    emit_gate_condition(a, "tier_homing", AIR_ICE_GATE, costs["homing"])
    return {"straight": "tier_straight", "double": "tier_double", "homing": "tier_homing"}
