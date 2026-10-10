"""Synthetic VI/PIF/AI alignment tests; no ROM, RMG or input device required."""
from analyze_input_audio_alignment import (
    decode_buttons,
    input_edges,
    rejected_audio_services,
    severe_bursts,
)


def row(index, ns, event, count, *values):
    return (index, ns, event, count, *(tuple(values) + (0,) * (8 - len(values))))


def test_guest_input_edges_align_to_vi():
    vi = [
        row(0, 1000, 0x20, 100),
        row(1, 2000, 0x20, 1000),
        row(2, 3000, 0x20, 1900),
    ]
    pif = [
        row(0, 1900, 0x60, 900, 0, 0, 0, 0, 0, 0, 1, 4),
        row(1, 2010, 0x60, 1010, 0, 8, 8, 0, 0, 0, 1, 4),
        row(2, 2200, 0x60, 1300, 0, 8, 8, 0, 0, 0, 1, 4),
        row(3, 2890, 0x60, 1700, 0, 0, 0, 0, 0, 0, 1, 4),
    ]
    edges = input_edges(pif, vi)
    assert len(edges) == 3
    assert [e["vi_event_index"] for e in edges] == [0, 1, 1]
    assert [e["buttons_hex"] for e in edges] == ["0x0000", "0x0008", "0x0000"]
    assert decode_buttons(0x0008) == "D-up"


def test_distinguishes_native_status_logger_from_second_service():
    ai = [
        row(0, 1900, 0x13, 100, 0xC0000000),
        row(1, 1910, 0x14, 110, 0),
        row(2, 1920, 0x13, 120, 0x40000000),
        row(3, 1930, 0x12, 130, 1400),
        row(4, 2900, 0x13, 200, 0x40000000),
        row(5, 2910, 0x12, 210, 1400),
    ]
    events = rejected_audio_services(ai, 1000)
    assert len(events) == 1
    assert events[0] == 9e-7
    assert severe_bursts(events) == []
