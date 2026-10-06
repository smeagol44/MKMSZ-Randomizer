from mkmszr.config import OutfitConfig, RandomizerConfig
from mkmszr.patcher import (
    _build_production_global_plan,
    _pickup_mode_required_count,
    build_pipeline,
)
from mkmszr.patches.arena import ArenaReservationPatch
from mkmszr.patches.controls_production import ControlsProductionPatch
from mkmszr.patches.enemy_randomization import EnemyRandomizationPatch
from mkmszr.patches.game_settings_turn import GameSettingsTurnPatch
from mkmszr.patches.inventory_boxes import FourBoxInventoryPatch
from mkmszr.patches.native_payload import NativePayloadPatch
from mkmszr.patches.pickup_persistence import PickupPersistencePatch
from mkmszr.patches.pickup_randomization import PickupRandomizationPatch
from mkmszr.patches.power_order import PowerOrderPatch
from mkmszr.patches.progression_presentation import ProgressionPickupPresentationPatch
from mkmszr.patches.rainbow_palette import RainbowPalettePatch
from mkmszr.patches.required_powers import RequiredPowersPatch
from mkmszr.patches.run_lifecycle import RunLifecyclePatch
from mkmszr.patches.stage_selector import SafeStageSelectorPatch
from mkmszr.patches.temple_special_check import TempleSpecialCheckPatch
from mkmszr.patches.xp_progression import EarnedXPPersistencePatch, XPProgressionPatch


def test_core_native_patches_are_always_first() -> None:
    pipeline = build_pipeline(RandomizerConfig())
    assert isinstance(pipeline.patches[0], SafeStageSelectorPatch)
    assert isinstance(pipeline.patches[1], ArenaReservationPatch)
    assert isinstance(pipeline.patches[2], NativePayloadPatch)
    assert isinstance(pipeline.patches[3], PickupPersistencePatch)


def test_progression_runs_after_generated_pickups_and_four_box_resume_patch() -> None:
    pipeline = build_pipeline(RandomizerConfig(seed="BCBDBF"))
    types = [type(patch) for patch in pipeline.patches]
    assert types.index(PickupRandomizationPatch) < types.index(FourBoxInventoryPatch)
    assert types.index(FourBoxInventoryPatch) < types.index(XPProgressionPatch)


def test_turn_settings_run_after_progression_in_shared_pipeline() -> None:
    pipeline = build_pipeline(RandomizerConfig())
    types = [type(patch) for patch in pipeline.patches]
    assert XPProgressionPatch in types
    assert GameSettingsTurnPatch in types
    assert types.index(XPProgressionPatch) < types.index(GameSettingsTurnPatch)


def test_rainbow_outfit_uses_runtime_palette_patch() -> None:
    pipeline = build_pipeline(
        RandomizerConfig(seed="RAINBOW64", outfit=OutfitConfig(mode="rainbow"))
    )
    types = [type(patch) for patch in pipeline.patches]
    assert RainbowPalettePatch in types
    assert types.index(ControlsProductionPatch) < types.index(RainbowPalettePatch)


def test_power_order_shuffle_is_optional_and_runs_after_controls() -> None:
    disabled = build_pipeline(RandomizerConfig(seed="POWER"))
    assert PowerOrderPatch not in [type(patch) for patch in disabled.patches]

    enabled = build_pipeline(
        RandomizerConfig(seed="POWER", shuffle_power_progression=True)
    )
    types = [type(patch) for patch in enabled.patches]
    assert types[-1] is PowerOrderPatch


def test_progression_presentation_follows_lifecycle_only_in_pickup_mode() -> None:
    enabled = build_pipeline(RandomizerConfig(seed="POWER-FLASH"))
    types = [type(patch) for patch in enabled.patches]
    assert ProgressionPickupPresentationPatch in types
    assert types.index(XPProgressionPatch) < types.index(ProgressionPickupPresentationPatch)
    assert types.index(RunLifecyclePatch) < types.index(ProgressionPickupPresentationPatch)

    disabled = build_pipeline(
        RandomizerConfig(seed="POWER-FLASH", powers_as_pickups=False)
    )
    disabled_types = [type(patch) for patch in disabled.patches]
    assert ProgressionPickupPresentationPatch not in disabled_types
    assert EarnedXPPersistencePatch in disabled_types
    assert disabled_types.index(RunLifecyclePatch) < disabled_types.index(
        EarnedXPPersistencePatch
    )


