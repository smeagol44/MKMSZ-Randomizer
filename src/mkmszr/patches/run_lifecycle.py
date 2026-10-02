"""Production run-lifecycle invariants, promoted from runtime-confirmed v06.

This module intentionally promotes the exact helper blob and seven permanent-code
transfers exercised by the accepted v06 proof.  It does not rebuild the rejected
v01-v04 compositions and does not touch the production XP/Mission Objective
restore graph.

Runtime-confirmed bounded behavior:
- Very Hard configuration; 9 total lives; 5 continues.
- HP/lives/continues and existing XP/powers/inventory survive living exits and
  stage transitions.
- Ordinary death preserves inventory/progression, decrements lives normally,
  and constructs the replacement player at full HP.
- Accepted Continue preserves run state while stock decrements continues and
  reloads configured lives.
- True final Game Over clears run progress and restores fresh-run defaults while
  preserving all five GAME SETTINGS preferences.
"""

from __future__ import annotations

import hashlib

from ..config import DifficultyMode
from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext
from .global_materialization import MATERIALIZER_HELPER_END_ROM
from .temple_special_check import (
    EXPANSION_FILE_ENTRY_ROM,
    EXPANSION_FILE_ROM,
    TEMPLE_MODULE_END_ROM,
    TOASTY_ROM,
)

# The runtime-confirmed v06 helper starts immediately after the current optional
# materializer allocation and ends twelve bytes before Toasty's fixed module.
LIFECYCLE_MODULE_ROM = 0x00F69240
LIFECYCLE_MODULE_K0 = 0x801B0A60
LIFECYCLE_MODULE_K1 = 0xA01B0A60
LIFECYCLE_MODULE_SIZE = 0x594
LIFECYCLE_MODULE_END_ROM = LIFECYCLE_MODULE_ROM + LIFECYCLE_MODULE_SIZE
LIFECYCLE_MODULE_END_K0 = LIFECYCLE_MODULE_K0 + LIFECYCLE_MODULE_SIZE
LIFECYCLE_MODULE_SHA256 = "b84e94b2c3f2dfbeb75ffd450523035e690545940ac515a205b9ccbd10e670e4"

if MATERIALIZER_HELPER_END_ROM != LIFECYCLE_MODULE_ROM:
    raise AssertionError("lifecycle v06 no longer starts after materializer helper")
if LIFECYCLE_MODULE_END_ROM != 0x00F697D4:
    raise AssertionError("lifecycle v06 module size/layout drifted")
if LIFECYCLE_MODULE_END_ROM >= TOASTY_ROM:
    raise AssertionError("lifecycle v06 reaches Toasty allocation")

LIFECYCLE_MODULE = bytes.fromhex(
    """
    3c08a01b8d09f7d03c0a4d4b354a5356152a000c8d09f7d4240a0002152a00098d09f7d8240a0050152a00068d09f7dc
    240a0020152a00032402000103e00008000000000000102103e000080000000027bdffe8afbf0010afa4000c0c06c298
    0000000010400038000000003c08a01b8d09f7e43c0a0004012a5824156000328fa4000c14800015000000003c0a0001
    012a58241160002c000000003c1980073739ad4c0320f809000000003c08a01b8d09f7e43c0a000201405027012a4824
    3c0a0008012a4825ad09f7e43c0a800ca54011f81000001c000000003c1980073739ad4c0320f809000000003c0a802c
    8d4a1ac01140001400000000954b0654116000113c08a01b8d09f7e400096402000c6400018b60253c0d0003018d6025
    3c0d000801a06827018d6024ad0cf7e43c0d80118daebcfcad0ef7e83c0d801b95aee45cad0ef7ec8fbf001027bd0018
    03e0000800000000ffffffffffffffff240400010c06c2ac0000000000002021000028213c198002373984880320f809
    000000003c1980003739d0800320f809000000003c1a8001375a66dc0340000800000000ffffffffffffffffffffffff
    27bdfff0afbf000cafa40008240800011368000700000000240800021368000700000000240400011000000e00000000
    000020211000000b000000008fa400082408001610880006000000002408001b10880003000020211000000200000000
    240400010c06c2ac000000008fa400088fbf000c27bd0010240800011368001f00000000240800021368001400000000
    24080003136800090000000027bdffe8240400122402001aafbf00103c1a8003375a5fd003400008000000003c02802f
    8c42ce2027bdffe8afbf00103c1a8003375a5f48034000080000000027bdffe0afb00010008080213c02802f3c1a8003
    375a5d44034000080000000027bdffa0afb3004400009821afbf005c3c1a8003375a55880340000800000000ffffffff
    3c08a01b8d09f7d03c0a4d4b354a5356152a0054000000008d09f7e43c0a800a854baff611600006000000003c0a0004
    012a4825ad09f7e41000004a000000003c0a000401405027012a48243c0a800a240b0004a54b5fa8240b0009a54b5faa
    240b0005a54b5fac3c0a802e240b0004a54b7dc83c0a0001012a582415600013000000003c0c8011240d0008ad8dbcfc
    ad0df7e83c0c801b240d0005a58de45cad0df7ec3c0c800ca58011f83c0c000a01806027012c48243c0c0001012c4825
    ad09f7e410000027000000003c0a0002012a58241160001d000000008d0cf7e83c0d8011adacbcfc8d0cf7ec3c0d801b
    a5ace45c312cffff1180000c000000002d8e00a715c0000200000000240c00a63c0d801ba5ace4c03c0d800c240e0001
    a5ae11f810000003000000003c0d800ca5a011f83c0c000a01806027012c4824ad09f7e410000007000000003c0d800c
    a5a011f83c0c000801806027012c4824ad09f7e43c04802c8c841ac03c02800c844211f83c1a8002375aed9403400008
    00000000ffffffffffffffffffffffff0c06c298000000001040003f000000003c08a01b8d09f7e43c0a0009012a5824
    156a0039000000003c0a0004012a582415600035000000003c0a80118d4bbcfc15600031000000003c0a801b854be45c
    1d60002d00000000250af7e0240b000fad400000254a0004256bffff1560fffc000000003c0a8011ad40200cad40bcfc
    3c0a802cad401ba43c0a800cad401248a54011f83c0a801ba540e45ca540e4c03c0a800a254c60483c0dffff35adffff
    240e0028ad8d0000258c000425ceffff15c0fffc00000000254c6048240d0004ad8d0000ad8d0004240d0001ad8d0008
    8d4d60e831ad3e00ad4d60e83c0d4d4b35ad4258ad4d60ec3c19800937399b140320f80900000000240400043c198002
    373987940320f809000000008fa7002c000020213c1a8003375a5bc40340000800000000
    """
)
if len(LIFECYCLE_MODULE) != LIFECYCLE_MODULE_SIZE:
    raise AssertionError("runtime-confirmed lifecycle v06 blob size drifted")
