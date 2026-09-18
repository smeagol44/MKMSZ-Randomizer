"""Experimental four-box native inventory switcher.

This first four-box checkpoint deliberately proves only the runtime switching
mechanism. It keeps the game's native ten live slots as the active window,
stores four ten-word boxes in the already-researched 168-byte main-image data
region, and uses the previously runtime-proven remapping-aware
Block + Use + Left/Right chord outside the inventory menu.

Transition synchronization/default-loader/sanitizer changes are intentionally
deferred until this bounded switching proof succeeds.
"""

from __future__ import annotations

from ..data.addresses import NATIVE_BOOTSTRAP_STUB_ROM, NATIVE_BOOTSTRAP_STUB_VA
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    addu,
    andi,
    jal,
    jump,
    lbu,
    lhu,
    lui,
    lw,
    or_,
    ori,
    sh,
    sll,
    srl,
    subu,
    sw,
    words_blob,
)
from ..rom import RomImage
from .base import PatchContext
from .stage_selector import (
    MAPPER_CAVE_END,
    MAPPER_ROM,
    MAPPER_VA,
    SELECTION_LOAD_ROM,
    build_selection_mapper,
)

NOP = 0

# The previously researched 168-byte inventory backing region.
BOX0_VA = 0x800A6048
BOX1_VA = 0x800A6070
BOX2_VA = 0x800A6098
BOX3_VA = 0x800A60C0
STATE_VA = 0x800A60E8
MAGIC_VA = 0x800A60EC
MAGIC = 0x4D4B4258  # MKBX
LIVE_INV_VA = 0x800A600C

BOX_DATA_ROM = 0x000A6C48
BOX_DATA_SIZE = 0xA8
DEFAULT_INV_ROM = 0x000A6BE4
DEFAULT_INV = words_blob(
    [0x00000004, 0x00000004, 0x00000001] + [0xFFFFFFFF] * 7
)

# Common point immediately after both configurable-control paths converge.
ACTION_HOOK_ROM = 0x0001674C
ACTION_HOOK_CONTINUE_VA = 0x80015B54
EXPECTED_ACTION_HOOK = bytes.fromhex("3C03802F 9463CE18")

ACTION_INPUT_VA = 0x800BF2EE
INVENTORY_OPEN_VA = 0x800A5FA3
USE_MASK = 0x0002
BLOCK_MASK = 0x0008
RIGHT_MASK = 0x2000
LEFT_MASK = 0x8000
CHORD_ACTION_MASK = USE_MASK | BLOCK_MASK
CHORD_DIRECTION_MASK = RIGHT_MASK | LEFT_MASK
CHORD_CLEAR_MASK = (~(CHORD_ACTION_MASK | CHORD_DIRECTION_MASK)) & 0xFFFF
LATCH_MASK = 0x0100

# Reuse only regions that already have inventory/stage-selector research behind
# them. The old 412-byte inventory cave is now occupied by MKMSZR bootstrap and
# pickup persistence, so the stage-selector mapper is moved into its confirmed
# 36-byte free tail and the selector's former 144-byte cave becomes available.
SELECTOR_CAVE_ROM = 0x0009A6C8
SELECTOR_CAVE_VA = 0x80099AC8
SELECTOR_CAVE_SIZE = MAPPER_CAVE_END - SELECTOR_CAVE_ROM

SECONDARY_CAVE_ROM = 0x0008F6E8
SECONDARY_CAVE_VA = 0x8008EAE8
SECONDARY_CAVE_SIZE = 0x68

RELOCATED_MAPPER_VA = 0x8009A2FC
RELOCATED_MAPPER_ROM = NATIVE_BOOTSTRAP_STUB_ROM + (
    RELOCATED_MAPPER_VA - NATIVE_BOOTSTRAP_STUB_VA
)

ACTION_ROUTINE_VA = SECONDARY_CAVE_VA
SWITCH_HELPER_VA = SELECTOR_CAVE_VA


def _move(rd: str, rs: str) -> int:
    return addu(rd, rs, "zero")


def build_copy10(copy_va: int) -> bytes:
    """Copy ten 32-bit words from A0 to A1; clobbers T5/T6 and A0/A1."""

    del copy_va
    e = Emitter()
    e.emit(addiu("t5", "zero", 10))
    e.label("loop")
    e.emit(lw("t6", 0, "a0"), sw("t6", 0, "a1"))
    e.emit(addiu("a0", "a0", 4), addiu("t5", "t5", -1))
    e.bne("t5", "zero", "loop")
    e.emit(addiu("a1", "a1", 4))
    e.emit(0x03E00008, NOP)  # jr ra
    return e.finish()


