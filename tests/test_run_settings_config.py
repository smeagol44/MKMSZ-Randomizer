import pytest

from mkmszr.config import RandomizerConfig


def test_run_settings_defaults_match_web_product_defaults() -> None:
    config = RandomizerConfig()
    assert config.difficulty == "very_hard"
    assert config.lives == 5
    assert config.continues == 3
    assert config.persist_hp is True


@pytest.mark.parametrize("lives", [0, 11])
def test_lives_validation(lives: int) -> None:
    with pytest.raises(ValueError, match="lives"):
        RandomizerConfig(lives=lives)


@pytest.mark.parametrize("continues", [-1, 6])
def test_continues_validation(continues: int) -> None:
    with pytest.raises(ValueError, match="continues"):
        RandomizerConfig(continues=continues)


def test_difficulty_validation() -> None:
    with pytest.raises(ValueError, match="difficulty"):
        RandomizerConfig(difficulty="impossible")  # type: ignore[arg-type]
