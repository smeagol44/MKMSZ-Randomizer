import hashlib

from mkmszr.patches.base import PatchContext
from mkmszr.patches.global_materialization import (
    MATERIALIZER_HELPER_END_ROM,
    MATERIALIZER_HELPER_ROM,
)
from mkmszr.patches.inventory_boxes import BOX0_VA, starting_inventory
from mkmszr.patches.run_lifecycle import (
    CONFIG_ROM,
    EXPECTED_CONFIG,
    EXPECTED_FINAL_FULL_HP_STORE,
    FINAL_FULL_HP_STORE_ROM,
    HOOKS,
    LIFECYCLE_MODULE,
    LIFECYCLE_MODULE_END_ROM,
    LIFECYCLE_MODULE_ROM,
    LIFECYCLE_MODULE_SHA256,
    LIFECYCLE_MODULE_SIZE,
    MODULE_RESET_INVENTORY_OFFSET,
    MODULE_RESET_INVENTORY_SIZE,
    RUNTIME_CONFIRMED_V06_CONFIG,
    RunLifecyclePatch,
    configured_lifecycle_module,
)
from mkmszr.patches.temple_special_check import (
    EXPANSION_FILE_ENTRY_ROM,
    EXPANSION_FILE_ROM,
    TEMPLE_MODULE_END_ROM,
    TOASTY_ROM,
)
from mkmszr.rom import RomImage


def _clean_shape() -> RomImage:
    data = bytearray(0x01000000)
    data[EXPANSION_FILE_ENTRY_ROM : EXPANSION_FILE_ENTRY_ROM + 12] = (
        EXPANSION_FILE_ROM.to_bytes(4, "big")
        + TEMPLE_MODULE_END_ROM.to_bytes(4, "big")
        + bytes(4)
    )
    data[LIFECYCLE_MODULE_ROM:LIFECYCLE_MODULE_END_ROM] = (
        b"\xFF" * LIFECYCLE_MODULE_SIZE
    )
    data[CONFIG_ROM : CONFIG_ROM + len(EXPECTED_CONFIG)] = EXPECTED_CONFIG
    data[
        FINAL_FULL_HP_STORE_ROM : FINAL_FULL_HP_STORE_ROM + 4
    ] = EXPECTED_FINAL_FULL_HP_STORE.to_bytes(4, "big")
    for offset, expected, _replacement, _label in HOOKS:
        data[offset : offset + len(expected)] = expected
    return RomImage(data=data, _original=bytes(data))


def test_runtime_confirmed_v06_blob_and_allocation_are_exact() -> None:
    assert len(LIFECYCLE_MODULE) == 0x594
    assert LIFECYCLE_MODULE_SIZE == 0x594
    assert hashlib.sha256(LIFECYCLE_MODULE).hexdigest() == LIFECYCLE_MODULE_SHA256
    assert LIFECYCLE_MODULE_END_ROM < MATERIALIZER_HELPER_ROM
    assert MATERIALIZER_HELPER_ROM < MATERIALIZER_HELPER_END_ROM
    assert LIFECYCLE_MODULE_END_ROM == 0x00F697D4
    assert LIFECYCLE_MODULE_END_ROM + 0x0C == TOASTY_ROM


def test_lifecycle_v06_installs_exact_runtime_confirmed_seams() -> None:
    rom = _clean_shape()
    result = RunLifecyclePatch(lives=9, continues=5).apply(
        rom, PatchContext(seed="LIFECYCLE-V06")
    )

    assert rom.data[LIFECYCLE_MODULE_ROM:LIFECYCLE_MODULE_END_ROM] == LIFECYCLE_MODULE
    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == LIFECYCLE_MODULE_END_ROM
    assert (
        rom.data[CONFIG_ROM : CONFIG_ROM + len(RUNTIME_CONFIRMED_V06_CONFIG)]
        == RUNTIME_CONFIRMED_V06_CONFIG
    )
    assert rom.read_u32(FINAL_FULL_HP_STORE_ROM) == 0

    for offset, _expected, replacement, _label in HOOKS:
        assert rom.data[offset : offset + len(replacement)] == replacement

    assert "Very Hard" in result[0]
    assert "Game Over" in result[3]


def test_lifecycle_v06_preserves_existing_longer_shared_file() -> None:
    rom = _clean_shape()
    existing_end = TOASTY_ROM + 0x100
    rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, existing_end)

    RunLifecyclePatch(lives=9, continues=5).apply(
        rom, PatchContext(seed="LIFECYCLE-V06")
    )

    assert rom.read_u32(EXPANSION_FILE_ENTRY_ROM + 4) == existing_end
    assert rom.data[LIFECYCLE_MODULE_ROM:LIFECYCLE_MODULE_END_ROM] == LIFECYCLE_MODULE


