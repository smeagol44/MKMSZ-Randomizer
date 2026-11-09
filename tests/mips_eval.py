"""Minimal evaluator for importer-generated MIPS routines (tests only).

Executes the small instruction subset the fighter-import assembler emits, against a
dict-backed memory, so a generated routine's data effects can be checked in CI. It
is not an N64 or game emulator: calls that leave the code block stop evaluation (after
their delay slot) and are reported to the caller, who stubs their effects.
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
        pending: tuple[str, int, int] | None = None  # (kind, target, jump pc)
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
                elif fn == 0x09:
                    jump = ("jal", r[rs])
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
            elif op in (0x21, 0x25, 0x29):
                address = (r[rs] + simm) & MASK
                shift = 16 if address & 2 == 0 else 0
                word = self.load(address)
                if op == 0x25:
                    r[rt] = (word >> shift) & 0xFFFF
                elif op == 0x21:
                    half = (word >> shift) & 0xFFFF
                    r[rt] = (half - 0x10000 if half & 0x8000 else half) & MASK
                else:
                    word = (word & ~(0xFFFF << shift)) | ((r[rt] & 0xFFFF) << shift)
                    self.store(address, word)
            elif op in (0x20, 0x24, 0x28):  # lb / lbu / sb
                address = (r[rs] + simm) & MASK
                shift = 8 * (3 - (address & 3))
                word = self.load(address)
                if op == 0x28:
                    self.store(address, (word & ~(0xFF << shift)) | ((r[rt] & 0xFF) << shift))
                else:
                    byte = (word >> shift) & 0xFF
                    r[rt] = ((byte - 0x100) & MASK) if op == 0x20 and byte & 0x80 else byte
            elif op in (0x04, 0x05):
                if (r[rs] == r[rt]) == (op == 0x04):
                    jump = ("b", pc + 4 + 4 * simm)
            elif op == 0x06:  # blez
                if _s32(r[rs]) <= 0:
                    jump = ("b", pc + 4 + 4 * simm)
            elif op == 0x01 and rt in (0, 1):  # bltz / bgez
                if (_s32(r[rs]) < 0) == (rt == 0):
                    jump = ("b", pc + 4 + 4 * simm)
            elif op == 0x03:
                jump = ("jal", (pc & 0xF0000000) | ((w & 0x03FFFFFF) << 2))
            else:
                raise NotImplementedError(f"{w:#010x} at {pc:#x}")
            r[0] = 0
            if pending is not None:  # this was a delay slot: now take the jump
                if jump is not None:
                    raise NotImplementedError(f"jump in a delay slot at {pc:#x}")
                kind, target, at = pending
                pending = None
                if kind == "jal" and not self.inside(target):
                    return Stop("call", target, at + 8)
                if kind == "jr" and not self.inside(target):
                    return Stop("return", target)
                pc = target
                continue
            if jump is not None:
                kind, target = jump
                if kind == "jal":
                    r[31] = pc + 8
                pending = (kind, target, pc)
            pc += 4
        raise RuntimeError("step limit")
