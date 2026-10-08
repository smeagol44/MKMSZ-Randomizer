"""Runtime-confirmed rich Inventory materialization/stability composition.

This patch promotes the bounded Fortress proof that kept the accepted rich
Inventory renderer intact while materializing only mutable status/table data per
Inventory session.  It composes three already-tested prerequisites after the
normal HUD -> menu-switch -> legend chain:

* Fortress preloads the 0x1200 HUD data allocation before the resident rewind
  anchor, preventing the reliable post-Kia-door cold allocation hang.
* Powers mode with an empty LIVE box accepts a fresh pure Left/Right press and
  tail-enters the already Runtime-confirmed four-box switch transaction.
* Requirement/check strings and the STG CHECKS KEYS rows are prepared only at
  Inventory-open/session boundaries, then redrawn through the exact existing
  native text renderer.  Item rows, paper title, fonts, palettes, portraits,
  spacing, and alignment remain the accepted production implementation.

The accepted proof intentionally did not replace the native glyph parser or
renderer.  Two earlier prepared-glyph experiments were rejected.
"""

from __future__ import annotations

import hashlib

from ..data.addresses import EXPANSION_POOL_END_EXCLUSIVE, EXPANSION_POOL_START
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    addu,
    andi,
    jal,
    jalr,
    jr,
    lhu,
    lui,
    lw,
    ori,
    sltiu,
    sw,
    words_blob,
)
from ..resource_materialization import GLOBAL_OUTPUT_SIZE
from ..rom import RomImage
from .base import PatchContext
from .inventory_hud import (
    ENSURE_DATA_VA,
    HUD_DATA_ROM,
    HUD_STATE_DATA_PTR_K1,
    TEXT_DRAW_VA,
)
from .inventory_legend import INVENTORY_LEGEND_MODULE, LEGEND_ROM
from .inventory_menu_switch import (
    EXPANSION_FILE_ENTRY_ROM,
    INVENTORY_COUNT_VA,
    INVENTORY_LOOP_HOOK_ROM,
    TRANSPORT_END_ROM,
    TRANSPORT_ROM,
)
from .inventory_menu_switch import (
    MODULE_K1 as SWITCH_MODULE_K1,
)
from .native_payload import kseg1_alias

NOP = 0

# Accepted final transport layout.  Keep this exact until a later independently
# runtime-confirmed composition supersedes it.
LEGEND_PAYLOAD_END_ROM = LEGEND_ROM + len(INVENTORY_LEGEND_MODULE)
PRELOAD_ROM = (LEGEND_PAYLOAD_END_ROM + 0xF) & ~0xF
PRELOAD_SIZE = 0x38
EMPTY_POWERS_ROM = PRELOAD_ROM + PRELOAD_SIZE
EMPTY_POWERS_SIZE = 0xDC
OPEN_ROM = (EMPTY_POWERS_ROM + EMPTY_POWERS_SIZE + 0xF) & ~0xF
OPEN_SIZE = 0x3C
REQUIREMENT_ROM = (OPEN_ROM + OPEN_SIZE + 0xF) & ~0xF
REQUIREMENT_SIZE = 0x48
CHECK_ROM = (REQUIREMENT_ROM + REQUIREMENT_SIZE + 0xF) & ~0xF
CHECK_SIZE = 0x50
TABLE_ROM = CHECK_ROM + CHECK_SIZE
TABLE_SIZE = 0xCC
MATERIALIZED_PAYLOAD_END_ROM = TABLE_ROM + TABLE_SIZE

