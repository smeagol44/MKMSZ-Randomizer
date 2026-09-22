"""Non-optional MKMSZR title-screen branding.

The accepted title art is a native 320x240 CI8 composite using the stock title
palette. File 0x5E is decoded, its six title-tile pixel regions are replaced,
then the package is re-encoded with the game's LZW grammar and relocated to a
guarded production ROM allocation. The edition line is native title text so a
build can select an uppercase character name without regenerating the art.
"""

from __future__ import annotations

import base64
import zlib
from importlib.resources import files

from ..data.addresses import NATIVE_BOOTSTRAP_STUB_ROM, NATIVE_BOOTSTRAP_STUB_VA
from ..errors import PatchError
from ..mips import addiu, jal, jr, lui, lw, split_address, sw, words_blob
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
TITLE_RELOCATED_SIZE = 0x2FD95
TITLE_RELOCATED_END = TITLE_RELOCATED_ROM + TITLE_RELOCATED_SIZE

TITLE_HOOK_ROM = 0x00079C24
TITLE_HOOK_EXPECTED = bytes.fromhex("3C04800B 2484ED1C")
TITLE_TEXT_RENDERER_VA = 0x8001CA88
TITLE_TEXT_STYLE_VA = 0x800B22B8
TITLE_START_STRING_VA = 0x800AED1C
TITLE_TEXT_X = 160
TITLE_TEXT_Y = 114

TITLE_WRAPPER_ROM = 0x0009ADE0
TITLE_WRAPPER_VA = 0x8009A1E0
TITLE_WRAPPER_CAPACITY = 0x80
TITLE_MAPPER_ROM = 0x0009AEFC
if not (
    NATIVE_BOOTSTRAP_STUB_ROM
    <= TITLE_WRAPPER_ROM
    < TITLE_WRAPPER_ROM + TITLE_WRAPPER_CAPACITY
    <= TITLE_MAPPER_ROM
):
    raise AssertionError("title wrapper allocation escaped bootstrap tail")
if TITLE_WRAPPER_VA != NATIVE_BOOTSTRAP_STUB_VA + (
    TITLE_WRAPPER_ROM - NATIVE_BOOTSTRAP_STUB_ROM
):
    raise AssertionError("title wrapper ROM/VA mapping drifted")

DEFAULT_EDITION_NAME = "SUB-ZERO"
EDITION_NAME_MAX_LENGTH = 12
EDITION_SUFFIX = " EDITION"
EDITION_ALLOWED = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -")
CANDIDATE_PIXELS_RESOURCE = "title_candidate_b_ci8.b64"

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
    if len(pixels) != 320 * 240:
        raise AssertionError("embedded title pixel count drifted")
    return pixels


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


def _build_title_package(stock_comp: bytes) -> bytes:
    decoded = bytearray(_lzw_decompress(stock_comp))
    if len(decoded) != TITLE_DECODED_SIZE:
        raise PatchError(
            f"unexpected decoded title size 0x{len(decoded):X}; expected 0x{TITLE_DECODED_SIZE:X}"
        )

    pixels = _candidate_pixels()
    for record, width, height, x, y in TITLE_TILES:
        tile = bytearray()
        for row in range(height):
            start = (y + row) * 320 + x
            tile.extend(pixels[start : start + width])
        decoded[record + 12 : record + 12 + width * height] = tile

    compressed = _lzw_compress(bytes(decoded))
    if len(compressed) != TITLE_RELOCATED_SIZE:
        raise PatchError(
            f"candidate title compressed size drifted: 0x{len(compressed):X} "
            f"!= 0x{TITLE_RELOCATED_SIZE:X}"
        )
    if _lzw_decompress(compressed) != bytes(decoded):
        raise PatchError("candidate title package failed LZW round-trip verification")
    return compressed


def build_title_text_wrapper(name: str | None) -> bytes:
    text = edition_text(name).encode("ascii") + b"\x00"
    words = [
        addiu("sp", "sp", -0x20),
        sw("ra", 0x1C, "sp"),
        0,
        0,
        addiu("a1", "zero", TITLE_TEXT_X),
        addiu("a2", "zero", TITLE_TEXT_Y),
        addiu("a3", "zero", 1),
    ]

    style_high, style_low = split_address(TITLE_TEXT_STYLE_VA)
    words.extend(
        [
            lui("t0", style_high),
            addiu("t0", "t0", style_low),
            sw("t0", 0x10, "sp"),
            addiu("t0", "zero", 800),
            sw("t0", 0x14, "sp"),
            jal(TITLE_TEXT_RENDERER_VA),
            sw("s1", 0x18, "sp"),
            lw("ra", 0x1C, "sp"),
        ]
    )

    start_high, start_low = split_address(TITLE_START_STRING_VA)
    words.extend(
        [
            lui("a0", start_high),
            addiu("a0", "a0", start_low),
            jr("ra"),
            addiu("sp", "sp", 0x20),
        ]
    )

    code = words_blob(words)
    string_offset = (len(code) + 3) & ~3
    string_va = TITLE_WRAPPER_VA + string_offset
    string_high, string_low = split_address(string_va)
    words[2] = lui("a0", string_high)
    words[3] = addiu("a0", "a0", string_low)
    code = words_blob(words)
    wrapper = code + bytes(string_offset - len(code)) + text
    if len(wrapper) > TITLE_WRAPPER_CAPACITY:
        raise ValueError("title edition wrapper exceeds its production allocation")
    return wrapper


class TitleBrandingPatch:
    """Install the accepted Randomizer title image and configurable edition line."""

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
        rom.expect_bytes(TITLE_HOOK_ROM, TITLE_HOOK_EXPECTED)
        rom.expect_bytes(TITLE_WRAPPER_ROM, bytes(TITLE_WRAPPER_CAPACITY))
        rom.expect_bytes(TITLE_RELOCATED_ROM, b"\xFF" * TITLE_RELOCATED_SIZE)

        stock_comp = bytes(rom.data[TITLE_STOCK_ROM_START:TITLE_STOCK_ROM_END])
        compressed = _build_title_package(stock_comp)
        wrapper = build_title_text_wrapper(self.edition_name)

        rom.write_bytes(TITLE_RELOCATED_ROM, compressed)
        rom.write_u32(TITLE_FILE_ENTRY_ROM + 0, TITLE_RELOCATED_ROM)
        rom.write_u32(TITLE_FILE_ENTRY_ROM + 4, TITLE_RELOCATED_END)
        rom.write_u32(TITLE_FILE_ENTRY_ROM + 8, TITLE_STOCK_FLAG)

        rom.write_bytes(TITLE_WRAPPER_ROM, wrapper)
        rom.write_u32(TITLE_HOOK_ROM, jal(TITLE_WRAPPER_VA))
        rom.write_u32(TITLE_HOOK_ROM + 4, 0)

        relocation_note = (
            f"relocates compressed title file 0x5E to ROM "
            f"0x{TITLE_RELOCATED_ROM:08X}..0x{TITLE_RELOCATED_END - 1:08X}"
        )
        return (
            "installs runtime-confirmed Candidate-B RANDOMIZER title art",
            f"draws {edition_text(self.edition_name)} at x={TITLE_TEXT_X}, y={TITLE_TEXT_Y}",
            relocation_note,
        )
