"""Generic combo translation (fighter_import.combos)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import combos as cb

MKT = os.environ.get("MKMSZR_MKT_ROM")
CLEAN = os.environ.get("MKMSZR_CLEAN_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")
needs_clean = pytest.mark.skipif(not CLEAN, reason="needs MKMSZR_CLEAN_ROM")

# Sektor proof v62 (Runtime-confirmed): records in donor order 0x800AF428..0x800AF478, then the
# kick root record 0x800AF508 (v62 placed it in proof space); next pointers excluded.
SEKTOR_V62 = [
    "800910030300100200000000", "000913010303100201000000", "80090b010201100205040000",
    "000913030103100204010000", "800911010103100201000000", "800913030103100204010000",
    "800911010103100204000000",
]  # fmt: skip


@needs_mkt
def test_sektor_translation_reproduces_v62() -> None:
    graph = cb.donor_graph(Path(MKT).read_bytes(), 7)
    assert sorted(cb.strings(graph)) == sorted(
        ["HK, HK", "HP, HP, D+LP", "HP, HP, HK, B+HK", "HP, HP, HK, HK, B+HK"]
    )
    low = cb.lower(graph, None, set(range(0x23)), capacity=8)
    order = [va for lst in graph.lists for va in lst]
    got = {va: low.records[16 * k : 16 * k + 12].hex() for k, va in enumerate(order)}
    donor = [0x800AF428 + 16 * k for k in range(6)] + [0x800AF508]
    assert [got[va] for va in donor] == SEKTOR_V62


@needs_mkt
def test_reptile_strings_and_translation() -> None:
    graph = cb.donor_graph(Path(MKT).read_bytes(), 19)
    assert sorted(cb.strings(graph)) == ["HK, HK, B+HK", "HP, HP, D+LP", "HP, HP, HK, B+HK"]
    low = cb.lower(graph, 0x00, set(range(0x23)))
    assert len(low.records) == 5 * 16 and low.roots == (0x800B10B0, 0x800B10C0)
    assert low.strikes == {0x01: 0x01, 0x05: 0x05, 0x12: 0x04}
    for k in range(5):
        rec = low.records[16 * k : 16 * k + 16]
        assert rec[2] < 0x80 and rec[6] < 0x80  # no table-1 animation left
        nxt = int.from_bytes(rec[12:], "big")
        assert nxt < 0x100 or cb.HOST_RECORDS_VA <= nxt < cb.HOST_RECORDS_VA + 0x50
    with pytest.raises(cb.ComboError):
        cb.lower(graph, None, set(range(0x23)))  # the table-1 animation needs a host slot


@needs_clean
def test_host_graph_is_stock() -> None:
    clean = Path(CLEAN).read_bytes()
    end = cb.HOST_RECORDS_ROM + 16 * cb.HOST_CAPACITY
    assert clean[cb.HOST_RECORDS_ROM : end] == cb.STOCK_RECORDS
    roots = [int.from_bytes(clean[p : p + 4], "big") for p in cb.HOST_ROOT_PTRS_ROM]
    assert tuple(roots) == cb.STOCK_ROOTS
