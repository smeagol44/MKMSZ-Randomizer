"""A fighter's Power Ups help text from its description (milestone 4 step 4, reusable).

The record format, string block and table are documented in ``power_help`` (Sektor's text,
a frozen Sektor-era module), whose writer :func:`power_help.edits` takes any help text. The
description's ``help`` gives, per power slot, ``"stock"`` (the clean ROM's text for that slot),
``"empty"`` (``--``, a removed power) or the groups ``[[title...], [command...],
[description...]]``: uppercase lines of at most 18 characters (``power_help.MAX_LINE``).
"""

from __future__ import annotations

from typing import Any

from ..patches.power_order import POWER_NAMES
from . import power_help

Help = dict[str, tuple[tuple[str, ...], ...]]


def resolve(clean: bytes, recipe: dict[str, Any]) -> Help:
    """The help groups per slot, ``stock`` read from the clean ROM."""

    missing = set(POWER_NAMES) - set(recipe)
    if missing:
        raise power_help.HelpError(f"help: no text for {', '.join(sorted(missing))}")
    stock = dict(zip(POWER_NAMES, power_help.read_help(clean), strict=True))  # clean: identity table
    out: Help = {}
    for name in POWER_NAMES:
        spec = recipe[name]
        if spec == "stock":
            out[name] = stock[name]
        elif spec == "empty":
            out[name] = power_help.EMPTY
        else:
            out[name] = tuple(tuple(group) for group in spec)
    return out


def edits(rom: bytes, clean: bytes, recipe: dict[str, Any]) -> dict[int, bytes]:
    """ROM offset -> bytes putting the fighter's help on the Power Ups screen of ``rom``."""

    return power_help.edits(rom, resolve(clean, recipe))
