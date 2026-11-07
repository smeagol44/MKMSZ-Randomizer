from pathlib import Path
from collections import Counter
from functools import lru_cache
import hashlib

root = Path('/mnt/data')
clean_path = root / 'Mortal Kombat Mythologies - Sub-Zero (USA).z64'
mkt_path = root / 'Mortal Kombat Trilogy (USA) (Rev 2)(1).z64'
v40_path = root / 'MKMSZR_mkt-sektor-idle-stage-select_prison-control_v40.z64'
out_path = root / 'MKMSZR_mkt-sektor-expanded-takeover_run-combo-throw-proof_v54.z64'

clean = clean_path.read_bytes()
mkt = mkt_path.read_bytes()
v40 = v40_path.read_bytes()
assert hashlib.sha256(clean).hexdigest() == '9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6'
assert hashlib.sha256(mkt).hexdigest() == '30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb'
assert hashlib.sha256(v40).hexdigest() == '6fa455c174d0d9417549bff5a3a662c9e67c179f5bc4d9842ae416be83b2659d'

# Reuse the already-tested MKT decoder/frame conversion helpers from v47,
# but execute only the function-definition prefix (no build side effects).
src = (root / 'build_v47.py').read_text()
prefix = src.split('# Exact v40 ownership/identity guards.')[0]
H = {}
exec(prefix, H)
be32 = H['be32']
put32 = H['put32']
align4 = H['align4']
_donor_frame_base = H['donor_frame']
BitWriter = H['BitWriter']
BitReader = H['BitReader']

# Extend the already-proven donor decoder with MKT codec 15, used by Sektor's
# throw frames. Public MKT source labels codec 15 as the 8-color RLE format.
def decode_mkt_ext(abs_off):
    codec = mkt[abs_off]
    if codec != 15:
        return H['decode_mkt'](abs_off)
    src = memoryview(mkt)[abs_off:]
    out_len = int.from_bytes(src[:4], 'big') & 0x00FFFFFF
    pos = 4
    out = bytearray()
    while len(out) < out_len:
        ch = src[pos]; pos += 1
        if ch & 0x80:
            out.extend(b'\x00' * ((ch & 0x7F) + 1))
        elif ch & 0x40:
            out.append((ch >> 3) & 0x07)
            if len(out) < out_len:
                out.append(ch & 0x07)
        else:
            pix = ch & 0x07
            if pix == 0:
                pix = (ch >> 3) & 0x07
                cnt = src[pos]; pos += 1
                out.extend(bytes([pix]) * cnt)
            else:
                cnt = ((ch >> 3) & 0x07) + 3
                out.extend(bytes([pix]) * cnt)
    return bytes(out[:out_len]), codec

def donor_frame(shape_rel):
    sa = MB + shape_rel
    sub_rel = be32(mkt, sa)
    assert sub_rel == shape_rel + 8 and be32(mkt, sa + 4) == 0, hex(shape_rel)
    s = MB + sub_rel
    image_rel = be32(mkt, s)
    h = int.from_bytes(mkt[s+4:s+6], 'big', signed=True)
    w = int.from_bytes(mkt[s+6:s+8], 'big', signed=True)
    x = int.from_bytes(mkt[s+8:s+10], 'big', signed=True)
    y = int.from_bytes(mkt[s+10:s+12], 'big', signed=True)
    decoded, codec = decode_mkt_ext(MB + image_rel)
    stride = align4(w)
    assert len(decoded) == stride * h, (hex(shape_rel), codec, len(decoded), stride*h)
    assert max(decoded, default=0) <= 31
    eh = (h + 1) & ~1
    padded = bytearray(stride * eh)
    for yy in range(h):
        padded[yy*stride:(yy+1)*stride] = decoded[yy*stride:(yy+1)*stride]
    blocks = []
    for yy in range(0, eh, 2):
        for xx in range(0, stride, 4):
            blocks.append(bytes(padded[yy*stride+xx:yy*stride+xx+4] + padded[(yy+1)*stride+xx:(yy+1)*stride+xx+4]))
    return dict(shape_rel=shape_rel, image_rel=image_rel, w=w, h=h, x=x, y=y, codec=codec, stride=stride, eh=eh, padded=bytes(padded), blocks=blocks)

MB = 0x8881C0
ORIG_FILE87_ROM = 0x748920
CLEAN_SIZE = 0x459E0
RR = 0xF40000
TYPE_START = 0x14AC
TYPE_END = 0x41684
PALETTE_OFF = 0x4584C

# Exact runtime-confirmed converted Sektor palette from v40. Only the lower
# 32 entries are replaced; stock upper 32 entries remain valid fallback colors.
SEKTOR_PALETTE32 = bytes(v40[RR + 0x4D7D4: RR + 0x4D7D4 + 64])
assert len(SEKTOR_PALETTE32) == 64


