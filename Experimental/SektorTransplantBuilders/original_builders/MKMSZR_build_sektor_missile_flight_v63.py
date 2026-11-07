#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse, bisect, hashlib, struct

parser=argparse.ArgumentParser(description='Build MKMSZR v63 Sektor chest-open + straight-missile visual/flight proof from the supplied v59 proof and MKT Rev.2 donor.')
parser.add_argument('v59_rom',type=Path)
parser.add_argument('mkt_rom',type=Path)
parser.add_argument('-o','--output',type=Path,default=Path('MKMSZR_sektor-missile-flight_common-proof_v63.z64'))
a=parser.parse_args()

v59=a.v59_rom.read_bytes(); mkt=a.mkt_rom.read_bytes()
V59_SHA='b8b1ddfa964de4da86dc9598f99139f4c50ac066deaaf4ab5cd91fda63baf1cc'
MKT_SHA='30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb'
assert hashlib.sha256(v59).hexdigest()==V59_SHA
assert hashlib.sha256(mkt).hexdigest()==MKT_SHA
rom=bytearray(v59)
RR=0xF40000
FILE87_SIZE=0x4E3FC
assert int.from_bytes(rom[0xA5668:0xA566C],'big')-RR==FILE87_SIZE

# ---------------------------------------------------------------------------
# Reconstruct the runtime-confirmed v62 baseline exactly from supplied v59.
# v60: first Scorpion/type-0x12 Cyrax-style lower-32 alternate TLUT.
CYRAX=bytes.fromhex(
 '0000df9ec75cb6faaab89a7791f2869a8a568214858f854d852b80c880648043'
 'f7bdef7be739d6b5ce73bdefb5adad6ba52998c690848c638842842180008000')
assert len(CYRAX)==64
assert bytes(rom[0xF858D0:0xF85910])==bytes.fromhex(
 '0000463135ad2d6b252921081ce718c614a510840c630842042100016fdf5f9f'
 '573f4adf469e427c3e3b39fa31d82db72976255521341d1210d10caf048e006b')
rom[0xF858D0:0xF85910]=CYRAX

# v61/v62: complete Sektor MKT combo graph with MKMSZ-safe reaction selectors.
def w16s(vals): return b''.join(int(x&0xffff).to_bytes(2,'big') for x in vals)
records=[
 [0x8009,0x1003,0x0300,0x1002,0x0000,0x0000,0x800B,0x10C0],
 [0x0009,0x1301,0x0303,0x1002,0x0100,0x0000,0x800B,0x10E0],
 [0x8009,0x0B01,0x0201,0x1002,0x0504,0x0000,0x0000,0x0010],
 [0x0009,0x1303,0x0103,0x1002,0x0401,0x0000,0x0000,0x0010],
 [0x8009,0x1101,0x0103,0x1002,0x0100,0x0000,0x800B,0x1100],
 [0x8009,0x1303,0x0103,0x1002,0x0401,0x0000,0x0000,0x0010],
]
for i,r in enumerate(records):rom[0xB1CB0+i*0x10:0xB1CC0+i*0x10]=w16s(r)
rom[0x9AD90:0x9ADA0]=w16s([0x8009,0x1101,0x0103,0x1002,0x0400,0,0,0x000E])
rom[0xA1CE8:0xA1CEC]=(0x8009A190).to_bytes(4,'big')

# ---------------------------------------------------------------------------
# MKT donor decoders / geometry.
MB=0x8881C0
ROBO_DICT=mkt[0x906A90:0x906B90]
assert len(ROBO_DICT)==0x100
SEKTOR_PALETTE32=bytes.fromhex(
 '0000defec63cb5baa95898f790b2843a88568014842f842d842b800880048003'
 'f7bdef7be739d6b5ce73bdefb5adad6ba52998c690848c638842842180008000')
TARGET=[int.from_bytes(SEKTOR_PALETTE32[i:i+2],'big') for i in range(0,64,2)]
# Authentic MKT ROCKET_P. Codec-16 rocket art uses only indices 0..15.
ROCKET_P=[0x001F,0x7FFF,0x6739,0x5EF7,0x5AD6,0x5294,0x4A52,0x4210,
          0x39CE,0x318C,0x35AD,0x2D6B,0x2529,0x1CE7,0x14A5,0x0C63,
          0x7FF4,0x7FE0,0x7F40,0x7EC0,0x7E20,0x7DA0,0x7D00,0x7C80,
          0x7400,0x6C00,0x5000,0x4800,0x3C00,0x3400,0x2800,0x2000]

