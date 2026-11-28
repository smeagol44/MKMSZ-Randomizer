"""Build the disposable Cyber Smoke proof from clean MKMSZ USA Rev. 0 and MKT USA Rev. 2."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from mkmszr.checksum import calculate_crc_6102
from mkmszr.fighter_import import commands, fighter_build
from mkmszr.fighter_import.mips import Assembler

SPEC = importlib.util.spec_from_file_location(
    "proof_harness", HERE / "MKMSZR_build_rayden-specials_proof_v31.py"
)
assert SPEC and SPEC.loader
proof_harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof_harness)


RUN_PRESS_CALLBACK = 0x800A0434
STOCK_RUN_PRESS = 0x8003C7E8
RUN_BLOCK_MASK = 0x000C


def install_run_invisibility(rom: bytearray, clean: bytes, built: fighter_build.Built) -> None:
    """Move the staged command to a private table reached from Run press only."""
    hp_table = commands.HOST_POWERS["spine_rip"] - commands.VA_TO_ROM
    record = bytearray(rom[hp_table:hp_table + commands.RECORD])
    polar_blast = commands.record_at(clean, commands.HOST_POWERS["polar_blast"], commands.VA_TO_ROM)
    action = int.from_bytes(record[12:16], "big")
    action_offset = action - fighter_build.LINK_VA
    if (
        record[:4] != bytes.fromhex("00100010")
        or record[4:8] != bytes(4)  # ground-only transfer mode
        or not 0 <= action_offset <= len(built.payload) - 16
        or int.from_bytes(built.payload[action_offset + 12:action_offset + 16], "big")
        != (0x24040000 | built.selectors["invisibility"])
        or record[0x10:0x12] != bytes.fromhex("0028")
        or record[0x12:0x18] != bytes.fromhex("000600060000")
        or rom[hp_table + commands.RECORD:hp_table + 2 * commands.RECORD] != polar_blast
        or rom[hp_table + 2 * commands.RECORD:hp_table + 2 * commands.RECORD + 2] != bytes(2)
    ):
        raise ValueError("Unexpected invisibility staging record")
    record[:4] = RUN_BLOCK_MASK.to_bytes(2, "big") * 2
    table = bytes(record) + bytes(4)

    offset = (len(built.payload) + 15) & ~15
    rom_offset = fighter_build.SCRATCH_ROM + offset
    table_va = fighter_build.LINK_VA + offset
    code = Assembler(table_va + len(table), cached_calls=True)
    code.li("t0", commands.HELD_BUTTONS)
    code.lhu("t1", 0, "t0")
    code.andi("t1", "t1", RUN_BLOCK_MASK)
    code.addiu("t0", "zero", RUN_BLOCK_MASK)
    code.bne("t1", "t0", "done")
    code.li("a0", table_va)
    code.j(commands.PARSER)
    code.label("done")
    code.jr("ra")
    code.nop()
    blob = table + code.link()
    end = rom_offset + len(blob)
    if end > fighter_build.SCRATCH_ROM + fighter_build.PAYLOAD_LIMIT:
        raise ValueError("Run command table would exceed the proof payload capacity")
    if rom[rom_offset:end] != clean[rom_offset:end]:
        raise ValueError("Run command table overlaps the built payload")

    slot = RUN_PRESS_CALLBACK - commands.VA_TO_ROM
    proof_harness.v01.guarded(rom, slot, f"{STOCK_RUN_PRESS:08x}", f"{table_va + len(table):08x}")
    rom[rom_offset:end] = blob
    rom[hp_table:hp_table + commands.RECORD] = polar_blast
    rom[hp_table + commands.RECORD:hp_table + commands.RECORD + 2] = bytes(2)


def build(clean: bytes, mkt: bytes) -> tuple[bytes, fighter_build.Built]:
    if hashlib.sha256(clean).hexdigest() != proof_harness.v01.CLEAN_SHA256:
        raise ValueError("Expected the clean MKMSZ USA Rev. 0 ROM")
    built = fighter_build.build(clean, mkt, "cyber-smoke")
    rom = bytearray(built.rom)
    install_run_invisibility(rom, clean, built)
    proof_harness.v01.proof_base(rom)
    proof_harness.harness(rom)
    crc1, crc2 = calculate_crc_6102(rom)
    proof_harness.v01.put32(rom, 0x10, crc1)
    proof_harness.v01.put32(rom, 0x14, crc2)
    return bytes(rom), built


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clean", type=Path)
    parser.add_argument("mkt", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() in {args.clean.resolve(), args.mkt.resolve()}:
        parser.error("Choose a separate output path")
    rom, built = build(args.clean.read_bytes(), args.mkt.read_bytes())
    with args.output.open("xb") as file:
        file.write(rom)
    print("SHA-256", hashlib.sha256(rom).hexdigest())
    print("Generic payload", hex(len(built.payload)), "selectors", built.selectors)
    print("Invisibility input: hold Block, Up, Up, press Run. Ground only.")
    for name, value in built.report.items():
        if name not in {"body", "commands", "payload_end"}:
            print(name, value)


if __name__ == "__main__":
    main()
