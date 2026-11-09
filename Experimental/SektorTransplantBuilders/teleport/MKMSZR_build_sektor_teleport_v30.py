from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse, bisect, hashlib

parser = argparse.ArgumentParser(description='Build MKMSZR Sektor teleport proof v30: v05-equivalent Sektor body repacked as 16-colour 4-bpp Type-5, plus the genuine MKT Sektor F,F+LK teleport uppercut on the Reverse Elbow v6 host lifecycle, with the donor teleport sound, Sektor\'s MKT voice/attack sounds and Sektor\'s MKT combo strings in place of Sub-Zero\'s; stock Ice Blast re-hosted (lifted) in the payload; rocket art + palette on the straight projectile; rocket first frame filled through the slot\'s stock storage (no texture allocation); rocket spawns at the MKT retail placement (+5,+38) px = (+10,+76) host units and draws behind Sektor; the teleport reappears on the target\'s floor; MKT chest open/hold/close around the rocket; MKT rocket flight (two-frame loop, donor speeds/acceleration/cap, flies from creation); rocket spawn +4 px outward (runtime-observed); 16 KiB arena, rocket setup from the lifted root (no token-handler patches, no code in the RSP microcode cave); MKT rocket sounds (chest open, launch, boom).')
parser.add_argument('clean_rom', type=Path, help='Clean supported MKMSZ USA Rev. 0 .z64')
parser.add_argument('mkt_rom', type=Path, help='MKT USA Rev. 2 N64 donor .z64')
parser.add_argument('-o', '--output', type=Path, default=Path('MKMSZR_sektor-teleport_common-proof_v30.z64'))
parser.add_argument('--v53', type=Path, default=None, help='Optional runtime-confirmed v53 ROM for an additional 129-frame inheritance cross-check')
args = parser.parse_args()
clean_path = args.clean_rom
mkt_path = args.mkt_rom
out_path = args.output

clean = clean_path.read_bytes()
mkt = mkt_path.read_bytes()
assert hashlib.sha256(clean).hexdigest() == '9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6'
assert hashlib.sha256(mkt).hexdigest() == '30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb'



MB = 0x8881C0
ROBO_DICT = mkt[0x906A90:0x906B90]
assert len(ROBO_DICT) == 0x100
ORIG_FILE87_ROM = 0x748920
CLEAN_SIZE = 0x459E0
RR = 0xF40000
TYPE_START = 0x14AC
TYPE_END = 0x41684
PALETTE_OFF = 0x4584C
SAFE_V49 = 0x4E544
ZERO_BLOCK = b'\0' * 8
# Exact runtime-confirmed v53 native Sektor TLUT lower half.
SEKTOR_PALETTE32 = bytes.fromhex(
    '0000defec63cb5baa95898f790b2843a88568014842f842d842b800880048003'
    'f7bdef7be739d6b5ce73bdefb5adad6ba52998c690848c638842842180008000'
)
assert len(SEKTOR_PALETTE32) == 64


def be16(b, o): return int.from_bytes(b[o:o+2], 'big')
def be32(b, o): return int.from_bytes(b[o:o+4], 'big')
def put32(b, o, v): b[o:o+4] = int(v & 0xffffffff).to_bytes(4, 'big')
def s16(v): return v - 0x10000 if v & 0x8000 else v
def s32(v): return v - 0x100000000 if v & 0x80000000 else v
def align4(v): return (v + 3) & ~3
def align2(v): return (v + 1) & ~1

def m32(rel): return be32(mkt, MB + rel)
def is_donor_shape(rel):
    return isinstance(rel, int) and rel > 0 and MB + rel + 8 <= len(mkt) and m32(rel) == rel + 8 and m32(rel + 4) == 0


class BitReader:
    def __init__(self, data): self.data = data; self.bit = 0
    def read(self, n):
        v = 0
        for _ in range(n):
            byte = self.data[self.bit >> 3]
            sh = 7 - (self.bit & 7)
            self.bit += 1
            v = (v << 1) | ((byte >> sh) & 1)
        return v


class BitWriter:
    def __init__(self): self.out = bytearray(); self.cur = 0; self.n = 0; self.bits = 0
    def write(self, v, n):
        assert n >= 0 and (n == 0 or 0 <= v < (1 << n))
        self.bits += n
        for sh in range(n-1, -1, -1):
            self.cur = (self.cur << 1) | ((v >> sh) & 1)
            self.n += 1
            if self.n == 8:
                self.out.append(self.cur); self.cur = 0; self.n = 0
    def finish(self):
        if self.n:
            self.out.append(self.cur << (8-self.n)); self.cur = 0; self.n = 0
        return bytes(self.out)


def dec_15(src):
    n = int.from_bytes(src[:4], 'big') & 0xffffff
    p = 4; out = bytearray()
    while len(out) < n:
        ch = src[p]; p += 1
        if ch & 0x80:
            out += bytes((0,)) * ((ch & 0x7f) + 1)
        elif ch & 0x40:
            out.append((ch >> 3) & 7)
            if len(out) < n: out.append(ch & 7)
        else:
            pix = ch & 7
            if pix == 0:
                pix = (ch >> 3) & 7
                cnt = src[p]; p += 1
                out += bytes((pix,)) * cnt
            else:
                cnt = ((ch >> 3) & 7) + 3
                out += bytes((pix,)) * cnt
    assert len(out) == n
    return bytes(out)


def dec_22_24(src, dictb=ROBO_DICT):
    typ = src[0]
    n = int.from_bytes(src[:4], 'big') & 0xffffff
    if typ == 24:
        top = src[4:8]; fp = 8; mini = None
    elif typ == 23:
        top = None; mini = src[4]; fp = 5
    elif typ == 22:
        top = None; mini = 0; fp = 4
    else:
        raise ValueError(typ)
    flip_len = src[fp]; fp += 1
    if flip_len & 0x80:
        flip_len = ((flip_len & 0x7f) << 8) | src[fp]; fp += 1
    flip_data = src[fp:]
    sp = fp + flip_len
    bit_count = 8
    fi = 0
    flip = flip_data[fi] if flip_data else 0
    fi += 1 if flip_data else 0
    out = bytearray()
    while len(out) < n:
        ch = src[sp]; sp += 1
        if ch & 0x80:
            idx = (ch & 0x7f) << 1
            if flip & 0x80: out.extend((dictb[idx+1], dictb[idx]))
            else: out.extend((dictb[idx], dictb[idx+1]))
            bit_count -= 1
            if bit_count == 0:
                flip = flip_data[fi]; fi += 1; bit_count = 8
            else:
                flip = (flip << 1) & 0xff
        else:
            sw = ch >> 5; ch &= 0x1f
            if sw == 3:
                cnt = src[sp]; sp += 1; out += bytes((ch,)) * cnt
            elif sw == 2:
                if top is None:
                    cnt = ch + 3; pix = mini
                else:
                    cnt = (ch & 7) + 3; pix = top[(ch >> 3) & 3]
                out += bytes((pix,)) * cnt
            elif sw == 1:
                out.append(ch); out.append(ch)
            else:
                out.append(ch)
    assert len(out) == n
    return bytes(out)


def make_blocks(padded, stride, eh):
    assert stride % 4 == 0 and eh % 2 == 0
    out = []
    for by in range(0, eh, 2):
        for bx in range(0, stride, 4):
            out.append(
                padded[by*stride+bx:by*stride+bx+4] +
                padded[(by+1)*stride+bx:(by+1)*stride+bx+4]
            )
    return out


def donor_frame(rel):
    o = MB + rel
    assert be32(mkt, o) == rel + 8 and be32(mkt, o+4) == 0, hex(rel)
    sub = o + 8
    image_rel = be32(mkt, sub)
    packed = be32(mkt, sub+4)
    anchor = be32(mkt, sub+8)
    h = (packed >> 16) & 0xffff
    w = packed & 0xffff
    x = s16((anchor >> 16) & 0xffff)
    y = s16(anchor & 0xffff)
    src = mkt[MB + image_rel:]
    typ = src[0]
    if typ == 15: raw = dec_15(src)
    elif typ in (22, 23, 24): raw = dec_22_24(src)
    else: raise ValueError((hex(rel), typ, hex(image_rel)))
    stride = align4(w)
    assert len(raw) == h * stride, (hex(rel), typ, w, h, len(raw))
    eh = align2(h)
    if eh > h: raw += bytes(stride * (eh-h))
    return dict(w=w,h=h,x=x,y=y,stride=stride,eh=eh,padded=raw,blocks=make_blocks(raw,stride,eh),codec=typ,donor=rel)


def visible_rows(fr):
    return [fr['padded'][y*fr['stride']:y*fr['stride']+fr['w']] for y in range(fr['h'])]


# MKT mechanical arm has its own 8-color MECARM_P palette. Convert the donor
# RGBA5551 colors into MKMSZ's A1BGR555 color space, then bind them to the closest
# entries already present in the runtime-confirmed native Sektor TLUT.
MECARM_RGBA5551=[0x07C0,0xD6B9,0xB5B1,0x94A9,0x6B5F,0x4215,0x294F,0x18CB]
TARGET_TLUT=[int.from_bytes(SEKTOR_PALETTE32[i:i+2],'big') for i in range(0,64,2)]
def target_rgb(v): return (v&31,(v>>5)&31,(v>>10)&31)
def rgba5551_to_target(v):
    r=(v>>11)&31; g=(v>>6)&31; b=(v>>1)&31; a=v&1
    return (a<<15)|(b<<10)|(g<<5)|r
ARM_TO_SEKTOR={0:0}
for i,v in enumerate(MECARM_RGBA5551[1:],1):
    c=target_rgb(rgba5551_to_target(v))
    ARM_TO_SEKTOR[i]=min(range(1,32),key=lambda j:sum((a-b)**2 for a,b in zip(c,target_rgb(TARGET_TLUT[j]))))
assert ARM_TO_SEKTOR=={0:0,1:17,2:19,3:20,4:22,5:24,6:25,7:26}

def composite(body, arm):
    # MKT anchors are actor-relative; nonzero arm pixels overlay the full body.
    bx0, by0 = -body['x'], -body['y']
    ax0, ay0 = -arm['x'], -arm['y']
    minx = min(bx0, ax0); miny = min(by0, ay0)
    maxx = max(bx0+body['w'], ax0+arm['w'])
    maxy = max(by0+body['h'], ay0+arm['h'])
    w = maxx-minx; h = maxy-miny
    stride = align4(w); eh = align2(h)
    out = bytearray(stride*eh)
    def blit(fr, x0, y0, remap=None):
        ox=x0-minx; oy=y0-miny
        for yy,row in enumerate(visible_rows(fr)):
            dst=(oy+yy)*stride+ox
            for xx,p in enumerate(row):
                if p:
                    out[dst+xx] = remap[p] if remap is not None else p
    blit(body,bx0,by0); blit(arm,ax0,ay0,ARM_TO_SEKTOR)
    raw=bytes(out)
    return dict(w=w,h=h,x=-minx,y=-miny,stride=stride,eh=eh,padded=raw,blocks=make_blocks(raw,stride,eh),codec='flattened-22+15')



