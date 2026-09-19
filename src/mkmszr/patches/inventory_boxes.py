"""Four-box native inventory with stage-local key-item masking.

The game's native ten inventory slots remain the active window while four
ten-word backing boxes retain authoritative inventory state. Block + Use +
Left/Right switches boxes outside the inventory menu using remapping-aware
semantic input.

Stage-specific key items that do not belong to the current stage are exposed
in LIVE as item 0x08 (Glass), while the true item ID remains in the backing
box. Glass is reserved as the non-consumable masking placeholder. Saves ignore
Glass slots; loads reconstruct LIVE from the backing box and apply the current
stage mask. This preserves the accepted no-spillover/no-global-scan design.
"""

from __future__ import annotations

from ..data.addresses import (
    CURRENT_STAGE_VA,
    NATIVE_BOOTSTRAP_STUB_ROM,
    NATIVE_BOOTSTRAP_STUB_VA,
    PICKUP_MANAGER_RESUME_VA,
    PROVEN_PAYLOAD_ROM,
    RUNTIME_V1_CODE_START,
)
from ..mips import (
    Emitter,
    addiu,
    address_words,
    addu,
    andi,
    jal,
    jr,
    jump,
    lbu,
    lhu,
    lui,
    lw,
    ori,
    sh,
    sll,
    sltiu,
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
LIVE_INV_ROM = 0x000A6C0C
DEFAULT_INV = words_blob(
    [0x00000004, 0x00000004, 0x00000001] + [0xFFFFFFFF] * 7
)
RAW_LIVE_INV = words_blob(
    [0x00000004, 0x00000004, 0x00000001] + [0x00000004] * 7
)

# Glass is deliberately reserved as the LIVE-only placeholder for a stage key
# that exists in the authoritative backing box but must not be usable here.
GLASS_ITEM = 0x08
KEY_FIRST = 0x0D
KEY_LAST = 0x22

# Native key IDs 0x0D..0x22 -> the one stage where each key is exposed.
# Temple's Map is explicitly stage 0; the legacy Lua omitted that entry even
# though the accepted native rule is "originating stage only".
KEY_STAGE_BY_ITEM = bytes(
    [
        0,        # 0D Map -> Temple
        1, 1, 1, # 0E..10 Wind
        3, 3, 3, # 11..13 Earth
        2, 2, 2, # 14..16 Water
        5, 5, 5, # 17..19 Fire
        4, 4, 4, # 1A..1C Prison
        8, 8, 8, # 1D..1F Bridge
        9, 9, 9, # 20..22 Fortress crystals
    ]
)
KEY_STAGE_TABLE = KEY_STAGE_BY_ITEM + bytes(len(DEFAULT_INV) - len(KEY_STAGE_BY_ITEM))
if len(KEY_STAGE_BY_ITEM) != KEY_LAST - KEY_FIRST + 1:
    raise AssertionError("stage-key table does not cover 0x0D..0x22 exactly")

# The stock default inventory template is no longer read after the native
# loader is replaced, so its uniquely-referenced 40-byte data area is reused as
# the stage-key table. The live initializer remains separately normalized.
KEY_STAGE_TABLE_VA = 0x800A5FE4

# Native stock sanitizer and default loader. The sanitizer used to delete all
# special/key IDs during transitions; stage-local masking replaces that role.
SANITIZE_ROM = 0x0007B900
SANITIZE_VA = 0x8007AD00
SANITIZE_END = 0x0007B94C
EXPECTED_SANITIZER = bytes.fromhex(
    "00002821 2407000B 2406FFFF 3C03800A 2463600C 8C640000 2482FFF3 "
    "2C420022 54400004 AC660000 54870003 24A50001 AC660000 24A50001 "
    "28A2000A 1440FFF5 24630004 03E00008 00000000"
)
SANITIZE_CALL_ROMS = (0x0000DCF8, 0x00036C6C)

# Native stock-default loader. Runtime testing showed this is the destructive
# title-menu START lifecycle boundary for the live ten-slot window.
LOAD_DEFAULT_ROM = 0x0007B94C
LOAD_DEFAULT_VA = 0x8007AD4C
LOAD_DEFAULT_END = 0x0007B980
EXPECTED_DEFAULT_LOADER = bytes.fromhex(
    "00002821 3C04800A 2484600C 3C03800A 24635FE4 8C620000 24630004 "
    "24A50001 AC820000 28A2000A 1440FFFA 24840004 03E00008"
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
SWITCH_HELPER_SIZE = 0x44
LOAD_MASK_WRAPPER_VA = SWITCH_HELPER_VA + SWITCH_HELPER_SIZE
LOAD_MASK_WRAPPER_UNCACHED_VA = LOAD_MASK_WRAPPER_VA | 0x20000000

# The confirmed pickup-persistence scanner ends with a 24-byte resume sequence
# at payload offset 0x1BC and leaves a 44-byte tail at 0x1D4..0x1FF.
# Inventory masking reuses that tail without changing the persistence scanner.
PERSISTENCE_RESUME_OFFSET = 0x1BC
PERSISTENCE_SAVE_OFFSET = 0x1D4
PERSISTENCE_RESUME_ROM = PROVEN_PAYLOAD_ROM + PERSISTENCE_RESUME_OFFSET
PERSISTENCE_SAVE_ROM = PROVEN_PAYLOAD_ROM + PERSISTENCE_SAVE_OFFSET
PERSISTENCE_CODE_END_ROM = PROVEN_PAYLOAD_ROM + 0x200
SAVE_FILTERED_CACHED_VA = RUNTIME_V1_CODE_START + PERSISTENCE_SAVE_OFFSET
SAVE_FILTERED_UNCACHED_VA = SAVE_FILTERED_CACHED_VA | 0x20000000


def _move(rd: str, rs: str) -> int:
    return addu(rd, rs, "zero")


def build_mask_copy_routine() -> bytes:
    """Copy backing A0 -> LIVE A1 while masking foreign-stage key items."""

    e = Emitter()
    e.emit(
        lui("t0", (CURRENT_STAGE_VA + 0x8000) >> 16),
        lw("t0", CURRENT_STAGE_VA & 0xFFFF, "t0"),
        lui("t1", 0x800A),
        addiu("t1", "t1", KEY_STAGE_TABLE_VA & 0xFFFF),
        addiu("t7", "a0", 40),
    )
    e.label("loop")
    e.emit(
        lw("t2", 0, "a0"),
        addiu("t3", "t2", -KEY_FIRST),
        sltiu("t4", "t3", len(KEY_STAGE_BY_ITEM)),
    )
    e.beq("t4", "zero", "store")
    e.emit(addu("t5", "t1", "t3"))
    e.emit(lbu("t5", 0, "t5"))
    e.bnel("t5", "t0", "store")
    e.emit(addiu("t2", "zero", GLASS_ITEM))
    e.label("store")
    e.emit(sw("t2", 0, "a1"), addiu("a0", "a0", 4))
    e.bne("a0", "t7", "loop")
    e.emit(addiu("a1", "a1", 4))
    e.emit(jr("ra"), NOP)

    blob = e.finish()
    if len(blob) != SANITIZE_END - SANITIZE_ROM:
        raise AssertionError("stage-key mask routine must exactly replace sanitizer")
    return blob


def build_save_filtered_routine() -> bytes:
    """Copy LIVE A0 -> backing A1, preserving slots currently shown as Glass."""

    e = Emitter()
    # T5=Glass is supplied by the transition-save wrapper.
    e.emit(addiu("v0", "zero", 10))
    e.label("loop")
    e.emit(lw("t6", 0, "a0"))
    e.beq("t6", "t5", "skip")
    e.emit(addiu("a0", "a0", 4))
    e.emit(sw("t6", 0, "a1"))
    e.label("skip")
    e.emit(addiu("v0", "v0", -1))
    e.bne("v0", "zero", "loop")
    e.emit(addiu("a1", "a1", 4))
    e.emit(jr("ra"), NOP)

    blob = e.finish()
    if len(blob) > PERSISTENCE_CODE_END_ROM - PERSISTENCE_SAVE_ROM:
        raise AssertionError("filtered inventory save exceeds persistence payload tail")
    return blob


def build_transition_save_wrapper() -> bytes:
    """Compute the active backing pointer, then tail-call filtered LIVE save."""

    words = [
        lui("t0", 0x800A),
        lw("t1", STATE_VA - 0x800A0000, "t0"),
        andi("t1", "t1", 3),
        sll("t2", "t1", 5),
        sll("t3", "t1", 3),
        addu("t2", "t2", "t3"),
        addiu("a0", "t0", LIVE_INV_VA - 0x800A0000),
        addiu("a1", "t0", BOX0_VA - 0x800A0000),
        addu("a1", "a1", "t2"),
        *address_words("t9", SAVE_FILTERED_UNCACHED_VA),
        jr("t9"),
        addiu("t5", "zero", GLASS_ITEM),
    ]
    blob = words_blob(words)
    if len(blob) != LOAD_DEFAULT_END - LOAD_DEFAULT_ROM:
        raise AssertionError("transition-save wrapper must exactly replace stock loader")
    return blob


def build_load_mask_wrapper() -> bytes:
    """Reconstruct LIVE from the selected backing box and apply stage masking."""

    return words_blob(
        [
            lui("t0", 0x800A),
            lw("t1", STATE_VA - 0x800A0000, "t0"),
            andi("t1", "t1", 3),
            sll("t2", "t1", 5),
            sll("t3", "t1", 3),
            addu("t2", "t2", "t3"),
            addiu("a0", "t0", BOX0_VA - 0x800A0000),
            addu("a0", "a0", "t2"),
            jump(SANITIZE_VA),
            addiu("a1", "t0", LIVE_INV_VA - 0x800A0000),
        ]
    )


def build_switch_helper(
    base_va: int,
    save_wrapper_va: int,
    load_wrapper_va: int,
    action_done_va: int,
) -> bytes:
    """Commit current LIVE, select a neighbor, then reconstruct masked LIVE."""

    del base_va
    e = Emitter()

    # Save the direction in T7. The transition-save path intentionally does not
    # clobber T7, so it remains available after the filtered commit.
    e.emit(jal(save_wrapper_va), _move("t7", "a0"))

    # Reload state because the external save wrapper uses T0..T3.
    e.emit(
        lui("t0", 0x800A),
        addiu("t0", "t0", STATE_VA & 0xFFFF),
        lw("t1", 0, "t0"),
        andi("t2", "t1", 3),
    )

    # Right = +1, Left = -1, modulo four.
    e.emit(srl("t4", "t7", 15), sll("t4", "t4", 1))
    e.emit(addiu("t2", "t2", 1), subu("t2", "t2", "t4"), andi("t2", "t2", 3))

    e.emit(ori("t1", "t2", LATCH_MASK), sw("t1", 0, "t0"))
    e.emit(jal(load_wrapper_va), NOP)
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


def build_selector_cave() -> tuple[bytes, int]:
    placeholder_action, done_va = build_action_routine(
        SECONDARY_CAVE_VA, SWITCH_HELPER_VA
    )
    del placeholder_action

    helper = build_switch_helper(
        SWITCH_HELPER_VA,
        LOAD_DEFAULT_VA,
        LOAD_MASK_WRAPPER_VA,
        done_va,
    )
    if len(helper) != SWITCH_HELPER_SIZE:
        raise AssertionError(f"four-box helper size drifted: 0x{len(helper):X}")

    load_wrapper = build_load_mask_wrapper()
    blob = helper + load_wrapper
    if len(blob) > SELECTOR_CAVE_SIZE:
        raise AssertionError("four-box helper/load-mask wrapper exceeds selector cave")
    return blob, done_va


SELECTOR_CAVE_BLOB, ACTION_DONE_VA = build_selector_cave()
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


MASK_COPY_ROUTINE = build_mask_copy_routine()
SAVE_FILTERED_ROUTINE = build_save_filtered_routine()
TRANSITION_SAVE_WRAPPER = build_transition_save_wrapper()

EXPECTED_PERSISTENCE_RESUME = words_blob(
    [
        lui("v1", 0x800A),
        lw("v1", -0x56F0, "v1"),
        *address_words("t9", PICKUP_MANAGER_RESUME_VA),
        jr("t9"),
        NOP,
    ]
)
PERSISTENCE_RESUME_PATCH = words_blob(
    [
        jal(LOAD_MASK_WRAPPER_UNCACHED_VA),
        lui("v1", 0x800A),
        *address_words("t9", PICKUP_MANAGER_RESUME_VA),
        jr("t9"),
        lw("v1", -0x56F0, "v1"),
    ]
)
if len(EXPECTED_PERSISTENCE_RESUME) != len(PERSISTENCE_RESUME_PATCH):
    raise AssertionError("persistence resume patch changed scanner size")


def initial_box_data() -> bytes:
    """ROM-initialized backing state for the four-box inventory."""

    return (
        DEFAULT_INV
        + words_blob([0xFFFFFFFF] * 30)
        + (0).to_bytes(4, "big")
        + MAGIC.to_bytes(4, "big")
    )


INITIAL_BOX_DATA = initial_box_data()
if len(INITIAL_BOX_DATA) != BOX_DATA_SIZE:
    raise AssertionError("four-box backing image is not exactly 168 bytes")


class FourBoxInventoryPatch:
    """Install the runtime-confirmed four-box inventory."""

    name = "four-box-inventory"

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
        rom.expect_bytes(LIVE_INV_ROM, RAW_LIVE_INV)
        rom.expect_bytes(SANITIZE_ROM, EXPECTED_SANITIZER)
        rom.expect_bytes(LOAD_DEFAULT_ROM, EXPECTED_DEFAULT_LOADER)
        for call_rom in SANITIZE_CALL_ROMS:
            rom.expect_u32(call_rom, jal(SANITIZE_VA))
        rom.expect_bytes(PERSISTENCE_RESUME_ROM, EXPECTED_PERSISTENCE_RESUME)
        rom.expect_bytes(
            PERSISTENCE_SAVE_ROM,
            bytes(PERSISTENCE_CODE_END_ROM - PERSISTENCE_SAVE_ROM),
        )

        rom.write_bytes(RELOCATED_MAPPER_ROM, RELOCATED_MAPPER)
        rom.write_u32(SELECTION_LOAD_ROM, jal(RELOCATED_MAPPER_VA))
        rom.write_u32(SELECTION_LOAD_ROM + 4, NOP)

        # The relocated mapper frees the former selector cave for the compact
        # switch helper plus active-box load/mask wrapper.
        rom.write_bytes(SELECTOR_CAVE_ROM, bytes(SELECTOR_CAVE_SIZE))
        rom.write_bytes(SELECTOR_CAVE_ROM, SELECTOR_CAVE_BLOB)

        rom.write_bytes(SECONDARY_CAVE_ROM, ACTION_ROUTINE)
        rom.write_u32(ACTION_HOOK_ROM, jal(ACTION_ROUTINE_VA))
        rom.write_u32(ACTION_HOOK_ROM + 4, NOP)

        # Seed box 1 with stock inventory and boxes 2-4 empty. LIVE starts from
        # the same stock image. The now-dead stock template becomes the compact
        # item-ID -> originating-stage table used by the mask routine.
        rom.write_bytes(BOX_DATA_ROM, INITIAL_BOX_DATA)
        rom.write_bytes(LIVE_INV_ROM, DEFAULT_INV)
        rom.write_bytes(DEFAULT_INV_ROM, KEY_STAGE_TABLE)

        # Replace native special-item cleanup with stage-local masking. Existing
        # sanitizer call sites are disabled; reconstruction happens explicitly
        # when a box is selected and at the pickup-manager stage-init boundary.
        rom.write_bytes(SANITIZE_ROM, MASK_COPY_ROUTINE)
        for call_rom in SANITIZE_CALL_ROMS:
            rom.write_u32(call_rom, NOP)

        # Leaving-stage/default-loader routes now commit LIVE through a filtered
        # saver. Glass slots are placeholders and therefore never overwrite the
        # real key IDs held by the authoritative backing box.
        rom.write_bytes(LOAD_DEFAULT_ROM, TRANSITION_SAVE_WRAPPER)
        rom.write_bytes(PERSISTENCE_SAVE_ROM, SAVE_FILTERED_ROUTINE)

        # The existing pickup-persistence restore scanner is left intact; only
        # its fixed-size resume sequence is replaced so stage initialization
        # reconstructs the selected box and applies the stage mask before the
        # native manager resumes.
        rom.write_bytes(PERSISTENCE_RESUME_ROM, PERSISTENCE_RESUME_PATCH)

        return (
            "4 native boxes x 10 slots; backing boxes remain authoritative",
            "Block + Use + Right/Left cycles using remapped actions",
            "switching is rejected while the inventory menu is open",
            "Glass (0x08) masks key items outside their originating stage",
            "stage transitions and box loads reconstruct masked LIVE from backing state",
        )


# Compatibility for the disposable phase-1 builder retained on this branch.
FourBoxInventoryExperimentPatch = FourBoxInventoryPatch
