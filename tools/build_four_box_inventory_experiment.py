"""Build the disposable four-box inventory switching experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from mkmszr.config import RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.base import PatchContext, PatchPipeline
from mkmszr.patches.inventory_boxes import FourBoxInventoryExperimentPatch
from mkmszr.rom import RomImage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="exact clean USA .z64")
    parser.add_argument("output", type=Path, help="new disposable output .z64")
    args = parser.parse_args()

    if args.source.resolve() == args.output.resolve():
        parser.error("output must be separate from the clean ROM")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    rom = RomImage.load(args.source, require_clean=True)
    core = build_pipeline(RandomizerConfig())
    patches = (*core.patches, FourBoxInventoryExperimentPatch())
    results = PatchPipeline(patches).apply(rom, PatchContext())
    crc1, crc2 = rom.update_header_crc()

    output = rom.to_bytes()
    args.output.write_bytes(output)
    if args.output.read_bytes() != output:
        raise OSError("output read-back verification failed")

    print(f"Output: {args.output}")
    print(f"SHA-256: {rom.output_sha256}")
    print(f"CRC1 / CRC2: {crc1:08X} / {crc2:08X}")
    print("Patches:")
    for result in results:
        print(f"  - {result.name}")
        for note in result.notes:
            print(f"      {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
