from mkmszr.config import RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.arena import ArenaReservationPatch
from mkmszr.patches.native_payload import NativePayloadPatch
from mkmszr.patches.inventory_boxes import FourBoxInventoryPatch
from mkmszr.patches.pickup_persistence import PickupPersistencePatch
from mkmszr.patches.pickup_randomization import PickupRandomizationPatch
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
