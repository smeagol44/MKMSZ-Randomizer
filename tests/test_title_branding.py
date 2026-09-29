import hashlib

import pytest

from mkmszr.config import OutfitConfig
from mkmszr.patches import title_branding as title
from mkmszr.patches.base import PatchContext
from mkmszr.patches.palette import SubZeroPalettePatch, make_hue
from mkmszr.rom import RomImage


def test_title_character_name_defaults_and_uppercases() -> None:
    assert title.normalize_edition_name(None) == title.DEFAULT_EDITION_NAME
    assert title.normalize_edition_name("") == title.DEFAULT_EDITION_NAME
    assert title.normalize_edition_name("  sub-zero  ") == "SUB-ZERO"
    assert title.normalize_edition_name("noob  saibot") == "NOOB SAIBOT"
    assert title.edition_text("sektor") == "SEKTOR EDITION"


def test_title_character_name_is_bounded_and_ascii_safe() -> None:
    assert title.normalize_edition_name("A" * title.EDITION_NAME_MAX_LENGTH) == (
        "A" * title.EDITION_NAME_MAX_LENGTH
    )

    with pytest.raises(ValueError):
        title.normalize_edition_name("A" * (title.EDITION_NAME_MAX_LENGTH + 1))
    with pytest.raises(ValueError):
        title.normalize_edition_name("SUB_ZERO")
    with pytest.raises(ValueError):
        title.normalize_edition_name("SCORPION!")


def test_typeset_asset_is_exact_native_16color_pixel_image() -> None:
    pixels = title._title_pixels()
    assert len(pixels) == 320 * 240
    assert hashlib.sha256(pixels).hexdigest() == (
        "280b9d838be6df2c65cb09fd2404d6b37ced89a29b879494c76ebe8cf1de4fd7"
    )
    assert set(pixels) <= set(title.TITLE_16COLOR_INDICES)
    assert set(pixels[113 * 320 : 140 * 320]) == {title.TITLE_BACKGROUND_INDEX}


def test_16color_title_palette_contract_is_shared_with_edition_text() -> None:
    assert len(title.TITLE_16COLOR_INDICES) == 16
    assert len(set(title.TITLE_16COLOR_INDICES)) == 16
    assert title.TITLE_16COLOR_INDICES[0] == title.TITLE_BACKGROUND_INDEX == 255
    assert title.TITLE_16COLOR_INDICES[1:] == title.EDITION_PALETTE_INDICES
    assert title.EDITION_PALETTE_WORDS == (
        0x0821, 0x0C41, 0x1881, 0x2CE2, 0x3D41,
        0x3D44, 0x45A6, 0x5E28, 0x628F, 0x6ED1,
        0x7732, 0x7B75, 0x7778, 0x7FB8, 0x7BDB,
    )


@pytest.mark.parametrize(
    "outfit",
    [
        OutfitConfig(mode="purple"),
        OutfitConfig(mode="hue", hue_degrees=123.0),
        OutfitConfig(mode="rgb", rgb=(192, 90, 25)),
        OutfitConfig(mode="seeded"),
    ],
)
def test_title_palette_matches_clothing_transform(outfit: OutfitConfig) -> None:
    context = PatchContext(seed="TITLE-COLOR-SEED")
    recolor = SubZeroPalettePatch(
        outfit.mode, hue_degrees=outfit.hue_degrees, rgb=outfit.rgb
    )
    assert title._palette_words_for_outfit(outfit, context) == tuple(
        recolor._transform(word, context) for word in title.EDITION_PALETTE_WORDS
    )
    assert title._palette_words_for_outfit(OutfitConfig(), context) == (
        title.EDITION_PALETTE_WORDS
    )


@pytest.mark.parametrize("mode,hue", [("red", 0.0), ("green", 120.0)])
def test_red_green_title_hue_matches_outfit_target(mode: str, hue: float) -> None:
    assert title._palette_words_for_outfit(OutfitConfig(mode=mode), PatchContext()) == (
        tuple(make_hue(word, hue) for word in title.EDITION_PALETTE_WORDS)
    )


