"""Guards and composition tests for Water's scripted boss checkpoint."""

import pytest

from mkmszr.config import RandomizerConfig
from mkmszr.errors import PatchError
from mkmszr.patcher import build_pipeline
from mkmszr.patches.base import PatchContext
from mkmszr.patches.water_scripted_checkpoint import (
    WATER_ABSOLUTE_SIX,
    WATER_SCRIPT_CONTEXT_EXPECTED,
    WATER_SCRIPT_CONTEXT_ROM,
    WATER_SCRIPTED_CHECKPOINT_ROM,
    WaterScriptedCheckpointPatch,
)
from mkmszr.rom import EXPECTED_SIZE, N64_Z64_MAGIC, RomImage


def _synthetic_stock_rom() -> RomImage:
    data = bytearray(EXPECTED_SIZE)
    data[:4] = N64_Z64_MAGIC.to_bytes(4, "big")
    data[
        WATER_SCRIPT_CONTEXT_ROM : WATER_SCRIPT_CONTEXT_ROM + len(WATER_SCRIPT_CONTEXT_EXPECTED)
    ] = WATER_SCRIPT_CONTEXT_EXPECTED
    return RomImage.from_bytes(bytes(data), require_clean=False)


def test_one_opcode_only_preserves_surrounding_water_script() -> None:
    rom = _synthetic_stock_rom()
    before = bytes(rom.data)
    WaterScriptedCheckpointPatch().apply(rom, PatchContext())
    assert rom.read_u32(WATER_SCRIPTED_CHECKPOINT_ROM) == WATER_ABSOLUTE_SIX
    assert bytes(rom.data[:WATER_SCRIPTED_CHECKPOINT_ROM]) == before[:WATER_SCRIPTED_CHECKPOINT_ROM]
    assert (
        bytes(rom.data[WATER_SCRIPTED_CHECKPOINT_ROM + 4 :])
        == before[WATER_SCRIPTED_CHECKPOINT_ROM + 4 :]
    )


@pytest.mark.parametrize("offset", [0, 0x14, 0x1C, 0x28])
def test_water_context_guard_rejects_modified_stock_script(offset: int) -> None:
    rom = _synthetic_stock_rom()
    target = WATER_SCRIPT_CONTEXT_ROM + offset
    rom.data[target] ^= 0x01
    before = bytes(rom.data)
    with pytest.raises(PatchError, match="guard failed"):
        WaterScriptedCheckpointPatch().apply(rom, PatchContext())
    assert bytes(rom.data) == before


def test_water_patch_is_always_in_shared_pipeline() -> None:
    for config in (
        RandomizerConfig(seed="WATER-DEFAULT"),
        RandomizerConfig(seed="WATER-DEBUG", debug_all_keys=True),
        RandomizerConfig(seed="WATER-POWER", powers_as_pickups=False),
        RandomizerConfig(seed="WATER-ENEMIES", enemy_randomization=True),
    ):
        types = [type(p) for p in build_pipeline(config).patches]
        assert types.count(WaterScriptedCheckpointPatch) == 1
