#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

V75_SHA256="e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
SIZE=0x1000000
FILE87_ROM=0xF40000
LIVE_TOKEN_REL=0xDB8
LIVE_OPERAND_REL=0xDBC
ICE_ENTRY=0x00034A58
ROCKET_ENTRY=0x0004E6E4

p=argparse.ArgumentParser(description="v80: bind genuine rocket as the token-0x0B constructor's first descriptor; exact v75 baseline.")
p.add_argument("v75_rom",type=Path)
p.add_argument("-o","--output",type=Path,default=Path("MKMSZR_sektor-missile-constructor-first-descriptor_common-proof_v80.z64"))
a=p.parse_args()
base=a.v75_rom.read_bytes(); rom=bytearray(base)
assert len(rom)==SIZE
assert hashlib.sha256(rom).hexdigest()==V75_SHA256

def u32(o): return int.from_bytes(rom[o:o+4],"big")
def w32(o,v): rom[o:o+4]=int(v&0xffffffff).to_bytes(4,"big")

# Static route guard:
# primary animation table = file+0x104; slot 0x24 -> file+0xD78.
assert u32(FILE87_ROM+0x104+0x24*4)==0x00000D78

# The live slot-0x24 stream contains the constructor token at +0xDB8.
# 0x80030974 calls 0x80034510; that helper reads the word at current +0x6E4
# and adds it to owner actor +0x98 before 0x800281A0 constructs the actor.
assert u32(FILE87_ROM+LIVE_TOKEN_REL)==0x0000000B
assert u32(FILE87_ROM+LIVE_OPERAND_REL)==ICE_ENTRY

# Imported rocket entry is already valid in exact v75:
# +0x4E6E4 -> +0x4E6EC, whose descriptor is 39x9, anchor (+26,+3).
assert u32(FILE87_ROM+ROCKET_ENTRY)==0x0004E6EC
assert u32(FILE87_ROM+0x4E6EC)==0x0004E6F8
assert rom[FILE87_ROM+0x4E6F0:FILE87_ROM+0x4E6F8]==bytes.fromhex("00270009001a0003")

# There are four token-0x0B / Ice-entry pairs in v75. The other three are
# +0xE00/+0xE04, +0xE50/+0xE54, +0xEAC/+0xEB0 and are intentionally untouched.
pairs=[]
needle=(0x0B).to_bytes(4,"big")+ICE_ENTRY.to_bytes(4,"big")
file87=bytes(rom[FILE87_ROM:FILE87_ROM+0x4E790])
for i in range(0,len(file87)-7,4):
    if file87[i:i+8]==needle: pairs.append(i)
assert pairs==[0xDB8,0xE00,0xE50,0xEAC], [hex(x) for x in pairs]

# SINGLE semantic edit: constructor input for the live slot-0x24 token.
w32(FILE87_ROM+LIVE_OPERAND_REL,ROCKET_ENTRY)

# Keep v75's later rocket substitution, helpers, placement, palette, child,
# flight, collision and cleanup byte-identical. This later substitution is a
# deliberate control for the constructor-time test.
assert rom[0x9ADA0:0x9AF20]==base[0x9ADA0:0x9AF20]
assert rom[0x4B784:0x4BE00]==base[0x4B784:0x4BE00]

# CIC-NUS-6102 CRC.
def rol(v,s):
    s&=31
    return v&0xffffffff if not s else ((v<<s)|(v>>(32-s)))&0xffffffff
seed=0xF8CA4DDC
t1=t2=t3=t4=t5=t6=seed
for off in range(0x1000,0x101000,4):
    d=u32(off); total=(t6+d)&0xffffffff
    if total<t6: t4=(t4+1)&0xffffffff
    t6=total; t3^=d; r=rol(d,d&31); t5=(t5+r)&0xffffffff
    t2 ^= r if t2>d else (t6^d)
    t1=(t1+(t5^d))&0xffffffff
crc1=(t6^t4^t3)&0xffffffff; crc2=(t5^t2^t1)&0xffffffff
w32(0x10,crc1); w32(0x14,crc2)

a.output.write_bytes(rom)
print("OUTPUT",a.output)
print("SHA256",hashlib.sha256(rom).hexdigest())
print("CRC1/CRC2",f"{crc1:08X} / {crc2:08X}")
print("TEST_INPUT","Forward, Forward + Low Punch")
print("ONLY_NONHEADER_EDIT",f"file87 +0x{LIVE_OPERAND_REL:X}: 0x{ICE_ENTRY:08X} -> 0x{ROCKET_ENTRY:08X}")
print("V75_PARENT_HELPERS_PLACEMENT_PALETTE_FLIGHT_COLLISION_CLEANUP","UNCHANGED")
