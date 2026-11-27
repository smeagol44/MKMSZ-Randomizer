"""The enlarged sound bank (fighter_import.sound_bank): more host chains than the 16 isolated ones."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import sound_bank as sb

CLEAN = os.environ.get("MKMSZR_CLEAN_ROM")
MKT = os.environ.get("MKMSZR_MKT_ROM")
needs_clean = pytest.mark.skipif(not CLEAN, reason="needs MKMSZR_CLEAN_ROM")
needs_roms = pytest.mark.skipif(not (CLEAN and MKT), reason="needs MKMSZR_CLEAN_ROM and MKMSZR_MKT_ROM")


@needs_clean
def test_the_stock_bank_parses_and_round_trips() -> None:
    """SN64 at 0x947C80: 683 patches, 740 subpatches, 598 waveforms, no drum maps; the books
    end the extra data (8-byte header, 60 loops of 0x30). With no extra chains, the enlarged bank
    is the stock bank, and moving both modules leaves the audio heap use as it was (0x6BBD0)."""

    clean = Path(CLEAN).read_bytes()
    assert sb.module_addresses(clean) == (sb.BANK_ROM, sb.EVENTS_ROM)
    bank = sb.Bank.parse(sb._bank_bytes(clean, sb.BANK_ROM))
    assert bank.counts == (683, 740, 598, 0) and sb.BANK_ROM + bank.books == 0x950490
    assert sb.BANK_ROM + bank.end == sb.EVENTS_ROM
    ext = sb.extension_for(clean)
    assert ext.base == (590, 683, 740, 598)
    assert sb.grown_bank(sb._bank_bytes(clean, sb.BANK_ROM), ext) == sb._bank_bytes(clean, sb.BANK_ROM)
    assert sb.heap_use(clean) == 0x6BBD0
    rom = bytearray(clean) + b"\xff" * 0x1000000
    sb.relocate(rom, ext, 0x01880000, 0x01900000)
    assert sb.module_addresses(rom) == (0x01880000, 0x018AF0C0) and sb.heap_use(rom) == 0x6BBD0
    with pytest.raises(ValueError, match="not stock"):
        sb.relocate(rom, ext, 0x01900000, 0x01980000)


@needs_clean
def test_appended_chains_count_up_and_cost_heap() -> None:
    clean = Path(CLEAN).read_bytes()
    ext = sb.extension_for(clean)
    track = (683).to_bytes(4, "big") + bytes(0x1C)
    for k in range(2):
        ext.records.append((ext.chain(k).patch.to_bytes(4, "big") + track[4:], bytes(20), bytes(24), bytes(264)))
    rom = bytearray(clean) + b"\xff" * 0x1000000
    bank_at, events_at = sb.relocate(rom, ext, 0x01880000, 0x01900000)
    bank = sb.Bank.parse(sb._bank_bytes(rom, bank_at))
    assert bank.counts == (685, 742, 600, 0)
    patch = bank_at + bank.tables[0] + 4 * 684
    assert rom[patch : patch + 4] == bytes([1, 0]) + (741).to_bytes(2, "big")  # one subpatch each
    sub = bank_at + bank.tables[1] + 20 * 741
    assert int.from_bytes(rom[sub + 10 : sub + 12], "big") == 599
    assert int.from_bytes(rom[events_at + 0xC : events_at + 0x10], "big") == 592
    grown = sb.heap_use(rom) - sb.heap_use(clean)
    assert grown == 2 * (4 + 20 + 24 + 264) + 2 * 16 + 2 * 0x30  # no alignment loss here
    assert sb.check_heap(bytes(rom), clean) == grown


@needs_roms
def test_rayden_gets_his_grab_voice_in_an_appended_chain() -> None:
    """Every isolated chain is taken, so his grab voice (MKT 0x66) is event 590 of the enlarged
    bank; the heap grows by 0x1C0 (his Shocker's second track 0x50, the chain 0x170)."""

    from mkmszr.fighter_import import fighter_build as fb

    built = fb.build(Path(CLEAN).read_bytes(), Path(MKT).read_bytes(), "rayden")
    assert built.report["appended_chains"] == 1 and built.report["throw_sounds"] == {"grab": [590]}
    assert built.report["audio_heap_growth"] == 0x1C0 and len(built.rom) == fb.OUTPUT_SIZE
    assert sb.module_addresses(built.rom) == (0x01880000, 0x018AF200)
