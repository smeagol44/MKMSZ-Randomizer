"""Runtime layout V1 and the first runtime-confirmed persistent pickup path.

The V1 layout divides the reserved 1 KiB block into 0x200 bytes of reloadable
native code and 0x200 bytes of persistent MKMSZR state. The only promoted pickup
behavior in this module is the bounded Fire Temple starting-Potion proof.
"""

from __future__ import annotations

from ..data.addresses import (
    CURRENT_STAGE_VA,
    FIRE_POTION_CALLBACK_EXPECTED,
    FIRE_POTION_CALLBACK_FIELD_ROM,
    FIRE_POTION_CALLBACK_VA,
    FIRE_POTION_FLAG_VA,
    FIRE_STAGE_ID,
    MKMSZR_FILE_ENTRY_ROM,
    NATIVE_BOOTSTRAP_HOOK_ROM,
    NATIVE_BOOTSTRAP_STUB_CAPACITY,
    NATIVE_BOOTSTRAP_STUB_ROM,
    NATIVE_BOOTSTRAP_STUB_VA,
    PICKUP_MANAGER_HOOK_EXPECTED,
    PICKUP_MANAGER_HOOK_ROM,
    PICKUP_MANAGER_RESUME_VA,
    PROVEN_PAYLOAD_ROM,
    RUNTIME_V1_CODE_END_EXCLUSIVE,
    RUNTIME_V1_CODE_START,
    RUNTIME_V1_STATE_END_EXCLUSIVE,
    RUNTIME_V1_STATE_START,
)
from ..errors import PatchError
from ..mips import Emitter, addiu, address_words, andi, jr, jump, lui, lw, ori, sw, words_blob
from ..rom import RomImage
from .arena import ArenaReservationPatch
from .base import PatchContext
from .native_payload import (
    NativePayloadPatch,
    NativePayloadSpec,
    build_loader_and_call_stub,
    kseg1_alias,
)

NOP = 0

CODE_CACHED_BASE = RUNTIME_V1_CODE_START
CODE_UNCACHED_BASE = kseg1_alias(CODE_CACHED_BASE)
CODE_SIZE = RUNTIME_V1_CODE_END_EXCLUSIVE - RUNTIME_V1_CODE_START

STATE_CACHED_BASE = RUNTIME_V1_STATE_START
STATE_UNCACHED_BASE = kseg1_alias(STATE_CACHED_BASE)
STATE_SIZE = RUNTIME_V1_STATE_END_EXCLUSIVE - RUNTIME_V1_STATE_START

STATE_MAGIC = 0x4D4B5356  # MKSV
STATE_VERSION = 1
STATE_HEADER_SIZE = 0x20
STATE_FLAGS_OFFSET = 0x10
FIRE_BITSET_OFFSET = 0x20
FIRE_STARTING_POTION_BIT = 0

INIT_OFFSET = 0x000
CAPTURE_OFFSET = 0x0A0
RESTORE_OFFSET = 0x100
INIT_ENTRY = CODE_UNCACHED_BASE + INIT_OFFSET
CAPTURE_ENTRY = CODE_UNCACHED_BASE + CAPTURE_OFFSET
RESTORE_ENTRY = CODE_UNCACHED_BASE + RESTORE_OFFSET

LOADER_STUB = build_loader_and_call_stub(payload_rdram=CODE_CACHED_BASE)
RESTORE_TRAMPOLINE_ROM = NATIVE_BOOTSTRAP_STUB_ROM + len(LOADER_STUB)
RESTORE_TRAMPOLINE_VA = NATIVE_BOOTSTRAP_STUB_VA + len(LOADER_STUB)


def _emit_u32(emitter: Emitter, rt: str, value: int) -> None:
    emitter.emit(lui(rt, value >> 16), ori(rt, rt, value & 0xFFFF))


