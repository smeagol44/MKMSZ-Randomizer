from mkmszr.mips import jal
from mkmszr.patches.base import PatchContext
from mkmszr.patches.flow_bypass import (
    BOOT_LOGO_BRANCH,
    BOOT_LOGO_BYPASS_ROM,
    BOOT_LOGO_GUARD,
    SAFE_SELECTOR_SKIP_SAVE_EXPECTED,
    SAFE_SELECTOR_SKIP_SAVE_PATCH,
    SAFE_SELECTOR_SKIP_SAVE_ROM,
    BootLogoBypassPatch,
    SafeStageSelectSkipAutoSavePatch,
)
from mkmszr.patches.inventory_boxes import RELOCATED_MAPPER_VA
from mkmszr.patches.stage_selector import SELECTION_LOAD_ROM
from mkmszr.rom import RomImage


def _flow_shape() -> RomImage:
    size = max(
        BOOT_LOGO_BYPASS_ROM + len(BOOT_LOGO_GUARD),
        SAFE_SELECTOR_SKIP_SAVE_ROM + len(SAFE_SELECTOR_SKIP_SAVE_EXPECTED),
    )
    data = bytearray(size)
    data[
        BOOT_LOGO_BYPASS_ROM :
        BOOT_LOGO_BYPASS_ROM + len(BOOT_LOGO_GUARD)
    ] = BOOT_LOGO_GUARD
    data[
        SAFE_SELECTOR_SKIP_SAVE_ROM :
        SAFE_SELECTOR_SKIP_SAVE_ROM + len(SAFE_SELECTOR_SKIP_SAVE_EXPECTED)
    ] = SAFE_SELECTOR_SKIP_SAVE_EXPECTED
    data[
        SELECTION_LOAD_ROM : SELECTION_LOAD_ROM + 4
    ] = jal(RELOCATED_MAPPER_VA).to_bytes(4, "big")
    return RomImage(data=data, _original=bytes(data))


def test_safe_selector_skip_auto_save_rewrites_only_relocated_mapper() -> None:
    rom = _flow_shape()
    before = bytes(rom.data)

    notes = SafeStageSelectSkipAutoSavePatch().apply(rom, PatchContext())

    assert rom.data[
        SAFE_SELECTOR_SKIP_SAVE_ROM :
        SAFE_SELECTOR_SKIP_SAVE_ROM + len(SAFE_SELECTOR_SKIP_SAVE_PATCH)
    ] == SAFE_SELECTOR_SKIP_SAVE_PATCH

    changed = [
        index
        for index, (old, new) in enumerate(zip(before, rom.data))
        if old != new
    ]
    expected = [
        SAFE_SELECTOR_SKIP_SAVE_ROM + index
        for index, (old, new) in enumerate(
            zip(SAFE_SELECTOR_SKIP_SAVE_EXPECTED, SAFE_SELECTOR_SKIP_SAVE_PATCH)
        )
        if old != new
    ]
    assert changed == expected
    assert "automatic stage-entry save prompt" in notes[1]


def test_boot_logo_bypass_changes_only_first_instruction() -> None:
    rom = _flow_shape()
    before = bytes(rom.data)

    notes = BootLogoBypassPatch().apply(rom, PatchContext())

    assert rom.read_u32(BOOT_LOGO_BYPASS_ROM) == BOOT_LOGO_BRANCH
    assert rom.data[
        BOOT_LOGO_BYPASS_ROM + 4 :
        BOOT_LOGO_BYPASS_ROM + len(BOOT_LOGO_GUARD)
    ] == before[
        BOOT_LOGO_BYPASS_ROM + 4 :
        BOOT_LOGO_BYPASS_ROM + len(BOOT_LOGO_GUARD)
    ]
    assert "company/logo" in notes[1]