def be16(b,o):return int.from_bytes(b[o:o+2],'big')
def be32(b,o):return int.from_bytes(b[o:o+4],'big')
def put32(b,o,v):b[o:o+4]=int(v&0xffffffff).to_bytes(4,'big')
def s16(v):return v-0x10000 if v&0x8000 else v
def s32(v):return v-0x100000000 if v&0x80000000 else v
def align4(v):return (v+3)&~3
def align2(v):return (v+1)&~1
def m32(rel):return be32(mkt,MB+rel)

class BitReader:
 def __init__(self,d):self.d=d;self.bit=0
 def read(self,n):
  v=0
  for _ in range(n):
   byte=self.d[self.bit>>3];sh=7-(self.bit&7);self.bit+=1;v=(v<<1)|((byte>>sh)&1)
  return v
class BitWriter:
 def __init__(self):self.out=bytearray();self.cur=0;self.n=0
 def write(self,v,n):
  assert n>=0 and (n==0 or 0<=v<(1<<n))
  for sh in range(n-1,-1,-1):
   self.cur=(self.cur<<1)|((v>>sh)&1);self.n+=1
   if self.n==8:self.out.append(self.cur);self.cur=0;self.n=0
 def finish(self):
  if self.n:self.out.append(self.cur<<(8-self.n));self.cur=0;self.n=0
  return bytes(self.out)

def dec_22_24(src):
 typ=src[0];n=int.from_bytes(src[:4],'big')&0xffffff
 if typ==24:top=src[4:8];fp=8;mini=None
 elif typ==23:top=None;mini=src[4];fp=5
 elif typ==22:top=None;mini=0;fp=4
 else:raise ValueError(typ)
 fl=src[fp];fp+=1
 if fl&0x80:fl=((fl&0x7f)<<8)|src[fp];fp+=1
 fd=src[fp:];sp=fp+fl;bc=8;fi=0;flip=fd[0] if fd else 0;fi=1 if fd else 0;out=bytearray()
 while len(out)<n:
  ch=src[sp];sp+=1
  if ch&0x80:
   ix=(ch&0x7f)<<1
   out.extend((ROBO_DICT[ix+1],ROBO_DICT[ix]) if flip&0x80 else (ROBO_DICT[ix],ROBO_DICT[ix+1]))
   bc-=1
   if bc==0:flip=fd[fi];fi+=1;bc=8
   else:flip=(flip<<1)&0xff
  else:
   sw=ch>>5;ch&=31
   if sw==3:cnt=src[sp];sp+=1;out+=bytes([ch])*cnt
   elif sw==2:
    if top is None:cnt=ch+3;pix=mini
    else:cnt=(ch&7)+3;pix=top[(ch>>3)&3]
    out+=bytes([pix])*cnt
   elif sw==1:out+=bytes([ch,ch])
   else:out.append(ch)
 assert len(out)==n
 return bytes(out)

def dec_16(src):
 # Retail MKT 0x80082820 grammar (type 16): zero runs, short repeats,
 # extended repeats, and packed 4-bit literal runs.
 assert src[0]==16
 n=int.from_bytes(src[:4],'big')&0xffffff;p=4;out=bytearray()
 while len(out)<n:
  ch=src[p];p+=1
  if ch&0x80:
   out+=b'\0'*((ch&0x7f)+7);continue
  hi=ch>>4;pix=ch&0x0f
  if hi==0:
   cnt=src[p];p+=1;out+=bytes([pix])*cnt
  elif hi<=6:out+=bytes([pix])*hi
  else:
   cnt=pix+3
   while cnt:
    q=src[p];p+=1;out.append(q>>4);cnt-=1
    if cnt:out.append(q&0x0f);cnt-=1
 assert len(out)==n
 return bytes(out)

