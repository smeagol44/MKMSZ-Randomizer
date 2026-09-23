from mkmszr.patches.rainbow_palette import (
    FRAME_SETUP_HOOK,
    RAINBOW_FILE_END_ROM,
    RAINBOW_FILE_ROM,
    RAINBOW_HELPER,
    RAINBOW_HELPER_OFFSET,
    RAINBOW_PALETTE_BANK_SIZE,
    SUBZERO_FILE_SIZE,
)
from mkmszr.patches.runtime_v2 import CODE_SIZE, STATE_CACHED_BASE, STATE_SIZE
from mkmszr.patches.xp_progression import PROGRESSION_EXTENSION


def test_runtime_layout_matches_confirmed_rainbow_proof() -> None:
    assert CODE_SIZE == 0x3B0
    assert STATE_CACHED_BASE == 0x801AF7D0
    assert STATE_SIZE == 0x50
    assert STATE_CACHED_BASE + STATE_SIZE == 0x801AF820


def test_rainbow_helper_matches_runtime_confirmed_v01() -> None:
    # The helper begins in the proven-zero tail of the XP extension and then
    # continues through the newly owned Runtime V2 code tail.
    assert PROGRESSION_EXTENSION[RAINBOW_HELPER_OFFSET - 0x200 :] == bytes(0x20)
    assert len(RAINBOW_HELPER) == 0xCC
    assert RAINBOW_HELPER.hex() == (
        "27bdffd8afbf0020afa40010afa5001494880078240900041509002000000000"
        "3c08a01b2508f7d08d090048252a0001314a003fad0a00488c8a0098000959c0"
        "014b20213c0c0004358c59e0008c202124050100000030213c1980022739c528"
        "0320f80900000000244800011100000b000000008faa00109548009e2449ff80"
        "a549009ea5420080250400803c1980022739c64c0320f809000000008fa40010"
        "8fa500148fbf002027bd0028008038218ce40074ace500748ca800003c198002"
        "2739bdb00320000800000000"
    )
    assert FRAME_SETUP_HOOK.hex() == "3c19a01b2739f7000320000800000000"


def test_rainbow_high_rom_bounds_do_not_reach_title_allocation() -> None:
    assert SUBZERO_FILE_SIZE == 0x459E0
    assert RAINBOW_PALETTE_BANK_SIZE == 0x2000
    assert RAINBOW_FILE_ROM == 0xF20000
    assert RAINBOW_FILE_END_ROM == 0xF679E0
    assert RAINBOW_FILE_END_ROM < 0xF90000
