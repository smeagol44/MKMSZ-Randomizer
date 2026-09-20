import pytest

from mkmszr.data.addresses import (
    COMBO_EXPERIENCE_RENDER_SITES,
    MKMSZR_FILE_ENTRY_ROM,
    PROVEN_PAYLOAD_ROM,
    XP_AWARD_STORE_SITES,
    XP_CAP_TABLE_ROM,
    XP_CAP_VALUE,
    XP_MAIN_STAGE_CAPS,
)
from mkmszr.data.pickups import IDENTITY_OFFSET, STAGE_PICKUPS
from mkmszr.errors import PatchError
from mkmszr.patches.base import PatchContext
from mkmszr.patches.inventory_boxes import PERSISTENCE_RESUME_PATCH, PERSISTENCE_RESUME_ROM
from mkmszr.patches.pickup_randomization import build_stage_assignment
from mkmszr.patches.runtime_v2 import CODE_SIZE
from mkmszr.patches.xp_progression import (
    CALLBACK_OFFSET_WITHIN_IDENTITY,
    HERBS_CALLBACK_VA,
    PROGRESSION_CALLBACK_ENTRY,
    PROGRESSION_COUNT_OFFSET,
    PROGRESSION_EXTENSION,
    PROGRESSION_EXTENSION_ROM,
    PROGRESSION_RESTORE_OFFSET,
    PROGRESSION_RESUME_PATCH,
    PROGRESSION_XP_OFFSET,
    THRESHOLD_TABLE_OFFSET,
    XP_THRESHOLDS,
    XPProgressionPatch,
    build_progression_locations,
)
from mkmszr.rom import RomImage


def _post_four_box_shape(seed: str) -> RomImage:
    end = max(
        PROVEN_PAYLOAD_ROM + CODE_SIZE,
        max(record.rom_base + 0x30 for stage in STAGE_PICKUPS for record in stage.records),
        max(XP_AWARD_STORE_SITES) + 4,
        max(COMBO_EXPERIENCE_RENDER_SITES) + 4,
        XP_CAP_TABLE_ROM + 20,
        PERSISTENCE_RESUME_ROM + len(PERSISTENCE_RESUME_PATCH),
    )
    data = bytearray(end)
    data[MKMSZR_FILE_ENTRY_ROM:MKMSZR_FILE_ENTRY_ROM + 12] = (
        PROVEN_PAYLOAD_ROM.to_bytes(4, "big")
        + (PROVEN_PAYLOAD_ROM + CODE_SIZE).to_bytes(4, "big")
        + bytes(4)
    )
    data[PROGRESSION_EXTENSION_ROM:PROGRESSION_EXTENSION_ROM + 0x100] = bytes(0x100)
    data[PERSISTENCE_RESUME_ROM:PERSISTENCE_RESUME_ROM + len(PERSISTENCE_RESUME_PATCH)] = PERSISTENCE_RESUME_PATCH

    for stage in STAGE_PICKUPS:
        assignment, _attempts = build_stage_assignment(stage, seed)
        for destination, source_index in enumerate(assignment):
            target = stage.records[destination]
            data[target.rom_base + IDENTITY_OFFSET:target.rom_base + IDENTITY_OFFSET + len(target.identity)] = stage.records[source_index].identity

    for offset, expected in XP_AWARD_STORE_SITES.items():
        data[offset:offset + 4] = expected.to_bytes(4, "big")
    for offset, expected in COMBO_EXPERIENCE_RENDER_SITES.items():
        data[offset:offset + 4] = expected.to_bytes(4, "big")
    for stage_id, expected in XP_MAIN_STAGE_CAPS.items():
        offset = XP_CAP_TABLE_ROM + stage_id * 2
        data[offset:offset + 2] = expected.to_bytes(2, "big")
    return RomImage(data=data, _original=bytes(data))


def test_thresholds_and_state_are_separate_from_ordinary_bits() -> None:
    assert XP_THRESHOLDS == (85, 258, 834, 1410, 2323, 3315, 4503, 5911, 7354)
    assert PROGRESSION_COUNT_OFFSET == 0x40
    assert PROGRESSION_XP_OFFSET == 0x44
    assert PROGRESSION_COUNT_OFFSET > 0x3C


