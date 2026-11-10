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
from mkmszr.config import GameSettingsConfig, RandomizerConfig
from mkmszr.errors import PatchError, RomValidationError
from mkmszr.patcher import build_pipeline
from mkmszr.patches import fighter_swap as fs
from mkmszr.patches.base import PatchContext
from mkmszr.rom import RomImage

# Sektor build v60 linked for the production pool tail (fighter_import.sektor_build).
SEKTOR_BUILD_SHA256 = "28e034afc736c90a614bffd4f4f9816a9706c763bcd8593121f054d828af6b58"
# --fighter sektor --seed SEKTOR-PROD-1 --debug-all-keys == composition proof v13.
COMPOSITION_V13_SHA256 = "e1f83b25cf0e323bce151f92f36a866fca57c25fc5bb807d86cc76f39e580248"


def test_config_accepts_the_fighters_and_requires_classic_specials() -> None:
    assert RandomizerConfig().fighter == "sub-zero"
    assert RandomizerConfig(fighter="sektor").fighter == "sektor"
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
def test_cli_reproduces_composition_v13(tmp_path: Path) -> None:
    out = tmp_path / "sektor.z64"
    assert main(["--mkt-rom", DONOR, "--seed", "SEKTOR-PROD-1", "--debug-all-keys",
                 "--fighter", "sektor", CLEAN, str(out)]) == 0  # fmt: skip
    assert hashlib.sha256(out.read_bytes()).hexdigest() == COMPOSITION_V13_SHA256
