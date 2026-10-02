"""Composable native ROM patch modules."""

from .arena import ArenaReservationPatch
from .boot_branding import BootBrandingPatch
from .box_indicator import BoxIndicatorPatch
from .enemy_randomization import EnemyRandomizationPatch
from .flow_bypass import BootLogoBypassPatch, SafeStageSelectSkipAutoSavePatch
from .game_settings_turn import GameSettingsTurnPatch
from .global_materialization import GlobalItemMaterializationPatch
from .inventory_boxes import FourBoxInventoryPatch
from .manager_persistence import (
    ManagerPersistenceFirePatch,
    manager_persistence_fire_patches,
)
from .native_payload import NativePayloadPatch, NativePayloadSpec
from .palette import SubZeroPalettePatch
from .pickup_persistence import (
    PICKUP_PERSISTENCE_PAYLOAD,
    PickupPersistencePatch,
    pickup_persistence_patches,
)
from .pickup_randomization import PickupRandomizationPatch
from .power_order import PowerOrderPatch
from .progression_presentation import ProgressionPickupPresentationPatch
from .rainbow_palette import RainbowPalettePatch
from .run_lifecycle import RunLifecyclePatch
from .runtime_v1 import (
    RuntimeV1FirePersistencePatch,
    runtime_v1_fire_patches,
)
from .stage_selector import SafeStageSelectorPatch
from .temple_intro_audio import MktAudioClip, TempleIntroAudioAssets, TempleIntroAudioPatch
from .temple_special_check import TempleSpecialCheckPatch
from .title_branding import TitleBrandingPatch
from .toasty import ToastyProductionCompositionPatch
from .toasty_constants import ToastyAssets
from .xp_progression import XPProgressionPatch

__all__ = [
    "PICKUP_PERSISTENCE_PAYLOAD",
    "ArenaReservationPatch",
    "BootBrandingPatch",
    "BootLogoBypassPatch",
    "BoxIndicatorPatch",
    "EnemyRandomizationPatch",
    "FourBoxInventoryPatch",
    "GameSettingsTurnPatch",
    "GlobalItemMaterializationPatch",
    "ManagerPersistenceFirePatch",
    "MktAudioClip",
    "NativePayloadPatch",
    "NativePayloadSpec",
    "PickupPersistencePatch",
    "PickupRandomizationPatch",
    "PowerOrderPatch",
    "ProgressionPickupPresentationPatch",
    "RainbowPalettePatch",
    "RunLifecyclePatch",
    "RuntimeV1FirePersistencePatch",
    "SafeStageSelectSkipAutoSavePatch",
    "SafeStageSelectorPatch",
    "SubZeroPalettePatch",
    "TempleIntroAudioAssets",
    "TempleIntroAudioPatch",
    "TempleSpecialCheckPatch",
    "TitleBrandingPatch",
    "ToastyAssets",
    "ToastyProductionCompositionPatch",
    "XPProgressionPatch",
    "manager_persistence_fire_patches",
    "pickup_persistence_patches",
    "runtime_v1_fire_patches",
]
