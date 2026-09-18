"""Eight-stage ordinary-pickup persistence experiment.

Implements the canonical v38 descriptor/Fire-translation design for the 84
catalogued ordinary pickup locations. Scripted/special stage mechanisms remain
outside this bitset by design.

This module is experimental until the full multi-stage runtime matrix is
manually validated.
"""

from __future__ import annotations

from ..data.addresses import (
    CURRENT_STAGE_VA,
    FIRE_POTION_CALLBACK_EXPECTED,
    FIRE_POTION_CALLBACK_FIELD_ROM,
    MKMSZR_FILE_ENTRY_ROM,
    NATIVE_BOOTSTRAP_HOOK_ROM,
    NATIVE_BOOTSTRAP_STUB_CAPACITY,
    NATIVE_BOOTSTRAP_STUB_ROM,
    NATIVE_BOOTSTRAP_STUB_VA,
    PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED,
    PICKUP_MANAGER_CAPTURE_EXPECTED,
    PICKUP_MANAGER_CAPTURE_HOOK_ROM,
    PICKUP_MANAGER_CONTEXT_PTR_VA,
    PICKUP_MANAGER_HOOK_EXPECTED,
    PICKUP_MANAGER_HOOK_ROM,
    PICKUP_MANAGER_RESUME_VA,
    PROVEN_PAYLOAD_ROM,
)
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    address_words,
    addu,
    and_,
    jal,
    jr,
    jump,
    lbu,
    lui,
    lw,
    or_,
    ori,
    sll,
    sllv,
    sltiu,
    sltu,
    sw,
    words_blob,
)
from ..rom import RomImage
from .arena import ArenaReservationPatch
from .base import PatchContext
from .native_payload import NativePayloadPatch, NativePayloadSpec, kseg1_alias
from .runtime_v1 import (
    CODE_SIZE,
    LOADER_STUB,
    STATE_HEADER_SIZE,
    STATE_MAGIC,
    STATE_SIZE,
    STATE_UNCACHED_BASE,
    STATE_VERSION,
    build_init,
)
from .stage_selector import SafeStageSelectorPatch

NOP = 0
RECORD_SIZE = 0x30

RESTORE_OFFSET = 0x0A0
RESTORE_ENTRY = kseg1_alias(0x801AF420 + RESTORE_OFFSET)

RESTORE_TRAMPOLINE_ROM = NATIVE_BOOTSTRAP_STUB_ROM + len(LOADER_STUB)
RESTORE_TRAMPOLINE_VA = NATIVE_BOOTSTRAP_STUB_VA + len(LOADER_STUB)

CAPTURE_HELPER_ROM = RESTORE_TRAMPOLINE_ROM + 0x10
CAPTURE_HELPER_VA = RESTORE_TRAMPOLINE_VA + 0x10

# Canonical v38 permanent-cave data layout.
DESCRIPTOR_TABLE_VA = 0x8009A2C0
DESCRIPTOR_TABLE_ROM = NATIVE_BOOTSTRAP_STUB_ROM + (
    DESCRIPTOR_TABLE_VA - NATIVE_BOOTSTRAP_STUB_VA
)
FIRE_TRANSLATION_VA = 0x8009A2E8
FIRE_TRANSLATION_ROM = NATIVE_BOOTSTRAP_STUB_ROM + (
    FIRE_TRANSLATION_VA - NATIVE_BOOTSTRAP_STUB_VA
)

FIRE_STAGE_ID = 5
FIRE_DESCRIPTOR_FLAG_TRANSLATE = 0x01

# Descriptor byte layout: expected manager count, bitset state offset,
# ordinary-pickup count, flags. Direct indexed by native stage ID 0..9.
STAGE_DESCRIPTORS = (
    (4, 0x24, 4, 0),   # 0 Temple
    (6, 0x28, 6, 0),   # 1 Wind
    (9, 0x2C, 9, 0),   # 2 Water
    (20, 0x30, 20, 0), # 3 Earth
    (10, 0x34, 10, 0), # 4 Prison
    (19, 0x20, 16, FIRE_DESCRIPTOR_FLAG_TRANSLATE), # 5 Fire
    (0, 0, 0, 0),      # 6 unused
    (0, 0, 0, 0),      # 7 Fire God room / excluded
    (10, 0x38, 10, 0), # 8 Bridge
    (9, 0x3C, 9, 0),   # 9 Fortress
)

DESCRIPTOR_TABLE = bytes(value for row in STAGE_DESCRIPTORS for value in row)

