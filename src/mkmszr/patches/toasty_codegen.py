"""Native Toasty code generation and expansion-module packing."""

from dataclasses import dataclass

from ..allocations import ExpansionPoolAllocator
from .toasty_constants import *

ZERO=0; V0=2; V1=3; A0=4; A1=5; A2=6; A3=7
T0=8; T1=9; T2=10; T3=11; T4=12; T5=13; T6=14; T7=15
S0=16; S1=17; S2=18; S3=19; S4=20; S5=21; S6=22; S7=23
T8=24; T9=25; SP=29; RA=31
NOP=0

def _r(rs:int,rt:int,rd:int,sh:int,fn:int)->int:
    return ((rs&31)<<21)|((rt&31)<<16)|((rd&31)<<11)|((sh&31)<<6)|(fn&63)
def _i(op:int,rs:int,rt:int,imm:int)->int:
    return ((op&63)<<26)|((rs&31)<<21)|((rt&31)<<16)|(imm&0xFFFF)
def addiu(rt:int,rs:int,imm:int)->int: return _i(0x09,rs,rt,imm)
def lui(rt:int,imm:int)->int: return _i(0x0F,0,rt,imm)
def ori(rt:int,rs:int,imm:int)->int: return _i(0x0D,rs,rt,imm)
def lw(rt:int,off:int,base:int)->int: return _i(0x23,base,rt,off)
def sw(rt:int,off:int,base:int)->int: return _i(0x2B,base,rt,off)
def lbu(rt:int,off:int,base:int)->int: return _i(0x24,base,rt,off)
def lhu(rt:int,off:int,base:int)->int: return _i(0x25,base,rt,off)
def lh(rt:int,off:int,base:int)->int: return _i(0x21,base,rt,off)
def sh(rt:int,off:int,base:int)->int: return _i(0x29,base,rt,off)
def sb(rt:int,off:int,base:int)->int: return _i(0x28,base,rt,off)
def addu(rd:int,rs:int,rt:int)->int: return _r(rs,rt,rd,0,0x21)
def or_reg(rd:int,rs:int,rt:int)->int: return _r(rs,rt,rd,0,0x25)
def move(rd:int,rs:int)->int: return addu(rd,rs,ZERO)
def sll(rd:int,rt:int,shamt:int)->int: return _r(0,rt,rd,shamt,0)
def jr(rs:int)->int: return _r(rs,0,0,0,8)
def jalr(rs:int,rd:int=RA)->int: return _r(rs,0,rd,0,9)
def jal(address:int)->int: return 0x0C000000|((address>>2)&0x03FFFFFF)
def jump(address:int)->int: return 0x08000000|((address>>2)&0x03FFFFFF)
def bne(rs:int,rt:int,off_words:int)->int: return _i(0x05,rs,rt,off_words)
def bltz(rs:int,off_words:int)->int: return (0x01<<26)|((rs&31)<<21)|(off_words&0xFFFF)
def words_blob(words)->bytes:
    return b"".join(int(w&0xFFFFFFFF).to_bytes(4,"big") for w in words)
def split_address(address:int)->tuple[int,int]:
    return ((address+0x8000)>>16)&0xFFFF,address&0xFFFF
def addr_words(rt:int,address:int)->list[int]:
    hi,lo=split_address(address); return [lui(rt,hi),addiu(rt,rt,lo)]
def kseg1(address:int)->int:
    if not 0x80000000<=address<0xA0000000:
        raise ValueError(f"expected KSEG0 address, got 0x{address:08X}")
    return address|0x20000000

class MiniEmitter:
    def __init__(self): self.w=[]; self.labels={}; self.fix=[]
    def emit(self,*ws): self.w.extend(ws)
    def label(self,name):
        if name in self.labels: raise ValueError(f"duplicate label: {name}")
        self.labels[name]=len(self.w)
    def bne(self,rs,rt,label): self.fix.append((len(self.w),'bne',rs,rt,label)); self.w.append(0)
    def beq(self,rs,rt,label): self.fix.append((len(self.w),'beq',rs,rt,label)); self.w.append(0)
    def bltz(self,rs,label): self.fix.append((len(self.w),'bltz',rs,0,label)); self.w.append(0)
    def finish(self):
        for idx,kind,rs,rt,label in self.fix:
            if label not in self.labels: raise ValueError(f"missing label: {label}")
            off=self.labels[label]-(idx+1)
            if kind=='bne': self.w[idx]=bne(rs,rt,off)
            elif kind=='beq': self.w[idx]=_i(0x04,rs,rt,off)
            else: self.w[idx]=bltz(rs,off)
        return words_blob(self.w)

