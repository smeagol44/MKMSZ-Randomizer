"""Deterministic optional shuffle of Sub-Zero's native Power Up order.

The native XP thresholds stay unchanged.  This patch remaps the tier gate for
each Power Up and keeps both native Power Ups presentation tables in the exact
same generated order.

The only ordering dependency is semantic: Ice Shatter must come after at least
one freezing Power Up (Ice Blast, Directional Ice, or Air Ice Blast).  Slide
and Super Slide are deliberately independent.
"""

from __future__ import annotations

import hashlib

from ..errors import PatchError
from ..mips import REGISTERS, addiu, jr, lw, ori, sll, subu, words_blob
from ..rom import RomImage
from .base import PatchContext

RNG_DOMAIN = b"MKMSZR:POWER-ORDER:V1\\0"
MAX_POWER_ORDER_ATTEMPTS = 1000

POWER_NAMES = (
    "ice-blast",
    "slide",
    "directional-ice",
    "air-ice-blast",
    "ice-clone",
    "ice-shatter",
    "super-slide",
    "freeze-on-contact",
    "polar-blast",
)
VANILLA_POWER_ORDER = POWER_NAMES
FREEZING_POWERS = ("ice-blast", "directional-ice", "air-ice-blast")

POWER_DISPLAY_NAMES = {
    "ice-blast": "Ice Blast",
    "slide": "Slide",
    "directional-ice": "Directional Ice",
    "air-ice-blast": "Air Ice Blast",
    "ice-clone": "Ice Clone",
    "ice-shatter": "Ice Shatter",
    "super-slide": "Super Slide",
    "freeze-on-contact": "Freeze on Contact",
    "polar-blast": "Polar Blast",
}

# Every simple gate is the immediate of the stock `slti v0,v0,N`.
# Directional Ice owns both angle recognizers; Ice Shatter owns two contextual
# gate sites.
SIMPLE_TIER_SITES: dict[str, tuple[int, int]] = {
    "slide": (0x0003D62C, 2),
    "directional-ice-up": (0x0004B084, 3),
    "directional-ice-down": (0x0004B0F4, 3),
    "air-ice-blast": (0x0004AFBC, 4),
    "ice-clone": (0x0004AEA8, 5),
    "ice-shatter-a": (0x000515A0, 6),
    "ice-shatter-b": (0x000535C4, 6),
    "super-slide": (0x0003D728, 7),
    "freeze-on-contact": (0x0005B5DC, 8),
    "polar-blast": (0x0004B2B4, 9),
}

# Ground Ice Blast's stock tier-1 condition is expressed as bgtz rather than
# the simple slti form.  The Runtime-confirmed v02/v04 proof replaces this
# exact seven-word tail in place with an arbitrary assigned threshold.
ICE_GROUND_TAIL_ROM = 0x0004B018
ICE_GROUND_TAIL_EXPECTED = bytes.fromhex(
    "1C400002 34028000 24024000 8FBF0010 27BD0018 03E00008 00000000"
)

# Native Power Ups presentation tables, in stock semantic order.
POWER_ICON_TABLE_ROM = 0x000A6BB0
POWER_HELP_TABLE_ROM = 0x000A78A0

POWER_ICONS = {
    "ice-blast": 0x000003CB,
    "slide": 0x000003C8,
    "directional-ice": 0x000003CC,
    "air-ice-blast": 0x000003CD,
    "ice-clone": 0x000003CF,
    "ice-shatter": 0x000003D1,
    "super-slide": 0x000003C9,
    "freeze-on-contact": 0x000003CE,
    "polar-blast": 0x000003CA,
}

POWER_HELP = {
    "ice-blast": 0x800A6B30,
    "slide": 0x800A6B54,
    "directional-ice": 0x800A6B7C,
    "air-ice-blast": 0x800A6BA8,
    "ice-clone": 0x800A6BEC,
    "ice-shatter": 0x800A6BD0,
    "super-slide": 0x800A6C10,
    "freeze-on-contact": 0x800A6C40,
    "polar-blast": 0x800A6C74,
}


def _slti(rt: str, rs: str, imm: int) -> int:
    return (
        (0x0A << 26)
        | (REGISTERS[rs] << 21)
        | (REGISTERS[rt] << 16)
        | (imm & 0xFFFF)
    )


def power_order_is_valid(order: tuple[str, ...]) -> bool:
    if len(order) != len(POWER_NAMES) or set(order) != set(POWER_NAMES):
        return False
    positions = {name: index for index, name in enumerate(order)}
    return positions["ice-shatter"] > min(positions[name] for name in FREEZING_POWERS)


