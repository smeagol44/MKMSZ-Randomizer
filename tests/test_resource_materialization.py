from mkmszr.errors import PatchError
from mkmszr.global_items import build_stock_logical_pool
from mkmszr.resource_materialization import (
    CANONICAL_VISUAL_DONORS,
    GLOBAL_OUTPUT_SIZE,
    GLOBAL_RESOURCE_REGION_END,
    GLOBAL_RESOURCE_REGION_START,
    GLOBAL_RESOURCE_SLOT_SIZE,
    STAGE_RESOURCES,
    VisualBundle,
    VisualFrame,
    build_extended_resource_file,
    decode_type4,
    encode_type4_literals,
    portable_fixed_callback_identity,
    production_global_resource_placements,
)


def test_canonical_visual_registry_covers_stock_keys_and_power_upgrade() -> None:
    keys = {item.key for item in build_stock_logical_pool()}
    assert set(CANONICAL_VISUAL_DONORS) == keys | {"power-upgrade"}



def test_earth_pickup_resource_mapping_uses_file_30() -> None:
    earth = STAGE_RESOURCES[3]
    assert earth.file_table_entry_rom == 0x000A5250
    assert earth.rom_start == 0x00305A30
    assert earth.rom_end == 0x0030AA00

    for key in ("earth-square", "earth-four-square", "earth-triangle"):
        assert CANONICAL_VISUAL_DONORS[key].frame_count == 8

def test_literal_type4_encoder_round_trips_without_ring_history() -> None:
    raw = bytes(range(64)) + b"\x00" * 17 + bytes(reversed(range(32)))
    encoded = encode_type4_literals(raw)

    assert encoded[3] == 4
    assert decode_type4(encoded) == raw


def test_extension_table_is_contiguous_deduplicated_and_self_contained() -> None:
    stock = bytes.fromhex("00000010 00000020 00000030 00000040")

    alpha_raw = (b"ALPHA" * 9) + b"!"
    beta_raw = bytes(range(23))

    alpha = VisualBundle(
        key="alpha",
        descriptor_control=1,
        frames=(
            VisualFrame(b"\x00\x11\x00\x12\x00\x08\x00\x08", encode_type4_literals(alpha_raw)),
            VisualFrame(b"\x00\x10\x00\x12\x00\x07\x00\x08", encode_type4_literals(alpha_raw[::-1])),
        ),
    )
    beta = VisualBundle(
        key="beta",
        descriptor_control=1,
        frames=(
            VisualFrame(b"\x00\x0F\x00\x11\x00\x06\x00\x09", encode_type4_literals(beta_raw)),
        ),
    )

    resource_file, visuals = build_extended_resource_file(
        stock,
        (beta, alpha, alpha),
    )

    assert [visual.key for visual in visuals] == ["alpha", "beta"]
    assert [visual.selector_entry_offset for visual in visuals] == [0x10, 0x14]
    assert [visual.selector for visual in visuals] == [4, 5]

    for visual in visuals:
        descriptor = int.from_bytes(
            resource_file[
                visual.selector_entry_offset : visual.selector_entry_offset + 4
            ],
            "big",
        )
        assert descriptor == visual.descriptor_offset

    alpha_visual = visuals[0]
    alpha_desc = alpha_visual.descriptor_offset
    alpha_record_0 = int.from_bytes(resource_file[alpha_desc : alpha_desc + 4], "big")
    alpha_record_1 = int.from_bytes(resource_file[alpha_desc + 4 : alpha_desc + 8], "big")

    for record_offset, expected_raw in (
        (alpha_record_0, alpha_raw),
        (alpha_record_1, alpha_raw[::-1]),
    ):
        assert int.from_bytes(
            resource_file[record_offset + 4 : record_offset + 8],
            "big",
        ) == 0
        block_offset = int.from_bytes(
            resource_file[record_offset + 8 : record_offset + 12],
            "big",
        )
        block_size = (
            resource_file[block_offset]
            | (resource_file[block_offset + 1] << 8)
            | (resource_file[block_offset + 2] << 16)
        )
        assert decode_type4(
            resource_file[block_offset : block_offset + block_size]
        ) == expected_raw


def test_extension_selector_order_is_independent_of_input_order() -> None:
    frame = VisualFrame(b"12345678", encode_type4_literals(b"frame"))
    first = VisualBundle("zeta", 1, (frame,))
    second = VisualBundle("alpha", 1, (frame,))

    left = build_extended_resource_file(bytes(0x20), (first, second))
    right = build_extended_resource_file(bytes(0x20), (second, first))

    assert left == right


def test_portable_identity_uses_canonical_fixed_callback_and_new_selector() -> None:
    identity = portable_fixed_callback_identity("health-urn", 0x123C)

    assert int.from_bytes(identity[0x08:0x0C], "big") == 0x800389EC
    assert int.from_bytes(identity[0x14:0x18], "big") == 0x123C


def test_stage_bound_token_identity_fails_closed() -> None:
    try:
        portable_fixed_callback_identity("prison-l1", 0x123C)
    except PatchError as exc:
        assert "destination-safe token wrapper required" in str(exc)
    else:
        raise AssertionError("stage-bound token callback should not be emitted")



def test_production_global_resource_slots_live_only_in_appended_rom() -> None:
    placements = production_global_resource_placements()

    assert len(placements) == 8
    assert placements[0].rom_start == GLOBAL_RESOURCE_REGION_START == 0x01000000
    assert placements[-1].rom_end_exclusive == GLOBAL_RESOURCE_REGION_END == 0x01800000
    assert GLOBAL_RESOURCE_REGION_END < GLOBAL_OUTPUT_SIZE == 0x02000000
    assert all(item.capacity == GLOBAL_RESOURCE_SLOT_SIZE == 0x00100000 for item in placements)
    assert [item.stage_id for item in placements] == [0, 1, 2, 3, 4, 5, 8, 9]
