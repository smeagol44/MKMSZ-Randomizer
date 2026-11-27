"""Move-program generator (owner decision 2026-11-25, Wiki Fighter-Recompiler-Amendment-1).

Writes a fighter's move programs from MKT's own special-move code: :mod:`.decompile` turns a
routine into a structured IR, and the rules below map MKT engine calls and code shapes to
components (:mod:`.components`). The output is a program in the move-program format, plus
``notes`` (what MKT does that the program leaves out or approximates) and ``unknown`` (calls and
shapes no rule covers yet, which a person turns into a rule once, for every fighter).

Nothing here knows a fighter or a move: rules name MKT engine routines (``mkt_registry``) and
shapes (a counted loop around a strike is a hit window, a branch on the strike result is
``on_hit``, a branch on the strike flag is ``on_block``). Owner adjustments (calibrations,
stand-ins chosen by the owner) stay in the fighter description; :func:`compare` checks a generated
program against an accepted hand-written one so differences are seen and decided, not hidden.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from . import decompile as dc
from . import reading
from .mkt_fighter import INLINE_DISPATCH as TRANSFER
from .mkt_fighter import INLINE_MATCHER as MATCHER
from .mkt_fighter import MktRom
from .mkt_registry import REGISTRY

VA_BASE = 0x80000000
STRIKE_TABLE = 0x800AFDB0  # MKT per-fighter strike tables (fighter -> record pointers)
REACTION_TABLE = 0x800A8AE0  # MKT victim reactions by strike record byte 8 (mkt_registry)
SUCCESS = 0x8000  # MKT routines answer 0x8000 (yes / contact) or 0x4000 (no)
PLAYER_OBJECTS = (0x8016994C,)  # MKT player 1's fighter object (per-player branches compare it)
MAX_DEPTH = 4

# MKT victim reaction id (strike record byte 8) -> reaction meaning (``components.REACTIONS``).
# One row per MKT reaction, shared by every fighter: the host stand-in where the host has no
# equivalent (owner-accepted stand-ins are marked).
REACTION_MEANINGS = {
    0x24: "launch",  # generic damaging launch (Reptile's elbow return hit)
    0x3B: "rocket_stumble",  # Sektor's rockets: r_rocket -> zap_stumble (push 0x33333)
    0x3D: "uppercut",  # Sektor's teleport uppercut: the host's stock uppercut (runtime-confirmed v08)
    0x71: "knockback_arc",  # Reptile's forceballs
    0x72: "acid_stagger",  # Reptile's acid
    0x74: "elbow_hold",  # Reptile's elbow first contact
    0x7F: "launch",  # Rayden's torpedo victim (the carry is the attacker's): stand-in
    0x80: "shock_stagger",  # Rayden's lightning: stagger back, cyan blink (0x800539A8)
    0x81: "shock_stagger_toward",  # his reversed lightning: the same, pushed towards him
}


# SMRE command reading (2026-11-27). MKT's input grid events -> host button bits (commands.BUTTONS):
# 0 High Punch, 1 Low Punch, 3 High Kick, 4 Low Kick; 6-9 the stick (Up, Down, Left, Right).
EVENT_BUTTONS = {0: 0x10, 1: 0x80, 3: 0x20, 4: 0x40}
STICK_EVENTS = {6, 7, 8, 9}
TICKS_SINCE = 0x8006D7E0  # (stamp pair, object) -> ticks since the stamp (mkt_registry)
BUTTONS_HELD = 0x8004EA64  # (object, mask, mask) -> 0x8000 when exactly those buttons are held
PRESS_STAMPS = {0x80257738: "HP"}  # button press stamps (Rayden's Shocker: HP held before release)
OWN_CONDITIONS = ("forceball_",)  # registry-named fighter condition helpers, read through
OTHER_GUARD_FIELDS = {0x38: "the opponent's fighter id", 0x408: "the opponent's reaction state",
                      0x3F6: "the opponent's action"}  # fmt: skip
MOVEMENT_OPS = {"relocate", "velocity"}
# Inline commands (Sektor's handlers: the matcher, then guards, then the transfer): the guard
# ``process_exist(id)`` on the player's projectile process (0x705 player 1, 0x805 player 2)
# refuses while one of his projectiles lives.
PROCESS_EXIST = 0x8005A614  # (id, mask) -> another process whose id & mask matches, or 0
PROJECTILE_PROCESSES = {0x705, 0x805}
PROCESS_SUICIDE = 0x8005A69C  # an inline handler's refusal
# Motion loops (Sektor's teleport uppercut, MKT 0x80048368): object +0x10 y velocity and +0x8
# gravity set, then one tick at a time until the object's y (+0x18, growing downward) passes the
# screen's bottom line (SCREEN_BOTTOM: "below_screen") or rises to its floor (process +0x3F8:
# "surface").
SCREEN_BOTTOM = 0x802576CE
JUMP_KEEP = 0xD  # do_jump: "keep the current value" (0x8006EC50)
PROCESS_ID = 0x40C  # process +0x40C: its id
# Grabs (SMRE step 2): the routine a grab gives the opponent at its release -> the victim reaction
# meaning that plays the whole hold (components.REACTIONS). Rayden's Shocker: 0x800734CC drops the
# victim (0x80058728) after its hold at his hands and the shocks (lower_special.shock_hold).
GRAB_RELEASES = {0x800734CC: "shock_hold"}
GRAB_BOX_HEIGHT = 120  # px: the victim's body height (MKT's grab tests only the horizontal reach)


def _tree_text(s: Any) -> str:
    """The conditions and calls of an ``if`` tree, as text (the grab shape's reach and guard)."""

    parts = []
    if s.kind == "if":
        parts.append(str(s.cond))
        for x in list(s.then) + list(s.other or []):
            parts.append(_tree_text(x))
    elif s.kind == "call":
        parts.append(REGISTRY[s.target].name if s.target in REGISTRY else f"0x{s.target or 0:08X}")
    return " ".join(parts)


def _same_command(a: Any, b: Any) -> bool:
    return (a.masks, a.condition, a.action, a.right) == (b.masks, b.condition, b.action, b.right)


def _walk_stmts(stmts: list):
    """Every decompiled statement, nested ones too."""

    for s in stmts:
        yield s
        for key in ("then", "other", "body"):
            yield from _walk_stmts(getattr(s, key, []) or [])


def _all(steps: list[dict[str, Any]]):
    for s in steps:
        yield s
        for key in ("steps", "every_tick", "on_hit", "on_block"):
            if key in s:
                yield from _all(s[key])


@dataclass
class Generated:
    entry: int
    steps: list[dict[str, Any]]
    notes: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)
    grab: bool = False  # the move is a grab (the grab rule read it)


