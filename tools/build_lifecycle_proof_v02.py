"""Build the bounded HP/lives/continues/Game-Over lifecycle proof v02.

This is deliberately proof-only. It first builds the current full product with
an MKT Rev. 2 donor, then installs five guarded lifecycle hooks into the
already-loaded FF gap between the Temple special-check module and Toasty.

Do not promote this allocation/hook composition to production until the
documented manual runtime route passes.\n\nv02 deliberately leaves Game Over reset unhooked after v01 proved that ROM 0x000364EC is a generic stage-state seam, not a terminal Game Over seam.
"""

# ruff: noqa: I001 -- proof builder keeps grouped MIPS imports readable.

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from mkmszr.config import RandomizerConfig
from mkmszr.donors.mkt_n64 import (
    extract_temple_intro_audio_assets,
    extract_toasty_assets,
)
from mkmszr.mips import (
    Emitter,
    addiu,
    address_words,
    andi,
    jal,
    jr,
    jump,
    lhu,
    lui,
    lw,
    ori,
    sh,
    sw,
)
from mkmszr.patcher import patch_bytes
from mkmszr.rom import RomImage


MODULE_ROM = 0x00F69150
MODULE_VA = 0x801B0970
MODULE_LIMIT_ROM = 0x00F697E0
MODULE_CAPACITY = MODULE_LIMIT_ROM - MODULE_ROM

STATE = 0xA01AF7D0
FLAGS = 0x10
HP = 0x14
LIVES = 0x18
CONTINUES = 0x1C
XP = 0x44
FLAG_LIFECYCLE_VALID = 0x0002
FLAG_RESET_PENDING = 0x0004

CONFIG = 0x800A5FA8
CONFIG_DIFFICULTY = 4
CONFIG_LIVES = 9
CONFIG_CONTINUES = 5
INITIAL_LIVE_LIVES = CONFIG_LIVES - 1
INITIAL_HP = 0x00A6

LIVE_LIVES = 0x8010BCFC
LIVE_CONTINUES = 0x801AE45C
CURRENT_XP = 0x8011200C
POWER_TIER_CACHE = 0x800C1248
PLAYER_PTR = 0x802C1AC0
PLAYER_HP_OFF = 0x654
HP_CARRIER = 0x801AE4C0
HP_CARRIER_VALID = 0x800C11F8

LIVE_INV = 0x800A600C
BOX0 = 0x800A6048
BOX_STATE = 0x800A60E8
BOX_MAGIC = 0x800A60EC
MKBX = 0x4D4B4258
SETTINGS_MASK = 0x3E00

TRANSITION_HOOK_ROM = 0x0007B94C
TRANSITION_RESUME = 0x8007AD54
PERSISTENCE_RESTORE_HOOK_ROM = 0x00F101BC
ORIGINAL_PROGRESSION_RESTORE = 0x801AF6C0
FINAL_GAME_OVER_HOOK_ROM = 0x000364EC
DEATH_COMMIT_SLEEP_HOOK_ROM = 0x000368A4
DEATH_COMMIT_ALT_HOOK_ROM = 0x00036B10
STOCK_SLEEP = 0x80028794
STOCK_ALT_AFTER_DEATH = 0x80017F78

EXPECTED_CONFIG = bytes.fromhex("000200030001")
EXPECTED_TRANSITION = bytes.fromhex("3c08800a8d0960e8")
EXPECTED_RESTORE_JAL = 0x0C06BDB0
EXPECTED_GAME_OVER = bytes.fromhex("8fa7002c24020004")
EXPECTED_DEATH_SLEEP = bytes.fromhex("0c00a1e52404001e")
EXPECTED_DEATH_ALT = bytes.fromhex("0c005fde240600ff")
NOP = 0


def _emit_u32(e: Emitter, reg: str, value: int) -> None:
    e.emit(lui(reg, (value >> 16) & 0xFFFF), ori(reg, reg, value & 0xFFFF))


def _force_config(e: Emitter) -> None:
    e.emit(*address_words("t3", CONFIG))
    e.emit(addiu("t4", "zero", CONFIG_DIFFICULTY), sh("t4", 0, "t3"))
    e.emit(addiu("t4", "zero", CONFIG_LIVES), sh("t4", 2, "t3"))
    e.emit(addiu("t4", "zero", CONFIG_CONTINUES), sh("t4", 4, "t3"))


