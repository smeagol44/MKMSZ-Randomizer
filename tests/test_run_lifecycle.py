import hashlib

from mkmszr.mips import words_blob
from mkmszr.patches.base import PatchContext
from mkmszr.patches.global_materialization import MATERIALIZER_HELPER_END_ROM
from mkmszr.patches.run_lifecycle import (
    CONFIG_ROM,
    EXPECTED_CONFIG,
    EXPECTED_FINAL_FULL_HP_STORE,
    FINAL_FULL_HP_STORE_ROM,
    HOOKS,
    LIFECYCLE_MODULE,
    LIFECYCLE_MODULE_END_ROM,
    LIFECYCLE_MODULE_ROM,
    LIFECYCLE_MODULE_SHA256,
    LIFECYCLE_MODULE_SIZE,
    PRODUCTION_CONFIG,
    RunLifecyclePatch,
)
from mkmszr.patches.temple_special_check import (
    EXPANSION_FILE_ENTRY_ROM,
    EXPANSION_FILE_ROM,
    TEMPLE_MODULE_END_ROM,
    TOASTY_ROM,
)
from mkmszr.rom import RomImage


def _clean_shape() -> RomImage:
    data = bytearray(0x01000000)
    data[EXPANSION_FILE_ENTRY_ROM : EXPANSION_FILE_ENTRY_ROM + 12] = (
        EXPANSION_FILE_ROM.to_bytes(4, "big")
        + TEMPLE_MODULE_END_ROM.to_bytes(4, "big")
        + bytes(4)
    )
    data[LIFECYCLE_MODULE_ROM:LIFECYCLE_MODULE_END_ROM] = (
        b"\xFF" * LIFECYCLE_MODULE_SIZE
    )
    data[CONFIG_ROM : CONFIG_ROM + len(EXPECTED_CONFIG)] = EXPECTED_CONFIG
    data[
        FINAL_FULL_HP_STORE_ROM : FINAL_FULL_HP_STORE_ROM + 4
    ] = EXPECTED_FINAL_FULL_HP_STORE.to_bytes(4, "big")
    for offset, expected, _replacement, _label in HOOKS:
        data[offset : offset + len(expected)] = expected
    return RomImage(data=data, _original=bytes(data))


def test_runtime_confirmed_v06_blob_and_allocation_are_exact() -> None:
    assert len(LIFECYCLE_MODULE) == 0x594
    assert LIFECYCLE_MODULE_SIZE == 0x594
    assert hashlib.sha256(LIFECYCLE_MODULE).hexdigest() == LIFECYCLE_MODULE_SHA256
    assert MATERIALIZER_HELPER_END_ROM == LIFECYCLE_MODULE_ROM
    assert LIFECYCLE_MODULE_END_ROM == 0x00F697D4
    assert LIFECYCLE_MODULE_END_ROM + 0x0C == TOASTY_ROM


def test_lifecycle_v06_installs_exact_runtime_confirmed_seams() -> None:
    rom = _clean_shape()
    result = RunLifecyclePatch().apply(rom, PatchContext(seed="LIFECYCLE-V06"))

    assert rom.data[LIFECYCLE_MODULE_ROM:LIFECYCLE_MODULE_END_ROM] == LIFECYCLE_MODULE
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == LIFECYCLE_MODULE_END_ROM
    assert rom.data[CONFIG_ROM : CONFIG_ROM + len(PRODUCTION_CONFIG)] == PRODUCTION_CONFIG
    assert rom.read_u32(FINAL_FULL_HP_STORE_ROM) == 0

    for offset, _expected, replacement, _label in HOOKS:
        assert rom.data[offset : offset + len(replacement)] == replacement

    assert "Very Hard" in result[0]
    assert "Game Over" in result[3]


def test_lifecycle_v06_preserves_existing_longer_shared_file() -> None:
    rom = _clean_shape()
    existing_end = TOASTY_ROM + 0x100
    rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, existing_end)

    RunLifecyclePatch().apply(rom, PatchContext(seed="LIFECYCLE-V06"))

    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == existing_end
    assert rom.data[LIFECYCLE_MODULE_ROM:LIFECYCLE_MODULE_END_ROM] == LIFECYCLE_MODULE
