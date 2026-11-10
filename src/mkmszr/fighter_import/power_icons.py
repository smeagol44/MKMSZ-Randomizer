"""Sektor's Power Ups icons, generated from the MKT donor art at build time (R4 presentation).

Native format (Static-confirmed; checked against a gameplay save state): the Power Ups strip
(``0x800750F0``) and the new-power popup (``0x80062FF0``) draw the icon IDs of the table at
ROM ``0xA6BB0`` through ``0x80073CEC`` with the shared palette record ``0x800B1B28`` (count
``0x40``, then 64 BGR555 colours; ROM ``0xB2728``); nothing else uses that palette. The icons
are 28x28 CI8 records (IDs ``0x3C8..0x3D1``) of the permanent image bank in global file
``0x5D``: an LZW package of ``count`` records, each a 12-byte header (flags, width word,
height, ID, spare) followed by its pixels. Index 0 is transparent; every stock icon uses the
same circle of non-zero pixels.

Recipe (no stored art; deterministic for a given donor ROM):

* each Sektor icon composes donor frames in their MKT palettes (Sektor ``0x800BC12C``,
  ROCKET_P ``0x800BC3AC``, crosshair ``0x800BC3D0``) on a canvas with a steel radial
  background, at fixed placements;
* the canvas square is box-averaged to 28x28 and clipped to the stock circle;
* the two empty slots are a dark disc with a dash; Polar Blast keeps the stock icon;
* all nine are reduced together to 63 colours by a fixed median cut (index 0 transparent),
  which becomes the shared palette.

Slots follow the Sub-Zero power whose tier each Sektor move took (``power_order`` names), so
the shuffled icon table keeps working unchanged.
"""

from __future__ import annotations

from collections.abc import Callable

from ..patches.power_order import POWER_ICONS, POWER_NAMES
from . import effects
from .actions import robo_tracker as trk
from .mkt_fighter import SEKTOR, MktRom

N = 28  # icon size
PIXELS = N * N
PALETTE_ROM = 0xB2728  # 0x800B1B28: count word, then 64 BGR555 colours
PALETTE_COUNT = 0x40
BANK_FILE = 0x5D
SEKTOR_PALETTE, ROCKET_PALETTE, TARGET_PALETTE = 0x800BC12C, 0x800BC3AC, 0x800BC3D0
ROCKET_FRAME = 0x2668  # ROCKETD1
CHEST_OPEN = 0x29B4  # RBCHEST2
EMERGE_2 = 0x2B5C  # teleport emerge, 2nd frame (user choice)
SWEEP = 0x1E50
TARGET_FILL = 7  # the crosshair's 50% dither fill: a see-through tint in game, left out here
MASK_ICON = "ice-blast"  # any stock icon: they share one circle
KEEP_STOCK = ("polar-blast",)

RGB = tuple[int, int, int]


def bgr555_to_rgb(word: int) -> RGB:
    return (
        (word & 31) * 255 // 31,
        ((word >> 5) & 31) * 255 // 31,
        ((word >> 10) & 31) * 255 // 31,
    )


