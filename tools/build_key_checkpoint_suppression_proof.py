"""Build the disposable key-checkpoint suppression proof ROM."""

from __future__ import annotations

import argparse
from pathlib import Path

from mkmszr.patches.base import PatchContext
from mkmszr.patches.key_checkpoint_proof import KeyCheckpointSuppressionProofPatch
from mkmszr.rom import RomImage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="clean MKMSZ USA Rev. 0 .z64")
    parser.add_argument("output", type=Path, help="new proof .z64")
    args = parser.parse_args()

    if args.source.resolve() == args.output.resolve():
        parser.error("output must be separate from the clean ROM")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    rom = RomImage.load(args.source, require_clean=True)
    notes = KeyCheckpointSuppressionProofPatch().apply(rom, PatchContext())
    crc1, crc2 = rom.update_header_crc()
    args.output.write_bytes(rom.to_bytes())

    print(f"wrote: {args.output}")
    for note in notes:
        print(f"  {note}")
    print(f"CRC1/CRC2: {crc1:08X} / {crc2:08X}")
    print(f"SHA-256: {rom.output_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
