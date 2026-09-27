"""Native controls emitters ported from the accepted manual-test composition.

The emitters retain their confirmed MIPS instructions and stock callbacks.
"""
from __future__ import annotations

from ..mips import Emitter, addiu, address_words, addu, andi, jal, jalr, jr, lhu, lui, lw, ori, sh, sw
FILE_ROM = 0x00F68000


FILE_ENTRY_ROM = 0x000A5148


MODULE_K0 = 0x801AF820


V09_FILE_END = 0x00F693F0


STATE_VA = 0x800A60E8


ATTACK_MODERN_MASK = 0x0400


SPECIALS_MODERN_MASK = 0x0800


RUN_AUTO_MASK = 0x2000


MODERN_LP_MASK = ATTACK_MODERN_MASK | SPECIALS_MODERN_MASK


CURRENT_CONTROLLER_PTR_VA = 0x802ECE20


PLAYER_CONTROLLER_PTR_VA = 0x802C1AC0


SEMANTIC_INPUT_VA = 0x800BF2EE


RUN_PREDICATE_VA = 0x8002EAFC


RUN_PREDICATE_ROM = RUN_PREDICATE_VA - 0x7FFFF400


RUN_PREDICATE_EXPECTED = bytes.fromhex(
    "3C02802F 8C42CE20 944306D8 3C04800C 2484F2EC 24020001 50620001 "
    "24840002 94830000 30630004 10600002 24024000 34028000 03E00008 00000000"
)


RUN_CALL_ROMS = (0x00029FD8, 0x0002A0A0, 0x0002A738, 0x0002A7C4)


RUN_CALL_EXPECTED = 0x0C00BABF  # jal 0x8002EAFC


RUN_LOOP_CLASSIFIER_ROM = 0x0002A2E8  # VA 0x800296E8


RUN_LOOP_CLASSIFIER_EXPECTED = 0x0C00AC7E  # jal 0x8002B1F8


RUN_LOOP_BACKEDGE_ROM = 0x0002A378  # VA 0x80029778


RUN_LOOP_BACKEDGE_EXPECTED = bytes.fromhex("0800A5AE 00000000")


RUN_LOOP_START_VA = 0x800296B8


WALK_REEVAL_VA = 0x800293A8


ACTION_HOOK_ROM = 0x0001674C


ACTION_HOOK_EXPECTED = bytes.fromhex("0C023ABA 00000000")  # jal 0x8008EAE8; nop


ACTION_RETURN_VA = 0x80015B54


INVENTORY_ACTION_VA = 0x8008EAE8


BOX_SETTINGS_MASK_ROM = 0x0009A6F4


BOX_SETTINGS_MASK_V09 = 0x31293E00


STATIC_DISPATCH_ROM = 0x00077668


STATIC_DISPATCH_VA = 0x80076A68


STATIC_LOOP_ROM = 0x00077678


STATIC_LOOP_VA = 0x80076A78


STATIC_TRAMPS_EXPECTED = b"\x00" * 0x20


LEFT_GAMEPLAY_TAIL_ROM = 0x00077688


LEFT_GAMEPLAY_TAIL = bytes.fromhex("2739FD30 03200008 00000000")


RIGHT_GAMEPLAY_TAIL_ROM = 0x000775D0


RIGHT_GAMEPLAY_TAIL = bytes.fromhex("2739FDA0 03200008 00000000")


BLOCK_HELPER_ROM = 0x00F68D70


BLOCK_HELPER_K1 = 0xA01B0590


BLOCK_HELPER_SIZE = 0x18C


BLOCK_HELPER_V09_SHA = "d446768865f85aa6963ce48d70767e53049078b906650130748af892560f7ebf"


BLOCK_START_VA = 0x80032810


BLOCK_START_ROM = BLOCK_START_VA - 0x7FFFF400


BLOCK_START_WRAPPER = bytes.fromhex("3C19A01B 27390590 03200008 00000000")


PLAYER_BLOCK_RETURN_VA = 0x80029C30


PREP_ACTION_VA = 0x80032AF8


STOP_FIGHTER_VA = 0x8002B1C0


SELECT_ANIM_VA = 0x8002FE54


ADVANCE_ANIM_VA = 0x800304C0


PROCESS_SLEEP_VA = 0x80028794


LP_ACTION_INTERNAL_VA = 0x8002A0B4


NOP = 0


