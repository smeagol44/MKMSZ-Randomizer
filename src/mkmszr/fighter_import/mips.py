"""Small MIPS III assembler for imported-fighter action code.

Only the instructions the host primitives need are provided. Every branch, ``jal``
and ``j`` gets an explicit ``nop`` delay slot, matching the proof builders this
module was extracted from (teleport proofs v03-v18); callers that need a filled
delay slot emit the instruction themselves after :meth:`Assembler.raw`.

Labels are resolved by :meth:`Assembler.link`. ``jal``/``j`` to a label keep the
upper four address bits of the call site, so code assembled for a KSEG1 base
calls KSEG1 labels.
"""

from __future__ import annotations

REGISTERS = [
    "zero",
    "at",
    "v0",
    "v1",
    "a0",
    "a1",
    "a2",
    "a3",
    "t0",
    "t1",
    "t2",
    "t3",
    "t4",
    "t5",
    "t6",
    "t7",
    "s0",
    "s1",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "s7",
    "t8",
    "t9",
    "k0",
    "k1",
    "gp",
    "sp",
    "fp",
    "ra",
]
REG = {name: index for index, name in enumerate(REGISTERS)}


class Assembler:
    def __init__(self, base: int) -> None:
        self.base = base
        self.code: list[int] = []
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, str, str]] = []

    # -- layout -----------------------------------------------------------------
    def pc(self) -> int:
        return self.base + 4 * len(self.code)

    def label(self, name: str) -> None:
        if name in self.labels:
            raise ValueError(f"duplicate label {name}")
        self.labels[name] = self.pc()

    def raw(self, word: int) -> None:
        self.code.append(word & 0xFFFFFFFF)

    def nop(self) -> None:
        self.raw(0)

    # -- encodings --------------------------------------------------------------
    def _i(self, op: int, rs: str, rt: str, imm: int) -> None:
        self.raw((op << 26) | (REG[rs] << 21) | (REG[rt] << 16) | (imm & 0xFFFF))

    def _r(self, rs: str, rt: str, rd: str, shift: int, funct: int) -> None:
        self.raw((REG[rs] << 21) | (REG[rt] << 16) | (REG[rd] << 11) | ((shift & 31) << 6) | funct)

    # arithmetic / logic
    def addu(self, rd: str, rs: str, rt: str) -> None:
        self._r(rs, rt, rd, 0, 0x21)

    def subu(self, rd: str, rs: str, rt: str) -> None:
        self._r(rs, rt, rd, 0, 0x23)

    def and_(self, rd: str, rs: str, rt: str) -> None:
        self._r(rs, rt, rd, 0, 0x24)

    def xor(self, rd: str, rs: str, rt: str) -> None:
        self._r(rs, rt, rd, 0, 0x26)

    def slt(self, rd: str, rs: str, rt: str) -> None:
        self._r(rs, rt, rd, 0, 0x2A)

    def sll(self, rd: str, rt: str, shift: int) -> None:
        self._r("zero", rt, rd, shift, 0x00)

    def sra(self, rd: str, rt: str, shift: int) -> None:
        self._r("zero", rt, rd, shift, 0x03)

    def mult(self, rs: str, rt: str) -> None:
        self._r(rs, rt, "zero", 0, 0x18)

    def div(self, rs: str, rt: str) -> None:
        self._r(rs, rt, "zero", 0, 0x1A)

    def mflo(self, rd: str) -> None:
        self._r("zero", "zero", rd, 0, 0x12)

    def move(self, rd: str, rs: str) -> None:
        self.addu(rd, rs, "zero")

    def addiu(self, rt: str, rs: str, imm: int) -> None:
        if not -0x8000 <= imm < 0x8000:
            raise ValueError(f"addiu immediate out of range: {imm:#x}")
        self._i(0x09, rs, rt, imm)

    def andi(self, rt: str, rs: str, imm: int) -> None:
        self._i(0x0C, rs, rt, imm)

    def ori(self, rt: str, rs: str, imm: int) -> None:
        self._i(0x0D, rs, rt, imm)

    def lui(self, rt: str, imm: int) -> None:
        self._i(0x0F, "zero", rt, imm)

    def li(self, rt: str, value: int) -> None:
        """Load a 32-bit constant: one ``addiu`` when it fits, else ``lui`` (+ ``ori``)."""

        value &= 0xFFFFFFFF
        if value < 0x8000 or value >= 0xFFFF8000:
            self.addiu(rt, "zero", value - (1 << 32) if value >= 0x80000000 else value)
        else:
            self.lui(rt, value >> 16)
            if value & 0xFFFF:
                self.ori(rt, rt, value & 0xFFFF)

    # memory
    def lb(self, rt: str, offset: int, rs: str) -> None:
        self._i(0x20, rs, rt, offset)

    def lh(self, rt: str, offset: int, rs: str) -> None:
        self._i(0x21, rs, rt, offset)

    def lw(self, rt: str, offset: int, rs: str) -> None:
        self._i(0x23, rs, rt, offset)

    def lhu(self, rt: str, offset: int, rs: str) -> None:
        self._i(0x25, rs, rt, offset)

    def sb(self, rt: str, offset: int, rs: str) -> None:
        self._i(0x28, rs, rt, offset)

    def sh(self, rt: str, offset: int, rs: str) -> None:
        self._i(0x29, rs, rt, offset)

    def sw(self, rt: str, offset: int, rs: str) -> None:
        self._i(0x2B, rs, rt, offset)

    # control flow (all with a nop delay slot)
    def jal(self, address: int) -> None:
        self.raw((3 << 26) | ((address >> 2) & 0x03FFFFFF))
        self.nop()

    def jal_label(self, name: str) -> None:
        self.fixups.append((len(self.code), "jal", name))
        self.raw(3 << 26)
        self.nop()

    def j_label(self, name: str) -> None:
        self.fixups.append((len(self.code), "j", name))
        self.raw(2 << 26)
        self.nop()

    def jr_ra(self) -> None:
        """``jr ra`` without a delay slot: the caller emits the delay-slot instruction."""

        self.raw(0x03E00008)

    def _branch(self, op: int, rs: str, rt: str, name: str) -> None:
        self.fixups.append((len(self.code), "b", name))
        self._i(op, rs, rt, 0)
        self.nop()

    def beq(self, rs: str, rt: str, name: str) -> None:
        self._branch(0x04, rs, rt, name)

    def bne(self, rs: str, rt: str, name: str) -> None:
        self._branch(0x05, rs, rt, name)

    def beqz(self, rs: str, name: str) -> None:
        self._branch(0x04, rs, "zero", name)

    def bnez(self, rs: str, name: str) -> None:
        self._branch(0x05, rs, "zero", name)

    def blez(self, rs: str, name: str) -> None:
        self._branch(0x06, rs, "zero", name)

    def bltz(self, rs: str, name: str) -> None:
        self.fixups.append((len(self.code), "b", name))
        self.raw((1 << 26) | (REG[rs] << 21))
        self.nop()

    def bgez(self, rs: str, name: str) -> None:
        self.fixups.append((len(self.code), "b", name))
        self.raw((1 << 26) | (REG[rs] << 21) | (1 << 16))
        self.nop()

    def la(self, rt: str, name: str) -> None:
        self.fixups.append((len(self.code), "la", name))
        self.lui(rt, 0)
        self.ori(rt, rt, 0)

    # -- linking ----------------------------------------------------------------
    def link(self) -> bytes:
        for index, kind, name in self.fixups:
            target = self.labels[name]
            pc = self.base + 4 * index
            if kind == "la":
                self.code[index] = (self.code[index] & 0xFFFF0000) | (target >> 16)
                self.code[index + 1] = (self.code[index + 1] & 0xFFFF0000) | (target & 0xFFFF)
            elif kind == "b":
                delta = (target - (pc + 4)) // 4
                if not -0x8000 <= delta < 0x8000:
                    raise ValueError(f"branch to {name} out of range")
                self.code[index] = (self.code[index] & 0xFFFF0000) | (delta & 0xFFFF)
            else:
                if (target & 0xF0000000) != (pc & 0xF0000000):
                    raise ValueError(f"{kind} to {name} crosses a 256 MiB segment")
                op = 3 if kind == "jal" else 2
                self.code[index] = (op << 26) | ((target >> 2) & 0x03FFFFFF)
        return b"".join(word.to_bytes(4, "big") for word in self.code)
