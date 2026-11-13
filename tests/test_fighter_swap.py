"""Fighter swap (``--fighter sektor``): configuration, CLI, classification tables and guards.

Synthetic tests always run. The ROM-backed acceptance tests run when the clean ROMs are
supplied through ``MKMSZR_CLEAN_ROM`` (MKMSZ USA Rev. 0) and ``MKMSZR_MKT_ROM`` (MKT USA
Rev. 2); CI has no ROMs, so they are skipped there.
"""

from __future__ import annotations

import hashlib
import os
from itertools import pairwise
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
# --fighter sektor --seed SEKTOR-PROD-1 --debug-all-keys (composition v13's config). Build v62:
# differs from the v61 output 7fe0ed36... only in ROM 0xB1A3A and the CRCs.
SEKTOR_CLI_SHA256 = "0c739f81669f2f02b11fe99f290ebe9b6353ac5f491b623be48fd12ee17395a2"


def test_config_accepts_the_fighters_and_requires_classic_specials() -> None:
    assert RandomizerConfig().fighter == "sub-zero"
    assert RandomizerConfig(fighter="sektor").fighter == "sektor"
    assert RandomizerConfig(fighter="reptile").fighter == "reptile"
    with pytest.raises(ValueError, match="outfit"):
        RandomizerConfig(fighter="reptile", outfit=OutfitConfig(mode="red"))
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
    with pytest.raises(SystemExit):
        main(["in.z64", "out.z64", "--fighter", "reptile", "--mkt-rom", "m.z64", "--outfit", "red"])
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


def test_classification_tables_are_disjoint() -> None:
    transplant = set(fs.TRANSPLANT_SITES)
    assert not transplant & fs.DERIVED_SITES and not transplant & fs.DROP_SITES
    assert not fs.DERIVED_SITES & fs.DROP_SITES
    for site in transplant | fs.DERIVED_SITES | fs.DROP_SITES:
        assert site % 4 == 0
        assert not (fs._in(site, fs.DROP_RANGES) and fs._in(site, fs.TRANSPLANT_RANGES)), hex(site)
    for a, b in (*fs.TRANSPLANT_RANGES, *fs.DROP_RANGES):
        assert a < b and a % 4 == 0 and b % 4 == 0
    spans = sorted((*fs.TRANSPLANT_RANGES, *fs.DROP_RANGES))
    assert all(x[1] <= y[0] for x, y in pairwise(spans))
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
REPTILE_CLI_SHA256 = "31c22f522fe98cbc3230793b405a64b65ff7ec5f9310b301242d1761db23d93c"


@needs_roms
def test_cli_reptile_build_is_the_validated_composition(tmp_path: Path) -> None:
    out = tmp_path / "reptile.z64"
    assert main(["--mkt-rom", DONOR, "--seed", "REPTILE-PROD-1", "--fighter", "reptile",
                 CLEAN, str(out)]) == 0  # fmt: skip
    assert hashlib.sha256(out.read_bytes()).hexdigest() == REPTILE_CLI_SHA256
