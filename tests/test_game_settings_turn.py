from mkmszr.patches.game_settings_turn import (
    ACTION_ENTRY,
    CONTROL_ALLOCATION,
    CONTROL_MODULE,
    CONTROL_MODULE_CACHED_BASE,
    RELEASE_ENTRY,
    SETTINGS_UNCACHED_VA,
    SHARED_EXPANSION_ROM,
    STATIC_REGION_BLOB,
    STATIC_REGION_SIZE,
    TOASTY_RUNTIME_BASE,
    build_action_gate_helper,
    build_release_helper,
)
from mkmszr.patches.inventory_boxes import STATE_VA, TURN_LOCK_STATE_MASK


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
