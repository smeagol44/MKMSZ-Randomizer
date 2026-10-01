"""Guarded production materializer for deterministic ordinary-enemy plans.

The materializer supports native profiles, bounded Runtime-confirmed raw
foreign profiles, compact 16-color PRIS profiles, and the phase-aware Prison
FAST-MONK profile. Unsupported semantic/resource combinations remain fail-closed.
"""

from __future__ import annotations

from ..enemy_planner import EnemyPlan, build_enemy_plan, format_enemy_plan
from ..errors import PatchError
from ..fighter_compaction import compact_pris_file
from ..rom import RomImage
from .base import PatchContext

MATERIALIZABLE_PROFILE_KEYS = frozenset(
    {
        "temple-native",
        "wind-native",
        "water-native",
        "water-hulk",
        "water-fast",
        "water-pris15",
        "water-pris16",
        "water-pris17",
        "water-pris14-16",
        "earth-native",
        "prison-native",
        "prison-fast-phase",
        "fire-native",
        "bridge-native",
        "fortress-native",
    }
)

WATER_FIRST_FILE_SIZE_IMM = 0x000B58B8
WATER_FIRST_SLOT_HI = 0x000B58C8
WATER_FIRST_SLOT_STORE = 0x000B58CC
WATER_FIRST_FILE_LOAD_IMM = 0x000B58D4

WATER_SECOND_TRANSACTION = (
    (0x000B58D8, 0x0C019738),
    (0x000B58DC, 0x2404008D),
    (0x000B58E0, 0x0C01990F),
    (0x000B58E4, 0x00402021),
    (0x000B58E8, 0x00402821),
    (0x000B58EC, 0x3C01802E),
    (0x000B58F0, 0xAC257268),
    (0x000B58F4, 0x0C019759),
    (0x000B58F8, 0x2404008D),
)

WATER_STOCK_FIRST = (
    (WATER_FIRST_FILE_SIZE_IMM, 0x2404008C),
    (WATER_FIRST_SLOT_HI, 0x3C018011),
    (WATER_FIRST_SLOT_STORE, 0xAC2514C0),
    (WATER_FIRST_FILE_LOAD_IMM, 0x2404008C),
)

WATER_PROFILE_PATCHES: dict[str, tuple[tuple[int, int, int], ...]] = {
    "water-fast": (
        (WATER_FIRST_FILE_SIZE_IMM, 0x2404008C, 0x24040020),
        (WATER_FIRST_SLOT_HI, 0x3C018011, 0x3C01800C),
        (WATER_FIRST_SLOT_STORE, 0xAC2514C0, 0xAC252560),
        (WATER_FIRST_FILE_LOAD_IMM, 0x2404008C, 0x24040020),
    ),
    "water-pris15": (
        (WATER_FIRST_FILE_SIZE_IMM, 0x2404008C, 0x2404008E),
        (WATER_FIRST_SLOT_HI, 0x3C018011, 0x3C018011),
        (WATER_FIRST_SLOT_STORE, 0xAC2514C0, 0xAC251528),
        (WATER_FIRST_FILE_LOAD_IMM, 0x2404008C, 0x2404008E),
        (0x000B58DC, 0x2404008D, 0x2404008F),
        (0x000B58EC, 0x3C01802E, 0x3C018011),
        (0x000B58F0, 0xAC257268, 0xAC252008),
        (0x000B58F8, 0x2404008D, 0x2404008F),
    ),
    "water-pris16": (
        (WATER_FIRST_FILE_SIZE_IMM, 0x2404008C, 0x2404008E),
        (WATER_FIRST_SLOT_HI, 0x3C018011, 0x3C018011),
        (WATER_FIRST_SLOT_STORE, 0xAC2514C0, 0xAC251528),
        (WATER_FIRST_FILE_LOAD_IMM, 0x2404008C, 0x2404008E),
        (0x000B58DC, 0x2404008D, 0x24040090),
        (0x000B58EC, 0x3C01802E, 0x3C01802C),
        (0x000B58F0, 0xAC257268, 0xAC250FA0),
        (0x000B58F8, 0x2404008D, 0x24040090),
    ),
    "water-pris14-16": (
        (WATER_FIRST_FILE_SIZE_IMM, 0x2404008C, 0x2404008E),
        (WATER_FIRST_SLOT_HI, 0x3C018011, 0x3C018011),
        (WATER_FIRST_SLOT_STORE, 0xAC2514C0, 0xAC251528),
        (WATER_FIRST_FILE_LOAD_IMM, 0x2404008C, 0x2404008E),
        (0x000B58DC, 0x2404008D, 0x24040090),
        (0x000B58EC, 0x3C01802E, 0x3C01802C),
        (0x000B58F0, 0xAC257268, 0xAC250FA0),
        (0x000B58F8, 0x2404008D, 0x24040090),
    ),
    "water-pris17": (
        (WATER_FIRST_FILE_SIZE_IMM, 0x2404008C, 0x2404008E),
        (WATER_FIRST_SLOT_HI, 0x3C018011, 0x3C018011),
        (WATER_FIRST_SLOT_STORE, 0xAC2514C0, 0xAC251528),
        (WATER_FIRST_FILE_LOAD_IMM, 0x2404008C, 0x2404008E),
        (0x000B58DC, 0x2404008D, 0x24040091),
        (0x000B58EC, 0x3C01802E, 0x3C018011),
        (0x000B58F0, 0xAC257268, 0xAC251ED0),
        (0x000B58F8, 0x2404008D, 0x24040091),
    ),
}

