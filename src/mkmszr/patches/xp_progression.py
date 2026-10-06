"""Production pickup-driven XP / special-move progression.

The ordinary 84-location shuffle runs first. A dedicated RNG namespace then
selects exactly nine locations whose generated identity is Herbs. Their
callback becomes the progression award callback and their presentation pointer
uses a stock-resident blue palette; the same-stage Herbs model/resource remains
intact, so no foreign resource import or new allocation is required.
"""

from __future__ import annotations

import hashlib

from ..data.addresses import (
    COMBO_EXPERIENCE_RENDER_SITES,
    CURRENT_XP_VA,
    MKMSZR_FILE_ENTRY_ROM,
    PICKUP_MANAGER_RESUME_VA,
    PICKUP_SOUND_VA,
    PROVEN_PAYLOAD_ROM,
    XP_AWARD_STORE_SITES,
    XP_CAP_TABLE_ROM,
    XP_CAP_VALUE,
    XP_MAIN_STAGE_CAPS,
    XP_TIER_EVALUATOR_VA,
)
from ..data.pickups import IDENTITY_OFFSET, STAGE_PICKUPS
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    address_words,
    addu,
    jal,
    jalr,
    jr,
    lhu,
    lw,
    sll,
    sltiu,
    sw,
    words_blob,
)
from ..rom import RomImage
from .base import PatchContext
from .inventory_boxes import (
    LOAD_MASK_WRAPPER_UNCACHED_VA,
    PERSISTENCE_RESUME_PATCH,
    PERSISTENCE_RESUME_ROM,
)
from .native_payload import kseg1_alias
from .pickup_randomization import build_stage_assignment
from .run_lifecycle import HOOKS
from .runtime_v2 import CODE_CACHED_BASE, CODE_SIZE, STATE_UNCACHED_BASE

NOP = 0
RNG_DOMAIN = b"MKMSZR:PROGRESSION:HERBS:V1\0"
HERBS_CALLBACK_VA = 0x800389BC
HERBS_PRESENTATION_VA = 0x800B1D38
CALLBACK_OFFSET_WITHIN_IDENTITY = 0x08
PRESENTATION_OFFSET_WITHIN_IDENTITY = 0x18

# Stock global 16-color Ice Blue palette descriptor. It is already resident and is
# referenced broadly by retail code/data, so progression Herbs can reuse it
# without adding ROM/RDRAM allocation or changing the stage-local Herbs model.
PROGRESSION_HERBS_PRESENTATION_VA = 0x800B1E68
PROGRESSION_HERBS_PALETTE_ROM = 0x000B2A68
PROGRESSION_HERBS_PALETTE = bytes.fromhex(
    "00000010"
    "0000 FF74 F331 EACE E28C DA2A D1E8 C9A6"
    "C165 B923 B0E2 A8A1 A080 9840 9020 8800"
)

XP_THRESHOLDS = (85, 258, 834, 1410, 2323, 3315, 4503, 5911, 7354)
PROGRESSION_REWARD_COUNT = len(XP_THRESHOLDS)

# Separate from ordinary pickup-persistence bitsets at state +0x20..+0x3C.
PROGRESSION_COUNT_OFFSET = 0x40
PROGRESSION_XP_OFFSET = 0x44

# Pickup persistence and four-box inventory own the first 0x200 payload bytes.
PROGRESSION_EXTENSION_OFFSET = 0x200
PROGRESSION_EXTENSION_SIZE = 0x100
PROGRESSION_EXTENSION_ROM = PROVEN_PAYLOAD_ROM + PROGRESSION_EXTENSION_OFFSET
PROGRESSION_EXTENSION_CACHED_VA = CODE_CACHED_BASE + PROGRESSION_EXTENSION_OFFSET
PROGRESSION_EXTENSION_UNCACHED_VA = kseg1_alias(PROGRESSION_EXTENSION_CACHED_VA)
PROGRESSION_CALLBACK_ENTRY = PROGRESSION_EXTENSION_UNCACHED_VA