class Generator:
    def __init__(self, mkt: bytes, fighter: int) -> None:
        self.mkt, self.fighter = mkt, fighter
        self.names = {va: r.name for va, r in REGISTRY.items()}

    # -- data ------------------------------------------------------------------------------------
    def word(self, va: int) -> int:
        o = (va & 0xFFFFFFFF) - VA_BASE
        return int.from_bytes(self.mkt[o : o + 4], "big")

    def strike(self, rec: dc.Value) -> tuple[dict[str, Any], int] | None:
        """``strike_check_a0``'s argument: the fighter's strike table entry ``+off`` (a load of
        a load from ``STRIKE_TABLE + fighter * 4``). Returns the strike and the record address."""

        if not (isinstance(rec, dc.Load) and isinstance(rec.base, dc.Load)):
            return None
        table = rec.base.base  # (STRIKE_TABLE + fighter * 4), the low half sometimes in the load
        if not (isinstance(table, dc.Bin) and table.op == "+" and table.a.const() is not None
                and (table.a.const() + rec.base.off) & 0xFFFFFFFF == STRIKE_TABLE):  # fmt: skip
            return None
        addr = self.word(self.word(STRIKE_TABLE + 4 * self.fighter) + rec.off)
        o = addr - VA_BASE
        raw = self.mkt[o : o + 16]
        box = [int.from_bytes(raw[i : i + 2], "big", signed=True) for i in range(0, 8, 2)]
        meaning = REACTION_MEANINGS.get(raw[8])
        out = {"box": box, "damage": raw[10], "block_damage": raw[11],
               "reaction": meaning or f"mkt_0x{raw[8]:02X}", "blocked_reaction": "blocked"}  # fmt: skip
        return out, addr

    def strike_index(self, index: int) -> dict[str, Any] | None:
        """The fighter's strike record ``index`` (``proj_flight`` / ``proj_strike_check``)."""

        raw = self.strike_raw(index)
        if raw is None:
            return None
        box = [int.from_bytes(raw[i : i + 2], "big", signed=True) for i in range(0, 8, 2)]
        meaning = REACTION_MEANINGS.get(raw[8])
        return {"box": box, "damage": raw[10], "block_damage": raw[11],
                "reaction": meaning or f"mkt_0x{raw[8]:02X}", "blocked_reaction": "blocked"}  # fmt: skip

    def strike_raw(self, index: int) -> bytes | None:
        addr = self.word(self.word(STRIKE_TABLE + 4 * self.fighter) + 4 * index)
        return self.mkt[addr - VA_BASE : addr - VA_BASE + 16] if addr else None

    def reaction_sound(self, reaction: int) -> int | None:
        """The attacker's sound MKT's victim reaction plays (``his_ft_sound``), if any: a host
        victim reaction plays none, so the impact carries it (Reptile's acid sizzle, reaction
        0x72)."""

        routine = self.word(REACTION_TABLE + 4 * reaction)
        if not routine:
            return None
        for x in _walk_calls(dc.decompile(self.mkt, routine)):
            if self.names.get(x.target or 0) == "his_ft_sound" and x.args[0].const() is not None:
                return x.args[0].const()
        return None

    # -- routines --------------------------------------------------------------------------------
    # -- commands (SMRE, 2026-11-27) --------------------------------------------------------------
    def command(self, record: int) -> tuple[dict[str, Any], list[str]]:
        """The move program's ``command`` block from the MKT command record at ``record``, and
        notes on the parts of its condition routine that are not lowered.

        * ``buttons``: the buttons of the input events that hold this record (or an identical
          copy: Reptile's forceballs sit in both the High Punch and Low Punch tables), within
          the record's masks; ``"stick"`` for the stick events. Rayden's Lightning record has
          masks 0xFC but sits only in the Low Punch event: 0x80.
        * ``release``: the record is in the button-release grid (Rayden's Shocker).
        * ``tokens``, ``window``: the record's (newest first, as facing right).
        * ``conditions``: read from the condition routine (:meth:`conditions`)."""

        rom = MktRom(self.mkt)
        if self.inline(record):
            return self.inline_command(record)
        rec = rom.record(record)
        same = [(g, e) for g, e, va in rom.record_sites(self.fighter) if _same_command(rom.record(va), rec)]
        if not same:
            raise ValueError(f"record 0x{record:08X} is not one of fighter {self.fighter}'s commands")
        grids = {g for g, _ in same}
        events = {e for _, e in same}
        if len(grids) != 1:
            raise ValueError(f"record 0x{record:08X} sits in both the press and the release grid")
        cmd: dict[str, Any] = {}
        if events & STICK_EVENTS:
            if events - STICK_EVENTS:
                raise ValueError(f"record 0x{record:08X} mixes stick and button events")
            cmd["buttons"] = "stick"
        else:
            unknown = events - set(EVENT_BUTTONS)
            if unknown:
                raise ValueError(f"record 0x{record:08X}: input events {sorted(unknown)} have no host button")
            buttons = 0
            for e in events:
                buttons |= EVENT_BUTTONS[e]
            cmd["buttons"] = f"0x{buttons & rec.masks[0]:X}"
        if grids == {"release"}:
            cmd["release"] = True
        cmd.update(tokens=list(rec.right), window=rec.window, src=f"MKT 0x{record:08X}")
        notes: list[str] = []
        if rec.condition:
            conds, notes = self.conditions(rec.condition)
            if conds:
                cmd["conditions"] = conds
        return cmd, notes

    def inline(self, table: int) -> list[tuple[Any, Any]]:
        """``(handler, inline command)`` for each inline matcher call on the compact command
        table at ``table`` in the fighter's imperative handlers (Sektor's specials)."""

        rom = MktRom(self.mkt)
        return [(h, c) for h in rom.handlers(self.fighter) for c in h.inline if c.table == table]

    def inline_command(self, table: int) -> tuple[dict[str, Any], list[str]]:
        """The ``command`` block of an inline command (:meth:`inline`): buttons from the events
        whose handlers match it, within its mask; tokens and window from its compact table;
        conditions from the handler's guards between the matcher call and the transfer
        (``process_exist`` on his projectile process: ``projectiles_below`` 1; other calls and
        guard fields are noted)."""

        hits = self.inline(table)
        events = {h.event for h, _ in hits}
        if {h.grid for h, _ in hits} != {"press"}:
            raise ValueError(f"inline command 0x{table:08X}: only press handlers are read")
        unknown = events - set(EVENT_BUTTONS)
        if unknown:
            raise ValueError(f"inline command 0x{table:08X}: input events {sorted(unknown)} have no host button")
        first = hits[0][1]
        buttons = 0
        for h, c in hits:
            buttons |= EVENT_BUTTONS[h.event] & c.mask
        cmd: dict[str, Any] = {"buttons": f"0x{buttons:X}", "tokens": list(first.right), "window": first.window,
                               "src": f"MKT 0x{table:08X}"}  # fmt: skip
        conds: list[dict] = []
        notes: list[str] = []
        r = reading.read(self.mkt, hits[0][0].address)
        insns = r.insns
        regs: dict[int, int] = {}
        start = None
        for k, ins in enumerate(insns):
            if ins.op == "lui":
                regs[ins.rt] = (ins.imm & 0xFFFF) << 16
            elif ins.op in ("addiu", "ori"):
                base = 0 if ins.rs == 0 else regs.get(ins.rs, 0)
                regs[ins.rt] = ((base + ins.imm) if ins.op == "addiu" else (base | (ins.imm & 0xFFFF))) & 0xFFFFFFFF
            if ins.op != "jal":
                if start is not None and ins.op in ("lhu", "lh", "lw") and ins.imm in OTHER_GUARD_FIELDS:
                    notes.append(f"0x{ins.pc:08X}: {OTHER_GUARD_FIELDS[ins.imm]} (not lowered)")
                if start is not None and ins.op == "lhu" and ins.imm == PROCESS_ID:  # a count of
                    limit = next((x for x in insns[k:k + 12] if x.op == "slti"), None)  # processes
                    if limit is not None and not any("live processes" in n for n in notes):
                        ids = sorted({x.imm for x in insns[start:k] if x.op == "addiu" and x.rs == 0 and x.imm >> 8 in (7, 8)})
                        notes.append(f"0x{ins.pc:08X}: fewer than {limit.imm} live processes with ids "
                                     f"{', '.join(f'0x{v:X}' for v in ids)} (not lowered)")  # fmt: skip
                continue
            delay = insns[k + 1] if k + 1 < len(insns) else None
            if delay is not None and delay.op == "addiu":
                base = 0 if delay.rs == 0 else regs.get(delay.rs, 0)
                regs[delay.rt] = (base + delay.imm) & 0xFFFFFFFF
            if ins.target == MATCHER and start is None and regs.get(6) == table:
                start = k
            elif start is not None and ins.target == TRANSFER:
                break
            elif start is not None and ins.target == PROCESS_EXIST:
                ids = {v for v in (0x705, 0x805) if any(x.op in ("addiu", "ori") and x.imm == v for x in insns[start:k + 2])}
                if ids & PROJECTILE_PROCESSES:
                    conds.append({"kind": "projectiles_below", "count": 1, "src": f"MKT 0x{ins.pc:08X}"})
                else:
                    notes.append(f"0x{ins.pc:08X}: process_exist (not lowered)")
            elif start is not None and ins.target != PROCESS_SUICIDE:  # (suicide: the refusal)
                notes.append(f"0x{ins.pc:08X}: {self.names.get(ins.target, f'0x{ins.target:08X}')} (not lowered)")
        if start is None:
            raise ValueError(f"inline command 0x{table:08X}: its matcher call was not found")
        if conds:
            cmd["conditions"] = conds
        return cmd, notes

    def conditions(self, entry: int, args: tuple[int | None, ...] = (), depth: int = 0) -> tuple[list[dict], list[str]]:
        """Command conditions from a condition routine, by a linear read of its instructions with
        constant tracking, following called routines with their arguments:

        * ``ticks_since(stamp)`` then ``slti v0, N``: ``held_for`` N when the stamp is a button
          press stamp (:data:`PRESS_STAMPS`), else ``cooldown`` (key = the stamp word);
        * ``buttons_held(a0, mask)``: ``buttons_held``;
        * any other test (airborne, the opponent's state) is noted, not lowered."""

        r = reading.read(self.mkt, entry)
        regs: dict[int, int | None] = {4 + i: a for i, a in enumerate(args)}
        conds: list[dict] = []
        notes: list[str] = []
        insns = r.insns
        k = 0

        def effect(ins: Any) -> None:
            if ins.op == "lui":
                regs[ins.rt] = (ins.imm & 0xFFFF) << 16
            elif ins.op in ("addiu", "ori"):
                base = 0 if ins.rs == 0 else regs.get(ins.rs)
                imm = ins.imm if ins.op == "addiu" else ins.imm & 0xFFFF
                regs[ins.rt] = None if base is None else ((base + imm) if ins.op == "addiu" else (base | imm)) & 0xFFFFFFFF
            elif ins.op == "or" and ins.rt == 0:
                regs[ins.rd] = 0 if ins.rs == 0 else regs.get(ins.rs)
            elif ins.op in ("lw", "lh", "lhu", "lb", "lbu", "addu", "subu", "and", "or", "sll", "srl", "sra"):
                regs[ins.rd if ins.op in ("addu", "subu", "and", "or", "sll", "srl", "sra") else ins.rt] = None

        while k < len(insns):
            ins = insns[k]
            if ins.op != "jal":
                effect(ins)
                if ins.op in ("lhu", "lh", "lw") and ins.rs != 29 and ins.imm in OTHER_GUARD_FIELDS:
                    notes.append(f"0x{ins.pc:08X}: {OTHER_GUARD_FIELDS[ins.imm]} (not lowered)")
                k += 1
                continue
            if k + 1 < len(insns):
                effect(insns[k + 1])  # the delay slot runs first
            target, a0, a1 = ins.target, regs.get(4), regs.get(5)
            if target == TICKS_SINCE:
                cmp_ = next((x for x in insns[k + 2 : k + 8] if x.op in ("slti", "sltiu") and x.rs == 2), None)
                if a0 is None or cmp_ is None:
                    notes.append(f"0x{ins.pc:08X}: ticks_since with an unread stamp or limit (not lowered)")
                elif a0 in PRESS_STAMPS:
                    conds.append({"kind": "held_for", "ticks": cmp_.imm, "src": f"MKT 0x{cmp_.pc:08X}"})
                else:
                    conds.append({"kind": "cooldown", "key": f"0x{a0:08X}", "ticks": cmp_.imm,
                                  "src": f"MKT 0x{cmp_.pc:08X}"})  # fmt: skip
            elif target == BUTTONS_HELD:
                setter = next((x for x in reversed(insns[max(0, k - 6) : k + 2]) if x.op == "addiu" and x.rt == 5), None)
                if a1 is None or setter is None:
                    notes.append(f"0x{ins.pc:08X}: buttons_held with an unread mask (not lowered)")
                else:
                    conds.append({"kind": "buttons_held", "mask": f"0x{a1:X}", "src": f"MKT 0x{setter.pc:08X}"})
            elif depth < 2 and target not in self.names or self.names.get(target, "").startswith(OWN_CONDITIONS):
                more, more_notes = self.conditions(target, tuple(regs.get(4 + i) for i in range(4)), depth + 1)
                conds += more
                notes += more_notes
                if not more and not more_notes:
                    notes.append(f"0x{ins.pc:08X}: {self.names.get(target, f'0x{target:08X}')} (not lowered)")
            else:
                notes.append(f"0x{ins.pc:08X}: {self.names.get(target, f'0x{target:08X}')} (not lowered)")
            for r_ in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 24, 25):
                regs[r_] = None
            k += 2
        return conds, notes

    def program(self, name: str, record: int) -> tuple[dict[str, Any], Generated, list[str]]:
        """A whole move program from its MKT command record: the command, the steps of the
        record's action (dispatchers followed), and ``movement`` when the move moves the fighter
        (a ``relocate`` or ``velocity`` step: the owner's no-Ice rule for moving abilities)."""

        cmd, notes = self.command(record)
        inline = self.inline(record)
        g = self.move(inline[0][1].dispatch if inline else MktRom(self.mkt).record(record).action)
        prog: dict[str, Any] = {"name": name, "command": cmd, "steps": g.steps}
        if any(s["op"] in MOVEMENT_OPS for s in _all(g.steps)):
            prog["movement"] = True
        if g.grab:
            prog["grab"] = True
        return prog, g, notes

    def move(self, entry: int, args: tuple[int, ...] = ()) -> Generated:
        self.top = entry
        g = Generated(entry, [])
        g.steps = _clean(_trim_ends(self.routine(entry, args, g, 0)))
        return g

    def routine(self, entry: int, args: tuple[int, ...], g: Generated, depth: int) -> list[dict]:
        if depth > MAX_DEPTH:
            g.unknown.append(f"0x{entry:08X}: too deep")
            return []
        stmts = dc.decompile(self.mkt, entry, args)
        _index_calls(stmts)
        return _Walk(self, g, depth).stmts(stmts)