def build_init() -> bytes:
    emitter = Emitter()
    emitter.emit(*address_words("t0", STATE_UNCACHED_BASE))
    emitter.emit(lw("t1", 0x00, "t0"))
    _emit_u32(emitter, "t2", STATE_MAGIC)
    emitter.bne("t1", "t2", "initialize")
    emitter.emit(NOP)
    emitter.emit(lw("t1", 0x04, "t0"), addiu("t2", "zero", STATE_VERSION))
    emitter.bne("t1", "t2", "initialize")
    emitter.emit(NOP)
    emitter.emit(lw("t1", 0x08, "t0"), addiu("t2", "zero", STATE_SIZE))
    emitter.bne("t1", "t2", "initialize")
    emitter.emit(NOP)
    emitter.emit(lw("t1", 0x0C, "t0"), addiu("t2", "zero", STATE_HEADER_SIZE))
    emitter.bne("t1", "t2", "initialize")
    emitter.emit(NOP, jr("ra"), NOP)

    emitter.label("initialize")
    emitter.emit(addiu("t3", "t0", 0), addiu("t4", "zero", STATE_SIZE // 4))
    emitter.label("clear_loop")
    emitter.emit(sw("zero", 0, "t3"), addiu("t3", "t3", 4), addiu("t4", "t4", -1))
    emitter.bne("t4", "zero", "clear_loop")
    emitter.emit(NOP)
    _emit_u32(emitter, "t1", STATE_MAGIC)
    emitter.emit(sw("t1", 0x00, "t0"))
    emitter.emit(addiu("t1", "zero", STATE_VERSION), sw("t1", 0x04, "t0"))
    emitter.emit(addiu("t1", "zero", STATE_SIZE), sw("t1", 0x08, "t0"))
    emitter.emit(addiu("t1", "zero", STATE_HEADER_SIZE), sw("t1", 0x0C, "t0"))
    emitter.emit(jr("ra"), NOP)
    return emitter.finish()


def build_capture() -> bytes:
    emitter = Emitter()
    emitter.emit(addiu("sp", "sp", -0x18), sw("ra", 0x10, "sp"))
    emitter.emit(*address_words("t9", FIRE_POTION_CALLBACK_VA))
    emitter.emit(0x0320F809, NOP)  # jalr t9
    emitter.emit(*address_words("t0", STATE_UNCACHED_BASE))
    emitter.emit(lw("t1", FIRE_BITSET_OFFSET, "t0"))
    emitter.emit(ori("t1", "t1", 1 << FIRE_STARTING_POTION_BIT))
    emitter.emit(sw("t1", FIRE_BITSET_OFFSET, "t0"))
    emitter.emit(lw("ra", 0x10, "sp"), addiu("sp", "sp", 0x18), jr("ra"), NOP)
    return emitter.finish()


def build_restore() -> bytes:
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
    emitter.emit(lw("t1", FIRE_BITSET_OFFSET, "t0"))
    emitter.emit(andi("t1", "t1", 1 << FIRE_STARTING_POTION_BIT))
    emitter.beq("t1", "zero", "resume")
    emitter.emit(NOP)
    emitter.emit(lui("t1", FIRE_POTION_FLAG_VA >> 16))
    emitter.emit(addiu("t2", "zero", 1), sw("t2", FIRE_POTION_FLAG_VA & 0xFFFF, "t1"))

    emitter.label("resume")
    emitter.emit(lui("v1", 0x800A), lw("v1", -0x56F0, "v1"))
    emitter.emit(*address_words("t9", PICKUP_MANAGER_RESUME_VA))
    emitter.emit(jr("t9"), NOP)
    return emitter.finish()


def build_payload() -> tuple[bytes, int]:
    init = build_init()
    capture = build_capture()
    restore = build_restore()
    if len(init) > CAPTURE_OFFSET:
        raise AssertionError("init routine overlaps capture wrapper")
    if CAPTURE_OFFSET + len(capture) > RESTORE_OFFSET:
        raise AssertionError("capture wrapper overlaps restore wrapper")
    actual_size = RESTORE_OFFSET + len(restore)
    if actual_size > CODE_SIZE:
        raise AssertionError("payload code exceeds the V1 code region")

    payload = bytearray(CODE_SIZE)
    payload[INIT_OFFSET : INIT_OFFSET + len(init)] = init
    payload[CAPTURE_OFFSET : CAPTURE_OFFSET + len(capture)] = capture
    payload[RESTORE_OFFSET : RESTORE_OFFSET + len(restore)] = restore
    return bytes(payload), actual_size


def build_restore_trampoline() -> bytes:
    return words_blob([*address_words("t9", RESTORE_ENTRY), jr("t9"), NOP])


RUNTIME_V1_PAYLOAD, RUNTIME_V1_ACTUAL_CODE_SIZE = build_payload()
RESTORE_TRAMPOLINE = build_restore_trampoline()


class RuntimeV1FirePersistencePatch:
    """Install the runtime-confirmed Fire bit-0 capture/restore hooks."""

    name = "runtime-v1-fire-persistence"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        expected_end = PROVEN_PAYLOAD_ROM + CODE_SIZE
        if (
            rom.read_u32(MKMSZR_FILE_ENTRY_ROM) != PROVEN_PAYLOAD_ROM
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 4) != expected_end
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 8) != 0
        ):
            raise PatchError(
                "runtime V1 persistence requires the V1 NativePayloadPatch first"
            )

        rom.expect_bytes(PROVEN_PAYLOAD_ROM, RUNTIME_V1_PAYLOAD)
        rom.expect_bytes(NATIVE_BOOTSTRAP_STUB_ROM, LOADER_STUB)
        rom.expect_u32(NATIVE_BOOTSTRAP_HOOK_ROM, jump(NATIVE_BOOTSTRAP_STUB_VA))
        rom.expect_u32(NATIVE_BOOTSTRAP_HOOK_ROM + 4, NOP)

        if len(LOADER_STUB) + len(RESTORE_TRAMPOLINE) > NATIVE_BOOTSTRAP_STUB_CAPACITY:
            raise PatchError("V1 loader and restore trampoline exceed the confirmed code cave")

        rom.expect_bytes(RESTORE_TRAMPOLINE_ROM, bytes(len(RESTORE_TRAMPOLINE)))
        rom.expect_bytes(PICKUP_MANAGER_HOOK_ROM, PICKUP_MANAGER_HOOK_EXPECTED)
        rom.expect_u32(FIRE_POTION_CALLBACK_FIELD_ROM, FIRE_POTION_CALLBACK_EXPECTED)

        rom.write_bytes(RESTORE_TRAMPOLINE_ROM, RESTORE_TRAMPOLINE)
        rom.write_u32(PICKUP_MANAGER_HOOK_ROM, jump(RESTORE_TRAMPOLINE_VA))
        rom.write_u32(PICKUP_MANAGER_HOOK_ROM + 4, NOP)
        rom.write_u32(FIRE_POTION_CALLBACK_FIELD_ROM, CAPTURE_ENTRY)

        return (
            (
                f"V1 code 0x{CODE_CACHED_BASE:08X}.."
                f"0x{RUNTIME_V1_CODE_END_EXCLUSIVE - 1:08X}; "
                f"state 0x{STATE_CACHED_BASE:08X}.."
                f"0x{RUNTIME_V1_STATE_END_EXCLUSIVE - 1:08X}"
            ),
            (
                f"Fire starting Potion -> persistent bit {FIRE_STARTING_POTION_BIT} "
                f"at 0x{STATE_CACHED_BASE + FIRE_BITSET_OFFSET:08X}"
            ),
        )


def runtime_v1_fire_patches() -> tuple[
    ArenaReservationPatch,
    NativePayloadPatch,
    RuntimeV1FirePersistencePatch,
]:
    """Return the exact patch sequence used by the runtime-confirmed V1 proof."""

    return (
        ArenaReservationPatch(),
        NativePayloadPatch(NativePayloadSpec(payload=RUNTIME_V1_PAYLOAD)),
        RuntimeV1FirePersistencePatch(),
    )
