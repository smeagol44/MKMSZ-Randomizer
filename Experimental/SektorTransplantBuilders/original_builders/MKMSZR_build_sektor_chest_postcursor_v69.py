from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse, bisect, hashlib, zipfile, importlib.util
import numpy as np

parser = argparse.ArgumentParser(description='Build MKMSZR v69 post-helper Sektor chest cursor diagnostic from clean MKMSZ and MKT donors.')
parser.add_argument('clean_rom', type=Path, help='Clean supported MKMSZ USA Rev. 0 .z64')
parser.add_argument('mkt_rom', type=Path, help='MKT USA Rev. 2 N64 donor .z64')
parser.add_argument('ps1_mkt', type=Path, help='PS1 MKT unpacked directory or PS1 - MKT (unpacked).zip supplemental donor')
parser.add_argument('-o', '--output', type=Path, default=Path('MKMSZR_sektor-chest-postcursor_common-proof_v69.z64'))
parser.add_argument('--v53', type=Path, default=None, help='Optional runtime-confirmed v53 ROM for an additional 129-frame inheritance cross-check')
args = parser.parse_args()
clean_path = args.clean_rom
mkt_path = args.mkt_rom
ps1_path = args.ps1_mkt
out_path = args.output

clean = clean_path.read_bytes()
mkt = mkt_path.read_bytes()
assert hashlib.sha256(clean).hexdigest() == '9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6'
assert hashlib.sha256(mkt).hexdigest() == '30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb'


def load_ps1_member(root, suffix):
    suffix=suffix.replace('\\','/').lower()
    if root.is_dir():
        hits=[p for p in root.rglob('*') if p.is_file() and p.as_posix().lower().endswith(suffix)]
        assert len(hits)==1, (suffix,hits)
        return hits[0].read_bytes()
    assert zipfile.is_zipfile(root), root
    with zipfile.ZipFile(root,'r') as z:
        hits=[n for n in z.namelist() if n.replace('\\','/').lower().endswith(suffix)]
        assert len(hits)==1, (suffix,hits)
        return z.read(hits[0])

ps_robot_dat=load_ps1_member(ps1_path,'/CHARS1/ROBOT.DAT')
ps_robot_bin=load_ps1_member(ps1_path,'/CODE/ROBOT.BIN')
assert hashlib.sha256(ps_robot_dat).hexdigest()=='99c5ae8c98f10947172d9964e2d1649d28746060b113d61358a5699ec0bbedd0'
assert hashlib.sha256(ps_robot_bin).hexdigest()=='d5c2752c62179be1d118813d2cdae4c54d2f434cf303941c51529e9e6e4935d6'

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


def dec_16(src):
    assert src[0] == 16
    n = int.from_bytes(src[:4], 'big') & 0xffffff
    p = 4; out = bytearray()
    while len(out) < n:
        ch = src[p]; p += 1
        if ch & 0x80:
            out += bytes((0,)) * ((ch & 0x7f) + 7)
            continue
        hi = ch >> 4; pix = ch & 0x0f
        if hi == 0:
            cnt = src[p]; p += 1; out += bytes((pix,)) * cnt
        elif hi <= 6:
            out += bytes((pix,)) * hi
        else:
            cnt = pix + 3
            while cnt:
                q = src[p]; p += 1; out.append(q >> 4); cnt -= 1
                if cnt: out.append(q & 0x0f); cnt -= 1
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
    elif typ == 16: raw = dec_16(src)
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

ROCKET_P=[0x001F,0x7FFF,0x6739,0x5EF7,0x5AD6,0x5294,0x4A52,0x4210,
          0x39CE,0x318C,0x35AD,0x2D6B,0x2529,0x1CE7,0x14A5,0x0C63]
ROCKET_TO_SEKTOR={0:0}
for i,v in enumerate(ROCKET_P[1:],1):
    c=target_rgb(rgba5551_to_target(v))
    ROCKET_TO_SEKTOR[i]=min(range(16,32),key=lambda j:sum((a-b)**2 for a,b in zip(c,target_rgb(TARGET_TLUT[j]))))

def rocket_frame(rel):
    fr=donor_frame(rel)
    assert fr['codec']==16 and max(fr['padded'])<=15
    raw=bytes(ROCKET_TO_SEKTOR[v] for v in fr['padded'])
    out=dict(fr); out['padded']=raw; out['blocks']=make_blocks(raw,fr['stride'],fr['eh']); out['codec']='mkt16-rocket-remap'
    return out

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


# --- PS1 MKT robot supplemental donor ---
def le16(buf,o): return int.from_bytes(buf[o:o+2],'little')
def le32(buf,o): return int.from_bytes(buf[o:o+4],'little')
def les16(buf,o): return int.from_bytes(buf[o:o+2],'little',signed=True)

