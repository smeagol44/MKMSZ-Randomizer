"""Exact ordinary-enemy spawn catalog for N64 USA Rev. 0.

The 104 entries below are the fighter-type words in the eight main ordinary
enemy streams. Five gated singleton encounters remain cataloged but are marked
special so the planner preserves them instead of adding them to the grunt pool.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class EnemySpawnSpec:
    type_word_rom: int
    stock_type: int
    special: bool = False


@dataclass(frozen=True)
class StageEnemySpec:
    key: str
    title: str
    stage_id: int
    stream_va: int
    records: tuple[EnemySpawnSpec, ...]

    @property
    def randomizable_records(self) -> tuple[EnemySpawnSpec, ...]:
        return tuple(record for record in self.records if not record.special)

    @property
    def special_records(self) -> tuple[EnemySpawnSpec, ...]:
        return tuple(record for record in self.records if record.special)

    @property
    def native_type_counts(self) -> tuple[tuple[int, int], ...]:
        return tuple(sorted(Counter(r.stock_type for r in self.randomizable_records).items()))


def _records(
    offsets: tuple[int, ...],
    types: tuple[int, ...],
    specials: frozenset[int] = frozenset(),
) -> tuple[EnemySpawnSpec, ...]:
    if len(offsets) != len(types):
        raise ValueError("enemy offsets/types length mismatch")
    return tuple(
        EnemySpawnSpec(offset, type_id, index in specials)
        for index, (offset, type_id) in enumerate(zip(offsets, types, strict=True))
    )


TEMPLE = StageEnemySpec(
    "temple", "Temple", 0, 0x800B2D40,
    _records(
        (0xB396C,0xB3998,0xB39C0,0xB39E4,0xB3A10,0xB3A38,0xB3A5C,0xB3A80,0xB3AA8),
        (0x01,0x01,0x01,0x02,0x02,0x02,0x02,0x02,0x12),
        frozenset((8,)),
    ),
)

WIND = StageEnemySpec(
    "wind", "Wind", 1, 0x800B30E4,
    _records(
        (0xB3D04,0xB3D2C,0xB3D54,0xB3D7C,0xB3DA4,0xB3DCC,0xB3DF4,0xB3E1C,
         0xB3E44,0xB3E6C,0xB3E9C,0xB3EC4,0xB3EF8,0xB3F20,0xB3F48,0xB3F70,0xB3F98),
        (0x03,) * 17,
    ),
)

WATER = StageEnemySpec(
    "water", "Water", 2, 0x800B2F9C,
    _records(
        (0xB3BB4,0xB3BD8,0xB3BFC,0xB3C20,0xB3C44,0xB3C68,0xB3C8C,0xB3CB0,0xB3CD4),
        (0x1A,0x1A,0x05,0x1A,0x05,0x1A,0x05,0x1A,0x05),
    ),
)

EARTH = StageEnemySpec(
    "earth", "Earth", 3, 0x800B2EB8,
    _records(
        (0xB3AC8,0xB3AE4,0xB3B00,0xB3B1C,0xB3B38,0xB3B54,0xB3B70,0xB3B8C),
        (0x00,) * 8,
    ),
)

PRISON = StageEnemySpec(
    "prison", "Prison", 4, 0x800B361C,
    _records(
        (0xB4240,0xB4260,0xB4280,0xB42A0,0xB42C0,0xB42E0,0xB4300,0xB4320,0xB4340,
         0xB4360,0xB4380,0xB43A0,0xB43BC,0xB43D8,0xB43F4,0xB4410,0xB442C,0xB4448,
         0xB4464,0xB4480),
        (0x15,0x15,0x15,0x15,0x15,0x15,0x0E,0x0E,0x15,0x15,0x11,0x16,0x16,0x16,
         0x14,0x16,0x14,0x14,0x16,0x16),
        frozenset((10,)),
    ),
)

FIRE = StageEnemySpec(
    "fire", "Fire", 5, 0x800B3890,
    _records(
        (0xB44A8,0xB44CC,0xB44F0,0xB4514,0xB4538,0xB4564,0xB4590,0xB45B4,0xB45D8,
         0xB45FC,0xB4620,0xB4644),
        (0x0A,0x09,0x0A,0x09,0x0A,0x09,0x09,0x0A,0x09,0x0A,0x0A,0x0A),
    ),
)

BRIDGE = StageEnemySpec(
    "bridge", "Bridge", 8, 0x800B3A7C,
    _records(
        (0xB4698,0xB46C0,0xB46E8,0xB4710,0xB4738,0xB4760,0xB4788,0xB47B0,0xB47D8,
         0xB4800,0xB4828,0xB4850,0xB4878),
        (0x14,0x14,0x14,0x17,0x14,0x17,0x14,0x17,0x14,0x17,0x17,0x14,0x17),
    ),
)

FORTRESS = StageEnemySpec(
    "fortress", "Fortress", 9, 0x800B33A8,
    _records(
        (0xB3FD0,0xB3FFC,0xB4028,0xB4054,0xB4078,0xB409C,0xB40C0,0xB40E4,0xB4108,
         0xB4134,0xB4158,0xB417C,0xB41A0,0xB41C4,0xB41E8,0xB420C),
        (0x0D,0x13,0x1C,0x0E,0x0E,0x0E,0x0E,0x0E,0x0E,0x0F,0x0F,0x0F,0x0F,0x0F,
         0x0F,0x0F),
        frozenset((0,1,2)),
    ),
)

STAGE_ENEMIES = (TEMPLE,WIND,WATER,EARTH,PRISON,FIRE,BRIDGE,FORTRESS)
STAGE_ENEMIES_BY_KEY = {stage.key: stage for stage in STAGE_ENEMIES}

TOTAL_ENEMY_SPAWNS = sum(len(stage.records) for stage in STAGE_ENEMIES)
TOTAL_RANDOMIZABLE_ENEMY_SPAWNS = sum(len(stage.randomizable_records) for stage in STAGE_ENEMIES)
TOTAL_FIXED_SPECIAL_ENEMY_SPAWNS = sum(len(stage.special_records) for stage in STAGE_ENEMIES)

assert TOTAL_ENEMY_SPAWNS == 104
assert TOTAL_RANDOMIZABLE_ENEMY_SPAWNS == 99
assert TOTAL_FIXED_SPECIAL_ENEMY_SPAWNS == 5
