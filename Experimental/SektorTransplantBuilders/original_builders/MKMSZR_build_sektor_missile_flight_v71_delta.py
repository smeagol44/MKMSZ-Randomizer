#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib

V70_SHA256 = "5fe374e8702e99c6e5361b2637dcdd5bd4e743f58abbbbbdba2ad63aa283d8ae"
EXPECTED_SIZE = 0x1000000

parser = argparse.ArgumentParser(
    description="Build MKMSZR Sektor missile-flight v71 as a guarded delta from the exact v70 proof ROM."
)
parser.add_argument("v70_rom", type=Path, help="MKMSZR_sektor-missile-flight_common-proof_v70.z64")
parser.add_argument(
    "-o", "--output", type=Path,
    default=Path("MKMSZR_sektor-missile-flight_common-proof_v71.z64")
)
args = parser.parse_args()

rom = bytearray(args.v70_rom.read_bytes())
assert len(rom) == EXPECTED_SIZE, hex(len(rom))
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

def R(rs, rt, rd, sh, fn):
    return (REG[rs] << 21) | (REG[rt] << 16) | (REG[rd] << 11) | ((sh & 31) << 6) | (fn & 63)

def J(op, va):
    return ((op & 0x3F) << 26) | ((va >> 2) & 0x03FFFFFF)

def jal(va):
    return J(0x03, va)

def branch(op, rs, rt, pc, target):
    delta = (target - (pc + 4)) // 4
    assert target == pc + 4 + delta * 4
    assert -0x8000 <= delta <= 0x7FFF
    return I(op, rs, rt, delta)

def words(seq):
    return b"".join(int(v & 0xFFFFFFFF).to_bytes(4, "big") for v in seq)

# ---------------------------------------------------------------------------
# v71 correction 1: use MKMSZ's actual facing-relative placement seam.
# v70 let stock Ice choose its distant offset, then nudged actor X afterward.
# v71 feeds the donor-retail (+5,+38) offset directly into 0x80031208.
# ---------------------------------------------------------------------------
expected = {
    0x4BBF0: 0x00122C00,  # sll a1,s2,16
    0x4BBF4: 0x00052C03,  # sra a1,a1,16
    0x4BBF8: 0x8C440648,  # lw a0,0x648(v0)
    0x4BBFC: 0x00133400,  # sll a2,s3,16
    0x4BC00: jal(0x80031208),
    0x4BC04: 0x00063403,  # sra a2,a2,16
}
for off, value in expected.items():
    assert be32(rom, off) == value, (hex(off), hex(be32(rom, off)), hex(value))

put32(rom, 0x4BBF0, I(0x09, "zero", "a1", 5))
put32(rom, 0x4BBF4, 0)
put32(rom, 0x4BBFC, I(0x09, "zero", "a2", 38))
put32(rom, 0x4BC04, 0)

# Neutralize v70's post-creation +/-0x6000 actor-X correction.
assert be32(rom, 0x9AE44) == I(0x09, "t3", "t3", 0x6000)
assert be32(rom, 0x9AE50) == I(0x09, "t3", "t3", -0x6000)
put32(rom, 0x9AE44, 0)
put32(rom, 0x9AE50, 0)

# ---------------------------------------------------------------------------
# v71 correction 2: donor straight-rocket motion through MKMSZ's own
# facing-aware projectile velocity helper 0x8004CC14.
#
# Normal launch: 0x33333 (~3.2 px/tick in the donor retail space)
# Per tick:      abs(v + (v >> 4))
# Cap:           0xB3333 (~11.2 px/tick)
# ---------------------------------------------------------------------------
CHILD_ROM = 0x9AE90
CALLBACK_ROM = 0x9AED0
CALLBACK_VA = 0x8009A2D0

assert be32(rom, 0x9AE90) == 0x3C08802F
assert be32(rom, 0x9AEB8) == 0x3C08802F
assert be32(rom, 0x9AF0C) == 0x03E00008