if hashlib.sha256(LIFECYCLE_MODULE).hexdigest() != LIFECYCLE_MODULE_SHA256:
    raise AssertionError("runtime-confirmed lifecycle v06 blob hash drifted")

# Each permanent-code transfer replaces four stock instructions and enters the
# exact uncached v06 helper. The helper replays those displaced instructions
# before returning to the stock continuation.
HOOKS = (
    (
        0x000172CC,
        bytes.fromhex("0c00a122000028210c00342000000000"),
        bytes.fromhex("3c1aa01b375a0bc00340000800000000"),
        "Pause -> Quit -> Yes living snapshot",
    ),
    (
        0x00036178,
        bytes.fromhex("27bdffa0afb3004400009821afbf005c"),
        bytes.fromhex("3c1aa01b375a0c1003400008241b0001"),
        "failure root / ordinary death",
    ),
    (
        0x00036934,
        bytes.fromhex("27bdffe0afb00010008080213c02802f"),
        bytes.fromhex("3c1aa01b375a0c1003400008241b0002"),
        "alternate reconstruction",
    ),
    (
        0x00036B38,
        bytes.fromhex("3c02802f8c42ce2027bdffe8afbf0010"),
        bytes.fromhex("3c1aa01b375a0c1003400008241b0003"),
        "carrier-preserving reconstruction",
    ),
    (
        0x00036BC0,
        bytes.fromhex("27bdffe8240400122402001aafbf0010"),
        bytes.fromhex("3c1aa01b375a0c1003400008241b0004"),
        "living stage completion",
    ),
    (
        0x0002F984,
        bytes.fromhex("3c04802c8c841ac03c02800c844211f8"),
        bytes.fromhex("3c1aa01b375a0d300340000800000000"),
        "player constructor one-shot HP/resource restore",
    ),
    (
        0x000367B4,
        bytes.fromhex("0c00a1e5240400048fa7002c00002021"),
        bytes.fromhex("3c1aa01b375a0ec00340000800000000"),
        "classified terminal Game Over reset",
    ),
)

# Initial GAME SETTINGS resource defaults.  The live current-lives counter is a
# spare-life count, so configured 9 yields 8 spare lives plus the active life.
CONFIG_ROM = 0x000A6BA8
EXPECTED_CONFIG = bytes.fromhex("000200030001")
RUNTIME_CONFIRMED_V06_CONFIG = bytes.fromhex("000400090005")

# v05 correctly restored a living HP snapshot through the native carrier, but
# stock immediately overwrote +0x654 with full HP in this later constructor
# delay slot. v06 NOPs only that redundant second full-HP store. Fresh run,
# ordinary death, and Continue still receive full HP from the earlier stock
# branch at 0x8002EDCC.
FINAL_FULL_HP_STORE_ROM = 0x0002FA44
EXPECTED_FINAL_FULL_HP_STORE = 0xA4A20654
NOP = 0


