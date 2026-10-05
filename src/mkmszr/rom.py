"""Validated in-memory representation of the supported MKMSZ ROM."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .checksum import calculate_crc_6102
from .errors import PatchError, RomValidationError

CLEAN_SHA256 = "9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6"
EXPECTED_SIZE = 16 * 1024 * 1024

N64_Z64_MAGIC = 0x80371240
N64_V64_MAGIC = 0x37804012
N64_N64_MAGIC = 0x40123780

# Backward-compatible name for code/tests that refer to the canonical magic.
EXPECTED_MAGIC = N64_Z64_MAGIC


def normalize_n64_byte_order(source: bytes) -> tuple[bytes, str]:
    """Return canonical big-endian .z64 bytes plus detected input format.

    N64 ROM dumps commonly appear in three byte-order serializations:

    - .z64: big-endian bytes, magic 80 37 12 40;
    - .v64: adjacent-byte-swapped, magic 37 80 40 12;
    - .n64: little-endian 32-bit words, magic 40 12 37 80.

    The filename extension is deliberately ignored. Detection is based only on
    the first four bytes, and all patching continues against canonical .z64
    bytes.
    """

    if len(source) < 4:
        raise RomValidationError("ROM is too small to contain an N64 header")

    magic = int.from_bytes(source[:4], "big")
    if magic == N64_Z64_MAGIC:
        return source, "z64"

    if magic == N64_V64_MAGIC:
        if len(source) % 2:
            raise RomValidationError("byte-swapped N64 ROM length is not divisible by 2")
        normalized = bytearray(len(source))
        normalized[0::2] = source[1::2]
        normalized[1::2] = source[0::2]
        return bytes(normalized), "v64"

    if magic == N64_N64_MAGIC:
        if len(source) % 4:
            raise RomValidationError("little-endian N64 ROM length is not divisible by 4")
        normalized = bytearray(len(source))
        normalized[0::4] = source[3::4]
        normalized[1::4] = source[2::4]
        normalized[2::4] = source[1::4]
        normalized[3::4] = source[0::4]
        return bytes(normalized), "n64"

    raise RomValidationError(
        "unrecognized N64 ROM byte order: expected header magic "
        "80 37 12 40 (.z64), 37 80 40 12 (.v64), or 40 12 37 80 (.n64); "
        f"got {source[:4].hex(' ').upper()}"
    )


def _changed_spans(before: bytes, after: bytes | bytearray) -> tuple[tuple[int, int], ...]:
    """Return half-open contiguous byte ranges that differ, including appended output."""

    spans: list[tuple[int, int]] = []
    start: int | None = None
    shared_length = min(len(before), len(after))
    for index, (old, new) in enumerate(zip(before[:shared_length], after[:shared_length])):
        if old != new and start is None:
            start = index
        elif old == new and start is not None:
            spans.append((start, index))
            start = None
    if start is not None:
        spans.append((start, shared_length))
    if len(after) > shared_length:
        spans.append((shared_length, len(after)))
    return tuple(spans)


@dataclass
class RomImage:
    data: bytearray
    _original: bytes

    @classmethod
    def from_bytes(cls, source: bytes, *, require_clean: bool = True) -> RomImage:
        if len(source) != EXPECTED_SIZE:
            raise RomValidationError(
                f"expected a {EXPECTED_SIZE}-byte ROM, got {len(source)} bytes"
            )

        normalized, _input_format = normalize_n64_byte_order(source)
        digest = hashlib.sha256(normalized).hexdigest()
        if require_clean and digest != CLEAN_SHA256:
            raise RomValidationError(
                "unsupported ROM: expected clean MKMSZ USA Rev. 0 after N64 "
                "byte-order normalization, SHA-256 " + CLEAN_SHA256
            )
        return cls(bytearray(normalized), normalized)

    @classmethod
    def load(cls, path: Path, *, require_clean: bool = True) -> RomImage:
        return cls.from_bytes(path.read_bytes(), require_clean=require_clean)

    @property
    def source_sha256(self) -> str:
        return hashlib.sha256(self._original).hexdigest()

    @property
    def output_sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()

    def fresh_copy(self) -> RomImage:
        """Return a fresh mutable image of the canonical source snapshot."""
        return RomImage(bytearray(self._original), self._original)

    def read_u16(self, offset: int) -> int:
        return int.from_bytes(self.data[offset : offset + 2], "big")

    def read_u32(self, offset: int) -> int:
        return int.from_bytes(self.data[offset : offset + 4], "big")

    def expect_bytes(self, offset: int, expected: bytes) -> None:
        actual = bytes(self.data[offset : offset + len(expected)])
        if actual != expected:
            raise PatchError(
                f"guard failed at ROM 0x{offset:08X}: "
                f"expected {expected.hex().upper()}, got {actual.hex().upper()}"
            )

    def expect_u16(self, offset: int, expected: int) -> None:
        actual = self.read_u16(offset)
        if actual != expected:
            raise PatchError(
                f"guard failed at ROM 0x{offset:08X}: expected 0x{expected:04X}, got 0x{actual:04X}"
            )

    def expect_u32(self, offset: int, expected: int) -> None:
        actual = self.read_u32(offset)
        if actual != expected:
            raise PatchError(
                f"guard failed at ROM 0x{offset:08X}: expected 0x{expected:08X}, got 0x{actual:08X}"
            )

    def write_u16(self, offset: int, value: int) -> None:
        self.data[offset : offset + 2] = (value & 0xFFFF).to_bytes(2, "big")

    def write_u32(self, offset: int, value: int) -> None:
        self.data[offset : offset + 4] = (value & 0xFFFFFFFF).to_bytes(4, "big")

    def write_bytes(self, offset: int, value: bytes) -> None:
        self.data[offset : offset + len(value)] = value

    def expand_output(self, size: int, *, fill: int = 0xFF) -> None:
        """Grow only the generated output image; clean-input validation stays 16 MiB."""

        if size < len(self.data):
            raise ValueError("expanded output size cannot shrink the ROM")
        if not 0 <= fill <= 0xFF:
            raise ValueError("fill byte must be 0..255")
        if size > len(self.data):
            self.data.extend(bytes((fill,)) * (size - len(self.data)))

    def update_header_crc(self) -> tuple[int, int]:
        crc1, crc2 = calculate_crc_6102(self.data)
        self.write_u32(0x10, crc1)
        self.write_u32(0x14, crc2)
        return crc1, crc2

    def changed_spans(self) -> tuple[tuple[int, int], ...]:
        return _changed_spans(self._original, self.data)

    def to_bytes(self) -> bytes:
        return bytes(self.data)
