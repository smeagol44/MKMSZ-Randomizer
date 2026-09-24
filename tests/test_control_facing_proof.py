from mkmszr.data.addresses import (
    PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED,
    PICKUP_MANAGER_CAPTURE_HOOK_ROM,
)
from mkmszr.mips import address_words, jal, jump, words_blob
from mkmszr.patches.base import PatchContext
from mkmszr.patches.control_facing_proof import (
    BOOTSTRAP_RUNTIME_ENTRY_WORDS_OFFSET,
    CAPTURE_ENTRY,
    CAPTURE_TRAMPOLINE_VA,
    CONTROL_ALLOCATION,
    CONTROL_MODULE,
    CONTROL_MODULE_CACHED_BASE,
    CONTROL_MODULE_UNCACHED_BASE,
    CURRENT_CONTROLLER_PTR_VA,
    DECISION_EXPECTED,
    DECISION_HOOK_ROM,
    DECISION_TRAMPOLINE_VA,
    EXPANSION_FILE_ENTRY_ROM,
    EXPANSION_FILE_ID,
    EXPANSION_LOADER_VA,
    EXPANSION_MODULE_ROM,
    RELEASE_EXPECTED,
    RELEASE_HOOK_ROM,
    RELEASE_TRAMPOLINE_VA,
    STATIC_REGION_BLOB,
    STATIC_REGION_ROM,
    STATIC_REGION_SIZE,
    TURN_EXPECTED,
    TURN_HOOK_ROM,
    TURN_TRAMPOLINE_VA,
    ControlFacingExpansionProofPatch,
)
from mkmszr.patches.native_payload import kseg1_alias
from mkmszr.patches.pickup_persistence import CAPTURE_HELPER, CAPTURE_HELPER_VA
from mkmszr.patches.runtime_v2 import CODE_UNCACHED_BASE
from mkmszr.rom import RomImage


def _production_shape() -> RomImage:
    size = EXPANSION_MODULE_ROM + len(CONTROL_MODULE) + 0x100
    data = bytearray(size)

    data[STATIC_REGION_ROM : STATIC_REGION_ROM + len(CAPTURE_HELPER)] = CAPTURE_HELPER

    bootstrap_patch_rom = 0x0009AD84 + BOOTSTRAP_RUNTIME_ENTRY_WORDS_OFFSET
    data[bootstrap_patch_rom : bootstrap_patch_rom + 8] = words_blob(
        address_words("t9", CODE_UNCACHED_BASE)
    )

    data[
        PICKUP_MANAGER_CAPTURE_HOOK_ROM : PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4
    ] = jal(CAPTURE_HELPER_VA).to_bytes(4, "big")
    data[
        PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4 : PICKUP_MANAGER_CAPTURE_HOOK_ROM + 8
    ] = PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED.to_bytes(4, "big")

    data[DECISION_HOOK_ROM : DECISION_HOOK_ROM + len(DECISION_EXPECTED)] = (
        DECISION_EXPECTED
    )
    data[RELEASE_HOOK_ROM : RELEASE_HOOK_ROM + len(RELEASE_EXPECTED)] = (
        RELEASE_EXPECTED
    )
    data[TURN_HOOK_ROM : TURN_HOOK_ROM + len(TURN_EXPECTED)] = TURN_EXPECTED

    data[EXPANSION_MODULE_ROM : EXPANSION_MODULE_ROM + len(CONTROL_MODULE)] = (
        b"\xFF" * len(CONTROL_MODULE)
    )
    return RomImage(data=data, _original=bytes(data))


def test_current_controller_global_uses_signed_immediate_address() -> None:
    # LUI 0x802F + signed low immediate 0xCE20 addresses 0x802ECE20.
    # 0x802FCE20 was the rejected interpretation that caused proof v01 to hang
    # immediately on the first opposite-direction flip path.
    assert CURRENT_CONTROLLER_PTR_VA == 0x802ECE20


def test_control_module_uses_first_bounded_expansion_slice() -> None:
    assert CONTROL_MODULE_CACHED_BASE == 0x801AF820
    assert CONTROL_MODULE_UNCACHED_BASE == 0xA01AF820
    assert CONTROL_ALLOCATION.start == 0x801AF820
    assert CONTROL_ALLOCATION.end_exclusive <= 0x801B3420
    assert len(CONTROL_MODULE) < 0x400
    assert CAPTURE_ENTRY == CONTROL_MODULE_UNCACHED_BASE


def test_static_loader_and_trampolines_fit_repurposed_capture_region() -> None:
    assert len(STATIC_REGION_BLOB) == STATIC_REGION_SIZE == 0xD8
    assert 0x80000000 <= EXPANSION_LOADER_VA < 0xA0000000
    assert 0x80000000 <= CAPTURE_TRAMPOLINE_VA < 0xA0000000
    assert 0x80000000 <= DECISION_TRAMPOLINE_VA < 0xA0000000
    assert 0x80000000 <= RELEASE_TRAMPOLINE_VA < 0xA0000000
    assert 0x80000000 <= TURN_TRAMPOLINE_VA < 0xA0000000


def test_control_facing_proof_installs_expansion_transport_and_hooks() -> None:
    rom = _production_shape()
    patch = ControlFacingExpansionProofPatch()
    notes = patch.apply(rom, PatchContext(seed="CONTROLTEST"))

    module_end = EXPANSION_MODULE_ROM + len(CONTROL_MODULE)
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 0) == EXPANSION_MODULE_ROM
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == module_end
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 8) == 0
    assert EXPANSION_FILE_ID == 0x1A
    assert rom.data[EXPANSION_MODULE_ROM:module_end] == CONTROL_MODULE

    bootstrap_patch_rom = 0x0009AD84 + BOOTSTRAP_RUNTIME_ENTRY_WORDS_OFFSET
    assert rom.read_u32(bootstrap_patch_rom) == jal(EXPANSION_LOADER_VA)
    assert rom.read_u32(bootstrap_patch_rom + 4) == 0

    assert rom.data[
        STATIC_REGION_ROM : STATIC_REGION_ROM + STATIC_REGION_SIZE
    ] == STATIC_REGION_BLOB

    assert rom.read_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM) == jal(
        CAPTURE_TRAMPOLINE_VA
    )
    assert rom.read_u32(DECISION_HOOK_ROM) == jal(DECISION_TRAMPOLINE_VA)
    assert rom.read_u32(RELEASE_HOOK_ROM) == jal(RELEASE_TRAMPOLINE_VA)
    assert rom.read_u32(TURN_HOOK_ROM) == jump(TURN_TRAMPOLINE_VA)

    assert any("held Turn" in note for note in notes)
    assert kseg1_alias(CONTROL_MODULE_CACHED_BASE) == CONTROL_MODULE_UNCACHED_BASE
