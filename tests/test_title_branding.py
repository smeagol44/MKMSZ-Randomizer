import hashlib

import pytest

from mkmszr.patches import title_branding as title
from mkmszr.patches.base import PatchContext
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


def test_candidate_b_asset_is_exact_native_pixel_image() -> None:
    pixels = title._candidate_pixels()
    assert len(pixels) == 320 * 240
    assert hashlib.sha256(pixels).hexdigest() == (
        "480bd0b816068feb82075747b0b2abb4e5c790c5970b156915fd363efd14d80b"
    )
    assert not set(pixels).intersection(title.EDITION_PALETTE_INDICES)


def test_embedded_edition_font_covers_all_allowed_input() -> None:
    glyphs = title._edition_font()
    required = set(title.EDITION_ALLOWED).union(title.EDITION_SUFFIX)
    assert required <= set(glyphs)


def test_baked_edition_uses_only_reserved_indices() -> None:
    before = title._candidate_pixels()
    after = bytearray(before)

    title._render_edition(after, "sektor")

    changed = [new for old, new in zip(before, after, strict=True) if old != new]
    assert changed
    assert set(changed) <= set(title.EDITION_PALETTE_INDICES)
    assert title.TITLE_EDITION_BASELINE_Y == 126


def test_worst_width_temporary_name_fits_canvas() -> None:
    pixels = bytearray(title._candidate_pixels())
    title._render_edition(pixels, "W" * title.EDITION_NAME_MAX_LENGTH)


def test_title_lzw_round_trip() -> None:
    raw = (bytes(range(256)) * 40) + (b"RANDOMIZER" * 500)
    encoded = title._lzw_compress(raw)
    assert encoded[:4] == len(raw).to_bytes(4, "big")
    assert title._lzw_decompress(encoded) == raw


def test_title_allocation_is_bounded_high_rom_data_only() -> None:
    assert title.TITLE_RELOCATED_ROM == 0x00F90000
    assert title.TITLE_RELOCATED_CAPACITY == 0x31000
    assert title.TITLE_RELOCATED_LIMIT <= 0x01000000
    assert not hasattr(title, "TITLE_WRAPPER_ROM")
    assert not hasattr(title, "TITLE_HOOK_ROM")


def test_title_patch_relocates_data_without_code_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = bytearray(16 * 1024 * 1024)
    data[title.TITLE_FILE_ENTRY_ROM : title.TITLE_FILE_ENTRY_ROM + 12] = (
        title.TITLE_STOCK_ROM_START.to_bytes(4, "big")
        + title.TITLE_STOCK_ROM_END.to_bytes(4, "big")
        + title.TITLE_STOCK_FLAG.to_bytes(4, "big")
    )
    data[
        title.TITLE_RELOCATED_ROM : title.TITLE_RELOCATED_LIMIT
    ] = b"\xFF" * title.TITLE_RELOCATED_CAPACITY
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
    monkeypatch.setattr(title, "_build_title_package", lambda _stock, _name: fake_package)

    title.TitleBrandingPatch("sektor").apply(rom, PatchContext())

    assert rom.data[hook_rom : hook_rom + 8] == stock_hook
    assert rom.read_u32(title.TITLE_FILE_ENTRY_ROM) == title.TITLE_RELOCATED_ROM
    assert rom.read_u32(title.TITLE_FILE_ENTRY_ROM + 4) == (
        title.TITLE_RELOCATED_ROM + len(fake_package)
    )
    assert rom.data[
        title.TITLE_RELOCATED_ROM : title.TITLE_RELOCATED_ROM + len(fake_package)
    ] == fake_package
