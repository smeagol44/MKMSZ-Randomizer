"""Reserve the runtime-tested 16 KiB MKMSZR arena prefix."""

from ..data.addresses import (
    ARENA_START_PATCHES,
    RESERVED_RDRAM_END_EXCLUSIVE,
    RESERVED_RDRAM_START,
)
from ..rom import RomImage
from .base import PatchContext


class ArenaReservationPatch:
    name = "arena-reservation"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context
        for offset, (expected, replacement) in ARENA_START_PATCHES.items():
            rom.expect_u32(offset, expected)
            rom.write_u32(offset, replacement)

        note = (
            f"reserved RDRAM 0x{RESERVED_RDRAM_START:08X}.."
            f"0x{RESERVED_RDRAM_END_EXCLUSIVE - 1:08X}"
        )
        return (note,)
