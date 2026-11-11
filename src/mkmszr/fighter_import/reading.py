"""Reading aid for MKT special moves (Fighter recompiler plan, milestone 3).

From a command record's action routine, :func:`read` disassembles the donor routine, follows
constants into call arguments and global accesses, names MKT engine routines from
:mod:`.mkt_registry`, and flags every call it cannot name. :func:`call_tree` walks unknown
callees to a depth. A person (normally the assistant) writes the move program from the report;
nothing here guesses semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .mipsdis import REGS, Insn, decode
from .mkt_fighter import CommandRecord, Handler, InlineCommand, MktRom
from .mkt_registry import REGISTRY

VA_BASE = 0x80000000
CODE_END = 0x800A0000
CALLER_SAVED = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 31}


@dataclass
class Call:
    pc: int
    target: int | None  # None: computed (jalr)
    args: tuple[int | None, ...]  # a0..a3 when constant
    name: str | None


@dataclass
class Reading:
    entry: int
    insns: list[Insn]
    calls: list[Call]
    globals: dict[int, list[int]]  # constant address -> pcs that access it
    notes: dict[int, str] = field(default_factory=dict)
    code_refs: set[int] = field(
        default_factory=set
    )  # routine addresses passed as arguments or stored

    @property
    def unknown_calls(self) -> list[Call]:
        return [c for c in self.calls if c.name is None]

    def text(self) -> str:
        lines = [
            f"routine 0x{self.entry:08X}"
            + (f" ({REGISTRY[self.entry].name})" if self.entry in REGISTRY else "")
        ]
        for ins in self.insns:
            note = self.notes.get(ins.pc, "")
            lines.append(
                f"  {ins.pc:08X}: {ins.word:08X}  {ins.text}" + (f"   ; {note}" if note else "")
            )
        return "\n".join(lines)


def _word(mkt: bytes, va: int) -> int:
    o = va - VA_BASE
    return int.from_bytes(mkt[o : o + 4], "big")


def extent(mkt: bytes, entry: int, limit: int = 4000) -> list[Insn]:
    """Instructions of the routine at ``entry``: up to the ``jr ra`` (or tail ``j``) after which no
    forward branch of the routine lands."""

    out: list[Insn] = []
    furthest = entry
    pc = entry
    while len(out) < limit:
        ins = decode(_word(mkt, pc), pc)
        out.append(ins)
        if (
            ins.target is not None
            and ins.op not in ("jal",)
            and entry <= ins.target < entry + 4 * limit
        ):
            furthest = max(furthest, ins.target)
        if ins.is_return or (ins.op == "j" and not entry <= (ins.target or 0) < entry + 4 * limit):
            delay = decode(_word(mkt, pc + 4), pc + 4)
            out.append(delay)
            if pc + 8 > furthest:
                return out
            pc += 8
            continue
        pc += 4
    raise ValueError(f"routine 0x{entry:08X} longer than {limit} instructions")


def _execute(regs: dict[int, int], ins: Insn) -> None:
    """Constant propagation for one instruction (unknown results drop the register)."""

    def setr(r: int, v: int | None) -> None:
        if r == 0:
            return
        if v is None:
            regs.pop(r, None)
        else:
            regs[r] = v & 0xFFFFFFFF

    def get(r: int) -> int | None:
        return 0 if r == 0 else regs.get(r)

    op = ins.op
    if op == "lui":
        setr(ins.rt, ins.imm << 16)
    elif op in ("addiu", "addi", "daddiu"):
        base = get(ins.rs)
        setr(ins.rt, None if base is None else base + ins.imm)
    elif op == "ori":
        base = get(ins.rs)
        setr(ins.rt, None if base is None else base | ins.imm)
    elif op in ("addu", "or", "daddu") and (ins.rt == 0 or ins.rs == 0):
        setr(ins.rd, get(ins.rs if ins.rt == 0 else ins.rt))
    elif op in ("addu", "daddu"):
        a, b = get(ins.rs), get(ins.rt)
        setr(ins.rd, None if a is None or b is None else a + b)
    elif op in ("sll",) and ins.word:
        v = get(ins.rt)
        setr(ins.rd, None if v is None else v << ins.imm)
    elif op in ("lb", "lh", "lw", "lbu", "lhu", "lwu", "ld", "lwl", "lwr"):
        setr(ins.rt, None)
    elif op in ("jal", "jalr"):
        for r in CALLER_SAVED:
            regs.pop(r, None)
    elif op in ("mfhi", "mflo", "mfc1", "dmfc1", "mfc0", "cfc1") or (
        op
        in ("slt", "sltu", "and", "xor", "nor", "subu", "sub", "srl", "sra", "sllv", "srlv", "srav")
        and ins.rd
    ):
        setr(ins.rd if op not in ("mfc1", "dmfc1", "mfc0", "cfc1") else ins.rt, None)
    elif op in ("slti", "sltiu", "andi", "xori"):
        setr(ins.rt, None)


_LIKELY = ("beql", "bnel", "blezl", "bgtzl", "bltzl", "bgezl", "bc1fl", "bc1tl")
_MEMOPS = (
    "lb",
    "lh",
    "lw",
    "lbu",
    "lhu",
    "lwu",
    "sb",
    "sh",
    "sw",
    "lwc1",
    "swc1",
    "ld",
    "sd",
    "ldc1",
    "sdc1",
)
# Engine dispatchers whose a0 indexes a routine table: address -> (table, entries, kind).
DISPATCHERS = {
    0x80076F70: (0x800AB140, 56, "special"),  # do_special: context_jump
    0x80045050: (0x800A80D0, 40, "propell"),  # do_body_propell: context_jump
    0x80072020: (0x800AAF00, 32, "quick"),  # do_quick_special: call, then reaction_exit
}


def _unconditional(ins: Insn) -> bool:
    return ins.op in ("j", "jr") or (ins.op == "beq" and ins.rs == 0 and ins.rt == 0)


def _edges(insns: list[Insn]) -> tuple[dict[int, list[tuple[int, int, bool]]], set[int]]:
    """Control-flow edges between instruction indices: ``succ[i] = [(j, via, call)]`` where the
    state flowing to ``j`` is the out-state of ``via`` (``call`` clobbers caller-saved registers).
    Also returns the indices that are delay slots of calls (folded into the call)."""

    index = {ins.pc: k for k, ins in enumerate(insns)}
    succ: dict[int, list[tuple[int, int, bool]]] = {k: [] for k in range(len(insns))}
    call_delays: set[int] = set()
    k = 0
    while k < len(insns):
        ins = insns[k]
        if ins.is_call and k + 1 < len(insns):
            call_delays.add(k + 1)
            if k + 2 < len(insns):
                succ[k].append((k + 2, k, True))
            k += 2
            continue
        if (ins.target is not None or ins.op == "jr") and k + 1 < len(insns):
            target = index.get(ins.target) if ins.target is not None else None
            likely = ins.op in _LIKELY
            succ[k].append((k + 1, k, False))  # delay slot (only on the taken path when likely)
            if target is not None:
                succ[k + 1].append((target, k + 1, False))
            if not _unconditional(ins) and k + 2 < len(insns):
                if likely:
                    succ[k].append((k + 2, k, False))
                else:
                    succ[k + 1].append((k + 2, k + 1, False))
            k += 2
            continue
        if k + 1 < len(insns):
            succ[k].append((k + 1, k, False))
        k += 1
    return succ, call_delays


def _states(insns: list[Insn]) -> tuple[list[dict[int, int] | None], set[int]]:
    """In-state (known constant registers) of every instruction, by forward dataflow with
    intersection at merges. ``None`` marks code reached only through computed jumps."""

    succ, call_delays = _edges(insns)
    n = len(insns)
    state_in: list[dict[int, int] | None] = [None] * n
    state_in[0] = {}
    work = [0]
    while work:
        k = work.pop()
        regs = dict(state_in[k] or {})
        if insns[k].is_call and k + 1 in call_delays:
            _execute(regs, insns[k + 1])
            state_in[k + 1] = dict(state_in[k] or {})
        _execute(regs, insns[k])
        for j, via, _call in succ[k]:
            out = regs if via == k else None
            if out is None:
                continue
            merged = (
                dict(out)
                if state_in[j] is None
                else {r: v for r, v in (state_in[j] or {}).items() if out.get(r) == v}
            )
            if state_in[j] != merged:
                state_in[j] = merged
                work.append(j)
    return state_in, call_delays


def resolve(mkt: bytes, dispatcher: int, index: int) -> int | None:
    """Routine a dispatcher reaches for a constant index (None: out of range or empty entry)."""

    table, count, _kind = DISPATCHERS[dispatcher]
    if not 0 <= index < count:
        return None
    return _word(mkt, table + 4 * index) or None


CODE_START = 0x80000400


def _is_code(value: int | None) -> bool:
    return value is not None and CODE_START <= value < CODE_END and value % 4 == 0


def read(mkt: bytes, entry: int) -> Reading:
    insns = extent(mkt, entry)
    state_in, call_delays = _states(insns)
    calls: list[Call] = []
    globs: dict[int, list[int]] = {}
    notes: dict[int, str] = {}
    refs: set[int] = set()
    for k, ins in enumerate(insns):
        regs = dict(state_in[k] or {})
        if ins.is_call:
            if k + 1 in call_delays:
                _execute(regs, insns[k + 1])
            args = tuple(regs.get(r) for r in (4, 5, 6, 7))
            refs.update(a for a in args if a is not None and _is_code(a) and a not in DISPATCHERS)
            target = ins.target if ins.op == "jal" else regs.get(ins.rs)
            name = REGISTRY[target].name if target in REGISTRY else None
            calls.append(Call(ins.pc, target, args, name))
            shown = ", ".join(
                f"{REGS[4 + i]}=" + ("?" if a is None else f"0x{a:X}") for i, a in enumerate(args)
            )
            note = (
                f"{name or 'UNKNOWN'}({shown})"
                if target is not None
                else f"computed call ({shown})"
            )
            if target in DISPATCHERS and args[0] is not None:
                routine = resolve(mkt, target, args[0])
                if routine is not None:
                    note += f" -> {DISPATCHERS[target][2]} 0x{args[0]:X} = 0x{routine:08X}" + (
                        f" ({REGISTRY[routine].name})" if routine in REGISTRY else ""
                    )
            notes[ins.pc] = note
            continue
        if ins.op == "sw" and _is_code(regs.get(ins.rt)):
            refs.add(regs[ins.rt])
            notes[ins.pc] = f"stores routine 0x{regs[ins.rt]:08X}" + (
                f" ({REGISTRY[regs[ins.rt]].name})" if regs[ins.rt] in REGISTRY else ""
            )
        if ins.op in _MEMOPS and ins.rs in regs:
            address = (regs[ins.rs] + ins.imm) & 0xFFFFFFFF
            globs.setdefault(address, []).append(ins.pc)
            name = REGISTRY[address].name if address in REGISTRY else None
            notes[ins.pc] = f"global 0x{address:08X}" + (f" ({name})" if name else "")
    return Reading(entry, insns, calls, globs, notes, refs)


def callees(mkt: bytes, reading: Reading) -> list[int]:
    """Routines a reading can transfer to: direct calls, resolved dispatcher entries and routine
    addresses it passes as arguments or stores (child processes, callbacks)."""

    out = sorted(reading.code_refs)
    for c in reading.calls:
        if c.target is None:
            continue
        out.append(c.target)
        if c.target in DISPATCHERS and c.args[0] is not None:
            routine = resolve(mkt, c.target, c.args[0])
            if routine is not None:
                out.append(routine)
    return out


def call_tree(mkt: bytes, entry: int, depth: int = 2) -> dict[int, Reading]:
    """Readings of ``entry`` and its callees not yet in the registry, down to ``depth``."""

    out: dict[int, Reading] = {}
    frontier = [(entry, 0)]
    while frontier:
        va, d = frontier.pop()
        if va in out or not VA_BASE <= va < CODE_END:
            continue
        reading = read(mkt, va)
        out[va] = reading
        if d < depth:
            frontier += [
                (t, d + 1) for t in callees(mkt, reading) if t not in REGISTRY or REGISTRY[t].follow
            ]
    return out


ROSTER = 26  # MKT fighter ids 0..25 (26..30 are not fighters)


@dataclass
class MoveReading:
    """One command of a fighter: where it is matched and what it runs."""

    grid: str
    event: int
    masks: tuple[int, ...]
    right: tuple[int, ...]
    condition: int | None
    action: int
    selector: int | None
    users: tuple[int, ...]  # fighters whose handlers carry the same action
    tree: dict[int, Reading]

    @property
    def shared(self) -> bool:
        """A roster-wide command (finishers and similar), not a fighter's special."""

        return len(self.users) > ROSTER // 2

    @property
    def unknown_calls(self) -> list[tuple[int, Call]]:
        return [(va, c) for va, r in self.tree.items() for c in r.unknown_calls]


