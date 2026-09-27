"""Guarded five-setting controls and native gameplay composition.

Port of the accepted v02 composition; stock progression remains intact.
"""
from __future__ import annotations

from ..data.addresses import RESERVED_RDRAM_END_EXCLUSIVE
from ..mips import Emitter, addiu, address_words, jal, jr, jump, lui, lw, sw, words_blob
from ..rom import RomImage
from . import controls_actions as cv04
from . import controls_combo as attackv04
from . import controls_frontend as v09
from . import controls_jump as cv05
from . import controls_ledge as cv06
from . import controls_run as v10
from . import game_settings_turn as turn
from .base import PatchContext
from .toasty_constants import MODULE_K0 as TOASTY_K0
from .toasty_constants import MODULE_ROM as TOASTY_ROM

FILE_ROM=0x00F68000


FILE_ENTRY_ROM=0x000A5148


# Runtime end of the accepted v02 modern-controls extension. Optional
# post-controls features may use the guarded gap after this address while
# remaining below Toasty's fixed 0x801B1000 base.
CONTROLS_RUNTIME_END=0x801B0880


MODULE_K0=0x801AF820


RUN_AUTO_MASK=0x2000


CURRENT_CONTROLLER_PTR_VA=0x802ECE20


PLAYER_CONTROLLER_PTR_VA=0x802C1AC0


SEMANTIC_INPUT_VA=0x800BF2EE


RUN_PREDICATE_VA=0x8002EAFC


RUN_CALL_ROMS=(0x00029FD8,0x0002A0A0,0x0002A738,0x0002A7C4)


RUN_CALL_EXPECTED=0x0C00BABF


RUN_LOOP_CLASSIFIER_ROM=0x0002A2E8


RUN_LOOP_CLASSIFIER_EXPECTED=0x0C00AC7E


RUN_LOOP_BACKEDGE_ROM=0x0002A378


RUN_LOOP_BACKEDGE_EXPECTED=bytes.fromhex('0800A5AE 00000000')


RUN_LOOP_START_VA=0x800296B8


WALK_REEVAL_VA=0x800293A8


ACTION_INPUT_HOOK_ROM=0x0001674C


ACTION_INPUT_EXPECTED=bytes.fromhex('0C023ABA 00000000')


ACTION_INPUT_RETURN_VA=0x80015B54


INVENTORY_ACTION_VA=0x8008EAE8


EVENT_HOOK_ROM=0x00015738


EVENT_HOOK_EXPECTED=bytes.fromhex('0C005570 24070001')


EVENT_RETURN_VA=0x80014B40


COMBO_HOOK_ROM=0x0004E3AC


COMBO_HOOK_EXPECTED=bytes.fromhex('000210C0 8CA306E0')


BLOCK_STEADY_HOOK_ROM=0x0002A848


BLOCK_STEADY_EXPECTED=bytes.fromhex('30624000 1440FF23')


SPECIAL_CALL_HOOK_ROM=0x0001645C


SPECIAL_CALL_EXPECTED=bytes.fromhex('10400003 00000000 0040F809 00000000')


STAND_JUMP_HOOK_ROM=0x00029DDC


STAND_JUMP_EXPECTED=bytes.fromhex('30621000 14400167 30624000 144001BC')


MOVE_JUMP_HOOK_ROM=0x0002BDF8


MOVE_JUMP_EXPECTED=bytes.fromhex('3C02802F 8C42CE20 8C420638 94440000')


BLOCK_START_HOOK_ROM=0x00033410


BLOCK_START_EXPECTED=bytes.fromhex('3C04802F 8C84CE20 27BDFFE8 AFBF0010')


LEDGE_HOOK_ROM=0x0002BA5C


LEDGE_EXPECTED=bytes.fromhex('3C04802F 8C84CE20 8C820638 94430000')


RIGHT_TAIL_ROM=0x000775D0


LEFT_TAIL_ROM=0x00077688


