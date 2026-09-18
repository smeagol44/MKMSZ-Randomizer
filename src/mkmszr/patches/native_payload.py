"""Low-level native payload registration and execution bootstrap.

This module promotes the runtime-confirmed file-ID 0x1B loader/execution path into
reusable implementation infrastructure. It is intentionally not enabled by the
user-facing patch pipeline yet; a versioned 1 KiB runtime layout must be defined
before the real randomizer runtime is installed by default.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..data.addresses import (
    ARENA_POINTER_GLOBAL_VA,
    ARENA_START_PATCHES,
    ARENA_SYNC_VA,
    MKMSZR_FILE_ENTRY_ROM,
    MKMSZR_FILE_ID,
    NATIVE_BOOTSTRAP_HOOK_ROM,
    NATIVE_BOOTSTRAP_STUB_CAPACITY,
    NATIVE_BOOTSTRAP_STUB_ROM,
    NATIVE_BOOTSTRAP_STUB_VA,
    PROVEN_PAYLOAD_RDRAM,
    PROVEN_PAYLOAD_ROM,
    RAW_FILE_LOADER_VA,
    RESERVED_RDRAM_END_EXCLUSIVE,
    RESERVED_RDRAM_START,
)
from ..errors import PatchError
from ..mips import addiu, jal, jalr, jump, lui, lw, split_address, sw, words_blob
from ..rom import RomImage
from .base import PatchContext

NOP = 0
RAW_FILE_FLAG = 0
HOOK_EXPECTED = bytes.fromhex("27BDFFE8 3C02801B")


def kseg1_alias(address: int) -> int:
    if not 0x80000000 <= address < 0xA0000000:
        raise ValueError(f"expected KSEG0 address, got 0x{address:08X}")
    return address | 0x20000000


def _store_zero_absolute(base: str, address: int) -> tuple[int, int]:
    high, low = split_address(address)
    return lui(base, high), sw("zero", low, base)


def build_loader_and_call_stub(
    *,
    payload_rdram: int = PROVEN_PAYLOAD_RDRAM,
    clear_word_rdram: int | None = None,
) -> bytes:
    """Build the confirmed arena-reset -> loader -> uncached-call bootstrap.

    Supplying clear_word_rdram reproduces the execution proof's marker clear.
    Production state layout is deliberately left undefined until the next research
    checkpoint.
    """

    arena_high, arena_low = split_address(RESERVED_RDRAM_END_EXCLUSIVE)
    pointer_high, pointer_low = split_address(ARENA_POINTER_GLOBAL_VA)
    payload_high, payload_low = split_address(payload_rdram)
    uncached_payload = kseg1_alias(payload_rdram)
    uncached_high, uncached_low = split_address(uncached_payload)

    words = [
        addiu("sp", "sp", -0x18),
        lui("v0", arena_high),
        addiu("v0", "v0", arena_low),
        sw("ra", 0x10, "sp"),
        lui("a0", pointer_high),
        sw("v0", pointer_low, "a0"),
        jal(ARENA_SYNC_VA),
        NOP,
        addiu("a0", "zero", MKMSZR_FILE_ID),
        lui("a1", payload_high),
        addiu("a1", "a1", payload_low),
        jal(RAW_FILE_LOADER_VA),
        NOP,
    ]

    if clear_word_rdram is not None:
        words.extend(_store_zero_absolute("t0", kseg1_alias(clear_word_rdram)))

    words.extend(
        [
            lui("t9", uncached_high),
            addiu("t9", "t9", uncached_low),
            jalr("t9"),
            NOP,
            lw("ra", 0x10, "sp"),
            addiu("sp", "sp", 0x18),
            jr("ra"),
            NOP,
        ]
    )
    return words_blob(words)


@dataclass(frozen=True)
class NativePayloadSpec:
    payload: bytes
    rom_start: int = PROVEN_PAYLOAD_ROM
    rdram_start: int = PROVEN_PAYLOAD_RDRAM
    clear_word_rdram: int | None = None

    def __post_init__(self) -> None:
        if not self.payload:
            raise ValueError("native payload must not be empty")
        if self.rom_start & 3 or self.rdram_start & 3 or len(self.payload) & 3:
            raise ValueError("native payload ROM/RDRAM addresses and size must be 4-byte aligned")
        if not 0 <= self.rom_start < self.rom_start + len(self.payload) <= 0x01000000:
            raise ValueError("native payload must fit inside the 16 MiB ROM")
        if not (
            RESERVED_RDRAM_START
            <= self.rdram_start
            < self.rdram_start + len(self.payload)
            <= RESERVED_RDRAM_END_EXCLUSIVE
        ):
            raise ValueError("native payload must fit entirely inside the reserved 1 KiB block")
        if self.clear_word_rdram is not None:
            if self.clear_word_rdram & 3:
                raise ValueError("clear word address must be 4-byte aligned")
            if not (
                RESERVED_RDRAM_START
                <= self.clear_word_rdram
                <= RESERVED_RDRAM_END_EXCLUSIVE - 4
            ):
                raise ValueError("clear word must be inside the reserved 1 KiB block")
            payload_end = self.rdram_start + len(self.payload)
            clear_end = self.clear_word_rdram + 4
            if self.clear_word_rdram < payload_end and clear_end > self.rdram_start:
                raise ValueError("clear word must not overlap the loaded payload")


class NativePayloadPatch:
    """Install one raw file-table payload and the confirmed execution bootstrap."""

    name = "native-payload-bootstrap"

    def __init__(self, spec: NativePayloadSpec):
        self.spec = spec

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        for offset, (_expected, reserved_value) in ARENA_START_PATCHES.items():
            if rom.read_u32(offset) != reserved_value:
                raise PatchError(
                    "native payload bootstrap requires ArenaReservationPatch first; "
                    f"ROM 0x{offset:08X} is not reserved"
                )

        stub = build_loader_and_call_stub(
            payload_rdram=self.spec.rdram_start,
            clear_word_rdram=self.spec.clear_word_rdram,
        )
        if len(stub) > NATIVE_BOOTSTRAP_STUB_CAPACITY:
            raise PatchError("native bootstrap stub exceeds the confirmed code cave")

        payload_end_rom = self.spec.rom_start + len(self.spec.payload)
        rom.expect_bytes(MKMSZR_FILE_ENTRY_ROM, bytes(12))
        rom.expect_bytes(self.spec.rom_start, b"\xFF" * len(self.spec.payload))
        rom.expect_bytes(NATIVE_BOOTSTRAP_HOOK_ROM, HOOK_EXPECTED)
        rom.expect_bytes(
            NATIVE_BOOTSTRAP_STUB_ROM,
            bytes(NATIVE_BOOTSTRAP_STUB_CAPACITY),
        )

        rom.write_u32(MKMSZR_FILE_ENTRY_ROM + 0, self.spec.rom_start)
        rom.write_u32(MKMSZR_FILE_ENTRY_ROM + 4, payload_end_rom)
        rom.write_u32(MKMSZR_FILE_ENTRY_ROM + 8, RAW_FILE_FLAG)
        rom.write_bytes(self.spec.rom_start, self.spec.payload)
        rom.write_bytes(NATIVE_BOOTSTRAP_STUB_ROM, stub)
        rom.write_u32(NATIVE_BOOTSTRAP_HOOK_ROM + 0, jump(NATIVE_BOOTSTRAP_STUB_VA))
        rom.write_u32(NATIVE_BOOTSTRAP_HOOK_ROM + 4, NOP)

        notes = [
            (
                f"file ID 0x{MKMSZR_FILE_ID:02X}: ROM "
                f"0x{self.spec.rom_start:08X}..0x{payload_end_rom - 1:08X} -> "
                f"RDRAM 0x{self.spec.rdram_start:08X}"
            ),
            (
                f"uncached execution entry 0x{kseg1_alias(self.spec.rdram_start):08X}; "
                f"bootstrap stub {len(stub)} bytes"
            ),
        ]
        if self.spec.clear_word_rdram is not None:
            notes.append(f"clears reserved word 0x{self.spec.clear_word_rdram:08X} before call")
        return tuple(notes)