def test_configurable_run_defaults_only_change_v06_immediates() -> None:
    configured = configured_lifecycle_module("hard", 5, 3)
    assert len(configured) == len(LIFECYCLE_MODULE)

    differing_words = [
        offset
        for offset in range(0, len(LIFECYCLE_MODULE), 4)
        if configured[offset : offset + 4] != LIFECYCLE_MODULE[offset : offset + 4]
    ]
    assert differing_words == [0x320, 0x328, 0x330, 0x33C, 0x358, 0x368]

    rom = _clean_shape()
    RunLifecyclePatch(
        difficulty="hard",
        lives=5,
        continues=3,
        persist_hp=True,
    ).apply(rom, PatchContext(seed="RUN-SETTINGS"))

    assert rom.data[CONFIG_ROM : CONFIG_ROM + 6] == bytes.fromhex("000300050003")
    assert rom.data[LIFECYCLE_MODULE_ROM:LIFECYCLE_MODULE_END_ROM] == configured
    assert rom.read_u32(FINAL_FULL_HP_STORE_ROM) == 0


def test_hp_persistence_off_keeps_stock_full_hp_store() -> None:
    rom = _clean_shape()
    RunLifecyclePatch(persist_hp=False).apply(
        rom, PatchContext(seed="HP-RESET")
    )

    assert rom.read_u32(FINAL_FULL_HP_STORE_ROM) == EXPECTED_FINAL_FULL_HP_STORE


def test_debug_reset_block_reconstructs_exact_initial_backing_with_bounded_stores() -> None:
    """Evaluate the emitted reset block's small instruction subset, delay slots included."""

    for debug in (False, True):
        module = configured_lifecycle_module("very_hard", 9, 5, debug_all_keys=debug)
        start = MODULE_RESET_INVENTORY_OFFSET
        end = start + MODULE_RESET_INVENTORY_SIZE
        assert module[:start] == LIFECYCLE_MODULE[:start]
        assert module[end:] == LIFECYCLE_MODULE[end:]
        code = module[start:end]
        words = [int.from_bytes(code[i:i + 4], "big") for i in range(0, len(code), 4)]
        registers = [0] * 32
        stores: dict[int, int] = {}

        def execute(word: int, registers: list[int], stores: dict[int, int]) -> None:
            op, rs, rt = word >> 26, (word >> 21) & 31, (word >> 16) & 31
            immediate = word & 0xFFFF
            signed = immediate if immediate < 0x8000 else immediate - 0x10000
            if word == 0:
                pass
            elif op == 0x0F:  # LUI
                registers[rt] = immediate << 16
            elif op == 0x09:  # ADDIU
                registers[rt] = (registers[rs] + signed) & 0xFFFFFFFF
            elif op == 0x0D:  # ORI
                registers[rt] = registers[rs] | immediate
            elif op == 0x0B:  # SLTIU
                registers[rt] = int(registers[rs] < (signed & 0xFFFFFFFF))
            elif op == 0 and word & 63 == 0x25:  # OR
                registers[(word >> 11) & 31] = registers[rs] | registers[rt]
            elif op == 0x2B:  # SW
                address = (registers[rs] + signed) & 0xFFFFFFFF
                assert BOX0_VA <= address < BOX0_VA + 160
                assert address % 4 == 0
                stores[address] = registers[rt]
            else:
                raise AssertionError(f"unexpected reset instruction 0x{word:08X}")

        pc = steps = 0
        while pc < len(words):
            steps += 1
            assert steps < 500, "reset loop must terminate"
            word = words[pc]
            if word >> 26 == 0x05:  # BNE, with one executed delay slot
                rs, rt = (word >> 21) & 31, (word >> 16) & 31
                immediate = word & 0xFFFF
                signed = immediate if immediate < 0x8000 else immediate - 0x10000
                taken = registers[rs] != registers[rt]
                execute(words[pc + 1], registers, stores)
                pc = pc + 1 + signed if taken else pc + 2
            else:
                execute(word, registers, stores)
                pc += 1
        assert pc == len(words)
        assert len(stores) == 40
        actual = b"".join(stores[a].to_bytes(4, "big") for a in sorted(stores))
        assert actual == starting_inventory(debug_all_keys=debug)
