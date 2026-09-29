"""Non-optional MKMSZR title-screen branding.

The approved typeset art uses the native 320x240 CI8 storage/render path and
the stock background plus 15 shared BGR555 art/edition entries. File 0x5E is
decoded, its six title-tile pixel regions are replaced, and a build-selected
uppercase <NAME> EDITION line is rasterized into the same shared palette before
the package is re-encoded into the original file slot.

The edition line is deliberately data-only: it does not claim an executable
code cave or title-menu hook, so it composes with the permanent native
bootstrap/pickup-persistence cave.
"""

from __future__ import annotations

import base64
import hashlib
import struct
import zlib
from importlib.resources import files

from ..config import OutfitConfig
from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext
from .palette import SubZeroPalettePatch, make_hue

TITLE_FILE_ID = 0x5E
FILE_TABLE_ROM = 0x000A5010
FILE_TABLE_ENTRY_SIZE = 12
TITLE_FILE_ENTRY_ROM = FILE_TABLE_ROM + TITLE_FILE_ID * FILE_TABLE_ENTRY_SIZE
TITLE_STOCK_ROM_START = 0x004E3060
TITLE_STOCK_ROM_END = 0x00512440
TITLE_STOCK_FLAG = 1
TITLE_STOCK_SHA256 = "98638b038e14cba3c1003f9997d629f59b072914728a703557fd4f710eefba83"
TITLE_DECODED_SIZE = 0x61494
TITLE_STOCK_CAPACITY = TITLE_STOCK_ROM_END - TITLE_STOCK_ROM_START

TITLE_PALETTE_ROM = 0x000B3364
TITLE_BACKGROUND_INDEX = 255
TITLE_EDITION_BASELINE_Y = 126
TITLE_CANVAS_WIDTH = 320
TITLE_CANVAS_HEIGHT = 240

DEFAULT_EDITION_NAME = "SUB-ZERO"
EDITION_NAME_MAX_LENGTH = 12
EDITION_SUFFIX = " EDITION"
EDITION_ALLOWED = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -")
TITLE_PIXELS_RESOURCE = "title_typeset_ci8.b64"
EDITION_FONT_RESOURCE = "title_edition_font.b64"

# These 15 stock-unused CI8 entries provide a shared title-art/edition ramp.
EDITION_PALETTE_INDICES = (8, 29, 39, 50, 56, 61, 64, 68, 71, 80, 100, 106, 115, 116, 132)
EDITION_PALETTE_EXPECTED = (
    0x77BC, 0x7EEA, 0x6270, 0x7AA7, 0x624D,
    0x564C, 0x5A2D, 0x5E2C, 0x7666, 0x460E,
    0x49E9, 0x3DCB, 0x51E6, 0x41C9, 0x3DA8,
)
# Dark -> light 15-entry icy-blue BGR555 ramp. Index 0xFF remains
# the stock near-black background (0x0001).
EDITION_PALETTE_WORDS = (
    0x0821, 0x0C41, 0x1881, 0x2CE2, 0x3D41,
    0x3D44, 0x45A6, 0x5E28, 0x628F, 0x6ED1,
    0x7732, 0x7B75, 0x7778, 0x7FB8, 0x7BDB,
)
TITLE_16COLOR_INDICES = (TITLE_BACKGROUND_INDEX,) + EDITION_PALETTE_INDICES