# Fire manager ordinal -> canonical ordinary-pickup bit. 0xFF excludes the
# three type-4 special records at manager ordinals 3, 4, and 5.
FIRE_TRANSLATION = bytes(
    [2, 5, 4, 0xFF, 0xFF, 0xFF, 9, 14, 0, 1, 8, 11, 12, 3, 7, 6, 10, 13, 15, 0xFF]
)


def _emit_u32(emitter: Emitter, register: str, value: int) -> None:
    emitter.emit(lui(register, value >> 16), ori(register, register, value & 0xFFFF))


def build_generalized_capture_helper() -> bytes:
    """Capture ordinary pickup collection through the single manager commit hook."""

    emitter = Emitter()

    # This is a mid-function hook rather than an ABI call site. Preserve the
    # temporaries used by the helper so the native manager sees its original
    # register values after the hook returns.
    emitter.emit(
        addiu("sp", "sp", -0x20),
        sw("t0", 0x00, "sp"),
        sw("t1", 0x04, "sp"),
        sw("t2", 0x08, "sp"),
        sw("t3", 0x0C, "sp"),
        sw("t4", 0x10, "sp"),
        sw("t5", 0x14, "sp"),
    )

    # Reproduce the displaced native store. The original following LUI executes
    # as the JAL delay slot, so V0 is no longer usable here.
    emitter.emit(addiu("t0", "zero", 1), sw("t0", 0x2C, "a1"))

    # Resolve direct-index stage descriptor and fail closed outside 0..9.
    emitter.emit(*address_words("t0", CURRENT_STAGE_VA))
    emitter.emit(lw("t0", 0, "t0"), sltiu("t1", "t0", len(STAGE_DESCRIPTORS)))

    descriptor_address = address_words("t2", DESCRIPTOR_TABLE_VA)
    emitter.beq("t1", "zero", "return")
    emitter.emit(descriptor_address[0])
    emitter.emit(descriptor_address[1])

    emitter.emit(sll("t3", "t0", 2), addu("t2", "t2", "t3"))
    emitter.emit(lbu("t3", 0, "t2"))
    emitter.beq("t3", "zero", "return")
    emitter.emit(sltu("t5", "s2", "t3"))
    emitter.beq("t5", "zero", "return")
    emitter.emit(NOP)

    # Non-Fire stages use manager ordinal directly. Fire translates around its
    # three nonordinary manager records.
    emitter.emit(addiu("t5", "zero", FIRE_STAGE_ID))
    emitter.beq("t0", "t5", "fire_translate")
    emitter.emit(NOP)
    emitter.emit(addu("t4", "s2", "zero"))
    emitter.beq("zero", "zero", "have_bit")
    emitter.emit(NOP)

    emitter.label("fire_translate")
    emitter.emit(*address_words("t4", FIRE_TRANSLATION_VA))
    emitter.emit(addu("t4", "t4", "s2"), lbu("t4", 0, "t4"))

    emitter.label("have_bit")
    emitter.emit(sltiu("t5", "t4", 32))
    emitter.beq("t5", "zero", "return")
    emitter.emit(NOP)

    emitter.emit(lbu("t5", 1, "t2"))
    emitter.emit(*address_words("t0", STATE_UNCACHED_BASE))
    emitter.emit(addu("t0", "t0", "t5"), lw("t1", 0, "t0"))
    emitter.emit(addiu("t3", "zero", 1), sllv("t3", "t3", "t4"))
    emitter.emit(or_("t1", "t1", "t3"), sw("t1", 0, "t0"))

    emitter.label("return")
    emitter.emit(
        lw("t0", 0x00, "sp"),
        lw("t1", 0x04, "sp"),
        lw("t2", 0x08, "sp"),
        lw("t3", 0x0C, "sp"),
        lw("t4", 0x10, "sp"),
        lw("t5", 0x14, "sp"),
        addiu("sp", "sp", 0x20),
        jr("ra"),
        NOP,
    )
    return emitter.finish()


