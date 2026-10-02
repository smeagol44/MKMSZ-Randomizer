"""Production-shaped global pickup materialization integration.

This module promotes only the runtime-confirmed composition contract into the
shared patch core:

* destination-native stage resources are extended through the pure planner;
* a generic logical inventory award callback and the immediate acquisition
  re-mask helper live in the guarded controls->Toasty expansion gap;
* helper transport reuses the already-established shared file 0x1A;
* no second raw-file load is inserted into pickup-manager stage initialization;
* destination records retain any stock bit-15 activation gate independently of reward identity.

ROM backing for expanded stage resource files remains caller-owned.  This patch
never infers reusable space from FF/padding bytes; GlobalMaterializationPlan must
supply explicit placements and the patch guards both bounds and collisions.

Destination locations with unresolved physical stage-state ownership fail
closed. Bridge's three icon destinations are now represented by their stock
bit-15 activation gates and stage-owned X relocation; Wind/Water/Earth/Prison/
Fire token locations remain blocked until their dedicated wrappers are
implemented.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import pairwise

from ..data.addresses import (
    EXPANSION_POOL_END_EXCLUSIVE,
    FILE_TABLE_ENTRY_SIZE,
    FILE_TABLE_ROM,
)
from ..data.pickups import IDENTITY_OFFSET, STAGE_PICKUPS
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    addu,
    address_words,
    andi,
    jal,
    jr,
    lbu,
    lhu,
    lui,
    lw,
    or_,
    ori,
    sb,
    sh,
    sllv,
    sltiu,
    srl,
    sw,
    words_blob,
)
from ..resource_materialization import (
    AWARD_EXTRA_LIFE,
    AWARD_INVENTORY,
    AWARD_MANA,
    AWARD_POWER_UPGRADE,
    CALLBACK_ACTION_MASK,
    CALLBACK_ACTION_SHIFT,
    CALLBACK_AWARD_MASK,
    CALLBACK_AWARD_SHIFT,
    CALLBACK_ITEM_MASK,
    CANONICAL_VISUAL_DONORS,
    DEST_EARTH_FOUR_SQUARE,
    DEST_EARTH_SQUARE,
    DEST_EARTH_TRIANGLE,
    DEST_FIRE_TRIANGLE_DOWN,
    DEST_FIRE_TRIANGLE_UP,
    DEST_FIRE_TWO_BARS,
    DEST_NONE,
    DEST_PRISON_L1,
    DEST_PRISON_L2,
    DEST_PRISON_STRENGTH,
    DEST_WATER_MOON,
    DEST_WATER_THREE_BARS,
    DEST_WATER_TRIANGLE,
    DEST_WIND_CIRCLE,
    DEST_WIND_THREE_BARS,
    DEST_WIND_TRIANGLE,
    GlobalMaterializationPlan,
    apply_stage_resource_plan,
    bind_materialized_visual_to_stock_selector,
    plan_stage_resources,
    portable_materialized_identity,
)
from ..rom import RomImage
from .base import PatchContext
from .controls_production import CONTROLS_RUNTIME_END, FILE_ROM, MODULE_K0
from .game_settings_turn import EXPANSION_FILE_ENTRY_ROM
from .inventory_boxes import (
    BOX0_VA,
    LOAD_DEFAULT_VA,
    LOAD_MASK_WRAPPER_VA,
)
from .native_payload import kseg1_alias
from .progression_presentation import PROGRESSION_FLASH_CALLBACK_ENTRY
from .temple_special_check import (
    AWARD_HELPER_VA as TEMPLE_BASE_AWARD_HELPER_VA,
    LEGACY_MAP_FLAG_VA,
    MAP_AWARD_CALL_ROM,
    STATE_FLAGS_VA,
    TEMPLE_SPECIAL_CHECK_STATE_MASK,
)
from .toasty_constants import MODULE_K0 as TOASTY_K0

NOP = 0
FILE_TABLE_COUNT = 0xAC

INVENTORY_INSERT_VA = 0x80075448
PICKUP_SOUND_VA = 0x80064C18
CHECKPOINT_PROCESS_VA = 0x80062D60
PROCESS_CREATE_VA = 0x8002830C
EXTRA_LIFE_CALLBACK_VA = 0x80038A1C
MANA_CALLBACK_VA = 0x80038A58
CURRENT_STAGE_VA = 0x8009A910
STAGE_SELECTOR_VA = 0x802C18F8
ACQUIRED_BITS_VA = 0x802C0D54
WIND_THREE_BARS_STATE_VA = 0x802F60A0
WATER_THREE_BARS_STATE_VA = 0x802F2980
EARTH_FOUR_SQUARE_STATE_VA = 0x802F5520
EARTH_TRIANGLE_STATE_VA = 0x802F5E22

PRISON_RESET_VA = 0x802ED538
PRISON_RESET_CALL_ROM = 0x00010E64
PRISON_RESET_CALL_EXPECTED = jal(PRISON_RESET_VA)

TEMPLE_SPECIAL_SELECTOR = 1
TEMPLE_PRESENTATION_HI_ROM = 0x000CC368
TEMPLE_PRESENTATION_LO_ROM = 0x000CC36C
TEMPLE_SELECTOR_A0_ROM = 0x000CC3A8
TEMPLE_SELECTOR_S0_ROM = 0x000CC428
TEMPLE_AWARD_ARG_ROM = MAP_AWARD_CALL_ROM + 4

TEMPLE_POST_PATCH_PRESENTATION_HI = 0x3C04800B
TEMPLE_POST_PATCH_PRESENTATION_LO = 0x24841D3C
TEMPLE_POST_PATCH_SELECTOR_A0 = 0x2604003C
TEMPLE_POST_PATCH_SELECTOR_S0 = 0x8E10003C
TEMPLE_POST_PATCH_AWARD_CALL = jal(TEMPLE_BASE_AWARD_HELPER_VA)
TEMPLE_POST_PATCH_AWARD_ARG = 0x24040004

ACQUISITION_HOOK_ROM = 0x00039FD4
ACQUISITION_DISPLACED_0 = 0x00121040  # sll v0,s2,1
ACQUISITION_DISPLACED_1 = 0x00521021  # addu v0,v0,s2

# The original 0x801B0970 candidate was only 0xF0 bytes and immediately
# preceded the now Runtime-confirmed lifecycle-v06 owner at 0x801B0A60.
# Destination wrappers make the helper larger, so preserve lifecycle/Toasty
# ownership and place this module in the high tail of the already-reserved
# 16-KiB expansion pool.  ROM 0xF6B140 is beyond the current supported
# Toasty module + voice footprint; if a future Toasty asset grows into this
# range the expected-FF guard fails closed rather than silently overlapping.
MATERIALIZER_HELPER_K0 = 0x801B2960
MATERIALIZER_HELPER_K1 = kseg1_alias(MATERIALIZER_HELPER_K0)
MATERIALIZER_HELPER_ROM = 0x00F6B140
MATERIALIZER_RUNTIME_LIMIT = EXPANSION_POOL_END_EXCLUSIVE

GENERIC_AWARD_OFFSET = 0x00


def _align(value: int, alignment: int = 16) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def _emit_checkpoint(e: Emitter, target: int, *, exact_predecessor: int | None) -> None:
    """Emit one destination-owned checkpoint transition."""

    e.emit(lui("t4", 0x802C), lhu("t5", STAGE_SELECTOR_VA & 0xFFFF, "t4"))
    if exact_predecessor is not None:
        e.emit(addiu("t6", "zero", exact_predecessor))
        e.bne("t5", "t6", "action_done")
        e.emit(addiu("t6", "zero", target))
    else:
        e.emit(sltiu("t6", "t5", target))
        e.beq("t6", "zero", "action_done")
        e.emit(addiu("t6", "zero", target))
    e.emit(
        sh("t6", STAGE_SELECTOR_VA & 0xFFFF, "t4"),
        lui("a1", 0x8006),
        addiu("a1", "a1", CHECKPOINT_PROCESS_VA & 0xFFFF),
        jal(PROCESS_CREATE_VA),
        addiu("a0", "zero", 0x15),
    )
    e.beq("zero", "zero", "action_done")
    e.emit(0)


def build_generic_inventory_award() -> bytes:
    """Compose logical award semantics with the physical destination wrapper."""

    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x28),
        sw("ra", 0x24, "sp"),
        sw("s0", 0x20, "sp"),
        sw("s1", 0x1C, "sp"),
        andi("s0", "a1", CALLBACK_ITEM_MASK),
        srl("s1", "a1", CALLBACK_ACTION_SHIFT),
        andi("s1", "s1", CALLBACK_ACTION_MASK),
        srl("t0", "a1", CALLBACK_AWARD_SHIFT),
        andi("t0", "t0", CALLBACK_AWARD_MASK),
    )

    # Logical award.
    e.emit(addiu("t1", "zero", AWARD_INVENTORY))
    e.bne("t0", "t1", "award_extra")
    e.emit(addu("a0", "s0", "zero"))
    e.emit(jal(INVENTORY_INSERT_VA), 0)

    # Prison key credentials are logical-key semantics. Commit immediately when
    # the award occurs inside Prison; stage-entry reconstruction covers keys
    # acquired elsewhere and later re-entry after the stock reset.
    e.emit(
        addiu("t1", "s0", -0x1A),
        sltiu("t2", "t1", 3),
    )
    e.beq("t2", "zero", "award_sound")
    e.emit(lui("t3", 0x800A))
    e.emit(lw("t3", CURRENT_STAGE_VA & 0xFFFF, "t3"), addiu("t2", "zero", 4))
    e.bne("t3", "t2", "award_sound")
    e.emit(addiu("t2", "zero", 1))
    e.emit(
        sllv("t2", "t2", "t1"),
        lui("t3", 0x802C),
        lw("t4", ACQUIRED_BITS_VA & 0xFFFF, "t3"),
        or_("t4", "t4", "t2"),
        sw("t4", ACQUIRED_BITS_VA & 0xFFFF, "t3"),
    )
    e.label("award_sound")
    e.emit(
        addiu("a0", "zero", 0x3B),
        addu("a1", "zero", "zero"),
        addiu("a2", "zero", 0x40),
        jal(PICKUP_SOUND_VA),
        0,
    )
    e.beq("zero", "zero", "dispatch_action")
    e.emit(0)

    e.label("award_extra")
    e.emit(addiu("t1", "zero", AWARD_EXTRA_LIFE))
    e.bne("t0", "t1", "award_mana")
    e.emit(0)
    e.emit(jal(EXTRA_LIFE_CALLBACK_VA), 0)
    e.beq("zero", "zero", "dispatch_action")
    e.emit(0)

    e.label("award_mana")
    e.emit(addiu("t1", "zero", AWARD_MANA))
    e.bne("t0", "t1", "award_power")
    e.emit(0)
    e.emit(jal(MANA_CALLBACK_VA), 0)
    e.beq("zero", "zero", "dispatch_action")
    e.emit(0)

    e.label("award_power")
    e.emit(addiu("t1", "zero", AWARD_POWER_UPGRADE))
    e.bne("t0", "t1", "dispatch_action")
    e.emit(0)
    e.emit(jal(PROGRESSION_FLASH_CALLBACK_ENTRY), 0)

    # Destination-owned stage/location action.
    e.label("dispatch_action")
    e.beq("s1", "zero", "action_done")
    e.emit(0)

    for action, label in (
        (DEST_WIND_CIRCLE, "wind_circle"),
        (DEST_WIND_TRIANGLE, "wind_triangle"),
        (DEST_WIND_THREE_BARS, "wind_three_bars"),
        (DEST_WATER_TRIANGLE, "water_triangle"),
        (DEST_WATER_THREE_BARS, "water_three_bars"),
        (DEST_WATER_MOON, "water_moon"),
        (DEST_EARTH_SQUARE, "earth_square"),
        (DEST_EARTH_FOUR_SQUARE, "earth_four_square"),
        (DEST_EARTH_TRIANGLE, "earth_triangle"),
        (DEST_FIRE_TRIANGLE_UP, "fire_triangle_up"),
        (DEST_FIRE_TWO_BARS, "fire_two_bars"),
        (DEST_FIRE_TRIANGLE_DOWN, "fire_triangle_down"),
        (DEST_PRISON_L1, "prison_l1"),
        (DEST_PRISON_L2, "prison_l2"),
        (DEST_PRISON_STRENGTH, "prison_strength"),
    ):
        e.emit(addiu("t0", "zero", action))
        e.beq("s1", "t0", label)
        e.emit(0)
    e.beq("zero", "zero", "action_done")
    e.emit(0)

    e.label("wind_circle")
    _emit_checkpoint(e, 3, exact_predecessor=2)

    e.label("wind_triangle")
    _emit_checkpoint(e, 5, exact_predecessor=4)

    e.label("wind_three_bars")
    e.emit(lui("t0", 0x802F), addiu("t1", "zero", 1), sb("t1", WIND_THREE_BARS_STATE_VA & 0xFFFF, "t0"))
    e.beq("zero", "zero", "action_done")
    e.emit(0)

    e.label("water_triangle")
    _emit_checkpoint(e, 2, exact_predecessor=1)

    e.label("water_three_bars")
    e.emit(
        lui("t0", 0x802F),
        lbu("t1", WATER_THREE_BARS_STATE_VA & 0xFFFF, "t0"),
        addiu("t1", "t1", 1),
        sb("t1", WATER_THREE_BARS_STATE_VA & 0xFFFF, "t0"),
    )
    _emit_checkpoint(e, 3, exact_predecessor=2)

    e.label("water_moon")
    _emit_checkpoint(e, 5, exact_predecessor=4)

    e.label("earth_square")
    _emit_checkpoint(e, 2, exact_predecessor=None)

    e.label("earth_four_square")
    e.emit(lui("t0", 0x802F), addiu("t1", "zero", 1), sb("t1", EARTH_FOUR_SQUARE_STATE_VA & 0xFFFF, "t0"))
    e.beq("zero", "zero", "action_done")
    e.emit(0)

    e.label("earth_triangle")
    e.emit(lui("t0", 0x802F), addiu("t1", "zero", 1), sh("t1", EARTH_TRIANGLE_STATE_VA & 0xFFFF, "t0"))
    e.beq("zero", "zero", "action_done")
    e.emit(0)

    e.label("fire_triangle_up")
    _emit_checkpoint(e, 2, exact_predecessor=None)

    e.label("fire_two_bars")
    _emit_checkpoint(e, 3, exact_predecessor=None)

    e.label("fire_triangle_down")
    _emit_checkpoint(e, 4, exact_predecessor=None)

    e.label("prison_l1")
    _emit_checkpoint(e, 7, exact_predecessor=None)

    e.label("prison_l2")
    _emit_checkpoint(e, 8, exact_predecessor=None)

    e.label("prison_strength")
    _emit_checkpoint(e, 11, exact_predecessor=None)

    e.label("action_done")
    e.emit(
        lw("s1", 0x1C, "sp"),
        lw("s0", 0x20, "sp"),
        lw("ra", 0x24, "sp"),
        addiu("sp", "sp", 0x28),
        jr("ra"),
        0,
    )
    return e.finish()


GENERIC_AWARD = build_generic_inventory_award()
GENERIC_AWARD_K0 = MATERIALIZER_HELPER_K0 + GENERIC_AWARD_OFFSET

ACQUISITION_REMASK_OFFSET = _align(len(GENERIC_AWARD), 0x40)
ACQUISITION_REMASK_K0 = MATERIALIZER_HELPER_K0 + ACQUISITION_REMASK_OFFSET


def build_acquisition_remask_helper() -> bytes:
    """Commit LIVE then reconstruct stage-masked LIVE after an ordinary award."""

    registers = (
        "v0", "v1", "a0", "a1", "a2", "a3",
        "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9",
    )
    frame = 0x50
    words = [addiu("sp", "sp", -frame)]
    for index, register in enumerate(registers):
        words.append(sw(register, index * 4, "sp"))
    words.append(sw("ra", 0x40, "sp"))
    words.extend((jal(LOAD_DEFAULT_VA), NOP))
    words.extend((jal(LOAD_MASK_WRAPPER_VA), NOP))
    for index, register in enumerate(registers):
        words.append(lw(register, index * 4, "sp"))
    words.append(lw("ra", 0x40, "sp"))
    words.extend(
        (
            ACQUISITION_DISPLACED_1,
            addiu("sp", "sp", frame),
            jr("ra"),
            NOP,
        )
    )
    return words_blob(words)


ACQUISITION_REMASK = build_acquisition_remask_helper()
PRISON_RECONSTRUCT_OFFSET = _align(
    ACQUISITION_REMASK_OFFSET + len(ACQUISITION_REMASK), 0x40
)
PRISON_RECONSTRUCT_K0 = MATERIALIZER_HELPER_K0 + PRISON_RECONSTRUCT_OFFSET


def build_prison_reconstruct_wrapper() -> bytes:
    """Run the stock Prison reset, then rebuild key credentials from all boxes."""

    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x20),
        sw("ra", 0x1C, "sp"),
        jal(PRISON_RESET_VA),
        0,
        lui("t0", 0x800A),
        addiu("t0", "t0", BOX0_VA & 0xFFFF),
        addiu("t1", "t0", 160),
        addu("t2", "zero", "zero"),
    )
    e.label("scan")
    e.emit(lw("t3", 0, "t0"), addiu("t4", "t3", -0x1A), sltiu("t5", "t4", 3))
    e.beq("t5", "zero", "next")
    e.emit(addiu("t6", "zero", 1))
    e.emit(sllv("t6", "t6", "t4"), or_("t2", "t2", "t6"))
    e.label("next")
    e.emit(addiu("t0", "t0", 4))
    e.bne("t0", "t1", "scan")
    e.emit(0)
    e.emit(
        lui("t3", 0x802C),
        sw("t2", ACQUIRED_BITS_VA & 0xFFFF, "t3"),
        lw("ra", 0x1C, "sp"),
        addiu("sp", "sp", 0x20),
        jr("ra"),
        0,
    )
    return e.finish()


PRISON_RECONSTRUCT = build_prison_reconstruct_wrapper()
TEMPLE_AWARD_OFFSET = _align(
    PRISON_RECONSTRUCT_OFFSET + len(PRISON_RECONSTRUCT), 0x40
)
TEMPLE_AWARD_K0 = MATERIALIZER_HELPER_K0 + TEMPLE_AWARD_OFFSET


def build_temple_award_wrapper() -> bytes:
    """Award the 85th shuffled reward, then persist the Temple special check."""

    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x20),
        sw("ra", 0x1C, "sp"),
        jal(GENERIC_AWARD_K0),
        0,
        # The scripted check bypasses the ordinary pickup-manager post-award
        # hook, so explicitly commit LIVE to backing and reconstruct stage mask.
        jal(LOAD_DEFAULT_VA),
        0,
        jal(LOAD_MASK_WRAPPER_VA),
        0,
        *address_words("t0", STATE_FLAGS_VA),
        lw("t1", 0, "t0"),
        ori("t1", "t1", TEMPLE_SPECIAL_CHECK_STATE_MASK),
        sw("t1", 0, "t0"),
        *address_words("t0", LEGACY_MAP_FLAG_VA),
        addiu("t1", "zero", 0x0100),
        sw("t1", 0, "t0"),
        lw("ra", 0x1C, "sp"),
        addiu("sp", "sp", 0x20),
        jr("ra"),
        0,
    )
    return e.finish()


TEMPLE_AWARD = build_temple_award_wrapper()
MATERIALIZER_HELPER_SIZE = _align(
    TEMPLE_AWARD_OFFSET + len(TEMPLE_AWARD), 0x10
)
MATERIALIZER_HELPER_END_K0 = MATERIALIZER_HELPER_K0 + MATERIALIZER_HELPER_SIZE
MATERIALIZER_HELPER_END_ROM = MATERIALIZER_HELPER_ROM + MATERIALIZER_HELPER_SIZE
GENERIC_AWARD_K1 = MATERIALIZER_HELPER_K1 + GENERIC_AWARD_OFFSET

if MATERIALIZER_HELPER_K0 < TOASTY_K0:
    raise AssertionError("materializer helper must remain after Toasty runtime base")
if MATERIALIZER_HELPER_END_K0 > MATERIALIZER_RUNTIME_LIMIT:
    raise AssertionError("materializer helper exceeds the reserved expansion pool")

MATERIALIZER_HELPER = bytearray(MATERIALIZER_HELPER_SIZE)
MATERIALIZER_HELPER[
    GENERIC_AWARD_OFFSET : GENERIC_AWARD_OFFSET + len(GENERIC_AWARD)
] = GENERIC_AWARD
MATERIALIZER_HELPER[
    ACQUISITION_REMASK_OFFSET :
    ACQUISITION_REMASK_OFFSET + len(ACQUISITION_REMASK)
] = ACQUISITION_REMASK
MATERIALIZER_HELPER[
    PRISON_RECONSTRUCT_OFFSET :
    PRISON_RECONSTRUCT_OFFSET + len(PRISON_RECONSTRUCT)
] = PRISON_RECONSTRUCT
MATERIALIZER_HELPER[
    TEMPLE_AWARD_OFFSET : TEMPLE_AWARD_OFFSET + len(TEMPLE_AWARD)
] = TEMPLE_AWARD
MATERIALIZER_HELPER = bytes(MATERIALIZER_HELPER)


def _stage_by_id(stage_id: int):
    try:
        return next(stage for stage in STAGE_PICKUPS if stage.stage_id == stage_id)
    except StopIteration as exc:
        raise PatchError(f"unknown pickup stage ID {stage_id}") from exc


DESTINATION_ACTIONS = {
    (1, 3): DEST_WIND_CIRCLE,
    (1, 4): DEST_WIND_TRIANGLE,
    (1, 5): DEST_WIND_THREE_BARS,
    (2, 6): DEST_WATER_TRIANGLE,
    (2, 7): DEST_WATER_THREE_BARS,
    (2, 8): DEST_WATER_MOON,
    (3, 0): DEST_EARTH_SQUARE,
    (3, 1): DEST_EARTH_FOUR_SQUARE,
    (3, 2): DEST_EARTH_TRIANGLE,
    (5, 4): DEST_FIRE_TRIANGLE_UP,
    (5, 9): DEST_FIRE_TWO_BARS,
    (5, 14): DEST_FIRE_TRIANGLE_DOWN,
    (4, 0): DEST_PRISON_L1,
    (4, 1): DEST_PRISON_L2,
    (4, 3): DEST_PRISON_STRENGTH,
}

CLOSED_TOKEN_DESTINATIONS = frozenset(
    set(DESTINATION_ACTIONS)
    | {
        (4, 2),  # Prison L3: activation gate only
        (8, 0), (8, 1), (8, 2),
        (9, 0), (9, 1), (9, 2),
    }
)


def _has_closed_token_destination_semantics(
    stage_id: int, destination_index: int
) -> bool:
    return (stage_id, destination_index) in CLOSED_TOKEN_DESTINATIONS


def _destination_action(stage_id: int, destination_index: int) -> int:
    return DESTINATION_ACTIONS.get((stage_id, destination_index), DEST_NONE)


def _destination_activation_gate(record) -> bool:
    parameter = int.from_bytes(record.identity[0x04:0x08], "big")
    return bool(parameter & 0x8000)


def _validate_destination(stage_id: int, destination_index: int) -> None:
    stage = _stage_by_id(stage_id)
    if not 0 <= destination_index < len(stage.records):
        raise PatchError(
            f"{stage.title}: destination index {destination_index} is out of range"
        )

    record = stage.records[destination_index]
    if record.progression_token is not None and not _has_closed_token_destination_semantics(
        stage_id, destination_index
    ):
        raise PatchError(
            f"{stage.title} record {destination_index + 1}: destination owns "
            "stage/progression semantics not yet represented by a production wrapper"
        )


def _validate_placements(
    rom: RomImage,
    plan: GlobalMaterializationPlan,
    planned_sizes: dict[int, int],
) -> None:
    placements = sorted(plan.placements, key=lambda item: item.rom_start)
    seen_stages: set[int] = set()

    for placement in placements:
        if placement.stage_id in seen_stages:
            raise PatchError(f"duplicate resource placement for stage {placement.stage_id}")
        seen_stages.add(placement.stage_id)
        if placement.capacity <= 0:
            raise PatchError(f"stage {placement.stage_id}: placement capacity must be positive")
        required = planned_sizes.get(placement.stage_id)
        if required is None:
            raise PatchError(
                f"stage {placement.stage_id}: placement supplied without assignments"
            )
        if required > placement.capacity:
            raise PatchError(
                f"stage {placement.stage_id}: expanded resource requires 0x{required:X} "
                f"bytes; placement capacity is 0x{placement.capacity:X}"
            )
        if not 0 <= placement.rom_start < placement.rom_end_exclusive <= len(rom.data):
            raise PatchError(f"stage {placement.stage_id}: placement exceeds ROM bounds")

    for left, right in pairwise(placements):
        if left.rom_end_exclusive > right.rom_start:
            raise PatchError(
                f"materializer placements overlap: stage {left.stage_id} and "
                f"stage {right.stage_id}"
            )

    assigned_stages = set(planned_sizes)
    if seen_stages != assigned_stages:
        missing = sorted(assigned_stages - seen_stages)
        extra = sorted(seen_stages - assigned_stages)
        raise PatchError(
            f"materializer placement mismatch; missing={missing}, extra={extra}"
        )

    # Guard against every currently active global-file allocation.  The caller
    # must still own the otherwise-unclassified placement; this collision scan
    # merely prevents accidental overlap with known live files.
    for placement in placements:
        start = placement.rom_start
        end = placement.rom_start + planned_sizes[placement.stage_id]
        for file_id in range(FILE_TABLE_COUNT):
            entry = FILE_TABLE_ROM + file_id * FILE_TABLE_ENTRY_SIZE
            file_start = rom.read_u32(entry)
            file_end = rom.read_u32(entry + 4)
            if not file_start or file_end <= file_start:
                continue
            if start < file_end and end > file_start:
                raise PatchError(
                    f"stage {placement.stage_id}: placement overlaps active "
                    f"file 0x{file_id:02X} [0x{file_start:X},0x{file_end:X})"
                )


class GlobalItemMaterializationPatch:
    """Apply an explicit, destination-aware global logical assignment."""

    name = "global-item-materialization"

    def __init__(self, plan: GlobalMaterializationPlan):
        if not plan.assignments and plan.temple_special_item_key is None:
            raise ValueError("global materialization plan must contain an assignment")
        self.plan = plan

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        # This patch runs after controls (and optional rainbow) so file 0x1A is
        # already the authoritative shared expansion transport.
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM, FILE_ROM)
        shared_end = rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)
        if shared_end < FILE_ROM + (CONTROLS_RUNTIME_END - MODULE_K0):
            raise PatchError("materializer requires ControlsProductionPatch first")
        if MATERIALIZER_HELPER_ROM < shared_end < MATERIALIZER_HELPER_END_ROM:
            raise PatchError("shared file 0x1A ends inside the materializer helper slice")
        rom.expect_bytes(
            MATERIALIZER_HELPER_ROM,
            b"\xFF" * MATERIALIZER_HELPER_SIZE,
        )

        rom.expect_u32(ACQUISITION_HOOK_ROM, ACQUISITION_DISPLACED_0)
        rom.expect_u32(ACQUISITION_HOOK_ROM + 4, ACQUISITION_DISPLACED_1)
        rom.expect_u32(PRISON_RESET_CALL_ROM, PRISON_RESET_CALL_EXPECTED)

        assignments_by_stage: dict[int, list] = defaultdict(list)
        seen_destinations: set[tuple[int, int]] = set()
        for assignment in self.plan.assignments:
            destination = (assignment.stage_id, assignment.destination_index)
            if destination in seen_destinations:
                raise PatchError(
                    f"duplicate materializer destination stage={assignment.stage_id} "
                    f"index={assignment.destination_index}"
                )
            seen_destinations.add(destination)
            _validate_destination(*destination)
            if assignment.item_key not in CANONICAL_VISUAL_DONORS:
                raise PatchError(
                    f"no canonical visual donor registered for {assignment.item_key!r}"
                )
            assignments_by_stage[assignment.stage_id].append(assignment)

        temple_special_key = self.plan.temple_special_item_key
        if (
            temple_special_key is not None
            and temple_special_key not in CANONICAL_VISUAL_DONORS
        ):
            raise PatchError(
                f"no canonical visual donor registered for {temple_special_key!r}"
            )

        # Build every stage plan before any write so failures are atomic.
        baseline = bytes(rom.data)
        stage_plans = {}
        stage_ids = set(assignments_by_stage)
        if temple_special_key is not None:
            stage_ids.add(0)

        for stage_id in sorted(stage_ids):
            assignments = assignments_by_stage.get(stage_id, [])
            placement = self.plan.placement_for(stage_id)
            item_keys = [assignment.item_key for assignment in assignments]
            if stage_id == 0 and temple_special_key is not None:
                item_keys.append(temple_special_key)
            stage_plan = plan_stage_resources(
                baseline,
                stage_id,
                item_keys,
                max_size=placement.capacity,
            )
            if stage_id == 0 and temple_special_key is not None:
                stage_plan = bind_materialized_visual_to_stock_selector(
                    stage_plan,
                    temple_special_key,
                    TEMPLE_SPECIAL_SELECTOR,
                )
            stage_plans[stage_id] = stage_plan

        _validate_placements(
            rom,
            self.plan,
            {stage_id: stage_plan.expanded_size for stage_id, stage_plan in stage_plans.items()},
        )

        # Guard destination records against the researched stock catalog and
        # precompute every final identity before any write.  This keeps unsupported
        # source reward semantics fail-closed and atomic.
        planned_identities: dict[tuple[int, int], bytes] = {}
        for stage_id, assignments in assignments_by_stage.items():
            stage = _stage_by_id(stage_id)
            stage_plan = stage_plans[stage_id]
            for assignment in assignments:
                target = stage.records[assignment.destination_index]
                rom.expect_bytes(target.rom_base + IDENTITY_OFFSET, target.identity)
                selector = stage_plan.selector_for(assignment.item_key)
                planned_identities[(stage_id, assignment.destination_index)] = (
                    portable_materialized_identity(
                        assignment.item_key,
                        selector,
                        generic_inventory_callback=GENERIC_AWARD_K1,
                        power_upgrade_callback=PROGRESSION_FLASH_CALLBACK_ENTRY,
                        activation_gate=_destination_activation_gate(target),
                        destination_action=_destination_action(
                            assignment.stage_id, assignment.destination_index
                        ),
                    )
                )

        temple_special_identity: bytes | None = None
        if temple_special_key is not None:
            stage_plan = stage_plans[0]
            temple_special_identity = portable_materialized_identity(
                temple_special_key,
                TEMPLE_SPECIAL_SELECTOR,
                generic_inventory_callback=GENERIC_AWARD_K1,
                power_upgrade_callback=PROGRESSION_FLASH_CALLBACK_ENTRY,
                force_shared_award=True,
            )
            rom.expect_u32(
                TEMPLE_PRESENTATION_HI_ROM, TEMPLE_POST_PATCH_PRESENTATION_HI
            )
            rom.expect_u32(
                TEMPLE_PRESENTATION_LO_ROM, TEMPLE_POST_PATCH_PRESENTATION_LO
            )
            rom.expect_u32(
                TEMPLE_SELECTOR_A0_ROM, TEMPLE_POST_PATCH_SELECTOR_A0
            )
            rom.expect_u32(
                TEMPLE_SELECTOR_S0_ROM, TEMPLE_POST_PATCH_SELECTOR_S0
            )
            rom.expect_u32(MAP_AWARD_CALL_ROM, TEMPLE_POST_PATCH_AWARD_CALL)
            rom.expect_u32(TEMPLE_AWARD_ARG_ROM, TEMPLE_POST_PATCH_AWARD_ARG)

        # Install runtime helpers through existing shared file 0x1A.
        rom.write_bytes(MATERIALIZER_HELPER_ROM, MATERIALIZER_HELPER)
        if shared_end < MATERIALIZER_HELPER_END_ROM:
            rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, MATERIALIZER_HELPER_END_ROM)

        rom.write_u32(ACQUISITION_HOOK_ROM, jal(ACQUISITION_REMASK_K0))
        rom.write_u32(ACQUISITION_HOOK_ROM + 4, ACQUISITION_DISPLACED_0)
        rom.write_u32(PRISON_RESET_CALL_ROM, jal(PRISON_RECONSTRUCT_K0))

        resource_notes: list[str] = []
        for stage_id, stage_plan in stage_plans.items():
            placement = self.plan.placement_for(stage_id)
            start, end = apply_stage_resource_plan(
                rom.data,
                stage_plan,
                placement.rom_start,
                expected_fill=0xFF,
            )
            resource_notes.append(
                f"stage {stage_id}: 0x{start:08X}..0x{end - 1:08X}"
            )

        # Publish the scripted Temple special reward after stage-0 resources are
        # resident. The proven Temple progression/persistence owner remains in
        # place; only visual selector/presentation and logical award are changed.
        if temple_special_identity is not None:
            presentation = int.from_bytes(
                temple_special_identity[0x18:0x1C], "big"
            ) + 4
            present_words = address_words("a0", presentation)
            rom.write_u32(TEMPLE_PRESENTATION_HI_ROM, present_words[0])
            rom.write_u32(TEMPLE_PRESENTATION_LO_ROM, present_words[1])
            selector_offset = TEMPLE_SPECIAL_SELECTOR * 4
            rom.write_u32(
                TEMPLE_SELECTOR_A0_ROM,
                addiu("a0", "s0", selector_offset),
            )
            rom.write_u32(
                TEMPLE_SELECTOR_S0_ROM,
                lw("s0", selector_offset, "s0"),
            )
            encoded_award = int.from_bytes(
                temple_special_identity[0x04:0x08], "big"
            ) & 0x7FFF
            rom.write_u32(MAP_AWARD_CALL_ROM, jal(TEMPLE_AWARD_K0))
            rom.write_u32(
                TEMPLE_AWARD_ARG_ROM,
                ori("a1", "zero", encoded_award),
            )

        # Finally publish ordinary destination reward identities after all
        # resources and helper code are resident.
        for stage_id, assignments in assignments_by_stage.items():
            stage = _stage_by_id(stage_id)
            for assignment in assignments:
                target = stage.records[assignment.destination_index]
                rom.write_bytes(
                    target.rom_base + IDENTITY_OFFSET,
                    planned_identities[(stage_id, assignment.destination_index)],
                )

        return (
            f"{len(self.plan.assignments)} explicit global pickup assignments materialized",
            (
                f"shared file 0x1A helper 0x{MATERIALIZER_HELPER_ROM:08X}.."
                f"0x{MATERIALIZER_HELPER_END_ROM - 1:08X} -> "
                f"RDRAM 0x{MATERIALIZER_HELPER_K0:08X}"
            ),
            "ordinary awards immediately commit backing inventory and reconstruct stage-masked LIVE",
            "destination checkpoint/state wrappers compose independently of logical rewards",
            "Prison acquired bits rebuild after the stock reset from authoritative backing inventory",
            "stock destination bit-15 activation gates are preserved independently of reward identity",
            (
                "Temple special check reward="
                + (temple_special_key if temple_special_key is not None else "interim Herbs")
            ),
            "resource placements: " + ", ".join(resource_notes),
        )
