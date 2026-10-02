"""Validated in-memory representation of the supported MKMSZ ROM."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .checksum import calculate_crc_6102
from .errors import PatchError, RomValidationError

CLEAN_SHA256 = "9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6"
EXPECTED_SIZE = 16 * 1024 * 1024
EXPECTED_MAGIC = 0x80371240


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
        magic = int.from_bytes(source[:4], "big")
        if magic != EXPECTED_MAGIC:
            raise RomValidationError(
                f"expected big-endian .z64 magic 0x{EXPECTED_MAGIC:08X}, got 0x{magic:08X}"
            )
        digest = hashlib.sha256(source).hexdigest()
        if require_clean and digest != CLEAN_SHA256:
            raise RomValidationError(
                "unsupported ROM: expected clean MKMSZ USA Rev. 0 SHA-256 " + CLEAN_SHA256
            )
        return cls(bytearray(source), source)

    @classmethod
    def load(cls, path: Path, *, require_clean: bool = True) -> RomImage:
        return cls.from_bytes(path.read_bytes(), require_clean=require_clean)

    @property
    def source_sha256(self) -> str:
        return hashlib.sha256(self._original).hexdigest()

    @property
    def output_sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()

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
