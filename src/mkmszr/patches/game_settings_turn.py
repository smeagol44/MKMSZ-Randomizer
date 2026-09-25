"""Production GAME SETTINGS -> TURN TOGGLE/LOCK controls.

This module promotes the Runtime-confirmed v06 control/menu proof into the
shared patch core.  It keeps the stock GAME SETTINGS entry, replaces its
Difficulty/Lives/Continues editor with TURN: TOGGLE/LOCK, and loads the
control helpers from the production expansion pool.

TURN defaults to TOGGLE (vanilla).  LOCK enables the v10 world-direction /
facing-lock model and temporarily defers to stock semantics when the bounded
v06 opponent face-policy scan detects +0x6BC bit 0x0200.

File ID 0x1A is the shared expansion transport.  TURN owns the low expansion
slice; optional Toasty content is appended later at its established
0x801B0000 runtime base.
"""

from __future__ import annotations

from ..allocations import ExpansionPoolAllocator
from ..data.addresses import (
    FILE_TABLE_ENTRY_SIZE,
    FILE_TABLE_ROM,
    PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED,
    PICKUP_MANAGER_CAPTURE_HOOK_ROM,
    RAW_FILE_LOADER_VA,
)
from ..mips import (
    Emitter,
    addiu,
    address_words,
    addu,
    andi,
    jal,
    jalr,
    jr,
    jump,
    lhu,
    lui,
    lw,
    or_,
    ori,
    sh,
    sll,
    sltiu,
    srl,
    sw,
    words_blob,
)
from ..rom import RomImage
from .base import PatchContext
from .inventory_boxes import (
    COMBOS_ASSIST_STATE_MASK,
    STATE_VA,
    TURN_LOCK_STATE_MASK,
)
from .native_payload import kseg1_alias
from .pickup_persistence import (
    CAPTURE_HELPER,
    CAPTURE_HELPER_ROM,
    CAPTURE_HELPER_VA,
    DESCRIPTOR_TABLE_ROM,
)
from .runtime_v2 import CODE_UNCACHED_BASE, STATE_SIZE, STATE_UNCACHED_BASE

NOP = 0

EXPANSION_FILE_ID = 0x1A
EXPANSION_FILE_ENTRY_ROM = FILE_TABLE_ROM + EXPANSION_FILE_ID * FILE_TABLE_ENTRY_SIZE
SHARED_EXPANSION_ROM = 0x00F68000
TOASTY_RUNTIME_BASE = 0x801B0000

PLAYER_SEMANTIC_INPUT_VA = 0x800BF2EE
CURRENT_CONTROLLER_PTR_VA = 0x802ECE20
CONTROLLER_LIST_HEAD_VA = 0x80111EAC
TURN_MASK = 0x0001

# The final reserved Runtime V2 word is only the native GAME SETTINGS editor's
# transient halfword backing while that frontend is open.  The durable user
# preference lives in the already-owned four-box state word so normal Runtime V2
# stage initialization cannot erase it.
SETTINGS_UNCACHED_VA = STATE_UNCACHED_BASE + STATE_SIZE - 4
TURN_TOGGLE = 0
TURN_LOCK = 1

FACE_POLICY_SCANNER_VA = 0x8004A6E8
FACING_FLIP_VA = 0x8003188C

DECISION_HOOK_ROM = 0x00029FB0
DECISION_RESUME_VA = 0x800293B8
DECISION_EXPECTED = bytes.fromhex("8C640704 24020305")

RELEASE_HOOK_ROM = 0x0002A0DC
RELEASE_EXPECTED = bytes.fromhex("8C820638 94430000")

# v10 action-selection boundary.  States 23/24 are standing/crouched Turn.
ACTION_HOOK_ROM = 0x00016354
ACTION_STOCK_RESUME_VA = 0x8001575C
ACTION_SUPPRESS_RESUME_VA = 0x80015768
ACTION_EXPECTED = bytes.fromhex("A62406DC 3C058003")

GAME_SETTINGS_VA = 0x800766BC
GAME_SETTINGS_CALL_ROM = 0x000770B8