def m32(rel):
    return be32(mkt, MB + rel)


def is_donor_shape(rel):
    return (
        isinstance(rel, int)
        and rel > 0
        and MB + rel + 8 <= len(mkt)
        and m32(rel) == rel + 8
        and m32(rel + 4) == 0
    )


# Common takeover scope: all ordinary/common mapped primary states through 0x22,
# excluding Victory 0x0D and Elbow/Combo 0x10. Throw/projectile/dizzy remain
# control-correct but visually fall back to a safe Sektor stance frame.
slot_cfg = {
    0x00: dict(name='idle', donor=0x1D4, target=0x2EC,
               words=[0x1768, 0x1780, 0x1794, 0x17A8, 0x17BC, 1, 0x1D4], mode='inplace'),
    0x01: dict(name='walk-f', donor=0x230, target=0x3C0, n=9, mode='inplace'),
    0x02: dict(name='walk-b', donor=0x254, target=0x3EC, n=9, mode='inplace'),
    0x03: dict(name='turn', donor=0x21C, target=0x418, n=5, mode='inplace'),
    0x04: dict(name='crouch', donor=0x278, target=0x42C, n=4, mode='inplace'),
    0x05: dict(name='crouch-turn', donor=0x2FC, target=0x43C, n=6, mode='inplace'),
    0x06: dict(name='crouch-block', donor=0x288, target=0x458, n=4, mode='inplace'),
    0x07: dict(name='crouch-hit', donor=0x298, target=0x468, n=4, mode='inplace'),
    0x08: dict(name='crouch-punch', donor=0x314, target=0x47C, n=8, mode='inplace'),
    0x09: dict(name='crouch-high-kick', donor=0x354, n=10, mode='append'),
    0x0A: dict(name='crouch-low-kick', donor=0x334, target=0x4C0, n=8, mode='inplace'),
    0x0B: dict(name='uppercut', donor=0x37C, target=0x49C, n=9, mode='inplace'),
    0x0C: dict(name='standing-block', donor=0x50C, target=0x624, n=4, mode='inplace'),
    0x0E: dict(name='high-punch', donor=0x3A0, target=0x504, n=28, mode='inplace'),
    0x0F: dict(name='low-punch', donor=0x410, target=0x574, n=27, mode='inplace'),
    0x10: dict(name='elbow-combo', donor=0x47C, n=36, mode='append'),
    0x11: dict(name='standing-high-kick', donor=0x5EC, n=13, mode='append'),
    0x12: dict(name='standing-low-kick', donor=0x51C, n=13, mode='append'),
    0x13: dict(name='knee', donor=0x550, target=0x684, n=7, mode='inplace'),
    0x14: dict(name='sweep', donor=0x594, target=0x704, n=12, mode='inplace'),
    0x15: dict(name='roundhouse', donor=0x5C4, target=0x6DC, n=10, mode='inplace'),
    0x16: dict(name='jump', donor=0x620, target=0x734, n=4, mode='inplace'),
    0x17: dict(name='jump-kick', donor=0x630, target=0x744, n=7, mode='inplace'),
    0x18: dict(name='flip-punch', donor=0x668, target=0x77C, n=7, mode='inplace'),
    0x19: dict(name='flip-kick', donor=0x64C, target=0x760, n=7, mode='inplace'),
    0x1A: dict(name='forward-flip', donor=0x684, n=8, mode='append'),
    0x1B: dict(name='back-flip', donor=0x6A4, n=8, mode='append'),
    0x1C: dict(name='hit-high', donor=0x70C, target=0x7E8, n=5, mode='inplace'),
    0x1D: dict(name='hit-low', donor=0x720, target=0x7FC, n=5, mode='inplace'),
    0x1E: dict(name='knockdown', donor=0x808, target=0x874, n=9, mode='inplace'),
    0x1F: dict(name='sweep-fall', donor=0x1100, target=0x8B4, n=9, mode='inplace'),
    0x20: dict(name='stumble', donor=0x734, n=17, mode='append'),
    0x21: dict(name='getup', donor=0x82C, target=0x898, n=7, mode='inplace'),
    0x22: dict(name='sweep-getup', donor=0x1124, target=0x8D8, n=6, mode='inplace'),
    # Visual-only throw transplant. MKMSZ's native throw script is 12 words:
    # 2 attacker frames, terminator, 5-frame middle phase, terminator,
    # 2 recovery frames, terminator. We keep that grammar and supply genuine
    # Sektor throw poses; MKT throw callbacks/commands are intentionally not copied.
    0x23: dict(name='throw', donor=0x1180, target=0x8F8, mode='inplace',
               words=[0x22EC, 0x2300, 0,
                      0x2318, 0x232C, 0x2340, 0x2354, 0x2368, 0,
                      0x23E0, 0x241C, 0]),
}

