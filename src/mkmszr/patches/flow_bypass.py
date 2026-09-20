"""Runtime-confirmed frontend/stage-entry flow bypasses.

These patches intentionally preserve the normal save system and the legal
branding screen. They only skip:
- the two fixed company/logo presentations after the legal screen;
- the automatic save prompt armed by MKMSZR Safe Stage Select.
"""

from __future__ import annotations

from ..mips import jal
from ..rom import RomImage
from .base import PatchContext
from .inventory_boxes import (
    RELOCATED_MAPPER,
    RELOCATED_MAPPER_ROM,
    RELOCATED_MAPPER_VA,
)
from .stage_selector import SELECTION_LOAD_ROM

BOOT_LOGO_BYPASS_ROM = 0x0007A3F4
BOOT_LOGO_BYPASS_VA = 0x800797F4
BOOT_LOGO_GUARD = bytes.fromhex(
    "0C01F113 00000000 "
    "0C01F143 00000000 "
    "0C018576 24040080"
)
BOOT_LOGO_BRANCH = 0x10000003

SAFE_SELECTOR_SKIP_SAVE_ROM = RELOCATED_MAPPER_ROM
SAFE_SELECTOR_SKIP_SAVE_VA = RELOCATED_MAPPER_VA
SAFE_SELECTOR_SKIP_SAVE_EXPECTED = RELOCATED_MAPPER
SAFE_SELECTOR_SKIP_SAVE_PATCH = bytes.fromhex(
    "3C03800C "
    "8C6311E0 "
    "2C610006 "
    "50200001 "
    "24630002 "
    "3C028029 "
    "03E00008 "
    "A0441C0C"
)

AUTO_SAVE_BYPASS_FLAG_VA = 0x80291C0C
AUTO_STAGE_SAVE_VA = 0x800798A8


class SafeStageSelectSkipAutoSavePatch:
    """Arm the game's native one-shot stage-entry save bypass from the selector."""

    name = "safe-stage-select-skip-auto-save"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        rom.expect_u32(SELECTION_LOAD_ROM, jal(RELOCATED_MAPPER_VA))
        rom.expect_bytes(
            SAFE_SELECTOR_SKIP_SAVE_ROM,
            SAFE_SELECTOR_SKIP_SAVE_EXPECTED,
        )

        rom.write_bytes(
            SAFE_SELECTOR_SKIP_SAVE_ROM,
            SAFE_SELECTOR_SKIP_SAVE_PATCH,
        )

        return (
            "Safe Stage Select arms vanilla one-shot byte 0x80291C0C",
            "only the selector-triggered automatic stage-entry save prompt is skipped",
            "generic FUN_800798A8/manual/later post-stage save flows remain untouched",
        )


class BootLogoBypassPatch:
    """Skip the two mandatory post-legal company/logo presentations."""

    name = "boot-logo-bypass"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        rom.expect_bytes(BOOT_LOGO_BYPASS_ROM, BOOT_LOGO_GUARD)
        rom.write_u32(BOOT_LOGO_BYPASS_ROM, BOOT_LOGO_BRANCH)

        return (
            "legal/MKMSZR branding screen remains intact",
            "two fixed company/logo presentations are skipped",
            "vanilla FUN_800615D8(0x80) fade normalization and title handoff are preserved",
        )
