"""Rope-attachment single-actor rewrite (Sektor composition v06)."""

from __future__ import annotations

import pytest

from mkmszr.fighter_import import attachment as att


def _file(pairs: dict[int, tuple[int, int, int]]) -> bytes:
    data = bytearray(0x400)
    for off, words in pairs.items():
        data[off : off + 12] = b"".join(w.to_bytes(4, "big") for w in words)
    return bytes(data)


def test_pairs_cover_p28_and_p29() -> None:
    assert len(att.ATTACHMENT_PAIRS) == 11
    assert att.ATTACHMENT_PAIRS[7] == 0x380 and att.ATTACHMENT_PAIRS[8] == 0x394
    assert att.ATTACHMENT_PAIRS[-1] + 12 == 0x3B8


def test_single_actor_keeps_the_owner_frame_and_the_layout() -> None:
    data = _file({off: (16, 0x1F82C, 0x1F82C) for off in att.ATTACHMENT_PAIRS})
    out = att.single_actor(data)
    for off in att.ATTACHMENT_PAIRS:
        assert out[off : off + 12] == bytes.fromhex("0001f82c0000000d0000000d")
    changed = {i for i in range(len(data)) if data[i] != out[i]}
    assert all(any(o <= i < o + 12 for o in att.ATTACHMENT_PAIRS) for i in changed)


def test_single_actor_refuses_other_content() -> None:
    pairs = {off: (16, 0x1F82C, 0x1F82C) for off in att.ATTACHMENT_PAIRS}
    with pytest.raises(ValueError):
        att.single_actor(_file({**pairs, 0x32C: (16, 0x1E1B4, 0x1DFCC)}))  # stock arm pair
    with pytest.raises(ValueError):
        att.single_actor(_file({**pairs, 0x3AC: (2, 0, 0)}))


def test_nops_first_keeps_the_stock_cursor_positions() -> None:
    data = _file({off: (16, 0x1F82C, 0x1F82C) for off in att.ATTACHMENT_PAIRS})
    out = att.single_actor(data, nops_first=True)
    for off in att.ATTACHMENT_PAIRS:
        assert out[off : off + 12] == bytes.fromhex("0000000d0000000d0001f82c")


def test_transparent_companion_keeps_token_16_and_the_owner_frame() -> None:
    data = _file({off: (16, 0x1F82C, 0x1F82C) for off in att.ATTACHMENT_PAIRS})
    out = att.transparent_companion(data, 0x3D010)
    for off in att.ATTACHMENT_PAIRS:
        assert out[off : off + 12] == bytes.fromhex("000000100003d0100001f82c")


def test_companion_frame_layout() -> None:
    blob, shape = att.companion_frame(0x3D000)
    word = lambda o: int.from_bytes(blob[o - 0x3D000 : o - 0x3D000 + 4], "big")
    assert shape == 0x3D010 and word(shape + 4) == 0  # one-part shape
    desc = word(shape)
    assert word(desc - 4) == 0  # the zero word before every descriptor
    image, size = word(desc), word(desc + 4)
    assert size == (8 << 16) | 8 and word(image) == 0  # raw type 0
    assert blob[image - 0x3D000 + 4 :] == bytes(64) and len(blob) == image - 0x3D000 + 4 + 64
    with pytest.raises(ValueError):
        att.companion_frame(0x3D002)
