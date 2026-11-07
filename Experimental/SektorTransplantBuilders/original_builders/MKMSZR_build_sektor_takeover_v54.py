from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse, bisect, hashlib

parser = argparse.ArgumentParser(description='Build the MKMSZR v54 Sektor Run/Combo/Throw proof ROM from clean MKMSZ + MKT donor ROMs.')
parser.add_argument('clean_rom', type=Path, help='Clean supported MKMSZ USA Rev. 0 .z64')
parser.add_argument('mkt_rom', type=Path, help='MKT USA Rev. 2 donor .z64')
parser.add_argument('-o', '--output', type=Path, default=Path('MKMSZR_mkt-sektor-run-combo-throw_common-proof_v54.z64'))
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
    def blit(fr, x0, y0):
        ox=x0-minx; oy=y0-miny
        for yy,row in enumerate(visible_rows(fr)):
            dst=(oy+yy)*stride+ox
            for xx,p in enumerate(row):
                if p: out[dst+xx]=p
    blit(body,bx0,by0); blit(arm,ax0,ay0)
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
new_frames={r:donor_frame(r) for r in RUN_RELS+COMBO_RELS+[BODY_REL]+ARM_RELS}
THROW_KEYS=[('throw-composite',r) for r in ARM_RELS]
throw_frames={k:composite(new_frames[BODY_REL],new_frames[k[1]]) for k in THROW_KEYS}
assert (throw_frames[('throw-composite',0x23B8)]['w'],throw_frames[('throw-composite',0x23B8)]['h'],throw_frames[('throw-composite',0x23B8)]['x'],throw_frames[('throw-composite',0x23B8)]['y'])==(114,115,88,-5)

