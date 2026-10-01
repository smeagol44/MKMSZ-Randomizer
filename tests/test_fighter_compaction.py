from mkmszr.fighter_compaction import (
    BODY_INDEX_MAP,
    BODY_PALETTE_REPRESENTATIVES,
    SPECS,
    _compact_palette,
)


def test_pris_body_mapping_is_16_color_and_transparency_preserving():
    assert len(BODY_INDEX_MAP) == 64
    assert BODY_INDEX_MAP[0] == 0
    assert set(BODY_INDEX_MAP) == set(range(16))
    assert len(BODY_PALETTE_REPRESENTATIVES) == 15


def test_pris_palette_compaction_uses_accepted_representatives():
    values = list(range(64))
    compact = _compact_palette(values)
    assert compact == [0, *BODY_PALETTE_REPRESENTATIVES]


def test_pris_compact_sizes_pin_recovered_production_layouts():
    assert SPECS[0x8E].expected_compact_size == 0x1A148
    assert SPECS[0x8F].expected_compact_size == 0x17138
    assert SPECS[0x90].expected_compact_size == 0x16AC0
    assert SPECS[0x91].expected_compact_size == 0x102F0
