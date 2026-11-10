"""A small MIPS III (R4300i) disassembler for reading donor routines (no dependencies).

Covers the integer ISA, the branch-likely forms, COP0 moves and the COP1 subset game code
uses. Unknown encodings print as ``.word``. Used by :mod:`.reading` (Fighter recompiler plan,
milestone 3).
"""

from __future__ import annotations

from dataclasses import dataclass

REGS = ("zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5",
        "t6", "t7", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp",
        "sp", "fp", "ra")  # fmt: skip


@dataclass(frozen=True)
class Insn:
    pc: int
    word: int
    op: str  # mnemonic
    rs: int = 0
    rt: int = 0
    rd: int = 0
    imm: int = 0  # sign-extended where the instruction sign-extends
    target: int | None = None  # branch or jump target
    text: str = ""

    @property
    def is_branch(self) -> bool:
        return self.target is not None and self.op not in ("j", "jal")

    @property
    def is_call(self) -> bool:
        return self.op in ("jal", "jalr")

    @property
    def is_return(self) -> bool:
        return self.op == "jr" and self.rs == 31


def _s16(v: int) -> int:
    return v - 0x10000 if v & 0x8000 else v


_SPECIAL = {
    0x00: "sll", 0x02: "srl", 0x03: "sra", 0x04: "sllv", 0x06: "srlv", 0x07: "srav", 0x08: "jr",
    0x09: "jalr", 0x0C: "syscall", 0x0D: "break", 0x0F: "sync", 0x10: "mfhi", 0x11: "mthi",
    0x12: "mflo", 0x13: "mtlo", 0x14: "dsllv", 0x16: "dsrlv", 0x17: "dsrav", 0x18: "mult",
    0x19: "multu", 0x1A: "div", 0x1B: "divu", 0x1C: "dmult", 0x1D: "dmultu", 0x1E: "ddiv",
    0x1F: "ddivu", 0x20: "add", 0x21: "addu", 0x22: "sub", 0x23: "subu", 0x24: "and", 0x25: "or",
    0x26: "xor", 0x27: "nor", 0x2A: "slt", 0x2B: "sltu", 0x2C: "dadd", 0x2D: "daddu",
    0x2E: "dsub", 0x2F: "dsubu", 0x38: "dsll", 0x3A: "dsrl", 0x3B: "dsra", 0x3C: "dsll32",
    0x3E: "dsrl32", 0x3F: "dsra32",
}  # fmt: skip
_IMM = {
    0x08: "addi", 0x09: "addiu", 0x0A: "slti", 0x0B: "sltiu", 0x0C: "andi", 0x0D: "ori",
    0x0E: "xori", 0x18: "daddi", 0x19: "daddiu",
}  # fmt: skip
_BRANCH = {0x04: "beq", 0x05: "bne", 0x06: "blez", 0x07: "bgtz", 0x14: "beql", 0x15: "bnel",
           0x16: "blezl", 0x17: "bgtzl"}  # fmt: skip
_REGIMM = {0x00: "bltz", 0x01: "bgez", 0x02: "bltzl", 0x03: "bgezl", 0x10: "bltzal", 0x11: "bgezal"}
_MEM = {
    0x20: "lb", 0x21: "lh", 0x22: "lwl", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x26: "lwr",
    0x27: "lwu", 0x28: "sb", 0x29: "sh", 0x2A: "swl", 0x2B: "sw", 0x2E: "swr", 0x2F: "cache",
    0x31: "lwc1", 0x35: "ldc1", 0x37: "ld", 0x39: "swc1", 0x3D: "sdc1", 0x3F: "sd",
}  # fmt: skip
_FPU = {0x00: "add", 0x01: "sub", 0x02: "mul", 0x03: "div", 0x04: "sqrt", 0x05: "abs",
        0x06: "mov", 0x07: "neg", 0x0D: "trunc.w", 0x20: "cvt.s", 0x21: "cvt.d", 0x24: "cvt.w"}  # fmt: skip
_FMT = {16: "s", 17: "d", 20: "w", 21: "l"}
_FPU.update({0x09: "trunc.l", 0x25: "cvt.l"})
_COND = (
    "f",
    "un",
    "eq",
    "ueq",
    "olt",
    "ult",
    "ole",
    "ule",
    "sf",
    "ngle",
    "seq",
    "ngl",
    "lt",
    "nge",
    "le",
    "ngt",
)


