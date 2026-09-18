"""High-level patch orchestration shared by CLI and future frontends."""

from dataclasses import dataclass
from pathlib import Path

from .config import RandomizerConfig
from .patches import ArenaReservationPatch, SafeStageSelectorPatch, SubZeroPalettePatch
from .patches.base import PatchContext, PatchPipeline, PatchResult
from .rom import RomImage


@dataclass(frozen=True)
class BuildResult:
    data: bytes
    crc1: int
    crc2: int
    output_sha256: str
    changed_spans: tuple[tuple[int, int], ...]
    patches: tuple[PatchResult, ...]


def build_pipeline(config: RandomizerConfig) -> PatchPipeline:
    # Core native infrastructure is always installed in randomizer ROMs.
    patches = [SafeStageSelectorPatch(), ArenaReservationPatch()]
    if config.outfit.mode.lower() != "vanilla":
        patches.append(
            SubZeroPalettePatch(
                config.outfit.mode,
                hue_degrees=config.outfit.hue_degrees,
                rgb=config.outfit.rgb,
            )
        )
    return PatchPipeline(patches)


def patch_bytes(source: bytes, config: RandomizerConfig) -> BuildResult:
    rom = RomImage.from_bytes(source, require_clean=True)
    results = build_pipeline(config).apply(rom, PatchContext(seed=config.seed))
    crc1, crc2 = rom.update_header_crc()
    return BuildResult(
        data=rom.to_bytes(),
        crc1=crc1,
        crc2=crc2,
        output_sha256=rom.output_sha256,
        changed_spans=rom.changed_spans(),
        patches=results,
    )


def patch_file(source: Path, output: Path, config: RandomizerConfig) -> BuildResult:
    if source.resolve() == output.resolve():
        raise ValueError("output must be a separate file; the clean ROM is never modified in place")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output}")
    result = patch_bytes(source.read_bytes(), config)
    output.write_bytes(result.data)
    if output.read_bytes() != result.data:
        raise OSError("output re-read verification failed")
    return result
