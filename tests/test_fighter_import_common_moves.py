"""Generic slide/death recipes on a synthetic fighter file."""

from __future__ import annotations

import pytest

from mkmszr.fighter_import import common_moves as cm
from mkmszr.fighter_import.mkmsz_fighter import TABLE1_OFFSET

F = 0x30000  # frame offsets live far past the scripts


def _file() -> bytearray:
    data = bytearray(0x800)
    scripts = {
        (0, 0x04): [F + 1 * 4, F + 2 * 4, 0],  # duck
        (0, 0x05): [F + 3 * 4, 2, F + 4 * 4, 0],  # duck turn (flip token in between)
        (0, 0x0A): [F + 5 * 4, F + 6 * 4, F + 7 * 4, 0],  # duck low kick
        (0, 0x1E): [F + 8 * 4, F + 9 * 4, 0, F + 10 * 4, F + 11 * 4, 0],  # knockdown, 2 phases
        (0, 0x2A): [F, F, 6, 1, 5, F, 6, 2, 3, F, F, 0, F],  # death: callbacks keep their words
        (1, 0x02): [F, F, F, 0],  # slide
    }
    p = 0x200
    for (table, index), words in scripts.items():
        slot = 4 * index if table == 0 else TABLE1_OFFSET + 4 * index
        data[slot : slot + 4] = p.to_bytes(4, "big")
        for w in words:
            data[p : p + 4] = w.to_bytes(4, "big")
            p += 4
        p += 4  # a gap so every script has a following start
    # secondary 9 points into the knockdown's second phase, as in the MKMSZ host file
    knock = int.from_bytes(data[4 * 0x1E : 4 * 0x1E + 4], "big")
    data[TABLE1_OFFSET + 4 * 9 : TABLE1_OFFSET + 4 * 10] = (knock + 12).to_bytes(4, "big")
    data[TABLE1_OFFSET + 4 * 40 : TABLE1_OFFSET + 4 * 41] = p.to_bytes(4, "big")  # end marker
    return data


def test_slide_takes_duck_turn_and_low_kick_frames() -> None:
    out = cm.apply(_file())
    assert cm.frames(out, cm.SLIDE) == [F + 4, F + 12, F + 28]


def test_death_takes_the_knockdown_and_holds_the_last_frame() -> None:
    data = _file()
    assert cm.phase_frames(data, cm.KNOCKDOWN, 2) == [F + 32, F + 36, F + 40, F + 44]
    out = cm.apply(data)
    assert cm.frames(out, cm.DEATH) == [F + 32, F + 36, F + 40, F + 44, F + 44, F + 44]
    start, _end = cm.slot_span(out, cm.DEATH)
    words = [int.from_bytes(out[start + 4 * i : start + 4 * i + 4], "big") for i in range(13)]
    assert words[2:5] == [6, 1, 5] and words[6:9] == [6, 2, 3] and words[11] == 0


def test_slide_needs_three_frames() -> None:
    data = _file()
    start, _ = cm.slot_span(data, cm.SLIDE)
    data[start + 8 : start + 12] = bytes(4)
    with pytest.raises(ValueError):
        cm.apply(data)