def decode(word: int, pc: int) -> Insn:
    op = word >> 26
    rs, rt, rd = (word >> 21) & 31, (word >> 16) & 31, (word >> 11) & 31
    sa, fn, imm16 = (word >> 6) & 31, word & 63, word & 0xFFFF
    r = REGS
    if word == 0:
        return Insn(pc, word, "nop", text="nop")
    if op == 0:
        name = _SPECIAL.get(fn)
        if name is None:
            return Insn(pc, word, ".word", text=f".word 0x{word:08X}")
        if name in ("sll", "srl", "sra", "dsll", "dsrl", "dsra", "dsll32", "dsrl32", "dsra32"):
            return Insn(pc, word, name, rt=rt, rd=rd, imm=sa, text=f"{name} {r[rd]}, {r[rt]}, {sa}")
        if name in ("jr",):
            return Insn(pc, word, name, rs=rs, text=f"jr {r[rs]}")
        if name == "jalr":
            return Insn(pc, word, name, rs=rs, rd=rd, text=f"jalr {r[rd]}, {r[rs]}")
        if name in ("mfhi", "mflo"):
            return Insn(pc, word, name, rd=rd, text=f"{name} {r[rd]}")
        if name in ("mthi", "mtlo"):
            return Insn(pc, word, name, rs=rs, text=f"{name} {r[rs]}")
        if name in ("mult", "multu", "div", "divu", "dmult", "dmultu", "ddiv", "ddivu"):
            return Insn(pc, word, name, rs=rs, rt=rt, text=f"{name} {r[rs]}, {r[rt]}")
        if name in ("syscall", "break", "sync"):
            return Insn(pc, word, name, text=name)
        if name in ("sllv", "srlv", "srav", "dsllv", "dsrlv", "dsrav"):
            return Insn(
                pc, word, name, rs=rs, rt=rt, rd=rd, text=f"{name} {r[rd]}, {r[rt]}, {r[rs]}"
            )
        return Insn(pc, word, name, rs=rs, rt=rt, rd=rd, text=f"{name} {r[rd]}, {r[rs]}, {r[rt]}")
    if op in (2, 3):
        target = ((pc + 4) & 0xF0000000) | ((word & 0x03FFFFFF) << 2)
        name = "j" if op == 2 else "jal"
        return Insn(pc, word, name, target=target, text=f"{name} 0x{target:08X}")
    if op in _BRANCH:
        name = _BRANCH[op]
        target = (pc + 4 + (_s16(imm16) << 2)) & 0xFFFFFFFF
        if name.startswith(("beq", "bne")):
            return Insn(
                pc,
                word,
                name,
                rs=rs,
                rt=rt,
                target=target,
                text=f"{name} {r[rs]}, {r[rt]}, 0x{target:08X}",
            )
        return Insn(pc, word, name, rs=rs, target=target, text=f"{name} {r[rs]}, 0x{target:08X}")
    if op == 1:
        name = _REGIMM.get(rt)
        if name is None:
            return Insn(pc, word, ".word", text=f".word 0x{word:08X}")
        target = (pc + 4 + (_s16(imm16) << 2)) & 0xFFFFFFFF
        return Insn(pc, word, name, rs=rs, target=target, text=f"{name} {r[rs]}, 0x{target:08X}")
    if op in _IMM:
        name = _IMM[op]
        value = imm16 if name in ("andi", "ori", "xori") else _s16(imm16)
        shown = f"0x{imm16:X}" if name in ("andi", "ori", "xori") else str(value)
        return Insn(
            pc, word, name, rs=rs, rt=rt, imm=value, text=f"{name} {r[rt]}, {r[rs]}, {shown}"
        )
    if op == 0x0F:
        return Insn(pc, word, "lui", rt=rt, imm=imm16, text=f"lui {r[rt]}, 0x{imm16:X}")
    if op in _MEM:
        name = _MEM[op]
        reg = f"f{rt}" if name in ("lwc1", "swc1", "ldc1", "sdc1") else r[rt]
        return Insn(
            pc,
            word,
            name,
            rs=rs,
            rt=rt,
            imm=_s16(imm16),
            text=f"{name} {reg}, {_s16(imm16)}({r[rs]})",
        )
    if op == 0x10:  # COP0
        name = {0: "mfc0", 4: "mtc0"}.get(rs)
        if name:
            return Insn(pc, word, name, rt=rt, rd=rd, text=f"{name} {r[rt]}, c0r{rd}")
        if rs == 16 and fn in (1, 2, 6, 8, 24):
            name = {1: "tlbr", 2: "tlbwi", 6: "tlbwr", 8: "tlbp", 24: "eret"}[fn]
            return Insn(pc, word, name, text=name)
        return Insn(pc, word, "cop0", text=f"cop0 0x{word & 0x1FFFFFF:X}")
    if op == 0x11:  # COP1
        if rs in (0, 1, 2, 4, 5, 6):
            name = {0: "mfc1", 1: "dmfc1", 4: "mtc1", 5: "dmtc1", 2: "cfc1", 6: "ctc1"}[rs]
            return Insn(pc, word, name, rt=rt, rd=rd, text=f"{name} {r[rt]}, f{rd}")
        if rs == 8:
            name = ("bc1f", "bc1t", "bc1fl", "bc1tl")[rt & 3]
            target = (pc + 4 + (_s16(imm16) << 2)) & 0xFFFFFFFF
            return Insn(pc, word, name, target=target, text=f"{name} 0x{target:08X}")
        fmt = _FMT.get(rs)
        ft, fs, fd = rt, rd, sa
        if fmt and fn in _FPU:
            name = f"{_FPU[fn]}.{fmt}"
            return Insn(
                pc,
                word,
                name,
                text=f"{name} f{fd}, f{fs}, f{ft}" if fn < 4 else f"{name} f{fd}, f{fs}",
            )
        if fmt and fn >= 0x30:
            name = f"c.{_COND[fn & 15]}.{fmt}"
            return Insn(pc, word, name, text=f"{name} f{fs}, f{ft}")
        return Insn(pc, word, "cop1", text=f"cop1 0x{word & 0x1FFFFFF:X}")
    return Insn(pc, word, ".word", text=f".word 0x{word:08X}")
