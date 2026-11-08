"""Native controls emitters ported from the accepted manual-test composition.

The emitters retain their confirmed MIPS instructions and stock callbacks.
"""
from __future__ import annotations

from ..mips import (
    Emitter,
    addiu,
    address_words,
    addu,
    and_,
    andi,
    jal,
    jr,
    jump,
    lui,
    lw,
    or_,
    ori,
    sh,
    sll,
    sllv,
    sltiu,
    srl,
    sw,
    words_blob,
    xori,
)

FILE_ROM = 0x00F68000


V06_FILE_END = 0x00F693F0


STATE_VA = 0x800A60E8


ATTACK_MODERN_MASK = 0x0400


SPECIALS_MODERN_MASK = 0x0800


JUMP_BUTTON_MASK = 0x1000


RUN_AUTO_MASK = 0x2000


BOX_SETTINGS_MASK_ROM = 0x0009A6F4


BOX_SETTINGS_MASK_V06 = 0x31291E00


BOX_SETTINGS_MASK_V09 = 0x31293E00


RUN_PREDICATE_VA = 0x8002EAFC


RUN_PREDICATE_ROM = RUN_PREDICATE_VA - 0x7FFFF400


RUN_PREDICATE_EXPECTED = bytes.fromhex(
    "3C02802F 8C42CE20 944306D8 3C04800C 2484F2EC 24020001 50620001 "
    "24840002 94830000 30630004 10600002 24024000 34028000 03E00008 00000000"
)


RUN_CALL_ROMS = (0x00029FD8, 0x0002A0A0, 0x0002A738, 0x0002A7C4)


RUN_CALL_EXPECTED = 0x0C00BABF


RUN_LOOP_CLASSIFIER_ROM = 0x0002A2E8


RUN_LOOP_CLASSIFIER_EXPECTED = 0x0C00AC7E


ACTION_HOOK_ROM = 0x0001674C


ACTION_HOOK_EXPECTED = bytes.fromhex("0C023ABA 00000000")


RUN_LOOP_BACKEDGE_ROM = 0x0002A378


RUN_LOOP_BACKEDGE_EXPECTED = bytes.fromhex("0800A5AE 00000000")  # j 0x800296B8; nop


RIGHT_EDIT_ROM = 0x00077480


RIGHT_EDIT_VA = 0x80076880


RIGHT_SAFE_END_ROM = 0x000775D0


RIGHT_EDIT_END_ROM = 0x000775DC


RIGHT_GAMEPLAY_TAIL_ROM = 0x000775D0


RIGHT_GAMEPLAY_TAIL = bytes.fromhex("2739FDA0 03200008 00000000")


LEFT_EDIT_ROM = 0x00077600


LEFT_EDIT_VA = 0x80076A00


LEFT_SAFE_END_ROM = 0x00077688


LEFT_EDIT_END_ROM = 0x0007769C


LEFT_GAMEPLAY_TAIL_ROM = 0x00077688


LEFT_GAMEPLAY_TAIL = bytes.fromhex("2739FD30 03200008 00000000")


RIGHT_DONE_VA = 0x800769DC


LEFT_DONE_VA = 0x80076A9C


RIGHT_V06_SHA = "5bfddc8d4c83623907120a562665935ddd0bd136aff68dd8945063f8bf1ed978"


LEFT_V06_SHA = "6d62ad4dfd0d5cac7e83502f0f97bb55fa36058de39f6983b1b65cbbb4d7ed51"


GAME_TEXT_DRAW_VA = 0x8001CA88


VALUE_STYLE_VA = 0x800B2724


SETTINGS_UNCACHED_VA = 0xA01AF81C


DPAD_VALUE_VA = 0x800AEAF0


JUMP_LABEL_VA = 0x800AEB15


RUN_LABEL_VA = 0x800AEB9C


HOLD_VALUE_VA = 0x800AEAD3


AUTO_VALUE_VA = 0x800AEAD8


EXISTING_LOCK_VALUE_VA = 0x800AEB95  # stock BLOCK substring "LOCK"


