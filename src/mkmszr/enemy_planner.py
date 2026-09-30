"""Deterministic, fail-closed resource-family planner for ordinary enemies.

Pure planner only: no ROM bytes are modified here.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Literal

from .data.enemies import STAGE_ENEMIES, EnemySpawnSpec, StageEnemySpec
from .errors import PatchError

RNG_DOMAIN = b"MKMSZR:ENEMIES:RESOURCE-PLANNER:V1\0"
MAX_STAGE_ATTEMPTS = 1000
WATER_FIGHTER_PAYLOAD_CEILING = 0x34520

Evidence = Literal["native", "runtime-confirmed"]
Accounting = Literal["simultaneous", "native-paged"]


@dataclass(frozen=True)
class EnemyResource:
    key: str
    file_id: int
    size: int
    variant: str = "stock"


@dataclass(frozen=True)
class RosterProfile:
    key: str
    stage_key: str
    type_counts: tuple[tuple[int, int], ...]
    resource_keys: tuple[str, ...]
    evidence: Evidence
    accounting: Accounting = "simultaneous"
    fighter_budget_bytes: int | None = None
    proof_sha256: str | None = None
    assignment_groups: tuple[tuple[tuple[int, int], ...], ...] = ()
    phase_resource_groups: tuple[tuple[str, ...], ...] = ()
    phase_fixed_resource_groups: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class EnemyAssignment:
    type_word_rom: int
    stock_type: int
    generated_type: int
    special: bool


@dataclass(frozen=True)
class StageEnemyPlan:
    stage_key: str
    stage_id: int
    profile_key: str
    assignments: tuple[EnemyAssignment, ...]
    resource_keys: tuple[str, ...]
    fighter_payload_bytes: int | None
    fighter_budget_bytes: int | None
    evidence: Evidence
    attempts: int

    @property
    def randomized_types(self) -> tuple[int, ...]:
        return tuple(a.generated_type for a in self.assignments if not a.special)

    @property
    def fixed_special_types(self) -> tuple[int, ...]:
        return tuple(a.generated_type for a in self.assignments if a.special)


@dataclass(frozen=True)
class EnemyPlan:
    seed: str
    stages: tuple[StageEnemyPlan, ...]

    @property
    def assignments(self) -> tuple[EnemyAssignment, ...]:
        return tuple(a for stage in self.stages for a in stage.assignments)

    @property
    def total_records(self) -> int:
        return len(self.assignments)

    @property
    def randomizable_records(self) -> int:
        return sum(not a.special for a in self.assignments)


RESOURCES = {
    "20-stock": EnemyResource("20-stock",0x20,0x21160),
    "22-stock": EnemyResource("22-stock",0x22,0x255E0),
    "23-stock": EnemyResource("23-stock",0x23,0x1C7C0),
    "25-stock": EnemyResource("25-stock",0x25,0x2C210),
    "88-stock": EnemyResource("88-stock",0x88,0x225B0),
    "89-stock": EnemyResource("89-stock",0x89,0x22BF0),
    "8A-stock": EnemyResource("8A-stock",0x8A,0xB510),
    "8B-stock": EnemyResource("8B-stock",0x8B,0x14EE0),
    "8C-stock": EnemyResource("8C-stock",0x8C,0x1E160),
    "8D-stock": EnemyResource("8D-stock",0x8D,0xA370),
    "8E-stock": EnemyResource("8E-stock",0x8E,0x1FC10),
    "8F-stock": EnemyResource("8F-stock",0x8F,0x1B910),
    "90-stock": EnemyResource("90-stock",0x90,0x1C550),
    "91-stock": EnemyResource("91-stock",0x91,0x131A0),
    "8E-v04": EnemyResource("8E-v04",0x8E,0x1B0B8,"compact-v04"),
    "8F-v04": EnemyResource("8F-v04",0x8F,0x17A04,"compact-v04"),
    "8E-grunt3-v01": EnemyResource("8E-grunt3-v01",0x8E,0x1A148,"compact-grunt3-v01"),
    "90-grunt3-v01": EnemyResource("90-grunt3-v01",0x90,0x16AC0,"compact-grunt3-v01"),
}

PROFILES = (
    RosterProfile("temple-native","temple",((0x01,3),(0x02,5)),("89-stock","8A-stock"),"native"),
    RosterProfile("wind-native","wind",((0x03,17),),("8B-stock",),"native"),
    RosterProfile("water-native","water",((0x05,4),(0x1A,5)),("8C-stock","8D-stock"),"native",
                  fighter_budget_bytes=WATER_FIGHTER_PAYLOAD_CEILING),
    RosterProfile("water-hulk","water",((0x09,9),),("25-stock",),"runtime-confirmed",
                  fighter_budget_bytes=WATER_FIGHTER_PAYLOAD_CEILING,
                  proof_sha256="90e6ae1f97934d42ededeb0b861caa577bc86870f1df7b27be7dc49b5f6ed4c7"),
    RosterProfile("water-fast","water",((0x0A,9),),("20-stock","8D-stock"),"runtime-confirmed",
                  fighter_budget_bytes=WATER_FIGHTER_PAYLOAD_CEILING,
                  proof_sha256="e01e8ece94f642411afb9150b8a1ee9f74b7871945bcf029a469dcb9349c774f"),
    RosterProfile("water-pris15","water",((0x15,9),),("8E-v04","8F-v04"),"runtime-confirmed",
                  fighter_budget_bytes=WATER_FIGHTER_PAYLOAD_CEILING),
    RosterProfile("water-pris16","water",((0x16,9),),("8E-grunt3-v01","90-grunt3-v01"),
                  "runtime-confirmed",fighter_budget_bytes=WATER_FIGHTER_PAYLOAD_CEILING,
                  proof_sha256="665bf98d6c457853a30f66de00680e6de761d3773ce7108598a3050c856c7bed"),
    RosterProfile("water-pris17","water",((0x17,9),),("8E-stock","91-stock"),
                  "runtime-confirmed",fighter_budget_bytes=WATER_FIGHTER_PAYLOAD_CEILING,
                  proof_sha256="0548808d417bbd006d54a8bd028926e0c3dd490a6c32cfa821c82be134ea1b34"),
    RosterProfile("water-pris14-16","water",((0x14,5),(0x16,4)),
                  ("8E-grunt3-v01","90-grunt3-v01"),"runtime-confirmed",
                  fighter_budget_bytes=WATER_FIGHTER_PAYLOAD_CEILING,
                  proof_sha256="57d92254e24e644f9f26b6a43d3410562081e3f66daa9db613bc25a3ece95d50"),
    RosterProfile("earth-native","earth",((0x00,8),),("88-stock",),"native"),
    RosterProfile(
        "prison-native",
        "prison",
        ((0x0E,2),(0x14,3),(0x15,8),(0x16,6)),
        ("22-stock","8E-stock","8F-stock","90-stock"),
        "native",
        accounting="native-paged",
        assignment_groups=(
            ((0x15,6),),
            ((0x0E,2),),
            ((0x15,2),),
            ((0x14,3),(0x16,6)),
        ),
        phase_resource_groups=(
            ("8F-stock","8E-stock"),
            ("22-stock",),
            ("8F-stock","8E-stock"),
            ("90-stock","8E-stock"),
        ),
        phase_fixed_resource_groups=((),(),(),()),
    ),
    RosterProfile(
        "prison-fast-phase",
        "prison",
        ((0x0A,8),(0x0E,2),(0x14,3),(0x16,6)),
        ("20-stock","22-stock","8E-stock","8F-stock","90-stock"),
        "runtime-confirmed",
        accounting="native-paged",
        proof_sha256="90188adb7a66460f0662de18cbdf65d4b17d5ba839c405395613bd30012c5ebb",
        assignment_groups=(
            ((0x0A,6),),
            ((0x0E,2),),
            ((0x0A,2),),
            ((0x14,3),(0x16,6)),
        ),
        phase_resource_groups=(
            ("20-stock",),
            ("22-stock",),
            ("20-stock",),
            ("90-stock","8E-stock"),
        ),
        phase_fixed_resource_groups=(
            ("8F-stock",),
            (),
            ("8F-stock",),
            (),
        ),
    ),
    RosterProfile("fire-native","fire",((0x09,5),(0x0A,7)),("25-stock","20-stock"),"native"),
    RosterProfile("fire-monk2-proof","fire",((0x09,5),(0x01,7)),("25-stock","89-stock"),
                  "runtime-confirmed"),
    RosterProfile("bridge-native","bridge",((0x14,7),(0x17,6)),("8E-stock","91-stock"),
                  "native"),
    RosterProfile("fortress-native","fortress",((0x0E,6),(0x0F,7)),("22-stock","23-stock"),
                  "native"),
)

PROFILES_BY_STAGE = {
    stage.key: tuple(profile for profile in PROFILES if profile.stage_key == stage.key)
    for stage in STAGE_ENEMIES
}

PENDING_FOREIGN_TYPES = {
    0x00:"MONK1 foreign terminal selector-10 closure unresolved",
    0x02:"MONK3 two-file/terminal composition unresolved",
    0x03:"MONK4 external selector-10/cache closure unresolved",
    0x0E:"GRUNT1 foreign action/reaction closure unresolved",
    0x0F:"GRUNT2 foreign paired-resource/action closure unresolved",
}


def _digest(seed: str, stage_id: int, attempt: int, counter: int, label: bytes) -> bytes:
    return hashlib.sha256(
        RNG_DOMAIN + seed.encode() + b"\0" + bytes((stage_id,))
        + attempt.to_bytes(4,"big") + counter.to_bytes(4,"big") + label
    ).digest()


def profile_fighter_payload_bytes(profile: RosterProfile) -> int | None:
    if profile.accounting != "simultaneous":
        return None
    return sum(RESOURCES[key].size for key in dict.fromkeys(profile.resource_keys))


def profile_is_valid(stage: StageEnemySpec, profile: RosterProfile) -> bool:
    if profile.stage_key != stage.key:
        return False
    if sum(count for _type_id,count in profile.type_counts) != len(stage.randomizable_records):
        return False
    if {r.stock_type for r in stage.special_records} & {t for t,_count in profile.type_counts}:
        return False
    if any(key not in RESOURCES for key in profile.resource_keys):
        return False
    if profile.assignment_groups:
        grouped_counts: dict[int, int] = {}
        for group in profile.assignment_groups:
            for type_id, count in group:
                grouped_counts[type_id] = grouped_counts.get(type_id, 0) + count
        if tuple(sorted(grouped_counts.items())) != tuple(sorted(profile.type_counts)):
            return False
        if sum(sum(count for _type_id, count in group) for group in profile.assignment_groups) != len(stage.randomizable_records):
            return False
        if profile.phase_resource_groups and len(profile.phase_resource_groups) != len(profile.assignment_groups):
            return False
        if profile.phase_fixed_resource_groups and len(profile.phase_fixed_resource_groups) != len(profile.assignment_groups):
            return False
        phase_keys = {
            key
            for groups in (profile.phase_resource_groups, profile.phase_fixed_resource_groups)
            for group in groups
            for key in group
        }
        if any(key not in RESOURCES for key in phase_keys):
            return False
    payload = profile_fighter_payload_bytes(profile)
    return not (
        profile.fighter_budget_bytes is not None
        and (payload is None or payload > profile.fighter_budget_bytes)
    )


def _shuffle_counts(
    seed: str,
    stage: StageEnemySpec,
    attempt: int,
    counts: tuple[tuple[int, int], ...],
    label: bytes,
) -> tuple[int, ...]:
    values = [type_id for type_id, count in counts for _ in range(count)]
    for counter, index in enumerate(range(len(values) - 1, 0, -1)):
        swap = int.from_bytes(
            _digest(seed, stage.stage_id, attempt, counter, label)[:8],
            "big",
        ) % (index + 1)
        values[index], values[swap] = values[swap], values[index]
    return tuple(values)


def _shuffle(seed: str, stage: StageEnemySpec, profile: RosterProfile, attempt: int) -> tuple[int,...]:
    if not profile.assignment_groups:
        return _shuffle_counts(
            seed,
            stage,
            attempt,
            profile.type_counts,
            b"types\0" + profile.key.encode(),
        )

    values: list[int] = []
    for group_index, group in enumerate(profile.assignment_groups):
        values.extend(
            _shuffle_counts(
                seed,
                stage,
                attempt,
                group,
                b"types\0"
                + profile.key.encode()
                + b"\0group\0"
                + group_index.to_bytes(2, "big"),
            )
        )
    return tuple(values)


def _candidate_profile(seed: str, stage: StageEnemySpec, attempt: int) -> RosterProfile:
    profiles = PROFILES_BY_STAGE[stage.key]
    value = int.from_bytes(_digest(seed,stage.stage_id,attempt,0,b"profile")[:8],"big")
    return profiles[value % len(profiles)]


def _assignment(record: EnemySpawnSpec, generated_type: int) -> EnemyAssignment:
    return EnemyAssignment(record.type_word_rom,record.stock_type,generated_type,record.special)


def build_stage_enemy_plan(
    stage: StageEnemySpec,
    seed: str,
    *,
    allowed_profile_keys: frozenset[str] | None = None,
) -> StageEnemyPlan:
    for attempt in range(MAX_STAGE_ATTEMPTS):
        profile = _candidate_profile(seed,stage,attempt)
        if allowed_profile_keys is not None and profile.key not in allowed_profile_keys:
            continue
        if not profile_is_valid(stage,profile):
            continue
        generated = iter(_shuffle(seed,stage,profile,attempt))
        assignments = tuple(
            _assignment(record,record.stock_type if record.special else next(generated))
            for record in stage.records
        )
        return StageEnemyPlan(
            stage.key,stage.stage_id,profile.key,assignments,profile.resource_keys,
            profile_fighter_payload_bytes(profile),profile.fighter_budget_bytes,
            profile.evidence,attempt+1,
        )
    raise PatchError(
        f"{stage.title}: no evidence-safe enemy profile after {MAX_STAGE_ATTEMPTS} attempts"
    )


def build_enemy_plan(
    seed: str,
    *,
    allowed_profile_keys: frozenset[str] | None = None,
) -> EnemyPlan:
    return EnemyPlan(
        seed,
        tuple(
            build_stage_enemy_plan(
                stage,
                seed,
                allowed_profile_keys=allowed_profile_keys,
            )
            for stage in STAGE_ENEMIES
        ),
    )


def format_enemy_plan(plan: EnemyPlan) -> tuple[str,...]:
    lines = []
    for stage in plan.stages:
        payload = "native-paged" if stage.fighter_payload_bytes is None else f"0x{stage.fighter_payload_bytes:X}"
        budget = "native/proof" if stage.fighter_budget_bytes is None else f"0x{stage.fighter_budget_bytes:X}"
        roster = ",".join(f"{type_id:02X}" for type_id in stage.randomized_types)
        resources = "+".join(stage.resource_keys)
        lines.append(
            f"{stage.stage_key}: profile={stage.profile_key} roster=[{roster}] "
            f"resources={resources} fighter-payload={payload} budget={budget} "
            f"evidence={stage.evidence} attempts={stage.attempts}"
        )
    return tuple(lines)
