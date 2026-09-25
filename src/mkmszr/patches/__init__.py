"""Composable native ROM patch modules."""

from .arena import ArenaReservationPatch
from .boot_branding import BootBrandingPatch
from .box_indicator import BoxIndicatorPatch
from .flow_bypass import BootLogoBypassPatch, SafeStageSelectSkipAutoSavePatch
from .game_settings_turn import GameSettingsTurnPatch
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
from .rainbow_palette import RainbowPalettePatch
from .runtime_v1 import (
    RuntimeV1FirePersistencePatch,
    runtime_v1_fire_patches,
)
from .stage_selector import SafeStageSelectorPatch
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
    "FourBoxInventoryPatch",
    "GameSettingsTurnPatch",
    "ManagerPersistenceFirePatch",
    "NativePayloadPatch",
    "NativePayloadSpec",
    "PickupPersistencePatch",
    "PickupRandomizationPatch",
    "RainbowPalettePatch",
    "RuntimeV1FirePersistencePatch",
    "SafeStageSelectSkipAutoSavePatch",
    "SafeStageSelectorPatch",
    "SubZeroPalettePatch",
    "TitleBrandingPatch",
    "ToastyAssets",
    "ToastyProductionCompositionPatch",
    "XPProgressionPatch",
    "manager_persistence_fire_patches",
    "pickup_persistence_patches",
    "runtime_v1_fire_patches",
]
