"""Fire-only runtime experiment for the generalized manager persistence hooks.

This is intentionally experimental. It validates the report-v37 shared manager
capture/restore architecture using the already-proven Fire starting Potion while
leaving that pickup's native callback pointer untouched.
"""

from __future__ import annotations

from ..data.addresses import (
    CURRENT_STAGE_VA,
    FIRE_MANAGER_RECORD_COUNT,
    FIRE_POTION_CALLBACK_EXPECTED,
    FIRE_POTION_CALLBACK_FIELD_ROM,
    FIRE_STAGE_ID,
    FIRE_STARTING_POTION_MANAGER_ORDINAL,
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
    andi,
    jal,
    jr,
    jump,
    lui,
    lw,
    ori,
    sw,
    words_blob,
)
from ..rom import RomImage
from .arena import ArenaReservationPatch
from .base import PatchContext
from .native_payload import NativePayloadPatch, NativePayloadSpec, kseg1_alias
from .runtime_v1 import (
    CODE_SIZE,
    FIRE_BITSET_OFFSET,
    FIRE_STARTING_POTION_BIT,
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

RESTORE_OFFSET = 0x0A0
RESTORE_ENTRY = kseg1_alias(0x801AF420 + RESTORE_OFFSET)

RESTORE_TRAMPOLINE_ROM = NATIVE_BOOTSTRAP_STUB_ROM + len(LOADER_STUB)
RESTORE_TRAMPOLINE_VA = NATIVE_BOOTSTRAP_STUB_VA + len(LOADER_STUB)

CAPTURE_HELPER_ROM = RESTORE_TRAMPOLINE_ROM + 0x10
CAPTURE_HELPER_VA = RESTORE_TRAMPOLINE_VA + 0x10


def _emit_u32(emitter: Emitter, register: str, value: int) -> None:
    emitter.emit(lui(register, value >> 16), ori(register, register, value & 0xFFFF))


def build_manager_capture_helper() -> bytes:
    """Capture Fire Potion bit 0 from the shared manager commit hook.

    The hook's JAL delay slot is the original LUI V0,0x802C. Therefore this
    helper leaves V0 untouched and reproduces the displaced native record flag
    store with T0.
    """

    emitter = Emitter()

    emitter.emit(addiu("t0", "zero", 1), sw("t0", 0x2C, "a1"))

    emitter.emit(*address_words("t0", CURRENT_STAGE_VA))
    emitter.emit(lw("t0", 0, "t0"), addiu("t1", "zero", FIRE_STAGE_ID))
    emitter.bne("t0", "t1", "return")
    emitter.emit(NOP)

    emitter.emit(addiu("t0", "zero", FIRE_STARTING_POTION_MANAGER_ORDINAL))
    emitter.bne("s2", "t0", "return")
    emitter.emit(NOP)

    emitter.emit(*address_words("t0", STATE_UNCACHED_BASE))
    emitter.emit(lw("t1", FIRE_BITSET_OFFSET, "t0"))
    emitter.emit(ori("t1", "t1", 1 << FIRE_STARTING_POTION_BIT))
    emitter.emit(sw("t1", FIRE_BITSET_OFFSET, "t0"))

    emitter.label("return")
    emitter.emit(jr("ra"), NOP)
    return emitter.finish()


def build_manager_restore_scanner() -> bytes:
    """Restore Fire Potion bit 0 through manager context, not an absolute record."""

    emitter = Emitter()

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

    emitter.emit(*address_words("t1", CURRENT_STAGE_VA))
    emitter.emit(lw("t1", 0, "t1"), addiu("t2", "zero", FIRE_STAGE_ID))
    emitter.bne("t1", "t2", "resume")
    emitter.emit(NOP)

    emitter.emit(*address_words("t2", PICKUP_MANAGER_CONTEXT_PTR_VA))
    emitter.emit(lw("t2", 0, "t2"))
    emitter.beq("t2", "zero", "resume")
    emitter.emit(NOP)

    emitter.emit(lw("t3", 0x6F4, "t2"))
    emitter.emit(addiu("t4", "zero", FIRE_MANAGER_RECORD_COUNT))
    emitter.bne("t3", "t4", "resume")
    emitter.emit(NOP)

    emitter.emit(lw("t3", 0x6F8, "t2"))
    emitter.beq("t3", "zero", "resume")
    emitter.emit(NOP)

    emitter.emit(lw("t1", FIRE_BITSET_OFFSET, "t0"))
    emitter.emit(andi("t1", "t1", 1 << FIRE_STARTING_POTION_BIT))
    emitter.beq("t1", "zero", "resume")
    emitter.emit(NOP)

    record_offset = FIRE_STARTING_POTION_MANAGER_ORDINAL * 0x30
    emitter.emit(addiu("t3", "t3", record_offset))
    emitter.emit(addiu("t4", "zero", 1), sw("t4", 0x2C, "t3"))

    emitter.label("resume")
    emitter.emit(lui("v1", 0x800A), lw("v1", -0x56F0, "v1"))
    emitter.emit(*address_words("t9", PICKUP_MANAGER_RESUME_VA))
    emitter.emit(jr("t9"), NOP)
    return emitter.finish()


def build_experiment_payload() -> tuple[bytes, int]:
    init = build_init()
    restore = build_manager_restore_scanner()

    if len(init) > RESTORE_OFFSET:
        raise AssertionError("V1 init overlaps generalized restore scanner")

    actual_size = RESTORE_OFFSET + len(restore)
    if actual_size > CODE_SIZE:
        raise AssertionError("generalized Fire experiment exceeds V1 code region")

    payload = bytearray(CODE_SIZE)
    payload[: len(init)] = init
    payload[RESTORE_OFFSET : RESTORE_OFFSET + len(restore)] = restore
    return bytes(payload), actual_size


def build_restore_trampoline() -> bytes:
    return words_blob([*address_words("t9", RESTORE_ENTRY), jr("t9"), NOP])


EXPERIMENT_PAYLOAD, EXPERIMENT_ACTUAL_CODE_SIZE = build_experiment_payload()
RESTORE_TRAMPOLINE = build_restore_trampoline()
CAPTURE_HELPER = build_manager_capture_helper()


class ManagerPersistenceFireExperimentPatch:
    """Install the shared manager capture/restore hooks for the Fire proof only."""

    name = "manager-persistence-fire-experiment"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        expected_end = PROVEN_PAYLOAD_ROM + CODE_SIZE
        if (
            rom.read_u32(MKMSZR_FILE_ENTRY_ROM) != PROVEN_PAYLOAD_ROM
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 4) != expected_end
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 8) != 0
        ):
            raise PatchError("manager experiment requires the V1 NativePayloadPatch first")

        rom.expect_bytes(PROVEN_PAYLOAD_ROM, EXPERIMENT_PAYLOAD)
        rom.expect_bytes(NATIVE_BOOTSTRAP_STUB_ROM, LOADER_STUB)
        rom.expect_u32(NATIVE_BOOTSTRAP_HOOK_ROM, jump(NATIVE_BOOTSTRAP_STUB_VA))
        rom.expect_u32(NATIVE_BOOTSTRAP_HOOK_ROM + 4, NOP)

        permanent_size = len(LOADER_STUB) + len(RESTORE_TRAMPOLINE) + len(CAPTURE_HELPER)
        if permanent_size > NATIVE_BOOTSTRAP_STUB_CAPACITY:
            raise PatchError("manager experiment exceeds the confirmed permanent cave")

        rom.expect_bytes(RESTORE_TRAMPOLINE_ROM, bytes(len(RESTORE_TRAMPOLINE)))
        rom.expect_bytes(CAPTURE_HELPER_ROM, bytes(len(CAPTURE_HELPER)))

        rom.expect_bytes(PICKUP_MANAGER_HOOK_ROM, PICKUP_MANAGER_HOOK_EXPECTED)
        rom.expect_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM, PICKUP_MANAGER_CAPTURE_EXPECTED)
        rom.expect_u32(
            PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4,
            PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED,
        )

        # The decisive experiment requires the Potion callback to remain vanilla.
        rom.expect_u32(FIRE_POTION_CALLBACK_FIELD_ROM, FIRE_POTION_CALLBACK_EXPECTED)

        rom.write_bytes(RESTORE_TRAMPOLINE_ROM, RESTORE_TRAMPOLINE)
        rom.write_bytes(CAPTURE_HELPER_ROM, CAPTURE_HELPER)

        rom.write_u32(PICKUP_MANAGER_HOOK_ROM, jump(RESTORE_TRAMPOLINE_VA))
        rom.write_u32(PICKUP_MANAGER_HOOK_ROM + 4, NOP)

        rom.write_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM, jal(CAPTURE_HELPER_VA))

        return (
            "Fire Potion callback remains vanilla; capture is manager-only",
            (
                f"manager capture JAL -> 0x{CAPTURE_HELPER_VA:08X}; "
                f"restore scanner -> 0x{RESTORE_ENTRY:08X}"
            ),
            (
                f"V1 Fire bit {FIRE_STARTING_POTION_BIT} remains at "
                f"0x{STATE_UNCACHED_BASE + FIRE_BITSET_OFFSET:08X} (KSEG1)"
            ),
        )


def manager_persistence_fire_experiment_patches() -> tuple[
    SafeStageSelectorPatch,
    ArenaReservationPatch,
    NativePayloadPatch,
    ManagerPersistenceFireExperimentPatch,
]:
    """Return the test build, including the proven selector needed to reach Fire."""

    return (
        SafeStageSelectorPatch(),
        ArenaReservationPatch(),
        NativePayloadPatch(NativePayloadSpec(payload=EXPERIMENT_PAYLOAD)),
        ManagerPersistenceFireExperimentPatch(),
    )
