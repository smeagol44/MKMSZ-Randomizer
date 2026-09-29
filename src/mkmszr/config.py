"""User-facing patch configuration."""

from dataclasses import dataclass, field
from typing import Literal


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
    powers_as_pickups: bool = True
    required_powers_mode: Literal["vanilla", "custom", "seed"] = "vanilla"
    custom_required_powers: int | None = None

    def __post_init__(self) -> None:
        if self.required_powers_mode not in ("vanilla", "custom", "seed"):
            raise ValueError("required powers mode must be vanilla, custom, or seed")
        if self.required_powers_mode == "custom":
            value = self.custom_required_powers
            if type(value) is not int or not 0 <= value <= 9:
                raise ValueError("custom required powers must be an integer from 0 to 9")
        elif self.custom_required_powers is not None:
            raise ValueError("custom required powers is only valid in custom mode")
