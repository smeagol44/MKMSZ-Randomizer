from mkmszr.config import RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.stage_selector import SafeStageSelectorPatch


def test_safe_stage_selector_is_always_first_patch() -> None:
    pipeline = build_pipeline(RandomizerConfig())
    assert isinstance(pipeline.patches[0], SafeStageSelectorPatch)


def test_safe_stage_selector_remains_when_runtime_reservation_is_disabled() -> None:
    pipeline = build_pipeline(RandomizerConfig(reserve_runtime_memory=False))
    assert isinstance(pipeline.patches[0], SafeStageSelectorPatch)
