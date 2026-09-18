"""Validated in-memory representation of the supported MKMSZ ROM."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .checksum import calculate_crc_6102
from .errors import PatchError, RomValidationError

CLEAN_SHA256 = "9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6"
EXPECTED_SIZE = 16 * 1024 * 1024
EXPECTED_MAGIC = 0x80371240


def _changed_spans(before: bytes, after: bytes | bytearray) -> tuple[tuple[int, int], ...]:
    """Return half-open contiguous byte ranges that differ."""

    if len(before) != len(after):
        raise ValueError("buffers must have equal length")

    spans: list[tuple[int, int]] = []
    start: int | None = None
    for index, (old, new) in enumerate(zip(before, after)):
        if old != new and start is None:
            start = index
        elif old == new and start is not None:
            spans.append((start, index))
            start = None
    if start is not None:
        spans.append((start, len(after)))
    return tuple(spans)


@dataclass
class RomImage:
    data: bytearray
    _original: bytes

    @classmethod
    def from_bytes(cls, source: bytes, *, require_clean: bool = True) -> "RomImage":
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
    def load(cls, path: Path, *, require_clean: bool = True) -> "RomImage":
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

    def update_header_crc(self) -> tuple[int, int]:
        crc1, crc2 = calculate_crc_6102(self.data)
        self.write_u32(0x10, crc1)
        self.write_u32(0x14, crc2)
        return crc1, crc2

    def changed_spans(self) -> tuple[tuple[int, int], ...]:
        return _changed_spans(self._original, self.data)

    def to_bytes(self) -> bytes:
        return bytes(self.data)