# The accepted COMBOS UI/state proof reuses stock row 1.  Stock row 2 remains
# visually hidden and its now-dead edit blocks become frontend-resident
# navigation helpers so selection moves 0 -> 1 -> 3 (EXIT) and back.
COMBOS_RIGHT_ROM = 0x00077524
COMBOS_RIGHT_END_ROM = 0x00077584
NAV_DOWN_HELPER_ROM = 0x00077584
NAV_DOWN_HELPER_VA = 0x80076984
NAV_DOWN_HELPER_END_ROM = 0x000775DC
COMBOS_LEFT_ROM = 0x00077654
COMBOS_LEFT_END_ROM = 0x0007767C
NAV_UP_HELPER_ROM = 0x0007767C
NAV_UP_HELPER_VA = 0x80076A7C
NAV_UP_HELPER_END_ROM = 0x0007769C
COMBOS_DRAW_ROM = 0x00077888
COMBOS_DRAW_END_ROM = 0x000778CC
GAME_TEXT_DRAW_VA = 0x8001CA88

BOOTSTRAP_RUNTIME_ENTRY_WORDS_OFFSET = 0x34

STATIC_REGION_ROM = CAPTURE_HELPER_ROM
STATIC_REGION_VA = CAPTURE_HELPER_VA
STATIC_REGION_END_ROM = DESCRIPTOR_TABLE_ROM
STATIC_REGION_SIZE = STATIC_REGION_END_ROM - STATIC_REGION_ROM


def _align(value: int, alignment: int = 16) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def _indirect_jump(target: int) -> bytes:
    return words_blob([*address_words("t9", target), jr("t9"), NOP])


def build_expansion_loader() -> bytes:
    """Load shared file 0x1A to the low expansion pool and restore Runtime V2 T9."""

    high = ((CONTROL_MODULE_CACHED_BASE + 0x8000) >> 16) & 0xFFFF
    low = CONTROL_MODULE_CACHED_BASE & 0xFFFF

    emitter = Emitter()
    emitter.emit(
        addiu("sp", "sp", -0x18),
        sw("ra", 0x10, "sp"),
        addiu("a0", "zero", EXPANSION_FILE_ID),
        lui("a1", high),
        jal(RAW_FILE_LOADER_VA),
        addiu("a1", "a1", low),
        *address_words("t9", CODE_UNCACHED_BASE),
        lw("ra", 0x10, "sp"),
        addiu("sp", "sp", 0x18),
        jr("ra"),
        NOP,
    )
    return emitter.finish()


def _emit_turn_lock_gate(emitter: Emitter, *, fallback_label: str) -> None:
    """Branch to fallback unless the durable MKMSZR preference is TURN=LOCK."""

    emitter.emit(*address_words("t0", STATE_VA))
    emitter.emit(lw("t1", 0, "t0"), andi("t1", "t1", TURN_LOCK_STATE_MASK))
    emitter.beq("t1", "zero", fallback_label)
    emitter.emit(NOP)


