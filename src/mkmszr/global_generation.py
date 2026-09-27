"""Deterministic global pickup generation and whole-run reachability primitives.

This module is intentionally pipeline-disconnected while cross-stage physical
materialization remains behind its production/runtime gate.  It owns only the
logical 84-location permutation, explicit retry sequencing, isolated
progression/required-Power RNG namespaces, and fixed-point reachability over the
current researched location requirements.

The final 1.0 completion predicate and allowed required-Power range are product
policy and are deliberately supplied by callers rather than invented here.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .data.pickups import STAGE_PICKUPS, TOTAL_ORDINARY_PICKUPS
from .global_items import LogicalItem, build_stock_logical_pool

GLOBAL_RNG_DOMAIN = b"MKMSZR:PICKUPS:GLOBAL:V1\0"
PROGRESSION_RNG_DOMAIN = b"MKMSZR:PROGRESSION:HERBS:V1\0"
REQUIRED_POWERS_RNG_DOMAIN = b"MKMSZR:REQUIRED-POWERS:V1\0"
TOTAL_POWER_UPGRADES = 9


@dataclass(frozen=True)
class GlobalLocation:
    """One stable destination in the flattened 84-location run graph."""

    global_index: int
    stage_id: int
    stage_key: str
    record_index: int
    requirements: frozenset[str]


@dataclass(frozen=True)
class GlobalCandidate:
    """One deterministic candidate permutation for an explicit attempt index."""

    attempt_index: int
    assignment: tuple[int, ...]


@dataclass(frozen=True)
class ReachabilityResult:
    """Fixed-point result for one global logical assignment."""

    reached_locations: frozenset[int]
    acquired_tokens: frozenset[str]
    power_upgrades: int
    passes: int

    @property
    def all_locations_reachable(self) -> bool:
        return len(self.reached_locations) == TOTAL_ORDINARY_PICKUPS


@dataclass(frozen=True)
class CompletionPolicy:
    """Caller-supplied completion rule.

    This is an evaluation container, not the final 1.0 policy.  The Roadmap
    still owns the decision about the required token set, whether all checks
    must be reachable, and which required-Power counts are allowed.
    """

    required_powers: int
    required_tokens: frozenset[str] = frozenset()
    require_all_locations: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.required_powers <= TOTAL_POWER_UPGRADES:
            raise ValueError(
                f"required_powers must be 0..{TOTAL_POWER_UPGRADES}, "
                f"got {self.required_powers}"
            )


def build_global_locations() -> tuple[GlobalLocation, ...]:
    result: list[GlobalLocation] = []
    for stage in STAGE_PICKUPS:
        for record_index, requirements in enumerate(stage.requirements):
            result.append(
                GlobalLocation(
                    global_index=len(result),
                    stage_id=stage.stage_id,
                    stage_key=stage.key,
                    record_index=record_index,
                    requirements=requirements,
                )
            )
    if len(result) != TOTAL_ORDINARY_PICKUPS:
        raise AssertionError(
            f"global location catalog drifted: {len(result)} != "
            f"{TOTAL_ORDINARY_PICKUPS}"
        )
    return tuple(result)


GLOBAL_LOCATIONS = build_global_locations()


def _validate_attempt_index(attempt_index: int) -> None:
    if not 0 <= attempt_index <= 0xFFFFFFFF:
        raise ValueError("attempt_index must fit unsigned 32-bit")


def _validate_assignment(assignment: tuple[int, ...]) -> None:
    if len(assignment) != TOTAL_ORDINARY_PICKUPS:
        raise ValueError(
            f"global assignment must contain {TOTAL_ORDINARY_PICKUPS} sources"
        )
    if set(assignment) != set(range(TOTAL_ORDINARY_PICKUPS)):
        raise ValueError("global assignment must be a permutation of all source items")


def candidate_permutation(seed: str, attempt_index: int) -> tuple[int, ...]:
    """Stable global Fisher-Yates permutation for one explicit attempt."""

    _validate_attempt_index(attempt_index)
    values = list(range(TOTAL_ORDINARY_PICKUPS))
    seed_bytes = seed.encode("utf-8")

    for counter, index in enumerate(range(len(values) - 1, 0, -1)):
        digest = hashlib.sha256(
            GLOBAL_RNG_DOMAIN
            + seed_bytes
            + b"\0"
            + attempt_index.to_bytes(4, "big")
            + counter.to_bytes(4, "big")
        ).digest()
        swap_index = int.from_bytes(digest[:8], "big") % (index + 1)
        values[index], values[swap_index] = values[swap_index], values[index]

    return tuple(values)


def iter_global_candidates(
    seed: str,
    *,
    start_attempt: int = 0,
) -> Iterable[GlobalCandidate]:
    """Yield deterministic candidates without imposing a product retry ceiling."""

    _validate_attempt_index(start_attempt)
    attempt_index = start_attempt
    while True:
        yield GlobalCandidate(
            attempt_index=attempt_index,
            assignment=candidate_permutation(seed, attempt_index),
        )
        if attempt_index == 0xFFFFFFFF:
            return
        attempt_index += 1


def find_accepted_candidate(
    seed: str,
    validator: Callable[[GlobalCandidate], bool],
    *,
    max_attempts: int,
) -> GlobalCandidate:
    """Return the first accepted candidate under an explicit caller ceiling.

    1.0 has no finalized retry ceiling yet, so callers/tests must state one
    explicitly instead of inheriting the stage-local 1000-attempt value.
    """

    if max_attempts <= 0:
        raise ValueError("max_attempts must be positive")

    for candidate in iter_global_candidates(seed):
        if candidate.attempt_index >= max_attempts:
            break
        if validator(candidate):
            return candidate

    raise ValueError(f"no accepted global candidate after {max_attempts} attempts")


def progression_locations(
    seed: str,
    assignment: tuple[int, ...],
    *,
    count: int = TOTAL_POWER_UPGRADES,
) -> tuple[int, ...]:
    """Select generated-Herbs destinations for Power Upgrades deterministically.

    Selection happens after the logical layout exists.  The RNG sequence has no
    attempt index, so rejected global candidates cannot perturb the progression
    namespace.  The accepted layout still determines which destinations are
    Herbs, matching the established production progression model.
    """

    _validate_assignment(assignment)
    if not 0 <= count <= TOTAL_POWER_UPGRADES:
        raise ValueError(f"progression count must be 0..{TOTAL_POWER_UPGRADES}")

    pool = build_stock_logical_pool()
    candidates = [
        destination
        for destination, source_index in enumerate(assignment)
        if pool[source_index].key == "herbs"
    ]
    if len(candidates) < count:
        raise ValueError(
            f"only {len(candidates)} generated Herbs locations; need {count}"
        )

    seed_bytes = seed.encode("utf-8")
    for counter, index in enumerate(range(len(candidates) - 1, 0, -1)):
        digest = hashlib.sha256(
            PROGRESSION_RNG_DOMAIN
            + seed_bytes
            + b"\0"
            + counter.to_bytes(4, "big")
        ).digest()
        swap_index = int.from_bytes(digest[:8], "big") % (index + 1)
        candidates[index], candidates[swap_index] = (
            candidates[swap_index],
            candidates[index],
        )

    return tuple(candidates[:count])


def required_power_target(seed: str, allowed_counts: Sequence[int]) -> int:
    """Choose the seed-specific required-Power target from caller-approved values."""

    allowed = tuple(allowed_counts)
    if not allowed:
        raise ValueError("allowed_counts must not be empty")
    if len(set(allowed)) != len(allowed):
        raise ValueError("allowed_counts must not contain duplicates")
    if any(not 0 <= value <= TOTAL_POWER_UPGRADES for value in allowed):
        raise ValueError(
            f"allowed required-Power counts must be 0..{TOTAL_POWER_UPGRADES}"
        )

    digest = hashlib.sha256(
        REQUIRED_POWERS_RNG_DOMAIN + seed.encode("utf-8") + b"\0"
    ).digest()
    return allowed[int.from_bytes(digest[:8], "big") % len(allowed)]


def solve_reachability(
    assignment: tuple[int, ...],
    *,
    power_locations: Iterable[int] = (),
) -> ReachabilityResult:
    """Collect every currently reachable check until the graph reaches a fixed point."""

    _validate_assignment(assignment)
    pool = build_stock_logical_pool()
    powers = frozenset(power_locations)

    if any(not 0 <= index < TOTAL_ORDINARY_PICKUPS for index in powers):
        raise ValueError("power location outside the 84-location catalog")
    for destination in powers:
        source_item = pool[assignment[destination]]
        if source_item.key != "herbs":
            raise ValueError(
                f"power location {destination} is not generated Herbs "
                f"(got {source_item.key})"
            )

    reached: set[int] = set()
    tokens: set[str] = set()
    power_count = 0
    passes = 0

    while True:
        newly_reached: list[int] = []
        for location in GLOBAL_LOCATIONS:
            if location.global_index in reached:
                continue
            if location.requirements.issubset(tokens):
                newly_reached.append(location.global_index)

        if not newly_reached:
            break

        passes += 1
        for destination in newly_reached:
            reached.add(destination)
            if destination in powers:
                power_count += 1
                continue

            item: LogicalItem = pool[assignment[destination]]
            if item.progression_token is not None:
                tokens.add(item.progression_token)

    return ReachabilityResult(
        reached_locations=frozenset(reached),
        acquired_tokens=frozenset(tokens),
        power_upgrades=power_count,
        passes=passes,
    )


def completion_satisfied(
    result: ReachabilityResult,
    policy: CompletionPolicy,
) -> bool:
    """Evaluate one explicit caller-supplied completion policy."""

    if result.power_upgrades < policy.required_powers:
        return False
    if not policy.required_tokens.issubset(result.acquired_tokens):
        return False
    if policy.require_all_locations and not result.all_locations_reachable:
        return False
    return True
