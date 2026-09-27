from mkmszr.patches.rainbow_palette import (
    ALLOC_SIZE_DELAY_SITES,
    FRAME_SETUP_HOOK,
    LOAD_JAL_SITES,
    RAINBOW_BANK_END_ROM,
    RAINBOW_BANK_FILE_ID,
    RAINBOW_BANK_ROM,
    RAINBOW_HELPER,
    RAINBOW_HELPER_OFFSET,
    RAINBOW_LOADER_CACHED_VA,
    RAINBOW_LOADER_ROM,
    RAINBOW_LOADER_WRAPPER,
    RAINBOW_PALETTE_BANK_SIZE,
    SUBZERO_FILE_SIZE,
)
from mkmszr.patches.runtime_v2 import CODE_SIZE, STATE_CACHED_BASE, STATE_SIZE
from mkmszr.patches.toasty_constants import MODULE_K0 as TOASTY_RUNTIME_BASE
from mkmszr.patches.xp_progression import PROGRESSION_EXTENSION


def test_runtime_layout_matches_confirmed_compact_rainbow_proof() -> None:
    assert CODE_SIZE == 0x3B0
    assert STATE_CACHED_BASE == 0x801AF7D0
    assert STATE_SIZE == 0x50
    assert STATE_CACHED_BASE + STATE_SIZE == 0x801AF820


def test_compact_rainbow_helper_fills_optional_runtime_tail() -> None:
    # The helper begins in the proven-zero tail of the XP extension and now
    # defensively masks the phase exactly as the all-stage compact proof did.
    assert PROGRESSION_EXTENSION[RAINBOW_HELPER_OFFSET - 0x200 :] == bytes(0x20)
    assert len(RAINBOW_HELPER) == 0xD0
    assert RAINBOW_HELPER_OFFSET + len(RAINBOW_HELPER) == CODE_SIZE
    assert FRAME_SETUP_HOOK.hex() == "3c19a01b2739f7000320000800000000"


def test_compact_rainbow_loader_wrapper_matches_runtime_proof_shape() -> None:
    assert len(RAINBOW_LOADER_WRAPPER) == 0x58
    assert RAINBOW_LOADER_CACHED_VA == 0x801B0880
    assert RAINBOW_LOADER_CACHED_VA + len(RAINBOW_LOADER_WRAPPER) < TOASTY_RUNTIME_BASE
    assert RAINBOW_LOADER_ROM == 0xF69060
    assert RAINBOW_LOADER_WRAPPER.hex() == (
        "27bdffe0afbf001cafa500180c01975900000000afa20014afa300108fa50018"
        "3c080004250859e000a82821240400920c019759000000008fa200148fa30010"
        "8fa50018240400878fbf001c27bd002003e0000800000000"
    )


def test_all_stock_subzero_load_paths_are_covered() -> None:
    assert len(ALLOC_SIZE_DELAY_SITES) == 15
    assert len(LOAD_JAL_SITES) == 15
    assert len(set(ALLOC_SIZE_DELAY_SITES)) == 15
    assert len(set(LOAD_JAL_SITES)) == 15


def test_compact_rainbow_rom_footprint_is_only_palette_bank() -> None:
    assert SUBZERO_FILE_SIZE == 0x459E0
    assert RAINBOW_PALETTE_BANK_SIZE == 0x2000
    assert RAINBOW_BANK_FILE_ID == 0x92
    assert RAINBOW_BANK_ROM == 0xF20000
    assert RAINBOW_BANK_END_ROM == 0xF22000
    assert RAINBOW_BANK_END_ROM < RAINBOW_LOADER_ROM