ROW_COUNT_RIGHT_ROM = 0x00077400


ROW_COUNT_LEFT_ROM = 0x000776EC


ROW_COUNT_V06 = 0x2A020004


ROW_COUNT_V09 = 0x2A020005


COMBOS_DRAW_ROM = 0x00077888


COMBOS_DRAW_END_ROM = 0x000778CC


SPECIALS_DRAW_ROM = 0x000778CC


SPECIALS_DRAW_END_ROM = 0x00077910


JUMP_DRAW_HOOK_ROM = 0x00077910


JUMP_DRAW_HOOK_V06 = bytes.fromhex("0C01DA47 00000000 00000000")


COMBOS_V06_SHA = "3e0d61654a06d068efb0f60d23d88dccb4ce99c1ea3fd580df22613ce983fe26"


SPECIALS_V06_SHA = "b940dc7d17e6ff9ebc409354a623e45ecdd348dbdaee013e2e39af6624d30274"


CURSOR_TABLE_ROM = 0x000AF824


CURSOR_TABLE_V06 = bytes.fromhex("00460037 0050005A 0050007D 005000A0")


CURSOR_TABLE_V09 = bytes.fromhex("00460032 00460046 0046005A 0046006E")


LABEL_X = 112


VALUE_X = 208


ROW0_Y = 50


ROW1_Y = 70


ROW2_Y = 90


ROW3_Y = 110


ROW4_Y = 130


WORD_PATCHES = {
    0x0007773C: (0x240500A0, 0x24050070),  # TURN label x
    0x00077790: (0x240500A0, 0x24050070),  # ATTACK label x
    0x000777E4: (0x240500A0, 0x24050070),  # SPECIALS label x
    0x00077748: (0x24060037, 0x24060032),  # TURN label y
    0x00077768: (0x24060037, 0x24060032),  # TURN value-related y
    0x0007779C: (0x2406005A, 0x24060046),  # ATTACK label y
    0x000777BC: (0x2406005A, 0x24060046),
    0x000777F0: (0x2406007D, 0x2406005A),  # SPECIALS label y
    0x00077810: (0x2406007D, 0x2406005A),
    0x00077854: (0x240500A0, 0x240500D0),  # TURN value x
    0x00077858: (0x24060046, 0x24060032),  # TURN value y
}


VALUES_REPACK_ROM = 0x000AF6D3


VALUES_REPACK_V06 = b"LOCK\x00ASSIST\x00\x00"


VALUES_REPACK_V09 = b"HOLD\x00AUTO\x00\x00\x00"


LOCK_PTR_ROM = 0x000AF700


LOCK_PTR_V06 = 0x800AEAD3


NOP = 0


def align(value: int, alignment: int = 4) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def pad(blob: bytes, size: int) -> bytes:
    if len(blob) > size:
        raise AssertionError(f"blob too large: {len(blob):#x} > {size:#x}")
    return blob + bytes(size - len(blob))


def _addr_hi(addr: int) -> int:
    return ((addr + 0x8000) >> 16) & 0xFFFF


def _addr_lo(addr: int) -> int:
    return addr & 0xFFFF


def build_right_edit_dispatch() -> bytes:
    """RIGHT: TURN or set ATTACK/SPECIALS/JUMP/RUN bit; EXIT inert."""
    e = Emitter()
    e.beq("s0", "zero", "turn")
    e.emit(sltiu("t0", "s0", 5))
    e.beq("t0", "zero", "done")
    e.emit(ori("t2", "zero", 0x0200))
    e.emit(
        sllv("t2", "t2", "s0"),
        lui("t0", 0x800A),
        lw("t1", STATE_VA - 0x800A0000, "t0"),
        addiu("t3", "zero", 3),
    )
    # JUMP can only be BUTTON when ATTACK+SPECIALS are both MODERN.
    e.bne("s0", "t3", "set")
    e.emit(andi("t4", "t1", ATTACK_MODERN_MASK | SPECIALS_MODERN_MASK))
    e.emit(addiu("t5", "zero", ATTACK_MODERN_MASK | SPECIALS_MODERN_MASK))
    e.bne("t4", "t5", "done")
    e.emit(NOP)
    e.label("set")
    e.emit(or_("t1", "t1", "t2"), sw("t1", STATE_VA - 0x800A0000, "t0"))
    e.label("done")
    e.emit(jump(RIGHT_DONE_VA), NOP)
    e.label("turn")
    e.emit(
        lui("t0", 0xA01B),
        addiu("t1", "zero", 1),
        sh("t1", SETTINGS_UNCACHED_VA - 0xA01B0000, "t0"),
        jump(RIGHT_DONE_VA),
        NOP,
    )
    return e.finish()