class _Walk:
    """One routine's statements -> steps (with its pending animation selection)."""

    def __init__(self, gen: Generator, g: Generated, depth: int) -> None:
        self.gen, self.g, self.depth = gen, g, depth
        self.pending: dict[str, int] | None = None  # get_char_ani not yet shown
        self.offset = 0  # words skipped on the pending selection (process +0x41C += 4n)
        self.action: int | None = None
        self.velocity: int | None = None  # towards_x_vel stopped by stop_me: applied later
        self.ended = False
        self.out: list[dict] = []  # the steps of the statement list being walked
        self.pending_at = 0  # where the pending selection was made (index in ``out``)
        self.begin: dict | None = None
        self.target: int | None = None  # process +0x8: the routine a context_jump restarts at
        self.begin_own = False  # the begin step named its action itself (begin_special mode 1)
        self.object_anim: dict[str, int] | None = None  # selection a projectile object was made from
        self.projectiles: dict[int, tuple[dict, int]] = {}  # proj_process pc -> (step, child)
        self.copy: int | None = None  # pc of new_object: the fighter's copy being set up
        self.matched = False  # match_me_to_opponent ran: an offset next is a relocation
        self.edges = False  # an arena-edge test ran in this routine (MKT's teleport side)
        self.grab: dict[str, Any] | None = None  # a grab's hit path is being read (damage, release)
        self.yvel: int | None = None  # object +0x10 / +0x8 set by the move (motion loops, do_jump)
        self.gravity: int | None = None
        self.gravity_hit: int | None = None  # the gravity after the move's strike was blocked
        self.anirate: int | None = None  # init_anirate: the rate next_anirate steps the selection at
        self.callback: int | None = None  # process +0x438: the routine the next jump runs each tick
        self.last_anim: dict[str, int] | None = None  # the selection last shown
        self.saved: tuple[dict[str, int], int] | None = None  # cursor saved at process +0x440
        self.proj_offset: list[int] | None = None  # multi_adjust_xy on the projectile object

    def name(self, c: dc.Call) -> str:
        return self.gen.names.get(c.target, f"0x{c.target:08X}" if c.target else "jalr")

    def note(self, text: str) -> None:
        if text not in self.g.notes:
            self.g.notes.append(text)

    def unknown(self, text: str) -> None:
        if text not in self.g.unknown:
            self.g.unknown.append(text)

    # -- statements --------------------------------------------------------------------------------
    def stmts(self, stmts: list) -> list[dict]:
        out: list[dict] = []
        saved, self.out = self.out, out
        try:
            return self._stmts(stmts, out)
        finally:
            self.out = saved

    def _stmts(self, stmts: list, out: list[dict]) -> list[dict]:
        i = 0
        while i < len(stmts) and not self.ended:
            s = stmts[i]
            if s.kind == "call" and self.name(s) == "grab_refused" and self.grab is None:
                made = self.grab_shape(stmts, i)
                if made is not None:  # the rest of the list is the grab's hit path, read by it
                    out += made
                    return out
            if s.kind == "loop":
                count = self._count(stmts[:i], s)
                if count is not None:
                    out += self.loop(s, count, out)
                    i += 1
                    continue
                motion = self.motion_loop(s)
                if motion is not None:
                    out += motion
                    i += 1
                    continue
            out += self.stmt(s)
            i += 1
        return out

    def stmt(self, s: Any) -> list[dict]:
        if s.kind == "call":
            return self.call(s)
        if s.kind == "store":
            return self.store(s)
        if s.kind == "if":
            return self.branch(s)
        if s.kind == "loop":
            self.unknown(f"0x{s.pc:08X}: loop without a counter")
            return []
        if s.kind in ("return", "break"):
            return []
        self.unknown(f"0x{s.pc:08X}: {s.why}")
        return []

    def store(self, s: dc.Store) -> list[dict]:
        if s.base == dc.PROC and s.off == 0x3F6 and s.value.const() is not None:
            self.action = s.value.const()  # the action id, kept on begin
            if self.begin is not None and not self.begin_own:
                self.begin["action_mkt"] = hex(self.action)
                self.begin.setdefault("src", {})["action_mkt"] = f"MKT 0x{s.pc:08X}"  # the store
            elif self.begin is not None:
                self.note(f"MKT changes the action to 0x{self.action:X} later in the move "
                          f"(0x{s.pc:08X}); the program keeps the begin's")  # fmt: skip
            return []
        if isinstance(s.base, dc.Result) and s.base.call in self.projectiles and s.off == 0x440:
            v = s.value.const()  # the parent hands its projectile process a value (+0x440)
            step, child = self.projectiles[s.base.call]
            if v is not None:
                fields = {(0x440, 4): v, (0x440, 2): (v >> 16) & 0xFFFF, (0x442, 2): v & 0xFFFF}
                for kept, first in ((self.g.notes, step.pop("_notes", [])), (self.g.unknown, step.pop("_unknown", []))):
                    kept[:] = [x for x in kept if x not in first]  # the provisional reading's
                refilled = _read_projectile(self, child, fields)
                src = step.get("src", {})
                step.clear()
                step.update(refilled)
                if src:
                    step["src"] = {k: next(iter(src.values())) for k in refilled if k not in _NO_SRC}
            else:
                self.unknown(f"0x{s.pc:08X}: projectile process field +0x440 = {s.value}")
            return []
        if s.base == dc.PROC and s.off == 0x8 and s.value.const() is not None:
            self.target = s.value.const() & 0xFFFFFFFF
            return []
        if s.base == dc.SELF and s.off == 0x24 and isinstance(s.value, dc.Bin) and s.value.op == "|":
            bits = s.value.b.const()
            if bits is not None and bits & 0x20:  # the object's invisible flag
                self.note("MKT's invisibility (object flag 0x20) has no timer in the move: the "
                          "stealth length is the owner's (description)")  # fmt: skip
                return [{"op": "stealth"}]
        if s.base == dc.PROC and s.off == 0x440 and isinstance(s.value, dc.Load) and s.value.off == 0x41C:
            anim = self.pending if self.pending is not None else self.last_anim
            if anim is not None:  # the animation cursor saved (teleport_land, MKT 0x80076ED4)
                self.saved = (dict(anim), self.offset)
                return []
        if s.base == dc.PROC and s.off == 0x41C and isinstance(s.value, dc.Load) and s.value.off == 0x41C:
            # the cursor restored from +0x440 (the decompiler forwards the saved value: the cursor
            # as it was when saved); the next frame shown is the saved one again
            if self.saved is None:  # saved outside this routine (Rayden's Shocker): as before
                return []
            self.pending, self.offset = dict(self.saved[0]), self.saved[1]
            return []
        if s.base == dc.PROC and s.off == 0x41C and isinstance(s.value, dc.Bin):
            step = s.value.b.const()
            if s.value.op == "+" and step is not None and self.pending is not None:
                self.offset += step // 4  # skip words of the selected animation
                return []
        if (
            isinstance(s.value, dc.Load) and s.value.base == dc.PROC and s.value.off == 0x440
            and self.velocity is not None
        ):  # fmt: skip
            # the saved velocity source written back (torpedo: after the take-off phase)
            v, self.velocity = self.velocity, None
            return [{"op": "velocity", "x": hex(v)}]
        if s.base == dc.SELF and s.off in (0x10, 0x8) and s.value.const() is not None:
            v = s.value.const() & 0xFFFFFFFF
            v = v - (1 << 32) if v & 0x80000000 else v
            if s.off == 0x10:
                self.yvel = v
            else:
                self.gravity = v
            return []
        if s.base == dc.SELF and s.off == 0x18 and f"0x{SCREEN_BOTTOM:08X}" in str(s.value):
            self.note("MKT starts the rise at the screen's bottom line (object +0x18 = "
                      f"[0x{SCREEN_BOTTOM:08X}]); the host rise starts below the floor")  # fmt: skip
            return []
        if s.base == dc.PROC and s.off == 0x438 and s.value.const() is not None:
            self.callback = s.value.const() & 0xFFFFFFFF  # the jump's per-tick callback
            return []
        if s.base == dc.SELF and s.off == 0x18 and "proc+0x3F8" in str(s.value):
            self.note("MKT puts the fighter on his floor (object +0x18 = process +0x3F8); the host "
                      "relocation lands him on the floor")  # fmt: skip
            return []
        return []  # other process/object fields: not modelled (flags, timers, links)

    def branch(self, s: dc.If) -> list[dict]:
        c = s.cond.const()
        if c is not None:  # decided by a known argument
            return self.stmts(s.then if c else s.other)
        ends = [x for x in s.then if x.kind != "break"]
        if (self.grab is not None and "proc+0x3C0" in str(s.cond) and not s.other and len(ends) == 1
                and ends[0].kind == "call" and self.name(ends[0]) == "reaction_exit"):  # fmt: skip
            self.note(f"MKT ends the grab if the victim breaks free (0x{s.pc:08X}: {s.cond}); the host "
                      "victim reaction holds it to the end")  # fmt: skip
            return []
        if any(f"[0x{p:08X}]" in str(s.cond) for p in PLAYER_OBJECTS) and "self" in str(s.cond):
            # which player the fighter is (per-player tables, e.g. the torpedo's velocity source):
            # bookkeeping; both arms do the same for their player
            return self.stmts(s.then)
        text = str(s.cond)
        if "self+0x38:2" in text and isinstance(s.cond, dc.Bin) and s.cond.b.const() is not None:
            # the fighter id (object +0x38): decided by the generated fighter
            same = s.cond.b.const() == self.gen.fighter
            return self.stmts(s.then if same == (s.cond.op == "==") else s.other)
        if "+0x3D0" in text and isinstance(s.cond, dc.Bin) and s.cond.op == "==":
            sides = [[x for x in b if x.kind != "break"] for b in (s.then, s.other)]
            if all(len(b) == 1 and b[0].kind == "store" and b[0].base == dc.SELF and b[0].off == 0x8
                   and b[0].value.const() is not None for b in sides):  # fmt: skip
                # the gravity by whether the move's strike was blocked (process +0x3D0: the check
                # copies MKT's blocked flag 0x8014C3B8 there on contact)
                self.gravity, self.gravity_hit = (b[0].value.const() for b in sides)
                return []
        if self.edges and "?" in text:  # the rest of the edge test (its distance, < 103 px)
            return self.stmts(s.then)
        if "0x802576F0" in text or "0x802576EC" in text:
            self.edges = True
            self.note("MKT picks a side by the arena's edges (0x802576EC / 0x802576F0); the host "
                      "relocation picks it by the room there (walls, floor)")  # fmt: skip
            return self.stmts(s.then)
        call = self._tested_call(s.cond)
        if call == "opponent_reacting":
            rates = [self._phase_rate(b) for b in (s.then, s.other)]
            if None not in rates and self.pending is not None:
                fast, normal = rates if "== 0x8000" in str(s.cond) else rates[::-1]
                anim, self.pending = self.pending, None
                return [{"op": "animate", "anim": anim, "rate": normal, "rate_reacting": fast, "until": "phase_end",
                         "src": {k: f"MKT 0x{s.pc:08X}" for k in ("anim", "rate", "rate_reacting", "until")}}]  # fmt: skip
        if call == "proc_flag1":
            self.note("MKT's landing leaves by another route when process +0x3FA bit 0 is set "
                      f"(0x{s.pc:08X}); the host landing ends the move")  # fmt: skip
            return self.stmts(s.other)
        if call == "is_airborne":
            self.note("MKT runs part of the move only when airborne (is_airborne); the program "
                      "runs it always (on the ground the drop ends at once)")  # fmt: skip
            return self.stmts(s.then)
        self.unknown(f"0x{s.pc:08X}: branch on {s.cond}")
        return self.stmts(s.then)

    def _phase_rate(self, branch: list) -> int | None:
        """A branch that only plays the selection to its phase end (mframew n): n."""

        calls = [x for x in branch if x.kind != "break"]
        if len(calls) == 1 and calls[0].kind == "call" and self.name(calls[0]) == "mframew":
            return calls[0].args[0].const()
        return None

    def _tested_call(self, cond: dc.Value) -> str | None:
        if isinstance(cond, dc.Bin) and cond.op in ("==", "!="):
            for v in (cond.a, cond.b):
                if isinstance(v, dc.Result):
                    return self.gen.names.get(self._targets.get(v.call, 0))
        return None

    @property
    def _targets(self) -> dict[int, int]:
        return _CALL_TARGETS

    # -- calls ------------------------------------------------------------------------------------
    def call(self, c: dc.Call) -> list[dict]:
        _CALL_TARGETS[c.pc] = c.target or 0
        n = self.name(c)
        if n in _OBJECT_CALLS and _victim(c.args[_OBJECT_CALLS[n]]):
            self.note(f"MKT also drives the victim ({n} on the opponent, 0x{c.pc:08X}); the host "
                      "victim reaction does")  # fmt: skip
            return []
        a = [v.const() for v in c.args]
        rule = CALL_RULES.get(n)
        if rule is not None:
            return _provenance(rule(self, c, a), c.pc)
        entry = REGISTRY.get(c.target or 0)
        if c.target and (entry is None or entry.follow):  # a move body or an unnamed routine
            if entry is None and not self._is_move_code(c.target):
                self.unknown(f"0x{c.pc:08X}: call {n}")
                return []
            return self.gen.routine(c.target, tuple(x for x in a[:1] if x is not None), self.g,
                                    self.depth + 1)  # fmt: skip
        self.unknown(f"0x{c.pc:08X}: call {n}")
        return []

    def _is_move_code(self, target: int) -> bool:
        """An unnamed routine next to the move's own body (the same source file: the torpedo's
        carry and bounce follow its body); farther ones are engine code a rule must name."""

        return abs(target - self.gen.top) < 0x1000

    def show_pending(self) -> list[dict]:
        if self.pending is None:
            return []
        anim = dict(self.pending)
        self.last_anim = dict(self.pending)
        if self.offset:
            anim["offset"] = self.offset
        self.pending, self.offset = None, 0
        return [{"op": "pose", "anim": anim}]

    # -- loops ------------------------------------------------------------------------------------
    @staticmethod
    def _count(before: list, loop: dc.Loop) -> int | None:
        """The loop's count: the constant stored to the process field its condition counts down,
        among the stores just before it, or a register counted down from a known value."""

        if loop.count is not None:
            return loop.count
        for s in reversed(before[-4:]):
            if s.kind != "store":
                break
            if s.base == dc.PROC and s.value.const() is not None and f"proc+0x{s.off:X}" in str(loop.cond):
                return s.value.const()
        return None

    def loop(self, loop: dc.Loop, count: int, out: list[dict]) -> list[dict]:
        body = [x for x in loop.body if not (x.kind == "store" and x.base == dc.PROC and "proc+0x" in str(x.value)
                                             and f"proc+0x{x.off:X}" in str(x.value))]  # fmt: skip
        if self.pending is not None and any(x.kind == "call" and self.name(x) == "do_next_a9_frame" for x in body):
            # frames stepped by hand each tick: show the first where it was selected
            out.insert(self.pending_at, {"op": "animate", "anim": dict(self.pending), "rate": 1, "until": "manual"})
            self.pending = None
        at = f"MKT 0x{loop.pc:08X}"  # steps made from the loop's shape name the loop as their source
        strike = self._find_strike(body)
        if strike is not None:
            step = self.window(body, strike, count)
            if "src" not in step:  # the window's length from the loop, the rest from the strike call
                call_at = f"MKT 0x{strike[0].pc:08X}"
                step["src"] = {k: (at if k == "ticks" else call_at) for k in step
                               if k not in ("op", "every_tick", "on_hit", "on_block")}  # fmt: skip
            return [step]
        if self._carry(body):
            self.note("MKT's carry shares one velocity between the fighters and ends when either "
                      "stops (a wall); the host keeps the victim at its contact distance")  # fmt: skip
            return [{"op": "carry", "ticks": count, "src": {"ticks": at},
                     "every_tick": [{"op": "pass_through", "ticks": 1, "src": {"ticks": at}}]}]  # fmt: skip
        steps = self.stmts(body)
        return [{"op": "repeat", "count": count, "steps": steps, "src": {"count": at}}]

    def motion_loop(self, loop: dc.Loop) -> list[dict] | None:
        """A loop of single ticks that moves the object until its y passes the screen's bottom
        line (``below_screen``) or reaches its floor (``surface``), with the velocity and gravity
        the move set: a ``jump`` step. The loop's rate-stepped animation (init_anirate /
        next_anirate) is an ``animate`` before it; a strike check made in the loop only within N
        px of the floor (``if (y - floor < N) strike``) is the jump's ``strike`` with
        ``strike_near_px``."""

        text = str(loop.cond)
        if "self+0x18" not in text or self.yvel is None or self.gravity is None:
            return None
        until = "below_screen" if f"0x{SCREEN_BOTTOM:08X}" in text else "surface" if "proc+0x3F8" in text else None
        if until is None:
            return None
        at = f"MKT 0x{loop.pc:08X}"
        out: list[dict] = []
        if self.pending is not None and self.anirate is not None:
            anim, self.pending = self.pending, None
            out.append({"op": "animate", "anim": anim, "rate": self.anirate, "until": "running",
                        "src": {"anim": at, "rate": at, "until": at}})  # fmt: skip
        else:
            out += self.show_pending()
        step: dict[str, Any] = {"op": "jump", "x": "0x0", "y": hex(self.yvel), "gravity": hex(self.gravity),
                                "until": until}  # fmt: skip
        for x in loop.body:
            if x.kind == "call" and self.name(x) in ("process_sleep", "next_anirate"):
                continue
            near = self._near_strike(x)
            if near is not None:
                step["strike"], step["strike_near_px"] = near
                continue
            self.unknown(f"0x{x.pc:08X}: {x.kind} in a motion loop")
        step["src"] = {k: at for k in step if k != "op"}
        return out + [step]

    def _near_strike(self, x: Any) -> tuple[dict, int] | None:
        """``if (self+0x18 - proc+0x3F8 < N) strike_routine()``: (strike, N)."""

        if x.kind != "if" or x.other or len(x.then) != 1 or x.then[0].kind != "call":
            return None
        m = re.search(r"\) < (0x[0-9A-F]+|\d+)\)", str(x.cond))
        if m is None or "proc+0x3F8" not in str(x.cond):
            return None
        strike = self._routine_strike(x.then[0].target)
        return None if strike is None else (strike, int(m.group(1), 0))

    def _routine_strike(self, target: int | None) -> dict | None:
        """The strike a small routine checks (``strike_check_a0`` on the fighter's strike table)."""

        if not target:
            return None
        body = dc.decompile(self.gen.mkt, target)
        calls = [y for y in _walk_stmts(body) if y.kind == "call" and self.gen.names.get(y.target) == "strike_check_a0"]
        if len(calls) != 1:
            return None
        decoded = self.gen.strike(calls[0].args[0])
        return None if decoded is None else decoded[0]

    def grab_shape(self, stmts: list, i: int) -> list[dict] | None:
        """A grab (Rayden's Shocker, MKT 0x80073228)::

            r = grab_refused()
            if (r != 0x8000) { if (|my x - his x| < N) { if (opponent settled) goto hit } }
            miss()        (a routine that ends the move)
            hit: ...      (damage_opponent, opponent_routine(hold), ..., opponent_routine(release))

        becomes one ``strike`` of one tick: an unblockable box reaching N px in front of him
        (the host box's first value is its front edge), MKT's damage, the reaction the release
        routine names (:data:`GRAB_RELEASES`), the hit path as ``on_hit``; the miss routine's
        steps follow (the strike falls through to them). The move is a ``grab`` (owner rule:
        twice Ice Blast's Ice)."""

        import re

        call = stmts[i]
        if i + 2 >= len(stmts):
            return None
        test, miss = stmts[i + 1], stmts[i + 2]
        if test.kind != "if" or f"r{call.pc:08X}" not in str(test.cond) or miss.kind != "call":
            return None
        text = _tree_text(test)
        reach = re.search(r"\(\? < (0x[0-9A-Fa-f]+|\d+)\)", text)
        if reach is None or "+0x14:2 - proc+0x3BC+0x14:2" not in text:
            self.unknown(f"0x{call.pc:08X}: grab without a horizontal reach")
            return None
        reach_px = int(reach.group(1), 0)
        settled = "opponent_unsettled" in text
        miss_steps = self.call(miss)  # first: its action id must not replace the hit's on begin
        self.grab = {}
        on_hit = self.stmts(stmts[i + 3 :])
        grab, self.grab = self.grab, None
        if "damage" not in grab or "reaction" not in grab:
            self.unknown(f"0x{call.pc:08X}: grab without {'a damage' if 'damage' not in grab else 'a known release'}")
            return None
        strike = {"box": [reach_px, 0, reach_px, GRAB_BOX_HEIGHT], "damage": grab["damage"], "block_damage": 0,
                  "reaction": grab["reaction"], "blocked_reaction": "blocked", "unblockable": True}  # fmt: skip
        step: dict[str, Any] = {"op": "strike", "strike": strike, "ticks": 1}
        if settled:
            step["only_if"] = "opponent_settled"
        step["on_hit"] = on_hit
        step["src"] = {"strike": f"MKT 0x{call.pc:08X}", "ticks": f"MKT 0x{call.pc:08X}",
                       **({"only_if": f"MKT 0x{test.pc:08X}"} if settled else {})}  # fmt: skip
        self.g.grab = True
        self.note(f"MKT's grab tests the reach between the fighters' anchors (|dx| < {reach_px}); the host "
                  "box meets the victim's body")  # fmt: skip
        return [step] + miss_steps

    def _find_strike(self, body: list, guard: str | None = None) -> tuple[dc.Call, str | None, dc.If | None] | None:
        for i, x in enumerate(body):
            if x.kind == "call" and self.name(x) == "strike_check_a0":
                hit = next((y for y in body[i + 1 :] if y.kind == "if" and f"r{x.pc:08X}" in str(y.cond)), None)
                return x, guard, hit
            if x.kind == "if":
                inner = self._find_strike(x.then, self._tested_call(x.cond) or guard)
                if inner is not None:
                    return inner
        return None

    def window(self, body: list, found: tuple, count: int) -> dict:
        call, guard, hit = found
        decoded = self.gen.strike(call.args[0])
        step: dict[str, Any] = {"op": "strike", "ticks": count}
        if decoded is None:
            self.unknown(f"0x{call.pc:08X}: strike record {call.args[0]}")
        else:
            step["strike"] = decoded[0]
        if guard == "opponent_unsettled":
            step["only_if"] = "opponent_settled"
        every: list[dict] = []
        for x in body:  # the per-tick work besides the strike (sleep 1 is the window's own tick)
            if x is call or x is hit or (x.kind == "if" and self._contains(x, call)):
                continue
            if x.kind == "call" and self.name(x) == "process_sleep" and x.args[0].const() == 1:
                continue
            every += self.stmt(x)
        if every:
            step["every_tick"] = every
        on_hit: list[dict] = []
        on_block: list[dict] = []
        if hit is not None:
            branch = hit.then if "==" in str(hit.cond) else hit.other
            branch = [y for y in branch if y.kind != "break"]
            calls = [y for y in branch if y.kind == "call"]
            if len(calls) == 1 and len(branch) == 1 and self._follows(calls[0]):
                branch = dc.decompile(self.gen.mkt, calls[0].target)  # the hit routine itself
                _index_calls(branch)
            flag = next((y for y in branch if y.kind == "if" and "0x8014C3B8" in str(y.cond)), None)
            if flag is not None:  # the strike flag: blocked
                on_block = self.sub(flag.then)
                rest = [y for y in branch if y is not flag]
                on_hit = self.sub(flag.other + rest)
            else:
                on_hit = self.sub([y for y in branch if y.kind != "break"])
        step["on_hit"] = on_hit
        if on_block:
            step["on_block"] = on_block
        if any(s["op"] == "carry" for s in on_hit) and "strike" in step:
            step["strike"]["reaction"] = "torpedo_carry"
        return step

    def _follows(self, c: dc.Call) -> bool:
        entry = REGISTRY.get(c.target or 0)
        return bool(c.target) and ((entry is not None and entry.follow) or (entry is None and self._is_move_code(c.target)))

    def sub(self, stmts: list) -> list[dict]:
        w = _Walk(self.gen, self.g, self.depth)
        w.velocity = self.velocity
        steps = w.stmts(stmts)
        return steps

    @staticmethod
    def _contains(x: Any, call: dc.Call) -> bool:
        if x is call:
            return True
        for key in ("then", "other", "body"):
            for y in getattr(x, key, []) or []:
                if _Walk._contains(y, call):
                    return True
        return False

    def _carry(self, body: list) -> bool:
        breaks = [x for x in body if x.kind == "if" and any(y.kind == "break" for y in x.then)]
        return len(breaks) >= 2 and any(x.kind == "call" and self.name(x) == "process_sleep" for x in body)