def test_fixed_rainbow_keeps_native_index_budget_and_blue_plaque() -> None:
    pixels = bytearray(title._title_pixels())
    title._render_edition(pixels, "SEKTOR")
    original = pixels[:]
    title._fixed_rainbow_pixels(pixels)
    assert len(title.RAINBOW_PALETTE_WORDS) == 15
    assert set(pixels) <= set(title.TITLE_16COLOR_INDICES)
    assert pixels[:39 * 320] == original[:39 * 320]
    assert pixels[140 * 320:] == original[140 * 320:]
    assert pixels[80 * 320:100 * 320] != original[80 * 320:100 * 320]
    assert pixels[115 * 320:128 * 320] != original[115 * 320:128 * 320]
    assert set(pixels[40 * 320:70 * 320]) <= (
        {title.TITLE_BACKGROUND_INDEX} | set(title.EDITION_PALETTE_INDICES[:5])
    )


def test_embedded_edition_font_covers_all_allowed_input() -> None:
    glyphs = title._edition_font()
    required = set(title.EDITION_ALLOWED).union(title.EDITION_SUFFIX)
    assert required <= set(glyphs)


def test_baked_edition_uses_only_reserved_indices() -> None:
    before = title._title_pixels()
    after = bytearray(before)

    title._render_edition(after, "sektor")

    changed = [new for old, new in zip(before, after, strict=True) if old != new]
    assert changed
    assert set(changed) <= set(title.EDITION_PALETTE_INDICES)
    assert title.TITLE_EDITION_BASELINE_Y == 126


def test_worst_width_temporary_name_fits_canvas() -> None:
    pixels = bytearray(title._title_pixels())
    title._render_edition(pixels, "W" * title.EDITION_NAME_MAX_LENGTH)


def test_title_lzw_round_trip() -> None:
    raw = (bytes(range(256)) * 40) + (b"RANDOMIZER" * 500)
    encoded = title._lzw_compress(raw)
    assert encoded[:4] == len(raw).to_bytes(4, "big")
    assert title._lzw_decompress(encoded) == raw


def test_title_allocation_is_bounded_to_stock_file_slot() -> None:
    assert title.TITLE_STOCK_CAPACITY == 0x2F3E0
    assert not hasattr(title, "TITLE_WRAPPER_ROM")
    assert not hasattr(title, "TITLE_HOOK_ROM")


def test_title_patch_replaces_stock_package_without_code_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = bytearray(16 * 1024 * 1024)
    data[title.TITLE_FILE_ENTRY_ROM : title.TITLE_FILE_ENTRY_ROM + 12] = (
        title.TITLE_STOCK_ROM_START.to_bytes(4, "big")
        + title.TITLE_STOCK_ROM_END.to_bytes(4, "big")
        + title.TITLE_STOCK_FLAG.to_bytes(4, "big")
    )
    data[title.TITLE_STOCK_ROM_START : title.TITLE_STOCK_ROM_END] = (
        b"\xA6" * title.TITLE_STOCK_CAPACITY
    )
    for index, expected in zip(
        title.EDITION_PALETTE_INDICES,
        title.EDITION_PALETTE_EXPECTED,
        strict=True,
    ):
        offset = title.TITLE_PALETTE_ROM + index * 2
        data[offset : offset + 2] = expected.to_bytes(2, "big")

    # Preserve the stock START setup as a negative control.
    hook_rom = 0x00079C24
    stock_hook = bytes.fromhex("3C04800B 2484ED1C")
    data[hook_rom : hook_rom + 8] = stock_hook
    rom = RomImage(data=data, _original=bytes(data))

    fake_package = bytes([0xA5]) * 0x80
    monkeypatch.setattr(
        title,
        "TITLE_STOCK_SHA256",
        hashlib.sha256(b"\xA6" * title.TITLE_STOCK_CAPACITY).hexdigest(),
    )
    monkeypatch.setattr(
        title,
        "_build_title_package",
        lambda _stock, _name, *, fixed_rainbow: fake_package,
    )

    title.TitleBrandingPatch("sektor").apply(rom, PatchContext())

    assert rom.data[hook_rom : hook_rom + 8] == stock_hook
    assert rom.read_u32(title.TITLE_FILE_ENTRY_ROM) == title.TITLE_STOCK_ROM_START
    assert rom.read_u32(title.TITLE_FILE_ENTRY_ROM + 4) == (
        title.TITLE_STOCK_ROM_START + len(fake_package)
    )
    assert rom.data[
        title.TITLE_STOCK_ROM_START : title.TITLE_STOCK_ROM_START + len(fake_package)
    ] == fake_package
    assert rom.data[
        title.TITLE_STOCK_ROM_START + len(fake_package) : title.TITLE_STOCK_ROM_END
    ] == b"\xA6" * (title.TITLE_STOCK_CAPACITY - len(fake_package))