def target_rgb(v):return(v&31,(v>>5)&31,(v>>10)&31)
def rgba5551_to_target(v):
 r=(v>>11)&31;g=(v>>6)&31;b=(v>>1)&31;a=v&1
 return(a<<15)|(b<<10)|(g<<5)|r
# Deliberately constrain rocket to Sektor's resident gray/metal half, never armor/red.
ROCKET_TO_SEKTOR={0:0}
for i,v in enumerate(ROCKET_P[1:16],1):
 c=target_rgb(rgba5551_to_target(v))
 ROCKET_TO_SEKTOR[i]=min(range(16,32),key=lambda j:sum((a-b)**2 for a,b in zip(c,target_rgb(TARGET[j]))))
assert set(ROCKET_TO_SEKTOR.values())-{0} <= set(range(16,32))

def make_blocks(raw,stride,eh):
 assert stride%4==0 and eh%2==0
 out=[]
 for y in range(0,eh,2):
  for x in range(0,stride,4):out.append(raw[y*stride+x:y*stride+x+4]+raw[(y+1)*stride+x:(y+1)*stride+x+4])
 return out

def donor_frame(rel,rocket=False):
 assert m32(rel)==rel+8 and m32(rel+4)==0,hex(rel)
 sub=MB+rel+8;img=be32(mkt,sub);packed=be32(mkt,sub+4);anchor=be32(mkt,sub+8)
 h=(packed>>16)&0xffff;w=packed&0xffff;x=s16(anchor>>16);y=s16(anchor&0xffff)
 src=mkt[MB+img:];typ=src[0]
 raw=dec_16(src) if typ==16 else dec_22_24(src)
 stride=align4(w);assert len(raw)==h*stride,(hex(rel),typ,w,h,len(raw))
 if rocket:
  assert max(raw)<=15
  raw=bytes(ROCKET_TO_SEKTOR[v] for v in raw)
 eh=align2(h)
 if eh>h:raw+=b'\0'*(stride*(eh-h))
 return dict(rel=rel,w=w,h=h,x=x,y=y,stride=stride,eh=eh,padded=raw,blocks=make_blocks(raw,stride,eh),codec=typ,img=img)

# Exact N64 donor poses used by the proof.
frames=[donor_frame(0x29A0),donor_frame(0x29B4),donor_frame(0x2668,True),donor_frame(0x267C,True)]
assert [(f['w'],f['h'],f['codec']) for f in frames]==[(46,115,22),(47,113,22),(39,9,16),(42,10,16)]
assert hashlib.sha256(frames[0]['padded']).hexdigest()=='9aae27a0624258a24717cf129d75947ad6e7302b16e70aad9cddb3eb4e051389'
assert hashlib.sha256(frames[1]['padded']).hexdigest()=='1bb7d592d4b0eaf27a45b1557b7e0e6d0430ccf453fb8ea1bd6e8de1cdfe756e'
assert hashlib.sha256(frames[2]['padded']).hexdigest()=='4da8898fb7efd41967fccbf2ae941991078a1128d1ba4ee0af596202a573eb3f'
assert hashlib.sha256(frames[3]['padded']).hexdigest()=='936329a3735c4c99e3fd198184e754cb500470b27003840f646c55df74336e8f'

# ---------------------------------------------------------------------------
# Exact one-model MKMSZ Type-5 pack for these four frames.
ZERO=b'\0'*8
freq=Counter(p for f in frames for p in f['blocks'] if p!=ZERO)
patterns=sorted(freq,key=lambda p:(-freq[p],p));pidx={p:i for i,p in enumerate(patterns)}

def best_partition():
 used=sorted((pidx[p],w,p) for p,w in freq.items());idx=[x[0] for x in used];wt=[x[1] for x in used];pref=[0]
 for w in wt:pref.append(pref[-1]+w)
 n=len(used)
 @lru_cache(None)
 def dp(pos,k):
  if pos>=n:return(0,())
  if k==0:return(10**30,None)
  base=idx[pos];best=(10**30,None)
  for bits in range(1,17):
   q=bisect.bisect_left(idx,base+(1<<bits),pos,n)
   if q==pos:continue
   rc,rp=dp(q,k-1);cost=bits*(pref[q]-pref[pos])+rc
   if rp is not None and cost<best[0]:best=(cost,((base,bits,pos,q),)+rp)
  return best
 _,plan=dp(0,13);assert plan is not None
 if len(plan)<13:
  base=plan[-1][0] if plan else 0;plan=plan+tuple((base,1,n,n) for _ in range(13-len(plan)))
 cmap={}
 for ci,(base,bits,aa,qq) in enumerate(plan):
  for j in range(aa,qq):ix,w,p=used[j];cmap[p]=(ci,ix-base,bits)
 return plan,cmap