# v53 common takeover mapping.
slot_cfg = {
    0x00: dict(name='idle', donor=0x1D4, target=0x2EC, words=[0x1768,0x1780,0x1794,0x17A8,0x17BC,1,0x1D4], mode='inplace'),
    0x01: dict(name='walk-f', donor=0x230, target=0x3C0, n=9, mode='inplace'),
    0x02: dict(name='walk-b', donor=0x254, target=0x3EC, n=9, mode='inplace'),
    0x03: dict(name='turn', donor=0x21C, target=0x418, n=5, mode='inplace'),
    0x04: dict(name='crouch', donor=0x278, target=0x42C, n=4, mode='inplace'),
    0x05: dict(name='crouch-turn', donor=0x2FC, target=0x43C, n=6, mode='inplace'),
    0x06: dict(name='crouch-block', donor=0x288, target=0x458, n=4, mode='inplace'),
    0x07: dict(name='crouch-hit', donor=0x298, target=0x468, n=4, mode='inplace'),
    0x08: dict(name='crouch-punch', donor=0x314, target=0x47C, n=8, mode='inplace'),
    0x09: dict(name='crouch-high-kick', donor=0x354, n=10, mode='relocated'),
    0x0A: dict(name='crouch-low-kick', donor=0x334, target=0x4C0, n=8, mode='inplace'),
    0x0B: dict(name='uppercut', donor=0x37C, target=0x49C, n=9, mode='inplace'),
    0x0C: dict(name='standing-block', donor=0x50C, target=0x624, n=4, mode='inplace'),
    0x0E: dict(name='high-punch', donor=0x3A0, target=0x504, n=28, mode='inplace'),
    0x0F: dict(name='low-punch', donor=0x410, target=0x574, n=27, mode='inplace'),
    0x11: dict(name='standing-high-kick', donor=0x5EC, n=13, mode='packed'),
    0x12: dict(name='standing-low-kick', donor=0x51C, n=13, mode='relocated'),
    0x13: dict(name='knee', donor=0x550, target=0x684, n=7, mode='inplace'),
    0x14: dict(name='sweep', donor=0x594, target=0x704, n=12, mode='inplace'),
    0x15: dict(name='roundhouse', donor=0x5C4, target=0x6DC, n=10, mode='inplace'),
    0x16: dict(name='jump', donor=0x620, target=0x734, n=4, mode='inplace'),
    0x17: dict(name='jump-kick', donor=0x630, target=0x744, n=7, mode='inplace'),
    0x18: dict(name='flip-punch', donor=0x668, target=0x77C, n=7, mode='inplace'),
    0x19: dict(name='flip-kick', donor=0x64C, target=0x760, n=7, mode='inplace'),
    0x1A: dict(name='forward-flip', donor=0x684, n=8, mode='relocated'),
    0x1B: dict(name='back-flip', donor=0x6A4, n=8, mode='relocated'),
    0x1C: dict(name='hit-high', donor=0x70C, target=0x7E8, n=5, mode='inplace'),
    0x1D: dict(name='hit-low', donor=0x720, target=0x7FC, n=5, mode='inplace'),
    0x1E: dict(name='knockdown', donor=0x808, target=0x874, n=9, mode='inplace'),
    0x1F: dict(name='sweep-fall', donor=0x1100, target=0x8B4, n=9, mode='inplace'),
    0x20: dict(name='stumble', donor=0x734, n=17, mode='relocated'),
    0x21: dict(name='getup', donor=0x82C, target=0x898, n=7, mode='inplace'),
    0x22: dict(name='sweep-getup', donor=0x1124, target=0x8D8, n=6, mode='inplace'),
}
for cfg in slot_cfg.values():
    if 'words' not in cfg: cfg['words'] = [m32(cfg['donor'] + 4*i) for i in range(cfg['n'])]
    else: cfg['n'] = len(cfg['words'])
    cfg['shapes'] = [v for v in cfg['words'] if is_donor_shape(v)]
assert slot_cfg[0x0B]['words'] == [0x1A54,0x1A68,0x1A7C,0x1A90,5,0x1AA4,0,0x1A90,0]
assert slot_cfg[0x14]['words'] == [0x1E28,0x1E3C,0x1E50,6,1,0x1E64,0x1E78,0,0x1E8C,0x1EA0,0x1EB4,0]
assert slot_cfg[0x20]['words'] == [0x21AC,0x21C0,0x21D4,0x21E8,0x21AC,0x21FC,0x2210,0,0x21AC,0x21C0,0x21D4,0x21E8,0x21AC,0x21FC,0x2210,1,0x754]

old_shapes=[]
for slot in sorted(slot_cfg):
    for rel in slot_cfg[slot]['shapes']:
        if rel not in old_shapes: old_shapes.append(rel)
assert len(old_shapes)==129
old_frames={rel:donor_frame(rel) for rel in old_shapes}

# New v54 visuals.
RUN_RELS=[0x2708,0x271C,0x2730,0x2744,0x2758,0x276C]  # RBRUN1,3,5,7,9,11
COMBO_RELS=[0x1C0C+i*0x14 for i in range(10)]            # RBELBOCOMBO1..10
BODY_REL=0x22EC                                           # RBSHOLDER4
ARM_RELS=[0x2318,0x2340,0x237C,0x2390,0x23B8,0x23CC,0x2408]  # seven sampled poses across Sektor's mechanical-arm arc
TELE_RELS=[0x2F08,0x2B48,0x2B5C,0x2B70,0x2B84]  # teleport: last frame of donor slot 0x0D + secondary slot 3
# v26: chest open frames (robot secondary slot 0: RBCHEST1, RBCHEST2) for the rocket.
import sys as _sys0
_sys0.path.insert(0, str(Path(__file__).resolve().parents[3] / 'src'))
from mkmszr.fighter_import.actions import robo_zap as _zap0
CHEST_RELS=list(_zap0.CHEST_FRAMES)
TELE_RELS=TELE_RELS+CHEST_RELS     # same entropy group and lossless pipeline as the teleport frames
new_frames={r:donor_frame(r) for r in RUN_RELS+COMBO_RELS+[BODY_REL]+ARM_RELS+TELE_RELS}
assert [(new_frames[r]['w'],new_frames[r]['h'],new_frames[r]['x'],new_frames[r]['y']) for r in CHEST_RELS]==[(46,115,19,-5),(47,113,20,-7)]
THROW_KEYS=[('throw-composite',r) for r in ARM_RELS]
throw_frames={k:composite(new_frames[BODY_REL],new_frames[k[1]]) for k in THROW_KEYS}
assert (throw_frames[('throw-composite',0x23B8)]['w'],throw_frames[('throw-composite',0x23B8)]['h'],throw_frames[('throw-composite',0x23B8)]['x'],throw_frames[('throw-composite',0x23B8)]['y'])==(114,115,88,-5)

# Compact v05 corpus: retail N64 MKT is the sole Run-pose authority.
# Keep only RBRUN1,3,5,7,9,11. The six WIMP-derived even poses and the
# rejected PS1 Run path are intentionally absent from both data and build inputs.
base_frame_cache={**old_frames}
for r in RUN_RELS+COMBO_RELS+TELE_RELS: base_frame_cache[r]=new_frames[r]
base_frame_cache.update(throw_frames)
base_keys=old_shapes+RUN_RELS+COMBO_RELS+THROW_KEYS+TELE_RELS
base_patterns=set()
for k in base_keys: base_patterns.update(p for p in base_frame_cache[k]['blocks'] if p!=ZERO_BLOCK)
frame_cache=dict(base_frame_cache)
# 16-colour normalization: exact 32->16 index map recovered from the visually accepted
# MKMSZR_sektor-16color_common-proof_v01 (every source index maps to exactly one target).
MAP32TO16=[0,12,11,3,3,14,9,13,5,5,7,7,7,7,1,1,2,2,12,6,6,10,10,4,4,15,8,8,1,1,1,1]
for k in list(frame_cache):
    fr=dict(frame_cache[k]); fr['padded']=bytes(MAP32TO16[p] for p in fr['padded'])
    fr['blocks']=make_blocks(fr['padded'],fr['stride'],fr['eh']); frame_cache[k]=fr
    assert max(fr['padded'])<16
# v04: the only generated asset is a transparent frame; sink/emerge use descriptor-only aliases
# of resident frames (anchor shifted, image shared), emitted in the teleport section.
EMPTY_KEY=('empty',0)
frame_cache[EMPTY_KEY]=dict(w=4,h=2,x=0,y=0,stride=4,eh=2,padded=bytes(8),blocks=make_blocks(bytes(8),4,2),codec='derived')
DERIVED_KEYS=[EMPTY_KEY]

