"""Sub-Zero clothing palette transformations."""

from __future__ import annotations

import colorsys
import hashlib

from ..data.addresses import (
    SUBZERO_CLOTHING_FIRST,
    SUBZERO_CLOTHING_LAST,
    SUBZERO_PALETTE_COLORS_ROM,
)
from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext

PRESET_HUES = {
    "purple": 285.0,
    "orange": 30.0,
    "yellow": 55.0,
    "cyan": 185.0,
    "pink": 330.0,
}


def decode_bgr555(word: int) -> tuple[int, int, int, int]:
    return word & 0x1F, (word >> 5) & 0x1F, (word >> 10) & 0x1F, word & 0x8000


def encode_bgr555(red: int, green: int, blue: int, high_bit: int) -> int:
    if not all(0 <= value <= 31 for value in (red, green, blue)):
        raise ValueError("BGR555 channels must be in the range 0..31")
    return (high_bit & 0x8000) | (blue << 10) | (green << 5) | red


def make_red(word: int) -> int:
    red, green, blue, high = decode_bgr555(word)
    return encode_bgr555(blue, green, red, high)


def make_green(word: int) -> int:
    red, green, blue, high = decode_bgr555(word)
    return encode_bgr555(red, blue, green, high)


def _target_hue(word: int, hue_degrees: float, saturation_scale: float = 1.0) -> int:
    red, green, blue, high = decode_bgr555(word)
    source_rgb = (red / 31.0, green / 31.0, blue / 31.0)
    _source_hue, saturation, value = colorsys.rgb_to_hsv(*source_rgb)
    saturation = max(0.0, min(1.0, saturation * saturation_scale))
    out = colorsys.hsv_to_rgb((hue_degrees % 360.0) / 360.0, saturation, value)
    channels = tuple(max(0, min(31, round(channel * 31.0))) for channel in out)
    return encode_bgr555(channels[0], channels[1], channels[2], high)


def make_hue(word: int, hue_degrees: float) -> int:
    return _target_hue(word, hue_degrees)


def make_rgb_tint(word: int, rgb: tuple[int, int, int]) -> int:
    if not all(0 <= value <= 255 for value in rgb):
        raise ValueError("RGB channels must be in the range 0..255")
    target = tuple(value / 255.0 for value in rgb)
    hue, saturation, _value = colorsys.rgb_to_hsv(*target)
    return _target_hue(word, hue * 360.0, saturation_scale=saturation)


def seeded_hue(seed: str) -> float:
    digest = hashlib.sha256(f"mkmszr:subzero-outfit:{seed}".encode()).digest()
    value = int.from_bytes(digest[:8], "big")
    return (value / 2**64) * 360.0


class SubZeroPalettePatch:
    name = "subzero-palette"

    def __init__(
        self,
        mode: str,
        *,
        hue_degrees: float | None = None,
        rgb: tuple[int, int, int] | None = None,
    ):
        self.mode = mode.lower()
        self.hue_degrees = hue_degrees
        self.rgb = rgb

    def _transform(self, word: int, context: PatchContext) -> int:
        if self.mode == "red":
            return make_red(word)
        if self.mode == "green":
            return make_green(word)
        if self.mode in PRESET_HUES:
            return make_hue(word, PRESET_HUES[self.mode])
        if self.mode == "hue":
            if self.hue_degrees is None:
                raise PatchError("hue palette mode requires hue_degrees")
            return make_hue(word, self.hue_degrees)
        if self.mode == "rgb":
            if self.rgb is None:
                raise PatchError("rgb palette mode requires an RGB tuple")
            return make_rgb_tint(word, self.rgb)
        if self.mode == "seeded":
            if context.seed is None:
                raise PatchError("seeded palette mode requires a seed")
            return make_hue(word, seeded_hue(context.seed))
        raise PatchError(f"unsupported Sub-Zero palette mode: {self.mode}")

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        for index in range(SUBZERO_CLOTHING_FIRST, SUBZERO_CLOTHING_LAST + 1):
            offset = SUBZERO_PALETTE_COLORS_ROM + index * 2
            original = rom.read_u16(offset)
            rom.write_u16(offset, self._transform(original, context))

        detail = self.mode
        if self.mode == "seeded" and context.seed is not None:
            detail += f" hue={seeded_hue(context.seed):.2f}°"
        elif self.mode == "hue" and self.hue_degrees is not None:
            detail += f" hue={self.hue_degrees % 360.0:.2f}°"
        elif self.mode == "rgb" and self.rgb is not None:
            detail += f" rgb=#{self.rgb[0]:02X}{self.rgb[1]:02X}{self.rgb[2]:02X}"

        note = (
            f"Sub-Zero clothing entries 0x{SUBZERO_CLOTHING_FIRST:02X}.."
            f"0x{SUBZERO_CLOTHING_LAST:02X}: {detail}"
        )
        return (note,)
