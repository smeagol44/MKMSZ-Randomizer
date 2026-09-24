"""Disposable control-facing proof using the 16 KiB expansion pool.

This proof deliberately layers after the normal production pipeline. It proves
two things together:

1. a second raw native file can be loaded into the build-time expansion pool
   without touching Runtime V2 persistent state; and
2. normal horizontal locomotion can use "direction = facing" by default while
   held Turn/Combine preserves vanilla backward walking.

The proof is intentionally not part of the browser/CLI production pipeline.
Runtime validation is required before any product integration.
"""

from __future__ import annotations

from ..allocations import ExpansionPoolAllocator
from ..data.addresses import (
    FILE_TABLE_ENTRY_SIZE,
    FILE_TABLE_ROM,
    RAW_FILE_LOADER_VA,
    RUNTIME_V2_CODE_START,
)
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    address_words,
    andi,
    jal,
    jalr,
    jr,
    lui,
    lw,
    ori,
    sh,
    sw,
    words_blob,
)
from ..rom import RomImage
from .base import PatchContext
from .native_payload import kseg1_alias
from .pickup_persistence import (
    CAPTURE_HELPER,
    CAPTURE_HELPER_ROM,
    CAPTURE_HELPER_VA,
    DESCRIPTOR_TABLE_ROM,
)
from .runtime_v2 import CODE_UNCACHED_BASE, LOADER_STUB

NOP = 0

# Proof-only transport. File 0x1A is zero in the supported clean table and was
# already exercised as the v39 expansion-file transport. v39 failed because it
# executed freshly loaded code through KSEG0, not because the raw load itself
# failed. This proof executes every expansion entry through KSEG1.
EXPANSION_FILE_ID = 0x1A
EXPANSION_FILE_ENTRY_ROM = FILE_TABLE_ROM + EXPANSION_FILE_ID * FILE_TABLE_ENTRY_SIZE
EXPANSION_MODULE_ROM = 0x00F72000

# Shared remapping-aware player semantic input.
PLAYER_SEMANTIC_INPUT_VA = 0x800BF2EE
TURN_MASK = 0x0001

# Current controller/process global.
CURRENT_CONTROLLER_PTR_VA = 0x802FCE20

# Host helpers established by the control trace.
FACE_POLICY_SCANNER_VA = 0x8004A6E8
FACING_FLIP_VA = 0x8003188C

# Locomotion patch sites.
DECISION_HOOK_ROM = 0x00029FB0
DECISION_HOOK_VA = 0x800293B0
DECISION_RESUME_VA = 0x800293B8
DECISION_EXPECTED = bytes.fromhex("8C640704 24020305")

RELEASE_HOOK_ROM = 0x0002A0DC
RELEASE_HOOK_VA = 0x800294DC
RELEASE_RESUME_VA = 0x800294E4
RELEASE_EXPECTED = bytes.fromhex("8C820638 94430000")

TURN_HOOK_ROM = 0x0003E46C
TURN_HOOK_VA = 0x8003D86C
TURN_STOCK_RESUME_VA = 0x8003D874
TURN_EXPECTED = bytes.fromhex("27BDFFE0 24040001")

# Bootstrap modification: replace only the existing two-word KSEG1 Runtime V2
# address construction. The following stock/proven JALR remains unchanged.
BOOTSTRAP_RUNTIME_ENTRY_WORDS_OFFSET = 0x34

# The static pickup-capture helper occupies the exact gap between the Runtime
# V2 restore trampoline and descriptor table. The proof moves that helper into
# the expansion module and reuses its former static footprint only for a small
# loader and KSEG0 -> KSEG1 trampolines.
STATIC_REGION_ROM = CAPTURE_HELPER_ROM
STATIC_REGION_VA = CAPTURE_HELPER_VA
STATIC_REGION_END_ROM = DESCRIPTOR_TABLE_ROM
STATIC_REGION_SIZE = STATIC_REGION_END_ROM - STATIC_REGION_ROM


def _align(value: int, alignment: int = 16) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def _indirect_jump(target: int) -> bytes:
    return words_blob([*address_words("t9", target), jr("t9"), NOP])


def build_expansion_loader(static_va: int) -> bytes:
    """Load file 0x1A to the expansion pool, then restore Runtime V2 T9."""

    del static_va
    pool_start = CONTROL_MODULE_CACHED_BASE
    high, low = ((pool_start + 0x8000) >> 16) & 0xFFFF, pool_start & 0xFFFF

    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x18),
        sw("ra", 0x10, "sp"),
        addiu("a0", "zero", EXPANSION_FILE_ID),
        lui("a1", high),
        jal(RAW_FILE_LOADER_VA),
        addiu("a1", "a1", low),
        *address_words("t9", CODE_UNCACHED_BASE),
        lw("ra", 0x10, "sp"),
        addiu("sp", "sp", 0x18),
        jr("ra"),
        NOP,
    )
    return e.finish()


