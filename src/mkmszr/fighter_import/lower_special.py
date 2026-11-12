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
    "ice_shatter": 0x800509A0,  # first of its two contextual sites (power_order sets both alike)
}
# Ground Ice Blast's tier is a bgtz tail (tier >= 1) at ROM 0x4B018; the product's power-order
# shuffle rewrites it to ``slti t0, v0, N`` (patches/power_order.build_ice_ground_tail).
ICE_BLAST_GATE, ICE_BLAST_STOCK_TIER = 0x8004A418, 1
SLTI_T0_V0 = 0x2848
COSTS = {
    "ice_blast": 0x20,
    "directional_ice_up": 0x20,
    "directional_ice_down": 0x60,
    "ice_clone": 0x60,
    "freeze_on_contact": 0x80,
    "polar_blast": 0xA6,
    "ice_shatter": 0,  # contextual, no Ice cost
}
BLOCKED_FLAG = 0x802ECD88  # halfword: the collision core sets it on a blocked contact
F_SET_XVEL = 0x8002B1EC  # (actor, x speed): actor +0x14 and +0x58
FACING_BIT = 0x10
# Host victim reactions by strike meaning: a stock entry, or None for one the builder supplies
# in a spare reaction-table entry (``reactions`` argument of emit_action).
# ``launch``: the stock roundhouse's reaction (player strike index 0x0D, record 0x800AF5E4; owner,
# specials proof v15: "the roundhouse kick one, not the uppercut"). ``uppercut``: 0x800507D0,
# Runtime-confirmed (Sektor teleport).
STOCK_REACTIONS = {"launch": 0x0C, "uppercut": 0x08}
SOLID_BIT = 0x1000  # actor +0x8C: Freeze on Contact clears it while it runs (0x80034740 / 0x80034658)


def emit_gate_condition(a: Assembler, label: str, gate_va: int, cost: int,
                        default: int | None = None, alive: tuple[str, ...] = ()) -> None:  # fmt: skip
    """``label() -> 0x8000 / 0x4000`` (see the module notes). With ``default``, the gate word
    is used only when it is ``slti t0, v0, N`` (Ice Blast's rewritten tail), else ``default``.
    With ``alive`` (labels of words that projectiles set while they live,
    ``lower_projectile.emit_process``), only those projectiles block it instead of any live one
    (Reptile: one fast and one slow forceball may coexist, owner 2026-11-11). Set words with no
    live projectile process are stale (a process ended by something else) and are cleared."""

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


