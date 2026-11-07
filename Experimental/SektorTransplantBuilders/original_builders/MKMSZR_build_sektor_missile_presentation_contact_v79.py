#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

V75_SHA256="e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
SIZE=0x1000000
p=argparse.ArgumentParser(description="Build Sektor missile v79 presentation/contact proof from exact runtime-confirmed v75.")
p.add_argument("v75_rom",type=Path)
p.add_argument("-o","--output",type=Path,default=Path("MKMSZR_sektor-missile-presentation-contact_common-proof_v79.z64"))
a=p.parse_args()
base=a.v75_rom.read_bytes(); rom=bytearray(base)
assert len(rom)==SIZE and hashlib.sha256(rom).hexdigest()==V75_SHA256

def u32(o): return int.from_bytes(rom[o:o+4],"big")
def w32(o,v): rom[o:o+4]=int(v&0xffffffff).to_bytes(4,"big")
R={'zero':0,'v0':2,'a0':4,'a1':5,'a2':6,'t0':8,'t1':9,'t2':10,'t3':11,'t4':12,
   's0':16,'s1':17,'sp':29,'ra':31}
def I(op,rs,rt,imm): return ((op&63)<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def RR(rs,rt,rd,sh,fn): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|((sh&31)<<6)|(fn&63)
def J(op,va): return ((op&63)<<26)|((va>>2)&0x03ffffff)

# ---------------------------------------------------------------------------
# v79: one meaningful composition proof, built from stable v75.
#
# 1) Reduced chest ANIMATION, not a one-frame injection:
#    - expand the dedicated chest script to eight repetitions of the one
#      available genuine open-chest shape;
#    - do NOT restore the old Ice cursor after the first chest frame;
#    - the seven subsequent stock animation-advance calls consume the remaining
#      seven identical chest frames;
#    - resample the six post-launch stock sleeps to total 0x20 target ticks,
#      matching donor do_robo_zap's process_sleep(0x20) recovery interval.
#
# 2) Projectile palette binding:
#    - stop forcing palette selector 0;
#    - copy the already-correct Sektor owner selector (caller s0) into the
#      projectile before stock 0x800304C0 binds the genuine rocket frame.
#      This uses the normal MKMSZ frame/palette bind path.
#
# 3) Remove the inherited Ice screen-tint helper VISUAL while preserving its
#    helper process lifetime/exit. Only its 0x80044964 presentation call is NOP'd.
#
# 4) Contact semantics:
#    - keep the proven generic projectile collision loop and selector 0x13;
#    - translate the type-4 selector-0x13 strike record away from Ice freeze:
#      unblocked reaction 0x2C -> target-native 0x04 (runtime-confirmed safe
#      hard-hit reaction family from v62), normal damage 0 -> 20, block damage
#      0 -> 2. Existing target hitbox and blocked reaction remain unchanged.
#
# Deliberately NOT changed yet:
#    v75 flight, (+5,+38) placement, clone helper actor process, smoke,
#    explosion, imported audio.
# ---------------------------------------------------------------------------

# ---- 1. reduced chest animation ----
RR_BASE=0xF40000
CHEST_SCRIPT_OFF=0x4E788
CHEST_ROM=RR_BASE+CHEST_SCRIPT_OFF
CHEST_SHAPE=u32(CHEST_ROM)
assert CHEST_SHAPE==0x0004E3E8
assert u32(CHEST_ROM+4)==0
assert u32(0xA5668)==0xF8E790
assert set(rom[CHEST_ROM+8:CHEST_ROM+0x24])=={0xFF}

# Eight identical genuine chest frames + terminator.
for i in range(8):
    w32(CHEST_ROM+i*4,CHEST_SHAPE)
w32(CHEST_ROM+8*4,0)
NEW_FILE_END=CHEST_ROM+9*4
w32(0xA5668,NEW_FILE_END)

# v69/v75 wrapper: after installing first chest frame, leave +0x6E4 pointing
# at the reduced chest script instead of restoring the saved Ice cursor.
assert u32(0x9ADEC)==0xAD1006E4
w32(0x9ADEC,0)

# Seven later stock 0x800304C0 calls now consume the seven remaining copies:
# one pre-launch at 0x8004AED8, six post-launch at B0F4/B108/B124/B140/B15C/B178/B194
# (the first post-launch pair occurs before the first sleep). The six sleeps
# after launch are resampled to total 0x20 ticks.
sleep_sites=[0x4BD14,0x4BD30,0x4BD4C,0x4BD68,0x4BD84,0x4BDA0]
old=[2,2,3,4,5,5]
new=[4,4,6,6,6,6]
for off,o,n in zip(sleep_sites,old,new):
    assert u32(off)==I(0x09,'zero','a0',o)
    w32(off,I(0x09,'zero','a0',n))
assert sum(new)==0x20

# ---- 2. bind projectile to owner's Sektor palette selector ----
# At the stock 0x8004B040 wrapper call, caller s0 still holds the owner actor.
# Replace "sh zero,+0x9E(a0)" plus obsolete v70/v72 correction setup with:
#     lhu t2,+0x9E(s0)
#     sh  t2,+0x9E(a0)
# and NOP the now-dead correction fragment through 0x9AE54.
assert u32(0x9AE2C)==I(0x29,'a0','zero',0x009E)
w32(0x9AE2C,I(0x25,'s0','t2',0x009E))
w32(0x9AE30,I(0x29,'a0','t2',0x009E))
for off in range(0x9AE34,0x9AE58,4):
    w32(off,0)
# Genuine rocket frame setup remains unchanged.
assert u32(0x9AE58)==I(0x23,'a0','t4',0x0098)
assert u32(0x9AE64)==J(0x03,0x800304C0)

# ---- 3. remove inherited Ice blue-screen tint, preserve process exit ----
assert u32(0x4B728)==J(0x03,0x80044964)
assert u32(0x4B730)==J(0x03,0x80028564)
w32(0x4B728,0)

# ---- 4. translated contact: damage/hard reaction, no freeze ----
# Fighter type 4 strike table pointer for selector 0x13 -> VA 0x800AF634,
# ROM 0xB0234. Preserve target-native hitbox and blocked reaction.
STRIKE=0xB0234
assert bytes(rom[STRIKE:STRIKE+16])==bytes.fromhex(
    "0004 fff3 0050 0014 2c05 0000 0001 0000".replace(" ","")
)
rom[STRIKE+8]=0x04     # target-native hard-hit reaction family
# STRIKE+9 remains 0x05 (target blocked reaction)
rom[STRIKE+10]=0x14    # 20 normal damage
rom[STRIKE+11]=0x02    # 2 blocked damage

# Strong scope guards: v75 movement child/callback and proven placement untouched.
assert bytes(rom[0x9AE90:0x9AF20])==base[0x9AE90:0x9AF20]
assert u32(0x4BBF0)==I(0x09,'zero','a1',5)
assert u32(0x4BBFC)==I(0x09,'zero','a2',38)
assert u32(0x4BC00)==J(0x03,0x80031208)
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
print("CHEST","8-frame reduced animation, one genuine frame repeated; post-launch sleeps total 0x20")
print("PROJECTILE_PALETTE","owner Sektor selector copied before native frame bind")
print("ICE_SCREEN_TINT","presentation call removed; helper process exit preserved")
print("CONTACT","selector 0x13 target record: hard reaction 0x04, damage 20/2; no freeze selector")
print("V75_FLIGHT_PLACEMENT","UNCHANGED")
