"""Reptile's Power Ups icons from his description (fighter_import.fighter_icons)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import description as fd
from mkmszr.fighter_import import fighter_icons as fi
from mkmszr.patches.power_order import POWER_ICONS, POWER_NAMES

CLEAN, MKT = os.environ.get("MKMSZR_CLEAN_ROM"), os.environ.get("MKMSZR_MKT_ROM")
needs_roms = pytest.mark.skipif(not (CLEAN and MKT), reason="needs MKMSZR_CLEAN_ROM and MKMSZR_MKT_ROM")


def _package(rom: bytes) -> bytes:
    from mkmszr.data.addresses import FILE_TABLE_ENTRY_SIZE, FILE_TABLE_ROM
    from mkmszr.resource_materialization import decompress_resource_package

    entry = FILE_TABLE_ROM + fi.BANK_FILE * FILE_TABLE_ENTRY_SIZE
    start, end = (int.from_bytes(rom[entry + k : entry + k + 4], "big") for k in (0, 4))
    return decompress_resource_package(rom[start:end])


@needs_roms
def test_reptile_icons_replace_his_slots_only() -> None:
    clean, mkt = Path(CLEAN).read_bytes(), Path(MKT).read_bytes()
    rom = bytearray(clean)
    fi.apply(rom, mkt, 19, fd.load("reptile").icons)
    before, after = fi.stock_icons(_package(clean)), fi.stock_icons(_package(bytes(rom)))
    changed = {name for name, image in POWER_ICONS.items() if before[image] != after[image]}
    assert changed >= set(POWER_ICONS) - {"polar-blast"}
    # Polar Blast stays stock (deferred, owner): same colours, re-indexed into the shared palette.
    pal = lambda r: [fi.bgr555_to_rgb(int.from_bytes(r[fi.PALETTE_ROM + 4 + 2 * i : fi.PALETTE_ROM + 6 + 2 * i], "big"))
                     for i in range(fi.PALETTE_COUNT)]  # fmt: skip
    old, new = pal(clean), pal(bytes(rom))
    polar = POWER_ICONS["polar-blast"]
    error = sum(abs(a - b) for p, q in zip(before[polar], after[polar], strict=True)
                for a, b in zip(old[p], new[q], strict=True)) / (3 * len(before[polar]))  # fmt: skip
    assert error < 12
    mask = [p != 0 for p in before[POWER_ICONS["ice-blast"]]]
    for image in after.values():  # the stock circle, every icon
        assert [p != 0 for p in image] == mask
    assert int.from_bytes(rom[fi.PALETTE_ROM : fi.PALETTE_ROM + 4], "big") == fi.PALETTE_COUNT


@needs_roms
def test_every_layer_fits_its_crop() -> None:
    mkt = Path(MKT).read_bytes()
    recipe = fd.load("reptile").icons
    d = fi._Donor(mkt, 19)
    for name, spec in recipe["slots"].items():
        if isinstance(spec, str):
            continue
        x0, y0, size = spec["crop"]
        for layer in spec["layers"]:
            f, _ = fi._layer_frame(d, layer)
            points = [(x - f.anchor_x + int(layer.get("dx", 0)), y - f.anchor_y + int(layer.get("dy", 0)))
                      for y in range(f.height) for x in range(f.width) if f.indices[y * f.stride + x]]  # fmt: skip
            inside = sum(x0 <= x < x0 + size and y0 <= y < y0 + size for x, y in points)
            assert inside >= 0.98 * len(points), (name, layer)


def test_description_rejects_a_bad_icon_recipe() -> None:
    import copy
    import json
    from importlib import resources

    raw = json.loads(resources.files("mkmszr.fighters").joinpath("reptile.json").read_text())
    data = copy.deepcopy(raw)
    del data["icons"]["slots"]["slide"]
    with pytest.raises(fd.DescriptionError, match="icons"):
        fd.validate(data)


@needs_roms
def test_reptile_help_text() -> None:
    from mkmszr.fighter_import import fighter_help, power_help

    clean = Path(CLEAN).read_bytes()
    rom = bytearray(clean)
    for off, blob in fighter_help.edits(bytes(rom), clean, fd.load("reptile").help).items():
        rom[off : off + len(blob)] = blob
    shown = dict(zip(POWER_NAMES, power_help.read_help(bytes(rom)), strict=True))
    stock = dict(zip(POWER_NAMES, power_help.read_help(clean), strict=True))
    assert shown["ice-blast"][0] == ("ACID SPIT",) and shown["ice-shatter"][0] == ("REVERSE ELBOW",)
    assert shown["freeze-on-contact"][1] == ("UP, DOWN,", "HIGH KICK.")
    assert shown["air-ice-blast"] == power_help.EMPTY
    for name in ("slide", "super-slide", "polar-blast"):
        assert shown[name] == stock[name]


def test_reptile_costs_come_from_his_description() -> None:
    import copy
    import json
    from importlib import resources

    assert fd.load("reptile").costs == {"forceball_fast": 0x30, "forceball_slow": 0x30, "invisibility": 0x40}
    raw = json.loads(resources.files("mkmszr.fighters").joinpath("reptile.json").read_text())
    for change in ({"forceball_fast": "0xA7"}, {"no_such_move": 1}):
        data = copy.deepcopy(raw)
        data["costs"] = change
        with pytest.raises(fd.DescriptionError, match="costs"):
            fd.validate(data)
    data = copy.deepcopy(raw)
    data["help"]["slide"] = [["far too long a title line"]]
    with pytest.raises(fd.DescriptionError, match="help"):
        fd.validate(data)