def _candidate_power_order(seed: str, attempt: int) -> tuple[str, ...]:
    values = list(POWER_NAMES)
    seed_bytes = seed.encode("utf-8")

    for counter, index in enumerate(range(len(values) - 1, 0, -1)):
        digest = hashlib.sha256(
            RNG_DOMAIN
            + seed_bytes
            + b"\\0"
            + attempt.to_bytes(4, "big")
            + counter.to_bytes(4, "big")
        ).digest()
        swap_index = int.from_bytes(digest[:8], "big") % (index + 1)
        values[index], values[swap_index] = values[swap_index], values[index]

    return tuple(values)


def build_power_order(seed: str) -> tuple[tuple[str, ...], int]:
    """Return the first deterministic order satisfying the accepted dependency."""

    for attempt in range(MAX_POWER_ORDER_ATTEMPTS):
        order = _candidate_power_order(seed, attempt)
        if power_order_is_valid(order):
            return order, attempt + 1

    raise PatchError(
        "no valid Power Up order after "
        f"{MAX_POWER_ORDER_ATTEMPTS} deterministic attempts"
    )


def assigned_power_tiers(order: tuple[str, ...]) -> dict[str, int]:
    if not power_order_is_valid(order):
        raise ValueError("invalid Power Up order")
    return {name: index + 1 for index, name in enumerate(order)}


def build_ice_ground_tail(threshold: int) -> bytes:
    """Build the Runtime-confirmed arbitrary-tier ground-Ice condition tail."""

    return words_blob(
        [
            _slti("t0", "v0", threshold),
            sll("t0", "t0", 14),
            ori("v0", "zero", 0x8000),
            subu("v0", "v0", "t0"),
            lw("ra", 0x10, "sp"),
            jr("ra"),
            addiu("sp", "sp", 0x18),
        ]
    )


class PowerOrderPatch:
    """Apply one deterministic constrained nine-slot Power Up permutation."""

    name = "power-order-shuffle"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        if not context.seed:
            raise PatchError("Shuffle Power Progression requires a seed")

        order, attempts = build_power_order(context.seed)
        tiers = assigned_power_tiers(order)

        # Guard all gameplay gates and both complete stock UI tables before any
        # writes.  Controls production runs earlier and calls these recognizers;
        # it intentionally leaves the gate instructions themselves untouched.
        for _label, (offset, vanilla_tier) in SIMPLE_TIER_SITES.items():
            rom.expect_u32(offset, _slti("v0", "v0", vanilla_tier))
        rom.expect_bytes(ICE_GROUND_TAIL_ROM, ICE_GROUND_TAIL_EXPECTED)

        for index, name in enumerate(VANILLA_POWER_ORDER):
            rom.expect_u32(POWER_ICON_TABLE_ROM + index * 4, POWER_ICONS[name])
            rom.expect_u32(POWER_HELP_TABLE_ROM + index * 4, POWER_HELP[name])

        tier_by_gate = {
            "slide": tiers["slide"],
            "directional-ice-up": tiers["directional-ice"],
            "directional-ice-down": tiers["directional-ice"],
            "air-ice-blast": tiers["air-ice-blast"],
            "ice-clone": tiers["ice-clone"],
            "ice-shatter-a": tiers["ice-shatter"],
            "ice-shatter-b": tiers["ice-shatter"],
            "super-slide": tiers["super-slide"],
            "freeze-on-contact": tiers["freeze-on-contact"],
            "polar-blast": tiers["polar-blast"],
        }
        for label, (offset, _vanilla_tier) in SIMPLE_TIER_SITES.items():
            rom.write_u32(offset, _slti("v0", "v0", tier_by_gate[label]))

        ice_tail = build_ice_ground_tail(tiers["ice-blast"])
        if len(ice_tail) != len(ICE_GROUND_TAIL_EXPECTED):
            raise AssertionError("ground Ice replacement changed in-place size")
        rom.write_bytes(ICE_GROUND_TAIL_ROM, ice_tail)

        for index, name in enumerate(order):
            rom.write_u32(POWER_ICON_TABLE_ROM + index * 4, POWER_ICONS[name])
            rom.write_u32(POWER_HELP_TABLE_ROM + index * 4, POWER_HELP[name])

        display_order = " -> ".join(POWER_DISPLAY_NAMES[name] for name in order)
        return (
            f"deterministic constrained Power Up order accepted after {attempts} attempt(s)",
            display_order,
            "Ice Shatter follows at least one freezing Power Up; Slide/Super Slide are independent",
        )
