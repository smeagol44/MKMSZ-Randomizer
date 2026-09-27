"""Runtime rainbow Sub-Zero outfit using a compact appended runtime tail.

The all-stage compact-tail v01 proof Runtime-confirmed that stock global fighter
file 0x87 can remain untouched in ROM while its runtime allocation grows by
exactly 0x2000 bytes.  Every stock 0x87 load is routed through a small wrapper
that loads a dedicated 8 KiB rainbow bank immediately after the stock fighter
resource.  The native frame-time palette acquisition/release behavior remains
unchanged.

The loader wrapper is emitted into the existing controls->Toasty expansion gap;
the bank itself is a separate raw global file (0x92).  This avoids the previous
0x459E0-byte duplicate copy of stock file 0x87 in high ROM.
"""

from __future__ import annotations

from ..data.addresses import (
    FILE_TABLE_ENTRY_SIZE,
    FILE_TABLE_ROM,
    PROVEN_PAYLOAD_ROM,
    RAW_FILE_LOADER_VA,
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
    jal,
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
from .controls_production import CONTROLS_RUNTIME_END, FILE_ROM as EXPANSION_FILE_ROM
from .game_settings_turn import EXPANSION_FILE_ENTRY_ROM
from .native_payload import kseg1_alias
from .palette import make_hue
from .runtime_v2 import CODE_CACHED_BASE, CODE_SIZE, STATE_UNCACHED_BASE
from .toasty_constants import MODULE_K0 as TOASTY_RUNTIME_BASE, MODULE_ROM as TOASTY_ROM

NOP = 0

SUBZERO_FILE_ID = 0x87
SUBZERO_FILE_ENTRY_ROM = FILE_TABLE_ROM + SUBZERO_FILE_ID * FILE_TABLE_ENTRY_SIZE
SUBZERO_FILE_ROM = 0x00748920
SUBZERO_FILE_END_ROM = 0x0078E300
SUBZERO_FILE_SIZE = SUBZERO_FILE_END_ROM - SUBZERO_FILE_ROM
SUBZERO_FILE_FLAG = 0

# The N64 clean-ROM entry is zero and the compact-tail v01 proof exercised this
# transport successfully across all eight safe stages.  This ID is now owned by
# the optional production rainbow feature.
RAINBOW_BANK_FILE_ID = 0x92
RAINBOW_BANK_FILE_ENTRY_ROM = FILE_TABLE_ROM + RAINBOW_BANK_FILE_ID * FILE_TABLE_ENTRY_SIZE
RAINBOW_BANK_ROM = 0x00F20000

RAINBOW_PALETTE_COUNT = 64
RAINBOW_PALETTE_SIZE = SUBZERO_PALETTE_COUNT * 2
RAINBOW_PALETTE_BANK_OFFSET = SUBZERO_FILE_SIZE
RAINBOW_PALETTE_BANK_SIZE = RAINBOW_PALETTE_COUNT * RAINBOW_PALETTE_SIZE
RAINBOW_BANK_END_ROM = RAINBOW_BANK_ROM + RAINBOW_PALETTE_BANK_SIZE
RAINBOW_START_HUE = 225.0
RAINBOW_HUE_STEP = 360.0 / RAINBOW_PALETTE_COUNT

RAINBOW_PHASE_OFFSET = 0x48

RAINBOW_HELPER_OFFSET = 0x2E0
RAINBOW_HELPER_CACHED_VA = CODE_CACHED_BASE + RAINBOW_HELPER_OFFSET
RAINBOW_HELPER_UNCACHED_VA = kseg1_alias(RAINBOW_HELPER_CACHED_VA)
RAINBOW_HELPER_ROM = PROVEN_PAYLOAD_ROM + RAINBOW_HELPER_OFFSET

# The accepted controls composition ends here and Toasty begins at 0x801B1000.
# The 88-byte wrapper occupies only the start of that already-reserved gap.
RAINBOW_LOADER_CACHED_VA = CONTROLS_RUNTIME_END
RAINBOW_LOADER_UNCACHED_VA = kseg1_alias(RAINBOW_LOADER_CACHED_VA)
RAINBOW_LOADER_ROM = EXPANSION_FILE_ROM + (RAINBOW_LOADER_CACHED_VA - 0x801AF820)

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

# Fifteen stock Sub-Zero loader paths share the same shape:
# size(0x87) -> allocate(v0) -> load(0x87, allocated_base).
# The proof changed only the allocator delay instruction and the loader JAL.
ALLOC_SIZE_DELAY_SITES = (
    0x0000DF40,
    0x0000E384,
    0x0000EF00,
    0x0000F628,
    0x0000FEB0,
    0x000105B0,
    0x000106B0,
    0x00010DBC,
    0x000116DC,
    0x000117DC,
    0x00011EA4,
    0x000125B4,
    0x00012F70,
    0x00013068,
    0x00024768,
)
LOAD_JAL_SITES = (
    0x0000DF50,
    0x0000E394,
    0x0000EF10,
    0x0000F638,
    0x0000FEC0,
    0x000105C0,
    0x000106C0,
    0x00010DCC,
    0x000116EC,
    0x000117EC,
    0x00011EB4,
    0x000125C4,
    0x00012F80,
    0x00013078,
    0x00024778,
)
EXPECTED_ALLOC_DELAY = 0x00402021  # addu a0,v0,zero
EXPECTED_RAW_LOADER_JAL = jal(RAW_FILE_LOADER_VA)
EXPECTED_LOAD_DELAY = addiu("a0", "zero", SUBZERO_FILE_ID)

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


def build_rainbow_loader_wrapper() -> bytes:
    """Load stock 0x87, then load the bank at base + stock file size.

    Entry matches the native raw-file loader call: a0=0x87 and a1=allocated
    fighter base.  Preserve v0/v1 from the stock load so callers observe the
    same return state.
    """

    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x20),
        sw("ra", 0x1C, "sp"),
        sw("a1", 0x18, "sp"),
        jal(RAW_FILE_LOADER_VA),
        NOP,
        sw("v0", 0x14, "sp"),
        sw("v1", 0x10, "sp"),
        lw("a1", 0x18, "sp"),
        *address_words("t0", SUBZERO_FILE_SIZE),
        addu("a1", "a1", "t0"),
        addiu("a0", "zero", RAINBOW_BANK_FILE_ID),
        jal(RAW_FILE_LOADER_VA),
        NOP,
        lw("v0", 0x14, "sp"),
        lw("v1", 0x10, "sp"),
        lw("a1", 0x18, "sp"),
        addiu("a0", "zero", SUBZERO_FILE_ID),
        lw("ra", 0x1C, "sp"),
        addiu("sp", "sp", 0x20),
        jr("ra"),
        NOP,
    )
    return e.finish()


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
        # The common V2 initializer owns this state word.  Mask defensively
        # before use as the all-stage compact proof did.
        andi("t1", "t1", RAINBOW_PALETTE_COUNT - 1),
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