for cfg in slot_cfg.values():
    if 'words' not in cfg:
        cfg['words'] = [m32(cfg['donor'] + 4 * i) for i in range(cfg['n'])]
    else:
        cfg['n'] = len(cfg['words'])
    cfg['shapes'] = [v for v in cfg['words'] if is_donor_shape(v)]

# Exact authoritative guards from the prior isolated proofs.
assert slot_cfg[0x0B]['words'] == [0x1A54, 0x1A68, 0x1A7C, 0x1A90, 5, 0x1AA4, 0, 0x1A90, 0]
assert slot_cfg[0x14]['words'] == [0x1E28, 0x1E3C, 0x1E50, 6, 1, 0x1E64, 0x1E78, 0, 0x1E8C, 0x1EA0, 0x1EB4, 0]
assert slot_cfg[0x20]['words'] == [0x21AC, 0x21C0, 0x21D4, 0x21E8, 0x21AC, 0x21FC, 0x2210, 0,
                                  0x21AC, 0x21C0, 0x21D4, 0x21E8, 0x21AC, 0x21FC, 0x2210, 1, 0x754]

all_shapes = []
for slot in sorted(slot_cfg):
    for rel in slot_cfg[slot]['shapes']:
        if rel not in all_shapes:
            all_shapes.append(rel)

# MKT Sektor primary 0x4A Run: six visual frames around the donor footstep callback.
# MKMSZ's own run loop is kept; only these six poses are imported.
RUN_SHAPES = [0x2708, 0x271C, 0x2730, 0x2744, 0x2758, 0x276C]
for rel in RUN_SHAPES:
    assert is_donor_shape(rel)
    if rel not in all_shapes:
        all_shapes.append(rel)

EXPECTED_UNIQUE = len(all_shapes)
assert EXPECTED_UNIQUE > 129
frame_cache = {rel: donor_frame(rel) for rel in all_shapes}

# Whole-corpus Type-5 model planner for v54.
# Keep stock-compatible 13 normal symbols and native zero-run symbols, but choose
# per-model normal class widths from the actual frequency distribution.  The
# codec-15 throw frames that use only palette indices 0..7 get a dedicated
# 3-bpp Type-5 model; all other Sektor frames remain 5-bpp.
ZERO_BITS = [2, 2, 3]
ZERO_BASES = [0, 4, 8]
ZERO_BLOCK = b'\x00' * 8
BASE_CAP = 20048
THROW_3BPP = {0x2300, 0x2318, 0x232C, 0x2340, 0x2354, 0x2368, 0x23E0, 0x241C}
assert all(max(frame_cache[r]['padded']) <= 7 for r in THROW_3BPP)

pattern_sets = {rel: {b for b in frame_cache[rel]['blocks'] if b != ZERO_BLOCK} for rel in all_shapes}

# Sequential semantic grouping for ordinary 5-bpp frames, with a dedicated
# low-bpp throw group.  This keeps every model within the stock-class 20k-ish
# pattern scale while avoiding wasting 5 bits/pixel on the codec-15 throw art.
model_groups = []
cur = []
union = set()
for rel in [r for r in all_shapes if r not in THROW_3BPP]:
    nxt = union | pattern_sets[rel]
    if cur and len(nxt) > BASE_CAP:
        model_groups.append(cur)
        cur = [rel]
        union = set(pattern_sets[rel])
    else:
        cur.append(rel)
        union = nxt
if cur:
    model_groups.append(cur)
model_groups.append([r for r in all_shapes if r in THROW_3BPP])
assert all(model_groups)

@lru_cache(None)
def zero_plan(n):
    if n == 0:
        return (0, ())
    best = (10**9, None)
    for zi, (bits, base) in enumerate(zip(ZERO_BITS, ZERO_BASES)):
        for extra in range(1 << bits):
            count = base + extra + 1
            if count <= n:
                prev_cost, prev = zero_plan(n - count)
                cost = prev_cost + 4 + bits
                if cost < best[0]:
                    best = (cost, prev + ((13 + zi, extra, bits, count),))
    return best


def optimize_normal_bits(freq_values, pattern_count):
    # 13 native normal symbols. Choose nondecreasing extra-bit widths that
    # cover this model's dictionary and minimize occurrence-weighted index bits.
    prefix = [0]
    for value in freq_values:
        prefix.append(prefix[-1] + value)

    @lru_cache(None)
    def dp(classes_left, pos, min_bits):
        if pos >= pattern_count:
            return (0, ())
        if classes_left == 0:
            return (10**30, None)
        best = (10**30, None)
        for bits in range(min_bits, 16):
            end = min(pattern_count, pos + (1 << bits))
            occurrences = prefix[end] - prefix[pos]
            rest_cost, rest = dp(classes_left - 1, end, bits)
            if rest is None:
                continue
            cost = occurrences * bits + rest_cost
            if cost < best[0]:
                best = (cost, (bits,) + rest)
        return best

    _, plan = dp(13, 0, 0)
    assert plan is not None
    plan = list(plan)
    # If all patterns were covered before 13 classes, pad unused classes with
    # the final width; they are never emitted but keep the 13-entry model ABI.
    while len(plan) < 13:
        plan.append(plan[-1] if plan else 0)
    assert len(plan) == 13
    return plan


