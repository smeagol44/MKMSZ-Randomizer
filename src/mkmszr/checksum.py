"""Nintendo 64 CIC-NUS-6102 header checksum support."""


def _u32(data: bytes | bytearray, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def _rol32(value: int, shift: int) -> int:
    shift &= 31
    if shift == 0:
        return value & 0xFFFFFFFF
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


def calculate_crc_6102(data: bytes | bytearray) -> tuple[int, int]:
    """Return the N64 CRC1/CRC2 pair for CIC-NUS-6102."""

    if len(data) < 0x101000:
        raise ValueError("ROM buffer is too small for N64 checksum calculation")

    seed = 0xF8CA4DDC
    t1 = t2 = t3 = t4 = t5 = t6 = seed

    for offset in range(0x1000, 0x101000, 4):
        value = _u32(data, offset)
        total = (t6 + value) & 0xFFFFFFFF
        if total < t6:
            t4 = (t4 + 1) & 0xFFFFFFFF
        t6 = total
        t3 ^= value
        rotated = _rol32(value, value & 31)
        t5 = (t5 + rotated) & 0xFFFFFFFF
        t2 ^= rotated if t2 > value else (t6 ^ value)
        t1 = (t1 + (t5 ^ value)) & 0xFFFFFFFF

    return (t6 ^ t4 ^ t3) & 0xFFFFFFFF, (t5 ^ t2 ^ t1) & 0xFFFFFFFF
