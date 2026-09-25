"""Production runtime layout V2.

V2 preserves its runtime-confirmed first-1-KiB layout inside the larger
16 KiB MKMSZR reservation. The first 0x3B0 bytes are reloadable native payload
space and the next 0x50 bytes are persistent state. Bytes after 0x801AF820 are
owned by the separate expansion pool and are not implicitly part of Runtime V2.
"""

from __future__ import annotations

from ..data.addresses import (
    RUNTIME_V2_CODE_END_EXCLUSIVE,
    RUNTIME_V2_CODE_START,
    RUNTIME_V2_STATE_END_EXCLUSIVE,
    RUNTIME_V2_STATE_START,
)
from ..mips import Emitter, addiu, address_words, jr, lhu, lui, lw, ori, sh, sltiu, sw
from .native_payload import build_loader_and_call_stub, kseg1_alias

NOP = 0

CODE_CACHED_BASE = RUNTIME_V2_CODE_START
CODE_UNCACHED_BASE = kseg1_alias(CODE_CACHED_BASE)
CODE_SIZE = RUNTIME_V2_CODE_END_EXCLUSIVE - RUNTIME_V2_CODE_START

STATE_CACHED_BASE = RUNTIME_V2_STATE_START
STATE_UNCACHED_BASE = kseg1_alias(STATE_CACHED_BASE)
STATE_SIZE = RUNTIME_V2_STATE_END_EXCLUSIVE - RUNTIME_V2_STATE_START

STATE_MAGIC = 0x4D4B5356  # MKSV
STATE_VERSION = 2
STATE_HEADER_SIZE = 0x20
STATE_FLAGS_OFFSET = 0x10
STATE_SETTINGS_OFFSET = STATE_SIZE - 4
STATE_SETTINGS_MARKER = 0x5452  # TR
STATE_TURN_TOGGLE = 0
STATE_TURN_LOCK = 1

LOADER_STUB = build_loader_and_call_stub(payload_rdram=CODE_CACHED_BASE)


def _emit_u32(emitter: Emitter, rt: str, value: int) -> None:
    emitter.emit(lui(rt, value >> 16), ori(rt, rt, value & 0xFFFF))


def build_init() -> bytes:
    """Validate V2 state or initialize the persistent 0x100-byte tail."""

    emitter = Emitter()
    emitter.emit(*address_words("t0", STATE_UNCACHED_BASE))
    emitter.emit(lw("t1", 0x00, "t0"))
    _emit_u32(emitter, "t2", STATE_MAGIC)
    emitter.bne("t1", "t2", "initialize")
    emitter.emit(NOP)
    emitter.emit(lw("t1", 0x04, "t0"), addiu("t2", "zero", STATE_VERSION))
    emitter.bne("t1", "t2", "initialize")
    emitter.emit(NOP)
    emitter.emit(lw("t1", 0x08, "t0"), addiu("t2", "zero", STATE_SIZE))
    emitter.bne("t1", "t2", "initialize")
    emitter.emit(NOP)
    emitter.emit(lw("t1", 0x0C, "t0"), addiu("t2", "zero", STATE_HEADER_SIZE))
    emitter.bne("t1", "t2", "initialize")
    emitter.emit(NOP, jr("ra"), NOP)

    emitter.label("initialize")

    # GAME SETTINGS exists before the first stage/runtime initialization.
    # Preserve only a validated TURN preference across an otherwise-invalid
    # V2 run-state reset; everything else still clears exactly as before.
    emitter.emit(
        lhu("t5", STATE_SETTINGS_OFFSET, "t0"),
        lhu("t6", STATE_SETTINGS_OFFSET + 2, "t0"),
        addiu("t7", "zero", STATE_SETTINGS_MARKER),
    )
    emitter.bne("t6", "t7", "settings_default")
    emitter.emit(NOP)
    emitter.emit(sltiu("t7", "t5", 2))
    emitter.bne("t7", "zero", "settings_ready")
    emitter.emit(NOP)

    emitter.label("settings_default")
    emitter.emit(
        addiu("t5", "zero", STATE_TURN_TOGGLE),
        addiu("t6", "zero", STATE_SETTINGS_MARKER),
    )

    emitter.label("settings_ready")
    emitter.emit(addiu("t3", "t0", 0), addiu("t4", "zero", STATE_SIZE // 4))
    emitter.label("clear_loop")
    emitter.emit(sw("zero", 0, "t3"), addiu("t3", "t3", 4), addiu("t4", "t4", -1))
    emitter.bne("t4", "zero", "clear_loop")
    emitter.emit(NOP)
    _emit_u32(emitter, "t1", STATE_MAGIC)
    emitter.emit(sw("t1", 0x00, "t0"))
    emitter.emit(addiu("t1", "zero", STATE_VERSION), sw("t1", 0x04, "t0"))
    emitter.emit(addiu("t1", "zero", STATE_SIZE), sw("t1", 0x08, "t0"))
    emitter.emit(addiu("t1", "zero", STATE_HEADER_SIZE), sw("t1", 0x0C, "t0"))
    emitter.emit(
        sh("t5", STATE_SETTINGS_OFFSET, "t0"),
        sh("t6", STATE_SETTINGS_OFFSET + 2, "t0"),
        jr("ra"),
        NOP,
    )
    return emitter.finish()
