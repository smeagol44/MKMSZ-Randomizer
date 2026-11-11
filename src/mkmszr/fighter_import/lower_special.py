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
animation the description copied into a host secondary slot, ``body.secondary_scripts``),
``projectile`` (a child built by ``lower_projectile``), ``sleep``, ``finish`` and ``end``.
"""

from __future__ import annotations

from typing import Any

from . import host
from . import lower_projectile as lp
from .host import hi, lo
from .mips import Assembler

PLAYER_ACTOR = 0x802E73DC
PLAYER_CTRL = 0x802C1AC0
SPECIAL_FLAG = 0x802E7DE8  # stock conditions refuse while it is set
F_FIND_CLASS = 0x80028510
F_TIER = 0x80074FBC  # tier count 0..9 from current XP
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
}
COSTS = {
    "ice_blast": 0x20,
    "directional_ice_up": 0x20,
    "directional_ice_down": 0x60,
    "ice_clone": 0x60,
    "freeze_on_contact": 0x80,
    "polar_blast": 0xA6,
}


def emit_gate_condition(a: Assembler, label: str, gate_va: int, cost: int) -> None:
    """``label() -> 0x8000 / 0x4000`` (see the module notes)."""

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
    a.lui("t6", hi(host.CURRENT_CTRL))
    a.lw("t6", lo(host.CURRENT_CTRL), "t6")
    a.lhu("t7", 0x6AA, "t6")
    a.li("t8", BUSY_ACTION)
    a.beq("t7", "t8", label + "_no")
    a.li("a0", lp.PROJECTILE_CLASS)
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

    a.lui("t0", hi(host.CURRENT_CTRL))
    a.lw("t0", lo(host.CURRENT_CTRL), "t0")
    a.lhu("t1", CTRL_ICE, "t0")
    a.addiu("t1", "t1", -amount)
    a.sh("t1", CTRL_ICE, "t0")


def emit_action(a: Assembler, label: str, steps: list[dict[str, Any]], *, cost: int,
                animations: dict[tuple[int, int], int], child: str,
                helper: str | None = None) -> None:  # fmt: skip
    """The action root for a move program (never returns). ``animations``: donor animation
    (table, slot) -> host secondary slot holding it; ``child``: the projectile process label;
    ``helper``: the throw helper's process label (``lower_projectile.emit_helper``), started
    with the throw animation."""

    a.label(label)
    host.enter_action(a, host.Frame(size=0x40, strike_offset=0x30), ())
    host.load_controller(a)
    for k, step in enumerate(steps):
        op = step["op"]
        if op == "stamp":
            continue  # MKT cooldown key: not lowered yet (host one-projectile rule instead)
        elif op == "begin":
            host.set_special_lock(a)
            host.set_action_id(a, ICE_ACTION_ID)
            host.special_begin(a)  # stop, face, busy input map
            host.load_controller(a)
            emit_charge(a, cost)
        elif op == "animate":
            anim = step["anim"]
            key = (int(anim["table"]), int(anim["slot"]))
            if key not in animations or step.get("until") != "phase_end":
                raise ValueError(f"{label}: animation {key} has no host slot / unsupported end")
            if helper is not None:
                lp.emit_spawn(a, helper, after=f"{label}_helper{k}")
            a.li("a0", 1)
            a.li("a1", animations[key])
            a.jal(lp.F_SELECT)
            a.li("a0", int(step["rate"]))
            a.jal(F_TO_PHASE_END)
            host.load_controller(a)
        elif op == "projectile":
            if helper is not None:  # the helper goes first: one type-4 object at a time
                lp.emit_helper_handover(a, helper, f"{label}_handover{k}")
                host.load_controller(a)
            lp.emit_spawn(a, child, after=f"{label}_spawned{k}")
        elif op == "sleep":
            host.sleep_ticks(a, int(step["ticks"]), f"{label}_sleep{k}")
            host.load_controller(a)
        elif op == "finish":
            a.li("a0", int(step["rate"]))
            a.jal(F_TO_PHASE_END)
            host.load_controller(a)
        elif op == "end":
            host.exit_action(a, hang=f"{label}_hang")
        else:
            raise ValueError(f"{label}: step {op!r} is not lowered yet")
