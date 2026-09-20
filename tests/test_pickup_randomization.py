from collections import Counter

import pytest

from mkmszr.data.pickups import (
    COLLECTED_OFFSET,
    IDENTITY_OFFSET,
    IDENTITY_SIZE,
    STAGE_PICKUPS,
    TOTAL_ORDINARY_PICKUPS,
)
from mkmszr.errors import PatchError
from mkmszr.patches.base import PatchContext
from mkmszr.patches.pickup_randomization import (
    PickupRandomizationPatch,
    build_stage_assignment,
    layout_is_progression_safe,
)
from mkmszr.rom import RomImage


def _catalog_shape() -> RomImage:
    end = max(
        record.rom_base + 0x30
        for stage in STAGE_PICKUPS
        for record in stage.records
    )
    data = bytearray(end)

    for stage_index, stage in enumerate(STAGE_PICKUPS):
        for record_index, record in enumerate(stage.records):
            # Non-item location fields are deliberately nonzero so the test
            # catches accidental writes outside +0x10..+0x2B.
            marker = bytes(
                (
                    stage_index,
                    record_index,
                    0xA5,
                    0x5A,
                )
            ) * 4
            data[record.rom_base : record.rom_base + IDENTITY_OFFSET] = marker
            data[
                record.rom_base + IDENTITY_OFFSET :
                record.rom_base + IDENTITY_OFFSET + IDENTITY_SIZE
            ] = record.identity
            data[
                record.rom_base + COLLECTED_OFFSET :
                record.rom_base + COLLECTED_OFFSET + 4
            ] = bytes(4)

    return RomImage(data=data, _original=bytes(data))


def test_catalog_covers_exactly_84_ordinary_locations() -> None:
    assert TOTAL_ORDINARY_PICKUPS == 84
    assert [len(stage.records) for stage in STAGE_PICKUPS] == [4, 6, 9, 20, 10, 16, 10, 9]


def test_same_seed_produces_same_stage_assignments() -> None:
    first = [
        build_stage_assignment(stage, "BCBDBF")[0]
        for stage in STAGE_PICKUPS
    ]
    second = [
        build_stage_assignment(stage, "BCBDBF")[0]
        for stage in STAGE_PICKUPS
    ]

    assert first == second
    assert first != [
        build_stage_assignment(stage, "DIFFERENT-SEED")[0]
        for stage in STAGE_PICKUPS
    ]


@pytest.mark.parametrize("seed_number", range(250))
def test_generated_layouts_are_progression_safe(seed_number: int) -> None:
    seed = f"TEST-{seed_number:04d}"
    for stage in STAGE_PICKUPS:
        assignment, attempts = build_stage_assignment(stage, seed)
        assert attempts >= 1
        assert layout_is_progression_safe(stage, assignment)


def test_pickup_patch_preserves_location_fields_and_stage_pools() -> None:
    rom = _catalog_shape()
    before = bytes(rom.data)

    notes = PickupRandomizationPatch().apply(rom, PatchContext(seed="BCBDBF"))

    assert notes[0].startswith("84 ordinary pickup locations processed")

    for stage in STAGE_PICKUPS:
        before_pool = Counter(record.identity for record in stage.records)
        after_pool = Counter(
            bytes(
                rom.data[
                    record.rom_base + IDENTITY_OFFSET :
                    record.rom_base + IDENTITY_OFFSET + IDENTITY_SIZE
                ]
            )
            for record in stage.records
        )
        assert after_pool == before_pool

        for record in stage.records:
            base = record.rom_base
            assert rom.data[base : base + IDENTITY_OFFSET] == before[
                base : base + IDENTITY_OFFSET
            ]
            assert rom.data[
                base + COLLECTED_OFFSET : base + COLLECTED_OFFSET + 4
            ] == bytes(4)


def test_pickup_patch_is_deterministic_on_rom_bytes() -> None:
    first = _catalog_shape()
    second = _catalog_shape()

    PickupRandomizationPatch().apply(first, PatchContext(seed="BCBDBF"))
    PickupRandomizationPatch().apply(second, PatchContext(seed="BCBDBF"))

    assert first.data == second.data


def test_pickup_patch_fails_closed_on_unknown_source_tuple() -> None:
    rom = _catalog_shape()
    target = STAGE_PICKUPS[1].records[0].rom_base + IDENTITY_OFFSET
    rom.data[target] ^= 0x01

    with pytest.raises(PatchError, match="guard failed"):
        PickupRandomizationPatch().apply(rom, PatchContext(seed="BCBDBF"))


def test_pickup_patch_without_seed_is_a_noop() -> None:
    rom = _catalog_shape()
    before = bytes(rom.data)

    notes = PickupRandomizationPatch().apply(rom, PatchContext())

    assert bytes(rom.data) == before
    assert notes == ("no seed supplied; ordinary pickup randomization skipped",)
