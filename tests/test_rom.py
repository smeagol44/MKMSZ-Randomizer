from mkmszr.rom import RomImage, _changed_spans


def test_changed_spans_groups_adjacent_bytes() -> None:
    before = bytes([0, 0, 0, 0, 0, 0, 0])
    after = bytes([0, 1, 2, 0, 0, 3, 0])
    assert _changed_spans(before, after) == ((1, 3), (5, 6))



def test_changed_spans_reports_appended_output_region() -> None:
    before = bytes([1, 2, 3])
    after = bytes([1, 2, 3, 0xFF, 0xFF])
    assert _changed_spans(before, after) == ((3, 5),)


def test_rom_output_can_expand_without_relaxing_input_validation() -> None:
    source = bytearray(16 * 1024 * 1024)
    source[:4] = bytes.fromhex("80371240")
    rom = RomImage(bytearray(source), bytes(source))

    rom.expand_output(32 * 1024 * 1024)

    assert len(rom.data) == 32 * 1024 * 1024
    assert rom.data[0x01000000:] == b"\xFF" * (16 * 1024 * 1024)
    assert rom.changed_spans() == ((0x01000000, 0x02000000),)
