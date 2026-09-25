from mkmszr.patches.game_settings_turn import (
    ACTION_ENTRY,
    COMBOS_DRAW_END_ROM,
    COMBOS_DRAW_ROM,
    CONTROL_ALLOCATION,
    CONTROL_MODULE,
    CONTROL_MODULE_CACHED_BASE,
    JUMP_DRAW_HELPER_VA,
    LEFT_EDIT_BLOB,
    LEFT_EDIT_END_ROM,
    LEFT_EDIT_ROM,
    RELEASE_ENTRY,
    RIGHT_EDIT_BLOB,
    RIGHT_EDIT_END_ROM,
    RIGHT_EDIT_ROM,
    SETTINGS_UNCACHED_VA,
    SHARED_EXPANSION_ROM,
    SPECIALS_DRAW_END_ROM,
    SPECIALS_DRAW_ROM,
    STATIC_REGION_BLOB,
    STATIC_REGION_SIZE,
    TOASTY_RUNTIME_BASE,
    build_action_gate_helper,
    build_combos_value_draw,
    build_jump_draw_helper,
    build_release_helper,
    build_specials_value_draw,
)
from mkmszr.patches.inventory_boxes import (
    COMBOS_ASSIST_STATE_MASK,
    JUMP_BUTTON_STATE_MASK,
    SPECIALS_MODERN_STATE_MASK,
    STATE_VA,
    TURN_LOCK_STATE_MASK,
    USER_SETTINGS_STATE_MASK,
)


def _has_link_call(blob: bytes) -> bool:
    for offset in range(0, len(blob), 4):
        word = int.from_bytes(blob[offset : offset + 4], "big")
        opcode = word >> 26
        if opcode == 0x03:  # JAL
            return True
        if opcode == 0 and (word & 0x3F) == 0x09:  # JALR
            return True
    return False


def test_settings_state_bits_are_distinct_and_owned() -> None:
    assert SETTINGS_UNCACHED_VA == 0xA01AF81C
    assert STATE_VA == 0x800A60E8
    assert TURN_LOCK_STATE_MASK == 0x0200
    assert COMBOS_ASSIST_STATE_MASK == 0x0400
    assert SPECIALS_MODERN_STATE_MASK == 0x0800
    assert JUMP_BUTTON_STATE_MASK == 0x1000
    assert USER_SETTINGS_STATE_MASK == 0x1E00


def test_turn_module_uses_low_expansion_slice_before_toasty() -> None:
    assert CONTROL_MODULE_CACHED_BASE == 0x801AF820
    assert CONTROL_ALLOCATION.start == CONTROL_MODULE_CACHED_BASE
    assert CONTROL_ALLOCATION.end_exclusive < TOASTY_RUNTIME_BASE
    assert len(CONTROL_MODULE) == CONTROL_ALLOCATION.size
    assert SHARED_EXPANSION_ROM == 0x00F68000


def test_v06_fragile_helpers_remain_leaf_only() -> None:
    assert not _has_link_call(build_release_helper())
    assert not _has_link_call(build_action_gate_helper())
    assert RELEASE_ENTRY < ACTION_ENTRY


def test_static_loader_trampolines_fit_repurposed_capture_region() -> None:
    assert len(STATIC_REGION_BLOB) == STATIC_REGION_SIZE == 0xD8


def test_full_settings_frontend_fits_reclaimed_stock_regions() -> None:
    assert len(RIGHT_EDIT_BLOB) == RIGHT_EDIT_END_ROM - RIGHT_EDIT_ROM
    assert len(LEFT_EDIT_BLOB) == LEFT_EDIT_END_ROM - LEFT_EDIT_ROM
    assert RIGHT_EDIT_ROM < JUMP_DRAW_HELPER_VA - 0x80000000 + 0xC00 < RIGHT_EDIT_END_ROM


def test_enum_value_draws_fit_stock_draw_regions() -> None:
    assert len(build_combos_value_draw()) == COMBOS_DRAW_END_ROM - COMBOS_DRAW_ROM
    assert len(build_specials_value_draw()) == SPECIALS_DRAW_END_ROM - SPECIALS_DRAW_ROM
    assert len(build_jump_draw_helper()) < RIGHT_EDIT_END_ROM - RIGHT_EDIT_ROM
