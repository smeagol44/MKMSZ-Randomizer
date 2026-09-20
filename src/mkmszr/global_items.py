"""Logical item model for the future global MKMSZR pickup pool.

This module deliberately separates *what a pickup awards* from *what the world
actor looks like*.  The latter is destination-stage data in the first 1.0
materialization strategy, matching the legacy Lua's logical-reward semantics
without requiring a foreign resource import for every cross-stage placement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .data.pickups import IDENTITY_SIZE, STAGE_PICKUPS, PickupSpec
from .mips import addiu, addu, jal, jump, sw, words_blob

AwardKind = Literal["inventory", "native-effect", "power-upgrade"]


@dataclass(frozen=True)
class LogicalItem:
    key: str
    display_name: str
    award_kind: AwardKind
    source_stage_id: int
    source_record_index: int
    inventory_id: int | None = None
    native_callback: int | None = None
    progression_token: str | None = None
    origin_stage_id: int | None = None


TOKEN_ITEMS: dict[str, tuple[str, int, int]] = {
    "wind-circle": ("Wind Icon Circle", 0x0E, 1),
    "wind-three-bars": ("Wind Icon 3 Bars", 0x0F, 1),
    "wind-triangle": ("Wind Icon Triangle", 0x10, 1),
    "earth-square": ("Earth Icon Square", 0x11, 3),
    "earth-four-square": ("Earth Icon 4 Squares", 0x12, 3),
    "earth-triangle": ("Earth Icon Triangle", 0x13, 3),
    "water-three-bars": ("Water Icon 3 Bars", 0x14, 2),
    "water-triangle": ("Water Icon Triangle", 0x15, 2),
    "water-moon": ("Water Icon Moon", 0x16, 2),
    "fire-triangle-down": ("Fire Icon Triangle Down", 0x17, 5),
    "fire-two-bars": ("Fire Icon 2 Bars", 0x18, 5),
    "fire-triangle-up": ("Fire Icon Triangle Up", 0x19, 5),
    "prison-l1": ("Prison Level 1 Key", 0x1A, 4),
    "prison-l2": ("Prison Level 2 Key", 0x1B, 4),
    "prison-l3": ("Prison Level 3 Key", 0x1C, 4),
    "bridge-omega": ("Bridge Icon Omega", 0x1D, 8),
    "bridge-rings": ("Bridge Icon Rings", 0x1E, 8),
    "bridge-arrow": ("Bridge Icon Arrow", 0x1F, 8),
    "crystal-jataaka": ("Crystal (Jataaka)", 0x20, 9),
    "crystal-kia": ("Crystal (Kia)", 0x21, 9),
    "crystal-sareena": ("Crystal (Sareena)", 0x22, 9),
}

# Global callbacks whose behavior is not derived from the current stage.
FIXED_CALLBACK_ITEMS: dict[int, tuple[str, str, AwardKind, int | None]] = {
    0x800388FC: ("potion", "Potion", "inventory", 0x01),
    0x8003898C: ("formula", "Formula", "inventory", 0x02),
    0x8003895C: ("eye", "Eye", "inventory", 0x03),
    0x800389BC: ("herbs", "Herbs", "inventory", 0x04),
    0x800389EC: ("health-urn", "Urn (Vitality)", "inventory", 0x05),
    0x8003892C: ("shield", "Shield", "inventory", 0x06),
    0x80038A1C: ("extra-life", "Urn (Extra Life)", "native-effect", None),
    0x80038A58: ("mana", "Mana", "native-effect", None),
    # Strength must retain its native callback because it does more than insert ID 0x0B.
    0x80038A90: ("strength-urn", "Urn (Strength)", "native-effect", None),
}


def _words(identity: bytes) -> tuple[int, ...]:
    return tuple(int.from_bytes(identity[i : i + 4], "big") for i in range(0, 0x1C, 4))


def logical_item_from_record(
    stage_id: int,
    record_index: int,
    record: PickupSpec,
) -> LogicalItem:
    if record.progression_token is not None:
        name, item_id, origin_stage = TOKEN_ITEMS[record.progression_token]
        return LogicalItem(
            key=record.progression_token,
            display_name=name,
            award_kind="inventory",
            source_stage_id=stage_id,
            source_record_index=record_index,
            inventory_id=item_id,
            progression_token=record.progression_token,
            origin_stage_id=origin_stage,
        )

    callback = _words(record.identity)[2]
    try:
        key, name, award_kind, inventory_id = FIXED_CALLBACK_ITEMS[callback]
    except KeyError as exc:
        raise ValueError(
            f"unclassified pickup callback 0x{callback:08X} "
            f"at stage {stage_id} record {record_index + 1}"
        ) from exc

    return LogicalItem(
        key=key,
        display_name=name,
        award_kind=award_kind,
        source_stage_id=stage_id,
        source_record_index=record_index,
        inventory_id=inventory_id,
        native_callback=callback,
    )


def build_stock_logical_pool() -> tuple[LogicalItem, ...]:
    """Return the 84 ordinary stock rewards as logical items.

    The Temple Map is intentionally absent because it is not an ordinary record.
    Power Upgrades are also absent here; the global generator will deterministically
    replace nine Herbs logical rewards before shuffling.
    """

    result: list[LogicalItem] = []
    for stage in STAGE_PICKUPS:
        for record_index, record in enumerate(stage.records):
            result.append(logical_item_from_record(stage.stage_id, record_index, record))
    return tuple(result)


POWER_UPGRADE = LogicalItem(
    key="power-upgrade",
    display_name="Power Upgrade",
    award_kind="power-upgrade",
    source_stage_id=-1,
    source_record_index=-1,
)


@dataclass(frozen=True)
class MaterializationPlan:
    logical_item: LogicalItem
    identity: bytes
    keeps_destination_visual: bool
    requires_foreign_resource: bool


def _decode(identity: bytes) -> list[int]:
    if len(identity) != IDENTITY_SIZE:
        raise ValueError(f"pickup identity must be {IDENTITY_SIZE} bytes")
    return [int.from_bytes(identity[i : i + 4], "big") for i in range(0, IDENTITY_SIZE, 4)]


def _encode(words: list[int]) -> bytes:
    return b"".join(word.to_bytes(4, "big") for word in words)


def materialize_destination_shell(
    destination_identity: bytes,
    logical_item: LogicalItem,
    *,
    generic_inventory_callback: int,
    power_upgrade_callback: int,
) -> MaterializationPlan:
    """Materialize a logical reward while keeping destination-stage actor resources.

    Word layout is type, parameter, callback, extent A, extent B, resource slot,
    presentation.  Type/extents/resource/presentation stay destination-native.
    """

    words = _decode(destination_identity)

    if logical_item.award_kind == "inventory":
        if logical_item.inventory_id is None:
            raise ValueError(f"{logical_item.key}: inventory reward has no item ID")
        words[1] = logical_item.inventory_id
        words[2] = generic_inventory_callback
    elif logical_item.award_kind == "native-effect":
        if logical_item.native_callback is None:
            raise ValueError(f"{logical_item.key}: native effect has no callback")
        words[1] = 0
        words[2] = logical_item.native_callback
    elif logical_item.award_kind == "power-upgrade":
        words[1] = 0
        words[2] = power_upgrade_callback
    else:  # pragma: no cover - defensive against future bad literal expansion
        raise ValueError(f"unsupported award kind: {logical_item.award_kind}")

    return MaterializationPlan(
        logical_item=logical_item,
        identity=_encode(words),
        keeps_destination_visual=True,
        requires_foreign_resource=False,
    )


def build_generic_inventory_award_callback(*, inventory_add_va: int, sound_and_return_tail_va: int) -> bytes:
    """Build the compact generic logical-inventory callback for proof use.

    Pickup-manager ABI is a0=record+0x10 and a1=record+0x14. The logical
    inventory ID is supplied through a1. The callback uses the same stack
    layout as the existing progression callback and tail-jumps to an existing
    sound+epilogue block after native inventory insertion.

    This helper is implementation/static-only until a disposable ROM confirms
    the callback at runtime.
    """

    return words_blob(
        [
            addiu("sp", "sp", -0x18),
            sw("ra", 0x10, "sp"),
            jal(inventory_add_va),
            addu("a0", "a1", "zero"),
            jump(sound_and_return_tail_va),
            0,
        ]
    )
