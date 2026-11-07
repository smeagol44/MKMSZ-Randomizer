#!/usr/bin/env python3
"""MKMSZR Sektor straight-missile v82 pre-insertion palette-bind proof.

Input: exact Runtime-confirmed v75 missile baseline.
Output: disposable v82 proof.

v81 Runtime-confirmed that the live token-0x0B constructor + pre-insertion selector
boundary removes the one-frame Ice-derived projectile fallback, but the rocket then
renders palette/graphics-corrupted. Static tracing shows why: resource construction
runs native frame setup before token 0x0B later writes actor+0x9E. Native frame setup
resolves +0x9E through the palette table and writes the active palette handle to
actor+0x80. Changing only +0x9E therefore leaves selector and active handle incoherent.

v82 changes only that same first-render transaction relative to v75:
  1. live slot-0x24 token-0x0B constructor operand -> genuine ROCKETD1 entry;
  2. token pre-insertion selector -> 0 (the Sektor TLUT used by the proven later wrapper);
  3. immediately resolve selector 0 through the same native table used by 0x8001BDA0
     and write the resulting active handle to actor+0x80 before insertion.

To fit the handle rebind in-place, v82 replaces the token handler's redundant rewrite
of actor+0x7C = actor+0x108. The generic constructor 0x800281A0 already performed that
exact assignment at 0x80028248..4C for this newly-created actor before returning.

This is a disposable diagnostic, not production adapter code. It keeps the stock
0x8001C528 allocation/refcount call and all v75 placement, flight, helper/tint,
child ownership, collision and cleanup machinery unchanged.
"""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

V75_SHA256 = "e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
ROM_SIZE = 0x1000000
FILE87_ROM_BASE = 0x00F40000
LIVE_OPERAND_REL = 0x00000DBC
ICE_ENTRY_REL = 0x00034A58
ROCKET_ENTRY_REL = 0x0004E6E4
TOKEN_SELECTOR_STORE_ROM = 0x000315E8  # VA 0x800309E8
STOCK_SELECTOR_STORE = 0xA602009E      # sh v0,0x9E(s0)
PROOF_SELECTOR_STORE = 0xA600009E      # sh zero,0x9E(s0)
REBIND_ROM = 0x000315EC                # VA 0x800309EC
REBIND_END = 0x00031604                # through VA 0x80030A00 inclusive

REG={"zero":0,"v0":2,"v1":3,"a0":4,"s0":16,"s2":18}
def I(op,rs,rt,imm): return ((op&0x3f)<<26)|(REG[rs]<<21)|(REG[rt]<<16)|(imm&0xffff)

def be16(b,o): return int.from_bytes(b[o:o+2],"big")
def be32(b,o): return int.from_bytes(b[o:o+4],"big")
def put32(b,o,v): b[o:o+4]=int(v&0xffffffff).to_bytes(4,"big")
def words(vs): return b"".join(int(v&0xffffffff).to_bytes(4,"big") for v in vs)
def rol32(v,s):
    s &= 31
    return v & 0xffffffff if s==0 else ((v<<s)|(v>>(32-s))) & 0xffffffff

