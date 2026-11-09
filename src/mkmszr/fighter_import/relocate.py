"""Relocatable imported-fighter code: a payload blob stored inside a fighter file.

An imported fighter's payload (actions, lifted stock routines, effects, state) can live
inside its own fighter file instead of a fixed RDRAM reservation, so it costs no heap
beyond the file's stock size. The file is loaded into the arena at a stage-dependent
address, so after every load a small fixed loader relocates the blob and refreshes the
stock pointers into it.

* Relocations are found by linking the payload at two bases and diffing the words
  (:func:`find`); a third link checks them (:func:`apply` must reproduce it exactly).
  Kinds: a full word (data pointer), a ``j``/``jal`` target, and ``lui`` + low pairs
  (``ori`` zero-extended, or a signed-immediate user such as ``addiu``/``lw``).
* The fixed part (:func:`emit_fixed`) wraps the stock raw-file loader call for the
  fighter file: load, relocate the blob (executed and addressed through KSEG1), then
  write each stock reference (data words such as record actions, table entries and
  trampoline slots) to point into it. Stock ``jal`` sites go to fixed trampolines
  that jump through those slots.

The blob runs from KSEG1 (no instruction cache), as the raw-loaded payload before it.
"""

from __future__ import annotations

from dataclasses import dataclass

from .mips import Assembler

M = 0xFFFFFFFF
KIND_WORD, KIND_JUMP, KIND_PAIR_ORI, KIND_PAIR_SIGNED = 0, 1, 2, 3
TABLE_END = 0xFFFFFFFF
LO_ORI = 0x0D
LO_SIGNED = {0x09, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B}  # addiu, loads, stores
MAX_PAIR_GAP = 8  # words between a lui and its low user
KSEG1_BIT = 0x20000000


class RelocationError(ValueError):
    pass


@dataclass(frozen=True)
class Reloc:
    kind: int
    index: int  # word index of the word (the lui for pairs)
    partner: int = 0  # word index of the low user (pairs)


def _words(blob: bytes) -> list[int]:
    if len(blob) % 4:
        raise RelocationError("blob length must be a multiple of 4")
    return [int.from_bytes(blob[i : i + 4], "big") for i in range(0, len(blob), 4)]


def _blob(words: list[int]) -> bytes:
    return b"".join(w.to_bytes(4, "big") for w in words)


def find(a: bytes, b: bytes, delta: int) -> list[Reloc]:
    """Relocations of ``a`` from ``b`` = the same payload linked ``delta`` bytes higher."""

    if len(a) != len(b):
        raise RelocationError("the two links differ in length (an address-dependent li?)")
    if delta & 3 or not delta & 0xFFFF or not delta >> 16:
        raise RelocationError("delta must be word-aligned with non-zero high and low halves")
    wa, wb = _words(a), _words(b)
    diffs = [i for i, (x, y) in enumerate(zip(wa, wb)) if x != y]
    used: set[int] = set()
    out: list[Reloc] = []
    for i in diffs:
        if i in used:
            continue
        x, y = wa[i], wb[i]
        op = x >> 26
        if (y - x) & M == delta & M:
            out.append(Reloc(KIND_WORD, i))
        elif op in (2, 3) and y >> 26 == op and (y - x) & 0x03FFFFFF == (delta >> 2) & 0x03FFFFFF:
            out.append(Reloc(KIND_JUMP, i))
        elif op == 0x0F and y >> 16 == x >> 16:
            rt = (x >> 16) & 31
            for j in range(i + 1, min(i + 1 + MAX_PAIR_GAP, len(wa))):
                user = wa[j]
                if j in diffs and j not in used and (user >> 21) & 31 == rt:
                    uop = user >> 26
                    if uop == LO_ORI or uop in LO_SIGNED:
                        kind = KIND_PAIR_ORI if uop == LO_ORI else KIND_PAIR_SIGNED
                        out.append(Reloc(kind, i, j))
                        used.add(j)
                        break
            else:
                raise RelocationError(f"lui at word {i:#x} has no changed low user")
        else:
            raise RelocationError(f"unclassified change at word {i:#x}: {x:#010x} -> {y:#010x}")
        used.add(i)
    return out


