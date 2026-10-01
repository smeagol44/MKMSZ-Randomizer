from collections import Counter

import pytest

from mkmszr.patches import enemy_randomization
from mkmszr.data.enemies import STAGE_ENEMIES
from mkmszr.enemy_planner import build_enemy_plan
from mkmszr.errors import PatchError
from mkmszr.patches.enemy_randomization import (
    MATERIALIZABLE_PROFILE_KEYS,
    WATER_SECOND_TRANSACTION,
    apply_enemy_plan,
    build_materializable_enemy_plan,
)
from mkmszr.rom import EXPECTED_SIZE, RomImage


def _stock_rom() -> RomImage:
    data = bytearray(EXPECTED_SIZE)
    original = bytearray(EXPECTED_SIZE)

    for stage in STAGE_ENEMIES:
        for record in stage.records:
            value = record.stock_type.to_bytes(4, "big")
            data[record.type_word_rom : record.type_word_rom + 4] = value
            original[record.type_word_rom : record.type_word_rom + 4] = value

    stock_words = {
        0xB58B8: 0x2404008C,
        0xB58C8: 0x3C018011,
        0xB58CC: 0xAC2514C0,
        0xB58D4: 0x2404008C,
        **dict(WATER_SECOND_TRANSACTION),
        0x1123C: 0x2404008E,
        0x1124C: 0x3C018011,
        0x11250: 0xAC251528,
        0x11258: 0x2404008E,
        0xC4E20: 0x2404008E,
        0xC4E30: 0x3C018011,
        0xC4E34: 0xAC251528,
        0xC4E3C: 0x2404008E,
        0xC4EDC: 0x3C048011,
        0xC4EE0: 0x8C842008,
    }
    for offset, value in stock_words.items():
        encoded = value.to_bytes(4, "big")
        data[offset : offset + 4] = encoded
        original[offset : offset + 4] = encoded

    return RomImage(data, bytes(original))


def _stage(plan, key):
    return next(stage for stage in plan.stages if stage.stage_key == key)


NATIVE_PROFILE_KEYS = frozenset(
    {
        "temple-native",
        "wind-native",
        "water-native",
        "earth-native",
        "prison-native",
        "fire-native",
        "bridge-native",
        "fortress-native",
    }
)


def _plan_with_water_profile(profile_key: str):
    allowed = frozenset(set(NATIVE_PROFILE_KEYS) | {profile_key})
    for index in range(2048):
        plan = build_enemy_plan(
            f"WATER-PROFILE-{profile_key}-{index}",
            allowed_profile_keys=allowed,
        )
        if _stage(plan, "water").profile_key == profile_key:
            return plan
    raise AssertionError(f"no deterministic seed found for {profile_key}")


def test_materializer_retries_to_supported_profiles_deterministically():
    first = build_materializable_enemy_plan("ENEMYPLAN05")
    second = build_materializable_enemy_plan("ENEMYPLAN05")

    assert first == second
    assert all(
        stage.profile_key in MATERIALIZABLE_PROFILE_KEYS for stage in first.stages
    )


def test_pris17_seed_materializes_resource_loader_and_keeps_specials_fixed():
    rom = _stock_rom()
    plan = _plan_with_water_profile("water-pris17")
    apply_enemy_plan(rom, plan)

    assert rom.read_u32(0xB58B8) == 0x2404008E
    assert rom.read_u32(0xB58CC) == 0xAC251528
    assert rom.read_u32(0xB58D4) == 0x2404008E
    assert rom.read_u32(0xB58DC) == 0x24040091
    assert rom.read_u32(0xB58EC) == 0x3C018011
    assert rom.read_u32(0xB58F0) == 0xAC251ED0
    assert rom.read_u32(0xB58F8) == 0x24040091

    for assignment in plan.assignments:
        actual = rom.read_u32(assignment.type_word_rom)
        expected = (
            assignment.stock_type if assignment.special else assignment.generated_type
        )
        assert actual == expected


def test_hulk_profile_nops_only_second_water_transaction():
    rom = _stock_rom()
    plan = _plan_with_water_profile("water-hulk")

    assert _stage(plan, "water").profile_key == "water-hulk"
    apply_enemy_plan(rom, plan)

    assert rom.read_u32(0xB58B8) == 0x24040025
    assert rom.read_u32(0xB58C8) == 0x3C01801B
    assert rom.read_u32(0xB58CC) == 0xAC25E578
    assert rom.read_u32(0xB58D4) == 0x24040025
    assert all(
        rom.read_u32(offset) == 0
        for offset, _expected in WATER_SECOND_TRANSACTION
    )


def test_fast_profile_preserves_second_water_transaction():
    rom = _stock_rom()
    plan = _plan_with_water_profile("water-fast")

    assert _stage(plan, "water").profile_key == "water-fast"
    apply_enemy_plan(rom, plan)

    assert rom.read_u32(0xB58B8) == 0x24040020
    assert rom.read_u32(0xB58C8) == 0x3C01800C
    assert rom.read_u32(0xB58CC) == 0xAC252560
    assert rom.read_u32(0xB58D4) == 0x24040020
    for offset, expected in WATER_SECOND_TRANSACTION:
        assert rom.read_u32(offset) == expected


