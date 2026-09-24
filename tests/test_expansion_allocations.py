import pytest

from mkmszr.allocations import ExpansionPoolAllocator
from mkmszr.data.addresses import (
    EXPANSION_POOL_END_EXCLUSIVE,
    EXPANSION_POOL_START,
    RESERVED_RDRAM_END_EXCLUSIVE,
    RESERVED_RDRAM_START,
)


def test_16k_reservation_keeps_existing_runtime_v2_prefix() -> None:
    assert RESERVED_RDRAM_START == 0x801AF420
    assert RESERVED_RDRAM_END_EXCLUSIVE == 0x801B3420
    assert RESERVED_RDRAM_END_EXCLUSIVE - RESERVED_RDRAM_START == 0x4000
    assert EXPANSION_POOL_START == 0x801AF820
    assert EXPANSION_POOL_END_EXCLUSIVE == 0x801B3420
    assert EXPANSION_POOL_END_EXCLUSIVE - EXPANSION_POOL_START == 0x3C00


def test_expansion_allocator_is_aligned_monotonic_and_bounded() -> None:
    pool = ExpansionPoolAllocator()
    first = pool.allocate("control-assist", 0x123, align=16)
    second = pool.allocate("shared-native-utils", 0x80, align=32)

    assert first.start == EXPANSION_POOL_START
    assert first.end_exclusive == EXPANSION_POOL_START + 0x123
    assert second.start % 32 == 0
    assert second.start >= first.end_exclusive
    assert pool.remaining == EXPANSION_POOL_END_EXCLUSIVE - second.end_exclusive


def test_expansion_allocator_rejects_overflow_and_duplicate_names() -> None:
    pool = ExpansionPoolAllocator()
    pool.allocate("owner", 0x10)
    with pytest.raises(ValueError, match="duplicate"):
        pool.allocate("owner", 0x10)

    too_large = ExpansionPoolAllocator()
    with pytest.raises(ValueError, match="exhausted"):
        too_large.allocate("too-large", 0x3C01, align=1)
