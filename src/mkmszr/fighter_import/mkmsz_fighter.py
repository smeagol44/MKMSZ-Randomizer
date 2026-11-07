"""MKMSZ fighter resource model (global fighter file ``0x87``).

Layout (Static-confirmed, clean USA Rev. 0): primary animation table 0 has 65
words at ``+0x000``, secondary table 1 has 43 words at ``+0x104``, and the script
region starts at ``+0x1B0``. Table-0 index ``0x41+n`` aliases table-1 index ``n``.
Frame records and image data follow the scripts and are carried verbatim here.
"""

from __future__ import annotations

from dataclasses import dataclass

from .script import MKMSZ, Region, assemble, decode_region

FILE_TABLE_ENTRY_ROM = 0x000A5664  # (start, end) ROM offsets of global file 0x87
CLEAN_FILE87_ROM = 0x00748920
CLEAN_FILE87_END = 0x0078E300
TABLE0_COUNT = 0x41
TABLE1_OFFSET = 0x104
TABLE1_COUNT = 43
SCRIPT_START = TABLE1_OFFSET + 4 * TABLE1_COUNT  # 0x1B0


def _be32(data: bytes | bytearray, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def file87_range(rom: bytes | bytearray) -> tuple[int, int]:
    """ROM (start, end) of fighter file 0x87 as published by the file table."""

    return _be32(rom, FILE_TABLE_ENTRY_ROM), _be32(rom, FILE_TABLE_ENTRY_ROM + 4)


@dataclass
class SlotEntry:
    """A slot-table word: 0, a script label, or a raw offset outside the region."""

    value: int
    label: str | None


@dataclass
class FighterFile:
    data: bytes
    table0: list[SlotEntry]
    table1: list[SlotEntry]
    region: Region

    @classmethod
    def parse(cls, data: bytes) -> FighterFile:
        region = decode_region(data, SCRIPT_START, MKMSZ)

        def entry(value: int) -> SlotEntry:
            if value and region.start <= value < region.end:
                return SlotEntry(value, region.label_at(value))
            return SlotEntry(value, None)

        table0 = [entry(_be32(data, 4 * i)) for i in range(TABLE0_COUNT)]
        table1 = [entry(_be32(data, TABLE1_OFFSET + 4 * i)) for i in range(TABLE1_COUNT)]
        return cls(data, table0, table1, region)

    @classmethod
    def from_rom(cls, rom: bytes | bytearray) -> FighterFile:
        start, end = file87_range(rom)
        return cls.parse(bytes(rom[start:end]))

    def slot(self, table: int, index: int) -> SlotEntry:
        """Resolve a selector the way ``0x8002FE54`` does (table-0 aliases table 1)."""

        if table == 0 and index >= TABLE0_COUNT:
            table, index = 1, index - TABLE0_COUNT
        return (self.table0 if table == 0 else self.table1)[index]

    def encode(self) -> bytes:
        """Re-assemble tables + scripts, then append the verbatim tail."""

        blob, labels = assemble(self.region.insns, self.region.labels, SCRIPT_START)
        if SCRIPT_START + len(blob) != self.region.end:
            raise ValueError("script region changed size; relocation of the tail is not supported")

        def word(e: SlotEntry) -> bytes:
            value = labels[e.label] if e.label else e.value
            return value.to_bytes(4, "big")

        head = b"".join(word(e) for e in self.table0)
        head += self.data[4 * TABLE0_COUNT : TABLE1_OFFSET]
        head += b"".join(word(e) for e in self.table1)
        return head + blob + self.data[self.region.end :]
