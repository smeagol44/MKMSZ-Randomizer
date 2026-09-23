"""Runtime rainbow Sub-Zero outfit.

This module productionizes the runtime-confirmed full-composition rainbow v01
proof. It keeps the established Sub-Zero clothing index boundary, relocates the
stock fighter file intact, appends 64 precomputed BGR555 palettes, and hooks the
native fighter frame-setup boundary through the existing MKMSZR 1 KiB runtime
reservation.
"""

from __future__ import annotations

from ..data.addresses import (
    FILE_TABLE_ENTRY_SIZE,
    FILE_TABLE_ROM,
    PROVEN_PAYLOAD_ROM,
    SUBZERO_CLOTHING_FIRST,
    SUBZERO_CLOTHING_LAST,
    SUBZERO_PALETTE_COLORS_ROM,
    SUBZERO_PALETTE_COUNT,
)
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    address_words,
    addu,
    andi,
    jalr,
    jr,
    lhu,
    lui,
    lw,
    ori,
    sh,
    sll,
    sw,
    words_blob,
)
from ..rom import RomImage
from .base import PatchContext
from .native_payload import kseg1_alias
from .palette import make_hue
from .runtime_v2 import CODE_CACHED_BASE, CODE_SIZE, STATE_UNCACHED_BASE

NOP = 0

SUBZERO_FILE_ID = 0x87
SUBZERO_FILE_ENTRY_ROM = FILE_TABLE_ROM + SUBZERO_FILE_ID * FILE_TABLE_ENTRY_SIZE
SUBZERO_FILE_ROM = 0x00748920
SUBZERO_FILE_END_ROM = 0x0078E300
SUBZERO_FILE_SIZE = SUBZERO_FILE_END_ROM - SUBZERO_FILE_ROM
SUBZERO_FILE_FLAG = 0

RAINBOW_FILE_ROM = 0x00F20000
RAINBOW_PALETTE_COUNT = 64
RAINBOW_PALETTE_SIZE = SUBZERO_PALETTE_COUNT * 2
RAINBOW_PALETTE_BANK_OFFSET = SUBZERO_FILE_SIZE
RAINBOW_PALETTE_BANK_SIZE = RAINBOW_PALETTE_COUNT * RAINBOW_PALETTE_SIZE
RAINBOW_FILE_SIZE = SUBZERO_FILE_SIZE + RAINBOW_PALETTE_BANK_SIZE
RAINBOW_FILE_END_ROM = RAINBOW_FILE_ROM + RAINBOW_FILE_SIZE
RAINBOW_START_HUE = 225.0
RAINBOW_HUE_STEP = 360.0 / RAINBOW_PALETTE_COUNT

RAINBOW_PHASE_OFFSET = 0x48

RAINBOW_HELPER_OFFSET = 0x2E0
RAINBOW_HELPER_CACHED_VA = CODE_CACHED_BASE + RAINBOW_HELPER_OFFSET
RAINBOW_HELPER_UNCACHED_VA = kseg1_alias(RAINBOW_HELPER_CACHED_VA)
RAINBOW_HELPER_ROM = PROVEN_PAYLOAD_ROM + RAINBOW_HELPER_OFFSET

FRAME_SETUP_ROM = 0x0001C9A0
FRAME_SETUP_CONTINUE_VA = 0x8001BDB0
FRAME_SETUP_EXPECTED = words_blob(
    [
        addu("a3", "a0", "zero"),
        lw("a0", 0x74, "a3"),
        sw("a1", 0x74, "a3"),
        lw("t0", 0, "a1"),
    ]
)

PALETTE_FIND_ALLOC_VA = 0x8001C528
PALETTE_RELEASE_VA = 0x8001C64C
SUBZERO_FIGHTER_TYPE = 4


def build_rainbow_bank(rom: RomImage) -> bytes:
    source = [
        rom.read_u16(SUBZERO_PALETTE_COLORS_ROM + index * 2)
        for index in range(SUBZERO_PALETTE_COUNT)
    ]
    out = bytearray()
    for phase in range(RAINBOW_PALETTE_COUNT):
        hue = (RAINBOW_START_HUE + phase * RAINBOW_HUE_STEP) % 360.0
        for index, word in enumerate(source):
            if SUBZERO_CLOTHING_FIRST <= index <= SUBZERO_CLOTHING_LAST:
                word = make_hue(word, hue)
            out += word.to_bytes(2, "big")
    return bytes(out)


