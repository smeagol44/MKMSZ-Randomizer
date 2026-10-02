"""Runtime-confirmed Power Upgrade pickup presentation.

The accepted TEST LAB v02 proof established the visual-only player flash:
three 2-tick white pulses alternating with the player's original palette.
This production patch reuses that exact helper loop and the stock Water-eel
all-white 64-color palette while changing only two proof-specific inputs:

- the wrapped callback is the existing pickup-progression award callback;
- the white palette lives in the global shared file-0x1A module instead of
  Water-stage resource memory.

No damage, reaction, stun, input lock, or Water-overlay state is imported.
"""

from __future__ import annotations

from ..data.addresses import EXPANSION_POOL_START
from ..data.pickups import IDENTITY_OFFSET, STAGE_PICKUPS
from ..errors import PatchError
from ..mips import address_words, words_blob
from ..rom import RomImage
from .base import PatchContext
from .native_payload import kseg1_alias
from .temple_special_check import EXPANSION_FILE_ENTRY_ROM, EXPANSION_FILE_ROM
from .toasty_constants import SHARED_EXPANSION_ROM
from .xp_progression import (
    CALLBACK_OFFSET_WITHIN_IDENTITY,
    PRESENTATION_OFFSET_WITHIN_IDENTITY,
    PROGRESSION_CALLBACK_ENTRY,
    PROGRESSION_HERBS_PRESENTATION_VA,
    build_progression_locations,
)

# Fixed late file-0x1A suballocation. Current compact Toasty ends at 0xF6A912.
FLASH_MODULE_ROM = 0x00F6A940
FLASH_MODULE_K0 = EXPANSION_POOL_START + (FLASH_MODULE_ROM - SHARED_EXPANSION_ROM)
FLASH_MODULE_K1 = kseg1_alias(FLASH_MODULE_K0)

WHITE_PALETTE_OFFSET = 0x000
FLASH_HELPER_OFFSET = 0x080
WHITE_PALETTE_ROM = FLASH_MODULE_ROM + WHITE_PALETTE_OFFSET
WHITE_PALETTE_K0 = FLASH_MODULE_K0 + WHITE_PALETTE_OFFSET
FLASH_HELPER_ROM = FLASH_MODULE_ROM + FLASH_HELPER_OFFSET
FLASH_HELPER_K0 = FLASH_MODULE_K0 + FLASH_HELPER_OFFSET
FLASH_HELPER_K1 = kseg1_alias(FLASH_HELPER_K0)

FLASH_HELPER_SIZE = 0x130
FLASH_MODULE_SIZE = FLASH_HELPER_OFFSET + FLASH_HELPER_SIZE
FLASH_MODULE_END_ROM = FLASH_MODULE_ROM + FLASH_MODULE_SIZE
FLASH_MODULE_END_K0 = FLASH_MODULE_K0 + FLASH_MODULE_SIZE

# Exact stock Water-eel white palette: transparent index 0 + 63 white entries.
WATER_EEL_WHITE_PALETTE_ROM = 0x00615A14
WHITE_FLASH_PALETTE = b"\x00\x00" + b"\x7F\xFF" * 63

# Runtime-confirmed TEST LAB v02 helper. Production changes only:
#   0x20..0x27: stock Herbs callback -> progression callback
#   0x50..0x5B: Water-resource palette lookup -> fixed white palette pointer
TESTLAB_FLASH_HELPER = bytes.fromhex(
    "27bdffd0afbf002cafb00028afb10024afb20020afb3001cafb40018afb50014"
    "3c198004273989bc0320f809000000003c08802c8d081ac01100002b00000000"
    "8d1006e012000028000000008611009e3c04802f8c8482b82484259024050100"
    "000030213c1980022739c5280320f809000000000440001c0000000000409021"
    "2453ff80241400033c15800326b58794026020210411001e0000000024040002"
    "02a0f809000000000220202104110018000000002694ffff1280000600000000"
    "2404000202a0f809000000001000fff000000000024020213c1980022739c64c"
    "0320f809000000008fb500148fb400188fb3001c8fb200208fb100248fb00028"
    "8fbf002c27bd003003e0000800000000a604009e000440c03c09802901284821"
    "95280a02a608008003e0000800000000"
)
if len(TESTLAB_FLASH_HELPER) != FLASH_HELPER_SIZE:
    raise AssertionError("accepted flash helper size drifted")


def build_production_flash_helper() -> bytes:
    """Return the accepted v02 loop with only production inputs substituted."""

    data = bytearray(TESTLAB_FLASH_HELPER)
    data[0x20:0x28] = words_blob(address_words("t9", PROGRESSION_CALLBACK_ENTRY))
    data[0x50:0x5C] = words_blob(
        (*address_words("a0", WHITE_PALETTE_K0), 0)
    )
    return bytes(data)


PRODUCTION_FLASH_HELPER = build_production_flash_helper()
PROGRESSION_FLASH_CALLBACK_ENTRY = FLASH_HELPER_K1


class ProgressionPickupPresentationPatch:
    """Install Ice Blue progression pickup flash presentation."""

    name = "progression-pickup-presentation"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        if not context.seed:
            return ("no seed supplied; progression pickup presentation skipped",)

        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM, EXPANSION_FILE_ROM)
        file_end = rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)
        if file_end > FLASH_MODULE_ROM:
            raise PatchError(
                "shared file 0x1A reaches the progression flash allocation"
            )

        rom.expect_bytes(
            WATER_EEL_WHITE_PALETTE_ROM,
            WHITE_FLASH_PALETTE,
        )
        rom.expect_bytes(
            FLASH_MODULE_ROM,
            b"\xFF" * FLASH_MODULE_SIZE,
        )

        stage_by_id = {stage.stage_id: stage for stage in STAGE_PICKUPS}
        selected = build_progression_locations(context.seed)
        for stage_id, destination in selected:
            record = stage_by_id[stage_id].records[destination]
            callback_rom = (
                record.rom_base
                + IDENTITY_OFFSET
                + CALLBACK_OFFSET_WITHIN_IDENTITY
            )
            presentation_rom = (
                record.rom_base
                + IDENTITY_OFFSET
                + PRESENTATION_OFFSET_WITHIN_IDENTITY
            )
            rom.expect_u32(callback_rom, PROGRESSION_CALLBACK_ENTRY)
            rom.expect_u32(
                presentation_rom,
                PROGRESSION_HERBS_PRESENTATION_VA,
            )

        rom.write_bytes(WHITE_PALETTE_ROM, WHITE_FLASH_PALETTE)
        rom.write_bytes(FLASH_HELPER_ROM, PRODUCTION_FLASH_HELPER)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, FLASH_MODULE_END_ROM)

        for stage_id, destination in selected:
            record = stage_by_id[stage_id].records[destination]
            callback_rom = (
                record.rom_base
                + IDENTITY_OFFSET
                + CALLBACK_OFFSET_WITHIN_IDENTITY
            )
            rom.write_u32(callback_rom, PROGRESSION_FLASH_CALLBACK_ENTRY)

        return (
            "Power Upgrade Herbs retain Ice Blue pickup presentation",
            "pickup callback wraps existing progression award with three 2-tick white pulses",
            "white palette is the exact stock Water-eel 64-color flash palette",
            "flash adds no damage, reaction, stun, or input-lock semantics",
            (
                f"shared file-0x1A flash module 0x{FLASH_MODULE_ROM:08X}.."
                f"0x{FLASH_MODULE_END_ROM - 1:08X}"
            ),
        )
