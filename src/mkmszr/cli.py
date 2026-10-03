"""Minimal developer CLI for the modular patching core."""

import argparse
from pathlib import Path

from .config import OutfitConfig, RandomizerConfig
from .donors import extract_temple_intro_audio_assets, extract_toasty_assets
from .errors import MKMSZRError
from .patcher import patch_file
from .patches.palette import PRESET_HUES
from .seed import generate_seed


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
    modes = ["vanilla", "red", "green", "rainbow", "seeded", "hue", "rgb", *PRESET_HUES]
    parser = argparse.ArgumentParser(description="MKMSZ Randomizer native ROM patcher")
    parser.add_argument("source", type=Path, help="clean MKMSZ USA Rev. 0 ROM (.z64/.v64/.n64 byte order)")
    parser.add_argument("output", type=Path, help="new disposable output .z64")
    parser.add_argument(
        "--mkt-rom",
        type=Path,
        help=("Mortal Kombat Trilogy (USA) Rev. 2 N64 donor .z64; enables "
              "donor-backed Toasty and seeded Temple intro audio"),
    )
    parser.add_argument(
        "--seed",
        help="seed string; omit to generate a random 64-bit hexadecimal seed",
    )
    parser.add_argument("--outfit", choices=modes, default="vanilla")
    parser.add_argument("--hue", type=float, help="hue in degrees for --outfit hue")
    parser.add_argument("--rgb", type=_parse_rgb, help="RRGGBB color for --outfit rgb")
    parser.add_argument(
        "--edition-name",
        default="SUB-ZERO",
        help="temporary uppercase title character name (max 12 chars)",
    )
    parser.add_argument(
        "--shuffle-power-progression",
        action="store_true",
        help="shuffle the nine Power Up unlock tiers with the accepted Ice Shatter constraint",
    )
    parser.add_argument(
        "--enemy-randomization",
        action="store_true",
        help="enable deterministic ordinary-enemy randomization using registered safe profiles",
    )
    parser.add_argument(
        "--no-powers-as-pickups",
        action="store_true",
        help="earn powers through stock XP instead of nine generated pickup rewards",
    )
    parser.add_argument(
        "--difficulty",
        choices=("very_easy", "easy", "medium", "hard", "very_hard"),
        default="very_hard",
        help="fresh-run difficulty (default: very_hard)",
    )
    parser.add_argument(
        "--lives",
        type=int,
        default=5,
        metavar="1..10",
        help="total starting lives (default: 5; max: 10)",
    )
    parser.add_argument(
        "--continues",
        type=int,
        default=3,
        metavar="0..5",
        help="starting continues (default: 3; max: 5)",
    )
    parser.add_argument(
        "--no-persist-hp",
        action="store_true",
        help="reset HP to full when leaving and re-entering a stage",
    )
    parser.add_argument(
        "--required-powers",
        choices=("vanilla", "custom", "seed"),
        default="vanilla",
        help="Fortress final XP requirement (default: stock threshold)",
    )
    parser.add_argument(
        "--global-completion",
        choices=("all_85", "game_beatable"),
        default="all_85",
        help="global seed acceptance rule (default: all_85)",
    )
    parser.add_argument(
        "--custom-required-powers",
        type=int,
        metavar="0..9",
        help="number of powers required when --required-powers custom",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.outfit == "hue" and args.hue is None:
        parser.error("--outfit hue requires --hue")
    if args.outfit == "rgb" and args.rgb is None:
        parser.error("--outfit rgb requires --rgb")
    if args.required_powers == "custom" and args.custom_required_powers is None:
        parser.error("--required-powers custom requires --custom-required-powers 0..9")
    if args.required_powers != "custom" and args.custom_required_powers is not None:
        parser.error("--custom-required-powers requires --required-powers custom")
    if args.custom_required_powers is not None and not 0 <= args.custom_required_powers <= 9:
        parser.error("--custom-required-powers must be from 0 to 9")
    if not 1 <= args.lives <= 10:
        parser.error("--lives must be from 1 to 10")
    if not 0 <= args.continues <= 5:
        parser.error("--continues must be from 0 to 5")

    effective_seed = args.seed.strip() if args.seed and args.seed.strip() else generate_seed()
    config = RandomizerConfig(
        seed=effective_seed,
        outfit=OutfitConfig(mode=args.outfit, hue_degrees=args.hue, rgb=args.rgb),
        edition_name=args.edition_name,
        shuffle_power_progression=args.shuffle_power_progression,
        enemy_randomization=args.enemy_randomization,
        powers_as_pickups=not args.no_powers_as_pickups,
        required_powers_mode=args.required_powers,
        global_completion_mode=args.global_completion,
        custom_required_powers=args.custom_required_powers,
        difficulty=args.difficulty,
        lives=args.lives,
        continues=args.continues,
        persist_hp=not args.no_persist_hp,
    )

    try:
        donor_bytes = args.mkt_rom.read_bytes() if args.mkt_rom is not None else None
        toasty_assets = extract_toasty_assets(donor_bytes) if donor_bytes is not None else None
        temple_intro_audio_assets = (
            extract_temple_intro_audio_assets(donor_bytes)
            if donor_bytes is not None
            else None
        )
        result = patch_file(
            args.source,
            args.output,
            config,
            toasty_assets=toasty_assets,
            temple_intro_audio_assets=temple_intro_audio_assets,
        )
    except (MKMSZRError, OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")

    print(f"wrote: {args.output}")
    print(f"seed: {effective_seed}")
    if result.required_powers_count is None:
        print(f"required powers: vanilla (stock XP threshold {result.required_powers_xp})")
    else:
        print(
            f"required powers: {result.required_powers_count} "
            f"(XP threshold {result.required_powers_xp}; {args.required_powers})"
        )
    for patch in result.patches:
        print(f"patch: {patch.name}")
        for note in patch.notes:
            print(f"  {note}")
    print(f"CRC1/CRC2: {result.crc1:08X} / {result.crc2:08X}")
    print(f"SHA-256: {result.output_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