class PSBitReader:
    # PS1/PC MKT BQ: little-endian 32-bit words, consumed MSB-first.
    def __init__(self,data,unit=32):
        self.data=data; self.off=0; self.unit=unit; self.mask=(1<<unit)-1; self.bits=unit
        self.cur=self._unit(); self.nxt=self._unit()
    def _unit(self):
        n=self.unit//8; chunk=self.data[self.off:self.off+n]
        if len(chunk)<n: chunk+=bytes(n-len(chunk))
        self.off+=n; return int.from_bytes(chunk,'little')
    def read(self,n):
        if n==0:return 0
        want=n; out=0
        if self.bits<n:
            out=self.cur>>(self.unit-n); self.cur=self.nxt; self.nxt=self._unit(); want-=self.bits; self.bits=self.unit
        out|=(self.cur>>(self.unit-want))&self.mask
        self.bits-=want; self.cur=(self.cur<<want)&self.mask
        return out&((1<<n)-1)

PS_PAL_OFF=le32(ps_robot_dat,0); PS_TABLES_OFF=le32(ps_robot_dat,4)
PS_HEADER_COUNT=(PS_TABLES_OFF-4)//12
assert PS_HEADER_COUNT==609

def ps_header(i):
    o=8+12*i; first=le32(ps_robot_dat,o); typ=(first>>24)&0xff
    return dict(i=i,data=first&0xffffff,typ=typ,fileid=typ&0x1f,w=(ps_robot_dat[o+4]+3)&~3,h=ps_robot_dat[o+5],x=les16(ps_robot_dat,o+6),y=les16(ps_robot_dat,o+8),pal=le16(ps_robot_dat,o+10))

PS_HEADERS=[ps_header(i) for i in range(PS_HEADER_COUNT)]
# Match img-viewer's duplicate-header fixup behavior.
for i in range(len(PS_HEADERS)-2,-1,-1):
    if PS_HEADERS[i+1]['data']==PS_HEADERS[i]['data']:
        for k in ('w','h','pal'): PS_HEADERS[i][k]=PS_HEADERS[i+1][k]

PS_PALETTES=[]; po=PS_PAL_OFF+8
while po+2<=len(ps_robot_dat):
    n=le16(ps_robot_dat,po); po+=2
    if n==0: break
    PS_PALETTES.append([le16(ps_robot_dat,po+2*j) for j in range(n)]); po+=2*n
assert len(PS_PALETTES)==51 and len(PS_PALETTES[23])==32