PRISON_FAST_PHASE_PATCHES = (
    # Initial Prison family load: keep 0x8F, replace only 0x8E with FAST MONK 0x20.
    (0x0001123C, 0x2404008E, 0x24040020),
    (0x0001124C, 0x3C018011, 0x3C01800C),
    (0x00011250, 0xAC251528, 0xAC252560),
    (0x00011258, 0x2404008E, 0x24040020),
    # Later reload of the same family: again keep 0x8F and replace 0x8E with 0x20.
    (0x000C4E20, 0x2404008E, 0x24040020),
    (0x000C4E30, 0x3C018011, 0x3C01800C),
    (0x000C4E34, 0xAC251528, 0xAC252560),
    (0x000C4E3C, 0x2404008E, 0x24040020),
)


def build_materializable_enemy_plan(seed: str) -> EnemyPlan:
    return build_enemy_plan(seed, allowed_profile_keys=MATERIALIZABLE_PROFILE_KEYS)


def _guard_stock_enemy_types(rom: RomImage, plan: EnemyPlan) -> None:
    for assignment in plan.assignments:
        rom.expect_u32(assignment.type_word_rom, assignment.stock_type)


def _apply_water_profile(rom: RomImage, profile_key: str) -> tuple[str, ...]:
    if profile_key == "water-native":
        return ()

    compact_files: tuple[int, ...] = ()
    if profile_key == "water-pris15":
        compact_files = (0x8E, 0x8F)
    elif profile_key in ("water-pris16", "water-pris14-16"):
        compact_files = (0x8E, 0x90)

    if profile_key == "water-hulk":
        for offset, expected in WATER_STOCK_FIRST:
            rom.expect_u32(offset, expected)
        for offset, expected in WATER_SECOND_TRANSACTION:
            rom.expect_u32(offset, expected)

        rom.write_u32(WATER_FIRST_FILE_SIZE_IMM, 0x24040025)
        rom.write_u32(WATER_FIRST_SLOT_HI, 0x3C01801B)
        rom.write_u32(WATER_FIRST_SLOT_STORE, 0xAC25E578)
        rom.write_u32(WATER_FIRST_FILE_LOAD_IMM, 0x24040025)
        for offset, _expected in WATER_SECOND_TRANSACTION:
            rom.write_u32(offset, 0)
        return ()

    try:
        patches = WATER_PROFILE_PATCHES[profile_key]
    except KeyError as exc:
        raise PatchError(f"materializer v1 has no Water builder for {profile_key}") from exc

    for offset, expected, _replacement in patches:
        rom.expect_u32(offset, expected)

    notes: list[str] = []
    for file_id in compact_files:
        notes.extend(compact_pris_file(rom, file_id))

    for offset, _expected, replacement in patches:
        rom.write_u32(offset, replacement)
    return tuple(notes)


def _apply_prison_profile(rom: RomImage, profile_key: str) -> None:
    if profile_key == "prison-native":
        return
    if profile_key != "prison-fast-phase":
        raise PatchError(f"materializer v1 has no Prison builder for {profile_key}")

    for offset, expected, _replacement in PRISON_FAST_PHASE_PATCHES:
        rom.expect_u32(offset, expected)
    for offset, _expected, replacement in PRISON_FAST_PHASE_PATCHES:
        rom.write_u32(offset, replacement)


def apply_enemy_plan(rom: RomImage, plan: EnemyPlan) -> tuple[str, ...]:
    if plan.total_records != 104 or plan.randomizable_records != 99:
        raise PatchError("enemy plan does not match the canonical 104/99 record catalog")
    if any(stage.profile_key not in MATERIALIZABLE_PROFILE_KEYS for stage in plan.stages):
        raise PatchError("enemy plan contains a profile unsupported by materializer v1")

    _guard_stock_enemy_types(rom, plan)

    water = next(stage for stage in plan.stages if stage.stage_key == "water")
    prison = next(stage for stage in plan.stages if stage.stage_key == "prison")
    water_notes = _apply_water_profile(rom, water.profile_key)
    _apply_prison_profile(rom, prison.profile_key)

    changed_types = 0
    for assignment in plan.assignments:
        if assignment.special:
            continue
        if assignment.generated_type != assignment.stock_type:
            rom.write_u32(assignment.type_word_rom, assignment.generated_type)
            changed_types += 1

    return (
        f"materialized deterministic enemy plan for seed {plan.seed}",
        f"{changed_types} of 99 randomizable type words changed; 5 gated singleton records fixed",
        f"Water resource profile: {water.profile_key}",
        f"Prison resource profile: {prison.profile_key}",
        *water_notes,
        *format_enemy_plan(plan),
    )


class EnemyRandomizationPatch:
    """Production-facing guarded enemy planner/materializer."""

    name = "enemy-randomization"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        if not context.seed:
            raise PatchError("enemy randomization requires a seed")
        plan = build_materializable_enemy_plan(context.seed)
        return apply_enemy_plan(rom, plan)


# Compatibility alias for older proof tooling/imports.
EnemyRandomizationProofPatch = EnemyRandomizationPatch