def pack_pattern_dynamic(block, bpp):
    bw = BitWriter()
    for px in block:
        assert 0 <= px < (1 << bpp)
        bw.write(px, bpp)
    out = bw.finish()
    assert len(out) == bpp   # 8 pixels * bpp bits == bpp bytes
    return out

models = []
frame_model = {}
streams = {}
model_meta = []
for mid, rels in enumerate(model_groups):
    freq = Counter()
    for rel in rels:
        for block in frame_cache[rel]['blocks']:
            if block != ZERO_BLOCK:
                freq[block] += 1
    patterns = [p for p, _ in freq.most_common()]
    freq_values = [freq[p] for p in patterns]
    bits_plan = optimize_normal_bits(freq_values, len(patterns))
    bases = []
    acc = 0
    for bits in bits_plan:
        bases.append(acc)
        acc += 1 << bits
    assert acc >= len(patterns)
    bpp = 3 if set(rels).issubset(THROW_3BPP) else 5

    index = {p: i for i, p in enumerate(patterns)}
    code = {}
    for p, idx in index.items():
        for ci, (base, bits) in enumerate(zip(bases, bits_plan)):
            if base <= idx < base + (1 << bits):
                code[p] = (ci, idx - base, bits)
                break
        else:
            raise AssertionError(idx)

    for rel in rels:
        fr = frame_cache[rel]
        bw = BitWriter()
        bw.write(mid, 6)
        blocks = fr['blocks']
        i = 0
        while i < len(blocks):
            if blocks[i] == ZERO_BLOCK:
                j = i + 1
                while j < len(blocks) and blocks[j] == ZERO_BLOCK:
                    j += 1
                _, plan = zero_plan(j - i)
                for sym, extra, bits, _count in plan:
                    bw.write(sym, 4)
                    bw.write(extra, bits)
                i = j
            else:
                ci, extra, bits = code[blocks[i]]
                bw.write(ci, 4)
                bw.write(extra, bits)
                i += 1
        stream = bw.finish()
        while len(stream) & 3:
            stream += b'\x00'
        streams[rel] = stream
        frame_model[rel] = mid

    models.append(patterns)
    model_meta.append(dict(bits=bits_plan, bases=bases, bpp=bpp))

# Shared Type-5 table with per-model class geometry / bpp.
table = bytearray()
table += (2).to_bytes(2, 'big')
table += len(models).to_bytes(2, 'big')
records = []
pattern_bytes = bytearray()
for patterns, meta in zip(models, model_meta):
    rec = bytearray(104)
    rec[0:4] = len(pattern_bytes).to_bytes(4, 'big')
    rec[4:6] = meta['bpp'].to_bytes(2, 'big')
    for i, bits in enumerate(meta['bits']):
        rec[6 + i*2: 8 + i*2] = bits.to_bytes(2, 'big')
    for i, bits in enumerate(ZERO_BITS):
        rec[32 + i*2: 34 + i*2] = bits.to_bytes(2, 'big')
    for i, base in enumerate(meta['bases']):
        rec[40 + i*4: 44 + i*4] = base.to_bytes(4, 'big')
    for i, base in enumerate(ZERO_BASES):
        rec[92 + i*4: 96 + i*4] = base.to_bytes(4, 'big')
    records.append(rec)
    for pattern in patterns:
        pattern_bytes += pack_pattern_dynamic(pattern, meta['bpp'])
for rec in records:
    table += rec
table += pattern_bytes
assert len(table) > 0

# Clean-derived proof ROM: stage selector + logo bypass only. No palette helper,
# no 1 KiB arena reservation, no file-0x1B bootstrap.
rom = bytearray(clean)

def words_bytes(vals):
    return b''.join(int(v & 0xFFFFFFFF).to_bytes(4, 'big') for v in vals)

def jal(va):
    return 0x0C000000 | ((va >> 2) & 0x03FFFFFF)