def _build_draw_table() -> bytes:
    out=bytearray()
    for idx,x,y in DRAW_ORDER:
        width,height=PIECE_GEOMETRY[idx]
        out+=int(x).to_bytes(2,'big',signed=True)
        out+=int(y).to_bytes(2,'big',signed=True)
        out+=width.to_bytes(2,'big')+height.to_bytes(2,'big')
    return bytes(out)

DRAW_TABLE=_build_draw_table()

def _build_init_table(source_addrs:tuple[int,...], assets:ToastyAssets)->bytes:
    out=bytearray()
    for idx in ALLOCATION_ORDER:
        width,height=PIECE_GEOMETRY[idx]
        stride=(width+31)&~31
        out+=bytes((idx,0,width,height))
        out+=stride.to_bytes(2,'big')
        out+=len(assets.visual_slices[idx]).to_bytes(2,'big')
        out+=source_addrs[idx].to_bytes(4,'big')
    return bytes(out)

def _build_compositor(state_k1:int,draw_table_k1:int,feature_state_k1:int,audio_helper_k1:int,probability:int)->bytes:
    e=MiniEmitter()
    e.emit(addiu(SP,SP,-0x50),sw(RA,0x4C,SP),sw(S0,0x48,SP),sw(S1,0x44,SP),
           sw(S2,0x40,SP),sw(S3,0x3C,SP),sw(S4,0x38,SP),sw(S5,0x34,SP),
           sw(S6,0x30,SP),sw(S7,0x2C,SP))
    e.emit(move(S0,A2),*addr_words(S2,state_k1),*addr_words(S3,draw_table_k1),
           *addr_words(S4,0x8002018C),*addr_words(S5,0x8001EAE4),*addr_words(S7,feature_state_k1))
    e.emit(jalr(S5),NOP)
    e.emit(lw(T0,0,S7));e.bne(T0,ZERO,'active');e.emit(NOP)
    e.emit(lw(T4,0x0C,S7));e.beq(T4,ZERO,'done');e.emit(NOP)
    e.emit(addiu(T4,T4,-1),sw(T4,0x0C,S7));e.bne(T4,ZERO,'done');e.emit(NOP)
    e.emit(addiu(A0,ZERO,probability),*addr_words(T9,RANDPER_VA),jalr(T9),NOP,ori(T1,ZERO,0x8000))
    e.bne(V0,T1,'done');e.emit(NOP)
    e.emit(addiu(T0,ZERO,1),sw(T0,0,S7),addiu(T0,ZERO,SLIDE_IN_TICKS),sw(T0,4,S7),
           addiu(T0,ZERO,SLIDE_START_X_SHIFT),sw(T0,8,S7),NOP)
    e.beq(ZERO,ZERO,'slide_in');e.emit(NOP)
    e.label('active')
    e.emit(addiu(T1,ZERO,1));e.beq(T0,T1,'slide_in');e.emit(NOP)
    e.emit(addiu(T1,ZERO,2));e.beq(T0,T1,'hold');e.emit(NOP)
    e.beq(ZERO,ZERO,'slide_out');e.emit(NOP)
    e.label('slide_in')
    e.emit(lw(T2,8,S7),addiu(T2,T2,-SLIDE_STEP),sw(T2,8,S7),lw(T3,4,S7),addiu(T3,T3,-1),sw(T3,4,S7))
    e.bne(T3,ZERO,'draw');e.emit(NOP)
    e.emit(addiu(T0,ZERO,2),sw(T0,0,S7),addiu(T0,ZERO,HOLD_TICKS),sw(T0,4,S7),
           *addr_words(T9,audio_helper_k1),jalr(T9),NOP,NOP,NOP,NOP)
    e.beq(ZERO,ZERO,'draw');e.emit(NOP)
    e.label('hold')
    e.emit(lw(T3,4,S7),addiu(T3,T3,-1),sw(T3,4,S7));e.bne(T3,ZERO,'draw');e.emit(NOP)
    e.emit(addiu(T0,ZERO,3),sw(T0,0,S7),addiu(T0,ZERO,SLIDE_OUT_TICKS),sw(T0,4,S7))
    e.beq(ZERO,ZERO,'draw');e.emit(NOP)
    e.label('slide_out')
    e.emit(lw(T2,8,S7),addiu(T2,T2,SLIDE_STEP),sw(T2,8,S7),lw(T3,4,S7),addiu(T3,T3,-1),sw(T3,4,S7))
    e.bne(T3,ZERO,'draw');e.emit(NOP)
    e.emit(sw(ZERO,0,S7),sw(ZERO,4,S7),addiu(T2,ZERO,SLIDE_START_X_SHIFT),sw(T2,8,S7))
    e.beq(ZERO,ZERO,'done');e.emit(NOP)
    e.label('draw')
    e.emit(addiu(S6,ZERO,9));e.label('piece_loop');e.emit(jalr(S4),NOP,move(S1,V0))
    e.emit(move(T0,S0),move(T1,S1),addiu(T2,ZERO,22));e.label('copy_loop')
    e.emit(lw(T3,0,T0),sw(T3,0,T1),addiu(T0,T0,4),addiu(T1,T1,4),addiu(T2,T2,-1))
    e.bne(T2,ZERO,'copy_loop');e.emit(NOP)
    e.emit(lw(T0,0,S2));e.bltz(T0,'done');e.emit(NOP)
    e.emit(sh(T0,0x4A,S1),addiu(T0,ZERO,CUSTOM_PALETTE_SELECTOR),sh(T0,0x4C,S1),sh(ZERO,0x10,S1),sh(ZERO,0x12,S1))
    e.emit(lhu(T0,4,S3),sh(T0,0x20,S1),lhu(T1,6,S3),sh(T1,0x22,S1))
    e.emit(lh(T0,0,S3),lw(T4,8,S7),addu(T0,T0,T4),lh(T1,0x08,S0),addu(T0,T0,T1),
           sh(T0,0x08,S1),sh(T0,0x28,S1),lhu(T1,4,S3),addu(T1,T1,T0),sh(T1,0x18,S1),sh(T1,0x38,S1))
    e.emit(lh(T0,2,S3),lh(T1,0x0A,S0),addu(T0,T0,T1),sh(T0,0x0A,S1),sh(T0,0x2A,S1),
           lhu(T1,6,S3),addu(T1,T1,T0),sh(T1,0x1A,S1),sh(T1,0x3A,S1))
    e.emit(addiu(A0,ZERO,2),move(A2,S1),jalr(S5),NOP,addiu(S2,S2,4),addiu(S3,S3,8),addiu(S6,S6,-1))
    e.bne(S6,ZERO,'piece_loop');e.emit(NOP)
    e.label('done')
    e.emit(lw(S7,0x2C,SP),lw(S6,0x30,SP),lw(S5,0x34,SP),lw(S4,0x38,SP),lw(S3,0x3C,SP),
           lw(S2,0x40,SP),lw(S1,0x44,SP),lw(S0,0x48,SP),lw(RA,0x4C,SP),addiu(SP,SP,0x50),jr(RA),NOP)
    return e.finish()