def test_guard_failure_occurs_before_any_enemy_type_write():
    rom = _stock_rom()
    plan = build_materializable_enemy_plan("ENEMYPLAN05")
    corrupt = plan.assignments[20]
    rom.write_u32(corrupt.type_word_rom, 0xDEADBEEF)

    with pytest.raises(PatchError):
        apply_enemy_plan(rom, plan)

    first = plan.assignments[0]
    assert rom.read_u32(first.type_word_rom) == first.stock_type


def test_unfiltered_plan_with_unsupported_profile_fails_closed():
    plan = build_enemy_plan("UNSUP1")
    assert _stage(plan, "fire").profile_key == "fire-monk2-proof"

    rom = _stock_rom()
    with pytest.raises(PatchError, match="unsupported"):
        apply_enemy_plan(rom, plan)


def test_generated_seed_keeps_prison_within_registered_paging_groups():
    plan = build_materializable_enemy_plan("ENEMYPLAN05")
    prison = _stage(plan, "prison")
    types = prison.randomized_types

    assert prison.profile_key in {"prison-native", "prison-fast-phase"}
    if prison.profile_key == "prison-native":
        assert types[:6] == (0x15,) * 6
        assert types[8:10] == (0x15,) * 2
    else:
        assert types[:6] == (0x0A,) * 6
        assert types[8:10] == (0x0A,) * 2

    assert types[6:8] == (0x0E,) * 2
    assert Counter(types[10:]) == Counter({0x14: 3, 0x16: 6})


def test_prison_fast_phase_materializes_combat_family_and_keeps_capture_anchor():
    rom = _stock_rom()
    allowed = frozenset(set(NATIVE_PROFILE_KEYS) | {"prison-fast-phase"})
    plan = build_enemy_plan("PRISON-FAST-PHASE", allowed_profile_keys=allowed)
    prison = _stage(plan, "prison")
    if prison.profile_key != "prison-fast-phase":
        # deterministically find one seed that lands on the profile
        for index in range(256):
            plan = build_enemy_plan(
                f"PRISON-FAST-PHASE-{index}",
                allowed_profile_keys=allowed,
            )
            prison = _stage(plan, "prison")
            if prison.profile_key == "prison-fast-phase":
                break
        else:
            raise AssertionError("no prison-fast-phase profile reached in seed sweep")

    apply_enemy_plan(rom, plan)

    assert rom.read_u32(0x1123C) == 0x24040020
    assert rom.read_u32(0x1124C) == 0x3C01800C
    assert rom.read_u32(0x11250) == 0xAC252560
    assert rom.read_u32(0x11258) == 0x24040020
    assert rom.read_u32(0xC4E20) == 0x24040020
    assert rom.read_u32(0xC4E30) == 0x3C01800C
    assert rom.read_u32(0xC4E34) == 0xAC252560
    assert rom.read_u32(0xC4E3C) == 0x24040020

    # Capture set-piece anchor remains stock file-0x8F slot.
    assert rom.read_u32(0xC4EDC) == 0x3C048011
    assert rom.read_u32(0xC4EE0) == 0x8C842008


@pytest.mark.parametrize(
    ("profile_key", "second_file", "slot_hi", "slot_store"),
    (
        ("water-pris15", 0x8F, 0x3C018011, 0xAC252008),
        ("water-pris16", 0x90, 0x3C01802C, 0xAC250FA0),
        ("water-pris14-16", 0x90, 0x3C01802C, 0xAC250FA0),
    ),
)
def test_compact_pris_profiles_use_production_compactor_and_loader(
    monkeypatch, profile_key, second_file, slot_hi, slot_store
):
    rom = _stock_rom()
    plan = _plan_with_water_profile(profile_key)
    compacted = []

    def fake_compactor(_rom, file_id):
        compacted.append(file_id)
        return (f"compact {file_id:02X}",)

    monkeypatch.setattr(enemy_randomization, "compact_pris_file", fake_compactor)
    notes = apply_enemy_plan(rom, plan)

    assert compacted == ([0x8E, 0x8F] if profile_key == "water-pris15" else [0x8E, 0x90])
    assert rom.read_u32(0xB58B8) == 0x2404008E
    assert rom.read_u32(0xB58CC) == 0xAC251528
    assert rom.read_u32(0xB58D4) == 0x2404008E
    assert rom.read_u32(0xB58DC) == 0x24040000 | second_file
    assert rom.read_u32(0xB58EC) == slot_hi
    assert rom.read_u32(0xB58F0) == slot_store
    assert rom.read_u32(0xB58F8) == 0x24040000 | second_file
    assert any("compact 8E" in note for note in notes)


def test_runtime_confirmed_compact_pris_profiles_are_materializable():
    assert {
        "water-pris15",
        "water-pris16",
        "water-pris14-16",
    } <= MATERIALIZABLE_PROFILE_KEYS
