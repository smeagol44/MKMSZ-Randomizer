#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib

V72_SHA256 = "355c4bfbb9d2c0f0d21f6e8bc628defa530f79bc0f322fae3ca48bb1ce088fca"
EXPECTED_SIZE = 0x1000000

parser = argparse.ArgumentParser(
    description="Build MKMSZR Sektor missile movement-only v73 from the exact v72 proof ROM."
)
parser.add_argument(
    "v72_rom",
    type=Path,
    help="MKMSZR_sektor-missile-placement_common-proof_v72.z64"
)
parser.add_argument(
    "-o", "--output",
    type=Path,
    default=Path("MKMSZR_sektor-missile-movement_common-proof_v73.z64")
)
args = parser.parse_args()

rom = bytearray(args.v72_rom.read_bytes())
assert len(rom) == EXPECTED_SIZE, f"wrong ROM size: {len(rom):#x}"
actual = hashlib.sha256(rom).hexdigest()
assert actual == V72_SHA256, f"wrong v72 baseline: {actual}"

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

def branch(op, rs, rt, pc, target):
    delta = (target - (pc + 4)) // 4
    assert target == pc + 4 + delta * 4
    assert -0x8000 <= delta <= 0x7FFF
    return I(op, rs, rt, delta)

def words(seq):
    return b"".join(int(v & 0xFFFFFFFF).to_bytes(4, "big") for v in seq)

# ---------------------------------------------------------------------------
# v73 MOVEMENT ONLY
#
# Keep v72's Runtime-confirmed placement exactly intact:
#   0x80031208(projectile, +5, +38)
#
# Keep stock Ice helper-process composition, collision path, chest marker,
# imported rocket art, palette behavior, and F,F+LP binding unchanged.
#
# Movement semantics for the normal (opponent-not-reacting) donor branch:
#   start magnitude = 0x33333
#   each callback: magnitude = abs(v + (v >> 4))
#   cap magnitude = 0xB3333
#
# The stock MKMSZ setup helper has already initialized animation rate = 3
# before this child routine runs. v73 changes ONLY actor +0x14 (X velocity).
# It never calls 0x8004CC14 from the per-tick callback.
#
# The MKT "opponent already reacting" 0x59999 initial branch is intentionally
# not added in this proof; target target_is_reacting() semantics remain Pending.
# ---------------------------------------------------------------------------

# Guard the v72 placement-only result.
assert be32(rom, 0x4BBF0) == I(0x09, "zero", "a1", 5)
assert be32(rom, 0x4BBF4) == 0
assert be32(rom, 0x4BBF8) == 0x8C440648
assert be32(rom, 0x4BBFC) == I(0x09, "zero", "a2", 38)
assert be32(rom, 0x4BC00) == J(0x03, 0x80031208)
assert be32(rom, 0x4BC04) == 0
assert be32(rom, 0x9AE44) == 0
assert be32(rom, 0x9AE50) == 0

# Guard the stock one-time setup helper: it still establishes the normal
# target projectile setup and animation rate = 3 before our child takes over.
# VA 0x8004B868 -> ROM 0x4C468.
assert be32(rom, 0x4C468) == 0x3C050004   # lui a1,0x0004
assert be32(rom, 0x4C46C) == J(0x03, 0x8004CC14)
assert be32(rom, 0x4C470) == I(0x09, "zero", "a2", 3)

CHILD_ROM = 0x9AE90
CHILD_VA = 0x8009A290
CALLBACK_ROM = 0x9AED0
CALLBACK_VA = 0x8009A2D0
END_ROM = 0x9AF20

# v72 inherited the v70 proof child/callback here.
old_region = bytes(rom[CHILD_ROM:END_ROM])
assert len(old_region) == 0x90
assert be32(rom, CHILD_ROM) == 0x3C08802F
assert be32(rom, 0x9AEB8) == 0x3C08802F

