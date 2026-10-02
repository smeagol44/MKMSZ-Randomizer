from mkmszr.config import OutfitConfig, RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.controls_production import ControlsProductionPatch
from mkmszr.patches.game_settings_turn import GameSettingsTurnPatch
from mkmszr.patches.rainbow_palette import RainbowPalettePatch
from mkmszr.patches.toasty import ToastyProductionCompositionPatch
from mkmszr.patches.toasty_codegen import (
    _build_call_trampoline,
    _build_init_loader,
    pack_toasty_module,
)
from mkmszr.patches.toasty_constants import (
    DEFAULT_PROBABILITY_PER_THOUSAND,
    MODULE_K0,
    MODULE_ROM,
    SHARED_EXPANSION_ROM,
    ToastyAssets,
)


def fake_assets() -> ToastyAssets:
    geometry = ((7,32),(64,32),(7,32),(7,32),(64,32),(7,32),(7,21),(64,21),(7,21))
    slices = tuple(bytes(((w + 31) & ~31) * h // 2) for w,h in geometry)
    wave = bytearray(24)
    wave[0x0C:0x10] = (-2253).to_bytes(4, "big", signed=True)
    return ToastyAssets(
        visual_slices=slices,
        palette_tlut=bytes(0x20),
        audio_subpatch=bytes(20),
        audio_wave=bytes(wave),
        audio_predictor=bytes(264),
        audio_sample=bytes(0x816),
    )


def test_toasty_module_fits_reserved_pool_at_aligned_base() -> None:
    packed = pack_toasty_module(fake_assets(), DEFAULT_PROBABILITY_PER_THOUSAND)
    assert packed.allocation_start == MODULE_K0 == 0x801B1000
    assert len(packed.data) == 0x9B6
    assert MODULE_K0 + len(packed.data) == 0x801B19B6


def test_toasty_is_optional_and_runs_after_rainbow() -> None:
    assets = fake_assets()
    base = build_pipeline(RandomizerConfig())
    assert not any(isinstance(p, ToastyProductionCompositionPatch) for p in base.patches)

    composed = build_pipeline(
        RandomizerConfig(outfit=OutfitConfig(mode="rainbow")),
        toasty_assets=assets,
        toasty_probability_per_thousand=DEFAULT_PROBABILITY_PER_THOUSAND,
    )
    types = [type(patch) for patch in composed.patches]
    toasty_index = types.index(ToastyProductionCompositionPatch)
    controls_index = types.index(ControlsProductionPatch)
    rainbow_index = types.index(RainbowPalettePatch)

    assert composed.patches[toasty_index].probability_per_thousand == (
        DEFAULT_PROBABILITY_PER_THOUSAND
    )
    assert types.index(GameSettingsTurnPatch) < toasty_index
    assert toasty_index < controls_index < rainbow_index


def test_product_default_probability_is_eight_percent() -> None:
    assert DEFAULT_PROBABILITY_PER_THOUSAND == 80


def test_toasty_source_offset_matches_shared_runtime_offset() -> None:
    assert SHARED_EXPANSION_ROM == 0x00F68000
    assert MODULE_ROM == 0x00F697E0
    assert MODULE_ROM - SHARED_EXPANSION_ROM == MODULE_K0 - 0x801AF820


def test_toasty_init_uses_shifted_ci4_module() -> None:
    assert _build_call_trampoline() == bytes.fromhex("080266CF 00000000 00000000")
    assert _build_init_loader() == bytes.fromhex("3C19A01B 27391000 03200008 00000000")
