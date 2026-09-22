"""Non-optional MKMSZR title-screen branding.

The accepted Candidate-B art is a native 320x240 CI8 composite using the stock
title palette. File 0x5E is decoded, its six title-tile pixel regions are
replaced, and a build-selected uppercase <NAME> EDITION line is rasterized
into the same CI8 image before the package is re-encoded.

The edition line is deliberately data-only: it does not claim an executable
code cave or title-menu hook, so it composes with the permanent native
bootstrap/pickup-persistence cave.
"""

from __future__ import annotations

import base64
import struct
import zlib
from importlib.resources import files

from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext

TITLE_FILE_ID = 0x5E
FILE_TABLE_ROM = 0x000A5010
FILE_TABLE_ENTRY_SIZE = 12
TITLE_FILE_ENTRY_ROM = FILE_TABLE_ROM + TITLE_FILE_ID * FILE_TABLE_ENTRY_SIZE
TITLE_STOCK_ROM_START = 0x004E3060
TITLE_STOCK_ROM_END = 0x00512440
TITLE_STOCK_FLAG = 1
TITLE_DECODED_SIZE = 0x61494
TITLE_RELOCATED_ROM = 0x00F90000
TITLE_RELOCATED_CAPACITY = 0x31000
TITLE_RELOCATED_LIMIT = TITLE_RELOCATED_ROM + TITLE_RELOCATED_CAPACITY

TITLE_PALETTE_ROM = 0x000B3364
TITLE_EDITION_BASELINE_Y = 126
TITLE_CANVAS_WIDTH = 320
TITLE_CANVAS_HEIGHT = 240

DEFAULT_EDITION_NAME = "SUB-ZERO"
EDITION_NAME_MAX_LENGTH = 12
EDITION_SUFFIX = " EDITION"
EDITION_ALLOWED = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -")
CANDIDATE_PIXELS_RESOURCE = "title_candidate_b_ci8.b64"
EDITION_FONT_RESOURCE = "title_edition_font.b64"

# Candidate B does not use these CI8 indices. Reserve them for the baked
# edition line, and guard their stock palette words before replacement.
EDITION_PALETTE_INDICES = (8, 29, 39, 50, 56, 61, 64, 68, 71, 80, 100, 106, 115, 116, 132)
EDITION_PALETTE_EXPECTED = (
    0x77BC, 0x7EEA, 0x6270, 0x7AA7, 0x624D,
    0x564C, 0x5A2D, 0x5E2C, 0x7666, 0x460E,
    0x49E9, 0x3DCB, 0x51E6, 0x41C9, 0x3DA8,
)
# Dark -> light grayscale, matching the title frontend's visual family.
EDITION_PALETTE_WORDS = (
    0x0842, 0x1084, 0x18C6, 0x2108, 0x294A,
    0x318C, 0x39CE, 0x4210, 0x4631, 0x4E73,
    0x5EF7, 0x6739, 0x6F7B, 0x77BD, 0x7FFF,
)

TITLE_TILES = (
    (0x3B780, 120, 120, 0, 0),
    (0x3EFCC, 100, 120, 120, 0),
    (0x41EB8, 100, 120, 220, 0),
    (0x44DA4, 120, 120, 0, 120),
    (0x485F0, 100, 120, 120, 120),
    (0x4B4DC, 100, 120, 220, 120),
)


def normalize_edition_name(value: str | None) -> str:
    """Normalize the temporary freeform title character name."""

    name = " ".join((value or "").strip().upper().split()) or DEFAULT_EDITION_NAME
    if len(name) > EDITION_NAME_MAX_LENGTH:
        raise ValueError(
            f"title character name must be at most {EDITION_NAME_MAX_LENGTH} characters"
        )
    invalid = sorted(set(name) - EDITION_ALLOWED)
    if invalid:
        shown = "".join(invalid)
        raise ValueError(
            "title character name supports only A-Z, 0-9, spaces and hyphens; "
            f"invalid: {shown!r}"
        )
    return name


def edition_text(value: str | None) -> str:
    return normalize_edition_name(value) + EDITION_SUFFIX


def _candidate_pixels() -> bytes:
    resource = files("mkmszr.data").joinpath(CANDIDATE_PIXELS_RESOURCE)
    pixels = zlib.decompress(base64.b64decode(resource.read_bytes(), validate=True))
    if len(pixels) != TITLE_CANVAS_WIDTH * TITLE_CANVAS_HEIGHT:
        raise AssertionError("embedded title pixel count drifted")
    return pixels


