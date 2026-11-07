#!/usr/bin/env python3
"""MKMSZR Sektor straight-missile v89 pre-published texture proof.

Baseline: exact Runtime-confirmed v75 missile proof.
Donor: exact MKT USA Rev. 2.

v87 Runtime-confirmed the donor-faithful ROCKETD1 + ROCKET_P asset/palette pair,
but its first published projectile frame is the old texture-slot contents colored by
ROCKET_P. v88 proved that changing the descriptor/cursor before insertion is not enough:
the one-frame glitched Sektor remains even though the later missile is correct.

Static render reconciliation explains the boundary. 0x8001BDA0/0x800304C0 updates the
actor record and marks +0xFA dirty, but the normal actor pass at 0x800185B8 only then
queues the texture upload through 0x8001D6EC. Native helper 0x8001BF70 is an established
synchronous texture-slot loader: it installs slot metadata, queues the pixels, and
immediately drains via 0x8001D7F0(1).

v89 therefore keeps v87's exact retail rocket pixels and dynamic ROCKET_P ownership,
uses the v80-proven rocket constructor entry and makes the next straight-parent frame a
rocket as well, then synchronously loads the already-constructed raw rocket into the
projectile's finalized texture slot before stock 0x80024650 publishes the actor. A final
0x8001BDA0 refresh binds the now-ready slot/palette metadata before insertion.

Helper/tint processes, (+5,+38) placement, child ownership, v75 acceleration/cadence,
collision and cleanup remain unchanged. 0x8001BF70 advances target texture-storage state,
so this is deliberately a one-shot disposable diagnostic, not a production lifecycle.
Palette/texture release remains Pending.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V75_SHA256 = "e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
MKT_SHA256 = "30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb"
ROM_SIZE = 0x1000000
MKT_SIZE = 0xC00000

# v75 relocated file 0x87.
RR = 0x00F40000
EXPECTED_V75_FILE87_END = 0x0004E790
ROCKET_SHAPE_OFF = 0x0004E6E4
ROCKET_DESC_OFF = 0x0004E6EC
ROCKET_OLD_IMAGE_OFF = 0x0004E6F8
STRAIGHT_NEXT_CURSOR = 0x00000DC0
STRAIGHT_NEXT_FRAME = 0x00000DC4

# Exact retail MKT robot data / ROCKETD1.
MKT_ROBOT_BASE = 0x008881C0
MKT_ROCKETD1_REL = 0x00002668
MKT_ROCKETD1_IMAGE_REL = 0x00049700

# Exact retail Rev. 2 ROCKET_P record, verified against donor bytes.
MKT_ROCKET_P_RECORD_ROM = 0x000BC3AC
MKT_ROCKET_P_COUNT = 16
MKT_ROCKET_P = (
    0x07C0, 0xF7BD, 0xF7A7, 0xBDEF,
    0x9CE7, 0x8C63, 0x5AD7, 0x318D,
    0xF5C1, 0xF381, 0xF1C1, 0xD801,
    0x9801, 0x7001, 0x6001, 0x4001,
)

# Token palette call and proof-only helper interval, inherited from v86 design.
TOKEN_PALETTE_CALL_ROM = 0x000315C8  # VA 0x800309C8
STOCK_PALETTE_JAL = 0x0C00714A      # jal 0x8001C528
TOKEN_SELECTOR_STORE_ROM = 0x000315E8
TOKEN_INSERT_CALL_ROM = 0x000316C8

PROOF_ROM = 0x0009AE10
PROOF_VA = 0x8009A210
PALETTE_HELPER_VA = PROOF_VA
INSERT_WRAP_VA = PROOF_VA + 0x24
CHILD_ROM = 0x0009AE90
PARENT_CALL_ROM = 0x0004BC40
STOCK_PARENT_JAL = 0x0C00C130      # jal 0x800304C0
TOKEN_RETURN_VA = 0x80030AD0

REG = {
    'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,
    't0':8,'t1':9,'t2':10,'t3':11,'t4':12,'t5':13,'t6':14,'t7':15,
    's0':16,'s1':17,'s2':18,'s3':19,'s4':20,'s5':21,'s6':22,'s7':23,
    't8':24,'t9':25,'k0':26,'k1':27,'gp':28,'sp':29,'fp':30,'ra':31,
}

def be32(b, o):
    return int.from_bytes(b[o:o+4], 'big')

def put32(b, o, v):
    b[o:o+4] = int(v & 0xffffffff).to_bytes(4, 'big')

def s16(v):
    return v - 0x10000 if v & 0x8000 else v

def align4(v):
    return (v + 3) & ~3

def I(op, rs, rt, imm):
    return ((op & 0x3f) << 26) | (REG[rs] << 21) | (REG[rt] << 16) | (imm & 0xffff)

def R(rs, rt, rd, sh, fn):
    return (REG[rs] << 21) | (REG[rt] << 16) | (REG[rd] << 11) | ((sh & 31) << 6) | (fn & 63)

def J(op, va):
    return ((op & 0x3f) << 26) | ((va >> 2) & 0x03ffffff)

def branch(op, rs, rt, pc, target):
    delta = (target - (pc + 4)) // 4
    assert target == pc + 4 + delta * 4
    assert -0x8000 <= delta <= 0x7fff
    return I(op, rs, rt, delta)

def words(xs):
    return b''.join(int(x & 0xffffffff).to_bytes(4, 'big') for x in xs)

def rol32(v, s):
    s &= 31
    return v & 0xffffffff if not s else ((v << s) | (v >> (32 - s))) & 0xffffffff

def update_crc(rom):
    seed = 0xF8CA4DDC
    t1 = t2 = t3 = t4 = t5 = t6 = seed
    for off in range(0x1000, 0x101000, 4):
        value = be32(rom, off)
        total = (t6 + value) & 0xffffffff
        if total < t6:
            t4 = (t4 + 1) & 0xffffffff
        t6 = total
        t3 ^= value
        r = rol32(value, value & 31)
        t5 = (t5 + r) & 0xffffffff
        t2 ^= r if t2 > value else (t6 ^ value)
        t1 = (t1 + (t5 ^ value)) & 0xffffffff
    c1 = (t6 ^ t4 ^ t3) & 0xffffffff
    c2 = (t5 ^ t2 ^ t1) & 0xffffffff
    put32(rom, 0x10, c1)
    put32(rom, 0x14, c2)
    return c1, c2

def dec16(src):
    assert src[0] == 16
    n = int.from_bytes(src[:4], 'big') & 0x00ffffff
    p = 4
    out = bytearray()
    while len(out) < n:
        ch = src[p]; p += 1
        if ch & 0x80:
            out += bytes((0,)) * ((ch & 0x7f) + 7)
            continue
        hi = ch >> 4
        pix = ch & 0x0f
        if hi == 0:
            cnt = src[p]; p += 1
            out += bytes((pix,)) * cnt
        elif hi <= 6:
            out += bytes((pix,)) * hi
        else:
            cnt = pix + 3
            while cnt:
                q = src[p]; p += 1
                out.append(q >> 4); cnt -= 1
                if cnt:
                    out.append(q & 0x0f); cnt -= 1
    assert len(out) == n
    return bytes(out), p

def rgba5551_to_target(v):
    r = (v >> 11) & 31
    g = (v >> 6) & 31
    b = (v >> 1) & 31
    a = v & 1
    if not a:
        return 0
    return 0x8000 | (b << 10) | (g << 5) | r

def main():
    ap = argparse.ArgumentParser(description='Build MKMSZR Sektor missile pre-published-texture + dedicated ROCKET_P v89 from exact v75.')
    ap.add_argument('baseline', type=Path, help='exact v75 missile ROM')
    ap.add_argument('mkt', type=Path, help='Mortal Kombat Trilogy USA Rev. 2 ROM')
    ap.add_argument('-o', '--output', type=Path,
                    default=Path('MKMSZR_sektor-missile-preupload_common-proof_v89.z64'))
    a = ap.parse_args()

    base = a.baseline.read_bytes()
    assert len(base) == ROM_SIZE
    actual = hashlib.sha256(base).hexdigest()
    assert actual == V75_SHA256, f'wrong v75 baseline: {actual}'

    mkt = a.mkt.read_bytes()
    assert len(mkt) == MKT_SIZE
    donor_sha = hashlib.sha256(mkt).hexdigest()
    assert donor_sha == MKT_SHA256, f'wrong MKT donor: {donor_sha}'

    rom = bytearray(base)

    # ---- Exact v75 / route guards ---------------------------------------------
    assert be32(rom, 0xA5664) == RR
    assert be32(rom, 0xA5668) == RR + EXPECTED_V75_FILE87_END
    assert be32(rom, RR + 0xDB8) == 0x0000000B
    assert be32(rom, RR + 0xDBC) == 0x00034A58
    assert be32(rom, RR + 0xDC0) == 0
    assert be32(rom, RR + STRAIGHT_NEXT_FRAME) == 0x00034A58
    assert be32(rom, RR + 0xFD0) == 0x00000D90
    assert [be32(rom, RR + 0xD90 + 4*i) for i in range(4)] == [ROCKET_SHAPE_OFF, ROCKET_SHAPE_OFF, 1, 0xD90]

    assert be32(rom, RR + ROCKET_SHAPE_OFF) == ROCKET_DESC_OFF
    assert be32(rom, RR + ROCKET_SHAPE_OFF + 4) == 0
    assert be32(rom, RR + ROCKET_DESC_OFF) == ROCKET_OLD_IMAGE_OFF
    assert rom[RR + ROCKET_DESC_OFF + 4:RR + ROCKET_DESC_OFF + 12] == bytes.fromhex('00270009001A0003')
    assert rom[RR + ROCKET_OLD_IMAGE_OFF:RR + ROCKET_OLD_IMAGE_OFF + 4] == b'\x05\x00\x00\x00'

    assert be32(rom, 0x315A8) == 0x3C04800B
    assert be32(rom, 0x315AC) == 0x24841A24
    assert be32(rom, TOKEN_PALETTE_CALL_ROM) == STOCK_PALETTE_JAL
    assert be32(rom, TOKEN_PALETTE_CALL_ROM + 4) == 0xACE206E4
    assert be32(rom, TOKEN_SELECTOR_STORE_ROM) == 0xA602009E
    assert be32(rom, TOKEN_INSERT_CALL_ROM) == 0x0C009194
    assert be32(rom, TOKEN_INSERT_CALL_ROM + 4) == 0xA48200AE

    assert be32(rom, 0x4BBF0) == 0x24050005
    assert be32(rom, 0x4BBFC) == 0x24060026
    assert be32(rom, 0x4BC00) == 0x0C00C482
    assert be32(rom, 0x4C484) == 0x080268A4
    assert be32(rom, 0x4BA68) == 0x0C00A0C3 and be32(rom, 0x4BA84) == 0x0C00A0C3
    child_before = bytes(rom[CHILD_ROM:0x9AF20])

    expected_parent = [
      0x27BDFFE0,0xAFBF001C,0xAFA40018,0x3C08802F,0x8D08CE20,0x8D0906E4,
      0xAFA90014,0xA480009E,0x948A008C,0x314A0010,0x8C8B002C,0x11400004,
      0x00000000,0x00000000,0x08026895,0x00000000,0x00000000,0xAC8B002C,
      0x8C8C0098,0x258C0D90,0xAD0C06E4,0x0C00C130,0x00000000,0x3C08802F,
      0x8D08CE20,0x8FA90014,0xAD0906E4,0x8FA40018,0x8FBF001C,0x27BD0020,
      0x03E00008,0x00000000,
    ]
    assert [be32(rom, PROOF_ROM + 4*i) for i in range(32)] == expected_parent
    assert be32(rom, PARENT_CALL_ROM) == J(3, PROOF_VA)
    assert be32(rom, PARENT_CALL_ROM + 4) == 0xAC4406E0

    # ---- Exact MKT ROCKETD1 + ROCKET_P extraction -----------------------------
    so = MKT_ROBOT_BASE + MKT_ROCKETD1_REL
    assert be32(mkt, so) == MKT_ROCKETD1_REL + 8
    assert be32(mkt, so + 4) == 0
    sub = so + 8
    image_rel = be32(mkt, sub)
    packed = be32(mkt, sub + 4)
    anchor = be32(mkt, sub + 8)
    h = (packed >> 16) & 0xffff
    w = packed & 0xffff
    x = s16((anchor >> 16) & 0xffff)
    y = s16(anchor & 0xffff)
    assert image_rel == MKT_ROCKETD1_IMAGE_REL
    assert (w, h, x, y) == (39, 9, 26, 3)
    donor_raw, donor_stream_bytes = dec16(mkt[MKT_ROBOT_BASE + image_rel:])
    assert donor_stream_bytes == 130
    assert len(donor_raw) == h * align4(w) == 360
    assert max(donor_raw) == 15 and set(donor_raw) == set(range(16))

    assert be32(mkt, MKT_ROCKET_P_RECORD_ROM) == MKT_ROCKET_P_COUNT
    exact_palette = tuple(int.from_bytes(mkt[MKT_ROCKET_P_RECORD_ROM+4+2*i:MKT_ROCKET_P_RECORD_ROM+6+2*i], 'big') for i in range(16))
    assert exact_palette == MKT_ROCKET_P

    # ---- Dedicated raw rocket asset + palette source ---------------------------
    old_end = EXPECTED_V75_FILE87_END
    raw_image_off = align4(old_end)
    raw_image = b'\x00\x00\x00\x00' + donor_raw  # native raw/type-0 wrapper
    palette_record_off = align4(raw_image_off + len(raw_image))
    palette_source_off = palette_record_off + 4

    target16 = [rgba5551_to_target(v) for v in exact_palette]
    assert target16[0] == 0
    assert all(v & 0x8000 for v in target16[1:])
    # Native fighter palette records are 64 entries. The rocket uses only 0..15;
    # keep the remaining 48 entries transparent for a self-contained source.
    target64 = target16 + [0] * 48
    palette_record = (64).to_bytes(4, 'big') + b''.join(v.to_bytes(2, 'big') for v in target64)
    new_end = align4(palette_record_off + len(palette_record))

    assert set(rom[RR + old_end:RR + new_end]) == {0xFF}
    rom[RR + raw_image_off:RR + raw_image_off + len(raw_image)] = raw_image
    rom[RR + palette_record_off:RR + palette_record_off + len(palette_record)] = palette_record
    put32(rom, RR + ROCKET_DESC_OFF, raw_image_off)
    put32(rom, 0xA5668, RR + new_end)

    # ---- Guarded straight-token dedicated-palette helper -----------------------
    # Same v87 ownership proof: at entry stock a0 still names Ice palette colors.
    # Detect the ordinary straight projectile by the post-token cursor relation,
    # substitute the dedicated ROCKET_P source, and tail-call native 0x8001C528.
    helper = []
    pc = PALETTE_HELPER_VA
    helper.append(I(0x23, 'a3', 't0', 0x06E4)); pc += 4
    helper.append(I(0x09, 't0', 't0', -STRAIGHT_NEXT_CURSOR)); pc += 4
    helper.append(I(0x23, 's0', 't1', 0x0098)); pc += 4
    call_palette_va = PALETTE_HELPER_VA + 7*4
    helper.append(branch(0x05, 't0', 't1', pc, call_palette_va)); pc += 4
    hi = (palette_source_off >> 16) & 0xffff
    lo = palette_source_off & 0xffff
    helper.append(I(0x0F, 'zero', 'at', hi)); pc += 4
    helper.append(I(0x0D, 'at', 'at', lo)); pc += 4
    helper.append(R('t1', 'at', 'a0', 0, 0x21)); pc += 4
    helper.append(J(0x02, 0x8001C528)); pc += 4
    helper.append(0); pc += 4
    assert len(helper) == 9 and pc == INSERT_WRAP_VA

    # v89 pre-publication texture preparation. The v80-proven constructor now
    # builds ROCKETD1, and the next ordinary-straight parent entry is also ROCKETD1.
    # Token +0x9C/+0x9E are finalized by this point. Before actor-list publication:
    #   1) synchronously load the raw/type-0 rocket into that finalized texture slot
    #      through native 0x8001BF70 (which internally queues + drains);
    #   2) rerun native frame setup on actor+0x74 so active slot/palette metadata is
    #      coherent with the newly loaded slot;
    #   3) tail-jump to stock 0x80024650 with the exact token return address.
    # ROCKETD1 is statically fixed at 39x9 with align4(width)=40 in this proof.
    insert = [
      I(0x23,'s0','t1',0x007C),          # render record
      I(0x23,'t1','a0',0x0000),          # raw/type-0 wrapper pointer
      I(0x09,'a0','a0',0x0004),          # decoded bytes = wrapper + 4
      I(0x09,'zero','a1',0x0028),        # aligned width 40
      I(0x09,'zero','a2',0x0009),        # height 9
      I(0x25,'s0','a3',0x009C),          # finalized texture slot (0x24)
      J(0x03,0x8001BF70),                # synchronous native slot load + drain
      0,
      R('s0','zero','a0',0,0x21),
      I(0x23,'s0','a1',0x0074),          # current ROCKETD1 entry
      J(0x03,0x8001BDA0),                # refresh active slot/palette/frame fields
      0,
      R('s0','zero','a0',0,0x21),
      I(0x0F,'zero','a1',0x8011),
      I(0x09,'a1','a1',0x1C98),
      I(0x0F,'zero','ra',0x8003),
      I(0x0D,'ra','ra',0x0AD0),
      J(0x02,0x80024650),
      0,
    ]
    assert len(insert) == 19
    payload = words(helper + insert)
    assert len(payload) == 0x70
    assert PROOF_ROM + len(payload) <= CHILD_ROM
    rom[PROOF_ROM:CHILD_ROM] = payload + bytes(CHILD_ROM - PROOF_ROM - len(payload))

    # Proven frame-schedule edits: v80 established the live constructor operand;
    # the normal straight parent consumes +0xDC4 next. Keep both on ROCKETD1 so the
    # stock parent advance cannot restore an Ice descriptor after publication.
    assert be32(rom, RR + 0xDBC) == 0x00034A58
    assert be32(rom, RR + STRAIGHT_NEXT_FRAME) == 0x00034A58
    put32(rom, RR + 0xDBC, ROCKET_SHAPE_OFF)
    put32(rom, RR + STRAIGHT_NEXT_FRAME, ROCKET_SHAPE_OFF)

    put32(rom, TOKEN_PALETTE_CALL_ROM, J(0x03, PALETTE_HELPER_VA))
    put32(rom, TOKEN_INSERT_CALL_ROM, J(0x03, INSERT_WRAP_VA))
    # Ordinary straight mode skips this site. Restore stock behavior rather than
    # letting nonzero mode enter the proof interval that is now owned by v89.
    put32(rom, PARENT_CALL_ROM, STOCK_PARENT_JAL)

    # ---- Post-build guards ------------------------------------------------------
    assert be32(rom, RR + ROCKET_DESC_OFF) == raw_image_off
    assert rom[RR + raw_image_off:RR + raw_image_off + 4] == b'\0\0\0\0'
    assert rom[RR + raw_image_off + 4:RR + raw_image_off + 4 + 360] == donor_raw
    assert be32(rom, RR + palette_record_off) == 64
    assert rom[RR + palette_source_off:RR + palette_source_off + 32] == b''.join(v.to_bytes(2,'big') for v in target16)
    assert be32(rom, 0xA5668) == RR + new_end

    assert be32(rom, RR + 0xDBC) == ROCKET_SHAPE_OFF                  # v80-proven rocket constructor
    assert be32(rom, RR + STRAIGHT_NEXT_FRAME) == ROCKET_SHAPE_OFF      # parent next frame remains rocket
    assert be32(rom, TOKEN_SELECTOR_STORE_ROM) == 0xA602009E    # stock dynamic selector store
    assert be32(rom, TOKEN_INSERT_CALL_ROM) == J(0x03, INSERT_WRAP_VA) # synchronous pre-publication slot prep
    assert bytes(rom[CHILD_ROM:0x9AF20]) == child_before        # v75 child/flight unchanged
    assert be32(rom, 0x4BBF0) == 0x24050005 and be32(rom, 0x4BBFC) == 0x24060026
    assert be32(rom, 0x4BC00) == 0x0C00C482 and be32(rom, 0x4C484) == 0x080268A4
    assert be32(rom, PARENT_CALL_ROM) == STOCK_PARENT_JAL and be32(rom, PARENT_CALL_ROM+4) == 0xAC4406E0
    assert be32(rom, 0x4BA68) == 0x0C00A0C3 and be32(rom, 0x4BA84) == 0x0C00A0C3

    c1, c2 = update_crc(rom)
    out = bytes(rom)
    a.output.write_bytes(out)

    print('OUTPUT', a.output)
    print('SHA256', hashlib.sha256(out).hexdigest())
    print('CRC1/CRC2', f'{c1:08X} / {c2:08X}')
    print('TEST_INPUT', 'Forward, Forward + Low Punch')
    print('MKT_ROCKET_P_RECORD', f'0x{MKT_ROCKET_P_RECORD_ROM:06X}', 'count', MKT_ROCKET_P_COUNT)
    print('ROCKET_RAW_IMAGE', f'file87 +0x{raw_image_off:X}', '39x9 stride40 donor indices 0..15')
    print('ROCKET_PALETTE_RECORD', f'file87 +0x{palette_record_off:X}', 'source', f'+0x{palette_source_off:X}')
    print('FILE87_END', f'0x{old_end:X} -> 0x{new_end:X}', 'growth', f'0x{new_end-old_end:X}')
    print('CHANGE', 'v87 exact rocket/palette + v80 constructor/next-frame rocket + synchronous 0x8001BF70 texture-slot preparation before publication')
    print('UNCHANGED', 'helper pair/tint; (+5,+38); child ownership; v75 flight/collision/cleanup')
    print('NONZERO_MODE', 'v75 proof wrapper restored to stock 0x800304C0 call; ordinary straight branch is the test scope')
    print('LIFECYCLE_LIMIT', '0x8001BF70 advances texture storage and palette/texture release remains unproven; test one neutral straight shot only')

if __name__ == '__main__':
    main()
