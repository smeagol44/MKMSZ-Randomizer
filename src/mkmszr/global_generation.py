"""Deterministic 85-check global generation and whole-run reachability.

The global model contains 84 ordinary pickup locations plus the scripted Temple
special check. Logical Map item 0x0D is excluded. The reward multiset is also
85 entries: the 84 ordinary stock rewards plus the accepted Temple-special
Herbs representative. When Powers-as-pickups is enabled, nine Herbs entries are
converted to explicit Power Upgrade rewards before the global Fisher-Yates
shuffle.

Physical emission remains a separate concern: ordinary destinations feed the
cross-stage materializer, while the Temple special check uses its dedicated
scripted-location seam.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Literal

from .data.pickups import STAGE_PICKUPS, TOTAL_ORDINARY_PICKUPS
from .global_items import (
    TOTAL_GLOBAL_REWARDS,
    TOTAL_POWER_UPGRADES,
    LogicalItem,
    build_global_logical_pool,
)
from .resource_materialization import (
    GlobalMaterializationPlan,
    MaterializationAssignment,
    StageResourcePlacement,
)

GLOBAL_RNG_DOMAIN = b"MKMSZR:PICKUPS:GLOBAL:V2\0"
REQUIRED_POWERS_RNG_DOMAIN = b"MKMSZR:REQUIRED-POWERS:V1\0"
TEMPLE_SPECIAL_LOCATION_INDEX = TOTAL_ORDINARY_PICKUPS
TOTAL_GLOBAL_LOCATIONS = TOTAL_ORDINARY_PICKUPS + 1

LocationKind = Literal["ordinary", "temple-special"]


@dataclass(frozen=True)
class GlobalLocation:
    """One stable destination in the 85-check global run graph."""

    global_index: int
    stage_id: int
    stage_key: str
    record_index: int | None
    requirements: frozenset[str]
    kind: LocationKind = "ordinary"


@dataclass(frozen=True)
class GlobalCandidate:
    """One deterministic 85-reward permutation for an explicit retry attempt."""

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
        return len(self.reached_locations) == TOTAL_GLOBAL_LOCATIONS


@dataclass(frozen=True)
class CompletionPolicy:
    """Explicit caller-owned completion rule.

    The solver does not invent the final 1.0 completion predicate. Required
    tokens, all-check reachability, and required Power Upgrades remain product
    policy supplied by the caller.
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
    """Build the stable 84 ordinary + 1 Temple-special destination catalog."""

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
            f"ordinary location catalog drifted: {len(result)} != "
            f"{TOTAL_ORDINARY_PICKUPS}"
        )

    # The scripted Temple Map location is an explicit randomizer check. Current
    # evidence does not assign it a key-item prerequisite; its elevator/exit
    # progression remains physical-location semantics owned by the Temple seam.
    result.append(
        GlobalLocation(
            global_index=TEMPLE_SPECIAL_LOCATION_INDEX,
            stage_id=0,
            stage_key="temple",
            record_index=None,
            requirements=frozenset(),
            kind="temple-special",
        )
    )

    if len(result) != TOTAL_GLOBAL_LOCATIONS:
        raise AssertionError(
            f"global location catalog drifted: {len(result)} != "
            f"{TOTAL_GLOBAL_LOCATIONS}"
        )
    return tuple(result)


GLOBAL_LOCATIONS = build_global_locations()

ALL_PROGRESSION_TOKENS = frozenset(
    item.progression_token
    for item in build_global_logical_pool(powers_as_pickups=False)
    if item.progression_token is not None
)
if len(ALL_PROGRESSION_TOKENS) != 21:
    raise AssertionError(
        f"progression-token catalog drifted: {len(ALL_PROGRESSION_TOKENS)} != 21"
    )


def build_completion_policy(mode: str, required_powers: int) -> CompletionPolicy:
    """Resolve the user-facing seed acceptance rule."""

    if mode == "all_85":
        return CompletionPolicy(
            required_powers=required_powers,
            require_all_locations=True,
        )
    if mode == "game_beatable":
        return CompletionPolicy(
            required_powers=required_powers,
            required_tokens=ALL_PROGRESSION_TOKENS,
            require_all_locations=False,
        )
    raise ValueError("completion mode must be all_85 or game_beatable")


def _validate_attempt_index(attempt_index: int) -> None:
    if not 0 <= attempt_index <= 0xFFFFFFFF:
        raise ValueError("attempt_index must fit unsigned 32-bit")


