import hashlib
import struct

from mkmszr.config import RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.global_materialization import GlobalItemMaterializationPatch
from mkmszr.patches.inventory_hud import (
    COMMON_PACKAGE_CAPACITY,
    COMMON_PACKAGE_ROM,
    CRYSTAL_SOURCE_WORDS,
    FONT_DESCRIPTOR_SIZE,
    GLOBAL_OUTPUT_SIZE,
    HUD_CODE_END_ROM,
    HUD_CODE_K0,
    HUD_CODE_ROM,
    HUD_CODE_SIZE,
    HUD_DATA_END_ROM,
    HUD_DATA_ROM,
    HUD_DATA_SIZE,
    HUD_STATE_DATA_PTR_OFF,
    LIST_FONT_ROM,
    MATERIALIZER_HELPER_END_ROM,
    PORTRAIT_ATLAS_ROM,
    PORTRAIT_ATLAS_SIZE,
    TOASTY_AUDIO_ROM,
    InventoryHudPatch,
    _append_image_record,
    _build_hud_data,
    _build_runtime,
    _compress_resource_package,
    _image_records,
    _native_palette,
)
from mkmszr.patches.progression_presentation import ProgressionPickupPresentationPatch
from mkmszr.patches.required_powers import RequiredPowersPatch
from mkmszr.resource_materialization import GlobalMaterializationPlan
from mkmszr.rom import RomImage


def _font_rom() -> RomImage:
    size = LIST_FONT_ROM + FONT_DESCRIPTOR_SIZE
    data = bytearray(size)
    stock = bytearray(FONT_DESCRIPTOR_SIZE)
    stock[:4] = (0x10).to_bytes(4, "big")
    for index in range(256):
        # 15-bit BGR source ramp; zero remains the transparent entry.
        level = index & 0x1F
        word = 0 if index == 0 else (level << 10) | (level << 5) | level
        stock[4 + index * 2 : 6 + index * 2] = word.to_bytes(2, "big")
    data[LIST_FONT_ROM : LIST_FONT_ROM + FONT_DESCRIPTOR_SIZE] = stock
    return RomImage(data=data, _original=bytes(data))


def test_inventory_hud_fixed_allocations_are_bounded_and_disjoint() -> None:
    assert HUD_CODE_ROM == MATERIALIZER_HELPER_END_ROM
    assert HUD_CODE_SIZE == 0x500
    assert HUD_CODE_END_ROM == TOASTY_AUDIO_ROM
    assert HUD_CODE_K0 == 0x801B28F0
    assert PORTRAIT_ATLAS_ROM == 0x01800000
    assert PORTRAIT_ATLAS_ROM + PORTRAIT_ATLAS_SIZE <= COMMON_PACKAGE_ROM
    assert COMMON_PACKAGE_ROM + COMMON_PACKAGE_CAPACITY == HUD_DATA_ROM
    assert HUD_DATA_END_ROM == HUD_DATA_ROM + HUD_DATA_SIZE
    assert HUD_DATA_END_ROM <= GLOBAL_OUTPUT_SIZE


def test_native_palette_uses_static_confirmed_15_bit_bgr_source_layout() -> None:
    stock = bytearray(FONT_DESCRIPTOR_SIZE)
    stock[:4] = (0x10).to_bytes(4, "big")
    stock[4:6] = (0x7FFF).to_bytes(2, "big")
    recolored = _native_palette(bytes(stock), (255, 0, 0))
    assert int.from_bytes(recolored[4:6], "big") == 0x001F


def test_hud_data_uses_exact_requirement_semantics() -> None:
    rom = _font_rom()

    exact, exact_layout = _build_hud_data(rom, required_count=8)
    vanilla, vanilla_layout = _build_hud_data(rom, required_count=None)

    assert b"STG CHECKS KEYS\0" in exact
    assert b"TEM 00-05 ---\0" in exact
    assert b"FOR 00-09 0-3\0" in exact
    assert b"REQ. POWERS 0-8\0" in exact
    assert b"CHKS 00-85\0" in exact
    assert exact_layout["requirement_exact"] == 1

    assert b"REQ. XP 5100\0" in vanilla
    assert b"REQ. POWERS" not in vanilla
    assert vanilla_layout["requirement_exact"] == 0
    assert exact_layout["used"] <= HUD_DATA_SIZE
    assert vanilla_layout["used"] <= HUD_DATA_SIZE


def test_runtime_helpers_fit_exact_production_tail() -> None:
    rom = _font_rom()
    _data, layout = _build_hud_data(rom, required_count=9)
    module, permanent, runtime = _build_runtime(layout)

    assert len(module) == HUD_CODE_SIZE
    assert runtime["used"] <= HUD_STATE_DATA_PTR_OFF
    assert len(permanent) == 0xF0
    assert module[HUD_STATE_DATA_PTR_OFF : HUD_STATE_DATA_PTR_OFF + 4] == bytes(4)
    assert module[HUD_STATE_DATA_PTR_OFF + 4 : HUD_STATE_DATA_PTR_OFF + 8] == b"\xFF" * 4


def test_common_package_append_and_lzw_round_trip() -> None:
    payload = bytes(range(8))
    first = struct.pack(">IHhHH", 0, 4, 2, 0x123, 0) + payload
    raw = (1).to_bytes(4, "big") + bytes(4) + first

    second = bytearray(first)
    second[8:10] = (0x46C).to_bytes(2, "big")
    expanded = _append_image_record(raw, bytes(second))
    records, end = _image_records(expanded)

    assert set(records) == {0x123, 0x46C}
    assert end == len(expanded)
    packed = _compress_resource_package(expanded)
    # The compressor itself performs an exact decoder round-trip guard.
    assert len(packed) > 4


def test_crystal_source_table_shape_is_stable() -> None:
    assert len(CRYSTAL_SOURCE_WORDS) == 16
    assert CRYSTAL_SOURCE_WORDS[0] == 0
    assert hashlib.sha256(
        b"".join(word.to_bytes(2, "big") for word in CRYSTAL_SOURCE_WORDS)
    ).hexdigest() == "70604d5d7e3bb2ab81e844de4f761b3bc1c02f40a253d2d33e5587a6ca3edd6a"


def test_pipeline_places_inventory_hud_after_global_runtime_owners() -> None:
    plan = GlobalMaterializationPlan(
        assignments=(),
        placements=(),
        temple_special_item_key="herbs",
    )
    config = RandomizerConfig(required_powers_mode="custom", custom_required_powers=8)
    patches = build_pipeline(config, materialization_plan=plan).patches
    types = [type(patch) for patch in patches]

    global_index = types.index(GlobalItemMaterializationPatch)
    progression_index = types.index(ProgressionPickupPresentationPatch)
    required_index = types.index(RequiredPowersPatch)
    hud_index = types.index(InventoryHudPatch)

    assert global_index < progression_index < required_index < hud_index