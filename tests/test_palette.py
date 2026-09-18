import pytest

from mkmszr.patches.palette import (
    decode_bgr555,
    encode_bgr555,
    make_green,
    make_hue,
    make_red,
    make_rgb_tint,
    seeded_hue,
)


def test_bgr555_round_trip() -> None:
    original = 0xFB17
    assert encode_bgr555(*decode_bgr555(original)) == original


def test_confirmed_red_transform_swaps_red_and_blue() -> None:
    red, green, blue, high = decode_bgr555(0xFB17)
    assert make_red(0xFB17) == 0xDF1E
    assert decode_bgr555(make_red(0xFB17)) == (blue, green, red, high)


def test_confirmed_green_transform_swaps_green_and_blue() -> None:
    red, green, blue, high = decode_bgr555(0xFB17)
    assert make_green(0xFB17) == 0xE3D7
    assert decode_bgr555(make_green(0xFB17)) == (red, blue, green, high)


def test_hue_transform_preserves_high_bit_and_value_ramp() -> None:
    source = 0xFB17
    transformed = make_hue(source, 285.0)
    assert transformed & 0x8000 == source & 0x8000
    source_rgb = decode_bgr555(source)[:3]
    output_rgb = decode_bgr555(transformed)[:3]
    assert max(output_rgb) == pytest.approx(max(source_rgb), abs=1)


def test_rgb_tint_preserves_high_bit() -> None:
    source = 0x9041
    transformed = make_rgb_tint(source, (255, 80, 180))
    assert transformed & 0x8000 == source & 0x8000


def test_seeded_hue_is_deterministic_and_stream_independent() -> None:
    assert seeded_hue("ABC123") == seeded_hue("ABC123")
    assert seeded_hue("ABC123") != seeded_hue("ABC124")
    assert 0.0 <= seeded_hue("ABC123") < 360.0
