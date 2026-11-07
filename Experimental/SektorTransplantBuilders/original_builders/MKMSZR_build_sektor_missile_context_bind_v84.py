#!/usr/bin/env python3
"""MKMSZR Sektor straight-missile v84 contextual pre-insertion frame-bind proof.

Baseline: exact Runtime-confirmed v75.

v83 showed that a raw 0x8001BDA0 ROCKETD1 bind immediately before token actor-list
insertion does not remove the initial Ice/Sektor projectile frame. Static reconciliation
shows that the Runtime-confirmed later v75 bind has an additional host-ABI transaction:
the projectile is made current in controller +0x6E0, controller +0x6E4 is redirected to
rocket loop +0xD90, selector 0 is installed, and the full animation interpreter
0x800304C0 advances the frame. v84 factors that exact transaction into a shared helper
and invokes it both at the existing v75 parent hook and immediately before token insertion.

No constructor operand, global token selector, placement, child, movement, helper/tint,
collision or cleanup changes are made.
"""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

V75_SHA256='e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb'
ROM_SIZE=0x1000000
PARENT_WRAP_ROM=0x9AE10
PARENT_WRAP_VA=0x8009A210
INSERT_SHIM_ROM=0x9AE64
INSERT_SHIM_VA=0x8009A264
CHILD_STUB_ROM=0x9AE90
TOKEN_INSERT_CALL_ROM=0x316C8
STOCK_INSERT_JAL=0x0C009194