DEBUG_MENU_VA = 0x8000D0B8
A_ROUTE_JAL_ROM = 0xE028
WRAP_LAST_ROM = 0xDD60
COUNT_ROM = 0xDD64
MENU_TABLE_ROM = 0x9B7DC
SELECTION_LOAD_ROM = 0x15CD0
MAPPER_ROM = 0x9A700
MAPPER_VA = 0x80099B00
ORIGINAL_MENU_POINTERS = (0x800AA034, 0x800AA02C, 0x800AA024, 0x800AA01C,
                          0x800AA014, 0x800AA00C, 0x800AA004, 0x800A9FF4,
                          0x800A9FEC, 0x800A9FE0, 0x800A9FD0, 0)
SAFE_MENU_POINTERS = (0x800AA034, 0x800AA02C, 0x800AA024, 0x800AA01C,
                      0x800AA014, 0x800AA00C, 0x800A9FEC, 0x800A9FE0,
                      0, 0, 0, 0)
MAPPER_WITH_SKIP = bytes.fromhex(
    '3C03800C 8C6311E0 2C610006 50200001 24630002 3C028029 03E00008 A0441C0C'
)
assert be32(rom, A_ROUTE_JAL_ROM) == 0x0C00A0C3
assert be32(rom, WRAP_LAST_ROM) == 0x2414000A
assert be32(rom, COUNT_ROM) == 0x2A82000B
assert bytes(rom[MENU_TABLE_ROM:MENU_TABLE_ROM+48]) == words_bytes(ORIGINAL_MENU_POINTERS)
assert bytes(rom[SELECTION_LOAD_ROM:SELECTION_LOAD_ROM+8]) == bytes.fromhex('3C03800C 8C6311E0')
assert bytes(rom[MAPPER_ROM:MAPPER_ROM+0x58]) == bytes(0x58)
put32(rom, A_ROUTE_JAL_ROM, jal(DEBUG_MENU_VA))
put32(rom, WRAP_LAST_ROM, 0x24140007)
put32(rom, COUNT_ROM, 0x2A820008)
rom[MENU_TABLE_ROM:MENU_TABLE_ROM+48] = words_bytes(SAFE_MENU_POINTERS)
put32(rom, SELECTION_LOAD_ROM, jal(MAPPER_VA))
put32(rom, SELECTION_LOAD_ROM+4, 0)
rom[MAPPER_ROM:MAPPER_ROM+len(MAPPER_WITH_SKIP)] = MAPPER_WITH_SKIP

BOOT = 0x7A3F4
assert bytes(rom[BOOT:BOOT+24]) == bytes.fromhex(
    '0C01F113 00000000 0C01F143 00000000 0C018576 24040080'
)
put32(rom, BOOT, 0x10000003)

# Explicit no-helper guards.
assert bytes(rom[0x1C9A0:0x1C9A8]) == clean[0x1C9A0:0x1C9A8]
assert be32(rom, 0x66F64) == 0x2442F420
assert bytes(rom[0xA5154:0xA5160]) == bytes(12)
assert bytes(rom[0x9AD84:0x9ADD4]) == bytes(0x50)
assert set(rom[0xF10000:0xF10400]) == {0xFF}

# Relocate pristine file 0x87 to the disposable high-ROM proof area.
clean_f87 = bytes(clean[ORIG_FILE87_ROM:ORIG_FILE87_ROM+CLEAN_SIZE])
assert set(rom[RR:RR+CLEAN_SIZE]) == {0xFF}
rom[RR:RR+CLEAN_SIZE] = clean_f87
put32(rom, 0xA5664, RR)
put32(rom, 0xA566C, 0)

# Native/default player palette: patch lower 32 entries of the stock 64-entry TLUT.
assert bytes(rom[RR+PALETTE_OFF:RR+PALETTE_OFF+128]) == clean_f87[PALETTE_OFF:PALETTE_OFF+128]
rom[RR+PALETTE_OFF:RR+PALETTE_OFF+64] = SEKTOR_PALETTE32
assert bytes(rom[RR+PALETTE_OFF+64:RR+PALETTE_OFF+128]) == clean_f87[PALETTE_OFF+64:PALETTE_OFF+128]

# Identify the clean stock Type-5 shape corpus and every direct script reference.
def f32(off):
    return int.from_bytes(clean_f87[off:off+4], 'big')

stock_shapes = []
for off in range(TYPE_START, TYPE_END, 4):
    if off + 20 <= CLEAN_SIZE and f32(off) == off + 8 and f32(off + 4) == 0:
        image = f32(off + 8)
        if 0 <= image < CLEAN_SIZE and clean_f87[image:image+4] == b'\x05\x00\x00\x00':
            stock_shapes.append(off)
assert len(stock_shapes) == 341
stock_shape_set = set(stock_shapes)
stock_ref_positions = [
    off for off in range(0x1B0, TYPE_START, 4)
    if f32(off) in stock_shape_set
]
assert len(stock_ref_positions) == 584

