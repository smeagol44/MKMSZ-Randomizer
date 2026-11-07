from pathlib import Path
import argparse, hashlib

parser = argparse.ArgumentParser(description='Build MKMSZR v60 first-Scorpion -> Cyrax-style palette proof from runtime-confirmed v59.')
parser.add_argument('v59_rom', type=Path, help='Runtime-confirmed MKMSZR v59 ROM')
parser.add_argument('-o', '--output', type=Path, default=Path('MKMSZR_scorpion-cyrax-palette_common-proof_v60.z64'))
args = parser.parse_args()

V59_SHA256 = 'b8b1ddfa964de4da86dc9598f99139f4c50ac066deaaf4ab5cd91fda63baf1cc'
RR = 0xF40000
# file 0x87 palette records: record 0 header + colors at +0x4584C; record 1 colors at +0x458D0.
ALT_PALETTE32_ROM = RR + 0x458D0

# Runtime-confirmed v59 native Sektor lower-32 TLUT.
SEKTOR_PALETTE32 = bytes.fromhex(
    '0000defec63cb5baa95898f790b2843a88568014842f842d842b800880048003'
    'f7bdef7be739d6b5ce73bdefb5adad6ba52998c690848c638842842180008000'
)

# Cyrax-style palette proof: entries 1..15 retain Sektor armor luminance/saturation but
# move the armor hue into MKMSZ Scorpion's native yellow/gold family. Entries 16..31
# are byte-identical to Sektor so gray/black robot metal is preserved.
CYRAX_PALETTE32 = bytes.fromhex(
    '0000df9ec75cb6faaab89a7791f2869a8a568214858f854d852b80c880648043'
    'f7bdef7be739d6b5ce73bdefb5adad6ba52998c690848c638842842180008000'
)
assert len(SEKTOR_PALETTE32) == len(CYRAX_PALETTE32) == 64
assert CYRAX_PALETTE32[32:] == SEKTOR_PALETTE32[32:]
assert CYRAX_PALETTE32[:32] != SEKTOR_PALETTE32[:32]

rom = bytearray(args.v59_rom.read_bytes())
assert len(rom) == 0x1000000
assert hashlib.sha256(rom).hexdigest() == V59_SHA256

# v59 leaves the alternate Scorpion palette's lower 32 entries as stock. Guard exact source.
EXPECTED_V59_ALT32 = bytes.fromhex(
    '0000463135ad2d6b252921081ce718c614a510840c630842042100016fdf5f9f'
    '573f4adf469e427c3e3b39fa31d82db72976255521341d1210d10caf048e006b'
)
assert bytes(rom[ALT_PALETTE32_ROM:ALT_PALETTE32_ROM+64]) == EXPECTED_V59_ALT32

before = bytes(rom)
rom[ALT_PALETTE32_ROM:ALT_PALETTE32_ROM+64] = CYRAX_PALETTE32

# CIC-6102 CRC, same implementation used by the v59 builder.
def be32(b, o): return int.from_bytes(b[o:o+4], 'big')
def put32(b, o, v): b[o:o+4] = int(v & 0xffffffff).to_bytes(4, 'big')
def rol32(v, s):
    s &= 31
    return v & 0xffffffff if s == 0 else ((v << s) | (v >> (32-s))) & 0xffffffff
seed = 0xF8CA4DDC
t1=t2=t3=t4=t5=t6=seed
for off in range(0x1000,0x101000,4):
    value=be32(rom,off); total=(t6+value)&0xffffffff
    if total<t6: t4=(t4+1)&0xffffffff
    t6=total; t3^=value; r=rol32(value,value&31); t5=(t5+r)&0xffffffff
    t2^=r if t2>value else (t6^value); t1=(t1+(t5^value))&0xffffffff
crc1=(t6^t4^t3)&0xffffffff; crc2=(t5^t2^t1)&0xffffffff
put32(rom,0x10,crc1); put32(rom,0x14,crc2)

# Guard scope: only header CRC bytes and the one 64-byte alternate palette window may differ.
allowed = set(range(0x10,0x18)) | set(range(ALT_PALETTE32_ROM, ALT_PALETTE32_ROM+64))
diffs = [i for i,(a,b) in enumerate(zip(before,rom)) if a != b]
assert diffs and all(i in allowed for i in diffs)
assert any(ALT_PALETTE32_ROM <= i < ALT_PALETTE32_ROM+64 for i in diffs)

args.output.write_bytes(rom)
print('OUT', args.output)
print('SHA256', hashlib.sha256(rom).hexdigest())
print('CRC', f'{crc1:08X} / {crc2:08X}')
print('ALT_PALETTE32_ROM', hex(ALT_PALETTE32_ROM))
print('CHANGED_BYTES', len(diffs))
print('PALETTE_CHANGED_BYTES', sum(ALT_PALETTE32_ROM <= i < ALT_PALETTE32_ROM+64 for i in diffs))
print('SCOPE', 'v59 + alternate Scorpion lower-32 TLUT only; Sektor metal indices 16..31 preserved exactly')
