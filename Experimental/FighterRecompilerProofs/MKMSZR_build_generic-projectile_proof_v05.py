"""Generic projectile proof v05 (Fighter recompiler plan, milestone 2 task 8). Disposable.

Owner runtime results for v04 (2026-11-11): launch force and gravity feel much better; the ball
spawns even lower (so the ``0x80031208`` y offset is positive *down* for this actor: +72 moved it
about 36 px down); the sound is wrong in flight and on hit; Sub-Zero stays busy far too long.

v05, otherwise v04:

* spawn offset (-20, -72): the ball about 36 px above v03's height, near MKT's hand height;
* sounds from MKT (``sound.install`` into isolated host chains, the Sektor teleport route):
  Reptile ``ft_sound(0x12)`` (MKT event 0x1CE, the flight hum) every 1.5 host ticks (MKT: every
  3 donor ticks, ``forceball_hum``) and ``ft_sound(5)`` (event 0x1C4) on contact; the lifted
  reaction no longer plays the stock hit sound 0x185;
* recovery: 12 host ticks after the throw instead of 24 (MKT ``forceball_launch``: sleep 8 then
  ``mframew(4)`` over the last part, about 24 donor ticks);
* payload arena widened from 1 KiB to 2 KiB (same v6 infrastructure, floor 0x801AFC20), as the
  later Sektor proofs widened it.
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
from mkmszr.fighter_import import host, sound
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


v01, v02, v04 = _load("v01"), _load("v02"), _load("v04")

PAYLOAD_LIMIT = 0x800
ARENA_LO = (0x801AF420 + PAYLOAD_LIMIT) & 0xFFFF  # 0xFC20, sign-extended under lui 0x801B
DX, DY = -20, -72
THROW_TICKS = 12
HUM, IMPACT = 0x12, 5  # Reptile ft_sound entries
HUM_CHAIN = sound.ISOLATED_CHAINS[10]  # host event 335 (the Sektor teleport chain)
IMPACT_CHAIN = sound.ISOLATED_CHAINS[11]  # host event 336
SAMPLE_ROM = 0x00F70000
REACTION_SOUND_JAL = 8  # word index of 'jal 0x80064D08' (hit sound 0x185) in the lifted reaction


def v6_infrastructure(rom: bytearray) -> None:
    lo = f"{ARENA_LO:04x}"
    v01.guarded(rom, 0x4B654, "2cc20003", "2cc20004")  # permit selector 3
    v01.guarded(rom, 0x66F64, "2442f420", "2442" + lo)  # arena prefix reservation
    v01.guarded(rom, 0x66FE0, "27bdffe83c02801b2442f420", "0802686100000000" + "2442" + lo)
    v01.guarded(rom, 0x9AD84, "00" * 0x50, (
        "27bdffe83c02801b2442" + lo + "afbf00103c04800fac82ecd00c0198e400000000"
        "2404001b3c05801b24a5f4200c01975900000000"
        "3c0880113409270fa509200e8fbf001027bd001803e0000800000000"
    ).ljust(0xA0, "0"))  # loader stub (+ v6 max EXP)  # fmt: skip
    v01.guarded(rom, 0xA1C5C, "00" * 16, "a01af42024040003" + "08012a93" + "00000000")
    v01.guarded(
        rom, 0xA5154, "00" * 8, f"{v01.PAYLOAD_ROM:08x}{v01.PAYLOAD_ROM + PAYLOAD_LIMIT:08x}"
    )
    for off, old in ((0xA6FFC, "0104036b"), (0xA7000, "09470591"), (0xA7004, "11ad0d16"),
                     (0xA700C, "1ccf4e20")):  # fmt: skip
        v01.guarded(rom, off, old, "270f270f")


def emit_payload(info: dict) -> tuple[bytes, dict[str, int]]:  # type: ignore[type-arg]
    a = Assembler(v01.PAYLOAD_VA)
    frame = host.Frame(size=0x40, strike_offset=0x30)

    host.enter_action(a, frame, ())
    host.load_controller(a)
    host.set_special_lock(a)
    host.set_action_id(a, v01.ICE_ACTION_ID)
    host.special_begin(a)
    host.start_animation(a, v01.THROW_SCRIPT, 3)
    a.li("a0", 0x700)
    a.la("a1", "projectile")
    a.jal(v01.F_CLONE)
    a.beqz("v0", "after_spawn")
    a.lw("t0", 0x63C, "s0")
    a.sw("t0", 0x63C, "v0")
    a.lw("t0", 0x640, "s0")
    a.sw("t0", 0x640, "v0")
    a.sw("zero", 0x638, "v0")
    a.label("after_spawn")
    host.sleep_ticks(a, THROW_TICKS, "throw_wait")
    host.exit_action(a)

    a.label("projectile")
    a.addiu("sp", "sp", -0x40)
    host.load_controller(a)
    a.lhu("a0", 0x78, "s1")
    a.li("a1", v02.SLOT_FLIGHT)
    a.li("a2", 0x46)
    a.li("a3", info["tex_w"])
    a.li("t0", info["tex_h"])
    a.sw("t0", 0x10, "sp")
    a.addiu("t0", "sp", 0x20)
    a.sw("t0", 0x14, "sp")
    a.li("t0", info["palette_record"])
    a.sw("t0", 0x18, "sp")
    a.jal(v01.F_PROJ_BUILD)
    host.load_controller(a)
    a.li("t0", 0x700)
    a.sh("t0", 0x72, "s1")
    a.move("a0", "s1")
    a.li("a1", DX)
    a.li("a2", DY)
    a.jal(v01.F_OFFSET)
    host.load_controller(a)
    a.li("t0", v02.SPEED)
    a.lw("t1", 0x700, "s0")
    a.li("t2", 0x10)
    a.bne("t1", "t2", "set_vel")
    a.subu("t0", "zero", "t0")
    a.label("set_vel")
    a.sw("t0", 0x14, "s1")
    a.li("a0", 1)
    a.li("a1", v02.SLOT_FLIGHT)
    a.jal(v01.F_SELECT)
    a.li("s3", 0)  # hum phase: +2 per host tick, play at >= 3 (every 1.5 host ticks)
    a.label("fly")
    a.addiu("s3", "s3", 2)
    a.slti("t0", "s3", 3)
    a.bnez("t0", "no_hum")
    a.addiu("s3", "s3", -3)
    host.play_sound(a, HUM_CHAIN.event)
    a.label("no_hum")
    host.load_controller(a)
    a.la("a0", "record")
    a.lui("t0", v01.KSEG0_DELTA >> 16)
    a.subu("a0", "a0", "t0")
    a.sw("a0", 0x638, "s0")
    a.move("a1", "zero")
    a.jal(v01.F_COLLIDE)
    a.andi("v0", "v0", 0xFFFF)
    a.li("t0", 0x8000)
    a.beq("v0", "t0", "on_contact")
    host.load_controller(a)
    a.move("a0", "s1")
    a.jal(v01.F_ADVANCE)
    a.li("a0", 1)
    a.jal(v01.F_SLEEP)
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", v01.OFFSCREEN_MARGIN)
    a.jal(v01.F_OFFSCREEN)
    a.beqz("v0", "fly")
    a.beq("zero", "zero", "done")
    a.label("on_contact")
    host.play_sound(a, IMPACT_CHAIN.event)
    host.load_controller(a)
    a.sw("zero", 0x14, "s1")
    a.li("a0", 1)
    a.li("a1", v02.SLOT_IMPACT)
    a.jal(v01.F_SELECT)
    a.li("s2", info["impact_ticks"])
    a.label("impact_loop")
    host.load_controller(a)
    a.move("a0", "s1")
    a.jal(v01.F_ADVANCE)
    a.li("a0", 1)
    a.jal(v01.F_SLEEP)
    a.addiu("s2", "s2", -1)
    a.bnez("s2", "impact_loop")
    a.label("done")
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", v01.ACTOR_LIST)
    a.jal(v01.F_ACTOR_REMOVE)
    a.lw("a0", 0x20, "sp")
    a.jal(v01.F_TEX_RELEASE)
    a.jal(v01.F_EXIT)
    a.label("child_hang")
    a.beq("zero", "zero", "child_hang")

    host.emit_sound_player(a)

    while (a.pc() - v01.PAYLOAD_VA) % 16:
        a.nop()
    a.label("record")
    record = v02.strike_record(v04.REACTION)
    for i in range(0, 16, 4):
        a.raw(int.from_bytes(record[i : i + 4], "big"))
    a.label("reaction")
    for word in info["reaction_words"]:
        a.raw(word)
    return a.link(), dict(a.labels)


def build(clean: bytes, mkt: bytes) -> tuple[bytes, dict[str, int]]:
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, (
        "not the clean MKMSZ USA Rev. 0 ROM"
    )
    validate_mkt_n64_rev2(mkt)
    rom = bytearray(clean)
    v01.proof_base(rom)
    v6_infrastructure(rom)

    v02.art = v04.art
    f87, info = v02.enlarged_file87(clean, mkt)
    assert set(rom[v02.FILE87_NEW_ROM : v02.FILE87_NEW_ROM + len(f87)]) == {0xFF}
    rom[v02.FILE87_NEW_ROM : v02.FILE87_NEW_ROM + len(f87)] = f87
    v01.guarded(rom, v02.FILE_TABLE_87, "007489200078e300",
                f"{v02.FILE87_NEW_ROM:08x}{v02.FILE87_NEW_ROM + len(f87):08x}")  # fmt: skip
    assert v02.FILE87_NEW_ROM + len(f87) <= SAMPLE_ROM

    bank = sound.MktSoundBank(mkt)
    at = SAMPLE_ROM
    for index, chain in ((HUM, HUM_CHAIN), (IMPACT, IMPACT_CHAIN)):
        at = sound.install(
            rom, clean, bank.event(bank.fighter_event(v02.REPTILE, index)), chain, at
        )

    words = v04.lifted_reaction(clean)
    assert words[REACTION_SOUND_JAL] == 0x0C019342  # jal 0x80064D08 (sound 0x185)
    words[REACTION_SOUND_JAL] = 0
    info = {**info, "reaction_words": words}
    payload, labels = emit_payload(info)
    assert len(payload) <= PAYLOAD_LIMIT, hex(len(payload))
    assert set(rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + PAYLOAD_LIMIT]) == {0xFF}
    rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + PAYLOAD_LIMIT] = payload + bytes(
        PAYLOAD_LIMIT - len(payload)
    )

    v01.guarded(rom, v04.REACTION_TABLE - v01.VA_TO_ROM + 4 * v04.REACTION, f"{v04.DUMMY_REACTION:08x}",
                f"{labels['reaction']:08x}")  # fmt: skip
    v01.guarded(rom, v01.TYPE_FILE_TABLE - v01.VA_TO_ROM + 4 * v01.PLAYER_TYPE, "00000000",
                f"{v01.PLAYER_FILE_BASE:08x}")  # fmt: skip
    stock_lk = v01.descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x80049CB0, 0x14, (8, 7), (9, 7))
    new_lk = v01.descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x800A1060, 0x18, (9, 9), (8, 8))
    v01.guarded(rom, 0xB1B68, stock_lk.hex(), new_lk.hex())

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {"payload_len": len(payload), "size": info["size"], "samples_end": at}


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
    print("CRC", " / ".join(f"{v01.be32(rom, o):08X}" for o in (0x10, 0x14)))
    print("FILE87", hex(info["size"]), "PAYLOAD", hex(info["payload_len"]), "of", hex(PAYLOAD_LIMIT),
          "SAMPLES to", hex(info["samples_end"]), "SPAWN", (DX, DY))  # fmt: skip
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