def build_switch_helper(base_va: int, copy_va: int, action_done_va: int) -> bytes:
    """Save current box, select left/right neighbor, then load the new box.

    Entry contract from the action hook:
      T0 = STATE_VA
      T1 = current state word
      A0 = semantic direction mask (LEFT or RIGHT)
    The routine intentionally jumps directly to the action hook's fixed done
    label after the second copy; its incoming RA is not needed.
    """

    del base_va
    e = Emitter()

    # Preserve direction across the first copy and compute current box pointer:
    # BOX0 + index*40 = BOX0 + index*(32+8).
    e.emit(_move("t7", "a0"), andi("t2", "t1", 3))
    e.emit(sll("t3", "t2", 5), sll("t4", "t2", 3), addu("t3", "t3", "t4"))
    e.emit(addiu("a1", "t0", BOX0_VA - STATE_VA), addu("a1", "a1", "t3"))
    e.emit(jal(copy_va), addiu("a0", "t0", LIVE_INV_VA - STATE_VA))

    # Right = +1, Left = -1, modulo four. Bit 15 is set only for Left after
    # the action hook rejects the both-directions case.
    e.emit(srl("t4", "t7", 15), sll("t4", "t4", 1))
    e.emit(addiu("t2", "t2", 1), subu("t2", "t2", "t4"), andi("t2", "t2", 3))

    # During an accepted held chord the state contains only index + latch.
    e.emit(ori("t1", "t2", LATCH_MASK), sw("t1", 0, "t0"))

    # Compute selected box pointer and restore it into the native live window.
    e.emit(sll("t3", "t2", 5), sll("t4", "t2", 3), addu("t3", "t3", "t4"))
    e.emit(addiu("a0", "t0", BOX0_VA - STATE_VA), addu("a0", "a0", "t3"))
    e.emit(jal(copy_va), addiu("a1", "t0", LIVE_INV_VA - STATE_VA))

    # This helper is only called by the fixed action hook.
    e.emit(jump(action_done_va), NOP)
    return e.finish()


def build_action_routine(base_va: int, helper_va: int) -> tuple[bytes, int]:
    """Build the remapping-aware four-box gameplay chord hook."""

    e = Emitter()

    # STATE/MKBX is ROM-preinitialized for this bounded proof.
    e.emit(lui("t0", 0x800A), addiu("t0", "t0", STATE_VA & 0xFFFF), lw("t1", 0, "t0"))

    # Never swap while the native inventory cursor is active.
    e.emit(lbu("t3", INVENTORY_OPEN_VA - STATE_VA, "t0"))
    e.bne("t3", "zero", "done")
    e.emit(lui("t7", 0x800C))

    # Read remapping-aware semantic actions.
    e.emit(lhu("t6", ACTION_INPUT_VA - 0x800C0000, "t7"))
    e.emit(andi("t3", "t6", CHORD_ACTION_MASK), addiu("t4", "zero", CHORD_ACTION_MASK))
    e.bne("t3", "t4", "release")
    e.emit(andi("t2", "t6", CHORD_DIRECTION_MASK))

    # Require exactly one direction. Both Left+Right is ignored safely.
    e.beq("t2", "zero", "release")
    e.emit(ori("t3", "zero", CHORD_DIRECTION_MASK))
    e.beq("t2", "t3", "release")
    e.emit(andi("t5", "t6", CHORD_CLEAR_MASK))

    # Consume Block/Use/direction so the chord does not also move/use/attack.
    e.emit(sh("t5", ACTION_INPUT_VA - 0x800C0000, "t7"))

    # One switch per press/hold cycle.
    e.emit(andi("t3", "t1", LATCH_MASK))
    e.bne("t3", "zero", "done")
    e.emit(_move("a0", "t2"))

    e.emit(jal(helper_va), NOP)

    e.label("release")
    e.emit(andi("t1", "t1", (~LATCH_MASK) & 0xFFFF), sw("t1", 0, "t0"))

    e.label("done")
    done_va = base_va + len(e.words) * 4
    # Recreate the two displaced native instructions and resume after the hook.
    e.emit(lui("v1", 0x802F), jump(ACTION_HOOK_CONTINUE_VA), lhu("v1", -0x31E8, "v1"))

    return e.finish(), done_va


