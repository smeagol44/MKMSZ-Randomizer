"""A fighter's Power Ups icons from its description (milestone 4, reusable).

The native icons, their palette and file ``0x5D`` are documented in ``power_icons`` (Sektor's
hand-composed set, a frozen Sektor-era module whose canvas, colour reduction and package helpers
this module reuses). Here each power slot's icon comes from the fighter description's ``icons``
recipe instead of code:

* ``"stock"``: the stock icon; ``"empty"``: the dark disc with a dash (a removed power);
* ``{"layers": [...], "crop": [x0, y0, size]}``: donor frames drawn on a radial background at one
  origin (MKT's fighter origin, the top of the head; frames are placed ``left = -anchor_x``,
  ``top = -anchor_y``), so a projectile's art lands at the mouth or hands as in MKT; then the
  square ``crop`` (donor pixels from that origin) is box-averaged to 28x28 and clipped to the
  stock circle.

A layer is ``{"anim": {"table", "slot", "phase" | "part", "frame"}}`` (``phase``: the body
script's phases, tokens dropped; ``part``: an MKT animation part, as the projectile art), or
``{"fx": {"animation", "dictionary", "frame"}}`` (a shared MKT effect, ``effects.
mkt_animation_art``), with optional ``palette`` (MKT VA; default the recipe's), ``dx``/``dy``,
``shade`` (0..1) and ``ghosts`` ``{"count", "dx"}`` (fading copies behind it, as motion).
All nine icons are reduced together to 63 colours (index 0 transparent), the shared palette.
"""

from __future__ import annotations

from typing import Any

from ..patches.power_order import POWER_ICONS, POWER_NAMES
from . import body_build, effects
from . import lower_projectile as lp
from .mkt_fighter import MktRom
from .power_icons import (
    BANK_FILE,
    MASK_ICON,
    PALETTE_COUNT,
    PALETTE_ROM,
    RGB,
    _Canvas,
    bgr555_to_rgb,
    median_cut,
    replace_icons,
    rgb_to_bgr555,
    stock_icons,
)
from .power_icons import N as ICON

DEFAULT_BACKGROUND = ("0xA0D2A0", "0x101E14")  # radial: inner glow -> dark edge


class IconError(ValueError):
    pass


def _int(v: Any) -> int:
    return int(v, 0) if isinstance(v, str) else int(v)


