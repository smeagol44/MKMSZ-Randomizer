"""Composable native ROM patch modules."""

from .arena import ArenaReservationPatch
from .manager_persistence import (
    ManagerPersistenceFirePatch,
    manager_persistence_fire_patches,
)
from .native_payload import NativePayloadPatch, NativePayloadSpec
from .palette import SubZeroPalettePatch
from .runtime_v1 import (
    RuntimeV1FirePersistencePatch,
    runtime_v1_fire_patches,
)
from .stage_selector import SafeStageSelectorPatch

__all__ = [
    "ArenaReservationPatch",
    "ManagerPersistenceFirePatch",
    "NativePayloadPatch",
    "NativePayloadSpec",
    "RuntimeV1FirePersistencePatch",
    "SafeStageSelectorPatch",
    "SubZeroPalettePatch",
    "manager_persistence_fire_patches",
    "runtime_v1_fire_patches",
]
