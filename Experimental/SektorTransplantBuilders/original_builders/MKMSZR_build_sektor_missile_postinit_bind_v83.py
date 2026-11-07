#!/usr/bin/env python3
"""MKMSZR Sektor straight-missile v83 post-init/pre-insertion bind proof.

Input: exact Runtime-confirmed v75 missile baseline.
Output: disposable v83 proof.

Purpose
-------
v81 proved that replacing the constructor's first descriptor plus its selector store
removes the one-frame Ice/Sektor projectile fallback, but the rocket then renders
corrupted. v82 showed that explicitly rewriting actor+0x80 from selector 0 does not
change that corruption.

Static reconciliation identifies the lifecycle error: resource constructor 0x800281A0
calls 0x8001BDA0 *before* token-0x0B handler 0x80030974 finishes initializing the
secondary actor. The token later assigns fighter/type/resource/render state and only
then inserts the actor at 0x80030AC8. Exact v75 subsequently swaps Ice -> rocket via
0x800304C0 after insertion; that shape transition is why v75 gets a usable rocket,
but one Ice-derived frame can already have been displayed.

v83 therefore keeps the stock Ice constructor and stock selector allocation exactly,
and moves only the genuine rocket descriptor bind to the fully-initialized actor seam
immediately before actor-list insertion. This preserves v75 placement, parent/child
ownership, helpers/tint, calibrated flight, collision, and cleanup. The later v75
parent wrapper still performs its selector-0/D90 bind; its proof code is compacted
without changing that behavior so a 56-byte insertion wrapper fits in the same
proof-owned [0x9AE10,0x9AE90) interval. No new allocation is claimed.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

V75_SHA256 = "e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
ROM_SIZE = 0x1000000

FILE87_ROM_BASE = 0x00F40000
LIVE_OPERAND_REL = 0x00000DBC
ICE_ENTRY_REL = 0x00034A58
ROCKET_ENTRY_REL = 0x0004E6E4
ROCKET_LOOP_REL = 0x00000D90
CHILD_CURSOR_ENTRY_REL = 0x00000FD0

TOKEN_SELECTOR_STORE_ROM = 0x000315E8  # VA 0x800309E8
STOCK_SELECTOR_STORE = 0xA602009E      # sh v0,0x9e(s0)
TOKEN_INSERT_CALL_ROM = 0x000316C8     # VA 0x80030AC8
STOCK_INSERT_JAL = 0x0C009194          # jal 0x80024650

PARENT_WRAP_ROM = 0x0009AE10
PARENT_WRAP_VA = 0x8009A210
INSERT_WRAP_ROM = 0x0009AE58
INSERT_WRAP_VA = 0x8009A258
CHILD_STUB_ROM = 0x0009AE90

REG = {
    "zero":0,"at":1,"v0":2,"v1":3,"a0":4,"a1":5,"a2":6,"a3":7,
    "t0":8,"t1":9,"t2":10,"t3":11,"t4":12,"t5":13,"t6":14,"t7":15,
    "s0":16,"s1":17,"s2":18,"s3":19,"s4":20,"s5":21,"s6":22,"s7":23,
    "t8":24,"t9":25,"k0":26,"k1":27,"gp":28,"sp":29,"fp":30,"ra":31,
}

def be16(b, o): return int.from_bytes(b[o:o+2], "big")
def be32(b, o): return int.from_bytes(b[o:o+4], "big")
def put32(b, o, v): b[o:o+4] = int(v & 0xffffffff).to_bytes(4, "big")
def I(op, rs, rt, imm): return ((op&0x3f)<<26)|(REG[rs]<<21)|(REG[rt]<<16)|(imm&0xffff)
def R(rs, rt, rd, sh, fn): return (REG[rs]<<21)|(REG[rt]<<16)|(REG[rd]<<11)|((sh&31)<<6)|(fn&63)
def J(op, va): return ((op&0x3f)<<26)|((va>>2)&0x03ffffff)
def words(seq): return b"".join(int(x&0xffffffff).to_bytes(4,"big") for x in seq)

def rol32(v, s):
    s &= 31
    return v & 0xffffffff if not s else ((v<<s)|(v>>(32-s))) & 0xffffffff

def update_crc_6102(rom):
    seed=0xF8CA4DDC
    t1=t2=t3=t4=t5=t6=seed
    for off in range(0x1000,0x101000,4):
        value=be32(rom,off)
        total=(t6+value)&0xffffffff
        if total<t6: t4=(t4+1)&0xffffffff
        t6=total; t3^=value
        r=rol32(value,value&31)
        t5=(t5+r)&0xffffffff
        t2 ^= r if t2>value else (t6^value)
        t1=(t1+(t5^value))&0xffffffff
    crc1=(t6^t4^t3)&0xffffffff; crc2=(t5^t2^t1)&0xffffffff
    put32(rom,0x10,crc1); put32(rom,0x14,crc2)
    return crc1,crc2

def diff_offsets(a,b): return [i for i,(x,y) in enumerate(zip(a,b)) if x!=y]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("baseline",type=Path,help="exact v75 ROM")
    ap.add_argument("output",type=Path)
    args=ap.parse_args()

    baseline=args.baseline.read_bytes()
    assert len(baseline)==ROM_SIZE
    assert hashlib.sha256(baseline).hexdigest()==V75_SHA256
    rom=bytearray(baseline)
    rr=FILE87_ROM_BASE

    # Exact v75 guards: this proof deliberately restores/keeps stock constructor/palette.
    assert be32(rom,rr+LIVE_OPERAND_REL)==ICE_ENTRY_REL
    assert be32(rom,rr+ROCKET_ENTRY_REL)==ROCKET_ENTRY_REL+8
    assert be32(rom,rr+CHILD_CURSOR_ENTRY_REL)==ROCKET_LOOP_REL
    assert be32(rom,TOKEN_SELECTOR_STORE_ROM)==STOCK_SELECTOR_STORE
    assert be32(rom,TOKEN_INSERT_CALL_ROM)==STOCK_INSERT_JAL

    # v75 later parent hook remains pointed at the proof wrapper.
    assert be32(rom,0x4BC40)==J(3,PARENT_WRAP_VA)
    # Runtime-confirmed placement and child route remain controls.
    assert be32(rom,0x4BBF0)==0x24050005
    assert be32(rom,0x4BBFC)==0x24060026
    assert be32(rom,0x4BC00)==0x0C00C482
    assert be32(rom,0x4C484)==0x080268A4
    assert be32(rom,CHILD_STUB_ROM)==0x3C08802F

    # Guard exact v75 parent-wrapper footprint before compacting it.
    expected_parent=[
        0x27BDFFE0,0xAFBF001C,0xAFA40018,0x3C08802F,0x8D08CE20,0x8D0906E4,
        0xAFA90014,0xA480009E,0x948A008C,0x314A0010,0x8C8B002C,0x11400004,
        0x00000000,0x00000000,0x08026895,0x00000000,0x00000000,0xAC8B002C,
        0x8C8C0098,0x258C0D90,0xAD0C06E4,0x0C00C130,0x00000000,0x3C08802F,
        0x8D08CE20,0x8FA90014,0xAD0906E4,0x8FA40018,0x8FBF001C,0x27BD0020,
        0x03E00008,0x00000000,
    ]
    assert [be32(rom,PARENT_WRAP_ROM+4*i) for i in range(32)]==expected_parent

    # Compact equivalent of v75 parent wrapper. It still:
    #   selector 0 -> cursor actor+0x98+D90 -> one 0x800304C0 advance -> restore cursor.
    parent=[
        I(0x09,"sp","sp",-0x10),
        I(0x2B,"sp","ra",0x0C),
        I(0x0F,"zero","t0",0x802F),
        I(0x23,"t0","t0",0xCE20),
        I(0x23,"t0","t1",0x06E4),
        I(0x2B,"sp","t1",0x08),
        I(0x29,"a0","zero",0x009E),
        I(0x23,"a0","t2",0x0098),
        I(0x09,"t2","t2",0x0D90),
        J(3,0x800304C0),
        I(0x2B,"t0","t2",0x06E4),
        I(0x0F,"zero","t0",0x802F),
        I(0x23,"t0","t0",0xCE20),
        I(0x23,"sp","t1",0x08),
        I(0x2B,"t0","t1",0x06E4),
        I(0x23,"sp","ra",0x0C),
        R("ra","zero","zero",0,0x08),
        I(0x09,"sp","sp",0x10),
    ]
    assert len(parent)==18

    # New bounded insertion wrapper. At this call site token-0x0B has already initialized
    # actor +0x9C/+0x78/+0x98/position/flags/palette selector. Bind ROCKETD1 through native
    # frame setup now, then tail-jump to the original actor-list insertion with original RA.
    # s0 is the token handler's callee-saved pointer to the new actor; 0x8001BDA0 preserves it.
    insert=[
        I(0x09,"sp","sp",-0x08),
        I(0x2B,"sp","ra",0x04),
        I(0x23,"a0","a1",0x0098),
        I(0x0F,"zero","t0",0x0005),
        I(0x09,"t0","t0",0xE6E4), # 0x00050000 - 0x191C = 0x4E6E4
        J(3,0x8001BDA0),
        R("a1","t0","a1",0,0x21), # delay: a1 = resource_base + ROCKET_ENTRY_REL
        I(0x23,"sp","ra",0x04),
        I(0x09,"sp","sp",0x08),
        R("s0","zero","a0",0,0x21),
        I(0x0F,"zero","a1",0x8011),
        I(0x09,"a1","a1",0x1C98),
        J(2,0x80024650),
        0x00000000,
    ]
    assert len(insert)==14
    payload=words(parent+insert)
    assert len(payload)==0x80
    rom[PARENT_WRAP_ROM:CHILD_STUB_ROM]=payload

    # Redirect only the final token insertion call to the new wrapper; its stock delay slot
    # (owner +0xAE -> child +0xAE) stays untouched and executes before the wrapper.
    assert be32(rom,TOKEN_INSERT_CALL_ROM+4)==0xA48200AE
    put32(rom,TOKEN_INSERT_CALL_ROM,J(3,INSERT_WRAP_VA))

    crc1,crc2=update_crc_6102(rom)
    out=bytes(rom)

    # Diff scope: header CRC, one callsite, and existing v75 proof-wrapper interval only.
    for off in diff_offsets(baseline,out):
        assert (0x10<=off<0x18) or (TOKEN_INSERT_CALL_ROM<=off<TOKEN_INSERT_CALL_ROM+4) or (PARENT_WRAP_ROM<=off<CHILD_STUB_ROM), hex(off)

    # Post-build guards: no constructor/selector/resource/flight changes.
    assert be32(out,rr+LIVE_OPERAND_REL)==ICE_ENTRY_REL
    assert be32(out,TOKEN_SELECTOR_STORE_ROM)==STOCK_SELECTOR_STORE
    assert be32(out,TOKEN_INSERT_CALL_ROM)==J(3,INSERT_WRAP_VA)
    assert be32(out,0x4BC40)==J(3,PARENT_WRAP_VA)
    assert be32(out,0x4C484)==0x080268A4
    assert be32(out,CHILD_STUB_ROM)==0x3C08802F

    args.output.write_bytes(out)
    print("OUTPUT",args.output)
    print("SHA256",hashlib.sha256(out).hexdigest())
    print("CRC1/CRC2",f"{crc1:08X} / {crc2:08X}")
    print("TEST_INPUT","Forward, Forward + Low Punch")
    print("BASELINE","exact Runtime-confirmed v75",V75_SHA256)
    print("CHANGE","bind genuine ROCKETD1 after token actor initialization but before actor-list insertion")
    print("UNCHANGED","stock Ice constructor + selector allocation; v75 (+5,+38) placement; child ownership; calibrated flight; helpers/tint; collision; cleanup")
    print("PROOF_CODE","reuses exactly [0x9AE10,0x9AE90); no new proof allocation")

if __name__=="__main__": main()