# Sixteen entropy models share one physical 5-bpp pattern dictionary. The inherited v53
# corpus is split into small entropy groups only; decoded pixels remain byte-identical. This buys
# enough stream savings for seven genuine throw keyframes while retaining ~1 KiB below v49.
def split_even(seq,n):
    L=len(seq)
    return [seq[(i*L)//n:((i+1)*L)//n] for i in range(n)]
old_groups=split_even(old_shapes[:69],7)+split_even(old_shapes[69:],6)
group_run=RUN_RELS
group_throw=THROW_KEYS
group_combo=COMBO_RELS
groups=old_groups+[group_run,group_throw,group_combo]
assert [len(g) for g in old_groups]==[9,10,10,10,10,10,10,10,10,10,10,10,10]
assert [len(group_run),len(group_throw),len(group_combo)]==[6,7,10]
frame_cache={**old_frames}
for r in RUN_RELS+COMBO_RELS: frame_cache[r]=new_frames[r]
frame_cache.update(throw_frames)
all_keys=[k for g in groups for k in g]
assert len(all_keys)==152

# Shared one-copy 5-bpp dictionary, with independent model entropy windows.
freqs=[]
for g in groups:
    c=Counter()
    for k in g: c.update(b for b in frame_cache[k]['blocks'] if b!=ZERO_BLOCK)
    freqs.append(c)
all_patterns=set().union(*(set(c) for c in freqs))
patterns=sorted(all_patterns,key=lambda p:tuple(-mf.get(p,0) for mf in freqs)+(p,))
assert len(patterns)==40594
pidx={p:i for i,p in enumerate(patterns)}


def best_partition(mf, K=13):
    used=sorted((pidx[p],w,p) for p,w in mf.items())
    idx=[x[0] for x in used]; wt=[x[1] for x in used]; pref=[0]
    for w in wt: pref.append(pref[-1]+w)
    n=len(used)
    @lru_cache(None)
    def dp(pos,k):
        if pos>=n: return (0,())
        if k==0: return (10**30,None)
        base=idx[pos]; best=(10**30,None)
        for bits in range(17):
            q=bisect.bisect_left(idx,base+(1<<bits),pos,n)
            if q==pos: continue
            cost=bits*(pref[q]-pref[pos]); rc,rp=dp(q,k-1)
            if rp is not None and cost+rc<best[0]: best=(cost+rc,((base,bits,pos,q),)+rp)
        return best
    cost,plan=dp(0,K)
    assert plan is not None and len(plan)==13
    cmap={}
    for ci,(base,bits,a,q) in enumerate(plan):
        for j in range(a,q):
            ix,w,p=used[j]; cmap[p]=(ci,ix-base,bits)
    assert len(cmap)==len(mf)
    return plan,cmap

model_plans=[]; model_maps=[]
for mf in freqs:
    pl,cm=best_partition(mf); model_plans.append(pl); model_maps.append(cm)
assert len(model_plans)==len(groups) and all(len(p)==13 for p in model_plans)
ZERO_BITS=[2,2,3]; ZERO_BASES=[0,4,8]
@lru_cache(None)
def zero_plan(n):
    if n==0:return (0,())
    best=(10**9,None)
    for zi,(bits,base) in enumerate(zip(ZERO_BITS,ZERO_BASES)):
        for extra in range(1<<bits):
            cnt=base+extra+1
            if cnt<=n:
                pc,pp=zero_plan(n-cnt); cost=pc+4+bits
                if cost<best[0]: best=(cost,pp+((13+zi,extra,bits,cnt),))
    return best

streams={}; frame_model={}
for mid,g in enumerate(groups):
    cm=model_maps[mid]
    for k in g:
        fr=frame_cache[k]; bw=BitWriter(); bw.write(mid,6); bl=fr['blocks']; i=0
        while i<len(bl):
            if bl[i]==ZERO_BLOCK:
                j=i+1
                while j<len(bl) and bl[j]==ZERO_BLOCK:j+=1
                _,plan=zero_plan(j-i)
                for sym,extra,bits,_ in plan: bw.write(sym,4); bw.write(extra,bits)
                i=j
            else:
                ci,extra,bits=cm[bl[i]]; bw.write(ci,4); bw.write(extra,bits); i+=1
        stream=bw.finish()
        while len(stream)&3: stream+=b'\0'
        streams[k]=stream; frame_model[k]=mid
STREAM_BYTES=sum(len(x) for x in streams.values())
assert STREAM_BYTES==0x156B8

# Shared table: every model record points to the same physical pattern array.
def pack_pattern(block):
    bw=BitWriter()
    for px in block:
        assert 0<=px<32; bw.write(px,5)
    out=bw.finish(); assert len(out)==5; return out

table=bytearray((2).to_bytes(2,'big')+len(groups).to_bytes(2,'big'))
for pl in model_plans:
    rec=bytearray(104)
    rec[0:4]=(0).to_bytes(4,'big')
    rec[4:6]=(5).to_bytes(2,'big')
    for i,(_base,bits,_a,_q) in enumerate(pl): rec[6+i*2:8+i*2]=bits.to_bytes(2,'big')
    for i,bits in enumerate(ZERO_BITS): rec[32+i*2:34+i*2]=bits.to_bytes(2,'big')
    for i,(base,_bits,_a,_q) in enumerate(pl): rec[40+i*4:44+i*4]=base.to_bytes(4,'big')
    for i,base in enumerate(ZERO_BASES): rec[92+i*4:96+i*4]=base.to_bytes(4,'big')
    table+=rec
for p in patterns: table+=pack_pattern(p)
TABLE_BYTES=len(table)
assert TABLE_BYTES==0x31F5E

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
rom[RR+PALETTE_OFF:RR+PALETTE_OFF+64]=SEKTOR_PALETTE32

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
assert NEW_END==0x4E154
assert NEW_END<SAFE_V49, (hex(NEW_END),hex(SAFE_V49))
assert set(clean[RR+CLEAN_SIZE:RR+NEW_END])=={0xFF}
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

# Run: preserve MKMSZ 7-visual loop grammar exactly; no MKT footstep callback.
RUN_TARGET=0x1B0
clean_run=[f32(RUN_TARGET+4*i) for i in range(9)]
assert clean_run[7:]==[1,0x1B4]
run_visual=[RUN_RELS[0],RUN_RELS[1],RUN_RELS[2],RUN_RELS[3],RUN_RELS[4],RUN_RELS[5],RUN_RELS[0]]
run_words=[shape_map[x] for x in run_visual]+clean_run[7:]
for i,v in enumerate(run_words): put32(rom,RR+RUN_TARGET+4*i,v); owned_script_positions.add(RUN_TARGET+4*i)
assert be32(rom,RR+0x104+0x27*4)==0x1B0

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
throw_sequence={
    0:throw_stance,
    1:throw_shapes[0x2318],
    3:throw_shapes[0x2340],
    4:throw_shapes[0x237C],
    5:throw_shapes[0x2390],
    6:throw_shapes[0x23B8],
    7:throw_shapes[0x23CC],
    9:throw_shapes[0x2408],
    10:throw_stance,
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

# Independent Type-5 decoder verifies all 152 emitted frames byte-for-byte.
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
    mo=table_off+4+104*mid; prel=be32(rom,RR+mo); bpp=be16(rom,RR+mo+4); assert bpp==5 and prel==0
    nbits=[be16(rom,RR+mo+6+i*2) for i in range(13)]
    zbits=[be16(rom,RR+mo+32+i*2) for i in range(3)]
    bases=[be32(rom,RR+mo+40+i*4) for i in range(13)]
    zbases=[be32(rom,RR+mo+92+i*4) for i in range(3)]
    out=bytearray(width*height); bw=width//4; total=bw*(height//rows); bi=0
    while bi<total:
        code=br.read(4)
        if code<13:
            pi=bases[code]+br.read(nbits[code]); po=pbase+prel+pi*5; pbr=BitReader(bytes(rom[RR+po:RR+po+5])); vals=[pbr.read(5) for _ in range(8)]
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
print('FRAMES',len(all_keys),'OLD',len(old_shapes),'RUN',len(RUN_RELS),'COMBO',len(COMBO_RELS),'THROW_KEYFRAMES',len(THROW_KEYS))
print('THROW_ARMS',[hex(r) for r in ARM_RELS]); print('THROW_GEOMETRY',{hex(r):(throw_frames[('throw-composite',r)]['w'],throw_frames[('throw-composite',r)]['h'],throw_frames[('throw-composite',r)]['x'],throw_frames[('throw-composite',r)]['y']) for r in ARM_RELS})
print('THROW_SEQUENCE',{pos:('RBSTANCE7' if shp==throw_stance else next(hex(r) for r,v in throw_shapes.items() if v==shp)) for pos,shp in throw_sequence.items()})
print('MODELS',len(groups),'PATTERNS',len(patterns),'TABLE',hex(TABLE_BYTES),'STREAMS',hex(STREAM_BYTES))
print('TYPE_TABLE_ALIGN_PAD',hex(align4(TYPE_START+len(table))-(TYPE_START+len(table))))
print('RECLAIM_PACK_USED',hex(best*4),'RECLAIM_CAP',hex(cap),'SLACK',hex(cap-best*4))
print('APPENDED_ITEMS',sum(1 for k in items if k not in packed),'APPENDED_BYTES',hex(sum(item_sizes[k] for k in items if k not in packed)))
print('SCRIPT_PACK','five former append scripts in dead pre-Type5 regions; High Kick packed item only')
print('RUN_SCRIPT',[hex(x) for x in run_words])
print('COMBO_SEQUENCE','RBELBOCOMBO 1,2,3 / 2,1 / 4,5,6 / 7,8,9,10,9')
print('THROW_VISUAL_POSITIONS',throw_visual_pos)
print('FALLBACK_STOCK_SHAPE_REFS',len(fallback_positions))
print('HELPER','REMOVED / native v53 palette architecture retained')
