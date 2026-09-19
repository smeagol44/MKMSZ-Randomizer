from mkmszr.mips import jal
from mkmszr.patches.base import PatchContext
from mkmszr.patches.inventory_boxes import (
    ACTION_HOOK_ROM,
    ACTION_ROUTINE,
    ACTION_ROUTINE_VA,
    BOX_DATA_ROM,
    BOX_DATA_SIZE,
    DEFAULT_INV,
    DEFAULT_INV_ROM,
    EXPECTED_DEFAULT_LOADER,
    EXPECTED_PERSISTENCE_RESUME,
    EXPECTED_SANITIZER,
    INITIAL_BOX_DATA,
    KEY_STAGE_BY_ITEM,
    KEY_STAGE_TABLE,
    LIVE_INV_ROM,
    LOAD_DEFAULT_END,
    LOAD_DEFAULT_ROM,
    LOAD_MASK_WRAPPER_VA,
    MAGIC,
    MASK_COPY_ROUTINE,
    PERSISTENCE_CODE_END_ROM,
    PERSISTENCE_RESUME_PATCH,
    PERSISTENCE_RESUME_ROM,
    PERSISTENCE_SAVE_ROM,
    RAW_LIVE_INV,
    RELOCATED_MAPPER,
    RELOCATED_MAPPER_ROM,
    RELOCATED_MAPPER_VA,
    SANITIZE_CALL_ROMS,
    SANITIZE_END,
    SANITIZE_ROM,
    SANITIZE_VA,
    SAVE_FILTERED_ROUTINE,
    SECONDARY_CAVE_ROM,
    SECONDARY_CAVE_SIZE,
    SELECTOR_CAVE_BLOB,
    SELECTOR_CAVE_ROM,
    SELECTOR_CAVE_SIZE,
    SWITCH_HELPER_SIZE,
    SWITCH_HELPER_VA,
    TRANSITION_SAVE_WRAPPER,
    FourBoxInventoryPatch,
)
from mkmszr.patches.stage_selector import (
    MAPPER_ROM,
    MAPPER_VA,
    SELECTION_LOAD_ROM,
    build_selection_mapper,
)
from mkmszr.rom import RomImage


def _post_core_shape() -> RomImage:
    size = max(BOX_DATA_ROM + BOX_DATA_SIZE, PERSISTENCE_CODE_END_ROM)
    data = bytearray(size)

    mapper = build_selection_mapper()
    mapper_offset = MAPPER_ROM - SELECTOR_CAVE_ROM
    data[
        SELECTOR_CAVE_ROM + mapper_offset :
        SELECTOR_CAVE_ROM + mapper_offset + len(mapper)
    ] = mapper

    data[SELECTION_LOAD_ROM : SELECTION_LOAD_ROM + 4] = jal(MAPPER_VA).to_bytes(
        4, "big"
    )
    data[ACTION_HOOK_ROM : ACTION_HOOK_ROM + 8] = bytes.fromhex(
        "3C03802F 9463CE18"
    )
    data[DEFAULT_INV_ROM : DEFAULT_INV_ROM + len(DEFAULT_INV)] = DEFAULT_INV
    data[LIVE_INV_ROM : LIVE_INV_ROM + len(RAW_LIVE_INV)] = RAW_LIVE_INV
    data[SANITIZE_ROM:SANITIZE_END] = EXPECTED_SANITIZER
    data[LOAD_DEFAULT_ROM:LOAD_DEFAULT_END] = EXPECTED_DEFAULT_LOADER
    for call_rom in SANITIZE_CALL_ROMS:
        data[call_rom : call_rom + 4] = jal(SANITIZE_VA).to_bytes(4, "big")
    data[
        PERSISTENCE_RESUME_ROM :
        PERSISTENCE_RESUME_ROM + len(EXPECTED_PERSISTENCE_RESUME)
    ] = EXPECTED_PERSISTENCE_RESUME

    return RomImage(data=data, _original=bytes(data))


def test_stage_key_map_matches_originating_stage_policy() -> None:
    assert KEY_STAGE_BY_ITEM == bytes(
        [
            0,
            1, 1, 1,
            3, 3, 3,
            2, 2, 2,
            5, 5, 5,
            4, 4, 4,
            8, 8, 8,
            9, 9, 9,
        ]
    )
    assert len(KEY_STAGE_TABLE) == len(DEFAULT_INV) == 40


