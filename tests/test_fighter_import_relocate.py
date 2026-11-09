"""Relocatable payload blob: diff-found relocations, MIPS relocator, load wrapper."""

from __future__ import annotations

import random

import pytest
from mips_eval import Machine

from mkmszr.fighter_import import relocate as rel
from mkmszr.fighter_import.host import hi, lo
from mkmszr.fighter_import.mips import Assembler

LINK = 0xA01AF420
M = 0xFFFFFFFF


def _payload(base: int) -> bytes:
    """A payload using every address form the Sektor payload does."""

    a = Assembler(base)
    a.label("entry")
    a.la("t0", "data")  # lui/ori
    a.lw("t1", 0, "t0")
    a.jal_label("leaf")  # internal jal
    a.j_label("tail")  # internal j
    a.label("leaf")
    target = base + 0x80  # a Python-computed address (lifted-code style)
    a.lui("a0", hi(target))
    a.addiu("a0", "a0", lo(target))  # lui/addiu (signed low)
    a.lui("t2", hi(base + 0x8A00))
    a.lw("t3", lo(base + 0x8A00), "t2")  # lui/lw
    a.jal(0x80028794)  # stock call: never relocated
    a.jr_ra()
    a.nop()
    a.label("tail")
    a.li("t4", 0x12345678)  # constant: never relocated
    a.jr_ra()
    a.nop()
    while a.pc() < base + 0x80:
        a.nop()
    a.label("data")
    a.word_label("leaf")  # data pointer
    a.raw((a.labels["leaf"] & ~0x20000000) & M)  # cached alias pointer
    a.raw(0xDEADBEEF)
    return a.link()


def test_find_and_apply_reproduce_a_third_link() -> None:
    a, b, c = _payload(LINK), _payload(LINK + 0x12340), _payload(LINK + 0x2468C)
    relocs = rel.find(a, b, 0x12340)
    kinds = sorted(r.kind for r in relocs)
    assert kinds.count(rel.KIND_WORD) == 2 and kinds.count(rel.KIND_JUMP) == 2
    assert kinds.count(rel.KIND_PAIR_ORI) == 1 and kinds.count(rel.KIND_PAIR_SIGNED) == 2
    assert rel.apply(a, relocs, 0x12340) == b
    assert rel.apply(a, relocs, 0x2468C) == c
    assert rel.apply(c, relocs, -0x2468C) == a


def test_find_rejects_length_changes_and_unknown_changes() -> None:
    a = _payload(LINK)
    with pytest.raises(rel.RelocationError):
        rel.find(a, a + bytes(4), 0x12340)
    broken = bytearray(_payload(LINK + 0x12340))
    broken[-4:] = b"\x11\x22\x33\x44"
    with pytest.raises(rel.RelocationError):
        rel.find(a, bytes(broken), 0x12340)


def test_mips_relocator_matches_the_model() -> None:
    blob = _payload(LINK)
    relocs = rel.find(blob, _payload(LINK + 0x12340), 0x12340)
    table = rel.encode(relocs)
    code = Assembler(0xA0100000)
    rel.emit_relocator(code)
    rng = random.Random(5)
    for delta in [0x1C4BC0, -0x40, 0x7FF0, 0x8010] + [
        rng.randrange(0, 0x100000, 4) for _ in range(40)
    ]:
        m = Machine(code.link(), 0xA0100000)
        at, tab = 0xA0300000, 0xA0380000
        for i in range(0, len(blob), 4):
            m.store(at + i, int.from_bytes(blob[i : i + 4], "big"))
        for i in range(0, len(table), 4):
            m.store(tab + i, int.from_bytes(table[i : i + 4], "big"))
        m.regs[4], m.regs[5], m.regs[6], m.regs[31] = at, tab, delta & M, 0x80001000
        assert m.run(code.labels["rel_apply"]).target == 0x80001000
        got = b"".join(m.load(at + i).to_bytes(4, "big") for i in range(0, len(blob), 4))
        assert got == rel.apply(blob, relocs, delta), hex(delta)


def test_load_wrapper_relocates_and_refreshes_the_stock_pointers() -> None:
    blob = _payload(LINK)
    relocs = rel.find(blob, _payload(LINK + 0x12340), 0x12340)
    table = rel.encode(relocs)
    blob_off, table_off = 0x34500, 0x34500 + len(blob)
    refs = [rel.StockRef(0x800B0F44, 0x0), rel.StockRef(0x800AF4D0, 0x80, kseg0=True)]
    fixed = Assembler(0xA01AF420)
    labels = rel.emit_fixed(fixed, 0x80065D64, 0x87, LINK, blob_off, table_off, refs, [0x20])
    assert labels == {0x20: "rel_tramp0"}
    m = Machine(fixed.link(), 0xA01AF420)
    base = 0x80230008  # where the arena put file 0x87
    m.regs[4], m.regs[5], m.regs[29], m.regs[31] = 0x87, base, 0x80200000, 0x8000DF58
    stop = m.run(fixed.labels["rel_load"] & ~0x20000000)  # entered by a cached jal
    assert stop.kind == "call" and stop.target & 0x1FFFFFFF == 0x00065D64
    assert (m.regs[4], m.regs[5]) == (0x87, base)
    file = base | 0x20000000
    for i in range(0, len(blob), 4):  # what the loader's DMA wrote
        m.store(file + blob_off + i, int.from_bytes(blob[i : i + 4], "big"))
    for i in range(0, len(table), 4):
        m.store(file + table_off + i, int.from_bytes(table[i : i + 4], "big"))
    m.regs[2], m.regs[3] = 0x1111, 0x2222  # loader results to preserve
    stop = m.run(stop.resume)
    assert stop.kind == "return" and stop.target == 0x8000DF58
    assert (m.regs[2], m.regs[3], m.regs[4], m.regs[5], m.regs[29]) == (
        0x1111,
        0x2222,
        0x87,
        base,
        0x80200000,
    )
    at = file + blob_off
    want = rel.apply(blob, relocs, at - LINK)
    got = b"".join(m.load(at + i).to_bytes(4, "big") for i in range(0, len(blob), 4))
    assert got == want
    assert m.load(0x800B0F44) == at and m.load(0x800AF4D0) == (at + 0x80) & ~0x20000000
    # the trampoline jumps through its slot with a0-a3 and ra intact
    m.regs[4:8], m.regs[31] = [1, 2, 3, 4], 0x8005BCDC
    stop = m.run(fixed.labels["rel_tramp0"])
    assert stop.kind == "return" and stop.target == at + 0x20
    assert m.regs[4:8] == [1, 2, 3, 4] and m.regs[31] == 0x8005BCDC
