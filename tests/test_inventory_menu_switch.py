from mkmszr.config import RandomizerConfig
from mkmszr.mips import address_words, jr, words_blob
from mkmszr.patcher import build_pipeline
from mkmszr.patches.base import PatchContext
from mkmszr.patches.inventory_hud import InventoryHudPatch
from mkmszr.patches.inventory_menu_switch import (
    EMPTY_BOX_R_GATE_ROM,
    EXPANSION_FILE_ENTRY_ROM,
    EXPECTED_EMPTY_BOX_R_GATE,
    EXPECTED_FILE_END,
    EXPECTED_FILE_START,
    EXPECTED_INVENTORY_LOOP_HOOK,
    INVENTORY_LOOP_HOOK_ROM,
    INVENTORY_MENU_SWITCH_MODULE,
    MODULE_CAPACITY,
    MODULE_K1,
    NOP,
    TRANSPORT_CAPACITY,
    TRANSPORT_END_ROM,
    TRANSPORT_ROM,
    InventoryMenuSwitchPatch,
)
from mkmszr.resource_materialization import GLOBAL_OUTPUT_SIZE, GlobalMaterializationPlan
from mkmszr.rom import RomImage


def _post_hud_shape() -> tuple[RomImage, bytes]:
    data = bytearray(GLOBAL_OUTPUT_SIZE)
    data[TRANSPORT_ROM:TRANSPORT_END_ROM] = b"\xFF" * TRANSPORT_CAPACITY
    prefix = bytes(
        (index * 37 + 11) & 0xFF
        for index in range(EXPECTED_FILE_END - EXPECTED_FILE_START)
    )
    data[EXPECTED_FILE_START:EXPECTED_FILE_END] = prefix
    data[EXPANSION_FILE_ENTRY_ROM : EXPANSION_FILE_ENTRY_ROM + 4] = (
        EXPECTED_FILE_START.to_bytes(4, "big")
    )
    data[EXPANSION_FILE_ENTRY_ROM + 4 : EXPANSION_FILE_ENTRY_ROM + 8] = (
        EXPECTED_FILE_END.to_bytes(4, "big")
    )
    data[INVENTORY_LOOP_HOOK_ROM : INVENTORY_LOOP_HOOK_ROM + 16] = (
        EXPECTED_INVENTORY_LOOP_HOOK
    )
    data[EMPTY_BOX_R_GATE_ROM : EMPTY_BOX_R_GATE_ROM + 4] = (
        EXPECTED_EMPTY_BOX_R_GATE.to_bytes(4, "big")
    )
    return RomImage(data=data, _original=bytes(data)), prefix


def test_inventory_menu_switch_module_fits_bounded_tail() -> None:
    assert len(INVENTORY_MENU_SWITCH_MODULE) == 0x154
    assert len(INVENTORY_MENU_SWITCH_MODULE) <= MODULE_CAPACITY == 0x630
    assert EXPECTED_FILE_END - EXPECTED_FILE_START == 0x35D0
    assert (
        EXPECTED_FILE_END - EXPECTED_FILE_START + len(INVENTORY_MENU_SWITCH_MODULE)
        == 0x3724
    )
    assert 0x3724 <= TRANSPORT_CAPACITY == 0x3C00


def test_inventory_menu_switch_relocates_final_file_and_installs_hooks() -> None:
    rom, prefix = _post_hud_shape()

    notes = InventoryMenuSwitchPatch().apply(rom, PatchContext(seed="TEST"))

    end = rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4)
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM) == TRANSPORT_ROM
    assert end == TRANSPORT_ROM + len(prefix) + len(INVENTORY_MENU_SWITCH_MODULE)
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 8) == 0
    assert bytes(rom.data[TRANSPORT_ROM : TRANSPORT_ROM + len(prefix)]) == prefix
    assert (
        bytes(rom.data[TRANSPORT_ROM + len(prefix) : end])
        == INVENTORY_MENU_SWITCH_MODULE
    )

    expected_trampoline = words_blob([*address_words("t9", MODULE_K1), jr("t9"), NOP])
    assert (
        bytes(rom.data[INVENTORY_LOOP_HOOK_ROM : INVENTORY_LOOP_HOOK_ROM + 16])
        == expected_trampoline
    )
    assert rom.read_u32(EMPTY_BOX_R_GATE_ROM) == NOP
    assert "Left/Right" in notes[0]


def test_pipeline_installs_menu_switch_after_inventory_hud() -> None:
    plan = GlobalMaterializationPlan(
        assignments=(),
        placements=(),
        temple_special_item_key="herbs",
    )
    patches = build_pipeline(RandomizerConfig(), materialization_plan=plan).patches
    types = [type(patch) for patch in patches]

    assert types.index(InventoryHudPatch) < types.index(InventoryMenuSwitchPatch)
