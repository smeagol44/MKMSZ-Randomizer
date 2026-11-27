"""Multi-track donor sounds (fighter_import.sound): WESS stream retargeting and hosting."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import sound

MKT = os.environ.get("MKMSZR_MKT_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")


def _track(stream: bytes, patch: int) -> bytes:
    return patch.to_bytes(4, "big") + bytes(12) + len(stream).to_bytes(4, "big") + stream


def test_retarget_rewrites_the_header_and_every_patch_change() -> None:
    # delta 0, patch 0x17; delta 0, patch 0x1A7; delta 2, note on 3C 7F; delta 0x8E, note off; end
    stream = bytes.fromhex("00071700" "0007a701" "02113c7f" "810e123c" "0022")
    out = sound.retarget(_track(stream, 0x1A7), 0x14E)
    assert out[:4] == (0x14E).to_bytes(4, "big")
    assert out[0x14:] == bytes.fromhex("00074e01" "00074e01" "02113c7f" "810e123c" "0022")
    assert out.count(bytes.fromhex("074e01")) == 2 and bytes.fromhex("07a701") not in out


def test_retarget_refuses_notes_on_another_patch_or_unknown_opcodes() -> None:
    two_patches = bytes.fromhex("00113c7f" "00073000" "00113c7f" "0022")
    with pytest.raises(ValueError, match="patches"):
        sound.retarget(_track(two_patches, 0x1A7), 1)
    with pytest.raises(ValueError, match="opcode"):
        sound.retarget(_track(bytes.fromhex("001400000000" "0022"), 0x1A7), 1)


@needs_mkt
def test_rayden_sound_5_has_two_retargetable_tracks() -> None:
    """MKT event 0x205 (Rayden's ft_sound(5), the Shocker's grab): two tracks, patches 0x1A7
    (three notes) and 0x1A8 (one note after a delay), 4 bytes of padding after them."""

    bank = sound.MktSoundBank(Path(MKT).read_bytes())  # type: ignore[arg-type]
    assert bank.fighter_event(24, 5) == 0x205
    tracks = bank.tracks(0x205)
    assert [int.from_bytes(t.track[:4], "big") for t in tracks] == [0x1A7, 0x1A8]
    assert [len(t.track) for t in tracks] == [0x3C, 0x30]
    with pytest.raises(ValueError, match="single"):
        bank.event(0x205)
    for t, patch in zip(tracks, (0x14E, 0x1E9), strict=True):
        out = sound.retarget(t.track, patch)
        assert out.count(bytes((sound.WESS_PATCH,)) + patch.to_bytes(2, "little")) == 2