_CALL_TARGETS: dict[int, int] = {}


def _index_calls(stmts: list) -> None:
    for x in stmts:
        if x.kind == "call":
            _CALL_TARGETS[x.pc] = x.target or 0
        for key in ("then", "other", "body"):
            _index_calls(getattr(x, key, []) or [])
_RANDU: dict[int, int | None] = {}  # randu call pc -> n
# calls that act on an object (argument index): on the opponent (process +0x3BC, +0x3C0) they are
# the victim's part, which the host victim reaction plays
_OBJECT_CALLS = {"stop_me": 0, "do_next_a9_frame": 0, "face_opponent": 0}


def _victim(v: dc.Value) -> bool:
    text = str(v)
    return "proc+0x3BC" in text or "proc+0x3C0" in text


_NO_SRC = ("op", "src", "steps", "every_tick", "on_hit", "on_block", "_notes", "_unknown")


def _provenance(steps: list[dict], pc: int) -> list[dict]:
    """Each parameter of a step a rule made comes from the MKT call it read (the move-program
    format's ``src``); a step that already names its sources keeps them."""

    for step in steps:
        params = [k for k in step if k not in _NO_SRC]
        if params and "src" not in step:
            step["src"] = {k: f"MKT 0x{pc:08X}" for k in params}
    return steps