def rgb_to_bgr555(rgb: RGB) -> int:
    r, g, b = ((v * 31 + 127) // 255 for v in rgb)
    return (b << 10) | (g << 5) | r


class _Canvas:
    def __init__(self, width: int, height: int, background: Callable[[int, int], RGB]) -> None:
        self.w, self.h = width, height
        self.px = [background(x, y) for y in range(height) for x in range(width)]

    def put(self, fr: effects.EffectFrame, pal: list[RGB], x0: int, y0: int,
            shade: float = 1.0, skip: tuple[int, ...] = ()) -> None:  # fmt: skip
        for y in range(fr.height):
            for x in range(fr.width):
                i = fr.indices[y * fr.stride + x]
                if not i or i in skip:
                    continue
                xx, yy = x0 + x, y0 + y
                if 0 <= xx < self.w and 0 <= yy < self.h:
                    r, g, b = pal[i]
                    self.px[yy * self.w + xx] = (int(r * shade), int(g * shade), int(b * shade))

    def icon(self, x0: int, y0: int, size: int) -> list[RGB]:
        """Box-average the square at (x0, y0) of side ``size`` down to N x N."""

        out = []
        for y in range(N):
            for x in range(N):
                xs = range(x0 + x * size // N, x0 + (x + 1) * size // N)
                ys = range(y0 + y * size // N, y0 + (y + 1) * size // N)
                acc, n = [0, 0, 0], 0
                for yy in ys:
                    for xx in xs:
                        p = self.px[yy * self.w + xx]
                        acc[0] += p[0]
                        acc[1] += p[1]
                        acc[2] += p[2]
                        n += 1
                out.append((acc[0] // n, acc[1] // n, acc[2] // n))
        return out


def _radial(cx: int, cy: int, r: int) -> Callable[[int, int], RGB]:
    inner, outer = (205, 215, 230), (22, 28, 44)  # steel glow -> dark slate

    def f(x: int, y: int) -> RGB:
        d = min(1.0, (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / r)
        return tuple(int(inner[i] + (outer[i] - inner[i]) * d) for i in range(3))  # type: ignore[return-value]

    return f


class _Donor:
    def __init__(self, mkt: bytes) -> None:
        self.rom = MktRom(mkt)
        self.heap = self.rom.heap_bytes(SEKTOR)
        start, end = self.rom.dictionary(SEKTOR)
        self.dic = mkt[start:end]
        rgb = lambda va: [bgr555_to_rgb(c) for c in effects.mkt_palette(mkt, va)]
        self.sektor, self.rocket, self.target = (
            rgb(SEKTOR_PALETTE),
            rgb(ROCKET_PALETTE),
            rgb(TARGET_PALETTE),
        )

    def parts(self, frame: int) -> list[effects.EffectFrame]:
        return [effects.heap_descriptor_frame(self.heap, p.descriptor, self.dic)
                for p in self.rom.frame_parts(SEKTOR, frame)]  # fmt: skip

    def sprite(self, c: _Canvas, frame: int, ox: int, oy: int, shade: float = 1.0) -> None:
        """Draw a donor frame with its reference at (ox, oy): left = -anchor_x, top = -anchor_y."""

        for fr in self.parts(frame):
            c.put(fr, self.sektor, ox - fr.anchor_x, oy - fr.anchor_y, shade)


def _sektor_icons(d: _Donor) -> dict[str, list[RGB]]:
    rocket = d.parts(ROCKET_FRAME)[0]

    def straight() -> list[RGB]:
        c = _Canvas(96, 96, _radial(62, 44, 40))
        d.sprite(c, CHEST_OPEN, 34, 4)
        c.put(rocket, d.rocket, 46, 42)
        return c.icon(26, 16, 48)

    def double() -> list[RGB]:
        c = _Canvas(96, 96, _radial(62, 44, 40))
        d.sprite(c, CHEST_OPEN, 34, 4)
        c.put(rocket, d.rocket, 50, 36)
        c.put(rocket, d.rocket, 42, 48)
        return c.icon(26, 16, 48)

    def homing() -> list[RGB]:
        c = _Canvas(64, 64, _radial(28, 16, 30))
        target = effects.heap_descriptor_frame(d.heap, trk.TARGET_DESCRIPTOR, d.dic)
        c.put(target, d.target, 16, 2, skip=(TARGET_FILL,))
        c.put(trk.direction_frames(d.heap, d.dic)[1][0], d.rocket, 4, 14)  # climbing (1 o'clock)
        return c.icon(0, 0, 44)

    def teleport() -> list[RGB]:
        c = _Canvas(130, 130, _radial(64, 44, 50))
        d.sprite(c, EMERGE_2, 64, 34)
        top = 34 - d.parts(EMERGE_2)[0].anchor_y
        return c.icon(64 - 30 + 2, max(0, top - 2), 60)

    def slide(ghosts: int) -> list[RGB]:
        c = _Canvas(110, 110, _radial(60, 70, 46))
        for g in range(ghosts, 0, -1):
            d.sprite(c, SWEEP, 40 - 12 * g, -20, shade=0.35 + 0.2 * (ghosts - g))
        d.sprite(c, SWEEP, 40, -20)
        return c.icon(14, 40, 62)

    def empty() -> list[RGB]:
        return [(170, 176, 186) if 9 <= x <= 18 and 13 <= y <= 14 else (30, 34, 48)
                for y in range(N) for x in range(N)]  # fmt: skip

    return {
        "ice-blast": straight(), "slide": slide(0), "directional-ice": teleport(),
        "air-ice-blast": homing(), "ice-clone": empty(), "ice-shatter": double(),
        "super-slide": empty(), "freeze-on-contact": slide(2),
    }  # fmt: skip


def median_cut(colors: list[RGB], k: int) -> list[RGB]:
    """Deterministic median cut: split the box with the widest channel range at its median
    (ties by first colour), until ``k`` boxes; each box's colour is its integer mean."""

    boxes = [sorted(set(colors))]
    span = lambda b, i: max(c[i] for c in b) - min(c[i] for c in b)
    while len(boxes) < k:
        boxes.sort(key=lambda b: (-max(span(b, i) for i in range(3)), b[0]))
        box = boxes.pop(0)
        if len(box) < 2:
            boxes.append(box)
            break
        ch = max(range(3), key=lambda i: span(box, i))
        box = sorted(box, key=lambda c: (c[ch], c))
        half = len(box) // 2
        boxes += [box[:half], box[half:]]
    return [tuple(sum(c[i] for c in b) // len(b) for i in range(3)) for b in boxes]  # type: ignore[misc]


def build(
    mkt: bytes, stock: dict[int, bytes], stock_palette: list[int]
) -> tuple[dict[int, bytes], list[int]]:
    """``(icon ID -> 784 CI8 bytes, 64 BGR555 colours)`` for Sektor.

    ``stock`` holds the stock icon pixels by ID (for the circle and the kept icons) and
    ``stock_palette`` their 64 colours."""

    mask = [p != 0 for p in stock[POWER_ICONS[MASK_ICON]]]
    rgb = _sektor_icons(_Donor(mkt))
    for name in KEEP_STOCK:
        rgb[name] = [bgr555_to_rgb(stock_palette[i]) for i in stock[POWER_ICONS[name]]]
    colours = [p for name in POWER_NAMES for p, m in zip(rgb[name], mask) if m]
    palette = [(0, 0, 0)] + median_cut(colours, PALETTE_COUNT - 1)
    if len(palette) != PALETTE_COUNT:
        raise ValueError("icon palette reduction produced too few colours")
    cache: dict[RGB, int] = {}

    def nearest(p: RGB) -> int:
        if p not in cache:
            cache[p] = 1 + min(range(PALETTE_COUNT - 1),
                               key=lambda i: (sum((a - b) ** 2 for a, b in zip(p, palette[1 + i])), i))  # fmt: skip
        return cache[p]

    icons = {POWER_ICONS[name]: bytes(nearest(p) if m else 0 for p, m in zip(rgb[name], mask))
             for name in POWER_NAMES}  # fmt: skip
    return icons, [rgb_to_bgr555(c) for c in palette]


# ---- package records ------------------------------------------------------------------------
def records(package: bytes) -> dict[int, tuple[int, int, int]]:
    """ID -> (pixel offset, stride, height) of every record of a decoded image package."""

    out, cursor = {}, 8
    for _ in range(int.from_bytes(package[0:4], "big")):
        flags = int.from_bytes(package[cursor : cursor + 4], "big")
        width_word = int.from_bytes(package[cursor + 4 : cursor + 6], "big")
        height = int.from_bytes(package[cursor + 6 : cursor + 8], "big")
        image_id = int.from_bytes(package[cursor + 8 : cursor + 10], "big")
        stride = (width_word & 0xFF) or 256
        if flags & 0x80000000:
            stride //= 2
        size = stride * height
        out[image_id] = (cursor + 12, stride, height)
        cursor += 12 + size + (size & 1)
    return out


def replace_icons(package: bytes, icons: dict[int, bytes]) -> bytes:
    """A copy of ``package`` with the pixels of the given 28x28 CI8 icon records replaced."""

    out = bytearray(package)
    table = records(package)
    for image_id, pixels in icons.items():
        offset, stride, height = table[image_id]
        if (stride, height) != (N, N) or len(pixels) != PIXELS:
            raise ValueError(f"image 0x{image_id:X} is not a 28x28 CI8 icon")
        out[offset : offset + PIXELS] = pixels
    return bytes(out)


def stock_icons(package: bytes) -> dict[int, bytes]:
    table = records(package)
    return {image_id: package[table[image_id][0] : table[image_id][0] + PIXELS]
            for image_id in POWER_ICONS.values()}  # fmt: skip


def apply(rom: bytearray, mkt: bytes) -> tuple[int, int]:
    """Write Sektor's icons into file 0x5D of ``rom`` (in place in its slot: the inventory HUD's
    owned capacity when production relocated it, else the stock slot) and the shared palette.
    Returns the package's new ROM span."""

    from ..data.addresses import FILE_TABLE_ENTRY_SIZE, FILE_TABLE_ROM
    from ..patches.inventory_hud import (
        COMMON_PACKAGE_CAPACITY,
        COMMON_PACKAGE_ROM,
        _compress_resource_package,
    )
    from ..resource_materialization import decompress_resource_package

    word = lambda off: int.from_bytes(rom[off : off + 4], "big")
    entry = FILE_TABLE_ROM + BANK_FILE * FILE_TABLE_ENTRY_SIZE
    start, end, flag = word(entry), word(entry + 4), word(entry + 8)
    if flag != 1:
        raise ValueError("file 0x5D is not a compressed image package")
    package = decompress_resource_package(bytes(rom[start:end]))
    if word(PALETTE_ROM) != PALETTE_COUNT:
        raise ValueError("unexpected Power Ups icon palette record")
    stock_palette = [int.from_bytes(rom[PALETTE_ROM + 4 + 2 * i : PALETTE_ROM + 6 + 2 * i], "big")
                     for i in range(PALETTE_COUNT)]  # fmt: skip
    icons, palette = build(mkt, stock_icons(package), stock_palette)
    packed = _compress_resource_package(replace_icons(package, icons))
    limit = start + COMMON_PACKAGE_CAPACITY if start == COMMON_PACKAGE_ROM else end
    if start + len(packed) > limit:
        raise ValueError("re-packed file 0x5D does not fit its slot")
    rom[start : start + len(packed)] = packed
    if start == COMMON_PACKAGE_ROM:
        rom[start + len(packed) : end] = b"\xff" * max(0, end - start - len(packed))
    rom[entry + 4 : entry + 8] = (start + len(packed)).to_bytes(4, "big")
    for i, colour in enumerate(palette):
        rom[PALETTE_ROM + 4 + 2 * i : PALETTE_ROM + 6 + 2 * i] = colour.to_bytes(2, "big")
    return start, start + len(packed)
