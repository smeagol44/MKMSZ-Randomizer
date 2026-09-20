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
from mkmszr.patches.arena import ArenaReservationPatch
from mkmszr.patches.base import PatchContext, PatchPipeline
from mkmszr.patches.native_payload import NativePayloadPatch, NativePayloadSpec
from mkmszr.patches.pickup_persistence import (
    CAPTURE_HELPER,
    CAPTURE_HELPER_ROM,
    CAPTURE_HELPER_VA,
    DESCRIPTOR_TABLE,
    DESCRIPTOR_TABLE_ROM,
    FIRE_TRANSLATION,
    FIRE_TRANSLATION_ROM,
    PICKUP_PERSISTENCE_ACTUAL_CODE_SIZE,
    PICKUP_PERSISTENCE_PAYLOAD,
    RESTORE_TRAMPOLINE,
    RESTORE_TRAMPOLINE_ROM,
    RESTORE_TRAMPOLINE_VA,
    STAGE_DESCRIPTORS,
    PickupPersistencePatch,
)
from mkmszr.patches.runtime_v2 import CODE_SIZE, LOADER_STUB
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


def test_v38_descriptor_and_bitset_design_is_exact() -> None:
    assert STAGE_DESCRIPTORS == (
        (4, 0x24, 4, 0),
        (6, 0x28, 6, 0),
        (9, 0x2C, 9, 0),
        (20, 0x30, 20, 0),
        (10, 0x34, 10, 0),
        (19, 0x20, 16, 1),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (10, 0x38, 10, 0),
        (9, 0x3C, 9, 0),
    )
    assert len(DESCRIPTOR_TABLE) == 40
    assert FIRE_TRANSLATION == bytes(
        [2, 5, 4, 0xFF, 0xFF, 0xFF, 9, 14, 0, 1, 8, 11, 12, 3, 7, 6, 10, 13, 15, 0xFF]
    )
    assert len(FIRE_TRANSLATION) == 20


def test_pickup_persistence_code_fits_confirmed_regions() -> None:
    assert len(PICKUP_PERSISTENCE_PAYLOAD) == CODE_SIZE == 0x300
    assert PICKUP_PERSISTENCE_ACTUAL_CODE_SIZE == 0x1D4
    assert PICKUP_PERSISTENCE_PAYLOAD[0x200:] == bytes(0x100)
    assert len(RESTORE_TRAMPOLINE) == 0x10
    assert len(LOADER_STUB) == 84
    assert len(CAPTURE_HELPER) == 0xD8

    assert CAPTURE_HELPER_ROM + len(CAPTURE_HELPER) == DESCRIPTOR_TABLE_ROM
    assert DESCRIPTOR_TABLE_ROM == 0x0009AEC0
    assert FIRE_TRANSLATION_ROM == 0x0009AEE8
    assert RESTORE_TRAMPOLINE_ROM == 0x0009ADD8
    assert RESTORE_TRAMPOLINE_VA == 0x8009A1D8
    assert CAPTURE_HELPER_VA == 0x8009A1E8


def test_pickup_persistence_installs_shared_hooks_and_data() -> None:
    rom = _clean_shape()

    results = PatchPipeline(
        (
            ArenaReservationPatch(),
            NativePayloadPatch(NativePayloadSpec(payload=PICKUP_PERSISTENCE_PAYLOAD)),
            PickupPersistencePatch(),
        )
    ).apply(rom, PatchContext())

    assert [result.name for result in results] == [
        "arena-reservation",
        "native-payload-bootstrap",
        "pickup-persistence",
    ]

    assert rom.data[PROVEN_PAYLOAD_ROM : PROVEN_PAYLOAD_ROM + CODE_SIZE] == (
        PICKUP_PERSISTENCE_PAYLOAD
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

    assert rom.data[
        DESCRIPTOR_TABLE_ROM : DESCRIPTOR_TABLE_ROM + len(DESCRIPTOR_TABLE)
    ] == DESCRIPTOR_TABLE
    assert rom.data[
        FIRE_TRANSLATION_ROM : FIRE_TRANSLATION_ROM + len(FIRE_TRANSLATION)
    ] == FIRE_TRANSLATION

    # The generalized path must not regress to a per-Potion callback patch.
    assert rom.read_u32(FIRE_POTION_CALLBACK_FIELD_ROM) == FIRE_POTION_CALLBACK_EXPECTED