def _callback_from_identity(identity: bytes) -> int:
    start = CALLBACK_OFFSET_WITHIN_IDENTITY
    return int.from_bytes(identity[start : start + 4], "big")


def _candidate_locations(seed: str) -> list[tuple[int, int]]:
    candidates: list[tuple[int, int]] = []
    for stage in STAGE_PICKUPS:
        assignment, _attempts = build_stage_assignment(stage, seed)
        for destination, source_index in enumerate(assignment):
            if _callback_from_identity(stage.records[source_index].identity) == HERBS_CALLBACK_VA:
                candidates.append((stage.stage_id, destination))
    return candidates


def build_progression_locations(seed: str) -> tuple[tuple[int, int], ...]:
    """Select nine generated Herbs locations in an isolated deterministic domain."""

    values = _candidate_locations(seed)
    if len(values) < PROGRESSION_REWARD_COUNT:
        raise PatchError(
            f"only {len(values)} generated Herbs identities are available; "
            f"need {PROGRESSION_REWARD_COUNT}"
        )

    seed_bytes = seed.encode("utf-8")
    for counter, index in enumerate(range(len(values) - 1, 0, -1)):
        digest = hashlib.sha256(
            RNG_DOMAIN + seed_bytes + b"\0" + counter.to_bytes(4, "big")
        ).digest()
        swap_index = int.from_bytes(digest[:8], "big") % (index + 1)
        values[index], values[swap_index] = values[swap_index], values[index]

    return tuple(values[:PROGRESSION_REWARD_COUNT])


def _build_callback(table_va: int) -> bytes:
    e = Emitter()
    e.emit(addiu("sp", "sp", -0x18), sw("ra", 0x10, "sp"))
    e.emit(*address_words("t0", STATE_UNCACHED_BASE))
    e.emit(lw("t1", PROGRESSION_COUNT_OFFSET, "t0"))
    e.emit(sltiu("t2", "t1", PROGRESSION_REWARD_COUNT))
    e.beq("t2", "zero", "done")
    e.emit(NOP)

    e.emit(*address_words("t3", table_va))
    e.emit(sll("t4", "t1", 1), addu("t3", "t3", "t4"))
    e.emit(lhu("t5", 0, "t3"))
    e.emit(addiu("t1", "t1", 1))
    e.emit(sw("t1", PROGRESSION_COUNT_OFFSET, "t0"))
    e.emit(sw("t5", PROGRESSION_XP_OFFSET, "t0"))

    e.emit(*address_words("t6", CURRENT_XP_VA))
    e.emit(sw("t5", 0, "t6"))

    # Refresh the game's native power-tier state from the exact new threshold.
    e.emit(addu("a0", "t5", "zero"))
    e.emit(*address_words("t9", XP_TIER_EVALUATOR_VA))
    e.emit(jalr("t9"), NOP)

    # Match ordinary pickup feedback without adding an inventory item.
    e.emit(addiu("a0", "zero", 0x3B))
    e.emit(addu("a1", "zero", "zero"))
    e.emit(addiu("a2", "zero", 0x40))
    e.emit(*address_words("t9", PICKUP_SOUND_VA))
    e.emit(jalr("t9"), NOP)

    e.label("done")
    e.emit(lw("ra", 0x10, "sp"), addiu("sp", "sp", 0x18), jr("ra"), NOP)
    return e.finish()


def _build_restore() -> bytes:
    """Restore persistent XP, then preserve four-box stage reconstruction.

    Do not call the native tier evaluator here. Diagnostic B runtime-confirmed
    that the evaluator is unsafe at this early stage-init boundary, while the
    tier state already established at pickup collection survives normal stage
    transitions and title-menu direct-stage routing.
    """

    e = Emitter()
    e.emit(addiu("sp", "sp", -0x18), sw("ra", 0x10, "sp"))
    e.emit(*address_words("t0", STATE_UNCACHED_BASE))
    e.emit(lw("t1", PROGRESSION_XP_OFFSET, "t0"))
    e.emit(*address_words("t2", CURRENT_XP_VA))
    e.emit(sw("t1", 0, "t2"))

    e.emit(*address_words("t9", LOAD_MASK_WRAPPER_UNCACHED_VA))
    e.emit(jalr("t9"), NOP)

    e.emit(lw("ra", 0x10, "sp"), addiu("sp", "sp", 0x18), jr("ra"), NOP)
    return e.finish()


