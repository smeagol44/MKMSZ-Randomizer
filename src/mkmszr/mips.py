"""Minimal big-endian MIPS instruction encoders for MKMSZR native stubs."""

from collections.abc import Iterable

REGISTERS = {
    "zero": 0,
    "v0": 2,
    "a0": 4,
    "a1": 5,
    "t0": 8,
    "t1": 9,
    "t9": 25,
    "sp": 29,
    "ra": 31,
}


def _reg(name: str) -> int:
    return REGISTERS[name]


def addiu(rt: str, rs: str, imm: int) -> int:
    return (0x09 << 26) | (_reg(rs) << 21) | (_reg(rt) << 16) | (imm & 0xFFFF)


def ori(rt: str, rs: str, imm: int) -> int:
    return (0x0D << 26) | (_reg(rs) << 21) | (_reg(rt) << 16) | (imm & 0xFFFF)


def lui(rt: str, imm: int) -> int:
    return (0x0F << 26) | (_reg(rt) << 16) | (imm & 0xFFFF)


def sw(rt: str, offset: int, base: str) -> int:
    return (0x2B << 26) | (_reg(base) << 21) | (_reg(rt) << 16) | (offset & 0xFFFF)


def lw(rt: str, offset: int, base: str) -> int:
    return (0x23 << 26) | (_reg(base) << 21) | (_reg(rt) << 16) | (offset & 0xFFFF)


def jal(address: int) -> int:
    return (0x03 << 26) | ((address >> 2) & 0x03FFFFFF)


def jalr(rs: str, rd: str = "ra") -> int:
    return (_reg(rs) << 21) | (_reg(rd) << 11) | 0x09


def jump(address: int) -> int:
    return (0x02 << 26) | ((address >> 2) & 0x03FFFFFF)


def jr(rs: str) -> int:
    return (_reg(rs) << 21) | 0x08


def split_address(address: int) -> tuple[int, int]:
    """Return adjusted high/low immediates for LUI + signed ADDIU/SW/LW."""

    return ((address + 0x8000) >> 16) & 0xFFFF, address & 0xFFFF


def words_blob(words: Iterable[int]) -> bytes:
    return b"".join((word & 0xFFFFFFFF).to_bytes(4, "big") for word in words)
