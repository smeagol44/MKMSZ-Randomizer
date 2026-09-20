"""Composable native ROM patch modules."""

from .arena import ArenaReservationPatch
from .boot_branding import BootBrandingPatch
from .box_indicator import BoxIndicatorPatch
from .flow_bypass import BootLogoBypassPatch, SafeStageSelectSkipAutoSavePatch
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
from .runtime_v1 import (
    RuntimeV1FirePersistencePatch,
    runtime_v1_fire_patches,
)
from .stage_selector import SafeStageSelectorPatch

__all__ = [
    "PICKUP_PERSISTENCE_PAYLOAD",
    "ArenaReservationPatch",
    "BootBrandingPatch",
    "BootLogoBypassPatch",
    "BoxIndicatorPatch",
    "FourBoxInventoryPatch",
    "ManagerPersistenceFirePatch",
    "NativePayloadPatch",
    "NativePayloadSpec",
    "PickupPersistencePatch",
    "PickupRandomizationPatch",
    "RuntimeV1FirePersistencePatch",
    "SafeStageSelectSkipAutoSavePatch",
    "SafeStageSelectorPatch",
    "SubZeroPalettePatch",
    "manager_persistence_fire_patches",
    "pickup_persistence_patches",
    "runtime_v1_fire_patches",
]
