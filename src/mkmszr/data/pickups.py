"""Research-backed N64 ordinary-pickup catalogs used by the native randomizer.

Only the 84 ordinary 0x30-byte pickup records are listed here. Scripted/special
mechanisms such as the Temple Map intentionally remain outside this catalog.

The movable identity slice is record +0x10..+0x2B. It contains behavior,
callback parameter, award callback, extents, the stage-local resource selector,
and presentation descriptor. Position/metadata (+0x00..+0x0F) and the collected
flag (+0x2C) remain properties of the destination location.
"""

from __future__ import annotations

from dataclasses import dataclass

IDENTITY_OFFSET = 0x10
IDENTITY_SIZE = 0x1C
COLLECTED_OFFSET = 0x2C
RECORD_SIZE = 0x30


def _identity(
    type_value: int,
    callback_parameter: int,
    callback: int,
    extent_a: int,
    extent_b: int,
    resource_slot: int,
    presentation: int,
) -> bytes:
    return b"".join(
        value.to_bytes(4, "big")
        for value in (
            type_value,
            callback_parameter,
            callback,
            extent_a,
            extent_b,
            resource_slot,
            presentation,
        )
    )


@dataclass(frozen=True)
class PickupSpec:
    rom_base: int
    identity: bytes
    progression_token: str | None = None


@dataclass(frozen=True)
class StagePickupSpec:
    key: str
    title: str
    stage_id: int
    records: tuple[PickupSpec, ...]
    requirements: tuple[frozenset[str], ...]

    def __post_init__(self) -> None:
        if len(self.records) != len(self.requirements):
            raise ValueError(f"{self.key}: records/requirements length mismatch")
        if any(len(record.identity) != IDENTITY_SIZE for record in self.records):
            raise ValueError(f"{self.key}: pickup identity must be {IDENTITY_SIZE} bytes")


FREE = frozenset()


def _p(
    rom_base: int,
    type_value: int,
    callback_parameter: int,
    callback: int,
    extent_a: int,
    extent_b: int,
    resource_slot: int,
    presentation: int,
    token: str | None = None,
) -> PickupSpec:
    return PickupSpec(
        rom_base,
        _identity(
            type_value,
            callback_parameter,
            callback,
            extent_a,
            extent_b,
            resource_slot,
            presentation,
        ),
        token,
    )


HERBS = (0x01, 0x00000000, 0x800389BC, 0x20, 0x20)
EXTRA_LIFE = (0x02, 0x00000000, 0x80038A1C, 0x20, 0x20)
HEALTH = (0x06, 0x00000000, 0x800389EC, 0x20, 0x20)

TEMPLE = StagePickupSpec(
    "temple",
    "Temple",
    0,
    (
        *(
            _p(base, *HERBS, 0x0F, 0x800B1D38)
            for base in (0x000CEF6C, 0x000CEF9C, 0x000CEFCC, 0x000CEFFC)
        ),
    ),
    (FREE,) * 4,
)

WIND = StagePickupSpec(
    "wind",
    "Wind",
    1,
    (
        _p(0x000D8424, *HERBS, 5, 0x800B1D38),
        _p(0x000D8454, *HERBS, 5, 0x800B1D38),
        _p(0x000D8484, *EXTRA_LIFE, 4, 0x800B1D38),
        _p(0x000D84B4, 0, 0, 0x802F2CB4, 0x20, 0x20, 0, 0x800B1D18, "wind-circle"),
        _p(0x000D84E4, 0, 1, 0x802F2CB4, 0x20, 0x20, 2, 0x800B1D18, "wind-triangle"),
        _p(0x000D8514, 0, 2, 0x802F2CB4, 0x20, 0x20, 1, 0x800B1D18, "wind-three-bars"),
    ),
    (
        FREE,
        FREE,
        FREE,
        FREE,
        frozenset({"wind-circle"}),
        frozenset({"wind-triangle"}),
    ),
)

