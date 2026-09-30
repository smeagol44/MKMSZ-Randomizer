from mkmszr.mips import jal, words_blob
from mkmszr.patches.base import PatchContext
from mkmszr.patches.stage_selector import (
    A_ROUTE_JAL_ROM,
    CONFIRM_SFX_HELPER,
    CONFIRM_SFX_HELPER_ROM,
    CONFIRM_SFX_HELPER_VA,
    CONFIRM_SFX_HOOK_ROM,
    COUNT_ROM,
    CURSOR_PALETTE_COUNT,
    DEAD_SELECTOR_EPILOGUE,
    DEBUG_MENU_VA,
    EXPECTED_A_ROUTE_JAL,
    EXPECTED_CONFIRM_SFX_HOOK,
    EXPECTED_COUNT,
    EXPECTED_MOVE_SFX_HOOK,
    EXPECTED_SELECTION_LOAD,
    EXPECTED_SELECTOR_CURSOR_PALETTE,
    EXPECTED_TITLE_CURSOR_PALETTE,
    EXPECTED_WRAP_LAST,
    MAPPER_CAVE_END,
    MAPPER_ROM,
    MAPPER_VA,
    MENU_TABLE_ROM,
    MOVE_SFX_HELPER,
    MOVE_SFX_HELPER_ROM,
    MOVE_SFX_HELPER_VA,
    MOVE_SFX_HOOK_ROM,
    ORIGINAL_MENU_POINTERS,
    PATCHED_COUNT,
    PATCHED_WRAP_LAST,
    SAFE_MENU_POINTERS,
    SELECTION_LOAD_ROM,
    SELECTOR_CURSOR_PALETTE_ROM,
    TITLE_CURSOR_PALETTE_ROM,
    WRAP_LAST_ROM,
    SafeStageSelectorPatch,
    build_selection_mapper,
)
from mkmszr.rom import RomImage


def _selector_shape() -> RomImage:
    size = max(
        MAPPER_CAVE_END,
        MENU_TABLE_ROM + 48,
        TITLE_CURSOR_PALETTE_ROM + len(EXPECTED_TITLE_CURSOR_PALETTE),
        MOVE_SFX_HELPER_ROM + len(DEAD_SELECTOR_EPILOGUE),
        CONFIRM_SFX_HELPER_ROM + len(DEAD_SELECTOR_EPILOGUE),
        CONFIRM_SFX_HOOK_ROM + len(EXPECTED_CONFIRM_SFX_HOOK),
    )
    data = bytearray(size)
    data[A_ROUTE_JAL_ROM : A_ROUTE_JAL_ROM + 4] = EXPECTED_A_ROUTE_JAL.to_bytes(4, "big")
    data[WRAP_LAST_ROM : WRAP_LAST_ROM + 4] = EXPECTED_WRAP_LAST.to_bytes(4, "big")
    data[COUNT_ROM : COUNT_ROM + 4] = EXPECTED_COUNT.to_bytes(4, "big")
    data[MENU_TABLE_ROM : MENU_TABLE_ROM + 48] = words_blob(ORIGINAL_MENU_POINTERS)
    data[SELECTION_LOAD_ROM : SELECTION_LOAD_ROM + 8] = EXPECTED_SELECTION_LOAD
    data[MAPPER_ROM:MAPPER_CAVE_END] = bytes(MAPPER_CAVE_END - MAPPER_ROM)

    data[SELECTOR_CURSOR_PALETTE_ROM - 4 : SELECTOR_CURSOR_PALETTE_ROM] = (
        CURSOR_PALETTE_COUNT.to_bytes(4, "big")
    )
    data[TITLE_CURSOR_PALETTE_ROM - 4 : TITLE_CURSOR_PALETTE_ROM] = (
        CURSOR_PALETTE_COUNT.to_bytes(4, "big")
    )
    data[
        SELECTOR_CURSOR_PALETTE_ROM:
        SELECTOR_CURSOR_PALETTE_ROM + len(EXPECTED_SELECTOR_CURSOR_PALETTE)
    ] = EXPECTED_SELECTOR_CURSOR_PALETTE
    data[
        TITLE_CURSOR_PALETTE_ROM:
        TITLE_CURSOR_PALETTE_ROM + len(EXPECTED_TITLE_CURSOR_PALETTE)
    ] = EXPECTED_TITLE_CURSOR_PALETTE

    data[MOVE_SFX_HOOK_ROM : MOVE_SFX_HOOK_ROM + len(EXPECTED_MOVE_SFX_HOOK)] = (
        EXPECTED_MOVE_SFX_HOOK
    )
    data[
        CONFIRM_SFX_HOOK_ROM:
        CONFIRM_SFX_HOOK_ROM + len(EXPECTED_CONFIRM_SFX_HOOK)
    ] = EXPECTED_CONFIRM_SFX_HOOK
    data[
        MOVE_SFX_HELPER_ROM:
        MOVE_SFX_HELPER_ROM + len(DEAD_SELECTOR_EPILOGUE)
    ] = DEAD_SELECTOR_EPILOGUE
    data[
        CONFIRM_SFX_HELPER_ROM:
        CONFIRM_SFX_HELPER_ROM + len(DEAD_SELECTOR_EPILOGUE)
    ] = DEAD_SELECTOR_EPILOGUE

    return RomImage(data=data, _original=bytes(data))