def _build_init(state_k1:int,init_table_k1:int,palette_k0:int,feature_state_k1:int)->bytes:
    e=MiniEmitter()
    e.emit(addiu(SP,SP,-0x40),sw(RA,0x3C,SP),sw(S0,0x38,SP),sw(S1,0x34,SP),sw(S2,0x30,SP),
           sw(S3,0x2C,SP),sw(S4,0x28,SP),sw(S5,0x24,SP),sw(S6,0x20,SP))
    e.emit(*addr_words(S0,state_k1),*addr_words(S1,0x802E83F0),*addr_words(S2,0x800ED940),
           *addr_words(S3,init_table_k1),*addr_words(S4,0x8001C2B4),addiu(S6,ZERO,9))
    e.label('alloc_loop')
    e.emit(lbu(A0,2,S3),lbu(A1,3,S3),jalr(S4),NOP);e.bltz(V0,'fail');e.emit(NOP)
    e.emit(lbu(T0,0,S3),sll(T0,T0,2),addu(T1,S0,T0),sw(V0,0,T1))
    e.emit(sll(T0,V0,4),addu(T1,S1,T0),lhu(T0,4,S3),sh(T0,0x08,T1))
    e.emit(sll(T0,V0,2),addu(T1,S2,T0),lw(T2,0,T1),lui(T3,0x2000),or_reg(T2,T2,T3),lw(T5,8,S3),lhu(T4,6,S3))
    e.label('copy_loop')
    e.emit(lbu(T6,0,T5),sb(T6,0,T2),addiu(T5,T5,1),addiu(T2,T2,1),addiu(T4,T4,-1))
    e.bne(T4,ZERO,'copy_loop');e.emit(NOP)
    e.emit(addiu(S3,S3,12),addiu(S6,S6,-1));e.bne(S6,ZERO,'alloc_loop');e.emit(NOP)
    e.emit(*addr_words(T0,0x80290A88),addiu(T1,ZERO,CUSTOM_PALETTE_SELECTOR),sh(T1,0,T0),sh(T1,2,T0),lui(T1,0x0100),sw(T1,4,T0))
    e.emit(*addr_words(T0,0x802E7424),*addr_words(T1,palette_k0),sw(T1,0,T0))
    e.emit(*addr_words(T0,feature_state_k1),sw(ZERO,0,T0),sw(ZERO,4,T0),addiu(T1,ZERO,SLIDE_START_X_SHIFT),sw(T1,8,T0),sw(ZERO,0x0C,T0))
    e.label('fail')
    e.emit(lw(S6,0x20,SP),lw(S5,0x24,SP),lw(S4,0x28,SP),lw(S3,0x2C,SP),lw(S2,0x30,SP),
           lw(S1,0x34,SP),lw(S0,0x38,SP),lw(RA,0x3C,SP),addiu(SP,SP,0x40))
    e.emit(lui(A0,0x8029),lw(A0,0x1C10,A0),*addr_words(T9,POST13_RESUME_VA),jr(T9),NOP)
    return e.finish()

