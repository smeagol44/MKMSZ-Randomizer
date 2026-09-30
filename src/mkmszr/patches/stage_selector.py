"""Compact safe native stage selector and selector-local presentation patch."""

from ..mips import (
    addiu,
    addu,
    and_,
    andi,
    branch,
    jal,
    jr,
    sltu,
    words_blob,
)
from ..rom import RomImage
from .base import PatchContext

DEBUG_MENU_VA = 0x8000D0B8

A_ROUTE_JAL_ROM = 0x0000E028
EXPECTED_A_ROUTE_JAL = 0x0C00A0C3

WRAP_LAST_ROM = 0x0000DD60
COUNT_ROM = 0x0000DD64
EXPECTED_WRAP_LAST = 0x2414000A
EXPECTED_COUNT = 0x2A82000B
PATCHED_WRAP_LAST = 0x24140007
PATCHED_COUNT = 0x2A820008

MENU_TABLE_ROM = 0x0009B7DC
ORIGINAL_MENU_POINTERS = (
    0x800AA034, 0x800AA02C, 0x800AA024, 0x800AA01C,
    0x800AA014, 0x800AA00C, 0x800AA004, 0x800A9FF4,
    0x800A9FEC, 0x800A9FE0, 0x800A9FD0, 0x00000000,
)
SAFE_MENU_POINTERS = (
    0x800AA034, 0x800AA02C, 0x800AA024, 0x800AA01C,
    0x800AA014, 0x800AA00C, 0x800A9FEC, 0x800A9FE0,
    0x00000000, 0x00000000, 0x00000000, 0x00000000,
)

SELECTION_LOAD_ROM = 0x00015CD0
EXPECTED_SELECTION_LOAD = bytes.fromhex("3C03800C 8C6311E0")

MAPPER_ROM = 0x0009A700
MAPPER_VA = 0x80099B00
MAPPER_CAVE_END = 0x0009A758

# The selector's 0x352..0x35A cursor and the title menu's 0x3CC..0x3D4
# cursor have byte-identical indexed pixel payloads for all nine frames.
# Both use all 29 palette indices. Keep file 0x5F and slot 0x1C2 intact and
# change only the selector-local 29-entry palette source.
SELECTOR_CURSOR_PALETTE_ROM = 0x000B21D8
TITLE_CURSOR_PALETTE_ROM = 0x000B32E8
CURSOR_PALETTE_COUNT = 0x1D
CURSOR_PALETTE_BYTES = CURSOR_PALETTE_COUNT * 2
EXPECTED_SELECTOR_CURSOR_PALETTE = bytes.fromhex(
    "0000 7FFF 6B5A 5294 4A52 1084 8000 0BBF 0EFF 0A7D "
    "09FB 0D38 0E37 09B7 4677 0236 3256 11D2 2DD2 0171 "
    "39F0 08F0 1530 2D8D 04CD 00EC 294B 048A 1CE9"
)
EXPECTED_TITLE_CURSOR_PALETTE = bytes.fromhex(
    "0000 7FFF 6AF4 5A70 51ED 2041 0001 7FA2 7EE3 7662 "
    "6DE2 6123 5E23 5DA2 5E71 5A20 5A4C 49C4 49A9 4560 "
    "4188 40E2 4125 3948 34C1 30E0 2CE6 2881 28C4"
)

# Frontend-resident selector audio hooks. These do not depend on the gameplay
# expansion files, which are not loaded yet at the title screen.
NATIVE_SFX_WRAPPER_VA = 0x80064C18
MOVE_SFX_DESCRIPTOR = 0x1FC
CONFIRM_SFX_DESCRIPTOR = 0x1FD

MOVE_SFX_HOOK_ROM = 0x0000DD70
EXPECTED_MOVE_SFX_HOOK = bytes.fromhex("24040050 24050014")
MOVE_SFX_HELPER_ROM = 0x0000E27C
MOVE_SFX_HELPER_VA = 0x8000D67C

# This helper region is a compiler epilogue after an unconditional debug-menu
# loop. Static scan found no direct branch/jump/JAL targets into the span.
DEAD_SELECTOR_EPILOGUE = words_blob(
    [
        0x8FBF0034,
        0x8FBE0030,
        0x8FB7002C,
        0x8FB60028,
        0x8FB50024,
        0x8FB40020,
        0x8FB3001C,
        0x8FB20018,
        0x8FB10014,
        0x8FB00010,
        0x27BD0038,
        0x03E00008,
        0x00000000,
    ]
)

NOP = 0


def build_selection_mapper() -> bytes:
    return words_blob(
        [
            0x3C03800C,
            0x8C6311E0,
            0x2C610006,
            0x14200002,
            NOP,
            0x24630002,
            0x03E00008,
            NOP,
        ]
    )


