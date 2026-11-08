import hashlib

import pytest

from mkmszr.data.addresses import (
    ARENA_START_PATCHES,
    FIRE_POTION_CALLBACK_EXPECTED,
    FIRE_POTION_CALLBACK_FIELD_ROM,
    MKMSZR_FILE_ENTRY_ROM,
    NATIVE_BOOTSTRAP_HOOK_ROM,
    PICKUP_MANAGER_HOOK_EXPECTED,
    PICKUP_MANAGER_HOOK_ROM,
    PROVEN_PAYLOAD_ROM,
)
from mkmszr.errors import PatchError
from mkmszr.mips import jump
from mkmszr.patches.base import PatchContext, PatchPipeline
from mkmszr.patches.runtime_v1 import (
    CAPTURE_ENTRY,
    CODE_CACHED_BASE,
    CODE_SIZE,
    FIRE_BITSET_OFFSET,
    FIRE_STARTING_POTION_BIT,
    LOADER_STUB,
    RESTORE_TRAMPOLINE,
    RESTORE_TRAMPOLINE_ROM,
    RESTORE_TRAMPOLINE_VA,
    RUNTIME_V1_ACTUAL_CODE_SIZE,
    RUNTIME_V1_PAYLOAD,
    STATE_CACHED_BASE,
    STATE_HEADER_SIZE,
    STATE_MAGIC,
    STATE_SIZE,
    STATE_VERSION,
    RuntimeV1FirePersistencePatch,
    runtime_v1_fire_patches,
)
from mkmszr.rom import RomImage


def _clean_shape() -> RomImage:
    size = PROVEN_PAYLOAD_ROM + CODE_SIZE
    data = bytearray(size)

    for offset, (expected, _replacement) in ARENA_START_PATCHES.items():
        data[offset : offset + 4] = expected.to_bytes(4, "big")

    data[NATIVE_BOOTSTRAP_HOOK_ROM : NATIVE_BOOTSTRAP_HOOK_ROM + 8] = bytes.fromhex(
        "27BDFFE8 3C02801B"
    )
    data[PICKUP_MANAGER_HOOK_ROM : PICKUP_MANAGER_HOOK_ROM + 8] = (
        PICKUP_MANAGER_HOOK_EXPECTED
    )
    data[
        FIRE_POTION_CALLBACK_FIELD_ROM : FIRE_POTION_CALLBACK_FIELD_ROM + 4
    ] = FIRE_POTION_CALLBACK_EXPECTED.to_bytes(4, "big")
    data[PROVEN_PAYLOAD_ROM : PROVEN_PAYLOAD_ROM + CODE_SIZE] = b"\xFF" * CODE_SIZE

    return RomImage(data=data, _original=bytes(data))


def test_runtime_v1_layout_matches_confirmed_memory_map() -> None:
    assert CODE_CACHED_BASE == 0x801AF420
    assert CODE_SIZE == 0x200
    assert STATE_CACHED_BASE == 0x801AF620
    assert STATE_SIZE == 0x200
    assert STATE_MAGIC == 0x4D4B5356
    assert STATE_VERSION == 1
    assert STATE_HEADER_SIZE == 0x20
    assert STATE_CACHED_BASE + FIRE_BITSET_OFFSET == 0x801AF640
    assert FIRE_STARTING_POTION_BIT == 0


def test_runtime_v1_payload_matches_confirmed_reference() -> None:
    assert len(RUNTIME_V1_PAYLOAD) == 0x200
    assert RUNTIME_V1_ACTUAL_CODE_SIZE == 0x198
    assert hashlib.sha256(RUNTIME_V1_PAYLOAD).hexdigest() == (
        "2cff837b6d9980a25264ad441054495c20e138665ffed282bcd817f072547981"
    )
    assert len(LOADER_STUB) == 84
    assert LOADER_STUB.hex() == (
        "27bdffe83c02801b24423420afbf00103c04800fac82ecd0"
        "0c0198e4000000002404001b3c05801b24a5f4200c019759"
        "000000003c19a01b2739f4200320f809000000008fbf0010"
        "27bd001803e0000800000000"
    )
    assert len(RESTORE_TRAMPOLINE) == 16
    assert RESTORE_TRAMPOLINE.hex() == "3c19a01b2739f5200320000800000000"
    assert RESTORE_TRAMPOLINE_ROM == 0x0009ADD8
    assert RESTORE_TRAMPOLINE_VA == 0x8009A1D8


def test_runtime_v1_fire_pipeline_installs_confirmed_hooks() -> None:
    rom = _clean_shape()

    results = PatchPipeline(runtime_v1_fire_patches()).apply(rom, PatchContext())

    assert [result.name for result in results] == [
        "arena-reservation",
        "native-payload-bootstrap",
        "runtime-v1-fire-persistence",
    ]
    assert rom.data[PROVEN_PAYLOAD_ROM : PROVEN_PAYLOAD_ROM + CODE_SIZE] == (
        RUNTIME_V1_PAYLOAD
    )
    assert rom.data[MKMSZR_FILE_ENTRY_ROM : MKMSZR_FILE_ENTRY_ROM + 12] == (
        PROVEN_PAYLOAD_ROM.to_bytes(4, "big")
        + (PROVEN_PAYLOAD_ROM + CODE_SIZE).to_bytes(4, "big")
        + bytes(4)
    )
    assert rom.data[
        RESTORE_TRAMPOLINE_ROM : RESTORE_TRAMPOLINE_ROM + len(RESTORE_TRAMPOLINE)
    ] == RESTORE_TRAMPOLINE
    assert rom.read_u32(PICKUP_MANAGER_HOOK_ROM) == jump(RESTORE_TRAMPOLINE_VA)
    assert rom.read_u32(PICKUP_MANAGER_HOOK_ROM + 4) == 0
    assert rom.read_u32(FIRE_POTION_CALLBACK_FIELD_ROM) == CAPTURE_ENTRY


def test_runtime_v1_fire_patch_requires_native_payload_first() -> None:
    rom = _clean_shape()

    with pytest.raises(PatchError, match="requires the V1 NativePayloadPatch first"):
        RuntimeV1FirePersistencePatch().apply(rom, PatchContext())
