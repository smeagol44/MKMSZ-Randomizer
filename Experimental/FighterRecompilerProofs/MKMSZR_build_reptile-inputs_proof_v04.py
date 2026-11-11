"""Reptile inputs proof v04 (Fighter recompiler plan, milestone 4 step 2b). Disposable.

v03 (owner-accepted combos, combo animation and throw) plus Reptile's MKT special commands
calling the Sub-Zero powers they replace (``fighter_import.commands``, the description's
``commands``): Acid Spit (F,F + HP) -> Ice Blast, Forceball fast (F,F + HP+LP) -> Directional
Ice down, Forceball slow (B,B + HP+LP) -> Ice Clone, Invisibility (U,D + HK) -> Freeze on
Contact; Reverse Elbow (B,F + LK) has no action yet (Ice Shatter has no command record).
Directional Ice up is removed; Spine Rip and Polar Blast keep their commands; Slide and Super
Slide keep the host's direct recognizers. The HP table (five records) moves to the v6 proof
arena with its load pair repointed; the forceballs' both-buttons check is a stub that hands the
rest of the table back to the parser (MKT order). The v6 infrastructure also sets maximum EXP,
so every power is unlocked. Usage::

    python3 MKMSZR_build_reptile-inputs_proof_v04.py CLEAN.z64 MKT.z64 -o MKMSZR_reptile-inputs_common_proof_v04.z64
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
from mkmszr.fighter_import import (
    body_build,
    combos,
    commands,
    common_moves,
    components,
    sound,
    voices,
)
from mkmszr.fighter_import import description as fd
from mkmszr.fighter_import.mkt_fighter import validate_mkt_n64_rev2

_spec = importlib.util.spec_from_file_location(
    "v01", HERE / "MKMSZR_build_generic-projectile_proof_v01.py"
)
assert _spec and _spec.loader
v01 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v01)
_spec5 = importlib.util.spec_from_file_location(
    "v05", HERE / "MKMSZR_build_generic-projectile_proof_v05.py"
)
assert _spec5 and _spec5.loader
v05 = importlib.util.module_from_spec(_spec5)
_spec5.loader.exec_module(v05)
STUB_OFFSET = 0x100  # stubs after the moved tables in the arena

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

    v05.v6_infrastructure(rom)
    moves, _ = components.load_programs(FIGHTER)
    cmds = commands.donor_commands(mkt, moves, description.commands)
    low_cmd = commands.lower(clean, cmds, set(description.remove_commands), v01.PAYLOAD_VA,
                             v01.PAYLOAD_VA + STUB_OFFSET)  # fmt: skip
    arena = rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v05.PAYLOAD_LIMIT]
    assert set(arena) == {0xFF}
    rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v05.PAYLOAD_LIMIT] = bytes(v05.PAYLOAD_LIMIT)
    commands.install(rom, clean, low_cmd, v01.PAYLOAD_ROM, v01.PAYLOAD_VA)
    stubs = v01.PAYLOAD_ROM + STUB_OFFSET
    assert all(v < v01.PAYLOAD_VA + STUB_OFFSET for v in low_cmd.moved.values())
    assert STUB_OFFSET + len(low_cmd.stubs) <= v05.PAYLOAD_LIMIT
    rom[stubs : stubs + len(low_cmd.stubs)] = low_cmd.stubs

    vs, samples_end = voices.install(
        rom, clean, mkt, description.donor_fighter_id, VOICE_CHAINS, SAMPLE_ROM
    )

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {"report": body.report, "voices": vs, "samples_end": samples_end, "combos": low, "commands": low_cmd}


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
    print("COMMANDS", *info["commands"].report, sep="\n  ")
    print("TEST", "debug stage select, max EXP; Reptile's commands calling Sub-Zero's specials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
