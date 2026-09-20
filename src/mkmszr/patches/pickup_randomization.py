"""Deterministic stage-local randomization of the 84 ordinary pickup records."""

from __future__ import annotations

import hashlib

from ..data.pickups import (
    COLLECTED_OFFSET,
    IDENTITY_OFFSET,
    STAGE_PICKUPS,
    TOTAL_ORDINARY_PICKUPS,
    StagePickupSpec,
)
from ..rom import RomImage
from .base import PatchContext

RNG_DOMAIN = b"MKMSZR:PICKUPS:STAGE-LOCAL:V1\0"
MAX_LAYOUT_ATTEMPTS = 1000


def _candidate_permutation(
    seed: str,
    stage: StagePickupSpec,
    attempt: int,
) -> tuple[int, ...]:
    """Stable Fisher-Yates permutation independent of Python's random module."""

    values = list(range(len(stage.records)))
    counter = 0
    seed_bytes = seed.encode("utf-8")

    for index in range(len(values) - 1, 0, -1):
        digest = hashlib.sha256(
            RNG_DOMAIN
            + seed_bytes
            + b"\0"
            + bytes((stage.stage_id,))
            + attempt.to_bytes(4, "big")
            + counter.to_bytes(4, "big")
        ).digest()
        swap_index = int.from_bytes(digest[:8], "big") % (index + 1)
        values[index], values[swap_index] = values[swap_index], values[index]
        counter += 1

    return tuple(values)


def layout_is_progression_safe(stage: StagePickupSpec, assignment: tuple[int, ...]) -> bool:
    """Return whether every ordinary location can be reached under known stage rules."""

    if len(assignment) != len(stage.records):
        return False

    inventory: set[str] = set()
    reached: set[int] = set()
    changed = True

    while changed:
        changed = False
        for destination, requirement in enumerate(stage.requirements):
            if destination in reached or not requirement.issubset(inventory):
                continue
            reached.add(destination)
            source = stage.records[assignment[destination]]
            if source.progression_token is not None:
                inventory.add(source.progression_token)
            changed = True

    return len(reached) == len(stage.records)


def build_stage_assignment(stage: StagePickupSpec, seed: str) -> tuple[tuple[int, ...], int]:
    """Build one deterministic, progression-safe assignment and return attempts used."""

    for attempt in range(MAX_LAYOUT_ATTEMPTS):
        assignment = _candidate_permutation(seed, stage, attempt)
        if layout_is_progression_safe(stage, assignment):
            return assignment, attempt + 1

    raise RuntimeError(
        f"{stage.title}: no progression-safe pickup layout after {MAX_LAYOUT_ATTEMPTS} attempts"
    )


class PickupRandomizationPatch:
    """Shuffle complete native item tuples within each stage.

    This deliberately does not move item identities across stage boundaries.
    The +0x24 resource selector is stage-local, so a global shuffle requires a
    production foreign-resource import planner. Scripted/special pickups such as
    the Temple Map remain outside the 84-record ordinary catalog.
    """

    name = "pickup-randomization"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        if not context.seed:
            return ("no seed supplied; ordinary pickup randomization skipped",)

        # Guard all source tuples before any writes. This makes the operation
        # all-or-nothing against the clean researched pickup catalog.
        for stage in STAGE_PICKUPS:
            for record in stage.records:
                rom.expect_bytes(record.rom_base + IDENTITY_OFFSET, record.identity)
                rom.expect_u32(record.rom_base + COLLECTED_OFFSET, 0)

        attempt_notes: list[str] = []
        for stage in STAGE_PICKUPS:
            assignment, attempts = build_stage_assignment(stage, context.seed)
            source_identities = tuple(record.identity for record in stage.records)

            for destination, source_index in enumerate(assignment):
                target = stage.records[destination]
                rom.write_bytes(
                    target.rom_base + IDENTITY_OFFSET,
                    source_identities[source_index],
                )

            attempt_notes.append(f"{stage.key}:{attempts}")

        return (
            f"{TOTAL_ORDINARY_PICKUPS} ordinary pickup locations processed across 8 stages",
            "mode=stage-local-v1; complete +0x10..+0x2B native item tuples shuffled",
            "known stage progression rules rejection-tested; Temple Map/special mechanisms excluded",
            "layout attempts " + ", ".join(attempt_notes),
        )
