#!/usr/bin/env python3
"""MKMSZR Sektor 16-color visual/storage experiment v01.

Input: exact Runtime-confirmed v75 Sektor missile-flight proof.
Output: disposable Sektor takeover proof using 16 total fighter palette entries
(transparent index 0 + 15 opaque colors) across the shared Type-5 Sektor corpus.

This is deliberately a palette/index-normalization proof, not a production change.
It preserves v75 scripts, animation mappings, timing, placement, move logic, helpers,
collision, allocation layout, and Type-5 bitstreams. Only:
  * the shared 5-bpp Type-5 dictionary pixel indices are normalized from 0..31 to 0..15;
  * the primary and alternate Sektor palette sources are reduced to matching 16-entry
    weighted RGB centroids in MKMSZ BGR555 source-palette format;
  * N64 CRC1/CRC2 are recomputed.

The 15 opaque clusters are derived deterministically from actual decoded pixel usage
in the first 158 v75 takeover frames (excluding the two missile-line special frames
from the clustering weights). The resulting index map is nevertheless applied to the
entire shared dictionary, so every Type-5 frame in this proof uses <= 16 indices.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import numpy as np

V75_SHA256 = "e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
ROM_SIZE = 0x1000000
FILE87_ROM = 0x00F40000
FILE87_SIZE = 0x0004E790
TYPE5_TABLE = 0x14AC
PRIMARY_COUNT = 0x45848
PRIMARY_COLORS = 0x4584C
ALT_COUNT = 0x458CC
ALT_COLORS = 0x458D0

def be32(b, o): return int.from_bytes(b[o:o+4], "big")
def put32(b, o, v): b[o:o+4] = int(v & 0xffffffff).to_bytes(4, "big")
def signed32(v): return v - 0x100000000 if v & 0x80000000 else v

class BitReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0
    def read(self, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | ((self.data[self.pos >> 3] >> (7 - (self.pos & 7))) & 1)
            self.pos += 1
        return v

def parse_table(fd, off):
    rows = int.from_bytes(fd[off:off+2], "big")
    model_count = int.from_bytes(fd[off+2:off+4], "big")
    pattern_base = off + 4 + 104 * model_count
    models = []
    for i in range(model_count):
        mo = off + 4 + 104*i
        models.append({
            "pattern_off": be32(fd, mo),
            "bpp": int.from_bytes(fd[mo+4:mo+6], "big"),
            "normal_bits": [int.from_bytes(fd[mo+6+2*j:mo+8+2*j], "big") for j in range(13)],
            "zero_bits": [int.from_bytes(fd[mo+32+2*j:mo+34+2*j], "big") for j in range(3)],
            "normal_bases": [be32(fd, mo+40+4*j) for j in range(13)],
            "zero_bases": [be32(fd, mo+92+4*j) for j in range(3)],
        })
    return rows, model_count, pattern_base, models

def decode_type5(fd, image_off):
    assert fd[image_off:image_off+4] == b"\x05\x00\x00\x00"
    table_off = image_off + signed32(be32(fd, image_off+4))
    dims = be32(fd, image_off+8)
    height = (dims >> 16) & 0xffff
    width = dims & 0xffff
    rows, model_count, pattern_base, models = parse_table(fd, table_off)
    br = BitReader(memoryview(fd)[image_off+12:])
    model_id = br.read(6)
    assert model_id < model_count
    model = models[model_id]
    blocks_wide = width // 4
    total_blocks = blocks_wide * (height // rows)
    out = bytearray(width * height)
    block_index = 0
    while block_index < total_blocks:
        code = br.read(4)
        if code < 13:
            pattern_index = model["normal_bases"][code] + br.read(model["normal_bits"][code])
            bytes_per_pattern = rows * 4 * model["bpp"] // 8
            po = pattern_base + model["pattern_off"] + pattern_index * bytes_per_pattern
            pr = BitReader(fd[po:po+bytes_per_pattern])
            pixels = [pr.read(model["bpp"]) for _ in range(rows*4)]
            by, bx = divmod(block_index, blocks_wide)
            for ry in range(rows):
                dst = (by*rows + ry) * width + bx*4
                out[dst:dst+4] = bytes(pixels[ry*4:(ry+1)*4])
            block_index += 1
        else:
            zi = code - 13
            run = model["zero_bases"][zi] + br.read(model["zero_bits"][zi]) + 1
            block_index += run
            assert block_index <= total_blocks
    return bytes(out)

def find_shapes(fd):
    out = []
    for off in range(0, len(fd)-20, 4):
        if be32(fd, off) != off + 8 or be32(fd, off+4) != 0:
            continue
        image_off = be32(fd, off+8)
        dims = be32(fd, off+12)
        width = (dims >> 16) & 0xffff
        height = dims & 0xffff
        if not (off + 0x14 <= image_off < len(fd)):
            continue
        if not (1 <= width <= 512 and 1 <= height <= 512):
            continue
        if fd[image_off:image_off+4] != b"\x05\x00\x00\x00":
            continue
        out.append((off, image_off))
    return out

def target_rgb(word):
    return np.array([word & 31, (word >> 5) & 31, (word >> 10) & 31], dtype=float)

def rgb_to_target(rgb):
    r, g, b = [max(0, min(31, int(round(x)))) for x in rgb]
    return 0x8000 | (b << 10) | (g << 5) | r

def weighted_clusters(counts, palette, k=15):
    used = [i for i in range(1, 32) if counts[i] > 0]
    pts = np.array([target_rgb(palette[i]) for i in used])
    wt = np.array([counts[i] for i in used], dtype=float)

    first = max(range(len(used)), key=lambda j: (wt[j], -used[j]))
    centers = [pts[first].copy()]
    while len(centers) < k:
        d2 = np.min(np.array([np.sum((pts-c)**2, axis=1) for c in centers]), axis=0)
        score = d2 * np.sqrt(wt)
        centers.append(pts[int(np.argmax(score))].copy())
    centers = np.array(centers)
    labels = np.zeros(len(used), dtype=int)

    for _ in range(100):
        dist = np.sum((pts[:,None,:] - centers[None,:,:])**2, axis=2)
        new_labels = np.argmin(dist, axis=1)
        new_centers = []
        for c in range(k):
            mask = new_labels == c
            if np.any(mask):
                new_centers.append(np.sum(pts[mask] * wt[mask,None], axis=0) / np.sum(wt[mask]))
            else:
                new_centers.append(centers[c])
        new_centers = np.array(new_centers)
        if np.array_equal(new_labels, labels) and np.allclose(new_centers, centers):
            labels = new_labels
            centers = new_centers
            break
        labels = new_labels
        centers = new_centers

    mapping = {0: 0}
    members = {c: [] for c in range(k)}
    for j, old_index in enumerate(used):
        c = int(labels[j])
        mapping[old_index] = c + 1
        members[c].append(old_index)
    return mapping, centers, members

def palette_from_clusters(src_palette, counts, members):
    out = [0] * 16
    out[0] = 0
    for c in range(15):
        inds = members[c]
        weights = np.array([counts[i] for i in inds], dtype=float)
        pts = np.array([target_rgb(src_palette[i]) for i in inds])
        center = np.sum(pts * weights[:,None], axis=0) / np.sum(weights)
        out[c+1] = rgb_to_target(center)
    return out

def remap_pattern5(raw5, mapping):
    value = int.from_bytes(raw5, "big")
    out = 0
    for i in range(8):
        shift = 35 - 5*i
        old = (value >> shift) & 0x1f
        new = mapping[old]
        out |= (new & 0x1f) << shift
    return out.to_bytes(5, "big")

def rol32(v, s):
    s &= 31
    return v & 0xffffffff if s == 0 else ((v << s) | (v >> (32-s))) & 0xffffffff

def update_crc_6102(rom):
    seed = 0xF8CA4DDC
    t1=t2=t3=t4=t5=t6=seed
    for off in range(0x1000, 0x101000, 4):
        value = be32(rom, off)
        total = (t6 + value) & 0xffffffff
        if total < t6:
            t4 = (t4 + 1) & 0xffffffff
        t6 = total
        t3 ^= value
        r = rol32(value, value & 31)
        t5 = (t5 + r) & 0xffffffff
        t2 ^= r if t2 > value else (t6 ^ value)
        t1 = (t1 + (t5 ^ value)) & 0xffffffff
    c1 = (t6 ^ t4 ^ t3) & 0xffffffff
    c2 = (t5 ^ t2 ^ t1) & 0xffffffff
    put32(rom, 0x10, c1)
    put32(rom, 0x14, c2)
    return c1, c2

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()

    base = args.baseline.read_bytes()
    assert len(base) == ROM_SIZE
    assert sha256(base).hexdigest() == V75_SHA256

    rom = bytearray(base)
    fd = bytearray(rom[FILE87_ROM:FILE87_ROM+FILE87_SIZE])
    shapes = find_shapes(fd)
    assert len(shapes) == 160
    assert min(s for s,_ in shapes) == 0x34A58

    rows, model_count, pattern_base, models = parse_table(fd, TYPE5_TABLE)
    assert rows == 2 and model_count == 64
    assert {m["bpp"] for m in models} == {5}
    assert {m["pattern_off"] for m in models} == {0}

    primary_count = be32(fd, PRIMARY_COUNT)
    alt_count = be32(fd, ALT_COUNT)
    assert primary_count == 0x40 and alt_count == 0x40
    primary = [int.from_bytes(fd[PRIMARY_COLORS+2*i:PRIMARY_COLORS+2*i+2], "big") for i in range(32)]
    alt = [int.from_bytes(fd[ALT_COLORS+2*i:ALT_COLORS+2*i+2], "big") for i in range(32)]
    assert primary[0] == 0 and alt[0] == 0

    counts = Counter()
    for _, image_off in shapes[:158]:
        counts.update(decode_type5(fd, image_off))

    mapping, centers, members = weighted_clusters(counts, primary, 15)
    assert set(mapping) == set(range(32))
    assert mapping[0] == 0
    assert max(mapping.values()) == 15

    primary16 = palette_from_clusters(primary, counts, members)
    alt16 = palette_from_clusters(alt, counts, members)

    # Shared dictionary occupies pattern_base up to the first 4-byte-aligned shape.
    first_shape = min(s for s,_ in shapes)
    pattern_bytes = first_shape - pattern_base
    pattern_count = pattern_bytes // 5
    padding = pattern_bytes % 5
    assert pattern_count == 40737 and padding == 3

    for i in range(pattern_count):
        off = pattern_base + i*5
        fd[off:off+5] = remap_pattern5(fd[off:off+5], mapping)

    for i, word in enumerate(primary16):
        fd[PRIMARY_COLORS+2*i:PRIMARY_COLORS+2*i+2] = int(word).to_bytes(2, "big")
    for i, word in enumerate(alt16):
        fd[ALT_COLORS+2*i:ALT_COLORS+2*i+2] = int(word).to_bytes(2, "big")

    # Upper palette entries remain untouched but are unreachable from remapped Type-5 art.
    rom[FILE87_ROM:FILE87_ROM+FILE87_SIZE] = fd

    # Static postcondition: every decoded Type-5 pixel index is now <= 15.
    check_fd = bytes(fd)
    max_index = 0
    for _, image_off in shapes:
        pix = decode_type5(check_fd, image_off)
        if pix:
            max_index = max(max_index, max(pix))
    assert max_index <= 15

    c1, c2 = update_crc_6102(rom)
    args.output.write_bytes(rom)

    print(f"output={args.output}")
    print(f"sha256={sha256(rom).hexdigest()}")
    print(f"crc1={c1:08X} crc2={c2:08X}")
    print(f"type5_frames={len(shapes)} pattern_count={pattern_count} max_index={max_index}")
    print("index_map=" + ",".join(f"{i}->{mapping[i]}" for i in range(32)))

if __name__ == "__main__":
    main()