def decode_ps1_povbq(h):
    assert (h['typ']&0x20)==0 and (h['typ']&0x40)!=0 and h['fileid']!=0x1e
    tb=ps_robot_dat[4:]; to=le32(tb,0); rows=le16(tb,to); ng=le16(tb,to+2); assert rows==2
    br=PSBitReader(ps_robot_dat[4+h['data']:],32); mid=br.read(6); go=to+4+mid*0x28
    vec_rel=le32(tb,go); bpp=le16(tb,go+4)
    codebits=[le16(tb,go+6+2*i) for i in range(7)]
    codeoff=[le16(tb,go+20+2*i) for i in range(7)]
    zbits=[le16(tb,go+34+2*i) for i in range(2)]
    vecbase=to+ng*0x28+vec_rel; nvec=(rows*4*bpp)//8
    out=bytearray(h['w']*h['h']); outo=0; left=(h['w']//4)*(h['h']//rows); ncols=h['w']//4; col=0
    def emit(vals):
        nonlocal outo,col
        out[outo:outo+4]=bytes(vals[:4]); outo+=h['w']
        out[outo:outo+4]=bytes(vals[4:]); outo+=4; outo-=h['w']
        col+=1
        if col==ncols: outo+=h['w']; col=0
    while left:
        code=br.read(3)
        if code==7:
            zi=br.read(1); run=br.read(zbits[zi])+1
            for _ in range(run): emit((0,)*8)
            left-=run
        else:
            vi=codeoff[code]+br.read(codebits[code]); vb=PSBitReader(tb[vecbase+vi*nvec:],8)
            emit([vb.read(bpp) for _ in range(8)]); left-=1
        assert left>=0
    return bytes(out)

# PS1 ROBOT.BIN slot 0x46 points to +0x140C. The script contains twelve distinct
# image-header references 222..233, two footstep callbacks, then 1 -> +0x140C.
PS_RUN_OFF=0x140C
ps_run_words=[le32(ps_robot_bin,PS_RUN_OFF+4*i) for i in range(19)]
ps_run_refs=[v for v in ps_run_words if (v&0xff000000)==0x88000000]
ps_run_indices=[((v&0xffffff)+4-8)//12 for v in ps_run_refs]
assert ps_run_indices==list(range(222,234)), ps_run_indices
assert ps_run_words[3:5]==[6,0x80097644] and ps_run_words[11:13]==[6,0x80097644]
assert ps_run_words[-3:]==[1,PS_RUN_OFF,0]

PS1_BODY_PAL=PS_PALETTES[23]
PS1_TO_SEKTOR={0:0}
for i,v in enumerate(PS1_BODY_PAL[1:],1):
    c=target_rgb(v)
    PS1_TO_SEKTOR[i]=min(range(1,32),key=lambda j:sum((a-b)**2 for a,b in zip(c,target_rgb(TARGET_TLUT[j]))))
assert PS1_TO_SEKTOR=={0:0,1:30,2:29,3:28,4:27,5:26,6:25,7:25,8:25,9:24,10:24,11:23,12:23,13:22,14:21,15:20,16:19,17:18,18:17,19:16,20:13,21:12,22:10,23:9,24:8,25:7,26:6,27:5,28:5,29:4,30:3,31:2}

def ps1_run_frame(num):
    idx=221+num; h=PS_HEADERS[idx]; assert h['pal']==23
    raw=decode_ps1_povbq(h); mapped=bytes(PS1_TO_SEKTOR[p] for p in raw); eh=align2(h['h'])
    if eh>h['h']: mapped+=bytes(h['w']*(eh-h['h']))
    return dict(w=h['w'],h=h['h'],x=h['x'],y=h['y'],stride=h['w'],eh=eh,padded=mapped,blocks=make_blocks(mapped,h['w'],eh),codec='ps1-povbq-vq',ps1_index=idx)


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

# Full v58 Run-fix corpus: preserve the six N64-retained odd Run poses and restore the six
# even poses from clean Midway ROBO8 source converted to calibrated N64 geometry.
# The helper data was regenerated from WIMP rows using source_stride=align4(source_width);
# this corrects the v57 tight-row extraction / diagonal-shear bug.
# A bounded Type-5 codebook approximation changes only palette/color pattern choices; transparency masks remain exact.
ROBO8_EVEN_NUMS=(2,4,6,8,10,12)
ROBO8_RUN_KEYS=[('robo8-run',n) for n in ROBO8_EVEN_NUMS]
_spec=importlib.util.spec_from_file_location('v58_run_frames', Path(__file__).with_name('v58_run_frames.py'))
_evenmod=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_evenmod)
def _robo8_even(num):
    d=_evenmod.frame(num); w=d['w']; h=d['h']; stride=align4(w); eh=align2(h)
    out=bytearray(stride*eh)
    for y in range(h): out[y*stride:y*stride+w]=d['padded'][y*w:(y+1)*w]
    raw=bytes(out)
    return dict(w=w,h=h,x=d['x'],y=d['y'],stride=stride,eh=eh,padded=raw,blocks=make_blocks(raw,stride,eh),codec='robo8-clean-vq',robo8_num=num)
robo8_source_frames={('robo8-run',n):_robo8_even(n) for n in ROBO8_EVEN_NUMS}
assert [(n,robo8_source_frames[('robo8-run',n)]['w'],robo8_source_frames[('robo8-run',n)]['h'],robo8_source_frames[('robo8-run',n)]['x'],robo8_source_frames[('robo8-run',n)]['y']) for n in ROBO8_EVEN_NUMS] == [(2,77,111,43,-8),(4,50,108,17,-12),(6,71,111,29,-8),(8,86,115,46,-8),(10,59,111,26,-9),(12,65,116,24,-4)]
assert {n:hashlib.sha256(_evenmod.frame(n)['padded']).hexdigest() for n in ROBO8_EVEN_NUMS} == {
    2:'c072299769b8d8b641ed0b21cd8853a611c408e9a9042164e5904808522f27da',
    4:'1e22189d2429a3c6c801b8d9bd28041bbdae71b61f6bc4206c2cb9551a4f4ce5',
    6:'061685549d5590ac92d63c71e9ca8b2162f75835164b2812c22597c675e93829',
    8:'20d601038e3d232c7a9313261023c11cd626404ad1624a1a6f176a9c7ae4372c',
    10:'e27e2cf419a28ef84bd2592a2c79505e87c06cc65de590da52588e652fe00419',
    12:'f61d87d13370ae3d545f75cd97bc7e35ea4745555a64b1f7800d55aeec219131',
}

base_frame_cache={**old_frames}
for r in RUN_RELS+COMBO_RELS: base_frame_cache[r]=new_frames[r]
base_frame_cache.update(throw_frames)
base_keys=old_shapes+RUN_RELS+COMBO_RELS+THROW_KEYS
base_patterns=set()
for k in base_keys: base_patterns.update(p for p in base_frame_cache[k]['blocks'] if p!=ZERO_BLOCK)
assert len(base_patterns)==40577

def pattern_mask(p):
    m=0
    for i,v in enumerate(p):
        if v:m|=1<<i
    return m

target_rgb_np=np.array([target_rgb(v) for v in TARGET_TLUT],dtype=np.float32)
def pattern_feature(p): return np.array([c for v in p for c in target_rgb_np[v]],dtype=np.float32)
# Same-mask candidate buckets preserve transparency/silhouette exactly for the clean ROBO8 even poses.
mask_buckets={}
for p in sorted(base_patterns): mask_buckets.setdefault(pattern_mask(p),[]).append(p)
mask_arrays={m:np.array([[c for v in p for c in target_rgb_np[v]] for p in vals],dtype=np.float32) for m,vals in mask_buckets.items()}
global_patterns=sorted(base_patterns)
def global_feature(p):
    out=[]
    for v in p:
        out.extend(target_rgb_np[v]); out.append(64.0 if v else 0.0)
    return np.array(out,dtype=np.float32)
global_arr=np.array([global_feature(p) for p in global_patterns],dtype=np.float32)

source_counts=Counter()
for fr in robo8_source_frames.values(): source_counts.update(p for p in fr['blocks'] if p!=ZERO_BLOCK)
nearest={}; residual={}
for p in source_counts:
    if p in base_patterns:
        nearest[p]=p; residual[p]=0.0; continue
    m=pattern_mask(p)
    if m in mask_buckets:
        q=pattern_feature(p); arr=mask_arrays[m]; ds=((arr-q)**2).sum(axis=1); j=int(ds.argmin()); cand=mask_buckets[m][j]
    else:
        q=global_feature(p); ds=((global_arr-q)**2).sum(axis=1); j=int(ds.argmin()); cand=global_patterns[j]
    e=0.0
    for a,b in zip(p,cand):
        if bool(a)!=bool(b): e+=4096.0
        elif a: e+=float(((target_rgb_np[a]-target_rgb_np[b])**2).sum())
    nearest[p]=cand; residual[p]=e

novel=[p for p in source_counts if p not in base_patterns]
by_mask={}
for p in novel: by_mask.setdefault(pattern_mask(p),[]).append(p)
features={p:pattern_feature(p) for p in novel}
# The greedy weighted medoid selector admits exactly 160 supplemental ROBO8 2x4 patterns.
# This is the highest selected quality point retained with useful headroom below the runtime-confirmed v49 footprint.
# Transparency masks/silhouettes remain exact; only opaque palette indices may be approximated.
vq_map={p:nearest[p] for p in novel}; cur={p:residual[p] for p in novel}; selected=[]; selected_set=set()
for _step in range(160):
    remaining=[q for q in novel if q not in selected_set]
    if not remaining: break
    p=max(remaining,key=lambda q:(cur[q]*source_counts[q],cur[q]))
    if cur[p] <= 0.0: break
    selected.append(p); selected_set.add(p); cur[p]=0.0; vq_map[p]=p; fp=features[p]; m=pattern_mask(p)
    for q in by_mask[m]:
        d=float(((features[q]-fp)**2).sum())
        if d<cur[q]: cur[q]=d; vq_map[q]=p
assert len(set(selected))==len(selected) and len(selected)<=160

robo8_vq_frames={}
vq_sqerr=0.0; vq_opaque=0; vq_exact=0
for k,srcfr in robo8_source_frames.items():
    qblocks=[]
    for p in srcfr['blocks']:
        if p==ZERO_BLOCK:q=ZERO_BLOCK
        elif p in base_patterns:q=p
        else:q=vq_map[p]
        qblocks.append(q)
        assert pattern_mask(p)==pattern_mask(q)  # silhouette is exact
        for a,b in zip(p,q):
            if a:
                vq_opaque+=1; vq_exact+=int(a==b); vq_sqerr+=float(((target_rgb_np[a]-target_rgb_np[b])**2).sum())
    out=bytearray(srcfr['stride']*srcfr['eh']); bw=srcfr['stride']//4
    for bi,p in enumerate(qblocks):
        by,bx=divmod(bi,bw); off=(by*2)*srcfr['stride']+bx*4
        out[off:off+4]=p[:4]; out[off+srcfr['stride']:off+srcfr['stride']+4]=p[4:]
    fr=dict(srcfr); fr['blocks']=qblocks; fr['padded']=bytes(out); robo8_vq_frames[k]=fr
VQ_RMSE=(vq_sqerr/(vq_opaque*3))**0.5
assert len(selected)==160
assert 1.895 < VQ_RMSE < 1.896
assert 0.541 < (vq_exact/vq_opaque) < 0.542

RUN12=[]
for n in range(1,13): RUN12.append(RUN_RELS[(n-1)//2] if n&1 else ('robo8-run',n))
assert len(RUN12)==12 and len(set(RUN12))==12
frame_cache=dict(base_frame_cache); frame_cache.update(robo8_vq_frames)

CHEST_KEY=('missile-proof','chest-open')
MISSILE_KEY=('missile-proof','rocket-horizontal')
EXTRA_KEYS=[CHEST_KEY]
# Fully-open chest = RBCHEST2; one horizontal rocket pose = ROCKETD1.
_chest_src=donor_frame(0x29B4)
_rocket_src=rocket_frame(0x2668)
assert (_chest_src['w'],_chest_src['h'])==(47,113)
assert (_rocket_src['w'],_rocket_src['h'])==(39,9)
# Bounded VQ: reuse only patterns already present in the current 158-frame v59 corpus.
_existing_keys=old_shapes+RUN12+COMBO_RELS+THROW_KEYS
_existing_patterns=set()
for _k in _existing_keys:
    _existing_patterns.update(p for p in frame_cache[_k]['blocks'] if p!=ZERO_BLOCK)
# Deterministic VQ candidate order: nearest-pattern ties must not depend on Python hash seed.
_existing_patterns=tuple(sorted(_existing_patterns))
_vq_buckets={}
for _p in _existing_patterns:_vq_buckets.setdefault(pattern_mask(_p),[]).append(_p)
_vq_arrays={m:np.array([[c for v in p for c in target_rgb_np[v]] for p in vals],dtype=np.float32) for m,vals in _vq_buckets.items()}
def _quantize_existing(fr,label):
    cache={}; sq=0.0; opaque=0; exact=0; missing=set(); qblocks=[]
    for p in fr['blocks']:
        if p==ZERO_BLOCK:q=ZERO_BLOCK
        elif p in _existing_patterns:q=p
        elif p in cache:q=cache[p]
        else:
            m=pattern_mask(p)
            if m not in _vq_buckets:
                missing.add(m); q=p
            else:
                feat=pattern_feature(p); arr=_vq_arrays[m]; ds=((arr-feat)**2).sum(axis=1); j=int(ds.argmin()); q=_vq_buckets[m][j]
            cache[p]=q
        qblocks.append(q)
        assert pattern_mask(p)==pattern_mask(q)
        for a,b in zip(p,q):
            if a:
                opaque+=1; exact+=int(a==b); sq+=float(((target_rgb_np[a]-target_rgb_np[b])**2).sum())
    assert not missing,(label,missing)
    out=bytearray(fr['stride']*fr['eh']); bw=fr['stride']//4
    for bi,p in enumerate(qblocks):
        by,bx=divmod(bi,bw); off=(by*2)*fr['stride']+bx*4
        out[off:off+4]=p[:4]; out[off+fr['stride']:off+fr['stride']+4]=p[4:]
    qfr=dict(fr);qfr['blocks']=qblocks;qfr['padded']=bytes(out);qfr['codec']=str(fr['codec'])+'-existing-vq'
    rmse=(sq/(opaque*3))**0.5 if opaque else 0.0
    print('EXTRA_VQ',label,'RMSE',rmse,'EXACT_OPAQUE_PCT',100*exact/opaque,'UNIQUE_SOURCE_NOVEL',len(cache))
    return qfr
frame_cache[CHEST_KEY]=_quantize_existing(_chest_src,'chest')
frame_cache[MISSILE_KEY]=_quantize_existing(_rocket_src,'rocket')

def split_even(seq,n):
    L=len(seq); return [seq[(i*L)//n:((i+1)*L)//n] for i in range(n) if (i*L)//n<((i+1)*L)//n]
# 46 inherited entropy groups + 4 Run groups + Throw + Combo = 52 model records.
old_groups=split_even(old_shapes,58); run_groups=split_even(RUN12,4)
groups=old_groups+run_groups+[THROW_KEYS,COMBO_RELS]
# Fold the two proof frames into existing model group 56; no new model record.
groups[56]=groups[56]+EXTRA_KEYS
all_keys=old_shapes+RUN12+COMBO_RELS+THROW_KEYS+EXTRA_KEYS
assert len(groups)==64 and len(all_keys)==159

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
print("AUDIT_PATTERNS",len(patterns))


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
print("AUDIT_STREAM_BYTES",hex(STREAM_BYTES))

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
print("AUDIT_TABLE_BYTES",hex(TABLE_BYTES))

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

# Item packer: 158 frame blobs + one 52-byte exact high-kick script. Maximize reclaimed bytes.
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
# v58 Run-fix bounded static footprint guard: corrected source data changes compression,
# so the exact end is intentionally re-pinned only after the first successful clean build.
print('AUDIT_SAFE_V49_OK',NEW_END<SAFE_V49)
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

# Run: +0xEE8 is the genuine 12-visual MKMSZ Run loop. Use all twelve distinct
# Sektor poses: N64-retained odd frames interleaved with clean ROBO8-derived even frames.
RUN_TARGET=0xEE8
clean_run=[f32(RUN_TARGET+4*i) for i in range(14)]
assert clean_run[12:]==[1,0xEE8]
run_visual=RUN12
run_words=[shape_map[x] for x in run_visual]+clean_run[12:]
assert len(set(run_words[:12]))==12
for i,v in enumerate(run_words): put32(rom,RR+RUN_TARGET+4*i,v); owned_script_positions.add(RUN_TARGET+4*i)

# Complete MKMSZ Knee animation ownership for combo-only late parts.
# Ordinary Knee uses only parts 1/2, but the six-hit MKMSZ combo table at ROM 0xB1CB0
# also invokes Knee part 5 (0x1305) and Knee part 3 (0x1303). v58 still left
# those later shape positions to the global safe-stance fallback, producing the neutral/missing
# middle combo visuals observed at runtime. Preserve every stock control/separator word and
# replace only those direct shape references with already-resident genuine Sektor art.
#
# Target Knee part 3 is a crossover into the last two shapes of target Roundhouse part 1
# (the same stock shape pointers occur at +0x6A0/+0x6A4 and +0x6E8/+0x6EC), so map them
# to the corresponding last two Sektor Roundhouse-part-1 poses RBSPINKICK4/5.
# Parts 4/5 reuse Knee poses; map them to RBKNEE3 and RBKNEE1/2/3 respectively.
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

# All controls/separators in late Knee remain byte-identical to clean MKMSZ.
for pos in (0x6A8,0x6B0,0x6B4,0x6B8,0x6BC,0x6C0,0x6C8,0x6CC,0x6D8):
    assert be32(rom,RR+pos)==f32(pos), (hex(pos),hex(be32(rom,RR+pos)),hex(f32(pos)))

# The target six-record combo chain is gameplay/control data and must remain untouched.
# Its animation selectors are 0x1003, 0x1004, 0x1305, 0x1501, 0x1303, 0x1501.
_combo_anim_words=[be32(clean,0xB1CB0+0x10*i)&0xFFFF for i in range(6)]
assert _combo_anim_words==[0x1003,0x1004,0x1305,0x1501,0x1303,0x1501], [hex(x) for x in _combo_anim_words]
assert bytes(rom[0xB1CB0:0xB1D10])==clean[0xB1CB0:0xB1D10]

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

# Independent Type-5 decoder verifies all 158 emitted frames byte-for-byte against their chosen target buffers.
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


# ---------------------------------------------------------------------------
# v64 proof composition on top of the compact 160-frame Sektor corpus.
# Preserve v60 Cyrax-style first-Scorpion alternate palette and v62-safe combo semantics.
CYRAX=bytes.fromhex(
 '0000df9ec75cb6faaab89a7791f2869a8a568214858f854d852b80c880648043'
 'f7bdef7be739d6b5ce73bdefb5adad6ba52998c690848c638842842180008000')
assert len(CYRAX)==64
ALT_PAL_ROM=RR+0x458D0
assert bytes(rom[ALT_PAL_ROM:ALT_PAL_ROM+64])==bytes.fromhex(
 '0000463135ad2d6b252921081ce718c614a510840c630842042100016fdf5f9f'
 '573f4adf469e427c3e3b39fa31d82db72976255521341d1210d10caf048e006b')
rom[ALT_PAL_ROM:ALT_PAL_ROM+64]=CYRAX

def w16s(vals): return b''.join(int(x&0xffff).to_bytes(2,'big') for x in vals)
combo_records=[
 [0x8009,0x1003,0x0300,0x1002,0x0000,0x0000,0x800B,0x10C0],
 [0x0009,0x1301,0x0303,0x1002,0x0100,0x0000,0x800B,0x10E0],
 [0x8009,0x0B01,0x0201,0x1002,0x0504,0x0000,0x0000,0x0010],
 [0x0009,0x1303,0x0103,0x1002,0x0401,0x0000,0x0000,0x0010],
 [0x8009,0x1101,0x0103,0x1002,0x0100,0x0000,0x800B,0x1100],
 [0x8009,0x1303,0x0103,0x1002,0x0401,0x0000,0x0000,0x0010],
]
for i,r in enumerate(combo_records): rom[0xB1CB0+i*0x10:0xB1CC0+i*0x10]=w16s(r)
# Disposable v62 proof-only HK,HK continuation allocation (same already runtime-confirmed proof site).
assert bytes(rom[0x9AD90:0x9ADA0])==bytes(16)
rom[0x9AD90:0x9ADA0]=w16s([0x8009,0x1101,0x0103,0x1002,0x0400,0,0,0x000E])
put32(rom,0xA1CE8,0x8009A190)

# v69 post-helper cursor diagnostic. Keep the entire stock Ice action/projectile/effect
# machinery intact. At the one straight-Ice player-animation call, run stock 0x80030E98
# completely first. Then temporarily redirect the *resolved process animation cursor*
# (current process +0x6E4), advance exactly one frame through stock 0x800304C0 to install
# the Sektor chest pose, and restore the original cursor immediately. This tests the
# statically-confirmed cursor field without changing normal animation lifecycle state.
CHEST_SHAPE=shape_map[CHEST_KEY]

# Ice secondary/effect and projectile scripts stay exactly as produced by the Sektor
# takeover baseline (fallback visuals, stock control grammar). This remains chest-only.
assert [be32(rom,RR+0x11AC+4*i) for i in range(7)]==[fallback]*6+[0]
assert be32(rom,RR+0xFD0)==0xD90
assert [be32(rom,RR+0xD90+4*i) for i in range(4)]==[fallback,fallback,1,0xD90]

# Dedicated one-frame chest script lives inside file 0x87. It is addressed directly via
# actor+0x98 resource base + CHEST_SCRIPT_OFF; no primary/secondary animation table entry
# is changed at runtime or statically.
CHEST_SCRIPT_OFF=align4(NEW_END)
CHEST_SCRIPT_BYTES=8
FINAL_END=CHEST_SCRIPT_OFF+CHEST_SCRIPT_BYTES
assert set(rom[RR+CHEST_SCRIPT_OFF:RR+FINAL_END])=={0xFF}
put32(rom,RR+CHEST_SCRIPT_OFF,CHEST_SHAPE)
put32(rom,RR+CHEST_SCRIPT_OFF+4,0)
put32(rom,0xA5668,RR+FINAL_END)

# Proof-only wrapper uses the same disposable cave line as the v62 combo proof. It calls
# the original helper first. Static disassembly establishes that 0x8002FE54 resolves the
# selected animation into current-process +0x6E4, and 0x800304C0 consumes/advances that
# cursor. Save the stock post-helper cursor, install one chest frame, then restore it.
CHEST_ROUTINE_ROM=0x9ADA0; CHEST_ROUTINE_VA=0x8009A1A0
assert set(rom[CHEST_ROUTINE_ROM:0x9AE20])=={0}
_R={'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,'t0':8,'t1':9,'t2':10,'t3':11,'t4':12,'t5':13,'t6':14,'t7':15,'s0':16,'s1':17,'s2':18,'s3':19,'s4':20,'s5':21,'s6':22,'s7':23,'t8':24,'t9':25,'k0':26,'k1':27,'gp':28,'sp':29,'fp':30,'ra':31}
def _i(op,rs,rt,imm): return ((op&0x3f)<<26)|((_R[rs]&31)<<21)|((_R[rt]&31)<<16)|(imm&0xffff)
def _r(rs,rt,rd,sh,fn): return ((_R[rs]&31)<<21)|((_R[rt]&31)<<16)|((_R[rd]&31)<<11)|((sh&31)<<6)|(fn&63)
def _words(vals): return b''.join(int(v&0xffffffff).to_bytes(4,'big') for v in vals)

_ch=[]
def C(w): _ch.append(w)
C(_i(0x09,'sp','sp',-0x20))
C(_i(0x2B,'sp','ra',0x1C))
C(_i(0x2B,'sp','s0',0x18))
C(_i(0x2B,'sp','s1',0x14))
C(jal(0x80030E98))                         # full stock player animation first
C(0)
C(_i(0x0F,'zero','t0',0x802F))
C(_i(0x23,'t0','t0',0xCE20))              # current process
C(_i(0x23,'t0','s0',0x06E4))              # preserve resolved stock cursor
C(_i(0x23,'t0','s1',0x06E0))              # player actor
C(_i(0x23,'s1','t1',0x0098))              # file-0x87 resource base
C(_i(0x0F,'zero','t2',(CHEST_SCRIPT_OFF>>16)&0xffff))
C(_i(0x0D,'t2','t2',CHEST_SCRIPT_OFF&0xffff))
C(_r('t1','t2','t2',0,0x21))              # absolute chest-script cursor
C(_i(0x2B,'t0','t2',0x06E4))
C(jal(0x800304C0))                         # install exactly one chest frame
C(_r('s1','zero','a0',0,0x21))
C(_i(0x0F,'zero','t0',0x802F))
C(_i(0x23,'t0','t0',0xCE20))
C(_i(0x2B,'t0','s0',0x06E4))              # restore stock post-helper cursor
C(_i(0x23,'sp','s1',0x14))
C(_i(0x23,'sp','s0',0x18))
C(_i(0x23,'sp','ra',0x1C))
C(_i(0x09,'sp','sp',0x20))
C(_r('ra','zero','zero',0,0x08))
C(0)
_ch_b=_words(_ch)
assert len(_ch_b)<=0x80
rom[CHEST_ROUTINE_ROM:CHEST_ROUTINE_ROM+len(_ch_b)]=_ch_b
assert be32(rom,0x4B938)==jal(0x80030E98)
put32(rom,0x4B938,jal(CHEST_ROUTINE_VA))

# All Ice helper processes and straight-projectile setup/flight remain stock.
assert be32(rom,0x4BA68)==jal(0x8002830C)
assert be32(rom,0x4BA84)==jal(0x8002830C)
assert be32(rom,0x4C468)==0x3C050009
assert be32(rom,0x4C470)==0x24060004
assert be32(rom,0x4C484)==0x08012E71
assert be32(rom,0x4C488)==0xAC40070C

# Authentic proof input remains Forward, Forward + Low Punch, mirrored by facing.
assert rom[0xB1B4A:0xB1B50]==bytes.fromhex('000900070000')
assert rom[0xB1B56:0xB1B5C]==bytes.fromhex('000800070000')
rom[0xB1B4C:0xB1B4E]=(9).to_bytes(2,'big')
rom[0xB1B58:0xB1B5A]=(8).to_bytes(2,'big')

# Proof-only max-tier gate: feed the native condition final-threshold XP (7354) so the
# special is immediately testable.  No production progression semantics are changed.
assert bytes(rom[0x4AFAC:0x4AFB4])==bytes.fromhex('3C048011 8C84200C')
assert bytes(rom[0x4B008:0x4B010])==bytes.fromhex('3C048011 8C84200C')
rom[0x4AFAC:0x4AFB4]=bytes.fromhex('24041CBA 00000000')
rom[0x4B008:0x4B010]=bytes.fromhex('24041CBA 00000000')

# Bounded allocation check. This proof contains one new chest image plus an 8-byte script.
assert FINAL_END<0x5100C
assert FINAL_END<=0x4E800,hex(FINAL_END)
assert [be32(rom,RR+0x11AC+4*i) for i in range(7)]==[fallback]*6+[0]
assert be32(rom,0x4B92C)==0x24050024
assert be32(rom,0x4B938)==jal(CHEST_ROUTINE_VA)
assert be32(rom,RR+CHEST_SCRIPT_OFF)==CHEST_SHAPE
assert be32(rom,RR+CHEST_SCRIPT_OFF+4)==0
assert be32(rom,0x4BA68)==jal(0x8002830C) and be32(rom,0x4BA84)==jal(0x8002830C)
assert be32(rom,0x4C468)==0x3C050009 and be32(rom,0x4C470)==0x24060004
assert be32(rom,0x4C484)==0x08012E71 and be32(rom,0x4C488)==0xAC40070C
assert [be32(rom,RR+0xD90+4*i) for i in range(4)]==[fallback,fallback,1,0xD90]
assert be16(rom,0xB1B4A)==9 and be16(rom,0xB1B4C)==9
assert be16(rom,0xB1B56)==8 and be16(rom,0xB1B58)==8

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
print('V69_CHEST_SHAPE',hex(CHEST_SHAPE),'SCRIPT',hex(CHEST_SCRIPT_OFF))
print('V69_INPUT','F,F+LP')
print('V69_TEST_XP_GATE',7354)
print('CRC',f'{crc1:08X} / {crc2:08X}')
print('FILE87_SIZE',hex(FINAL_END),'HEADROOM_V49',hex(SAFE_V49-FINAL_END),'DELTA_V59',hex(FINAL_END-0x4E3FC))
print('FRAMES',len(all_keys),'OLD',len(old_shapes),'RUN12',len(RUN12),'ROBO8_RESTORED',len(ROBO8_RUN_KEYS),'COMBO',len(COMBO_RELS),'THROW_KEYFRAMES',len(THROW_KEYS))
print('THROW_ARMS',[hex(r) for r in ARM_RELS]); print('THROW_GEOMETRY',{hex(r):(throw_frames[('throw-composite',r)]['w'],throw_frames[('throw-composite',r)]['h'],throw_frames[('throw-composite',r)]['x'],throw_frames[('throw-composite',r)]['y']) for r in ARM_RELS})
print('THROW_SEQUENCE',{pos:('RBSTANCE7' if shp==throw_stance else next(hex(r) for r,v in throw_shapes.items() if v==shp)) for pos,shp in throw_sequence.items()})
print('MODELS',len(groups),'PATTERNS',len(patterns),'TABLE',hex(TABLE_BYTES),'STREAMS',hex(STREAM_BYTES))
print('TYPE_TABLE_ALIGN_PAD',hex(align4(TYPE_START+len(table))-(TYPE_START+len(table))))
print('RECLAIM_PACK_USED',hex(best*4),'RECLAIM_CAP',hex(cap),'SLACK',hex(cap-best*4))
print('APPENDED_ITEMS',sum(1 for k in items if k not in packed),'APPENDED_BYTES',hex(sum(item_sizes[k] for k in items if k not in packed)))
print('SCRIPT_PACK','five former append scripts in dead pre-Type5 regions; High Kick packed item only')
print('PUSH_SCRIPT',[hex(x) for x in push_words]); print('RUN_SCRIPT',[hex(x) for x in run_words])
print('COMBO_SEQUENCE','RBELBOCOMBO 1,2,3 / 2,1 / 4,5,6 / 7,8,9,10,9'); print('COMBO_LATE_KNEE_MAP',{hex(k):hex(v) for k,v in KNEE_LATE_MAP.items()})
print('THROW_VISUAL_POSITIONS',throw_visual_pos)
print('FALLBACK_STOCK_SHAPE_REFS',len(fallback_positions))
print('ARM_PALETTE_MAP',ARM_TO_SEKTOR); print('ROBO8_VQ_SELECTED',len(selected),'VQ_RMSE',round(VQ_RMSE,6),'VQ_EXACT_PIXELS_PCT',round(100*vq_exact/vq_opaque,3)); print('SWEEP_FALL_MODELS',[frame_model[x] for x in slot_cfg[0x1F]['shapes']]); print('HELPER','REMOVED / native v53 palette architecture retained')
