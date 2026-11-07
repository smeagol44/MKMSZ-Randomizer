#!/usr/bin/env python3
"""MKMSZR Sektor straight-missile v85 deferred-insertion proof.

Baseline: exact Runtime-confirmed v75.

v84 proved that moving the full v75 contextual rocket bind earlier removes the initial
Ice/Sektor projectile flash, but corrupts the rocket because the later v75 bind then
re-enters native frame setup as a rocket->same-rocket update. v85 keeps the staged actor
on its stock Ice descriptor until the original v75 bind point, but defers actor-list
insertion until immediately AFTER that proven Ice->rocket transition.

Token 0x0B still constructs, palettes, stages, positions and owns the same actor. Its
0x80024650 list insertion call is suppressed but its delay-slot +0xAE store is preserved.
The existing v75 parent wrapper is rewritten equivalently to:
  * make selector 0 + D90 current and run one 0x800304C0 advance at the original point;
  * insert the now-rocket actor with the same stock list helper;
  * temporarily use the owner's pre-placement Y only while sorting the list, matching the
    original token-time insertion key, then restore the projectile's final placed Y;
  * restore the parent's animation cursor and return normally.

No constructor operand, token palette allocation/selector, placement, child ownership,
movement/cadence, helper/tint processes, collision or cleanup path is changed.
This remains a disposable proof; token insertion suppression is globally patched and is
validated only on the bounded straight-missile route.
"""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

