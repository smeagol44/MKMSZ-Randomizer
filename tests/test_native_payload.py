import pytest

from mkmszr.data.addresses import (
    ARENA_START_PATCHES,
    MKMSZR_FILE_ENTRY_ROM,
    NATIVE_BOOTSTRAP_HOOK_ROM,
    NATIVE_BOOTSTRAP_STUB_ROM,
    PROVEN_PAYLOAD_RDRAM,
    PROVEN_PAYLOAD_ROM,
)
from mkmszr.errors import PatchError
from mkmszr.mips import jr, lui, ori, sw, words_blob
from mkmszr.patches.arena import ArenaReservationPatch
from mkmszr.patches.base import PatchContext, PatchPipeline
from mkmszr.patches.native_payload import (
    NativePayloadPatch,
    NativePayloadSpec,
    build_loader_and_call_stub,
)
from mkmszr.rom import RomImage

MARKER_RDRAM = 0x801AF440
MARKER_VALUE = 0x4D4B4558

EXECUTION_PROOF_PAYLOAD = words_blob(
    [
        lui("t0", 0xA01B),
        lui("t1", MARKER_VALUE >> 16),
        ori("t1", "t1", MARKER_VALUE & 0xFFFF),
        sw("t1", MARKER_RDRAM & 0xFFFF, "t0"),
        jr("ra"),
        0,
        0,
        0,
    ]
)

EXPECTED_PROOF_STUB = bytes.fromhex(
    "27BDFFE8 3C02801B 24423420 AFBF0010 "
    "3C04800F AC82ECD0 0C0198E4 00000000 "
    "2404001B 3C05801B 24A5F420 0C019759 00000000 "
    "3C08A01B AD00F440 "
    "3C19A01B 2739F420 0320F809 00000000 "
    "8FBF0010 27BD0018 03E00008 00000000"
)


def _proof_rom() -> RomImage:
    size = PROVEN_PAYLOAD_ROM + len(EXECUTION_PROOF_PAYLOAD)
    data = bytearray(size)
    for offset, (expected, _replacement) in ARENA_START_PATCHES.items():
        data[offset : offset + 4] = expected.to_bytes(4, "big")
    data[NATIVE_BOOTSTRAP_HOOK_ROM : NATIVE_BOOTSTRAP_HOOK_ROM + 8] = bytes.fromhex(
        "27BDFFE8 3C02801B"
    )
    data[PROVEN_PAYLOAD_ROM : PROVEN_PAYLOAD_ROM + len(EXECUTION_PROOF_PAYLOAD)] = (
        b"\xFF" * len(EXECUTION_PROOF_PAYLOAD)
    )
    return RomImage(data=data, _original=bytes(data))


def test_confirmed_execution_proof_stub_is_reproduced_exactly() -> None:
    stub = build_loader_and_call_stub(
        payload_rdram=PROVEN_PAYLOAD_RDRAM,
        clear_word_rdram=MARKER_RDRAM,
    )
    assert stub == EXPECTED_PROOF_STUB
    assert len(stub) == 92


def test_native_payload_patch_composes_after_arena_reservation() -> None:
    rom = _proof_rom()
    spec = NativePayloadSpec(
        payload=EXECUTION_PROOF_PAYLOAD,
        clear_word_rdram=MARKER_RDRAM,
    )

    results = PatchPipeline(
        [
            ArenaReservationPatch(),
            NativePayloadPatch(spec),
        ]
    ).apply(rom, PatchContext())

    assert [result.name for result in results] == [
        "arena-reservation",
        "native-payload-bootstrap",
    ]
    assert rom.data[PROVEN_PAYLOAD_ROM : PROVEN_PAYLOAD_ROM + 0x20] == EXECUTION_PROOF_PAYLOAD
    assert rom.data[MKMSZR_FILE_ENTRY_ROM : MKMSZR_FILE_ENTRY_ROM + 12] == (
        PROVEN_PAYLOAD_ROM.to_bytes(4, "big")
        + (PROVEN_PAYLOAD_ROM + 0x20).to_bytes(4, "big")
        + bytes(4)
    )
    assert rom.data[NATIVE_BOOTSTRAP_STUB_ROM : NATIVE_BOOTSTRAP_STUB_ROM + 92] == (
        EXPECTED_PROOF_STUB
    )
    assert rom.read_u32(NATIVE_BOOTSTRAP_HOOK_ROM) == 0x08026861
    assert rom.read_u32(NATIVE_BOOTSTRAP_HOOK_ROM + 4) == 0


def test_native_payload_requires_reserved_arena_first() -> None:
    rom = _proof_rom()
    spec = NativePayloadSpec(payload=EXECUTION_PROOF_PAYLOAD)

    with pytest.raises(PatchError, match="requires ArenaReservationPatch first"):
        NativePayloadPatch(spec).apply(rom, PatchContext())


def test_clear_word_must_not_overlap_payload() -> None:
    with pytest.raises(ValueError, match="must not overlap"):
        NativePayloadSpec(
            payload=EXECUTION_PROOF_PAYLOAD,
            clear_word_rdram=PROVEN_PAYLOAD_RDRAM,
        )