def test_safe_stage_selector_is_guarded_and_title_only() -> None:
    rom = _selector_shape()

    notes = SafeStageSelectorPatch().apply(rom, PatchContext())

    assert rom.read_u32(A_ROUTE_JAL_ROM) == jal(DEBUG_MENU_VA)
    assert rom.read_u32(WRAP_LAST_ROM) == PATCHED_WRAP_LAST
    assert rom.read_u32(COUNT_ROM) == PATCHED_COUNT
    assert rom.data[MENU_TABLE_ROM : MENU_TABLE_ROM + 48] == words_blob(SAFE_MENU_POINTERS)
    assert rom.read_u32(SELECTION_LOAD_ROM) == jal(MAPPER_VA)
    assert rom.read_u32(SELECTION_LOAD_ROM + 4) == 0
    assert rom.data[MAPPER_ROM : MAPPER_ROM + len(build_selection_mapper())] == (
        build_selection_mapper()
    )

    assert rom.data[
        SELECTOR_CURSOR_PALETTE_ROM:
        SELECTOR_CURSOR_PALETTE_ROM + len(EXPECTED_TITLE_CURSOR_PALETTE)
    ] == EXPECTED_TITLE_CURSOR_PALETTE

    assert rom.read_u32(MOVE_SFX_HOOK_ROM) == jal(MOVE_SFX_HELPER_VA)
    # The second original word stays in the JAL delay slot.
    assert rom.data[MOVE_SFX_HOOK_ROM + 4 : MOVE_SFX_HOOK_ROM + 8] == (
        EXPECTED_MOVE_SFX_HOOK[4:8]
    )
    assert rom.data[
        MOVE_SFX_HELPER_ROM:
        MOVE_SFX_HELPER_ROM + len(MOVE_SFX_HELPER)
    ] == MOVE_SFX_HELPER

    assert rom.read_u32(CONFIRM_SFX_HOOK_ROM) == jal(CONFIRM_SFX_HELPER_VA)
    # Preserve the native-stage store in the JAL delay slot.
    assert rom.data[CONFIRM_SFX_HOOK_ROM + 4 : CONFIRM_SFX_HOOK_ROM + 8] == (
        EXPECTED_CONFIRM_SFX_HOOK[4:8]
    )
    assert rom.data[
        CONFIRM_SFX_HELPER_ROM:
        CONFIRM_SFX_HELPER_ROM + len(CONFIRM_SFX_HELPER)
    ] == CONFIRM_SFX_HELPER

    assert "Fire" in notes[0]
    assert "title-menu" in notes[1]
    assert "blue palette" in notes[2]
    assert "0x1FC" in notes[3]
    assert "pending manual runtime validation" in notes[4]
    assert "stage-loader" in notes[5]


def test_selector_cursor_and_audio_guards_reject_drift() -> None:
    for offset in (
        SELECTOR_CURSOR_PALETTE_ROM,
        TITLE_CURSOR_PALETTE_ROM,
        MOVE_SFX_HOOK_ROM,
        CONFIRM_SFX_HOOK_ROM,
        MOVE_SFX_HELPER_ROM,
        CONFIRM_SFX_HELPER_ROM,
    ):
        rom = _selector_shape()
        rom.data[offset] ^= 0x01
        try:
            SafeStageSelectorPatch().apply(rom, PatchContext())
        except Exception:
            pass
        else:
            raise AssertionError(f"selector presentation guard did not reject drift at 0x{offset:X}")
