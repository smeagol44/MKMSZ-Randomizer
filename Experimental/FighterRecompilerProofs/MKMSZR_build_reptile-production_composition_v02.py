"""Reptile production-composition proof v02 (milestone 4 step 5 / milestone 5). Disposable.

v01 with one fix (owner, v01): the forceball's forming arc (the throw helper) stayed up to 4 s
when a hit interrupted the throw; the helper now ends as soon as the owner is in a hit reaction
or another action (``lower_projectile.emit_helper``). v01:

A normal randomizer ROM from the real CLI (Sub-Zero, SPECIALS: CLASSIC), then Reptile put in
by the production Fighter option's generic path for described fighters
(``patches.fighter_swap._apply_described`` -> ``fighter_import.fighter_build.production``):

* every word Reptile's build changes in the 16 MiB part, after an owner-conflict check;
* his fighter file (body, move art, and his payload as a relocatable blob with its relocation
  table) and his donor samples in the generated-output tail ``[0x01820000, 0x0186E4C0)``;
* the fixed loader in shared file 0x1A at KSEG0 ``0x801B30F0``: it wraps the 15 file-0x87
  loads, relocates the blob and refreshes the 17 stock words that point into it (transfer
  entries 3-7, reaction entries 0x23/0x2B/0x4C, the LP/LK/HK command records, and the pointer
  the HP handler now reads its moved table from);
* his Power Ups icons and help text from his description.

The first time his code runs from inside his fighter file (Sektor's accepted "option C"
layout); the specials proofs ran it from a raw-loaded 16 KiB arena. ``--all-powers`` is the
test convenience of the Sektor composition builders (XP 20000 at every stage entry; needs
Powers as pickups).

Usage::

    python3 MKMSZR_build_reptile-production_composition_v02.py CLEAN.z64 MKT.z64 \\
        -o MKMSZR_reptile-production_composition_proof_v02.z64 [--all-powers] [-- CLI options]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from mkmszr.checksum import calculate_crc_6102
from mkmszr.patches.base import PatchContext
from mkmszr.patches.fighter_swap import FighterSwapPatch
from mkmszr.rom import RomImage

_sek = importlib.util.spec_from_file_location(
    "sek13", ROOT / "Experimental/SektorTransplantBuilders/production/MKMSZR_build_sektor_production_v13.py"
)
assert _sek and _sek.loader
sek13 = importlib.util.module_from_spec(_sek)
_sek.loader.exec_module(sek13)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("clean_rom", type=Path)
    p.add_argument("mkt_rom", type=Path)
    p.add_argument("-o", "--output", type=Path,
                   default=Path("MKMSZR_reptile-production_composition_proof_v02.z64"))  # fmt: skip
    p.add_argument("--seed", default="REPTILE-PROD-1")
    p.add_argument("--all-powers", action="store_true",
                   help="test convenience: every stage entry sets current XP to 20000")  # fmt: skip
    p.add_argument("cli_args", nargs="*", help="extra randomizer CLI options (after --)")
    args = p.parse_args()
    if any("specials" in a.lower() for a in args.cli_args):
        raise SystemExit("Reptile needs SPECIALS: CLASSIC")
    clean = args.clean_rom.read_bytes()
    mkt = args.mkt_rom.read_bytes()
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "base.z64"
        subprocess.run([sys.executable, "-m", "mkmszr.cli", "--mkt-rom", str(args.mkt_rom), "--seed", args.seed,
                        *args.cli_args, str(args.clean_rom), str(base)],
                       check=True, env={"PYTHONPATH": str(ROOT / "src")}, stdout=subprocess.DEVNULL)  # fmt: skip
        randomized = base.read_bytes()
    rom = RomImage(bytearray(randomized), RomImage.from_bytes(clean)._original)
    notes = FighterSwapPatch("reptile", mkt).apply(rom, PatchContext(seed=args.seed))
    data = rom.data
    if args.all_powers:
        restore_site, load, award_site, store = sek13._all_powers_sites()
        for off, old, new in ((restore_site, load, 0x34094E20), (award_site, store, 0)):
            if sek13.be32(data, off) != old:
                raise SystemExit(f"0x{off:X}: needs Powers as pickups ON")
            sek13.put32(data, off, new)
    crc1, crc2 = calculate_crc_6102(data)
    sek13.put32(data, 0x10, crc1)
    sek13.put32(data, 0x14, crc2)
    args.output.write_bytes(data)
    print(*notes, sep="\n")
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(data).hexdigest())
    print("CRC", f"{crc1:08X} / {crc2:08X}")


if __name__ == "__main__":
    main()
