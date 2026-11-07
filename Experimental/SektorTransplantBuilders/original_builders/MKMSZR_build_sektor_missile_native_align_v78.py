#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

V75_SHA256="c2387e8badc6f27a2028407966668e15e58caf155b5721f95150cd6e338919e5"
SIZE=0x1000000
p=argparse.ArgumentParser(description="Build Sektor missile v78: target-native match-points alignment on exact v77 artifact (v75 flight baseline).")
p.add_argument("v75_rom",type=Path)
p.add_argument("-o","--output",type=Path,default=Path("MKMSZR_sektor-missile-native-align_common-proof_v78.z64"))
a=p.parse_args()
base=a.v75_rom.read_bytes()
rom=bytearray(base)
assert len(rom)==SIZE and hashlib.sha256(rom).hexdigest()==V75_SHA256

def u32(o): return int.from_bytes(rom[o:o+4],"big")
def w32(o,v): rom[o:o+4]=int(v&0xffffffff).to_bytes(4,"big")
R={'zero':0,'v0':2,'a0':4,'a1':5,'a2':6,'t0':8,'t1':9,'sp':29,'ra':31}
def I(op,rs,rt,imm): return ((op&63)<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def RR(rs,rt,rd,sh,fn): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|((sh&31)<<6)|(fn&63)
def J(op,va): return ((op&63)<<26)|((va>>2)&0x03ffffff)
def jal(va): return J(3,va)
def words(xs): return b"".join(int(x&0xffffffff).to_bytes(4,"big") for x in xs)

# v78 scope:
#   v75 flight/presentation/lifecycle remains unchanged.
#   Replace only the placement call with the newly identified native MKMSZ
#   match-points primitive:
#
#       0x80031394(owner, projectile)
#       0x80031208(projectile, +5, +38)
#
# Static trace:
#   0x80031394 copies owner +0x2C/+0x30 into child and then applies the child
#   current render descriptor's X/Y anchor with facing/flip semantics. This is
#   the target-native semantic analogue of MKT match_ani_points().
#
# Stock straight Ice does NOT call 0x80031394 at 0x8004AFF8; it directly applies
# 0x80031208 to the token-0x0B secondary actor. This is the architectural
# mismatch being tested.
#
# IMPORTANT: this proof deliberately aligns using the secondary actor's current
# native render descriptor at the placement seam. The later v75 genuine-rocket
# first-frame wrapper remains byte-identical. If alignment improves but is not
# exact, the next integration is to install the genuine rocket descriptor
# before this same native alignment primitive—not to tune Y constants.

# Guard v77 placement seam.
assert u32(0x4BBF0)==I(0x09,'zero','a1',5)
assert u32(0x4BBF4)==0
assert u32(0x4BBF8)==0x8C440648
assert u32(0x4BBFC)==I(0x09,'zero','a2',38)
assert u32(0x4BC00)==jal(0x8009A268)
assert u32(0x4BC04)==0

# Reuse only the tail of the existing proof-owned v75 wrapper interval.
# [0x9AE68,0x9AE90) is replaced by a 40-byte placement shim.
SHIM_ROM=0x9AE68
SHIM_VA=0x8009A268
END=0x9AE90

# v77 compact wrapper has returned by 0x9AE68; replace only its rejected
# ownerY+3 shim with the native match-points shim.
assert u32(0x9AE60)==0x03E00008  # jr ra
assert u32(0x9AE64)==0
assert u32(0x9AE68)==I(0x23,'v0','t0',0x06E0)

shim=[
    RR('a0','zero','t0',0,0x21),       # t0 = projectile
    I(0x23,'v0','a0',0x06E0),          # a0 = owner actor
    RR('t0','zero','a1',0,0x21),       # a1 = projectile
    jal(0x80031394),                    # native match-points
    0,
    RR('t0','zero','a0',0,0x21),       # projectile
    I(0x09,'zero','a1',5),             # proven donor retail X
    I(0x09,'zero','a2',38),            # proven donor retail Y
    J(2,0x80031208),                    # tail-call native relative placement
    0,
]
assert len(words(shim))==END-SHIM_ROM
rom[SHIM_ROM:END]=words(shim)
w32(0x4BC00,jal(SHIM_VA))

# Strong scope guards: v75 rocket wrapper and movement child/callback remain unchanged.
assert bytes(rom[0x9AE10:0x9AE68])==base[0x9AE10:0x9AE68]
assert bytes(rom[0x9AE90:0x9AF20])==base[0x9AE90:0x9AF20]
assert rom[0xB1B4C:0xB1B4E]==(9).to_bytes(2,'big')
assert rom[0xB1B58:0xB1B5A]==(8).to_bytes(2,'big')

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
print("TEST_INPUT","Forward, Forward + Low Punch")
print("V78_SCOPE","v75 + native 0x80031394 match-points before proven (+5,+38)")
print("V75_FLIGHT","UNCHANGED")
