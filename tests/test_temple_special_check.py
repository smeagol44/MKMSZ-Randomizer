from mkmszr.mips import jal, jump
from mkmszr.patches.base import PatchContext
from mkmszr.patches.temple_special_check import (
    AWARD_HELPER_VA,
    CHECK_HELPER_VA,
    CONTROLS_END_ROM,
    EXPANSION_FILE_ENTRY_ROM,
    EXPANSION_FILE_ROM,
    MAP_AWARD_CALL_ROM,
    MAP_CHECK_HOOK_ROM,
    TEMPLE_MODULE,
    TEMPLE_MODULE_CACHED_BASE,
    TEMPLE_MODULE_END_CACHED,
    TEMPLE_MODULE_END_ROM,
    TEMPLE_MODULE_ROM,
    TEMPLE_MODULE_SIZE,
    TEMPLE_SPECIAL_CHECK_STATE_MASK,
    TOASTY_ROM,
    VISUAL_PATCHES,
    TempleSpecialCheckPatch,
)
from mkmszr.rom import RomImage


def _clean_shape() -> RomImage:
    data = bytearray(0x01000000)
    data[EXPANSION_FILE_ENTRY_ROM : EXPANSION_FILE_ENTRY_ROM + 12] = (
        EXPANSION_FILE_ROM.to_bytes(4, "big")
        + CONTROLS_END_ROM.to_bytes(4, "big")
        + bytes(4)
    )
    data[TEMPLE_MODULE_ROM:TEMPLE_MODULE_END_ROM] = b"\xFF" * TEMPLE_MODULE_SIZE

    for offset, (expected, _replacement) in VISUAL_PATCHES.items():
        data[offset : offset + 4] = expected.to_bytes(4, "big")

    data[MAP_CHECK_HOOK_ROM : MAP_CHECK_HOOK_ROM + 8] = bytes.fromhex(
        "8C420018 30420080"
    )
    data[MAP_AWARD_CALL_ROM : MAP_AWARD_CALL_ROM + 4] = (0x0C01D512).to_bytes(
        4, "big"
    )
    return RomImage(data=data, _original=bytes(data))


def test_temple_special_check_allocation_is_bounded() -> None:
    assert TEMPLE_SPECIAL_CHECK_STATE_MASK == 0x0001
    assert TEMPLE_MODULE_CACHED_BASE == 0x801B08E0
    assert TEMPLE_MODULE_ROM == 0x00F690C0
    assert TEMPLE_MODULE_SIZE == 0x90
    assert TEMPLE_MODULE_END_CACHED == 0x801B0970
    assert TEMPLE_MODULE_END_ROM == 0x00F69150
    assert TEMPLE_MODULE_END_ROM < TOASTY_ROM


def test_temple_special_check_installs_runtime_confirmed_v02_seams() -> None:
    rom = _clean_shape()
    result = TempleSpecialCheckPatch().apply(rom, PatchContext(seed="TEMPLE"))

    assert rom.data[TEMPLE_MODULE_ROM:TEMPLE_MODULE_END_ROM] == TEMPLE_MODULE
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == TEMPLE_MODULE_END_ROM

    for offset, (_expected, replacement) in VISUAL_PATCHES.items():
        assert rom.read_u32(offset) == replacement

    assert rom.read_u32(MAP_CHECK_HOOK_ROM) == jump(CHECK_HELPER_VA)
    assert rom.read_u32(MAP_CHECK_HOOK_ROM + 4) == 0
    assert rom.read_u32(MAP_AWARD_CALL_ROM) == jal(AWARD_HELPER_VA)

    assert "84 ordinary" in result[2]


def test_temple_special_check_composes_with_existing_longer_file_1a() -> None:
    rom = _clean_shape()
    existing_end = TOASTY_ROM + 0x100
    rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, existing_end)

    TempleSpecialCheckPatch().apply(rom, PatchContext(seed="TEMPLE"))

    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == existing_end
    assert rom.data[TEMPLE_MODULE_ROM:TEMPLE_MODULE_END_ROM] == TEMPLE_MODULE
