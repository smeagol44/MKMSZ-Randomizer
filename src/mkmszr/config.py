"""User-facing patch configuration."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OutfitConfig:
    mode: str = "vanilla"
    hue_degrees: float | None = None
    rgb: tuple[int, int, int] | None = None


@dataclass(frozen=True)
class GameSettingsConfig:
    turn_lock: bool = False
    attack_modern: bool = False
    specials_modern: bool = False
    jump_button: bool = False
    run_auto: bool = False

    def __post_init__(self) -> None:
        if self.jump_button and not (self.attack_modern and self.specials_modern):
            raise ValueError(
                "JUMP: BUTTON requires ATTACK: MODERN and SPECIALS: MODERN"
            )


@dataclass(frozen=True)
class RandomizerConfig:
    seed: str | None = None
    outfit: OutfitConfig = field(default_factory=OutfitConfig)
    edition_name: str = "SUB-ZERO"
    game_settings: GameSettingsConfig = field(default_factory=GameSettingsConfig)
    shuffle_power_progression: bool = False
