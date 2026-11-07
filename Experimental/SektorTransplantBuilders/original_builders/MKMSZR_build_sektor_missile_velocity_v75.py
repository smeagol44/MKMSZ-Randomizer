#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib

V73_SHA256 = "a6cbf8c061df46c5a85668680ba268153a55ea2f293e3bd87db6b148abcfd36b"
EXPECTED_SIZE = 0x1000000

parser = argparse.ArgumentParser(
    description="Build MKMSZR Sektor missile magnitude-calibration v75 from the exact v73 proof ROM."
)
parser.add_argument(
    "v73_rom",
    type=Path,
    help="MKMSZR_sektor-missile-movement_common-proof_v73.z64"
)
parser.add_argument(
    "-o", "--output",
    type=Path,
    default=Path("MKMSZR_sektor-missile-velocity_common-proof_v75.z64")
)
args = parser.parse_args()

rom = bytearray(args.v73_rom.read_bytes())
assert len(rom) == EXPECTED_SIZE, f"wrong ROM size: {len(rom):#x}"
actual = hashlib.sha256(rom).hexdigest()
assert actual == V73_SHA256, f"wrong v73 baseline: {actual}"

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
# v75: cadence-resampled movement + bounded 2x magnitude calibration ONLY
#
# Keep v72/v73 placement exactly:
#     0x80031208(projectile, +5, +38)
#
# Keep stock Ice helper-process composition, chest marker, collision path,
# rocket art, blue tint, Ice SFX, and F,F+LP input unchanged.
#
# Static calibration:
#   - MKT object velocity integrates at nominal 60 Hz: pos += vel
#   - MKMSZ actor +0x14 integrates at ~30 Hz with an effective 3x host factor
#
# Donor recurrence before clamp:
#       d_next = d * 17/16
#
# Two donor ticks folded into one MKMSZ tick:
#       (17/16)^2 = 289/256
#                    = 1 + 1/8 + 1/256
#
# Therefore the target callback uses:
#       h_next = h + (h >> 3) + (h >> 8)
#
# Initial target interval is the pair-average displacement:
#       d0 = 0x33333
#       d1 = d0 + (d0 >> 4) = 0x36666
#       h0 = floor((d0 + d1) / 3) = 0x23333
#
# Steady donor cap 0xB3333 maps to target cap:
#       floor(2 * 0xB3333 / 3) = 0x77777
#
# This is algebraically equivalent to the two-donor-step resampler before the
# donor clamp. Because donor integer clamping happens inside the two substeps,
# the penultimate near-cap interval can differ slightly from an explicit
# donor-state implementation; steady cap and all pre-cap exponential timing are
# preserved. That remaining clamp-transition quantization is accepted for this
# bounded runtime proof and is NOT a license for by-eye speed tuning.
#
# v75 bounded runtime calibration:
#   Comparative tracking of 7 donor MKT flights and 5 v74 MKMSZ flights found
#   late visible speed ratio ~= 1.97x normalized (~2.04x raw recording pixels),
#   while launch-to-plateau time remained broadly similar. Keep the v74 temporal
#   resampler exactly and multiply ONLY the host velocity magnitude by 2:
#       initial 0x23333 -> 0x46666
#       cap     0x77777 -> 0xEEEEE
#   This tests the missing spatial scale independently. It does NOT establish
#   2.0x as a universal donor->target scale until runtime validated.
# ---------------------------------------------------------------------------

# Guard v72 placement and v73 inherited presentation/lifecycle controls.
assert be32(rom, 0x4BBF0) == I(0x09, "zero", "a1", 5)
assert be32(rom, 0x4BBF4) == 0
assert be32(rom, 0x4BBF8) == 0x8C440648
assert be32(rom, 0x4BBFC) == I(0x09, "zero", "a2", 38)
assert be32(rom, 0x4BC00) == J(0x03, 0x80031208)
assert be32(rom, 0x4BC04) == 0
assert be32(rom, 0x9AE44) == 0
assert be32(rom, 0x9AE50) == 0

# Stock one-time projectile setup remains rate=3 and facing-aware.
assert be32(rom, 0x4C468) == 0x3C050004
assert be32(rom, 0x4C46C) == J(0x03, 0x8004CC14)
assert be32(rom, 0x4C470) == I(0x09, "zero", "a2", 3)

# v73 redirects the stock path into the proof child and still clears +0x70C
# in the jump delay slot. v74 replaces only that delay-slot clear with a
# callback-address high-half preload; the child stores +0x70C before flight.
CHILD_ROM = 0x9AE90
CHILD_VA = 0x8009A290
CALLBACK_ROM = 0x9AEC8
CALLBACK_VA = 0x8009A2C8
END_ROM = 0x9AF20

assert be32(rom, 0x4C484) == J(0x02, CHILD_VA)
assert be32(rom, 0x4C488) == I(0x2B, "v0", "zero", 0x070C)
put32(rom, 0x4C488, I(0x0F, "zero", "t2", 0x800A))  # lui t2,0x800A