PRELOAD_K0 = EXPANSION_POOL_START + (PRELOAD_ROM - TRANSPORT_ROM)
PRELOAD_K1 = kseg1_alias(PRELOAD_K0)
EMPTY_POWERS_K0 = EXPANSION_POOL_START + (EMPTY_POWERS_ROM - TRANSPORT_ROM)
EMPTY_POWERS_K1 = kseg1_alias(EMPTY_POWERS_K0)
OPEN_K0 = EXPANSION_POOL_START + (OPEN_ROM - TRANSPORT_ROM)
OPEN_K1 = kseg1_alias(OPEN_K0)
REQUIREMENT_K0 = EXPANSION_POOL_START + (REQUIREMENT_ROM - TRANSPORT_ROM)
REQUIREMENT_K1 = kseg1_alias(REQUIREMENT_K0)
CHECK_K0 = EXPANSION_POOL_START + (CHECK_ROM - TRANSPORT_ROM)
CHECK_K1 = kseg1_alias(CHECK_K0)
TABLE_K0 = EXPANSION_POOL_START + (TABLE_ROM - TRANSPORT_ROM)
TABLE_K1 = kseg1_alias(TABLE_K0)
MATERIALIZED_RUNTIME_END_K0 = EXPANSION_POOL_START + (
    MATERIALIZED_PAYLOAD_END_ROM - TRANSPORT_ROM
)

# Exact accepted addresses from the final bounded proof.
if PRELOAD_ROM != 0x018198D0 or PRELOAD_K0 != 0x801B30F0:
    raise AssertionError("Inventory preload placement drifted")
if EMPTY_POWERS_ROM != 0x01819908 or EMPTY_POWERS_K0 != 0x801B3128:
    raise AssertionError("empty-Powers wrapper placement drifted")
if OPEN_ROM != 0x018199F0 or OPEN_K0 != 0x801B3210:
    raise AssertionError("Inventory-open wrapper placement drifted")
if REQUIREMENT_ROM != 0x01819A30 or REQUIREMENT_K0 != 0x801B3250:
    raise AssertionError("requirement wrapper placement drifted")
if CHECK_ROM != 0x01819A80 or CHECK_K0 != 0x801B32A0:
    raise AssertionError("check wrapper placement drifted")
if TABLE_ROM != 0x01819AD0 or TABLE_K0 != 0x801B32F0:
    raise AssertionError("table wrapper placement drifted")
if MATERIALIZED_PAYLOAD_END_ROM != 0x01819B9C:
    raise AssertionError("materialized Inventory payload end drifted")
if MATERIALIZED_PAYLOAD_END_ROM > TRANSPORT_END_ROM:
    raise AssertionError("materialized Inventory payload exceeds transport capacity")
if MATERIALIZED_RUNTIME_END_K0 > EXPANSION_POOL_END_EXCLUSIVE:
    raise AssertionError("materialized Inventory payload exceeds reserved arena parent")

# Stock/core seams.
FORTRESS_PRELOAD_HOOK_ROM = 0x0001315C
FORTRESS_PRELOAD_GETTER_VA = 0x80066410
FORTRESS_REWIND_ANCHOR_VA = 0x802E822C
EXPECTED_FORTRESS_PRELOAD_HOOK = words_blob(
    [
        jal(FORTRESS_PRELOAD_GETTER_VA),
        NOP,
        0x3C01802F,  # lui at,0x802F
        0xAC22822C,  # sw v0,-0x7DD4(at) -> 0x802E822C
    ]
)

INVENTORY_OPEN_HOOK_ROM = 0x00074310
INVENTORY_OPEN_RESUME_VA = 0x80073720
EXPECTED_INVENTORY_OPEN_HOOK = words_blob(
    [
        lui("s4", 0x800C),
        addiu("s4", "s4", 0xF2EE),
        ori("fp", "zero", 0x8000),
        lui("s5", 0x800A),
    ]
)

# Existing HUD helper seams inside the relocated final file-0x1A prefix.
TABLE_COMPUTE_ROM = 0x018192D0
TABLE_COMPUTE_RESUME_K1 = 0xA01B2B00
EXPECTED_TABLE_COMPUTE = words_blob(
    [
        lui("s0", 0x800A),
        addiu("s0", "s0", 0x6048),
        addiu("s1", "zero", 40),
        addu("s2", "zero", "zero"),
    ]
)