def build_generalized_restore_scanner() -> bytes:
    """Restore all ordinary collected flags for the current manager before actors."""

    emitter = Emitter()

    # Preserve the confirmed V1 validation contract before trusting state.
    emitter.emit(*address_words("t0", STATE_UNCACHED_BASE))
    emitter.emit(lw("t1", 0x00, "t0"))
    _emit_u32(emitter, "t2", STATE_MAGIC)
    emitter.bne("t1", "t2", "resume")
    emitter.emit(NOP)

    emitter.emit(lw("t1", 0x04, "t0"), addiu("t2", "zero", STATE_VERSION))
    emitter.bne("t1", "t2", "resume")
    emitter.emit(NOP)

    emitter.emit(lw("t1", 0x08, "t0"), addiu("t2", "zero", STATE_SIZE))
    emitter.bne("t1", "t2", "resume")
    emitter.emit(NOP)

    emitter.emit(lw("t1", 0x0C, "t0"), addiu("t2", "zero", STATE_HEADER_SIZE))
    emitter.bne("t1", "t2", "resume")
    emitter.emit(NOP)

    # Direct-index descriptor by native stage ID and reject unsupported stages.
    emitter.emit(*address_words("t1", CURRENT_STAGE_VA))
    emitter.emit(lw("t1", 0, "t1"), sltiu("t2", "t1", len(STAGE_DESCRIPTORS)))
    emitter.beq("t2", "zero", "resume")
    emitter.emit(NOP)

    emitter.emit(*address_words("t2", DESCRIPTOR_TABLE_VA))
    emitter.emit(sll("t3", "t1", 2), addu("t2", "t2", "t3"))
    emitter.emit(lbu("t4", 0, "t2"))
    emitter.beq("t4", "zero", "resume")
    emitter.emit(NOP)

    # Fail closed unless the live manager exactly matches the catalogued count.
    emitter.emit(*address_words("t3", PICKUP_MANAGER_CONTEXT_PTR_VA))
    emitter.emit(lw("t3", 0, "t3"))
    emitter.beq("t3", "zero", "resume")
    emitter.emit(NOP)
    emitter.emit(lw("t5", 0x6F4, "t3"))
    emitter.bne("t5", "t4", "resume")
    emitter.emit(NOP)
    emitter.emit(lw("t3", 0x6F8, "t3"))
    emitter.beq("t3", "zero", "resume")
    emitter.emit(NOP)

    # Load this stage's persistent word once; then scan manager records.
    emitter.emit(lbu("t5", 1, "t2"), addu("t5", "t0", "t5"), lw("t5", 0, "t5"))
    emitter.emit(lbu("t7", 3, "t2"), addiu("t6", "zero", 0))

    emitter.label("record_loop")
    emitter.beq("t7", "zero", "ordinal_bit")
    emitter.emit(NOP)

    emitter.emit(*address_words("t8", FIRE_TRANSLATION_VA))
    emitter.emit(addu("t8", "t8", "t6"), lbu("t8", 0, "t8"))
    emitter.beq("zero", "zero", "have_bit")
    emitter.emit(NOP)

    emitter.label("ordinal_bit")
    emitter.emit(addu("t8", "t6", "zero"))

    emitter.label("have_bit")
    emitter.emit(sltiu("t2", "t8", 32))
    emitter.beq("t2", "zero", "next_record")
    emitter.emit(NOP)

    emitter.emit(addiu("t2", "zero", 1), sllv("t2", "t2", "t8"))
    emitter.emit(and_("t2", "t5", "t2"))
    emitter.beq("t2", "zero", "next_record")
    emitter.emit(NOP)
    emitter.emit(addiu("t2", "zero", 1), sw("t2", 0x2C, "t3"))

    emitter.label("next_record")
    emitter.emit(addiu("t3", "t3", RECORD_SIZE), addiu("t6", "t6", 1))
    emitter.bne("t6", "t4", "record_loop")
    emitter.emit(NOP)

    emitter.label("resume")
    # Reproduce the two instructions displaced by the manager-entry hook.
    emitter.emit(lui("v1", 0x800A), lw("v1", -0x56F0, "v1"))
    emitter.emit(*address_words("t9", PICKUP_MANAGER_RESUME_VA))
    emitter.emit(jr("t9"), NOP)
    return emitter.finish()


def build_generalized_payload() -> tuple[bytes, int]:
    init = build_init()
    restore = build_generalized_restore_scanner()

    if len(init) > RESTORE_OFFSET:
        raise AssertionError("V1 init overlaps generalized restore scanner")

    actual_size = RESTORE_OFFSET + len(restore)
    if actual_size > CODE_SIZE:
        raise AssertionError("generalized persistence exceeds V1 code region")

    payload = bytearray(CODE_SIZE)
    payload[: len(init)] = init
    payload[RESTORE_OFFSET : RESTORE_OFFSET + len(restore)] = restore
    return bytes(payload), actual_size


