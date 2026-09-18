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
    reserve_runtime_memory: bool = True
    outfit: OutfitConfig = field(default_factory=OutfitConfig)
