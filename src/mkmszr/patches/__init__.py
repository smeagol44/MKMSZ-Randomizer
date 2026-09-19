"""Composable native ROM patch modules."""

from .arena import ArenaReservationPatch
from .boot_branding import BootBrandingPatch
from .box_indicator import BoxIndicatorPatch
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
from .runtime_v1 import (
    RuntimeV1FirePersistencePatch,
    runtime_v1_fire_patches,
)
from .stage_selector import SafeStageSelectorPatch

__all__ = [
    "PICKUP_PERSISTENCE_PAYLOAD",
    "ArenaReservationPatch",
    "BootBrandingPatch",
    "BoxIndicatorPatch",
    "FourBoxInventoryPatch",
    "ManagerPersistenceFirePatch",
    "NativePayloadPatch",
    "NativePayloadSpec",
    "PickupPersistencePatch",
    "RuntimeV1FirePersistencePatch",
    "SafeStageSelectorPatch",
    "SubZeroPalettePatch",
    "manager_persistence_fire_patches",
    "pickup_persistence_patches",
    "runtime_v1_fire_patches",
]
