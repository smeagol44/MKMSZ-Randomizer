import pytest

from mkmszr.errors import PatchError
from mkmszr.patches.base import PatchContext
from mkmszr.patches.key_checkpoint_proof import (
    KEY_CHECKPOINT_SPAWN_SITES,
    KeyCheckpointSuppressionProofPatch,
)
from mkmszr.rom import RomImage


def _proof_shape() -> RomImage:
    end = max(offset + len(expected) for offset, expected in KEY_CHECKPOINT_SPAWN_SITES)
    data = bytearray(end)
    for offset, expected in KEY_CHECKPOINT_SPAWN_SITES:
        data[offset : offset + len(expected)] = expected
    return RomImage(data=data, _original=bytes(data))


def test_checkpoint_proof_changes_only_three_jal_words() -> None:
    rom = _proof_shape()
    before = bytes(rom.data)

    notes = KeyCheckpointSuppressionProofPatch().apply(rom, PatchContext())

    assert notes[0].startswith("proof-only")
    for offset, expected in KEY_CHECKPOINT_SPAWN_SITES:
        assert rom.read_u32(offset) == 0
        assert rom.data[offset + 4 : offset + 8] == expected[4:8]

    changed = [
        (index, old, new)
        for index, (old, new) in enumerate(zip(before, rom.data))
        if old != new
    ]
    assert {index // 4 * 4 for index, _old, _new in changed} == {
        offset for offset, _expected in KEY_CHECKPOINT_SPAWN_SITES
    }


def test_checkpoint_proof_fails_closed_if_any_spawn_site_drifted() -> None:
    rom = _proof_shape()
    offset = KEY_CHECKPOINT_SPAWN_SITES[1][0]
    rom.data[offset] ^= 1

    with pytest.raises(PatchError, match="guard failed"):
        KeyCheckpointSuppressionProofPatch().apply(rom, PatchContext())
