from mkmszr.config import OutfitConfig, RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.arena import ArenaReservationPatch
from mkmszr.patches.game_settings_turn import GameSettingsTurnPatch
from mkmszr.patches.inventory_boxes import FourBoxInventoryPatch
from mkmszr.patches.native_payload import NativePayloadPatch
from mkmszr.patches.pickup_persistence import PickupPersistencePatch
from mkmszr.patches.pickup_randomization import PickupRandomizationPatch
from mkmszr.patches.rainbow_palette import RainbowPalettePatch
from mkmszr.patches.stage_selector import SafeStageSelectorPatch
from mkmszr.patches.xp_progression import XPProgressionPatch


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
