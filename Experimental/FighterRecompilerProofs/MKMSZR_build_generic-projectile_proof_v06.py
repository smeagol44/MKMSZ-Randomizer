"""Generic projectile proof v06 (Fighter recompiler plan, milestone 2 task 8). Disposable.

Owner runtime results for v05 (2026-11-11): height right; looks and sounds very good; the ball is
still a bit far forward; the flight animation, its loop and the hum play too fast.

v06 is v05 with:

* spawn x offset -60 world units (v05: -20): the ball about 20 px closer;
* donor timing one host tick per MKT process tick (v02-v05 assumed two MKT ticks per host tick):
  flight and impact frames 3 host ticks each (MKT rate 3), the hum every 3 host ticks (MKT
  ``forceball_hum``). The owner's "twice too fast" matches the earlier Sektor finding (proofs
  v35-v41: MKT puffs about twice as slow) on the open MKT process-tick-rate question. The flight
  speed keeps the accepted rocket conversion.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(
        name, HERE / f"MKMSZR_build_generic-projectile_proof_{name}.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v05 = _load("v05")
v05.DX = -60
v05.HUM_STEP = 1  # every 3 host ticks
v05.v02.DONOR_RATE = 6  # the file builder assumes 2 donor ticks per host tick: 6 -> 3 host ticks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("clean", type=Path)
    parser.add_argument("mkt", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    rom, info = v05.build(args.clean.read_bytes(), args.mkt.read_bytes())
    args.output.write_bytes(rom)
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    print("PAYLOAD", hex(info["payload_len"]), "SPAWN", (v05.DX, v05.DY))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