EARTH = StagePickupSpec(
    "earth",
    "Earth",
    3,
    (
        _p(0x000E1284, 0, 0, 0x802F52B0, 0x0E, 0x10, 0, 0x800B1D18, "earth-square"),
        _p(0x000E12B4, 0, 1, 0x802F52B0, 0x12, 0x0C, 1, 0x800B1D18, "earth-four-square"),
        _p(0x000E12E4, 0, 2, 0x802F52B0, 0x10, 0x0F, 2, 0x800B1D18, "earth-triangle"),
        _p(0x000E1314, 9, 0, 0x8003898C, 0x20, 0x20, 20, 0x800B1D38),
        _p(0x000E1344, *EXTRA_LIFE, 13, 0x800B1D38),
        _p(0x000E1374, *HERBS, 14, 0x800B1D38),
        _p(0x000E13A4, *EXTRA_LIFE, 13, 0x800B1D38),
        _p(0x000E13D4, 3, 0, 0x80038A58, 0x20, 0x20, 15, 0x800B1C14),
        _p(0x000E1404, 3, 0, 0x80038A58, 0x20, 0x20, 15, 0x800B1C14),
        _p(0x000E1434, *EXTRA_LIFE, 13, 0x800B1D38),
        _p(0x000E1464, *HERBS, 14, 0x800B1D38),
        _p(0x000E1494, *HERBS, 14, 0x800B1D38),
        _p(0x000E14C4, *HERBS, 14, 0x800B1D38),
        _p(0x000E14F4, *EXTRA_LIFE, 13, 0x800B1D38),
        _p(0x000E1524, *HERBS, 14, 0x800B1D38),
        _p(0x000E1554, *HERBS, 14, 0x800B1D38),
        _p(0x000E1584, *HERBS, 14, 0x800B1D38),
        _p(0x000E15B4, *EXTRA_LIFE, 13, 0x800B1D38),
        _p(0x000E15E4, 0x0A, 0, 0x8003895C, 0x20, 0x20, 18, 0x800B1D38),
        _p(0x000E1614, 7, 0, 0x8003892C, 0x20, 0x20, 19, 0x800B1D38),
    ),
    (
        FREE,
        frozenset({"earth-square"}),
        frozenset({"earth-four-square"}),
        FREE,
        FREE,
        FREE,
        FREE,
        frozenset({"earth-square"}),
        frozenset({"earth-square"}),
        frozenset({"earth-square"}),
        frozenset({"earth-square"}),
        frozenset({"earth-square"}),
        frozenset({"earth-four-square"}),
        frozenset({"earth-four-square"}),
        frozenset({"earth-four-square"}),
        frozenset({"earth-four-square"}),
        frozenset({"earth-four-square"}),
        frozenset({"earth-four-square"}),
        frozenset({"earth-four-square"}),
        frozenset({"earth-four-square"}),
    ),
)

WATER = StagePickupSpec(
    "water",
    "Water",
    2,
    (
        _p(0x000BAB14, *HEALTH, 28, 0x800B1D38),
        _p(0x000BAB44, *HEALTH, 28, 0x800B1D38),
        _p(0x000BAB74, 3, 0, 0x80038A58, 0x20, 0x20, 26, 0x800B1C14),
        _p(0x000BABA4, *HERBS, 25, 0x800B1D38),
        _p(0x000BABD4, 1, 0, 0x800388FC, 0x20, 0x20, 27, 0x800B1BAC),
        _p(0x000BAC04, *EXTRA_LIFE, 24, 0x800B1D38),
        _p(0x000BAC34, 0, 0, 0x802F2448, 0x20, 0x20, 4, 0x800B1D18, "water-triangle"),
        _p(0x000BAC64, 0, 1, 0x802F2448, 0x20, 0x20, 5, 0x800B1D18, "water-three-bars"),
        _p(0x000BAC94, 0, 2, 0x802F2448, 0x20, 0x20, 6, 0x800B1D18, "water-moon"),
    ),
    (
        FREE,
        frozenset({"water-moon"}),
        FREE,
        FREE,
        FREE,
        FREE,
        FREE,
        frozenset({"water-triangle"}),
        frozenset({"water-three-bars"}),
    ),
)

FIRE = StagePickupSpec(
    "fire",
    "Fire",
    5,
    (
        _p(0x000E6218, 0x0B, 0, 0x800388FC, 0x20, 0x20, 24, 0x800B1BAC),
        _p(0x000E6248, 9, 0, 0x8003898C, 0x20, 0x20, 25, 0x800B1D38),
        _p(0x000E6098, *HEALTH, 26, 0x800B1D38),
        _p(0x000E6308, *HERBS, 21, 0x800B1D38),
        _p(0x000E60F8, 0, 0, 0x802F0EBC, 0x20, 0x20, 0, 0x800B1D18, "fire-triangle-up"),
        _p(0x000E60C8, *HEALTH, 26, 0x800B1D38),
        _p(0x000E6368, 7, 0, 0x8003892C, 0x20, 0x20, 22, 0x800B1D38),
        _p(0x000E6338, *HERBS, 21, 0x800B1D38),
        _p(0x000E6278, *EXTRA_LIFE, 20, 0x800B1D38),
        _p(0x000E61B8, 0, 1, 0x802F0EBC, 0x20, 0x20, 1, 0x800B1D18, "fire-two-bars"),
        _p(0x000E6398, *EXTRA_LIFE, 20, 0x800B1D38),
        _p(0x000E62A8, 0x0A, 0, 0x8003895C, 0x20, 0x20, 23, 0x800B1D38),
        _p(0x000E62D8, 0x0B, 0, 0x800388FC, 0x20, 0x20, 24, 0x800B1BAC),
        _p(0x000E63C8, *HERBS, 21, 0x800B1D38),
        _p(0x000E61E8, 0, 2, 0x802F0EBC, 0x20, 0x20, 2, 0x800B1D18, "fire-triangle-down"),
        _p(0x000E63F8, *HERBS, 21, 0x800B1D38),
    ),
    (FREE,) * 16,
)