# Child program: overwrite only the already-facing-aware X velocity magnitude
# with retail normal start 0x33333; preserve the sign chosen by stock setup.
# Then install the translated per-tick callback and enter the same v70/v72
# generic flight/collision path.
child = [
    I(0x0F, "zero", "t0", 0x802F),          # lui   t0,0x802F
    I(0x23, "t0", "t0", 0xCE20),            # lw    t0,current_proc
    I(0x23, "t0", "t1", 0x06E0),            # lw    t1,actor
    I(0x23, "t1", "t2", 0x0014),            # lw    t2,actor->xvel
    I(0x0F, "zero", "t3", 0x0003),          # lui   t3,0x0003
    I(0x0D, "t3", "t3", 0x3333),            # ori   t3,t3,0x3333
    R("zero", "t2", "t2", 31, 0x03),         # sra   t2,t2,31 (sign mask)
    R("t3", "t2", "t3", 0, 0x26),           # xor   t3,t3,t2
    R("t3", "t2", "t3", 0, 0x23),           # subu  t3,t3,t2 -> signed 0x33333
    I(0x2B, "t1", "t3", 0x0014),            # sw    t3,actor->xvel

    I(0x0F, "zero", "t2", 0x800A),          # callback VA 0x8009A2D0
    I(0x09, "t2", "t2", -0x5D30),
    I(0x2B, "t0", "t2", 0x070C),            # current_proc->callback

    I(0x09, "zero", "a1", 0x0013),          # retain v70/v72 collision proof
    J(0x02, 0x8004B9C4),                    # same generic flight entry
    0,
]
assert len(child) == 16
assert CHILD_ROM + len(words(child)) == CALLBACK_ROM

# Per-tick callback:
#   signed_new = old + (old >> 4)
#   magnitude  = abs(signed_new)
#   clamp      = min(magnitude, 0xB3333)
#   restore original direction sign
#   store ONLY actor +0x14
callback = []
pc = CALLBACK_VA

def emit(w):
    global pc
    callback.append(w)
    pc += 4

emit(I(0x0F, "zero", "t0", 0x802F))          # current process
emit(I(0x23, "t0", "t0", 0xCE20))
emit(I(0x23, "t0", "t1", 0x06E0))            # projectile actor
emit(I(0x23, "t1", "t2", 0x0014))            # signed old X velocity
emit(R("zero", "t2", "t3", 4, 0x03))         # old >> 4
emit(R("t2", "t3", "t2", 0, 0x21))           # signed_new = old + old/16

emit(R("zero", "t2", "t6", 31, 0x03))        # sign mask
emit(R("t2", "t6", "t3", 0, 0x26))           # xor for abs
emit(R("t3", "t6", "t3", 0, 0x23))           # magnitude = abs(signed_new)

emit(I(0x0F, "zero", "t4", 0x000B))
emit(I(0x0D, "t4", "t4", 0x3333))            # retail cap 0xB3333
emit(R("t4", "t3", "t5", 0, 0x2A))           # t5 = cap < magnitude

nocap = CALLBACK_VA + 15 * 4
emit(branch(0x04, "t5", "zero", pc, nocap))   # if <= cap skip replacement
emit(0)
emit(R("t4", "zero", "t3", 0, 0x21))         # magnitude = cap

emit(R("t3", "t6", "t3", 0, 0x26))           # restore direction sign
emit(R("t3", "t6", "t3", 0, 0x23))
emit(I(0x2B, "t1", "t3", 0x0014))            # ONLY per-tick state mutation
emit(R("ra", "zero", "zero", 0, 0x08))        # jr ra
emit(0)

assert len(callback) == 20
assert CALLBACK_ROM + len(words(callback)) == END_ROM

rom[CHILD_ROM:CALLBACK_ROM] = words(child)
rom[CALLBACK_ROM:END_ROM] = words(callback)

# Scope guards: placement still identical to v72 and no per-tick call to
# 0x8004CC14 exists in the rewritten region.
assert be32(rom, 0x4BBF0) == I(0x09, "zero", "a1", 5)
assert be32(rom, 0x4BBFC) == I(0x09, "zero", "a2", 38)
assert be32(rom, 0x4BC00) == J(0x03, 0x80031208)
assert be32(rom, CHILD_ROM + 14*4) == J(0x02, 0x8004B9C4)
assert J(0x03, 0x8004CC14).to_bytes(4, "big") not in rom[CALLBACK_ROM:END_ROM]

# Helper processes remain untouched.
assert be32(rom, 0x4BA68) == J(0x03, 0x8002830C)
assert be32(rom, 0x4BA84) == J(0x03, 0x8002830C)

# Input remains Forward, Forward + Low Punch.
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
print("V73_SCOPE", "movement only on v72 placement baseline")
print("START", "0x33333 normal donor-retail branch")
print("ACCEL", "abs(v + (v >> 4)) each flight callback")
print("CAP", "0xB3333")
print("PER_TICK_0x8004CC14", "NO")
print("REACTING_START_0x59999", "NOT YET IMPLEMENTED")
