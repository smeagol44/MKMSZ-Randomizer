"""Native Inventory control legend for four-box navigation.

This patch promotes the Runtime-confirmed legend v01 presentation without
changing Inventory navigation or storage behavior. It replaces only the stock
legend text-emission block, preserves the native panel/background, and appends
a small helper after the production Inventory-menu switch module in the same
relocated file-0x1A transport.
"""

from __future__ import annotations

from ..data.addresses import (
    EXPANSION_POOL_END_EXCLUSIVE,
    EXPANSION_POOL_START,
    FILE_TABLE_ENTRY_SIZE,
    FILE_TABLE_ROM,
)
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    address_words,
    andi,
    jal,
    jr,
    lui,
    lw,
    ori,
    sb,
    sw,
    words_blob,
)
from ..resource_materialization import GLOBAL_OUTPUT_SIZE
from ..rom import RomImage
from .base import PatchContext
from .inventory_boxes import STATE_VA
from .inventory_menu_switch import (
    EXPANSION_FILE_ID,
    INVENTORY_MENU_SWITCH_MODULE,
    MODULE_K0 as SWITCH_MODULE_K0,
    TRANSPORT_END_ROM,
    TRANSPORT_ROM,
)
from .temple_special_check import EXPANSION_FILE_ENTRY_ROM

NOP = 0

LEGEND_HOOK_ROM = 0x0007372C
LEGEND_RESUME_VA = 0x80072BF0
TEXT_RENDER_VA = 0x80073E74
TEXT_DESCRIPTOR_VA = 0x800B1E20

LEGEND_EXPECTED_WORDS = (
    0x3C04800B, 0x2484E914, 0x24050014, 0x240600A9,
    0x24070002, 0x3C10800B, 0x26101E20, 0x0C01CF9D,
    0xAFB00010, 0x3C04800B, 0x2484E918, 0x24050014,
    0x240600BE, 0x24070002, 0x0C01CF9D, 0xAFB00010,
    0x3C04800B, 0x2484E91C, 0x24050014, 0x240600D3,
    0x24070002, 0x0C01CF9D, 0xAFB00010, 0x3C04800B,
    0x2484E920, 0x24050022, 0x240600A9, 0x24070002,
    0x0C01CF9D, 0xAFB00010, 0x3C04800B, 0x2484E928,
    0x24050022, 0x240600BE, 0x24070002, 0x0C01CF9D,
    0xAFB00010, 0x16200005, 0xAFB00010, 0x3C04800B,
    0x2484E92C, 0x0801CAF9, 0x24050022, 0x3C04800B,
    0x2484E938, 0x24050022, 0x240600D3, 0x0C01CF9D,
    0x24070002,
)
EXPECTED_LEGEND_BLOCK = words_blob(LEGEND_EXPECTED_WORDS)
if len(EXPECTED_LEGEND_BLOCK) != 0xC4:
    raise AssertionError("stock Inventory legend block size drifted")

SWITCH_RUNTIME_END_K0 = SWITCH_MODULE_K0 + len(INVENTORY_MENU_SWITCH_MODULE)
LEGEND_K0 = (SWITCH_RUNTIME_END_K0 + 0xF) & ~0xF
LEGEND_K1 = LEGEND_K0 | 0x20000000
LEGEND_PAD = LEGEND_K0 - SWITCH_RUNTIME_END_K0
LEGEND_CEILING = 0x300

SWITCH_TRANSPORT_END_ROM = (
    TRANSPORT_ROM
    + (SWITCH_MODULE_K0 - EXPANSION_POOL_START)
    + len(INVENTORY_MENU_SWITCH_MODULE)
)
LEGEND_ROM = (SWITCH_TRANSPORT_END_ROM + 0xF) & ~0xF
if LEGEND_ROM - SWITCH_TRANSPORT_END_ROM != LEGEND_PAD:
    raise AssertionError("legend runtime/ROM alignment drifted")