def build_left_edit_dispatch() -> bytes:
    """LEFT: TURN or clear ATTACK/SPECIALS/JUMP/RUN; classic ATTACK/SPECIALS clear JUMP."""
    e = Emitter()
    e.beq("s0", "zero", "turn")
    e.emit(sltiu("t0", "s0", 5))
    e.beq("t0", "zero", "done")
    e.emit(ori("t2", "zero", 0x0200))
    e.emit(sllv("t2", "t2", "s0"), sltiu("t4", "s0", 3))
    e.beq("t4", "zero", "mask_ready")
    e.emit(NOP)
    e.emit(ori("t2", "t2", JUMP_BUTTON_MASK))
    e.label("mask_ready")
    e.emit(
        xori("t2", "t2", 0xFFFF),
        lui("t0", 0x800A),
        lw("t1", STATE_VA - 0x800A0000, "t0"),
        and_("t1", "t1", "t2"),
        sw("t1", STATE_VA - 0x800A0000, "t0"),
    )
    e.label("done")
    e.emit(jump(LEFT_DONE_VA), NOP)
    e.label("turn")
    e.emit(
        *address_words("t0", SETTINGS_UNCACHED_VA),
        sh("zero", 0, "t0"),
        jump(LEFT_DONE_VA),
        NOP,
    )
    return e.finish()


def build_cursor_helper() -> bytes:
    """Rows 0..3 -> GAME SETTINGS type2; RUN/EXIT -> stock OPTIONS type0."""
    e = Emitter()
    e.emit(
        sltiu("t0", "s0", 4),
        sll("t1", "t0", 1),
        sw("s0", 0x6F4, "fp"),
        jr("ra"),
        sw("t1", 0x6F8, "fp"),
    )
    return e.finish()