def apply(blob: bytes, relocs: list[Reloc], delta: int) -> bytes:
    """Python model of the runtime relocator."""

    w = _words(blob)
    for r in relocs:
        x = w[r.index]
        if r.kind == KIND_WORD:
            w[r.index] = (x + delta) & M
        elif r.kind == KIND_JUMP:
            w[r.index] = (x & 0xFC000000) | ((x + (delta >> 2)) & 0x03FFFFFF)
        else:
            low = w[r.partner] & 0xFFFF
            if r.kind == KIND_PAIR_SIGNED and low & 0x8000:
                low -= 0x10000
            value = (((x & 0xFFFF) << 16) + low + delta) & M
            high = value >> 16 if r.kind == KIND_PAIR_ORI else ((value + 0x8000) & M) >> 16
            w[r.index] = (x & 0xFFFF0000) | (high & 0xFFFF)
            w[r.partner] = (w[r.partner] & 0xFFFF0000) | (value & 0xFFFF)
    return _blob(w)


def encode(relocs: list[Reloc]) -> bytes:
    """Table words: kind << 30 | (partner - index) << 16 | index; then TABLE_END."""

    out = []
    for r in relocs:
        gap = r.partner - r.index if r.kind >= KIND_PAIR_ORI else 0
        if not 0 <= r.index < 0x10000 or not 0 <= gap < 0x4000:
            raise RelocationError("relocation out of encodable range")
        word = (r.kind << 30) | (gap << 16) | r.index
        if word == TABLE_END:
            raise RelocationError("relocation collides with the end marker")
        out.append(word)
    out.append(TABLE_END)
    return _blob(out)


@dataclass(frozen=True)
class StockRef:
    """A stock RAM word that must point into the blob (``address`` is its VA)."""

    address: int
    offset: int  # byte offset in the blob
    kseg0: bool = False  # store the cached alias (e.g. a strike record) instead of KSEG1


def emit_relocator(a: Assembler, label: str = "rel_apply") -> None:
    """``rel_apply(a0 = blob, a1 = table, a2 = delta)``: apply the table. Leaf; t0-t9."""

    a.label(label)
    a.label(label + "_next")
    a.lw("t0", 0, "a1")
    a.addiu("a1", "a1", 4)
    a.li("t1", -1)
    a.beq("t0", "t1", label + "_done")
    a.andi("t2", "t0", 0xFFFF)
    a.sll("t2", "t2", 2)
    a.addu("t2", "a0", "t2")  # the word (lui for pairs)
    a.lw("t4", 0, "t2")
    a.srl("t3", "t0", 30)
    a.bnez("t3", label + "_jump")
    a.addu("t4", "t4", "a2")  # full word
    a.beq("zero", "zero", label + "_store")
    a.label(label + "_jump")
    a.li("t5", KIND_JUMP)
    a.bne("t3", "t5", label + "_pair")
    a.sra("t6", "a2", 2)
    a.addu("t6", "t4", "t6")
    a.sll("t6", "t6", 6)
    a.srl("t6", "t6", 6)  # 26-bit target
    a.srl("t4", "t4", 26)
    a.sll("t4", "t4", 26)
    a.or_("t4", "t4", "t6")
    a.beq("zero", "zero", label + "_store")
    a.label(label + "_pair")
    a.srl("t5", "t0", 16)
    a.andi("t5", "t5", 0x3FFF)
    a.sll("t5", "t5", 2)
    a.addu("t5", "t2", "t5")  # the low user
    a.lw("t6", 0, "t5")
    a.andi("t7", "t6", 0xFFFF)  # low (zero-extended)
    a.li("t8", KIND_PAIR_SIGNED)
    a.bne("t3", "t8", label + "_value")
    a.sll("t7", "t7", 16)
    a.sra("t7", "t7", 16)  # signed low
    a.label(label + "_value")
    a.sll("t9", "t4", 16)  # high << 16
    a.addu("t9", "t9", "t7")
    a.addu("t9", "t9", "a2")  # new value
    a.srl("t6", "t6", 16)
    a.sll("t6", "t6", 16)
    a.andi("t7", "t9", 0xFFFF)
    a.or_("t6", "t6", "t7")
    a.sw("t6", 0, "t5")  # new low
    a.bne("t3", "t8", label + "_high")
    a.addiu("t9", "t9", 0x7FFF)  # signed: round by 0x8000 (two steps: addiu is signed)
    a.addiu("t9", "t9", 1)
    a.label(label + "_high")
    a.srl("t9", "t9", 16)
    a.srl("t4", "t4", 16)
    a.sll("t4", "t4", 16)
    a.or_("t4", "t4", "t9")
    a.label(label + "_store")
    a.sw("t4", 0, "t2")
    a.beq("zero", "zero", label + "_next")
    a.label(label + "_done")
    a.jr_ra()
    a.nop()