def _call_abs(emitter: Emitter, target: int) -> None:
    emitter.emit(*address_words("t9", target), jal("t9"), NOP)


def _jump_abs(emitter: Emitter, target: int) -> None:
    emitter.emit(*address_words("t9", target), jr("t9"), NOP)


def _emit_draw_call(
    emitter: Emitter,
    draw_helper_k1: int,
    string_va: int | None,
    y: int,
    tracking: int,
    *,
    stack_box: bool = False,
) -> None:
    if stack_box:
        emitter.emit(addiu("a0", "sp", 0x20))
    else:
        if string_va is None:
            raise AssertionError("legend string pointer is required")
        emitter.emit(*address_words("a0", string_va))
    emitter.emit(
        addiu("a1", "zero", 20),
        addiu("a2", "zero", y),
        addiu("a3", "zero", tracking),
        jal(draw_helper_k1),
        NOP,
    )


def _build_main(draw_helper_k1: int, strings: dict[str, int]) -> bytes:
    e = Emitter()
    e.emit(addiu("sp", "sp", -0x40), sw("ra", 0x34, "sp"))

    e.emit(lui("t0", 0x424F), ori("t0", "t0", 0x5820), sw("t0", 0x20, "sp"))
    e.emit(lui("t0", 0x3120), ori("t0", "t0", 0x4F46), sw("t0", 0x24, "sp"))
    e.emit(lui("t0", 0x2034), sw("t0", 0x28, "sp"))
    e.emit(
        lui("t0", 0x800A),
        lw("t1", STATE_VA - 0x800A0000, "t0"),
        andi("t1", "t1", 3),
        addiu("t1", "t1", ord("1")),
        sb("t1", 0x24, "sp"),
    )
    _emit_draw_call(e, draw_helper_k1, None, 169, 2, stack_box=True)

    e.bne("s1", "zero", "powers")
    e.emit(NOP)

    _emit_draw_call(e, draw_helper_k1, strings["left_right_box"], 180, 0)
    _emit_draw_call(e, draw_helper_k1, strings["a_use"], 191, 2)
    _emit_draw_call(e, draw_helper_k1, strings["b_combine"], 202, 2)
    _emit_draw_call(e, draw_helper_k1, strings["r_powers"], 213, 2)
    e.beq("zero", "zero", "done")
    e.emit(NOP)

    e.label("powers")
    _emit_draw_call(e, draw_helper_k1, strings["lr_power"], 180, 2)
    _emit_draw_call(e, draw_helper_k1, strings["r_items"], 213, 2)

    e.label("done")
    e.emit(lw("ra", 0x34, "sp"), addiu("sp", "sp", 0x40))
    _jump_abs(e, LEGEND_RESUME_VA)
    return e.finish()


def _build_draw_helper() -> bytes:
    e = Emitter()
    e.emit(addiu("sp", "sp", -0x20), sw("ra", 0x18, "sp"))
    e.emit(*address_words("t0", TEXT_DESCRIPTOR_VA), sw("t0", 0x10, "sp"))
    _call_abs(e, TEXT_RENDER_VA)
    e.emit(lw("ra", 0x18, "sp"), addiu("sp", "sp", 0x20), jr("ra"), NOP)
    return e.finish()


