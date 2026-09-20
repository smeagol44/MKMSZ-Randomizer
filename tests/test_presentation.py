from mkmszr.config import RandomizerConfig
from mkmszr.data.boot_phrases import (
    BOOT_PHRASE_LINE_LIMIT,
    BOOT_PHRASES,
    DEFAULT_BOOT_PHRASE,
    select_boot_phrase,
)
from mkmszr.patcher import build_pipeline
from mkmszr.patches.base import PatchContext
from mkmszr.patches.boot_branding import (
    BOOT_POINTER_PATCHES,
    BOOT_TEXT_END,
    BOOT_TEXT_ROM,
    EXPECTED_BOOT_TEXT,
    EXPECTED_LICENSE_TEXT,
    LICENSE_END,
    LICENSE_ROM,
    PHRASE1_ROM,
    PHRASE2_ROM,
    BootBrandingPatch,
)
from mkmszr.patches.box_indicator import (
    BOX_HOOK_CALL,
    BOX_REGION,
    BOX_REGION_END,
    BOX_REGION_ROM,
    EXPECTED_BOX_REGION,
    EXPECTED_HUD_CALL,
    HUD_HOOK_ROM,
    BoxIndicatorPatch,
)
from mkmszr.patches.inventory_boxes import FourBoxInventoryPatch
from mkmszr.patches.pickup_randomization import PickupRandomizationPatch
from mkmszr.rom import RomImage


def _presentation_base_shape() -> RomImage:
    data = bytearray(LICENSE_END)
    data[BOX_REGION_ROM:BOX_REGION_END] = EXPECTED_BOX_REGION
    data[HUD_HOOK_ROM : HUD_HOOK_ROM + 4] = EXPECTED_HUD_CALL.to_bytes(4, "big")
    data[BOOT_TEXT_ROM:BOOT_TEXT_END] = EXPECTED_BOOT_TEXT
    data[LICENSE_ROM:LICENSE_END] = EXPECTED_LICENSE_TEXT
    for offset, expected, _replacement in BOOT_POINTER_PATCHES:
        data[offset : offset + 4] = expected.to_bytes(4, "big")
    return RomImage(data=data, _original=bytes(data))


def _read_c_string(data: bytearray, offset: int, limit: int = 20) -> str:
    chunk = bytes(data[offset : offset + limit])
    return chunk.split(b"\x00", 1)[0].decode("ascii")


def test_boot_phrase_pool_is_large_ascii_and_slot_safe() -> None:
    assert len(BOOT_PHRASES) >= 100
    assert DEFAULT_BOOT_PHRASE in BOOT_PHRASES

    for phrase in BOOT_PHRASES:
        assert len(phrase) == 2
        for line in phrase:
            assert len(line.encode("ascii")) <= BOOT_PHRASE_LINE_LIMIT


def test_boot_phrase_selection_is_deterministic() -> None:
    assert select_boot_phrase(None) == DEFAULT_BOOT_PHRASE
    assert select_boot_phrase("") == DEFAULT_BOOT_PHRASE
    assert select_boot_phrase("BCBDBF") == ("THIS SEED LOOKED", "BETTER ON PAPER")
    assert select_boot_phrase("BCBDBF") == select_boot_phrase("BCBDBF")


def test_runtime_confirmed_box_and_boot_presentation_install_together() -> None:
    rom = _presentation_base_shape()

    BoxIndicatorPatch().apply(rom, PatchContext())
    notes = BootBrandingPatch().apply(rom, PatchContext())

    assert rom.read_u32(HUD_HOOK_ROM) == BOX_HOOK_CALL
    assert rom.data[BOX_REGION_ROM:BOX_REGION_END] == BOX_REGION

    assert _read_c_string(rom.data, 0x000AF9BE) == "RANDOMIZER"
    assert _read_c_string(rom.data, 0x000AF9C9, 24) == "~1997 MIDWAY GAMES INC."
    assert _read_c_string(rom.data, PHRASE1_ROM) == "DO PEOPLE EVEN READ"
    assert _read_c_string(rom.data, PHRASE2_ROM) == "THESE THINGS?"
    assert _read_c_string(rom.data, 0x000AFA09) == "BY SMEAG"
    assert _read_c_string(rom.data, LICENSE_ROM, 24) == "LICENSED BY NINTENDO"

    for offset, _expected, replacement in BOOT_POINTER_PATCHES:
        assert rom.read_u32(offset) == replacement

    assert notes[-1] == "seed boot phrase: DO PEOPLE EVEN READ / THESE THINGS?"


def test_seeded_phrase_is_written_into_fixed_slots() -> None:
    rom = _presentation_base_shape()

    BoxIndicatorPatch().apply(rom, PatchContext())
    BootBrandingPatch().apply(rom, PatchContext(seed="BCBDBF"))

    assert _read_c_string(rom.data, PHRASE1_ROM) == "THIS SEED LOOKED"
    assert _read_c_string(rom.data, PHRASE2_ROM) == "BETTER ON PAPER"


def test_presentation_patches_follow_four_box_inventory() -> None:
    pipeline = build_pipeline(RandomizerConfig())
    assert isinstance(pipeline.patches[4], PickupRandomizationPatch)
    assert isinstance(pipeline.patches[5], FourBoxInventoryPatch)
    assert isinstance(pipeline.patches[6], BoxIndicatorPatch)
    assert isinstance(pipeline.patches[7], BootBrandingPatch)
