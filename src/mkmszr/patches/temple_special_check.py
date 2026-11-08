"""Production Temple scripted-check replacement.

The Temple Map is not an ordinary pickup. 1.0 keeps its scripted physical
location/progression owner, removes logical Map item 0x0D from the randomizer
pool, and treats the location as a special check.

The current interim product materializes Herbs at that special check. The
global item materializer will later supply the assigned logical reward; this
module owns only the Temple-specific seams that were Runtime-confirmed by the
v02 bounded proof:

- stock scripted actor/progression path remains intact;
- visible Map presentation is replaced by Temple's native Herbs presentation;
- inventory award becomes Herbs instead of Map;
- one dedicated MKSV header flag persists the special check independently of
  the 84 ordinary-pickup bitsets;
- on Temple re-entry, the stock Map-local collected word is reconstructed and
  execution resumes at the post-award elevator/platform loop without re-award.
"""

from __future__ import annotations

from ..data.addresses import FILE_TABLE_ENTRY_SIZE, FILE_TABLE_ROM
from ..errors import PatchError
from ..mips import Emitter, addiu, address_words, andi, jal, jr, jump, lw, ori, sw
from ..rom import RomImage
from .base import PatchContext
from .runtime_v2 import STATE_FLAGS_OFFSET, STATE_UNCACHED_BASE

NOP = 0

# Shared production expansion file 0x1A. Modern controls end at 0x801B0880;
# compact rainbow may own 0x801B0880..0x801B08D8. The Temple helper starts at
# the next 16-byte boundary and remains well below Toasty's fixed 0x801B1000.
EXPANSION_FILE_ID = 0x1A
EXPANSION_FILE_ENTRY_ROM = FILE_TABLE_ROM + EXPANSION_FILE_ID * FILE_TABLE_ENTRY_SIZE
EXPANSION_FILE_ROM = 0x00F68000
EXPANSION_FILE_RDRAM = 0x801AF820
CONTROLS_END_ROM = 0x00F69060
RAINBOW_WRAPPER_END_ROM = 0x00F690B8
TOASTY_ROM = 0x00F697E0

TEMPLE_MODULE_CACHED_BASE = 0x801B08E0
TEMPLE_MODULE_ROM = EXPANSION_FILE_ROM + (
    TEMPLE_MODULE_CACHED_BASE - EXPANSION_FILE_RDRAM
)

STATE_FLAGS_VA = STATE_UNCACHED_BASE + STATE_FLAGS_OFFSET
TEMPLE_SPECIAL_CHECK_STATE_MASK = 0x0001

# Stock stage-local Map collected/state word used by the scripted Temple path.
LEGACY_MAP_FLAG_VA = 0x8026E9A4

# Temple overlay file 0xA0, loaded at 0x802ECE30.
MAP_CHECK_HOOK_ROM = 0x000CC358  # VA 0x802EEC78
MAP_CHECK_RESUME_VA = 0x802EEC80
MAP_POST_AWARD_LOOP_VA = 0x802EEE94
MAP_AWARD_CALL_ROM = 0x000CC53C
INSERT_INVENTORY_VA = 0x80075448

# Runtime-confirmed v02 Herbs presentation/reward transform.
# The visual path uses Temple's native Herbs resource selector 15 and palette.
VISUAL_PATCHES = {
    0x000CC368: (0x3C02802F, 0x3C04800B),
    0x000CC36C: (0x8C4282B8, 0x24841D3C),
    0x000CC378: (0x0C007207, 0x0C00714A),
    0x000CC37C: (0x00442021, NOP),
    0x000CC384: (0x24050024, 0x24050020),
    0x000CC3A8: (0x02002021, 0x2604003C),
    0x000CC428: (0x8E100000, 0x8E10003C),
    0x000CC540: (0x2404000D, 0x24040004),
}


def build_check_helper() -> bytes:
    """Skip re-award after re-entry while preserving the elevator process."""

    e = Emitter()
    e.emit(*address_words("t0", STATE_FLAGS_VA))
    e.emit(lw("t1", 0, "t0"), andi("t1", "t1", TEMPLE_SPECIAL_CHECK_STATE_MASK))
    e.bne("t1", "zero", "collected")
    e.emit(NOP)

    # Replay the two instructions displaced by MAP_CHECK_HOOK_ROM.
    e.emit(lw("v0", 0x18, "v0"), andi("v0", "v0", 0x0080))
    e.emit(jump(MAP_CHECK_RESUME_VA), NOP)

    e.label("collected")
    e.emit(*address_words("t0", LEGACY_MAP_FLAG_VA))
    e.emit(addiu("t1", "zero", 0x0100), sw("t1", 0, "t0"))
    e.emit(jump(MAP_POST_AWARD_LOOP_VA), NOP)
    return e.finish()


