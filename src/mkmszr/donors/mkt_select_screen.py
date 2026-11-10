"""MKT's Character Select screen, decoded at runtime from the user's MKT ROM.

The web app's "Swap character" window shows this screen (user design, 2026-11-10): MKT's
select background and portrait grid, every portrait in grayscale except the fighters the
importer supports, and an MKT-style selection box that follows the mouse. Nothing from the
donor is stored in this repository; :func:`render` decodes it from the user's ROM.

Static-confirmed (MKT N64 USA Rev. 2; the decodes match the decoded copies in RAM of a
user-supplied save state at the select screen byte for byte):

* **Grid table** ``0x800A2940`` (ROM ``0xA2940``), 12-byte entries ``{u32 descriptor,
  u16 column, u16 row, u16 fighter id, u16 0}`` ended by a zero descriptor; read by
  ``0x80007E48`` (fighter id at ``+8``) and the select-screen setup ``0x800069A4``.
  Descriptors ``1`` and ``2`` are the two hidden slots (drawn with descriptor
  ``0x803E40A4``). Fighter names: pointer table ``0x800A6004``.
* **Portrait descriptors** ``{u32 image, u16 height 45, u16 width 34, u32 0, u32 palette}``
  in the select-screen file ROM ``[0x1364F4, 0x145EF0)``, loaded at RAM ``0x803E1534``.
  Images use codec ``0x14`` (dispatcher ``0x80081C4C``; PackBits ``0x8008209C``) and decode to
  36x45 CI8 (row pitch 36, index 0 transparent). Palettes: ``u32 count`` then RGBA5551 words.
* **Background**: file ROM ``[0x34A540, 0x3560F0)`` (file table ``0x800A2188``, RAM
  ``0x803F0F30``) starts with four palette pointers; background definition ``0x803F63C8``
  (passed to ``0x800090CC`` by ``0x8000679C``) places modules ``0x803F6308`` (0, 0x2B),
  ``0x803F6358`` (0, 0xC7) and ``0x803F6378`` (0xD4, 0xC9). Module placements are
  ``{u16 x, u16 y, u16 0x40, u16 flags, u16 image}`` (palette = flags >> 8, 0x10 =
  horizontal flip); the image list is ``{u16 w, u16 h, u32 offset}`` into one blob, ROM
  ``[0x3560F0, 0x365500)``: codec ``0x12`` (raw DEFLATE, ``0x800885C8``), 0x247B8 bytes,
  whose base the game keeps at ``0x801B3D10``.
* **Screen layout** (from the frame's display list in that save state; the bottom plates'
  layer has its own scroll offset, so positions are taken from the display list, not
  recomputed): ``BG_DRAW`` / ``BG_PLATES`` below; portraits at
  ``(59 + 34 * column, 14 + 45 * row)``, then 1-pixel grid lines (``GRID_LINES``,
  ``0x7BDB``); the selection box is a 34x45, 2-pixel frame in
  palette index 1 (``0x07C1``, green, at capture).
"""

from __future__ import annotations

import struct
import zlib

from .mkt_n64 import validate_mkt_n64_rev2

WIDTH, HEIGHT = 320, 240
SCISSOR = (319, 239)  # the display list's scissor: column 319 and row 239 stay black
GRID_TABLE = 0xA2940
NAME_TABLE = 0xA6004
VA_BASE = 0x80000000
CSS_FILE = (0x1364F4, 0x145EF0, 0x803E1534)  # ROM start, ROM end, RAM base
BG_FILE = (0x34A540, 0x3560F0, 0x803F0F30)
BG_BLOB = (0x3560F0, 0x365500)
BG_BLOB_SIZE = 0x247B8
HIDDEN_DESCRIPTOR = 0x803E40A4
PORTRAIT = (36, 45)  # stored width (row pitch), height
CELL = (34, 45)  # visible portrait and selection box size
GRID_ORIGIN = (59, 14)
BOX_COLOR = 0x07C1  # RGBA5551 green
GRID_COLOR = 0x7BDB
# 1-pixel grid lines (fill rectangles, inclusive) drawn after the portraits.
GRID_LINES = (
    (263, 14, 263, 193), (229, 14, 229, 238), (195, 14, 195, 238), (161, 14, 161, 238),
    (127, 14, 127, 238), (93, 14, 93, 238), (59, 14, 59, 193), (59, 14, 262, 14),
    (59, 59, 262, 59), (59, 104, 262, 104), (59, 149, 262, 149), (59, 194, 262, 194),
    (93, 239, 228, 239),
)  # fmt: skip
BOX_THICKNESS = 2
# Background draw lists: (module definition, placement index, screen x, screen y), in the
# display list's order; image, palette and flip come from the module placement.
BG_DRAW = (
    (0x803F6308, 3, 166, 46), (0x803F6308, 0, 6, 46), (0x803F6308, 4, 166, 48),
    (0x803F6308, 1, 6, 48), (0x803F6308, 5, 166, 130), (0x803F6308, 2, 6, 130),
)  # fmt: skip
BG_PLATES = ((0x803F6378, 0, 219, 205), (0x803F6358, 0, 10, 204))  # drawn over the portraits
# MKT fighter ids the importer can bring into MKMSZ -> RandomizerConfig.fighter.
IMPORTABLE = {6: "sektor"}