def build_decision_helper() -> bytes:
    """v10 direction-facing decision, gated by TURN=LOCK."""

    emitter = Emitter()
    emitter.emit(
        addiu("sp", "sp", -0x40),
        sw("v1", 0x00, "sp"),
        sw("a1", 0x04, "sp"),
        sw("a2", 0x08, "sp"),
        sw("a3", 0x0C, "sp"),
        sw("t0", 0x10, "sp"),
        sw("t1", 0x14, "sp"),
        sw("t2", 0x18, "sp"),
        sw("t3", 0x1C, "sp"),
        sw("t4", 0x20, "sp"),
        sw("t5", 0x24, "sp"),
        sw("t6", 0x28, "sp"),
        sw("t7", 0x2C, "sp"),
        sw("t8", 0x30, "sp"),
        sw("t9", 0x34, "sp"),
        sw("ra", 0x38, "sp"),
    )

    emitter.emit(lw("a0", 0x704, "v1"), sw("a0", 0x3C, "sp"))
    emitter.beq("a0", "zero", "finish")
    emitter.emit(NOP)

    _emit_turn_lock_gate(emitter, fallback_label="restore_mismatch")

    # Held Turn keeps stock backward locomotion.
    emitter.emit(lw("t0", 0x638, "v1"), lhu("t1", 0, "t0"), andi("t1", "t1", TURN_MASK))
    emitter.bne("t1", "zero", "restore_mismatch")
    emitter.emit(NOP)

    # This scanner call is retained exactly from the stable v03/v06 decision path.
    emitter.emit(*address_words("t9", FACE_POLICY_SCANNER_VA), jalr("t9"), NOP)
    emitter.emit(ori("t0", "zero", 0x8000))
    emitter.bne("v0", "t0", "flip")
    emitter.emit(NOP)

    emitter.label("restore_mismatch")
    emitter.emit(lw("a0", 0x3C, "sp"))
    emitter.beq("zero", "zero", "finish")
    emitter.emit(NOP)

    emitter.label("flip")
    emitter.emit(*address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"))
    emitter.emit(lw("a0", 0x6E0, "t0"))
    emitter.emit(*address_words("t9", FACING_FLIP_VA), jalr("t9"), NOP)
    emitter.emit(*address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"))
    emitter.emit(sw("zero", 0x704, "t0"), addiu("a0", "zero", 0))

    emitter.label("finish")
    emitter.emit(addiu("v0", "zero", 0x305))
    emitter.emit(
        lw("v1", 0x00, "sp"),
        lw("a1", 0x04, "sp"),
        lw("a2", 0x08, "sp"),
        lw("a3", 0x0C, "sp"),
        lw("t0", 0x10, "sp"),
        lw("t1", 0x14, "sp"),
        lw("t2", 0x18, "sp"),
        lw("t3", 0x1C, "sp"),
        lw("t4", 0x20, "sp"),
        lw("t5", 0x24, "sp"),
        lw("t6", 0x28, "sp"),
        lw("t7", 0x2C, "sp"),
        lw("t8", 0x30, "sp"),
        lw("t9", 0x34, "sp"),
        lw("ra", 0x38, "sp"),
        addiu("sp", "sp", 0x40),
        jr("ra"),
        NOP,
    )
    return emitter.finish()


def _emit_leaf_face_policy_scan(
    emitter: Emitter,
    *,
    forced_label: str,
    clear_label: str,
    prefix: str,
) -> None:
    """Bounded v06 face-policy scan with no nested native calls."""

    emitter.emit(
        *address_words("t0", CONTROLLER_LIST_HEAD_VA),
        lw("t0", 0, "t0"),
        addiu("t2", "zero", 64),
    )
    emitter.label(prefix + "_loop")
    emitter.beq("t0", "zero", clear_label)
    emitter.emit(NOP)
    emitter.emit(*address_words("t1", CURRENT_CONTROLLER_PTR_VA), lw("t1", 0, "t1"))
    emitter.beq("t0", "t1", prefix + "_next")
    emitter.emit(NOP)
    emitter.emit(lhu("t1", 0x6D8, "t0"), addiu("t1", "t1", -2), sltiu("t1", "t1", 2))
    emitter.beq("t1", "zero", prefix + "_next")
    emitter.emit(NOP)
    emitter.emit(lhu("t1", 0x6BC, "t0"), andi("t1", "t1", 0x0200))
    emitter.bne("t1", "zero", forced_label)
    emitter.emit(NOP)
    emitter.label(prefix + "_next")
    emitter.emit(lw("t0", 0, "t0"), addiu("t2", "t2", -1))
    emitter.bne("t2", "zero", prefix + "_loop")
    emitter.emit(NOP)
    emitter.beq("zero", "zero", clear_label)
    emitter.emit(NOP)


def build_release_helper() -> bytes:
    """Exit LOCK backpedal on Turn release; defer to stock during forced-facing."""

    emitter = Emitter()
    _emit_turn_lock_gate(emitter, fallback_label="stock")

    emitter.emit(
        lw("v0", 0x638, "a0"),
        lhu("v1", 0, "v0"),
        lw("v0", 0x6FC, "a0"),
        addiu("v0", "v0", -2),
    )
    emitter.bne("v0", "zero", "return")
    emitter.emit(NOP)

    # Preserve only leaf-scan temporaries.  v06 proved these mid-function hooks
    # must not make nested native calls.
    emitter.emit(
        addiu("sp", "sp", -0x10),
        sw("t0", 0x00, "sp"),
        sw("t1", 0x04, "sp"),
        sw("t2", 0x08, "sp"),
    )
    _emit_leaf_face_policy_scan(
        emitter,
        forced_label="forced",
        clear_label="clear",
        prefix="release_scan",
    )

    emitter.label("forced")
    emitter.emit(
        lw("t0", 0x00, "sp"),
        lw("t1", 0x04, "sp"),
        lw("t2", 0x08, "sp"),
        addiu("sp", "sp", 0x10),
    )
    emitter.beq("zero", "zero", "return")
    emitter.emit(NOP)

    emitter.label("clear")
    emitter.emit(
        lw("t0", 0x00, "sp"),
        lw("t1", 0x04, "sp"),
        lw("t2", 0x08, "sp"),
        addiu("sp", "sp", 0x10),
    )
    emitter.emit(andi("v0", "v1", TURN_MASK))
    emitter.bne("v0", "zero", "return")
    emitter.emit(NOP)
    emitter.emit(addiu("v1", "zero", 0))
    emitter.beq("zero", "zero", "return")
    emitter.emit(NOP)

    emitter.label("stock")
    emitter.emit(lw("v0", 0x638, "a0"), lhu("v1", 0, "v0"))

    emitter.label("return")
    emitter.emit(jr("ra"), NOP)
    return emitter.finish()


def build_action_gate_helper() -> bytes:
    """Suppress player Turn states 23/24 only while effective LOCK is active."""

    emitter = Emitter()
    emitter.emit(
        addiu("sp", "sp", -0x10),
        sw("t0", 0x00, "sp"),
        sw("t1", 0x04, "sp"),
        sw("t2", 0x08, "sp"),
    )
    emitter.emit(lw("t0", 0x638, "s1"), *address_words("t1", PLAYER_SEMANTIC_INPUT_VA))
    emitter.bne("t0", "t1", "stock")
    emitter.emit(NOP)

    _emit_turn_lock_gate(emitter, fallback_label="stock")

    emitter.emit(addiu("t2", "zero", 23))
    emitter.beq("a0", "t2", "check_policy")
    emitter.emit(NOP)
    emitter.emit(addiu("t2", "zero", 24))
    emitter.bne("a0", "t2", "stock")
    emitter.emit(NOP)

    emitter.label("check_policy")
    _emit_leaf_face_policy_scan(
        emitter,
        forced_label="stock",
        clear_label="suppress",
        prefix="action_scan",
    )

    emitter.label("stock")
    emitter.emit(
        lw("t0", 0x00, "sp"),
        lw("t1", 0x04, "sp"),
        lw("t2", 0x08, "sp"),
        addiu("sp", "sp", 0x10),
        sh("a0", 0x6DC, "s1"),
        lui("a1", 0x8003),
        jump(ACTION_STOCK_RESUME_VA),
        NOP,
    )

    emitter.label("suppress")
    emitter.emit(
        lw("t0", 0x00, "sp"),
        lw("t1", 0x04, "sp"),
        lw("t2", 0x08, "sp"),
        addiu("sp", "sp", 0x10),
        jump(ACTION_SUPPRESS_RESUME_VA),
        NOP,
    )
    return emitter.finish()


def build_menu_wrapper() -> bytes:
    """Frontend-safe TURN editor wrapper using only global/title-resident code."""

    emitter = Emitter()
    emitter.emit(
        addiu("sp", "sp", -0x18),
        sw("ra", 0x10, "sp"),
        *address_words("t0", STATE_VA),
        lw("t1", 0, "t0"),
        andi("t1", "t1", TURN_LOCK_STATE_MASK),
        srl("t1", "t1", 9),
        *address_words("t2", SETTINGS_UNCACHED_VA),
        sh("t1", 0, "t2"),
        jal(GAME_SETTINGS_VA),
        NOP,
    )

    # The four-box state word currently defines only low-halfword state bits:
    # active box, latch, and TURN.  Replace only TURN inside that owned low
    # halfword; no high-halfword owner exists in the current layout.
    emitter.emit(
        *address_words("t0", STATE_VA),
        lw("t2", 0, "t0"),
        andi("t2", "t2", (~TURN_LOCK_STATE_MASK) & 0xFFFF),
        *address_words("t3", SETTINGS_UNCACHED_VA),
        lhu("t1", 0, "t3"),
        sll("t1", "t1", 9),
        or_("t2", "t2", "t1"),
        sw("t2", 0, "t0"),
        lw("ra", 0x10, "sp"),
        addiu("sp", "sp", 0x18),
        jr("ra"),
        NOP,
    )
    return emitter.finish()


def _pack_module() -> tuple[bytes, dict[str, int]]:
    routines = [
        ("capture", CAPTURE_HELPER),
        ("decision", build_decision_helper()),
        ("release", build_release_helper()),
        ("action", build_action_gate_helper()),
    ]
    blob = bytearray()
    offsets: dict[str, int] = {}
    for name, routine in routines:
        aligned = _align(len(blob))
        blob.extend(bytes(aligned - len(blob)))
        offsets[name] = aligned
        blob.extend(routine)
    return bytes(blob), offsets


CONTROL_MODULE, CONTROL_MODULE_OFFSETS = _pack_module()
_pool = ExpansionPoolAllocator()
CONTROL_ALLOCATION = _pool.allocate("turn-controls-production", len(CONTROL_MODULE), align=16)
CONTROL_MODULE_CACHED_BASE = CONTROL_ALLOCATION.start
CONTROL_MODULE_UNCACHED_BASE = kseg1_alias(CONTROL_MODULE_CACHED_BASE)
if CONTROL_ALLOCATION.end_exclusive > TOASTY_RUNTIME_BASE:
    raise AssertionError("TURN production module reaches Toasty runtime base")

CAPTURE_ENTRY = CONTROL_MODULE_UNCACHED_BASE + CONTROL_MODULE_OFFSETS["capture"]
DECISION_ENTRY = CONTROL_MODULE_UNCACHED_BASE + CONTROL_MODULE_OFFSETS["decision"]
RELEASE_ENTRY = CONTROL_MODULE_UNCACHED_BASE + CONTROL_MODULE_OFFSETS["release"]
ACTION_ENTRY = CONTROL_MODULE_UNCACHED_BASE + CONTROL_MODULE_OFFSETS["action"]


def _pack_static_region() -> tuple[bytes, dict[str, int]]:
    pieces = [
        ("loader", build_expansion_loader()),
        ("capture", _indirect_jump(CAPTURE_ENTRY)),
        ("decision", _indirect_jump(DECISION_ENTRY)),
        ("release", _indirect_jump(RELEASE_ENTRY)),
        ("action", _indirect_jump(ACTION_ENTRY)),
        ("menu", build_menu_wrapper()),
    ]
    blob = bytearray()
    offsets: dict[str, int] = {}
    for name, piece in pieces:
        # Static global-code entries only require instruction alignment.  Using
        # 16-byte padding here needlessly consumed the last bytes needed by the
        # frontend-resident menu wrapper.
        aligned = _align(len(blob), 4)
        blob.extend(bytes(aligned - len(blob)))
        offsets[name] = aligned
        blob.extend(piece)
    if len(blob) > STATIC_REGION_SIZE:
        raise AssertionError("TURN loaders/trampolines exceed repurposed capture region")
    blob.extend(bytes(STATIC_REGION_SIZE - len(blob)))
    return bytes(blob), offsets


STATIC_REGION_BLOB, STATIC_OFFSETS = _pack_static_region()
EXPANSION_LOADER_VA = STATIC_REGION_VA + STATIC_OFFSETS["loader"]
CAPTURE_TRAMPOLINE_VA = STATIC_REGION_VA + STATIC_OFFSETS["capture"]
DECISION_TRAMPOLINE_VA = STATIC_REGION_VA + STATIC_OFFSETS["decision"]
RELEASE_TRAMPOLINE_VA = STATIC_REGION_VA + STATIC_OFFSETS["release"]
ACTION_TRAMPOLINE_VA = STATIC_REGION_VA + STATIC_OFFSETS["action"]
MENU_WRAPPER_VA = STATIC_REGION_VA + STATIC_OFFSETS["menu"]



def _pad_region(blob: bytes, size: int) -> bytes:
    if len(blob) > size:
        raise AssertionError("GAME SETTINGS helper exceeds reclaimed stock region")
    return blob + bytes(size - len(blob))


def build_nav_down_helper() -> bytes:
    """Move TURN -> COMBOS -> EXIT while skipping hidden stock row 2."""

    e = Emitter()
    e.emit(addiu("v0", "zero", 1))
    e.bne("s0", "v0", "increment")
    e.emit(NOP)
    e.emit(addiu("s0", "zero", 3), jr("ra"), NOP)
    e.label("increment")
    e.emit(addiu("s0", "s0", 1), jr("ra"), NOP)
    return e.finish()


def build_nav_up_helper() -> bytes:
    """Move EXIT -> COMBOS -> TURN while skipping hidden stock row 2."""

    # The delay-slot decrement handles COMBOS(1) -> TURN(0).  EXIT(3) does not
    # take the branch and therefore executes one additional decrement: 3 -> 2
    # in the delay slot, then 2 -> 1 before returning.
    e = Emitter()
    e.emit(addiu("v0", "zero", 3))
    e.bne("s0", "v0", "done")
    e.emit(addiu("s0", "s0", -1))
    e.emit(addiu("s0", "s0", -1))
    e.label("done")
    e.emit(jr("ra"), NOP)
    return e.finish()


def build_combos_right_handler() -> bytes:
    """CLASSIC -> ASSIST; repeated Right while ASSIST is a no-op."""

    return words_blob(
        [
            lui("t0", 0x800A),
            lw("t1", STATE_VA - 0x800A0000, "t0"),
            ori("t1", "t1", COMBOS_ASSIST_STATE_MASK),
            sw("t1", STATE_VA - 0x800A0000, "t0"),
            jump(0x800769DC),
            NOP,
        ]
    )


def build_combos_left_handler() -> bytes:
    """ASSIST -> CLASSIC; repeated Left while CLASSIC is a no-op."""

    return words_blob(
        [
            lui("t0", 0x800A),
            lw("t1", STATE_VA - 0x800A0000, "t0"),
            andi("t1", "t1", (~COMBOS_ASSIST_STATE_MASK) & 0xFFFF),
            sw("t1", STATE_VA - 0x800A0000, "t0"),
            jump(0x80076A9C),
            NOP,
        ]
    )


def build_combos_value_draw() -> bytes:
    """Draw CLASSIC/ASSIST using unused entries 2/3 of the stock value table."""

    return words_blob(
        [
            lui("v0", 0x800A),
            lw("v0", STATE_VA - 0x800A0000, "v0"),
            andi("v0", "v0", COMBOS_ASSIST_STATE_MASK),
            srl("v0", "v0", 10),
            sll("v0", "v0", 2),
            addu("v0", "v0", "s5"),
            lw("a0", 16, "v0"),
            addiu("a1", "zero", 160),
            addiu("a2", "zero", 125),
            addiu("a3", "zero", 1),
            lui("t0", 0x800B),
            addiu("t0", "t0", 0x2724),
            sw("t0", 16, "sp"),
            addiu("t0", "zero", 10),
            sw("t0", 20, "sp"),
            jal(GAME_TEXT_DRAW_VA),
            sw("s1", 24, "sp"),
        ]
    )


def _patch_game_settings(rom: RomImage) -> None:
    rom.expect_bytes(GAME_SETTINGS_CALL_ROM, bytes.fromhex("0C01D9AF 02402021"))
    rom.write_u32(GAME_SETTINGS_CALL_ROM, jal(MENU_WRAPPER_VA))

    # Stock indices are settings 0/1/2 and EXIT 3.  TURN uses row 0 and COMBOS
    # uses row 1.  Row 2 stays hidden, while small reclaimed stock-row helpers
    # make vertical navigation 0 <-> 1 <-> 3 without an invisible stop.
    rom.expect_u32(0x00077400, 0x2A020003)
    rom.expect_u32(0x00077418, 0x26100001)
    rom.expect_u32(0x0007744C, 0x2610FFFF)
    rom.write_u32(0x00077418, jal(NAV_DOWN_HELPER_VA))
    rom.write_u32(0x0007744C, jal(NAV_UP_HELPER_VA))

    replacements = {
        0x000774B0: (0x3C02800A, 0x3C02A01B),
        0x000774B4: (0x84425FA8, 0x8442F81C),
        0x000774BC: (0x28420004, 0x28420001),
        0x000774C8: (0x3C01800A, 0x3C01A01B),
        0x000774CC: (0xA4225FA8, 0xA422F81C),
        0x000774D0: (0x3C02800A, 0x3C02A01B),
        0x000774D4: (0x84425FA8, 0x8442F81C),
        0x00077630: (0x3C02800A, 0x3C02A01B),
        0x00077634: (0x84425FA8, 0x8442F81C),
        0x00077644: (0x3C01800A, 0x3C01A01B),
        0x00077648: (0xA4225FA8, 0xA422F81C),
        0x0007784C: (0x3C02800A, 0x3C02A01B),
        0x00077850: (0x84425FA8, 0x8442F81C),
    }
    for offset, (expected, replacement) in replacements.items():
        rom.expect_u32(offset, expected)
        rom.write_u32(offset, replacement)

    rom.expect_bytes(
        COMBOS_RIGHT_ROM,
        bytes.fromhex(
            "3c02800a84425fa82842000210400008000000003c02800a84425faa"
            "2842000c10400025000000000801da5a000000003c02800a84425faa"
            "284200061040001e000000003c02800a94425faa244200013c01800a"
            "a4225faa0801da7700000000"
        ),
    )
    rom.expect_bytes(
        NAV_DOWN_HELPER_ROM,
        bytes.fromhex(
            "3c02800a84425fa82842000210400008000000003c02800a84425fac"
            "284200081040000d000000000801da72000000003c02800a84425fac"
            "2842000410400006000000003c02800a94425fac244200013c01800a"
            "a4225fac"
        ),
    )
    rom.expect_bytes(
        COMBOS_LEFT_ROM,
        bytes.fromhex(
            "3c02800a84425faa00401821284200041440000d2462ffff3c01800a"
            "a4225faa0801daa700000000"
        ),
    )
    rom.expect_bytes(
        NAV_UP_HELPER_ROM,
        bytes.fromhex(
            "3c02800a84425fac0040182128420002144000032462ffff3c01800a"
            "a4225fac"
        ),
    )
    rom.expect_bytes(
        COMBOS_DRAW_ROM,
        bytes.fromhex(
            "3c06800a84c65faa3c05800b24a5eb300c023a2002a0202102a02021"
            "240500a02406007d240700013c08800b25082724afa800102408000a"
            "afa800140c0072a2afb10018"
        ),
    )

    rom.write_bytes(
        COMBOS_RIGHT_ROM,
        _pad_region(build_combos_right_handler(), COMBOS_RIGHT_END_ROM - COMBOS_RIGHT_ROM),
    )
    rom.write_bytes(
        NAV_DOWN_HELPER_ROM,
        _pad_region(build_nav_down_helper(), NAV_DOWN_HELPER_END_ROM - NAV_DOWN_HELPER_ROM),
    )
    rom.write_bytes(
        COMBOS_LEFT_ROM,
        _pad_region(build_combos_left_handler(), COMBOS_LEFT_END_ROM - COMBOS_LEFT_ROM),
    )
    rom.write_bytes(
        NAV_UP_HELPER_ROM,
        _pad_region(build_nav_up_helper(), NAV_UP_HELPER_END_ROM - NAV_UP_HELPER_ROM),
    )
    rom.write_bytes(
        COMBOS_DRAW_ROM,
        _pad_region(build_combos_value_draw(), COMBOS_DRAW_END_ROM - COMBOS_DRAW_ROM),
    )

    rom.expect_bytes(0x000AF6CC, b"VERY EASY\x00\x00\x00")
    rom.expect_bytes(0x000AF6D8, b"EASY\x00\x00\x00\x00")
    rom.expect_bytes(0x000AF6E0, b"MEDIUM\x00\x00")
    rom.expect_bytes(0x000AF6E8, b"HARD\x00\x00\x00\x00")
    rom.expect_bytes(0x000AF710, b"DIFFICULTY\x00\x00")
    rom.expect_bytes(0x000AF71C, b"LIVES\x00\x00\x00")
    rom.expect_bytes(0x000AF724, b"CONTINUES\x00\x00\x00")
    rom.write_bytes(0x000AF6CC, b"TOGGLE\x00" + bytes(5))
    rom.write_bytes(0x000AF6D8, b"LOCK\x00" + bytes(3))
    rom.write_bytes(0x000AF6E0, b"CLASSIC\x00")
    rom.write_bytes(0x000AF6E8, b"ASSIST\x00" + bytes(1))
    rom.write_bytes(0x000AF710, b"TURN\x00" + bytes(7))
    rom.write_bytes(0x000AF71C, b"COMBOS\x00" + bytes(1))
    rom.write_bytes(0x000AF724, bytes(12))

    # Row 1 is now drawn by the COMBOS text-value replacement above.  The
    # hidden former Continues row remains blank and its numeric draw stays off.
    rom.expect_u32(0x00077908, 0x0C0072A2)
    rom.write_u32(0x00077908, NOP)


class GameSettingsTurnPatch:
    """Install production TURN: TOGGLE/LOCK menu and v06 control behavior."""

    name = "game-settings-turn"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        # Layer after ordinary-pickup persistence.  Its capture helper is moved
        # into the expansion module without changing capture semantics.
        rom.expect_bytes(STATIC_REGION_ROM, CAPTURE_HELPER)
        rom.expect_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM, jal(CAPTURE_HELPER_VA))
        rom.expect_u32(
            PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4,
            PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED,
        )

        rom.expect_bytes(EXPANSION_FILE_ENTRY_ROM, bytes(FILE_TABLE_ENTRY_SIZE))
        rom.expect_bytes(SHARED_EXPANSION_ROM, b"\xFF" * len(CONTROL_MODULE))

        bootstrap_patch_rom = 0x0009AD84 + BOOTSTRAP_RUNTIME_ENTRY_WORDS_OFFSET
        rom.expect_bytes(
            bootstrap_patch_rom,
            words_blob(address_words("t9", CODE_UNCACHED_BASE)),
        )

        rom.expect_bytes(DECISION_HOOK_ROM, DECISION_EXPECTED)
        rom.expect_bytes(RELEASE_HOOK_ROM, RELEASE_EXPECTED)
        rom.expect_bytes(ACTION_HOOK_ROM, ACTION_EXPECTED)

        module_end = SHARED_EXPANSION_ROM + len(CONTROL_MODULE)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 0, SHARED_EXPANSION_ROM)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, module_end)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)
        rom.write_bytes(SHARED_EXPANSION_ROM, CONTROL_MODULE)

        rom.write_bytes(STATIC_REGION_ROM, STATIC_REGION_BLOB)
        rom.write_u32(bootstrap_patch_rom, jal(EXPANSION_LOADER_VA))
        rom.write_u32(bootstrap_patch_rom + 4, NOP)

        rom.write_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM, jal(CAPTURE_TRAMPOLINE_VA))
        rom.write_u32(DECISION_HOOK_ROM, jal(DECISION_TRAMPOLINE_VA))
        rom.write_u32(DECISION_HOOK_ROM + 4, NOP)
        rom.write_u32(RELEASE_HOOK_ROM, jal(RELEASE_TRAMPOLINE_VA))
        rom.write_u32(RELEASE_HOOK_ROM + 4, NOP)
        rom.write_u32(ACTION_HOOK_ROM, jump(ACTION_TRAMPOLINE_VA))
        rom.write_u32(ACTION_HOOK_ROM + 4, NOP)

        _patch_game_settings(rom)

        return (
            "GAME SETTINGS exposes TURN: TOGGLE / LOCK and UI-only COMBOS: CLASSIC / ASSIST",
            "COMBOS defaults to CLASSIC and has no gameplay effect in this proof",
            (
                f"TURN module ROM 0x{SHARED_EXPANSION_ROM:08X}.."
                f"0x{module_end - 1:08X} -> RDRAM "
                f"0x{CONTROL_MODULE_CACHED_BASE:08X}"
            ),
            "LOCK uses runtime-confirmed v10 facing behavior",
            "v06 leaf-only forced-facing fallback retained for boss/special encounters",
            "Inventory Combine remains on the native Turn/Combine semantic bit",
        )
