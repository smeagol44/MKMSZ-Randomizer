"""Water overlay boss-area scripted checkpoint target (stage-qualified).

The stock Water overlay script reads global selector 0x802C18F8,
increments it, writes it back, and immediately requests reconstruction.
That incorrectly chooses predecessor+1 when the immediately preceding
physical checkpoint was skipped. The owner reported the exact single-word
constant-six proof working; this implementation retains that proven opcode,
not an untested monotonic wrapper. Re-entry from selector >6 is not yet
runtime-covered, so do not generalize the rule to other stage writers.
"""

from __future__ import annotations

from ..rom import RomImage
from .base import PatchContext

WATER_SCRIPTED_CHECKPOINT_ROM = 0x000B9330
WATER_SCRIPTED_CHECKPOINT_VA = 0x802F11A0
WATER_SELECTOR_VA = 0x802C18F8
WATER_CHECKPOINT_TARGET = 6

# Entire stock local data-flow through selector load, event-state stores,
# checkpoint commit, and native stage-reconstruction JAL.
WATER_SCRIPT_CONTEXT_ROM = 0x000B931C
WATER_SCRIPT_CONTEXT_EXPECTED = bytes.fromhex(
    "3C02802C 944218F8 94630654 3C01800C "
    "A43211F8 24420001 3C01802C A42218F8 "
    "3C01801B A423E4C0 0C00D7CE 00000000"
)
WATER_RELATIVE_INCREMENT = 0x24420001  # addiu v0,v0,1
WATER_ABSOLUTE_SIX = 0x24020006  # addiu v0,zero,6


class WaterScriptedCheckpointPatch:
    """Use the verified Water boss-area target instead of predecessor+1."""

    name = "water-scripted-checkpoint"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context
        rom.expect_bytes(WATER_SCRIPT_CONTEXT_ROM, WATER_SCRIPT_CONTEXT_EXPECTED)
        rom.write_u32(WATER_SCRIPTED_CHECKPOINT_ROM, WATER_ABSOLUTE_SIX)
        return (
            (
                "Water overlay 0xA1 scripted transition sets checkpoint selector 6 "
                "before stock reconstruction, independent of skipped key checkpoints"
            ),
            (
                "Only ROM 0xB9330 is changed; scripted world-state, item callbacks "
                "and native reconstruction call are preserved"
            ),
        )
