"""Sektor SMRE proof v02 (SMRE step 3, Sektor's base on the generic build). Disposable.

Sektor built by the generic fighter build (``fighter_import.fighter_build.build``) from the
migration description ``fighters/sektor-smre.json``, with no special moves yet: the base the
moves are then added to one at a time (owner, 2026-11-27: "start with Sektor. Let's do 1 move
at a time"). The product Sektor (``fighters/sektor.json`` and its frozen legacy build) is not
touched. Harness: the specials proofs' (debug stage select, boot skip, max EXP, the payload
raw-loaded at 0x801AF420 from ROM 0xF10000 through file 0x1B: Rayden specials proof v31's).

What the generic build gives him, and how it differs from the accepted (legacy) Sektor:

* **body**: the computed layout (as Reptile and Rayden), his accepted 16-colour map and palette;
  the generic recipes (slide, death, long fall, pickup, grabbed) as before;
* **throw**: MKT's own throw script (table 0 slot 0x23). It draws his mechanical arm as a
  second actor (MKT token 11 creates it from frame 0x2300, tokens 12/14 step it), with its own
  palette MECARM_P (0x800BC310). New generic rule (``body_build.phase_slot_frames``): each step
  shows one flattened frame, the arm over his pose, the arm's colours mapped to his nearest body
  colours. New phase mode ``scale``: MKT's 4 windup, 4 arm-out and 8 swing frames scaled over
  the host's first 7 positions, the 8 retract frames over its last 2 (the legacy throw used
  seven hand-picked arm poses);
* **combos**: MKT's own combo graph (``HP, HP, HK, B+HK``; ``HP, HP, HK, HK, B+HK``; ``HP, HP,
  D+LP``; ``HK, HK``): seven records on the host's six, so the last option list goes into the
  payload (``combos.lower(overflow_va=...)``), as the legacy build kept his HK,HK record there;
  the legacy elbow-combo presentation (slot 0x10 hand-ordered) is now MKT table 0 slot 0x10;
* **voices**: the generic voice rule (as before);
* **specials**: none. Sub-Zero's Ice Blast, Directional Ice (up and down), Ice Clone and Freeze
  on Contact are removed (``remove_commands``); Slide, Super Slide and Polar Blast stay.

v02 (owner on v01, 2026-11-27: throw, combos and body "all looking good", but "the throw is
missing its sound"): MKT's throw table ``0x800A7ED8`` (by fighter id) gives Sektor's throw
``0x80042498``, which plays his sounds 0 (arm out), 1 (arm throw) and 2 (arm in) around the grab,
the throw and the victim's transfer; its start (``0x80042878``) plays the grab voice (voice group
3, event 0x67) for every fighter. The host voice rule leaves the throw's voice category silent.
New generic ``throw_sounds``: the throw routine's own sounds are read from MKT and played by
payload hooks on the host throw's three stages (the legacy build's sites and wrappers, proof
v41: grab voice call 0x8005BCD4, throw phase 0x8005BDC8, finish 0x8005BDF8), and
``body.throw_voice`` adds the grab voice (on for Sektor; Reptile's and Rayden's MKT throws play
no sounds of their own, and their grab voice is left off until the owner decides).

Usage::

    python3 MKMSZR_build_sektor-smre_proof_v02.py CLEAN.z64 MKT.z64 -o MKMSZR_sektor-smre_common_proof_v02.z64
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

_spec = importlib.util.spec_from_file_location("rayden_v31", HERE / "MKMSZR_build_rayden-specials_proof_v31.py")
assert _spec and _spec.loader
rayden_v31 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rayden_v31)
v01 = rayden_v31.v01

FIGHTER = "sektor-smre"


def build(clean: bytes, mkt: bytes) -> tuple[bytes, fb.Built]:
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, "not the clean MKMSZ USA Rev. 0 ROM"
    built = fb.build(clean, mkt, FIGHTER)
    rom = bytearray(built.rom)
    v01.proof_base(rom)
    rayden_v31.harness(rom)
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
    print("COMBOS", built.report["combos"], "THROW SOUNDS", built.report.get("throw_sounds"), "PAYLOAD", hex(len(built.payload)))
    print("TEST", "debug stage select, max EXP; the throw's sounds: grab voice and arm out at the grab, "
          "arm throw before the throw, arm in at the release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
