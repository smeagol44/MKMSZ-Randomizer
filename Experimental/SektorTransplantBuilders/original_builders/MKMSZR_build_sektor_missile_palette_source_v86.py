#!/usr/bin/env python3
"""MKMSZR Sektor straight-missile v86 palette-source-only proof.

Baseline: exact Runtime-confirmed v75.

Work reconciliation through v84 separated the normal straight-shot frame schedule
from projectile palette ownership.  On ordinary mode zero, the stock token-0x0B
handler acquires the Ice palette from 0x800B1A24 and stores (handle - 0x80) in
the projectile actor's +0x9E selector.  The transplanted Sektor player palette,
including the mapped ROCKET_P indices, lives in file-0x87 at +0x4584C and is
normally acquired dynamically through 0x8001C528.

v86 changes ONLY that palette-source choice for the guarded straight-shot token:
  * the token still constructs the stock Ice projectile descriptor;
  * frame/cursor timing is untouched;
  * stock 0x8001C528 acquisition/refcount semantics are preserved;
  * the returned dynamic selector is still stored by stock code as handle-0x80;
  * insertion, helper actors/tint, placement, child handoff, v75 velocity/cadence,
    collision and cleanup are untouched.

The tiny guard helper reuses the v75 proof-only nonzero-mode wrapper interval.
To avoid changing that wrapper's semantics, a compact equivalent is relocated
within the same [0x9AE10,0x9AE90) proof interval and its existing call is retargeted.
No new ROM/RDRAM allocation is claimed.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V75_SHA256 = "e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
ROM_SIZE = 0x1000000

RR = 0xF40000                    # relocated file 0x87 in the v75 proof
TYPE4_TABLE_ROM = 0xB1FD0        # VA 0x800B13D0 -> ROM mapping for this global segment
TYPE4_INDEX = 4
SEKTOR_PALETTE_RECORD = 0x45848
SEKTOR_PALETTE_SOURCE = 0x4584C
STRAIGHT_NEXT_CURSOR = 0x0DC0    # cursor after live token +0xDB8/+0xDBC is consumed

TOKEN_PALETTE_CALL_ROM = 0x315C8 # VA 0x800309C8
STOCK_PALETTE_JAL = 0x0C00714A   # jal 0x8001C528
TOKEN_SELECTOR_STORE_ROM = 0x315E8
TOKEN_INSERT_CALL_ROM = 0x316C8

PROOF_ROM = 0x9AE10
PROOF_VA = 0x8009A210
PALETTE_HELPER_ROM = PROOF_ROM
PALETTE_HELPER_VA = PROOF_VA
RELOC_PARENT_ROM = PROOF_ROM + 0x24
RELOC_PARENT_VA = PROOF_VA + 0x24
CHILD_ROM = 0x9AE90

PARENT_CALL_ROM = 0x4BC40
ORIG_PARENT_VA = 0x8009A210

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


def main():
    ap = argparse.ArgumentParser(description='Build MKMSZR Sektor missile palette-source-only v86 from exact v75.')
    ap.add_argument('baseline', type=Path, help='MKMSZR_sektor-missile-velocity_common-proof_v75.z64')
    ap.add_argument('-o', '--output', type=Path,
                    default=Path('MKMSZR_sektor-missile-palette-source_common-proof_v86.z64'))
    a = ap.parse_args()

    base = a.baseline.read_bytes()
    assert len(base) == ROM_SIZE, f'wrong ROM size: {len(base):#x}'
    actual = hashlib.sha256(base).hexdigest()
    assert actual == V75_SHA256, f'wrong v75 baseline: {actual}'
    rom = bytearray(base)

    # ---- Exact v75 route guards -------------------------------------------------
    # Live ordinary straight token and its next cursor.
    assert be32(rom, RR + 0xDB8) == 0x0000000B
    assert be32(rom, RR + 0xDBC) == 0x00034A58
    assert be32(rom, RR + 0xDC0) == 0x00000000

    # Type-4 player palette provenance: table entry -> +0x45848 count record,
    # with colors beginning at +0x4584C.
    assert be32(rom, TYPE4_TABLE_ROM + TYPE4_INDEX * 4) == SEKTOR_PALETTE_RECORD
    assert be32(rom, RR + SEKTOR_PALETTE_RECORD) == 0x00000040
    expected_lower32 = bytes.fromhex(
        '0000defec63cb5baa95898f790b2843a88568014842f842d842b800880048003'
        'f7bdef7be739d6b5ce73bdefb5adad6ba52998c690848c638842842180008000'
    )
    assert len(expected_lower32) == 64
    assert rom[RR + SEKTOR_PALETTE_SOURCE:RR + SEKTOR_PALETTE_SOURCE + 64] == expected_lower32

    # Stock token acquisition path and dynamic selector store remain structurally stock.
    assert be32(rom, 0x315A8) == 0x3C04800B          # lui a0,0x800B
    assert be32(rom, 0x315AC) == 0x24841A24          # addiu a0,a0,0x1A24
    assert be32(rom, TOKEN_PALETTE_CALL_ROM) == STOCK_PALETTE_JAL
    assert be32(rom, TOKEN_PALETTE_CALL_ROM + 4) == 0xACE206E4  # delay: commit advanced cursor
    assert be32(rom, TOKEN_SELECTOR_STORE_ROM) == 0xA602009E    # sh v0,0x9E(s0), v0=handle-0x80
    assert be32(rom, TOKEN_INSERT_CALL_ROM) == 0x0C009194       # stock 0x80024650 insertion
    assert be32(rom, TOKEN_INSERT_CALL_ROM + 4) == 0xA48200AE

    # v75 constructor, placement, parent scheduling, child and helper controls.
    assert be32(rom, RR + 0xDBC) == 0x00034A58                  # stock Ice constructor retained
    assert be32(rom, 0x4BBF0) == 0x24050005                     # +5
    assert be32(rom, 0x4BBFC) == 0x24060026                     # +38
    assert be32(rom, 0x4BC00) == 0x0C00C482                     # 0x80031208
    assert be32(rom, 0x4C484) == 0x080268A4                     # v75 child
    assert be32(rom, 0x4BA68) == 0x0C00A0C3 and be32(rom, 0x4BA84) == 0x0C00A0C3
    child_before = bytes(rom[CHILD_ROM:0x9AF20])

    # Guard the exact v75 proof wrapper that shares this proof-only interval.
    expected_parent = [
      0x27BDFFE0,0xAFBF001C,0xAFA40018,0x3C08802F,0x8D08CE20,0x8D0906E4,
      0xAFA90014,0xA480009E,0x948A008C,0x314A0010,0x8C8B002C,0x11400004,
      0x00000000,0x00000000,0x08026895,0x00000000,0x00000000,0xAC8B002C,
      0x8C8C0098,0x258C0D90,0xAD0C06E4,0x0C00C130,0x00000000,0x3C08802F,
      0x8D08CE20,0x8FA90014,0xAD0906E4,0x8FA40018,0x8FBF001C,0x27BD0020,
      0x03E00008,0x00000000,
    ]
    assert [be32(rom, PROOF_ROM + 4*i) for i in range(32)] == expected_parent
    assert be32(rom, PARENT_CALL_ROM) == J(3, ORIG_PARENT_VA)

    # ---- v86 guarded palette-source helper --------------------------------------
    # At the token call, original code has already loaded a0=0x800B1A24.
    # The JAL delay slot advances controller +0x6E4.  For this exact straight
    # token that new cursor is actor/resource-base +0xDC0.  Only then override
    # a0 with actor resource base +0x4584C (resident Sektor colors).
    # All other token-0x0B users tail-call 0x8001C528 with the untouched stock a0.
    helper = []
    pc = PALETTE_HELPER_VA
    helper.append(I(0x23, 'a3', 't0', 0x06E4)); pc += 4       # lw t0,+6E4(a3)
    helper.append(I(0x09, 't0', 't0', -STRAIGHT_NEXT_CURSOR)); pc += 4
    helper.append(I(0x23, 's0', 't1', 0x0098)); pc += 4       # projectile resource base
    call_palette_va = PALETTE_HELPER_VA + 7*4
    helper.append(branch(0x05, 't0', 't1', pc, call_palette_va)); pc += 4  # bne -> stock a0
    helper.append(I(0x0F, 'zero', 'at', 0x0004)); pc += 4     # delay: high +0x40000
    helper.append(I(0x09, 'at', 'at', 0x584C)); pc += 4       # at=+0x4584C
    helper.append(R('t1', 'at', 'a0', 0, 0x21)); pc += 4      # addu a0,t1,at
    helper.append(J(0x02, 0x8001C528)); pc += 4               # tail-call; preserve caller RA
    helper.append(0); pc += 4
    assert len(helper) == 9 and pc == RELOC_PARENT_VA

    # Compact semantic equivalent of the v75 nonzero-mode parent wrapper.
    # The removed X-correction instructions were already NOP controls in v75.
    # This relocation prevents the v86 helper from changing that wrapper's behavior.
    parent = [
      I(0x09,'sp','sp',-0x10),
      I(0x2B,'sp','ra',0x0C),
      I(0x2B,'sp','a0',0x08),
      I(0x0F,'zero','t0',0x802F),
      I(0x23,'t0','t0',0xCE20),
      I(0x23,'t0','t1',0x06E4),
      I(0x2B,'sp','t1',0x04),
      I(0x29,'a0','zero',0x009E),
      I(0x23,'a0','t2',0x0098),
      I(0x09,'t2','t2',0x0D90),
      I(0x2B,'t0','t2',0x06E4),
      J(0x03,0x800304C0),
      0,
      I(0x0F,'zero','t0',0x802F),
      I(0x23,'t0','t0',0xCE20),
      I(0x23,'sp','t1',0x04),
      I(0x2B,'t0','t1',0x06E4),
      I(0x23,'sp','a0',0x08),
      I(0x23,'sp','ra',0x0C),
      I(0x09,'sp','sp',0x10),
      R('ra','zero','zero',0,0x08),
      0,
    ]
    assert len(parent) == 22
    payload = words(helper + parent + [0])
    assert len(payload) == 0x80
    rom[PROOF_ROM:CHILD_ROM] = payload

    # Retarget only the token palette-loader call and relocate the pre-existing
    # proof wrapper to the compact equivalent above.
    put32(rom, TOKEN_PALETTE_CALL_ROM, J(0x03, PALETTE_HELPER_VA))
    put32(rom, PARENT_CALL_ROM, J(0x03, RELOC_PARENT_VA))

    # ---- Post-patch controls -----------------------------------------------------
    assert be32(rom, RR + 0xDBC) == 0x00034A58
    assert be32(rom, TOKEN_SELECTOR_STORE_ROM) == 0xA602009E
    assert be32(rom, TOKEN_INSERT_CALL_ROM) == 0x0C009194
    assert bytes(rom[CHILD_ROM:0x9AF20]) == child_before
    assert be32(rom, 0x4BBF0) == 0x24050005 and be32(rom, 0x4BBFC) == 0x24060026
    assert be32(rom, 0x4BC00) == 0x0C00C482 and be32(rom, 0x4C484) == 0x080268A4
    assert be32(rom, 0x4BA68) == 0x0C00A0C3 and be32(rom, 0x4BA84) == 0x0C00A0C3

    c1, c2 = update_crc(rom)
    out = bytes(rom)
    a.output.write_bytes(out)

    print('OUTPUT', a.output)
    print('SHA256', hashlib.sha256(out).hexdigest())
    print('CRC1/CRC2', f'{c1:08X} / {c2:08X}')
    print('TEST_INPUT', 'Forward, Forward + Low Punch')
    print('V86_SCOPE', 'guarded straight-token palette source only: Ice 0x800B1A24 -> file87 +0x4584C via stock 0x8001C528')
    print('SELECTOR_SEMANTICS', 'UNCHANGED: stock stores returned handle - 0x80 at actor +0x9E')
    print('FRAME_INSERT_HELPERS_CHILD_FLIGHT', 'UNCHANGED from v75 on ordinary straight mode zero')
    print('LIFECYCLE_LIMIT', 'palette release remains unproven; test one neutral straight shot first')

if __name__ == '__main__':
    main()
