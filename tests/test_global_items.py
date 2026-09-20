from collections import Counter

from mkmszr.data.pickups import STAGE_PICKUPS
from mkmszr.global_items import TOKEN_ITEMS, build_stock_logical_pool


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


def test_logical_items_retain_source_location_for_exact_visual_materialization() -> None:
    pool = build_stock_logical_pool()
    assert all(item.source_stage_id >= 0 for item in pool)
    assert all(item.source_record_index >= 0 for item in pool)

    prison_key = next(item for item in pool if item.key == "prison-l1")
    assert prison_key.source_stage_id == 4
    assert prison_key.inventory_id == 0x1A