def _build_audio_helper()->bytes:
    e=MiniEmitter();e.emit(addiu(SP,SP,-0x20),sw(RA,0x1C,SP),sw(S0,0x18,SP))
    e.emit(*addr_words(S0,AUDIO_PARAM_VA),addiu(T0,ZERO,0x0B),sw(T0,0,S0),addiu(T0,ZERO,0x7F),sb(T0,5,S0),sh(ZERO,8,S0))
    e.emit(*addr_words(T9,AUDIO_PREP_A_VA),jalr(T9),NOP,*addr_words(T9,AUDIO_PREP_B_VA),jalr(T9),NOP)
    e.emit(addiu(A0,ZERO,TOASTY_EVENT_ID),move(A1,ZERO),move(A2,S0),*addr_words(T9,RAW_SOUND_VA),jalr(T9),NOP)
    e.emit(*addr_words(T9,AUDIO_PREP_A_VA),jalr(T9),NOP,*addr_words(T9,AUDIO_PREP_B_VA),jalr(T9),NOP)
    e.emit(lw(S0,0x18,SP),lw(RA,0x1C,SP),addiu(SP,SP,0x20),jr(RA),NOP)
    return e.finish()

def _build_trigger(feature_state_k1:int)->bytes:
    e=MiniEmitter();e.emit(addiu(SP,SP,-0x18),sw(RA,0x14,SP))
    for ptr in QUALIFYING_REACTION_CALLBACKS:
        e.emit(*addr_words(T0,ptr));e.beq(A0,T0,'qualify');e.emit(NOP)
    e.beq(ZERO,ZERO,'transfer');e.emit(NOP);e.label('qualify')
    e.emit(*addr_words(T1,feature_state_k1),addiu(T2,ZERO,COMMENT_DELAY_TICKS),sw(T2,0x0C,T1))
    e.label('transfer');e.emit(*addr_words(T9,REACTION_TRANSFER_VA),jalr(T9),NOP,lw(RA,0x14,SP),addiu(SP,SP,0x18),jr(RA),NOP)
    return e.finish()

def _build_dispatcher(init_k1:int,comp_k1:int,trigger_k1:int)->bytes:
    e=MiniEmitter();e.emit(*addr_words(T0,REACTION_RETURN_VA));e.beq(RA,T0,'reaction');e.emit(NOP)
    e.emit(*addr_words(T0,HUD_RETURN_VA));e.beq(RA,T0,'hud');e.emit(NOP)
    e.emit(jump(init_k1),NOP);e.label('reaction');e.emit(jump(trigger_k1),NOP);e.label('hud');e.emit(jump(comp_k1),NOP)
    return e.finish()

def _build_call_trampoline()->bytes:
    return words_blob([lui(T9,0xA01B),jr(T9),NOP])

