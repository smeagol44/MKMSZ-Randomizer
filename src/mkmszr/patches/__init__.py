"""Composable native ROM patch modules."""

from .arena import ArenaReservationPatch
from .native_payload import NativePayloadPatch, NativePayloadSpec
from .palette import SubZeroPalettePatch
from .runtime_v1 import (
    RuntimeV1FirePersistencePatch,
    runtime_v1_fire_patches,
)

__all__ = [
    "ArenaReservationPatch",
    "NativePayloadPatch",
    "NativePayloadSpec",
    "RuntimeV1FirePersistencePatch",
    "SubZeroPalettePatch",
    "runtime_v1_fire_patches",
]
