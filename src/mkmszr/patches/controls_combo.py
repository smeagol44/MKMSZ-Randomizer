"""Confirmed modern Attack combo parser helper."""

ATTACK_MODERN_MASK = 0x0400


STATE_VA = 0x800A60E8


REG = {
    'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,
    't0':8,'t1':9,'t2':10,'t3':11,'t4':12,'t5':13,'t6':14,'t7':15,
    's0':16,'s1':17,'s2':18,'s3':19,'s4':20,'s5':21,'s6':22,'s7':23,
    't8':24,'t9':25,'k0':26,'k1':27,'gp':28,'sp':29,'fp':30,'ra':31,
}


def _i(op, rt, rs, imm):
    return ((op & 0x3F)<<26) | ((REG[rs]&31)<<21) | ((REG[rt]&31)<<16) | (imm & 0xFFFF)


def lui(rt,imm): return _i(0x0F,rt,'zero',imm)


def lw(rt,imm,rs): return _i(0x23,rt,rs,imm)


def andi(rt,rs,imm): return _i(0x0C,rt,rs,imm)


def addiu(rt,rs,imm): return _i(0x09,rt,rs,imm)


def addu(rd,rs,rt): return ((REG[rs]<<21)|(REG[rt]<<16)|(REG[rd]<<11)|0x21)


def sll(rd,rt,sh): return ((REG[rt]<<16)|(REG[rd]<<11)|((sh&31)<<6))


def jr(rs): return (REG[rs]<<21)|0x08


NOP=0


def addr_words(reg, addr):
    hi=((addr+0x8000)>>16)&0xFFFF
    lo=addr&0xFFFF
    return [lui(reg,hi), addiu(reg,reg,lo)]


class E:
    def __init__(self): self.items=[]; self.labels={}
    def emit(self,*ws): self.items.extend(ws)
    def label(self,n): self.labels[n]=len(self.items)
    def beq(self,rs,rt,label): self.items.append(('b',0x04,rs,rt,label))
    def bne(self,rs,rt,label): self.items.append(('b',0x05,rs,rt,label))
    def b(self,label): self.items.append(('b',0x04,'zero','zero',label))
    def finish(self):
        out=[]
        for idx,x in enumerate(self.items):
            if isinstance(x,tuple):
                _,op,rs,rt,label=x
                off=self.labels[label]-(idx+1)
                if not -0x8000 <= off <= 0x7FFF: raise ValueError('branch out of range')
                out.append(_i(op,rt,rs,off))
            else: out.append(x)
        return b''.join(w.to_bytes(4,'big') for w in out)


def build_combo_helper():
    e=E()
    e.emit(*addr_words('t0',STATE_VA), lw('t1',0,'t0'), andi('t1','t1',ATTACK_MODERN_MASK))
    e.beq('t1','zero','classic'); e.emit(NOP)
    # Modern: use event-0 history for this combo record. The true expected
    # event was already stored by stock at controller+0x71C one instruction
    # earlier, so conditions/debug state keep their stock meaning.
    e.emit(addu('v0','zero','zero'))
    e.b('replay'); e.emit(NOP)
    e.label('classic')
    e.emit(sll('v0','v0',3))
    e.label('replay')
    # Replay displaced stock instruction and return to 0x8004D7B4.
    e.emit(lw('v1',0x6E0,'a1'), jr('ra'), NOP)
    return e.finish()

