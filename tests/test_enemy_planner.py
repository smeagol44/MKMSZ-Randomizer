from collections import Counter

from mkmszr.data.enemies import (
    STAGE_ENEMIES,
    TOTAL_ENEMY_SPAWNS,
    TOTAL_FIXED_SPECIAL_ENEMY_SPAWNS,
    TOTAL_RANDOMIZABLE_ENEMY_SPAWNS,
)
from mkmszr.enemy_planner import (
    PENDING_FOREIGN_TYPES,
    PROFILES,
    WATER_FIGHTER_PAYLOAD_CEILING,
    build_enemy_plan,
    format_enemy_plan,
    profile_fighter_payload_bytes,
    profile_is_valid,
)


def _stage(plan, key):
    return next(stage for stage in plan.stages if stage.stage_key == key)


def test_catalog_has_104_records_99_randomized_and_five_fixed_specials():
    assert TOTAL_ENEMY_SPAWNS == 104
    assert TOTAL_RANDOMIZABLE_ENEMY_SPAWNS == 99
    assert TOTAL_FIXED_SPECIAL_ENEMY_SPAWNS == 5
    records = tuple(record for stage in STAGE_ENEMIES for record in stage.records)
    assert len({record.type_word_rom for record in records}) == 104
    fixed = Counter(r.stock_type for r in records if r.special)
    assert fixed == Counter({0x12:1,0x11:1,0x0D:1,0x13:1,0x1C:1})


def test_water_type_words_match_the_proven_spawn_records():
    water = next(stage for stage in STAGE_ENEMIES if stage.key == "water")
    assert tuple(record.type_word_rom for record in water.records) == (
        0xB3BB4,0xB3BD8,0xB3BFC,0xB3C20,0xB3C44,
        0xB3C68,0xB3C8C,0xB3CB0,0xB3CD4,
    )


def test_same_seed_is_identical_and_covers_all_records():
    first = build_enemy_plan("DETERMINISTIC")
    second = build_enemy_plan("DETERMINISTIC")
    assert first == second
    assert format_enemy_plan(first) == format_enemy_plan(second)
    assert first.total_records == 104
    assert first.randomizable_records == 99


def test_special_records_never_change():
    for index in range(64):
        for assignment in build_enemy_plan(f"SPECIAL-{index}").assignments:
            if assignment.special:
                assert assignment.generated_type == assignment.stock_type


def test_seed_sweep_reaches_all_current_water_and_fire_profiles():
    water_profiles = set()
    fire_profiles = set()
    for index in range(256):
        plan = build_enemy_plan(f"PROFILE-{index}")
        water_profiles.add(_stage(plan,"water").profile_key)
        fire_profiles.add(_stage(plan,"fire").profile_key)
    assert water_profiles == {p.key for p in PROFILES if p.stage_key == "water"}
    assert fire_profiles == {p.key for p in PROFILES if p.stage_key == "fire"}


def test_all_profiles_are_structurally_valid():
    stages = {stage.key:stage for stage in STAGE_ENEMIES}
    assert all(profile_is_valid(stages[p.stage_key],p) for p in PROFILES)


def test_all_water_profiles_fit_the_bounded_payload_ceiling():
    for profile in PROFILES:
        if profile.stage_key == "water":
            payload = profile_fighter_payload_bytes(profile)
            assert payload is not None
            assert payload <= WATER_FIGHTER_PAYLOAD_CEILING


def test_mixed_pris_profile_counts_shared_base_once():
    profile = next(p for p in PROFILES if p.key == "water-pris14-16")
    assert profile.resource_keys == ("8E-grunt3-v01","90-grunt3-v01")
    assert profile_fighter_payload_bytes(profile) == 0x30C08


def test_pending_foreign_families_never_leak_into_generated_profiles():
    pending = set(PENDING_FOREIGN_TYPES)
    for index in range(128):
        plan = build_enemy_plan(f"FAIL-CLOSED-{index}")
        for stage_spec,stage_plan in zip(STAGE_ENEMIES,plan.stages,strict=True):
            native = {r.stock_type for r in stage_spec.randomizable_records}
            for type_id in stage_plan.randomized_types:
                if type_id in pending:
                    assert type_id in native


def test_only_runtime_proven_non_native_pairs_are_generated():
    allowed = {
        ("water",0x09),("water",0x0A),("water",0x14),
        ("water",0x15),("water",0x16),("water",0x17),
        ("prison",0x0A),("fire",0x01),
    }
    for index in range(128):
        plan = build_enemy_plan(f"FOREIGN-{index}")
        for stage_spec,stage_plan in zip(STAGE_ENEMIES,plan.stages,strict=True):
            native = {r.stock_type for r in stage_spec.randomizable_records}
            for type_id in stage_plan.randomized_types:
                if type_id not in native:
                    assert (stage_plan.stage_key,type_id) in allowed


def test_profiles_preserve_evidence_backed_type_multiplicities():
    for index in range(64):
        for stage_plan in build_enemy_plan(f"COUNTS-{index}").stages:
            profile = next(p for p in PROFILES if p.key == stage_plan.profile_key)
            assert Counter(stage_plan.randomized_types) == Counter(dict(profile.type_counts))


def test_native_prison_does_not_treat_paged_resource_union_as_simultaneous():
    profile = next(p for p in PROFILES if p.key == "prison-native")
    assert profile_fighter_payload_bytes(profile) is None
    assert profile.assignment_groups == (
        ((0x15,6),),
        ((0x0E,2),),
        ((0x15,2),),
        ((0x14,3),(0x16,6)),
    )
    assert profile.phase_resource_groups == (
        ("8F-stock","8E-stock"),
        ("22-stock",),
        ("8F-stock","8E-stock"),
        ("90-stock","8E-stock"),
    )


def test_prison_fast_phase_keeps_capture_resource_as_fixed_auxiliary():
    profile = next(p for p in PROFILES if p.key == "prison-fast-phase")
    assert profile.evidence == "runtime-confirmed"
    assert profile.proof_sha256 == "90188adb7a66460f0662de18cbdf65d4b17d5ba839c405395613bd30012c5ebb"
    assert profile.assignment_groups == (
        ((0x0A,6),),
        ((0x0E,2),),
        ((0x0A,2),),
        ((0x14,3),(0x16,6)),
    )
    assert profile.phase_resource_groups == (
        ("20-stock",),
        ("22-stock",),
        ("20-stock",),
        ("90-stock","8E-stock"),
    )
    assert profile.phase_fixed_resource_groups == (
        ("8F-stock",),
        (),
        ("8F-stock",),
        (),
    )


def test_prison_never_crosses_resource_lifetime_groups():
    for index in range(128):
        plan = build_enemy_plan(f"PRISON-PAGING-{index}")
        prison = next(stage for stage in plan.stages if stage.stage_key == "prison")
        types = prison.randomized_types

        if prison.profile_key == "prison-native":
            assert types[:6] == (0x15,) * 6
            assert types[8:10] == (0x15,) * 2
        else:
            assert prison.profile_key == "prison-fast-phase"
            assert types[:6] == (0x0A,) * 6
            assert types[8:10] == (0x0A,) * 2

        assert types[6:8] == (0x0E,) * 2
        assert Counter(types[10:]) == Counter({0x14:3,0x16:6})