def build_award_helper() -> bytes:
    """Award the configured item, then persist the special location."""

    e = Emitter()
    e.emit(addiu("sp", "sp", -0x18), sw("ra", 0x10, "sp"))
    e.emit(jal(INSERT_INVENTORY_VA), NOP)

    # Stock ignores the insertion return and continues cleanup/progression.
    e.emit(*address_words("t0", STATE_FLAGS_VA))
    e.emit(
        lw("t1", 0, "t0"),
        ori("t1", "t1", TEMPLE_SPECIAL_CHECK_STATE_MASK),
        sw("t1", 0, "t0"),
    )
    e.emit(*address_words("t0", LEGACY_MAP_FLAG_VA))
    e.emit(addiu("t1", "zero", 0x0100), sw("t1", 0, "t0"))
    e.emit(
        lw("ra", 0x10, "sp"),
        addiu("sp", "sp", 0x18),
        jr("ra"),
        NOP,
    )
    return e.finish()


CHECK_HELPER = build_check_helper()
AWARD_HELPER = build_award_helper()
CHECK_HELPER_OFFSET = 0
AWARD_HELPER_OFFSET = (len(CHECK_HELPER) + 0x0F) & ~0x0F
TEMPLE_MODULE_SIZE = (AWARD_HELPER_OFFSET + len(AWARD_HELPER) + 0x0F) & ~0x0F
TEMPLE_MODULE = (
    CHECK_HELPER
    + bytes(AWARD_HELPER_OFFSET - len(CHECK_HELPER))
    + AWARD_HELPER
    + bytes(TEMPLE_MODULE_SIZE - AWARD_HELPER_OFFSET - len(AWARD_HELPER))
)
TEMPLE_MODULE_END_ROM = TEMPLE_MODULE_ROM + TEMPLE_MODULE_SIZE
TEMPLE_MODULE_END_CACHED = TEMPLE_MODULE_CACHED_BASE + TEMPLE_MODULE_SIZE
CHECK_HELPER_VA = TEMPLE_MODULE_CACHED_BASE + CHECK_HELPER_OFFSET
AWARD_HELPER_VA = TEMPLE_MODULE_CACHED_BASE + AWARD_HELPER_OFFSET

if TEMPLE_MODULE_ROM < RAINBOW_WRAPPER_END_ROM:
    raise AssertionError("Temple special-check module overlaps compact rainbow")
if TEMPLE_MODULE_END_ROM > TOASTY_ROM:
    raise AssertionError("Temple special-check module reaches Toasty allocation")


class TempleSpecialCheckPatch:
    """Install the Runtime-confirmed Temple special-check policy."""

    name = "temple-special-check"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM, EXPANSION_FILE_ROM)
        file_end = rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)
        if file_end < CONTROLS_END_ROM:
            raise PatchError(
                "Temple special check requires the production controls/file-0x1A "
                "composition first"
            )
        if TEMPLE_MODULE_ROM < file_end < TEMPLE_MODULE_END_ROM:
            raise PatchError("file 0x1A end falls inside Temple module allocation")

        rom.expect_bytes(TEMPLE_MODULE_ROM, b"\xFF" * TEMPLE_MODULE_SIZE)
        for offset, (expected, _replacement) in VISUAL_PATCHES.items():
            rom.expect_u32(offset, expected)

        rom.expect_bytes(MAP_CHECK_HOOK_ROM, bytes.fromhex("8C420018 30420080"))
        rom.expect_u32(MAP_AWARD_CALL_ROM, 0x0C01D512)

        rom.write_bytes(TEMPLE_MODULE_ROM, TEMPLE_MODULE)
        if file_end < TEMPLE_MODULE_END_ROM:
            rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, TEMPLE_MODULE_END_ROM)

        for offset, (_expected, replacement) in VISUAL_PATCHES.items():
            rom.write_u32(offset, replacement)

        rom.write_u32(MAP_CHECK_HOOK_ROM, jump(CHECK_HELPER_VA))
        rom.write_u32(MAP_CHECK_HOOK_ROM + 4, NOP)
        rom.write_u32(MAP_AWARD_CALL_ROM, jal(AWARD_HELPER_VA))

        return (
            "Temple logical Map item 0x0D excluded; scripted location awards Herbs 0x04",
            "scripted actor uses native Temple Herbs presentation while stock progression remains",
            "special-check collection persists in MKSV header flags bit 0, outside 84 ordinary bits",
            "Temple re-entry reconstructs stock local state and resumes post-award elevator loop",
        )
