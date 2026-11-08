import pytest

from mkmszr.config import RandomizerConfig
from mkmszr.errors import PatchError
from mkmszr.patches.base import PatchContext
from mkmszr.patches.required_powers import (
    FORTRESS_FILE_END,
    FORTRESS_FILE_ENTRY_ROM,
    FORTRESS_FILE_START,
    FORTRESS_GATE_ROM,
    FORTRESS_GATE_STOCK,
    RequiredPowersPatch,
    resolve_required_powers,
)
from mkmszr.patches.xp_progression import XP_THRESHOLDS
from mkmszr.rom import RomImage


def _stock_fortress_shape() -> RomImage:
    data = bytearray(FORTRESS_FILE_END)
    for index, value in enumerate((FORTRESS_FILE_START, FORTRESS_FILE_END, 0)):
        offset = FORTRESS_FILE_ENTRY_ROM + index * 4
        data[offset:offset + 4] = value.to_bytes(4, "big")
    data[FORTRESS_GATE_ROM:FORTRESS_GATE_ROM + 4] = FORTRESS_GATE_STOCK.to_bytes(4, "big")
    return RomImage(data=data, _original=bytes(data))


@pytest.mark.parametrize("count", (0, 1, 2, 8, 9))
def test_custom_requirement_uses_native_tier_threshold(count: int) -> None:
    rom = _stock_fortress_shape()
    threshold = XP_THRESHOLDS[count - 1] if count else 0
    RequiredPowersPatch("custom", count).apply(rom, PatchContext(seed="CHECK"))
    assert rom.read_u32(FORTRESS_GATE_ROM) == 0x28630000 | threshold


def test_stock_requirement_and_seed_domain() -> None:
    assert resolve_required_powers("vanilla", None, None) == (None, 5100)
    first = resolve_required_powers("seed", None, "CHECK")
    assert first == resolve_required_powers("seed", None, "CHECK")
    assert 0 <= first[0] <= 9
    assert first[1] == (XP_THRESHOLDS[first[0] - 1] if first[0] else 0)
    assert len({resolve_required_powers("seed", None, f"CHECK-{i}")[0] for i in range(50)}) == 10
    with pytest.raises(PatchError, match="needs a seed"):
        resolve_required_powers("seed", None, None)


def test_fortress_gate_and_overlay_owner_are_guarded() -> None:
    rom = _stock_fortress_shape()
    rom.data[FORTRESS_GATE_ROM + 3] ^= 1
    with pytest.raises(PatchError, match="guard failed"):
        RequiredPowersPatch("custom", 5).apply(rom, PatchContext(seed="CHECK"))

    rom = _stock_fortress_shape()
    rom.data[FORTRESS_FILE_ENTRY_ROM] ^= 1
    with pytest.raises(PatchError, match="guard failed"):
        RequiredPowersPatch("seed").apply(rom, PatchContext(seed="CHECK"))


@pytest.mark.parametrize("value", (-1, 10, True, 1.5, None))
def test_custom_count_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValueError, match="integer from 0 to 9"):
        RandomizerConfig(required_powers_mode="custom", custom_required_powers=value)


def test_custom_count_is_rejected_in_other_modes() -> None:
    with pytest.raises(ValueError, match="only valid in custom mode"):
        RandomizerConfig(required_powers_mode="seed", custom_required_powers=3)
