#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

V75_SHA256='e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb'
SIZE=0x1000000
p=argparse.ArgumentParser(description='Build Sektor straight-missile donor base-alignment v77 from exact Runtime-confirmed v75.')
p.add_argument('v75_rom',type=Path)
p.add_argument('-o','--output',type=Path,default=Path('MKMSZR_sektor-missile-basealign_common-proof_v77.z64'))
a=p.parse_args()
rom=bytearray(a.v75_rom.read_bytes())
assert len(rom)==SIZE
assert hashlib.sha256(rom).hexdigest()==V75_SHA256

def u32(o): return int.from_bytes(rom[o:o+4],'big')
def w32(o,v): rom[o:o+4]=int(v&0xffffffff).to_bytes(4,'big')
R={'zero':0,'v0':2,'a0':4,'a1':5,'a2':6,'t0':8,'t1':9,'t4':12,'sp':29,'ra':31}
def I(op,rs,rt,imm): return ((op&63)<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def J(op,va): return ((op&63)<<26)|((va>>2)&0x03ffffff)
def jal(va): return J(3,va)
def words(xs): return b''.join(int(x&0xffffffff).to_bytes(4,'big') for x in xs)

# v77 scope: isolate the newly traced donor pre-adjust Y origin semantics.
# Base = owner Y, then donor single-part match_ani_points contributes aniyoff +3,
# then the already-proven retail adjust_xy Y=+38 is applied by native 0x80031208.
# Thus visible actor-origin target for this bounded vertical proof is ownerY + 3 + 38.
# X remains the Runtime-confirmed v75/v72 path unchanged; no by-eye X tuning.
# v75 flight magnitude/cadence, collision, helpers, chest marker, art, palette, SFX,
# input and lifecycle remain byte-identical.

# Guard Runtime-confirmed v75 placement call.
assert u32(0x4BBF0)==I(0x09,'zero','a1',5)
assert u32(0x4BBF4)==0
assert u32(0x4BBF8)==0x8C440648
assert u32(0x4BBFC)==I(0x09,'zero','a2',38)
assert u32(0x4BC00)==jal(0x80031208)
assert u32(0x4BC04)==0

# Compact the already-stable v75 projectile first-frame wrapper without changing
# its semantics. v72 removed the obsolete +/-96px correction, leaving branch/jump
# scaffolding that is no longer needed. Reclaim only this existing proof-owned
# interval; do not allocate a new cave.
WR=0x9AE10; WR_VA=0x8009A210; SHIM_ROM=0x9AE68; SHIM_VA=0x8009A268; END=0x9AE90
# Guard recognizable v75 wrapper entry and rocket-script install.
assert u32(WR)==I(0x09,'sp','sp',-0x20)
assert u32(WR+4)==I(0x2B,'sp','ra',0x1C)
assert u32(WR+8)==I(0x2B,'sp','a0',0x18)
assert u32(0x9AE5C)==I(0x09,'t4','t4',0x0D90)
assert u32(0x9AE60)==I(0x2B,'t0','t4',0x06E4)
assert u32(0x9AE64)==jal(0x800304C0)

wrap=[
    I(0x09,'sp','sp',-0x20),
    I(0x2B,'sp','ra',0x1C),
    I(0x2B,'sp','a0',0x18),
    I(0x0F,'zero','t0',0x802F),
    I(0x23,'t0','t0',0xCE20),
    I(0x23,'t0','t1',0x06E4),
    I(0x2B,'sp','t1',0x14),
    I(0x29,'a0','zero',0x009E),       # native Sektor palette selector
    I(0x23,'a0','t1',0x0098),
    I(0x09,'t1','t1',0x0D90),        # genuine rocket first-frame script
    I(0x2B,'t0','t1',0x06E4),
    jal(0x800304C0),
    0,
    I(0x0F,'zero','t0',0x802F),
    I(0x23,'t0','t0',0xCE20),
    I(0x23,'sp','t1',0x14),
    I(0x2B,'t0','t1',0x06E4),
    I(0x23,'sp','a0',0x18),
    I(0x23,'sp','ra',0x1C),
    I(0x09,'sp','sp',0x20),
    ((R['ra']<<21)|0x08),
    0,
]
wb=words(wrap)
assert WR+len(wb)<=SHIM_ROM
rom[WR:END]=b'\x00'*(END-WR)
rom[WR:WR+len(wb)]=wb

# Compact vertical base-alignment shim in the reclaimed tail of the same
# proof-owned wrapper interval. At the stock placement call, v0=current parent
# process and a0=staged projectile (+0x648); +0x6E0 is the owner actor.
# Donor match_ani_points sets projectile Y from owner Y and then adds the missile
# descriptor aniyoff (+3). Native 0x80031208 then applies the proven retail +38.
shim=[
    I(0x23,'v0','t0',0x06E0),       # owner actor
    I(0x23,'t0','t1',0x0030),       # owner Y fixed8
    I(0x09,'t1','t1',0x0300),       # donor missile aniyoff +3
    J(2,0x80031208),                 # tail-call native (+5,+38)
    I(0x2B,'a0','t1',0x0030),       # delay: projectile Y = ownerY + 3
]
sb=words(shim)
assert SHIM_ROM+len(sb)<=END
rom[SHIM_ROM:SHIM_ROM+len(sb)]=sb

# Redirect only the placement call to the shim. Arguments stay proven +5,+38.
w32(0x4BC00,jal(SHIM_VA))

# Strong guards: v75 movement child/callback and stock projectile setup untouched.
assert bytes(rom[0x9AE90:0x9AF20])==a.v75_rom.read_bytes()[0x9AE90:0x9AF20]
assert u32(0x4C468)==0x3C050004
assert u32(0x4C46C)==jal(0x8004CC14)
assert u32(0x4C470)==I(0x09,'zero','a2',3)
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
print('OUTPUT',a.output)
print('SHA256',hashlib.sha256(rom).hexdigest())
print('CRC1/CRC2',f'{crc1:08X} / {crc2:08X}')
print('TEST_INPUT','Forward, Forward + Low Punch')
print('V77_SCOPE','v75 + donor-derived vertical pre-adjust base alignment only')
print('Y_SEMANTICS','projectileY = ownerY + donor anchor 3; then native local +38')
print('V75_FLIGHT','UNCHANGED')