class SelectScreenError(ValueError):
    pass


def _u32(data: bytes, off: int) -> int:
    return struct.unpack_from(">I", data, off)[0]


def _file_offset(file: tuple[int, int, int], va: int) -> int:
    start, end, base = file
    off = start + (va - base)
    if not start <= off < end:
        raise SelectScreenError(f"pointer 0x{va:08X} is outside its file")
    return off


def _packbits(rom: bytes, off: int) -> bytes:
    header = _u32(rom, off)
    if header >> 24 != 0x14:
        raise SelectScreenError(f"unexpected portrait codec 0x{header >> 24:02X}")
    size, p, out = header & 0xFFFFFF, off + 4, bytearray()
    while len(out) < size:
        count = rom[p]
        p += 1
        if count >= 0x80:
            out += bytes((rom[p],)) * (0x101 - count)
            p += 1
        else:
            out += rom[p : p + count + 1]
            p += count + 1
    return bytes(out[:size])


def _palette(rom: bytes, off: int) -> list[int]:
    count = _u32(rom, off)
    if not 1 <= count <= 0x100:
        raise SelectScreenError("bad palette record")
    return list(struct.unpack_from(f">{count}H", rom, off + 4))


def _rgba(word: int) -> tuple[int, int, int, int]:
    r, g, b = (word >> 11) & 31, (word >> 6) & 31, (word >> 1) & 31
    return (r << 3 | r >> 2, g << 3 | g >> 2, b << 3 | b >> 2, 255 if word & 1 else 0)