REQUIREMENT_GATE_ROM = 0x01819474
REQUIREMENT_CONTINUE_K1 = 0xA01B2CA4
REQUIREMENT_DRAW_K1 = 0xA01B2CC0
EXPECTED_REQUIREMENT_GATE = words_blob(
    [
        lui("t0", 0x800C),
        addiu("t0", "t0", 0x1248),
        lw("t1", 0, "t0"),
        sltiu("t2", "t1", 10),
    ]
)

CHECK_GATE_ROM = 0x018194C4
CHECK_CONTINUE_K1 = 0xA01B2CF4
CHECK_DRAW_K1 = 0xA01B2D5C
VANILLA_CHECK_GATE_ROM = 0x018194A0
VANILLA_CHECK_CONTINUE_K1 = 0xA01B2CD0
VANILLA_CHECK_DRAW_K1 = 0xA01B2D38
EXPECTED_CHECK_GATE = words_blob(
    [
        lui("t0", 0xA01B),
        addiu("t0", "t0", 0xF7D0),
        addiu("t1", "t0", 0x20),
        addiu("t2", "zero", 8),
    ]
)

# Existing 0x1200 HUD data uses exactly 0x1198 bytes.  These two words are the
# accepted per-session validity state; they remain derived display state only.
STATUS_FLAG_OFF = 0x1198
TABLE_FLAG_OFF = 0x119C
STATUS_VALID = 2
REQUIREMENT_TEXT_OFF = 0x1168
CHECK_TEXT_OFF = 0x1180
TABLE_HEADER_OFF = 0x1058
TABLE_ROWS_OFF = 0x10E8

PAPER_FONT_VA = 0x800B1E44

# Accepted helper hashes are ROM-free regression identities for the emitted
# code, not copied game bytes.
ACCEPTED_HELPER_SHA256 = {
    "preload": "2259ee525187ae1a13ee5c1eb9ebd83889791e444cdb92b2e0d8f36ab6db77a9",
    "empty_powers": "bb30597a08a3d46c7eb6315711227266035225dd9ab228eb602646fb2a81254f",
    "open": "92e2bc344e96950cef7d2f6ec6700733c9bd6984881d186e54b52a8600be4a62",
    "requirement": "3ecfa3310e6768aa430a6b89e431a84a5a0fa0b0bdb247a0f2c7f4b4e01a82be",
    "check": "4b99c7d39d0e53d1cedfc98cb0cf442b6bb2a3a6a9e8bdeeecd625eddffa805f",
    "table": "77d65f456f73d3e43ecb6f5e7cd10f286786829a3c8870ddf58c7383762fbcfc",
}


def _ori_address_words(reg: str, address: int) -> tuple[int, int]:
    """Exact LUI+ORI form used by the accepted disposable proof."""

    return lui(reg, (address >> 16) & 0xFFFF), ori(reg, reg, address & 0xFFFF)


def _jump_abs(emitter: Emitter, target: int) -> None:
    emitter.emit(*_ori_address_words("t9", target), jr("t9"), NOP)


def _call_abs(emitter: Emitter, target: int) -> None:
    emitter.emit(*_ori_address_words("t9", target), jalr("t9"), NOP)


def _jump_trampoline(target: int) -> bytes:
    return words_blob([*_ori_address_words("t9", target), jr("t9"), NOP])


def _call_trampoline_addiu(target: int) -> bytes:
    # The accepted Fortress hook used the repository's signed-ADDIU address
    # construction rather than the ORI form used by the later proof wrappers.
    return words_blob(
        [
            lui("t9", (target + 0x8000) >> 16),
            addiu("t9", "t9", target & 0xFFFF),
            jalr("t9"),
            NOP,
        ]
    )