DIFFICULTY_VALUES: dict[DifficultyMode, int] = {
    "very_easy": 0,
    "easy": 1,
    "medium": 2,
    "hard": 3,
    "very_hard": 4,
}

# Immediate-word offsets inside the exact v06 helper blob.
MODULE_CONFIG_DIFFICULTY_OFFSET = 0x320
MODULE_CONFIG_LIVES_OFFSET = 0x328
MODULE_CONFIG_CONTINUES_OFFSET = 0x330
MODULE_NATIVE_DIFFICULTY_OFFSET = 0x33C
MODULE_CURRENT_LIVES_OFFSET = 0x358
MODULE_CURRENT_CONTINUES_OFFSET = 0x368


def _addiu_zero(register: int, value: int) -> bytes:
    return ((0x09 << 26) | (register << 16) | (value & 0xFFFF)).to_bytes(4, "big")


def configured_lifecycle_module(
    difficulty: DifficultyMode,
    lives: int,
    continues: int,
) -> bytes:
    """Return v06 control flow with only run-setting immediates changed."""

    data = bytearray(LIFECYCLE_MODULE)
    difficulty_value = DIFFICULTY_VALUES[difficulty]
    replacements = (
        (MODULE_CONFIG_DIFFICULTY_OFFSET, 11, difficulty_value),
        (MODULE_CONFIG_LIVES_OFFSET, 11, lives),
        (MODULE_CONFIG_CONTINUES_OFFSET, 11, continues),
        (MODULE_NATIVE_DIFFICULTY_OFFSET, 11, difficulty_value),
        (MODULE_CURRENT_LIVES_OFFSET, 13, lives - 1),
        (MODULE_CURRENT_CONTINUES_OFFSET, 13, continues),
    )
    for offset, register, value in replacements:
        data[offset : offset + 4] = _addiu_zero(register, value)
    return bytes(data)


class RunLifecyclePatch:
    """Install v06 lifecycle semantics with configurable fresh-run settings."""

    name = "run-lifecycle-v06"

    def __init__(
        self,
        *,
        difficulty: DifficultyMode = "very_hard",
        lives: int = 5,
        continues: int = 3,
        persist_hp: bool = True,
    ):
        self.difficulty = difficulty
        self.lives = lives
        self.continues = continues
        self.persist_hp = persist_hp

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context

        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM, EXPANSION_FILE_ROM)
        file_end = rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)
        if file_end < TEMPLE_MODULE_END_ROM:
            raise PatchError(
                "run lifecycle requires controls + Temple shared file-0x1A composition first"
            )
        if LIFECYCLE_MODULE_ROM < file_end < LIFECYCLE_MODULE_END_ROM:
            raise PatchError("shared file 0x1A ends inside lifecycle v06 allocation")

        rom.expect_bytes(
            LIFECYCLE_MODULE_ROM,
            b"\xFF" * LIFECYCLE_MODULE_SIZE,
        )
        rom.expect_bytes(CONFIG_ROM, EXPECTED_CONFIG)
        rom.expect_u32(FINAL_FULL_HP_STORE_ROM, EXPECTED_FINAL_FULL_HP_STORE)
        for offset, expected, _replacement, _label in HOOKS:
            rom.expect_bytes(offset, expected)

        module = configured_lifecycle_module(self.difficulty, self.lives, self.continues)
        rom.write_bytes(LIFECYCLE_MODULE_ROM, module)
        if file_end < LIFECYCLE_MODULE_END_ROM:
            rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, LIFECYCLE_MODULE_END_ROM)

        difficulty_value = DIFFICULTY_VALUES[self.difficulty]
        rom.write_bytes(
            CONFIG_ROM,
            (
                difficulty_value.to_bytes(2, "big")
                + self.lives.to_bytes(2, "big")
                + self.continues.to_bytes(2, "big")
            ),
        )
        if self.persist_hp:
            rom.write_u32(FINAL_FULL_HP_STORE_ROM, NOP)
        for offset, _expected, replacement, _label in HOOKS:
            rom.write_bytes(offset, replacement)

        return (
            (
                f"{self.difficulty.replace('_', ' ').title()} / {self.lives} total lives / "
                f"{self.continues} continues configured for fresh real runs"
            ),
            (
                "HP persists across living exits/transitions"
                if self.persist_hp
                else "HP resets to full on living stage re-entry"
            ),
            "ordinary death and Continue retain stock counter/full-HP behavior while preserving run progress",
            "classified final Game Over resets run progress and starter inventory while preserving GAME SETTINGS",
            (
                f"runtime-confirmed v06 helper 0x{LIFECYCLE_MODULE_ROM:08X}.."
                f"0x{LIFECYCLE_MODULE_END_ROM - 1:08X} via KSEG1 0x{LIFECYCLE_MODULE_K1:08X}"
            ),
        )