def build_restore_trampoline() -> bytes:
    return words_blob([*address_words("t9", RESTORE_ENTRY), jr("t9"), NOP])


GENERALIZED_PAYLOAD, GENERALIZED_ACTUAL_CODE_SIZE = build_generalized_payload()
RESTORE_TRAMPOLINE = build_restore_trampoline()
CAPTURE_HELPER = build_generalized_capture_helper()


class GeneralizedPickupPersistencePatch:
    """Install the v38 eight-stage ordinary-pickup capture/restore design."""

    name = "generalized-pickup-persistence-experiment"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        expected_end = PROVEN_PAYLOAD_ROM + CODE_SIZE
        if (
            rom.read_u32(MKMSZR_FILE_ENTRY_ROM) != PROVEN_PAYLOAD_ROM
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 4) != expected_end
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 8) != 0
        ):
            raise PatchError("generalized persistence requires NativePayloadPatch first")

        rom.expect_bytes(PROVEN_PAYLOAD_ROM, GENERALIZED_PAYLOAD)
        rom.expect_bytes(NATIVE_BOOTSTRAP_STUB_ROM, LOADER_STUB)
        rom.expect_u32(NATIVE_BOOTSTRAP_HOOK_ROM, jump(NATIVE_BOOTSTRAP_STUB_VA))
        rom.expect_u32(NATIVE_BOOTSTRAP_HOOK_ROM + 4, NOP)

        capture_limit = DESCRIPTOR_TABLE_ROM
        if CAPTURE_HELPER_ROM + len(CAPTURE_HELPER) > capture_limit:
            raise PatchError("generalized capture helper overlaps descriptor table")

        data_end = FIRE_TRANSLATION_ROM + len(FIRE_TRANSLATION)
        cave_end = NATIVE_BOOTSTRAP_STUB_ROM + NATIVE_BOOTSTRAP_STUB_CAPACITY
        if data_end > cave_end:
            raise PatchError("generalized persistence exceeds the confirmed permanent cave")

        rom.expect_bytes(RESTORE_TRAMPOLINE_ROM, bytes(len(RESTORE_TRAMPOLINE)))
        rom.expect_bytes(CAPTURE_HELPER_ROM, bytes(len(CAPTURE_HELPER)))
        rom.expect_bytes(DESCRIPTOR_TABLE_ROM, bytes(len(DESCRIPTOR_TABLE)))
        rom.expect_bytes(FIRE_TRANSLATION_ROM, bytes(len(FIRE_TRANSLATION)))

        rom.expect_bytes(PICKUP_MANAGER_HOOK_ROM, PICKUP_MANAGER_HOOK_EXPECTED)
        rom.expect_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM, PICKUP_MANAGER_CAPTURE_EXPECTED)
        rom.expect_u32(
            PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4,
            PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED,
        )

        # Preserve the already-proven Fire invariant while generalizing.
        rom.expect_u32(FIRE_POTION_CALLBACK_FIELD_ROM, FIRE_POTION_CALLBACK_EXPECTED)

        rom.write_bytes(RESTORE_TRAMPOLINE_ROM, RESTORE_TRAMPOLINE)
        rom.write_bytes(CAPTURE_HELPER_ROM, CAPTURE_HELPER)
        rom.write_bytes(DESCRIPTOR_TABLE_ROM, DESCRIPTOR_TABLE)
        rom.write_bytes(FIRE_TRANSLATION_ROM, FIRE_TRANSLATION)

        rom.write_u32(PICKUP_MANAGER_HOOK_ROM, jump(RESTORE_TRAMPOLINE_VA))
        rom.write_u32(PICKUP_MANAGER_HOOK_ROM + 4, NOP)
        rom.write_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM, jal(CAPTURE_HELPER_VA))

        return (
            "84 catalogued ordinary pickups covered across 8 main stages",
            "restore fails closed on manager-count mismatch before touching records",
            "Fire ordinals 3/4/5 remain excluded through the v38 translation map",
            "scripted/special stage mechanisms are intentionally outside this bitset",
        )


def generalized_persistence_test_patches() -> tuple[
    SafeStageSelectorPatch,
    ArenaReservationPatch,
    NativePayloadPatch,
    GeneralizedPickupPersistencePatch,
]:
    """Return the disposable multi-stage runtime-test patch sequence."""

    return (
        SafeStageSelectorPatch(),
        ArenaReservationPatch(),
        NativePayloadPatch(NativePayloadSpec(payload=GENERALIZED_PAYLOAD)),
        GeneralizedPickupPersistencePatch(),
    )
