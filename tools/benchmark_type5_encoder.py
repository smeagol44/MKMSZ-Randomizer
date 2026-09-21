#!/usr/bin/env python3
"""Benchmark MKMSZ stock Type-5 fighter compression against a generated encoder.

This tool does not modify the ROM. It:
1. verifies the supported USA Rev 0 ROM,
2. locates the stock file-0x87 Sub-Zero Type-5 fighter frames,
3. decodes every native Type-5 frame to raw indexed pixels,
4. re-encodes those exact pixels with the project encoder-v2 strategy,
   generalized to the stock four-model layout, and
5. reports apples-to-apples storage totals.

The benchmark intentionally keeps the stock frame-to-model assignment and
stock per-model normal/zero-run class widths while regenerating/frequency-
ordering the pattern dictionaries. This isolates codec efficiency from
character artwork differences.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse

SUPPORTED_SHA256 = "9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6"
FILE87_ROM = 0x748920
FILE87_SIZE = 0x459E0


class BitReader:
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


def u32be(data: bytes, off: int) -> int:
    return int.from_bytes(data[off : off + 4], "big")


def signed32(value: int) -> int:
    return value - 0x100000000 if value & 0x80000000 else value


def align4(value: int) -> int:
    return (value + 3) & ~3


def parse_table(file_data: bytes, table_off: int):
    rows = int.from_bytes(file_data[table_off : table_off + 2], "big")
    model_count = int.from_bytes(file_data[table_off + 2 : table_off + 4], "big")
    pattern_base = table_off + 4 + 104 * model_count
    models = []

    for model_id in range(model_count):
        mo = table_off + 4 + 104 * model_id
        pattern_off = u32be(file_data, mo)
        bpp = int.from_bytes(file_data[mo + 4 : mo + 6], "big")
        normal_bits = [
            int.from_bytes(file_data[mo + 6 + i * 2 : mo + 8 + i * 2], "big")
            for i in range(13)
        ]
        zero_bits = [
            int.from_bytes(file_data[mo + 32 + i * 2 : mo + 34 + i * 2], "big")
            for i in range(3)
        ]
        normal_bases = [u32be(file_data, mo + 40 + i * 4) for i in range(13)]
        zero_bases = [u32be(file_data, mo + 92 + i * 4) for i in range(3)]
        models.append(
            {
                "pattern_off": pattern_off,
                "bpp": bpp,
                "normal_bits": normal_bits,
                "zero_bits": zero_bits,
                "normal_bases": normal_bases,
                "zero_bases": zero_bases,
            }
        )

    return rows, model_count, pattern_base, models


def decode_type5(file_data: bytes, image_off: int):
    assert file_data[image_off : image_off + 4] == b"\x05\x00\x00\x00"

    table_off = image_off + signed32(u32be(file_data, image_off + 4))
    dims = u32be(file_data, image_off + 8)
    height = (dims >> 16) & 0xFFFF
    width = dims & 0xFFFF

    rows, model_count, pattern_base, models = parse_table(file_data, table_off)
    reader = BitReader(memoryview(file_data)[image_off + 12 :])
    model_id = reader.read(6)
    assert model_id < model_count
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
            pattern_off = (
                pattern_base
                + model["pattern_off"]
                + pattern_index * bytes_per_pattern
            )
            pattern = BitReader(
                file_data[pattern_off : pattern_off + bytes_per_pattern]
            )
            pixels = [pattern.read(model["bpp"]) for _ in range(rows * 4)]
            by, bx = divmod(block_index, blocks_wide)
            for ry in range(rows):
                dst = (by * rows + ry) * width + bx * 4
                output[dst : dst + 4] = bytes(pixels[ry * 4 : (ry + 1) * 4])
            block_index += 1
        else:
            zero_index = code - 13
            run = (
                model["zero_bases"][zero_index]
                + reader.read(model["zero_bits"][zero_index])
                + 1
            )
            block_index += run
            assert block_index <= total_blocks

    return {
        "pixels": bytes(output),
        "bits": reader.pos,
        "stream_bytes": (reader.pos + 7) // 8,
        "model": model_id,
        "bpp": model["bpp"],
        "rows": rows,
        "width": width,
        "height": height,
        "table_off": table_off,
    }


def blocks_for(decoded):
    width = decoded["width"]
    rows = decoded["rows"]
    pixels = decoded["pixels"]
    out = []

    for y in range(0, decoded["height"], rows):
        for x in range(0, width, 4):
            block = bytearray()
            for ry in range(rows):
                start = (y + ry) * width + x
                block.extend(pixels[start : start + 4])
            out.append(bytes(block))

    return out


def find_type5_shapes(file_data: bytes):
    shapes = []

    for off in range(0, len(file_data) - 20, 4):
        if u32be(file_data, off) != off + 8 or u32be(file_data, off + 4) != 0:
            continue

        image_off = u32be(file_data, off + 8)
        dims = u32be(file_data, off + 12)
        width = (dims >> 16) & 0xFFFF
        height = dims & 0xFFFF

        if not (off + 0x14 <= image_off < len(file_data)):
            continue
        if not (1 <= width <= 512 and 1 <= height <= 512):
            continue
        if file_data[image_off : image_off + 4] != b"\x05\x00\x00\x00":
            continue

        shapes.append((off, image_off))

    return shapes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    args = parser.parse_args()

    rom = args.rom.read_bytes()
    digest = sha256(rom).hexdigest()
    if digest != SUPPORTED_SHA256:
        raise SystemExit(
            f"Unsupported ROM SHA-256 {digest}; expected {SUPPORTED_SHA256}"
        )

    file_data = rom[FILE87_ROM : FILE87_ROM + FILE87_SIZE]
    shapes = find_type5_shapes(file_data)
    assert len(shapes) == 341

    decoded = {image: decode_type5(file_data, image) for _, image in shapes}
    table_offsets = {item["table_off"] for item in decoded.values()}
    assert table_offsets == {0x14AC}

    first_shape = min(shape for shape, _ in shapes)
    last_shape, last_image = max(shapes)
    last = decoded[last_image]
    last_end = last_shape + 32 + align4(last["stream_bytes"])

    # Exact stock accounting.
    stock_table_bytes = first_shape - 0x14AC
    stock_stream_bytes = sum(align4(item["stream_bytes"]) for item in decoded.values())
    frame_overhead = 32 * len(shapes)
    stock_total = stock_table_bytes + stock_stream_bytes + frame_overhead
    assert stock_total == last_end - 0x14AC

    raw_bytes = sum(len(item["pixels"]) for item in decoded.values())

    # Re-encode using the same stock four-model class geometries but rebuilt,
    # frequency-ordered dictionaries containing only patterns used by this corpus.
    rows, model_count, _, models = parse_table(file_data, 0x14AC)
    assert rows == 2 and model_count == 4

    freq_by_model = {model_id: Counter() for model_id in range(model_count)}
    blocks_by_image = {}

    for image, item in decoded.items():
        blocks = blocks_for(item)
        blocks_by_image[image] = blocks
        for block in blocks:
            if any(block):
                freq_by_model[item["model"]][block] += 1

    pattern_code = {}
    unique_counts = {}

    for model_id, model in enumerate(models):
        patterns = [pattern for pattern, _ in freq_by_model[model_id].most_common()]
        unique_counts[model_id] = len(patterns)

        for index, pattern in enumerate(patterns):
            for code, (base, extra_bits) in enumerate(
                zip(model["normal_bases"], model["normal_bits"])
            ):
                if base <= index < base + (1 << extra_bits):
                    pattern_code[(model_id, pattern)] = (
                        code,
                        index - base,
                        extra_bits,
                    )
                    break
            else:
                raise AssertionError(
                    f"model {model_id}: {len(patterns)} patterns exceed class capacity"
                )

    @lru_cache(None)
    def zero_cost(model_id: int, run: int) -> int:
        if run == 0:
            return 0

        model = models[model_id]
        best = 1 << 60

        for bits, base in zip(model["zero_bits"], model["zero_bases"]):
            for extra in range(1 << bits):
                count = base + extra + 1
                if count <= run:
                    best = min(best, 4 + bits + zero_cost(model_id, run - count))

        return best

    generated_bits = 0
    generated_stream_bytes = 0

    for image, item in decoded.items():
        model_id = item["model"]
        bits = 6
        blocks = blocks_by_image[image]
        index = 0

        while index < len(blocks):
            if not any(blocks[index]):
                end = index + 1
                while end < len(blocks) and not any(blocks[end]):
                    end += 1
                bits += zero_cost(model_id, end - index)
                index = end
            else:
                code, extra, extra_bits = pattern_code[(model_id, blocks[index])]
                _ = code, extra  # values are structurally validated by lookup
                bits += 4 + extra_bits
                index += 1

        generated_bits += bits
        generated_stream_bytes += align4((bits + 7) // 8)

    generated_table_bytes = 4 + 104 * model_count
    for model_id, model in enumerate(models):
        bytes_per_pattern = rows * 4 * model["bpp"] // 8
        generated_table_bytes += unique_counts[model_id] * bytes_per_pattern

    generated_total = (
        generated_table_bytes + generated_stream_bytes + frame_overhead
    )

    print(f"Type-5 frames: {len(shapes)}")
    print(f"Raw decoded pixels: {raw_bytes:,} bytes")
    print()
    print("Midway stock:")
    print(f"  shared table/dictionaries: {stock_table_bytes:,}")
    print(f"  padded compressed streams: {stock_stream_bytes:,}")
    print(f"  frame/descriptor/wrapper overhead: {frame_overhead:,}")
    print(f"  total: {stock_total:,}")
    print()
    print("Generated encoder-v2 benchmark:")
    print(f"  shared table/dictionaries: {generated_table_bytes:,}")
    print(f"  padded compressed streams: {generated_stream_bytes:,}")
    print(f"  frame/descriptor/wrapper overhead: {frame_overhead:,}")
    print(f"  total: {generated_total:,}")
    print()
    delta = generated_total - stock_total
    pct = delta / stock_total * 100.0
    print(f"Delta vs Midway: {delta:+,} bytes ({pct:+.3f}%)")
    print(
        f"Compression factor: stock {raw_bytes / stock_total:.4f}x, "
        f"generated {raw_bytes / generated_total:.4f}x"
    )
    print(f"Generated compressed-stream bits: {generated_bits:,}")


if __name__ == "__main__":
    main()
