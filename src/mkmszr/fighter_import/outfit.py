"""The outfit colour option on Sektor's palette (R4 presentation, user decision).

Production's outfit option recolours Sub-Zero's clothing entries ``0x21..0x3F`` of the stock
file-0x87 palette (``patches.palette``). Sektor's body uses the first 16 entries of his own
palette (file ``+0x4584C``): greys and the red armour. This applies the same option to the red
entries. Hue, preset, seeded and RGB modes set an absolute hue, so they work from red as from
blue. ``red`` is Sektor's own colour (no change), and ``green`` swaps red and green the way
Sub-Zero's swaps blue and green.
"""

from __future__ import annotations

from ..patches import palette as pal

PALETTE_OFFSET = 0x4584C  # file 0x87
RED_ENTRIES = (0x3, 0x5, 0x7, 0x9, 0xB, 0xD, 0xE)  # saturated reds; 1 is near-black


def _swap_red_green(word: int) -> int:
    red, green, blue, high = pal.decode_bgr555(word)
    return pal.encode_bgr555(green, red, blue, high)


def transform(word: int, mode: str, *, hue: float | None = None,
              rgb: tuple[int, int, int] | None = None, seed: str | None = None) -> int:  # fmt: skip
    mode = mode.lower()
    if mode in ("vanilla", "red"):
        return word
    if mode == "green":
        return _swap_red_green(word)
    if mode in pal.PRESET_HUES:
        return pal.make_hue(word, pal.PRESET_HUES[mode])
    if mode == "hue" and hue is not None:
        return pal.make_hue(word, hue)
    if mode == "rgb" and rgb is not None:
        return pal.make_rgb_tint(word, rgb)
    if mode == "seeded" and seed is not None:
        return pal.make_hue(word, pal.seeded_hue(seed))
    raise ValueError(f"unsupported outfit mode for Sektor: {mode}")


def recolor(file87: bytes | bytearray, mode: str, **kwargs) -> bytearray:
    """A copy of Sektor's fighter file with the outfit applied to his red entries."""

    out = bytearray(file87)
    for index in RED_ENTRIES:
        off = PALETTE_OFFSET + 2 * index
        word = int.from_bytes(out[off : off + 2], "big")
        out[off : off + 2] = transform(word, mode, **kwargs).to_bytes(2, "big")
    return out