PRISON = StagePickupSpec(
    "prison",
    "Prison",
    4,
    (
        _p(0x000CA030, 0, 0, 0x80038770, 0x12, 0x14, 0, 0x800B1D18, "prison-l1"),
        _p(0x000CA060, 0, 1, 0x80038770, 0x12, 0x14, 1, 0x800B1D18, "prison-l2"),
        _p(0x000CA090, 0, 0x8002, 0x80038770, 0x12, 0x14, 2, 0x800B1D18, "prison-l3"),
        _p(0x000CA0C0, 5, 0, 0x80038A90, 0x12, 0x15, 11, 0x800B1D38),
        *(
            _p(base, *HERBS, 8, 0x800B1D38)
            for base in (
                0x000CA0F0,
                0x000CA120,
                0x000CA150,
                0x000CA180,
                0x000CA1B0,
                0x000CA1E0,
            )
        ),
    ),
    (
        FREE,
        frozenset({"prison-l1"}),
        frozenset({"prison-l1", "prison-l2"}),
        frozenset({"prison-l1", "prison-l2"}),
        FREE,
        FREE,
        FREE,
        FREE,
        frozenset({"prison-l1", "prison-l2", "prison-l3"}),
        frozenset({"prison-l1"}),
    ),
)

BRIDGE = StagePickupSpec(
    "bridge",
    "Bridge",
    8,
    (
        _p(0x000BFFD8, 0, 0x8000, 0x802EF178, 0x20, 0x20, 0, 0x800B1D18, "bridge-omega"),
        _p(0x000C0008, 0, 0x8001, 0x802EF178, 0x20, 0x20, 1, 0x800B1D18, "bridge-rings"),
        _p(0x000C0038, 0, 0x8002, 0x802EF178, 0x20, 0x20, 2, 0x800B1D18, "bridge-arrow"),
        _p(0x000C0068, 6, 0x8000, 0x800389EC, 0x20, 0x20, 24, 0x800B1D38),
        _p(0x000C0098, 0x0B, 0, 0x800388FC, 0x20, 0x20, 23, 0x800B1BAC),
        _p(0x000C00C8, *HERBS, 21, 0x800B1D38),
        _p(0x000C00F8, *EXTRA_LIFE, 22, 0x800B1D38),
        _p(0x000C0128, *HEALTH, 24, 0x800B1D38),
        _p(0x000C0158, *HEALTH, 24, 0x800B1D38),
        _p(0x000C0188, *HEALTH, 24, 0x800B1D38),
    ),
    (FREE,) * 10,
)

FORTRESS = StagePickupSpec(
    "fortress",
    "Fortress",
    9,
    (
        _p(0x000C4834, 0, 0x8001, 0x80038770, 0x12, 0x14, 1, 0x800B1BD0, "crystal-kia"),
        _p(0x000C4864, 0, 0x8000, 0x80038770, 0x12, 0x14, 0, 0x800B1BD0, "crystal-jataaka"),
        _p(0x000C4894, 0, 0x8002, 0x80038770, 0x12, 0x14, 2, 0x800B1BD0, "crystal-sareena"),
        *(
            _p(base, *HERBS, 3, 0x800B1D38)
            for base in (
                0x000C48C4,
                0x000C48F4,
                0x000C4924,
                0x000C4954,
                0x000C4984,
                0x000C49B4,
            )
        ),
    ),
    (FREE,) * 9,
)

STAGE_PICKUPS = (TEMPLE, WIND, WATER, EARTH, PRISON, FIRE, BRIDGE, FORTRESS)
TOTAL_ORDINARY_PICKUPS = sum(len(stage.records) for stage in STAGE_PICKUPS)

if TOTAL_ORDINARY_PICKUPS != 84:
    raise AssertionError(f"expected 84 ordinary pickups, got {TOTAL_ORDINARY_PICKUPS}")
