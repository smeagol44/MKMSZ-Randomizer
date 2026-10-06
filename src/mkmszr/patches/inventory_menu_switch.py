"""In-Inventory navigation for the production four-box inventory.

The native Inventory keeps the ten-word LIVE window.  This patch lets Items
mode replace that window with the previous/next authoritative backing box while
the Inventory process remains alive.  It reuses the production filtered-save
and stage-masked load helpers, resets native selection/Combine state, and lets
the normal per-frame renderer rebuild presentation.
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
    addu,
    and_,
    andi,
    jalr,
    jr,
    lhu,
    lui,
    lw,
    ori,
    sh,
    sll,
    srl,
    subu,
    sw,
    words_blob,
)
from ..resource_materialization import GLOBAL_OUTPUT_SIZE
from ..rom import RomImage
from .base import PatchContext
from .inventory_boxes import LEFT_MASK, LOAD_MASK_WRAPPER_UNCACHED_VA, RIGHT_MASK, STATE_VA
from .inventory_hud import HUD_CODE_END_K0, HUD_CODE_END_ROM
from .temple_special_check import EXPANSION_FILE_ENTRY_ROM
from .toasty_constants import SHARED_EXPANSION_ROM

NOP = 0

# Native Inventory loop seam, before highlight and item-action processing.
INVENTORY_LOOP_HOOK_ROM = 0x00074324
INVENTORY_LOOP_HOOK_VA = 0x80073724
EXPECTED_INVENTORY_LOOP_HOOK = bytes.fromhex(
    "1640000F 00000000 0C01D06D 00000000"
)
INVENTORY_ITEMS_RESUME_VA = 0x80073734
INVENTORY_POWERS_RESUME_VA = 0x80073764
INVENTORY_COUNT_VA = 0x800741B4
INVENTORY_FIRST_OCCUPIED_VA = 0x80075320
INPUT_COUNTDOWN_VA = 0x800BF30A

# Stock R-toggle path rejects Items mode when the active LIVE count is zero.
# Removing only this rejection keeps the preceding positive-Power-count check,
# so an empty box can still enter and return from Power Ups.
EMPTY_BOX_R_GATE_ROM = 0x00074748
EMPTY_BOX_R_GATE_VA = 0x80073B48
EXPECTED_EMPTY_BOX_R_GATE = 0x18400005

# Existing production four-box helpers.
SAVE_FILTERED_VA = 0x8007AD4C
HORIZONTAL_MASK = RIGHT_MASK | LEFT_MASK

# The production Inventory HUD fills file 0x1A exactly through 0x801B2DF0.
# The 16 KiB arena reservation ends at 0x801B3420, leaving this bounded tail.
MODULE_K0 = HUD_CODE_END_K0
MODULE_K1 = MODULE_K0 | 0x20000000
MODULE_CAPACITY = EXPANSION_POOL_END_EXCLUSIVE - MODULE_K0

# Generated-output transport.  The original source file cannot grow in place:
# fixed Toasty audio begins at HUD_CODE_END_ROM.  Copy the final file-0x1A
# prefix here, append this module, then repoint the existing file-table entry.
TRANSPORT_ROM = 0x01816000
TRANSPORT_CAPACITY = 0x3C00
TRANSPORT_END_ROM = TRANSPORT_ROM + TRANSPORT_CAPACITY
EXPANSION_FILE_ID = 0x1A
EXPECTED_FILE_START = SHARED_EXPANSION_ROM
EXPECTED_FILE_END = HUD_CODE_END_ROM
EXPECTED_FILE_FLAG = 0


def _move(rd: str, rs: str) -> int:
    return addu(rd, rs, "zero")


def _call_abs(emitter: Emitter, target: int) -> None:
    emitter.emit(*address_words("t9", target), jalr("t9"), NOP)


def _jump_abs(emitter: Emitter, target: int) -> None:
    emitter.emit(*address_words("t9", target), jr("t9"), NOP)


def build_inventory_menu_switch_module() -> bytes:
    """Build the Runtime-confirmed v03 Items-mode four-box switch helper."""

    e = Emitter()

    # Power-Ups mode keeps native horizontal strip navigation unchanged.
    e.bne("s2", "zero", "powers")
    e.emit(NOP)

    # Items mode accepts only a pure Left or Right semantic word.
    e.emit(lhu("t0", 0, "s4"), ori("t1", "zero", RIGHT_MASK))
    e.beq("t0", "t1", "direction_ok")
    e.emit(NOP)
    e.emit(ori("t1", "zero", LEFT_MASK))
    e.bne("t0", "t1", "no_switch")
    e.emit(NOP)

    # One switch per horizontal release/press cycle.
    e.label("direction_ok")
    e.emit(andi("t1", "s7", HORIZONTAL_MASK))
    e.bne("t1", "zero", "no_switch")
    e.emit(NOP)

    # Private helper frame.  Keep the native Inventory frame address and exact
    # direction across the existing save/load helper calls.
    e.emit(
        _move("t8", "sp"),
        addiu("sp", "sp", -0x30),
        sw("t8", 0x20, "sp"),
        sw("ra", 0x24, "sp"),
        sw("t0", 0x28, "sp"),
    )

    # Commit LIVE to the current authoritative backing box, preserving hidden
    # foreign credentials through the established filtered-save path.
    _call_abs(e, SAVE_FILTERED_VA)

    # Replace only active-box bits 0..1.  Right = +1, Left = -1 modulo four;
    # preserve the gameplay latch and all durable GAME SETTINGS bits.
    e.emit(
        lui("t0", 0x800A),
        lw("t1", STATE_VA - 0x800A0000, "t0"),
        andi("t2", "t1", 3),
        lw("t7", 0x28, "sp"),
        srl("t4", "t7", 15),
        sll("t4", "t4", 1),
        addiu("t2", "t2", 1),
        subu("t2", "t2", "t4"),
        andi("t2", "t2", 3),
        addiu("t3", "zero", -4),
        and_("t1", "t1", "t3"),
        addu("t1", "t1", "t2"),
        sw("t1", STATE_VA - 0x800A0000, "t0"),
    )

    # Reconstruct LIVE from the selected backing box with current-stage
    # credential masking.
    _call_abs(e, LOAD_MASK_WRAPPER_UNCACHED_VA)

    # Cancel pending Combine, stay in Items mode, and clear native presentation
    # countdown so the new selection can render immediately.
    e.emit(
        addiu("s0", "zero", -1),
        _move("s2", "zero"),
        lui("t0", 0x800C),
        sh("zero", INPUT_COUNTDOWN_VA - 0x800C0000, "t0"),
        lw("t8", 0x20, "sp"),
        sw("zero", 0x10, "t8"),
        sw("zero", 0x14, "t8"),
        sw("zero", 0x18, "t8"),
        sw("zero", 0x1C, "t8"),
    )

    # Count the new LIVE window.  Nonempty boxes select the first occupied
    # physical slot at visible row zero; empty boxes keep harmless zero locals.
    _call_abs(e, INVENTORY_COUNT_VA)
    e.emit(sw("v0", 0x1C, "sp"))
    e.beq("v0", "zero", "selection_done")
    e.emit(NOP)
    e.emit(lw("t8", 0x20, "sp"), addiu("a0", "t8", 0x10))
    _call_abs(e, INVENTORY_FIRST_OCCUPIED_VA)
    e.emit(lw("t8", 0x20, "sp"), lw("t0", 0x10, "t8"), sw("t0", 0x18, "t8"))

    # Suppress further native item actions on the switching frame by making
    # this direction the previous semantic word, then resume the stock Items
    # loop with the new count already in v0.
    e.label("selection_done")
    e.emit(
        lw("t0", 0x28, "sp"),
        _move("s7", "t0"),
        lw("v0", 0x1C, "sp"),
        lw("ra", 0x24, "sp"),
        lw("t8", 0x20, "sp"),
        _move("sp", "t8"),
    )
    _jump_abs(e, INVENTORY_ITEMS_RESUME_VA)

    # No-switch replay for Items mode: reproduce the displaced count call.
    e.label("no_switch")
    _call_abs(e, INVENTORY_COUNT_VA)
    _jump_abs(e, INVENTORY_ITEMS_RESUME_VA)

    # Power-Ups mode resumes at the stock branch destination.
    e.label("powers")
    _jump_abs(e, INVENTORY_POWERS_RESUME_VA)

    return e.finish()


INVENTORY_MENU_SWITCH_MODULE = build_inventory_menu_switch_module()
if len(INVENTORY_MENU_SWITCH_MODULE) > MODULE_CAPACITY:
    raise AssertionError("Inventory menu switch module exceeds reserved RDRAM tail")


def _guard_generated_output(rom: RomImage, start: int, end: int) -> None:
    if len(rom.data) != GLOBAL_OUTPUT_SIZE:
        raise PatchError("Inventory menu switching requires the normal 32 MiB generated output")
    if not (0 <= start < end <= len(rom.data)):
        raise PatchError("Inventory menu switch transport is outside generated output")
    if bytes(rom.data[start:end]) != b"\xFF" * (end - start):
        raise PatchError(
            f"Inventory menu switch transport 0x{start:08X}..0x{end - 1:08X} is not unassigned"
        )


def _guard_transport_overlap(rom: RomImage, payload_end: int) -> None:
    for file_id in range(0xAC):
        if file_id == EXPANSION_FILE_ID:
            continue
        entry = FILE_TABLE_ROM + file_id * FILE_TABLE_ENTRY_SIZE
        start = rom.read_u32(entry)
        end = rom.read_u32(entry + 4)
        if start and end and end > start and not (end <= TRANSPORT_ROM or start >= payload_end):
            raise PatchError(
                f"Inventory menu switch transport overlaps file 0x{file_id:02X} "
                f"at 0x{start:08X}..0x{end - 1:08X}"
            )


class InventoryMenuSwitchPatch:
    """Promote Runtime-confirmed Left/Right four-box navigation inside Inventory."""

    name = "inventory-menu-box-switch"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        rom.expect_bytes(INVENTORY_LOOP_HOOK_ROM, EXPECTED_INVENTORY_LOOP_HOOK)
        rom.expect_u32(EMPTY_BOX_R_GATE_ROM, EXPECTED_EMPTY_BOX_R_GATE)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 0, EXPECTED_FILE_START)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 4, EXPECTED_FILE_END)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 8, EXPECTED_FILE_FLAG)

        old_payload = bytes(rom.data[EXPECTED_FILE_START:EXPECTED_FILE_END])
        module_k0 = EXPANSION_POOL_START + len(old_payload)
        if module_k0 != MODULE_K0:
            raise PatchError(
                f"Inventory menu switch module base drifted: expected 0x{MODULE_K0:08X}, "
                f"got 0x{module_k0:08X}"
            )

        new_payload = old_payload + INVENTORY_MENU_SWITCH_MODULE
        if len(new_payload) > TRANSPORT_CAPACITY:
            raise PatchError(
                f"Inventory menu switch file 0x1A payload 0x{len(new_payload):X} "
                f"exceeds transport capacity 0x{TRANSPORT_CAPACITY:X}"
            )
        payload_end = TRANSPORT_ROM + len(new_payload)
        _guard_generated_output(rom, TRANSPORT_ROM, TRANSPORT_END_ROM)
        _guard_transport_overlap(rom, payload_end)

        rom.write_bytes(TRANSPORT_ROM, new_payload)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 0, TRANSPORT_ROM)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, payload_end)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)

        trampoline = words_blob([*address_words("t9", MODULE_K1), jr("t9"), NOP])
        if len(trampoline) != len(EXPECTED_INVENTORY_LOOP_HOOK):
            raise AssertionError("Inventory menu switch trampoline must replace exactly 16 bytes")
        rom.write_bytes(INVENTORY_LOOP_HOOK_ROM, trampoline)

        # Allow empty Items boxes to enter/return from Power Ups.  The stock
        # preceding positive-Power-count requirement remains intact.
        rom.write_u32(EMPTY_BOX_R_GATE_ROM, NOP)

        if bytes(rom.data[TRANSPORT_ROM : TRANSPORT_ROM + len(old_payload)]) != old_payload:
            raise AssertionError(
                "Inventory menu switch transport changed production file 0x1A prefix"
            )

        return (
            "Items-mode Left/Right cycles all four authoritative boxes without closing Inventory",
            "switch commits through filtered SAVE and reconstructs LIVE through stage masking",
            (
                "switch cancels Combine, selects first occupied row, "
                "and suppresses same-frame item actions"
            ),
            "Power Ups keep stock Left/Right; empty Items boxes retain R toggle/recovery",
            (
                f"file 0x1A relocated to generated ROM 0x{TRANSPORT_ROM:08X}.."
                f"0x{payload_end - 1:08X}; "
                f"switch module K0 0x{MODULE_K0:08X}, size 0x{len(INVENTORY_MENU_SWITCH_MODULE):X}"
            ),
        )
