"""Sektor presentation: Power Ups help text and the outfit on Sektor's palette."""

from __future__ import annotations

import pytest

from mkmszr.fighter_import import outfit, power_help
from mkmszr.patches import palette as pal
from mkmszr.patches.power_order import POWER_HELP, POWER_NAMES


def _stock_rom(order: tuple[str, ...] = POWER_NAMES) -> bytearray:
    """A ROM with the stock help table (``order``), records and pinned string only."""

    rom = bytearray(0xB0000)
    for i, name in enumerate(order):
        off = power_help.HELP_TABLE_ROM + 4 * i
        rom[off : off + 4] = POWER_HELP[name].to_bytes(4, "big")
    for va, text in power_help.PINNED.items():
        off = va - power_help.VA_TO_ROM
        rom[off : off + len(text) + 1] = text.encode() + b"\0"
    return rom


@pytest.mark.parametrize("order", [POWER_NAMES, tuple(reversed(POWER_NAMES))])
def test_help_follows_the_slot_order(order) -> None:
    rom = _stock_rom(order)
    for off, data in power_help.edits(bytes(rom)).items():
        rom[off : off + len(data)] = data
    shown = power_help.read_help(bytes(rom))
    assert shown == [power_help.SEKTOR_HELP[name] for name in order]
    for va, text in power_help.PINNED.items():
        off = va - power_help.VA_TO_ROM
        assert rom[off : off + len(text) + 1] == text.encode() + b"\0"


def test_help_stays_inside_the_stock_blocks() -> None:
    rom = bytes(_stock_rom())
    out = power_help.edits(rom)
    v = power_help.VA_TO_ROM
    assert set(out) == {
        power_help.RECORDS[0] - v,
        power_help.STRINGS[0] - v,
        power_help.HELP_TABLE_ROM,
    }
    assert len(out[power_help.RECORDS[0] - v]) == power_help.RECORDS[1] - power_help.RECORDS[0]
    assert len(out[power_help.STRINGS[0] - v]) == power_help.STRINGS[1] - power_help.STRINGS[0]


def test_help_rejects_bad_text_and_tables() -> None:
    rom = bytes(_stock_rom())
    with pytest.raises(power_help.HelpError):
        power_help.edits(rom, {**power_help.SEKTOR_HELP, "slide": (("SEKTOR'S SLIDE",),)})
    with pytest.raises(power_help.HelpError):
        power_help.edits(rom, {**power_help.SEKTOR_HELP, "slide": (("X" * 19,),)})
    broken = bytearray(rom)
    broken[power_help.HELP_TABLE_ROM : power_help.HELP_TABLE_ROM + 4] = bytes(4)
    with pytest.raises(power_help.HelpError):
        power_help.edits(bytes(broken))


def _file_with_palette(words: list[int]) -> bytearray:
    data = bytearray(outfit.PALETTE_OFFSET + 0x80)
    for i, word in enumerate(words):
        off = outfit.PALETTE_OFFSET + 2 * i
        data[off : off + 2] = word.to_bytes(2, "big")
    return data


SEKTOR16 = [0x0000, 0x8001, 0xF39C, 0xAD79, 0xA94A, 0x8435, 0xD294, 0x842C,
            0x9084, 0x90B2, 0xB9CE, 0xC63C, 0xE73A, 0x843A, 0x98F7, 0x98C6]  # fmt: skip


def test_outfit_recolors_only_the_red_entries() -> None:
    data = _file_with_palette(SEKTOR16)
    for mode in ("vanilla", "red"):
        assert outfit.recolor(data, mode) == data
    purple = outfit.recolor(data, "purple")
    changed = [i for i in range(16) if purple[outfit.PALETTE_OFFSET + 2 * i : outfit.PALETTE_OFFSET + 2 * i + 2]
               != data[outfit.PALETTE_OFFSET + 2 * i : outfit.PALETTE_OFFSET + 2 * i + 2]]  # fmt: skip
    assert changed == list(outfit.RED_ENTRIES)
    word = int.from_bytes(purple[outfit.PALETTE_OFFSET + 10 : outfit.PALETTE_OFFSET + 12], "big")
    assert word == pal.make_hue(0x8435, pal.PRESET_HUES["purple"])
    green = outfit.recolor(data, "green")
    r, g, b, _ = pal.decode_bgr555(
        int.from_bytes(green[outfit.PALETTE_OFFSET + 10 : outfit.PALETTE_OFFSET + 12], "big")
    )
    assert (r, g, b) == (1, 21, 1)
    assert outfit.recolor(data, "seeded", seed="X") == outfit.recolor(data, "seeded", seed="X")
    with pytest.raises(ValueError):
        outfit.recolor(data, "hue")
