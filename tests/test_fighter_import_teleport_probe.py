"""Teleport floor probe (production composition v03): MIPS vs the Python model."""

from __future__ import annotations

import random

from mips_eval import Machine

from mkmszr.fighter_import.actions import robo_teleport as rt
from mkmszr.fighter_import.mips import Assembler

BASE = 0xA01B0000
TABLE = 0x80400000


def _store_half(m: Machine, address: int, value: int) -> None:
    word = m.load(address & ~3)
    shift = 16 if address & 2 == 0 else 0
    m.store(address & ~3, (word & ~(0xFFFF << shift)) | ((value & 0xFFFF) << shift))


def _load_regions(m: Machine, regions) -> None:
    m.store(rt.REGION_COUNT, len(regions))
    m.store(rt.REGION_TABLE_PTR, TABLE)
    for i, (enabled, flags, (bx, by, bz), points) in enumerate(regions):
        rec = TABLE + i * rt.REGION_STRIDE
        flag_word = (rt.REGION_ENABLED + i) & ~3
        shift = 8 * (3 - ((rt.REGION_ENABLED + i) & 3))
        m.store(
            flag_word, (m.load(flag_word) & ~(0xFF << shift)) | ((1 if enabled else 0) << shift)
        )
        for off, value in ((0, bx), (4, by), (8, bz), (0x0C, len(points)), (0x94, flags)):
            m.store(rec + off, value & 0xFFFFFFFF)
        for k, (dx, dy) in enumerate(points):
            _store_half(m, rec + 0x10 + 8 * k, dx)
            _store_half(m, rec + 0x12 + 8 * k, dy)


def _random_regions(rng: random.Random):
    regions = []
    for _ in range(rng.randint(0, 6)):
        n = rng.randint(1, 6)
        xs = sorted(rng.sample(range(-400, 400), n))
        points = [(x, rng.randint(-60, 60)) for x in xs]
        flags = rng.choice([0, 0, 0, 0x100, 0x300, 0x800])
        regions.append((rng.random() < 0.85, flags, (rng.randint(-200, 200), rng.randint(-300, 300),
                        rng.randint(-200, 200)), points))  # fmt: skip
    return regions


def test_probe_matches_the_model() -> None:
    a = Assembler(BASE)
    rt.emit_floor_probe(a)
    rng = random.Random(11)
    hits = 0
    for _ in range(400):
        regions = _random_regions(rng)
        m = Machine(a.link(), BASE)
        _load_regions(m, regions)
        for _ in range(8):
            if regions and rng.random() < 0.6:  # aim at a real floor
                _, _, (bx, by, bz), pts = rng.choice(regions)
                k = rng.randrange(len(pts))
                x = bx + pts[k][0] - rng.randint(0, 3)
                y = ((by + pts[k][1]) << 8) + rng.randint(-0x2400, 0x2400)
                z = bz + rng.randint(-0x90, 0x90)
            else:
                x, y, z = (
                    rng.randint(-700, 700),
                    rng.randint(-0x50000, 0x50000),
                    rng.randint(-400, 400),
                )
            m.regs[4], m.regs[5], m.regs[6], m.regs[31] = (
                x & 0xFFFFFFFF,
                z & 0xFFFFFFFF,
                y & 0xFFFFFFFF,
                0x80001000,
            )
            assert m.run(a.labels["floor_probe"]).target == 0x80001000
            want = rt.probe_model(regions, x, z, y)
            hits += want
            assert m.regs[2] == int(want), (regions, x, z, y)
    assert hits > 300


def test_probe_ignores_disabled_and_shaped_regions() -> None:
    floor = (True, 0, (0, 100, 0), [(-50, 0), (50, 0)])
    assert rt.probe_model([floor], 10, 0, 100 << 8)
    assert not rt.probe_model([(False, *floor[1:])], 10, 0, 100 << 8)
    assert not rt.probe_model([(True, 0x300, *floor[2:])], 10, 0, 100 << 8)
    assert not rt.probe_model([floor], 60, 0, 100 << 8)  # past the last point: the drop-off
    assert not rt.probe_model([floor], 10, 0x81, 100 << 8)  # other depth
    assert not rt.probe_model([floor], 10, 0, (100 + 0x21) << 8)  # floor too far from the placement
