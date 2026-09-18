"""Minimal big-endian MIPS instruction encoders for MKMSZR native stubs."""

from collections.abc import Iterable
from dataclasses import dataclass

REGISTERS = {
    "zero": 0,
    "v0": 2,
    "v1": 3,
    "a0": 4,
    "a1": 5,
    "t0": 8,
    "t1": 9,
    "t2": 10,
    "t3": 11,
    "t4": 12,
    "t5": 13,
    "t6": 14,
    "t7": 15,
    "s2": 18,
    "t8": 24,
    "t9": 25,
    "sp": 29,
    "ra": 31,
}


def _reg(name: str) -> int:
    return REGISTERS[name]


def addiu(rt: str, rs: str, imm: int) -> int:
    return (0x09 << 26) | (_reg(rs) << 21) | (_reg(rt) << 16) | (imm & 0xFFFF)


def andi(rt: str, rs: str, imm: int) -> int:
    return (0x0C << 26) | (_reg(rs) << 21) | (_reg(rt) << 16) | (imm & 0xFFFF)


def sltiu(rt: str, rs: str, imm: int) -> int:
    return (0x0B << 26) | (_reg(rs) << 21) | (_reg(rt) << 16) | (imm & 0xFFFF)


def ori(rt: str, rs: str, imm: int) -> int:
    return (0x0D << 26) | (_reg(rs) << 21) | (_reg(rt) << 16) | (imm & 0xFFFF)


def lui(rt: str, imm: int) -> int:
    return (0x0F << 26) | (_reg(rt) << 16) | (imm & 0xFFFF)


def sw(rt: str, offset: int, base: str) -> int:
    return (0x2B << 26) | (_reg(base) << 21) | (_reg(rt) << 16) | (offset & 0xFFFF)


def lw(rt: str, offset: int, base: str) -> int:
    return (0x23 << 26) | (_reg(base) << 21) | (_reg(rt) << 16) | (offset & 0xFFFF)


def lbu(rt: str, offset: int, base: str) -> int:
    return (0x24 << 26) | (_reg(base) << 21) | (_reg(rt) << 16) | (offset & 0xFFFF)


def lhu(rt: str, offset: int, base: str) -> int:
    return (0x25 << 26) | (_reg(base) << 21) | (_reg(rt) << 16) | (offset & 0xFFFF)


def sh(rt: str, offset: int, base: str) -> int:
    return (0x29 << 26) | (_reg(base) << 21) | (_reg(rt) << 16) | (offset & 0xFFFF)


def addu(rd: str, rs: str, rt: str) -> int:
    return (_reg(rs) << 21) | (_reg(rt) << 16) | (_reg(rd) << 11) | 0x21


def and_(rd: str, rs: str, rt: str) -> int:
    return (_reg(rs) << 21) | (_reg(rt) << 16) | (_reg(rd) << 11) | 0x24


def or_(rd: str, rs: str, rt: str) -> int:
    return (_reg(rs) << 21) | (_reg(rt) << 16) | (_reg(rd) << 11) | 0x25


def subu(rd: str, rs: str, rt: str) -> int:
    return (_reg(rs) << 21) | (_reg(rt) << 16) | (_reg(rd) << 11) | 0x23


def sll(rd: str, rt: str, shamt: int) -> int:
    if not 0 <= shamt <= 31:
        raise ValueError("shift amount is out of range")
    return (_reg(rt) << 16) | (_reg(rd) << 11) | (shamt << 6)


def sllv(rd: str, rt: str, rs: str) -> int:
    return (_reg(rs) << 21) | (_reg(rt) << 16) | (_reg(rd) << 11) | 0x04


def srl(rd: str, rt: str, shamt: int) -> int:
    if not 0 <= shamt <= 31:
        raise ValueError("shift amount is out of range")
    return (_reg(rt) << 16) | (_reg(rd) << 11) | (shamt << 6) | 0x02


def sltu(rd: str, rs: str, rt: str) -> int:
    return (_reg(rs) << 21) | (_reg(rt) << 16) | (_reg(rd) << 11) | 0x2B


def jal(address: int) -> int:
    return (0x03 << 26) | ((address >> 2) & 0x03FFFFFF)


def jalr(rs: str, rd: str = "ra") -> int:
    return (_reg(rs) << 21) | (_reg(rd) << 11) | 0x09


def jump(address: int) -> int:
    return (0x02 << 26) | ((address >> 2) & 0x03FFFFFF)


def jr(rs: str) -> int:
    return (_reg(rs) << 21) | 0x08


def branch(opcode: int, rs: str, rt: str, displacement: int) -> int:
    if not -0x8000 <= displacement <= 0x7FFF:
        raise ValueError("branch displacement is out of range")
    return (
        (opcode << 26)
        | (_reg(rs) << 21)
        | (_reg(rt) << 16)
        | (displacement & 0xFFFF)
    )


def split_address(address: int) -> tuple[int, int]:
    """Return adjusted high/low immediates for LUI + signed ADDIU/SW/LW."""

    return ((address + 0x8000) >> 16) & 0xFFFF, address & 0xFFFF


def address_words(rt: str, address: int) -> tuple[int, int]:
    high, low = split_address(address)
    return lui(rt, high), addiu(rt, rt, low)


def words_blob(words: Iterable[int]) -> bytes:
    return b"".join((word & 0xFFFFFFFF).to_bytes(4, "big") for word in words)


@dataclass(frozen=True)
class BranchFixup:
    index: int
    opcode: int
    rs: str
    rt: str
    label: str


class Emitter:
    """Tiny label-aware emitter for the bounded runtime payload."""

    def __init__(self) -> None:
        self.words: list[int] = []
        self.labels: dict[str, int] = {}
        self.fixups: list[BranchFixup] = []

    def emit(self, *words: int) -> None:
        self.words.extend(words)

    def label(self, name: str) -> None:
        if name in self.labels:
            raise ValueError(f"duplicate label: {name}")
        self.labels[name] = len(self.words)

    def bne(self, rs: str, rt: str, label: str) -> None:
        self.fixups.append(BranchFixup(len(self.words), 0x05, rs, rt, label))
        self.words.append(0)

    def beq(self, rs: str, rt: str, label: str) -> None:
        self.fixups.append(BranchFixup(len(self.words), 0x04, rs, rt, label))
        self.words.append(0)

    def finish(self) -> bytes:
        for fixup in self.fixups:
            if fixup.label not in self.labels:
                raise ValueError(f"missing label: {fixup.label}")
            displacement = self.labels[fixup.label] - (fixup.index + 1)
            self.words[fixup.index] = branch(
                fixup.opcode, fixup.rs, fixup.rt, displacement
            )
        return words_blob(self.words)