def _build_init_loader()->bytes:
    # GAME SETTINGS TURN owns the shared file-0x1A stage-init load.  By the
    # time the post-13 Toasty hook runs, the packed Toasty module is already
    # resident at its established 0x801B0000 runtime base.
    return _build_call_trampoline()

def _align(value:int,alignment:int=16)->int:
    return (value+alignment-1)&~(alignment-1)

@dataclass(frozen=True)
class PackedToastyModule:
    data: bytes
    allocation_start: int
    offsets: dict[str,int]

def pack_toasty_module(assets:ToastyAssets, probability_per_thousand:int)->PackedToastyModule:
    if not 1<=probability_per_thousand<=1000:
        raise ValueError("Toasty probability must be between 1 and 1000 per thousand")

    dummy_state=0xA01B1000;dummy_table=0xA01B1100;dummy_feature=0xA01B1200;dummy_audio=0xA01B1300
    comp_probe=_build_compositor(dummy_state,dummy_table,dummy_feature,dummy_audio,probability_per_thousand)
    init_probe=_build_init(dummy_state,dummy_table,0x801B1400,dummy_feature)
    audio=_build_audio_helper();trigger_probe=_build_trigger(dummy_feature)
    dispatch_probe=_build_dispatcher(0xA01B0100,0xA01B0200,0xA01B0300)

    cursor=0; offsets={}
    def take(name:str,size:int,alignment:int=16)->int:
        nonlocal cursor
        cursor=_align(cursor,alignment); offsets[name]=cursor; cursor+=size; return offsets[name]

    take('dispatcher',len(dispatch_probe));take('compositor',len(comp_probe));take('init',len(init_probe))
    take('audio',len(audio));take('trigger',len(trigger_probe));take('draw-table',len(DRAW_TABLE))
    take('init-table',9*12);take('slot-state',9*4);take('feature-state',0x10);take('palette',0x200)
    for index,data in enumerate(assets.visual_slices): take(f'piece-{index}',len(data))

    pool=ExpansionPoolAllocator()
    allocation=pool.allocate('toasty-production',cursor,align=0x1000)
    if allocation.start!=MODULE_K0:
        raise ValueError(f"Toasty production base drifted: 0x{allocation.start:08X}")
    if allocation.end_exclusive>0x801B3420:
        raise ValueError("Toasty module exceeds reserved expansion pool")

    source_addrs=tuple(kseg1(MODULE_K0+offsets[f'piece-{i}']) for i in range(9))
    state_k1=kseg1(MODULE_K0+offsets['slot-state']);draw_k1=kseg1(MODULE_K0+offsets['draw-table'])
    table_k1=kseg1(MODULE_K0+offsets['init-table']);feature_k1=kseg1(MODULE_K0+offsets['feature-state'])
    audio_k1=kseg1(MODULE_K0+offsets['audio']);palette_k0=MODULE_K0+offsets['palette']
    comp_k1=kseg1(MODULE_K0+offsets['compositor']);init_k1=kseg1(MODULE_K0+offsets['init'])
    trigger_k1=kseg1(MODULE_K0+offsets['trigger'])

    dispatch=_build_dispatcher(init_k1,comp_k1,trigger_k1)
    comp=_build_compositor(state_k1,draw_k1,feature_k1,audio_k1,probability_per_thousand)
    init_table=_build_init_table(source_addrs,assets)
    init=_build_init(state_k1,table_k1,palette_k0,feature_k1)
    trigger=_build_trigger(feature_k1)
    if not (len(dispatch)==len(dispatch_probe) and len(comp)==len(comp_probe) and len(init)==len(init_probe) and len(trigger)==len(trigger_probe)):
        raise AssertionError("Toasty packing pass changed code size")

    blob=bytearray(cursor)
    def put(name:str,data:bytes)->None:
        start=offsets[name];blob[start:start+len(data)]=data
    put('dispatcher',dispatch);put('compositor',comp);put('init',init);put('audio',audio);put('trigger',trigger)
    put('draw-table',DRAW_TABLE);put('init-table',init_table);put('slot-state',bytes([0xFF])*(9*4))
    put('feature-state',(0).to_bytes(8,'big')+SLIDE_START_X_SHIFT.to_bytes(4,'big')+(0).to_bytes(4,'big'))
    put('palette',assets.palette_tlut)
    for index,data in enumerate(assets.visual_slices): put(f'piece-{index}',data)
    return PackedToastyModule(bytes(blob),allocation.start,offsets)
