"""Production-shaped global pickup materialization integration.

This module promotes only the runtime-confirmed composition contract into the
shared patch core:

* destination-native stage resources are extended through the pure planner;
* a generic logical inventory award callback and the immediate acquisition
  re-mask helper live in the guarded controls->Toasty expansion gap;
* helper transport reuses the already-established shared file 0x1A;
* no second raw-file load is inserted into pickup-manager stage initialization;
* Fortress boss reward records retain their encounter-owned high-bit gate.

ROM backing for expanded stage resource files remains caller-owned.  This patch
never infers reusable space from FF/padding bytes; GlobalMaterializationPlan must
supply explicit placements and the patch guards both bounds and collisions.

Destination locations with unresolved physical stage-state ownership fail
closed.  In particular, ordinary Wind/Water/Earth/Prison/Fire/Bridge token
locations are not silently rewritten until their destination wrapper semantics
are represented explicitly by the global generator.
"""

from __future__ import annotations

from collections import defaultdict

from ..data.addresses import FILE_TABLE_ENTRY_SIZE, FILE_TABLE_ROM
from ..data.pickups import IDENTITY_OFFSET, STAGE_PICKUPS
from ..errors import PatchError
from ..mips import addiu, addu, andi, jal, jr, lw, sw, words_blob
from ..resource_materialization import (
    CANONICAL_VISUAL_DONORS,
    GlobalMaterializationPlan,
    apply_stage_resource_plan,
    plan_stage_resources,
    portable_materialized_identity,
)
from ..rom import RomImage
from .base import PatchContext
from .controls_production import CONTROLS_RUNTIME_END, FILE_ROM, MODULE_K0
from .game_settings_turn import EXPANSION_FILE_ENTRY_ROM
from .inventory_boxes import LOAD_DEFAULT_VA, LOAD_MASK_WRAPPER_VA
from .native_payload import kseg1_alias
from .toasty_constants import MODULE_K0 as TOASTY_K0

NOP = 0
FILE_TABLE_COUNT = 0xAC

INVENTORY_INSERT_VA = 0x80075448
PICKUP_SOUND_VA = 0x80064C18

ACQUISITION_HOOK_ROM = 0x00039FD4
ACQUISITION_DISPLACED_0 = 0x00121040  # sll v0,s2,1
ACQUISITION_DISPLACED_1 = 0x00521021  # addu v0,v0,s2

# v02 runtime-confirmed placement: after accepted controls runtime and optional
# compact-rainbow loader, below fixed Toasty base.
MATERIALIZER_HELPER_K0 = 0x801B0900
MATERIALIZER_HELPER_K1 = kseg1_alias(MATERIALIZER_HELPER_K0)
MATERIALIZER_HELPER_ROM = FILE_ROM + (MATERIALIZER_HELPER_K0 - MODULE_K0)
MATERIALIZER_RUNTIME_LIMIT = TOASTY_K0

GENERIC_AWARD_OFFSET = 0x00


def _align(value: int, alignment: int = 16) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def build_generic_inventory_award() -> bytes:
    """Award low-15-bit callback parameter and reproduce ordinary pickup SFX."""

    return words_blob(
        [
            addiu("sp", "sp", -0x20),
            sw("ra", 0x1C, "sp"),
            sw("a1", 0x18, "sp"),
            andi("a0", "a1", 0x7FFF),
            jal(INVENTORY_INSERT_VA),
            NOP,
            addiu("a0", "zero", 0x3B),
            addu("a1", "zero", "zero"),
            addiu("a2", "zero", 0x40),
            jal(PICKUP_SOUND_VA),
            NOP,
            lw("a1", 0x18, "sp"),
            lw("ra", 0x1C, "sp"),
            addiu("sp", "sp", 0x20),
            jr("ra"),
            NOP,
        ]
    )


GENERIC_AWARD = build_generic_inventory_award()
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
MATERIALIZER_HELPER_SIZE = _align(
    ACQUISITION_REMASK_OFFSET + len(ACQUISITION_REMASK), 0x10
)
MATERIALIZER_HELPER_END_K0 = MATERIALIZER_HELPER_K0 + MATERIALIZER_HELPER_SIZE
MATERIALIZER_HELPER_END_ROM = MATERIALIZER_HELPER_ROM + MATERIALIZER_HELPER_SIZE
GENERIC_AWARD_K1 = MATERIALIZER_HELPER_K1 + GENERIC_AWARD_OFFSET

if MATERIALIZER_HELPER_K0 < CONTROLS_RUNTIME_END:
    raise AssertionError("materializer helper overlaps accepted controls runtime")