def _clean(steps: list[dict]) -> list[dict]:
    for s in steps:
        s.pop("_notes", None)
        s.pop("_unknown", None)
        for key in ("steps", "every_tick", "on_hit", "on_block"):
            if key in s:
                _clean(s[key])
    return steps


def _trim_ends(steps: list[dict]) -> list[dict]:
    """A branch that ends the move where its parent would end it next anyway falls through
    (the program format's branches rejoin; MKT's end each one with reaction_exit)."""

    for i, s in enumerate(steps):
        rest = [x["op"] for x in steps[i + 1 :]]
        for key in ("on_hit", "on_block"):
            branch = s.get(key)
            if branch and branch[-1]["op"] == "end" and rest == ["end"]:
                s[key] = branch[:-1]
        for key in ("steps", "every_tick", "on_hit", "on_block"):
            if key in s:
                s[key] = _trim_ends(s[key])
    return steps


# ---- call rules: MKT engine routine -> steps ---------------------------------------------------
def _begin(face: bool):
    def rule(w: _Walk, c: dc.Call, a: list) -> list[dict]:
        step: dict[str, Any] = {"op": "begin", "face": face, "stop": True}
        if w.action is not None:
            step["action_mkt"] = hex(w.action)
        w.begin = step
        return [step]

    return rule


