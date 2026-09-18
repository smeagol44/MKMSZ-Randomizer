"""User-facing patch configuration."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OutfitConfig:
    mode: str = "vanilla"
    hue_degrees: float | None = None
    rgb: tuple[int, int, int] | None = None


@dataclass(frozen=True)
class RandomizerConfig:
    seed: str | None = None
    outfit: OutfitConfig = field(default_factory=OutfitConfig)