def _align4(value: int) -> int:
    return (value + 3) & ~3


def build_progression_extension() -> tuple[bytes, int, int]:
    probe = _build_callback(0)
    table_offset = _align4(len(probe))
    table_va = PROGRESSION_EXTENSION_UNCACHED_VA + table_offset
    callback = _build_callback(table_va)
    if len(callback) != len(probe):
        raise AssertionError("progression callback size depends on table address")

    table = b"".join(value.to_bytes(2, "big") for value in XP_THRESHOLDS)
    restore_offset = _align4(table_offset + len(table))
    restore = _build_restore()
    end = restore_offset + len(restore)
    if end > PROGRESSION_EXTENSION_SIZE:
        raise AssertionError(
            f"progression extension exceeds 0x{PROGRESSION_EXTENSION_SIZE:X} bytes: "
            f"0x{end:X}"
        )

    blob = bytearray(PROGRESSION_EXTENSION_SIZE)
    blob[: len(callback)] = callback
    blob[table_offset : table_offset + len(table)] = table
    blob[restore_offset : restore_offset + len(restore)] = restore
    return bytes(blob), table_offset, restore_offset


PROGRESSION_EXTENSION, THRESHOLD_TABLE_OFFSET, PROGRESSION_RESTORE_OFFSET = (
    build_progression_extension()
)
PROGRESSION_RESTORE_ENTRY = PROGRESSION_EXTENSION_UNCACHED_VA + PROGRESSION_RESTORE_OFFSET

PROGRESSION_RESUME_PATCH = words_blob(
    [
        jal(PROGRESSION_RESTORE_ENTRY),
        0x3C03800A,  # displaced LUI v1, 0x800A
        *address_words("t9", PICKUP_MANAGER_RESUME_VA),
        jr("t9"),
        0x8C63A910,  # displaced LW v1, -0x56F0(v1)
    ]
)
if len(PROGRESSION_RESUME_PATCH) != len(PERSISTENCE_RESUME_PATCH):
    raise AssertionError("progression resume patch changed scanner size")



# Powers-as-pickups OFF keeps the game's stock XP award stores/caps, but stock
# stage reconstruction does not preserve CURRENT_XP_VA. Reuse the already-owned
# XP payload/state instead of adding a second authority: snapshot native earned
# XP at the established lifecycle-v06 teardown seams, then restore state +0x44
# at the same pickup-manager stage-init boundary used by pickup progression.
#
# The last 0x20 bytes of the historical 0x100 progression extension belong to
# the optional Runtime-V2 tail (rainbow in affected builds), so this late OFF
# patch writes only the canonical 0xE0-byte XP payload owner.
EARNED_XP_EXTENSION_SIZE = 0xE0
EARNED_XP_EXTENSION_ROM = PROGRESSION_EXTENSION_ROM
LIFECYCLE_PAUSE_ENTRY_UNCACHED_VA = 0xA01B0BC0
LIFECYCLE_REASON_ENTRY_UNCACHED_VA = 0xA01B0C10
JR_K0 = 0x03400008


def _k0_jump_words(address: int, delay_slot: int = NOP) -> tuple[int, int, int, int]:
    return (
        0x3C1A0000 | ((address >> 16) & 0xFFFF),  # lui k0,hi
        0x375A0000 | (address & 0xFFFF),          # ori k0,k0,lo
        JR_K0,
        delay_slot,
    )


