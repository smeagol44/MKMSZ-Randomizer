"""User-facing patch configuration."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OutfitConfig:
    mode: str = "vanilla"
    hue_degrees: float | None = None
    rgb: tuple[int, int, int] | None = None


@dataclass(frozen=True)
class GameSettingsConfig:
    attack_modern: bool = False
    specials_modern: bool = False
    jump_button: bool = False
    run_auto: bool = False


@dataclass(frozen=True)
class RandomizerConfig:
    seed: str | None = None
    outfit: OutfitConfig = field(default_factory=OutfitConfig)
    edition_name: str = "SUB-ZERO"
    game_settings: GameSettingsConfig = field(default_factory=GameSettingsConfig)