def build_decision_helper() -> bytes:
    """Return stock branch operands, optionally flipping to requested direction."""

    e = Emitter()

    # Mid-function hook: preserve every volatile register that the displaced
    # two stock instructions did not modify.
    e.emit(
        addiu("sp", "sp", -0x40),
        sw("v1", 0x00, "sp"),
        sw("a1", 0x04, "sp"),
        sw("a2", 0x08, "sp"),
        sw("a3", 0x0C, "sp"),
        sw("t0", 0x10, "sp"),
        sw("t1", 0x14, "sp"),
        sw("t2", 0x18, "sp"),
        sw("t3", 0x1C, "sp"),
        sw("t4", 0x20, "sp"),
        sw("t5", 0x24, "sp"),
        sw("t6", 0x28, "sp"),
        sw("t7", 0x2C, "sp"),
        sw("t8", 0x30, "sp"),
        sw("t9", 0x34, "sp"),
        sw("ra", 0x38, "sp"),
    )

    # First displaced instruction and a scratch copy of the mismatch.
    e.emit(lw("a0", 0x704, "v1"), sw("a0", 0x3C, "sp"))
    e.beq("a0", "zero", "finish")
    e.emit(NOP)

    # Held Turn/Combine intentionally preserves stock backward locomotion.
    e.emit(lw("t0", 0x638, "v1"), lhu("t1", 0, "t0"), andi("t1", "t1", TURN_MASK))
    e.bne("t1", "zero", "restore_mismatch")
    e.emit(NOP)

    # Fail closed around stock forced-facing policy. This helper has no args.
    e.emit(*address_words("t9", FACE_POLICY_SCANNER_VA), jalr("t9"), NOP)
    e.emit(ori("t0", "zero", 0x8000))
    e.bne("v0", "t0", "flip")
    e.emit(NOP)

    e.label("restore_mismatch")
    e.emit(lw("a0", 0x3C, "sp"))
    e.beq("zero", "zero", "finish")
    e.emit(NOP)

    e.label("flip")
    # Use the stock facing primitive through an indirect KSEG1 -> KSEG0 call.
    e.emit(*address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"))
    e.emit(lw("a0", 0x6E0, "t0"))
    e.emit(*address_words("t9", FACING_FLIP_VA), jalr("t9"), NOP)

    # Recompute the stock branch operand as forward-compatible after the flip.
    e.emit(*address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"))
    e.emit(sw("zero", 0x704, "t0"), addiu("a0", "zero", 0))

    e.label("finish")
    # Second displaced instruction.
    e.emit(addiu("v0", "zero", 0x305))

    e.emit(
        lw("v1", 0x00, "sp"),
        lw("a1", 0x04, "sp"),
        lw("a2", 0x08, "sp"),
        lw("a3", 0x0C, "sp"),
        lw("t0", 0x10, "sp"),
        lw("t1", 0x14, "sp"),
        lw("t2", 0x18, "sp"),
        lw("t3", 0x1C, "sp"),
        lw("t4", 0x20, "sp"),
        lw("t5", 0x24, "sp"),
        lw("t6", 0x28, "sp"),
        lw("t7", 0x2C, "sp"),
        lw("t8", 0x30, "sp"),
        lw("t9", 0x34, "sp"),
        lw("ra", 0x38, "sp"),
        addiu("sp", "sp", 0x40),
        jr("ra"),
        NOP,
    )
    return e.finish()


def build_release_helper() -> bytes:
    """Exit an active backward walk as soon as Turn is released."""

    e = Emitter()
    # Reproduce the two displaced stock instructions.
    e.emit(lw("v0", 0x638, "a0"), lhu("v1", 0, "v0"))

    # controller+0x6FC == 2 is the stock backward locomotion mode.
    e.emit(lw("v0", 0x6FC, "a0"), addiu("v0", "v0", -2))
    e.bne("v0", "zero", "return")
    e.emit(NOP)

    # If Turn remains held, stock continues the backward walk.
    e.emit(andi("v0", "v1", TURN_MASK))
    e.bne("v0", "zero", "return")
    e.emit(NOP)

    # Otherwise make the immediately following stock active-direction test fail.
    e.emit(addiu("v1", "zero", 0))

    e.label("return")
    e.emit(jr("ra"), NOP)
    return e.finish()


def build_turn_gate_helper() -> bytes:
    """Suppress standalone Turn only for the real player semantic controller."""

    e = Emitter()
    e.emit(*address_words("t0", CURRENT_CONTROLLER_PTR_VA), lw("t0", 0, "t0"))
    e.beq("t0", "zero", "stock")
    e.emit(NOP)

    e.emit(lw("t1", 0x638, "t0"), *address_words("t2", PLAYER_SEMANTIC_INPUT_VA))
    e.bne("t1", "t2", "stock")
    e.emit(NOP)

    # Player Turn becomes a held facing-lock modifier; inventory Combine is a
    # separate consumer and never reaches this gameplay action routine.
    e.emit(jr("ra"), NOP)

    e.label("stock")
    # Reproduce the two displaced prologue words and resume stock Turn.
    e.emit(addiu("sp", "sp", -0x20), addiu("a0", "zero", 1))
    e.emit(*address_words("t9", TURN_STOCK_RESUME_VA), jr("t9"), NOP)
    return e.finish()


def _pack_module() -> tuple[bytes, dict[str, int]]:
    routines = [
        ("capture", CAPTURE_HELPER),
        ("decision", build_decision_helper()),
        ("release", build_release_helper()),
        ("turn_gate", build_turn_gate_helper()),
    ]

    blob = bytearray()
    offsets: dict[str, int] = {}
    for name, routine in routines:
        aligned = _align(len(blob))
        blob.extend(bytes(aligned - len(blob)))
        offsets[name] = aligned
        blob.extend(routine)

    return bytes(blob), offsets


CONTROL_MODULE, CONTROL_MODULE_OFFSETS = _pack_module()

_pool = ExpansionPoolAllocator()
CONTROL_ALLOCATION = _pool.allocate("control-facing-proof", len(CONTROL_MODULE), align=16)
CONTROL_MODULE_CACHED_BASE = CONTROL_ALLOCATION.start
CONTROL_MODULE_UNCACHED_BASE = kseg1_alias(CONTROL_MODULE_CACHED_BASE)

CAPTURE_ENTRY = CONTROL_MODULE_UNCACHED_BASE + CONTROL_MODULE_OFFSETS["capture"]
DECISION_ENTRY = CONTROL_MODULE_UNCACHED_BASE + CONTROL_MODULE_OFFSETS["decision"]
RELEASE_ENTRY = CONTROL_MODULE_UNCACHED_BASE + CONTROL_MODULE_OFFSETS["release"]
TURN_GATE_ENTRY = CONTROL_MODULE_UNCACHED_BASE + CONTROL_MODULE_OFFSETS["turn_gate"]


def _pack_static_region() -> tuple[bytes, dict[str, int]]:
    pieces: list[tuple[str, bytes]] = []

    # build_expansion_loader reads CONTROL_MODULE_CACHED_BASE, which is fixed by
    # the allocator above before this routine is invoked.
    pieces.append(("loader", build_expansion_loader(STATIC_REGION_VA)))
    pieces.extend(
        [
            ("capture_trampoline", _indirect_jump(CAPTURE_ENTRY)),
            ("decision_trampoline", _indirect_jump(DECISION_ENTRY)),
            ("release_trampoline", _indirect_jump(RELEASE_ENTRY)),
            ("turn_trampoline", _indirect_jump(TURN_GATE_ENTRY)),
        ]
    )

    blob = bytearray()
    offsets: dict[str, int] = {}
    for name, piece in pieces:
        aligned = _align(len(blob))
        blob.extend(bytes(aligned - len(blob)))
        offsets[name] = aligned
        blob.extend(piece)

    if len(blob) > STATIC_REGION_SIZE:
        raise AssertionError("control proof static loader/trampolines exceed repurposed helper region")
    blob.extend(bytes(STATIC_REGION_SIZE - len(blob)))
    return bytes(blob), offsets


STATIC_REGION_BLOB, STATIC_OFFSETS = _pack_static_region()

EXPANSION_LOADER_VA = STATIC_REGION_VA + STATIC_OFFSETS["loader"]
CAPTURE_TRAMPOLINE_VA = STATIC_REGION_VA + STATIC_OFFSETS["capture_trampoline"]
DECISION_TRAMPOLINE_VA = STATIC_REGION_VA + STATIC_OFFSETS["decision_trampoline"]
RELEASE_TRAMPOLINE_VA = STATIC_REGION_VA + STATIC_OFFSETS["release_trampoline"]
TURN_TRAMPOLINE_VA = STATIC_REGION_VA + STATIC_OFFSETS["turn_trampoline"]


class ControlFacingExpansionProofPatch:
    """Install the production-composition control-facing expansion proof."""

    name = "control-facing-expansion-proof"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        # The proof must layer after current pickup persistence.
        rom.expect_bytes(STATIC_REGION_ROM, CAPTURE_HELPER)

        # File 0x1A and the proof-only high-ROM source must still be untouched.
        rom.expect_bytes(EXPANSION_FILE_ENTRY_ROM, bytes(FILE_TABLE_ENTRY_SIZE))
        rom.expect_bytes(EXPANSION_MODULE_ROM, b"\xFF" * len(CONTROL_MODULE))

        # Verify the two bootstrap words we replace are still exactly the
        # established Runtime V2 uncached-entry construction.
        runtime_entry_words = words_blob(address_words("t9", CODE_UNCACHED_BASE))
        bootstrap_patch_rom = (
            0x0009AD84 + BOOTSTRAP_RUNTIME_ENTRY_WORDS_OFFSET
        )
        rom.expect_bytes(bootstrap_patch_rom, runtime_entry_words)

        # Current production capture hook and untouched control seams.
        from .pickup_persistence import PICKUP_MANAGER_CAPTURE_HOOK_ROM
        from ..data.addresses import PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED

        rom.expect_u32(PICKUP_MANAGER_CAPTURE_HOOK_ROM, jal(CAPTURE_HELPER_VA))
        rom.expect_u32(
            PICKUP_MANAGER_CAPTURE_HOOK_ROM + 4,
            PICKUP_MANAGER_CAPTURE_DELAY_EXPECTED,
        )
        rom.expect_bytes(DECISION_HOOK_ROM, DECISION_EXPECTED)
        rom.expect_bytes(RELEASE_HOOK_ROM, RELEASE_EXPECTED)
        rom.expect_bytes(TURN_HOOK_ROM, TURN_EXPECTED)

        # Register and store the expansion module.
        module_end = EXPANSION_MODULE_ROM + len(CONTROL_MODULE)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 0, EXPANSION_MODULE_ROM)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, module_end)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)
        rom.write_bytes(EXPANSION_MODULE_ROM, CONTROL_MODULE)

        # Replace the old static capture helper with the bounded loader and four
        # KSEG0 trampolines. Descriptor/translation/mapper data after this range
        # remain untouched.
        rom.write_bytes(STATIC_REGION_ROM, STATIC_REGION_BLOB)

        # Bootstrap now loads file 0x1A, returns T9 = Runtime V2 KSEG1 entry,
        # then falls through to the already-existing JALR.
        rom.write_u32(bootstrap_patch_rom, jal(EXPANSION_LOADER_VA))
        rom.write_u32(bootstrap_patch_rom + 4, NOP)

        # Pickup persistence capture is semantically unchanged; only its helper
        # transport moves into the expansion module.
        rom.write_u32(
            PICKUP_MANAGER_CAPTURE_HOOK_ROM,
            jal(CAPTURE_TRAMPOLINE_VA),
        )

        # Normal movement: helper returns A0 mismatch / V0 animation token, then
        # stock code at +8 continues unchanged.
        rom.write_u32(DECISION_HOOK_ROM, jal(DECISION_TRAMPOLINE_VA))
        rom.write_u32(DECISION_HOOK_ROM + 4, NOP)

        # Active backward movement: release Turn -> fail stock held-direction
        # test -> re-enter locomotion and take the auto-facing path.
        rom.write_u32(RELEASE_HOOK_ROM, jal(RELEASE_TRAMPOLINE_VA))
        rom.write_u32(RELEASE_HOOK_ROM + 4, NOP)

        # Standalone gameplay Turn becomes a modifier-only action for the player.
        # Use J rather than JAL so the caller's RA survives function entry.
        from ..mips import jump

        rom.write_u32(TURN_HOOK_ROM, jump(TURN_TRAMPOLINE_VA))
        rom.write_u32(TURN_HOOK_ROM + 4, NOP)

        return (
            (
                f"file 0x{EXPANSION_FILE_ID:02X} -> "
                f"0x{CONTROL_MODULE_CACHED_BASE:08X}, {len(CONTROL_MODULE)} bytes"
            ),
            (
                "default horizontal input flips through native 0x8003188C and "
                "continues through stock forward/run locomotion"
            ),
            "held Turn keeps vanilla backward walk; release Turn exits backward mode",
            "inventory Combine remains on the untouched semantic 0x0001 consumer",
            "stock +0x6BC/0x0200 forced-facing policy is left authoritative",
            "Earth special boss remains an explicit runtime observation, not hard-coded",
        )