def emit_tail_jump(e: Emitter, target: int) -> None:
    e.emit(*address_words("t9", target), jr("t9"), NOP)


def build_corrected_block_start_helper() -> bytes:
    """Interrupt normal-player Block startup; scripted/other callers stay stock.

    The old v05/v06 proof gated on controller+0x6DC == 0x000B. The player
    dispatcher clears +0x6DC before it reaches the Block call, so that gate is
    false on the actual startup path. v10 instead identifies the exact normal
    player Block caller by its preserved return address 0x80029C30, while also
    retaining actual-player and MODERN-control gates.
    """
    e = Emitter()

    e.emit(*address_words("t0", STATE_VA), lw("t0", 0, "t0"), andi("t0", "t0", MODERN_LP_MASK))
    e.beq("t0", "zero", "stock"); e.emit(NOP)
    e.emit(
        *address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"),
        *address_words("t1", PLAYER_CONTROLLER_PTR_VA), lw("t1", 0, "t1"),
    )
    e.bne("t0", "t1", "stock"); e.emit(NOP)
    e.emit(*address_words("t1", PLAYER_BLOCK_RETURN_VA))
    e.bne("ra", "t1", "stock"); e.emit(NOP)
    e.beq("zero", "zero", "modern"); e.emit(NOP)

    e.label("stock")
    # Replay displaced 0x80032810..0x8003281C then resume stock.
    e.emit(
        lui("a0", 0x802F), lw("a0", 0xCE20, "a0"),
        addiu("sp", "sp", -0x18), sw("ra", 0x10, "sp"),
    )
    emit_tail_jump(e, 0x80032820)

    e.label("modern")
    e.emit(addiu("sp", "sp", -0x20), sw("ra", 0x1C, "sp"), sw("zero", 0x18, "sp"))

    # Stock Block-start setup.
    e.emit(lui("t0", 0x802F), sh("zero", 0xCCC8, "t0"))
    e.emit(lui("t0", 0x800C), sh("zero", 0xF308, "t0"))
    e.emit(jal(PREP_ACTION_VA), NOP)
    e.emit(*address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"), lw("a0", 0x6E0, "t0"))
    e.emit(jal(STOP_FIGHTER_VA), NOP)
    e.emit(addu("a0", "zero", "zero"), addiu("a1", "zero", 0x0C), jal(SELECT_ANIM_VA), NOP)
    e.emit(
        *address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"),
        addiu("t1", "zero", 0x0700), sh("t1", 0x6AA, "t0"),
    )

    # Stock rate=3 normalizes to a two-tick wait. Split into sleep(1) ticks to
    # poll Block+Attack during either startup tick without changing cadence.
    e.label("loop")
    e.emit(
        *address_words("t0", SEMANTIC_INPUT_VA), lhu("t1", 0, "t0"),
        andi("t1", "t1", 0x0018), addiu("t2", "zero", 0x0018),
    )
    e.beq("t1", "t2", "cancel"); e.emit(NOP)

    e.emit(lw("t0", 0x18, "sp"))
    e.beq("t0", "zero", "advance"); e.emit(NOP)
    e.emit(addiu("a0", "zero", 1), jal(PROCESS_SLEEP_VA), NOP)
    e.emit(lw("t0", 0x18, "sp"), addiu("t0", "t0", -1), sw("t0", 0x18, "sp"))
    e.beq("zero", "zero", "loop"); e.emit(NOP)

    e.label("advance")
    e.emit(*address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"), lw("a0", 0x6E0, "t0"))
    e.emit(jal(ADVANCE_ANIM_VA), NOP, addu("t3", "v0", "zero"))
    e.emit(andi("t0", "t3", 0x0003), addiu("t1", "zero", 2))
    e.beq("t0", "t1", "done"); e.emit(NOP)
    e.emit(andi("t0", "t3", 0xC000), addiu("t1", "zero", 0x4000))
    e.bne("t0", "t1", "loop"); e.emit(NOP)
    e.emit(addiu("t0", "zero", 2), sw("t0", 0x18, "sp"))
    e.beq("zero", "zero", "loop"); e.emit(NOP)

    e.label("done")
    e.emit(lw("ra", 0x1C, "sp"), addiu("sp", "sp", 0x20), jr("ra"), NOP)

    e.label("cancel")
    e.emit(lw("ra", 0x1C, "sp"), addiu("sp", "sp", 0x20))
    emit_tail_jump(e, LP_ACTION_INTERNAL_VA)
    return e.finish()


def build_capture_wrapper(run_button_state_va: int) -> bytes:
    """Snapshot configured/remapped physical Run before analog synthesis."""
    e = Emitter()
    e.emit(
        *address_words("t0", SEMANTIC_INPUT_VA),
        lhu("t1", 0, "t0"),
        andi("t1", "t1", 0x0004),
        *address_words("t0", run_button_state_va),
        sw("t1", 0, "t0"),
        *address_words("t9", INVENTORY_ACTION_VA),
        jr("t9"),
        NOP,
    )
    return e.finish()


def build_run_decision_helper(run_button_state_va: int) -> bytes:
    """HOLD delegates to stock; AUTO changes locomotion only for actual player."""
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x20),
        sw("ra", 0x1C, "sp"),
        sw("t0", 0x18, "sp"),
        sw("t1", 0x14, "sp"),
        sw("t2", 0x10, "sp"),
        *address_words("t9", RUN_PREDICATE_VA),
        jalr("t9"),
        NOP,
        *address_words("t0", STATE_VA),
        lw("t1", 0, "t0"),
        andi("t1", "t1", RUN_AUTO_MASK),
    )
    e.beq("t1", "zero", "done"); e.emit(NOP)
    e.emit(
        *address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"),
        *address_words("t1", PLAYER_CONTROLLER_PTR_VA), lw("t1", 0, "t1"),
    )
    e.bne("t0", "t1", "done"); e.emit(NOP)
    e.emit(*address_words("t0", run_button_state_va), lw("t1", 0, "t0"))
    e.beq("t1", "zero", "auto_run"); e.emit(NOP)
    e.emit(ori("v0", "zero", 0x4000))  # physical Run held => Walk
    e.beq("zero", "zero", "done"); e.emit(NOP)
    e.label("auto_run")
    e.emit(ori("v0", "zero", 0x8000))  # physical Run released => Run
    e.label("done")
    e.emit(
        lw("t2", 0x10, "sp"),
        lw("t1", 0x14, "sp"),
        lw("t0", 0x18, "sp"),
        lw("ra", 0x1C, "sp"),
        addiu("sp", "sp", 0x20),
        jr("ra"),
        NOP,
    )
    return e.finish()