plan,cmap=best_partition();ZBITS=[2,2,3];ZBASE=[0,4,8]
@lru_cache(None)
def zero_plan(n):
 if n==0:return(0,())
 best=(10**9,None)
 for zi,(bits,base) in enumerate(zip(ZBITS,ZBASE)):
  for extra in range(1<<bits):
   cnt=base+extra+1
   if cnt<=n:
    pc,pp=zero_plan(n-cnt);cost=pc+4+bits
    if cost<best[0]:best=(cost,pp+((13+zi,extra,bits,cnt),))
 return best
streams=[]
for fr in frames:
 bw=BitWriter();bw.write(0,6);bl=fr['blocks'];i=0
 while i<len(bl):
  if bl[i]==ZERO:
   j=i+1
   while j<len(bl) and bl[j]==ZERO:j+=1
   for sym,extra,bits,_cnt in zero_plan(j-i)[1]:bw.write(sym,4);bw.write(extra,bits)
   i=j
  else:
   ci,extra,bits=cmap[bl[i]];bw.write(ci,4);bw.write(extra,bits);i+=1
 s=bw.finish();s+=b'\0'*((-len(s))&3);streams.append(s)
assert [len(s) for s in streams]==[500,480,52,56]

def pack_pattern(block):
 bw=BitWriter()
 for px in block:assert 0<=px<32;bw.write(px,5)
 out=bw.finish();assert len(out)==5;return out

table=bytearray((2).to_bytes(2,'big')+(1).to_bytes(2,'big'))
rec=bytearray(104);rec[0:4]=(0).to_bytes(4,'big');rec[4:6]=(5).to_bytes(2,'big')
for i,(_base,bits,_aa,_qq) in enumerate(plan):rec[6+2*i:8+2*i]=bits.to_bytes(2,'big')
for i,bits in enumerate(ZBITS):rec[32+2*i:34+2*i]=bits.to_bytes(2,'big')
for i,(base,_bits,_aa,_qq) in enumerate(plan):rec[40+4*i:44+4*i]=base.to_bytes(4,'big')
for i,base in enumerate(ZBASE):rec[92+4*i:96+4*i]=base.to_bytes(4,'big')
table+=rec
for p in patterns:table+=pack_pattern(p)
assert len(patterns)==746 and len(table)==3838

# Closed/unreachable stock special-animation bank established by the prior audit.
DEAD_LO=0x41984;DEAD_HI=0x43190
assert DEAD_HI-DEAD_LO==0x180C
# Guard the exact pre-proof bank so a later builder cannot silently reuse it.
EXPECTED_DEAD_SHA='a52d1f20875d90a50ef1dbf8474a7f97306cd220aebbc9ffb0c464ef775dd615'
actual_dead_sha=hashlib.sha256(bytes(rom[RR+DEAD_LO:RR+DEAD_HI])).hexdigest()
assert actual_dead_sha==EXPECTED_DEAD_SHA,(actual_dead_sha,EXPECTED_DEAD_SHA)

TABLE_OFF=DEAD_LO
cursor=align4(TABLE_OFF+len(table))
shape_offsets=[]
for fr,s in zip(frames,streams):
 shape_offsets.append(cursor);cursor+=32+len(s)
