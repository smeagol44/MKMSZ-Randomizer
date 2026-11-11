"""Generic projectile proof v07 (Fighter recompiler plan, milestone 2 task 8). Disposable.

The same artifact as v06 (Runtime-confirmed bounded), built by the backend instead of proof code:
the projectile comes from Reptile's move program (``fighters/moves/reptile.json``,
``forceball_fast``) through ``fighter_import.lower_projectile``. Only the proof base (debug stage
select, v6 payload arena, file relocation, the Sub-Zero parent action on ``F,F + LK``) stays here.
v07 is byte-identical to v06; ``tests/test_lower_projectile.py`` checks it.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from mkmszr.checksum import calculate_crc_6102
from mkmszr.fighter_import import components, host, sound
from mkmszr.fighter_import import lower_projectile as lp
from mkmszr.fighter_import.mips import Assembler
from mkmszr.fighter_import.mkt_fighter import validate_mkt_n64_rev2


def _load(name: str):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(
        name, HERE / f"MKMSZR_build_generic-projectile_proof_{name}.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v01, v05 = _load("v01"), _load("v05")

REPTILE = 19
FILE87_NEW_ROM, FILE87_SIZE, SAFE_END, FILE_TABLE_87 = 0x00F20000, 0x459E0, 0x4E544, 0xA5664
SLOTS = (0x0D, 0x12)  # empty stock table-1 slots
CHAINS = (sound.ISOLATED_CHAINS[10], sound.ISOLATED_CHAINS[11])  # host events 335, 336
SAMPLE_ROM = 0x00F70000
REACTION_SLOT = 0x2B  # dummy stock reaction
THROW_TICKS = 12


def projectile_step(move: str = "forceball_fast") -> dict:  # type: ignore[type-arg]
    moves, _ = components.load_programs("reptile")
    (m,) = [m for m in moves if m.name == move]
    (step,) = [s for s in m.steps if s["op"] == "projectile"]
    return step


def build(clean: bytes, mkt: bytes) -> tuple[bytes, dict[str, int]]:
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, (
        "not the clean MKMSZ USA Rev. 0 ROM"
    )
    validate_mkt_n64_rev2(mkt)
    step = projectile_step()
    rom = bytearray(clean)
    v01.proof_base(rom)
    v05.v6_infrastructure(rom)

    file87 = bytearray(clean[v01.FILE87_ROM : v01.FILE87_ROM + FILE87_SIZE])
    art = lp.place_art(file87, mkt, REPTILE, step, SLOTS, SAFE_END)
    assert set(rom[FILE87_NEW_ROM : FILE87_NEW_ROM + len(file87)]) == {0xFF}
    rom[FILE87_NEW_ROM : FILE87_NEW_ROM + len(file87)] = file87
    v01.guarded(
        rom,
        FILE_TABLE_87,
        "007489200078e300",
        f"{FILE87_NEW_ROM:08x}{FILE87_NEW_ROM + len(file87):08x}",
    )
    assert FILE87_NEW_ROM + len(file87) <= SAMPLE_ROM
    events, samples_end = lp.install_sounds(rom, clean, mkt, REPTILE, step, CHAINS, SAMPLE_ROM)
    lowered = lp.lower(step, art, events, REACTION_SLOT, clean)

    a = Assembler(v01.PAYLOAD_VA)
    host.enter_action(a, host.Frame(size=0x40, strike_offset=0x30), ())
    host.load_controller(a)
    host.set_special_lock(a)
    host.set_action_id(a, v01.ICE_ACTION_ID)
    host.special_begin(a)
    host.start_animation(a, v01.THROW_SCRIPT, 3)
    lp.emit_spawn(a)
    host.sleep_ticks(a, THROW_TICKS, "throw_wait")
    host.exit_action(a)
    lp.emit_process(a, lowered)
    host.emit_sound_player(a)
    lp.emit_data(a, lowered, v01.PAYLOAD_VA)
    payload = a.link()
    assert len(payload) <= v05.PAYLOAD_LIMIT, hex(len(payload))
    assert set(rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v05.PAYLOAD_LIMIT]) == {0xFF}
    rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v05.PAYLOAD_LIMIT] = payload + bytes(
        v05.PAYLOAD_LIMIT - len(payload)
    )

    reaction_rom = lp.REACTION_TABLE - v01.VA_TO_ROM + 4 * REACTION_SLOT
    v01.guarded(rom, reaction_rom, f"{lp.DUMMY_REACTION:08x}", f"{a.labels['reaction']:08x}")
    type_rom = lp.TYPE_FILE_TABLE - v01.VA_TO_ROM + 4 * lp.PLAYER_TYPE
    v01.guarded(rom, type_rom, "00000000", f"{lp.PLAYER_FILE_BASE:08x}")
    stock_lk = v01.descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x80049CB0, 0x14, (8, 7), (9, 7))
    new_lk = v01.descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x800A1060, 0x18, (9, 9), (8, 8))
    v01.guarded(rom, 0xB1B68, stock_lk.hex(), new_lk.hex())

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {
        "payload_len": len(payload),
        "file87": len(file87),
        "samples_end": samples_end,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("clean", type=Path)
    parser.add_argument("mkt", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    rom, info = build(args.clean.read_bytes(), args.mkt.read_bytes())
    args.output.write_bytes(rom)
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    print("PAYLOAD", hex(info["payload_len"]), "FILE87", hex(info["file87"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
