"""Native controls emitters ported from the accepted manual-test composition.

The emitters retain their confirmed MIPS instructions and stock callbacks.
"""
from __future__ import annotations

from ..mips import Emitter, addiu, address_words, addu, andi, jr, lhu, lui, lw, sw
from . import controls_specials_v03 as v03
from . import game_settings_turn as turn
FILE_ROM = v03.FILE_ROM


FILE_ENTRY_ROM = v03.FILE_ENTRY_ROM


MODULE_K0 = v03.MODULE_K0


V03_FILE_END = 0x00F68BF0


WRAPPER_ROM = v03.WRAPPER_ROM


WRAPPER_SLOT_END = 0x00F686C0


EVENT_ROM = 0x00F68AD0


EVENT_SLOT_END = V03_FILE_END


STATE_VA = v03.STATE_VA


ATTACK_MODERN_MASK = v03.ATTACK_MODERN_MASK


SPECIALS_MODERN_MASK = v03.SPECIALS_MODERN_STATE_MASK


JUMP_BUTTON_MASK = 0x1000


SEMANTIC_INPUT_VA = v03.SEMANTIC_INPUT_VA


DISPATCH_VA = v03.DISPATCH_VA


MAP_AIR = v03.MAP_AIR


MAP_SOMERSAULT = v03.MAP_SOMERSAULT


LP_CALL_RETURN = v03.LP_CALL_RETURN


HK_CALL_RETURN = v03.HK_CALL_RETURN


LK_CALL_RETURN = v03.LK_CALL_RETURN


JUMP_DECISION_ROM = 0x00029DDC


JUMP_DECISION_EXPECTED = bytes.fromhex('30621000 14400167 30624000 144001BC')


JUMP_UP_STOCK_VA = 0x80029780


JUMP_BUTTON_ENTRY_VA = 0x8002983C  # stock non-attached Up path after +0x6B0 gate


DOWN_STOCK_VA = 0x800298DC


JUMP_DECISION_RESUME_VA = 0x800291EC


CURRENT_CONTROLLER_PTR_VA = 0x802ECE20


WRAPPER_V03_SHA = 'd3e541b3012c34a73135db2054ed21e3a6d7db140110d083997765398efc0aa3'


EVENT_V03_SHA = '6812cfd45f22c77f48fcd84f3c1cb3d146cdc90d3a69f7e1581827566fa90f5b'


NOP = 0


def emit_tail_jump(e: Emitter, target: int) -> None:
    e.emit(*address_words('t9', target), jr('t9'), NOP)


def build_attack_wrapper() -> bytes:
    """Accepted v03 raw-action gate, with explicit JUMP:BUTTON HK/LK ownership."""
    e = Emitter()
    e.emit(addiu('sp','sp',-0x10), sw('t0',0,'sp'), sw('t1',4,'sp'))
    e.emit(lw('t0',0x638,'s1'), *address_words('t1', turn.PLAYER_SEMANTIC_INPUT_VA))
    e.bne('t0','t1','stock'); e.emit(NOP)

    e.emit(*address_words('t0',STATE_VA), lw('t1',0,'t0'))
    e.emit(lw('t0',0x44,'sp'))

    # LP physical button belongs to Special whenever either modern system owns it.
    e.emit(*address_words('t9', LP_CALL_RETURN)); e.bne('t0','t9','not_lp'); e.emit(NOP)
    e.emit(andi('t9','t1',ATTACK_MODERN_MASK | SPECIALS_MODERN_MASK))
    e.bne('t9','zero','suppress'); e.emit(NOP)
    e.beq('zero','zero','stock'); e.emit(NOP)

    # HK/LK are unavailable as ordinary attacks under ATTACK:MODERN, and are
    # explicitly owned by Jump when JUMP:BUTTON is selected.
    e.label('not_lp')
    e.emit(andi('t9','t1',ATTACK_MODERN_MASK | JUMP_BUTTON_MASK)); e.beq('t9','zero','stock'); e.emit(NOP)
    e.emit(*address_words('t9', HK_CALL_RETURN)); e.beq('t0','t9','suppress'); e.emit(NOP)
    e.emit(*address_words('t9', LK_CALL_RETURN)); e.beq('t0','t9','suppress'); e.emit(NOP)

    e.label('stock')
    e.emit(lw('t0',0,'sp'), lw('t1',4,'sp'), addiu('sp','sp',0x10),
           *address_words('t9',turn.ACTION_ENTRY), jr('t9'), NOP)
    e.label('suppress')
    e.emit(lw('t0',0,'sp'), lw('t1',4,'sp'), addiu('sp','sp',0x10),
           *address_words('t9',turn.ACTION_SUPPRESS_RESUME_VA), jr('t9'), NOP)
    return e.finish()


