#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

V75_SHA256="e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
SIZE=0x1000000

p=argparse.ArgumentParser(description="Build Sektor straight-missile chest alignment/hold v76 from exact v75.")
p.add_argument("v75_rom",type=Path)
p.add_argument("-o","--output",type=Path,default=Path("MKMSZR_sektor-missile-chest-hold_common-proof_v76.z64"))
a=p.parse_args()
rom=bytearray(a.v75_rom.read_bytes())
assert len(rom)==SIZE
assert hashlib.sha256(rom).hexdigest()==V75_SHA256

def u32(o): return int.from_bytes(rom[o:o+4],"big")
def w32(o,v): rom[o:o+4]=int(v&0xffffffff).to_bytes(4,"big")
R={"zero":0,"v0":2,"a0":4,"a1":5,"a2":6,"t0":8,"t1":9,"t2":10,"t3":11,"t4":12,
   "s0":16,"s1":17,"sp":29,"ra":31}
def I(op,rs,rt,imm): return ((op&63)<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def RR(rs,rt,rd,sh,fn): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|((sh&31)<<6)|(fn&63)
def J(op,va): return ((op&63)<<26)|((va>>2)&0x03ffffff)
def jal(va): return J(3,va)
def words(xs): return b"".join(int(x&0xffffffff).to_bytes(4,"big") for x in xs)

# v76 scope:
#   * v75 flight math/lifecycle/collision stays byte-identical.
#   * Move only the owner-relative Y placement from +38 to +46 (8 local units lower).
#   * After the genuine projectile first frame is installed, re-install the genuine
#     open-chest player frame and sleep 0x20 native process ticks before restoring
#     the stock animation cursor. Stock special-action ownership remains in force.
#
# Donor video/source check:
#   do_robo_zap holds the firing state through process_sleep(0x20) after projectile
#   creation; the supplied 60-fps donor recording visually shows about one second
#   of open-chest recovery. MKMSZ process/action cadence is ~30 Hz, so 0x20 target
#   process ticks is the direct bounded timing proof (~1.07 s).
#
# The +8 Y correction is presentation/asset-anchor compensation only. It does NOT
# change the generic donor retail placement contract (+5,+38).

# Guard Runtime-confirmed v75 placement.
assert u32(0x4BBF0)==I(0x09,"zero","a1",5)
assert u32(0x4BBF4)==0
assert u32(0x4BBF8)==0x8C440648
assert u32(0x4BBFC)==I(0x09,"zero","a2",38)
assert u32(0x4BC00)==jal(0x80031208)
assert u32(0x4BC04)==0

# Presentation-only Y correction: +38 -> +46.
w32(0x4BBFC,I(0x09,"zero","a2",46))

# Preserve exact v75 movement child/callback.
movement_before=bytes(rom[0x9AE90:0x9AF20])

# v70-v75 chest script offset can be recovered from the Runtime-confirmed chest
# routine itself: LUI/ORI pair at 0x9ADD0/0x9ADD4 contains CHEST_SCRIPT_OFF.
hi=u32(0x9ADCC)&0xffff
lo=u32(0x9ADD0)&0xffff
CHEST_SCRIPT_OFF=(hi<<16)|lo
assert CHEST_SCRIPT_OFF < 0x80000

# Rewrite the v70 projectile-first-frame wrapper compactly. The genuine chest
# frame has already been installed by the Runtime-confirmed v69 chest hook.
# v72 removed the old +/-96px correction, so reclaim that dead proof logic and
# simply hold the parent process after the projectile's genuine first frame.
WR=0x9AE10
END=0x9AE90
seq=[]
def E(x): seq.append(x)

E(I(0x09,"sp","sp",-0x20))
E(I(0x2B,"sp","ra",0x1c))
E(I(0x2B,"sp","a0",0x18))             # projectile actor
E(I(0x0F,"zero","t0",0x802F))
E(I(0x23,"t0","t0",0xCE20))           # current parent process
E(I(0x23,"t0","t1",0x06E4))
E(I(0x2B,"sp","t1",0x14))             # save stock animation cursor

# Genuine rocket first frame, same v75 mechanism.
E(I(0x29,"a0","zero",0x009E))
E(I(0x23,"a0","t2",0x0098))
E(I(0x09,"t2","t2",0x0D90))
E(I(0x2B,"t0","t2",0x06E4))
E(jal(0x800304C0))
E(0)

# The chest frame already displayed by the earlier v69 hook remains the player's
# current rendered shape. Hold the stock special-action parent here, after launch.
E(I(0x09,"zero","a0",0x20))
E(jal(0x80028794))
E(0)

# Restore stock cursor and return to the untouched Ice parent lifecycle.
E(I(0x0F,"zero","t0",0x802F))
E(I(0x23,"t0","t0",0xCE20))
E(I(0x23,"sp","t1",0x14))
E(I(0x2B,"t0","t1",0x06E4))
E(I(0x23,"sp","a0",0x18))
E(I(0x23,"sp","ra",0x1c))
E(I(0x09,"sp","sp",0x20))
E(RR("ra","zero","zero",0,0x08))
E(0)

blob=words(seq)
assert len(blob)<=END-WR,(len(blob),END-WR)
rom[WR:END]=b"\x00"*(END-WR)
rom[WR:WR+len(blob)]=blob

# Guard that v75 flight code is untouched.
assert bytes(rom[0x9AE90:0x9AF20])==movement_before
# Placement X and native helper untouched; only Y differs.
assert u32(0x4BBF0)==I(0x09,"zero","a1",5)
assert u32(0x4BBFC)==I(0x09,"zero","a2",46)
assert u32(0x4BC00)==jal(0x80031208)

# Input remains F,F+LP.
assert rom[0xB1B4C:0xB1B4E]==(9).to_bytes(2,"big")
assert rom[0xB1B58:0xB1B5A]==(8).to_bytes(2,"big")

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
print("MISSILE_Y","native +46 (generic +38 plus +8 presentation correction)")
print("CHEST_HOLD","0x20 native process ticks")
print("V75_FLIGHT","UNCHANGED")