def build_selector_cave() -> tuple[bytes, int, int]:
    # Build once to get the fixed action done address used by the helper.
    # The action routine has no PC-relative instructions outside Emitter
    # branches, so its done address is deterministic from SECONDARY_CAVE_VA.
    placeholder_action, done_va = build_action_routine(
        SECONDARY_CAVE_VA, SWITCH_HELPER_VA
    )
    del placeholder_action

    # The helper is immediately followed by its shared 10-word copier.
    # Its expected 0x64-byte size is part of the packing contract.
    provisional_copy_va = SWITCH_HELPER_VA + 0x64
    helper = build_switch_helper(SWITCH_HELPER_VA, provisional_copy_va, done_va)
    if len(helper) != 0x64:
        raise AssertionError(f"four-box helper size drifted: 0x{len(helper):X}")

    copy_va = SWITCH_HELPER_VA + len(helper)
    copy = build_copy10(copy_va)
    blob = helper + copy
    if len(blob) > SELECTOR_CAVE_SIZE:
        raise AssertionError("four-box helper/copy exceeds reclaimed selector cave")
    return blob, copy_va, done_va


SELECTOR_CAVE_BLOB, COPY10_VA, ACTION_DONE_VA = build_selector_cave()
ACTION_ROUTINE, _ACTION_DONE_CHECK = build_action_routine(
    ACTION_ROUTINE_VA, SWITCH_HELPER_VA
)
if _ACTION_DONE_CHECK != ACTION_DONE_VA:
    raise AssertionError("action done address changed between packing passes")

RELOCATED_MAPPER = build_selection_mapper()

if len(ACTION_ROUTINE) > SECONDARY_CAVE_SIZE:
    raise AssertionError("four-box action routine exceeds confirmed secondary cave")
if len(RELOCATED_MAPPER) > 0x20:
    raise AssertionError("stage selector mapper unexpectedly exceeds 32 bytes")


def initial_box_data() -> bytes:
    """ROM-initialized data for the first switching proof."""

    return (
        DEFAULT_INV
        + words_blob([0xFFFFFFFF] * 30)
        + (0).to_bytes(4, "big")
        + MAGIC.to_bytes(4, "big")
    )


INITIAL_BOX_DATA = initial_box_data()
if len(INITIAL_BOX_DATA) != BOX_DATA_SIZE:
    raise AssertionError("four-box backing image is not exactly 168 bytes")


class FourBoxInventoryExperimentPatch:
    """Install the bounded four-box switching proof."""

    name = "four-box-inventory-experiment"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        # This patch is intentionally layered after the current selector and
        # pickup-persistence patches.
        mapper = build_selection_mapper()
        expected_selector_cave = bytearray(SELECTOR_CAVE_SIZE)
        mapper_offset = MAPPER_ROM - SELECTOR_CAVE_ROM
        expected_selector_cave[mapper_offset : mapper_offset + len(mapper)] = mapper
        rom.expect_bytes(SELECTOR_CAVE_ROM, bytes(expected_selector_cave))
        rom.expect_u32(SELECTION_LOAD_ROM, jal(MAPPER_VA))

        rom.expect_bytes(RELOCATED_MAPPER_ROM, bytes(len(RELOCATED_MAPPER)))
        rom.expect_bytes(SECONDARY_CAVE_ROM, bytes(SECONDARY_CAVE_SIZE))
        rom.expect_bytes(ACTION_HOOK_ROM, EXPECTED_ACTION_HOOK)
        rom.expect_bytes(BOX_DATA_ROM, bytes(BOX_DATA_SIZE))
        rom.expect_bytes(DEFAULT_INV_ROM, DEFAULT_INV)

        rom.write_bytes(RELOCATED_MAPPER_ROM, RELOCATED_MAPPER)
        rom.write_u32(SELECTION_LOAD_ROM, jal(RELOCATED_MAPPER_VA))
        rom.write_u32(SELECTION_LOAD_ROM + 4, NOP)

        # The relocated mapper frees the entire previously researched selector
        # cave for the switch helper + shared copy loop.
        rom.write_bytes(SELECTOR_CAVE_ROM, bytes(SELECTOR_CAVE_SIZE))
        rom.write_bytes(SELECTOR_CAVE_ROM, SELECTOR_CAVE_BLOB)

        rom.write_bytes(SECONDARY_CAVE_ROM, ACTION_ROUTINE)
        rom.write_u32(ACTION_HOOK_ROM, jal(ACTION_ROUTINE_VA))
        rom.write_u32(ACTION_HOOK_ROM + 4, NOP)

        # For this first proof only, seed box 1 with the stock inventory and
        # boxes 2-4 empty directly in the main executable image.
        rom.write_bytes(BOX_DATA_ROM, INITIAL_BOX_DATA)

        return (
            "4 native boxes x 10 slots; native live inventory remains the active window",
            "Block + Use + Right/Left cycles forward/backward using remapped actions",
            "switching is rejected while the inventory menu is open",
            "phase 1 only: transition/default-loader synchronization is not patched yet",
        )
