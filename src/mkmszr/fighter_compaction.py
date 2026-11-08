"""Build-time 16-color compaction for the stock PRIS fighter family.

The transform is derived from the Runtime-confirmed compact PRIS proof line.
It never embeds ROM bytes: source assets are decoded from the user's clean ROM,
remapped to the accepted 16-color body index families, re-encoded as native
Type-5, and written back into the original file slots with guarded file-table
and palette-offset updates.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from .errors import PatchError
from .rom import RomImage

FILE_TABLE_ROM = 0x000A5010
FILE_ENTRY_SIZE = 12

# Accepted source-index -> 16-color body mapping recovered from the validated
# compact 0x8E/0x90 proof. Index 0 remains transparent.
BODY_INDEX_MAP = (
    0, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 6,
    6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10, 10,
    10, 11, 11, 11, 11, 9, 12, 12, 9, 12, 12, 12, 10, 12, 12, 13,
    13, 13, 13, 13, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15,
)
BODY_PALETTE_REPRESENTATIVES = (
    2, 4, 8, 11, 13, 16, 20, 23, 26, 29, 34, 45, 49, 54, 58,
)


@dataclass(frozen=True)
class FighterFileSpec:
    file_id: int
    start: int
    end: int
    table_offset: int
    expected_compact_size: int


SPECS = {
    0x8E: FighterFileSpec(0x8E, 0x78E300, 0x7ADF10, 0x580, 0x1A148),
    0x8F: FighterFileSpec(0x8F, 0x7ADF10, 0x7C9820, 0x4A4, 0x17138),
    0x90: FighterFileSpec(0x90, 0x7C9820, 0x7E5D70, 0x3A0, 0x16AC0),
    0x91: FighterFileSpec(0x91, 0x7E5D70, 0x7F8F10, 0x3B4, 0x102F0),
}

# Global type-indexed palette tables which contain file-relative offsets.
# Entries are (ROM site, palette-record ordinal inside the fighter file).
PALETTE_POINTER_SITES = {
    0x8E: ((0xB2020, 0), (0xB2098, 1), (0xB2188, 2)),
    0x8F: ((0xB2024, 0), (0xB218C, 0), (0xA1C14, 1), (0xB209C, 2)),
    0x90: ((0xB2028, 0), (0xB2190, 0), (0xA1C18, 1), (0xB20A0, 2)),
    0x91: ((0xB202C, 0), (0xB2194, 0), (0xA1C1C, 1), (0xB20A4, 2)),
}


@dataclass(frozen=True)
class CompactFighterFile:
    data: bytes
    old_palette_offsets: tuple[int, ...]
    new_palette_offsets: tuple[int, ...]
    frame_count: int


class _BitReader:
    def __init__(self, data: bytes | memoryview):
        self.data = data
        self.pos = 0

    def read(self, count: int) -> int:
        value = 0
        for _ in range(count):
            value = (value << 1) | (
                (self.data[self.pos >> 3] >> (7 - (self.pos & 7))) & 1
            )
            self.pos += 1
        return value


class _BitWriter:
    def __init__(self) -> None:
        self.bits: list[int] = []

    def write(self, value: int, count: int) -> None:
        for shift in range(count - 1, -1, -1):
            self.bits.append((value >> shift) & 1)

    def to_bytes(self) -> bytes:
        result = bytearray((len(self.bits) + 7) // 8)
        for index, bit in enumerate(self.bits):
            if bit:
                result[index >> 3] |= 1 << (7 - (index & 7))
        return bytes(result)


def _u32(data: bytes | bytearray, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def _signed32(value: int) -> int:
    return value - 0x100000000 if value & 0x80000000 else value


def _align4(value: int) -> int:
    return (value + 3) & ~3


def _align8(value: int) -> int:
    return (value + 7) & ~7


def _parse_table(data: bytes, table_offset: int):
    rows = int.from_bytes(data[table_offset : table_offset + 2], "big")
    model_count = int.from_bytes(data[table_offset + 2 : table_offset + 4], "big")
    pattern_base = table_offset + 4 + 104 * model_count
    models = []

    for model_id in range(model_count):
        offset = table_offset + 4 + 104 * model_id
        models.append(
            {
                "pattern_offset": _u32(data, offset),
                "bpp": int.from_bytes(data[offset + 4 : offset + 6], "big"),
                "normal_bits": tuple(
                    int.from_bytes(
                        data[offset + 6 + i * 2 : offset + 8 + i * 2], "big"
                    )
                    for i in range(13)
                ),
                "zero_bits": tuple(
                    int.from_bytes(
                        data[offset + 32 + i * 2 : offset + 34 + i * 2], "big"
                    )
                    for i in range(3)
                ),
                "normal_bases": tuple(
                    _u32(data, offset + 40 + i * 4) for i in range(13)
                ),
                "zero_bases": tuple(
                    _u32(data, offset + 92 + i * 4) for i in range(3)
                ),
            }
        )

    return rows, model_count, pattern_base, models


def _find_type5_shapes(data: bytes) -> tuple[tuple[int, int], ...]:
    shapes = []
    for offset in range(0, len(data) - 20, 4):
        if _u32(data, offset) != offset + 8 or _u32(data, offset + 4) != 0:
            continue
        image_offset = _u32(data, offset + 8)
        dimensions = _u32(data, offset + 12)
        width = (dimensions >> 16) & 0xFFFF
        height = dimensions & 0xFFFF
        if not (offset + 0x14 <= image_offset < len(data)):
            continue
        if not (1 <= width <= 512 and 1 <= height <= 512):
            continue
        if data[image_offset : image_offset + 4] != b"\x05\x00\x00\x00":
            continue
        shapes.append((offset, image_offset))
    return tuple(shapes)


def _decode_type5(data: bytes, image_offset: int):
    table_offset = image_offset + _signed32(_u32(data, image_offset + 4))
    dimensions = _u32(data, image_offset + 8)
    height = (dimensions >> 16) & 0xFFFF
    width = dimensions & 0xFFFF
    rows, model_count, pattern_base, models = _parse_table(data, table_offset)

    reader = _BitReader(memoryview(data)[image_offset + 12 :])
    model_id = reader.read(6)
    if model_id >= model_count:
        raise PatchError("invalid Type-5 model selector")
    model = models[model_id]

    blocks_wide = width // 4
    total_blocks = blocks_wide * (height // rows)
    output = bytearray(width * height)
    block_index = 0

    while block_index < total_blocks:
        code = reader.read(4)
        if code < 13:
            pattern_index = (
                model["normal_bases"][code]
                + reader.read(model["normal_bits"][code])
            )
            bytes_per_pattern = rows * 4 * model["bpp"] // 8
            pattern_offset = (
                pattern_base
                + model["pattern_offset"]
                + pattern_index * bytes_per_pattern
            )
            pattern = _BitReader(
                data[pattern_offset : pattern_offset + bytes_per_pattern]
            )
            pixels = [pattern.read(model["bpp"]) for _ in range(rows * 4)]
            by, bx = divmod(block_index, blocks_wide)
            for row in range(rows):
                target = (by * rows + row) * width + bx * 4
                output[target : target + 4] = bytes(
                    pixels[row * 4 : (row + 1) * 4]
                )
            block_index += 1
        else:
            zero_index = code - 13
            run = (
                model["zero_bases"][zero_index]
                + reader.read(model["zero_bits"][zero_index])
                + 1
            )
            block_index += run
            if block_index > total_blocks:
                raise PatchError("Type-5 transparent run exceeds image")

    return {
        "pixels": bytes(output),
        "bits": reader.pos,
        "stream_bytes": (reader.pos + 7) // 8,
        "model": model_id,
        "bpp": model["bpp"],
        "rows": rows,
        "width": width,
        "height": height,
        "table_offset": table_offset,
    }


def _blocks(pixels: bytes, width: int, height: int, rows: int) -> tuple[bytes, ...]:
    result = []
    for y in range(0, height, rows):
        for x in range(0, width, 4):
            block = bytearray()
            for row in range(rows):
                start = (y + row) * width + x
                block.extend(pixels[start : start + 4])
            result.append(bytes(block))
    return tuple(result)


def _pack_pattern(block: bytes, bpp: int) -> bytes:
    writer = _BitWriter()
    for pixel in block:
        writer.write(pixel, bpp)
    return writer.to_bytes()


def _compact_palette(values: list[int]) -> list[int]:
    if len(values) == 16:
        return values
    if len(values) not in (63, 64):
        raise PatchError(f"unsupported PRIS palette count {len(values)}")
    return [values[0], *(values[index] for index in BODY_PALETTE_REPRESENTATIVES)]


def build_compact_pris_file(source: bytes, table_offset: int) -> CompactFighterFile:
    shapes = _find_type5_shapes(source)
    if not shapes:
        raise PatchError("no Type-5 fighter shapes found")

    rows, model_count, pattern_base, models = _parse_table(source, table_offset)
    if rows != 2 or model_count != 2:
        raise PatchError("unexpected PRIS Type-5 table geometry")

    decoded = []
    blocks_by_frame = []
    frequencies = [Counter() for _ in range(model_count)]

    for _shape_offset, image_offset in shapes:
        frame = _decode_type5(source, image_offset)
        if frame["bpp"] == 6:
            target_pixels = bytes(BODY_INDEX_MAP[pixel] for pixel in frame["pixels"])
        elif frame["bpp"] == 4:
            target_pixels = frame["pixels"]
        else:
            raise PatchError(f"unsupported PRIS Type-5 bpp {frame['bpp']}")

        frame_blocks = _blocks(
            target_pixels, frame["width"], frame["height"], frame["rows"]
        )
        for block in frame_blocks:
            if any(block):
                frequencies[frame["model"]][block] += 1
        decoded.append((frame, target_pixels))
        blocks_by_frame.append(frame_blocks)

    patterns = [
        tuple(pattern for pattern, _count in counter.most_common())
        for counter in frequencies
    ]
    pattern_indices = [
        {pattern: index for index, pattern in enumerate(model_patterns)}
        for model_patterns in patterns
    ]

    table = bytearray(source[table_offset:pattern_base])
    pattern_blob = bytearray()
    pattern_offsets = []

    for model_id, model_patterns in enumerate(patterns):
        pattern_offsets.append(len(pattern_blob))
        for pattern in model_patterns:
            pattern_blob.extend(_pack_pattern(pattern, 4))

        model_offset = 4 + 104 * model_id
        table[model_offset : model_offset + 4] = pattern_offsets[-1].to_bytes(
            4, "big"
        )
        table[model_offset + 4 : model_offset + 6] = (4).to_bytes(2, "big")

    table_blob = bytearray(table)
    table_blob.extend(pattern_blob)
    while (table_offset + len(table_blob)) % 4:
        table_blob.append(0)

    relocation: dict[int, int] = {}
    frame_blob = bytearray()
    current = table_offset + len(table_blob)

    def zero_plan(model_id: int, run: int):
        model = models[model_id]

        @lru_cache(None)
        def solve(remaining: int):
            if remaining == 0:
                return 0, ()
            best = None
            for zero_index, (bits, base) in enumerate(
                zip(model["zero_bits"], model["zero_bases"])
            ):
                for extra in range(1 << bits):
                    count = base + extra + 1
                    if count > remaining:
                        continue
                    tail_cost, tail = solve(remaining - count)
                    candidate = (
                        4 + bits + tail_cost,
                        ((13 + zero_index, extra, bits),) + tail,
                    )
                    if best is None or candidate[0] < best[0]:
                        best = candidate
            if best is None:
                raise PatchError("cannot encode Type-5 transparent run")
            return best

        return solve(run)[1]

    for frame_index, ((old_shape, old_image), (frame, target_pixels)) in enumerate(
        zip(shapes, decoded)
    ):
        if current % 4:
            padding = 4 - (current % 4)
            frame_blob.extend(b"\x00" * padding)
            current += padding

        model_id = frame["model"]
        model = models[model_id]
        writer = _BitWriter()
        writer.write(model_id, 6)

        blocks = blocks_by_frame[frame_index]
        index = 0
        while index < len(blocks):
            if not any(blocks[index]):
                end = index + 1
                while end < len(blocks) and not any(blocks[end]):
                    end += 1
                for code, extra, bits in zero_plan(model_id, end - index):
                    writer.write(code, 4)
                    writer.write(extra, bits)
                index = end
                continue

            pattern_index = pattern_indices[model_id][blocks[index]]
            for code, (base, bits) in enumerate(
                zip(model["normal_bases"], model["normal_bits"])
            ):
                if base <= pattern_index < base + (1 << bits):
                    writer.write(code, 4)
                    writer.write(pattern_index - base, bits)
                    break
            else:
                raise PatchError("compact PRIS dictionary exceeds Type-5 class capacity")
            index += 1

        stream = writer.to_bytes()
        new_shape = current
        new_image = new_shape + 20
        relocation[old_shape] = new_shape
        relocation[old_image] = new_image

        descriptor = bytearray(source[old_shape : old_shape + 20])
        descriptor[0:4] = (new_shape + 8).to_bytes(4, "big")
        descriptor[8:12] = new_image.to_bytes(4, "big")

        wrapper = bytearray()
        wrapper.extend((0x05000000).to_bytes(4, "big"))
        wrapper.extend(((table_offset - new_image) & 0xFFFFFFFF).to_bytes(4, "big"))
        wrapper.extend(source[old_image + 8 : old_image + 12])

        built = bytearray(descriptor)
        built.extend(wrapper)
        built.extend(stream)
        built.extend(b"\x00" * (_align4(len(built)) - len(built)))
        frame_blob.extend(built)
        current += len(built)

        # Build-time round-trip guard for every emitted frame.
        _ = target_pixels

    last_shape, _last_image = shapes[-1]
    last_frame = decoded[-1][0]
    suffix_offset = (
        last_shape + 32 + _align4(last_frame["stream_bytes"])
    )

    old_palette_offsets = []
    new_palette_offsets = []
    suffix = bytearray()
    cursor = suffix_offset

    while cursor + 4 <= len(source):
        count = _u32(source, cursor)
        if count not in (16, 63, 64):
            break
        values = [
            int.from_bytes(source[cursor + 4 + 2 * i : cursor + 6 + 2 * i], "big")
            for i in range(count)
        ]
        old_palette_offsets.append(cursor)
        new_palette_offsets.append(current + len(suffix))
        relocation[cursor] = new_palette_offsets[-1]

        compact_values = _compact_palette(values)
        suffix.extend(len(compact_values).to_bytes(4, "big"))
        for value in compact_values:
            suffix.extend(value.to_bytes(2, "big"))
        while len(suffix) % 4:
            suffix.append(0)

        cursor = _align4(cursor + 4 + count * 2)

    suffix.extend(source[cursor:])
    final_size = _align8(table_offset + len(table_blob) + len(frame_blob) + len(suffix))
    suffix.extend(
        b"\x00"
        * (final_size - (table_offset + len(table_blob) + len(frame_blob) + len(suffix)))
    )

    prefix = bytearray(source[:table_offset])
    for offset in range(0, len(prefix) - 3, 4):
        value = _u32(prefix, offset)
        if value in relocation:
            prefix[offset : offset + 4] = relocation[value].to_bytes(4, "big")

    result = bytes(prefix + table_blob + frame_blob + suffix)

    # Independently decode every emitted frame and compare with the selected target.
    emitted_shapes = _find_type5_shapes(result)
    if len(emitted_shapes) != len(shapes):
        raise PatchError("compact PRIS frame-count mismatch")
    for emitted, (_stock_frame, target_pixels) in zip(emitted_shapes, decoded):
        round_trip = _decode_type5(result, emitted[1])
        if round_trip["pixels"] != target_pixels:
            raise PatchError("compact PRIS Type-5 round-trip mismatch")

    return CompactFighterFile(
        result,
        tuple(old_palette_offsets),
        tuple(new_palette_offsets),
        len(shapes),
    )


def _file_entry_offset(file_id: int) -> int:
    return FILE_TABLE_ROM + file_id * FILE_ENTRY_SIZE


def compact_pris_file(rom: RomImage, file_id: int) -> tuple[str, ...]:
    try:
        spec = SPECS[file_id]
    except KeyError as exc:
        raise PatchError(f"unsupported compact PRIS file 0x{file_id:02X}") from exc

    entry = _file_entry_offset(file_id)
    rom.expect_u32(entry, spec.start)
    rom.expect_u32(entry + 4, spec.end)
    rom.expect_u32(entry + 8, 0)

    source = bytes(rom.data[spec.start : spec.end])
    built = build_compact_pris_file(source, spec.table_offset)
    if len(built.data) != spec.expected_compact_size:
        raise PatchError(
            f"file 0x{file_id:02X} compact size 0x{len(built.data):X}; "
            f"expected 0x{spec.expected_compact_size:X}"
        )

    sites = PALETTE_POINTER_SITES[file_id]
    for site, palette_index in sites:
        old_value = built.old_palette_offsets[palette_index]
        rom.expect_u32(site, old_value)
    for site, palette_index in sites:
        rom.write_u32(site, built.new_palette_offsets[palette_index])

    rom.write_bytes(spec.start, built.data)
    if len(built.data) < spec.end - spec.start:
        rom.write_bytes(
            spec.start + len(built.data),
            bytes((spec.end - spec.start) - len(built.data)),
        )
    rom.write_u32(entry + 4, spec.start + len(built.data))

    return (
        (
            f"compact PRIS file 0x{file_id:02X}: "
            f"0x{spec.end - spec.start:X} -> 0x{len(built.data):X}"
        ),
        f"{built.frame_count} Type-5 frames round-trip validated",
    )
