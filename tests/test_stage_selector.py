from mkmszr.mips import jal, jump, words_blob
from mkmszr.patches.base import PatchContext
from mkmszr.patches.stage_selector import (
    A_ROUTE_JAL_ROM,
    COUNT_ROM,
    DEBUG_MENU_VA,
    EXPECTED_A_ROUTE_JAL,
    EXPECTED_COUNT,
    EXPECTED_SELECTION_LOAD,
    EXPECTED_STAGE_LOADER_PROLOGUE,
    EXPECTED_WRAP_LAST,
    GATE_ROM,
    GATE_VA,
    MAPPER_ROM,
    MAPPER_VA,
    MENU_TABLE_ROM,
    ORIGINAL_MENU_POINTERS,
    PATCHED_COUNT,
    PATCHED_WRAP_LAST,
    SAFE_MENU_POINTERS,
    SELECTION_LOAD_ROM,
    STAGE_CODE_CAVE_END,
    STAGE_LOADER_PROLOGUE_ROM,
    WRAP_LAST_ROM,
    SafeStageSelectorPatch,
    build_loader_gate,
    build_selection_mapper,
)
from mkmszr.rom import RomImage


def _selector_shape() -> RomImage:
    size = max(STAGE_CODE_CAVE_END, MENU_TABLE_ROM + 48)
    data = bytearray(size)
    data[A_ROUTE_JAL_ROM : A_ROUTE_JAL_ROM + 4] = EXPECTED_A_ROUTE_JAL.to_bytes(4, "big")
    data[WRAP_LAST_ROM : WRAP_LAST_ROM + 4] = EXPECTED_WRAP_LAST.to_bytes(4, "big")
    data[COUNT_ROM : COUNT_ROM + 4] = EXPECTED_COUNT.to_bytes(4, "big")
    data[MENU_TABLE_ROM : MENU_TABLE_ROM + 48] = words_blob(ORIGINAL_MENU_POINTERS)
    data[SELECTION_LOAD_ROM : SELECTION_LOAD_ROM + 8] = EXPECTED_SELECTION_LOAD
    data[
        STAGE_LOADER_PROLOGUE_ROM : STAGE_LOADER_PROLOGUE_ROM + 8
    ] = EXPECTED_STAGE_LOADER_PROLOGUE
    data[GATE_ROM:STAGE_CODE_CAVE_END] = bytes(STAGE_CODE_CAVE_END - GATE_ROM)
    return RomImage(data=data, _original=bytes(data))


def test_safe_stage_selector_is_guarded_and_exact() -> None:
    rom = _selector_shape()

    notes = SafeStageSelectorPatch().apply(rom, PatchContext())

    assert rom.read_u32(A_ROUTE_JAL_ROM) == jal(DEBUG_MENU_VA)
    assert rom.read_u32(WRAP_LAST_ROM) == PATCHED_WRAP_LAST
    assert rom.read_u32(COUNT_ROM) == PATCHED_COUNT
    assert rom.data[MENU_TABLE_ROM : MENU_TABLE_ROM + 48] == words_blob(SAFE_MENU_POINTERS)
    assert rom.read_u32(STAGE_LOADER_PROLOGUE_ROM) == jump(GATE_VA)
    assert rom.read_u32(STAGE_LOADER_PROLOGUE_ROM + 4) == 0
    assert rom.data[GATE_ROM : GATE_ROM + len(build_loader_gate())] == build_loader_gate()
    assert rom.read_u32(SELECTION_LOAD_ROM) == jal(MAPPER_VA)
    assert rom.read_u32(SELECTION_LOAD_ROM + 4) == 0
    assert rom.data[MAPPER_ROM : MAPPER_ROM + len(build_selection_mapper())] == (
        build_selection_mapper()
    )
    assert "Fire" in notes[0]
