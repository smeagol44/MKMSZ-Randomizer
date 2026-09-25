import hashlib

import pytest

from mkmszr.donors.mkt_n64 import (
    MKT_N64_REV2_SHA256,
    MKT_N64_REV2_SIZE,
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


def test_visual_translation_uses_first_appearance_palette_order() -> None:
    # Build 85 rows of 80 pixels. The visible 78 columns use source indices 5,2,7
    # in first-appearance order; the two padding columns deliberately use 63 and
    # must not affect the compact target palette.
    rows = []
    for row in range(85):
        visible = bytes([5, 2, 7] + [5] * 75)
        rows.append(visible + bytes((63, 63)))
    decoded = b"".join(rows)

    palette = b"".join(value.to_bytes(2, "big") for value in range(64))
    slices, tlut = _build_visual_assets(decoded, palette)

    assert len(slices) == 9
    assert tlut[:6] == bytes.fromhex("0005 0002 0007")
    assert tlut[6:] == bytes(len(tlut) - 6)
    assert len(tlut) == 0x200
    assert hashlib.sha256(b"".join(slices)).hexdigest()
