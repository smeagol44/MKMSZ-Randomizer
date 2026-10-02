from mkmszr.config import RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.controls_production import ControlsProductionPatch
from mkmszr.patches.global_materialization import (
    ACQUISITION_REMASK,
    DESTINATION_ACTIONS,
    GENERIC_AWARD,
    MATERIALIZER_HELPER,
    MATERIALIZER_HELPER_END_K0,
    MATERIALIZER_HELPER_K0,
    MATERIALIZER_RUNTIME_LIMIT,
    PRISON_RECONSTRUCT,
    PRISON_RECONSTRUCT_K0,
    GlobalItemMaterializationPatch,
)
from mkmszr.patches.pickup_randomization import PickupRandomizationPatch
from mkmszr.resource_materialization import (
    DEST_EARTH_SQUARE,
    DEST_FIRE_TRIANGLE_DOWN,
    DEST_PRISON_L1,
    DEST_PRISON_STRENGTH,
    DEST_WATER_THREE_BARS,
    DEST_WIND_CIRCLE,
    GlobalMaterializationPlan,
    MaterializationAssignment,
    StageResourcePlacement,
    portable_materialized_identity,
)


def _plan(*assignments: MaterializationAssignment) -> GlobalMaterializationPlan:
    stages = sorted({assignment.stage_id for assignment in assignments})
    return GlobalMaterializationPlan(
        assignments=tuple(assignments),
        placements=tuple(
            StageResourcePlacement(stage_id=stage_id, rom_start=0x00F00000 + i * 0x10000, capacity=0x10000)
            for i, stage_id in enumerate(stages)
        ),
    )


def test_materializer_helper_fits_controls_to_toasty_gap() -> None:
    assert MATERIALIZER_HELPER_K0 == 0x801B2960
    assert MATERIALIZER_HELPER_END_K0 <= MATERIALIZER_RUNTIME_LIMIT == 0x801B3420
    assert len(GENERIC_AWARD) > 0
    assert len(ACQUISITION_REMASK) > 0
    assert len(PRISON_RECONSTRUCT) > 0
    assert MATERIALIZER_HELPER_K0 <= PRISON_RECONSTRUCT_K0 < MATERIALIZER_HELPER_END_K0
    assert len(MATERIALIZER_HELPER) == MATERIALIZER_HELPER_END_K0 - MATERIALIZER_HELPER_K0


def test_portable_inventory_token_uses_generic_award_callback() -> None:
    identity = portable_materialized_identity(
        "wind-circle",
        0x123C,
        generic_inventory_callback=0xA01B0970,
    )
    assert int.from_bytes(identity[0x04:0x08], "big") == 0x0E
    assert int.from_bytes(identity[0x08:0x0C], "big") == 0xA01B0970
    assert int.from_bytes(identity[0x14:0x18], "big") == 0x123C


def test_destination_activation_gate_composes_with_fixed_reward() -> None:
    identity = portable_materialized_identity(
        "potion",
        0x0D88,
        generic_inventory_callback=0xA01B0900,
        activation_gate=True,
    )
    assert int.from_bytes(identity[0x04:0x08], "big") == 0x8000
    assert int.from_bytes(identity[0x08:0x0C], "big") == 0x800388FC


def test_strength_uses_generic_inventory_award_without_prison_checkpoint() -> None:
    identity = portable_materialized_identity(
        "strength-urn",
        0x0D89,
        generic_inventory_callback=0xA01B0900,
    )
    assert int.from_bytes(identity[0x04:0x08], "big") == 0x0B
    assert int.from_bytes(identity[0x08:0x0C], "big") == 0xA01B0900


def test_activation_gate_composes_with_generic_inventory_award() -> None:
    identity = portable_materialized_identity(
        "bridge-omega",
        0x0D8A,
        generic_inventory_callback=0xA01B0900,
        activation_gate=True,
    )
    assert int.from_bytes(identity[0x04:0x08], "big") == 0x801D
    assert int.from_bytes(identity[0x08:0x0C], "big") == 0xA01B0900


