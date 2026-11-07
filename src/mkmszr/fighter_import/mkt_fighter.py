"""Read-only MKT USA Rev. 2 N64 fighter reader (donor side of the importer).

Retail VA = ROM offset + 0x80000000 for the main executable. All tables below are
Static-confirmed against the exact Rev. 2 ROM; see Wiki ``MKT-Adapter-Primitives``
(Animation script grammar translation, Special-move command translation).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..donors.mkt_n64 import validate_mkt_n64_rev2
from .script import MKT, Region, decode_region

VA_BASE = 0x80000000
FIGHTER_NAME_TABLE = 0x800A6000  # 32 name pointers indexed by fighter ID
HEAP_TABLE = 0x800A247C  # (ROM start, ROM end) per fighter ID
DICT_TABLE = 0x800A257C  # (ROM start, ROM end) per fighter ID; follows HEAP_TABLE
FIGHTER_COUNT = 32
TABLE0_COUNT = 90  # get_char_ani 0x8000F910: table 1 at heap +0x168
TABLE1_OFFSET = 0x168
PRESS_GRID = 0x800A8780  # 10 event pointers -> 32-entry handler tables
RELEASE_GRID = 0x800A8AB8  # 6 event pointers
SPECIAL_TABLE = 0x800AB140  # 56 special-move routines, dispatched by 0x80076F70
SPECIAL_COUNT = 56
RECORD_PARSER = 0x8004BEB0  # declarative 0x2C-record parser
INLINE_MATCHER = 0x8004BFD4  # robot-style (mask, mask, compact table) matcher
INLINE_DISPATCH = 0x8004FDDC
SPECIAL_DISPATCH = 0x80076F70

ROBOT_HEAP_ROM = 0x008881C0
SEKTOR = 7


def _jal(target: int) -> int:
    return 0x0C000000 | ((target & 0x0FFFFFFF) >> 2)


@dataclass(frozen=True)
class FramePart:
    descriptor: int  # heap-relative descriptor offset
    image: int  # heap-relative image offset
    width: int
    height: int
    anchor_x: int
    anchor_y: int
    codec: int  # first byte of the image stream


@dataclass(frozen=True)
class CommandRecord:
    """A 0x2C special-move command record (same layout as the MKMSZ descriptor)."""

    masks: tuple[int, int]
    selector: int
    condition: int
    action: int
    window: int
    right: tuple[int, ...]  # newest-first direction tokens, zero-terminated
    left: tuple[int, ...]


@dataclass(frozen=True)
class InlineCommand:
    """A robot-style matcher call inside an imperative per-fighter handler."""

    mask: int
    table: int
    window: int
    right: tuple[int, ...]
    left: tuple[int, ...]
    dispatch: int | None  # wrapper passed to 0x8004FDDC
    special_id: int | None
    target: int | None  # routine the wrapper ends up calling
    argument: int | None  # immediate a0 passed by the wrapper (e.g. body-propell selector)


@dataclass(frozen=True)
class Handler:
    grid: str  # "press" or "release"
    event: int
    address: int
    records: tuple[CommandRecord, ...]  # declarative wrapper
    inline: tuple[InlineCommand, ...]  # imperative handler


class MktRom:
    def __init__(self, rom: bytes) -> None:
        validate_mkt_n64_rev2(rom)
        self.rom = rom

    # -- primitive reads ---------------------------------------------------
    def u32(self, va: int) -> int:
        offset = va - VA_BASE if va >= VA_BASE else va
        return int.from_bytes(self.rom[offset : offset + 4], "big")

    def u16(self, va: int) -> int:
        offset = va - VA_BASE
        return int.from_bytes(self.rom[offset : offset + 2], "big")

    def name(self, fighter: int) -> str:
        pointer = self.u32(FIGHTER_NAME_TABLE + 4 * fighter) - VA_BASE
        return self.rom[pointer : pointer + 16].split(b"\0")[0].decode("latin-1")

    # -- fighter heaps and scripts ------------------------------------------
    def heap(self, fighter: int) -> tuple[int, int]:
        return self.u32(HEAP_TABLE + 8 * fighter), self.u32(HEAP_TABLE + 8 * fighter + 4)

    def dictionary(self, fighter: int) -> tuple[int, int]:
        return self.u32(DICT_TABLE + 8 * fighter), self.u32(DICT_TABLE + 8 * fighter + 4)

    def heap_bytes(self, fighter: int) -> bytes:
        start, end = self.heap(fighter)
        return self.rom[start:end]

    def table0(self, fighter: int) -> list[int]:
        heap = self.heap_bytes(fighter)
        return [int.from_bytes(heap[4 * i : 4 * i + 4], "big") for i in range(TABLE0_COUNT)]

    def script_region(self, fighter: int) -> Region:
        heap = self.heap_bytes(fighter)
        roots = [r for r in self.table0(fighter) if r >= TABLE1_OFFSET]
        return decode_region(heap, min(roots), MKT)

    def table1(self, fighter: int) -> list[int]:
        """Secondary table; its length is bounded by the start of the scripts."""

        heap = self.heap_bytes(fighter)
        start = min(r for r in self.table0(fighter) if r >= TABLE1_OFFSET)
        count = (start - TABLE1_OFFSET) // 4
        return [
            int.from_bytes(heap[TABLE1_OFFSET + 4 * i : TABLE1_OFFSET + 4 * i + 4], "big")
            for i in range(count)
        ]

    def frame_parts(self, fighter: int, frame: int) -> tuple[FramePart, ...]:
        """Decode a frame record: zero-terminated heap-relative descriptor list."""

        heap = self.heap_bytes(fighter)
        parts = []
        cursor = frame
        while True:
            descriptor = int.from_bytes(heap[cursor : cursor + 4], "big")
            if descriptor == 0:
                break
            image = int.from_bytes(heap[descriptor : descriptor + 4], "big")
            packed = int.from_bytes(heap[descriptor + 4 : descriptor + 8], "big")
            anchor_x = int.from_bytes(heap[descriptor + 8 : descriptor + 10], "big", signed=True)
            anchor_y = int.from_bytes(heap[descriptor + 10 : descriptor + 12], "big", signed=True)
            parts.append(
                FramePart(
                    descriptor,
                    image,
                    packed & 0xFFFF,
                    packed >> 16,
                    anchor_x,
                    anchor_y,
                    heap[image],
                )
            )
            cursor += 4
            if len(parts) > 16:
                raise ValueError(f"frame 0x{frame:X} part list is not terminated")
        return tuple(parts)

    # -- special-move commands ------------------------------------------------
    def record(self, va: int) -> CommandRecord:
        def tokens(base: int, count: int) -> tuple[int, ...]:
            values = [self.u16(base + 2 * i) for i in range(count)]
            return tuple(values[: values.index(0)] if 0 in values else values)

        return CommandRecord(
            (self.u16(va), self.u16(va + 2)),
            self.u32(va + 4),
            self.u32(va + 8),
            self.u32(va + 0x0C),
            self.u16(va + 0x10),
            tokens(va + 0x12, 6),
            tokens(va + 0x1E, 7),
        )

    def record_table(self, va: int) -> tuple[CommandRecord, ...]:
        records = []
        while self.u16(va) != 0:
            records.append(self.record(va))
            va += 0x2C
            if len(records) > 32:
                raise ValueError("command table is not terminated")
        return tuple(records)

    def _wrapper_table(self, va: int) -> int | None:
        """Declarative wrapper: ``lui a0; jal 0x8004BEB0; addiu a0`` -> table VA."""

        for i in range(6):
            if self.u32(va + 4 * i) == _jal(RECORD_PARSER):
                hi, lo = self.u32(va + 4 * i - 4), self.u32(va + 4 * i + 4)
                if hi >> 16 == 0x3C04 and lo >> 16 == 0x2484:
                    return ((hi & 0xFFFF) << 16) + ((lo & 0xFFFF) ^ 0x8000) - 0x8000
        return None

    def _call_target(self, wrapper: int) -> tuple[int | None, int | None, int | None]:
        """Resolve a small wrapper to (special_id, called routine, immediate argument)."""

        for i in range(6):
            word = self.u32(wrapper + 4 * i)
            if word >> 26 == 3:
                target = (word & 0x03FFFFFF) << 2 | (wrapper & 0xF0000000)
                delay = self.u32(wrapper + 4 * i + 4)
                imm = delay & 0xFFFF if delay >> 16 == 0x2404 else None
                if target == SPECIAL_DISPATCH and imm is not None:
                    return imm, self.u32(SPECIAL_TABLE + 4 * imm), imm
                return None, target, imm
        return None, None, None

    def _inline_commands(self, handler: int) -> tuple[InlineCommand, ...]:
        """Pair each inline matcher call with the next 0x8004FDDC dispatch."""

        out: list[InlineCommand] = []
        regs: dict[int, int] = {}
        pending: tuple[int, int] | None = None
        va = handler
        for _ in range(400):
            word = self.u32(va)
            op, rs, rt, imm = word >> 26, (word >> 21) & 31, (word >> 16) & 31, word & 0xFFFF
            simm = imm - 0x10000 if imm & 0x8000 else imm
            if op == 0x0F:
                regs[rt] = imm << 16
            elif op == 0x09:
                regs[rt] = (regs.get(rs, 0) + simm) & 0xFFFFFFFF if rs else simm & 0xFFFFFFFF
            if word == _jal(INLINE_MATCHER) or word == _jal(INLINE_DISPATCH):
                delay = self.u32(va + 4)
                if delay >> 26 == 0x09:  # delay-slot addiu
                    d_rs, d_rt = (delay >> 21) & 31, (delay >> 16) & 31
                    d_imm = (delay & 0xFFFF) - 0x10000 if delay & 0x8000 else delay & 0xFFFF
                    regs[d_rt] = (regs.get(d_rs, 0) + d_imm) & 0xFFFFFFFF if d_rs else d_imm
                if word == _jal(INLINE_MATCHER):
                    pending = (regs.get(4, 0), regs.get(6, 0))
                elif pending is not None:
                    mask, table = pending
                    special, target, argument = self._call_target(regs.get(5, 0))
                    out.append(
                        InlineCommand(
                            mask,
                            table,
                            self.u16(table),
                            self._compact_tokens(table + 2),
                            self._compact_tokens(table + 14),
                            regs.get(5),
                            special,
                            target,
                            argument,
                        )
                    )
                    pending = None
            # jr ra followed (after its delay slot) by the next function's prologue
            if (
                word == 0x03E00008
                and va > handler + 8
                and pending is None
                and self.u32(va + 8) & 0xFFFF0000 == 0x27BD0000
            ):
                break
            va += 4
        return tuple(out)

    def _compact_tokens(self, va: int) -> tuple[int, ...]:
        values = [self.u16(va + 2 * i) for i in range(6)]
        return tuple(values[: values.index(0)] if 0 in values else values)

    def handlers(self, fighter: int) -> tuple[Handler, ...]:
        result = []
        for grid, base, count in (("press", PRESS_GRID, 10), ("release", RELEASE_GRID, 6)):
            for event in range(count):
                table = self.u32(base + 4 * event)
                address = self.u32(table + 4 * fighter)
                if not address:
                    continue
                wrapped = self._wrapper_table(address)
                if wrapped is not None:
                    result.append(Handler(grid, event, address, self.record_table(wrapped), ()))
                else:
                    result.append(Handler(grid, event, address, (), self._inline_commands(address)))
        return tuple(result)
