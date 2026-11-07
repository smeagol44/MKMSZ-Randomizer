#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

V75_SHA256="e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
RR=0xF40000
SIZE=0x1000000

p=argparse.ArgumentParser(description="Build Sektor missile v80 constructor-time first-descriptor proof from exact v75.")
p.add_argument("v75_rom",type=Path)
p.add_argument("-o","--output",type=Path,default=Path("MKMSZR_sektor-missile-constructor_common-proof_v80.z64"))
a=p.parse_args()
rom=bytearray(a.v75_rom.read_bytes())
assert len(rom)==SIZE
assert hashlib.sha256(rom).hexdigest()==V75_SHA256

def u32(o): return int.from_bytes(rom[o:o+4],"big")
def w32(o,v): rom[o:o+4]=int(v&0xffffffff).to_bytes(4,"big")

# Static trace, exact v75:
#
# Primary Zap slot 0x24 -> +0xDA0.
# The straight-Ice parent selects slot 0x24 through 0x80030E98. Its initial
# animation phase leaves the cursor at the first post-phase token:
#
#   +0xDB8 = 0x0000000B
#   +0xDBC = 0x00034A58
#
# Token 0x0B dispatches to 0x80030974.
# 0x80030974 calls 0x80034510 with owner resource base (actor+0x98).
# 0x80034510 reads exactly ONE following stream operand from current +0x6E4,
# adds the owner resource base, and passes that pointer to 0x800281A0.
# 0x800281A0 then uses the pointed descriptor's first word to construct/bind
# the new actor before 0x80030974 inserts it via 0x80024650.
#
# The later repeated token sites +0xE00/+0xE04 and +0xE50/+0xE54 are distinct
# later phases and are NOT changed in this proof.
#
# v75's first genuine horizontal rocket descriptor is +0x4E6E4, already used
# by the proven later D90 substitution. v80 changes ONLY the first token's
# descriptor operand:
#
#       +0xDBC: 0x34A58 -> 0x4E6E4
#
# Everything else in v75 remains byte-identical, including the later parent
# rocket substitution (control), both Ice helper processes, palette path,
# (+5,+38) placement, child handoff, acceleration, collision, and cleanup.

assert u32(RR+0x24*4)==0x00000DA0
assert u32(RR+0xDB8)==0x0000000B
assert u32(RR+0xDBC)==0x00034A58
assert u32(RR+0xE00)==0x0000000B and u32(RR+0xE04)==0x00034A58
assert u32(RR+0xE50)==0x0000000B and u32(RR+0xE54)==0x00034A58

MISSILE_SHAPE=u32(RR+0xD90)
assert MISSILE_SHAPE==0x0004E6E4
assert u32(RR+0xD94)==MISSILE_SHAPE
assert u32(RR+MISSILE_SHAPE)==MISSILE_SHAPE+8
assert u32(RR+MISSILE_SHAPE+4)==0

w32(RR+0xDBC,MISSILE_SHAPE)

# CIC-NUS-6102 CRC.
def rol(v,s):
    s&=31
    return v&0xffffffff if not s else ((v<<s)|(v>>(32-s)))&0xffffffff
seed=0xF8CA4DDC
t1=t2=t3=t4=t5=t6=seed
for off in range(0x1000,0x101000,4):
    d=u32(off); s=(t6+d)&0xffffffff
    if s<t6: t4=(t4+1)&0xffffffff
    t6=s; t3^=d; r=rol(d,d&31); t5=(t5+r)&0xffffffff
    t2^=r if t2>d else (t6^d)
    t1=(t1+(t5^d))&0xffffffff
crc1=(t6^t4^t3)&0xffffffff
crc2=(t5^t2^t1)&0xffffffff
w32(0x10,crc1); w32(0x14,crc2)

a.output.write_bytes(rom)
print("OUTPUT",a.output)
print("SHA256",hashlib.sha256(rom).hexdigest())
print("CRC1/CRC2",f"{crc1:08X} / {crc2:08X}")
print("PATCH",f"file87 +0xDBC: 00034A58 -> {MISSILE_SHAPE:08X}")
print("UNCHANGED","all v75 code/lifecycle/placement/flight/collision; later rocket substitution retained")
print("TEST_INPUT","Forward, Forward + Low Punch")