STATIC_RUN_DISPATCH_ROM=0x00077668


STATIC_RUN_DISPATCH_VA=0x80076A68


STATIC_RUN_LOOP_ROM=0x00077678


STATIC_RUN_LOOP_VA=0x80076A78


ATTACK_LABEL_ROM=0x000AF71C


ATTACK_LABEL_EXPECTED=b'COMBOS\x00\x00'


ATTACK_LABEL=b'ATTACK\x00\x00'


ATTACK_MODERN_PTR_ROM=0x000AF708


ATTACK_ASSIST_PTR=0x800AEAD8


ATTACK_MODERN_PTR=0x800AEAE8


STEADY_BLOCK_BASE=bytes.fromhex(
    '3c08800a250860e88d09000031290400112000090000000030690018'
    '240a0018152a0005000000003c1980032739a0b40320000800000000'
    '3062400010400005000000003c198003273998dc0320000800000000'
    '306200013c19800327399c540320000800000000'
)


def align(v:int,a:int=16)->int:return (v+a-1)&~(a-1)


def runtime_for_rom(off:int)->int:return MODULE_K0+(off-FILE_ROM)


def rom_for_runtime(va:int)->int:return FILE_ROM+(va-MODULE_K0)


def k1(va:int)->int:return va|0x20000000


SLIDE_RECOGNIZER_VA=0x8003C9F8


SUPER_SLIDE_RECOGNIZER_VA=0x8003CAF4


def no_xp_specials(rom:RomImage)->bytes:
    """Accepted MODERN mapping with proof XP force removed and native Slide gates restored.

    The research helper routed Slide/Super Slide directly to their callbacks because
    the proof also forced XP=20000. In a real-progression build that bypasses the
    stock tier/context checks. Keep every label/offset stable, but replace only the
    two direct-route bodies with calls to the stock direct recognizers, which already
    own tier >=2 / tier >=7 and the remaining native eligibility checks.
    """
    blob=bytearray(cv06.build_specials_helper_v06())
    force=words_blob([
        *address_words('t0',0x8011200C),
        addiu('t1','zero',20000),
        sw('t1',0,'t0'),
    ])
    at=bytes(blob).find(force)
    if at<0 or bytes(blob).find(force,at+1)>=0:
        raise AssertionError('could not isolate proof-only XP-force sequence')
    blob[at:at+len(force)]=bytes(len(force))

    # These offsets are guarded against the exact accepted v06 helper. Keep the
    # existing label locations so all earlier classifier branches remain valid.
    slide_off=0x3E4
    super_off=0x40C
    transfer_off=0x44C
    done_off=0x464
    expected_slide=words_blob([
        0x3C04802F,0x2484CE20,0x8C840000,0x0C00CABE,0x00000000,
        0x24040000,0x3C058004,0x24A5CFAC,0x10000011,0x00000000,
    ])
    expected_super=words_blob([
        0x3C08802C,0x8D081AC0,0x95090656,0x2D2A0060,0x15400011,0x00000000,
        0x3C04802F,0x2484CE20,0x8C840000,0x0C00CABE,0x00000000,0x24040000,
        0x3C058006,0x24A5A5C0,0x10000001,0x00000000,
    ])
    if bytes(blob[slide_off:super_off])!=expected_slide:
        raise AssertionError('accepted Slide direct-route body drifted')
    if bytes(blob[super_off:transfer_off])!=expected_super:
        raise AssertionError('accepted Super Slide direct-route body drifted')
    if bytes(blob[done_off:done_off+0x10])!=bytes.fromhex('8FBF001C 27BD0020 03E00008 00000000'):
        raise AssertionError('SPECIALS done epilogue drifted')

    local_return=words_blob([
        jal(SLIDE_RECOGNIZER_VA),0,
        0x8FBF001C,0x27BD0020,0x03E00008,0,
    ])
    blob[slide_off:super_off]=local_return+bytes((super_off-slide_off)-len(local_return))
    local_return=words_blob([
        jal(SUPER_SLIDE_RECOGNIZER_VA),0,
        0x8FBF001C,0x27BD0020,0x03E00008,0,
    ])
    blob[super_off:transfer_off]=local_return+bytes((transfer_off-super_off)-len(local_return))

    # Static clean-ROM guards for the stock progression gates we now reuse:
    # Slide calls the native tier evaluator then rejects tier < 2.
    # Super Slide rejects tier < 7 and later rejects resource < 0x60.
    clean=rom.data
    def roff(va:int)->int:return va-0x7FFFF400
    if clean[roff(SLIDE_RECOGNIZER_VA)+0x2C:roff(SLIDE_RECOGNIZER_VA)+0x44] != bytes.fromhex(
        '0C01D3EF 00000000 28420002 1440002B 240500C8 3C02802F'
    ):
        raise AssertionError('stock Slide tier gate drifted')
    if clean[roff(SUPER_SLIDE_RECOGNIZER_VA)+0x2C:roff(SUPER_SLIDE_RECOGNIZER_VA)+0x3C] != bytes.fromhex(
        '0C01D3EF 00000000 28420007 1440002C'
    ):
        raise AssertionError('stock Super Slide tier gate drifted')
    if clean[roff(SUPER_SLIDE_RECOGNIZER_VA)+0xBC:roff(SUPER_SLIDE_RECOGNIZER_VA)+0xC8] != bytes.fromhex(
        '94820656 2C420060 14400009'
    ):
        raise AssertionError('stock Super Slide resource gate drifted')

    if force in blob:
        raise AssertionError('XP force remains in production candidate specials helper')
    return bytes(blob)


