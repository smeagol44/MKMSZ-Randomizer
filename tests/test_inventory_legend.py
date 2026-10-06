from mkmszr.config import RandomizerConfig
from mkmszr.mips import address_words, jr, words_blob
from mkmszr.patcher import build_pipeline
from mkmszr.patches.base import PatchContext
from mkmszr.patches.inventory_legend import (
    EXPECTED_LEGEND_BLOCK,
    INVENTORY_LEGEND_MODULE,
    LEGEND_CEILING,
    LEGEND_HOOK_ROM,
    LEGEND_K0,
    LEGEND_K1,
    LEGEND_PAD,
    LEGEND_ROM,
    SWITCH_TRANSPORT_END_ROM,
    InventoryLegendPatch,
)
from mkmszr.patches.inventory_menu_switch import (
    EXPANSION_FILE_ENTRY_ROM,
    InventoryMenuSwitchPatch,
    TRANSPORT_END_ROM,
    TRANSPORT_ROM,
)
from mkmszr.resource_materialization import GLOBAL_OUTPUT_SIZE, GlobalMaterializationPlan
from mkmszr.rom import RomImage

NOP = 0


def _post_switch_shape() -> tuple[RomImage, bytes]:
    data = bytearray(GLOBAL_OUTPUT_SIZE)
    data[TRANSPORT_ROM:TRANSPORT_END_ROM] = b"\xFF" * (
        TRANSPORT_END_ROM - TRANSPORT_ROM
    )
    prefix = bytes(
        (index * 29 + 7) & 0xFF
        for index in range(SWITCH_TRANSPORT_END_ROM - TRANSPORT_ROM)
    )
    data[TRANSPORT_ROM:SWITCH_TRANSPORT_END_ROM] = prefix
    data[EXPANSION_FILE_ENTRY_ROM : EXPANSION_FILE_ENTRY_ROM + 4] = (
        TRANSPORT_ROM.to_bytes(4, "big")
    )
    data[EXPANSION_FILE_ENTRY_ROM + 4 : EXPANSION_FILE_ENTRY_ROM + 8] = (
        SWITCH_TRANSPORT_END_ROM.to_bytes(4, "big")
    )
    data[LEGEND_HOOK_ROM : LEGEND_HOOK_ROM + len(EXPECTED_LEGEND_BLOCK)] = (
        EXPECTED_LEGEND_BLOCK
    )
    return RomImage(data=data, _original=bytes(data)), prefix


def test_inventory_legend_module_matches_runtime_proof_layout() -> None:
    assert LEGEND_PAD == 0x0C
    assert LEGEND_K0 == 0x801B2F50
    assert LEGEND_ROM == 0x01819730
    assert len(INVENTORY_LEGEND_MODULE) == 0x196
    assert len(INVENTORY_LEGEND_MODULE) <= LEGEND_CEILING == 0x300
    assert LEGEND_ROM + len(INVENTORY_LEGEND_MODULE) <= TRANSPORT_END_ROM


def test_inventory_legend_appends_without_changing_switch_payload() -> None:
    rom, prefix = _post_switch_shape()

    notes = InventoryLegendPatch().apply(rom, PatchContext(seed="TEST"))

    payload_end = rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4)
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM) == TRANSPORT_ROM
    assert payload_end == LEGEND_ROM + len(INVENTORY_LEGEND_MODULE)
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 8) == 0
    assert bytes(rom.data[TRANSPORT_ROM:SWITCH_TRANSPORT_END_ROM]) == prefix
    assert (
        bytes(rom.data[SWITCH_TRANSPORT_END_ROM:LEGEND_ROM])
        == b"\x00" * LEGEND_PAD
    )
    assert bytes(rom.data[LEGEND_ROM:payload_end]) == INVENTORY_LEGEND_MODULE

    expected_trampoline = words_blob([*address_words("t9", LEGEND_K1), jr("t9"), NOP])
    assert bytes(rom.data[LEGEND_HOOK_ROM : LEGEND_HOOK_ROM + 16]) == expected_trampoline
    assert bytes(
        rom.data[
            LEGEND_HOOK_ROM + 16 : LEGEND_HOOK_ROM + len(EXPECTED_LEGEND_BLOCK)
        ]
    ) == b"\x00" * (len(EXPECTED_LEGEND_BLOCK) - 16)
    assert "BOX n OF 4" in notes[0]
    assert "L-R POWER" in notes[1]


def test_pipeline_installs_legend_after_menu_switch() -> None:
    plan = GlobalMaterializationPlan(
        assignments=(),
        placements=(),
        temple_special_item_key="herbs",
    )
    patches = build_pipeline(RandomizerConfig(), materialization_plan=plan).patches
    types = [type(patch) for patch in patches]

    assert types.index(InventoryMenuSwitchPatch) < types.index(InventoryLegendPatch)
