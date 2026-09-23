from mkmszr.patches.runtime_v2 import (
    CODE_CACHED_BASE,
    CODE_SIZE,
    STATE_CACHED_BASE,
    STATE_HEADER_SIZE,
    STATE_MAGIC,
    STATE_SIZE,
    STATE_VERSION,
)


def test_runtime_v2_repartitions_only_existing_reserved_kib() -> None:
    assert CODE_CACHED_BASE == 0x801AF420
    assert CODE_SIZE == 0x3B0
    assert STATE_CACHED_BASE == 0x801AF7D0
    assert STATE_SIZE == 0x50
    assert STATE_CACHED_BASE + STATE_SIZE == 0x801AF820


def test_runtime_v2_header_contract_is_versioned() -> None:
    assert STATE_MAGIC == 0x4D4B5356
    assert STATE_VERSION == 2
    assert STATE_HEADER_SIZE == 0x20