def steady_block()->bytes:
    b=bytearray(STEADY_BLOCK_BASE)
    if b[12:16]!=bytes.fromhex('31290400'): raise AssertionError('steady Block mask drift')
    b[12:16]=bytes.fromhex('31290C00')
    return bytes(b)


def capture_event_dispatch(event_k1:int)->bytes:
    e=Emitter()
    e.emit(addiu('sp','sp',-0x10),sw('t0',0,'sp'))
    e.emit(*address_words('t0',EVENT_RETURN_VA))
    e.beq('ra','t0','event'); e.emit(0)
    e.emit(*address_words('t9',turn.CAPTURE_ENTRY))
    e.beq('zero','zero','dispatch'); e.emit(0)
    e.label('event'); e.emit(*address_words('t9',event_k1))
    e.label('dispatch'); e.emit(lw('t0',0,'sp'),addiu('sp','sp',0x10),jr('t9'),0)
    return e.finish()


def run_capture(state_va:int)->bytes:
    return v10.build_capture_wrapper(state_va)


def run_decision(state_va:int)->bytes:
    return v10.build_run_decision_helper(state_va)


def run_loop(state_va:int)->bytes:
    return v10.build_run_backedge_helper(state_va)


def run_dispatch(decision_k1:int,capture_k1:int)->bytes:
    return v10.build_runtime_dispatcher(decision_k1,capture_k1)


def trampoline(target_k1:int)->bytes:
    return words_blob([*address_words('t9',target_k1),jr('t9'),0])


