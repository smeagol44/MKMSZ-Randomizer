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
from dataclasses import dataclass, field
from typing import Any

from . import decompile as dc
from . import reading
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
    0x71: "knockback_arc",  # Reptile's forceballs
    0x72: "acid_stagger",  # Reptile's acid
    0x74: "elbow_hold",  # Reptile's elbow first contact
    0x7F: "launch",  # Rayden's torpedo victim (the carry is the attacker's): stand-in
    0x80: "shock_stagger",  # Rayden's lightning: stagger back, cyan blink (0x800539A8)
}


@dataclass
class Generated:
    entry: int
    steps: list[dict[str, Any]]
    notes: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)


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
        table = rec.base.base
        if not (isinstance(table, dc.Bin) and table.op == "+" and table.a.const() is not None
                and table.a.const() & 0xFFFFFFFF == STRIKE_TABLE):  # fmt: skip
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
            if s.kind == "loop":
                count = self._count(stmts[:i], s)
                if count is not None:
                    out += self.loop(s, count, out)
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
                step.clear()
                step.update(refilled)
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
        return []  # other process/object fields: not modelled (flags, timers, links)

    def branch(self, s: dc.If) -> list[dict]:
        c = s.cond.const()
        if c is not None:  # decided by a known argument
            return self.stmts(s.then if c else s.other)
        if any(f"[0x{p:08X}]" in str(s.cond) for p in PLAYER_OBJECTS) and "self" in str(s.cond):
            # which player the fighter is (per-player tables, e.g. the torpedo's velocity source):
            # bookkeeping; both arms do the same for their player
            return self.stmts(s.then)
        call = self._tested_call(s.cond)
        if call == "is_airborne":
            self.note("MKT runs part of the move only when airborne (is_airborne); the program "
                      "runs it always (on the ground the drop ends at once)")  # fmt: skip
            return self.stmts(s.then)
        self.unknown(f"0x{s.pc:08X}: branch on {s.cond}")
        return self.stmts(s.then)

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
            return rule(self, c, a)
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
        if self.offset:
            anim["offset"] = self.offset
        self.pending, self.offset = None, 0
        return [{"op": "pose", "anim": anim}]

    # -- loops ------------------------------------------------------------------------------------
    @staticmethod
    def _count(before: list, loop: dc.Loop) -> int | None:
        """The loop's count: the constant stored to the process field its condition counts down,
        among the stores just before it."""

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
        strike = self._find_strike(body)
        if strike is not None:
            return [self.window(body, strike, count)]
        if self._carry(body):
            self.note("MKT's carry shares one velocity between the fighters and ends when either "
                      "stops (a wall); the host keeps the victim at its contact distance")  # fmt: skip
            return [{"op": "carry", "ticks": count, "every_tick": [{"op": "pass_through", "ticks": 1}]}]
        steps = self.stmts(body)
        return [{"op": "repeat", "count": count, "steps": steps}]

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
    if None in (x, y, g):
        w.unknown(f"0x{c.pc:08X}: jump {c.args}")
        return []
    rate = c.args[4].const()
    step: dict[str, Any] = {"op": "jump", "x": hex(x), "y": hex(y), "gravity": hex(g), "until": "landing"}
    if rate is not None and 0 < rate < 0x100:  # do_jump animates the selection at this rate
        step["rate"] = rate
    return w.show_pending() + [step]


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
            hum = _hum(w, x.value.const() & 0xFFFFFFFF)
            if hum is not None:
                step["hum"] = hum
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


def _hum(w: _Walk, callback: int) -> dict[str, Any] | None:
    """A flight callback that plays a sound each time its counter (process +0x440) runs out."""

    body = dc.decompile(w.gen.mkt, callback)
    for x in body:
        if x.kind == "if":
            sound = next((y for y in x.then if y.kind == "call" and w.name(y) == "ft_sound"), None)
            reset = next((y for y in x.then if y.kind == "store" and y.base == dc.PROC and y.off == 0x440), None)
            if sound is not None and reset is not None and reset.value.const():
                return {"sound": {"fighter": sound.args[0].const()}, "every": reset.value.const()}
    w.unknown(f"0x{callback:08X}: flight callback")
    return None


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
    "proj_object": _ignore,
    "do_special": _dispatch,
    "do_body_propell": _dispatch,
    "do_quick_special": _dispatch,
    "flip_single": _note_only("MKT turns the fighter around (flip_single) at the start"),
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
}


# ---- comparison --------------------------------------------------------------------------------
_KEYS = ("anim", "rate", "until", "ticks", "count", "x", "y", "gravity", "sound", "strike",
         "only_if", "dx", "dy", "effect", "action_mkt", "amplitude",
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