def _commit_counters(e: Emitter, *, death: bool) -> None:
    # T0 = MKSV state, T1 = flags.
    e.emit(*address_words("t3", LIVE_LIVES), lw("t4", 0, "t3"), sw("t4", LIVES, "t0"))
    e.emit(
        *address_words("t3", LIVE_CONTINUES),
        lhu("t4", 0, "t3"),
        sw("t4", CONTINUES, "t0"),
    )
    if death:
        # Stock death/Continue starts the replacement life at full HP.
        e.emit(addiu("t4", "zero", INITIAL_HP), sw("t4", HP, "t0"))
    e.emit(
        ori("t1", "t1", FLAG_LIFECYCLE_VALID),
        sw("t1", FLAGS, "t0"),
    )


def build_transition_save() -> bytes:
    e = Emitter()
    _force_config(e)
    e.emit(*address_words("t0", STATE), lw("t1", FLAGS, "t0"))
    e.emit(andi("t2", "t1", FLAG_RESET_PENDING))
    e.bne("t2", "zero", "resume")
    e.emit(NOP)

    _commit_counters(e, death=False)
    e.emit(
        *address_words("t3", CURRENT_XP),
        lw("t4", 0, "t3"),
        sw("t4", XP, "t0"),
    )

    e.emit(*address_words("t3", PLAYER_PTR), lw("t3", 0, "t3"))
    e.beq("t3", "zero", "resume")
    e.emit(NOP)
    e.emit(lhu("t4", PLAYER_HP_OFF, "t3"))
    e.beq("t4", "zero", "resume")
    e.emit(NOP)
    e.emit(sw("t4", HP, "t0"))
    e.emit(*address_words("t5", HP_CARRIER), sh("t4", 0, "t5"))
    e.emit(
        *address_words("t5", HP_CARRIER_VALID),
        addiu("t6", "zero", 1),
        sh("t6", 0, "t5"),
    )

    e.label("resume")
    # Replay the displaced beginning of the existing four-box wrapper.
    e.emit(
        lui("t0", 0x800A),
        lw("t1", 0x60E8, "t0"),
        jump(TRANSITION_RESUME),
        NOP,
    )
    return e.finish()


def build_restore() -> bytes:
    e = Emitter()
    e.emit(addiu("sp", "sp", -0x18), sw("ra", 0x10, "sp"))
    # Preserve the already-accepted XP + inventory restore first.
    e.emit(jal(ORIGINAL_PROGRESSION_RESTORE), NOP)
    _force_config(e)

    e.emit(*address_words("t0", STATE), lw("t1", FLAGS, "t0"))
    e.emit(andi("t2", "t1", FLAG_LIFECYCLE_VALID))
    e.beq("t2", "zero", "initialize")
    e.emit(NOP)
    e.emit(andi("t2", "t1", FLAG_RESET_PENDING))
    e.bne("t2", "zero", "initialize")
    e.emit(NOP)

    e.emit(
        lw("t4", LIVES, "t0"),
        *address_words("t3", LIVE_LIVES),
        sw("t4", 0, "t3"),
    )
    e.emit(
        lw("t4", CONTINUES, "t0"),
        *address_words("t3", LIVE_CONTINUES),
        sh("t4", 0, "t3"),
    )
    e.emit(lw("t4", HP, "t0"))
    e.beq("t4", "zero", "full_hp")
    e.emit(NOP)
    e.beq("zero", "zero", "apply_hp")
    e.emit(NOP)

    e.label("initialize")
    e.emit(addiu("t4", "zero", INITIAL_LIVE_LIVES), sw("t4", LIVES, "t0"))
    e.emit(*address_words("t3", LIVE_LIVES), sw("t4", 0, "t3"))
    e.emit(addiu("t4", "zero", CONFIG_CONTINUES), sw("t4", CONTINUES, "t0"))
    e.emit(*address_words("t3", LIVE_CONTINUES), sh("t4", 0, "t3"))
    e.emit(
        andi("t1", "t1", 0xFFFB),
        ori("t1", "t1", FLAG_LIFECYCLE_VALID),
        sw("t1", FLAGS, "t0"),
    )

    e.label("full_hp")
    e.emit(addiu("t4", "zero", INITIAL_HP), sw("t4", HP, "t0"))

    e.label("apply_hp")
    e.emit(*address_words("t3", PLAYER_PTR), lw("t3", 0, "t3"))
    e.beq("t3", "zero", "carrier")
    e.emit(NOP)
    e.emit(sh("t4", PLAYER_HP_OFF, "t3"))
    e.label("carrier")
    e.emit(*address_words("t5", HP_CARRIER), sh("t4", 0, "t5"))
    e.emit(
        *address_words("t5", HP_CARRIER_VALID),
        addiu("t6", "zero", 1),
        sh("t6", 0, "t5"),
    )

    e.emit(
        lw("ra", 0x10, "sp"),
        addiu("sp", "sp", 0x18),
        jr("ra"),
        NOP,
    )
    return e.finish()


