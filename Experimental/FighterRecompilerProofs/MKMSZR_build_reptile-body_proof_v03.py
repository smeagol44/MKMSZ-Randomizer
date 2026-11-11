"""Reptile body proof v03 (Fighter recompiler plan, milestone 4 step 1). Disposable.

v03 is v02 with Reptile's own MKT palette: the body builder now reads the per-fighter palette
table 0x800A3660 (Reptile 0x800BE864: skin, greys and black, a green ramp). v01 and v02 read
0x800A1738, which is not indexed by fighter id past 16 and gave another fighter's palette
(owner, v02: "as if the palette was mapped wrongly"). v02 also brought ramp-aware colour
reduction, the flat lying pose and the HP/LP switch phases (owner-accepted: lying and switch).
v02's own SHA-256 reproduces at commit ``fce72cf``.

Sub-Zero's body replaced by MKT Reptile's, with nothing Reptile-specific in code:

* fighter file 0x87 from the generic body builder and Reptile's description
  (``fighters/reptile.json``: computed layout, automatic 16-colour reduction), the generic common
  animations (slide, death, long fall, pickup, grabbed) and the Run-rate edit; the file keeps its
  stock size and its stock place in ROM;
* Reptile's MKT voice set on the player's voice slots through the generic voice rule
  (``fighter_import.voices``: Sektor's accepted rule with the donor as a parameter), samples at
  ROM 0xF20000 in isolated host chains;
* the proof base of the projectile proofs (debug stage select, boot skip).

Specials stay Sub-Zero's (milestone 4 steps 2-3). Usage::

    python3 MKMSZR_build_reptile-body_proof_v03.py CLEAN.z64 MKT.z64 -o MKMSZR_reptile-body_common_proof_v03.z64
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
from mkmszr.fighter_import import body_build, common_moves, sound, voices
from mkmszr.fighter_import import description as fd
from mkmszr.fighter_import.mkt_fighter import validate_mkt_n64_rev2

_spec = importlib.util.spec_from_file_location(
    "v01", HERE / "MKMSZR_build_generic-projectile_proof_v01.py"
)
assert _spec and _spec.loader
v01 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v01)

FIGHTER = "reptile"
SAMPLE_ROM = 0x00F20000
VOICE_CHAINS = sound.ISOLATED_CHAINS[:10]  # 11-12 (host 335/336) stay for the projectile


def build(clean: bytes, mkt: bytes) -> tuple[bytes, dict]:  # type: ignore[type-arg]
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, (
        "not the clean MKMSZ USA Rev. 0 ROM"
    )
    validate_mkt_n64_rev2(mkt)
    description = fd.load(FIGHTER)
    rom = bytearray(clean)
    v01.proof_base(rom)

    body = body_build.build_body(description, clean, mkt, body_build.Extras(), rom=rom)
    file87 = common_moves.apply(bytes(body.file), stock=body.clean_file, flipped=body.flipped)
    assert len(file87) == body_build.FILE87_SIZE, hex(len(file87))
    start = body_build.FILE87_ROM
    rom[start : start + len(file87)] = file87

    vs, samples_end = voices.install(
        rom, clean, mkt, description.donor_fighter_id, VOICE_CHAINS, SAMPLE_ROM
    )

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {"report": body.report, "voices": vs, "samples_end": samples_end}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("clean", type=Path)
    parser.add_argument("mkt", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    rom, info = build(args.clean.read_bytes(), args.mkt.read_bytes())
    args.output.write_bytes(rom)
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    r = info["report"]
    print(
        "BODY",
        {
            k: (hex(v) if isinstance(v, int) else v)
            for k, v in r.items()
            if not isinstance(v, (list, dict))
        },
    )
    print("VOICES", info["voices"].category, "samples to", hex(info["samples_end"]))
    print("TEST", "debug stage select; Sub-Zero's specials with Reptile's body")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