V75_SHA256 = 'e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb'
ROM_SIZE = 0x1000000
TOKEN_INSERT_CALL_ROM = 0x316C8
TOKEN_INSERT_DELAY_ROM = 0x316CC
PARENT_WRAP_ROM = 0x9AE10
PARENT_WRAP_VA = 0x8009A210
CHILD_STUB_ROM = 0x9AE90

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
        if total<t6: t4=(t4+1)&0xffffffff
        t6=total; t3^=value; r=rol32(value,value&31); t5=(t5+r)&0xffffffff
        t2^=r if t2>value else (t6^value); t1=(t1+(t5^value))&0xffffffff
    c1=(t6^t4^t3)&0xffffffff; c2=(t5^t2^t1)&0xffffffff
    put32(rom,0x10,c1); put32(rom,0x14,c2); return c1,c2

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('baseline',type=Path)
    ap.add_argument('output',type=Path)
    a=ap.parse_args()
    base=a.baseline.read_bytes()
    assert len(base)==ROM_SIZE
    actual=hashlib.sha256(base).hexdigest()
    assert actual==V75_SHA256, f'wrong v75 baseline: {actual}'
    rom=bytearray(base)

    # Immutable v75 controls around the targeted seams.
    assert be32(rom,TOKEN_INSERT_CALL_ROM)==J(3,0x80024650)
    assert be32(rom,TOKEN_INSERT_DELAY_ROM)==0xA48200AE  # sh v0,0xAE(a0)
    assert be32(rom,0x4BC40)==J(3,PARENT_WRAP_VA)
    assert be32(rom,0x4BC44)==0xAC4406E0               # delay: projectile current
    assert be32(rom,0x4BC48)==0x3C02802F
    assert be32(rom,0x4BC4C)==0x8C42CE20
    assert be32(rom,0x4BC50)==0xAC5006E0               # caller restores owner
    assert be32(rom,0xF40DBC)==0x00034A58              # stock Ice constructor
    assert be32(rom,0x315E8)==0xA602009E               # stock token selector
    assert be32(rom,0x4BBF0)==0x24050005               # +5
    assert be32(rom,0x4BBFC)==0x24060026               # +38
    assert be32(rom,0x4BC00)==J(3,0x80031208)
    assert be32(rom,0x4C484)==J(2,0x8009A290)          # v75 child
    child_before=bytes(rom[CHILD_STUB_ROM:0x9AF20])

    # Guard exact v75 parent wrapper. The old v70 +/-96px correction is already NOPed by
    # v72; this rewrite preserves the actual live selector/cursor/advance semantics and
    # uses the recovered space to perform the deferred stock list insertion.
    expected=[
      0x27BDFFE0,0xAFBF001C,0xAFA40018,0x3C08802F,0x8D08CE20,0x8D0906E4,
      0xAFA90014,0xA480009E,0x948A008C,0x314A0010,0x8C8B002C,0x11400004,
      0x00000000,0x00000000,0x08026895,0x00000000,0x00000000,0xAC8B002C,
      0x8C8C0098,0x258C0D90,0xAD0C06E4,0x0C00C130,0x00000000,0x3C08802F,
      0x8D08CE20,0x8FA90014,0xAD0906E4,0x8FA40018,0x8FBF001C,0x27BD0020,
      0x03E00008,0x00000000]
    assert [be32(rom,PARENT_WRAP_ROM+4*i) for i in range(32)]==expected

    # Suppress only the stock token-time list link. Its delay-slot +0xAE store remains.
    put32(rom,TOKEN_INSERT_CALL_ROM,0)

    # Original call site has already made projectile current at controller +0x6E0 and s0
    # still holds the owner actor. Perform the exact v75 Ice->rocket transition first;
    # only then make the actor visible by linking it into the active list.
    #
    # 0x80024650 sorts by actor +0x5C then +0x30. Token-time insertion originally saw
    # owner-copy Y. Placement has happened by this later point, so temporarily restore
    # owner Y for the list-link operation, then restore the final projectile Y. This keeps
    # the stock insertion ordering key while still deferring visibility.
    wrapper=[
      I(0x09,'sp','sp',-0x28),               # 00
      I(0x2B,'sp','ra',0x24),                 # 01
      I(0x2B,'sp','a0',0x20),                 # 02 projectile
      I(0x0F,'zero','t0',0x802F),             # 03
      I(0x23,'t0','t0',0xCE20),               # 04 current process
      I(0x23,'t0','t1',0x06E4),               # 05 saved parent cursor
      I(0x2B,'sp','t1',0x1C),                 # 06
      I(0x29,'a0','zero',0x009E),             # 07 selector 0
      I(0x23,'a0','t2',0x0098),               # 08 resource base
      I(0x09,'t2','t2',0x0D90),               # 09 rocket loop
      I(0x2B,'t0','t2',0x06E4),               # 10 cursor -> D90
      J(3,0x800304C0),                         # 11 full native advance
      0,                                       # 12
      I(0x23,'sp','a0',0x20),                 # 13 projectile
      I(0x23,'a0','t3',0x0030),               # 14 final placed Y
      I(0x2B,'sp','t3',0x18),                 # 15 save final Y
      I(0x23,'s0','t4',0x0030),               # 16 original token-time owner Y
      I(0x2B,'a0','t4',0x0030),               # 17 temporary stock sort key
      I(0x0F,'zero','a1',0x8011),             # 18
      I(0x09,'a1','a1',0x1C98),               # 19 active actor-list head
      J(3,0x80024650),                         # 20 deferred stock insertion
      0,                                       # 21
      I(0x23,'sp','a0',0x20),                 # 22
      I(0x23,'sp','t3',0x18),                 # 23
      I(0x2B,'a0','t3',0x0030),               # 24 restore final Y
      I(0x0F,'zero','t0',0x802F),             # 25
      I(0x23,'t0','t0',0xCE20),               # 26
      I(0x23,'sp','t1',0x1C),                 # 27
      I(0x2B,'t0','t1',0x06E4),               # 28 restore parent cursor
      I(0x23,'sp','ra',0x24),                 # 29
      I(0x09,'sp','sp',0x28),                 # 30
      R('ra','zero','zero',0,0x08),            # 31
      0,                                       # 32 delay
    ]
    # 33 words = 0x84, but only 0x80 is available before child code. Fold the final
    # stack restore into JR delay slot to stay inside the existing proof interval.
    wrapper=wrapper[:-4] + [
      I(0x23,'sp','ra',0x24),                 # restore ra
      R('ra','zero','zero',0,0x08),            # jr ra
      I(0x09,'sp','sp',0x28),                 # delay: restore sp
    ]
    assert len(wrapper)==32
    rom[PARENT_WRAP_ROM:CHILD_STUB_ROM]=words(wrapper)

    # Guard resulting composition.
    assert be32(rom,TOKEN_INSERT_CALL_ROM)==0
    assert be32(rom,TOKEN_INSERT_DELAY_ROM)==0xA48200AE
    assert bytes(rom[CHILD_STUB_ROM:0x9AF20])==child_before
    assert be32(rom,0xF40DBC)==0x00034A58
    assert be32(rom,0x315E8)==0xA602009E
    assert be32(rom,0x4BBF0)==0x24050005 and be32(rom,0x4BBFC)==0x24060026
    assert be32(rom,0x4BC00)==J(3,0x80031208)
    assert be32(rom,0x4C484)==J(2,0x8009A290)
    assert be32(rom,0x4BA68)==J(3,0x8002830C) and be32(rom,0x4BA84)==J(3,0x8002830C)

    c1,c2=update_crc(rom)
    out=bytes(rom); a.output.write_bytes(out)
    print('OUTPUT',a.output)
    print('SHA256',hashlib.sha256(out).hexdigest())
    print('CRC1/CRC2',f'{c1:08X} / {c2:08X}')
    print('TEST_INPUT','Forward, Forward + Low Punch')
    print('CHANGE','defer token actor-list insertion until immediately after original v75 Ice->rocket bind')
    print('LIST_ORDER','temporary owner Y during insertion; final placed projectile Y restored afterward')
    print('UNCHANGED','stock constructor/token palette; (+5,+38); v75 child/flight; helper pair; tint; collision; cleanup')

if __name__=='__main__': main()
