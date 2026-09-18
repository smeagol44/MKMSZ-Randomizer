from mkmszr.rom import _changed_spans


def test_changed_spans_groups_adjacent_bytes() -> None:
    before = bytes([0, 0, 0, 0, 0, 0, 0])
    after = bytes([0, 1, 2, 0, 0, 3, 0])
    assert _changed_spans(before, after) == ((1, 3), (5, 6))
