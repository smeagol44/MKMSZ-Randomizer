from mkmszr.data.addresses import ARENA_START_PATCHES
from mkmszr.patches.arena import ArenaReservationPatch
from mkmszr.patches.base import PatchContext
from mkmszr.rom import RomImage


def test_arena_patch_is_guarded_and_exact() -> None:
    size = max(ARENA_START_PATCHES) + 4
    data = bytearray(size)
    for offset, (expected, _replacement) in ARENA_START_PATCHES.items():
        data[offset : offset + 4] = expected.to_bytes(4, "big")
    rom = RomImage(data=data, _original=bytes(data))

    ArenaReservationPatch().apply(rom, PatchContext())

    for offset, (_expected, replacement) in ARENA_START_PATCHES.items():
        assert rom.read_u32(offset) == replacement
