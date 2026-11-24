"""Rayden inputs proof v01 (Fighter recompiler plan, milestone 6; Reptile's step 2). Disposable.

Body proof v01 (owner, 2026-11-13: "The sprites look very good") plus:

* his getup sound (owner: "the same as the teleport"): MKT's Rayden-only getup helper
  ``0x80053AE8`` plays his fighter sound 7. ``body.script_sounds`` starts his getup and sweep
  getup scripts with host callback 2 on the spare descriptor 0x2A, whose event 41 takes that
  sound (``voices.install_script_sound``);
* his MKT combo strings through the generic ``fighter_import.combos``: ``HP, HP, LP, LP``,
  ``HK, HK, LK, B+HK`` and ``HK, LK, B+HK``. One option after ``HP, HP`` ends in his torpedo
  routine (``0x8004F3C0``), a combo into a special the host graph cannot call: left out until
  the torpedo special exists;
* his MKT throw poses in the host throw script (``body.phase_slots`` ``shift:+1``, Reptile's
  accepted rule; to be judged).

His special commands stay Sub-Zero's here: Lightning (D,F + LP) is Ice Blast's own input; the
teleport (D,U) and torpedo (B,B,F) are stick-only commands and the shocker a High Punch
release, which need a new host input hook (next). Usage::

    python3 MKMSZR_build_rayden-inputs_proof_v01.py CLEAN.z64 MKT.z64 -o MKMSZR_rayden-inputs_common_proof_v01.z64
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

FIGHTER = "rayden"
SAMPLE_ROM = 0x00F20000
VOICE_CHAINS = sound.ISOLATED_CHAINS[:10]
SCRIPT_SOUND_CHAIN = sound.ISOLATED_CHAINS[10]


def build(clean: bytes, mkt: bytes) -> tuple[bytes, dict]:  # type: ignore[type-arg]
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, (
        "not the clean MKMSZ USA Rev. 0 ROM"
    )
    validate_mkt_n64_rev2(mkt)
    description = fd.load(FIGHTER)
    rom = bytearray(clean)
    v01.proof_base(rom)

    body = body_build.build_body(description, clean, mkt, body_build.Extras(), rom=rom)
    file87 = common_moves.apply(bytes(body.file), stock=body.clean_file, flipped=body.flipped,
                                slide="slide" in description.body.common_animations)  # fmt: skip
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
    (sfx,) = set(description.body.script_sounds.values())
    samples_end = voices.install_script_sound(rom, clean, mkt, description.donor_fighter_id, sfx,
                                              SCRIPT_SOUND_CHAIN, samples_end, vs)  # fmt: skip

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {"report": body.report, "voices": vs, "samples_end": samples_end,
                        "combos": low, "dropped": graph.dropped}  # fmt: skip


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
    print("BODY", {k: (hex(v) if isinstance(v, int) else v) for k, v in r.items() if not isinstance(v, (list, dict))})
    print("VOICES", info["voices"].category, "samples to", hex(info["samples_end"]))
    print("COMBOS", list(info["combos"].strings), {hex(k): hex(v) for k, v in info["combos"].strikes.items()},
          "left out:", [(hex(a), hex(b)) for a, b in info["dropped"]])  # fmt: skip
    print("TEST", "debug stage select; Rayden's combos, throw and getup sound; Sub-Zero's specials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
