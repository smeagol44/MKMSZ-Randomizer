from mkmszr.checksum import calculate_crc_6102


def test_crc_6102_zero_vector() -> None:
    data = bytearray(0x101000)
    assert calculate_crc_6102(data) == (0xF8CA4DDC, 0x303A4DDC)


def test_crc_6102_incrementing_vector() -> None:
    data = bytearray(index & 0xFF for index in range(0x101000))
    assert calculate_crc_6102(data) == (0xFAC847DA, 0xB2DEA121)