# Five preserved blue shades for the plaque; five fixed hue bands with a
# shadow/highlight pair for RANDOMIZER and the configurable edition line.
# Rainbow clothing itself continues to cycle independently during gameplay.
RAINBOW_PALETTE_WORDS = (
    0x0821, 0x2CE2, 0x5E28, 0x7B75, 0x7BDB,
    0x18D4, 0x319E, 0x1A54, 0x339E, 0x1E86,
    0x37CC, 0x5206, 0x7B0C, 0x50D1, 0x799A,
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


def _title_pixels() -> bytes:
    resource = files("mkmszr.data").joinpath(TITLE_PIXELS_RESOURCE)
    pixels = zlib.decompress(base64.b64decode(resource.read_bytes(), validate=True))
    if len(pixels) != TITLE_CANVAS_WIDTH * TITLE_CANVAS_HEIGHT:
        raise AssertionError("embedded title pixel count drifted")
    if not set(pixels) <= set(TITLE_16COLOR_INDICES):
        raise AssertionError("embedded title art exceeds shared 16-color palette")
    return pixels


def _fixed_rainbow_pixels(pixels: bytearray) -> None:
    """Reindex the approved art into the fixed five-band rainbow palette."""

    levels = {index: level for level, index in enumerate(EDITION_PALETTE_INDICES)}
    for y in range(39, 140):
        row = y * TITLE_CANVAS_WIDTH
        for x in range(TITLE_CANVAS_WIDTH):
            offset = row + x
            index = pixels[offset]
            if index == TITLE_BACKGROUND_INDEX:
                continue
            level = levels[index]
            if y < 72:
                # Keep the plaque's restrained blue bevel and its lettering.
                pixels[offset] = EDITION_PALETTE_INDICES[round(level * 4 / 14)]
            elif y < 113 and level <= 4:
                # Retain the darkest letter outline instead of painting it vivid.
                pixels[offset] = EDITION_PALETTE_INDICES[round(level * 2 / 4)]
            else:
                band = min(4, max(0, (x - 10) * 5 // 300))
                highlight = level >= (9 if y >= 113 else 11)
                pixels[offset] = EDITION_PALETTE_INDICES[5 + 2 * band + highlight]


def _palette_words_for_outfit(
    outfit: OutfitConfig, context: PatchContext
) -> tuple[int, ...]:
    mode = outfit.mode.lower()
    if mode == "vanilla":
        return EDITION_PALETTE_WORDS
    if mode == "rainbow":
        return RAINBOW_PALETTE_WORDS
    if mode in ("red", "green"):
        # Clothing swaps channels in its darker blue source. On the title's
        # brighter cyan source the same swap looks bronze/teal; target the
        # corresponding outfit hue while retaining the title's luminance.
        hue = 0.0 if mode == "red" else 120.0
        return tuple(make_hue(word, hue) for word in EDITION_PALETTE_WORDS)
    recolor = SubZeroPalettePatch(
        mode, hue_degrees=outfit.hue_degrees, rgb=outfit.rgb
    )
    return tuple(recolor._transform(word, context) for word in EDITION_PALETTE_WORDS)


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


def _build_title_package(
    stock_comp: bytes,
    name: str | None,
    *,
    fixed_rainbow: bool = False,
) -> bytes:
    decoded = bytearray(_lzw_decompress(stock_comp))
    if len(decoded) != TITLE_DECODED_SIZE:
        raise PatchError(
            f"unexpected decoded title size 0x{len(decoded):X}; expected 0x{TITLE_DECODED_SIZE:X}"
        )

    pixels = bytearray(_title_pixels())
    _render_edition(pixels, name)
    if fixed_rainbow:
        _fixed_rainbow_pixels(pixels)
    for record, width, height, x, y in TITLE_TILES:
        tile = bytearray()
        for row in range(height):
            start = (y + row) * TITLE_CANVAS_WIDTH + x
            tile.extend(pixels[start : start + width])
        decoded[record + 12 : record + 12 + width * height] = tile

    compressed = _lzw_compress(bytes(decoded))
    if len(compressed) > TITLE_STOCK_CAPACITY:
        raise PatchError(
            f"title package 0x{len(compressed):X} exceeds stock "
            f"0x{TITLE_STOCK_CAPACITY:X}-byte file slot"
        )
    if _lzw_decompress(compressed) != bytes(decoded):
        raise PatchError("title package failed LZW round-trip verification")
    return compressed


class TitleBrandingPatch:
    """Install typeset title art and a configurable uppercase edition line."""

    name = "title-branding"

    def __init__(
        self,
        edition_name: str | None = DEFAULT_EDITION_NAME,
        outfit: OutfitConfig | None = None,
    ):
        self.edition_name = normalize_edition_name(edition_name)
        self.outfit = outfit or OutfitConfig()

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        mode = self.outfit.mode.lower()
        palette_words = _palette_words_for_outfit(self.outfit, context)

        expected_entry = (
            TITLE_STOCK_ROM_START.to_bytes(4, "big")
            + TITLE_STOCK_ROM_END.to_bytes(4, "big")
            + TITLE_STOCK_FLAG.to_bytes(4, "big")
        )
        rom.expect_bytes(TITLE_FILE_ENTRY_ROM, expected_entry)
        for index, expected in zip(
            EDITION_PALETTE_INDICES, EDITION_PALETTE_EXPECTED, strict=True
        ):
            rom.expect_u16(TITLE_PALETTE_ROM + index * 2, expected)

        stock_comp = bytes(rom.data[TITLE_STOCK_ROM_START:TITLE_STOCK_ROM_END])
        if hashlib.sha256(stock_comp).hexdigest() != TITLE_STOCK_SHA256:
            raise PatchError("stock title file 0x5E no longer matches the clean ROM")
        compressed = _build_title_package(
            stock_comp,
            self.edition_name,
            fixed_rainbow=mode == "rainbow",
        )
        title_end = TITLE_STOCK_ROM_START + len(compressed)

        rom.write_bytes(TITLE_STOCK_ROM_START, compressed)
        rom.write_u32(TITLE_FILE_ENTRY_ROM + 4, title_end)
        rom.write_u32(TITLE_FILE_ENTRY_ROM + 8, TITLE_STOCK_FLAG)
        for index, replacement in zip(
            EDITION_PALETTE_INDICES, palette_words, strict=True
        ):
            rom.write_u16(TITLE_PALETTE_ROM + index * 2, replacement)

        return (
            f"installs the approved 16-color typeset title art ({mode} outfit palette)",
            (
                f"bakes {edition_text(self.edition_name)} into the shared "
                "16-color CI8 title palette at y~114"
            ),
            (
                f"writes compressed title file 0x5E in its stock ROM slot "
                f"0x{TITLE_STOCK_ROM_START:08X}..0x{title_end - 1:08X}"
            ),
            "no title executable cave or title-menu code hook is used",
        )
