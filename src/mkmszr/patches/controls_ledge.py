"""Native controls emitters ported from the accepted manual-test composition.

The emitters retain their confirmed MIPS instructions and stock callbacks.
"""
from __future__ import annotations

from ..mips import Emitter, addiu, address_words, addu, andi, jal, jr, lhu, lw, ori
from . import controls_specials_v03 as v03

FILE_ROM = 0x00F68000


FILE_ENTRY_ROM = 0x000A5148


MODULE_K0 = 0x801AF820


V05_FILE_END = 0x00F68F00


STATE_VA = 0x800A60E8


JUMP_BUTTON_MASK = 0x1000


CURRENT_CONTROLLER_PTR_VA = 0x802ECE20


PLAYER_CONTROLLER_PTR_VA = 0x802C1AC0


LEDGE_STATE = 0x030F


NOP = 0


SPECIAL_CALL_HOOK_ROM = 0x0001645C


SPECIAL_CALL_V05 = bytes.fromhex('3C19A01B2739FEE00320F80900000000')


LEDGE_INPUT_HOOK_VA = 0x8002AE5C


LEDGE_INPUT_HOOK_ROM = LEDGE_INPUT_HOOK_VA - 0x7FFFF400


LEDGE_INPUT_EXPECTED = bytes.fromhex('3C04802F8C84CE208C82063894430000')


LEDGE_STOCK_CHECK_VA = 0x8002AE6C


LEDGE_UP_BODY_VA = 0x8002AE78


def emit_tail_jump(e: Emitter, target: int) -> None:
    e.emit(*address_words('t9', target), jr('t9'), NOP)


def build_ledge_input_helper() -> bytes:
    """Alias HK/LK to the ledge loop's native Up branch in BUTTON mode."""
    e = Emitter()
    # Re-establish the four displaced stock instructions first.
    e.emit(*address_words('a0', CURRENT_CONTROLLER_PTR_VA), lw('a0', 0, 'a0'),
           lw('v0', 0x638, 'a0'), lhu('v1', 0, 'v0'))

    # Only the actual player and JUMP:BUTTON gain the alias. Scripted/non-player
    # uses of this code path keep stock semantics.
    e.emit(*address_words('t0', PLAYER_CONTROLLER_PTR_VA), lw('t0', 0, 't0'))
    e.bne('a0', 't0', 'stock'); e.emit(NOP)
    e.emit(*address_words('t0', STATE_VA), lw('t0', 0, 't0'), andi('t0', 't0', JUMP_BUTTON_MASK))
    e.beq('t0', 'zero', 'stock'); e.emit(NOP)

    # HK or LK acts exactly like the stock Up decision from this hanging loop.
    e.emit(andi('t0', 'v1', 0x0060))
    e.bne('t0', 'zero', 'button_up'); e.emit(NOP)

    e.label('stock')
    emit_tail_jump(e, LEDGE_STOCK_CHECK_VA)
    e.label('button_up')
    emit_tail_jump(e, LEDGE_UP_BODY_VA)
    return e.finish()


