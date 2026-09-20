"""Logical item model for the future global MKMSZR pickup pool.

The logical catalog is separate from physical placement, but 1.0 requires the
placed pickup to use the *actual visual identity of the randomized item*.

Cross-stage materialization therefore must import/remap the source item's
resource bundle into the destination stage when that visual is not already
resident.  Keeping a destination pickup's old graphics while awarding a
different logical item is explicitly not an acceptable 1.0 strategy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .data.pickups import STAGE_PICKUPS, PickupSpec

AwardKind = Literal["inventory", "native-effect", "power-upgrade"]


@dataclass(frozen=True)
class LogicalItem:
    """A stage-independent randomized reward backed by an exact source visual."""

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

# Global callbacks whose reward semantics are not tied to a stage overlay.
FIXED_CALLBACK_ITEMS: dict[int, tuple[str, str, AwardKind, int | None]] = {
    0x800388FC: ("potion", "Potion", "inventory", 0x01),
    0x8003898C: ("formula", "Formula", "inventory", 0x02),
    0x8003895C: ("eye", "Eye", "inventory", 0x03),
    0x800389BC: ("herbs", "Herbs", "inventory", 0x04),
    0x800389EC: ("health-urn", "Urn (Vitality)", "inventory", 0x05),
    0x8003892C: ("shield", "Shield", "inventory", 0x06),
    0x80038A1C: ("extra-life", "Urn (Extra Life)", "native-effect", None),
    0x80038A58: ("mana", "Mana", "native-effect", None),
    # Strength does more than merely insert inventory ID 0x0B.
    0x80038A90: ("strength-urn", "Urn (Strength)", "native-effect", None),
}


def _identity_words(identity: bytes) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(identity[index : index + 4], "big")
        for index in range(0, len(identity), 4)
    )


def logical_item_from_record(
    stage_id: int,
    record_index: int,
    record: PickupSpec,
) -> LogicalItem:
    """Decode one researched ordinary record into a logical reward."""

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

    callback = _identity_words(record.identity)[2]
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
    """Return all 84 ordinary stock rewards as logical items.

    Source stage/record are retained because exact 1.0 materialization must be
    able to recover the source item's native type/extents/resource/presentation
    and import that visual bundle when placed in another stage.

    Temple Map is intentionally absent because it is not an ordinary record.
    Power Upgrades are synthetic and are introduced by the global generator.
    """

    result: list[LogicalItem] = []
    for stage in STAGE_PICKUPS:
        for record_index, record in enumerate(stage.records):
            result.append(
                logical_item_from_record(stage.stage_id, record_index, record)
            )
    return tuple(result)


POWER_UPGRADE = LogicalItem(
    key="power-upgrade",
    display_name="Power Upgrade",
    award_kind="power-upgrade",
    source_stage_id=-1,
    source_record_index=-1,
)
