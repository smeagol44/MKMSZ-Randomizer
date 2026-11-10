"""Sektor production-composition proof v02 (integration plan step 5, stage 1): v01 with the Sektor build v51, whose stock calls run from KSEG0 (v01 hung on a teleport hit: Toasty's dispatcher did not recognise the KSEG1 return address).

Builds a normal randomizer ROM with the real CLI, builds the Sektor proof line (v50) from the
clean ROM with its fixed loader linked for the production pool tail, and transplants only
Sektor's changes into the randomizer ROM:

* every word the Sektor build changes is classified, by an explicit list, as Sektor
  (transplanted) or proof infrastructure (dropped: its bootstrap, file 0x1B, arena hook,
  debug stage menu, boot-logo skip and max-EXP cheat). An unclassified change fails the build;
* every transplanted word must still hold its clean value in the randomizer ROM (no owner
  conflict), else the build fails;
* the 0x268-byte fixed loader goes into production's shared file 0x1A at KSEG0 0x801B30F0
  (pool tail after the Inventory legend), extending the file-0x1A entry;
* fighter file 0x87 and the donor samples are copied to the generated-output tail
  [0x01820000, 0x0186E4C0) (Runtime-confirmed in proof v49).

Disposable proof; not the production module. SPECIALS must stay on CLASSIC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from mkmszr.checksum import calculate_crc_6102
from mkmszr.patches.rainbow_palette import LOAD_JAL_SITES

SEKTOR_BUILDER = ROOT / "Experimental/SektorTransplantBuilders/teleport/MKMSZR_build_sektor_teleport_v51.py"
FIXED_VA = 0xA01B30F0  # production pool tail after the Inventory legend (ends 0x801B30E6)
POOL_BASE, POOL_END = 0x801AF820, 0x801B3420
FILE_TABLE, FILE_1A, FILE_87 = 0x000A5010, 0x1A, 0x87
TAIL = (0x01820000, 0x0186E4C0)
SOUND_TABLES = (0x00947000, 0x00980000)  # patch/subpatch/wave/book/track records

# Sektor words (transplanted), by ROM offset or range [start, end).
TRANSPLANT_SITES = {
    *LOAD_JAL_SITES,  # 15 file-0x87 load calls -> fixed loader
    0x0002F7A0,  # Run animation rate 2 -> 3
    0x0004B654,  # transfer-selector bound (selectors 3 teleport, 4 lifted Ice root)
    0x0005C8D4, 0x0005C9C8, 0x0005C9F8,  # throw sound hooks -> trampolines
    0x000A1C5C, 0x000A1C60,  # transfer table entries 3, 4
    0x000A1CE8,  # knee root (Sektor HK,HK combo)
    0x000A1E1C,  # reaction table entry 0x23
    0x000A3AD8, 0x000A3ADC,  # Sub-Zero player voice table (Sektor voice set)
    0x000A5664, 0x000A5668,  # file 0x87 entry (repointed below)
    0x000B00D0,  # strike pointer, selector 0x13
}  # fmt: skip
TRANSPLANT_RANGES = (
    (0x000B1B0C, 0x000B1B94),  # LP (double, straight) and LK (teleport) records
    (0x000B1C80, 0x000B1D10),  # HP record (homing) and Sektor combo records
    SOUND_TABLES,
)
# Proof infrastructure (dropped).
DROP_SITES = {0x10, 0x14, 0x0000DD60, 0x0000DD64, 0x0000E028, 0x00015CD0, 0x00015CD4,
              0x0007A3F4, 0x00066F64, 0x000A5154, 0x000A5158}  # fmt: skip
DROP_RANGES = (
    (0x00066FE0, 0x00066FEC),  # proof loader hook
    (0x0009A700, 0x0009A720),  # debug stage-menu mapper
    (0x0009AD84, 0x0009ADD4),  # proof bootstrap stub
    (0x0009B7DC, 0x0009B80C),  # debug stage-menu table
    (0x000A6FFC, 0x000A7010),  # max-EXP cheat
    (0x00F10000, 0x00F14000),  # proof file 0x1B (fixed loader harvested from here)
)


def _in(off: int, ranges) -> bool:
    return any(a <= off < b for a, b in ranges)


def be32(data, off: int) -> int:
    return int.from_bytes(data[off : off + 4], "big")


def put32(data: bytearray, off: int, value: int) -> None:
    data[off : off + 4] = (value & 0xFFFFFFFF).to_bytes(4, "big")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("clean_rom", type=Path)
    p.add_argument("mkt_rom", type=Path)
    p.add_argument("-o", "--output", type=Path, default=Path("MKMSZR_sektor_production-composition_proof_v02.z64"))
    p.add_argument("--seed", default="SEKTOR-PROD-1")
    p.add_argument("cli_args", nargs="*", help="extra randomizer CLI options (after --)")
    args = p.parse_args()
    if any("specials" in a.lower() for a in args.cli_args):
        raise SystemExit("Sektor needs SPECIALS: CLASSIC")
    clean = args.clean_rom.read_bytes()

    with tempfile.TemporaryDirectory() as td:
        base_path, sek_path, man_path = Path(td) / "base.z64", Path(td) / "sek.z64", Path(td) / "sek.json"
        env = {"PYTHONPATH": str(ROOT / "src")}
        subprocess.run([sys.executable, "-m", "mkmszr.cli", "--mkt-rom", str(args.mkt_rom), "--seed", args.seed,
                        *args.cli_args, str(args.clean_rom), str(base_path)],
                       check=True, env=env, stdout=subprocess.DEVNULL)  # fmt: skip
        subprocess.run([sys.executable, str(SEKTOR_BUILDER), str(args.clean_rom), str(args.mkt_rom), "-o", str(sek_path),
                        "--fixed-va", hex(FIXED_VA), "--manifest", str(man_path)],
                       check=True, env=env, stdout=subprocess.DEVNULL)  # fmt: skip
        rom = bytearray(base_path.read_bytes())
        sek = sek_path.read_bytes()
        man = json.loads(man_path.read_text())

    assert len(rom) == len(sek) == 0x02000000 and len(clean) == 0x01000000
    assert man["fixed_va"] == FIXED_VA

    # 1. Classify and transplant every changed word of the 16 MiB part.
    moved, conflicts, unknown = 0, [], []
    for off in range(0, 0x01000000, 4):
        if sek[off : off + 4] == clean[off : off + 4]:
            continue
        if off in DROP_SITES or _in(off, DROP_RANGES):
            continue
        if off in TRANSPLANT_SITES or _in(off, TRANSPLANT_RANGES):
            if rom[off : off + 4] != clean[off : off + 4]:
                conflicts.append(hex(off))
                continue
            rom[off : off + 4] = sek[off : off + 4]
            moved += 1
            continue
        unknown.append(hex(off))
    if unknown or conflicts:
        raise SystemExit(f"unclassified {unknown[:20]} / conflicts with production {conflicts[:20]}")

    # 2. Fighter file 0x87 and samples in the generated-output tail.
    assert set(rom[TAIL[0] : TAIL[1]]) == {0xFF}, "tail region not free in the randomizer ROM"
    rom[TAIL[0] : TAIL[1]] = sek[TAIL[0] : TAIL[1]]
    assert (be32(rom, FILE_TABLE + FILE_87 * 12), be32(rom, FILE_TABLE + FILE_87 * 12 + 4)) == (
        man["file87_rom"], man["file87_rom"] + man["file87_size"])  # fmt: skip

    # 3. Fixed loader into shared file 0x1A at FIXED_VA.
    e1a = FILE_TABLE + FILE_1A * 12
    f1a_start, f1a_end = be32(rom, e1a), be32(rom, e1a + 4)
    fixed_k0 = FIXED_VA & ~0x20000000
    loaded_end = POOL_BASE + (f1a_end - f1a_start)
    assert loaded_end <= fixed_k0, (hex(loaded_end), "file 0x1A already reaches the fixed loader")
    fixed = sek[man["fixed_rom"] : man["fixed_rom"] + man["fixed_len"]]
    at = f1a_start + (fixed_k0 - POOL_BASE)
    end_k0 = fixed_k0 + len(fixed)
    assert end_k0 <= POOL_END and set(rom[f1a_end:at + len(fixed)]) == {0xFF}, "pool tail not free"
    rom[f1a_end:at] = bytes(at - f1a_end)  # padding inside the loaded file
    rom[at : at + len(fixed)] = fixed
    put32(rom, e1a + 4, at + len(fixed))
    # The transplanted load/throw jal words already target the fixed loader at FIXED_VA.
    for site in LOAD_JAL_SITES:
        assert be32(rom, site) == 0x0C000000 | ((man["load_wrapper"] >> 2) & 0x03FFFFFF), hex(site)

    crc1, crc2 = calculate_crc_6102(rom)
    put32(rom, 0x10, crc1)
    put32(rom, 0x14, crc2)
    args.output.write_bytes(rom)
    print("TRANSPLANTED", moved, "words; tail", hex(TAIL[0]), hex(TAIL[1]), "; fixed loader", hex(fixed_k0), hex(end_k0),
          "file 0x1A end", hex(f1a_end), "->", hex(at + len(fixed)))  # fmt: skip
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    print("CRC", f"{crc1:08X} / {crc2:08X}")


if __name__ == "__main__":
    main()