def build_move_sfx_helper() -> bytes:
    """Play selector MOVE/CONFIRM sounds on their input edges.

    v01 proved the blue cursor and MOVE sound at runtime, but its confirmation
    call at the later stage-commit seam was inaudible. v02 instead observes the
    A-button edge while the selector frontend loop is still live. The native
    selector sleeps two ticks later in the same loop before commit handling.
    """

    # At 0x8000D170:
    #   A0 = current-input XOR previous-input (changed bits)
    #   S6 = current input
    #
    # New A is semantic bit 0x0002. New Up/Down are 0x4000/0x1000.
    # A has priority if pressed simultaneously with a direction:
    #   descriptor = 0x1FC + bool(new A) => MOVE or CONFIRM.
    #
    # S0 is dead until 0x8000D1AC and the native SFX wrapper preserves S0,
    # so S0 safely carries the hook return address across the nested JAL.
    return words_blob(
        [
            and_("t0", "a0", "s6"),
            andi("t1", "t0", 0x0002),
            sltu("t1", "zero", "t1"),
            andi("t0", "t0", 0x5002),
            branch(0x04, "t0", "zero", 5),
            addu("s0", "ra", "zero"),
            addiu("a0", "t1", MOVE_SFX_DESCRIPTOR),
            addiu("a2", "zero", 0x3F),
            jal(NATIVE_SFX_WRAPPER_VA),
            addu("a1", "zero", "zero"),
            # Recreate the draw arguments displaced by the hook/callee.
            addiu("a0", "zero", 0x50),
            jr("s0"),
            addiu("a1", "zero", 0x14),
        ]
    )


MOVE_SFX_HELPER = build_move_sfx_helper()
if len(MOVE_SFX_HELPER) != len(DEAD_SELECTOR_EPILOGUE):
    raise AssertionError("selector SFX helper must exactly fill its dead epilogue")


class SafeStageSelectorPatch:
    """Install the compact 8-stage selector plus selector-local cursor/audio."""

    name = "safe-stage-selector"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        rom.expect_u32(A_ROUTE_JAL_ROM, EXPECTED_A_ROUTE_JAL)
        rom.expect_u32(WRAP_LAST_ROM, EXPECTED_WRAP_LAST)
        rom.expect_u32(COUNT_ROM, EXPECTED_COUNT)
        rom.expect_bytes(MENU_TABLE_ROM, words_blob(ORIGINAL_MENU_POINTERS))
        rom.expect_bytes(SELECTION_LOAD_ROM, EXPECTED_SELECTION_LOAD)
        rom.expect_bytes(
            MAPPER_ROM,
            bytes(MAPPER_CAVE_END - MAPPER_ROM),
        )

        # Presentation guards are deliberately selector-local. File 0x5E/0x5F
        # contents and file-table entries remain untouched.
        rom.expect_u32(SELECTOR_CURSOR_PALETTE_ROM - 4, CURSOR_PALETTE_COUNT)
        rom.expect_u32(TITLE_CURSOR_PALETTE_ROM - 4, CURSOR_PALETTE_COUNT)
        rom.expect_bytes(
            SELECTOR_CURSOR_PALETTE_ROM,
            EXPECTED_SELECTOR_CURSOR_PALETTE,
        )
        rom.expect_bytes(
            TITLE_CURSOR_PALETTE_ROM,
            EXPECTED_TITLE_CURSOR_PALETTE,
        )
        rom.expect_bytes(MOVE_SFX_HOOK_ROM, EXPECTED_MOVE_SFX_HOOK)
        rom.expect_bytes(MOVE_SFX_HELPER_ROM, DEAD_SELECTOR_EPILOGUE)

        mapper = build_selection_mapper()

        rom.write_u32(A_ROUTE_JAL_ROM, jal(DEBUG_MENU_VA))
        rom.write_u32(WRAP_LAST_ROM, PATCHED_WRAP_LAST)
        rom.write_u32(COUNT_ROM, PATCHED_COUNT)
        rom.write_bytes(MENU_TABLE_ROM, words_blob(SAFE_MENU_POINTERS))

        rom.write_u32(SELECTION_LOAD_ROM, jal(MAPPER_VA))
        rom.write_u32(SELECTION_LOAD_ROM + 4, NOP)
        rom.write_bytes(MAPPER_ROM, mapper)

        rom.write_bytes(
            SELECTOR_CURSOR_PALETTE_ROM,
            EXPECTED_TITLE_CURSOR_PALETTE,
        )
        rom.write_bytes(MOVE_SFX_HELPER_ROM, MOVE_SFX_HELPER)
        rom.write_u32(MOVE_SFX_HOOK_ROM, jal(MOVE_SFX_HELPER_VA))

        return (
            "compact selector: Temple, Wind, Water, Earth, Prison, Fire, Bridge, Fortress",
            "verified A-button title-menu route enabled",
            "selector 0x352..0x35A keeps file 0x5F/slot 0x1C2 and uses the title cursor blue palette",
            "valid Up/Down edges use title MOVE descriptor 0x1FC; new A edges use title CONFIRM 0x1FD",
            "blue cursor and MOVE are runtime-confirmed; v02 input-loop CONFIRM remains runtime pending",
            "normal stage-loader path left vanilla for cinematics and stage progression",
        )