def _scale(n: int, donor_ticks: int) -> int:
    return max(1, -(-n // donor_ticks))


def emit_action(a: Assembler, label: str, steps: list[dict[str, Any]], *, cost: int,
                animations: dict[tuple[int, int], int | tuple[str, int]], child: str | None = None,
                helper: str | None = None, sounds: dict[int, int] | None = None,
                face: bool | None = None, donor_ticks: int = 1,
                reactions: dict[str, int] | None = None,
                speed: Callable[[int], int] | None = None) -> list[tuple[str, bytes]]:  # fmt: skip
    """The action root for a move program (never returns). ``animations``: donor animation
    (table, slot) -> host secondary slot holding it, or ``("at", offset)`` for a body script
    without a table entry (selected by setting the cursor); ``child``: the projectile process
    label; ``helper``: the throw helper's process label (``lower_projectile.emit_helper``),
    started with the throw animation; ``sounds``: donor fighter sound -> host event, for
    ``sound`` steps (needs ``host.emit_sound_player``); ``face``: overrides the program's
    ``begin.face`` (MKT turns to its one opponent; the host may not want that);
    ``donor_ticks``: donor ticks per host tick (module notes); ``reactions``: strike meaning ->
    host reaction index (else :data:`STOCK_REACTIONS`); ``speed``: donor x speed -> host speed.

    Returns the strike records ``(label, 16 bytes)`` to place with :func:`emit_strike_data`.

    ``pass_through`` (MKT ``sans_repell_3``, no fighter repulsion; the host's fighter
    separation is not located). Specials proof v15 stopped at the victim. From v16 each
    pass-through tick clears actor ``+0x8C`` bit ``0x1000`` as stock Freeze on Contact does while
    Sub-Zero runs through enemies, and re-applies the move's last speed (kept in ``s5``); ``end``
    sets the bit again (Hypothesis until runtime-tested)."""

    records: list[tuple[str, bytes]] = []
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

    def anim_at(anim: dict[str, Any]) -> int | tuple[str, int]:
        key = (int(anim["table"]), int(anim["slot"]))
        if key not in animations:
            raise ValueError(f"{label}: animation {key} has no host slot")
        return animations[key]

    def select(where: int | tuple[str, int], offset: int = 0) -> None:
        if isinstance(where, tuple):
            host.load_controller(a)
            host.set_cursor(a, where[1] + 4 * offset)
        else:
            if offset:
                raise ValueError(f"{label}: a pose offset needs a script offset")
            a.li("a0", 1)
            a.li("a1", where)
            a.jal(lp.F_SELECT)

    def advance(times: int = 1) -> None:
        for _ in range(times):
            host.load_controller(a)
            host.advance_animation(a)
        host.load_controller(a)

    def sleep(ticks: int) -> None:
        host.sleep_ticks(a, _scale(ticks, donor_ticks), fresh("sleep"))
        host.load_controller(a)

    def emit(steps: list[dict[str, Any]], after: str | None) -> None:
        for step in steps:
            op = step["op"]
            if op == "stamp":
                continue  # MKT cooldown key: not lowered yet (host one-projectile rule instead)
            elif op == "begin":
                host.set_special_lock(a)
                host.set_action_id(a, ICE_ACTION_ID)
                turn = step.get("face", True) if face is None else face
                host.special_begin(a, face=turn)  # stop, (face), busy input map
                host.load_controller(a)
                emit_charge(a, cost)
            elif op == "animate":
                where = anim_at(step["anim"])
                until = step.get("until")
                if until not in ("phase_end", "manual"):
                    raise ValueError(f"{label}: animation end {until!r} is not lowered yet")
                if helper is not None and until == "phase_end":
                    lp.emit_spawn(a, helper, after=fresh("helper"))
                select(where)
                if until == "phase_end":
                    a.li("a0", _scale(int(step["rate"]), donor_ticks))
                    a.jal(F_TO_PHASE_END)
                    host.load_controller(a)
                else:
                    advance()  # show the first frame; next_frame steps advance it
            elif op == "pose":
                select(anim_at(step["anim"]), int(step["anim"].get("offset", 0)))
                advance()
            elif op == "next_frame":
                advance(donor_ticks)
            elif op == "pass_through":  # see the docstring
                host.load_controller(a)
                a.lhu("t0", lp.ACTOR_FLAGS, "s1")
                a.andi("t0", "t0", 0xFFFF ^ SOLID_BIT)
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
                skip = fresh("ahead")
                a.beqz("t0", skip)
                a.subu("a1", "zero", "a1")  # facing left: negative x
                a.label(skip)
                a.move("s5", "a1")  # pass_through re-applies it
                a.move("a0", "s1")
                a.jal(F_SET_XVEL)
                host.load_controller(a)
            elif op == "stop":
                host.load_controller(a)
                host.stop(a)
                host.load_controller(a)
            elif op == "face":
                host.load_controller(a)
                host.face_opponent(a)
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
                loop, count = fresh("repeat"), _scale(int(step["count"]), donor_ticks)
                a.li("s4", count)
                a.label(loop)
                emit(step["steps"], None)
                a.addiu("s4", "s4", -1)
                a.bnez("s4", loop)
            elif op == "strike":
                _emit_strike(step)
            elif op == "sound":
                fighter = int(step["sound"]["fighter"])
                if not sounds or fighter not in sounds:
                    raise ValueError(f"{label}: fighter sound {fighter} has no host event")
                host.play_sound(a, sounds[fighter])
                host.load_controller(a)
            elif op == "projectile":
                if child is None:
                    raise ValueError(f"{label}: projectile step without a child process")
                if helper is not None:  # the helper goes first: one type-4 object at a time
                    lp.emit_helper_handover(a, helper, fresh("handover"))
                    host.load_controller(a)
                lp.emit_spawn(a, child, after=fresh("spawned"))
            elif op == "sleep":
                sleep(int(step["ticks"]))
            elif op == "finish":
                a.li("a0", _scale(int(step["rate"]), donor_ticks))
                a.jal(F_TO_PHASE_END)
                host.load_controller(a)
            elif op == "end":
                if passes:
                    host.load_controller(a)
                    a.lhu("t0", lp.ACTOR_FLAGS, "s1")
                    a.ori("t0", "t0", SOLID_BIT)
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
    return records


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
# 0x1C); the owner saw a hit, not a hold.
HOLD_DONOR_TICKS = 20
F_REACT_A, F_REACT_B = 0x800504C4, 0x800556A4  # stock reaction 0x10 preamble calls
F_REACT_PREAMBLE, AIRBORNE_HANDLER = 0x80053028, 0x800532F8
HIT_SLOT = 0x1C  # victim primary slot of the stock hit flinch


def emit_hold_reaction(a: Assembler, label: str, donor_ticks: int = 1, pose: bool = False) -> None:
    """Victim reaction ``elbow_hold`` (installed by the collision core as the victim's callback)."""

    a.label(label)
    a.addiu("sp", "sp", -0x30)
    a.sw("ra", 0x28, "sp")
    for k, reg in enumerate(("s0", "s1", "s2")):
        a.sw(reg, 0x18 + 4 * k, "sp")
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
