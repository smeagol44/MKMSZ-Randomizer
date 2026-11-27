"""MKT's shared effects (``create_fx``) read from their routines (SMRE step 3, reusable).

``create_fx(n)`` (``0x8002A820``) starts a process at the routine ``CREATE_FX[n]``
(Static-confirmed table ``0x800A5590``). The routines read here set the animation list in the
process (+0x41C), animate it at a fixed rate (``framew``: a list of image descriptors;
``mframew``: a list of one-part shapes), put it in front of or behind the fighters (object
+0x1C: 0 behind, else in front) and, for some, offset it by a placement entry
(``multi_adjust_xy`` with the table ``0x800A5BB8`` indexed by process +0x444, the caller's
argument: Sektor's ``rocket_smoke(3)``). Sektor's missile (accepted legacy build): fx 4 rocket
puff (``0x800CC7E0``, framew 4, behind, entry 3 = (5, 0) then x - 0x18: 19 px behind) and fx 5
explosion (``0x800CC7F8``, mframew 4, in front).

The image dictionary is not named by the routine: the art takes the donor fighter's dictionary
when every index fits the palette, else the shared one (``0x800CCA88``; Sektor's explosion fits
his own, ROM 0x906A90, as the legacy build found by scoring; the shared one does not).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import decompile as dc
from . import effects

CREATE_FX = 0x800A5590
FRAMEW, MFRAMEW = 0x8000E59C, 0x8000DB98
ADJUST = 0x8000DD3C  # multi_adjust_xy(object, dx, dy): facing-aware
CURRENT_PROC = 0x8014C31C  # the running process (pointer)
ANIMATION_FIELD = 0x41C
PLACE_FIELD = 0x444
OBJECT_Z = 0x1C
SHARED_DICTIONARY = 0x800CCA88
# Free processes / objects an effect leaves before it starts (the host spawner's pool reserve):
# the legacy rocket's, runtime-confirmed (smoke 16, explosion 4; stock spawners check neither).
TRAIL_RESERVE, EFFECT_RESERVE = 16, 4


@dataclass(frozen=True)
class MktEffect:
    fx: int
    routine: int
    animation: int  # the list of descriptors (framew) or one-part shapes (mframew), 0-ended
    ticks_per_frame: int  # donor ticks
    front: bool
    dx: int = 0  # donor px along the source's heading (multi_adjust_xy), after the placement
    dy: int = 0


def _u32(mkt: bytes, va: int) -> int:
    return int.from_bytes(mkt[va - 0x80000000 : va - 0x80000000 + 4], "big")


def _s32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - (1 << 32) if v & 0x80000000 else v


def _walk(stmts: list) -> list:
    out = []
    for x in stmts:
        out.append(x)
        for key in ("then", "other", "body"):
            out += _walk(getattr(x, key, None) or [])
    return out


def _is_proc(e: Any) -> bool:
    return (getattr(e, "kind", None) == "load" or type(e).__name__ == "Load") and isinstance(
        getattr(e, "base", None), dc.Const) and _s32(e.base.v) == _s32(CURRENT_PROC) and e.off == 0  # fmt: skip


def _eval(mkt: bytes, e: Any, place: int | None) -> int:
    """A constant expression of the routine (process +0x444 = ``place``; ROM loads)."""

    name = type(e).__name__
    if name == "Const":
        return _s32(e.v)
    if name == "Load":
        if _is_proc(e.base):
            if e.off != PLACE_FIELD or place is None:
                raise ValueError(f"process field +0x{e.off:X} is not known here")
            return place
        va = _eval(mkt, e.base, place) + e.off
        raw = mkt[(va & 0xFFFFFFFF) - 0x80000000 :][: e.width]
        return int.from_bytes(raw, "big", signed=e.signed)
    if name == "Bin":
        x, y = _eval(mkt, e.a, place), _eval(mkt, e.b, place)
        ops = {"+": lambda: x + y, "-": lambda: x - y, "<<": lambda: x << (y & 31),
               ">>": lambda: x >> (y & 31), "&": lambda: x & y, "|": lambda: x | y}  # fmt: skip
        if e.op not in ops:
            raise ValueError(f"operator {e.op!r} is not read")
        return _s32(ops[e.op]())
    raise ValueError(f"{name} is not a constant")


def read(mkt: bytes, fx: int, place: int | None = None) -> MktEffect:
    """Effect ``fx`` as its routine starts it (``place``: the caller's placement index)."""

    routine = _u32(mkt, CREATE_FX + 4 * fx)
    stmts = _walk(dc.decompile(mkt, routine))
    animation = next((x.value.const() & 0xFFFFFFFF for x in stmts if x.kind == "store"
                      and x.off == ANIMATION_FIELD and x.value.const()), None)  # fmt: skip
    rate = next((x for x in stmts if x.kind == "call" and x.target in (FRAMEW, MFRAMEW)), None)
    if animation is None or rate is None or rate.args[0].const() is None:
        raise ValueError(f"MKT effect {fx} (0x{routine:08X}): no animation list or rate read")
    z = next((x.value.const() for x in stmts if x.kind == "store" and x.off == OBJECT_Z
              and x.width == 2 and x.value.const() is not None), None)  # fmt: skip
    dx = dy = 0
    adjust = next((x for x in stmts if x.kind == "call" and x.target == ADJUST), None)
    if adjust is not None:
        dx, dy = (_eval(mkt, arg, place) for arg in adjust.args[1:3])
    return MktEffect(fx, routine, animation, rate.args[0].const(), z != 0, dx, dy)


def _fits(art: effects.EffectArt) -> bool:
    return all(max(f.indices, default=0) < len(art.palette) for f in art.frames)


def art(mkt: bytes, effect: MktEffect, dictionaries: list[bytes]) -> effects.EffectArt:
    """Its frames as host art, with the first dictionary every index of which fits the palette
    (the donor fighter's, then the shared one)."""

    last: Exception | None = None
    for dictionary in dictionaries:
        try:
            made = effects.mkt_animation_art(mkt, effect.animation, dictionary, compressed=None)
        except ValueError as e:
            last = e
            continue
        if _fits(made):
            return made
    raise ValueError(f"MKT effect {effect.fx}: no dictionary decodes it within its palette") from last