def update_crc_6102(rom):
    seed=0xF8CA4DDC; t1=t2=t3=t4=t5=t6=seed
    for off in range(0x1000,0x101000,4):
        value=be32(rom,off); total=(t6+value)&0xffffffff
        if total<t6: t4=(t4+1)&0xffffffff
        t6=total; t3^=value; r=rol32(value,value&31); t5=(t5+r)&0xffffffff
        t2 ^= r if t2>value else (t6^value); t1=(t1+(t5^value))&0xffffffff
    c1=(t6^t4^t3)&0xffffffff; c2=(t5^t2^t1)&0xffffffff
    put32(rom,0x10,c1); put32(rom,0x14,c2); return c1,c2

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("baseline",type=Path); ap.add_argument("output",type=Path); a=ap.parse_args()
    base=a.baseline.read_bytes(); assert len(base)==ROM_SIZE
    assert hashlib.sha256(base).hexdigest()==V75_SHA256
    rom=bytearray(base); rr=FILE87_ROM_BASE

    # Exact live constructor and v75 child/rocket facts.
    assert be32(rom,rr+LIVE_OPERAND_REL)==ICE_ENTRY_REL
    assert be32(rom,rr+ROCKET_ENTRY_REL)==ROCKET_ENTRY_REL+8
    assert be32(rom,rr+0xFD0)==0xD90
    assert [be32(rom,rr+0xD90+4*i) for i in range(4)][2:]==[1,0xD90]

    # Exact token-handler bytes being replaced.
    assert be32(rom,TOKEN_SELECTOR_STORE_ROM)==STOCK_SELECTOR_STORE
    expected=[
        0x96440078, # lhu a0,0x78(s2)
        0x3C03802F, # lui v1,0x802F
        0x8C63CE20, # lw v1,-0x31E0(v1) -> 0x802ECE20
        0x26020108, # addiu v0,s0,0x108
        0xAE02007C, # sw v0,0x7C(s0) -- redundant constructor assignment
        0xA6040078, # sh a0,0x78(s0)
    ]
    assert [be32(rom,REBIND_ROM+4*i) for i in range(6)]==expected

    # Constructor 0x800281A0 already installs actor+0x7C = actor+0x108 before frame setup.
    assert be32(rom,0x28E48)==0x26020108
    assert be32(rom,0x28E4C)==0xAE02007C

    # Preserve stable v75 machinery.
    assert be32(rom,0x4BBF0)==0x24050005
    assert be32(rom,0x4BBFC)==0x24060026
    assert be32(rom,0x4BC00)==0x0C00C482
    assert be32(rom,0x4BA68)==0x0C00A0C3 and be32(rom,0x4BA84)==0x0C00A0C3
    assert be32(rom,0x4C484)==0x080268A4 and be32(rom,0x4C488)==0x3C0A800A
    assert be16(rom,0xB1B4A)==9 and be16(rom,0xB1B4C)==9
    assert be16(rom,0xB1B56)==8 and be16(rom,0xB1B58)==8

    # v82 first-render transaction.
    put32(rom,rr+LIVE_OPERAND_REL,ROCKET_ENTRY_REL)
    put32(rom,TOKEN_SELECTOR_STORE_ROM,PROOF_SELECTOR_STORE)

    # Mirror exactly the active-handle lookup used by native frame setup for selector 0:
    #   lhu handle, 0x0A02(0x80290000 + selector*8)
    # selector is fixed zero here, so the effective address is 0x80290A02.
    # Then restore the two displaced live values needed by the continuation.
    rebind=[
        I(0x0F,"zero","v0",0x8029),       # lui v0,0x8029
        I(0x25,"v0","v0",0x0A02),         # lhu v0,0x0A02(v0)
        I(0x29,"s0","v0",0x0080),         # sh v0,0x80(s0)
        I(0x25,"s2","a0",0x0078),         # lhu a0,0x78(s2)
        I(0x0F,"zero","v1",0x802F),       # lui v1,0x802F
        I(0x23,"v1","v1",0xCE20),         # lw v1,-0x31E0(v1)
    ]
    rom[REBIND_ROM:REBIND_END]=words(rebind)

    c1,c2=update_crc_6102(rom); out=bytes(rom)
    # Scope audit: CRC + constructor operand + selector store + six-word rebind only.
    for i,(x,y) in enumerate(zip(base,out)):
        if x!=y:
            assert (0x10<=i<0x18) or (rr+LIVE_OPERAND_REL<=i<rr+LIVE_OPERAND_REL+4) or \
                   (TOKEN_SELECTOR_STORE_ROM<=i<TOKEN_SELECTOR_STORE_ROM+4) or (REBIND_ROM<=i<REBIND_END), hex(i)
    a.output.write_bytes(out)
    print("OUTPUT",a.output)
    print("SHA256",hashlib.sha256(out).hexdigest())
    print("CRC1/CRC2",f"{c1:08X} / {c2:08X}")
    print("TEST_INPUT","Forward, Forward + Low Punch")
    print("BASELINE",V75_SHA256)
    print("CHANGE_1","live token-0x0B constructor operand -> genuine ROCKETD1 entry")
    print("CHANGE_2","pre-insertion selector -> 0")
    print("CHANGE_3","pre-insertion actor+0x80 rebound from native selector-0 handle table")
    print("UNCHANGED","v75 placement, child ownership, calibrated flight, companions/tint, collision, cleanup")
    print("NOTE","disposable diagnostic; omits only redundant token rewrite actor+0x7C=actor+0x108 already done by constructor")

if __name__=="__main__": main()
