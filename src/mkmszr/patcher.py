"""High-level patch orchestration shared by CLI and future frontends."""

from dataclasses import dataclass
from pathlib import Path

from .config import RandomizerConfig
from .resource_materialization import GlobalMaterializationPlan
from .patches import (
    PICKUP_PERSISTENCE_PAYLOAD,
    ArenaReservationPatch,
    BootBrandingPatch,
    BootLogoBypassPatch,
    BoxIndicatorPatch,
    EnemyRandomizationPatch,
    FourBoxInventoryPatch,
    GameSettingsTurnPatch,
    GlobalItemMaterializationPatch,
    NativePayloadPatch,
    NativePayloadSpec,
    PickupPersistencePatch,
    PickupRandomizationPatch,
    PowerOrderPatch,
    RainbowPalettePatch,
    SafeStageSelectorPatch,
    SafeStageSelectSkipAutoSavePatch,
    SubZeroPalettePatch,
    TempleIntroAudioAssets,
    TempleIntroAudioPatch,
    TempleSpecialCheckPatch,
    TitleBrandingPatch,
    ToastyAssets,
    ToastyProductionCompositionPatch,
    XPProgressionPatch,
)
from .patches.base import PatchContext, PatchPipeline, PatchResult
from .patches.controls_production import ControlsProductionPatch
from .patches.inventory_boxes import (
    COMBOS_ASSIST_STATE_MASK,
    JUMP_BUTTON_STATE_MASK,
    RUN_AUTO_STATE_MASK,
    SPECIALS_MODERN_STATE_MASK,
    TURN_LOCK_STATE_MASK,
)
from .patches.required_powers import RequiredPowersPatch, resolve_required_powers
from .patches.toasty_codegen import pack_toasty_module
from .rom import RomImage


@dataclass(frozen=True)
class BuildResult:
    data: bytes
    crc1: int
    crc2: int
    output_sha256: str
    changed_spans: tuple[tuple[int, int], ...]
    patches: tuple[PatchResult, ...]
    required_powers_count: int | None
    required_powers_xp: int


def build_pipeline(
    config: RandomizerConfig,
    *,
    toasty_assets: ToastyAssets | None = None,
    temple_intro_audio_assets: TempleIntroAudioAssets | None = None,
    toasty_probability_per_thousand: int = 80,
    materialization_plan: GlobalMaterializationPlan | None = None,
) -> PatchPipeline:
    settings_state = 0
    if config.game_settings.turn_lock:
        settings_state |= TURN_LOCK_STATE_MASK
    if config.game_settings.attack_modern:
        settings_state |= COMBOS_ASSIST_STATE_MASK
    if config.game_settings.specials_modern:
        settings_state |= SPECIALS_MODERN_STATE_MASK
    if config.game_settings.jump_button:
        settings_state |= JUMP_BUTTON_STATE_MASK
    if config.game_settings.run_auto:
        settings_state |= RUN_AUTO_STATE_MASK

    if materialization_plan is not None and config.powers_as_pickups:
        raise ValueError(
            "explicit global materialization is not yet composable with the current "
            "pickup-XP overlay; global progression placement must be supplied by the "
            "future global generator/solver"
        )

    patches = [
        SafeStageSelectorPatch(),
        ArenaReservationPatch(),
        NativePayloadPatch(NativePayloadSpec(payload=PICKUP_PERSISTENCE_PAYLOAD)),
        PickupPersistencePatch(),
    ]
    if materialization_plan is None:
        patches.append(PickupRandomizationPatch())
    patches.append(FourBoxInventoryPatch(initial_settings_state=settings_state))
    if config.powers_as_pickups:
        # Only pickup mode replaces the four-box resume tail. The other mode
        # keeps stock XP stores/caps and ordinary Herbs callbacks.
        patches.append(XPProgressionPatch())
    patches.extend(
        [
            GameSettingsTurnPatch(),
            SafeStageSelectSkipAutoSavePatch(),
            BoxIndicatorPatch(),
            BootBrandingPatch(config.edition_name),
            BootLogoBypassPatch(),
            TitleBrandingPatch(config.edition_name, config.outfit),
        ]
    )
    outfit_mode = config.outfit.mode.lower()
    if outfit_mode != "rainbow" and outfit_mode != "vanilla":
        patches.append(
            SubZeroPalettePatch(
                outfit_mode,
                hue_degrees=config.outfit.hue_degrees,
                rgb=config.outfit.rgb,
            )
        )
    if toasty_assets is not None:
        patches.append(
            ToastyProductionCompositionPatch(
                toasty_assets,
                probability_per_thousand=toasty_probability_per_thousand,
            )
        )
    if temple_intro_audio_assets is not None:
        patches.append(TempleIntroAudioPatch(temple_intro_audio_assets))
    patches.append(
        ControlsProductionPatch(
            toasty_size=(
                len(pack_toasty_module(toasty_assets, toasty_probability_per_thousand).data)
                if toasty_assets is not None else None
            ),
        )
    )
    # Compact rainbow owns an optional wrapper in the guarded controls->Toasty
    # expansion gap, so it must compose after ControlsProductionPatch.
    if outfit_mode == "rainbow":
        patches.append(RainbowPalettePatch())
    # The scripted Temple check uses the production file-0x1A expansion
    # transport and composes after the optional rainbow wrapper. Its validated
    # location/progression/persistence behavior remains separate from the 84
    # ordinary pickup records.
    patches.append(TempleSpecialCheckPatch())
    if materialization_plan is not None:
        patches.append(GlobalItemMaterializationPatch(materialization_plan))
    # Controls production deliberately verifies the stock Slide/Super Slide
    # gates before installing helpers that call those recognizers. Apply the
    # optional order remap afterwards so both safety guards and shuffled tiers
    # remain authoritative.
    if config.shuffle_power_progression:
        patches.append(PowerOrderPatch())
    if config.required_powers_mode != "vanilla":
        patches.append(
            RequiredPowersPatch(
                config.required_powers_mode, config.custom_required_powers
            )
        )
    if config.enemy_randomization:
        patches.append(EnemyRandomizationPatch())
    return PatchPipeline(patches)


