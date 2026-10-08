import hashlib

from mkmszr.config import RandomizerConfig
from mkmszr.mips import address_words, jr, words_blob
from mkmszr.patcher import build_pipeline
from mkmszr.patches.base import PatchContext
from mkmszr.patches.inventory_legend import InventoryLegendPatch
from mkmszr.patches.inventory_materialized import (
    ACCEPTED_HELPER_SHA256,
    CHECK_GATE,
    CHECK_GATE_ROM,
    EMPTY_POWERS_ROM,
    EMPTY_POWERS_WRAPPER,
    EXPECTED_CHECK_GATE,
    EXPECTED_FORTRESS_PRELOAD_HOOK,
    EXPECTED_INVENTORY_OPEN_HOOK,
    EXPECTED_REQUIREMENT_GATE,
    EXPECTED_TABLE_COMPUTE,
    FORTRESS_PRELOAD_HOOK_ROM,
    LEGEND_PAYLOAD_END_ROM,
    MATERIALIZED_PAYLOAD_END_ROM,
    MATERIALIZED_RUNTIME_END_K0,
    OPEN_ROM,
    OPEN_WRAPPER,
    PRELOAD_HELPER,
    PRELOAD_ROM,
    REQUIREMENT_GATE,
    REQUIREMENT_GATE_ROM,
    REQUIREMENT_ROM,
    TABLE_COMPUTE_ROM,
    TABLE_GATE,
    TABLE_ROM,
    VANILLA_CHECK_GATE,
    VANILLA_CHECK_GATE_ROM,
    InventoryMaterializedHudPatch,
)
from mkmszr.patches.inventory_menu_switch import (
    EXPANSION_FILE_ENTRY_ROM,
    INVENTORY_LOOP_HOOK_ROM,
    TRANSPORT_END_ROM,
    TRANSPORT_ROM,
)
from mkmszr.patches.inventory_menu_switch import (
    MODULE_K1 as SWITCH_MODULE_K1,
)
from mkmszr.resource_materialization import GLOBAL_OUTPUT_SIZE, GlobalMaterializationPlan
from mkmszr.rom import RomImage

NOP = 0


def _jump_trampoline(target: int) -> bytes:
    return words_blob([*address_words("t9", target), jr("t9"), NOP])


def _post_legend_shape(*, requirement_exact: bool = True) -> RomImage:
    data = bytearray(GLOBAL_OUTPUT_SIZE)
    data[TRANSPORT_ROM:TRANSPORT_END_ROM] = b"\xFF" * (
        TRANSPORT_END_ROM - TRANSPORT_ROM
    )
    # The final production prefix exists before this patch. Only the three
    # materialization seams need exact contents for the focused unit shape.
    data[TRANSPORT_ROM:LEGEND_PAYLOAD_END_ROM] = bytes(
        (index * 13 + 5) & 0xFF
        for index in range(LEGEND_PAYLOAD_END_ROM - TRANSPORT_ROM)
    )
    data[EXPANSION_FILE_ENTRY_ROM : EXPANSION_FILE_ENTRY_ROM + 4] = (
        TRANSPORT_ROM.to_bytes(4, "big")
    )
    data[EXPANSION_FILE_ENTRY_ROM + 4 : EXPANSION_FILE_ENTRY_ROM + 8] = (
        LEGEND_PAYLOAD_END_ROM.to_bytes(4, "big")
    )
    data[EXPANSION_FILE_ENTRY_ROM + 8 : EXPANSION_FILE_ENTRY_ROM + 12] = (
        (0).to_bytes(4, "big")
    )
    data[FORTRESS_PRELOAD_HOOK_ROM : FORTRESS_PRELOAD_HOOK_ROM + 16] = (
        EXPECTED_FORTRESS_PRELOAD_HOOK
    )
    data[0x00074310 : 0x00074320] = EXPECTED_INVENTORY_OPEN_HOOK
    data[
        INVENTORY_LOOP_HOOK_ROM : INVENTORY_LOOP_HOOK_ROM + 16
    ] = _jump_trampoline(SWITCH_MODULE_K1)
    data[TABLE_COMPUTE_ROM : TABLE_COMPUTE_ROM + 16] = EXPECTED_TABLE_COMPUTE
    if requirement_exact:
        data[
            REQUIREMENT_GATE_ROM : REQUIREMENT_GATE_ROM + 16
        ] = EXPECTED_REQUIREMENT_GATE
        data[CHECK_GATE_ROM : CHECK_GATE_ROM + 16] = EXPECTED_CHECK_GATE
    else:
        data[
            VANILLA_CHECK_GATE_ROM : VANILLA_CHECK_GATE_ROM + 16
        ] = EXPECTED_CHECK_GATE
    data[0x01815198:0x018151A0] = b"\x00" * 8
    return RomImage(data=data, _original=bytes(data))


