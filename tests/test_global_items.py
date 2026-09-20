from collections import Counter

from mkmszr.data.pickups import FIRE, FORTRESS, STAGE_PICKUPS
from mkmszr.global_items import (
    POWER_UPGRADE,
    TOKEN_ITEMS,
    build_generic_inventory_award_callback,
    build_stock_logical_pool,
    materialize_destination_shell,
)

GENERIC_CALLBACK = 0xA01AF6FC
POWER_CALLBACK = 0xA01AF620


def _words(identity: bytes) -> tuple[int, ...]:
    return tuple(int.from_bytes(identity[i : i + 4], "big") for i in range(0, 0x1C, 4))


def test_stock_logical_pool_matches_all_84_ordinary_records() -> None:
    pool = build_stock_logical_pool()
    assert len(pool) == 84
    assert len(pool) == sum(len(stage.records) for stage in STAGE_PICKUPS)

    counts = Counter(item.key for item in pool)
    assert counts["herbs"] == 31
    assert counts["extra-life"] == 10
    assert counts["health-urn"] == 8
    assert counts["potion"] == 4
    assert counts["mana"] == 3
    assert counts["formula"] == 2
    assert counts["eye"] == 2
    assert counts["shield"] == 2
    assert counts["strength-urn"] == 1
    assert sum(item.progression_token is not None for item in pool) == 21


def test_every_progression_token_has_a_unique_native_inventory_id() -> None:
    assert len(TOKEN_ITEMS) == 21
    ids = [item_id for _name, item_id, _stage in TOKEN_ITEMS.values()]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(range(0x0E, 0x23))


def test_cross_stage_inventory_reward_keeps_fire_potion_shell() -> None:
    pool = build_stock_logical_pool()
    prison_key = next(item for item in pool if item.key == "prison-l1")

    plan = materialize_destination_shell(
        FIRE.records[0].identity,
        prison_key,
        generic_inventory_callback=GENERIC_CALLBACK,
        power_upgrade_callback=POWER_CALLBACK,
    )

    before = _words(FIRE.records[0].identity)
    after = _words(plan.identity)

    assert after[0] == before[0]
    assert after[1] == 0x1A
    assert after[2] == GENERIC_CALLBACK
    assert after[3:] == before[3:]
    assert plan.keeps_destination_visual
    assert not plan.requires_foreign_resource


def test_power_upgrade_can_use_any_destination_shell() -> None:
    before = _words(FORTRESS.records[0].identity)
    plan = materialize_destination_shell(
        FORTRESS.records[0].identity,
        POWER_UPGRADE,
        generic_inventory_callback=GENERIC_CALLBACK,
        power_upgrade_callback=POWER_CALLBACK,
    )
    after = _words(plan.identity)

    assert after[0] == before[0]
    assert after[1] == 0
    assert after[2] == POWER_CALLBACK
    assert after[3:] == before[3:]


def test_native_effect_keeps_global_native_callback() -> None:
    pool = build_stock_logical_pool()
    extra_life = next(item for item in pool if item.key == "extra-life")
    before = _words(FIRE.records[0].identity)

    plan = materialize_destination_shell(
        FIRE.records[0].identity,
        extra_life,
        generic_inventory_callback=GENERIC_CALLBACK,
        power_upgrade_callback=POWER_CALLBACK,
    )
    after = _words(plan.identity)

    assert after[0] == before[0]
    assert after[1] == 0
    assert after[2] == 0x80038A1C
    assert after[3:] == before[3:]


def test_generic_inventory_callback_is_compact_and_uses_a1_item_id() -> None:
    callback = build_generic_inventory_award_callback(
        inventory_add_va=0x80075448,
        sound_and_return_tail_va=0xA01AF680,
    )
    assert len(callback) == 0x18
    assert callback == bytes.fromhex(
        "27BDFFE8 "
        "AFBF0010 "
        "0C01D512 "
        "00A02021 "
        "0806BDA0 "
        "00000000"
    )