def build_specials_helper_v06() -> bytes:
    """Accepted v03 SPECIALS helper plus one ledge-state Ice-Up override."""
    e = Emitter()
    e.emit(addu('t8','v0','zero'), *address_words('t0',v03.STATE_VA), lw('t1',0,'t0'),
           andi('t1','t1',v03.SPECIALS_MODERN_STATE_MASK))
    e.bne('t1','zero','modern'); e.emit(NOP)
    e.beq('t8','zero','return_direct'); e.emit(NOP)
    e.emit(jr('t8'), NOP)

    e.label('return_direct')
    e.emit(jr('ra'), NOP)

    e.label('modern')
    e.emit(*address_words('t0',v03.CURRENT_XP_VA), addiu('t1','zero',v03.XP_MAX), v03.sw('t1',0,'t0'))
    e.emit(addiu('t0','zero',1))
    e.bne('s2','t0','return_direct'); e.emit(NOP)
    e.emit(*address_words('t0',v03.SEMANTIC_INPUT_VA), lhu('t1',0,'t0'), andi('t2','t1',0x0080))
    e.beq('t2','zero','return_direct'); e.emit(NOP)

    e.emit(addiu('sp','sp',-0x20), v03.sw('ra',0x1C,'sp'))
    e.emit(*address_words('t0',v03.SEMANTIC_INPUT_VA), lhu('t1',0,'t0'))

    e.emit(andi('t2','t1',0x000C), addiu('t3','zero',0x000C))
    e.beq('t2','t3','spine'); e.emit(NOP)

    e.emit(andi('t2','t1',0x0048), addiu('t3','zero',0x0048))
    e.beq('t2','t3','maybe_old_chord'); e.emit(NOP)
    e.emit(andi('t2','t1',0x0018), addiu('t3','zero',0x0018))
    e.bne('t2','t3','history'); e.emit(NOP)
    e.label('maybe_old_chord')
    e.emit(andi('t2','t1',0xA000))
    e.beq('t2','zero','history'); e.emit(NOP)
    e.emit(v03.lui('t2',0x802C), lw('t2',0x1AC0,'t2'), lw('t2',0x704,'t2'))
    e.bne('t2','zero','done'); e.emit(NOP)

    e.label('history')
    for rec, next_label in [(v03.LP_RECORD_ICE_BLAST,'check_clone_history'), (v03.LP_RECORD_ICE_CLONE,'after_history')]:
        e.emit(addiu('a0','zero',0x80), addiu('a1','zero',0x80), *address_words('a2',rec+0x10), jal(v03.MATCHER_VA), NOP)
        e.emit(andi('v0','v0',0xFFFF), ori('t0','zero',0x8000))
        e.beq('v0','t0','done'); e.emit(NOP)
        e.label(next_label)

    e.emit(*address_words('t0',v03.SEMANTIC_INPUT_VA), lhu('t1',0,'t0'))

    # v06-only: action state 0x030F is the stock ledge-hang loop. Before the
    # normal air/ground classifier, allow the exact modern ground chord
    # Block + Forward + Special to route to Directional Ice Up. Preserve
    # Action+Special priority and do not broaden the Back chord here.
    e.emit(*address_words('t0',PLAYER_CONTROLLER_PTR_VA), lw('t0',0,'t0'),
           lhu('t2',0x6AA,'t0'), addiu('t3','zero',LEDGE_STATE))
    e.bne('t2','t3','normal_context'); e.emit(NOP)
    e.emit(andi('t2','t1',0x0002))
    e.bne('t2','zero','normal_context'); e.emit(NOP)
    e.emit(andi('t2','t1',0x0008))
    e.beq('t2','zero','normal_context'); e.emit(NOP)
    e.emit(andi('t2','t1',0xA000))
    e.beq('t2','zero','normal_context'); e.emit(NOP)

    # Facing-relative Forward test, identical to the accepted v03 classifier.
    e.emit(lw('t3',0x6E0,'t0'), lhu('t4',0x8C,'t3'), andi('t4','t4',0x0010))
    e.emit(andi('t2','t1',0x2000))
    e.beq('t2','zero','ledge_left'); e.emit(NOP)
    # Right held: facing right (bit clear) means Forward.
    e.beq('t4','zero','ice_up'); e.emit(NOP)
    e.beq('zero','zero','normal_context'); e.emit(NOP)
    e.label('ledge_left')
    # Left held: facing left (bit set) means Forward.
    e.bne('t4','zero','ice_up'); e.emit(NOP)

    e.label('normal_context')
    e.emit(v03.lui('t0',0x802E), lw('t0',0x7DFC,'t0'))
    e.emit(*address_words('t2',v03.MAP_AIR)); e.beq('t0','t2','air'); e.emit(NOP)
    e.emit(*address_words('t2',v03.MAP_SOMERSAULT)); e.beq('t0','t2','air'); e.emit(NOP)

    e.emit(andi('t2','t1',0x0002)); e.bne('t2','zero','freeze'); e.emit(NOP)
    e.emit(andi('t2','t1',0x0008)); e.beq('t2','zero','ground_horizontal'); e.emit(NOP)
    e.emit(andi('t2','t1',0xA000)); e.beq('t2','zero','polar'); e.emit(NOP)
    e.beq('zero','zero','block_direction'); e.emit(NOP)

    e.label('ground_horizontal')
    e.emit(andi('t2','t1',0xA000)); e.beq('t2','zero','ice_blast'); e.emit(NOP)
    e.beq('zero','zero','ground_direction'); e.emit(NOP)

    e.label('air')
    e.emit(andi('t2','t1',0xA000)); e.beq('t2','zero','ice_blast'); e.emit(NOP)
    e.beq('zero','zero','air_direction'); e.emit(NOP)

    e.label('block_direction')
    e.emit(addiu('t6','zero',1)); e.beq('zero','zero','classify_direction'); e.emit(NOP)
    e.label('ground_direction')
    e.emit(addiu('t6','zero',2)); e.beq('zero','zero','classify_direction'); e.emit(NOP)
    e.label('air_direction')
    e.emit(addiu('t6','zero',3))

    e.label('classify_direction')
    e.emit(v03.lui('t3',0x802C), lw('t3',0x1AC0,'t3'), lw('t3',0x6E0,'t3'), lhu('t4',0x8C,'t3'), andi('t4','t4',0x0010))
    e.emit(andi('t2','t1',0x2000))
    e.beq('t2','zero','left_held'); e.emit(NOP)
    e.beq('t4','zero','dir_forward'); e.emit(NOP)
    e.beq('zero','zero','dir_back'); e.emit(NOP)
    e.label('left_held')
    e.beq('t4','zero','dir_back'); e.emit(NOP)
    e.beq('zero','zero','dir_forward'); e.emit(NOP)

    e.label('dir_forward')
    e.emit(addiu('t5','zero',1)); e.beq('t6','t5','ice_up'); e.emit(NOP)
    e.emit(addiu('t5','zero',3)); e.beq('t6','t5','ice_blast'); e.emit(NOP)
    e.emit(andi('t2','t1',0x0004)); e.bne('t2','zero','super_slide'); e.emit(NOP)
    e.beq('zero','zero','slide'); e.emit(NOP)

    e.label('dir_back')
    e.emit(addiu('t5','zero',1)); e.beq('t6','t5','ice_down'); e.emit(NOP)
    e.beq('zero','zero','ice_clone'); e.emit(NOP)

    v03.emit_condition_route(e,'spine',v03.COND_SPINE,v03.CB_SPINE,0)
    v03.emit_condition_route(e,'ice_blast',v03.COND_ICE_BLAST,v03.CB_ICE_BLAST,1)
    v03.emit_condition_route(e,'ice_clone',v03.COND_ICE_CLONE,v03.CB_ICE_CLONE,1)
    v03.emit_condition_route(e,'ice_up',v03.COND_ICE_UP,v03.CB_ICE_UP,0)
    v03.emit_condition_route(e,'ice_down',v03.COND_ICE_DOWN,v03.CB_ICE_DOWN,0)
    v03.emit_condition_route(e,'freeze',v03.COND_FREEZE,v03.CB_FREEZE,0)
    v03.emit_condition_route(e,'polar',v03.COND_POLAR,v03.CB_POLAR,0)

    e.label('slide')
    e.emit(*address_words('a0',v03.CURRENT_PROCESS_PTR_VA), lw('a0',0,'a0'), jal(v03.PREP_SPECIAL_VA), NOP)
    e.emit(addiu('a0','zero',0), *address_words('a1',v03.CB_SLIDE))
    e.beq('zero','zero','transfer'); e.emit(NOP)

    e.label('super_slide')
    e.emit(v03.lui('t0',0x802C), lw('t0',0x1AC0,'t0'), lhu('t1',0x656,'t0'), v03.sltiu('t2','t1',0x60))
    e.bne('t2','zero','done'); e.emit(NOP)
    e.emit(*address_words('a0',v03.CURRENT_PROCESS_PTR_VA), lw('a0',0,'a0'), jal(v03.PREP_SPECIAL_VA), NOP)
    e.emit(addiu('a0','zero',0), *address_words('a1',v03.CB_SUPER_SLIDE))
    e.beq('zero','zero','transfer'); e.emit(NOP)

    e.label('transfer')
    e.emit(lw('ra',0x1C,'sp'), addiu('sp','sp',0x20),
           *address_words('t9',v03.TRANSFER_VA), jr('t9'), NOP)
    e.label('done')
    e.emit(lw('ra',0x1C,'sp'), addiu('sp','sp',0x20), jr('ra'), NOP)
    return e.finish()