def test_fortress_crystal_logical_award_separates_source_and_destination_gate() -> None:
    ordinary_identity = portable_materialized_identity(
        "crystal-kia",
        0x0D8B,
        generic_inventory_callback=0xA01B0900,
    )
    boss_identity = portable_materialized_identity(
        "crystal-kia",
        0x0D8B,
        generic_inventory_callback=0xA01B0900,
        activation_gate=True,
    )
    assert int.from_bytes(ordinary_identity[0x04:0x08], "big") == 0x21
    assert int.from_bytes(ordinary_identity[0x08:0x0C], "big") == 0xA01B0900
    assert int.from_bytes(boss_identity[0x04:0x08], "big") == 0x8021
    assert int.from_bytes(boss_identity[0x08:0x0C], "big") == 0xA01B0900


def test_prison_key_uses_shared_inventory_award_after_credential_closure() -> None:
    identity = portable_materialized_identity(
        "prison-l1",
        0x123C,
        generic_inventory_callback=0xA01B0900,
    )
    assert int.from_bytes(identity[0x04:0x08], "big") == 0x1A
    assert int.from_bytes(identity[0x08:0x0C], "big") == 0xA01B0900


def test_destination_action_encoding_composes_with_logical_award() -> None:
    cases = (
        ("herbs", DEST_WIND_CIRCLE, 0x0104),
        ("potion", DEST_WATER_THREE_BARS, 0x0501),
        ("earth-square", DEST_EARTH_SQUARE, 0x0711),
        ("fire-two-bars", DEST_FIRE_TRIANGLE_DOWN, 0x0C18),
        ("prison-l2", DEST_PRISON_L1, 0x0D1B),
        ("strength-urn", DEST_PRISON_STRENGTH, 0x0F0B),
    )
    for key, action, expected_parameter in cases:
        identity = portable_materialized_identity(
            key,
            0x123C,
            generic_inventory_callback=0xA01B0900,
            destination_action=action,
        )
        assert int.from_bytes(identity[0x04:0x08], "big") == expected_parameter
        assert int.from_bytes(identity[0x08:0x0C], "big") == 0xA01B0900


def test_all_progression_destination_actions_are_registered() -> None:
    assert DESTINATION_ACTIONS[(1, 3)] == DEST_WIND_CIRCLE
    assert DESTINATION_ACTIONS[(2, 7)] == DEST_WATER_THREE_BARS
    assert DESTINATION_ACTIONS[(3, 0)] == DEST_EARTH_SQUARE
    assert DESTINATION_ACTIONS[(5, 14)] == DEST_FIRE_TRIANGLE_DOWN
    assert DESTINATION_ACTIONS[(4, 0)] == DEST_PRISON_L1
    assert DESTINATION_ACTIONS[(4, 3)] == DEST_PRISON_STRENGTH


def test_explicit_materialization_replaces_stage_local_patch_in_pipeline() -> None:
    plan = _plan(MaterializationAssignment(5, 0, "wind-circle"))
    pipeline = build_pipeline(
        RandomizerConfig(seed="GLOBAL-PROOF", powers_as_pickups=False),
        materialization_plan=plan,
    )
    types = [type(patch) for patch in pipeline.patches]
    assert PickupRandomizationPatch not in types
    assert GlobalItemMaterializationPatch in types
    assert types.index(ControlsProductionPatch) < types.index(GlobalItemMaterializationPatch)


def test_materialization_rejects_current_pickup_xp_overlay() -> None:
    plan = _plan(MaterializationAssignment(5, 0, "wind-circle"))
    try:
        build_pipeline(RandomizerConfig(seed="GLOBAL-PROOF"), materialization_plan=plan)
    except ValueError as exc:
        assert "pickup-XP overlay" in str(exc)
    else:
        raise AssertionError("global materialization must not silently compose with stage-local XP placement")