def build_death_commit(target: int) -> bytes:
    e = Emitter()
    e.emit(addiu("sp", "sp", -0x18), sw("ra", 0x10, "sp"))
    _force_config(e)
    e.emit(*address_words("t0", STATE), lw("t1", FLAGS, "t0"))
    e.emit(andi("t2", "t1", FLAG_RESET_PENDING))
    e.bne("t2", "zero", "call_stock")
    e.emit(NOP)
    _commit_counters(e, death=True)
    e.label("call_stock")
    e.emit(jal(target), NOP)
    e.emit(
        lw("ra", 0x10, "sp"),
        addiu("sp", "sp", 0x18),
        jr("ra"),
        NOP,
    )
    return e.finish()


def build_game_over_reset() -> bytes:
    e = Emitter()
    _force_config(e)

    # Preserve the V2 header, clear every run-owned word +0x10..+0x4C.
    e.emit(
        *address_words("t0", STATE),
        addiu("t1", "t0", 0x10),
        addiu("t2", "zero", 16),
    )
    e.label("clear_state")
    e.emit(
        sw("zero", 0, "t1"),
        addiu("t1", "t1", 4),
        addiu("t2", "t2", -1),
    )
    e.bne("t2", "zero", "clear_state")
    e.emit(NOP)
    e.emit(
        addiu("t1", "zero", FLAG_RESET_PENDING),
        sw("t1", FLAGS, "t0"),
    )

    for addr in (CURRENT_XP, POWER_TIER_CACHE):
        e.emit(*address_words("t0", addr), sw("zero", 0, "t0"))
    e.emit(*address_words("t0", LIVE_LIVES), sw("zero", 0, "t0"))
    e.emit(*address_words("t0", LIVE_CONTINUES), sh("zero", 0, "t0"))
    e.emit(*address_words("t0", HP_CARRIER), sh("zero", 0, "t0"))
    e.emit(*address_words("t0", HP_CARRIER_VALID), sh("zero", 0, "t0"))

    # Four authoritative backing boxes: empty everything, then restore the
    # stock starter set (Herbs, Herbs, Potion) in Box 1 only.
    e.emit(*address_words("t0", BOX0))
    _emit_u32(e, "t1", 0xFFFFFFFF)
    e.emit(addiu("t2", "zero", 40))
    e.label("clear_boxes")
    e.emit(
        sw("t1", 0, "t0"),
        addiu("t0", "t0", 4),
        addiu("t2", "t2", -1),
    )
    e.bne("t2", "zero", "clear_boxes")
    e.emit(NOP)
    e.emit(*address_words("t0", BOX0))
    e.emit(
        addiu("t1", "zero", 4),
        sw("t1", 0, "t0"),
        sw("t1", 4, "t0"),
        addiu("t1", "zero", 1),
        sw("t1", 8, "t0"),
    )

    e.emit(*address_words("t0", LIVE_INV))
    _emit_u32(e, "t1", 0xFFFFFFFF)
    e.emit(addiu("t2", "zero", 10))
    e.label("clear_live")
    e.emit(
        sw("t1", 0, "t0"),
        addiu("t0", "t0", 4),
        addiu("t2", "t2", -1),
    )
    e.bne("t2", "zero", "clear_live")
    e.emit(NOP)
    e.emit(*address_words("t0", LIVE_INV))
    e.emit(
        addiu("t1", "zero", 4),
        sw("t1", 0, "t0"),
        sw("t1", 4, "t0"),
        addiu("t1", "zero", 1),
        sw("t1", 8, "t0"),
    )

    # Reset box index/latch, preserve all five non-progress GAME SETTINGS.
    e.emit(
        *address_words("t0", BOX_STATE),
        lw("t1", 0, "t0"),
        andi("t1", "t1", SETTINGS_MASK),
        sw("t1", 0, "t0"),
    )
    e.emit(*address_words("t0", BOX_MAGIC))
    _emit_u32(e, "t1", MKBX)
    e.emit(sw("t1", 0, "t0"))

    # Replay the displaced instruction; the following stock branch needs v0=4.
    e.emit(
        lw("a3", 0x2C, "sp"),
        addiu("v0", "zero", 4),
        jr("ra"),
        NOP,
    )
    return e.finish()