# Entire stock Type-5 corpus is now disposable because all direct script users
# will either receive genuine Sektor shapes or a safe Sektor fallback.
rom[RR+TYPE_START:RR+TYPE_END] = b'\xFF' * (TYPE_END - TYPE_START)
rom[RR+TYPE_START:RR+TYPE_START+len(table)] = table
cursor = align4(TYPE_START + len(table))

# Reserve the few longer exact scripts inside reclaimed Type-5 storage.
append_slots = [slot for slot, cfg in slot_cfg.items() if cfg['mode'] == 'append']
script_offsets = {}
for slot in append_slots:
    cursor = align4(cursor)
    script_offsets[slot] = cursor
    cursor += slot_cfg[slot]['n'] * 4
assert cursor < TYPE_END

# Materialize all 129 common Sektor frames. Fill reclaimed stock Type-5 space first;
# only the small overflow is appended after the pristine stock file end.
append_cursor = align4(CLEAN_SIZE)
shape_map = {}
frame_locations = {}
for rel in all_shapes:
    fr = frame_cache[rel]
    stream = streams[rel]
    blob_size = 20 + 12 + len(stream)
    cursor = align4(cursor)
    if cursor + blob_size <= TYPE_END:
        shape = cursor
        cursor += blob_size
        where = 'reclaimed'
    else:
        append_cursor = align4(append_cursor)
        shape = append_cursor
        append_cursor += blob_size
        where = 'append'
    sub = shape + 8
    image = sub + 12
    shape_map[rel] = shape
    frame_locations[rel] = (where, shape, blob_size)
    put32(rom, RR + shape, sub)
    put32(rom, RR + shape + 4, 0)
    put32(rom, RR + sub, image)
    rom[RR + sub + 4: RR + sub + 6] = fr['w'].to_bytes(2, 'big')
    rom[RR + sub + 6: RR + sub + 8] = fr['h'].to_bytes(2, 'big')
    rom[RR + sub + 8: RR + sub + 10] = (fr['x'] & 0xFFFF).to_bytes(2, 'big')
    rom[RR + sub + 10: RR + sub + 12] = (fr['y'] & 0xFFFF).to_bytes(2, 'big')
    rom[RR + image: RR + image + 4] = b'\x05\x00\x00\x00'
    put32(rom, RR + image + 4, TYPE_START - image)
    put32(rom, RR + image + 8, (fr['eh'] << 16) | fr['stride'])
    rom[RR + image + 12: RR + image + 12 + len(stream)] = stream

assert len(shape_map) == len(all_shapes)
assert all((off & 3) == 0 for off in shape_map.values())

# Exact script translation. Most direct states can use donor grammar with local
# jumps translated. High/Low Punch and Sweep preserve MKMSZ-native control words
# while replacing only donor-shape positions, matching the runtime-confirmed proofs.
capacity = {
    0x00:11, 0x01:11, 0x02:11, 0x03:5, 0x04:4, 0x05:7, 0x06:4, 0x07:5, 0x08:8,
    0x0A:8, 0x0B:9, 0x0C:4, 0x0E:28, 0x0F:27, 0x13:7, 0x14:12, 0x15:10, 0x16:4,
    0x17:7, 0x18:7, 0x19:7, 0x1C:5, 0x1D:5, 0x1E:9, 0x1F:9, 0x21:7, 0x22:8, 0x23:12,
}
hybrid_slots = {0x0E, 0x0F, 0x14}
owned_script_positions = set()
translated = {}
for slot, cfg in slot_cfg.items():
    donor_words = cfg['words']
    if cfg['mode'] == 'append':
        target = script_offsets[slot]
        vals = []
        for value in donor_words:
            if is_donor_shape(value):
                vals.append(shape_map[value])
            elif cfg['donor'] <= value < cfg['donor'] + cfg['n'] * 4 and (value - cfg['donor']) % 4 == 0:
                vals.append(target + (value - cfg['donor']))
            else:
                vals.append(value)
        for i, value in enumerate(vals):
            put32(rom, RR + target + 4*i, value)
            owned_script_positions.add(target + 4*i)
        put32(rom, RR + slot*4, target)
    else:
        target = cfg['target']
        if slot in hybrid_slots:
            stock_words = [f32(target + 4*i) for i in range(cfg['n'])]
            vals = [shape_map[v] if is_donor_shape(v) else stock_words[i]
                    for i, v in enumerate(donor_words)]
        else:
            vals = []
            for value in donor_words:
                if is_donor_shape(value):
                    vals.append(shape_map[value])
                elif cfg['donor'] <= value < cfg['donor'] + cfg['n'] * 4 and (value - cfg['donor']) % 4 == 0:
                    vals.append(target + (value - cfg['donor']))
                else:
                    vals.append(value)
        cap = capacity[slot]
        assert len(vals) <= cap
        for i in range(cap):
            value = vals[i] if i < len(vals) else 0
            put32(rom, RR + target + 4*i, value)
            owned_script_positions.add(target + 4*i)
    translated[slot] = vals

