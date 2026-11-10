"""Fighter descriptions: one data file per imported fighter (Fighter recompiler plan).

A description is JSON in ``src/mkmszr/fighters/<id>.json``: data only, no code. Format 1
covers the body (milestone 1); later milestones add moves, presentation and progression
as new keys. Integers that are offsets or slot numbers may be written as hex strings
(``"0x4A"``). :func:`load` parses and validates; :func:`validate` raises
:class:`DescriptionError` listing every problem found.

Body fields:

* ``donor``: ``fighter_id`` (MKT table index, 0..31) and ``name`` (the MKT name-table entry,
  checked against the donor ROM by :func:`check_donor`).
* ``body.slots``: host primary slots imported by the generic rule "host slot *i* takes MKT
  table 0 index *i*" (Wiki ``Fighter-Recompiler-Inventory``).
* ``body.run``: the MKT slot with the Run poses (``0x4A`` for every MKT fighter) and the host
  Run rate.
* ``body.colour``: colour depth and method. ``explicit`` gives the 32→16 index map and the
  32-entry palette (BGR555 words, hex); ``auto`` derives them from the donor palette (the
  reduction is milestone 1 work).
* ``body.common_animations``: the generic recipes in ``common_moves`` to apply.
* ``legacy``: frozen Sektor-era modules this fighter still uses (plan rule 4).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Any

FORMAT = 1
COMMON_ANIMATIONS = ("slide", "death", "long_fall", "pickup", "grabbed")
LEGACY_MODULES = (
    "sektor-teleport",
    "sektor-rockets",
    "sektor-throw-arm",
    "sektor-combos",
    "sektor-tiers",
    "sektor-presentation",
)
HOST_PRIMARY_SLOTS = range(0x41)
MKT_SLOTS = range(0x5A)  # MKT table 0 (90 entries)
DONOR_GAMES = ("MKT-N64-USA-Rev2",)


class DescriptionError(ValueError):
    pass


@dataclass(frozen=True)
class Colour:
    depth: int
    method: str
    index_map: tuple[int, ...] | None
    palette: bytes | None


@dataclass(frozen=True)
class Body:
    slots: tuple[int, ...]
    run_slot: int
    run_rate: int
    colour: Colour
    common_animations: tuple[str, ...]


@dataclass(frozen=True)
class FighterDescription:
    id: str
    display_name: str
    title: str
    donor_fighter_id: int
    donor_name: str
    body: Body
    legacy: tuple[str, ...]


def _int(value: Any, where: str, errors: list[str]) -> int | None:
    if isinstance(value, bool):
        errors.append(f"{where}: expected an integer")
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value, 0)
        except ValueError:
            pass
    errors.append(f"{where}: expected an integer or hex string, got {value!r}")
    return None


def _get(d: dict, key: str, kind: type, where: str, errors: list[str]) -> Any:
    if not isinstance(d, dict) or key not in d:
        errors.append(f"{where}.{key}: missing")
        return None
    value = d[key]
    if not isinstance(value, kind):
        errors.append(f"{where}.{key}: expected {kind.__name__}")
        return None
    return value


def validate(data: Any) -> FighterDescription:
    """Check ``data`` (a parsed description) and return it typed; raise listing all errors."""

    errors: list[str] = []
    if not isinstance(data, dict):
        raise DescriptionError("description must be a JSON object")
    if data.get("format") != FORMAT:
        errors.append(f"format: expected {FORMAT}")
    fid = _get(data, "id", str, "", errors)
    if fid is not None and not (fid.isascii() and fid.replace("-", "").isalnum() and fid == fid.lower()):
        errors.append("id: lowercase letters, digits and '-' only")
    display = _get(data, "display_name", str, "", errors)
    title = _get(data, "title", str, "", errors)
    if title is not None and not (0 < len(title) <= 12 and title == title.upper()):
        errors.append("title: 1..12 uppercase characters")
    donor = _get(data, "donor", dict, "", errors) or {}
    if donor.get("game") not in DONOR_GAMES:
        errors.append(f"donor.game: one of {DONOR_GAMES}")
    donor_id = _int(donor.get("fighter_id"), "donor.fighter_id", errors)
    if donor_id is not None and not 0 <= donor_id < 32:
        errors.append("donor.fighter_id: 0..31")
    donor_name = _get(donor, "name", str, "donor", errors)

    body_d = _get(data, "body", dict, "", errors) or {}
    slots: list[int] = []
    for k, s in enumerate(_get(body_d, "slots", list, "body", errors) or []):
        v = _int(s, f"body.slots[{k}]", errors)
        if v is None:
            continue
        if v not in HOST_PRIMARY_SLOTS:
            errors.append(f"body.slots[{k}]: host primary slot 0x00..0x40")
        if v in slots:
            errors.append(f"body.slots[{k}]: duplicate 0x{v:02X}")
        slots.append(v)
    run_d = _get(body_d, "run", dict, "body", errors) or {}
    run_slot = _int(run_d.get("mkt_slot"), "body.run.mkt_slot", errors)
    if run_slot is not None and run_slot not in MKT_SLOTS:
        errors.append("body.run.mkt_slot: MKT table 0 slot 0x00..0x59")
    run_rate = _int(run_d.get("host_rate"), "body.run.host_rate", errors)
    if run_rate is not None and not 1 <= run_rate <= 8:
        errors.append("body.run.host_rate: 1..8")

    colour_d = _get(body_d, "colour", dict, "body", errors) or {}
    depth = _int(colour_d.get("depth"), "body.colour.depth", errors)
    index_map = palette = None
    method = colour_d.get("method")
    if depth not in (16, 32, None):
        errors.append("body.colour.depth: 16 or 32")
    if method not in ("explicit", "auto"):
        errors.append("body.colour.method: explicit or auto")
    if method == "explicit" and depth == 16:
        raw_map = colour_d.get("index_map_32_to_16")
        if not (isinstance(raw_map, list) and len(raw_map) == 32 and all(isinstance(x, int) and 0 <= x < 16 for x in raw_map)):
            errors.append("body.colour.index_map_32_to_16: 32 integers 0..15")
        elif raw_map[0] != 0:
            errors.append("body.colour.index_map_32_to_16: index 0 (transparent) must map to 0")
        else:
            index_map = tuple(raw_map)
        raw_pal = colour_d.get("palette_bgr555")
        try:
            palette = bytes.fromhex(raw_pal) if isinstance(raw_pal, str) else None
        except ValueError:
            palette = None
        if palette is None or len(palette) != 64:
            errors.append("body.colour.palette_bgr555: 32 BGR555 words as 128 hex digits")
            palette = None

    anims = _get(body_d, "common_animations", list, "body", errors) or []
    for a in anims:
        if a not in COMMON_ANIMATIONS:
            errors.append(f"body.common_animations: unknown {a!r} (known: {', '.join(COMMON_ANIMATIONS)})")
    legacy = data.get("legacy", [])
    if not isinstance(legacy, list) or any(x not in LEGACY_MODULES for x in legacy):
        errors.append(f"legacy: a list of {', '.join(LEGACY_MODULES)}")
        legacy = []
    unknown = set(data) - {"format", "id", "display_name", "title", "donor", "body", "legacy", "notes"}
    if unknown:
        errors.append(f"unknown keys: {', '.join(sorted(unknown))}")
    if errors:
        raise DescriptionError("; ".join(errors))
    return FighterDescription(
        id=fid, display_name=display, title=title, donor_fighter_id=donor_id, donor_name=donor_name,
        body=Body(tuple(slots), run_slot, run_rate, Colour(depth, method, index_map, palette), tuple(anims)),
        legacy=tuple(legacy),
    )  # fmt: skip


def load(fighter_id: str) -> FighterDescription:
    """The packaged description ``mkmszr/fighters/<fighter_id>.json``."""

    text = resources.files("mkmszr.fighters").joinpath(f"{fighter_id}.json").read_text(encoding="utf-8")
    description = validate(json.loads(text))
    if description.id != fighter_id:
        raise DescriptionError(f"{fighter_id}.json declares id {description.id!r}")
    return description


def available() -> list[str]:
    """Ids of every packaged description."""

    root = resources.files("mkmszr.fighters")
    return sorted(p.name[:-5] for p in root.iterdir() if p.name.endswith(".json"))


def check_donor(description: FighterDescription, mkt: bytes) -> None:
    """The donor name-table entry for the declared fighter id must be the declared name."""

    from .mkt_fighter import MktRom

    name = MktRom(mkt).name(description.donor_fighter_id)
    if name != description.donor_name:
        raise DescriptionError(
            f"donor fighter {description.donor_fighter_id} is {name!r}, not {description.donor_name!r}"
        )