def build_run_backedge_helper(run_button_state_va: int) -> bytes:
    """Post-classifier AUTO Run->Walk transition; preserve original back-edge otherwise."""
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x10),
        sw("t0", 0x0C, "sp"),
        sw("t1", 0x08, "sp"),
        sw("t2", 0x04, "sp"),
        *address_words("t0", STATE_VA),
        lw("t1", 0, "t0"),
        andi("t1", "t1", RUN_AUTO_MASK),
    )
    e.beq("t1", "zero", "normal"); e.emit(NOP)
    e.emit(
        *address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"),
        *address_words("t1", PLAYER_CONTROLLER_PTR_VA), lw("t1", 0, "t1"),
    )
    e.bne("t0", "t1", "normal"); e.emit(NOP)
    e.emit(*address_words("t0", run_button_state_va), lw("t1", 0, "t0"))
    e.beq("t1", "zero", "normal"); e.emit(NOP)

    e.emit(
        lw("t2", 0x04, "sp"), lw("t1", 0x08, "sp"), lw("t0", 0x0C, "sp"),
        addiu("sp", "sp", 0x10),
        *address_words("t9", WALK_REEVAL_VA), jr("t9"), NOP,
    )

    e.label("normal")
    e.emit(
        lw("t2", 0x04, "sp"), lw("t1", 0x08, "sp"), lw("t0", 0x0C, "sp"),
        addiu("sp", "sp", 0x10),
        *address_words("t9", RUN_LOOP_START_VA), jr("t9"), NOP,
    )
    return e.finish()


def build_runtime_dispatcher(decision_k1: int, capture_k1: int) -> bytes:
    """JAL trampoline: action-hook RA selects capture; all Run calls use decision."""
    e = Emitter()
    e.emit(*address_words("t0", ACTION_RETURN_VA))
    e.beq("ra", "t0", "capture"); e.emit(NOP)
    e.emit(*address_words("t9", decision_k1), jr("t9"), NOP)
    e.label("capture")
    e.emit(*address_words("t9", capture_k1), jr("t9"), NOP)
    return e.finish()
