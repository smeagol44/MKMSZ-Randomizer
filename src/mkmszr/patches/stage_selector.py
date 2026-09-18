"""Runtime-confirmed compact safe native stage selector."""

from ..errors import PatchError
from ..mips import jal, jump, words_blob
from ..rom import RomImage
from .base import PatchContext

DEBUG_MENU_VA = 0x8000D0B8
STAGE_LOADER_CONTINUE_VA = 0x80016088

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

STAGE_LOADER_PROLOGUE_ROM = 0x00016C80
EXPECTED_STAGE_LOADER_PROLOGUE = bytes.fromhex("27BDFFE8 00002021")

GATE_ROM = 0x0009A6C8
GATE_VA = 0x80099AC8
MAPPER_ROM = 0x0009A700
MAPPER_VA = 0x80099B00
STAGE_CODE_CAVE_END = 0x0009A758

NOP = 0


def build_loader_gate() -> bytes:
    return words_blob(
        [
            0x3C08800A,
            0x8D08A910,
            0x05010003,
            NOP,
            jump(DEBUG_MENU_VA),
            NOP,
            0x27BDFFE8,
            jump(STAGE_LOADER_CONTINUE_VA),
            0x00002021,
        ]
    )


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


class SafeStageSelectorPatch:
    """Install the previously runtime-confirmed compact 8-stage selector."""

    name = "safe-stage-selector"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        rom.expect_u32(A_ROUTE_JAL_ROM, EXPECTED_A_ROUTE_JAL)
        rom.expect_u32(WRAP_LAST_ROM, EXPECTED_WRAP_LAST)
        rom.expect_u32(COUNT_ROM, EXPECTED_COUNT)
        rom.expect_bytes(MENU_TABLE_ROM, words_blob(ORIGINAL_MENU_POINTERS))
        rom.expect_bytes(SELECTION_LOAD_ROM, EXPECTED_SELECTION_LOAD)
        rom.expect_bytes(STAGE_LOADER_PROLOGUE_ROM, EXPECTED_STAGE_LOADER_PROLOGUE)
        rom.expect_bytes(
            GATE_ROM,
            bytes(STAGE_CODE_CAVE_END - GATE_ROM),
        )

        gate = build_loader_gate()
        mapper = build_selection_mapper()

        rom.write_u32(A_ROUTE_JAL_ROM, jal(DEBUG_MENU_VA))
        rom.write_u32(WRAP_LAST_ROM, PATCHED_WRAP_LAST)
        rom.write_u32(COUNT_ROM, PATCHED_COUNT)
        rom.write_bytes(MENU_TABLE_ROM, words_blob(SAFE_MENU_POINTERS))

        rom.write_u32(STAGE_LOADER_PROLOGUE_ROM, jump(GATE_VA))
        rom.write_u32(STAGE_LOADER_PROLOGUE_ROM + 4, NOP)
        rom.write_bytes(GATE_ROM, gate)

        rom.write_u32(SELECTION_LOAD_ROM, jal(MAPPER_VA))
        rom.write_u32(SELECTION_LOAD_ROM + 4, NOP)
        rom.write_bytes(MAPPER_ROM, mapper)

        return (
            "compact selector: Temple, Wind, Water, Earth, Prison, Fire, Bridge, Fortress",
            "verified A-button title-menu route enabled",
        )
