from pathlib import Path
import argparse, hashlib

parser = argparse.ArgumentParser(
    description='Build MKMSZR v61 full Sektor MKT combo-string proof from runtime-confirmed v60.'
)
parser.add_argument('v60_rom', type=Path, help='Runtime-confirmed MKMSZR v60 ROM')
parser.add_argument('-o', '--output', type=Path,
                    default=Path('MKMSZR_sektor-mkt-combos_common-proof_v61.z64'))
args = parser.parse_args()

V60_SHA256 = 'caebb133e7ea759e5f115d169fe84f00d4120caa6545373b28983fd8efde048b'

# MKMSZ main-segment mapping in this region is VA = 0x80000000 + (ROM - 0xC00).
def rom_to_va(off):
    return 0x80000000 + (off - 0xC00)

def be32(b, o):
    return int.from_bytes(b[o:o+4], 'big')

def put32(b, o, v):
    b[o:o+4] = int(v & 0xffffffff).to_bytes(4, 'big')

def rol32(v, s):
    s &= 31
    return v & 0xffffffff if s == 0 else ((v << s) | (v >> (32-s))) & 0xffffffff

# Existing Sub-Zero combo graph in MKMSZ / v60.
ELBOW_ROOT_PTR_ROM = 0xA1C70
KNEE_ROOT_PTR_ROM  = 0xA1CE8
COMBO_ROM           = 0xB1CB0
COMBO_SIZE          = 0x60   # six contiguous 0x10-byte records

# One extra 0x10-byte record is needed because Sektor has an independent HK -> HK root
# in addition to the six-record HP-chain graph. This location is proof-only and conflicts
# with the production randomizer bootstrap reservation; it must be reallocated for production.
KNEE_PROOF_ROM = 0x9AD90
KNEE_PROOF_VA  = rom_to_va(KNEE_PROOF_ROM)  # 0x8009A190

# Exact v60 guards. These are the stock MKMSZ Sub-Zero ct_sz_* records, unchanged through v60.
EXPECTED_V60_COMBO = bytes.fromhex(
    '800910030200100200000000800b10c0'
    '000910040201100200000000800b10d0'
    '000913050304100201050000800b10f0'
    '8009150101031002010100000000000e'
    '800c13030303130201000000800b1100'
    '8009150102031302040100000000000e'
)
assert len(EXPECTED_V60_COMBO) == COMBO_SIZE

EXPECTED_ELBOW_ROOT = 0x800B10B0
EXPECTED_KNEE_ROOT  = 0x800B10F0
EXPECTED_PROOF_CAVE = bytes(0x10)

# Genuine retail MKT Rev.2 Sektor combo semantics, with only internal pointers translated
# to the MKMSZ locations used by this proof. Midway source names / intended input graph:
#   ct_sektor_elbow2 : HP        -> ct_sektor_knee1
#   ct_sektor_knee1  : HK        -> ct_sektor_roundh1
#     alternate      : D+LP      -> uppercut / stk_5 (uppercutted), terminal
#   ct_sektor_roundh1: B+HK      -> terminal
#     alternate      : HK        -> ct_sektor_roundh2
#   ct_sektor_roundh2: B+HK      -> terminal
#   ct_sektor_knee2  : HK        -> terminal  (rooted after the ordinary first HK)
# Therefore the complete visible strings are:
#   HK, HK
#   HP, HP, D+LP
#   HP, HP, HK, B+HK
#   HP, HP, HK, HK, B+HK
#
# The c_stk word 0x0504 is stk_5 | req_stkdown in Midway's source:
# stk_5 = "uppercutted" and req_stkdown = joystick down.
R1_VA = rom_to_va(COMBO_ROM + 0x00)
R2_VA = rom_to_va(COMBO_ROM + 0x10)
R3_VA = rom_to_va(COMBO_ROM + 0x20)
R4_VA = rom_to_va(COMBO_ROM + 0x30)
R5_VA = rom_to_va(COMBO_ROM + 0x40)
R6_VA = rom_to_va(COMBO_ROM + 0x50)
assert [R1_VA,R2_VA,R3_VA,R4_VA,R5_VA,R6_VA] == [
    0x800B10B0,0x800B10C0,0x800B10D0,0x800B10E0,0x800B10F0,0x800B1100
]

SEKTOR_SIX = bytes.fromhex(
    # R1: second HP -> Sektor elbow2, continue to R2
    '800910030300100200000000800b10c0'
    # R2: HK option -> knee1, continue to R4; R3 is the adjacent alternate D+LP option
    '000913010303100201000000800b10e0'
    # R3: D+LP -> uppercut, stk_5 uppercutted, terminal
    '80090b01020110020504000000000010'
    # R4: B+HK -> knee2, knocked-back reaction, terminal; R5 is alternate plain HK
    '00091303010310020201000000000010'
    # R5: plain HK -> high kick, continue to R6
    '800911010103100201000000800b1100'
    # R6: B+HK -> knee2, knocked-back reaction, terminal
    '80091303010310020201000000000010'
)
assert len(SEKTOR_SIX) == COMBO_SIZE