def emit_fixed(
    a: Assembler,
    loader: int,
    file_id: int,
    link_base: int,
    blob_offset: int,
    table_offset: int,
    refs: list[StockRef],
    trampolines: list[int],
) -> dict[int, str]:
    """The fixed part: ``rel_load`` (the wrapper for ``jal loader`` with ``a0 = file_id``
    in the delay slot), the relocator, one trampoline per entry of ``trampolines``
    (blob offsets, labels ``rel_tramp<k>``) and the reference table. Returns
    ``{blob offset: trampoline label}``."""

    a.label("rel_load")
    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x1C, "sp")
    a.sw("a1", 0x18, "sp")
    a.jal(loader)  # a0 = file_id (the stock delay slot)
    a.sw("v0", 0x14, "sp")
    a.sw("v1", 0x10, "sp")
    a.lw("t0", 0x18, "sp")  # file base (KSEG0)
    a.li("t1", KSEG1_BIT)
    a.or_("t0", "t0", "t1")
    a.li("t1", blob_offset)
    a.addu("a0", "t0", "t1")  # blob (KSEG1)
    a.li("t1", table_offset)
    a.addu("a1", "t0", "t1")
    a.li("t1", link_base)
    a.subu("a2", "a0", "t1")  # delta
    a.sw("a0", 0x0C, "sp")
    a.jal_label("rel_apply")
    a.lw("t0", 0x0C, "sp")
    a.la("t1", "rel_refs")
    a.label("rel_ref")
    a.lw("t2", 0, "t1")  # stock address
    a.beqz("t2", "rel_refs_done")
    a.lw("t3", 4, "t1")
    a.addiu("t1", "t1", 8)
    a.sll("t4", "t3", 1)
    a.srl("t4", "t4", 1)  # offset
    a.addu("t4", "t0", "t4")  # KSEG1 address in the blob
    a.bgez("t3", "rel_ref_store")
    a.li("t5", ~KSEG1_BIT & M)
    a.and_("t4", "t4", "t5")  # cached alias
    a.label("rel_ref_store")
    a.sw("t4", 0, "t2")
    a.beq("zero", "zero", "rel_ref")
    a.label("rel_refs_done")
    a.lw("v0", 0x14, "sp")
    a.lw("v1", 0x10, "sp")
    a.lw("a1", 0x18, "sp")
    a.li("a0", file_id)
    a.lw("ra", 0x1C, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x20)

    emit_relocator(a)

    labels = {}
    for k, offset in enumerate(trampolines):
        label = f"rel_tramp{k}"
        labels[offset] = label
        a.label(label)
        slot = f"rel_slot{k}"
        a.la("t9", slot)
        a.lw("t9", 0, "t9")
        a.jr("t9")
        a.nop()
    for k in range(len(trampolines)):
        a.label(f"rel_slot{k}")
        a.raw(0)

    a.label("rel_refs")
    for ref in refs:
        if ref.offset >> 31:
            raise RelocationError("blob offset too large")
        a.raw(ref.address)
        a.raw(ref.offset | (0x80000000 if ref.kseg0 else 0))
    for k, offset in enumerate(trampolines):
        a.word_label(f"rel_slot{k}")
        a.raw(offset)
    a.raw(0)
    return labels


__all__ = [
    "KIND_JUMP",
    "KIND_PAIR_ORI",
    "KIND_PAIR_SIGNED",
    "KIND_WORD",
    "Reloc",
    "RelocationError",
    "StockRef",
    "apply",
    "emit_fixed",
    "emit_relocator",
    "encode",
    "find",
]