def build_inventory_legend_module() -> bytes:
    dummy = {
        "left_right_box": LEGEND_K0 + 0x250,
        "a_use": LEGEND_K0 + 0x260,
        "b_combine": LEGEND_K0 + 0x270,
        "r_powers": LEGEND_K0 + 0x280,
        "lr_power": LEGEND_K0 + 0x290,
        "r_items": LEGEND_K0 + 0x2A0,
    }
    provisional = _build_main(LEGEND_K1 + 0x200, dummy)
    draw_k1 = LEGEND_K1 + len(provisional)
    draw = _build_draw_helper()
    data_k0 = LEGEND_K0 + len(provisional) + len(draw)

    literals = (
        ("left_right_box", b"LEFT-RIGHT BOX\0"),
        ("a_use", b"A USE\0"),
        ("b_combine", b"B COMBINE\0"),
        ("r_powers", b"R POWERS\0"),
        ("lr_power", b"L-R POWER\0"),
        ("r_items", b"R ITEMS\0"),
    )
    addresses: dict[str, int] = {}
    data = bytearray()
    for name, raw in literals:
        addresses[name] = data_k0 + len(data)
        data.extend(raw)

    main = _build_main(draw_k1, addresses)
    if len(main) != len(provisional):
        raise AssertionError("legend main size changed between address passes")
    module = main + draw + bytes(data)
    if len(module) > LEGEND_CEILING:
        raise AssertionError("Inventory legend module exceeds its 0x300-byte ceiling")
    if LEGEND_K0 + len(module) > EXPANSION_POOL_END_EXCLUSIVE:
        raise AssertionError("Inventory legend module exceeds reserved RDRAM parent")
    if LEGEND_ROM + len(module) > TRANSPORT_END_ROM:
        raise AssertionError("Inventory legend module exceeds file-0x1A transport")
    return module


INVENTORY_LEGEND_MODULE = build_inventory_legend_module()


class InventoryLegendPatch:
    """Install the Runtime-confirmed dynamic four-box Inventory legend."""

    name = "inventory-four-box-legend"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        if len(rom.data) != GLOBAL_OUTPUT_SIZE:
            raise PatchError("Inventory legend requires the normal 32 MiB generated output")
        rom.expect_bytes(LEGEND_HOOK_ROM, EXPECTED_LEGEND_BLOCK)

        entry = FILE_TABLE_ROM + EXPANSION_FILE_ID * FILE_TABLE_ENTRY_SIZE
        rom.expect_u32(entry + 0, TRANSPORT_ROM)
        rom.expect_u32(entry + 4, SWITCH_TRANSPORT_END_ROM)
        rom.expect_u32(entry + 8, 0)

        capacity_end = LEGEND_ROM + LEGEND_CEILING
        if bytes(rom.data[SWITCH_TRANSPORT_END_ROM:capacity_end]) != (
            b"\xFF" * (capacity_end - SWITCH_TRANSPORT_END_ROM)
        ):
            raise PatchError("Inventory legend append capacity is not unassigned")

        prefix = bytes(rom.data[TRANSPORT_ROM:SWITCH_TRANSPORT_END_ROM])
        rom.write_bytes(SWITCH_TRANSPORT_END_ROM, b"\x00" * LEGEND_PAD)
        rom.write_bytes(LEGEND_ROM, INVENTORY_LEGEND_MODULE)
        payload_end = LEGEND_ROM + len(INVENTORY_LEGEND_MODULE)
        rom.write_u32(entry + 4, payload_end)

        trampoline = words_blob([*address_words("t9", LEGEND_K1), jr("t9"), NOP])
        if len(trampoline) != 16:
            raise AssertionError("Inventory legend trampoline must be exactly 16 bytes")
        rom.write_bytes(LEGEND_HOOK_ROM, trampoline)
        rom.write_bytes(
            LEGEND_HOOK_ROM + 16,
            b"\x00" * (len(EXPECTED_LEGEND_BLOCK) - 16),
        )

        if bytes(rom.data[TRANSPORT_ROM:SWITCH_TRANSPORT_END_ROM]) != prefix:
            raise AssertionError("Inventory legend changed the promoted switch payload")

        return (
            "Inventory legend shows dynamic BOX n OF 4 and Left/Right box controls in Items mode",
            "Power Ups keep native horizontal navigation and show L-R POWER / R ITEMS",
            "stock six-tile legend panel is preserved; only native text emissions are replaced",
            (
                f"legend module K0 0x{LEGEND_K0:08X}, size 0x{len(INVENTORY_LEGEND_MODULE):X}; "
                f"file 0x1A ends at generated ROM 0x{payload_end:08X}"
            ),
        )
