import hashlib

import pytest

import mkmszr.rom as rom_module
from mkmszr.errors import RomValidationError
from mkmszr.rom import (
    EXPECTED_SIZE,
    N64_N64_MAGIC,
    N64_V64_MAGIC,
    N64_Z64_MAGIC,
    RomImage,
    _changed_spans,
    normalize_n64_byte_order,
)


def _as_v64(source: bytes) -> bytes:
    out = bytearray(len(source))
    out[0::2] = source[1::2]
    out[1::2] = source[0::2]
    return bytes(out)


def _as_n64(source: bytes) -> bytes:
    out = bytearray(len(source))
    out[0::4] = source[3::4]
    out[1::4] = source[2::4]
    out[2::4] = source[1::4]
    out[3::4] = source[0::4]
    return bytes(out)


def test_changed_spans_groups_adjacent_bytes() -> None:
    before = bytes([0, 0, 0, 0, 0, 0, 0])
    after = bytes([0, 1, 2, 0, 0, 3, 0])
    assert _changed_spans(before, after) == ((1, 3), (5, 6))


def test_changed_spans_reports_appended_output_region() -> None:
    before = bytes([1, 2, 3])
    after = bytes([1, 2, 3, 0xFF, 0xFF])
    assert _changed_spans(before, after) == ((3, 5),)


def test_rom_output_can_expand_without_relaxing_input_validation() -> None:
    source = bytearray(EXPECTED_SIZE)
    source[:4] = N64_Z64_MAGIC.to_bytes(4, "big")
    rom = RomImage(bytearray(source), bytes(source))

    rom.expand_output(32 * 1024 * 1024)

    assert len(rom.data) == 32 * 1024 * 1024
    assert rom.data[0x01000000:] == b"\xFF" * (16 * 1024 * 1024)
    assert rom.changed_spans() == ((0x01000000, 0x02000000),)


def test_n64_byte_order_normalizer_recognizes_all_three_serializations() -> None:
    canonical = bytes.fromhex("80371240 11223344 AABBCCDD")

    v64 = _as_v64(canonical)
    n64 = _as_n64(canonical)

    assert int.from_bytes(canonical[:4], "big") == N64_Z64_MAGIC
    assert int.from_bytes(v64[:4], "big") == N64_V64_MAGIC
    assert int.from_bytes(n64[:4], "big") == N64_N64_MAGIC

    assert normalize_n64_byte_order(canonical) == (canonical, "z64")
    assert normalize_n64_byte_order(v64) == (canonical, "v64")
    assert normalize_n64_byte_order(n64) == (canonical, "n64")


def test_rom_validation_hashes_normalized_canonical_bytes(monkeypatch) -> None:
    canonical = bytearray(EXPECTED_SIZE)
    canonical[:4] = N64_Z64_MAGIC.to_bytes(4, "big")
    canonical[0x100:0x108] = bytes.fromhex("DEADBEEF01234567")
    canonical_bytes = bytes(canonical)
    canonical_sha = hashlib.sha256(canonical_bytes).hexdigest()
    monkeypatch.setattr(rom_module, "CLEAN_SHA256", canonical_sha)

    for serialized in (canonical_bytes, _as_v64(canonical_bytes), _as_n64(canonical_bytes)):
        rom = RomImage.from_bytes(serialized, require_clean=True)
        assert rom.to_bytes() == canonical_bytes
        assert rom.source_sha256 == canonical_sha
        assert rom.changed_spans() == ()


def test_rom_validation_rejects_unknown_byte_order() -> None:
    source = bytearray(EXPECTED_SIZE)
    source[:4] = bytes.fromhex("12345678")

    with pytest.raises(RomValidationError, match="unrecognized N64 ROM byte order"):
        RomImage.from_bytes(bytes(source), require_clean=False)