def test_powers_as_pickups_and_required_count_are_independent() -> None:
    for shuffle in (False, True):
        pipeline = build_pipeline(
            RandomizerConfig(
                seed="POWER", powers_as_pickups=False,
                shuffle_power_progression=shuffle,
                required_powers_mode="custom", custom_required_powers=0,
            )
        )
        types = [type(patch) for patch in pipeline.patches]
        assert XPProgressionPatch not in types
        assert EarnedXPPersistencePatch in types
        assert FourBoxInventoryPatch in types
        assert types.index(RunLifecyclePatch) < types.index(EarnedXPPersistencePatch)
        assert (PowerOrderPatch in types) is shuffle
        assert types[-1] is RequiredPowersPatch

    assert RequiredPowersPatch not in [
        type(patch) for patch in build_pipeline(RandomizerConfig(seed="POWER")).patches
    ]


def test_enemy_randomization_is_default_off_and_optional_in_shared_pipeline() -> None:
    disabled = build_pipeline(RandomizerConfig(seed="ENEMIES"))
    assert EnemyRandomizationPatch not in [type(patch) for patch in disabled.patches]

    enabled = build_pipeline(
        RandomizerConfig(seed="ENEMIES", enemy_randomization=True)
    )
    types = [type(patch) for patch in enabled.patches]
    assert EnemyRandomizationPatch in types
    assert types[-1] is EnemyRandomizationPatch


def test_lifecycle_v06_runs_after_temple_and_before_optional_power_order() -> None:
    pipeline = build_pipeline(RandomizerConfig(seed="LIFECYCLE-V06"))
    types = [type(patch) for patch in pipeline.patches]
    assert RunLifecyclePatch in types
    assert types.index(TempleSpecialCheckPatch) < types.index(RunLifecyclePatch)

    shuffled = build_pipeline(
        RandomizerConfig(seed="LIFECYCLE-V06", shuffle_power_progression=True)
    )
    types = [type(patch) for patch in shuffled.patches]
    assert types.index(RunLifecyclePatch) < types.index(PowerOrderPatch)

    earned = build_pipeline(
        RandomizerConfig(
            seed="LIFECYCLE-V06-OFF",
            powers_as_pickups=False,
            shuffle_power_progression=True,
        )
    )
    types = [type(patch) for patch in earned.patches]
    assert types.index(RunLifecyclePatch) < types.index(EarnedXPPersistencePatch)
    assert types.index(EarnedXPPersistencePatch) < types.index(PowerOrderPatch)


def test_temple_special_check_runs_after_controls_and_optional_rainbow() -> None:
    normal = build_pipeline(RandomizerConfig(seed="TEMPLE-SPECIAL"))
    types = [type(patch) for patch in normal.patches]
    assert TempleSpecialCheckPatch in types
    assert types.index(ControlsProductionPatch) < types.index(TempleSpecialCheckPatch)

    rainbow = build_pipeline(
        RandomizerConfig(seed="TEMPLE-SPECIAL", outfit=OutfitConfig(mode="rainbow"))
    )
    types = [type(patch) for patch in rainbow.patches]
    assert types.index(ControlsProductionPatch) < types.index(RainbowPalettePatch)
    assert types.index(RainbowPalettePatch) < types.index(TempleSpecialCheckPatch)



def test_vanilla_fortress_gate_requires_eight_pickup_tiers() -> None:
    assert _pickup_mode_required_count(None, 5100) == 8


def test_normal_product_global_plan_is_complete_and_deterministic() -> None:
    config = RandomizerConfig(seed="GLOBAL85-V01")
    first_plan, first_run = _build_production_global_plan(
        config,
        required_count=None,
        required_xp=5100,
    )
    second_plan, second_run = _build_production_global_plan(
        config,
        required_count=None,
        required_xp=5100,
    )

    assert first_run == second_run
    assert first_plan == second_plan
    assert first_run.candidate.attempt_index == 0
    assert len(first_plan.assignments) == 84
    assert len(first_plan.placements) == 8
    assert first_plan.temple_special_item_key == "mana"
    assert len(first_run.power_locations) == 9
