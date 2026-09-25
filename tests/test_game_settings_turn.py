from mkmszr.patches.game_settings_turn import (
    ACTION_ENTRY,
    COMBOS_DRAW_END_ROM,
    COMBOS_DRAW_ROM,
    CONTROL_ALLOCATION,
    CONTROL_MODULE,
    CONTROL_MODULE_CACHED_BASE,
    NAV_DOWN_HELPER_VA,
    NAV_UP_HELPER_VA,
    RELEASE_ENTRY,
    SETTINGS_UNCACHED_VA,
    SHARED_EXPANSION_ROM,
    STATIC_REGION_BLOB,
    STATIC_REGION_SIZE,
    TOASTY_RUNTIME_BASE,
    build_action_gate_helper,
    build_combos_value_draw,
    build_nav_down_helper,
    build_nav_up_helper,
    build_release_helper,
)
from mkmszr.patches.inventory_boxes import (
    COMBOS_ASSIST_STATE_MASK,
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


def test_turn_editor_uses_reserved_runtime_word_and_durable_inventory_state_bit() -> None:
    assert SETTINGS_UNCACHED_VA == 0xA01AF81C
    assert STATE_VA == 0x800A60E8
    assert TURN_LOCK_STATE_MASK == 0x0200
    assert COMBOS_ASSIST_STATE_MASK == 0x0400
    assert USER_SETTINGS_STATE_MASK == 0x0600


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


def test_combos_ui_proof_uses_second_owned_settings_bit() -> None:
    assert COMBOS_ASSIST_STATE_MASK == 0x0400
    assert TURN_LOCK_STATE_MASK & COMBOS_ASSIST_STATE_MASK == 0


def test_combos_menu_reuses_frontend_resident_stock_regions() -> None:
    assert NAV_DOWN_HELPER_VA == 0x80076984
    assert NAV_UP_HELPER_VA == 0x80076A7C
    assert len(build_nav_down_helper()) <= 0x58
    assert len(build_nav_up_helper()) <= 0x20
    assert len(build_combos_value_draw()) == COMBOS_DRAW_END_ROM - COMBOS_DRAW_ROM
