import pytest

from mkmszr.errors import PatchError
from mkmszr.patches.base import PatchContext
from mkmszr.patches.power_order import (
    FREEZING_POWERS,
    ICE_GROUND_TAIL_EXPECTED,
    ICE_GROUND_TAIL_ROM,
    POWER_HELP,
    POWER_HELP_TABLE_ROM,
    POWER_ICON_TABLE_ROM,
    POWER_ICONS,
    POWER_NAMES,
    SIMPLE_TIER_SITES,
    VANILLA_POWER_ORDER,
    PowerOrderPatch,
    _candidate_power_order,
    _slti,
    assigned_power_tiers,
    build_power_order,
    power_order_is_valid,
)
from mkmszr.rom import RomImage


def _stock_shape() -> RomImage:
    end = max(
        POWER_HELP_TABLE_ROM + len(POWER_NAMES) * 4,
        POWER_ICON_TABLE_ROM + len(POWER_NAMES) * 4,
        ICE_GROUND_TAIL_ROM + len(ICE_GROUND_TAIL_EXPECTED),
        max(offset for offset, _tier in SIMPLE_TIER_SITES.values()) + 4,
    )
    data = bytearray(end)
    for offset, tier in SIMPLE_TIER_SITES.values():
        data[offset : offset + 4] = _slti("v0", "v0", tier).to_bytes(4, "big")
    data[
        ICE_GROUND_TAIL_ROM : ICE_GROUND_TAIL_ROM + len(ICE_GROUND_TAIL_EXPECTED)
    ] = ICE_GROUND_TAIL_EXPECTED
    for index, name in enumerate(VANILLA_POWER_ORDER):
        data[POWER_ICON_TABLE_ROM + 4 * index : POWER_ICON_TABLE_ROM + 4 * index + 4] = (
            POWER_ICONS[name].to_bytes(4, "big")
        )
        data[POWER_HELP_TABLE_ROM + 4 * index : POWER_HELP_TABLE_ROM + 4 * index + 4] = (
            POWER_HELP[name].to_bytes(4, "big")
        )
    return RomImage(data=data, _original=bytes(data))


@pytest.mark.parametrize("seed", ["POWER", "WEB00002", "TEST-0042", "different"])
def test_power_order_is_deterministic_and_valid(seed: str) -> None:
    first = build_power_order(seed)
    assert first == build_power_order(seed)
    order, attempts = first
    assert attempts >= 1
    assert power_order_is_valid(order)
    assert set(order) == set(POWER_NAMES)
    positions = {name: order.index(name) for name in order}
    assert positions["ice-shatter"] > min(positions[name] for name in FREEZING_POWERS)


def test_slide_and_super_slide_are_not_constrained() -> None:
    found_super_first = False
    for index in range(1000):
        order, _attempts = build_power_order(f"SLIDE-{index}")
        if order.index("super-slide") < order.index("slide"):
            found_super_first = True
            break
    assert found_super_first


def test_invalid_shatter_first_candidate_is_rejected() -> None:
    for index in range(10000):
        candidate = _candidate_power_order(f"SHATTER-{index}", 0)
        if not power_order_is_valid(candidate):
            order, attempts = build_power_order(f"SHATTER-{index}")
            assert attempts > 1
            assert power_order_is_valid(order)
            return
    pytest.fail("could not find a rejected attempt-0 candidate")


def test_patch_keeps_gameplay_and_both_ui_tables_in_one_order() -> None:
    seed = "WEB00002"
    rom = _stock_shape()
    order, _attempts = build_power_order(seed)
    tiers = assigned_power_tiers(order)

    PowerOrderPatch().apply(rom, PatchContext(seed=seed))

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
    for label, (offset, _tier) in SIMPLE_TIER_SITES.items():
        assert rom.read_u32(offset) == _slti("v0", "v0", tier_by_gate[label])

    assert tuple(
        rom.read_u32(POWER_ICON_TABLE_ROM + index * 4) for index in range(9)
    ) == tuple(POWER_ICONS[name] for name in order)
    assert tuple(
        rom.read_u32(POWER_HELP_TABLE_ROM + index * 4) for index in range(9)
    ) == tuple(POWER_HELP[name] for name in order)


def test_patch_requires_seed() -> None:
    rom = _stock_shape()
    with pytest.raises(PatchError, match="requires a seed"):
        PowerOrderPatch().apply(rom, PatchContext(seed=None))