def _build_earned_xp_save_wrapper(resume_va: int) -> bytes:
    """Mirror native current XP to MKSV +0x44, then tail-enter lifecycle v06."""

    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x10),
        sw("t0", 0x00, "sp"),
        sw("t1", 0x04, "sp"),
    )
    e.emit(*address_words("t0", CURRENT_XP_VA), lw("t1", 0, "t0"))
    e.emit(
        *address_words("t0", STATE_UNCACHED_BASE),
        sw("t1", PROGRESSION_XP_OFFSET, "t0"),
    )
    e.emit(
        lw("t0", 0x00, "sp"),
        lw("t1", 0x04, "sp"),
        addiu("sp", "sp", 0x10),
    )
    e.emit(*_k0_jump_words(resume_va))
    return e.finish()


def build_earned_xp_extension() -> tuple[bytes, int, int, int]:
    pause = _build_earned_xp_save_wrapper(LIFECYCLE_PAUSE_ENTRY_UNCACHED_VA)
    reason_offset = _align4(len(pause))
    reason = _build_earned_xp_save_wrapper(LIFECYCLE_REASON_ENTRY_UNCACHED_VA)
    restore_offset = _align4(reason_offset + len(reason))
    restore = _build_restore()
    end = restore_offset + len(restore)
    if end > EARNED_XP_EXTENSION_SIZE:
        raise AssertionError(
            f"earned-XP persistence exceeds 0x{EARNED_XP_EXTENSION_SIZE:X} bytes: "
            f"0x{end:X}"
        )

    blob = bytearray(EARNED_XP_EXTENSION_SIZE)
    blob[: len(pause)] = pause
    blob[reason_offset : reason_offset + len(reason)] = reason
    blob[restore_offset : restore_offset + len(restore)] = restore
    return bytes(blob), 0, reason_offset, restore_offset


(
    EARNED_XP_EXTENSION,
    EARNED_XP_PAUSE_SAVE_OFFSET,
    EARNED_XP_REASON_SAVE_OFFSET,
    EARNED_XP_RESTORE_OFFSET,
) = build_earned_xp_extension()
EARNED_XP_PAUSE_SAVE_ENTRY = (
    PROGRESSION_EXTENSION_UNCACHED_VA + EARNED_XP_PAUSE_SAVE_OFFSET
)
EARNED_XP_REASON_SAVE_ENTRY = (
    PROGRESSION_EXTENSION_UNCACHED_VA + EARNED_XP_REASON_SAVE_OFFSET
)
EARNED_XP_RESTORE_ENTRY = PROGRESSION_EXTENSION_UNCACHED_VA + EARNED_XP_RESTORE_OFFSET

EARNED_XP_RESUME_PATCH = words_blob(
    [
        jal(EARNED_XP_RESTORE_ENTRY),
        0x3C03800A,  # displaced LUI v1, 0x800A
        *address_words("t9", PICKUP_MANAGER_RESUME_VA),
        jr("t9"),
        0x8C63A910,  # displaced LW v1, -0x56F0(v1)
    ]
)
if len(EARNED_XP_RESUME_PATCH) != len(PERSISTENCE_RESUME_PATCH):
    raise AssertionError("earned-XP resume patch changed scanner size")


def _lifecycle_hook_patch(entry: int, delay_slot: int) -> bytes:
    return words_blob(_k0_jump_words(entry, delay_slot))


# Fail loudly if lifecycle-v06's validated direct entries ever move. The OFF
# composition retargets only the first five teardown hooks through XP snapshot
# wrappers; constructor and final-Game-Over hooks remain byte-for-byte v06.
if HOOKS[0][2] != _lifecycle_hook_patch(LIFECYCLE_PAUSE_ENTRY_UNCACHED_VA, NOP):
    raise AssertionError("lifecycle-v06 Pause entry drifted")
for reason, hook in enumerate(HOOKS[1:5], start=1):
    if hook[2] != _lifecycle_hook_patch(
        LIFECYCLE_REASON_ENTRY_UNCACHED_VA,
        0x241B0000 | reason,  # addiu k1,zero,reason
    ):
        raise AssertionError(f"lifecycle-v06 reason entry {reason} drifted")