def _rgb(text: str) -> RGB:
    v = int(text, 16)
    return ((v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF)


class _Donor:
    def __init__(self, mkt: bytes, fighter: int) -> None:
        self.mkt = mkt
        self.body = body_build.Donor(mkt, fighter)
        self.table1 = MktRom(mkt).table1(fighter)
        self.starts = set(self.body.table0) | set(self.table1)

    def palette(self, va: int) -> list[RGB]:
        return [bgr555_to_rgb(c) for c in effects.mkt_palette(self.mkt, va)]

    def frame(self, anim: dict[str, Any]) -> effects.EffectFrame:
        table, slot, k = _int(anim["table"]), _int(anim["slot"]), _int(anim.get("frame", 0))
        if "part" in anim:
            frames = lp.donor_part(self.body, {"table": table, "slot": slot, "part": _int(anim["part"])}).frames
        else:
            root = (self.body.table0 if table == 0 else self.table1)[slot]
            phases = body_build.donor_frames_by_phase(self.body, root, self.starts)
            frames = phases[_int(anim.get("phase", 1)) - 1]
        return lp._frame(self.body, frames[k], 0)


def _layer_frame(d: _Donor, layer: dict[str, Any]) -> tuple[effects.EffectFrame, list[RGB] | None]:
    if "fx" in layer:
        fx = layer["fx"]
        art = effects.mkt_animation_art(d.mkt, _int(fx["animation"]), _int(fx["dictionary"]))
        frame = art.frames[_int(fx.get("frame", 0))]
        return frame, [bgr555_to_rgb(c) for c in art.palette]
    return d.frame(layer["anim"]), None


def _radial(size: int, inner: RGB, outer: RGB):
    c = size / 2

    def f(x: int, y: int) -> RGB:
        t = min(1.0, (((x - c) ** 2 + (y - c) ** 2) ** 0.5) / c)
        return tuple(int(inner[i] + (outer[i] - inner[i]) * t) for i in range(3))  # type: ignore[return-value]

    return f


def compose(d: _Donor, spec: dict[str, Any], palette: list[RGB], background: tuple[RGB, RGB]) -> list[RGB]:
    """One icon (28 x 28 RGB) from a layers-and-crop recipe."""

    x0, y0, size = (_int(v) for v in spec["crop"])
    if size < ICON:
        raise IconError("crop is smaller than the icon")
    canvas = _Canvas(size, size, _radial(size, *background))
    for layer in spec["layers"]:
        frame, own = _layer_frame(d, layer)
        pal = d.palette(_int(layer["palette"])) if "palette" in layer else (own or palette)
        left = _int(layer.get("dx", 0)) - frame.anchor_x - x0
        top = _int(layer.get("dy", 0)) - frame.anchor_y - y0
        ghosts = layer.get("ghosts")
        if ghosts:
            count, step = _int(ghosts["count"]), _int(ghosts["dx"])
            for g in range(count, 0, -1):
                canvas.put(frame, pal, left + step * g, top, shade=0.3 + 0.5 * (count - g) / count)
        canvas.put(frame, pal, left, top, shade=float(layer.get("shade", 1.0)))
    return canvas.icon(0, 0, size)


def build(mkt: bytes, fighter: int, recipe: dict[str, Any], stock: dict[int, bytes],
          stock_palette: list[int]) -> tuple[dict[int, bytes], list[int]]:  # fmt: skip
    """``(icon ID -> 784 CI8 bytes, 64 BGR555 colours)`` for the nine power slots."""

    missing = set(POWER_NAMES) - set(recipe["slots"])
    if missing:
        raise IconError(f"icons: no recipe for {', '.join(sorted(missing))}")
    d = _Donor(mkt, fighter)
    palette = d.palette(_int(recipe["palette"]))
    background = tuple(_rgb(c) for c in recipe.get("background", DEFAULT_BACKGROUND))
    mask = [p != 0 for p in stock[POWER_ICONS[MASK_ICON]]]
    rgb: dict[str, list[RGB]] = {}
    for name in POWER_NAMES:
        spec = recipe["slots"][name]
        if spec == "stock":
            rgb[name] = [bgr555_to_rgb(stock_palette[i]) for i in stock[POWER_ICONS[name]]]
        elif spec == "empty":
            rgb[name] = [(170, 176, 186) if 9 <= x <= 18 and 13 <= y <= 14 else (30, 34, 48)
                         for y in range(ICON) for x in range(ICON)]  # fmt: skip
        else:
            rgb[name] = compose(d, spec, palette, background)  # type: ignore[arg-type]
    colours = [p for name in POWER_NAMES for p, m in zip(rgb[name], mask, strict=True) if m]
    shared = [(0, 0, 0)] + median_cut(colours, PALETTE_COUNT - 1)
    if len(shared) != PALETTE_COUNT:
        raise IconError("icon palette reduction produced too few colours")
    cache: dict[RGB, int] = {}

    def nearest(p: RGB) -> int:
        if p not in cache:
            cache[p] = 1 + min(range(PALETTE_COUNT - 1),
                               key=lambda i: (sum((a - b) ** 2 for a, b in zip(p, shared[1 + i], strict=True)), i))  # fmt: skip
        return cache[p]

    icons = {POWER_ICONS[name]: bytes(nearest(p) if m else 0 for p, m in zip(rgb[name], mask, strict=True))
             for name in POWER_NAMES}  # fmt: skip
    return icons, [rgb_to_bgr555(c) for c in shared]


def apply(rom: bytearray, mkt: bytes, fighter: int, recipe: dict[str, Any]) -> tuple[int, int]:
    """Write the icons into file 0x5D of ``rom`` and the shared palette, as ``power_icons.apply``
    does for Sektor (in place in the package's slot: the inventory HUD's owned capacity when
    production relocated it, else the stock slot). Returns the package's new ROM span."""

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
        raise IconError("file 0x5D is not a compressed image package")
    package = decompress_resource_package(bytes(rom[start:end]))
    if word(PALETTE_ROM) != PALETTE_COUNT:
        raise IconError("unexpected Power Ups icon palette record")
    stock_palette = [int.from_bytes(rom[PALETTE_ROM + 4 + 2 * i : PALETTE_ROM + 6 + 2 * i], "big")
                     for i in range(PALETTE_COUNT)]  # fmt: skip
    icons, palette = build(mkt, fighter, recipe, stock_icons(package), stock_palette)
    packed = _compress_resource_package(replace_icons(package, icons))
    limit = start + COMMON_PACKAGE_CAPACITY if start == COMMON_PACKAGE_ROM else end
    if start + len(packed) > limit:
        raise IconError(f"re-packed file 0x5D (0x{len(packed):X}) does not fit its slot (0x{limit - start:X})")
    rom[start : start + len(packed)] = packed
    if start == COMMON_PACKAGE_ROM:
        rom[start + len(packed) : end] = b"\xff" * max(0, end - start - len(packed))
    rom[entry + 4 : entry + 8] = (start + len(packed)).to_bytes(4, "big")
    for i, colour in enumerate(palette):
        rom[PALETTE_ROM + 4 + 2 * i : PALETTE_ROM + 6 + 2 * i] = colour.to_bytes(2, "big")
    return start, start + len(packed)
