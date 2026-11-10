"""Minimal evaluator for importer-generated MIPS routines (tests only).

Executes the small instruction subset the fighter-import assembler emits, against a
dict-backed memory, so a generated routine's data effects can be checked in CI. It
is not an N64 or game emulator: calls that leave the code block stop evaluation (after
their delay slot) and are reported to the caller, who stubs their effects.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field

MASK = 0xFFFFFFFF


def _s32(v: int) -> int:
    return v - (1 << 32) if v & 0x80000000 else v


def _phys(address: int) -> int:
    return address & 0x1FFFFFFF


@dataclass
class Stop:
    kind: str  # "return" (jr out of the block), "call" (jal out) or "jump" (j out)
    target: int
    resume: int = 0  # for "call": address after the delay slot


@dataclass
class Machine:
    code: bytes
    base: int
    mem: dict[int, int] = field(default_factory=dict)
    regs: list[int] = field(default_factory=lambda: [0] * 32)
    lo: int = 0
    hi: int = 0
    fpr: list[int] = field(default_factory=lambda: [0] * 32)  # raw 32-bit FPU registers
    fcc: bool = False
    cop0: list[int] = field(default_factory=lambda: [0] * 32)  # mfc0/mtc0 only

    def __post_init__(self) -> None:
        for i in range(0, len(self.code), 4):
            self.store(self.base + i, int.from_bytes(self.code[i : i + 4], "big"))

    def inside(self, address: int) -> bool:
        return 0 <= _phys(address) - _phys(self.base) < len(self.code)

    def load(self, address: int) -> int:
        return self.mem.get(_phys(address) & ~3, 0)

    def store(self, address: int, value: int) -> None:
        self.mem[_phys(address) & ~3] = value & MASK

    # ---- FPU subset (FR=0: a double lives in an even/odd register pair, low word even) ----
    def _fs(self, i: int) -> float:
        return struct.unpack(">f", self.fpr[i].to_bytes(4, "big"))[0]

    def _set_fs(self, i: int, v: float) -> None:
        self.fpr[i] = int.from_bytes(struct.pack(">f", v), "big")

    def _fd(self, i: int) -> float:
        raw = (self.fpr[i | 1] << 32) | self.fpr[i & ~1]
        return struct.unpack(">d", raw.to_bytes(8, "big"))[0]

    def _set_fd(self, i: int, v: float) -> None:
        raw = int.from_bytes(struct.pack(">d", v), "big")
        self.fpr[i & ~1], self.fpr[i | 1] = raw & MASK, raw >> 32

    def _cop1(self, w: int) -> None:
        fmt, ft, fs, fd, fn = (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31, w & 63
        r = self.regs
        if fmt == 0x00:  # mfc1
            r[ft] = self.fpr[fs]
            return
        if fmt == 0x04:  # mtc1
            self.fpr[fs] = r[ft]
            return
        if fmt in (0x02, 0x06):  # cfc1 / ctc1: rounding/flags not modelled
            if fmt == 0x02:
                r[ft] = 0
            return
        if fmt == 0x14:  # W: only conversions from integer
            v = _s32(self.fpr[fs])
            if fn == 0x20:
                self._set_fs(fd, float(v))
            elif fn == 0x21:
                self._set_fd(fd, float(v))
            else:
                raise NotImplementedError(f"{w:#010x} cop1.w")
            return
        if fmt not in (0x10, 0x11):
            raise NotImplementedError(f"{w:#010x} cop1")
        get, put = (self._fs, self._set_fs) if fmt == 0x10 else (self._fd, self._set_fd)
        a, b = get(fs), get(ft)
        if fn == 0x00:
            put(fd, a + b)
        elif fn == 0x01:
            put(fd, a - b)
        elif fn == 0x02:
            put(fd, a * b)
        elif fn == 0x03:
            put(fd, a / b if b else math.copysign(math.inf, a))
        elif fn == 0x04:
            put(fd, math.sqrt(a) if a >= 0 else math.nan)
        elif fn == 0x05:
            put(fd, abs(a))
        elif fn == 0x06:
            put(fd, a)
        elif fn == 0x07:
            put(fd, -a)
        elif fn in (0x0C, 0x0D, 0x0E, 0x0F, 0x24):  # round/trunc/ceil/floor/cvt.w (trunc for cvt)
            op = {0x0C: round, 0x0D: math.trunc, 0x0E: math.ceil, 0x0F: math.floor, 0x24: round}[fn]
            self.fpr[fd] = int(op(a)) & MASK if math.isfinite(a) else 0x7FFFFFFF
        elif fn == 0x20:
            self._set_fs(fd, a)
        elif fn == 0x21:
            self._set_fd(fd, a)
        elif fn >= 0x30:  # c.cond: bit0 unordered, bit1 equal, bit2 less
            unordered = math.isnan(a) or math.isnan(b)
            self.fcc = bool(
                (fn & 1 and unordered)
                or (fn & 2 and not unordered and a == b)
                or (fn & 4 and not unordered and a < b)
            )
        else:
            raise NotImplementedError(f"{w:#010x} cop1")

    def run(self, pc: int, limit: int = 10000) -> Stop:
        r = self.regs
        pending: tuple[str, int, int] | None = None  # (kind, target, jump pc)
        for _ in range(limit):
            self.last_pc = pc
            w = self.load(pc)
            op, rs, rt, rd = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31
            imm = w & 0xFFFF
            simm = imm - 0x10000 if imm & 0x8000 else imm
            jump = None
            if op == 0:
                fn, sh = w & 63, (w >> 6) & 31
                if fn in (0x20, 0x21):  # add / addu (no overflow trap modelled)
                    r[rd] = (r[rs] + r[rt]) & MASK
                elif fn == 0x22:
                    r[rd] = (r[rs] - r[rt]) & MASK
                elif fn == 0x27:
                    r[rd] = ~(r[rs] | r[rt]) & MASK
                elif fn == 0x04:
                    r[rd] = (r[rt] << (r[rs] & 31)) & MASK
                elif fn == 0x06:
                    r[rd] = r[rt] >> (r[rs] & 31)
                elif fn == 0x07:
                    r[rd] = (_s32(r[rt]) >> (r[rs] & 31)) & MASK
                elif fn == 0x23:
                    r[rd] = (r[rs] - r[rt]) & MASK
                elif fn == 0x24:
                    r[rd] = r[rs] & r[rt]
                elif fn == 0x25:
                    r[rd] = r[rs] | r[rt]
                elif fn == 0x26:
                    r[rd] = r[rs] ^ r[rt]
                elif fn == 0x2A:
                    r[rd] = int(_s32(r[rs]) < _s32(r[rt]))
                elif fn == 0x2B:
                    r[rd] = int(r[rs] < r[rt])
                elif fn == 0x02:
                    r[rd] = r[rt] >> sh
                elif fn == 0x18:  # mult
                    p = _s32(r[rs]) * _s32(r[rt])
                    self.lo, self.hi = p & MASK, (p >> 32) & MASK
                elif fn == 0x1A:  # div (truncating, as the CPU)
                    n, d = _s32(r[rs]), _s32(r[rt])
                    if d:
                        q = abs(n) // abs(d) * (1 if (n < 0) == (d < 0) else -1)
                        self.lo, self.hi = q & MASK, (n - q * d) & MASK
                elif fn == 0x19:  # multu
                    p = r[rs] * r[rt]
                    self.lo, self.hi = p & MASK, (p >> 32) & MASK
                elif fn == 0x1B:  # divu
                    if r[rt]:
                        self.lo, self.hi = r[rs] // r[rt], r[rs] % r[rt]
                elif fn == 0x12:
                    r[rd] = self.lo
                elif fn == 0x10:
                    r[rd] = self.hi
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
            elif op == 0x0A:
                r[rt] = int(_s32(r[rs]) < simm)
            elif op == 0x0F:
                r[rt] = imm << 16
            elif op == 0x0D:
                r[rt] = r[rs] | imm
            elif op == 0x0C:
                r[rt] = r[rs] & imm
            elif op == 0x0E:
                r[rt] = r[rs] ^ imm
            elif op == 0x2F:  # cache: no architectural effect in this model
                pass
            elif op == 0x0B:  # sltiu (sign-extended immediate, unsigned compare)
                r[rt] = int(r[rs] < (simm & MASK))
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
            elif op == 0x07:  # bgtz
                if _s32(r[rs]) > 0:
                    jump = ("b", pc + 4 + 4 * simm)
            elif op == 0x01 and rt in (0, 1):  # bltz / bgez
                if (_s32(r[rs]) < 0) == (rt == 0):
                    jump = ("b", pc + 4 + 4 * simm)
            elif op in (0x14, 0x15, 0x16, 0x17) or (op == 0x01 and rt in (2, 3)):
                # branch likely: the delay slot runs only when the branch is taken
                if op == 0x14:
                    taken = r[rs] == r[rt]
                elif op == 0x15:
                    taken = r[rs] != r[rt]
                elif op == 0x16:
                    taken = _s32(r[rs]) <= 0
                elif op == 0x17:
                    taken = _s32(r[rs]) > 0
                else:
                    taken = (_s32(r[rs]) < 0) == (rt == 2)
                if taken:
                    jump = ("b", pc + 4 + 4 * simm)
                else:
                    pc += 8
                    continue
            elif op == 0x31:  # lwc1
                self.fpr[rt] = self.load(r[rs] + simm)
            elif op == 0x39:  # swc1
                self.store(r[rs] + simm, self.fpr[rt])
            elif op == 0x35:  # ldc1 (FR=0 pair: low word in the even register)
                address = r[rs] + simm
                self.fpr[rt | 1], self.fpr[rt & ~1] = self.load(address), self.load(address + 4)
            elif op == 0x3D:  # sdc1
                address = r[rs] + simm
                self.store(address, self.fpr[rt | 1])
                self.store(address + 4, self.fpr[rt & ~1])
            elif op == 0x11 and (w >> 21) & 31 == 0x08:  # bc1f / bc1t (/ likely)
                taken = self.fcc == bool(rt & 1)
                if taken:
                    jump = ("b", pc + 4 + 4 * simm)
                elif rt & 2:
                    pc += 8
                    continue
            elif op == 0x11:
                self._cop1(w)
            elif op == 0x10 and rs in (0, 4):  # mfc0 / mtc0 (no side effects modelled)
                if rs == 0:
                    r[rt] = self.cop0[rd]
                else:
                    self.cop0[rd] = r[rt]
            elif op == 0x03:
                jump = ("jal", (pc & 0xF0000000) | ((w & 0x03FFFFFF) << 2))
            elif op == 0x02:
                jump = ("j", (pc & 0xF0000000) | ((w & 0x03FFFFFF) << 2))
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
                if kind == "j" and not self.inside(target):
                    return Stop("jump", target)
                pc = target
                continue
            if jump is not None:
                kind, target = jump
                if kind == "jal":
                    r[31] = pc + 8
                pending = (kind, target, pc)
            pc += 4
        raise RuntimeError("step limit")