EARNED_XP_LIFECYCLE_HOOK_PATCHES = tuple(
    (
        offset,
        replacement,
        _lifecycle_hook_patch(
            EARNED_XP_PAUSE_SAVE_ENTRY if index == 0 else EARNED_XP_REASON_SAVE_ENTRY,
            int.from_bytes(replacement[12:16], "big"),
        ),
        label,
    )
    for index, (offset, _expected, replacement, label) in enumerate(HOOKS[:5])
)


class EarnedXPPersistencePatch:
    """Persist stock-earned XP when Powers as pickups is disabled."""

    name = "earned-xp-persistence"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        expected_end = PROVEN_PAYLOAD_ROM + CODE_SIZE
        if (
            rom.read_u32(MKMSZR_FILE_ENTRY_ROM) != PROVEN_PAYLOAD_ROM
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 4) != expected_end
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 8) != 0
        ):
            raise PatchError(
                "earned-XP persistence requires the production V2 native payload first"
            )

        rom.expect_bytes(
            EARNED_XP_EXTENSION_ROM,
            bytes(EARNED_XP_EXTENSION_SIZE),
        )
        rom.expect_bytes(PERSISTENCE_RESUME_ROM, PERSISTENCE_RESUME_PATCH)

        # OFF mode must retain all stock XP-producing behavior. These guards
        # deliberately reject composing this path after pickup-mode XP edits.
        for offset, expected in XP_AWARD_STORE_SITES.items():
            rom.expect_u32(offset, expected)
        for offset, expected in COMBO_EXPERIENCE_RENDER_SITES.items():
            rom.expect_u32(offset, expected)
        for stage_id, expected in XP_MAIN_STAGE_CAPS.items():
            rom.expect_u16(XP_CAP_TABLE_ROM + stage_id * 2, expected)

        for offset, expected, _patched, _label in EARNED_XP_LIFECYCLE_HOOK_PATCHES:
            rom.expect_bytes(offset, expected)

        rom.write_bytes(EARNED_XP_EXTENSION_ROM, EARNED_XP_EXTENSION)
        rom.write_bytes(PERSISTENCE_RESUME_ROM, EARNED_XP_RESUME_PATCH)
        for offset, _expected, patched, _label in EARNED_XP_LIFECYCLE_HOOK_PATCHES:
            rom.write_bytes(offset, patched)

        return (
            "stock combat/award XP stores, combo XP UI, and stage caps remain untouched",
            "native current XP is snapshotted to MKSV +0x44 before lifecycle-v06 teardown",
            "stage init restores MKSV +0x44 before the existing four-box reconstruction",
            "native tier evaluator remains absent from stage-init restore per Diagnostic B",
            "lifecycle-v06 constructor and final Game Over/reset hooks remain unchanged",
        )