def build_event_helper() -> bytes:
    """Accepted v03 Attack translator, with immediate Block+Attack -> LP."""
    e = Emitter()
    e.emit(*address_words('t0', STATE_VA), lw('t1', 0, 't0'))
    e.emit(*address_words('t2', SEMANTIC_INPUT_VA), lhu('t3', 0, 't2'))

    # Immediate Block+Attack -> LP. This intentionally does NOT wait for the
    # controller to reach stock Block state 0x0B; semantic Block held is enough.
    e.emit(andi('t4', 't1', ATTACK_MODERN_MASK | SPECIALS_MODERN_MASK))
    e.beq('t4', 'zero', 'attack_mode'); e.emit(NOP)
    e.emit(andi('t4', 't3', 0x0008))
    e.beq('t4', 'zero', 'attack_mode'); e.emit(NOP)
    e.emit(addiu('a0', 'zero', 1))
    e.beq('zero', 'zero', 'dispatch'); e.emit(NOP)

    e.label('attack_mode')
    e.emit(andi('t4', 't1', ATTACK_MODERN_MASK))
    e.beq('t4', 'zero', 'dispatch'); e.emit(NOP)
    e.emit(lui('t0', 0x802C), lw('t0', 0x1AC0, 't0'))

    e.emit(lui('t4', 0x802E), lw('t4', 0x7DFC, 't4'))
    e.emit(*address_words('t5', MAP_AIR)); e.beq('t4', 't5', 'air'); e.emit(NOP)
    e.emit(*address_words('t5', MAP_SOMERSAULT)); e.beq('t4', 't5', 'air'); e.emit(NOP)
    e.emit(*address_words('t5', 0x8009F9E8)); e.bne('t4', 't5', 'dispatch'); e.emit(NOP)
    e.emit(andi('t5', 't3', 0xA000)); e.beq('t5', 'zero', 'dispatch'); e.emit(NOP)
    e.emit(lw('t5', 0x704, 't0'))
    e.beq('t5', 'zero', 'forward'); e.emit(NOP)

    # Backward accepted behavior: Run held => Roundhouse, otherwise Sweep.
    e.emit(andi('t5', 't3', 0x0004)); e.beq('t5', 'zero', 'sweep'); e.emit(NOP)
    e.emit(addiu('a0', 'zero', 3)); e.beq('zero', 'zero', 'dispatch'); e.emit(NOP)
    e.label('sweep')
    e.emit(addiu('a0', 'zero', 4)); e.beq('zero', 'zero', 'dispatch'); e.emit(NOP)

    e.label('forward')
    # Forward+Run+Attack remains permanently removed.
    e.beq('zero', 'zero', 'dispatch'); e.emit(NOP)

    e.label('air')
    e.emit(andi('t4', 't3', 0x4000)); e.beq('t4', 'zero', 'dispatch'); e.emit(NOP)
    e.emit(addiu('a0', 'zero', 3))

    e.label('dispatch')
    e.emit(*address_words('t9', DISPATCH_VA), jr('t9'), NOP)
    return e.finish()


def build_jump_helper() -> bytes:
    """Translate DPAD/BUTTON Jump selection at the stock Up/Down decision seam."""
    e = Emitter()
    # Load current semantic input and durable settings fresh.
    e.emit(*address_words('t0', CURRENT_CONTROLLER_PTR_VA), lw('t0',0,'t0'),
           lw('t2',0x638,'t0'), lhu('t3',0,'t2'),
           *address_words('t4', STATE_VA), lw('t4',0,'t4'), andi('t4','t4',JUMP_BUTTON_MASK))
    e.beq('t4','zero','classic'); e.emit(NOP)

    # BUTTON mode: either HK or LK (0x20|0x40) enters the native non-attached
    # jump path directly. Their ordinary attack events are suppressed above.
    e.emit(andi('t5','t3',0x0060))
    e.bne('t5','zero','button_jump'); e.emit(NOP)

    # D-pad Up no longer jumps. Preserve stock Up only while +0x6B0 says the
    # controller is in an attached/contextual state (rope/attachment family).
    e.emit(andi('t5','t3',0x1000))
    e.beq('t5','zero','check_down'); e.emit(NOP)
    e.emit(lhu('t5',0x6B0,'t0'))
    e.bne('t5','zero','stock_up'); e.emit(NOP)
    e.beq('zero','zero','check_down'); e.emit(NOP)

    e.label('classic')
    e.emit(andi('t5','t3',0x1000))
    e.bne('t5','zero','stock_up'); e.emit(NOP)

    e.label('check_down')
    e.emit(andi('t5','t3',0x4000))
    e.bne('t5','zero','stock_down'); e.emit(NOP)
    e.beq('zero','zero','resume'); e.emit(NOP)

    e.label('button_jump')
    # 0x8002983C is reached stock with v1=current controller from 0x80029780.
    # Re-establish that exact prerequisite because BUTTON mode bypasses it.
    e.emit(addu('v1','t0','zero'))
    emit_tail_jump(e, JUMP_BUTTON_ENTRY_VA)
    e.label('stock_up'); emit_tail_jump(e, JUMP_UP_STOCK_VA)
    e.label('stock_down'); emit_tail_jump(e, DOWN_STOCK_VA)
    e.label('resume'); emit_tail_jump(e, JUMP_DECISION_RESUME_VA)
    return e.finish()