def build_preload_helper() -> bytes:
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x18),
        sw("ra", 0x10, "sp"),
        lui("t0", 0xA01B),
        addiu("t0", "t0", 0x2DE0),
        sw("zero", 0, "t0"),
        jal(ENSURE_DATA_VA),
        NOP,
        jal(FORTRESS_PRELOAD_GETTER_VA),
        NOP,
        0x3C01802F,  # lui at,0x802F
        0xAC22822C,  # sw v0,-0x7DD4(at)
        lw("ra", 0x10, "sp"),
        jr("ra"),
        addiu("sp", "sp", 0x18),
    )
    return e.finish()


def build_empty_powers_wrapper() -> bytes:
    e = Emitter()

    # Items mode tail-enters the already Runtime-confirmed switch helper.
    e.bne("s2", "zero", "powers")
    e.emit(NOP)
    _jump_abs(e, SWITCH_MODULE_K1)

    # Powers mode accepts only a fresh pure Left or Right semantic word.
    e.label("powers")
    e.emit(
        addiu("sp", "sp", -0x20),
        sw("v0", 0x00, "sp"),
        sw("v1", 0x04, "sp"),
        sw("a0", 0x08, "sp"),
        sw("a1", 0x0C, "sp"),
        sw("t0", 0x10, "sp"),
        sw("t1", 0x14, "sp"),
        sw("ra", 0x18, "sp"),
        lhu("t0", 0, "s4"),
        ori("t1", "zero", 0x2000),
    )
    e.beq("t0", "t1", "direction_ok")
    e.emit(NOP)
    e.emit(ori("t1", "zero", 0x8000))
    e.bne("t0", "t1", "restore")
    e.emit(NOP)

    e.label("direction_ok")
    e.emit(andi("t1", "s7", 0xA000))
    e.bne("t1", "zero", "restore")
    e.emit(NOP)
    _call_abs(e, INVENTORY_COUNT_VA)
    e.beq("v0", "zero", "empty")
    e.emit(NOP)

    e.label("restore")
    e.emit(
        lw("v0", 0x00, "sp"),
        lw("v1", 0x04, "sp"),
        lw("a0", 0x08, "sp"),
        lw("a1", 0x0C, "sp"),
        lw("t0", 0x10, "sp"),
        lw("t1", 0x14, "sp"),
        lw("ra", 0x18, "sp"),
        addiu("sp", "sp", 0x20),
    )
    _jump_abs(e, SWITCH_MODULE_K1)

    e.label("empty")
    e.emit(
        lw("v0", 0x00, "sp"),
        lw("v1", 0x04, "sp"),
        lw("a0", 0x08, "sp"),
        lw("a1", 0x0C, "sp"),
        lw("t0", 0x10, "sp"),
        lw("t1", 0x14, "sp"),
        lw("ra", 0x18, "sp"),
        addiu("sp", "sp", 0x20),
        addu("s2", "zero", "zero"),
    )
    _jump_abs(e, SWITCH_MODULE_K1)
    return e.finish()


def build_open_wrapper() -> bytes:
    e = Emitter()
    e.emit(
        *_ori_address_words("t0", HUD_STATE_DATA_PTR_K1),
        lw("t1", 0, "t0"),
    )
    e.beq("t1", "zero", "replay")
    e.emit(NOP)
    e.emit(sw("zero", STATUS_FLAG_OFF, "t1"), sw("zero", TABLE_FLAG_OFF, "t1"))
    e.label("replay")
    e.emit(
        lui("s4", 0x800C),
        addiu("s4", "s4", 0xF2EE),
        ori("fp", "zero", 0x8000),
        lui("s5", 0x800A),
    )
    _jump_abs(e, INVENTORY_OPEN_RESUME_VA)
    return e.finish()