child = [
    I(0x0F, "zero", "t0", 0x802F),
    I(0x23, "t0", "t0", 0xCE20),
    I(0x23, "t0", "a0", 0x06E0),

    I(0x0F, "zero", "a1", 0x0003),
    I(0x0D, "a1", "a1", 0x3333),
    I(0x09, "zero", "a2", 3),
    jal(0x8004CC14),
    0,

    # Reacquire current process after native helper call.
    I(0x0F, "zero", "t0", 0x802F),
    I(0x23, "t0", "t0", 0xCE20),

    I(0x0F, "zero", "t1", 0x800A),
    I(0x09, "t1", "t1", -0x5D30),  # 0x8009A2D0
    I(0x2B, "t0", "t1", 0x070C),

    I(0x09, "zero", "a1", 0x0013),  # retain v70 stock collision proof
    J(0x02, 0x8004B9C4),
    0,
]
assert len(child) == 16
assert CHILD_ROM + len(words(child)) == CALLBACK_ROM

acc = []
pc = CALLBACK_VA
def emit(w):
    global pc
    acc.append(w)
    pc += 4

emit(I(0x0F, "zero", "t0", 0x802F))
emit(I(0x23, "t0", "t0", 0xCE20))
emit(I(0x23, "t0", "a0", 0x06E0))
emit(I(0x23, "a0", "t2", 0x0014))       # signed current X velocity
emit(R("zero", "t2", "t3", 4, 0x03))    # old v >> 4
emit(R("t2", "t3", "t2", 0, 0x21))      # v + (v >> 4)

positive = CALLBACK_VA + 9 * 4
emit(branch(0x01, "t2", "zero", pc, positive))  # bgez t2,positive
emit(0)
emit(R("zero", "t2", "t2", 0, 0x23))    # abs()

emit(I(0x0F, "zero", "t4", 0x000B))
emit(I(0x0D, "t4", "t4", 0x3333))       # cap 0xB3333
emit(R("t4", "t2", "t5", 0, 0x2A))      # cap < speed?

nocap = CALLBACK_VA + 15 * 4
emit(branch(0x04, "t5", "zero", pc, nocap))
emit(0)
emit(R("t4", "zero", "t2", 0, 0x21))

emit(R("t2", "zero", "a1", 0, 0x21))
emit(I(0x0C, "t3", "a2", 0xFFFF))        # donor set_proj_vel anirate argument
emit(J(0x02, 0x8004CC14))                # tail-call native velocity helper
emit(0)

assert len(acc) == 19
assert CALLBACK_ROM + len(words(acc)) == 0x9AF1C

rom[CHILD_ROM:0x9AF20] = bytes(0x9AF20 - CHILD_ROM)
rom[CHILD_ROM:CHILD_ROM + len(words(child))] = words(child)
rom[CALLBACK_ROM:CALLBACK_ROM + len(words(acc))] = words(acc)

# Static scope checks.
assert be32(rom, 0x4BBF0) == 0x24050005
assert be32(rom, 0x4BBFC) == 0x24060026
assert be32(rom, 0x4BC00) == jal(0x80031208)
assert be32(rom, 0x9AE44) == 0 and be32(rom, 0x9AE50) == 0
assert be32(rom, CHILD_ROM + 6*4) == jal(0x8004CC14)
assert be32(rom, CHILD_ROM + 14*4) == J(0x02, 0x8004B9C4)
assert be32(rom, CALLBACK_ROM + 17*4) == J(0x02, 0x8004CC14)

# CIC-NUS-6102 CRC1/CRC2.
def rol32(v, s):
    s &= 31
    return v & 0xFFFFFFFF if s == 0 else ((v << s) | (v >> (32 - s))) & 0xFFFFFFFF

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
out_sha = hashlib.sha256(rom).hexdigest()

print("OUTPUT", args.output)
print("SHA256", out_sha)
print("CRC1/CRC2", f"{crc1:08X} / {crc2:08X}")
print("TEST_INPUT", "Forward, Forward + Low Punch")
print("V71_SCOPE", "native (+5,+38) placement; 0x33333 start; +1/16 per tick; 0xB3333 cap")
