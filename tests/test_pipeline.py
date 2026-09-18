from mkmszr.config import RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.arena import ArenaReservationPatch
from mkmszr.patches.native_payload import NativePayloadPatch
from mkmszr.patches.pickup_persistence import PickupPersistencePatch
from mkmszr.patches.stage_selector import SafeStageSelectorPatch


def test_core_native_patches_are_always_first() -> None:
    pipeline = build_pipeline(RandomizerConfig())
    assert isinstance(pipeline.patches[0], SafeStageSelectorPatch)
    assert isinstance(pipeline.patches[1], ArenaReservationPatch)
    assert isinstance(pipeline.patches[2], NativePayloadPatch)
    assert isinstance(pipeline.patches[3], PickupPersistencePatch)