def build_requirement_gate() -> bytes:
    e = Emitter()
    e.emit(
        lw("t8", 0x18, "sp"),
        lw("t9", STATUS_FLAG_OFF, "t8"),
        addiu("t7", "zero", STATUS_VALID),
    )
    e.bne("t9", "t7", "prepare")
    e.emit(NOP)
    e.emit(addiu("t3", "t8", REQUIREMENT_TEXT_OFF))
    _jump_abs(e, REQUIREMENT_DRAW_K1)

    e.label("prepare")
    e.emit(
        lui("t0", 0x800C),
        addiu("t0", "t0", 0x1248),
        lw("t1", 0, "t0"),
        sltiu("t2", "t1", 10),
    )
    _jump_abs(e, REQUIREMENT_CONTINUE_K1)
    return e.finish()


def build_check_gate(
    *,
    continue_k1: int = CHECK_CONTINUE_K1,
    draw_k1: int = CHECK_DRAW_K1,
) -> bytes:
    e = Emitter()
    e.emit(
        lw("t8", 0x18, "sp"),
        lw("t9", STATUS_FLAG_OFF, "t8"),
        addiu("t7", "zero", STATUS_VALID),
    )
    e.bne("t9", "t7", "prepare")
    e.emit(NOP)
    e.emit(addiu("t6", "t8", CHECK_TEXT_OFF))
    _jump_abs(e, draw_k1)

    e.label("prepare")
    e.emit(
        addiu("t9", "t9", 1),
        sw("t9", STATUS_FLAG_OFF, "t8"),
        lui("t0", 0xA01B),
        addiu("t0", "t0", 0xF7D0),
        addiu("t1", "t0", 0x20),
        addiu("t2", "zero", 8),
    )
    _jump_abs(e, continue_k1)
    return e.finish()


def _emit_paper_restore_return(e: Emitter) -> None:
    e.emit(
        lw("s5", 0x44, "sp"),
        lw("s4", 0x48, "sp"),
        lw("s3", 0x4C, "sp"),
        lw("s2", 0x50, "sp"),
        lw("s1", 0x54, "sp"),
        lw("s0", 0x58, "sp"),
        lw("ra", 0x5C, "sp"),
        jr("ra"),
        addiu("sp", "sp", 0x60),
    )


def build_table_gate() -> bytes:
    e = Emitter()
    e.emit(lw("t8", 0x24, "sp"), lw("t9", TABLE_FLAG_OFF, "t8"))
    e.bne("t9", "zero", "cached")
    e.emit(NOP)

    # First frame prepares the exact existing mutable row strings.
    e.emit(
        addiu("t9", "zero", 1),
        sw("t9", TABLE_FLAG_OFF, "t8"),
        lui("s0", 0x800A),
        addiu("s0", "s0", 0x6048),
        addiu("s1", "zero", 40),
        addu("s2", "zero", "zero"),
    )
    _jump_abs(e, TABLE_COMPUTE_RESUME_K1)

    # Later frames submit the already-prepared strings through the same native
    # text renderer/font/coordinates.  No alternate glyph path is introduced.
    e.label("cached")
    e.emit(
        lw("t2", 0x24, "sp"),
        addiu("a0", "t2", TABLE_HEADER_OFF),
        addiu("a1", "zero", 170),
        addiu("a2", "zero", 43),
        addiu("a3", "zero", 1),
        lui("t0", 0x800B),
        addiu("t0", "t0", 0x1E44),
        sw("t0", 0x10, "sp"),
        jal(TEXT_DRAW_VA),
        NOP,
        lw("t2", 0x24, "sp"),
        addiu("s3", "t2", TABLE_ROWS_OFF),
        addiu("s4", "zero", 8),
        addiu("s5", "zero", 55),
    )
    e.label("row")
    e.emit(
        addu("a0", "s3", "zero"),
        addiu("a1", "zero", 170),
        addu("a2", "s5", "zero"),
        addiu("a3", "zero", 1),
        lui("t0", 0x800B),
        addiu("t0", "t0", 0x1E44),
        sw("t0", 0x10, "sp"),
        jal(TEXT_DRAW_VA),
        NOP,
        addiu("s3", "s3", 0x10),
        addiu("s4", "s4", -1),
        addiu("s5", "s5", 11),
    )
    e.bne("s4", "zero", "row")
    e.emit(NOP)
    _emit_paper_restore_return(e)
    return e.finish()