def _begin_special(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    mode, action = a[0], a[1]
    step: dict[str, Any] = {"op": "begin", "face": mode == 0, "stop": True}
    if mode == 1 and action is not None:
        step["action_mkt"] = hex(action)
        w.begin_own = True
    elif w.action is not None:
        step["action_mkt"] = hex(w.action)
    w.begin = step
    return [step]


def _sound(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    if a[0] is not None:
        return [{"op": "sound", "sound": {"fighter": a[0]}}]
    v = c.args[0]
    if isinstance(v, dc.Bin) and v.op == "&":
        v = v.a
    if isinstance(v, dc.Bin) and v.op == "+" and isinstance(v.a, dc.Result) and v.b.const() is not None:
        n = _RANDU.get(v.a.call)
        first = v.b.const() + 1  # randu(n) is 1..n
        span = f"{first}..{first + n - 1}" if n else f"{first} up"
        if n:
            return [{"op": "sound", "sound": {"fighter": first, "random": n}}]
        w.note(f"MKT picks the sound at random, {span} (0x{c.pc:08X}); the program plays {first}")
        return [{"op": "sound", "sound": {"fighter": first}}]
    w.unknown(f"0x{c.pc:08X}: sound {c.args[0]}")
    return []


def _select(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    if a[0] is None or a[1] is None:
        w.unknown(f"0x{c.pc:08X}: animation {c.args[0]}, {c.args[1]}")
        return []
    out = w.show_pending() if w.pending is not None and w.offset else []
    w.pending, w.offset = {"table": a[0], "slot": a[1]}, 0
    w.pending_at = len(w.out) + len(out)
    return out


def _last_frame(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """find_last_frame: the pending selection's cursor on the last frame of its first part (the
    offset counts its frames: the host copies a donor script's frames, tokens dropped)."""

    if w.pending is None:
        w.unknown(f"0x{c.pc:08X}: find_last_frame without a selection")
        return []
    from . import body_build
    from .mkt_fighter import MktRom

    donor = body_build.Donor(w.gen.mkt, w.gen.fighter)
    t1 = MktRom(w.gen.mkt).table1(w.gen.fighter)
    root = (donor.table0 if w.pending["table"] == 0 else t1)[w.pending["slot"]]
    phases = body_build.donor_frames_by_phase(donor, root, set(donor.table0) | set(t1))
    w.offset = len(phases[0]) - 1
    return []


def _backward(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """ani_backward(rate, -1): the selection from its last frame back to its first, ``rate``
    ticks a frame (MKT 0x8000E004; Sektor's chest closing)."""

    if w.pending is None or a[0] is None:
        w.unknown(f"0x{c.pc:08X}: ani_backward without a selection")
        return []
    anim, w.pending = w.pending, None
    return [{"op": "animate", "anim": anim, "rate": a[0], "until": "phase_end", "reverse": True}]


def _anirate(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    w.anirate = a[0]
    return []


def _follow(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """A named engine routine whose steps are the move's (teleport_land: the landing poses)."""

    return w.gen.routine(c.target, tuple(x for x in a if x is not None), w.g, w.depth + 1)


def _randu(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    _RANDU[c.pc] = a[0]
    return []


def _to_phase_end(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    if w.pending is not None and not w.offset:
        anim, w.pending = w.pending, None
        return [{"op": "animate", "anim": anim, "rate": a[0], "until": "phase_end"}]
    return w.show_pending() + [{"op": "finish", "rate": a[0]}]


def _animate_table1(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    return [{"op": "animate", "anim": {"table": 1, "slot": a[1]}, "rate": a[0], "until": "phase_end"}]


def _next_frame(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    if w.pending is not None:
        return w.show_pending()
    return [{"op": "next_frame"}]


def _context_jump(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """The process restarts at process +0x8 (stored just before): its steps follow, and nothing
    after the jump runs."""

    target, w.target = w.target, None
    w.ended = True
    if target is None or not w._is_move_code(target):
        w.unknown(f"0x{c.pc:08X}: context jump to {hex(target) if target else '?'}")
        return []
    return w.gen.routine(target, (), w.g, w.depth + 1)


def _velocity(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    w.velocity = a[2]
    return [{"op": "velocity", "x": hex(a[2])}] if a[2] is not None else []


def _stop(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    if w.out and w.out[-1]["op"] == "velocity":
        # MKT sets the speed, stops, and writes the saved speed back later (the torpedo after its
        # take-off phase): the velocity step goes where it is written back
        w.out.pop()
        return []
    return [{"op": "stop"}]


def _jump(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    x, y, g = a[1], a[2], a[3]
    if JUMP_KEEP in (y, g) and x is not None:  # keep the move's current velocity / gravity
        return w.show_pending() + _kept_jump(w, c, x, y, g)
    if None in (x, y, g):
        w.unknown(f"0x{c.pc:08X}: jump {c.args}")
        return []
    rate = c.args[4].const()
    step: dict[str, Any] = {"op": "jump", "x": hex(x), "y": hex(y), "gravity": hex(g), "until": "landing"}
    if rate is not None and 0 < rate < 0x100:  # do_jump animates the selection at this rate
        step["rate"] = rate
    return w.show_pending() + [step]


def _kept_jump(w: _Walk, c: dc.Call, x: int, y: int, g: int) -> list[dict]:
    """do_jump with ``JUMP_KEEP`` (0xD) for the y velocity and/or gravity: the jump goes on from
    the velocity the move left (no ``y``) with the gravity it set (``gravity_on_block``: the
    other one after its strike was blocked). A per-tick callback (process +0x438) that strikes while the object
    rises (``if (self+0x10 < 0) strike``) is the jump's ``strike`` with ``strike_while: rising``."""

    gravity = w.gravity if g == JUMP_KEEP else g
    if gravity is None:
        w.unknown(f"0x{c.pc:08X}: jump keeps a gravity the move did not set")
        return []
    step: dict[str, Any] = {"op": "jump", "x": hex(x), "gravity": hex(gravity), "until": "landing"}
    if y != JUMP_KEEP:
        step["y"] = hex(y)
    if w.gravity_hit is not None and g == JUMP_KEEP:
        step["gravity_on_block"] = hex(w.gravity_hit)
    if w.callback is not None:
        body = dc.decompile(w.gen.mkt, w.callback)
        ifs = [s for s in body if s.kind == "if"]
        if len(ifs) == 1 and "self+0x10" in str(ifs[0].cond) and "<0 0" in str(ifs[0].cond) and len(ifs[0].then) == 1:
            strike = w._routine_strike(ifs[0].then[0].target)
            if strike is not None:
                step["strike"], step["strike_while"] = strike, "rising"
        if "strike" not in step:
            w.unknown(f"0x{c.pc:08X}: jump callback 0x{w.callback:08X}")
        w.callback = None
    step["src"] = {k: f"MKT 0x{c.pc:08X}" for k in step if k != "op"}
    return [step]


def _end(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    w.ended = True
    return [{"op": "end"}]


def _sleep(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    return [{"op": "sleep", "ticks": a[0]}] if a[0] is not None else []


def _face(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    return [{"op": "face"}]


def _effect(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    return [{"op": "effect", "effect": {"mkt_fx": a[0]}}]


def _no_repel(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    return [{"op": "pass_through", "ticks": 3}]


def _shake_screen(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    if a[0] is None or a[1] is None:
        w.unknown(f"0x{c.pc:08X}: shake_screen {c.args[0]}, {c.args[1]}")
        return []
    # 0x8002A78C steps every 3 ticks (Static-confirmed)
    return [{"op": "shake_screen", "amplitude": a[0], "count": a[1], "ticks": 3}]


def _shake_object(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    count, dx, dy, ticks = a[3], a[1], a[2], c.args[4].const()
    if None in (count, dx, dy, ticks):
        w.unknown(f"0x{c.pc:08X}: shake {c.args}")
        return []
    return [{"op": "shake", "dx": dx, "dy": dy, "count": count, "ticks": ticks}]


def _frame_at(w: _Walk, c: dc.Call, a: list) -> list[dict]:  # ani_frame_at_t0(skip, slot)
    return [{"op": "pose", "anim": {"table": 0, "slot": a[1], "offset": a[0]}}]


def _ignore(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    return []


def _damage_opponent(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    if w.grab is None or a[0] is None:
        w.unknown(f"0x{c.pc:08X}: damage_opponent outside a grab")
    else:
        w.grab["damage"] = a[0]
    return []


def _opponent_routine(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    routine = None if a[1] is None else a[1] & 0xFFFFFFFF
    if w.grab is not None and routine in GRAB_RELEASES:
        w.grab["reaction"] = GRAB_RELEASES[routine]
    elif w.grab is None:
        w.unknown(f"0x{c.pc:08X}: opponent_routine outside a grab")
    return []  # the hold (a waiting routine) and the release are the victim reaction's


def _step_frames(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """step_frames(ticks, n) after a selection: its first frame, then n - 1 more, ``ticks`` each."""

    if a[0] is None or a[1] is None or w.pending is None:
        w.unknown(f"0x{c.pc:08X}: step_frames {c.args[0]}, {c.args[1]}")
        return []
    first = w.show_pending()
    at = f"MKT 0x{c.pc:08X}"
    body = [{"op": "sleep", "ticks": a[0], "src": {"ticks": at}}, {"op": "next_frame"}]
    return first + [{"op": "repeat", "count": a[1] - 1, "steps": body}, {"op": "sleep", "ticks": a[0]}]


def _note_only(text: str):
    def rule(w: _Walk, c: dc.Call, a: list) -> list[dict]:
        w.note(text)
        return []

    return rule


def _dispatch(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """do_special / do_body_propell / do_quick_special: the move body from the dispatch table."""

    target = reading.resolve(w.gen.mkt, c.target or 0, a[0]) if a[0] is not None else None
    if target is None:
        w.unknown(f"0x{c.pc:08X}: dispatch {w.name(c)}({c.args[0]})")
        return []
    w.gen.top = target  # the move's own code: its helpers sit next to it
    return w.gen.routine(target, (), w.g, w.depth + 1)


def _projectile(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """proj_process(child): the projectile step, read from the child process (refilled when the
    parent then hands the child a value in its +0x440, as Rayden's lightning does its argument)."""

    if a[0] is None:
        w.unknown(f"0x{c.pc:08X}: projectile process {c.args[0]}")
        return []
    child = a[0] & 0xFFFFFFFF
    step = _read_projectile(w, child, {})
    if w.proj_offset is not None:  # placed by the parent before the process (make_rocket)
        step["offset"], w.proj_offset = w.proj_offset, None
    w.projectiles[c.pc] = (step, child)
    return [step]


def _read_projectile(w: _Walk, child: int, fields: dict[tuple[int, int], int]) -> dict[str, Any]:
    """:func:`projectile`, remembering (as ``_notes`` / ``_unknown``) what it reported, so a
    refill with the parent's value replaces it; :func:`clean` drops the two keys."""

    notes, unknown = list(w.g.notes), list(w.g.unknown)
    step = projectile(w, child, fields)
    step["_notes"] = [x for x in w.g.notes if x not in notes]
    step["_unknown"] = [x for x in w.g.unknown if x not in unknown]
    return step


def _new_object(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    w.copy = c.pc  # a copy of the fighter (its art): an afterimage when a process animates it
    return []


def _frame_at_t1(w: _Walk, c: dc.Call, a: list) -> list[dict]:  # ani_frame_at(skip, slot)
    if w.copy is not None:
        return []  # the copy's first frame: the afterimage shows it
    return [{"op": "pose", "anim": {"table": 1, "slot": a[1], "offset": a[0]}}]


def _create_process(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """create_process(id, routine): a process that plays a table-1 animation on the fighter's
    copy, then ends: an afterimage left where he stands (Rayden's teleport 0x80045854)."""

    routine = (a[1] or 0) & 0xFFFFFFFF
    body = dc.decompile(w.gen.mkt, routine) if routine else []
    anim = next((x for x in _walk_calls(body) if w.name(x) == "animate_table1"), None)
    if w.copy is None or anim is None or None in (anim.args[0].const(), anim.args[1].const()):
        w.unknown(f"0x{c.pc:08X}: process 0x{routine:08X}")
        return []
    w.copy = None
    return [{"op": "afterimage", "anim": {"table": 1, "slot": anim.args[1].const()},
             "rate": anim.args[0].const()}]  # fmt: skip


def _match_opponent(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    w.matched = True
    return []


def _adjust(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """multi_adjust_xy(self, dx, dy) after match_me_to_opponent: the fighter is placed by the
    opponent, facing as the opponent; a negative dx is behind it (Rayden's teleport: -0x43, or
    +0x43 by an arena edge)."""

    obj = c.args[0]
    if isinstance(obj, dc.Load) and obj.off == 0x440 and "proc" in str(obj.base) and None not in a[1:3]:
        w.proj_offset = [a[1], a[2]]  # the projectile object placed by the fighter (Sektor's rockets)
        return []
    if not (w.matched and c.args[0] == dc.SELF):
        w.unknown(f"0x{c.pc:08X}: offset {c.args[1]}")
        return []
    w.matched = False
    v = c.args[1]
    lead = re.search(r"proc\+0x3BC\+0xC\b.*\+ (-?0x[0-9A-F]+)\)", str(v))
    if lead is not None:  # dx = (the opponent's x velocity * 16 ticks) + constant (Sektor: -12)
        w.note(f"MKT adds the opponent's x velocity over 16 ticks to the offset (0x{c.pc:08X}); the host "
               "relocation omits that lead (Sektor's teleport, accepted v08)")  # fmt: skip
        return [{"op": "relocate", "to": "behind_opponent", "dx": abs(int(lead.group(1), 0))}]
    values = v.values if isinstance(v, dc.Phi) else (v.const(),)
    if None in values:
        w.unknown(f"0x{c.pc:08X}: offset {v}")
        return []
    step: dict[str, Any] = {"op": "relocate", "to": "behind_opponent", "dx": max(abs(x) for x in values)}
    if len(values) > 1:
        w.note(f"MKT places him {', '.join(str(x) for x in values)} px from the opponent by the "
               "arena edges (behind unless the opponent is near one)")  # fmt: skip
    return [step]


def _flip(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """flip_single(self): the fighter turns around (Rayden's reversed lightning)."""

    if c.args[0] == dc.SELF:
        return [{"op": "flip"}]
    w.note(f"MKT turns another object around (flip_single {c.args[0]}, 0x{c.pc:08X})")
    return []


def _stamp(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    """stamp_tick(word, self): the tick of this use, which the command's cooldown condition
    reads (the condition names the same word)."""

    if a[0] is None:
        w.unknown(f"0x{c.pc:08X}: stamp {c.args[0]}")
        return []
    return [{"op": "stamp", "key": f"0x{a[0] & 0xFFFFFFFF:08X}"}]


def _object_here(w: _Walk, c: dc.Call, a: list) -> list[dict]:
    w.object_anim = dict(w.pending) if w.pending is not None else None
    return []


# ---- projectiles ---------------------------------------------------------------------------------
# A projectile process (MKT ``proj_process``' child) reads as: its art (get_char_ani / find_part /
# skip_frame; a part played to its end first with mframew is the forming part), close-range
# checks before the flight (a call whose routine steps one frame, sleeps and strike-checks), the
# flight (proj_set_xvel: speed and frame rate; proj_flight: the strike record; process +0x438: a
# per-tick callback, a hum when it plays a sound every n ticks), then the impact (inline or a
# routine: at the opponent when match_me_to_opponent, multi_adjust_xy, its art and rate, its sound
# and effect, follow when it copies the opponent's velocity each tick). The palette is the one
# of the frame the projectile object is created from (a throw helper, token 11, or the selection
# proj_object_here takes).
def projectile(w: _Walk, child: int, fields: dict[tuple[int, int], int]) -> dict[str, Any]:
    gen = w.gen
    stmts = dc.decompile(gen.mkt, child, (), fields)
    _index_calls(stmts)
    flat = _flatten(w, stmts)
    step: dict[str, Any] = {"op": "projectile"}
    art: dict[str, int] | None = None
    checks: list[dict[str, Any]] = []
    flown = False
    sizzle: int | None = None
    rest: list = []
    for i, x in enumerate(flat):
        n = w.name(x) if x.kind == "call" else None
        a = [v.const() for v in x.args] if x.kind == "call" else []
        if flown:
            rest = flat[i:]
            break
        if n == "get_char_ani" and None not in a[:2]:
            art = {"table": a[0], "slot": a[1], "part": 1}
        elif n == "char_ani_part2" and a[0] is not None:
            art = {"table": 0, "slot": a[0], "part": 2}
        elif n == "find_part" and art is not None and a[0] is not None:
            art["part"] = a[0]
        elif n == "skip_frame" and art is not None:
            art["part"] += 1
        elif n == "mframew" and art is not None:
            w.note(f"MKT plays the projectile's part {art['part']} (forming) before the flight; "
                   "the program starts at the flight part")  # fmt: skip
            art["part"] += 1
        elif n == "ft_sound" and a[0] is not None:
            step["sound"] = {"fighter": a[0]}  # played as the projectile starts (Sektor's launch)
        elif x.kind == "if" and w._tested_call(x.cond) == "opponent_reacting":
            speeds = []
            for branch in (x.then, x.other):
                sets = [y for y in branch if y.kind == "call" and w.name(y) == "proj_set_xvel"]
                speeds.append(sets[0].args[1].const() if len(sets) == 1 else None)
                if len(sets) == 1 and sets[0].args[2].const() is not None:
                    step["rate"] = sets[0].args[2].const()
            if None in speeds:
                w.unknown(f"0x{x.pc:08X}: speeds by the opponent's reaction")
            else:
                fast, normal = speeds if "== 0x8000" in str(x.cond) else speeds[::-1]
                step["speed"], step["speed_reacting"] = hex(normal), hex(fast)
        elif n == "opponent_reacting":
            pass  # tested by the branch that follows
        elif n == "proj_set_xvel":
            speed = a[1]
            if speed is None and isinstance(x.args[1], dc.Load) and x.args[1].base == dc.PROC:
                speed = fields.get((x.args[1].off, 4))
            if speed is None:
                w.unknown(f"0x{x.pc:08X}: projectile speed {x.args[1]}")
            else:
                step["speed"] = hex(speed)
            if a[2] is not None:
                step["rate"] = a[2]
        elif n == "proj_flight":
            decoded = gen.strike_index(a[1]) if a[1] is not None else None
            if decoded is None:
                w.unknown(f"0x{x.pc:08X}: projectile strike {x.args[1]}")
            else:
                step["strike"] = decoded
                sizzle = gen.reaction_sound(gen.strike_raw(a[1])[8])
            flown = True
        elif x.kind == "store" and x.base == dc.PROC and x.off == 0x438 and x.value.const():
            for key, value in _callback(w, x.value.const() & 0xFFFFFFFF):
                step[key] = value
        elif x.kind == "call" and x.target and _readable(x.target):
            check = _check(w, x, len(checks) + 1)
            if check is not None:
                checks.append(check)
            else:
                w.unknown(f"0x{x.pc:08X}: call {n} before the flight")
        elif n in ("proj_set_strike",) or x.kind in ("store", "if"):
            pass  # the flight's record decides; per-tick flags and the check-hit impacts
        elif x.kind == "call" and n not in ("proj_delete",):
            w.unknown(f"0x{x.pc:08X}: call {n} in the projectile")
    if art is not None:
        step["art"] = art
    step["offset"] = [0, 0]  # MKT matches the object to the owner's animation point
    if checks:
        step["checks"] = checks
    palette = _object_palette(w, art)
    if palette:
        step["palette"] = hex(palette)
    impact = _impact(w, rest)
    if impact is not None:
        if sizzle is not None and "sound" not in impact:
            impact["sound"] = {"fighter": sizzle}  # MKT's victim reaction plays it
        step["impact"] = impact
    return step


def _readable(target: int) -> bool:
    """A move routine (registry ``move`` kind) or an unnamed one: read it, not a rule."""

    entry = REGISTRY.get(target)
    return entry is None or entry.follow


def _flatten(w: _Walk, stmts: list) -> list:
    """Top-level statements with decided branches inlined (a known argument or field)."""

    out: list = []
    for x in stmts:
        if x.kind == "if" and x.cond.const() is not None:
            out += _flatten(w, x.then if x.cond.const() else x.other)
        elif x.kind != "return":
            out.append(x)
    return out


def _check(w: _Walk, c: dc.Call, after: int) -> dict[str, Any] | None:
    """A close-range check routine: one frame, a sleep, a strike check (its record's box, or the
    box it passes to strike_box_check)."""

    body = dc.decompile(w.gen.mkt, c.target or 0, tuple(v.const() or 0 for v in c.args[:4]))
    calls = [x for x in _walk_calls(body)]
    names = [w.name(x) for x in calls]
    if "do_next_a9_frame" not in names or "process_sleep" not in names:
        return None
    for x in calls:
        n, a = w.name(x), [v.const() for v in x.args]
        if n == "strike_box_check" and None not in a[2:4] and None not in (x.args[4].const(), x.args[5].const()):
            return {"box": [a[2], a[3], x.args[4].const(), x.args[5].const()], "after": after}
        if n == "proj_strike_check" and a[1] is not None:
            decoded = w.gen.strike_index(a[1])
            if decoded is not None:
                return {"box": decoded["box"], "after": after}
    return None


def _walk_calls(stmts: list) -> list:
    out: list = []
    for x in stmts:
        if x.kind == "call":
            out.append(x)
        for key in ("then", "other", "body"):
            out += _walk_calls(getattr(x, key, []) or [])
    return out


def _callback(w: _Walk, callback: int) -> list[tuple[str, Any]]:
    """A flight callback (process +0x438, run each flight tick):

    * ``hum``: it plays a sound each time its counter (process +0x440) runs out;
    * ``wrap``: when the object has left the screen (``proj_offscreen``) it moves it past the
      opposite edge (its x, ``+0x14``), then counts ``cooldown`` ticks and switches itself off
      (process +0x3CC = 0), so the flight deletes the object the next time it leaves (MKT's
      flight keeps an offscreen object while this callback is on: Rayden's reversed lightning,
      ``0x80078070``)."""

    body = dc.decompile(w.gen.mkt, callback)
    for x in body:
        if x.kind == "if":
            sound = next((y for y in x.then if y.kind == "call" and w.name(y) == "ft_sound"), None)
            reset = next((y for y in x.then if y.kind == "store" and y.base == dc.PROC and y.off == 0x440), None)
            if sound is not None and reset is not None and reset.value.const():
                return [("hum", {"sound": {"fighter": sound.args[0].const()}, "every": reset.value.const()})]
    every = _walk_all(body)
    if any(x.kind == "call" and w.name(x) == "proj_offscreen" for x in every) and any(
        x.kind == "store" and x.base == dc.SELF and x.off == 0x14 for x in every
    ):
        cooldown = next((x.value.const() for x in every if x.kind == "store" and x.base == dc.PROC
                         and x.value.const() and x.off != 0x3CC), None)  # fmt: skip
        if cooldown is not None:
            return [("wrap", {"cooldown": cooldown})]
    out: list[tuple[str, Any]] = []
    smoke = next((x for x in every if x.kind == "call" and w.name(x) == "rocket_smoke"), None)
    if smoke is not None:  # MKT's smoke: create_fx(n) every other flight tick (rocket_smoke)
        fx = next((y.args[0].const() for y in _walk_all(dc.decompile(w.gen.mkt, smoke.target))
                   if y.kind == "call" and w.name(y) == "create_fx"), None)  # fmt: skip
        place = smoke.args[0].const()  # its placement index (the effect's process +0x444)
        if fx is not None:
            effect = {"mkt_fx": fx} if place is None else {"mkt_fx": fx, "place": place}
            out.append(("trail", {"effect": effect, "every": 2}))
    text = " ".join(str(getattr(x, "cond", "")) for x in every)
    shift = re.search(r"\+0xC >> (\d+)\)", text)
    cap = re.search(r"< (0x[0-9A-F]+)\)", text)
    if shift is not None and cap is not None and any(x.kind == "call" and w.name(x) == "proj_set_xvel" for x in every):
        # each flight tick v += v >> shift, kept below the cap (Sektor's rocket: 4, 0xB3334)
        out += [("accel_shift", int(shift.group(1))), ("cap", hex(int(cap.group(1), 16) - 1))]
    if out:
        return out
    w.unknown(f"0x{callback:08X}: flight callback")
    return []


def _object_palette(w: _Walk, art: dict[str, int] | None) -> int | None:
    from .lower_projectile import MKT_TABLE1, Donor, donor_helper
    from .script import MKT

    donor = Donor(w.gen.mkt, w.gen.fighter)
    throw = next((s for s in reversed(w.out) if s["op"] == "animate"), None)
    if throw is not None:
        helper = donor_helper(donor, throw["anim"])
        if helper is not None and helper.frames:
            return donor.m32(helper.frames[0] + 0x14)
    anim = w.object_anim
    if anim is None and art is not None:  # the object made from the art's slot (Sektor's rocket:
        anim = art  # slot 0x43's first frame, the vertical rocket, names ROCKET_P 0x800BC3AC)
    if anim is not None:
        p = donor.m32((0 if anim["table"] == 0 else MKT_TABLE1) + 4 * anim["slot"])
        while MKT.is_token(donor.m32(p)):
            p += 4 * (1 + len(MKT.operands[donor.m32(p)]))
        return donor.m32(donor.m32(p) + 0x14) if donor.m32(p) > 1 else None
    return None


def _impact(w: _Walk, rest: list) -> dict[str, Any] | None:
    """The statements after the flight: inline, or a call to the impact routine."""

    calls = [x for x in rest if x.kind == "call"]
    if calls and calls[0].target and _readable(calls[0].target):
        body = dc.decompile(w.gen.mkt, calls[0].target)
        _index_calls(body)
        rest = _flatten(w, body)
    impact: dict[str, Any] = {"at": "projectile", "end": "animation"}
    anim: dict[str, int] | None = None
    for x in _walk_all(rest):
        if x.kind == "store" and x.base == dc.SELF and x.off in (0xC, 0x10):
            v = x.value
            if isinstance(v, dc.Load) and "proc+0x3BC" in str(v.base):
                impact["follow"] = "opponent"  # the opponent's velocity copied each tick
            continue
        if x.kind != "call":
            continue
        n, a = w.name(x), [v.const() for v in x.args]
        if n == "match_me_to_opponent":
            impact["at"] = "opponent"
        elif n == "multi_adjust_xy" and None not in a[1:3]:
            impact["adjust"] = [a[1], a[2]]
        elif n == "get_char_ani" and None not in a[:2]:
            anim = {"table": a[0], "slot": a[1], "part": 1}
        elif n == "char_ani_part2" and a[0] is not None:
            anim = {"table": 0, "slot": a[0], "part": 2}
        elif n == "find_part" and anim is not None and a[0] is not None:
            anim["part"] = a[0]
        elif n == "skip_frame" and anim is not None:
            anim["part"] += 1
        elif n in ("mframew", "init_anirate") and a[0] is not None:
            impact["rate"] = a[0]
        elif n == "ft_sound" and a[0] is not None:
            impact["sound"] = {"fighter": a[0]}
        elif n == "create_fx" and a[0] is not None:
            impact["effect"] = {"mkt_fx": a[0]}
    if anim is None:
        if "effect" in impact:  # a shared MKT effect at the projectile (Sektor's explosion)
            impact["end"] = "effect"
            return impact
        return None
    impact["anim"] = anim
    return impact


def _walk_all(stmts: list) -> list:
    out: list = []
    for x in stmts:
        out.append(x)
        for key in ("then", "other", "body"):
            out += _walk_all(getattr(x, key, []) or [])
    return out


CALL_RULES = {
    "damage_opponent": _damage_opponent,
    "opponent_routine": _opponent_routine,
    "step_frames": _step_frames,
    "opponent_voice": _note_only("MKT's grab plays the victim's voice; the host victim reaction plays its own"),
    "count_grab_hit": _ignore,  # MKT's hit counters (no host equivalent needed)
    "count_grab_miss": _ignore,
    "adjust_opponent": _ignore,  # the victim's moves during a grab: the host victim reaction's
    "match_opponent_to_me": _ignore,
    "opponent_call": _ignore,
    "init_special_face": _begin(True),
    "init_special": _begin(False),
    "begin_special": _begin_special,
    "ft_sound": _sound,
    "get_char_ani": _select,
    "mframew": _to_phase_end,
    "ani_to_phase_end": _to_phase_end,
    "animate_table1": _animate_table1,
    "do_next_a9_frame": _next_frame,
    "towards_x_vel": _velocity,
    "stop_me": _stop,
    "dash_stop": _stop,
    "do_jump": _jump,
    "reaction_exit": _end,
    "process_sleep": _sleep,
    "face_opponent": _face,
    "create_fx": _effect,
    "sans_repell_3": _no_repel,
    "shake_screen": _shake_screen,
    "shake_object": _shake_object,
    "ani_frame_at_t0": _frame_at,
    "proj_process": _projectile,
    "proj_object_here": _object_here,
    "new_object": _new_object,
    "ani_frame_at": _frame_at_t1,
    "create_process": _create_process,
    "match_me_to_opponent": _match_opponent,
    "multi_adjust_xy": _adjust,
    "match_ani_points": _ignore,  # the copy put where the fighter stands
    "bind_palette": _note_only("MKT binds a temporary palette (Rayden: his cyan 0x800B9B04 while "
                               "he reappears); the host keeps the fighter's palette"),
    "palette_back": _ignore,
    "reset_fighter_state": _ignore,
    "proj_object": _ignore,
    "do_special": _dispatch,
    "do_body_propell": _dispatch,
    "do_quick_special": _dispatch,
    "flip_single": _flip,
    "context_jump": _context_jump,
    "randu": _randu,
    "give_routine": _note_only(
        "MKT gives the victim a new routine after the carry (0x8006D3B4); the host victim reaction "
        "is the stand-in"
    ),
    "get_his_char_ani": _ignore,  # the victim's pose (the reaction's)
    "is_airborne": _ignore,
    "opponent_unsettled": _ignore,
    "strike_check_a0": _ignore,  # outside a window: handled by loops
    "stamp_tick": _stamp,
    "link_object": _ignore,
    "find_last_frame": _last_frame,
    "init_anirate": _anirate,
    "next_anirate": _ignore,  # in a motion loop: the animate step's rate
    "teleport_strike_check": _ignore,  # read by its loop or jump (motion_loop, _kept_jump)
    "teleport_land": _follow,
    "triple_sound": _note_only("MKT's landing thud (triple_sound 0x18): the host's own landing sound "
                               "plays (owner, Sektor teleport v10)"),
    "land_reset": _ignore,  # the host's end of the move resets the fighter
    "proc_flag1": _ignore,  # tested by its branch
    "opponent_reacting": _ignore,  # tested by its branch
    "rzap3": _follow,
    "make_rocket": _follow,
    "robo_chest_open": _follow,
    "robo_chest_close": _follow,
    "ani_backward": _backward,
    "proj_recover": _note_only("MKT sets action 0x604 for the recovery after a projectile; the program "
                               "keeps the begin's"),
}


# ---- comparison --------------------------------------------------------------------------------
_KEYS = ("anim", "rate", "until", "ticks", "count", "x", "y", "gravity", "sound", "strike",
         "only_if", "dx", "dy", "effect", "action_mkt", "amplitude", "face", "stop",
         "art", "offset", "speed", "checks", "palette", "impact", "hum")  # fmt: skip
_NESTED = ("steps", "every_tick", "on_hit", "on_block")


def canonical(steps: list[dict]) -> list[str]:
    """One line per step (nested steps indented), values normalized, provenance dropped."""

    def norm(v: Any) -> Any:
        if isinstance(v, str):
            try:
                return int(v, 0)
            except ValueError:
                return v
        if isinstance(v, dict):
            return {k: norm(x) for k, x in sorted(v.items())}
        if isinstance(v, list):
            return [norm(x) for x in v]
        return v

    out: list[str] = []

    def walk(ss: list[dict], ind: str) -> None:
        for s in ss:
            p = {k: norm(s[k]) for k in _KEYS if k in s}
            out.append(f"{ind}{s['op']} {json.dumps(p, sort_keys=True, separators=(',', ':'))}")
            for k in _NESTED:
                if k in s:
                    out.append(f"{ind}  [{k}]")
                    walk(s[k], ind + "    ")

    walk(steps, "")
    return out


def compare(generated: list[dict], accepted: list[dict]) -> list[str]:
    """A unified diff (accepted -> generated) of the canonical forms; empty when equal."""

    import difflib

    a, b = canonical(accepted), canonical(generated)
    return list(difflib.unified_diff(a, b, "accepted", "generated", lineterm="", n=1))
