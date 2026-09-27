"""Disposable proof: suppress key-pickup checkpoint process spawns only.

The stock generic key/special callback at 0x80038770 launches the same class-0x15
process callback (0x80062D60) from three key-specific sites.  This proof NOPs
only those three JAL instructions while preserving their delay slots, stage/key
state writes, native inventory award, acquired-bit bookkeeping, and pickup SFX.

This module is intentionally NOT part of the production patch pipeline until the
bounded manual runtime route is validated.
"""

from __future__ import annotations

from ..rom import RomImage
from .base import PatchContext

NOP = 0

# Each guard covers the spawn call plus its existing delay-slot argument setup:
#   jal   0x8002830C
#   addiu a0, zero, 0x15
KEY_CHECKPOINT_SPAWN_SITES: tuple[tuple[int, bytes], ...] = (
    (0x000393D4, bytes.fromhex("0C00A0C3 24040015")),
    (0x00039460, bytes.fromhex("0C00A0C3 24040015")),
    (0x00039484, bytes.fromhex("0C00A0C3 24040015")),
)


class KeyCheckpointSuppressionProofPatch:
    """Suppress only the three generic-key checkpoint process spawns."""

    name = "key-checkpoint-suppression-proof"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        for offset, expected in KEY_CHECKPOINT_SPAWN_SITES:
            rom.expect_bytes(offset, expected)

        for offset, _expected in KEY_CHECKPOINT_SPAWN_SITES:
            rom.write_u32(offset, NOP)

        return (
            "proof-only: suppressed 3 key callback checkpoint-process JALs",
            "preserved delay slots, inventory awards, key state/bit bookkeeping, and pickup sound",
            "requires manual runtime validation before production integration",
        )