def split_even(seq,n):
    L=len(seq); return [seq[(i*L)//n:((i+1)*L)//n] for i in range(n) if (i*L)//n<((i+1)*L)//n]
# 58 inherited entropy groups + 4 Run groups + Throw + Combo = 64 model records.
# Frame count falls from 158 to 152 solely by deleting the six non-retail Run poses.
old_groups=split_even(old_shapes,58); run_groups=split_even(RUN_RELS,4)
groups=old_groups+run_groups+[THROW_KEYS,COMBO_RELS+TELE_RELS+DERIVED_KEYS]
all_keys=old_shapes+RUN_RELS+COMBO_RELS+THROW_KEYS+TELE_RELS+DERIVED_KEYS
assert len(groups)==64 and len(all_keys)==160

freqs=[]
for g in groups:
    c=Counter()
    for k in g:c.update(p for p in frame_cache[k]['blocks'] if p!=ZERO_BLOCK)
    freqs.append(c)
all_patterns=set().union(*(set(c) for c in freqs))
# Ordering priority found statically best for this exact shared dictionary: new Combo,
# Throw, restored Run, then inherited corpus. It changes compression only, never pixels.
order=[len(groups)-1,len(groups)-2]+list(range(58,62))+list(range(58))
patterns=sorted(all_patterns,key=lambda p:tuple(-freqs[i].get(p,0) for i in order)+(p,))
pidx={p:i for i,p in enumerate(patterns)}



def best_partition(mf,K=13):
    used=sorted((pidx[p],w,p) for p,w in mf.items())
    idx=[x[0] for x in used]; wt=[x[1] for x in used]; pref=[0]
    for w in wt: pref.append(pref[-1]+w)
    n=len(used)
    @lru_cache(None)
    def dp(pos,k):
        if pos>=n:return (0,())
        if k==0:return (10**30,None)
        base=idx[pos];best=(10**30,None)
        for bits in range(1,17):  # native decoder safety: never emit a 0-bit normal class
            q=bisect.bisect_left(idx,base+(1<<bits),pos,n)
            if q==pos:continue
            rc,rp=dp(q,k-1);cost=bits*(pref[q]-pref[pos])+rc
            if rp is not None and cost<best[0]:best=(cost,((base,bits,pos,q),)+rp)
        return best
    _cost,plan=dp(0,K); assert plan is not None
    if len(plan)<K:
        base=plan[-1][0] if plan else 0
        plan=plan+tuple((base,1,n,n) for _ in range(K-len(plan)))
    cmap={}
    for ci,(base,bits,a,q) in enumerate(plan):
        for j in range(a,q):ix,w,p=used[j];cmap[p]=(ci,ix-base,bits)
    assert len(cmap)==len(mf) and len(plan)==13 and all(x[1]>=1 for x in plan)
    return plan,cmap

model_plans=[];model_maps=[]
for mf in freqs:
    pl,cm=best_partition(mf);model_plans.append(pl);model_maps.append(cm)
assert all(bits>=1 for pl in model_plans for _base,bits,_a,_q in pl)
ZERO_BITS=[2,2,3];ZERO_BASES=[0,4,8]
@lru_cache(None)
def zero_plan(n):
    if n==0:return (0,())
    best=(10**9,None)
    for zi,(bits,base) in enumerate(zip(ZERO_BITS,ZERO_BASES)):
        for extra in range(1<<bits):
            cnt=base+extra+1
            if cnt<=n:
                pc,pp=zero_plan(n-cnt);cost=pc+4+bits
                if cost<best[0]:best=(cost,pp+((13+zi,extra,bits,cnt),))
    return best

streams={};frame_model={}
for mid,g in enumerate(groups):
    cm=model_maps[mid]
    for k in g:
        fr=frame_cache[k];bw=BitWriter();bw.write(mid,6);bl=fr['blocks'];i=0
        while i<len(bl):
            if bl[i]==ZERO_BLOCK:
                j=i+1
                while j<len(bl) and bl[j]==ZERO_BLOCK:j+=1
                _,zp=zero_plan(j-i)
                for sym,extra,bits,_ in zp:bw.write(sym,4);bw.write(extra,bits)
                i=j
            else:
                ci,extra,bits=cm[bl[i]];bw.write(ci,4);bw.write(extra,bits);i+=1
        stream=bw.finish()
        while len(stream)&3:stream+=b'\0'
        streams[k]=stream;frame_model[k]=mid
STREAM_BYTES=sum(map(len,streams.values()))


# Shared table: every model record points to the same physical pattern array.

def pack_pattern(block):
    bw=BitWriter()
    for px in block:
        assert 0<=px<16; bw.write(px,4)
    out=bw.finish(); assert len(out)==4; return out

table=bytearray((2).to_bytes(2,'big')+len(groups).to_bytes(2,'big'))
for pl in model_plans:
    rec=bytearray(104)
    rec[0:4]=(0).to_bytes(4,'big')
    rec[4:6]=(4).to_bytes(2,'big')
    for i,(_base,bits,_a,_q) in enumerate(pl): rec[6+i*2:8+i*2]=bits.to_bytes(2,'big')
    for i,bits in enumerate(ZERO_BITS): rec[32+i*2:34+i*2]=bits.to_bytes(2,'big')
    for i,(base,_bits,_a,_q) in enumerate(pl): rec[40+i*4:44+i*4]=base.to_bytes(4,'big')
    for i,base in enumerate(ZERO_BASES): rec[92+i*4:96+i*4]=base.to_bytes(4,'big')
    table+=rec
for p in patterns: table+=pack_pattern(p)
TABLE_BYTES=len(table)


# Clean-derived ROM + v53 selector/logo convenience, no helper and stock arena.
rom=bytearray(clean)
def words_bytes(vals): return b''.join(int(v&0xffffffff).to_bytes(4,'big') for v in vals)
def jal(va): return 0x0C000000|((va>>2)&0x03ffffff)
DEBUG_MENU_VA=0x8000D0B8; A_ROUTE_JAL_ROM=0xE028; WRAP_LAST_ROM=0xDD60; COUNT_ROM=0xDD64
MENU_TABLE_ROM=0x9B7DC; SELECTION_LOAD_ROM=0x15CD0; MAPPER_ROM=0x9A700; MAPPER_VA=0x80099B00
ORIGINAL_MENU_POINTERS=(0x800AA034,0x800AA02C,0x800AA024,0x800AA01C,0x800AA014,0x800AA00C,0x800AA004,0x800A9FF4,0x800A9FEC,0x800A9FE0,0x800A9FD0,0)
SAFE_MENU_POINTERS=(0x800AA034,0x800AA02C,0x800AA024,0x800AA01C,0x800AA014,0x800AA00C,0x800A9FEC,0x800A9FE0,0,0,0,0)
MAPPER_WITH_SKIP=bytes.fromhex('3C03800C 8C6311E0 2C610006 50200001 24630002 3C028029 03E00008 A0441C0C')
assert be32(rom,A_ROUTE_JAL_ROM)==0x0C00A0C3 and be32(rom,WRAP_LAST_ROM)==0x2414000A and be32(rom,COUNT_ROM)==0x2A82000B
assert bytes(rom[MENU_TABLE_ROM:MENU_TABLE_ROM+48])==words_bytes(ORIGINAL_MENU_POINTERS)
put32(rom,A_ROUTE_JAL_ROM,jal(DEBUG_MENU_VA)); put32(rom,WRAP_LAST_ROM,0x24140007); put32(rom,COUNT_ROM,0x2A820008)
rom[MENU_TABLE_ROM:MENU_TABLE_ROM+48]=words_bytes(SAFE_MENU_POINTERS)
put32(rom,SELECTION_LOAD_ROM,jal(MAPPER_VA)); put32(rom,SELECTION_LOAD_ROM+4,0)
rom[MAPPER_ROM:MAPPER_ROM+len(MAPPER_WITH_SKIP)]=MAPPER_WITH_SKIP
BOOT=0x7A3F4
assert bytes(rom[BOOT:BOOT+24])==bytes.fromhex('0C01F113 00000000 0C01F143 00000000 0C018576 24040080')
put32(rom,BOOT,0x10000003)
assert bytes(rom[0x1C9A0:0x1C9A8])==clean[0x1C9A0:0x1C9A8] and be32(rom,0x66F64)==0x2442F420
assert bytes(rom[0xA5154:0xA5160])==bytes(12) and bytes(rom[0x9AD84:0x9ADD4])==bytes(0x50)
assert set(rom[0xF10000:0xF10400])=={0xFF}

clean_f87=bytes(clean[ORIG_FILE87_ROM:ORIG_FILE87_ROM+CLEAN_SIZE])
assert set(rom[RR:RR+CLEAN_SIZE])=={0xFF}
rom[RR:RR+CLEAN_SIZE]=clean_f87
put32(rom,0xA5664,RR); put32(rom,0xA566C,0)
assert bytes(rom[RR+PALETTE_OFF:RR+PALETTE_OFF+128])==clean_f87[PALETTE_OFF:PALETTE_OFF+128]
# Accepted 16-colour Sektor palette (entries 0..15 of MKMSZR_sektor-16color_common-proof_v01); 16..31 unused.
SEKTOR_PALETTE16=bytes.fromhex('00008001f39cad79a94a8435d294842c908490b2b9cec63ce73a843a98f798c6')
rom[RR+PALETTE_OFF:RR+PALETTE_OFF+64]=SEKTOR_PALETTE16+SEKTOR_PALETTE32[32:]

# Stock Type-5 corpus and stock direct script references.
def f32(off): return int.from_bytes(clean_f87[off:off+4],'big')
stock_shapes=[]
for off in range(TYPE_START,TYPE_END,4):
    if off+20<=CLEAN_SIZE and f32(off)==off+8 and f32(off+4)==0:
        image=f32(off+8)
        if 0<=image<CLEAN_SIZE and clean_f87[image:image+4]==b'\x05\0\0\0': stock_shapes.append(off)
assert len(stock_shapes)==341
stock_shape_set=set(stock_shapes)
stock_ref_positions=[off for off in range(0x1B0,TYPE_START,4) if f32(off) in stock_shape_set]
assert len(stock_ref_positions)==584

# The four original append-script areas are externally dead once their six primary roots are redirected.
dead_regions=[(0x4E0,0x504),(0x634,0x684),(0x798,0x7E8),(0x810,0x84C)]
redirect_slots={0x09,0x11,0x12,0x1A,0x1B,0x20}
for lo,hi in dead_regions:
    for p in range(0,TYPE_START,4):
        v=f32(p)
        if lo<=v<hi and not (lo<=p<hi) and not (p<0x104 and p//4 in redirect_slots):
            raise AssertionError(('external dead-script reference',hex(p),hex(v),hex(lo),hex(hi)))

# Reclaim stock fighter corpus and write optimized shared table.
rom[RR+TYPE_START:RR+TYPE_END]=b'\xFF'*(TYPE_END-TYPE_START)
rom[RR+TYPE_START:RR+TYPE_START+len(table)]=table
reclaim_cursor=align4(TYPE_START+len(table))

# Item packer: 152 frame blobs + one 52-byte exact high-kick script. Maximize reclaimed bytes.
item_sizes={k:32+len(streams[k]) for k in all_keys}
HIGH_KICK_ITEM=('script',0x11); item_sizes[HIGH_KICK_ITEM]=13*4
items=list(all_keys)+[HIGH_KICK_ITEM]
cap=TYPE_END-reclaim_cursor
capu=cap//4
reachable=[False]*(capu+1); parent=[None]*(capu+1); reachable[0]=True
for ii,k in enumerate(items):
    u=item_sizes[k]//4; assert item_sizes[k]%4==0
    for s in range(capu-u,-1,-1):
        if reachable[s] and not reachable[s+u]:
            reachable[s+u]=True; parent[s+u]=(s,ii)
best=max(i for i,v in enumerate(reachable) if v)
packed=set(); cur=best
while cur:
    prev,ii=parent[cur]; packed.add(items[ii]); cur=prev
assert sum(item_sizes[k] for k in packed)==best*4

item_offsets={}; append_cursor=align4(CLEAN_SIZE)
for k in items:
    if k in packed:
        off=reclaim_cursor; reclaim_cursor+=item_sizes[k]
    else:
        off=append_cursor; append_cursor+=item_sizes[k]
    item_offsets[k]=off
assert reclaim_cursor<=TYPE_END
NEW_END=append_cursor
# Exact compact six-retail-pose footprint from the prior static audit.
assert NEW_END<SAFE_V49, (hex(NEW_END),hex(SAFE_V49))
assert NEW_END==align4(CLEAN_SIZE) or set(clean[RR+CLEAN_SIZE:RR+NEW_END])=={0xFF}
put32(rom,0xA5668,RR+NEW_END)

# Emit all frame blobs at their packed locations.
shape_map={}
for k in all_keys:
    fr=frame_cache[k]; shape=item_offsets[k]; stream=streams[k]
    sub=shape+8; image=sub+12; shape_map[k]=shape
    put32(rom,RR+shape,sub); put32(rom,RR+shape+4,0); put32(rom,RR+sub,image)
    rom[RR+sub+4:RR+sub+6]=fr['w'].to_bytes(2,'big'); rom[RR+sub+6:RR+sub+8]=fr['h'].to_bytes(2,'big')
    rom[RR+sub+8:RR+sub+10]=(fr['x']&0xffff).to_bytes(2,'big'); rom[RR+sub+10:RR+sub+12]=(fr['y']&0xffff).to_bytes(2,'big')
    rom[RR+image:RR+image+4]=b'\x05\0\0\0'; put32(rom,RR+image+4,TYPE_START-image); put32(rom,RR+image+8,(fr['eh']<<16)|fr['stride'])
    rom[RR+image+12:RR+image+12+len(stream)]=stream
assert all((x&3)==0 for x in shape_map.values())

# Physical script layout: five former append scripts live in their now-dead stock regions; only High Kick is packed as an item.
script_targets={
    0x09:0x798,   # Crouch High Kick in old Forward-Flip region
    0x11:item_offsets[HIGH_KICK_ITEM],
    0x12:0x810,   # Low Kick in old Stumble region
    0x1A:0x4E0,   # Forward Flip in old Crouch-High-Kick region
    0x1B:0x7C0,   # Back Flip at its original body, after relocated Crouch HK
    0x20:0x634,   # Stumble across the two dead standing-kick bodies
}
assert script_targets[0x09]+40==0x7C0
assert script_targets[0x1B]+32<=0x7E8
assert script_targets[0x20]+68<=0x684
assert script_targets[0x12]+52<=0x84C
assert script_targets[0x1A]+32<=0x504

capacity={0x00:11,0x01:11,0x02:11,0x03:5,0x04:4,0x05:7,0x06:4,0x07:5,0x08:8,0x0A:8,0x0B:9,0x0C:4,0x0E:28,0x0F:27,0x13:7,0x14:12,0x15:10,0x16:4,0x17:7,0x18:7,0x19:7,0x1C:5,0x1D:5,0x1E:9,0x1F:9,0x21:7,0x22:8}
hybrid_slots={0x0E,0x0F,0x14}
owned_script_positions=set(); translated={}
for slot,cfg in slot_cfg.items():
    target = script_targets.get(slot,cfg.get('target'))
    donor_words=cfg['words']
    if slot in hybrid_slots:
        stock_words=[f32(cfg['target']+4*i) for i in range(cfg['n'])]
        vals=[shape_map[v] if is_donor_shape(v) else stock_words[i] for i,v in enumerate(donor_words)]
    else:
        vals=[]
        for value in donor_words:
            if is_donor_shape(value): vals.append(shape_map[value])
            elif cfg['donor']<=value<cfg['donor']+cfg['n']*4 and (value-cfg['donor'])%4==0:
                vals.append(target+(value-cfg['donor']))
            else: vals.append(value)
    if slot in script_targets:
        put32(rom,RR+slot*4,target)
        for i,v in enumerate(vals): put32(rom,RR+target+4*i,v); owned_script_positions.add(target+4*i)
    else:
        target=cfg['target']; capw=capacity[slot]; assert len(vals)<=capw
        for i in range(capw):
            put32(rom,RR+target+4*i,vals[i] if i<len(vals) else 0); owned_script_positions.add(target+4*i)
    translated[slot]=vals

# Existing v53 semantic guards remain true under relocation.
assert translated[0x00]==[shape_map[x] for x in (0x1768,0x1780,0x1794,0x17A8,0x17BC)]+[1,0x2EC]
assert translated[0x05]==[shape_map[0x1928],shape_map[0x193C],2,shape_map[0x1928],shape_map[0x1914],0]
assert translated[0x0B][4]==5 and translated[0x14][3:5]==[6,0]
assert translated[0x1A][-2:]==[1,script_targets[0x1A]+4]
assert translated[0x1B][-2:]==[1,script_targets[0x1B]+4]
assert translated[0x20][-2:]==[1,script_targets[0x20]+0x20]

# Push: MKMSZ's 7-frame +0x1B0 sequence is the pushing animation. Sektor has no
# dedicated push set in MKT, so retain the closest semantic substitute: the six
# genuine Sektor Run poses across the seven native Push ticks.
PUSH_TARGET=0x1B0
clean_push=[f32(PUSH_TARGET+4*i) for i in range(9)]
assert clean_push[7:]==[1,0x1B4]
push_visual=[RUN_RELS[0],RUN_RELS[1],RUN_RELS[2],RUN_RELS[3],RUN_RELS[4],RUN_RELS[5],RUN_RELS[0]]
push_words=[shape_map[x] for x in push_visual]+clean_push[7:]
for i,v in enumerate(push_words): put32(rom,RR+PUSH_TARGET+4*i,v); owned_script_positions.add(PUSH_TARGET+4*i)
assert be32(rom,RR+0x104+0x27*4)==0x1B0

# Compact v05 live Run script: exactly six genuine retail N64 pose pointers,
# followed immediately by the native MKMSZ loop token + root. No duplicated Run
# pointers and no non-retail even-pose assets are generated or referenced.
RUN_TARGET=0xEE8
clean_run=[f32(RUN_TARGET+4*i) for i in range(14)]
assert clean_run[12:]==[1,0xEE8]
# v13: robot run sound once per run start (MK3 run_setup -> group_sound(7) 'voice: run'; MKT group 7 for the
# robot voice group = event 35). Callback 2 plays descriptor 0x22 before the loop label; the loop skips it.
# v15: the run sound is dropped at the user's request (characteristic, but repetitive in MKMSZ's run-heavy play).
run_words=[shape_map[x] for x in RUN_RELS]+[1,RUN_TARGET]
assert len(run_words)==8 and len(set(run_words[:6]))==6
for i,v in enumerate(run_words):
    put32(rom,RR+RUN_TARGET+4*i,v); owned_script_positions.add(RUN_TARGET+4*i)

# v18: v59's Runtime-confirmed late-Knee ownership (MKMSZR_build_sektor_takeover_v59_combofix.py, KNEE_LATE_MAP),
# missing from the Run/teleport lineage. Combo selectors 0x1303/0x1305 play Knee parts 3-5; without this they fall
# to the global stance fallback (v17: 'missing animation when doing the kicks'). Only direct shape words change.
KNEE_LATE_MAP={
    0x6A0:0x1DD8,  # Knee part3 -> RBSPINKICK4
    0x6A4:0x1DC4,  # Knee part3 -> RBSPINKICK5
    0x6AC:0x1D74,  # Knee part4 -> RBKNEE3
    0x6C4:0x17A8,  # Knee part5 -> RBKNEE1 (retail Sektor uses RBSTANCE7 here)
    0x6D0:0x1D60,  # Knee part5 -> RBKNEE2
    0x6D4:0x1D74,  # Knee part5 -> RBKNEE3
}
for pos,rel in KNEE_LATE_MAP.items():
    assert f32(pos) in stock_shape_set, (hex(pos),hex(f32(pos)))
    put32(rom,RR+pos,shape_map[rel]); owned_script_positions.add(pos)
for pos in (0x6A8,0x6B0,0x6B4,0x6B8,0x6BC,0x6C0,0x6C8,0x6CC,0x6D8):
    assert be32(rom,RR+pos)==f32(pos), (hex(pos),hex(be32(rom,RR+pos)),hex(f32(pos)))

# Elbow/full combo: preserve all four MKMSZ native segments (3/2/3/5 visuals) and zeros.
COMBO_TARGET=0x5E0
combo_visual_pos=[0,1,2,4,5,7,8,9,11,12,13,14,15]
combo_seq=[0,1,2,1,0,3,4,5,6,7,8,9,8]  # 1,2,3 / 2,1 / 4,5,6 / 7,8,9,10,9
combo_words=[f32(COMBO_TARGET+4*i) for i in range(17)]
assert [i for i,v in enumerate(combo_words) if v==0]==[3,6,10,16]
for pos,ix in zip(combo_visual_pos,combo_seq): combo_words[pos]=shape_map[COMBO_RELS[ix]]
for i,v in enumerate(combo_words): put32(rom,RR+COMBO_TARGET+4*i,v); owned_script_positions.add(COMBO_TARGET+4*i)
assert be32(rom,RR+0x10*4)==COMBO_TARGET

# Throw: the actual MKMSZ a_throw body is exactly 12 words / 9 visual shapes in three zero-terminated parts.
# The command-heavy words beginning at +0x928 are a separate adjacent reaction/flip animation block and must not be rewritten as Throw.
THROW_TARGET=0x8F8
throw_visual_pos=[0,1,3,4,5,6,7,9,10]
throw_stance=shape_map[0x17A8]  # RBSTANCE7; retail Sektor throw itself enters from this already-resident pose.
throw_shapes={r:shape_map[('throw-composite',r)] for r in ARM_RELS}
# MKMSZ has nine attacker visual slots in three zero-terminated parts. Downsample Sektor's much
# longer throw into seven genuine mechanical-arm phases plus the genuine stance at entry/exit,
# preserving every target separator/control word.
# Runtime v54 observation: arm choreography leads the actual grab by one visual tick.
# Shift the seven arm phases right by one MKMSZ visual slot; gameplay/victim timing is untouched.
throw_sequence={
    0:throw_stance,
    1:throw_stance,
    3:throw_shapes[0x2318],
    4:throw_shapes[0x2340],
    5:throw_shapes[0x237C],
    6:throw_shapes[0x2390],
    7:throw_shapes[0x23B8],
    9:throw_shapes[0x23CC],
    10:throw_shapes[0x2408],
}
for pos in throw_visual_pos:
    put32(rom,RR+THROW_TARGET+4*pos,throw_sequence[pos]); owned_script_positions.add(THROW_TARGET+4*pos)
# Exact non-shape words in the 12-word Throw body remain stock.
for i in range(12):
    if i not in throw_visual_pos: assert be32(rom,RR+THROW_TARGET+4*i)==f32(THROW_TARGET+4*i)
assert be32(rom,RR+0x23*4)==THROW_TARGET
# Adjacent +0x928 reaction/flip block is NOT part of Throw and must remain fallback-managed, never throw-owned.
for p in (14,17,20,23,26,29):
    assert THROW_TARGET+4*p not in owned_script_positions

# Redirect every remaining direct stock Type-5 art reference to safe Sektor stance.
fallback=shape_map[0x1768]; fallback_positions=[]
for pos in stock_ref_positions:
    if pos in owned_script_positions: continue
    put32(rom,RR+pos,fallback); fallback_positions.append(pos)

# Runtime-unported primary roots remain stock except 0x10/0x23 now explicitly mapped.
for slot in (0x0D,0x24,0x25): assert be32(rom,RR+slot*4)==f32(slot*4)

# Independent Type-5 decoder verifies all 152 emitted frames byte-for-byte against their chosen target buffers.
def decode_generated(shape_off):
    assert be32(rom,RR+shape_off)==shape_off+8 and be32(rom,RR+shape_off+4)==0
    sub=shape_off+8; image=be32(rom,RR+sub)
    assert bytes(rom[RR+image:RR+image+4])==b'\x05\0\0\0'
    table_off=image+s32(be32(rom,RR+image+4)); assert table_off==TYPE_START
    dims=be32(rom,RR+image+8); height=(dims>>16)&0xffff; width=dims&0xffff
    rows=be16(rom,RR+table_off); mc=be16(rom,RR+table_off+2); assert rows==2 and mc==len(groups)
    pbase=table_off+4+104*mc
    br=BitReader(bytes(rom[RR+image+12:RR+NEW_END]))
    mid=br.read(6); assert mid<mc
    mo=table_off+4+104*mid; prel=be32(rom,RR+mo); bpp=be16(rom,RR+mo+4); assert bpp==4 and prel==0
    nbits=[be16(rom,RR+mo+6+i*2) for i in range(13)]
    zbits=[be16(rom,RR+mo+32+i*2) for i in range(3)]
    bases=[be32(rom,RR+mo+40+i*4) for i in range(13)]
    zbases=[be32(rom,RR+mo+92+i*4) for i in range(3)]
    out=bytearray(width*height); bw=width//4; total=bw*(height//rows); bi=0
    while bi<total:
        code=br.read(4)
        if code<13:
            pi=bases[code]+br.read(nbits[code]); po=pbase+prel+pi*4; pbr=BitReader(bytes(rom[RR+po:RR+po+4])); vals=[pbr.read(4) for _ in range(8)]
            by,bx=divmod(bi,bw)
            for ry in range(2):
                dst=(by*2+ry)*width+bx*4; out[dst:dst+4]=bytes(vals[ry*4:ry*4+4])
            bi+=1
        else:
            zi=code-13; bi+=zbases[zi]+br.read(zbits[zi])+1; assert bi<=total
    return bytes(out),mid,width,height

for k in all_keys:
    dec,mid,w,h=decode_generated(shape_map[k]); fr=frame_cache[k]
    assert mid==frame_model[k] and w==fr['stride'] and h==fr['eh'] and dec==fr['padded']

# Every original direct stock-shape site not explicitly rewritten by a mapped script is now the safe generated fallback.
generated_shapes=set(shape_map.values())
for pos in fallback_positions:
    assert be32(rom,RR+pos)==fallback
assert all((s&3)==0 for s in generated_shapes)
# Every selected throw composite really contains visible mechanical-arm pixels beyond the body.
for k in THROW_KEYS:
    assert throw_frames[k]['padded']!=new_frames[BODY_REL]['padded']
assert ARM_RELS==[0x2318,0x2340,0x237C,0x2390,0x23B8,0x23CC,0x2408]

# Helper remains absent and stock arena restored.
assert bytes(rom[0x1C9A0:0x1C9A8])==clean[0x1C9A0:0x1C9A8] and be32(rom,0x66F64)==0x2442F420
assert bytes(rom[0xA5154:0xA5160])==bytes(12) and bytes(rom[0x9AD84:0x9ADD4])==bytes(0x50)
assert set(rom[0xF10000:0xF10400])=={0xFF}

# Optional cross-check: if runtime-confirmed v53 is beside the builder, verify all 129 inherited frame pixels/geometry exactly.
v53_path = args.v53
if v53_path is not None:
    assert v53_path.exists(), v53_path
    v53=v53_path.read_bytes(); assert hashlib.sha256(v53).hexdigest()=='65181aa5a270ec2ba404d01d02a8054ffba923991408a87465a25515b6b99e7f'
    VF=v53[RR:RR+0x473D8]
    def valid_v53_shape(s):
        return 0<=s+20<len(VF) and be32(VF,s)==s+8 and be32(VF,s+4)==0 and 0<=be32(VF,s+8)<len(VF)-12 and VF[be32(VF,s+8):be32(VF,s+8)+4]==b'\x05\0\0\0'
    v53_shapes=sorted({be32(VF,p) for p in range(0,len(VF)-3,4) if valid_v53_shape(be32(VF,p))})
    assert len(v53_shapes)==129
    # Decode with the same generic routine logic against v53's two-model table.
    def decode_v53(s):
        sub=s+8; image=be32(VF,sub); w=be16(VF,sub+4); h=be16(VF,sub+6); x=s16(be16(VF,sub+8)); y=s16(be16(VF,sub+10)); dims=be32(VF,image+8); eh=(dims>>16)&0xffff; stride=dims&0xffff
        table=image+s32(be32(VF,image+4)); rows=be16(VF,table); mc=be16(VF,table+2); pb=table+4+104*mc; br=BitReader(VF[image+12:]); mid=br.read(6); mo=table+4+104*mid; prel=be32(VF,mo); bpp=be16(VF,mo+4)
        nb=[be16(VF,mo+6+i*2) for i in range(13)]; zb=[be16(VF,mo+32+i*2) for i in range(3)]; bases=[be32(VF,mo+40+i*4) for i in range(13)]; zbase=[be32(VF,mo+92+i*4) for i in range(3)]
        out=bytearray(stride*eh); bw=stride//4; total=bw*(eh//rows); bi=0
        while bi<total:
            code=br.read(4)
            if code<13:
                pi=bases[code]+br.read(nb[code]); po=pb+prel+pi*5; pbr=BitReader(VF[po:po+5]); vals=[pbr.read(5) for _ in range(8)]; by,bx=divmod(bi,bw)
                for ry in range(2): out[(by*2+ry)*stride+bx*4:(by*2+ry)*stride+bx*4+4]=bytes(vals[ry*4:ry*4+4])
                bi+=1
            else:
                zi=code-13; bi+=zbase[zi]+br.read(zb[zi])+1
        return dict(w=w,h=h,x=x,y=y,stride=stride,eh=eh,padded=bytes(out))
    for rel,s in zip(old_shapes,v53_shapes):
        a=frame_cache[rel]; b=decode_v53(s)
        assert all(a[k]==b[k] for k in ('w','h','x','y','stride','eh','padded')), (hex(rel),hex(s))

# Preserve the v03 donor-equivalent cadence: ordinary MKMSZ Run rate 2 -> 3.
# v05 preserves the runtime-confirmed v04 live script and rate; only physical Run storage is compacted.
RUN_RATE_ROM = 0x2F7A0
assert bytes(rom[RUN_RATE_ROM:RUN_RATE_ROM+4]) == bytes.fromhex('24040002')
rom[RUN_RATE_ROM:RUN_RATE_ROM+4] = bytes.fromhex('24040003')


# ============================================================================
# Teleport v01 section (appended to the 16-colour/4-bpp v05-equivalent build).
# Donor: MKT Rev. 2 Sektor F,F+LK -> do_body_propell(8) -> 0x80048368.
# Host lifecycle: exact Runtime-confirmed Reverse Elbow v6 infrastructure
# (file-0x1B raw payload at 0x801AF420, uncached entry, selector-3 bridge,
# lock 0x800BF308, exit 0x800328FC + v6 non-returning fallback).
# Disposable proof only. Silent (no SFX).
# ============================================================================

# ---- extra teleport scripts appended to file 0x87 ---------------------------
TELE_POSE_REL = 0x2F08                       # last frame of donor slot 0x0D
TELE_DROP_RELS = [0x2B48, 0x2B5C, 0x2B70, 0x2B70, 0x2B84]   # donor secondary slot 3
LAND_RELS = [0x1EDC, 0x1EC8]                 # donor slot 0x16 frames [1], [0] (already resident)
for r in [TELE_POSE_REL] + TELE_DROP_RELS + LAND_RELS + DERIVED_KEYS:
    assert r in shape_map, r

SCRIPT_BASE = align4(NEW_END)
scripts = {}
cur = SCRIPT_BASE
def emit(name, words_):
    global cur
    scripts[name] = cur
    for i, v in enumerate(words_):
        put32(rom, RR + cur + 4 * i, v)
    cur += 4 * len(words_)
# Each script holds its last frame with a self-jump so later advances cannot run past it.
DROP_RATE = 3                     # donor rate 5 @60 Hz ~= 2.5 target ticks
# Descriptor-only aliases: shape [sub, 0] + sub [image, w|h, x|y'] sharing the base image.
# Donor anchor convention: feet = h - anchor_y; moving the image down by d is anchor_y - d.
# MKT sinks the sprite down over the floor and off the bottom of the screen (no floor clip).
SINK_DEPTHS = [13, 28, 46, 66, 89, 113, 140, 170, 202, 236, 273, 311]   # donor 5.95 px/t60 + 0.584 px/t60^2, every 2 donor ticks
EMERGE_DEPTHS = [311, 236, 170, 113, 66, 28]                              # rises back over ~the donor emerge time
def alias(base_key, d):
    global cur
    shape = cur; sub = shape + 8; base_sub = shape_map[base_key] + 8
    put32(rom, RR + shape, sub); put32(rom, RR + shape + 4, 0)
    rom[RR + sub:RR + sub + 10] = rom[RR + base_sub:RR + base_sub + 10]          # image, w, h, x
    y = int.from_bytes(rom[RR + base_sub + 10:RR + base_sub + 12], 'big', signed=True)
    rom[RR + sub + 10:RR + sub + 12] = ((y - d) & 0xFFFF).to_bytes(2, 'big')
    cur += 20
    return shape
sink_alias = [alias(TELE_POSE_REL, d) for d in SINK_DEPTHS]
emerge_alias = [alias(TELE_DROP_RELS[0], d) for d in EMERGE_DEPTHS]
sink = cur
sink_words = [shape_map[TELE_POSE_REL]] + sink_alias + [shape_map[EMPTY_KEY]]
emit('SINK', sink_words + [1, sink + 4 * (len(sink_words) - 1)])      # holds the transparent frame
SINK_STEPS = len(sink_words) - 1
drop = cur
emerge_words = emerge_alias + [shape_map[TELE_DROP_RELS[0]]]
EMERGE_STEPS = len(emerge_words) - 1                                   # last step shows the full first rise frame
rise_words = [shape_map[r] for r in TELE_DROP_RELS[1:]]
drop_words = emerge_words + [6, 1, DROP_RATE] + rise_words             # callback 1: set rate for the rise
emit('DROP', drop_words + [1, drop + 4 * (len(drop_words) - 1)])
landa = cur
emit('LANDA', [shape_map[LAND_RELS[0]], 1, landa])
landb = cur
emit('LANDB', [shape_map[LAND_RELS[1]], 1, landb])
TELE_END = cur
assert set(clean[RR + SCRIPT_BASE:RR + TELE_END]) == {0xFF}
NEW_END_TELE = align4(TELE_END)
assert NEW_END_TELE < SAFE_V49, (hex(NEW_END_TELE), hex(SAFE_V49))
put32(rom, 0xA5668, RR + NEW_END_TELE)

# ---- v21: rocket art + palette on the straight projectile (R2 step 2a) ----
# Donor ROCKETD1 (MKT robot frame +0x2668: 39x9, anchor (26,3), codec 16) and ROCKET_P (retail record
# 0x0BC3AC, 16 colours) as a raw/type-0 image + 64-entry palette record appended to file 0x87. The Zap
# script's projectile frames point at it; two token-0x0B hooks (fighter_import.projectile, v87/v89 design)
# bind ROCKET_P and pre-load the texture slot before publication, for this projectile only.
# v23: the pre-load no longer calls the allocating 0x8001BF70 (v21 per-shot storage leak; v22's fixed
# 368-byte buffer was overrun by the up/down Ice stance frame -> hang). It runs the render pass's
# deferred slot upload early, into the slot's stock storage.
from mkmszr.fighter_import import MktRom as _MktRom, projectile as _proj
from mkmszr.fighter_import.mips import Assembler as _Asm
_donor = _MktRom(mkt)
(_part,) = _donor.frame_parts(7, 0x2668)
assert (_part.width, _part.height, _part.anchor_x, _part.anchor_y, _part.codec) == (39, 9, 26, 3, 16)
_heap = _donor.heap_bytes(7)
_indices, _used = _proj.decode_mkt_codec16(_heap[_part.image:])
assert _used == 130 and len(_indices) == 9 * 40
ROCKET_P_ROM = 0x0BC3AC
assert int.from_bytes(mkt[ROCKET_P_ROM:ROCKET_P_ROM + 4], 'big') == 16
_pal = tuple(_proj.mkt_color_to_host(int.from_bytes(mkt[ROCKET_P_ROM + 4 + 2 * i:ROCKET_P_ROM + 6 + 2 * i], 'big')) for i in range(16))
ROCKET = _proj.ProjectileArt(39, 9, 26, 3, _indices, _pal)
_end = be32(rom, 0xA5668) - RR
ROCKET_IMAGE_OFF = _end
ROCKET_PAL_OFF = (ROCKET_IMAGE_OFF + len(ROCKET.raw_image()) + 3) & ~3
ROCKET_PAL_SRC = ROCKET_PAL_OFF + 4
ROCKET_SHAPE_OFF = (ROCKET_PAL_OFF + len(ROCKET.palette_record()) + 3) & ~3
ROCKET_DESC_OFF = ROCKET_SHAPE_OFF + 8
_new_end = ROCKET_DESC_OFF + 12
assert _new_end < SAFE_V49 and set(rom[RR + _end:RR + _new_end]) == {0xFF}
rom[RR + ROCKET_IMAGE_OFF:RR + ROCKET_IMAGE_OFF + len(ROCKET.raw_image())] = ROCKET.raw_image()
rom[RR + ROCKET_PAL_OFF:RR + ROCKET_PAL_OFF + len(ROCKET.palette_record())] = ROCKET.palette_record()
put32(rom, RR + ROCKET_SHAPE_OFF, ROCKET_DESC_OFF); put32(rom, RR + ROCKET_SHAPE_OFF + 4, 0)
put32(rom, RR + ROCKET_DESC_OFF, ROCKET_IMAGE_OFF)
put32(rom, RR + ROCKET_DESC_OFF + 4, (ROCKET.width << 16) | ROCKET.height)
put32(rom, RR + ROCKET_DESC_OFF + 8, ((ROCKET.anchor_x & 0xFFFF) << 16) | (ROCKET.anchor_y & 0xFFFF))
put32(rom, 0xA5668, RR + _new_end)
# v27 (R2 step 2d): second flat-rocket frame ROCKETD2 (+0x267C, same ROCKET_P) and the flight loop
# script: MKT anirate 3 (60 Hz) resampled to one frame per host tick, entered at the flight child's phase.
from mkmszr.fighter_import.actions import robo_zap as _zapf
(_part2,) = _donor.frame_parts(7, _zapf.ROCKET_FRAMES[1])
assert (_part2.width, _part2.height, _part2.anchor_x, _part2.anchor_y, _part2.codec) == (42, 10, 30, 4, 16)
_indices2, _ = _proj.decode_mkt_codec16(_heap[_part2.image:])
assert len(_indices2) == 10 * 44 and max(_indices2) < 16
ROCKET2 = _proj.ProjectileArt(42, 10, 30, 4, _indices2, _pal)
ROCKET2_IMAGE_OFF = _new_end
ROCKET2_SHAPE_OFF = (ROCKET2_IMAGE_OFF + len(ROCKET2.raw_image()) + 3) & ~3
ROCKET2_DESC_OFF = ROCKET2_SHAPE_OFF + 8
FLIGHT_LOOP_OFF = ROCKET2_DESC_OFF + 12
_cycle = _zapf.flight_frame_cycle((ROCKET_SHAPE_OFF, ROCKET2_SHAPE_OFF))
assert _cycle == [ROCKET_SHAPE_OFF, ROCKET_SHAPE_OFF, ROCKET2_SHAPE_OFF, ROCKET_SHAPE_OFF, ROCKET2_SHAPE_OFF, ROCKET2_SHAPE_OFF]
_loop_words = _cycle + [1, FLIGHT_LOOP_OFF]
FLIGHT_ENTRY_OFF = FLIGHT_LOOP_OFF + 4 * (_zapf.CHILD_START_TICKS % len(_cycle))
_new_end2 = FLIGHT_LOOP_OFF + 4 * len(_loop_words)
assert _new_end2 < SAFE_V49 and set(rom[RR + _new_end:RR + _new_end2]) == {0xFF}
rom[RR + ROCKET2_IMAGE_OFF:RR + ROCKET2_IMAGE_OFF + len(ROCKET2.raw_image())] = ROCKET2.raw_image()
put32(rom, RR + ROCKET2_SHAPE_OFF, ROCKET2_DESC_OFF); put32(rom, RR + ROCKET2_SHAPE_OFF + 4, 0)
put32(rom, RR + ROCKET2_DESC_OFF, ROCKET2_IMAGE_OFF)
put32(rom, RR + ROCKET2_DESC_OFF + 4, (ROCKET2.width << 16) | ROCKET2.height)
put32(rom, RR + ROCKET2_DESC_OFF + 8, ((ROCKET2.anchor_x & 0xFFFF) << 16) | (ROCKET2.anchor_y & 0xFFFF))
for _i, _w in enumerate(_loop_words):
    put32(rom, RR + FLIGHT_LOOP_OFF + 4 * _i, _w)
put32(rom, 0xA5668, RR + _new_end2)
print('ROCKET_FLIGHT', 'D2 image', hex(ROCKET2_IMAGE_OFF), 'shape', hex(ROCKET2_SHAPE_OFF), 'loop', hex(FLIGHT_LOOP_OFF),
      [hex(w) for w in _loop_words], 'entry', hex(FLIGHT_ENTRY_OFF), 'file87 end', hex(_new_end2))


# ---- v19: action code from the importer library (src/mkmszr/fighter_import) ----
# The teleport adapter, sound player and descriptor condition are now assembled by
# mkmszr.fighter_import.actions.robo_teleport on the host primitive library; with these
# parameters the payload is byte-identical to v18 (asserted below).
import sys as _sys
_REPO_SRC = Path(__file__).resolve().parents[3] / 'src'
if str(_REPO_SRC) not in _sys.path:
    _sys.path.insert(0, str(_REPO_SRC))
from mkmszr.fighter_import.actions import robo_teleport as _rt

PAYLOAD_VA = 0xA01AF420                      # KSEG1 execution / data alias
PAYLOAD_LIMIT = 0x4000                        # v29: arena 0x801AF420..0x801B3420 = production's Runtime-confirmed 16 KiB floor
# (v20-v28: 0x1000). Static audit: no clean-ROM code addresses [0x801AF420,0x801B3420) except the two heap-base
# sites this reservation patches (0x66F64, 0x66FE8); the range is allocator heap in the clean game.
ARENA_END = 0x801AF420 + PAYLOAD_LIMIT
_ARENA_LO = f'{(ARENA_END & 0xFFFF):04x}'
STRIKE_WORDS = (0x0049FFF7, 0x00490057, 0x08021803, 0x00010E02)   # stock uppercut reaction/aux/trailer; damage 0x18 / chip 3 (v08)
TELE_EVENT = 335                             # isolated host chain carrying MKT event 0x104 (v09)
_params = _rt.TeleportParams(
    scripts=_rt.TeleportScripts(sink=scripts['SINK'], drop=scripts['DROP'], land_a=scripts['LANDA'],
                                land_b=scripts['LANDB'], sink_steps=SINK_STEPS, emerge_steps=EMERGE_STEPS),
    strike_words=STRIKE_WORDS, sound_event=TELE_EVENT)
# The library still reproduces the v18 teleport exactly with the v18 parameters (checked below);
# v25 builds with emerge_on_floor: reappear on the target's floor rather than at its current height.
from dataclasses import replace as _replace
_v18_params = _params
_params = _replace(_params, emerge_on_floor=True)
_m = _rt.motion()
EMERGE_VEL, GRAV_NOHIT, GRAV_HIT = _m.emerge_velocity, _m.gravity_nohit, _m.gravity_hit
RANGE_UNITS, HIDDEN_TICKS, AIR_CAP = _params.range_units, _params.hidden_ticks, _params.air_cap
DROP_RATE, SINK_TICKS, X_OFFSET = 3, 3, -10   # report-only (TELEPORT_PHYSICS line), as in v18
_v18 = _rt.assemble(PAYLOAD_VA, _v18_params)
for _w in (0x80091101, 0x01031002, 0x04000000, 0x0000000E):
    _v18.raw(_w)
assert hashlib.sha256(_v18.link()).hexdigest() == 'a35d9732bbe72c1d0a39fba280e03b14a5fb2532fe22b2f790a55c86ddce1c3a', 'library no longer reproduces v18'
a = _rt.assemble(PAYLOAD_VA, _params)
# v16: standalone Sektor HK,HK combo record (v62 'SEKTOR_KNEE_ROOT_SAFE') in the payload arena (KSEG1).
a.label('knee_rec')
for _w in (0x80091101, 0x01031002, 0x04000000, 0x0000000E):
    a.raw(_w)
_V19_PAYLOAD_LEN = a.pc() - PAYLOAD_VA
# ---- v20: re-host stock Ice Blast (R2 step 1) ----
# The LP Ice Blast record's action becomes a lifted copy of stock callback 0x80049C34 whose ground branch
# transfers to selector 4 instead of 0; selector 4 is a lifted, relocated copy of the stock root 0x8004AB84
# (all three Ice modes). The lifter verifies both copies word-for-word against the clean ROM: only internal
# j/jal are retargeted, plus the one declared patch. The teleport keeps selector 3 through a payload thunk.
from mkmszr.fighter_import import host as _host, lifter as _lifter
def _clean_code(va, end):
    return clean[va - 0x7FFFF400:end - 0x7FFFF400]
_host.emit_transfer_thunk(a, 'tele_thunk', 3)
from mkmszr.fighter_import.actions import robo_zap as _zap
ICE_CB_SRC, ICE_CB_END = _zap.ICE_CALLBACK_SRC, _zap.ICE_CALLBACK_END
ICE_ROOT_SRC, ICE_ROOT_END = _zap.ICE_ROOT_SRC, _zap.ICE_ROOT_END
ICE_CB_VA = a.pc()
_cb = _lifter.lift(_clean_code(ICE_CB_SRC, ICE_CB_END), ICE_CB_SRC, ICE_CB_VA,
                   patches={0x80049C70: 0x24040004})       # ground branch: move a0,zero -> addiu a0,zero,4
_lifter.verify(_clean_code(ICE_CB_SRC, ICE_CB_END), _cb)
_zap.check_stock(_cb)
assert _cb.patched[0x80049C70][0] == 0x00002021            # stock 'move a0, zero' (selector 0)
for _i in range(0, len(_cb.code), 4):
    a.raw(int.from_bytes(_cb.code[_i:_i + 4], 'big'))
# v30 (R2 step 3a): MKT rocket sounds hosted in isolated chains (sound section below): chest 0x0B -> host 173,
# launch 3 -> host 175, boom 0x0A -> host 177. The chest sound wraps the root's open phase; the launch sound
# plays at creation (the Ice launch block is skipped); the boom replaces the Ice hit sound in a lifted copy of
# the hit child, reached from the flight child and from a lifted copy of the straight helper (point-blank).
ROCKET_SOUND_HOSTS = {'chest': 173, 'launch': 175, 'boom': 177}
_zapf.emit_sound_wrappers(a, ROCKET_SOUND_HOSTS['chest'], ROCKET_SOUND_HOSTS['boom'])
HIT_CHILD_VA = a.pc()
_hit = _lifter.lift(_clean_code(_zapf.HIT_CHILD_SRC, _zapf.HIT_CHILD_END), _zapf.HIT_CHILD_SRC, HIT_CHILD_VA,
                    patches=_zapf.hit_child_patches(a.labels['zap_boom']))
_lifter.verify(_clean_code(_zapf.HIT_CHILD_SRC, _zapf.HIT_CHILD_END), _hit)
_zapf.check_stock(_hit)
for _i in range(0, len(_hit.code), 4):
    a.raw(int.from_bytes(_hit.code[_i:_i + 4], 'big'))
STRAIGHT_VA = a.pc()
_str = _lifter.lift(_clean_code(_zapf.STRAIGHT_SRC, _zapf.STRAIGHT_END), _zapf.STRAIGHT_SRC, STRAIGHT_VA,
                    patches=_zapf.straight_patches(HIT_CHILD_VA))
_lifter.verify(_clean_code(_zapf.STRAIGHT_SRC, _zapf.STRAIGHT_END), _str)
_zapf.check_stock(_str)
for _i in range(0, len(_str.code), 4):
    a.raw(int.from_bytes(_str.code[_i:_i + 4], 'big'))
# v27: rocket flight child + per-tick callback + speed table (robo_zap.emit_flight), ahead of the root so
# the root's child-creation patch knows the child's address. v30: contact goes to the lifted hit child.
_zapf.emit_flight(a, FLIGHT_ENTRY_OFF, hit_child=HIT_CHILD_VA)
# v29: rocket creation setup, called from the lifted root right after its token advance (0x8004AEE4).
_proj.emit_bind_after_creation(a, 'zap_post_token', ROCKET_PAL_SRC, ROCKET, behind_owner=True,
                               on_create=_zapf.on_create(ROCKET_SOUND_HOSTS['launch']),
                               epilogue=_zapf.emit_mode_reload)
ZAP_POST_TOKEN_VA = a.labels['zap_post_token']
_zapf.emit_speed_table(a, 'zap_speeds')
ICE_ROOT_VA = a.pc()
# v24 (R2 step 2b): the lifted root places the projectile at the donor retail offset (+5,+38) through
# the same host call 0x80031208 (v72 Runtime-confirmed placement). Only the LP rocket runs this copy.
_root = _lifter.lift(_clean_code(ICE_ROOT_SRC, ICE_ROOT_END), ICE_ROOT_SRC, ICE_ROOT_VA,
                     patches={**_zap.placement_patches(), **_zap.close_patches(),       # v26: closing frame 2 ticks
                              **_zapf.child_patches(a.labels['zap_child']),                # v27: rocket flight child
                              **_zapf.post_token_patches(ZAP_POST_TOKEN_VA),               # v29: creation setup
                              **_zapf.root_sound_patches(a.labels['zap_chest_open']),      # v30: chest sound, no Ice launch sound
                              **_zapf.root_straight_patch(STRAIGHT_VA)})                   # v30: lifted straight helper
_lifter.verify(_clean_code(ICE_ROOT_SRC, ICE_ROOT_END), _root)
_zap.check_stock(_root)
for _i in range(0, len(_root.code), 4):
    a.raw(int.from_bytes(_root.code[_i:_i + 4], 'big'))
print('ICE_REHOST', 'callback', hex(ICE_CB_VA), 'root', hex(ICE_ROOT_VA), 'root relocated j/jal', len(_root.relocated),
      'callback relocated', len(_cb.relocated), 'patches', {hex(k): (hex(v[0]), hex(v[1])) for k, v in _cb.patched.items()},
      'root patches', {hex(k): (hex(v[0]), hex(v[1])) for k, v in _root.patched.items()})
payload = a.link()
COND_VA = a.labels['cond']
KNEE_REC_VA = a.labels['knee_rec']
assert KNEE_REC_VA & 3 == 0 and (KNEE_REC_VA >> 28) == 0xA
assert len(payload) <= PAYLOAD_LIMIT, hex(len(payload))
PAYLOAD_ROM = 0x00F10000
assert set(rom[PAYLOAD_ROM:PAYLOAD_ROM + PAYLOAD_LIMIT]) == {0xFF}
rom[PAYLOAD_ROM:PAYLOAD_ROM + PAYLOAD_LIMIT] = payload + b'\0' * (PAYLOAD_LIMIT - len(payload))

# ---- exact Reverse Elbow v6 infrastructure (guarded against clean bytes) ----
def guarded(off, old_hex, new_hex):
    old = bytes.fromhex(old_hex); new = bytes.fromhex(new_hex)
    assert bytes(rom[off:off + len(old)]) == old, hex(off)
    rom[off:off + len(new)] = new
guarded(0x4B654, '2cc20003', '2cc20005')                                  # permit selectors 3 (teleport) and 4 (Ice re-host)
assert be32(rom, 0x66F60) == 0x3C02801B
guarded(0x66F64, '2442f420', '2442' + _ARENA_LO)                         # arena prefix reservation
guarded(0x66FE0, '27bdffe83c02801b2442f420', '0802686100000000' + '2442' + _ARENA_LO)  # loader hook
guarded(0x9AD84, '00' * 0x50, (
    '27bdffe83c02801b2442' + _ARENA_LO + 'afbf00103c04800fac82ecd00c0198e400000000'
    '2404001b3c05801b24a5f4200c01975900000000'
    '3c0880113409270fa509200e8fbf001027bd001803e0000800000000'
).ljust(0xA0, '0'))                                                        # loader stub (+ v6 max EXP)
guarded(0xA1C5C, '00' * 16, 'a01af420' + f'{ICE_ROOT_VA:08x}' + '00000000' * 2)  # table[3] teleport, table[4] Ice re-host
guarded(0xA5154, '00' * 8, f'{PAYLOAD_ROM:08x}{PAYLOAD_ROM + PAYLOAD_LIMIT:08x}')  # file 0x1B
for off, old in ((0xA6FFC, '0104036b'), (0xA7000, '09470591'), (0xA7004, '11ad0d16'), (0xA700C, '1ccf4e20')):
    guarded(off, old, '270f270f')                                         # v6 EXP caps
# Low Kick descriptor -> F,F + LK teleport (stock condition retained, as in v6)
def descriptor(masks, sel, cond, action, window, right, left):
    b = bytearray(0x2C)
    b[0:2] = masks[0].to_bytes(2, 'big'); b[2:4] = masks[1].to_bytes(2, 'big')
    b[4:8] = sel.to_bytes(4, 'big'); b[8:12] = cond.to_bytes(4, 'big'); b[12:16] = action.to_bytes(4, 'big')
    b[16:18] = window.to_bytes(2, 'big')
    for n, t in enumerate(right): b[0x12 + 2 * n:0x14 + 2 * n] = t.to_bytes(2, 'big')
    for n, t in enumerate(left): b[0x1E + 2 * n:0x20 + 2 * n] = t.to_bytes(2, 'big')
    return bytes(b)
STOCK_LK = descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x80049CB0, 0x14, (8, 7), (9, 7))
TELE_LK = descriptor((0x40, 0x40), 1, COND_VA, a.labels['tele_thunk'], 0x18, (9, 9), (8, 8))
guarded(0xB1B68, STOCK_LK.hex(), TELE_LK.hex())
assert be16(rom, 0xB1B94) == 0                                            # table sentinel intact
# v20: LP Ice Blast record (0x800B0F38) action -> lifted callback (ground branch = selector 4)
guarded(0xB1B44, '80049c34', f'{ICE_CB_VA:08x}')

# ---- v09: donor sounds into isolated MKMSZ hosts (guarded) ----
import zlib as _zlib
_ctl = _zlib.decompress(mkt[0xA8F588:0xA8F588 + 0x17AE0], -15)
_defs = _zlib.decompress(mkt[0xAA7090:0xAA7090 + 0x7A6], -15)
assert hashlib.sha256(_ctl).hexdigest().startswith('8dc6f036dc795cba')
assert hashlib.sha256(_defs).hexdigest().startswith('6cdfcf946ba78f49')
def _donor(event_id):
    d = _defs[event_id * 16:event_id * 16 + 16]
    ln = int.from_bytes(d[4:8], 'big'); off = int.from_bytes(d[8:12], 'big')
    track = _zlib.decompress(mkt[0xAA7836 + off:], -15)[:ln]
    pid = int.from_bytes(track[0:4], 'big'); sid = int.from_bytes(_ctl[pid * 4 + 2:pid * 4 + 4], 'big')
    sub = _ctl[0x6E0 + sid * 20:0x6E0 + sid * 20 + 20]; wid = int.from_bytes(sub[10:12], 'big')
    wav = _ctl[0x2828 + wid * 24:0x2828 + wid * 24 + 24]; pred = _ctl[0x4F48 + wid * 264:0x4F48 + wid * 264 + 264]
    so = 0xAB4370 + int.from_bytes(wav[0:4], 'big'); sl = int.from_bytes(wav[4:8], 'big')
    return track, sub, wav, pred, mkt[so:so + sl]
MSZ_SSEQ_TRACKS, MSZ_PATCH, MSZ_SUB, MSZ_WAVE, MSZ_PRED, MSZ_TBL = 0x979240, 0x947CB8, 0x948768, 0x94C138, 0x950490, 0x9B0650
SOUND_ROM = 0xF20000
SOUND_LIMIT = 0xF28000                 # v12: room for the voice set
# (donor event, sample sha256 prefix, host event, host patch, host subpatch, host wave, host track, patch, subpatch, wave, pred sha prefix)
SOUNDS = (
    (0x104, '7e039ca338e13838', TELE_EVENT, 492, 335, 325,
     '000001ec00007f4000000078007800000000000c00113c7f8105123c00227820', '0100014f',
     '647340003c00007f0505014500017d00000a7f7f', '0018ce8c00000d5400000000fffffb50ffffffff00000000', '1fee28ccadb934a1'),
)
assert set(rom[SOUND_ROM:SOUND_LIMIT]) == {0xFF}
_cur = SOUND_ROM
for (dev, ssha, hev, hp, hs, hw, htrk, hpat, hsub, hwav, hpred) in SOUNDS:
    track, sub, wav, pred, smp = _donor(dev)
    assert hashlib.sha256(smp).hexdigest().startswith(ssha), hex(dev)
    toff = int.from_bytes(clean[0x976D60 + hev * 16 + 8:0x976D60 + hev * 16 + 12], 'big')
    assert int.from_bytes(clean[0x976D60 + hev * 16 + 4:0x976D60 + hev * 16 + 8], 'big') == 0x20 == len(track)
    trk_rom = MSZ_SSEQ_TRACKS + toff
    assert int.from_bytes(clean[trk_rom:trk_rom + 4], 'big') == hp
    assert hashlib.sha256(clean[MSZ_PRED + hw * 264:MSZ_PRED + hw * 264 + 264]).hexdigest().startswith(hpred)
    t = bytearray(track); t[0:4] = hp.to_bytes(4, 'big')
    sb = bytearray(sub); sb[10:12] = hw.to_bytes(2, 'big')
    wv = bytearray(wav); wv[0:4] = (_cur - MSZ_TBL).to_bytes(4, 'big')
    guarded(trk_rom, htrk, bytes(t).hex())
    assert clean[MSZ_PATCH + hp * 4:MSZ_PATCH + hp * 4 + 4].hex() == hpat          # patch kept: -> host subpatch
    guarded(MSZ_SUB + hs * 20, hsub, bytes(sb).hex())
    guarded(MSZ_WAVE + hw * 24, hwav, bytes(wv).hex())
    rom[MSZ_PRED + hw * 264:MSZ_PRED + hw * 264 + 264] = pred
    assert _cur + len(smp) <= SOUND_LIMIT
    rom[_cur:_cur + len(smp)] = smp
    print('SOUND', hex(dev), '-> event', hev, 'patch', hp, 'sub', hs, 'wave', hw, 'sample ROM', hex(_cur), hex(len(smp)))
    _cur = (_cur + len(smp) + 0xF) & ~0xF

# ---- v12: Sektor's MKT voice/attack set replaces Sub-Zero's player-only voice ----
# Sub-Zero's voice: player (type 4) table 0x800A2EC8 (ROM 0xA3AC8) -> descriptors 0x20..0x2C -> events 30..43,
# owned only by that table (no enemy table, no other descriptor). Each used Sub-Zero event keeps its slot and
# descriptor; its 0x20-byte track is replaced by the donor track pointing at an isolated host chain.
# Donor identities (arcade MK3 REV13 MKSOUND.ASM labels; MKT kept the slot order, durations match):
#   attacks: robots have no attack voice, only rsnd_whoosh -> MKT triple 6 'whoosh #1' (event 416), triple 7
#   'whoosh #3' (event 417); hurt: robo sparks ft 0x0F/0x10/0x11 (events 268/269/270); death ('wasted'):
#   robo speech 1, ft 0x12 (event 271). Jump and slide/special yells: robots have none -> table entry 0 (skipped
#   by 0x80064B00). Death gets its own descriptor 0x2A (stock-unreferenced, event 41) instead of sharing hurt 0x26.
# v14: data-driven, donor-faithful voice rule (reusable for any MKT donor fighter).
# MKT voice groups (arcade MK3 group_table semantics): 0 attack, 1 jump, 2 wasted, 3 grab, 4 throw voice,
# 5 tripped, 6 face hit, 7 run, 8 shook, 9 death scream. Group table 0x800A19D4[group] -> {u16 count, then
# count entries per voice group}; the fighter's voice group is 0x800A19FC[fighter] (Sektor 7 -> group 5,
# robots). 0xFFFF = no sound for that group.
# MKMSZ player categories -> MKT semantics (by the reactions that play them; MK3 MKREACT.ASM):
#   0-1 attack effort  -> group 0 voice + rsnd_whoosh; MKMSZ plays one sample, so: voice if the donor has one,
#                         else MKT whoosh #1 / #3 (triple slots 6 / 7)
#   2-3, 4-5 stand-up hits -> group 6 'face hit' (r_hi/lo_punch, lo_kick, duck hits: rsnd_react_voice)
#   6-7 launching hits -> group 2 'wasted' (r_hi_kick, r_roundhouse, r_uppercut, launching combos)
#   8 jump -> group 1;  9 sweep family -> group 5 'tripped' (r_sweep, r_slide)
#   10 knockdown landing (0x800546E8, after its own ground thud descriptor 0x10) and zero-HP death (0x80029100)
#      -> MK3 land_on_my_back is shake_n_sound = rsnd_ground only, and a KO has no extra voice -> silent for every
#      donor. (v14 used group 9 'death scream': Rejected, it is the pit/fatality scream.)
#   11 slide/special yell -> no MK3 counterpart for robots -> silent
#   run (descriptor 0x22 via the Run script) -> group 7
MKT_GROUP_TABLE, MKT_VOICE_GROUP = 0x800A19D4, 0x800A19FC
DONOR_FIGHTER = 7
def _u16(va): return int.from_bytes(mkt[va - 0x80000000:va - 0x80000000 + 2], 'big')
def _u32(va): return int.from_bytes(mkt[va - 0x80000000:va - 0x80000000 + 4], 'big')
_vg = _u16(MKT_VOICE_GROUP + 2 * DONOR_FIGHTER)
def donor_group(g):
    t = _u32(MKT_GROUP_TABLE + 4 * g); n = _u16(t)
    ev = [_u16(t + 2 + 2 * (_vg * n + k)) for k in range(n)]
    return [e & 0x7FFF for e in ev if e != 0xFFFF]
_g = {g: donor_group(g) for g in range(10)}
assert _vg == 5 and _g[0] == [] and _g[1] == [] and _g[5] == [] and _g[6] == [62, 63, 64] and _g[2] == [126, 127] \
    and _g[9] == [17] and _g[7] == [35], _g
WHOOSH = [_u16(0x800A1AA8 + 2 * 6) & 0x7FFF, _u16(0x800A1AA8 + 2 * 7) & 0x7FFF]    # triple 6/7: whoosh #1/#3
assert WHOOSH == [416, 417]
WHOOSH_VOLUME = 1.0   # v17: v16's 0.85 Rejected - categories 0/1 also play the somersault jump (0x8002FB08), not only attacks
def pair(evs):            # MKMSZ picks 1 of 2; keep every distinct donor sound, in table order
    d = list(dict.fromkeys(evs)); return (d * 2)[:2] if d else [None, None]
_face = [e for e in _g[6] if e != 63]   # 62 and 63 are the same waveform (158) in MKT; 1-of-2 keeps both sounds
CATEGORY_DONOR = {
    0: (_g[0] or WHOOSH)[0], 1: (_g[0] or WHOOSH)[1 % len(_g[0] or WHOOSH)],
    2: pair(_face)[0], 3: pair(_face)[1], 4: pair(_face)[0], 5: pair(_face)[1],
    6: pair(_g[2])[0], 7: pair(_g[2])[1],
    8: (_g[1] or [None])[0], 9: (_g[5] or [None])[0], 10: None, 11: None,
}
RUN_DONOR = _g[7][0]
# host chains (isolated; see Audio system), one per distinct donor event
HOST_POOL = [
    (159, 316, 159, 149, '0000013c00007f4000000078007800000000000c00113c7f3f123c0022227820', '0100009f',
     '647340003c00007f0505009500017d00000a7f7f', '000c1d6c0000064c00000000fffffb50ffffffff00000000', '1e18f07270047889'),
    (164, 321, 164, 154, '0000014100007f4000000078007800000000000c00113c7f8365123c00227820', '010000a4',
     '647340004e00007f0505009a00017d00000a7f7f', '000d19ae0000114400000000fffffb50ffffffff00000000', '5b3eef19e893868d'),
    (168, 325, 168, 158, '0000014500007f4000000078007800000000000c00113c7f43123c0022227820', '010000a8',
     '647340003c00007f0505009e00017d00000a7f7f', '000d54dc000006a600000000fffffb50ffffffff00000000', 'cc960512bcea3be8'),
    (170, 327, 170, 160, '0000014700007f4000000078007800000000000c00113c7f8375123c00227820', '010000aa',
     '647340004800007f050500a000017d00000a7f7f', '000d63ce0000193e00000000fffffb50ffffffff00000000', 'd5b755b9ead2f240'),
    (171, 328, 171, 161, '0000014800007f4000000078007800000000000c00113c7f6f123c0022227820', '010000ab',
     '647340004800007f050500a100017d00000a7f7f', '000d7d0c0000059800000000fffffb50ffffffff00000000', 'c77d9e2a5a0b3d9f'),
    (172, 329, 172, 162, '0000014900007f4000000078007800000000000c00113c7f8141123c00227820', '010000ac',
     '647340004800007f050500a200017d00000a7f7f', '000d82a4000009b400000000fffffb50ffffffff00000000', '41f7e8f634ffd33b'),
    (173, 330, 173, 163, '0000014a00007f4000000078007800000000000c00113c7f6b123c0022227820', '010000ad',
     '647340003c00007f050500a300017d00000a7f7f', '000d8c5800000aba00000000fffffb50ffffffff00000000', '2b7c8f1d366073d9'),
    (175, 332, 175, 165, '0000014c00007f4000000078007800000000000c00113c7f8109123c00227820', '010000af',
     '647340004800007f050500a500017d00000a7f7f', '000d9d54000006dc00000000fffffb50ffffffff00000000', '3d9376e9afdccac0'),
]
_needed = list(dict.fromkeys([e for e in CATEGORY_DONOR.values() if e is not None]))
assert len(_needed) <= len(HOST_POOL)
VOICE_HOSTS = {dev: HOST_POOL[k] for k, dev in enumerate(_needed)}
CAT_EVENT = {0: 31, 1: 32, 2: 38, 3: 39, 4: 36, 5: 37, 6: 34, 7: 35, 8: 43, 9: 40, 10: 41, 11: 42}   # stock events (10 via new desc 0x2A)
CAT_DESC = {0: 0x20, 1: 0x21, 2: 0x27, 3: 0x28, 4: 0x25, 5: 0x26, 6: 0x23, 7: 0x24, 8: 0x2C, 9: 0x29, 10: 0x2A, 11: 0x2B}
SZ_VOICE_MAP = {CAT_EVENT[c]: dev for c, dev in CATEGORY_DONOR.items() if dev is not None}
NEW_TABLE = b''.join((CAT_DESC[c] if CATEGORY_DONOR[c] is not None else 0).to_bytes(2, 'big') for c in range(12))
print('CATEGORY_DONOR', CATEGORY_DONOR, 'RUN', RUN_DONOR)
SZ_TABLE_ROM = 0xA3AC8
assert clean[0xA2330 + 0x22 * 10:0xA2330 + 0x22 * 10 + 10].hex() == '00210064000000000000'   # descriptor 0x22 -> event 33
guarded(SZ_TABLE_ROM, '00200021002700280025002600230024002c00290026002b', NEW_TABLE.hex())
def _event_track_rom(e):
    assert int.from_bytes(clean[0x976D60 + e * 16 + 4:0x976D60 + e * 16 + 8], 'big') == 0x20
    return MSZ_SSEQ_TRACKS + int.from_bytes(clean[0x976D60 + e * 16 + 8:0x976D60 + e * 16 + 12], 'big')
_donor_tracks = {}
for dev, (hev, hp, hs, hw, htrk, hpat, hsub, hwav, hpred) in VOICE_HOSTS.items():
    track, sub, wav, pred, smp = _donor(dev)
    assert len(track) == 0x20, hex(dev)
    trk_rom = _event_track_rom(hev)
    assert clean[trk_rom:trk_rom + 0x20].hex() == htrk and clean[MSZ_PATCH + hp * 4:MSZ_PATCH + hp * 4 + 4].hex() == hpat
    assert hashlib.sha256(clean[MSZ_PRED + hw * 264:MSZ_PRED + hw * 264 + 264]).hexdigest().startswith(hpred)
    sb = bytearray(sub); sb[10:12] = hw.to_bytes(2, 'big')
    wv = bytearray(wav); wv[0:4] = (_cur - MSZ_TBL).to_bytes(4, 'big')
    guarded(MSZ_SUB + hs * 20, hsub, bytes(sb).hex())
    guarded(MSZ_WAVE + hw * 24, hwav, bytes(wv).hex())
    rom[MSZ_PRED + hw * 264:MSZ_PRED + hw * 264 + 264] = pred
    assert _cur + len(smp) <= SOUND_LIMIT
    rom[_cur:_cur + len(smp)] = smp
    t = bytearray(track); t[0:4] = hp.to_bytes(4, 'big')
    if dev in WHOOSH:                      # v16: attack whooshes at 85% track volume (user request)
        assert t[6] == 0x7F and WHOOSH_VOLUME == 1.0
    _donor_tracks[dev] = bytes(t)
    print('VOICE', 'MKT event', dev, '-> host', hev, hp, hs, hw, 'sample', hex(_cur), hex(len(smp)))
    _cur = (_cur + len(smp) + 0xF) & ~0xF
for sze, dev in SZ_VOICE_MAP.items():
    trk_rom = _event_track_rom(sze)
    assert int.from_bytes(clean[trk_rom:trk_rom + 4], 'big') == 157 + sze          # stock patch 187 + (event - 30)
    rom[trk_rom:trk_rom + 0x20] = _donor_tracks[dev]
print('VOICE_MAP', {k: v for k, v in SZ_VOICE_MAP.items()}, 'SAMPLES_END', hex(_cur))

# ---- v30: rocket sounds (fighter_import.sound) ----
from mkmszr.fighter_import import sound as _snd
_bank = _snd.MktSoundBank(mkt)
_chains = {c.event: c for c in _snd.ISOLATED_CHAINS}
for _name, _host in ROCKET_SOUND_HOSTS.items():
    _ev = _bank.fighter_event(DONOR_FIGHTER, _zapf.SOUND_OCHAR[_name])
    _d = _bank.event(_ev)
    _nxt = _snd.install(rom, clean, _d, _chains[_host], _cur)
    assert _nxt <= SOUND_LIMIT
    print('ROCKET_SOUND', _name, 'ochar', hex(_zapf.SOUND_OCHAR[_name]), 'MKT event', hex(_ev), '-> host', _host,
          'sample', hex(_cur), hex(len(_d.sample)), _snd.sample_digest(_d)[:16])
    _cur = _nxt
assert {_bank.fighter_event(DONOR_FIGHTER, _zapf.SOUND_OCHAR[k]) for k in ROCKET_SOUND_HOSTS} == {0x108, 0x100, 0x107}

# ---- v16: Sektor's MKT combo strings (v62 Runtime-confirmed graph, reaction selectors MKMSZ-native) ----
# Strings: HK,HK / HP,HP,D+LP / HP,HP,HK,B+HK / HP,HP,HK,HK,B+HK. See wiki Sektor takeover proof history v61/v62.
COMBO_ROM, ELBOW_ROOT_PTR_ROM, KNEE_ROOT_PTR_ROM = 0xB1CB0, 0xA1C70, 0xA1CE8
guarded(COMBO_ROM,
        '800910030200100200000000800b10c0' '000910040201100200000000800b10d0' '000913050304100201050000800b10f0'
        '8009150101031002010100000000000e' '800c13030303130201000000800b1100' '8009150102031302040100000000000e',
        '800910030300100200000000800b10c0' '000913010303100201000000800b10e0' '80090b01020110020504000000000010'
        '00091303010310020401000000000010' '800911010103100201000000800b1100' '80091303010310020401000000000010')
assert be32(rom, ELBOW_ROOT_PTR_ROM) == 0x800B10B0                     # HP/elbow root unchanged
guarded(KNEE_ROOT_PTR_ROM, '800b10f0', f'{KNEE_REC_VA:08x}')            # knee/HK root -> payload record
_kr = PAYLOAD_ROM + (KNEE_REC_VA - PAYLOAD_VA)
assert rom[_kr:_kr + 16].hex() == '8009110101031002040000000000000e'
print('COMBOS', 'graph at ROM', hex(COMBO_ROM), 'HK,HK record', hex(KNEE_REC_VA), 'ROM', hex(_kr))

# Zap script: projectile loop frames (+0xD90/+0xD94), token-0x0B constructor frame (+0xDBC) and the next
# parent frame (+0xDC4, v80/v89: keeps the parent advance from restoring an Ice descriptor) -> rocket.
_FALLBACK = be32(rom, RR + 0xD90)
assert be32(rom, RR + 0xDB8) == 0x0B and be32(rom, RR + 0xD98) == 1 and be32(rom, RR + 0xD9C) == 0xD90
for _pos in (0xD90, 0xD94, 0xDBC, 0xDC4):
    assert be32(rom, RR + _pos) == _FALLBACK, hex(_pos)
    put32(rom, RR + _pos, ROCKET_SHAPE_OFF)
# v29: no token-handler patches and no code in ROM [0x9ADD4,0x9AF20): that span is the zero tail of the
# F3DLX.Rej graphics microcode's overlay 1 (text +0x1024..+0x11C0, DMA'd into RSP IMEM 0x18DC..0x1A78).
# The rocket's palette/sub-layer/speed/first-frame setup runs from the lifted root instead (zap_post_token).
assert rom[_proj.TOKEN_PALETTE_CALL_ROM:_proj.TOKEN_PALETTE_CALL_ROM + 4].hex() == f'{_proj.STOCK_PALETTE_JAL:08x}'
assert rom[_proj.TOKEN_INSERT_CALL_ROM:_proj.TOKEN_INSERT_CALL_ROM + 4].hex() == f'{_proj.STOCK_INSERT_JAL:08x}'
assert set(rom[0x9ADD4:0x9AF20]) == {0}
print('ROCKET', 'image', hex(ROCKET_IMAGE_OFF), 'palette', hex(ROCKET_PAL_OFF), 'shape', hex(ROCKET_SHAPE_OFF),
      'file87 end', hex(_new_end), 'post-token routine', hex(ZAP_POST_TOKEN_VA))

# ---- v26: chest open / hold / close (R2 step 2c) ----
# MKT do_robo_zap: robo_open_chest_fast (RBCHEST1, RBCHEST2) -> rocket -> sleep 0x20 -> robo_close_chest.
# The Zap script's parent frames carry the chest poses (robo_zap.chest_script_words); phase 1 ends early
# and jumps to the unchanged token, so the projectile hooks keep their offsets. One lifted-root patch
# shortens the closing frame's hold to the donor 4 ticks @60 Hz.
_chest = _zap.chest_script_words(shape_map[CHEST_RELS[0]], shape_map[CHEST_RELS[1]])
for _pos, _word in sorted(_chest.items()):
    assert be32(rom, RR + _pos) == (0 if _pos == _zap.ZAP_SCRIPT + 0x14 else _FALLBACK), hex(_pos)  # stock layout
    put32(rom, RR + _pos, _word)
assert be32(rom, RR + _zap.ZAP_TOKEN) == 0x0B and be32(rom, RR + 0xDBC) == ROCKET_SHAPE_OFF
print('CHEST', {hex(r): hex(shape_map[r]) for r in CHEST_RELS}, 'script', {hex(k): hex(v) for k, v in sorted(_chest.items())})

# CIC-6102 CRC.
def rol32(v,s):
    s&=31
    return v&0xffffffff if s==0 else ((v<<s)|(v>>(32-s)))&0xffffffff
seed=0xF8CA4DDC; t1=t2=t3=t4=t5=t6=seed
for off in range(0x1000,0x101000,4):
    value=be32(rom,off); total=(t6+value)&0xffffffff
    if total<t6:t4=(t4+1)&0xffffffff
    t6=total; t3^=value; r=rol32(value,value&31); t5=(t5+r)&0xffffffff; t2^=r if t2>value else (t6^value); t1=(t1+(t5^value))&0xffffffff
crc1=(t6^t4^t3)&0xffffffff; crc2=(t5^t2^t1)&0xffffffff
put32(rom,0x10,crc1); put32(rom,0x14,crc2)
out_path.write_bytes(rom)

print('OUT',out_path)
print('SHA256',hashlib.sha256(rom).hexdigest())
print('CRC',f'{crc1:08X} / {crc2:08X}')
print('FILE87_SIZE',hex(NEW_END),'HEADROOM_V49',hex(SAFE_V49-NEW_END))
print('FRAMES',len(all_keys),'OLD',len(old_shapes),'RUN_ASSETS',len(RUN_RELS),'RUN_VISUAL_UNIQUE',len(set(run_words[:6])),'COMBO',len(COMBO_RELS),'THROW_KEYFRAMES',len(THROW_KEYS))
print('THROW_ARMS',[hex(r) for r in ARM_RELS]); print('THROW_GEOMETRY',{hex(r):(throw_frames[('throw-composite',r)]['w'],throw_frames[('throw-composite',r)]['h'],throw_frames[('throw-composite',r)]['x'],throw_frames[('throw-composite',r)]['y']) for r in ARM_RELS})
print('THROW_SEQUENCE',{pos:('RBSTANCE7' if shp==throw_stance else next(hex(r) for r,v in throw_shapes.items() if v==shp)) for pos,shp in throw_sequence.items()})
print('MODELS',len(groups),'PATTERNS',len(patterns),'TABLE',hex(TABLE_BYTES),'STREAMS',hex(STREAM_BYTES))
print('TYPE_TABLE_ALIGN_PAD',hex(align4(TYPE_START+len(table))-(TYPE_START+len(table))))
print('RECLAIM_PACK_USED',hex(best*4),'RECLAIM_CAP',hex(cap),'SLACK',hex(cap-best*4))
print('APPENDED_ITEMS',sum(1 for k in items if k not in packed),'APPENDED_BYTES',hex(sum(item_sizes[k] for k in items if k not in packed)))
print('SCRIPT_PACK','five former append scripts in dead pre-Type5 regions; High Kick packed item only')
print('PUSH_SCRIPT',[hex(x) for x in push_words]); print('RUN_LIVE_SCRIPT',[hex(x) for x in run_words]); print('RUN_POLICY','six genuine retail N64 poses only, immediate loop to +0xEE8, MKMSZ Run rate 3')
print('RUN_RATE_PATCH','ROM 0x2F7A0: 24040002 -> 24040003')
print('COMPACT_REPACK',len(all_keys),'frames /',len(patterns),'patterns / 16-colour 4-bpp')
print('TELEPORT_SCRIPTS',{k:hex(v) for k,v in scripts.items()},'FILE87_END',hex(NEW_END_TELE),'HEADROOM_V49',hex(SAFE_V49-NEW_END_TELE))
print('TELEPORT_PAYLOAD',hex(len(payload)),'bytes at ROM',hex(PAYLOAD_ROM),'-> 0x801AF420; strike record on stack (KSEG0)', [hex(x) for x in STRIKE_WORDS])
print('ALIASES','sink',[hex(x) for x in sink_alias][:3],'... emerge',[hex(x) for x in emerge_alias][:3],'...','depths',SINK_DEPTHS,EMERGE_DEPTHS,'range',RANGE_UNITS)
print('TELEPORT_PHYSICS',dict(emerge_vel=hex(EMERGE_VEL&0xffffffff),grav_nohit=hex(GRAV_NOHIT),grav_hit=hex(GRAV_HIT),drop_rate=DROP_RATE,sink=SINK_TICKS,hidden=HIDDEN_TICKS,cap=AIR_CAP,x_offset=X_OFFSET))
print('COND',hex(COND_VA))
print('TEST_INPUT','Forward, Forward + Low Kick (classic controls, ground or air), target within 592 world units (square) on the same path')
print('COMBO_SEQUENCE','RBELBOCOMBO 1,2,3 / 2,1 / 4,5,6 / 7,8,9,10,9')
print('THROW_VISUAL_POSITIONS',throw_visual_pos)
print('FALLBACK_STOCK_SHAPE_REFS',len(fallback_positions))
print('ARM_PALETTE_MAP',ARM_TO_SEKTOR); print('RUN_SUPPLEMENTAL_DEPENDENCIES','NONE'); print('SWEEP_FALL_MODELS',[frame_model[x] for x in slot_cfg[0x1F]['shapes']]); print('HELPER','REMOVED / native v53 palette architecture retained')