def _align(value: int, alignment: int = 16) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def pack_module() -> tuple[bytes, dict[str, int]]:
    pieces = (
        ("transition", build_transition_save()),
        ("restore", build_restore()),
        ("death_sleep", build_death_commit(STOCK_SLEEP)),
        ("death_alt", build_death_commit(STOCK_ALT_AFTER_DEATH)),
        ("reset", build_game_over_reset()),
    )
    blob = bytearray()
    offsets: dict[str, int] = {}
    for name, data in pieces:
        offset = _align(len(blob))
        blob.extend(bytes(offset - len(blob)))
        offsets[name] = offset
        blob.extend(data)
    return bytes(blob), offsets


def apply_proof(product: bytes) -> tuple[bytes, int, int]:
    rom = RomImage.from_bytes(product, require_clean=False)
    module, offsets = pack_module()
    if len(module) > MODULE_CAPACITY:
        raise AssertionError(
            f"lifecycle proof module 0x{len(module):X} > gap 0x{MODULE_CAPACITY:X}"
        )

    rom.expect_bytes(0x000A6BA8, EXPECTED_CONFIG)
    rom.expect_bytes(TRANSITION_HOOK_ROM, EXPECTED_TRANSITION)
    rom.expect_u32(PERSISTENCE_RESTORE_HOOK_ROM, EXPECTED_RESTORE_JAL)
    rom.expect_bytes(FINAL_GAME_OVER_HOOK_ROM, EXPECTED_GAME_OVER)
    rom.expect_bytes(DEATH_COMMIT_SLEEP_HOOK_ROM, EXPECTED_DEATH_SLEEP)
    rom.expect_bytes(DEATH_COMMIT_ALT_HOOK_ROM, EXPECTED_DEATH_ALT)
    rom.expect_bytes(MODULE_ROM, b"\xFF" * MODULE_CAPACITY)

    rom.write_u16(0x000A6BA8, CONFIG_DIFFICULTY)
    rom.write_u16(0x000A6BAA, CONFIG_LIVES)
    rom.write_u16(0x000A6BAC, CONFIG_CONTINUES)
    rom.write_bytes(MODULE_ROM, module)

    va = {name: MODULE_VA + offset for name, offset in offsets.items()}
    rom.write_u32(TRANSITION_HOOK_ROM, jump(va["transition"]))
    rom.write_u32(TRANSITION_HOOK_ROM + 4, NOP)
    rom.write_u32(PERSISTENCE_RESTORE_HOOK_ROM, jal(va["restore"]))
    rom.write_u32(DEATH_COMMIT_SLEEP_HOOK_ROM, jal(va["death_sleep"]))
    rom.write_u32(DEATH_COMMIT_ALT_HOOK_ROM, jal(va["death_alt"]))
    rom.write_u32(FINAL_GAME_OVER_HOOK_ROM, jal(va["reset"]))

    crc1, crc2 = rom.update_header_crc()
    return rom.to_bytes(), crc1, crc2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="exact clean MKMSZ USA Rev. 0 .z64")
    parser.add_argument("mkt", type=Path, help="exact MKT USA Rev. 2 donor .z64")
    parser.add_argument("output", type=Path, help="new disposable proof .z64")
    parser.add_argument("--seed", default="LIFECYCLE-V01")
    args = parser.parse_args()

    if args.source.resolve() == args.output.resolve():
        parser.error("output must be separate from the clean ROM")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    source = args.source.read_bytes()
    donor = args.mkt.read_bytes()
    base = patch_bytes(
        source,
        RandomizerConfig(seed=args.seed),
        toasty_assets=extract_toasty_assets(donor),
        temple_intro_audio_assets=extract_temple_intro_audio_assets(donor),
    ).data
    output, crc1, crc2 = apply_proof(base)
    args.output.write_bytes(output)
    if args.output.read_bytes() != output:
        raise OSError("output read-back verification failed")

    print(f"Output: {args.output}")
    print(f"SHA-256: {hashlib.sha256(output).hexdigest()}")
    print(f"CRC1 / CRC2: {crc1:08X} / {crc2:08X}")
    print(f"Proof module: 0x{len(pack_module()[0]):X} / 0x{MODULE_CAPACITY:X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