def _gray(rgba: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    y = (299 * rgba[0] + 587 * rgba[1] + 114 * rgba[2] + 500) // 1000
    return (y, y, y, rgba[3])


def _blit(canvas: bytearray, pixels: bytes, pitch: int, w: int, h: int, x0: int, y0: int,
          palette: list[int], *, flip: bool = False, gray: bool = False) -> None:  # fmt: skip
    colors = [_rgba(word) for word in palette]
    if gray:
        colors = [_gray(c) for c in colors]
    for y in range(h):
        sy = y0 + y
        if not 0 <= sy < SCISSOR[1]:
            continue
        row = pixels[y * pitch : y * pitch + w]
        for x in range(w):
            index = row[w - 1 - x] if flip else row[x]
            if index >= len(colors) or not colors[index][3]:
                continue  # index 0 / alpha 0 is transparent
            sx = x0 + x
            if 0 <= sx < SCISSOR[0]:
                o = 4 * (sy * WIDTH + sx)
                canvas[o : o + 4] = bytes(colors[index])


def _names(rom: bytes) -> list[str]:
    out = []
    for i in range(32):
        p = _u32(rom, NAME_TABLE + 4 * i) - VA_BASE
        out.append(rom[p : rom.index(b"\0", p)].decode("latin1") if 0 <= p < len(rom) else "")
    return out


def grid(rom: bytes) -> list[dict]:
    """The select grid: one dict per cell (fighter id, name, column, row, descriptor)."""

    names, cells = _names(rom), []
    for off in range(GRID_TABLE, GRID_TABLE + 12 * 64, 12):
        descriptor, col, row, fighter = struct.unpack_from(">IHHH", rom, off)
        if descriptor == 0:
            return cells
        cells.append({
            "fighter_id": fighter,
            "name": names[fighter] if fighter < len(names) else "",
            "column": col,
            "row": row,
            "hidden": descriptor < 3,
            "descriptor": HIDDEN_DESCRIPTOR if descriptor < 3 else descriptor,
        })  # fmt: skip
    raise SelectScreenError("select grid table is not terminated")


def _background(rom: bytes, draws) -> list[tuple[bytes, int, int, int, int, list[int], bool]]:
    """(pixels, w, h, x, y, palette, flip) for each entry of ``draws``."""

    blob_rom = rom[BG_BLOB[0] : BG_BLOB[1]]
    header = _u32(blob_rom, 0)
    if header != (0x12 << 24) | BG_BLOB_SIZE:
        raise SelectScreenError("unexpected background blob header")
    blob = zlib.decompressobj(-15).decompress(blob_rom[4:])
    if len(blob) != BG_BLOB_SIZE:
        raise SelectScreenError("background blob size mismatch")
    palettes = [_palette(rom, _file_offset(BG_FILE, _u32(rom, BG_FILE[0] + 4 * k))) for k in range(4)]
    out = []
    for module, k, x, y in draws:
        m = _file_offset(BG_FILE, module)
        count, placements, images = _u32(rom, m + 4), _u32(rom, m + 8), _u32(rom, m + 12)
        if k >= count:
            raise SelectScreenError("background placement out of range")
        p, i = _file_offset(BG_FILE, placements), _file_offset(BG_FILE, images)
        _, _, _, flags, image = struct.unpack_from(">HHHHH", rom, p + 10 * k)
        w, h, offset = struct.unpack_from(">HHI", rom, i + 8 * image)
        pixels = blob[offset : offset + w * h]
        if len(pixels) != w * h or flags >> 8 >= len(palettes):
            raise SelectScreenError("background image outside the blob")
        out.append((pixels, w, h, x, y, palettes[flags >> 8], bool(flags & 0x10)))
    return out


def render(rom: bytes, importable: dict[int, str] | None = None) -> dict:
    """The select screen as a 320x240 RGBA image plus its cells.

    Returns ``{'width', 'height', 'rgba' (bytes), 'cell': (w, h), 'box_color' (r, g, b),
    'box_thickness', 'cells': [{fighter_id, name, column, row, x, y, hidden, fighter}]}``;
    ``fighter`` is the importer's name for a selectable cell, else ``None``. Selectable
    portraits keep their colours; every other portrait is grayscale.
    """

    validate_mkt_n64_rev2(rom)
    importable = IMPORTABLE if importable is None else importable
    canvas = bytearray(bytes((0, 0, 0, 255)) * (WIDTH * HEIGHT))
    for pixels, w, h, x, y, palette, flip in _background(rom, BG_DRAW):
        _blit(canvas, pixels, w, w, h, x, y, palette, flip=flip)
    cells = []
    for cell in grid(rom):
        d = _file_offset(CSS_FILE, cell["descriptor"])
        image, size, _, palette_va = struct.unpack_from(">IIII", rom, d)
        if size != (CELL[1] << 16) | CELL[0]:
            raise SelectScreenError("unexpected portrait size")
        pixels = _packbits(rom, _file_offset(CSS_FILE, image))
        if len(pixels) != PORTRAIT[0] * PORTRAIT[1]:
            raise SelectScreenError("unexpected portrait data size")
        fighter = None if cell["hidden"] else importable.get(cell["fighter_id"])
        x = GRID_ORIGIN[0] + CELL[0] * cell["column"]
        y = GRID_ORIGIN[1] + CELL[1] * cell["row"]
        _blit(canvas, pixels, PORTRAIT[0], PORTRAIT[0], PORTRAIT[1], x, y,
              _palette(rom, _file_offset(CSS_FILE, palette_va)), gray=fighter is None)  # fmt: skip
        cells.append({
            "fighter_id": cell["fighter_id"],
            "name": "?" if cell["hidden"] else cell["name"],
            "column": cell["column"],
            "row": cell["row"],
            "x": x,
            "y": y,
            "hidden": cell["hidden"],
            "fighter": fighter,
        })  # fmt: skip
    line = bytes(_rgba(GRID_COLOR)[:3] + (255,))
    for x0, y0, x1, y1 in GRID_LINES:
        for y in range(y0, min(y1 + 1, SCISSOR[1])):
            for x in range(x0, min(x1 + 1, SCISSOR[0])):
                canvas[4 * (y * WIDTH + x) : 4 * (y * WIDTH + x) + 4] = line
    for pixels, w, h, x, y, palette, flip in _background(rom, BG_PLATES):
        _blit(canvas, pixels, w, w, h, x, y, palette, flip=flip)
    return {
        "width": WIDTH,
        "height": HEIGHT,
        "rgba": bytes(canvas),
        "cell": CELL,
        "box_color": _rgba(BOX_COLOR)[:3],
        "box_thickness": BOX_THICKNESS,
        "cells": cells,
    }
