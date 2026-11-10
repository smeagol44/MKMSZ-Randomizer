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
        (1, 0x08): [F, F, F],  # long-fall loop (a jump back is added below)
    }
    p = 0x200
    for (table, index), words in scripts.items():
        slot = 4 * index if table == 0 else TABLE1_OFFSET + 4 * index
        data[slot : slot + 4] = p.to_bytes(4, "big")
        for w in words:
            data[p : p + 4] = w.to_bytes(4, "big")
            p += 4
        if (table, index) == (1, 0x08):
            start = int.from_bytes(data[slot : slot + 4], "big")
            for w in (1, start):  # jump back to the loop start
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


def test_long_fall_holds_the_last_fall_back_frame_and_keeps_its_loop() -> None:
    out = cm.apply(_file())
    assert cm.frames(out, cm.LONG_FALL) == [F + 36] * 3
    start, _ = cm.slot_span(out, cm.LONG_FALL)
    assert int.from_bytes(out[start + 12 : start + 16], "big") == 1
    assert int.from_bytes(out[start + 16 : start + 20], "big") == start


def _layout(scripts: dict[tuple[int, int], list[int]]) -> bytearray:
    """A file with ``scripts`` laid out in order, each followed by a gap and an end marker."""

    data = bytearray(0x900)
    p = 0x200
    for (table, index), words in scripts.items():
        slot = 4 * index if table == 0 else TABLE1_OFFSET + 4 * index
        data[slot : slot + 4] = p.to_bytes(4, "big")
        for w in words:
            data[p : p + 4] = w.to_bytes(4, "big")
            p += 4
        p += 4
    data[TABLE1_OFFSET + 4 * 40 : TABLE1_OFFSET + 4 * 41] = p.to_bytes(4, "big")  # end marker
    return data


S, I = 0x40000, 0x50000  # stock / imported frame ranges


def _host(frames: int, imported: bool) -> bytearray:
    f = (lambda k: I + 4 * k) if imported else (lambda k: S + 4 * k)
    flip = [f(60 + k) for k in range(5)] if not imported else [f(0)] * 5  # imported: placeholders
    return _layout({
        (0, 0x0F): [f(1), f(2), f(3), 0, f(4), f(5), 0],  # low punch: first punch, second punch
        (1, 0x03): [f(0)] * 5 + [0],  # pickup
        # knockdown fall-back phase, zero-padded to the stock capacity as the importer does
        (0, 0x1E): [f(10 + k) for k in range(frames)] + [0] * (7 - frames),
        (1, 0x09): [f(20), 0],  # lying
        (0, 0x20): [f(30), f(31), f(32), 0, f(30), f(31), f(32), 0],  # stumble
        (0, 0x1A): [f(40), f(41), 0],  # forward flip
        (0, 0x1B): [f(41), f(40), 0],  # back flip
        (0, 0x2E): flip + [0],  # flipped
        # a victim script: token 10 + operand before each pose, two phases
        (1, 0x0E): [10, 0xFF89000F, flip[0], 10, 0x0004_0015, flip[1], 10, 7, f(15 if not imported else 0),
                    0, 10, 0x5C, flip[4], 10, 0x10, f(20 if not imported else 0), 0],
        (1, 0x16): [f(32), flip[0], flip[2], f(20), 0],  # flipped script without token 10
    })  # fmt: skip


def test_pickup_is_the_first_low_punch_1_2_2_3_3() -> None:
    data = _host(6, imported=True)
    cm.pickup(data)
    assert cm.frames(data, cm.PICKUP) == [I + 4, I + 8, I + 8, I + 12, I + 12]


def test_victim_poses_translate_by_role_and_keep_the_choreography() -> None:
    stock, data = _host(6, imported=False), _host(5, imported=True)
    flips = [0x70000 + 4 * k for k in range(5)]
    before = bytes(data)
    assert [s for s, _ in cm.victim_scripts(stock)] == [
        cm.slot_span(stock, (0, 0x2E))[0], cm.slot_span(stock, (1, 0x0E))[0], cm.slot_span(stock, (1, 0x16))[0]
    ]  # fmt: skip
    assert cm.victim(data, stock, flips) == 5 + 5 + 4
    assert cm.frames(data, (0, 0x2E)) == flips
    start, end = cm.slot_span(data, (1, 0x0E))
    words = [int.from_bytes(data[p : p + 4], "big") for p in range(start, end, 4)][:17]
    # tokens and operands untouched; knockdown frame 5 of 6 (index 5) -> imported index 4 of 5
    assert words == [10, 0xFF89000F, flips[0], 10, 0x0004_0015, flips[1], 10, 7, I + 4 * 14,
                     0, 10, 0x5C, flips[4], 10, 0x10, I + 4 * 20, 0]  # fmt: skip
    assert cm.frames(data, (1, 0x16)) == [I + 4 * 32, flips[0], flips[2], I + 4 * 20]
    # outside the victim scripts nothing changes
    for slot in ((0, 0x0F), (0, 0x1E), (0, 0x20)):
        s0, e0 = cm.slot_span(data, slot)
        assert data[s0:e0] == before[s0:e0]


def test_victim_refuses_a_changed_choreography() -> None:
    stock, data = _host(6, imported=False), _host(5, imported=True)
    start, _ = cm.slot_span(data, (1, 0x0E))
    data[start + 4 : start + 8] = (0x12345678).to_bytes(4, "big")
    with pytest.raises(ValueError):
        cm.victim(data, stock, [0x70000] * 5)
