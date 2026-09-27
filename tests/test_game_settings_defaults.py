import pytest

from mkmszr.config import GameSettingsConfig, RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.inventory_boxes import (
    COMBOS_ASSIST_STATE_MASK,
    JUMP_BUTTON_STATE_MASK,
    RUN_AUTO_STATE_MASK,
    SPECIALS_MODERN_STATE_MASK,
    FourBoxInventoryPatch,
    initial_box_data,
)


def _inventory_patch(config: RandomizerConfig) -> FourBoxInventoryPatch:
    for patch in build_pipeline(config).patches:
        if isinstance(patch, FourBoxInventoryPatch):
            return patch
    raise AssertionError("FourBoxInventoryPatch missing from pipeline")


def test_game_settings_defaults_remain_vanilla_when_unselected() -> None:
    patch = _inventory_patch(RandomizerConfig())
    assert patch.initial_settings_state == 0
    assert int.from_bytes(initial_box_data()[160:164], "big") == 0


def test_selected_game_settings_seed_existing_durable_state_bits() -> None:
    config = RandomizerConfig(
        game_settings=GameSettingsConfig(
            attack_modern=True,
            specials_modern=True,
            jump_button=True,
            run_auto=True,
        )
    )
    patch = _inventory_patch(config)
    expected = (
        COMBOS_ASSIST_STATE_MASK
        | SPECIALS_MODERN_STATE_MASK
        | JUMP_BUTTON_STATE_MASK
        | RUN_AUTO_STATE_MASK
    )
    assert expected == 0x3C00
    assert patch.initial_settings_state == expected
    assert int.from_bytes(initial_box_data(expected)[160:164], "big") == expected


def test_jump_button_requires_both_modern_modes() -> None:
    with pytest.raises(
        ValueError,
        match="JUMP: BUTTON requires ATTACK: MODERN and SPECIALS: MODERN",
    ):
        GameSettingsConfig(jump_button=True)

    with pytest.raises(ValueError):
        GameSettingsConfig(attack_modern=True, jump_button=True)

    with pytest.raises(ValueError):
        GameSettingsConfig(specials_modern=True, jump_button=True)
