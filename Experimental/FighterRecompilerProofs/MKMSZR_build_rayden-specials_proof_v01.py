"""Rayden specials proof v01 (Fighter recompiler plan, milestone 6): Lightning. Disposable.

The generic build of his description (``fighter_import.fighter_build.build``: body, combos,
throw, getup sound, voices, and his specials from ``fighters/moves/rayden.json``) plus the
specials proofs' harness (debug stage select, boot skip, max EXP, the payload raw-loaded at
0x801AF420 from ROM 0xF10000 through file 0x1B, 16 KiB arena: Reptile proof v22's).

Lightning (D,F + LP, MKT ``0x800ABA54`` -> special 0x2E -> ``0x80077DF8(0)``) in Ice Blast's
slot, with the generic projectile: his throw pose (table-0 slot 0x24, phase 1, rate 3) and
sound 2, the bolt (slot 0x43 part 3, looping) at speed 0x80000 rate 3 with palette 0x800B9B04,
strike 17 (box 133,36,60,16; damage 22, chip 4) and the impact burst (part 4, rate 4) at the
opponent. Stand-ins and gaps (owner to judge): the host roundhouse launch (0x0C) for MKT's
victim reaction 0x80, no forming sparks (parts 1-2), a silent impact (his layered hit sounds),
a first spawn offset. Also: the knockdown's later lying phase shows his flat frame (owner,
inputs v01). Usage::

    python3 MKMSZR_build_rayden-specials_proof_v01.py CLEAN.z64 MKT.z64 -o MKMSZR_rayden-specials_common_proof_v01.z64
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from mkmszr.checksum import calculate_crc_6102
from mkmszr.fighter_import import fighter_build as fb

_spec = importlib.util.spec_from_file_location(
    "v01", HERE / "MKMSZR_build_generic-projectile_proof_v01.py"
)
assert _spec and _spec.loader
v01 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v01)

FIGHTER = "rayden"
ARENA_LO = f"{(fb.LINK_VA + fb.PAYLOAD_LIMIT) & 0xFFFF:04x}"


def harness(rom: bytearray) -> None:
    """The v6 harness of the specials proofs, less what the generic build already writes (the
    transfer selectors and their bound)."""

    v01.guarded(rom, 0x66F64, "2442f420", "2442" + ARENA_LO)  # arena prefix reservation
    v01.guarded(rom, 0x66FE0, "27bdffe83c02801b2442f420", "0802686100000000" + "2442" + ARENA_LO)
    v01.guarded(rom, 0x9AD84, "00" * 0x50, (
        "27bdffe83c02801b2442" + ARENA_LO + "afbf00103c04800fac82ecd00c0198e400000000"
        "2404001b3c05801b24a5f4200c01975900000000"
        "3c0880113409270fa509200e8fbf001027bd001803e0000800000000"
    ).ljust(0xA0, "0"))  # loader stub (+ max EXP)  # fmt: skip
    v01.guarded(rom, 0xA5154, "00" * 8, f"{fb.SCRATCH_ROM:08x}{fb.SCRATCH_ROM + fb.PAYLOAD_LIMIT:08x}")
    for off, old in ((0xA6FFC, "0104036b"), (0xA7000, "09470591"), (0xA7004, "11ad0d16"),
                     (0xA700C, "1ccf4e20")):  # fmt: skip
        v01.guarded(rom, off, old, "270f270f")


def build(clean: bytes, mkt: bytes) -> tuple[bytes, fb.Built]:
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, "not the clean MKMSZ USA Rev. 0 ROM"
    built = fb.build(clean, mkt, FIGHTER)
    rom = bytearray(built.rom)
    v01.proof_base(rom)
    harness(rom)
    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), built


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("clean", type=Path)
    parser.add_argument("mkt", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    rom, built = build(args.clean.read_bytes(), args.mkt.read_bytes())
    args.output.write_bytes(rom)
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    print("SELECTORS", built.selectors, "REACTIONS", built.reactions, "PAYLOAD", hex(len(built.payload)))
    print("TEST", "debug stage select, max EXP; Lightning D,F + LP (Ice Blast's slot)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
