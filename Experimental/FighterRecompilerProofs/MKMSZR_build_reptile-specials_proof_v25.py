"""Reptile specials proof v25 (Fighter recompiler, after Rayden's milestone 6). Disposable. WITHDRAWN.

Withdrawn (owner, 2026-11-27): grab sounds are dropped for now, so this builder now gives v24's
ROM. The v25 ROM (his grab voice) is reproducible at commit 9dd5ebe.

Reptile through the generic build (``fighter_import.fighter_build.build``: body, combos, throw,
sounds, his five specials from ``fighters/moves/reptile.json``), on the specials proofs' harness
(debug stage select, boot skip, max EXP, the payload raw-loaded at 0x801AF420 from ROM 0xF10000
through file 0x1B, 16 KiB arena), as Rayden's proofs v01-v18. His v22 builder predates the
generic build.

Owner (2026-11-26, after PR #213): "Can we test this with Reptile now?" Earlier (PR #212):
Acid Spit's hit effect "sometimes shows up in a completely wrong spot". MKT's acid impact
(0x80079920) is placed as Rayden's burst: match_me_to_opponent, flip_single, multi_adjust_xy
(-153, 0), then its part 4 once (no following). The host corrections Rayden needed are now the
defaults for every "at opponent" impact (``fighter_build.impact_mirror``):

* **the enemy hit** (``impact_at_hit``, Rayden v11/v12): the splash goes to the enemy the spit
  hit, at its whole position (path, path position, x, y, z). Before, it went to the player's
  opponent at launch, which can be another enemy, and on a walkway it kept the spit's path
  position: the likely "completely wrong spot";
* **MKT's flip, art mirrored** (``impact_mirror``, Rayden v13-v15): Reptile dropped the flip
  instead (``impact_flip`` false, his v11), which also moved the splash by the offset's
  direction. Now MKT's placement, with the art mirrored around one axis;
* **the spit's own height** (``impact_keep_y``, his v13, unchanged).

Everything else is as accepted (the generic projectile art now keeps flight and impact frames
apart; Reptile's projectiles share none, so they are unaffected). Rayden's v18 ROM is
byte-identical with these defaults.

v24 (SMRE steps 1-2, 2026-11-27): his five specials are written at build time by the Special
Move Recompile Engine from his MKT command records (description ``smre``). One behaviour change
(owner: "let's remove it and have it being pure MKT"): the forceballs no longer turn to face the
opponent at the start; MKT's init_special does not turn, the hand-written programs did. Everything
else is byte-identical to v23.

v25 (owner, 2026-11-27, on Sektor SMRE v02: the throw's sounds "on by default, so for any
character that has a sound we could play it"): MKT's throw start (0x80042878) plays every
fighter's grab voice (voice group 3); the host voice rule left the throw's voice category silent.
His grab voice (MKT event 0x64) now plays at the grab of his throw (``throw_sounds``: a payload
hook on the host throw's grab voice call 0x8005BCD4, the player's throw only). His MKT throw
(0x80040234) plays no sounds of its own. Everything else is v24.

Usage::

    python3 MKMSZR_build_reptile-specials_proof_v25.py CLEAN.z64 MKT.z64 -o MKMSZR_reptile-specials_common_proof_v25.z64
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

FIGHTER = "reptile"
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
    print("TEST", "debug stage select, max EXP; Acid Spit (Ice Blast's command) on several enemies and on walkway stages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