def _actions(rom: MktRom, fighter: int) -> list[tuple[Handler, CommandRecord | InlineCommand, int]]:
    out: list[tuple[Handler, CommandRecord | InlineCommand, int]] = []
    for h in rom.handlers(fighter):
        for r in h.records:
            out.append((h, r, r.action))
        for c in h.inline:
            action = c.target if c.target is not None else (c.dispatch or 0)
            if action in DISPATCHERS and c.argument is not None:
                action = resolve(rom.rom, action, c.argument) or action
            out.append((h, c, action))
    return out


def fighter_moves(mkt: bytes, fighter: int, depth: int = 6) -> list[MoveReading]:
    """Readings of every command a fighter's event handlers match (records and inline commands).
    Roster-wide commands are listed without a reading tree."""

    rom = MktRom(mkt)
    users: dict[int, set[int]] = {}
    for f in range(ROSTER):
        for _h, _c, action in _actions(rom, f):
            users.setdefault(action, set()).add(f)
    out: list[MoveReading] = []
    for h, c, action in _actions(rom, fighter):
        masks: tuple[int, ...]
        if isinstance(c, CommandRecord):
            masks, condition, selector = c.masks, c.condition or None, c.selector
        else:
            masks, condition, selector = (c.mask,), None, None
        move = MoveReading(
            h.grid,
            h.event,
            masks,
            c.right,
            condition,
            action,
            selector,
            tuple(sorted(users[action])),
            {},
        )
        if not move.shared:
            move.tree = call_tree(mkt, action, depth)
            if condition:
                move.tree.update(call_tree(mkt, condition, 1))
        out.append(move)
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Annotated readings of MKT routines (fighter recompiler, M3)"
    )
    parser.add_argument("--mkt-rom", required=True, type=Path)
    parser.add_argument("--fighter", type=int, help="read every command of this MKT fighter id")
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("routines", nargs="*", help="routine addresses (hex)")
    args = parser.parse_args(argv)
    mkt = args.mkt_rom.read_bytes()
    if args.fighter is not None:
        for m in fighter_moves(mkt, args.fighter, args.depth):
            print(
                f"== {m.grid} {m.event} masks {m.masks} right {m.right} selector {m.selector} "
                f"condition {m.condition and hex(m.condition)} action 0x{m.action:08X}"
                + (f" (shared by {len(m.users)} fighters, not read)" if m.shared else "")
            )
            for reading in m.tree.values():
                print(reading.text())
            for va, c in m.unknown_calls:
                print(
                    f"UNKNOWN call at 0x{c.pc:08X} (in 0x{va:08X}) to "
                    + ("computed" if c.target is None else f"0x{c.target:08X}")
                )
    for routine in args.routines:
        print(read(mkt, int(routine, 16)).text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