def _edition_font() -> dict[str, tuple[int, int, int, int, int, bytes]]:
    resource = files("mkmszr.data").joinpath(EDITION_FONT_RESOURCE)
    raw = zlib.decompress(base64.b64decode(resource.read_bytes(), validate=True))
    if raw[:4] != b"TF1\x00" or len(raw) < 5:
        raise AssertionError("embedded edition font header is invalid")

    count = raw[4]
    pos = 5
    glyphs: dict[str, tuple[int, int, int, int, int, bytes]] = {}
    for _ in range(count):
        if pos + 6 > len(raw):
            raise AssertionError("embedded edition font is truncated")
        code, advance, x_offset, y_offset, width, height = struct.unpack_from(
            ">BBbbBB", raw, pos
        )
        pos += 6
        size = width * height
        if pos + size > len(raw):
            raise AssertionError("embedded edition glyph is truncated")
        glyphs[chr(code)] = (
            advance,
            x_offset,
            y_offset,
            width,
            height,
            raw[pos : pos + size],
        )
        pos += size
    if pos != len(raw):
        raise AssertionError("embedded edition font has trailing data")
    return glyphs


def _render_edition(pixels: bytearray, value: str | None) -> None:
    text = edition_text(value)
    glyphs = _edition_font()
    try:
        width = sum(glyphs[char][0] for char in text)
    except KeyError as exc:
        raise ValueError(f"title font does not contain {exc.args[0]!r}") from exc

    cursor_x = (TITLE_CANVAS_WIDTH - width) // 2
    if cursor_x < 0:
        raise ValueError("title edition text is too wide")

    for char in text:
        advance, x_offset, y_offset, glyph_width, glyph_height, mask = glyphs[char]
        for y in range(glyph_height):
            target_y = TITLE_EDITION_BASELINE_Y + y_offset + y
            if not 0 <= target_y < TITLE_CANVAS_HEIGHT:
                continue
            row = target_y * TITLE_CANVAS_WIDTH
            mask_row = y * glyph_width
            for x in range(glyph_width):
                alpha = mask[mask_row + x]
                if alpha < 8:
                    continue
                target_x = cursor_x + x_offset + x
                if not 0 <= target_x < TITLE_CANVAS_WIDTH:
                    continue
                level = (alpha * (len(EDITION_PALETTE_INDICES) - 1) + 127) // 255
                pixels[row + target_x] = EDITION_PALETTE_INDICES[level]
        cursor_x += advance


def _lzw_decompress(comp: bytes) -> bytes:
    """Decode MKMSZ's file-0x5E MSB-first LZW stream."""

    if len(comp) < 4:
        raise PatchError("title package is truncated")
    output_size = int.from_bytes(comp[:4], "big")
    data = comp[4:]
    bit_pos = 0
    bits = 9
    next_code = 258
    table = {index: bytes([index]) for index in range(256)}
    previous: int | None = None
    output = bytearray()

    def get_code(width: int) -> int | None:
        nonlocal bit_pos
        if bit_pos + width > len(data) * 8:
            return None
        value = 0
        for _ in range(width):
            byte = data[bit_pos >> 3]
            bit = 7 - (bit_pos & 7)
            value = (value << 1) | ((byte >> bit) & 1)
            bit_pos += 1
        return value

    while len(output) < output_size:
        code = get_code(bits)
        if code is None:
            raise PatchError("title LZW stream ended early")
        if code == 257:
            break
        if code == 256:
            table = {index: bytes([index]) for index in range(256)}
            next_code = 258
            bits = 9
            previous = None
            continue

        if previous is None:
            try:
                phrase = table[code]
            except KeyError as exc:
                raise PatchError(f"invalid first title LZW code {code}") from exc
            output.extend(phrase)
            previous = code
            continue

        if code < next_code:
            try:
                phrase = table[code]
            except KeyError as exc:
                raise PatchError(f"invalid title LZW code {code}") from exc
        else:
            previous_phrase = table[previous]
            phrase = previous_phrase + previous_phrase[:1]

        table[next_code] = table[previous] + phrase[:1]
        output.extend(phrase)
        next_code += 1
        if next_code == (1 << bits) - 1 and bits < 12:
            bits += 1
        previous = code

    if len(output) != output_size:
        raise PatchError(
            f"title LZW size mismatch: expected 0x{output_size:X}, got 0x{len(output):X}"
        )
    return bytes(output)


def _lzw_codes(raw: bytes) -> list[int]:
    clear = 256
    end = 257
    maximum = 1 << 12
    table = {bytes([index]): index for index in range(256)}
    next_code = 258
    codes = [clear]
    current = b""

    for value in raw:
        char = bytes([value])
        if not current:
            current = char
            continue
        joined = current + char
        if joined in table:
            current = joined
            continue

        codes.append(table[current])
        if next_code < maximum:
            table[joined] = next_code
            next_code += 1
        else:
            codes.append(clear)
            table = {bytes([index]): index for index in range(256)}
            next_code = 258
        current = char

    if current:
        codes.append(table[current])
    codes.append(end)
    return codes


