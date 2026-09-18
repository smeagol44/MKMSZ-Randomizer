import hashlib

from mkmszr.data.addresses import (
    ARENA_START_PATCHES,
    FIRE_POTION_CALLBACK_EXPECTED,
    FIRE_POTION_CALLBACK_FIELD_ROM,
    MKMSZR_FILE_ENTRY_ROM,
    NATIVE_BOOTSTRAP_HOOK_ROM,
    PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED,
    PICKUP_MANAGER_CAPTURE_EXPECTED,
    PICKUP_MANAGER_CAPTURE_HOOK_ROM,
    PICKUP_MANAGER_HOOK_EXPECTED,
    PICKUP_MANAGER_HOOK_ROM,
    PROVEN_PAYLOAD_ROM,
)
from mkmszr.mips import jal, jump
from mkmszr.patches.base import PatchContext, PatchPipeline
from mkmszr.patches.manager_persistence_experiment import (
    CAPTURE_HELPER,
    CAPTURE_HELPER_ROM,
    CAPTURE_HELPER_VA,
    EXPERIMENT_ACTUAL_CODE_SIZE,
    EXPERIMENT_PAYLOAD,
    RESTORE_TRAMPOLINE,
    RESTORE_TRAMPOLINE_ROM,
    RESTORE_TRAMPOLINE_VA,
    manager_persistence_fire_experiment_patches,
)
from mkmszr.patches.runtime_v1 import CODE_SIZE, LOADER_STUB
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
    data[PICKUP_MANAGER_CAPTURE_HOOK_ROM : PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4] = (
        PICKUP_MANAGER_CAPTURE_EXPECTED.to_bytes(4, "big")
    )
    data[
        PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4 : PICKUP_MANAGER_CAPTURE_HOOK_ROM + 8
    ] = PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED.to_bytes(4, "big")
    data[
        FIRE_POTION_CALLBACK_FIELD_ROM : FIRE_POTION_CALLBACK_FIELD_ROM + 4
    ] = FIRE_POTION_CALLBACK_EXPECTED.to_bytes(4, "big")
    data[PROVEN_PAYLOAD_ROM : PROVEN_PAYLOAD_ROM + CODE_SIZE] = b"\xFF" * CODE_SIZE

    return RomImage(data=data, _original=bytes(data))


def test_experiment_binary_layout_is_pinned() -> None:
    assert len(EXPERIMENT_PAYLOAD) == 0x200
    assert EXPERIMENT_ACTUAL_CODE_SIZE == 0x168
    assert hashlib.sha256(EXPERIMENT_PAYLOAD).hexdigest() == (
        "9941360df93289912ccad301ca855f9db66fd4f174ce452fec4a14f48a28a5b2"
    )

    assert len(RESTORE_TRAMPOLINE) == 0x10
    assert RESTORE_TRAMPOLINE.hex() == "3c19a01b2739f4c00320000800000000"

    assert len(CAPTURE_HELPER) == 0x48
    assert hashlib.sha256(CAPTURE_HELPER).hexdigest() == (
        "21cee62eb6e1f41ed596f2e9d970b1d08b7b66bc14e59822a3933707c1a3f0b5"
    )

    assert len(LOADER_STUB) + len(RESTORE_TRAMPOLINE) + len(CAPTURE_HELPER) == 0xAC
    assert RESTORE_TRAMPOLINE_ROM == 0x0009ADD8
    assert CAPTURE_HELPER_ROM == 0x0009ADE8
    assert RESTORE_TRAMPOLINE_VA == 0x8009A1D8
    assert CAPTURE_HELPER_VA == 0x8009A1E8


def test_experiment_installs_manager_hooks_and_keeps_callback_vanilla() -> None:
    rom = _clean_shape()

    results = PatchPipeline(manager_persistence_fire_experiment_patches()).apply(
        rom, PatchContext()
    )

    assert [result.name for result in results] == [
        "safe-stage-selector",
        "arena-reservation",
        "native-payload-bootstrap",
        "manager-persistence-fire-experiment",
    ]

    assert rom.data[PROVEN_PAYLOAD_ROM : PROVEN_PAYLOAD_ROM + CODE_SIZE] == (
        EXPERIMENT_PAYLOAD
    )
    assert rom.data[MKMSZR_FILE_ENTRY_ROM : MKMSZR_FILE_ENTRY_ROM + 12] == (
        PROVEN_PAYLOAD_ROM.to_bytes(4, "big")
        + (PROVEN_PAYLOAD_ROM + CODE_SIZE).to_bytes(4, "big")
        + bytes(4)
    )

    assert rom.read_u32(PICKUP_MANAGER_HOOK_ROM) == jump(RESTORE_TRAMPOLINE_VA)
    assert rom.read_u32(PICKUP_MANAGER_HOOK_ROM + 4) == 0

    assert rom.read_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM) == jal(CAPTURE_HELPER_VA)
    assert (
        rom.read_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4)
        == PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED
    )

    assert rom.read_u32(FIRE_POTION_CALLBACK_FIELD_ROM) == FIRE_POTION_CALLBACK_EXPECTED
