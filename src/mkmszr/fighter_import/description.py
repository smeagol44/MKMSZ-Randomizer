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
* ``body.layout`` (optional): explicit layout choices that replace the computed layout,
  used to keep an accepted fighter byte-identical (Sektor). ``slots`` gives, per body slot,
  ``mode`` (``inplace``: the host script's place, ``capacity`` words; ``relocated``: at
  ``place`` inside a ``dead_regions`` span; ``packed``: placed by the frame packer), the
  donor word count ``n`` or explicit ``words``, and ``hybrid`` (non-frame words stay stock).
  ``inherited_groups``/``run_groups`` split the body and Run frames into entropy groups;
  ``frame_edits`` sets host script words (file offset) to donor frames.
* ``legacy``: frozen Sektor-era modules this fighter still uses (plan rule 4).
"""

from __future__ import annotations

import itertools
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
class SlotLayout:
    mode: str
    n: int | None
    words: tuple[int, ...] | None
    place: int | None
    capacity: int | None
    hybrid: bool


@dataclass(frozen=True)
class Layout:
    slots: dict[int, SlotLayout]
    dead_regions: tuple[tuple[int, int], ...]
    inherited_groups: int
    run_groups: int
    run_frames: tuple[int, ...] | None
    frame_edits: dict[int, int]


@dataclass(frozen=True)
class Body:
    slots: tuple[int, ...]
    run_slot: int
    run_rate: int
    colour: Colour
    common_animations: tuple[str, ...]
    layout: Layout | None = None


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

    layout = _layout(body_d.get("layout"), slots, errors) if "layout" in body_d else None
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
        body=Body(tuple(slots), run_slot, run_rate, Colour(depth, method, index_map, palette), tuple(anims), layout),
        legacy=tuple(legacy),
    )  # fmt: skip


def _layout(raw: Any, slots: list[int], errors: list[str]) -> Layout | None:
    if not isinstance(raw, dict):
        errors.append("body.layout: expected an object")
        return None
    where = "body.layout"
    regions = []
    for k, pair in enumerate(raw.get("dead_regions", [])):
        lo = _int(pair[0] if isinstance(pair, list) and len(pair) == 2 else None, f"{where}.dead_regions[{k}]", errors)
        hi = _int(pair[1] if isinstance(pair, list) and len(pair) == 2 else None, f"{where}.dead_regions[{k}]", errors)
        if lo is not None and hi is not None:
            if not lo < hi:
                errors.append(f"{where}.dead_regions[{k}]: start must be below end")
            regions.append((lo, hi))
    slot_layouts: dict[int, SlotLayout] = {}
    raw_slots = raw.get("slots", {})
    if not isinstance(raw_slots, dict):
        errors.append(f"{where}.slots: expected an object")
        raw_slots = {}
    for key, entry in raw_slots.items():
        slot = _int(key, f"{where}.slots key {key!r}", errors)
        w = f"{where}.slots[{key}]"
        if slot is None or not isinstance(entry, dict):
            errors.append(f"{w}: expected an object keyed by a body slot")
            continue
        if slot not in slots:
            errors.append(f"{w}: not in body.slots")
        mode = entry.get("mode")
        if mode not in ("inplace", "relocated", "packed"):
            errors.append(f"{w}.mode: inplace, relocated or packed")
        words = entry.get("words")
        if words is not None:
            words = tuple(v for v in (_int(x, f"{w}.words", errors) for x in words) if v is not None)
        n = _int(entry["n"], f"{w}.n", errors) if "n" in entry else None
        if (n is None) == (words is None):
            errors.append(f"{w}: exactly one of n or words")
        place = _int(entry["place"], f"{w}.place", errors) if "place" in entry else None
        capacity = _int(entry["capacity"], f"{w}.capacity", errors) if "capacity" in entry else None
        length = len(words) if words is not None else (n or 0)
        if mode == "inplace" and (capacity is None or capacity < length):
            errors.append(f"{w}.capacity: required for inplace and at least the script length")
        if mode == "relocated":
            if place is None:
                errors.append(f"{w}.place: required for relocated")
            elif not any(lo <= place and place + 4 * length <= hi for lo, hi in regions):
                errors.append(f"{w}.place: the script must lie inside one dead region")
        slot_layouts[slot] = SlotLayout(mode, n, words, place, capacity, bool(entry.get("hybrid", False)))
    missing = [s for s in slots if s not in slot_layouts]
    if missing:
        errors.append(f"{where}.slots: missing {', '.join(f'0x{s:02X}' for s in missing)}")
    placed = sorted((sl.place, sl.place + 4 * (len(sl.words) if sl.words else sl.n or 0))
                    for sl in slot_layouts.values() if sl.mode == "relocated" and sl.place is not None)  # fmt: skip
    if any(a[1] > b[0] for a, b in itertools.pairwise(placed)):
        errors.append(f"{where}.slots: relocated scripts overlap")
    groups = {k: _int(raw.get(k), f"{where}.{k}", errors) for k in ("inherited_groups", "run_groups")}
    run_frames = raw.get("run_frames")
    if run_frames is not None:
        run_frames = tuple(v for v in (_int(x, f"{where}.run_frames", errors) for x in run_frames) if v is not None)
    edits = {}
    for pos, rel in (raw.get("frame_edits") or {}).items():
        a, b = _int(pos, f"{where}.frame_edits", errors), _int(rel, f"{where}.frame_edits", errors)
        if a is not None and b is not None:
            edits[a] = b
    return Layout(slot_layouts, tuple(regions), groups["inherited_groups"] or 0, groups["run_groups"] or 0,
                  run_frames, edits)  # fmt: skip


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