def _lzw_compress(raw: bytes) -> bytes:
    """Encode with the exact width-growth/reset grammar used by file 0x5E."""

    bits = 9
    next_code = 258
    have_previous = False
    accumulator = 0
    pending_bits = 0
    output = bytearray(len(raw).to_bytes(4, "big"))

    for code in _lzw_codes(raw):
        if code >= 1 << bits:
            raise PatchError(
                f"title LZW code {code} cannot fit current {bits}-bit width"
            )
        accumulator = (accumulator << bits) | code
        pending_bits += bits
        while pending_bits >= 8:
            pending_bits -= 8
            output.append((accumulator >> pending_bits) & 0xFF)
            accumulator &= (1 << pending_bits) - 1 if pending_bits else 0

        if code == 256:
            bits = 9
            next_code = 258
            have_previous = False
        elif code == 257:
            pass
        elif not have_previous:
            have_previous = True
        else:
            next_code += 1
            if next_code == (1 << bits) - 1 and bits < 12:
                bits += 1

    if pending_bits:
        output.append((accumulator << (8 - pending_bits)) & 0xFF)
    return bytes(output)


def _build_title_package(stock_comp: bytes, name: str | None) -> bytes:
    decoded = bytearray(_lzw_decompress(stock_comp))
    if len(decoded) != TITLE_DECODED_SIZE:
        raise PatchError(
            f"unexpected decoded title size 0x{len(decoded):X}; expected 0x{TITLE_DECODED_SIZE:X}"
        )

    pixels = bytearray(_candidate_pixels())
    _render_edition(pixels, name)
    for record, width, height, x, y in TITLE_TILES:
        tile = bytearray()
        for row in range(height):
            start = (y + row) * TITLE_CANVAS_WIDTH + x
            tile.extend(pixels[start : start + width])
        decoded[record + 12 : record + 12 + width * height] = tile

    compressed = _lzw_compress(bytes(decoded))
    if len(compressed) > TITLE_RELOCATED_CAPACITY:
        raise PatchError(
            f"title package 0x{len(compressed):X} exceeds reserved "
            f"0x{TITLE_RELOCATED_CAPACITY:X}-byte allocation"
        )
    if _lzw_decompress(compressed) != bytes(decoded):
        raise PatchError("title package failed LZW round-trip verification")
    return compressed


class TitleBrandingPatch:
    """Install Candidate-B art and a configurable baked uppercase edition line."""

    name = "title-branding"

    def __init__(self, edition_name: str | None = DEFAULT_EDITION_NAME):
        self.edition_name = normalize_edition_name(edition_name)

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        expected_entry = (
            TITLE_STOCK_ROM_START.to_bytes(4, "big")
            + TITLE_STOCK_ROM_END.to_bytes(4, "big")
            + TITLE_STOCK_FLAG.to_bytes(4, "big")
        )
        rom.expect_bytes(TITLE_FILE_ENTRY_ROM, expected_entry)
        rom.expect_bytes(TITLE_RELOCATED_ROM, b"\xFF" * TITLE_RELOCATED_CAPACITY)
        for index, expected in zip(
            EDITION_PALETTE_INDICES, EDITION_PALETTE_EXPECTED, strict=True
        ):
            rom.expect_u16(TITLE_PALETTE_ROM + index * 2, expected)

        stock_comp = bytes(rom.data[TITLE_STOCK_ROM_START:TITLE_STOCK_ROM_END])
        compressed = _build_title_package(stock_comp, self.edition_name)
        relocated_end = TITLE_RELOCATED_ROM + len(compressed)

        rom.write_bytes(TITLE_RELOCATED_ROM, compressed)
        rom.write_u32(TITLE_FILE_ENTRY_ROM + 0, TITLE_RELOCATED_ROM)
        rom.write_u32(TITLE_FILE_ENTRY_ROM + 4, relocated_end)
        rom.write_u32(TITLE_FILE_ENTRY_ROM + 8, TITLE_STOCK_FLAG)
        for index, replacement in zip(
            EDITION_PALETTE_INDICES, EDITION_PALETTE_WORDS, strict=True
        ):
            rom.write_u16(TITLE_PALETTE_ROM + index * 2, replacement)

        return (
            "installs runtime-confirmed Candidate-B RANDOMIZER title art",
            f"bakes {edition_text(self.edition_name)} into the CI8 title at y~114",
            (
                f"relocates compressed title file 0x5E to ROM "
                f"0x{TITLE_RELOCATED_ROM:08X}..0x{relocated_end - 1:08X}"
            ),
            "no title executable cave or title-menu code hook is used",
        )