@pytest.mark.parametrize("seed", ["BCBDBF", "TEST153", "TEST-0042", "different"])
def test_selection_is_deterministic_and_targets_only_generated_herbs(seed: str) -> None:
    first = build_progression_locations(seed)
    assert first == build_progression_locations(seed)
    assert len(first) == len(set(first)) == 9
    stage_by_id = {stage.stage_id: stage for stage in STAGE_PICKUPS}
    for stage_id, destination in first:
        stage = stage_by_id[stage_id]
        assignment, _attempts = build_stage_assignment(stage, seed)
        identity = stage.records[assignment[destination]].identity
        callback = int.from_bytes(identity[CALLBACK_OFFSET_WITHIN_IDENTITY:CALLBACK_OFFSET_WITHIN_IDENTITY + 4], "big")
        assert callback == HERBS_CALLBACK_VA


def test_progression_namespace_does_not_perturb_base_assignments() -> None:
    seed = "BCBDBF"
    before = [build_stage_assignment(stage, seed)[0] for stage in STAGE_PICKUPS]
    build_progression_locations(seed)
    assert [build_stage_assignment(stage, seed)[0] for stage in STAGE_PICKUPS] == before


def test_extension_fits_reserved_v2_tail() -> None:
    assert len(PROGRESSION_EXTENSION) == 0x100
    assert 0 < THRESHOLD_TABLE_OFFSET < PROGRESSION_RESTORE_OFFSET < 0x100


def test_patch_disables_xp_caps_and_converts_exactly_nine_callbacks() -> None:
    seed = "BCBDBF"
    rom = _post_four_box_shape(seed)
    XPProgressionPatch().apply(rom, PatchContext(seed=seed))

    assert rom.data[PROGRESSION_EXTENSION_ROM:PROGRESSION_EXTENSION_ROM + 0x100] == PROGRESSION_EXTENSION
    assert rom.data[PERSISTENCE_RESUME_ROM:PERSISTENCE_RESUME_ROM + len(PROGRESSION_RESUME_PATCH)] == PROGRESSION_RESUME_PATCH
    assert all(rom.read_u32(offset) == 0 for offset in XP_AWARD_STORE_SITES)
    assert all(rom.read_u32(offset) == 0 for offset in COMBO_EXPERIENCE_RENDER_SITES)
    assert all(rom.read_u16(XP_CAP_TABLE_ROM + stage_id * 2) == XP_CAP_VALUE for stage_id in XP_MAIN_STAGE_CAPS)

    selected = set(build_progression_locations(seed))
    changed = 0
    for stage in STAGE_PICKUPS:
        assignment, _attempts = build_stage_assignment(stage, seed)
        for destination, target in enumerate(stage.records):
            base = target.rom_base + IDENTITY_OFFSET
            original = stage.records[assignment[destination]].identity
            actual = bytes(rom.data[base:base + len(original)])
            if (stage.stage_id, destination) in selected:
                assert actual[:CALLBACK_OFFSET_WITHIN_IDENTITY] == original[:CALLBACK_OFFSET_WITHIN_IDENTITY]
                assert int.from_bytes(actual[CALLBACK_OFFSET_WITHIN_IDENTITY:CALLBACK_OFFSET_WITHIN_IDENTITY + 4], "big") == PROGRESSION_CALLBACK_ENTRY
                assert actual[CALLBACK_OFFSET_WITHIN_IDENTITY + 4:] == original[CALLBACK_OFFSET_WITHIN_IDENTITY + 4:]
                changed += 1
            else:
                assert actual == original
    assert changed == 9


def test_patch_guards_mapped_xp_sites() -> None:
    rom = _post_four_box_shape("BCBDBF")
    first = next(iter(XP_AWARD_STORE_SITES))
    rom.data[first] ^= 1
    with pytest.raises(PatchError, match="guard failed"):
        XPProgressionPatch().apply(rom, PatchContext(seed="BCBDBF"))
