"""Runtime-confirmed Power Upgrade pickup presentation.

The accepted v23 TEST LAB proof closes the rapid-pickup lifecycle edge exposed
by dense debug placement: progression is awarded synchronously and the pickup
callback returns immediately, while the accepted three 2-tick white pulses run
in one guarded class-0x100 child process. Additional Power pickups collected
while that visual child is active still award normally and do not spawn a
second overlapping flash.

Production keeps the exact existing 0x1B0-byte file-0x1A allocation. The white
palette remains the stock Water-eel 64-color palette; the async helper occupies
0x12C bytes and the final module word is its active flag. No damage, reaction,
stun, input lock, or Water-overlay state is imported.
"""

from __future__ import annotations

from ..data.addresses import EXPANSION_POOL_START
from ..data.pickups import IDENTITY_OFFSET, STAGE_PICKUPS
from ..errors import PatchError
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

# v23 architecture fits the existing allocation exactly:
# 0x80 white palette + 0x12C helper + 4-byte active flag = 0x1B0.
FLASH_HELPER_SIZE = 0x12C
FLASH_ACTIVE_FLAG_OFFSET = 0x1AC
FLASH_MODULE_SIZE = 0x1B0
FLASH_MODULE_END_ROM = FLASH_MODULE_ROM + FLASH_MODULE_SIZE
FLASH_MODULE_END_K0 = FLASH_MODULE_K0 + FLASH_MODULE_SIZE
FLASH_ACTIVE_FLAG_ROM = FLASH_MODULE_ROM + FLASH_ACTIVE_FLAG_OFFSET
FLASH_ACTIVE_FLAG_K0 = FLASH_MODULE_K0 + FLASH_ACTIVE_FLAG_OFFSET
FLASH_ACTIVE_FLAG_K1 = kseg1_alias(FLASH_ACTIVE_FLAG_K0)

if FLASH_HELPER_OFFSET + FLASH_HELPER_SIZE != FLASH_ACTIVE_FLAG_OFFSET:
    raise AssertionError("async flash helper must end immediately before active flag")
if FLASH_ACTIVE_FLAG_OFFSET + 4 != FLASH_MODULE_SIZE:
    raise AssertionError("async flash flag must occupy the final module word")

# Exact stock Water-eel white palette: transparent index 0 + 63 white entries.
WATER_EEL_WHITE_PALETTE_ROM = 0x00615A14
WHITE_FLASH_PALETTE = b"\x00\x00" + b"\x7F\xFF" * 63

# Runtime-confirmed v23 architecture translated to the fixed production
# allocation. Wrapper entry 0xA01B21E0 awards synchronously and never sleeps.
# Child entry 0xA01B2228 owns every sleep/yield and exits through 0x80028564.
# The one-word active flag is the final word of the existing 0x1B0 allocation.
PRODUCTION_FLASH_HELPER = bytes.fromhex(
    "27bdffe8afbf00100c06bd88000000003c08a01b8d09230c15200007000000003c05a01b24a5222824090001ad09230c0c00a0c3240401008fbf001027bd001803e00008000000003c15800326b587943c08802c8d081ac011000027000000008d1006e012000024000000008611009e3c04801b2484216024050100000030213c16800226d9c5280320f809000000000440001900000000004090212453ff80241400030260202104110018000000002404000202a0f809000000000220202104110012000000002694ffff12800006000000002404000202a0f809000000001000fff0000000000240202126d9c64c0320f809000000003c08a01bad00230c26b9fdd00320f80900000000a604009e000440c03c0980290128482195280a02a608008003e0000800000000"
)
FLASH_CHILD_CALLBACK_ENTRY = 0xA01B2228
PRODUCTION_FLASH_HELPER_SHA256 = "373cc543b7586957681bda6770c0ed3eaa94e731ea4ff35c189305030aaf8563"

if len(PRODUCTION_FLASH_HELPER) != FLASH_HELPER_SIZE:
    raise AssertionError("async flash helper size drifted")

PROGRESSION_FLASH_CALLBACK_ENTRY = FLASH_HELPER_K1


class ProgressionPickupPresentationPatch:
    """Install Ice Blue Power Upgrade pickup flash presentation."""

    name = "progression-pickup-presentation"

    def __init__(self, *, global_mode: bool = False):
        self.global_mode = global_mode

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        if not context.seed:
            return ("no seed supplied; progression pickup presentation skipped",)

        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM, EXPANSION_FILE_ROM)
        file_end = rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)
        if FLASH_MODULE_ROM < file_end < FLASH_MODULE_END_ROM:
            raise PatchError(
                "shared file 0x1A ends inside the progression flash allocation"
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
        selected: tuple[tuple[int, int], ...] = ()
        if not self.global_mode:
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
        rom.write_u32(FLASH_ACTIVE_FLAG_ROM, 0)
        if file_end < FLASH_MODULE_END_ROM:
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
            "progression award completes synchronously; pickup callback performs no sleep/yield",
            "one guarded class-0x100 child owns the accepted three 2-tick white pulses",
            "rapid Power pickups still award while an existing flash child is active",
            "white palette is the exact stock Water-eel 64-color flash palette",
            "flash adds no damage, reaction, stun, or input-lock semantics",
            (
                f"shared file-0x1A flash module 0x{FLASH_MODULE_ROM:08X}.."
                f"0x{FLASH_MODULE_END_ROM - 1:08X}"
            ),
        )
