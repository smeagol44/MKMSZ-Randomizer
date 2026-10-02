from mkmszr.global_generation import (
    GLOBAL_LOCATIONS,
    TEMPLE_SPECIAL_LOCATION_INDEX,
    TOTAL_GLOBAL_LOCATIONS,
    CompletionPolicy,
    candidate_permutation,
    completion_satisfied,
    find_accepted_candidate,
    required_power_target,
    solve_reachability,
)
from mkmszr.global_items import (
    TOTAL_GLOBAL_REWARDS,
    TOTAL_POWER_UPGRADES,
    build_global_logical_pool,
)


def test_global_location_catalog_is_84_ordinary_plus_temple_special() -> None:
    assert TOTAL_GLOBAL_LOCATIONS == 85
    assert len(GLOBAL_LOCATIONS) == 85
    assert [location.global_index for location in GLOBAL_LOCATIONS] == list(range(85))

    special = GLOBAL_LOCATIONS[TEMPLE_SPECIAL_LOCATION_INDEX]
    assert special.global_index == 84
    assert special.stage_id == 0
    assert special.stage_key == "temple"
    assert special.record_index is None
    assert special.kind == "temple-special"
    assert special.requirements == frozenset()


def test_global_reward_pool_is_85_and_excludes_map() -> None:
    pool = build_global_logical_pool(powers_as_pickups=False)

    assert TOTAL_GLOBAL_REWARDS == 85
    assert len(pool) == 85
    assert all(item.key != "map" for item in pool)
    assert sum(item.key == "power-upgrade" for item in pool) == 0


def test_powers_as_pickups_are_explicit_rewards_before_shuffle() -> None:
    pool = build_global_logical_pool(powers_as_pickups=True)

    assert len(pool) == 85
    assert sum(item.key == "power-upgrade" for item in pool) == TOTAL_POWER_UPGRADES == 9

    off_pool = build_global_logical_pool(powers_as_pickups=False)
    assert sum(item.key == "herbs" for item in off_pool) == (
        sum(item.key == "herbs" for item in pool) + 9
    )


def test_global_candidate_is_one_deterministic_85_reward_permutation() -> None:
    first = candidate_permutation("GLOBAL-SEED", 0)
    second = candidate_permutation("GLOBAL-SEED", 0)
    retry = candidate_permutation("GLOBAL-SEED", 1)

    assert first == second
    assert first != retry
    assert sorted(first) == list(range(85))
    assert first != candidate_permutation("OTHER-SEED", 0)


def test_retry_acceptance_is_reproducible_and_attempt_explicit() -> None:
    accepted_a = find_accepted_candidate(
        "RETRY-SEED",
        lambda candidate: candidate.attempt_index == 7,
        max_attempts=20,
    )
    accepted_b = find_accepted_candidate(
        "RETRY-SEED",
        lambda candidate: candidate.attempt_index == 7,
        max_attempts=20,
    )

    assert accepted_a.attempt_index == 7
    assert accepted_a == accepted_b
    assert accepted_a.assignment == candidate_permutation("RETRY-SEED", 7)


def test_required_power_target_has_retry_independent_namespace() -> None:
    allowed = tuple(range(10))
    target = required_power_target("REQ-POWERS", allowed)

    assert target in allowed
    assert target == required_power_target("REQ-POWERS", allowed)

    for attempt in range(25):
        candidate_permutation("REQ-POWERS", attempt)
    assert target == required_power_target("REQ-POWERS", allowed)


def test_identity_layout_reaches_all_85_currently_modeled_locations() -> None:
    identity = tuple(range(85))
    result = solve_reachability(identity, powers_as_pickups=False)

    assert result.all_locations_reachable
    assert result.power_upgrades == 0
    assert len(result.acquired_tokens) == 21
    assert TEMPLE_SPECIAL_LOCATION_INDEX in result.reached_locations
    assert result.passes >= 1


def test_solver_rejects_self_locked_required_token_location() -> None:
    assignment = list(range(85))

    wind_locations = [x for x in GLOBAL_LOCATIONS if x.stage_key == "wind"]
    locked_destination = next(
        x.global_index
        for x in wind_locations
        if x.requirements == frozenset({"wind-circle"})
    )

    pool = build_global_logical_pool(powers_as_pickups=False)
    wind_circle_source = next(
        index for index, item in enumerate(pool) if item.key == "wind-circle"
    )

    current_source = assignment[locked_destination]
    other_destination = assignment.index(wind_circle_source)
    assignment[locked_destination] = wind_circle_source
    assignment[other_destination] = current_source

    result = solve_reachability(tuple(assignment), powers_as_pickups=False)
    assert not result.all_locations_reachable
    assert locked_destination not in result.reached_locations


def test_solver_counts_power_upgrades_as_shuffled_rewards() -> None:
    identity = tuple(range(85))
    pool = build_global_logical_pool(powers_as_pickups=True)
    expected_power_locations = {
        destination
        for destination, source_index in enumerate(identity)
        if pool[source_index].key == "power-upgrade"
    }

    result = solve_reachability(identity, powers_as_pickups=True)

    assert result.all_locations_reachable
    assert result.power_upgrades == 9
    assert expected_power_locations.issubset(result.reached_locations)


def test_completion_policy_is_explicit_not_hardcoded() -> None:
    identity = tuple(range(85))
    result = solve_reachability(identity, powers_as_pickups=True)

    assert completion_satisfied(
        result,
        CompletionPolicy(required_powers=9, require_all_locations=True),
    )
    assert not completion_satisfied(
        result,
        CompletionPolicy(
            required_powers=9,
            required_tokens=frozenset({"not-a-real-token"}),
        ),
    )
