"""The outfit colour option on an imported fighter's palette (R4 presentation, user decision).

Production's outfit option recolours Sub-Zero's clothing entries ``0x21..0x3F`` of the stock
file-0x87 palette (``patches.palette``). An imported fighter's body uses the first 16 entries of
his own palette (file ``+0x4584C``); the option recolours his outfit entries there. Hue, preset,
seeded and RGB modes set an absolute hue, so they work from any colour. His own colour (``own``)
is no change, and the other of red and green swaps those two channels, the way Sub-Zero's
``green`` swaps blue and green.

* Sektor (user decision, R4b): greys and red armour; ``RED_ENTRIES``, own colour red.
* Reptile (owner, 2026-11-13): greens 10..14 (15 is near-black), own colour green, from his
  fighter description's ``outfit`` section.
"""

from __future__ import annotations

from ..patches import palette as pal

PALETTE_OFFSET = 0x4584C  # file 0x87
RED_ENTRIES = (0x3, 0x5, 0x7, 0x9, 0xB, 0xD, 0xE)  # saturated reds; 1 is near-black


def _swap_red_green(word: int) -> int:
    red, green, blue, high = pal.decode_bgr555(word)
    return pal.encode_bgr555(green, red, blue, high)


def transform(word: int, mode: str, *, hue: float | None = None,
              rgb: tuple[int, int, int] | None = None, seed: str | None = None,
              own: str = "red") -> int:  # fmt: skip
    mode = mode.lower()
    if mode in ("vanilla", own):
        return word
    if mode in ("red", "green"):
        return _swap_red_green(word)
    if mode in pal.PRESET_HUES:
        return pal.make_hue(word, pal.PRESET_HUES[mode])
    if mode == "hue" and hue is not None:
        return pal.make_hue(word, hue)
    if mode == "rgb" and rgb is not None:
        return pal.make_rgb_tint(word, rgb)
    if mode == "seeded" and seed is not None:
        return pal.make_hue(word, pal.seeded_hue(seed))
    raise ValueError(f"unsupported outfit mode: {mode}")


def recolor(file87: bytes | bytearray, mode: str, *, entries: tuple[int, ...] = RED_ENTRIES,
            **kwargs) -> bytearray:  # fmt: skip
    """A copy of the fighter file with the outfit applied to ``entries`` of his body palette
    (default: Sektor's red entries)."""

    out = bytearray(file87)
    for index in entries:
        off = PALETTE_OFFSET + 2 * index
        word = int.from_bytes(out[off : off + 2], "big")
        out[off : off + 2] = transform(word, mode, **kwargs).to_bytes(2, "big")
    return out
