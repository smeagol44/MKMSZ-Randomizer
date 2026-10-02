"""User-facing patch configuration."""

from dataclasses import dataclass, field
from typing import Literal

DifficultyMode = Literal["very_easy", "easy", "medium", "hard", "very_hard"]
CompletionMode = Literal["all_checks", "beatable"]


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
    enemy_randomization: bool = False
    powers_as_pickups: bool = True
    required_powers_mode: Literal["vanilla", "custom", "seed"] = "vanilla"
    custom_required_powers: int | None = None
    completion_mode: CompletionMode = "all_checks"
    difficulty: DifficultyMode = "very_hard"
    lives: int = 5
    continues: int = 3
    persist_hp: bool = True

    def __post_init__(self) -> None:
        if self.difficulty not in ("very_easy", "easy", "medium", "hard", "very_hard"):
            raise ValueError("difficulty must be very_easy, easy, medium, hard, or very_hard")
        if type(self.lives) is not int or not 1 <= self.lives <= 10:
            raise ValueError("lives must be an integer from 1 to 10")
        if type(self.continues) is not int or not 0 <= self.continues <= 5:
            raise ValueError("continues must be an integer from 0 to 5")
        if type(self.persist_hp) is not bool:
            raise ValueError("persist_hp must be a boolean")
        if self.required_powers_mode not in ("vanilla", "custom", "seed"):
            raise ValueError("required powers mode must be vanilla, custom, or seed")
        if self.completion_mode not in ("all_checks", "beatable"):
            raise ValueError("completion mode must be all_checks or beatable")
        if self.required_powers_mode == "custom":
            value = self.custom_required_powers
            if type(value) is not int or not 0 <= value <= 9:
                raise ValueError("custom required powers must be an integer from 0 to 9")
        elif self.custom_required_powers is not None:
            raise ValueError("custom required powers is only valid in custom mode")