def test_four_box_binary_layout_fits_confirmed_regions() -> None:
    assert len(ACTION_ROUTINE) <= SECONDARY_CAVE_SIZE == 0x68
    assert SWITCH_HELPER_SIZE == 0x44
    assert LOAD_MASK_WRAPPER_VA == SWITCH_HELPER_VA + SWITCH_HELPER_SIZE
    assert len(SELECTOR_CAVE_BLOB) <= SELECTOR_CAVE_SIZE == 0x90

    assert len(RELOCATED_MAPPER) == 0x20
    assert RELOCATED_MAPPER_ROM + len(RELOCATED_MAPPER) == 0x0009AF1C

    assert len(MASK_COPY_ROUTINE) == SANITIZE_END - SANITIZE_ROM == 0x4C
    assert len(TRANSITION_SAVE_WRAPPER) == LOAD_DEFAULT_END - LOAD_DEFAULT_ROM == 0x34
    assert PERSISTENCE_SAVE_ROM + len(SAVE_FILTERED_ROUTINE) <= PERSISTENCE_CODE_END_ROM

    assert len(INITIAL_BOX_DATA) == BOX_DATA_SIZE == 0xA8
    assert INITIAL_BOX_DATA[:40] == DEFAULT_INV
    assert INITIAL_BOX_DATA[40:160] == b"\xFF" * 120
    assert int.from_bytes(INITIAL_BOX_DATA[160:164], "big") == 0
    assert int.from_bytes(INITIAL_BOX_DATA[164:168], "big") == MAGIC
    assert RAW_LIVE_INV[:12] == DEFAULT_INV[:12]
    assert RAW_LIVE_INV[12:] != DEFAULT_INV[12:]


def test_four_box_patch_installs_stage_masking_and_filtered_sync() -> None:
    rom = _post_core_shape()

    notes = FourBoxInventoryPatch().apply(rom, PatchContext())

    assert rom.read_u32(SELECTION_LOAD_ROM) == jal(RELOCATED_MAPPER_VA)
    assert rom.data[
        RELOCATED_MAPPER_ROM : RELOCATED_MAPPER_ROM + len(RELOCATED_MAPPER)
    ] == RELOCATED_MAPPER
    assert rom.data[
        SELECTOR_CAVE_ROM : SELECTOR_CAVE_ROM + len(SELECTOR_CAVE_BLOB)
    ] == SELECTOR_CAVE_BLOB
    assert rom.data[
        SECONDARY_CAVE_ROM : SECONDARY_CAVE_ROM + len(ACTION_ROUTINE)
    ] == ACTION_ROUTINE
    assert rom.read_u32(ACTION_HOOK_ROM) == jal(ACTION_ROUTINE_VA)
    assert rom.read_u32(ACTION_HOOK_ROM + 4) == 0

    assert rom.data[BOX_DATA_ROM : BOX_DATA_ROM + BOX_DATA_SIZE] == INITIAL_BOX_DATA
    assert rom.data[LIVE_INV_ROM : LIVE_INV_ROM + len(DEFAULT_INV)] == DEFAULT_INV
    assert rom.data[
        DEFAULT_INV_ROM : DEFAULT_INV_ROM + len(KEY_STAGE_TABLE)
    ] == KEY_STAGE_TABLE

    assert rom.data[SANITIZE_ROM:SANITIZE_END] == MASK_COPY_ROUTINE
    for call_rom in SANITIZE_CALL_ROMS:
        assert rom.read_u32(call_rom) == 0

    assert rom.data[
        LOAD_DEFAULT_ROM:LOAD_DEFAULT_END
    ] == TRANSITION_SAVE_WRAPPER
    assert rom.data[
        PERSISTENCE_RESUME_ROM :
        PERSISTENCE_RESUME_ROM + len(PERSISTENCE_RESUME_PATCH)
    ] == PERSISTENCE_RESUME_PATCH
    assert rom.data[
        PERSISTENCE_SAVE_ROM :
        PERSISTENCE_SAVE_ROM + len(SAVE_FILTERED_ROUTINE)
    ] == SAVE_FILTERED_ROUTINE

    assert "Glass (0x08)" in notes[-2]