if MATERIALIZER_HELPER_END_K0 > MATERIALIZER_RUNTIME_LIMIT:
    raise AssertionError("materializer helper reaches Toasty runtime allocation")

MATERIALIZER_HELPER = bytearray(MATERIALIZER_HELPER_SIZE)
MATERIALIZER_HELPER[
    GENERIC_AWARD_OFFSET : GENERIC_AWARD_OFFSET + len(GENERIC_AWARD)
] = GENERIC_AWARD
MATERIALIZER_HELPER[
    ACQUISITION_REMASK_OFFSET :
    ACQUISITION_REMASK_OFFSET + len(ACQUISITION_REMASK)
] = ACQUISITION_REMASK
MATERIALIZER_HELPER = bytes(MATERIALIZER_HELPER)


def _stage_by_id(stage_id: int):
    try:
        return next(stage for stage in STAGE_PICKUPS if stage.stage_id == stage_id)
    except StopIteration as exc:
        raise PatchError(f"unknown pickup stage ID {stage_id}") from exc


def _is_fortress_boss_destination(stage_id: int, destination_index: int) -> bool:
    return stage_id == 9 and destination_index in (0, 1, 2)


def _validate_destination(stage_id: int, destination_index: int) -> None:
    stage = _stage_by_id(stage_id)
    if not 0 <= destination_index < len(stage.records):
        raise PatchError(
            f"{stage.title}: destination index {destination_index} is out of range"
        )

    record = stage.records[destination_index]
    if record.progression_token is not None and not _is_fortress_boss_destination(
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

    for left, right in zip(placements, placements[1:]):
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
        if not plan.assignments:
            raise ValueError("global materialization plan must contain assignments")
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

        # Build every stage plan before any write so failures are atomic.
        baseline = bytes(rom.data)
        stage_plans = {}
        for stage_id, assignments in assignments_by_stage.items():
            placement = self.plan.placement_for(stage_id)
            stage_plans[stage_id] = plan_stage_resources(
                baseline,
                stage_id,
                (assignment.item_key for assignment in assignments),
                max_size=placement.capacity,
            )

        _validate_placements(
            rom,
            self.plan,
            {stage_id: stage_plan.expanded_size for stage_id, stage_plan in stage_plans.items()},
        )

        # Guard destination records against the researched stock catalog.  The
        # explicit global plan is mutually exclusive with stage-local tuple
        # randomization and pickup-XP callback overlay in the current pipeline.
        for stage_id, assignments in assignments_by_stage.items():
            stage = _stage_by_id(stage_id)
            for assignment in assignments:
                target = stage.records[assignment.destination_index]
                rom.expect_bytes(target.rom_base + IDENTITY_OFFSET, target.identity)

        # Install runtime helpers through existing shared file 0x1A.
        rom.write_bytes(MATERIALIZER_HELPER_ROM, MATERIALIZER_HELPER)
        if shared_end < MATERIALIZER_HELPER_END_ROM:
            rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, MATERIALIZER_HELPER_END_ROM)

        rom.write_u32(ACQUISITION_HOOK_ROM, jal(ACQUISITION_REMASK_K0))
        rom.write_u32(ACQUISITION_HOOK_ROM + 4, ACQUISITION_DISPLACED_0)

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

        # Finally publish destination reward identities after all resources and
        # helper code are resident.
        for stage_id, assignments in assignments_by_stage.items():
            stage = _stage_by_id(stage_id)
            stage_plan = stage_plans[stage_id]
            for assignment in assignments:
                target = stage.records[assignment.destination_index]
                selector = stage_plan.selector_for(assignment.item_key)
                identity = portable_materialized_identity(
                    assignment.item_key,
                    selector,
                    generic_inventory_callback=GENERIC_AWARD_K1,
                    boss_gate=_is_fortress_boss_destination(
                        assignment.stage_id, assignment.destination_index
                    ),
                )
                rom.write_bytes(target.rom_base + IDENTITY_OFFSET, identity)

        return (
            f"{len(self.plan.assignments)} explicit global pickup assignments materialized",
            (
                f"shared file 0x1A helper 0x{MATERIALIZER_HELPER_ROM:08X}.."
                f"0x{MATERIALIZER_HELPER_END_ROM - 1:08X} -> "
                f"RDRAM 0x{MATERIALIZER_HELPER_K0:08X}"
            ),
            "ordinary awards immediately commit backing inventory and reconstruct stage-masked LIVE",
            "Fortress boss reward destinations preserve encounter-owned activation bit",
            "resource placements: " + ", ".join(resource_notes),
        )