SEKTOR_KNEE_ROOT = bytes.fromhex(
    # Second HK after an ordinary first HK: high kick, stk_2, terminal.
    '8009110101031002020000000000000e'
)
assert len(SEKTOR_KNEE_ROOT) == 0x10

rom = bytearray(args.v60_rom.read_bytes())
assert len(rom) == 0x1000000
assert hashlib.sha256(rom).hexdigest() == V60_SHA256

# Exact source guards.
assert bytes(rom[COMBO_ROM:COMBO_ROM+COMBO_SIZE]) == EXPECTED_V60_COMBO
assert be32(rom, ELBOW_ROOT_PTR_ROM) == EXPECTED_ELBOW_ROOT
assert be32(rom, KNEE_ROOT_PTR_ROM) == EXPECTED_KNEE_ROOT
assert bytes(rom[KNEE_PROOF_ROM:KNEE_PROOF_ROM+0x10]) == EXPECTED_PROOF_CAVE

before = bytes(rom)

# Keep the native elbow/HP root unchanged; replace the complete six-record Sub-Zero graph
# in place with Sektor's six-record HP graph.
rom[COMBO_ROM:COMBO_ROM+COMBO_SIZE] = SEKTOR_SIX
assert be32(rom, ELBOW_ROOT_PTR_ROM) == R1_VA

# Add the one independent Sektor HK->HK continuation record and point MKMSZ's native
# knee/high-kick combo root at it.
rom[KNEE_PROOF_ROM:KNEE_PROOF_ROM+0x10] = SEKTOR_KNEE_ROOT
put32(rom, KNEE_ROOT_PTR_ROM, KNEE_PROOF_VA)

# Structural graph guards.
assert be32(rom, COMBO_ROM + 0x0C) == R2_VA
assert be32(rom, COMBO_ROM + 0x1C) == R4_VA
assert int.from_bytes(rom[COMBO_ROM+0x28:COMBO_ROM+0x2A], 'big') == 0x0504
assert be32(rom, COMBO_ROM + 0x4C) == R6_VA
assert be32(rom, KNEE_ROOT_PTR_ROM) == KNEE_PROOF_VA

# CIC-6102 CRC.
seed = 0xF8CA4DDC
t1=t2=t3=t4=t5=t6=seed
for off in range(0x1000,0x101000,4):
    value=be32(rom,off); total=(t6+value)&0xffffffff
    if total<t6: t4=(t4+1)&0xffffffff
    t6=total; t3^=value; r=rol32(value,value&31); t5=(t5+r)&0xffffffff
    t2^=r if t2>value else (t6^value); t1=(t1+(t5^value))&0xffffffff
crc1=(t6^t4^t3)&0xffffffff; crc2=(t5^t2^t1)&0xffffffff
put32(rom,0x10,crc1); put32(rom,0x14,crc2)

# Scope guard: only CRC, the one proof record, the knee root pointer, and six native
# combo records may differ from runtime-confirmed v60.
allowed = (
    set(range(0x10,0x18)) |
    set(range(KNEE_PROOF_ROM,KNEE_PROOF_ROM+0x10)) |
    set(range(KNEE_ROOT_PTR_ROM,KNEE_ROOT_PTR_ROM+4)) |
    set(range(COMBO_ROM,COMBO_ROM+COMBO_SIZE))
)
diffs=[i for i,(a,b) in enumerate(zip(before,rom)) if a!=b]
assert diffs and all(i in allowed for i in diffs)
assert any(COMBO_ROM <= i < COMBO_ROM+COMBO_SIZE for i in diffs)
assert any(KNEE_PROOF_ROM <= i < KNEE_PROOF_ROM+0x10 for i in diffs)
assert any(KNEE_ROOT_PTR_ROM <= i < KNEE_ROOT_PTR_ROM+4 for i in diffs)

args.output.write_bytes(rom)
print('OUT', args.output)
print('SHA256', hashlib.sha256(rom).hexdigest())
print('CRC', f'{crc1:08X} / {crc2:08X}')
print('ELBOW_ROOT', hex(R1_VA), 'at ROM', hex(ELBOW_ROOT_PTR_ROM))
print('KNEE_ROOT', hex(KNEE_PROOF_VA), 'at ROM', hex(KNEE_ROOT_PTR_ROM))
print('COMBO_BLOCK', hex(COMBO_ROM), '..', hex(COMBO_ROM+COMBO_SIZE-1))
print('KNEE_PROOF_RECORD', hex(KNEE_PROOF_ROM), '..', hex(KNEE_PROOF_ROM+0x0F))
print('CHANGED_BYTES', len(diffs))
print('SCOPE', 'v60 + Sektor MKT combo graph only; no fighter-resource or palette changes')
