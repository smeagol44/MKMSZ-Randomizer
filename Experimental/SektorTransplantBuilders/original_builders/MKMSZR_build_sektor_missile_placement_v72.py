#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib

V70_SHA256 = "5fe374e8702e99c6e5361b2637dcdd5bd4e743f58abbbbbdba2ad63aa283d8ae"
EXPECTED_SIZE = 0x1000000

parser = argparse.ArgumentParser(
    description="Build MKMSZR Sektor missile placement-only v72 from the exact v70 proof ROM."
)
parser.add_argument(
    "v70_rom",
    type=Path,
    help="MKMSZR_sektor-missile-flight_common-proof_v70.z64"
)
parser.add_argument(
    "-o", "--output",
    type=Path,
    default=Path("MKMSZR_sektor-missile-placement_common-proof_v72.z64")
)
args = parser.parse_args()

rom = bytearray(args.v70_rom.read_bytes())
assert len(rom) == EXPECTED_SIZE, f"wrong ROM size: {len(rom):#x}"
actual = hashlib.sha256(rom).hexdigest()
assert actual == V70_SHA256, f"wrong v70 baseline: {actual}"

def be32(b, o):
    return int.from_bytes(b[o:o+4], "big")

def put32(b, o, v):
    b[o:o+4] = int(v & 0xFFFFFFFF).to_bytes(4, "big")

REG = {
    "zero":0, "at":1, "v0":2, "v1":3, "a0":4, "a1":5, "a2":6, "a3":7,
    "t0":8, "t1":9, "t2":10, "t3":11, "t4":12, "t5":13, "t6":14, "t7":15,
    "s0":16, "s1":17, "s2":18, "s3":19, "s4":20, "s5":21, "s6":22, "s7":23,
    "t8":24, "t9":25, "k0":26, "k1":27, "gp":28, "sp":29, "fp":30, "ra":31,
}

def I(op, rs, rt, imm):
    return ((op & 0x3F) << 26) | (REG[rs] << 21) | (REG[rt] << 16) | (imm & 0xFFFF)

def J(op, va):
    return ((op & 0x3F) << 26) | ((va >> 2) & 0x03FFFFFF)

def jal(va):
    return J(0x03, va)

# Preserve the exact v70 movement / child-process code as a negative-control guard.
movement_before = bytes(rom[0x9AE90:0x9AF20])

# ---------------------------------------------------------------------------
# v72: PLACEMENT ONLY
#
# Static trace established:
#   MKT source:  adjust_xy_a5(projectile, SCX(7), SCY(45))
#   MKT N64:     SCX(7)=5, SCY(45)=38
#   MKMSZ host:  0x80031208(actor, local_x, local_y)
#
# 0x80031208 itself handles horizontal facing and converts whole local units
# into actor 8-fractional-bit world position. Do not pre-scale or pre-negate.
# ---------------------------------------------------------------------------

# Guard the original v70 stock-placement argument setup.
expected = {
    0x4BBF0: 0x00122C00,       # sll a1,s2,16
    0x4BBF4: 0x00052C03,       # sra a1,a1,16
    0x4BBF8: 0x8C440648,       # lw a0,0x648(v0)
    0x4BBFC: 0x00133400,       # sll a2,s3,16
    0x4BC00: jal(0x80031208),
    0x4BC04: 0x00063403,       # sra a2,a2,16
}
for off, value in expected.items():
    got = be32(rom, off)
    assert got == value, (hex(off), hex(got), hex(value))

# Feed the translated MKT retail local displacement directly to the native
# placement helper. a0 remains the staged projectile actor from +0x648.
put32(rom, 0x4BBF0, I(0x09, "zero", "a1", 5))    # addiu a1,zero,+5
put32(rom, 0x4BBF4, 0)                            # nop
put32(rom, 0x4BBFC, I(0x09, "zero", "a2", 38))   # addiu a2,zero,+38
put32(rom, 0x4BC04, 0)                            # nop

# v70 also performed a later proof-only +/-96px X correction after creation.
# Remove only that correction so the native (+5,+38) placement is authoritative.
assert be32(rom, 0x9AE44) == I(0x09, "t3", "t3", 0x6000)
assert be32(rom, 0x9AE50) == I(0x09, "t3", "t3", -0x6000)
put32(rom, 0x9AE44, 0)
put32(rom, 0x9AE50, 0)

# Prove this revision did not touch v70's movement callback / projectile child code.
assert bytes(rom[0x9AE90:0x9AF20]) == movement_before

# Stock helper/effect process composition remains exactly as v70.
assert be32(rom, 0x4BA68) == jal(0x8002830C)
assert be32(rom, 0x4BA84) == jal(0x8002830C)

# Input remains authentic Forward, Forward + Low Punch proof binding.
assert rom[0xB1B4C:0xB1B4E] == (9).to_bytes(2, "big")
assert rom[0xB1B58:0xB1B5A] == (8).to_bytes(2, "big")

# CIC-NUS-6102 CRC1/CRC2.
def rol32(v, s):
    s &= 31
    if s == 0:
        return v & 0xFFFFFFFF
    return ((v << s) | (v >> (32 - s))) & 0xFFFFFFFF

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

args.output.write_bytes(rom)

print("OUTPUT", args.output)
print("SHA256", hashlib.sha256(rom).hexdigest())
print("CRC1/CRC2", f"{crc1:08X} / {crc2:08X}")
print("TEST_INPUT", "Forward, Forward + Low Punch")
print("V72_SCOPE", "placement only: native local (+5,+38), v70 +/-96px correction removed")
print("V70_MOVEMENT_CALLBACK", "UNCHANGED")
