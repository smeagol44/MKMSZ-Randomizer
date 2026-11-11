"""Reptile inputs proof v01 (Fighter recompiler plan, milestone 4 step 2a). Disposable.

The owner-accepted body (body proof v03) plus, all from Reptile's description and reusable
components:

* his MKT combo strings on the player's combo graph (``fighter_import.combos``): HP, HP, D+LP;
  HP, HP, HK, B+HK; HK, HK, B+HK. Records copied with relocated pointers; his combo animation
  (MKT table-1 slot 0) in host primary 0x10 (``body.slot_sources``); strike selector 0x12
  ("knocked on back", damage 10) translated to the Runtime-confirmed knockback 0x04 (damage 7);
* his MKT throw poses in the host throw script, phase by phase (``body.phase_slots``).

Special commands are step 2b. Usage::

    python3 MKMSZR_build_reptile-inputs_proof_v01.py CLEAN.z64 MKT.z64 -o MKMSZR_reptile-inputs_common_proof_v01.z64
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
from mkmszr.fighter_import import body_build, combos, common_moves, sound, voices
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

    graph = combos.donor_graph(mkt, description.donor_fighter_id)
    (table, index) = description.body.sources.get(combos.COMBO_SLOT, (0, combos.COMBO_SLOT))
    low = combos.lower(graph, index if table == 1 else None, set(description.body.slots))
    combos.install(rom, low)

    vs, samples_end = voices.install(
        rom, clean, mkt, description.donor_fighter_id, VOICE_CHAINS, SAMPLE_ROM
    )

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {"report": body.report, "voices": vs, "samples_end": samples_end, "combos": low}


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
    print("COMBOS", list(info["combos"].strings), {hex(k): hex(v) for k, v in info["combos"].strikes.items()})
    print("TEST", "debug stage select; combos and throw; Sub-Zero's specials and commands")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