def build_rainbow_helper() -> bytes:
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x28),
        sw("ra", 0x20, "sp"),
        sw("a0", 0x10, "sp"),
        sw("a1", 0x14, "sp"),
        lhu("t0", 0x78, "a0"),
        addiu("t1", "zero", SUBZERO_FIGHTER_TYPE),
    )
    e.bne("t0", "t1", "resume")
    e.emit(NOP)

    e.emit(*address_words("t0", STATE_UNCACHED_BASE))
    e.emit(
        lw("t1", RAINBOW_PHASE_OFFSET, "t0"),
        addiu("t2", "t1", 1),
        andi("t2", "t2", RAINBOW_PALETTE_COUNT - 1),
        sw("t2", RAINBOW_PHASE_OFFSET, "t0"),
        lw("t2", 0x98, "a0"),
        sll("t3", "t1", 7),
        addu("a0", "t2", "t3"),
        lui("t4", RAINBOW_PALETTE_BANK_OFFSET >> 16),
        ori("t4", "t4", RAINBOW_PALETTE_BANK_OFFSET & 0xFFFF),
        addu("a0", "a0", "t4"),
        addiu("a1", "zero", 0x100),
        addu("a2", "zero", "zero"),
        *address_words("t9", PALETTE_FIND_ALLOC_VA),
    )
    e.emit(jalr("t9"), NOP)
    e.emit(addiu("t0", "v0", 1))
    e.beq("t0", "zero", "resume")
    e.emit(NOP)

    e.emit(
        lw("t2", 0x10, "sp"),
        lhu("t0", 0x9E, "t2"),
        addiu("t1", "v0", -0x80),
        sh("t1", 0x9E, "t2"),
        sh("v0", 0x80, "t2"),
        addiu("a0", "t0", 0x80),
        *address_words("t9", PALETTE_RELEASE_VA),
    )
    e.emit(jalr("t9"), NOP)

    e.label("resume")
    e.emit(
        lw("a0", 0x10, "sp"),
        lw("a1", 0x14, "sp"),
        lw("ra", 0x20, "sp"),
        addiu("sp", "sp", 0x28),
        addu("a3", "a0", "zero"),
        lw("a0", 0x74, "a3"),
        sw("a1", 0x74, "a3"),
        lw("t0", 0, "a1"),
        *address_words("t9", FRAME_SETUP_CONTINUE_VA),
        jr("t9"),
        NOP,
    )
    return e.finish()


def build_frame_setup_hook() -> bytes:
    return words_blob([*address_words("t9", RAINBOW_HELPER_UNCACHED_VA), jr("t9"), NOP])


RAINBOW_HELPER = build_rainbow_helper()
FRAME_SETUP_HOOK = build_frame_setup_hook()

if len(RAINBOW_HELPER) != 0xCC:
    raise AssertionError(f"rainbow helper size drifted: 0x{len(RAINBOW_HELPER):X}")
if RAINBOW_HELPER_OFFSET + len(RAINBOW_HELPER) > CODE_SIZE:
    raise AssertionError("rainbow helper exceeds runtime code reservation")


class RainbowPalettePatch:
    """Install the runtime-confirmed continuously cycling Sub-Zero palette."""

    name = "subzero-rainbow-palette"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        if rom.read_u32(SUBZERO_FILE_ENTRY_ROM) != SUBZERO_FILE_ROM:
            raise PatchError("rainbow palette requires the stock Sub-Zero file entry")
        if rom.read_u32(SUBZERO_FILE_ENTRY_ROM + 4) != SUBZERO_FILE_END_ROM:
            raise PatchError("rainbow palette requires the stock Sub-Zero file size")
        if rom.read_u32(SUBZERO_FILE_ENTRY_ROM + 8) != SUBZERO_FILE_FLAG:
            raise PatchError("rainbow palette requires the stock Sub-Zero file flags")

        rom.expect_bytes(FRAME_SETUP_ROM, FRAME_SETUP_EXPECTED)
        rom.expect_bytes(RAINBOW_HELPER_ROM, bytes(len(RAINBOW_HELPER)))
        rom.expect_bytes(RAINBOW_FILE_ROM, b"\xFF" * RAINBOW_FILE_SIZE)

        source_file = bytes(rom.data[SUBZERO_FILE_ROM:SUBZERO_FILE_END_ROM])
        bank = build_rainbow_bank(rom)
        if len(bank) != RAINBOW_PALETTE_BANK_SIZE:
            raise AssertionError("rainbow palette bank size changed")

        rom.write_bytes(RAINBOW_FILE_ROM, source_file + bank)
        rom.write_u32(SUBZERO_FILE_ENTRY_ROM, RAINBOW_FILE_ROM)
        rom.write_u32(SUBZERO_FILE_ENTRY_ROM + 4, RAINBOW_FILE_END_ROM)
        rom.write_u32(SUBZERO_FILE_ENTRY_ROM + 8, SUBZERO_FILE_FLAG)
        rom.write_bytes(RAINBOW_HELPER_ROM, RAINBOW_HELPER)
        rom.write_bytes(FRAME_SETUP_ROM, FRAME_SETUP_HOOK)

        return (
            "runtime-confirmed 64-phase rainbow palette cycle",
            "only Sub-Zero clothing indices 0x21..0x3F change",
            (
                f"stock file 0x87 relocated intact to 0x{RAINBOW_FILE_ROM:08X} "
                f"and extended by 0x{RAINBOW_PALETTE_BANK_SIZE:X} palette bytes"
            ),
            "native palette allocation/release path is preserved at fighter frame setup",
        )