# Key semantic guards from prior runtime-confirmed proofs.
assert translated[0x00] == [shape_map[x] for x in (0x1768,0x1780,0x1794,0x17A8,0x17BC)] + [1,0x2EC]
assert translated[0x05] == [shape_map[0x1928],shape_map[0x193C],2,shape_map[0x1928],shape_map[0x1914],0]
assert translated[0x07] == [shape_map[0x1950],shape_map[0x198C],shape_map[0x19A0],0]
assert translated[0x0B][4] == 5
assert translated[0x14][3:5] == [6,0]
assert translated[0x1A][-2:] == [1, script_offsets[0x1A] + 4]
assert translated[0x1B][-2:] == [1, script_offsets[0x1B] + 4]
assert translated[0x20][-2:] == [1, script_offsets[0x20] + 0x20]

# MKMSZ native run loop is the 12-frame loop at +0xEE8 followed by
# command 1 -> +0xEE8 and terminator. Preserve that exact target control grammar.
# Use the six genuine Sektor run poses twice to fill MKMSZ's 12 visual ticks.
RUN_TARGET = 0xEE8
run_visuals = RUN_SHAPES + RUN_SHAPES
for i, rel in enumerate(run_visuals):
    pos = RUN_TARGET + 4*i
    assert f32(pos) in stock_shape_set
    put32(rom, RR + pos, shape_map[rel])
    owned_script_positions.add(pos)
assert [f32(RUN_TARGET + 4*12 + 4*i) for i in range(3)] == [1, RUN_TARGET, 0]
assert [be32(rom, RR + RUN_TARGET + 4*12 + 4*i) for i in range(3)] == [1, RUN_TARGET, 0]

# Any still-unported/rare stock animation state keeps its stock control grammar,
# but every direct stock Type-5 frame pointer is replaced by one safe Sektor
# stance frame. This prevents stale Sub-Zero art from depending on the reclaimed
# stock Type-5 corpus; rare states may look ugly/frozen, but should remain bounded.
fallback = shape_map[0x1768]
fallback_positions = []
for pos in stock_ref_positions:
    if pos in owned_script_positions:
        continue
    put32(rom, RR + pos, fallback)
    fallback_positions.append(pos)
assert len(fallback_positions) < 413

# Set compact file end. Only 11 of 129 Sektor frames overflow the reclaimed stock
# Type-5 region; the final footprint remains far below v49's Fortress-safe 0x4E544.
NEW_END = append_cursor
assert NEW_END < 0x5100C
assert set(clean[RR + CLEAN_SIZE: RR + NEW_END]) == {0xFF}
put32(rom, 0xA5668, RR + NEW_END)

# Independent generated-Type5 decode check for all 129 frames.
def s32(v):
    return v - 0x100000000 if v & 0x80000000 else v