class ControlsProductionPatch:
    """Enable the accepted menu, Attack, Specials, Jump, and Run behavior."""

    name = "controls-production-composition"

    def __init__(self, *, toasty_size:int|None=None):
        self.toasty_size=toasty_size

    def apply(self,rom:RomImage,context:PatchContext)->tuple[str,...]:
        del context
        if RESERVED_RDRAM_END_EXCLUSIVE!=0x801B3420 or TOASTY_K0!=0x801B1000:
            raise AssertionError("16 KiB controls/Toasty allocation drifted")
        baseline=bytes(rom.data)
        # Full product composition guards.
        rom.expect_u32(FILE_ENTRY_ROM,FILE_ROM)
        file_end=rom.read_u32(FILE_ENTRY_ROM+4)
        toasty_size=self.toasty_size
        if toasty_size is not None:
            if file_end!=TOASTY_ROM+toasty_size: raise AssertionError(f'unexpected CI4 Toasty file end {file_end:#x}')
        else:
            rom.expect_u32(FILE_ENTRY_ROM+4,FILE_ROM+len(turn.CONTROL_MODULE))
        rom.expect_u32(FILE_ENTRY_ROM+8,0)
        if rom.data[0x66F60:0x66F68]!=bytes.fromhex('3C02801B24423420'):
            raise AssertionError('16 KiB first arena guard failed')
        if rom.read_u32(0x66FE8)!=0x24423420:
            raise AssertionError('16 KiB bootstrap arena floor guard failed')

        # Stock/current-product gameplay seams.
        rom.expect_bytes(EVENT_HOOK_ROM,EVENT_HOOK_EXPECTED)
        rom.expect_bytes(SPECIAL_CALL_HOOK_ROM,SPECIAL_CALL_EXPECTED)
        rom.expect_bytes(ACTION_INPUT_HOOK_ROM,ACTION_INPUT_EXPECTED)
        rom.expect_bytes(BLOCK_STEADY_HOOK_ROM,BLOCK_STEADY_EXPECTED)
        rom.expect_bytes(STAND_JUMP_HOOK_ROM,STAND_JUMP_EXPECTED)
        rom.expect_bytes(MOVE_JUMP_HOOK_ROM,MOVE_JUMP_EXPECTED)
        rom.expect_bytes(BLOCK_START_HOOK_ROM,BLOCK_START_EXPECTED)
        rom.expect_bytes(LEDGE_HOOK_ROM,LEDGE_EXPECTED)
        rom.expect_bytes(COMBO_HOOK_ROM,COMBO_HOOK_EXPECTED)
        rom.expect_bytes(RUN_LOOP_BACKEDGE_ROM,RUN_LOOP_BACKEDGE_EXPECTED)
        rom.expect_u32(RUN_LOOP_CLASSIFIER_ROM,RUN_LOOP_CLASSIFIER_EXPECTED)
        for off in RUN_CALL_ROMS: rom.expect_u32(off,RUN_CALL_EXPECTED)

        # Production frontend state before promotion.
        rom.expect_bytes(RIGHT_TAIL_ROM,bytes(12)); rom.expect_bytes(LEFT_TAIL_ROM,bytes(12))
        rom.expect_bytes(ATTACK_LABEL_ROM,ATTACK_LABEL_EXPECTED)
        rom.expect_u32(ATTACK_MODERN_PTR_ROM,ATTACK_ASSIST_PTR)
        if rom.data[v09.RIGHT_EDIT_ROM:v09.RIGHT_EDIT_END_ROM] != turn.RIGHT_EDIT_BLOB:
            raise AssertionError('production right GAME SETTINGS body drifted')
        if rom.data[v09.LEFT_EDIT_ROM:v09.LEFT_EDIT_END_ROM] != turn.LEFT_EDIT_BLOB:
            raise AssertionError('production left GAME SETTINGS body drifted')

        # Build accepted helpers. Specials has only the 16-byte XP-force sequence removed.
        helpers=[
            ('event',cv04.build_event_helper()),
            ('attack-wrapper',cv04.build_attack_wrapper()),
            ('combo',attackv04.build_combo_helper()),
            ('steady-block',steady_block()),
            ('specials',no_xp_specials(rom)),
            ('standing-jump',cv04.build_jump_helper()),
            ('moving-jump',cv05.build_move_jump_classifier()),
            ('block-start',v10.build_corrected_block_start_helper()),
            ('ledge',cv06.build_ledge_input_helper()),
        ]

        cursor=align(turn.CONTROL_ALLOCATION.end_exclusive,16)
        alloc={}; blobs={}
        for name,blob in helpers:
            cursor=align(cursor,16); alloc[name]=cursor; blobs[name]=blob; cursor+=len(blob)

        # RUN state/helpers require resolved state VA; allocate sizes first with dummy state.
        rd0=run_decision(0x801AF000); rc0=run_capture(0x801AF000); rl0=run_loop(0x801AF000)
        cursor=align(cursor,16); alloc['run-decision']=cursor; cursor+=len(rd0)
        cursor=align(cursor,16); alloc['run-capture']=cursor; cursor+=len(rc0)
        cursor=align(cursor,16); alloc['run-loop']=cursor; cursor+=len(rl0)
        cursor=align(cursor,16); alloc['run-state']=cursor; state_va=cursor; cursor+=4
        rd=run_decision(state_va); rc=run_capture(state_va); rl=run_loop(state_va)
        if (len(rd),len(rc),len(rl))!=(len(rd0),len(rc0),len(rl0)): raise AssertionError('RUN helper size drift')
        blobs['run-decision']=rd; blobs['run-capture']=rc; blobs['run-loop']=rl; blobs['run-state']=bytes(4)
        cursor=align(cursor,16); alloc['run-dispatch']=cursor
        rdisp=run_dispatch(k1(alloc['run-decision']),k1(alloc['run-capture'])); blobs['run-dispatch']=rdisp; cursor+=len(rdisp)
        cursor=align(cursor,16); alloc['capture-event-dispatch']=cursor
        ced=capture_event_dispatch(k1(alloc['event'])); blobs['capture-event-dispatch']=ced; cursor+=len(ced)
        controls_end=align(cursor,16)
        if controls_end!=CONTROLS_RUNTIME_END:
            raise AssertionError(
                f'controls allocation end drifted: {controls_end:#x}!={CONTROLS_RUNTIME_END:#x}'
            )
        if controls_end>TOASTY_K0:
            raise AssertionError(f'controls reach Toasty: {controls_end:#x}>{TOASTY_K0:#x}')

        # Shared file gap is current product-owned padding from low TURN prefix to shifted Toasty.
        start_rom=rom_for_runtime(align(turn.CONTROL_ALLOCATION.end_exclusive,16))
        end_rom=rom_for_runtime(controls_end)
        if any(x!=0xFF for x in rom.data[start_rom:(TOASTY_ROM if toasty_size is not None else end_rom)]):
            raise AssertionError('shared low-gap is not intact reserved padding')
        for name,blob in blobs.items():
            off=rom_for_runtime(alloc[name]); rom.write_bytes(off,blob)
        # Deterministic zero pad through final controls end; leave remaining shared padding FF.
        last_written=max(rom_for_runtime(alloc[n])+len(blobs[n]) for n in blobs)
        if last_written<end_rom: rom.write_bytes(last_written,bytes(end_rom-last_written))

        if toasty_size is None:
            rom.write_u32(FILE_ENTRY_ROM+4,end_rom)

        # Capture/event sharing: keep existing pickup-capture hook; retarget only its owned static stub.
        cap_stub_rom=turn.STATIC_REGION_ROM+turn.STATIC_OFFSETS['capture']
        rom.expect_bytes(cap_stub_rom,trampoline(turn.CAPTURE_ENTRY))
        rom.write_bytes(cap_stub_rom,trampoline(k1(alloc['capture-event-dispatch'])))
        rom.write_u32(EVENT_HOOK_ROM,jal(turn.CAPTURE_TRAMPOLINE_VA))

        # ATTACK raw-action gate composes in front of the production TURN action helper.
        action_stub_rom=turn.STATIC_REGION_ROM+turn.STATIC_OFFSETS['action']
        rom.expect_bytes(action_stub_rom,trampoline(turn.ACTION_ENTRY))
        rom.write_bytes(action_stub_rom,trampoline(k1(alloc['attack-wrapper'])))

        # Whole/mid-function control seams.
        rom.write_bytes(SPECIAL_CALL_HOOK_ROM,words_blob([*address_words('t9',k1(alloc['specials'])),0x0320F809,0])) # jalr t9
        rom.write_bytes(STAND_JUMP_HOOK_ROM,trampoline(k1(alloc['standing-jump'])))
        rom.write_bytes(MOVE_JUMP_HOOK_ROM,trampoline(k1(alloc['moving-jump'])))
        rom.write_bytes(BLOCK_START_HOOK_ROM,trampoline(k1(alloc['block-start'])))
        rom.write_bytes(LEDGE_HOOK_ROM,trampoline(k1(alloc['ledge'])))

        # Five-setting v09 frontend. First promote COMBOS -> ATTACK and CLASSIC/MODERN.
        rom.write_bytes(ATTACK_LABEL_ROM,ATTACK_LABEL)
        rom.write_u32(ATTACK_MODERN_PTR_ROM,ATTACK_MODERN_PTR)

        # Verify v04 frontend fixed pieces before replacing only v09-owned bytes.
        rom.expect_u32(v09.ROW_COUNT_RIGHT_ROM,v09.ROW_COUNT_V06)
        rom.expect_u32(v09.ROW_COUNT_LEFT_ROM,v09.ROW_COUNT_V06)
        rom.expect_bytes(v09.JUMP_DRAW_HOOK_ROM,v09.JUMP_DRAW_HOOK_V06)
        rom.expect_bytes(v09.CURSOR_TABLE_ROM,v09.CURSOR_TABLE_V06)
        rom.expect_bytes(v09.VALUES_REPACK_ROM,v09.VALUES_REPACK_V06)
        rom.expect_u32(v09.LOCK_PTR_ROM,v09.LOCK_PTR_V06)
        for off,(expected,_) in v09.WORD_PATCHES.items(): rom.expect_u32(off,expected)

        right_dispatch=v09.build_right_edit_dispatch(); draw_off=v09.align(len(right_dispatch),4)
        draw_va=v09.RIGHT_EDIT_VA+draw_off
        left_dispatch=v09.build_left_edit_dispatch(); cursor_off=v09.align(len(left_dispatch),4)
        cursor_va=v09.LEFT_EDIT_VA+cursor_off
        right_content=right_dispatch+bytes(draw_off-len(right_dispatch))+v09.build_jump_run_draw_helper(cursor_va)
        left_content=left_dispatch+bytes(cursor_off-len(left_dispatch))+v09.build_cursor_helper()
        right_cap=v09.RIGHT_SAFE_END_ROM-v09.RIGHT_EDIT_ROM; left_cap=v09.LEFT_SAFE_END_ROM-v09.LEFT_EDIT_ROM
        if len(right_content)>right_cap or len(left_content)>left_cap: raise AssertionError('v09 frontend capacity drift')
        rom.write_u32(v09.ROW_COUNT_RIGHT_ROM,v09.ROW_COUNT_V09); rom.write_u32(v09.ROW_COUNT_LEFT_ROM,v09.ROW_COUNT_V09)
        rom.write_bytes(v09.RIGHT_EDIT_ROM,v09.pad(right_content,right_cap)); rom.write_bytes(v09.LEFT_EDIT_ROM,v09.pad(left_content,left_cap))
        for off,(_,replacement) in v09.WORD_PATCHES.items(): rom.write_u32(off,replacement)
        rom.write_bytes(v09.COMBOS_DRAW_ROM,v09.build_attack_value_draw()); rom.write_bytes(v09.SPECIALS_DRAW_ROM,v09.build_specials_value_draw())
        rom.write_u32(v09.JUMP_DRAW_HOOK_ROM,jal(draw_va)); rom.write_u32(v09.JUMP_DRAW_HOOK_ROM+4,0); rom.write_u32(v09.JUMP_DRAW_HOOK_ROM+8,0)
        rom.write_bytes(v09.CURSOR_TABLE_ROM,v09.CURSOR_TABLE_V09); rom.write_bytes(v09.VALUES_REPACK_ROM,v09.VALUES_REPACK_V09); rom.write_u32(v09.LOCK_PTR_ROM,v09.EXISTING_LOCK_VALUE_VA)
        # Preserve all five durable user setting bits across inventory box switching.
        rom.expect_u32(v09.BOX_SETTINGS_MASK_ROM,v09.BOX_SETTINGS_MASK_V06); rom.write_u32(v09.BOX_SETTINGS_MASK_ROM,v09.BOX_SETTINGS_MASK_V09)

        # ATTACK combo/steady-Block tails live outside v09 frontend ownership.
        combo_k1=k1(alloc['combo']); sb_k1=k1(alloc['steady-block'])
        rom.expect_bytes(RIGHT_TAIL_ROM,bytes(12)); rom.expect_bytes(LEFT_TAIL_ROM,bytes(12))
        rom.write_bytes(RIGHT_TAIL_ROM,words_blob([addiu('t9','t9',combo_k1&0xFFFF),jr('t9'),0]))
        rom.write_bytes(LEFT_TAIL_ROM,words_blob([addiu('t9','t9',sb_k1&0xFFFF),jr('t9'),0]))
        rom.write_u32(COMBO_HOOK_ROM,jal(0x800769D0)); rom.write_u32(COMBO_HOOK_ROM+4,lui('t9',(combo_k1+0x8000)>>16))
        rom.write_u32(BLOCK_STEADY_HOOK_ROM,jump(0x80076A88)); rom.write_u32(BLOCK_STEADY_HOOK_ROM+4,lui('t9',(sb_k1+0x8000)>>16))

        # RUN static trampolines occupy the same v09-zero padding proven by v10.
        rom.expect_bytes(STATIC_RUN_DISPATCH_ROM,bytes(0x20))
        rom.write_bytes(STATIC_RUN_DISPATCH_ROM,trampoline(k1(alloc['run-dispatch'])))
        rom.write_bytes(STATIC_RUN_LOOP_ROM,trampoline(k1(alloc['run-loop'])))
        for off in RUN_CALL_ROMS: rom.write_u32(off,jal(STATIC_RUN_DISPATCH_VA))
        rom.write_u32(ACTION_INPUT_HOOK_ROM,jal(STATIC_RUN_DISPATCH_VA))
        rom.write_u32(RUN_LOOP_BACKEDGE_ROM,jump(STATIC_RUN_LOOP_VA))

        # Invariants: stock predicate and running jump classifier remain untouched.
        if rom.data[RUN_PREDICATE_VA-0x7FFFF400:RUN_PREDICATE_VA-0x7FFFF400+0x3C] != baseline[RUN_PREDICATE_VA-0x7FFFF400:RUN_PREDICATE_VA-0x7FFFF400+0x3C]:
            raise AssertionError('stock Run predicate changed')
        rom.expect_u32(RUN_LOOP_CLASSIFIER_ROM,RUN_LOOP_CLASSIFIER_EXPECTED)
        # Toasty module remains at shifted composed base and is not overwritten.
        if toasty_size is not None and rom.data[TOASTY_ROM:TOASTY_ROM+toasty_size] != baseline[TOASTY_ROM:TOASTY_ROM+toasty_size]:
            raise AssertionError('CI4 Toasty module changed during controls packing')
        # No proof-only max-XP write in the generated specials helper.
        xp_force=words_blob([*address_words('t0',0x8011200C),addiu('t1','zero',20000),sw('t1',0,'t0')])
        if xp_force in blobs['specials']: raise AssertionError('proof XP force leaked into product candidate')

        return (
            f"Five-setting controls: 0x{align(turn.CONTROL_ALLOCATION.end_exclusive,16):08X}..0x{controls_end-1:08X}",
            "Native progression gates for Slide and Super Slide; no proof XP override",
        )
