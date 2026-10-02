from mkmszr.global_generation import (
    GLOBAL_LOCATIONS,
    TOTAL_POWER_UPGRADES,
    CompletionPolicy,
    candidate_permutation,
    completion_satisfied,
    find_accepted_candidate,
    progression_locations,
    required_power_target,
    solve_reachability,
)
from mkmszr.global_items import build_stock_logical_pool


def test_global_location_catalog_matches_all_84_records() -> None:
    assert len(GLOBAL_LOCATIONS) == 84
    assert [location.global_index for location in GLOBAL_LOCATIONS] == list(range(84))


def test_global_candidate_is_one_deterministic_84_item_permutation() -> None:
    first = candidate_permutation("GLOBAL-SEED", 0)
    second = candidate_permutation("GLOBAL-SEED", 0)
    retry = candidate_permutation("GLOBAL-SEED", 1)

    assert first == second
    assert first != retry
    assert sorted(first) == list(range(84))
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


def test_progression_selection_is_deterministic_on_accepted_layout() -> None:
    assignment = candidate_permutation("POWER-LAYOUT", 3)
    first = progression_locations("POWER-LAYOUT", assignment)
    second = progression_locations("POWER-LAYOUT", assignment)

    assert first == second
    assert len(first) == TOTAL_POWER_UPGRADES
    assert len(set(first)) == TOTAL_POWER_UPGRADES

    pool = build_stock_logical_pool()
    assert all(pool[assignment[index]].key == "herbs" for index in first)


def test_required_power_target_has_its_own_retry_independent_namespace() -> None:
    allowed = (3, 4, 5, 6, 7, 8, 9)
    target = required_power_target("REQ-POWERS", allowed)

    assert target in allowed
    assert target == required_power_target("REQ-POWERS", allowed)

    # Generating arbitrary layout retries cannot perturb the independent target.
    for attempt in range(25):
        candidate_permutation("REQ-POWERS", attempt)
    assert target == required_power_target("REQ-POWERS", allowed)


def test_stock_identity_layout_reaches_all_currently_modeled_locations() -> None:
    identity = tuple(range(84))
    result = solve_reachability(identity)

    assert result.all_locations_reachable
    assert result.power_upgrades == 0
    assert len(result.acquired_tokens) == 21
    assert result.passes >= 1


def test_solver_rejects_self_locked_required_token_location() -> None:
    # Start from stock identity, then swap Wind Circle into the location that
    # requires Wind Circle. This creates a direct fixed-point deadlock while
    # retaining a valid global permutation.
    assignment = list(range(84))

    wind_locations = [x for x in GLOBAL_LOCATIONS if x.stage_key == "wind"]
    wind_circle_destination = next(
        x.global_index
        for x in wind_locations
        if x.requirements == frozenset({"wind-circle"})
    )
    wind_circle_source = next(
        index
        for index, item in enumerate(build_stock_logical_pool())
        if item.key == "wind-circle"
    )

    current_source = assignment[wind_circle_destination]
    other_destination = assignment.index(wind_circle_source)
    assignment[wind_circle_destination] = wind_circle_source
    assignment[other_destination] = current_source

    result = solve_reachability(tuple(assignment))
    assert not result.all_locations_reachable
    assert wind_circle_destination not in result.reached_locations


def test_solver_counts_only_reachable_power_locations() -> None:
    assignment = tuple(range(84))
    power_locations = progression_locations("POWER-COUNT", assignment)

    result = solve_reachability(assignment, power_locations=power_locations)
    assert result.all_locations_reachable
    assert result.power_upgrades == 9


def test_completion_policy_is_explicit_not_hardcoded() -> None:
    assignment = tuple(range(84))
    powers = progression_locations("POLICY", assignment)
    result = solve_reachability(assignment, power_locations=powers)

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
