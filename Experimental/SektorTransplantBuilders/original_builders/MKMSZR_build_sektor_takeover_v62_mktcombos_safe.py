from pathlib import Path
import argparse, hashlib

parser = argparse.ArgumentParser(
    description='Build MKMSZR v62 Sektor MKT combo proof with MKMSZ-native safe reaction semantics from runtime-confirmed v60.'
)
parser.add_argument('v60_rom', type=Path, help='Runtime-confirmed MKMSZR v60 ROM')
parser.add_argument('-o', '--output', type=Path,
                    default=Path('MKMSZR_sektor-mkt-combos-safe_common-proof_v62.z64'))
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

ELBOW_ROOT_PTR_ROM = 0xA1C70
KNEE_ROOT_PTR_ROM  = 0xA1CE8
COMBO_ROM           = 0xB1CB0
COMBO_SIZE          = 0x60
KNEE_PROOF_ROM      = 0x9AD90
KNEE_PROOF_VA       = rom_to_va(KNEE_PROOF_ROM)

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

R1_VA = rom_to_va(COMBO_ROM + 0x00)
R2_VA = rom_to_va(COMBO_ROM + 0x10)
R3_VA = rom_to_va(COMBO_ROM + 0x20)
R4_VA = rom_to_va(COMBO_ROM + 0x30)
R5_VA = rom_to_va(COMBO_ROM + 0x40)
R6_VA = rom_to_va(COMBO_ROM + 0x50)
assert [R1_VA,R2_VA,R3_VA,R4_VA,R5_VA,R6_VA] == [
    0x800B10B0,0x800B10C0,0x800B10D0,0x800B10E0,0x800B10F0,0x800B1100
]

# v61 showed that blindly copying MKT reaction selector 0x02 into MKMSZ is unsafe:
# the long branch catastrophically corrupted world rendering. v62 keeps the genuine
# Sektor MKT button graph and attacker animations but translates reactions to selectors
# already used by MKMSZ's runtime-confirmed stock combo path.
#
# Proven safe MKMSZ semantics used here:
#   0x0000 = stock ordinary combo hit / no direction requirement
#   0x0100 = stock stagger/stumble family / no direction requirement
#   0x0401 = stock Sub-Zero strong terminal combo hit + stick-away requirement
#   0x0504 = uppercut + stick-down; runtime-confirmed in the user's v61 test
#
# For HK,HK we use the same proven strong terminal selector 0x04 with req_none (0x0400):
# the selector is native/proven; only the low-byte input requirement is omitted as required
# by Sektor's genuine HK,HK command.
SEKTOR_SIX_SAFE = bytes.fromhex(
    # R1: HP (second HP of the visible string) -> elbow2; continue R2
    '800910030300100200000000800b10c0'
    # R2: HK -> knee1; native safe stagger; continue R4. R3 is adjacent D+LP option.
    '000913010303100201000000800b10e0'
    # R3: D+LP -> uppercut; runtime-confirmed launch; terminal
    '80090b01020110020504000000000010'
    # R4: B+HK -> knee2; MKMSZ-native strong terminal reaction + stick-away
    '00091303010310020401000000000010'
    # R5: plain HK alternate -> high kick; native safe stagger; continue R6
    '800911010103100201000000800b1100'
    # R6: B+HK -> knee2; MKMSZ-native strong terminal reaction + stick-away
    '80091303010310020401000000000010'
)
assert len(SEKTOR_SIX_SAFE) == COMBO_SIZE

SEKTOR_KNEE_ROOT_SAFE = bytes.fromhex(
    # Second HK after ordinary first HK: high kick, native strong terminal selector, req_none.
    '8009110101031002040000000000000e'
)
assert len(SEKTOR_KNEE_ROOT_SAFE) == 0x10

rom = bytearray(args.v60_rom.read_bytes())
assert len(rom) == 0x1000000
assert hashlib.sha256(rom).hexdigest() == V60_SHA256

