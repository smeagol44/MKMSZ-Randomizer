"""Fighter swap (``--fighter sektor``): configuration, CLI, classification tables and guards.

Synthetic tests always run. The ROM-backed acceptance tests run when the clean ROMs are
supplied through ``MKMSZR_CLEAN_ROM`` (MKMSZ USA Rev. 0) and ``MKMSZR_MKT_ROM`` (MKT USA
Rev. 2); CI has no ROMs, so they are skipped there.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from mkmszr.cli import _build_parser, main
from mkmszr.config import GameSettingsConfig, OutfitConfig, RandomizerConfig
from mkmszr.errors import PatchError, RomValidationError
from mkmszr.patcher import build_pipeline
from mkmszr.patches import fighter_swap as fs
from mkmszr.patches.base import PatchContext
from mkmszr.rom import RomImage

# Sektor build v62 (v61 + combo knockback finishers at 10 damage, owner 2026-11-11; differs from
# v61 ad2ceb4b... only in ROM 0xB1A3A and the CRCs) linked for the production pool tail
# (fighter_import.sektor_build). v60 was 28e034af...; composition proof v13 (v60) e1f83b25...
SEKTOR_BUILD_SHA256 = "e35df9c55330ff6d2ce2d19fab7c357c421e3b0884f3a4a7826ca62df95240c4"
# --fighter sektor --seed SEKTOR-PROD-1 --debug-all-keys (composition v13's config). Since SMRE step 3
# (2026-11-27) Sektor is built from his description (fighters/sektor.json: SMRE proofs v01-v15 with the
# product's slots, costs, Super Slide tier, help, icons and outfit). The legacy build v62's output
# was 0c739f81... (v61: 7fe0ed36...).
SEKTOR_CLI_SHA256 = "36d00d33171ee8f7d898273724dbadce5fec94952bcff893e434791352ad2cf7"


def test_config_accepts_the_fighters_and_requires_classic_specials() -> None:
    assert RandomizerConfig().fighter == "sub-zero"
    assert RandomizerConfig(fighter="sektor").fighter == "sektor"
    assert RandomizerConfig(fighter="reptile").fighter == "reptile"
    assert RandomizerConfig(fighter="reptile", outfit=OutfitConfig(mode="red")).fighter == "reptile"
    assert RandomizerConfig(fighter="rayden", outfit=OutfitConfig(mode="green")).fighter == "rayden"
    assert RandomizerConfig(fighter="sektor", outfit=OutfitConfig(mode="red")).fighter == "sektor"
    with pytest.raises(ValueError):
        RandomizerConfig(fighter="scorpion")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="CLASSIC"):
        RandomizerConfig(fighter="sektor", game_settings=GameSettingsConfig(specials_modern=True))
    modern_ok = RandomizerConfig(game_settings=GameSettingsConfig(specials_modern=True))
    assert modern_ok.fighter == "sub-zero"


def test_cli_fighter_option() -> None:
    parser = _build_parser()
    assert parser.parse_args(["in.z64", "out.z64"]).fighter == "sub-zero"
    assert parser.parse_args(["in.z64", "out.z64", "--fighter", "sektor"]).fighter == "sektor"
    assert parser.parse_args(["in.z64", "out.z64", "--fighter", "reptile"]).fighter == "reptile"
    assert parser.parse_args(["in.z64", "out.z64", "--fighter", "rayden"]).fighter == "rayden"
    with pytest.raises(SystemExit):
        parser.parse_args(["in.z64", "out.z64", "--fighter", "kano"])
    with pytest.raises(SystemExit):
        main(["in.z64", "out.z64", "--fighter", "sektor"])  # no --mkt-rom


def test_pipeline_needs_a_valid_donor_and_puts_the_swap_last() -> None:
    config = RandomizerConfig(seed="X", fighter="sektor")
    with pytest.raises(PatchError, match="donor"):
        build_pipeline(config)
    with pytest.raises(RomValidationError):
        build_pipeline(config, fighter_donor=bytes(16))
    assert all(p.name != "fighter-swap" for p in build_pipeline(RandomizerConfig(seed="X")).patches)


def test_every_importable_fighter_is_described() -> None:
    """Since SMRE step 3 (2026-11-27) Sektor is built from his description as Reptile and Rayden;
    the legacy transplant lists are gone."""

    assert set(fs.DESCRIBED) == set(fs.FIGHTERS) - {"sub-zero"}
    assert fs.TAIL[1] <= fs.OUTPUT_SIZE and fs.TAIL[0] >= fs.CLEAN_SIZE


def test_changed_words_scan() -> None:
    a = bytes(0x3000)
    b = bytearray(a)
    for off in (0, 0x1FFC, 0x2004):
        b[off + 1] = 1
    assert list(fs._changed_words(a, bytes(b), len(a))) == [0, 0x1FFC, 0x2004]


def test_swap_rejects_unknown_fighters_and_short_output() -> None:
    rom = RomImage(bytearray(16), bytes(16))
    with pytest.raises(PatchError, match="cannot be imported"):
        fs.FighterSwapPatch("kano", b"").apply(rom, PatchContext())
    with pytest.raises(PatchError, match="32 MiB"):
        fs.FighterSwapPatch("sektor", b"").apply(rom, PatchContext())


# ---------------------------------------------------------------- ROM-backed

CLEAN = os.environ.get("MKMSZR_CLEAN_ROM")
DONOR = os.environ.get("MKMSZR_MKT_ROM")
needs_roms = pytest.mark.skipif(not (CLEAN and DONOR), reason="needs MKMSZR_CLEAN_ROM and MKMSZR_MKT_ROM")


@needs_roms
def test_sektor_build_matches_the_proof_line() -> None:
    from mkmszr.fighter_import.sektor_build import build

    made = build(Path(CLEAN).read_bytes(), Path(DONOR).read_bytes(), fixed_va=fs.FIXED_VA)
    assert hashlib.sha256(made["rom"]).hexdigest() == SEKTOR_BUILD_SHA256
    assert made["manifest"]["fixed_va"] == fs.FIXED_VA


@needs_roms
def test_cli_sektor_build_is_pinned(tmp_path: Path) -> None:
    out = tmp_path / "sektor.z64"
    assert main(["--mkt-rom", DONOR, "--seed", "SEKTOR-PROD-1", "--debug-all-keys",
                 "--fighter", "sektor", CLEAN, str(out)]) == 0  # fmt: skip
    assert hashlib.sha256(out.read_bytes()).hexdigest() == SEKTOR_CLI_SHA256


# Reptile through the product option: the CLI output equals the owner-validated composition
# proof v03 byte for byte (Runtime-confirmed bounded, owner 2026-11-13: the forceball no longer
# hangs on the Temple monk).
# Since Reptile specials proof v23 (owner, 2026-11-26: "Acid spit works now"): the same with Acid
# Spit's splash on the enemy hit, MKT's flip and mirrored art (composition v03 was 31c22f52...).
# Since SMRE step 1 (owner, 2026-11-27): the forceballs no longer turn at the start, pure MKT
# (with the turn: 96fbf32a...).
REPTILE_CLI_SHA256 = "1296f815cfcdc5a7d01d5c2ab514739d4021b934048a034d1d52d55484a53c65"


@needs_roms
def test_cli_reptile_build_is_the_validated_composition(tmp_path: Path) -> None:
    out = tmp_path / "reptile.z64"
    assert main(["--mkt-rom", DONOR, "--seed", "REPTILE-PROD-1", "--fighter", "reptile",
                 CLEAN, str(out)]) == 0  # fmt: skip
    assert hashlib.sha256(out.read_bytes()).hexdigest() == REPTILE_CLI_SHA256


@needs_roms
def test_cli_reptile_outfit_recolours_only_his_greens(tmp_path: Path) -> None:
    from mkmszr.fighter_import.outfit import PALETTE_OFFSET

    def fighter_file(outfit: str) -> bytes:
        out = tmp_path / f"reptile-{outfit}.z64"
        assert main(["--mkt-rom", DONOR, "--seed", "REPTILE-PROD-1", "--fighter", "reptile",
                     "--outfit", outfit, CLEAN, str(out)]) == 0  # fmt: skip
        rom = out.read_bytes()
        entry = 0x000A5010 + 0x87 * 12
        start, end = (int.from_bytes(rom[entry + k : entry + k + 4], "big") for k in (0, 4))
        return rom[start:end]

    vanilla, purple = fighter_file("vanilla"), fighter_file("purple")
    changed = {(i - PALETTE_OFFSET) // 2 for i in range(len(vanilla)) if vanilla[i] != purple[i]}
    assert changed == {10, 11, 12, 13, 14}  # his greens; skin, greys and black stay


# Rayden through the product option (milestone 6; Pending the owner's full-seed run): his payload
# blob no longer fits the fighter file's body tail (his move art fills it), so it is appended to
# the file inside the runtime-confirmed file budget (body_build.SAFE_END, v49); his samples need
# the enlarged generated-output tail [0x01820000, 0x01880000).
@needs_roms
def test_cli_rayden_build_places_his_blob_and_samples(tmp_path: Path) -> None:
    from mkmszr.fighter_import import body_build
    from mkmszr.fighter_import.outfit import PALETTE_OFFSET
    from mkmszr.patches.fighter_swap import TAIL

    def build(outfit: str) -> bytes:
        out = tmp_path / f"rayden-{outfit}.z64"
        assert main(["--mkt-rom", DONOR, "--seed", "RAYDEN-PROD-1", "--fighter", "rayden",
                     "--outfit", outfit, CLEAN, str(out)]) == 0  # fmt: skip
        return out.read_bytes()

    rom = build("vanilla")
    entry = 0x000A5010 + 0x87 * 12
    start, end = (int.from_bytes(rom[entry + k : entry + k + 4], "big") for k in (0, 4))
    assert start == TAIL[0] and body_build.FILE87_SIZE < end - start < body_build.SAFE_END
    assert set(rom[TAIL[1] : TAIL[1] + 0x1000]) == {0xFF}
    vanilla, red = rom[start:end], build("red")[start:end]
    changed = {(i - PALETTE_OFFSET) // 2 for i in range(len(vanilla)) if vanilla[i] != red[i]}
    assert changed == {2, 3, 4}  # his blue tunic only
