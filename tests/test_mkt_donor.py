import hashlib

import pytest

from mkmszr.donors.mkt_n64 import (
    CI4_INDEX_MAP,
    CI4_PALETTE_RGBA5551_OVERRIDES,
    CI4_PALETTE_SOURCES,
    MKT_N64_REV2_SHA256,
    MKT_N64_REV2_SIZE,
    TEMPLE_AUDIO_PROFILES,
    _build_visual_assets,
    _decode_dict64_final,
    validate_mkt_n64_rev2,
)
from mkmszr.errors import RomValidationError


def test_mkt_rev2_identity_constants_are_exact() -> None:
    assert MKT_N64_REV2_SIZE == 12 * 1024 * 1024
    assert MKT_N64_REV2_SHA256 == (
        "30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb"
    )


def test_validate_mkt_rejects_wrong_size_before_hash() -> None:
    with pytest.raises(RomValidationError, match="12582912-byte MKT N64 ROM"):
        validate_mkt_n64_rev2(b"bad")


def test_dict64_final_decoder_handles_literal_double_dictionary_and_run() -> None:
    dictionary = bytes(range(256))
    # type 25, output length 7. flip stream length 1; first dictionary pair is forward.
    # literal 3; doubled literal 4; dictionary index 2 -> bytes 4,5; run two copies of 6.
    source = bytes.fromhex("19000007 01 00 03 44 82 C6 02")
    decoded = _decode_dict64_final(source, dictionary)
    assert decoded == bytes((3, 4, 4, 4, 5, 6, 6))


def test_visual_translation_uses_confirmed_ci4_palette_order() -> None:
    # The 55 visible indices appear in order; padding must not affect the palette.
    rows = []
    for row in range(85):
        visible = bytes(range(55)) + bytes(23)
        rows.append(visible + bytes((63, 63)))
    decoded = b"".join(rows)

    palette = b"".join(value.to_bytes(2, "big") for value in range(64))
    slices, tlut = _build_visual_assets(decoded, palette)

    assert len(slices) == 9
    assert len(tlut) == 0x20
    expected_tlut = bytearray(
        b"".join(index.to_bytes(2, "big") for index in CI4_PALETTE_SOURCES)
    )
    for index, rgba5551 in CI4_PALETTE_RGBA5551_OVERRIDES.items():
        start = index * 2
        expected_tlut[start : start + 2] = rgba5551.to_bytes(2, "big")
    assert tlut == bytes(expected_tlut)
    assert CI4_PALETTE_RGBA5551_OVERRIDES == {
        3: 0x388F,
        4: 0x5059,
        6: 0x6221,
        9: 0xA2AD,
    }
    assert slices[0][:4] == bytes(
        (CI4_INDEX_MAP[0] << 4 | CI4_INDEX_MAP[1],
         CI4_INDEX_MAP[2] << 4 | CI4_INDEX_MAP[3],
         CI4_INDEX_MAP[4] << 4 | CI4_INDEX_MAP[5],
         CI4_INDEX_MAP[6] << 4)
    )
    assert hashlib.sha256(b"".join(slices)).hexdigest()


def test_temple_audio_donor_profiles_match_approved_pools() -> None:
    assert tuple(TEMPLE_AUDIO_PROFILES) == (
        "friendship",
        "choose-your-destiny",
        "excellent",
        "superb",
        "well-done",
        "liu-bike",
        "raiden-bbb",
        "raiden-sss",
        "raiden-ttt",
        "robot-run",
        "shao-laugh",
        "mk3-04070",
        "mk3-04270",
        "mk3-05205",
        "mk3-05220",
        "mk3-21135",
        "mk3-21140",
        "mk3-02205",
        "mk3-07015",
        "mk3-04025",
        "mk3-04075",
        "mk3-02200",
    )