assert shape_offsets==[0x42884,0x42A98,0x42C98,0x42CEC]
assert cursor==0x42D44 and cursor<=DEAD_HI
rom[RR+TABLE_OFF:RR+TABLE_OFF+len(table)]=table
# Keep 2-byte alignment pad deterministic/zero.
rom[RR+TABLE_OFF+len(table):RR+align4(TABLE_OFF+len(table))]=b'\0'*(align4(TABLE_OFF+len(table))-(TABLE_OFF+len(table)))
for fr,s,shape in zip(frames,streams,shape_offsets):
 sub=shape+8;image=sub+12
 put32(rom,RR+shape,sub);put32(rom,RR+shape+4,0);put32(rom,RR+sub,image)
 rom[RR+sub+4:RR+sub+6]=fr['w'].to_bytes(2,'big');rom[RR+sub+6:RR+sub+8]=fr['h'].to_bytes(2,'big')
 rom[RR+sub+8:RR+sub+10]=(fr['x']&0xffff).to_bytes(2,'big');rom[RR+sub+10:RR+sub+12]=(fr['y']&0xffff).to_bytes(2,'big')
 rom[RR+image:RR+image+4]=b'\x05\0\0\0';put32(rom,RR+image+4,TABLE_OFF-image);put32(rom,RR+image+8,(fr['eh']<<16)|fr['stride'])
 rom[RR+image+12:RR+image+12+len(s)]=s

# Exact software round-trip of every new Type-5 frame.
def decode_new(shape):
 assert be32(rom,RR+shape)==shape+8 and be32(rom,RR+shape+4)==0
 sub=shape+8;image=be32(rom,RR+sub);assert bytes(rom[RR+image:RR+image+4])==b'\x05\0\0\0'
 to=image+s32(be32(rom,RR+image+4));assert to==TABLE_OFF
 dims=be32(rom,RR+image+8);height=dims>>16;width=dims&0xffff
 rows=be16(rom,RR+to);mc=be16(rom,RR+to+2);assert(rows,mc)==(2,1)
 mo=to+4;pbase=to+4+104
 nbits=[be16(rom,RR+mo+6+2*i) for i in range(13)];zbits=[be16(rom,RR+mo+32+2*i) for i in range(3)]
 bases=[be32(rom,RR+mo+40+4*i) for i in range(13)];zbases=[be32(rom,RR+mo+92+4*i) for i in range(3)]
 br=BitReader(bytes(rom[RR+image+12:RR+DEAD_HI]));assert br.read(6)==0
 out=bytearray(width*height);bw=width//4;total=bw*(height//2);bi=0
 while bi<total:
  code=br.read(4)
  if code<13:
   pi=bases[code]+br.read(nbits[code]);po=pbase+pi*5;pbr=BitReader(bytes(rom[RR+po:RR+po+5]));vals=[pbr.read(5) for _ in range(8)]
   by,bx=divmod(bi,bw)
   out[(by*2)*width+bx*4:(by*2)*width+bx*4+4]=bytes(vals[:4])
   out[(by*2+1)*width+bx*4:(by*2+1)*width+bx*4+4]=bytes(vals[4:])
   bi+=1
  else:
   zi=code-13;bi+=zbases[zi]+br.read(zbits[zi])+1;assert bi<=total
 return bytes(out),width,height
for fr,shape in zip(frames,shape_offsets):
 dec,w,h=decode_new(shape);assert(w,h)==(fr['stride'],fr['eh']) and dec==fr['padded']

CHEST1,CHEST2,MISSILE1,MISSILE2=shape_offsets
# Stock Ice launch secondary slot 6 has seven visual positions; use authentic chest poses
# in an open/hold/close presentation. Its control grammar stays stock.
assert [be32(rom,RR+0x11AC+4*i) for i in range(7)]==[0x34A58]*6+[0]
chest_script=[CHEST1,CHEST2,CHEST2,CHEST2,CHEST1,CHEST1,0]
for i,v in enumerate(chest_script):put32(rom,RR+0x11AC+4*i,v)
# Stock basic Ice projectile points through +0xFD0 -> +0xD90. Preserve that routing,
# replace only its two-frame loop with the genuine horizontal Sektor rocket.
assert be32(rom,RR+0xFD0)==0xD90
assert [be32(rom,RR+0xD90+4*i) for i in range(4)]==[0x34A58,0x34A58,1,0xD90]
for i,v in enumerate([MISSILE1,MISSILE2,1,0xD90]):put32(rom,RR+0xD90+4*i,v)

