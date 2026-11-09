"""Relocate a stock MKMSZ routine into the imported-fighter payload, unchanged.

A lifted routine is the starting point for decomposing a stock behaviour into
library primitives: first prove the copy equivalent, then replace marked stretches
one at a time. Equivalence is structural:

* the routine must be self-contained: every branch stays inside it, there are no
  computed jumps other than ``jr ra``, and no address constant points inside it;
* branches are PC-relative and move with the block unchanged;
* ``j``/``jal`` to targets inside the routine are retargeted to the copy;
* ``j``/``jal`` to external targets keep their 28-bit target. Executed from a
  KSEG1 payload they reach the KSEG1 alias of the same code (uncached), exactly as
  the Runtime-confirmed teleport payload already does;
* every other word is identical, except explicit, reported ``patches``.

:func:`lift` returns the copy plus a report; :func:`verify` re-checks a copy
against the original independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field

BRANCH_OPS = {0x01, 0x04, 0x05, 0x06, 0x07, 0x14, 0x15, 0x16, 0x17}
JR_RA = 0x03E00008


class LiftError(ValueError):
    pass


@dataclass
class LiftResult:
    code: bytes
    src_va: int
    dst_va: int
    relocated: list[int] = field(default_factory=list)  # source VAs of retargeted j/jal
    patched: dict[int, tuple[int, int]] = field(default_factory=dict)  # va -> (old, new)


def _words(code: bytes) -> list[int]:
    if len(code) % 4:
        raise LiftError("routine length is not a multiple of 4")
    return [int.from_bytes(code[i : i + 4], "big") for i in range(0, len(code), 4)]


def _target(word: int, pc: int) -> int:
    return ((pc + 4) & 0xF0000000) | ((word & 0x03FFFFFF) << 2)


def _branch_target(word: int, pc: int) -> int:
    offset = word & 0xFFFF
    if offset & 0x8000:
        offset -= 0x10000
    return pc + 4 + offset * 4


def check_self_contained(code: bytes, src_va: int) -> None:
    words = _words(code)
    end = src_va + 4 * len(words)
    regs: dict[int, int] = {}
    for index, word in enumerate(words):
        pc = src_va + 4 * index
        op = word >> 26
        if op in BRANCH_OPS and not src_va <= _branch_target(word, pc) < end:
            raise LiftError(f"branch at {pc:#x} leaves the routine")
        if op == 0 and (word & 0x3F) in (0x08, 0x09) and word != JR_RA:
            raise LiftError(f"computed jump at {pc:#x}")
        if op == 0x0F:
            regs[(word >> 16) & 31] = (word & 0xFFFF) << 16
        elif op in (0x09, 0x0D) and ((word >> 21) & 31) in regs:
            low = word & 0xFFFF
            if op == 0x09 and low & 0x8000:
                low -= 0x10000
            value = (regs[(word >> 21) & 31] + low) & 0xFFFFFFFF
            if src_va <= (value | 0x80000000) < end:
                raise LiftError(f"address constant at {pc:#x} points inside the routine")


def lift(
    code: bytes, src_va: int, dst_va: int, patches: dict[int, int] | None = None
) -> LiftResult:
    """Copy ``code`` (loaded at ``src_va``) to run at ``dst_va``; apply word ``patches``."""

    if (src_va ^ dst_va) & 3:
        raise LiftError("misaligned destination")
    check_self_contained(code, src_va)
    words = _words(code)
    end = src_va + 4 * len(words)
    result = LiftResult(b"", src_va, dst_va)
    out = []
    for index, word in enumerate(words):
        pc = src_va + 4 * index
        op = word >> 26
        if op in (2, 3):
            target = _target(word, pc) & 0x0FFFFFFF | (src_va & 0xF0000000)
            if src_va <= target < end:
                moved = dst_va + (target - src_va)
                if (moved ^ (dst_va + 4 * index + 4)) & 0xF0000000:
                    raise LiftError("relocated jump crosses a 256 MiB segment")
                word = (op << 26) | ((moved >> 2) & 0x03FFFFFF)
                result.relocated.append(pc)
        out.append(word)
    for va, new in (patches or {}).items():
        index = (va - src_va) // 4
        if not 0 <= index < len(out) or va & 3:
            raise LiftError(f"patch address {va:#x} outside the routine")
        result.patched[va] = (out[index], new & 0xFFFFFFFF)
        out[index] = new & 0xFFFFFFFF
    result.code = b"".join(word.to_bytes(4, "big") for word in out)
    return result


def verify(original: bytes, lifted: LiftResult) -> None:
    """Independent check: only relocated jumps and declared patches differ."""

    old = _words(original)
    new = _words(lifted.code)
    if len(old) != len(new):
        raise LiftError("length changed")
    for index, (a, b) in enumerate(zip(old, new, strict=True)):
        va = lifted.src_va + 4 * index
        if va in lifted.patched:
            if b != lifted.patched[va][1]:
                raise LiftError(f"patch at {va:#x} not applied")
            continue
        if a == b:
            continue
        if va not in lifted.relocated or a >> 26 != b >> 26:
            raise LiftError(f"unexpected difference at {va:#x}")
        expected = lifted.dst_va + (_target(a, va) & 0x0FFFFFFF) - (lifted.src_va & 0x0FFFFFFF)
        if _target(b, lifted.dst_va + 4 * index) != expected:
            raise LiftError(f"relocated jump at {va:#x} has the wrong target")