# Exact v60 source guards.
assert bytes(rom[COMBO_ROM:COMBO_ROM+COMBO_SIZE]) == EXPECTED_V60_COMBO
assert be32(rom, ELBOW_ROOT_PTR_ROM) == EXPECTED_ELBOW_ROOT
assert be32(rom, KNEE_ROOT_PTR_ROM) == EXPECTED_KNEE_ROOT
assert bytes(rom[KNEE_PROOF_ROM:KNEE_PROOF_ROM+0x10]) == EXPECTED_PROOF_CAVE

before = bytes(rom)

# Keep native HP/elbow root and replace only the six combo records.
rom[COMBO_ROM:COMBO_ROM+COMBO_SIZE] = SEKTOR_SIX_SAFE
assert be32(rom, ELBOW_ROOT_PTR_ROM) == R1_VA

# Proof-only standalone HK->HK record and redirect native knee/high-kick combo root.
rom[KNEE_PROOF_ROM:KNEE_PROOF_ROM+0x10] = SEKTOR_KNEE_ROOT_SAFE
put32(rom, KNEE_ROOT_PTR_ROM, KNEE_PROOF_VA)

# Structural graph + semantic guards.
assert be32(rom, COMBO_ROM + 0x0C) == R2_VA
assert be32(rom, COMBO_ROM + 0x1C) == R4_VA
assert int.from_bytes(rom[COMBO_ROM+0x28:COMBO_ROM+0x2A], 'big') == 0x0504
assert int.from_bytes(rom[COMBO_ROM+0x38:COMBO_ROM+0x3A], 'big') == 0x0401
assert be32(rom, COMBO_ROM + 0x4C) == R6_VA
assert int.from_bytes(rom[COMBO_ROM+0x58:COMBO_ROM+0x5A], 'big') == 0x0401
assert int.from_bytes(rom[KNEE_PROOF_ROM+0x08:KNEE_PROOF_ROM+0x0A], 'big') == 0x0400
assert be32(rom, KNEE_ROOT_PTR_ROM) == KNEE_PROOF_VA

# Explicitly exclude v61's unsafe donor selector 0x02 from every v62 combo strike word.
for off in [COMBO_ROM+0x08, COMBO_ROM+0x18, COMBO_ROM+0x28, COMBO_ROM+0x38,
            COMBO_ROM+0x48, COMBO_ROM+0x58, KNEE_PROOF_ROM+0x08]:
    assert rom[off] != 0x02

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

# Scope guard: v60 may differ only at CRC, proof record, knee-root pointer and six combo records.
allowed = (
    set(range(0x10,0x18)) |
    set(range(KNEE_PROOF_ROM,KNEE_PROOF_ROM+0x10)) |
    set(range(KNEE_ROOT_PTR_ROM,KNEE_ROOT_PTR_ROM+4)) |
    set(range(COMBO_ROM,COMBO_ROM+COMBO_SIZE))
)
diffs=[i for i,(a,b) in enumerate(zip(before,rom)) if a!=b]
assert diffs and all(i in allowed for i in diffs)

args.output.write_bytes(rom)
print('OUT', args.output)
print('SHA256', hashlib.sha256(rom).hexdigest())
print('CRC', f'{crc1:08X} / {crc2:08X}')
print('ELBOW_ROOT', hex(R1_VA), 'at ROM', hex(ELBOW_ROOT_PTR_ROM))
print('KNEE_ROOT', hex(KNEE_PROOF_VA), 'at ROM', hex(KNEE_ROOT_PTR_ROM))
print('COMBO_BLOCK', hex(COMBO_ROM), '..', hex(COMBO_ROM+COMBO_SIZE-1))
print('KNEE_PROOF_RECORD', hex(KNEE_PROOF_ROM), '..', hex(KNEE_PROOF_ROM+0x0F))
print('CHANGED_BYTES', len(diffs))
print('SCOPE', 'v60 + Sektor MKT combo graph with MKMSZ-native safe reaction selectors only')