# Replace Ice Blast's two-direction Low-Punch command with authentic Sektor F,F+LP.
# Descriptor base ROM 0xB1B38: right tokens at +0x12, left at +0x1E.
assert rom[0xB1B4A:0xB1B50]==bytes.fromhex('000900070000')
assert rom[0xB1B56:0xB1B5C]==bytes.fromhex('000800070000')
rom[0xB1B4C:0xB1B4E]=(9).to_bytes(2,'big')
rom[0xB1B58:0xB1B5A]=(8).to_bytes(2,'big')

# File allocation must remain exactly the runtime-confirmed v62/v59 footprint.
assert int.from_bytes(rom[0xA5668:0xA566C],'big')-RR==FILE87_SIZE
assert cursor<DEAD_HI<RR  # file-relative sanity only; RR is much larger

# Guarded patch-scope audit versus exact reconstructed v62 before CRC.
base=bytearray(v59);base[0xF858D0:0xF85910]=CYRAX
for i,r in enumerate(records):base[0xB1CB0+i*0x10:0xB1CC0+i*0x10]=w16s(r)
base[0x9AD90:0x9ADA0]=w16s([0x8009,0x1101,0x0103,0x1002,0x0400,0,0,0x000E]);base[0xA1CE8:0xA1CEC]=(0x8009A190).to_bytes(4,'big')
allowed=[(0xB1B4C,0xB1B4E),(0xB1B58,0xB1B5A),(RR+0x11AC,RR+0x11C8),(RR+0xD90,RR+0xDA0),(RR+DEAD_LO,RR+cursor)]
def in_allowed(i):return any(lo<=i<hi for lo,hi in allowed)
diffs=[i for i,(x,y) in enumerate(zip(base,rom)) if x!=y]
assert diffs and all(in_allowed(i) for i in diffs),hex(next(i for i in diffs if not in_allowed(i))) if any(not in_allowed(i) for i in diffs) else ''

# N64 CIC-6102 header CRC.
def rol(v,s):return((v<<s)|(v>>(32-s)))&0xffffffff
def n64crc(b):
 seed=0xF8CA4DDC;t1=t2=t3=t4=t5=t6=seed
 for off in range(0x1000,0x101000,4):
  d=int.from_bytes(b[off:off+4],'big')
  if ((t6+d)&0xffffffff)<t6:t4=(t4+1)&0xffffffff
  t6=(t6+d)&0xffffffff;t3^=d;r=rol(d,d&31);t5=(t5+r)&0xffffffff
  if t2>d:t2^=r
  else:t2^=t6^d
  t1=(t1+(t5^d))&0xffffffff
 return(t6^t4^t3)&0xffffffff,(t5^t2^t1)&0xffffffff
c1,c2=n64crc(rom);rom[0x10:0x18]=struct.pack('>II',c1,c2)

# Final static assertions.
assert int.from_bytes(rom[0xA5668:0xA566C],'big')-RR==FILE87_SIZE
assert [be32(rom,RR+0x11AC+4*i) for i in range(7)]==chest_script
assert [be32(rom,RR+0xD90+4*i) for i in range(4)]==[MISSILE1,MISSILE2,1,0xD90]
assert be16(rom,0xB1B4A)==9 and be16(rom,0xB1B4C)==9 and be16(rom,0xB1B56)==8 and be16(rom,0xB1B58)==8

a.output.write_bytes(rom)
print('OUT',a.output)
print('SHA256',hashlib.sha256(rom).hexdigest())
print('CRC1_CRC2',f'{c1:08X}',f'{c2:08X}')
print('FILE87_SIZE',hex(FILE87_SIZE),'UNCHANGED')
print('DEAD_BANK',hex(DEAD_LO),hex(DEAD_HI),'USED_END',hex(cursor),'SLACK',hex(DEAD_HI-cursor))
print('NEW_SHAPES',*[hex(x) for x in shape_offsets])
print('TYPE5_PATTERNS',len(patterns),'STREAM_BYTES',sum(map(len,streams)),'PACK_BYTES',hex(cursor-DEAD_LO))
print('ROCKET_TO_SEKTOR',ROCKET_TO_SEKTOR)
print('INPUT','F,F+LP (right 9,9 / left 8,8)')
print('CONTACT','stock Ice projectile collision behavior intentionally still present; this is visual/spawn/flight proof only')