def build_jump_run_draw_helper(cursor_va: int) -> bytes:
    """Draw JUMP/RUN rows without assuming caller-saved registers survive renderer calls.

    s1 is already copied to stack+0x18 as the renderer's sixth argument. We use
    s1 as our only cross-render-call scratch because native callees must preserve
    it, then restore the caller's original s1 from that same saved stack word.
    """
    e = Emitter()
    e.emit(addiu("sp", "sp", -0x20), sw("ra", 0x1C, "sp"))
    e.emit(sw("s7", 16, "sp"), sw("s6", 20, "sp"), sw("s1", 24, "sp"))

    # JUMP label. Delay slot prepares RUN label upper half in callee-saved s1.
    e.emit(
        *address_words("a0", JUMP_LABEL_VA),
        addiu("a1", "zero", LABEL_X),
        addiu("a2", "zero", ROW3_Y),
        addiu("a3", "zero", 1),
        jal(GAME_TEXT_DRAW_VA),
        lui("s1", _addr_hi(RUN_LABEL_VA)),
    )

    # RUN label. Delay slot repurposes s1 as the durable-settings upper base;
    # renderer preserves s1, so the following load is safe.
    e.emit(
        addiu("a0", "s1", _addr_lo(RUN_LABEL_VA)),
        addiu("a1", "zero", LABEL_X),
        addiu("a2", "zero", ROW4_Y),
        addiu("a3", "zero", 1),
        jal(GAME_TEXT_DRAW_VA),
        lui("s1", 0x800A),
    )

    # JUMP value, including accepted disabled-grey DPAD behavior.
    e.emit(
        lw("t1", STATE_VA - 0x800A0000, "s1"),
        andi("t2", "t1", ATTACK_MODERN_MASK | SPECIALS_MODERN_MASK),
        addiu("t3", "zero", ATTACK_MODERN_MASK | SPECIALS_MODERN_MASK),
        *address_words("a0", DPAD_VALUE_VA),
        *address_words("t4", VALUE_STYLE_VA),
    )
    e.bne("t2", "t3", "jump_disabled")
    e.emit(andi("t2", "t1", JUMP_BUTTON_MASK))
    e.beq("t2", "zero", "jump_draw")
    e.emit(NOP)
    e.emit(addiu("a0", "a0", 5))  # DPAD\0 -> BUTTON\0
    e.beq("zero", "zero", "jump_draw")
    e.emit(NOP)
    e.label("jump_disabled")
    e.emit(addu("t4", "s7", "zero"))
    e.label("jump_draw")
    e.emit(
        addiu("a1", "zero", VALUE_X),
        addiu("a2", "zero", ROW3_Y),
        addiu("a3", "zero", 1),
        sw("t4", 16, "sp"),
        addiu("t0", "zero", 10),
        sw("t0", 20, "sp"),
        jal(GAME_TEXT_DRAW_VA),
        NOP,
    )

    # RUN value. s1 survives the preceding renderer, so reload state safely.
    e.emit(
        lw("t1", STATE_VA - 0x800A0000, "s1"),
        andi("t2", "t1", RUN_AUTO_MASK),
        *address_words("a0", HOLD_VALUE_VA),
    )
    e.beq("t2", "zero", "run_ptr_done")
    e.emit(lui("t4", _addr_hi(VALUE_STYLE_VA)))
    e.emit(addiu("a0", "a0", 5))
    e.label("run_ptr_done")
    e.emit(
        addiu("t4", "t4", _addr_lo(VALUE_STYLE_VA)),
        addiu("a1", "zero", VALUE_X),
        addiu("a2", "zero", ROW4_Y),
        addiu("a3", "zero", 1),
        sw("t4", 16, "sp"),
        addiu("t0", "zero", 10),
        jal(GAME_TEXT_DRAW_VA),
        sw("t0", 20, "sp"),
        jal(cursor_va),
        NOP,
        lw("ra", 0x1C, "sp"),
        lw("s1", 0x18, "sp"),
        jr("ra"),
        addiu("sp", "sp", 0x20),
    )
    return e.finish()


def build_attack_value_draw() -> bytes:
    return words_blob(
        [
            lui("v0", 0x800A),
            lw("v0", STATE_VA - 0x800A0000, "v0"),
            andi("v0", "v0", ATTACK_MODERN_MASK),
            srl("v0", "v0", 10),
            sll("v0", "v0", 2),
            addu("v0", "v0", "s5"),
            lw("a0", 16, "v0"),
            addiu("a1", "zero", VALUE_X),
            addiu("a2", "zero", ROW1_Y),
            addiu("a3", "zero", 1),
            *address_words("t0", VALUE_STYLE_VA),
            sw("t0", 16, "sp"),
            addiu("t0", "zero", 10),
            sw("t0", 20, "sp"),
            jal(GAME_TEXT_DRAW_VA),
            sw("s1", 24, "sp"),
        ]
    )


def build_specials_value_draw() -> bytes:
    return words_blob(
        [
            lui("v0", 0x800A),
            lw("v0", STATE_VA - 0x800A0000, "v0"),
            andi("v0", "v0", SPECIALS_MODERN_MASK),
            srl("v0", "v0", 10),
            sll("v0", "v0", 2),
            addu("v0", "v0", "s5"),
            lw("a0", 16, "v0"),
            addiu("a1", "zero", VALUE_X),
            addiu("a2", "zero", ROW2_Y),
            addiu("a3", "zero", 1),
            *address_words("t0", VALUE_STYLE_VA),
            sw("t0", 16, "sp"),
            addiu("t0", "zero", 10),
            sw("t0", 20, "sp"),
            jal(GAME_TEXT_DRAW_VA),
            sw("s1", 24, "sp"),
        ]
    )