# Child: install cadence-correct first host interval with the bounded 2x
# video-derived spatial calibration (0x46666), preserving the
# facing sign already established by stock setup. Then finish callback address,
# install it, and enter the exact same generic v73 flight/collision path.
child = [
    I(0x0F, "zero", "t0", 0x802F),          # current process
    I(0x23, "t0", "t0", 0xCE20),
    I(0x23, "t0", "t1", 0x06E0),            # projectile actor
    I(0x23, "t1", "t3", 0x0014),            # current signed xvel -> sign source

    I(0x0F, "zero", "t4", 0x0004),
    I(0x0D, "t4", "t4", 0x6666),            # magnitude 0x46666
    R("zero", "t3", "t3", 31, 0x03),         # sign mask
    R("t4", "t3", "t4", 0, 0x26),
    R("t4", "t3", "t4", 0, 0x23),           # signed +/-0x23333
    I(0x2B, "t1", "t4", 0x0014),

    I(0x09, "t2", "t2", -0x5D38),           # 0x800A0000 -> 0x8009A2C8
    I(0x2B, "t0", "t2", 0x070C),            # child callback
    J(0x02, 0x8004B9C4),                    # same generic flight/collision loop
    I(0x09, "zero", "a1", 0x0013),          # delay: original strike selector
]
assert len(child) == 14
assert CHILD_ROM + len(words(child)) == CALLBACK_ROM

# Callback: one 30 Hz host update represents two 60 Hz donor recurrence steps.
# Work in magnitude, then restore the current direction sign. It mutates ONLY
# actor +0x14 and returns normally to the proven generic projectile loop.
callback = []
pc = CALLBACK_VA

def emit(w):
    global pc
    callback.append(w)
    pc += 4

emit(I(0x0F, "zero", "t0", 0x802F))
emit(I(0x23, "t0", "t0", 0xCE20))
emit(I(0x23, "t0", "t1", 0x06E0))
emit(I(0x23, "t1", "t2", 0x0014))            # signed host xvel

emit(R("zero", "t2", "t6", 31, 0x03))        # sign mask
emit(R("t2", "t6", "t2", 0, 0x26))
emit(R("t2", "t6", "t2", 0, 0x23))           # magnitude

emit(R("zero", "t2", "t3", 3, 0x02))         # h >> 3
emit(R("zero", "t2", "t4", 8, 0x02))         # h >> 8
emit(R("t2", "t3", "t2", 0, 0x21))
emit(R("t2", "t4", "t2", 0, 0x21))           # h *= 289/256

emit(I(0x0F, "zero", "t4", 0x000E))
emit(I(0x0D, "t4", "t4", 0xEEEE))            # bounded video-calibrated host cap
emit(R("t4", "t2", "t5", 0, 0x2B))           # cap < magnitude ?

nocap = CALLBACK_VA + 17 * 4
emit(branch(0x04, "t5", "zero", pc, nocap))   # if not over cap
emit(R("t2", "zero", "t3", 0, 0x21))          # delay: out = magnitude
emit(R("t4", "zero", "t3", 0, 0x21))          # over cap: out = cap

emit(R("t3", "t6", "t3", 0, 0x26))
emit(R("t3", "t6", "t3", 0, 0x23))           # restore sign
emit(I(0x2B, "t1", "t3", 0x0014))            # ONLY state mutation
emit(R("ra", "zero", "zero", 0, 0x08))
emit(0)

assert len(callback) == 22
assert CALLBACK_ROM + len(words(callback)) == END_ROM

rom[CHILD_ROM:CALLBACK_ROM] = words(child)
rom[CALLBACK_ROM:END_ROM] = words(callback)

# Scope guards.
assert be32(rom, 0x4BBF0) == I(0x09, "zero", "a1", 5)
assert be32(rom, 0x4BBFC) == I(0x09, "zero", "a2", 38)
assert be32(rom, 0x4BC00) == J(0x03, 0x80031208)
assert J(0x03, 0x8004CC14).to_bytes(4, "big") not in rom[CALLBACK_ROM:END_ROM]

# Ice helper processes remain intentionally intact.
assert be32(rom, 0x4BA68) == J(0x03, 0x8002830C)
assert be32(rom, 0x4BA84) == J(0x03, 0x8002830C)

# Authentic input unchanged: Forward, Forward + Low Punch.
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
print("V75_SCOPE", "v74 cadence resampler with bounded 2x velocity-magnitude calibration; placement/lifecycle unchanged")
print("INITIAL_HOST", "0x46666")
print("HOST_RECURRENCE", "h += (h >> 3) + (h >> 8)  # x289/256 per ~30Hz tick")
print("HOST_CAP", "0xEEEEE")
print("PLACEMENT", "(+5,+38) unchanged")
print("ICE_HELPERS_TINT_SFX", "UNCHANGED / expected")
print("PER_TICK_0x8004CC14", "NO")
