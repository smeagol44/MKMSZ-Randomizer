import hashlib

import pytest

from mkmszr.patches.title_branding import (
    DEFAULT_EDITION_NAME,
    EDITION_NAME_MAX_LENGTH,
    TITLE_RELOCATED_END,
    TITLE_RELOCATED_ROM,
    TITLE_TEXT_Y,
    TITLE_WRAPPER_CAPACITY,
    TITLE_WRAPPER_ROM,
    _candidate_pixels,
    _lzw_compress,
    _lzw_decompress,
    build_title_text_wrapper,
    edition_text,
    normalize_edition_name,
)


def test_title_character_name_defaults_and_uppercases() -> None:
    assert normalize_edition_name(None) == DEFAULT_EDITION_NAME
    assert normalize_edition_name("") == DEFAULT_EDITION_NAME
    assert normalize_edition_name("  sub-zero  ") == "SUB-ZERO"
    assert normalize_edition_name("noob  saibot") == "NOOB SAIBOT"
    assert edition_text("sektor") == "SEKTOR EDITION"


def test_title_character_name_is_bounded_and_ascii_safe() -> None:
    assert normalize_edition_name("A" * EDITION_NAME_MAX_LENGTH) == (
        "A" * EDITION_NAME_MAX_LENGTH
    )

    with pytest.raises(ValueError):
        normalize_edition_name("A" * (EDITION_NAME_MAX_LENGTH + 1))
    with pytest.raises(ValueError):
        normalize_edition_name("SUB_ZERO")
    with pytest.raises(ValueError):
        normalize_edition_name("SCORPION!")


def test_candidate_b_asset_is_exact_native_pixel_image() -> None:
    pixels = _candidate_pixels()
    assert len(pixels) == 320 * 240
    assert hashlib.sha256(pixels).hexdigest() == (
        "480bd0b816068feb82075747b0b2abb4e5c790c5970b156915fd363efd14d80b"
    )


def test_title_lzw_round_trip() -> None:
    raw = (bytes(range(256)) * 40) + (b"RANDOMIZER" * 500)
    encoded = _lzw_compress(raw)
    assert encoded[:4] == len(raw).to_bytes(4, "big")
    assert _lzw_decompress(encoded) == raw


def test_title_wrapper_uses_final_position_and_configured_uppercase_text() -> None:
    wrapper = build_title_text_wrapper("sektor")
    assert TITLE_TEXT_Y == 114
    assert wrapper.endswith(b"SEKTOR EDITION\x00")
    assert len(wrapper) <= TITLE_WRAPPER_CAPACITY


def test_title_allocations_are_bounded() -> None:
    assert TITLE_WRAPPER_ROM + TITLE_WRAPPER_CAPACITY <= 0x0009AEFC
    assert TITLE_RELOCATED_ROM == 0x00F90000
    assert TITLE_RELOCATED_END < 0x01000000
