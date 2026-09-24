"""Build-time allocator for the MKMSZR RDRAM expansion pool.

The first 1 KiB of the 16 KiB reservation keeps the established Runtime V2
layout. New native features may request aligned slices from the remaining pool
instead of hard-coding overlapping addresses.
"""

from __future__ import annotations

from dataclasses import dataclass

from .data.addresses import EXPANSION_POOL_END_EXCLUSIVE, EXPANSION_POOL_START


@dataclass(frozen=True)
class ExpansionAllocation:
    name: str
    start: int
    end_exclusive: int
    alignment: int

    @property
    def size(self) -> int:
        return self.end_exclusive - self.start


class ExpansionPoolAllocator:
    """Monotonic build-time allocator for the reserved expansion pool."""

    def __init__(
        self,
        *,
        start: int = EXPANSION_POOL_START,
        end_exclusive: int = EXPANSION_POOL_END_EXCLUSIVE,
    ) -> None:
        if start >= end_exclusive:
            raise ValueError("expansion pool must have positive size")
        self.start = start
        self.end_exclusive = end_exclusive
        self._cursor = start
        self._allocations: list[ExpansionAllocation] = []

    @staticmethod
    def _align_up(value: int, alignment: int) -> int:
        if alignment <= 0 or alignment & (alignment - 1):
            raise ValueError("alignment must be a positive power of two")
        return (value + alignment - 1) & ~(alignment - 1)

    def allocate(self, name: str, size: int, *, align: int = 16) -> ExpansionAllocation:
        if not name or not name.strip():
            raise ValueError("allocation name must not be empty")
        if size <= 0:
            raise ValueError("allocation size must be positive")
        if any(item.name == name for item in self._allocations):
            raise ValueError(f"duplicate expansion allocation name: {name}")

        start = self._align_up(self._cursor, align)
        end = start + size
        if end > self.end_exclusive:
            remaining = max(0, self.end_exclusive - start)
            raise ValueError(
                f"expansion pool exhausted by {name}: requested 0x{size:X} bytes, "
                f"only 0x{remaining:X} aligned bytes remain"
            )

        allocation = ExpansionAllocation(name, start, end, align)
        self._allocations.append(allocation)
        self._cursor = end
        return allocation

    @property
    def allocations(self) -> tuple[ExpansionAllocation, ...]:
        return tuple(self._allocations)

    @property
    def used(self) -> int:
        return self._cursor - self.start

    @property
    def remaining(self) -> int:
        return self.end_exclusive - self._cursor