REG={'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,'t0':8,'t1':9,'t2':10,'t3':11,'t4':12,'t5':13,'t6':14,'t7':15,'s0':16,'s1':17,'s2':18,'s3':19,'s4':20,'s5':21,'s6':22,'s7':23,'t8':24,'t9':25,'k0':26,'k1':27,'gp':28,'sp':29,'fp':30,'ra':31}
def be32(b,o): return int.from_bytes(b[o:o+4],'big')
def put32(b,o,v): b[o:o+4]=int(v&0xffffffff).to_bytes(4,'big')
def I(op,rs,rt,imm): return ((op&0x3f)<<26)|(REG[rs]<<21)|(REG[rt]<<16)|(imm&0xffff)
def R(rs,rt,rd,sh,fn): return (REG[rs]<<21)|(REG[rt]<<16)|(REG[rd]<<11)|((sh&31)<<6)|(fn&63)
def J(op,va): return ((op&0x3f)<<26)|((va>>2)&0x03ffffff)
def words(xs): return b''.join(int(x&0xffffffff).to_bytes(4,'big') for x in xs)
def rol32(v,s):
    s&=31
    return v&0xffffffff if not s else ((v<<s)|(v>>(32-s)))&0xffffffff
def update_crc(rom):
    seed=0xF8CA4DDC; t1=t2=t3=t4=t5=t6=seed
    for off in range(0x1000,0x101000,4):
        value=be32(rom,off); total=(t6+value)&0xffffffff
        if total<t6:t4=(t4+1)&0xffffffff
        t6=total;t3^=value;r=rol32(value,value&31);t5=(t5+r)&0xffffffff
        t2^=r if t2>value else (t6^value);t1=(t1+(t5^value))&0xffffffff
    c1=(t6^t4^t3)&0xffffffff;c2=(t5^t2^t1)&0xffffffff
    put32(rom,0x10,c1);put32(rom,0x14,c2);return c1,c2

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('baseline',type=Path); ap.add_argument('output',type=Path); a=ap.parse_args()
    base=a.baseline.read_bytes(); assert len(base)==ROM_SIZE; assert hashlib.sha256(base).hexdigest()==V75_SHA256
    rom=bytearray(base)

    # Immutable v75 controls.
    assert be32(rom,0x4BC40)==J(3,PARENT_WRAP_VA)
    assert be32(rom,TOKEN_INSERT_CALL_ROM)==STOCK_INSERT_JAL
    assert be32(rom,TOKEN_INSERT_CALL_ROM+4)==0xA48200AE
    assert be32(rom,0xF40DBC)==0x00034A58          # stock Ice constructor retained
    assert be32(rom,0x315E8)==0xA602009E           # stock token selector retained
    assert be32(rom,0x4BBF0)==0x24050005           # +5
    assert be32(rom,0x4BBFC)==0x24060026           # +38
    assert be32(rom,0x4BC00)==0x0C00C482           # 0x80031208
    assert be32(rom,0x4C484)==0x080268A4           # v75 child
    child_before=bytes(rom[CHILD_STUB_ROM:0x9AF20])

    # Guard exact v75 parent wrapper before replacing it with a context-complete equivalent.
    expected=[
      0x27BDFFE0,0xAFBF001C,0xAFA40018,0x3C08802F,0x8D08CE20,0x8D0906E4,
      0xAFA90014,0xA480009E,0x948A008C,0x314A0010,0x8C8B002C,0x11400004,
      0x00000000,0x00000000,0x08026895,0x00000000,0x00000000,0xAC8B002C,
      0x8C8C0098,0x258C0D90,0xAD0C06E4,0x0C00C130,0x00000000,0x3C08802F,
      0x8D08CE20,0x8FA90014,0xAD0906E4,0x8FA40018,0x8FBF001C,0x27BD0020,
      0x03E00008,0x00000000]
    assert [be32(rom,PARENT_WRAP_ROM+4*i) for i in range(32)]==expected

    # Shared contextual bind helper. Input a0=projectile. Unlike v83 raw frame setup,
    # this reproduces the full later-v75 host transaction and makes projectile current.
    bind=[
      I(0x09,'sp','sp',-0x10),
      I(0x2B,'sp','ra',0x0C),
      I(0x0F,'zero','t0',0x802F),
      I(0x23,'t0','t0',0xCE20),
      I(0x23,'t0','t2',0x06E4),
      I(0x2B,'sp','t2',0x08),
      I(0x2B,'t0','a0',0x06E0),
      I(0x29,'a0','zero',0x009E),
      I(0x23,'a0','t3',0x0098),
      I(0x09,'t3','t3',0x0D90),
      I(0x2B,'t0','t3',0x06E4),
      J(3,0x800304C0),
      0,
      I(0x0F,'zero','t0',0x802F),
      I(0x23,'t0','t0',0xCE20),
      I(0x23,'sp','t2',0x08),
      I(0x2B,'t0','t2',0x06E4),
      I(0x23,'sp','ra',0x0C),
      I(0x09,'sp','sp',0x10),
      R('ra','zero','zero',0,0x08),
      0,
    ]
    assert len(bind)==21 and PARENT_WRAP_ROM+len(words(bind))==INSERT_SHIM_ROM

    # Insertion shim: run the exact contextual bind, then preserve the stock insertion.
    # Original RA is restored before tail-jump so 0x80024650 returns to token 0x80030AD0.
    shim=[
      I(0x09,'sp','sp',-0x08),
      I(0x2B,'sp','ra',0x04),
      J(3,PARENT_WRAP_VA),
      0,
      I(0x23,'sp','ra',0x04),
      I(0x09,'sp','sp',0x08),
      I(0x2B,'t0','s2',0x06E0),   # restore owner current-actor at token seam
      R('s0','zero','a0',0,0x21),
      I(0x0F,'zero','a1',0x8011),
      J(2,0x80024650),
      I(0x09,'a1','a1',0x1C98),
    ]
    assert len(shim)==11 and INSERT_SHIM_ROM+len(words(shim))==CHILD_STUB_ROM
    payload=words(bind+shim)
    assert len(payload)==0x80
    rom[PARENT_WRAP_ROM:CHILD_STUB_ROM]=payload
    put32(rom,TOKEN_INSERT_CALL_ROM,J(3,INSERT_SHIM_VA))

    # All non-first-render controls remain byte-identical.
    assert bytes(rom[CHILD_STUB_ROM:0x9AF20])==child_before
    assert be32(rom,0xF40DBC)==0x00034A58
    assert be32(rom,0x315E8)==0xA602009E
    assert be32(rom,0x4BBF0)==0x24050005 and be32(rom,0x4BBFC)==0x24060026
    assert be32(rom,0x4BC00)==0x0C00C482 and be32(rom,0x4C484)==0x080268A4
    assert be32(rom,0x4BA68)==0x0C00A0C3 and be32(rom,0x4BA84)==0x0C00A0C3

    c1,c2=update_crc(rom); out=bytes(rom); a.output.write_bytes(out)
    print('OUTPUT',a.output)
    print('SHA256',hashlib.sha256(out).hexdigest())
    print('CRC1/CRC2',f'{c1:08X} / {c2:08X}')
    print('TEST_INPUT','Forward, Forward + Low Punch')
    print('CHANGE','reuse full v75 contextual rocket-frame transaction before token actor insertion')
    print('UNCHANGED','stock constructor/token selector; (+5,+38); v75 child/flight; helper pair; tint; collision; cleanup')

if __name__=='__main__': main()