def _validate_assignment(assignment: tuple[int, ...]) -> None:
    if len(assignment) != TOTAL_GLOBAL_LOCATIONS:
        raise ValueError(
            f"global assignment must contain {TOTAL_GLOBAL_LOCATIONS} sources"
        )
    if set(assignment) != set(range(TOTAL_GLOBAL_REWARDS)):
        raise ValueError(
            f"global assignment must be a permutation of all "
            f"{TOTAL_GLOBAL_REWARDS} rewards"
        )


def candidate_permutation(seed: str, attempt_index: int) -> tuple[int, ...]:
    """Stable 85-entry Fisher-Yates permutation for one explicit attempt."""

    _validate_attempt_index(attempt_index)
    values = list(range(TOTAL_GLOBAL_REWARDS))
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
    """Return the first accepted candidate under an explicit caller ceiling."""

    if max_attempts <= 0:
        raise ValueError("max_attempts must be positive")

    for candidate in iter_global_candidates(seed):
        if candidate.attempt_index >= max_attempts:
            break
        if validator(candidate):
            return candidate

    raise ValueError(f"no accepted global candidate after {max_attempts} attempts")


def required_power_target(seed: str, allowed_counts: Sequence[int]) -> int:
    """Choose the seed-specific required-Power target in an isolated namespace."""

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
    powers_as_pickups: bool,
) -> ReachabilityResult:
    """Collect every currently reachable check until reaching a fixed point."""

    _validate_assignment(assignment)
    pool = build_global_logical_pool(powers_as_pickups=powers_as_pickups)

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
            item: LogicalItem = pool[assignment[destination]]
            if item.key == "power-upgrade":
                power_count += 1
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
    return not (
        policy.require_all_locations and not result.all_locations_reachable
    )


def validate_candidate(
    candidate: GlobalCandidate,
    *,
    powers_as_pickups: bool,
    policy: CompletionPolicy,
) -> bool:
    """Evaluate one deterministic candidate against the supplied policy."""

    return completion_satisfied(
        solve_reachability(
            candidate.assignment,
            powers_as_pickups=powers_as_pickups,
        ),
        policy,
    )



@dataclass(frozen=True)
class GlobalRunPlan:
    """Accepted logical run split into ordinary and Temple-special destinations."""

    candidate: GlobalCandidate
    rewards: tuple[LogicalItem, ...]
    ordinary_assignments: tuple[tuple[int, int, str], ...]
    temple_special_item_key: str
    power_locations: frozenset[int]


def build_global_run_plan(
    seed: str,
    *,
    powers_as_pickups: bool,
    policy: CompletionPolicy,
    max_attempts: int,
) -> GlobalRunPlan:
    """Generate the first deterministic solver-accepted 85-check logical run.

    Physical resource placement is deliberately not chosen here. The returned
    ordinary assignments feed GlobalMaterializationPlan once the caller supplies
    explicitly owned stage-resource backing. The Temple-special reward feeds its
    dedicated scripted-location materializer seam.
    """

    rewards = build_global_logical_pool(powers_as_pickups=powers_as_pickups)

    candidate = find_accepted_candidate(
        seed,
        lambda item: validate_candidate(
            item,
            powers_as_pickups=powers_as_pickups,
            policy=policy,
        ),
        max_attempts=max_attempts,
    )

    ordinary: list[tuple[int, int, str]] = []
    power_locations: set[int] = set()
    for location in GLOBAL_LOCATIONS:
        reward = rewards[candidate.assignment[location.global_index]]
        if reward.key == "power-upgrade":
            power_locations.add(location.global_index)
        if location.kind == "ordinary":
            assert location.record_index is not None
            ordinary.append((location.stage_id, location.record_index, reward.key))

    temple_reward = rewards[candidate.assignment[TEMPLE_SPECIAL_LOCATION_INDEX]]
    if len(ordinary) != TOTAL_ORDINARY_PICKUPS:
        raise AssertionError("global run plan lost an ordinary destination")

    return GlobalRunPlan(
        candidate=candidate,
        rewards=rewards,
        ordinary_assignments=tuple(ordinary),
        temple_special_item_key=temple_reward.key,
        power_locations=frozenset(power_locations),
    )



def materialization_plan_from_run(
    run: GlobalRunPlan,
    placements: Iterable[StageResourcePlacement],
) -> GlobalMaterializationPlan:
    """Convert one accepted logical run into the physical materializer schema.

    Placement ownership remains explicit and caller-supplied. This function
    performs no free-space discovery or allocation inference.
    """

    assignments = tuple(
        MaterializationAssignment(stage_id, record_index, item_key)
        for stage_id, record_index, item_key in run.ordinary_assignments
    )
    return GlobalMaterializationPlan(
        assignments=assignments,
        placements=tuple(placements),
        temple_special_item_key=run.temple_special_item_key,
    )
