from mkmszr.data.pickups import IDENTITY_OFFSET, STAGE_PICKUPS
from mkmszr.mips import jal
from mkmszr.patches.base import PatchContext
from mkmszr.patches.progression_presentation import (
    FLASH_ACTIVE_FLAG_OFFSET,
    FLASH_ACTIVE_FLAG_ROM,
    FLASH_CHILD_CALLBACK_ENTRY,
    FLASH_HELPER_OFFSET,
    FLASH_HELPER_ROM,
    FLASH_HELPER_SIZE,
    FLASH_MODULE_END_ROM,
    FLASH_MODULE_K0,
    FLASH_MODULE_ROM,
    FLASH_MODULE_SIZE,
    PRODUCTION_FLASH_HELPER,
    PROGRESSION_FLASH_CALLBACK_ENTRY,
    WATER_EEL_WHITE_PALETTE_ROM,
    WHITE_FLASH_PALETTE,
    WHITE_PALETTE_ROM,
    ProgressionPickupPresentationPatch,
)
from mkmszr.patches.temple_special_check import (
    EXPANSION_FILE_ENTRY_ROM,
    EXPANSION_FILE_ROM,
)
from mkmszr.patches.xp_progression import (
    CALLBACK_OFFSET_WITHIN_IDENTITY,
    PRESENTATION_OFFSET_WITHIN_IDENTITY,
    PROGRESSION_CALLBACK_ENTRY,
    PROGRESSION_HERBS_PRESENTATION_VA,
    build_progression_locations,
)
from mkmszr.rom import RomImage


def _post_progression_shape(seed: str) -> RomImage:
    selected = build_progression_locations(seed)
    stage_by_id = {stage.stage_id: stage for stage in STAGE_PICKUPS}
    end = max(
        FLASH_MODULE_END_ROM,
        WATER_EEL_WHITE_PALETTE_ROM + len(WHITE_FLASH_PALETTE),
        EXPANSION_FILE_ENTRY_ROM + 12,
        max(
            stage_by_id[stage_id].records[destination].rom_base + 0x30
            for stage_id, destination in selected
        ),
    )
    data = bytearray(end)
    data[EXPANSION_FILE_ENTRY_ROM : EXPANSION_FILE_ENTRY_ROM + 12] = (
        EXPANSION_FILE_ROM.to_bytes(4, "big")
        + (FLASH_MODULE_ROM - 0x20).to_bytes(4, "big")
        + bytes(4)
    )
    data[
        WATER_EEL_WHITE_PALETTE_ROM :
        WATER_EEL_WHITE_PALETTE_ROM + len(WHITE_FLASH_PALETTE)
    ] = WHITE_FLASH_PALETTE
    data[FLASH_MODULE_ROM:FLASH_MODULE_END_ROM] = b"\xFF" * FLASH_MODULE_SIZE

    for stage_id, destination in selected:
        record = stage_by_id[stage_id].records[destination]
        callback = (
            record.rom_base
            + IDENTITY_OFFSET
            + CALLBACK_OFFSET_WITHIN_IDENTITY
        )
        presentation = (
            record.rom_base
            + IDENTITY_OFFSET
            + PRESENTATION_OFFSET_WITHIN_IDENTITY
        )
        data[callback:callback + 4] = PROGRESSION_CALLBACK_ENTRY.to_bytes(4, "big")
        data[presentation:presentation + 4] = (
            PROGRESSION_HERBS_PRESENTATION_VA.to_bytes(4, "big")
        )

    return RomImage(data=data, _original=bytes(data))


def test_async_wrapper_awards_before_spawning_and_contains_no_direct_sleep_jal() -> None:
    words = [
        int.from_bytes(PRODUCTION_FLASH_HELPER[offset:offset + 4], "big")
        for offset in range(0, len(PRODUCTION_FLASH_HELPER), 4)
    ]
    assert jal(PROGRESSION_CALLBACK_ENTRY) in words
    assert jal(0x8002830C) in words
    assert words.index(jal(PROGRESSION_CALLBACK_ENTRY)) < words.index(jal(0x8002830C))
    child_offset = FLASH_CHILD_CALLBACK_ENTRY - PROGRESSION_FLASH_CALLBACK_ENTRY
    assert child_offset > 0
    wrapper_words = words[: child_offset // 4]
    assert jal(0x80028794) not in wrapper_words


def test_flash_module_fits_reserved_expansion_pool() -> None:
    assert FLASH_MODULE_ROM == 0x00F6A940
    assert FLASH_MODULE_K0 == 0x801B2160
    assert FLASH_MODULE_SIZE == 0x1B0
    assert FLASH_HELPER_ROM == FLASH_MODULE_ROM + FLASH_HELPER_OFFSET
    assert FLASH_HELPER_SIZE == 0x12C
    assert FLASH_ACTIVE_FLAG_OFFSET == 0x1AC
    assert FLASH_ACTIVE_FLAG_ROM == FLASH_MODULE_END_ROM - 4
    assert FLASH_MODULE_END_ROM == 0x00F6AAF0
    assert FLASH_MODULE_K0 + FLASH_MODULE_SIZE == 0x801B2310
    assert FLASH_MODULE_K0 + FLASH_MODULE_SIZE < 0x801B3420


def test_white_palette_is_exact_stock_eel_flash_palette() -> None:
    assert len(WHITE_FLASH_PALETTE) == 0x80
    assert WHITE_FLASH_PALETTE[:2] == b"\x00\x00"
    assert WHITE_FLASH_PALETTE[2:] == b"\x7F\xFF" * 63


def test_patch_installs_flash_and_wraps_exactly_nine_progression_pickups() -> None:
    seed = "BCBDBF"
    rom = _post_progression_shape(seed)
    selected = set(build_progression_locations(seed))
    stage_by_id = {stage.stage_id: stage for stage in STAGE_PICKUPS}

    ProgressionPickupPresentationPatch().apply(
        rom, PatchContext(seed=seed)
    )

    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == FLASH_MODULE_END_ROM
    assert (
        rom.data[WHITE_PALETTE_ROM:WHITE_PALETTE_ROM + len(WHITE_FLASH_PALETTE)]
        == WHITE_FLASH_PALETTE
    )
    assert (
        rom.data[FLASH_HELPER_ROM:FLASH_HELPER_ROM + FLASH_HELPER_SIZE]
        == PRODUCTION_FLASH_HELPER
    )
    assert rom.read_u32(FLASH_ACTIVE_FLAG_ROM) == 0

    changed = 0
    for stage_id, destination in selected:
        record = stage_by_id[stage_id].records[destination]
        callback = (
            record.rom_base
            + IDENTITY_OFFSET
            + CALLBACK_OFFSET_WITHIN_IDENTITY
        )
        presentation = (
            record.rom_base
            + IDENTITY_OFFSET
            + PRESENTATION_OFFSET_WITHIN_IDENTITY
        )
        assert rom.read_u32(callback) == PROGRESSION_FLASH_CALLBACK_ENTRY
        assert rom.read_u32(presentation) == PROGRESSION_HERBS_PRESENTATION_VA
        changed += 1
    assert changed == 9
