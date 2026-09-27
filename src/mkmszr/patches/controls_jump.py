"""Native controls emitters ported from the accepted manual-test composition.

The emitters retain their confirmed MIPS instructions and stock callbacks.
"""
from __future__ import annotations

from ..mips import Emitter, addiu, address_words, addu, andi, jr, lhu, lw, ori

FILE_ROM = 0x00F68000


FILE_ENTRY_ROM = 0x000A5148


MODULE_K0 = 0x801AF820


V04_FILE_END = 0x00F68CB0


TOASTY_ROM = 0x00F687E0


STATE_VA = 0x800A60E8


ATTACK_MODERN_MASK = 0x0400


SPECIALS_MODERN_MASK = 0x0800


JUMP_BUTTON_MASK = 0x1000


MODERN_LP_MASK = ATTACK_MODERN_MASK | SPECIALS_MODERN_MASK


CURRENT_CONTROLLER_PTR_VA = 0x802ECE20


PLAYER_CONTROLLER_PTR_VA = 0x802C1AC0


SEMANTIC_INPUT_VA = 0x800BF2EE


MOVE_JUMP_CLASSIFIER_VA = 0x8002B1F8


MOVE_JUMP_CLASSIFIER_ROM = MOVE_JUMP_CLASSIFIER_VA - 0x7FFFF400


MOVE_JUMP_EXPECTED = bytes.fromhex('3C02802F 8C42CE20 8C420638 94440000')


BLOCK_START_VA = 0x80032810


BLOCK_START_ROM = BLOCK_START_VA - 0x7FFFF400


BLOCK_START_EXPECTED = bytes.fromhex('3C04802F 8C84CE20 27BDFFE8 AFBF0010')


PREP_ACTION_VA = 0x80032AF8


STOP_FIGHTER_VA = 0x8002B1C0


SELECT_ANIM_VA = 0x8002FE54


ADVANCE_ANIM_VA = 0x800304C0


PROCESS_SLEEP_VA = 0x80028794


LP_ACTION_INTERNAL_VA = 0x8002A0B4


NOP = 0


def emit_tail_jump(e: Emitter, target: int) -> None:
    e.emit(*address_words('t9', target), jr('t9'), NOP)


def build_move_jump_classifier() -> bytes:
    """Stock 0x8002B1F8 with BUTTON-mode substitution.

    Stock result: 1 for Up+Right, 2 for Up+Left, 0 otherwise.
    BUTTON result: 1 for (HK|LK)+Right, 2 for (HK|LK)+Left, 0 otherwise.
    This preserves the caller's existing forward/back/run jump branches.
    """
    e = Emitter()
    e.emit(*address_words('t0', CURRENT_CONTROLLER_PTR_VA), lw('t0', 0, 't0'),
           *address_words('t1', PLAYER_CONTROLLER_PTR_VA), lw('t1', 0, 't1'))
    e.bne('t0', 't1', 'classic_load'); e.emit(NOP)
    e.emit(lw('t2', 0x638, 't0'), lhu('a0', 0, 't2'))
    e.emit(*address_words('t0', STATE_VA), lw('t0', 0, 't0'), andi('t0', 't0', JUMP_BUTTON_MASK))
    e.beq('t0', 'zero', 'classic'); e.emit(NOP)

    # BUTTON: no kick button => no jump, even if Up is held.
    e.emit(andi('t0', 'a0', 0x0060))
    e.beq('t0', 'zero', 'none'); e.emit(NOP)
    e.emit(andi('t0', 'a0', 0x2000))
    e.bne('t0', 'zero', 'right'); e.emit(NOP)
    e.emit(andi('t0', 'a0', 0x8000))
    e.bne('t0', 'zero', 'left'); e.emit(NOP)
    e.beq('zero', 'zero', 'none'); e.emit(NOP)

    # Exact stock truth table for DPAD mode. Non-player callers reload the
    # current controller's own semantic input before using stock semantics.
    e.label('classic_load')
    e.emit(lw('t2', 0x638, 't0'), lhu('a0', 0, 't2'))
    e.label('classic')
    e.emit(andi('t0', 'a0', 0x3000), addiu('t1', 'zero', 0x3000))
    e.beq('t0', 't1', 'right'); e.emit(NOP)
    e.emit(andi('t0', 'a0', 0x9000), ori('t1', 'zero', 0x9000))
    e.beq('t0', 't1', 'left'); e.emit(NOP)

    e.label('none')
    e.emit(addu('v0', 'zero', 'zero'), jr('ra'), NOP)
    e.label('right')
    e.emit(addiu('v0', 'zero', 1), jr('ra'), NOP)
    e.label('left')
    e.emit(addiu('v0', 'zero', 2), jr('ra'), NOP)
    return e.finish()