PRELOAD_HELPER = build_preload_helper()
EMPTY_POWERS_WRAPPER = build_empty_powers_wrapper()
OPEN_WRAPPER = build_open_wrapper()
REQUIREMENT_GATE = build_requirement_gate()
CHECK_GATE = build_check_gate()
VANILLA_CHECK_GATE = build_check_gate(
    continue_k1=VANILLA_CHECK_CONTINUE_K1,
    draw_k1=VANILLA_CHECK_DRAW_K1,
)
TABLE_GATE = build_table_gate()

_HELPERS = {
    "preload": PRELOAD_HELPER,
    "empty_powers": EMPTY_POWERS_WRAPPER,
    "open": OPEN_WRAPPER,
    "requirement": REQUIREMENT_GATE,
    "check": CHECK_GATE,
    "table": TABLE_GATE,
}
_EXPECTED_SIZES = {
    "preload": PRELOAD_SIZE,
    "empty_powers": EMPTY_POWERS_SIZE,
    "open": OPEN_SIZE,
    "requirement": REQUIREMENT_SIZE,
    "check": CHECK_SIZE,
    "table": TABLE_SIZE,
}
for _name, _blob in _HELPERS.items():
    if len(_blob) != _EXPECTED_SIZES[_name]:
        raise AssertionError(
            f"{_name} helper size drifted: 0x{len(_blob):X} != 0x{_EXPECTED_SIZES[_name]:X}"
        )
    if hashlib.sha256(_blob).hexdigest() != ACCEPTED_HELPER_SHA256[_name]:
        raise AssertionError(f"{_name} helper bytes drifted from accepted proof")


def _expected_switch_trampoline() -> bytes:
    from ..mips import address_words

    return words_blob([*address_words("t9", SWITCH_MODULE_K1), jr("t9"), NOP])