def decode_generated(shape_off):
    assert be32(rom, RR + shape_off) == shape_off + 8
    sub = shape_off + 8
    image = be32(rom, RR + sub)
    assert bytes(rom[RR + image: RR + image + 4]) == b'\x05\x00\x00\x00'
    table_off = image + s32(be32(rom, RR + image + 4))
    assert table_off == TYPE_START
    dims = be32(rom, RR + image + 8)
    height = (dims >> 16) & 0xFFFF
    width = dims & 0xFFFF
    rows = int.from_bytes(rom[RR+table_off:RR+table_off+2], 'big')
    model_count = int.from_bytes(rom[RR+table_off+2:RR+table_off+4], 'big')
    assert rows == 2 and model_count == len(models)
    pattern_base = table_off + 4 + 104 * model_count
    br = BitReader(bytes(rom[RR + image + 12: RR + image + 12 + 0x100000]))
    mid = br.read(6)
    assert mid < model_count
    mo = table_off + 4 + 104 * mid
    pattern_rel = be32(rom, RR + mo)
    bpp = int.from_bytes(rom[RR+mo+4:RR+mo+6], 'big')
    assert bpp in (3, 5)
    nbits = [int.from_bytes(rom[RR+mo+6+i*2:RR+mo+8+i*2], 'big') for i in range(13)]
    zbits = [int.from_bytes(rom[RR+mo+32+i*2:RR+mo+34+i*2], 'big') for i in range(3)]
    bases = [be32(rom, RR+mo+40+i*4) for i in range(13)]
    zbases = [be32(rom, RR+mo+92+i*4) for i in range(3)]
    out = bytearray(width * height)
    blocks_w = width // 4
    total = blocks_w * (height // rows)
    bi = 0
    while bi < total:
        code = br.read(4)
        if code < 13:
            pi = bases[code] + br.read(nbits[code])
            pattern_bytes_per = bpp
            po = pattern_base + pattern_rel + pi * pattern_bytes_per
            pbr = BitReader(bytes(rom[RR+po:RR+po+pattern_bytes_per]))
            vals = [pbr.read(bpp) for _ in range(8)]
            by, bx = divmod(bi, blocks_w)
            for ry in range(2):
                dst = (by*2+ry)*width + bx*4
                out[dst:dst+4] = bytes(vals[ry*4:ry*4+4])
            bi += 1
        else:
            zi = code - 13
            run = zbases[zi] + br.read(zbits[zi]) + 1
            bi += run
            assert bi <= total
    return bytes(out), mid, width, height

for rel in all_shapes:
    decoded, mid, width, height = decode_generated(shape_map[rel])
    fr = frame_cache[rel]
    assert mid == frame_model[rel]
    assert width == fr['stride'] and height == fr['eh']
    assert decoded == fr['padded']

# No direct clean stock Type-5 image/table references exist outside the reclaimed
# region; and every original direct stock-shape script word is now owned or fallback.
for pos in fallback_positions:
    assert be32(rom, RR + pos) == fallback
for pos in stock_ref_positions:
    if pos not in owned_script_positions:
        assert be32(rom, RR + pos) == fallback

# Unported primary slots keep their stock script roots/control grammar.
for slot in (0x0D, 0x24, 0x25):
    assert be32(rom, RR + slot*4) == f32(slot*4)

# v54 semantic guards.
assert translated[0x10][0:2] == [3, 8]
assert translated[0x10][2] == shape_map[0x1C0C]
assert translated[0x23] == [
    shape_map[0x22EC], shape_map[0x2300], 0,
    shape_map[0x2318], shape_map[0x232C], shape_map[0x2340],
    shape_map[0x2354], shape_map[0x2368], 0,
    shape_map[0x23E0], shape_map[0x241C], 0,
]
assert [be32(rom, RR + RUN_TARGET + 4*i) for i in range(12)] == [
    shape_map[r] for r in run_visuals
]

# Helper really is absent; default arena begins at stock 0x801AF420.
assert bytes(rom[0x1C9A0:0x1C9A8]) == clean[0x1C9A0:0x1C9A8]
assert be32(rom, 0x66F64) == 0x2442F420
assert bytes(rom[0xA5154:0xA5160]) == bytes(12)
assert bytes(rom[0x9AD84:0x9ADD4]) == bytes(0x50)
assert set(rom[0xF10000:0xF10400]) == {0xFF}

# CIC-6102 CRC.
def rol32(v, s):
    s &= 31
    return v & 0xFFFFFFFF if s == 0 else ((v << s) | (v >> (32-s))) & 0xFFFFFFFF
seed = 0xF8CA4DDC
t1 = t2 = t3 = t4 = t5 = t6 = seed
for off in range(0x1000, 0x101000, 4):
    value = be32(rom, off)
    total = (t6 + value) & 0xFFFFFFFF
    if total < t6:
        t4 = (t4 + 1) & 0xFFFFFFFF
    t6 = total
    t3 ^= value
    r = rol32(value, value & 31)
    t5 = (t5 + r) & 0xFFFFFFFF
    t2 ^= r if t2 > value else (t6 ^ value)
    t1 = (t1 + (t5 ^ value)) & 0xFFFFFFFF
crc1 = (t6 ^ t4 ^ t3) & 0xFFFFFFFF
crc2 = (t5 ^ t2 ^ t1) & 0xFFFFFFFF
put32(rom, 0x10, crc1)
put32(rom, 0x14, crc2)

out_path.write_bytes(rom)
print('OUT', out_path)
print('SHA256', hashlib.sha256(rom).hexdigest())
print('CRC', f'{crc1:08X} / {crc2:08X}')
print('FILE87_SIZE', hex(NEW_END))
print('MAPPED_PRIMARY_SLOTS', len(slot_cfg))
print('UNIQUE_SEKTOR_FRAMES', len(all_shapes))
print('MODELS', len(models), 'PATTERNS', [len(x) for x in models])
print('TABLE_BYTES', hex(len(table)), 'STREAM_BYTES', hex(sum(len(s) for s in streams.values())))
print('RECLAIMED_FRAME_COUNT', sum(1 for x in frame_locations.values() if x[0] == 'reclaimed'))
print('APPENDED_FRAME_COUNT', sum(1 for x in frame_locations.values() if x[0] == 'append'))
print('FALLBACK_STOCK_SHAPE_REFS', len(fallback_positions))
print('HEADROOM_V49_SAFE', hex(0x4E544 - NEW_END))
print('HELPER', 'REMOVED / stock frame-setup + stock arena restored')
print('PALETTE', 'native stock TLUT lower 32 replaced with Sektor; upper 32 preserved')