RAINBOW_LOADER_WRAPPER = build_rainbow_loader_wrapper()
RAINBOW_HELPER = build_rainbow_helper()
FRAME_SETUP_HOOK = build_frame_setup_hook()

if len(RAINBOW_LOADER_WRAPPER) != 0x58:
    raise AssertionError(f"rainbow loader wrapper size drifted: 0x{len(RAINBOW_LOADER_WRAPPER):X}")
if RAINBOW_LOADER_CACHED_VA + len(RAINBOW_LOADER_WRAPPER) > TOASTY_RUNTIME_BASE:
    raise AssertionError("rainbow loader wrapper reaches Toasty allocation")
if len(RAINBOW_HELPER) != 0xD0:
    raise AssertionError(f"rainbow helper size drifted: 0x{len(RAINBOW_HELPER):X}")
if RAINBOW_HELPER_OFFSET + len(RAINBOW_HELPER) > CODE_SIZE:
    raise AssertionError("rainbow helper exceeds runtime code reservation")


class RainbowPalettePatch:
    """Install the Runtime-confirmed compact-tail 64-phase rainbow palette."""

    name = "subzero-rainbow-palette"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        # Stock 0x87 must remain the retail file.  The compact architecture
        # deliberately does not repoint or rewrite this file-table entry.
        if rom.read_u32(SUBZERO_FILE_ENTRY_ROM) != SUBZERO_FILE_ROM:
            raise PatchError("rainbow palette requires the stock Sub-Zero file entry")
        if rom.read_u32(SUBZERO_FILE_ENTRY_ROM + 4) != SUBZERO_FILE_END_ROM:
            raise PatchError("rainbow palette requires the stock Sub-Zero file size")
        if rom.read_u32(SUBZERO_FILE_ENTRY_ROM + 8) != SUBZERO_FILE_FLAG:
            raise PatchError("rainbow palette requires the stock Sub-Zero file flags")

        # Rainbow runs after ControlsProductionPatch so the shared file-0x1A
        # composition is already established and its runtime end is guarded.
        expansion_end_rom = rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4)
        if expansion_end_rom < RAINBOW_LOADER_ROM:
            raise PatchError("rainbow palette requires the controls production composition first")
        if expansion_end_rom > TOASTY_ROM and expansion_end_rom < RAINBOW_LOADER_ROM + len(
            RAINBOW_LOADER_WRAPPER
        ):
            raise PatchError("shared expansion file end is inconsistent with rainbow wrapper")

        rom.expect_bytes(FRAME_SETUP_ROM, FRAME_SETUP_EXPECTED)
        rom.expect_bytes(RAINBOW_HELPER_ROM, bytes(len(RAINBOW_HELPER)))
        rom.expect_bytes(RAINBOW_BANK_FILE_ENTRY_ROM, bytes(FILE_TABLE_ENTRY_SIZE))
        rom.expect_bytes(RAINBOW_BANK_ROM, b"\xFF" * RAINBOW_PALETTE_BANK_SIZE)
        rom.expect_bytes(RAINBOW_LOADER_ROM, b"\xFF" * len(RAINBOW_LOADER_WRAPPER))

        bank = build_rainbow_bank(rom)
        if len(bank) != RAINBOW_PALETTE_BANK_SIZE:
            raise AssertionError("rainbow palette bank size changed")

        # Dedicated raw bank transport.
        rom.write_bytes(RAINBOW_BANK_ROM, bank)
        rom.write_u32(RAINBOW_BANK_FILE_ENTRY_ROM + 0, RAINBOW_BANK_ROM)
        rom.write_u32(RAINBOW_BANK_FILE_ENTRY_ROM + 4, RAINBOW_BANK_END_ROM)
        rom.write_u32(RAINBOW_BANK_FILE_ENTRY_ROM + 8, 0)

        # Loader wrapper lives in the controls->Toasty gap.  Without Toasty the
        # shared file must be extended so stage init actually loads the wrapper.
        rom.write_bytes(RAINBOW_LOADER_ROM, RAINBOW_LOADER_WRAPPER)
        wrapper_end_rom = RAINBOW_LOADER_ROM + len(RAINBOW_LOADER_WRAPPER)
        if expansion_end_rom < wrapper_end_rom:
            rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, wrapper_end_rom)

        # Every stock 0x87 runtime allocation receives exactly one 8 KiB tail,
        # and every corresponding raw load routes through the wrapper.
        if len(ALLOC_SIZE_DELAY_SITES) != len(LOAD_JAL_SITES):
            raise AssertionError("rainbow Sub-Zero loader-site tables drifted")
        for alloc_site, load_site in zip(
            ALLOC_SIZE_DELAY_SITES, LOAD_JAL_SITES, strict=True
        ):
            rom.expect_u32(alloc_site, EXPECTED_ALLOC_DELAY)
            rom.expect_u32(load_site, EXPECTED_RAW_LOADER_JAL)
            rom.expect_u32(load_site + 4, EXPECTED_LOAD_DELAY)
            rom.write_u32(
                alloc_site,
                addiu("a0", "v0", RAINBOW_PALETTE_BANK_SIZE),
            )
            rom.write_u32(load_site, jal(RAINBOW_LOADER_UNCACHED_VA))

        rom.write_bytes(RAINBOW_HELPER_ROM, RAINBOW_HELPER)
        rom.write_bytes(FRAME_SETUP_ROM, FRAME_SETUP_HOOK)

        return (
            "Runtime-confirmed compact-tail 64-phase rainbow palette cycle",
            "stock global fighter file 0x87 remains untouched and at its retail file-table entry",
            (
                f"all {len(LOAD_JAL_SITES)} stock Sub-Zero loads allocate +"
                f"0x{RAINBOW_PALETTE_BANK_SIZE:X} and append the dedicated rainbow bank"
            ),
            (
                f"rainbow ROM data is only 0x{RAINBOW_PALETTE_BANK_SIZE:X} bytes at "
                f"0x{RAINBOW_BANK_ROM:08X}..0x{RAINBOW_BANK_END_ROM - 1:08X}"
            ),
            "native palette allocation/release path is preserved at fighter frame setup",
        )
