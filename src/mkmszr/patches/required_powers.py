"""Guarded Fortress XP gate for the required Power Upgrades build setting.

Stock Fortress compares current XP with 5100 at VA 0x802EF49C. That value
lies between tiers 7 and 8, so it is an XP requirement, not an exact tier count.
Only the immediate of this comparison is changed for custom/seed modes.
"""

from __future__ import annotations

import hashlib

from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext
from .xp_progression import XP_THRESHOLDS

RNG_DOMAIN = b"MKMSZR:REQUIRED-POWERS:V1\0"
FORTRESS_FILE_ENTRY_ROM = 0x000A5778  # Raw overlay file 0x9E.
FORTRESS_FILE_START = 0x000C0330
FORTRESS_FILE_END = 0x000C4C70
FORTRESS_GATE_ROM = 0x000C299C
FORTRESS_GATE_STOCK = 0x286313EC  # slti v1,v1,5100
VANILLA_XP_REQUIREMENT = 5100


def resolve_required_powers(
    mode: str, custom_count: int | None, seed: str | None
) -> tuple[int | None, int]:
    """Return (tier count or None for stock, XP comparison threshold)."""

    if mode == "vanilla":
        return None, VANILLA_XP_REQUIREMENT
    if mode == "custom":
        if type(custom_count) is not int or not 0 <= custom_count <= 9:
            raise ValueError("custom required powers must be an integer from 0 to 9")
        count = custom_count
    elif mode == "seed":
        if not seed:
            raise PatchError("seed-derived required powers needs a seed")
        digest = hashlib.sha256(RNG_DOMAIN + seed.encode("utf-8")).digest()
        count = int.from_bytes(digest[:8], "big") % 10
    else:
        raise ValueError("required powers mode must be vanilla, custom, or seed")
    return count, XP_THRESHOLDS[count - 1] if count else 0


class RequiredPowersPatch:
    """Change only the guarded Fortress final XP comparison immediate."""

    name = "required-powers"

    def __init__(self, mode: str, custom_count: int | None = None):
        self.mode = mode
        self.custom_count = custom_count

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        count, threshold = resolve_required_powers(
            self.mode, self.custom_count, context.seed
        )
        if self.mode == "vanilla":
            return ("stock Fortress XP requirement 5100",)

        rom.expect_u32(FORTRESS_FILE_ENTRY_ROM, FORTRESS_FILE_START)
        rom.expect_u32(FORTRESS_FILE_ENTRY_ROM + 4, FORTRESS_FILE_END)
        rom.expect_u32(FORTRESS_FILE_ENTRY_ROM + 8, 0)
        rom.expect_u32(FORTRESS_GATE_ROM, FORTRESS_GATE_STOCK)
        rom.write_u32(FORTRESS_GATE_ROM, (FORTRESS_GATE_STOCK & 0xFFFF0000) | threshold)
        return (
            f"Fortress XP gate requires {count} power tier(s): XP >= {threshold}",
            f"mode={self.mode}; stock comparison and raw overlay file 0x9E guarded",
        )