def patch_bytes(
    source: bytes,
    config: RandomizerConfig,
    *,
    toasty_assets: ToastyAssets | None = None,
    temple_intro_audio_assets: TempleIntroAudioAssets | None = None,
    toasty_probability_per_thousand: int = 80,
    materialization_plan: GlobalMaterializationPlan | None = None,
) -> BuildResult:
    rom = RomImage.from_bytes(source, require_clean=True)
    results = build_pipeline(
        config,
        toasty_assets=toasty_assets,
        temple_intro_audio_assets=temple_intro_audio_assets,
        toasty_probability_per_thousand=toasty_probability_per_thousand,
        materialization_plan=materialization_plan,
    ).apply(rom, PatchContext(seed=config.seed))
    required_count, required_xp = resolve_required_powers(
        config.required_powers_mode, config.custom_required_powers, config.seed
    )
    crc1, crc2 = rom.update_header_crc()
    return BuildResult(
        data=rom.to_bytes(),
        crc1=crc1,
        crc2=crc2,
        output_sha256=rom.output_sha256,
        changed_spans=rom.changed_spans(),
        patches=results,
        required_powers_count=required_count,
        required_powers_xp=required_xp,
    )


def patch_file(
    source: Path,
    output: Path,
    config: RandomizerConfig,
    *,
    toasty_assets: ToastyAssets | None = None,
    temple_intro_audio_assets: TempleIntroAudioAssets | None = None,
    toasty_probability_per_thousand: int = 80,
    materialization_plan: GlobalMaterializationPlan | None = None,
) -> BuildResult:
    if source.resolve() == output.resolve():
        raise ValueError("output must be a separate file; the clean ROM is never modified in place")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output}")
    result = patch_bytes(
        source.read_bytes(),
        config,
        toasty_assets=toasty_assets,
        temple_intro_audio_assets=temple_intro_audio_assets,
        toasty_probability_per_thousand=toasty_probability_per_thousand,
        materialization_plan=materialization_plan,
    )
    output.write_bytes(result.data)
    if output.read_bytes() != result.data:
        raise OSError("output re-read verification failed")
    return result