class InventoryMaterializedHudPatch:
    """Install the accepted preload + empty-box + materialized rich-HUD composition."""

    name = "inventory-rich-materialized"

    def __init__(self, *, requirement_exact: bool = True) -> None:
        self.requirement_exact = requirement_exact

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        if len(rom.data) != GLOBAL_OUTPUT_SIZE:
            raise PatchError("materialized Inventory requires the normal 32 MiB generated output")

        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 0, TRANSPORT_ROM)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 4, LEGEND_PAYLOAD_END_ROM)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)

        rom.expect_bytes(FORTRESS_PRELOAD_HOOK_ROM, EXPECTED_FORTRESS_PRELOAD_HOOK)
        rom.expect_bytes(INVENTORY_OPEN_HOOK_ROM, EXPECTED_INVENTORY_OPEN_HOOK)
        rom.expect_bytes(INVENTORY_LOOP_HOOK_ROM, _expected_switch_trampoline())
        rom.expect_bytes(TABLE_COMPUTE_ROM, EXPECTED_TABLE_COMPUTE)
        if self.requirement_exact:
            rom.expect_bytes(REQUIREMENT_GATE_ROM, EXPECTED_REQUIREMENT_GATE)
            rom.expect_bytes(CHECK_GATE_ROM, EXPECTED_CHECK_GATE)
        else:
            # Vanilla requirement text is immutable "REQ. XP 5100"; only the
            # CHKS path is mutable, and its helper body is 0x24 bytes earlier.
            rom.expect_bytes(VANILLA_CHECK_GATE_ROM, EXPECTED_CHECK_GATE)
        rom.expect_bytes(HUD_DATA_ROM + STATUS_FLAG_OFF, b"\x00" * 8)

        if bytes(rom.data[LEGEND_PAYLOAD_END_ROM:MATERIALIZED_PAYLOAD_END_ROM]) != (
            b"\xFF" * (MATERIALIZED_PAYLOAD_END_ROM - LEGEND_PAYLOAD_END_ROM)
        ):
            raise PatchError("materialized Inventory append capacity is not unassigned")

        prefix = bytes(rom.data[TRANSPORT_ROM:LEGEND_PAYLOAD_END_ROM])

        # Keep the accepted padding/layout byte-for-byte.
        rom.write_bytes(
            LEGEND_PAYLOAD_END_ROM,
            b"\x00" * (PRELOAD_ROM - LEGEND_PAYLOAD_END_ROM),
        )
        rom.write_bytes(PRELOAD_ROM, PRELOAD_HELPER)
        rom.write_bytes(EMPTY_POWERS_ROM, EMPTY_POWERS_WRAPPER)
        rom.write_bytes(
            EMPTY_POWERS_ROM + len(EMPTY_POWERS_WRAPPER),
            b"\x00" * (OPEN_ROM - (EMPTY_POWERS_ROM + len(EMPTY_POWERS_WRAPPER))),
        )
        rom.write_bytes(OPEN_ROM, OPEN_WRAPPER)
        rom.write_bytes(
            OPEN_ROM + len(OPEN_WRAPPER),
            b"\x00" * (REQUIREMENT_ROM - (OPEN_ROM + len(OPEN_WRAPPER))),
        )
        rom.write_bytes(REQUIREMENT_ROM, REQUIREMENT_GATE)
        rom.write_bytes(
            REQUIREMENT_ROM + len(REQUIREMENT_GATE),
            b"\x00" * (CHECK_ROM - (REQUIREMENT_ROM + len(REQUIREMENT_GATE))),
        )
        rom.write_bytes(CHECK_ROM, CHECK_GATE)
        rom.write_bytes(TABLE_ROM, TABLE_GATE)

        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, MATERIALIZED_PAYLOAD_END_ROM)

        # Core hooks.
        rom.write_bytes(
            FORTRESS_PRELOAD_HOOK_ROM,
            _call_trampoline_addiu(PRELOAD_K1),
        )
        rom.write_bytes(INVENTORY_OPEN_HOOK_ROM, _jump_trampoline(OPEN_K1))
        rom.write_bytes(INVENTORY_LOOP_HOOK_ROM, _jump_trampoline(EMPTY_POWERS_K1))

        # Only the mutable table/status preparation seams change inside the
        # already-promoted HUD.  Rich rows and paper-title rendering stay exact.
        rom.write_bytes(TABLE_COMPUTE_ROM, _jump_trampoline(TABLE_K1))
        if self.requirement_exact:
            rom.write_bytes(REQUIREMENT_GATE_ROM, _jump_trampoline(REQUIREMENT_K1))
            rom.write_bytes(CHECK_GATE_ROM, _jump_trampoline(CHECK_K1))
        else:
            rom.write_bytes(
                VANILLA_CHECK_GATE_ROM,
                _jump_trampoline(CHECK_K1),
            )

        if bytes(rom.data[TRANSPORT_ROM:LEGEND_PAYLOAD_END_ROM]) == prefix:
            raise AssertionError(
                "materialized Inventory expected to patch table/status seams inside transport prefix"
            )

        return (
            "Fortress preloads the existing 0x1200 Inventory HUD allocation before its rewind anchor",
            "empty Powers mode accepts fresh pure Left/Right and reuses the promoted four-box switch transaction",
            (
                "REQ/CHKS and STG CHECKS KEYS mutable values are materialized per Inventory session"
                if self.requirement_exact
                else "Vanilla REQ. XP 5100 remains static; CHKS and STG CHECKS KEYS are materialized per Inventory session"
            ),
            "item rows, paper title, portraits, fonts, palettes, spacing and native text renderer remain unchanged",
            (
                f"materialized file 0x1A end 0x{MATERIALIZED_PAYLOAD_END_ROM:08X}; "
                f"runtime end 0x{MATERIALIZED_RUNTIME_END_K0:08X}"
            ),
        )