class XPProgressionPatch:
    """Install no-combat-XP and pickup-driven native progression runtime."""

    name = "xp-progression"

    def __init__(self, *, global_mode: bool = False):
        self.global_mode = global_mode

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        if not context.seed:
            return ("no seed supplied; XP progression generation skipped",)

        expected_end = PROVEN_PAYLOAD_ROM + CODE_SIZE
        if (
            rom.read_u32(MKMSZR_FILE_ENTRY_ROM) != PROVEN_PAYLOAD_ROM
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 4) != expected_end
            or rom.read_u32(MKMSZR_FILE_ENTRY_ROM + 8) != 0
        ):
            raise PatchError("XP progression requires the production V2 native payload first")

        rom.expect_bytes(PROGRESSION_EXTENSION_ROM, bytes(PROGRESSION_EXTENSION_SIZE))
        rom.expect_bytes(PERSISTENCE_RESUME_ROM, PERSISTENCE_RESUME_PATCH)

        stage_by_id = {stage.stage_id: stage for stage in STAGE_PICKUPS}
        selected: tuple[tuple[int, int], ...] = ()
        if not self.global_mode:
            # Stage-local mode still overlays nine generated Herbs after the
            # accepted within-stage shuffle. Global mode receives explicit
            # Power Upgrade rewards from the 85-item generator instead.
            for stage in STAGE_PICKUPS:
                assignment, _attempts = build_stage_assignment(stage, context.seed)
                for destination, source_index in enumerate(assignment):
                    target = stage.records[destination]
                    rom.expect_bytes(
                        target.rom_base + IDENTITY_OFFSET,
                        stage.records[source_index].identity,
                    )

            rom.expect_bytes(
                PROGRESSION_HERBS_PALETTE_ROM,
                PROGRESSION_HERBS_PALETTE,
            )

            selected = build_progression_locations(context.seed)
            for stage_id, destination in selected:
                stage = stage_by_id[stage_id]
                callback_rom = (
                    stage.records[destination].rom_base
                    + IDENTITY_OFFSET
                    + CALLBACK_OFFSET_WITHIN_IDENTITY
                )
                presentation_rom = (
                    stage.records[destination].rom_base
                    + IDENTITY_OFFSET
                    + PRESENTATION_OFFSET_WITHIN_IDENTITY
                )
                rom.expect_u32(callback_rom, HERBS_CALLBACK_VA)
                rom.expect_u32(presentation_rom, HERBS_PRESENTATION_VA)

        for offset, expected in XP_AWARD_STORE_SITES.items():
            rom.expect_u32(offset, expected)
        for offset, expected in COMBO_EXPERIENCE_RENDER_SITES.items():
            rom.expect_u32(offset, expected)
        for stage_id, expected in XP_MAIN_STAGE_CAPS.items():
            rom.expect_u16(XP_CAP_TABLE_ROM + stage_id * 2, expected)

        rom.write_bytes(PROGRESSION_EXTENSION_ROM, PROGRESSION_EXTENSION)
        rom.write_bytes(PERSISTENCE_RESUME_ROM, PROGRESSION_RESUME_PATCH)

        for stage_id, destination in selected:
            stage = stage_by_id[stage_id]
            callback_rom = (
                stage.records[destination].rom_base
                + IDENTITY_OFFSET
                + CALLBACK_OFFSET_WITHIN_IDENTITY
            )
            presentation_rom = (
                stage.records[destination].rom_base
                + IDENTITY_OFFSET
                + PRESENTATION_OFFSET_WITHIN_IDENTITY
            )
            rom.write_u32(callback_rom, PROGRESSION_CALLBACK_ENTRY)
            rom.write_u32(presentation_rom, PROGRESSION_HERBS_PRESENTATION_VA)

        for offset in XP_AWARD_STORE_SITES:
            rom.write_u32(offset, NOP)
        for offset in COMBO_EXPERIENCE_RENDER_SITES:
            rom.write_u32(offset, NOP)
        for stage_id in XP_MAIN_STAGE_CAPS:
            rom.write_u16(XP_CAP_TABLE_ROM + stage_id * 2, XP_CAP_VALUE)

        if self.global_mode:
            reward_note = (
                "global mode: progression callback/state installed; shuffled "
                "Power Upgrade rewards are emitted by the global materializer"
            )
        else:
            locations = ", ".join(
                f"{stage_by_id[stage_id].key}:{destination + 1}"
                for stage_id, destination in selected
            )
            reward_note = (
                "9 generated Herbs callbacks -> progression callback and stock-resident "
                f"blue palette 0x{PROGRESSION_HERBS_PRESENTATION_VA:08X} ({locations})"
            )
        return (
            "normal XP stores disabled at the central helper and all three mapped direct paths",
            "combo EXPERIENCE label/value suppressed; HITS render calls preserved",
            f"8 main-stage XP caps guarded and set to {XP_CAP_VALUE}",
            reward_note,
            "progression count/XP use V2 state +0x40/+0x44; ordinary pickup bitsets remain separate",
        )
