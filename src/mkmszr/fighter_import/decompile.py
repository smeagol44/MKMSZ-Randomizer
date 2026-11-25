"""Structured decompiler for donor move routines (generator, owner decision 2026-11-25).

The generator (:mod:`.generate`) writes move programs from MKT's own special-move code instead of
a person reading the disassembly. This module is its first half: it turns one routine into a
small structured IR (calls with symbolic arguments, stores, if/else, do-while loops) that the
second half maps to components.

Values are symbolic. A register holds a constant, a load from a symbolic address
(``proc`` = the current process ``*0x8014C31C``; ``proc+0x418`` = its fighter object), the
result of an earlier call, or an arithmetic combination; anything else is ``?``. The routine is
compiled code (IDO): forward branches nest as if/else, backward branches close do-while loops.
Delay slots are honoured (a branch-likely's delay slot belongs to its taken path). Code that does
not fit the shapes is not guessed: it becomes an ``unstructured`` statement, and the generator
reports it.

Approximations (documented, checked by the golden comparison in :mod:`.generate`): memory written
in the routine is remembered across calls; registers a loop writes are unknown inside and after
it; at a join, a register keeps its value only if both paths agree.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .mipsdis import REGS, Insn, decode

CURRENT_PROCESS = 0x8014C31C  # MKT current process pointer (Wiki MKT-Adapter-Primitives)
CALLER_SAVED = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 31})
VA_BASE = 0x80000000


# ---- values -------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Value:
    def const(self) -> int | None:
        return None


@dataclass(frozen=True)
class Const(Value):
    v: int

    def const(self) -> int | None:
        return self.v

    def __str__(self) -> str:
        if -10 < self.v < 10:
            return str(self.v)
        if self.v < -0x10000:  # an address or a large mask: unsigned
            return f"0x{self.v & 0xFFFFFFFF:X}"
        return f"-0x{-self.v:X}" if self.v < 0 else f"0x{self.v:X}"


@dataclass(frozen=True)
class Unknown(Value):
    def __str__(self) -> str:
        return "?"


@dataclass(frozen=True)
class Load(Value):
    base: Value
    off: int
    width: int = 4
    signed: bool = True

    def __str__(self) -> str:
        if isinstance(self.base, Const) and self.base.v & 0xFFFFFFFF == CURRENT_PROCESS and self.off == 0:
            return "proc"
        if self == SELF:
            return "self"
        if isinstance(self.base, Const) and self.off == 0:
            return f"[0x{self.base.v & 0xFFFFFFFF:08X}]" + ("" if self.width == 4 else f":{self.width}")
        b = str(self.base)
        return f"{b}+0x{self.off:X}" if self.width == 4 else f"{b}+0x{self.off:X}:{self.width}"


@dataclass(frozen=True)
class Result(Value):
    call: int  # pc of the call

    def __str__(self) -> str:
        return f"r{self.call:08X}"


@dataclass(frozen=True)
class Bin(Value):
    op: str
    a: Value
    b: Value

    def __str__(self) -> str:
        return f"({self.a} {self.op} {self.b})"


UNKNOWN = Unknown()
PROC = Load(Const(CURRENT_PROCESS - 0x100000000), 0)
SELF = Load(PROC, 0x418)  # the current fighter's object


def _fold(op: str, a: Value, b: Value) -> Value:
    x, y = a.const(), b.const()
    if x is not None and y is not None:
        f = {
            "+": lambda: x + y,
            "-": lambda: x - y,
            "|": lambda: x | y,
            "&": lambda: x & y,
            "^": lambda: x ^ y,
            "<<": lambda: x << y,
            ">>": lambda: x >> y,
        }.get(op)
        if f is not None:
            return Const(_s32(f()))
    if op in ("+", "|", "^", "-") and y == 0:
        return a
    if op in ("+", "|", "^") and x == 0:
        return b
    if isinstance(a, Unknown) or isinstance(b, Unknown):
        return UNKNOWN
    return Bin(op, a, b)


def _s32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


# ---- statements ---------------------------------------------------------------------------------
@dataclass
class Call:
    pc: int
    target: int | None
    args: list[Value]  # a0..a3, then stack words sp+0x10, sp+0x14
    kind: str = "call"


@dataclass
class Store:
    pc: int
    base: Value
    off: int
    width: int
    value: Value
    kind: str = "store"

    @property
    def address(self) -> str:
        return str(Load(self.base, self.off, self.width))


@dataclass
class If:
    pc: int
    cond: Value  # the then-block runs when it is true (non-zero)
    then: list = field(default_factory=list)
    other: list = field(default_factory=list)
    kind: str = "if"


@dataclass
class Loop:
    pc: int
    body: list
    cond: Value  # do { body } while (cond)
    kind: str = "loop"


@dataclass
class Return:
    pc: int
    kind: str = "return"


@dataclass
class Break:
    pc: int
    target: int  # leaves the enclosing region (a loop exit)
    kind: str = "break"


@dataclass
class Unstructured:
    pc: int
    why: str
    kind: str = "unstructured"


# ---- machine state -------------------------------------------------------------------------------
@dataclass
class State:
    regs: dict[int, Value]
    mem: dict[tuple[str, int, int], Value]
    stack: dict[int, Value]

    def copy(self) -> State:
        return State(dict(self.regs), dict(self.mem), dict(self.stack))

    def get(self, r: int) -> Value:
        return Const(0) if r == 0 else self.regs.get(r, UNKNOWN)

    def set(self, r: int, v: Value) -> None:
        if r:
            self.regs[r] = v


def _merge(a: State, b: State) -> State:
    regs = {r: v for r, v in a.regs.items() if b.regs.get(r) == v}
    mem = {k: v for k, v in a.mem.items() if b.mem.get(k) == v}
    stack = {k: v for k, v in a.stack.items() if b.stack.get(k) == v}
    return State(regs, mem, stack)


# ---- the decompiler -------------------------------------------------------------------------------
class Decompiler:
    def __init__(self, rom: bytes, entry: int, end: int) -> None:
        self.rom, self.entry, self.end = rom, entry, end
        self.insns = {pc: decode(self.word(pc), pc) for pc in range(entry, end, 4)}
        self.back: dict[int, int] = {}  # loop head -> its closing branch (the last one)
        for pc, ins in self.insns.items():
            if ins.is_branch and ins.target is not None and ins.target <= pc:
                self.back[ins.target] = max(self.back.get(ins.target, 0), pc)

    def word(self, va: int) -> int:
        o = va - VA_BASE
        return int.from_bytes(self.rom[o : o + 4], "big")

    # -- one instruction ------------------------------------------------------------------------
    def step(self, ins: Insn, st: State, out: list) -> None:
        op, rs, rt, rd, imm = ins.op, ins.rs, ins.rt, ins.rd, ins.imm
        g = st.get
        if op == "lui":
            st.set(rt, Const(_s32(imm << 16)))
        elif op in ("addiu", "addi", "daddiu"):
            st.set(rt, _fold("+", g(rs), Const(imm)))
        elif op == "ori":
            st.set(rt, _fold("|", g(rs), Const(imm & 0xFFFF)))
        elif op == "andi":
            st.set(rt, _fold("&", g(rs), Const(imm & 0xFFFF)))
        elif op == "xori":
            st.set(rt, _fold("^", g(rs), Const(imm & 0xFFFF)))
        elif op in ("slti", "sltiu"):
            st.set(rt, Bin("<", g(rs), Const(imm)))
        elif op in ("addu", "add", "daddu"):
            st.set(rd, _fold("+", g(rs), g(rt)))
        elif op in ("subu", "sub", "dsubu"):
            st.set(rd, _fold("-", g(rs), g(rt)))
        elif op == "or":
            st.set(rd, _fold("|", g(rs), g(rt)))
        elif op == "and":
            st.set(rd, _fold("&", g(rs), g(rt)))
        elif op == "xor":
            st.set(rd, _fold("^", g(rs), g(rt)))
        elif op in ("slt", "sltu"):
            st.set(rd, Bin("<", g(rs), g(rt)))
        elif op == "sll":
            st.set(rd, _fold("<<", g(rt), Const(ins.word >> 6 & 31)))
        elif op in ("sra", "srl"):
            st.set(rd, _fold(">>", g(rt), Const(ins.word >> 6 & 31)))
        elif op in ("lw", "lh", "lhu", "lb", "lbu"):
            width = {"lw": 4, "lh": 2, "lhu": 2, "lb": 1, "lbu": 1}[op]
            base = g(rs)
            if rs == 29:
                word = st.stack.get(imm & ~3, UNKNOWN)
                c = word.const()
                if width == 4:
                    st.set(rt, word)
                elif c is not None:  # part of a stored constant (big-endian)
                    shift = 8 * (4 - width - (imm & 3))
                    part = (c >> shift) & ((1 << 8 * width) - 1)
                    if op in ("lh", "lb") and part >> (8 * width - 1):
                        part -= 1 << 8 * width
                    st.set(rt, Const(part))
                else:
                    st.set(rt, UNKNOWN)
            else:
                if base.const() is not None:
                    base, imm = Const(_s32(base.const() + imm)), 0
                key = (str(base), imm, width)
                st.set(rt, st.mem.get(key, Load(base, imm, width, op in ("lw", "lh", "lb"))))
        elif op in ("sw", "sh", "sb"):
            width = {"sw": 4, "sh": 2, "sb": 1}[op]
            if rs == 29:
                st.stack[imm] = g(rt)
            else:
                base = g(rs)
                if base.const() is not None:
                    base, imm = Const(_s32(base.const() + imm)), 0
                st.mem[(str(base), imm, width)] = g(rt)
                out.append(Store(ins.pc, base, imm, width, g(rt)))
        elif op == "mflo" or op == "mfhi":
            st.set(rd, UNKNOWN)
        elif op in ("mult", "multu", "div", "divu", "nop", "sync", "cache"):
            pass
        elif op.endswith("c1") or op.startswith(("mtc", "mfc", "cvt", "trunc")):
            if op in ("mfc1",):
                st.set(rt, UNKNOWN)
        elif op == "jr" or ins.is_branch or op in ("jal", "jalr", "j"):
            pass  # handled by the structurer
        else:
            for r in (rt, rd):
                st.set(r, UNKNOWN)

    def call(self, ins: Insn, st: State, out: list) -> None:
        target = ins.target if ins.op == "jal" else None
        args = [st.get(r) for r in (4, 5, 6, 7)] + [st.stack.get(o, UNKNOWN) for o in (0x10, 0x14)]
        out.append(Call(ins.pc, target, args))
        for r in CALLER_SAVED:
            st.regs.pop(r, None)
        st.set(2, Result(ins.pc))

    def cond(self, ins: Insn, st: State) -> Value:
        """True when the branch is taken."""

        a, b = st.get(ins.rs), st.get(ins.rt)
        if a.const() is not None and b.const() is not None:  # decided: a constant condition
            x, y = a.const(), b.const()
            taken = {"beq": x == y, "bne": x != y, "blez": x <= 0, "bgtz": x > 0, "bltz": x < 0,
                     "bgez": x >= 0}.get(ins.op.rstrip("l") if ins.op.endswith("l") else ins.op)  # fmt: skip
            if taken is not None:
                return Const(int(taken))
        base = ins.op.rstrip("l") if ins.op.endswith("l") and ins.op not in ("bltzal",) else ins.op
        if base in ("beq",):
            return Bin("==", a, b)
        if base in ("bne",):
            return Bin("!=", a, b)
        return Bin({"blez": "<=0", "bgtz": ">0", "bltz": "<0", "bgez": ">=0"}.get(base, base), a, Const(0))

    @staticmethod
    def negate(v: Value) -> Value:
        if isinstance(v, Const):
            return Const(int(not v.v))
        if isinstance(v, Bin):
            flip = {"==": "!=", "!=": "==", "<=0": ">0", ">0": "<=0", "<0": ">=0", ">=0": "<0"}
            if v.op in flip:
                return Bin(flip[v.op], v.a, v.b)
        return Bin("!", v, Const(0))

    # -- regions --------------------------------------------------------------------------------
    def block(self, pc: int, end: int, st: State) -> tuple[list, State, bool]:
        """Statements of [pc, end); returns (statements, state, falls through)."""

        out: list = []
        while pc < end:
            if pc in self.back and self.back[pc] < end and self.back[pc] >= pc:
                close = self.back[pc]
                ins = self.insns[close]
                inner = st.copy()
                written = self._written(pc, close + 8)
                for r in written:
                    inner.regs.pop(r, None)
                inner.mem.clear()  # memory the loop writes is not known inside it
                body, inner, _ = self.block(pc, close, inner, ) if close > pc else ([], inner, True)
                cond = self.cond(ins, inner)
                delay = self.insns[close + 4]
                tail: list = []
                self.step(delay, inner, tail)
                out.append(Loop(pc, body + tail, cond))
                st = inner
                for r in written:
                    st.regs.pop(r, None)
                st.mem.clear()
                pc = close + 8
                continue
            ins = self.insns[pc]
            if ins.is_call:
                self.step(self.insns[pc + 4], st, out)  # delay slot first: argument setup
                self.call(ins, st, out)
                pc += 8
                continue
            if ins.is_return:
                self.step(self.insns[pc + 4], st, out)
                out.append(Return(pc))
                return out, st, False
            if ins.op == "j" or (ins.is_branch and ins.op == "beq" and ins.rs == 0 and ins.rt == 0):
                out.append(Unstructured(pc, f"jump to 0x{ins.target:08X}"))
                return out, st, False
            if ins.is_branch:
                t = ins.target or 0
                if t <= pc or t > self.end:
                    out.append(Unstructured(pc, f"branch to 0x{t:08X}"))
                    return out, st, False
                cond = self.cond(ins, st)
                if t > end:  # out of this region: a loop exit
                    likely = ins.op.endswith("l") and ins.op not in ("bltzal", "bgezal")
                    exit_: list = []
                    if likely:
                        self.step(self.insns[pc + 4], st.copy(), exit_)
                    else:
                        self.step(self.insns[pc + 4], st, out)
                    out.append(If(pc, cond, exit_ + [Break(pc, t)], []))
                    pc += 8
                    continue
                likely = ins.op.endswith("l") and ins.op not in ("bltzal", "bgezal")
                delay = self.insns[pc + 4]
                taken = st.copy()
                prefix: list = []
                if likely:
                    self.step(delay, taken, prefix)
                    fall = st.copy()
                else:
                    self.step(delay, st, out)
                    taken, fall = st.copy(), st.copy()
                # then-block: the fall-through [pc + 8, t); an else when it ends in a forward jump
                last = self.insns.get(t - 8)
                join = t
                hoist = self.insns.get(t - 12)
                if (likely and hoist is not None and t - 12 >= pc + 8 and self._jump(hoist)
                        and hoist.target is not None and t < hoist.target <= self.end
                        and self.insns[t - 4].word == delay.word):  # fmt: skip
                    # IDO copied the else-block's first instruction into the branch-likely's
                    # delay slot and branched past it: else = [t - 4, join)
                    join = hoist.target
                    then, fall, ft1 = self.block(pc + 8, t - 12, fall)
                    self.step(self.insns[t - 8], fall, then)
                    if join > end:  # the then-block leaves the region (a loop exit)
                        then.append(Break(t - 12, join))
                        ft1, join = False, end
                    other, taken, ft2 = self.block(t, join, taken)
                    other = prefix + other
                elif last is not None and t - 8 >= pc + 8 and (
                    last.op == "j" or (last.op == "beq" and last.rs == 0 and last.rt == 0)
                ) and last.target is not None and last.target > t and last.target <= self.end:
                    join = last.target
                    then, fall, ft1 = self.block(pc + 8, t - 8, fall)
                    self.step(self.insns[t - 4], fall, then)
                    if join > end:  # the then-block leaves the region (a loop exit)
                        then.append(Break(t - 8, join))
                        ft1, join = False, end
                    other, taken, ft2 = self.block(t, join, taken)
                    other = prefix + other
                else:
                    then, fall, ft1 = self.block(pc + 8, t, fall)
                    other, ft2 = prefix, True
                out.append(If(pc, self.negate(cond), then, other))
                if ft1 and ft2:
                    st = _merge(fall, taken)
                elif ft1:
                    st = fall
                elif ft2:
                    st = taken
                else:
                    return out, st, False
                pc = join
                continue
            self.step(ins, st, out)
            pc += 4
        return out, st, True

    @staticmethod
    def _jump(ins: Insn) -> bool:
        return ins.op == "j" or (ins.op == "beq" and ins.rs == 0 and ins.rt == 0)

    def _written(self, start: int, end: int) -> set[int]:
        regs: set[int] = set()
        for pc in range(start, end, 4):
            ins = self.insns[pc]
            if ins.is_call:
                regs |= CALLER_SAVED
            if ins.op in ("lui", "addiu", "addi", "ori", "andi", "xori", "slti", "sltiu", "lw", "lh",
                          "lhu", "lb", "lbu", "daddiu"):  # fmt: skip
                regs.add(ins.rt)
            elif ins.op not in ("sw", "sh", "sb", "j", "jal", "jr", "nop") and not ins.is_branch:
                regs.add(ins.rd)
        return regs

    def run(self, args: tuple[int, ...] = ()) -> list:
        """``args``: known constant arguments a0, a1, ... (a routine entered with them, such as
        Rayden's lightning ``0x80077DF8(0)``); branches on them fold away."""

        regs: dict[int, Value] = {4 + i: Const(v) for i, v in enumerate(args)}
        stmts, _, _ = self.block(self.entry, self.end, State(regs, {}, {}))
        return stmts


def routine_end(rom: bytes, entry: int, limit: int = 0x800) -> int:
    """The end of a routine: past the last ``jr ra`` reachable before the next ``addiu sp, -N``
    prologue (compiled routines start with one), within ``limit`` bytes."""

    end = entry + 4
    for pc in range(entry + 4, entry + limit, 4):
        ins = decode(int.from_bytes(rom[pc - VA_BASE : pc - VA_BASE + 4], "big"), pc)
        if ins.op == "addiu" and ins.rs == 29 and ins.rt == 29 and ins.imm < 0:
            break
        end = pc + 4
    return end


def decompile(rom: bytes, entry: int, args: tuple[int, ...] = ()) -> list:
    return Decompiler(rom, entry, routine_end(rom, entry)).run(args)


def render(stmts: list, names: dict[int, str] | None = None, indent: str = "") -> str:
    names = names or {}
    lines: list[str] = []
    for s in stmts:
        if s.kind == "call":
            name = names.get(s.target, f"0x{s.target:08X}" if s.target else "jalr")
            args = ", ".join(str(a) for a in s.args[:4])
            extra = "" if all(isinstance(a, Unknown) for a in s.args[4:]) else f" | {s.args[4]}, {s.args[5]}"
            lines.append(f"{indent}{name}({args}{extra})   @{s.pc:08X}")
        elif s.kind == "store":
            lines.append(f"{indent}{s.address} = {s.value}")
        elif s.kind == "if":
            lines.append(f"{indent}if {s.cond}:")
            lines.append(render(s.then, names, indent + "    ") or indent + "    pass")
            if s.other:
                lines.append(f"{indent}else:")
                lines.append(render(s.other, names, indent + "    "))
        elif s.kind == "loop":
            lines.append(f"{indent}do:")
            lines.append(render(s.body, names, indent + "    ") or indent + "    pass")
            lines.append(f"{indent}while {s.cond}")
        elif s.kind == "return":
            lines.append(f"{indent}return")
        elif s.kind == "break":
            lines.append(f"{indent}break (to 0x{s.target:08X})")
        else:
            lines.append(f"{indent}?? {s.why} @{s.pc:08X}")
    return "\n".join(x for x in lines if x)


__all__ = ["REGS", "Decompiler", "decompile", "render", "routine_end"]
