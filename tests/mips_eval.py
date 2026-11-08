"""Minimal evaluator for importer-generated MIPS routines (tests only).

Executes the small instruction subset the fighter-import assembler emits, against a
dict-backed memory, so a generated routine's data effects can be checked in CI. It
is not an N64 or game emulator: calls that leave the code block stop evaluation and
are reported to the caller, who stubs their effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field

MASK = 0xFFFFFFFF


def _s32(v: int) -> int:
    return v - (1 << 32) if v & 0x80000000 else v


def _phys(address: int) -> int:
    return address & 0x1FFFFFFF


@dataclass
class Stop:
    kind: str  # "return" (jr out of the block) or "call" (jal out of the block)
    target: int
    resume: int = 0  # for "call": address after the delay slot


@dataclass
class Machine:
    code: bytes
    base: int
    mem: dict[int, int] = field(default_factory=dict)
    regs: list[int] = field(default_factory=lambda: [0] * 32)

    def __post_init__(self) -> None:
        for i in range(0, len(self.code), 4):
            self.store(self.base + i, int.from_bytes(self.code[i : i + 4], "big"))

    def inside(self, address: int) -> bool:
        return 0 <= _phys(address) - _phys(self.base) < len(self.code)

    def load(self, address: int) -> int:
        return self.mem.get(_phys(address) & ~3, 0)

    def store(self, address: int, value: int) -> None:
        self.mem[_phys(address) & ~3] = value & MASK

    def run(self, pc: int, limit: int = 10000) -> Stop:
        r = self.regs
        for _ in range(limit):
            w = self.load(pc)
            op, rs, rt, rd = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31
            imm = w & 0xFFFF
            simm = imm - 0x10000 if imm & 0x8000 else imm
            jump = None
            if op == 0:
                fn, sh = w & 63, (w >> 6) & 31
                if fn == 0x21:
                    r[rd] = (r[rs] + r[rt]) & MASK
                elif fn == 0x23:
                    r[rd] = (r[rs] - r[rt]) & MASK
                elif fn == 0x24:
                    r[rd] = r[rs] & r[rt]
                elif fn == 0x26:
                    r[rd] = r[rs] ^ r[rt]
                elif fn == 0x2A:
                    r[rd] = int(_s32(r[rs]) < _s32(r[rt]))
                elif fn == 0x00:
                    r[rd] = (r[rt] << sh) & MASK
                elif fn == 0x03:
                    r[rd] = (_s32(r[rt]) >> sh) & MASK
                elif fn == 0x08:
                    jump = ("jr", r[rs])
                else:
                    raise NotImplementedError(f"{w:#010x} at {pc:#x}")
            elif op == 0x0F:
                r[rt] = imm << 16
            elif op == 0x0D:
                r[rt] = r[rs] | imm
            elif op == 0x0C:
                r[rt] = r[rs] & imm
            elif op == 0x09:
                r[rt] = (r[rs] + simm) & MASK
            elif op == 0x23:
                r[rt] = self.load(r[rs] + simm)
            elif op == 0x2B:
                self.store(r[rs] + simm, r[rt])
            elif op in (0x25, 0x29):
                address = (r[rs] + simm) & MASK
                shift = 16 if address & 2 == 0 else 0
                word = self.load(address)
                if op == 0x25:
                    r[rt] = (word >> shift) & 0xFFFF
                else:
                    word = (word & ~(0xFFFF << shift)) | ((r[rt] & 0xFFFF) << shift)
                    self.store(address, word)
            elif op in (0x04, 0x05):
                if (r[rs] == r[rt]) == (op == 0x04):
                    jump = ("b", pc + 4 + 4 * simm)
            elif op == 0x03:
                jump = ("jal", (pc & 0xF0000000) | ((w & 0x03FFFFFF) << 2))
            else:
                raise NotImplementedError(f"{w:#010x} at {pc:#x}")
            r[0] = 0
            if jump is None:
                pc += 4
                continue
            if self.load(pc + 4) != 0:
                raise NotImplementedError(f"filled delay slot at {pc + 4:#x}")
            kind, target = jump
            if kind == "jal":
                if not self.inside(target):
                    return Stop("call", target, pc + 8)
                r[31] = pc + 8
            elif kind == "jr" and not self.inside(target):
                return Stop("return", target)
            pc = target
        raise RuntimeError("step limit")
