"""Minimal developer CLI for the modular patching core."""

import argparse
from pathlib import Path

from .config import OutfitConfig, RandomizerConfig
from .errors import MKMSZRError
from .patcher import patch_file
from .patches.palette import PRESET_HUES


def _parse_rgb(value: str) -> tuple[int, int, int]:
    text = value.strip().removeprefix("#")
    if len(text) != 6:
        raise argparse.ArgumentTypeError("RGB color must be RRGGBB or #RRGGBB")
    try:
        red, green, blue = (int(text[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("RGB color contains non-hex characters") from exc
    return red, green, blue


def _build_parser() -> argparse.ArgumentParser:
    modes = ["vanilla", "red", "green", "seeded", "hue", "rgb", *PRESET_HUES]
    parser = argparse.ArgumentParser(description="MKMSZ Randomizer native ROM patcher")
    parser.add_argument("source", type=Path, help="clean MKMSZ USA Rev. 0 .z64 ROM")
    parser.add_argument("output", type=Path, help="new disposable output .z64")
    parser.add_argument("--seed", help="seed string; controls boot message and seeded features")
    parser.add_argument("--outfit", choices=modes, default="vanilla")
    parser.add_argument("--hue", type=float, help="hue in degrees for --outfit hue")
    parser.add_argument("--rgb", type=_parse_rgb, help="RRGGBB color for --outfit rgb")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.outfit == "hue" and args.hue is None:
        parser.error("--outfit hue requires --hue")
    if args.outfit == "rgb" and args.rgb is None:
        parser.error("--outfit rgb requires --rgb")
    if args.outfit == "seeded" and args.seed is None:
        parser.error("--outfit seeded requires --seed")

    config = RandomizerConfig(
        seed=args.seed,
        outfit=OutfitConfig(mode=args.outfit, hue_degrees=args.hue, rgb=args.rgb),
    )

    try:
        result = patch_file(args.source, args.output, config)
    except (MKMSZRError, OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")

    print(f"wrote: {args.output}")
    for patch in result.patches:
        print(f"patch: {patch.name}")
        for note in patch.notes:
            print(f"  {note}")
    print(f"CRC1/CRC2: {result.crc1:08X} / {result.crc2:08X}")
    print(f"SHA-256: {result.output_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