def test_materialized_inventory_helpers_match_accepted_runtime_proof() -> None:
    helpers = {
        "preload": PRELOAD_HELPER,
        "empty_powers": EMPTY_POWERS_WRAPPER,
        "open": OPEN_WRAPPER,
        "requirement": REQUIREMENT_GATE,
        "check": CHECK_GATE,
        "table": TABLE_GATE,
    }
    for name, blob in helpers.items():
        assert hashlib.sha256(blob).hexdigest() == ACCEPTED_HELPER_SHA256[name]

    assert PRELOAD_ROM == 0x018198D0
    assert EMPTY_POWERS_ROM == 0x01819908
    assert OPEN_ROM == 0x018199F0
    assert REQUIREMENT_ROM == 0x01819A30
    assert TABLE_ROM == 0x01819AD0
    assert MATERIALIZED_PAYLOAD_END_ROM == 0x01819B9C
    assert MATERIALIZED_RUNTIME_END_K0 == 0x801B33BC


def test_materialized_inventory_appends_inside_existing_transport() -> None:
    rom = _post_legend_shape()

    notes = InventoryMaterializedHudPatch().apply(
        rom,
        PatchContext(seed="TEST"),
    )

    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM) == TRANSPORT_ROM
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == MATERIALIZED_PAYLOAD_END_ROM
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 8) == 0
    assert MATERIALIZED_PAYLOAD_END_ROM <= TRANSPORT_END_ROM
    assert bytes(rom.data[PRELOAD_ROM : PRELOAD_ROM + len(PRELOAD_HELPER)]) == PRELOAD_HELPER
    assert bytes(
        rom.data[
            EMPTY_POWERS_ROM : EMPTY_POWERS_ROM + len(EMPTY_POWERS_WRAPPER)
        ]
    ) == EMPTY_POWERS_WRAPPER
    assert bytes(rom.data[OPEN_ROM : OPEN_ROM + len(OPEN_WRAPPER)]) == OPEN_WRAPPER
    assert bytes(
        rom.data[REQUIREMENT_ROM : REQUIREMENT_ROM + len(REQUIREMENT_GATE)]
    ) == REQUIREMENT_GATE
    assert bytes(rom.data[TABLE_ROM : TABLE_ROM + len(TABLE_GATE)]) == TABLE_GATE

    assert (
        bytes(rom.data[FORTRESS_PRELOAD_HOOK_ROM : FORTRESS_PRELOAD_HOOK_ROM + 16])
        == words_blob(
            [
                0x3C19A01B,
                0x273930F0,
                0x0320F809,
                0x00000000,
            ]
        )
    )
    assert bytes(rom.data[0x00074310:0x00074320]) == words_blob(
        [0x3C19A01B, 0x37393210, 0x03200008, 0x00000000]
    )
    assert (
        bytes(
            rom.data[
                INVENTORY_LOOP_HOOK_ROM : INVENTORY_LOOP_HOOK_ROM + 16
            ]
        )
        == words_blob([0x3C19A01B, 0x37393128, 0x03200008, 0x00000000])
    )
    assert bytes(rom.data[TABLE_COMPUTE_ROM : TABLE_COMPUTE_ROM + 16]) == words_blob(
        [0x3C19A01B, 0x373932F0, 0x03200008, 0x00000000]
    )
    assert bytes(
        rom.data[REQUIREMENT_GATE_ROM : REQUIREMENT_GATE_ROM + 16]
    ) == words_blob([0x3C19A01B, 0x37393250, 0x03200008, 0x00000000])
    assert bytes(rom.data[CHECK_GATE_ROM : CHECK_GATE_ROM + 16]) == words_blob(
        [0x3C19A01B, 0x373932A0, 0x03200008, 0x00000000]
    )
    assert "materialized" in notes[2]




def test_materialized_inventory_supports_vanilla_static_requirement_layout() -> None:
    rom = _post_legend_shape(requirement_exact=False)

    InventoryMaterializedHudPatch(requirement_exact=False).apply(
        rom,
        PatchContext(seed="TEST"),
    )

    assert bytes(
        rom.data[VANILLA_CHECK_GATE_ROM : VANILLA_CHECK_GATE_ROM + 16]
    ) == words_blob([0x3C19A01B, 0x373932A0, 0x03200008, 0x00000000])
    assert len(VANILLA_CHECK_GATE) == len(CHECK_GATE)

def test_pipeline_installs_materialized_inventory_after_legend() -> None:
    plan = GlobalMaterializationPlan(
        assignments=(),
        placements=(),
        temple_special_item_key="herbs",
    )
    patches = build_pipeline(RandomizerConfig(), materialization_plan=plan).patches
    types = [type(patch) for patch in patches]

    assert types.index(InventoryLegendPatch) < types.index(InventoryMaterializedHudPatch)
    materialized = next(
        patch for patch in patches if isinstance(patch, InventoryMaterializedHudPatch)
    )
    assert materialized.requirement_exact is False
