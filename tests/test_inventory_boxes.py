from mkmszr.mips import jal
from mkmszr.patches.base import PatchContext
from mkmszr.patches.inventory_boxes import (
    ACTION_HOOK_ROM,
    ACTION_ROUTINE,
    ACTION_ROUTINE_VA,
    BOX_DATA_ROM,
    BOX_DATA_SIZE,
    COPY10_VA,
    DEFAULT_INV,
    DEFAULT_INV_ROM,
    INITIAL_BOX_DATA,
    MAGIC,
    RELOCATED_MAPPER,
    RELOCATED_MAPPER_ROM,
    RELOCATED_MAPPER_VA,
    SECONDARY_CAVE_ROM,
    SECONDARY_CAVE_SIZE,
    SELECTOR_CAVE_BLOB,
    SELECTOR_CAVE_ROM,
    SELECTOR_CAVE_SIZE,
    SWITCH_HELPER_VA,
    FourBoxInventoryExperimentPatch,
)
from mkmszr.patches.stage_selector import (
    MAPPER_ROM,
    MAPPER_VA,
    SELECTION_LOAD_ROM,
    build_selection_mapper,
)
from mkmszr.rom import RomImage


def _post_core_shape() -> RomImage:
    size = BOX_DATA_ROM + BOX_DATA_SIZE
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

    return RomImage(data=data, _original=bytes(data))


def test_four_box_binary_layout_fits_confirmed_regions() -> None:
    assert len(ACTION_ROUTINE) <= SECONDARY_CAVE_SIZE == 0x68
    assert len(SELECTOR_CAVE_BLOB) <= SELECTOR_CAVE_SIZE == 0x90
    assert len(RELOCATED_MAPPER) == 0x20
    assert RELOCATED_MAPPER_ROM + len(RELOCATED_MAPPER) == 0x0009AF1C
    assert COPY10_VA >= SWITCH_HELPER_VA
    assert len(INITIAL_BOX_DATA) == BOX_DATA_SIZE == 0xA8
    assert INITIAL_BOX_DATA[:40] == DEFAULT_INV
    assert INITIAL_BOX_DATA[40:160] == b"\xFF" * 120
    assert int.from_bytes(INITIAL_BOX_DATA[160:164], "big") == 0
    assert int.from_bytes(INITIAL_BOX_DATA[164:168], "big") == MAGIC


def test_four_box_experiment_installs_expected_hooks_and_backing() -> None:
    rom = _post_core_shape()

    notes = FourBoxInventoryExperimentPatch().apply(rom, PatchContext())

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
    assert "phase 1" in notes[-1]
