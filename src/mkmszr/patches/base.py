"""Patch protocol and pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..rom import RomImage, _changed_spans


@dataclass(frozen=True)
class PatchContext:
    seed: str | None = None


@dataclass(frozen=True)
class PatchResult:
    name: str
    changed_spans: tuple[tuple[int, int], ...]
    notes: tuple[str, ...] = ()


class Patch(Protocol):
    name: str

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...] | None:
        ...


class PatchPipeline:
    def __init__(self, patches: list[Patch] | tuple[Patch, ...]):
        self.patches = tuple(patches)

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[PatchResult, ...]:
        results: list[PatchResult] = []
        for patch in self.patches:
            before = bytes(rom.data)
            notes = patch.apply(rom, context) or ()
            results.append(
                PatchResult(
                    name=patch.name,
                    changed_spans=_changed_spans(before, rom.data),
                    notes=tuple(notes),
                )
            )
        return tuple(results)
