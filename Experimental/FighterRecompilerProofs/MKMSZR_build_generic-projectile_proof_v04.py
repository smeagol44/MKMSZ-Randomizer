"""Generic projectile proof v04 (Fighter recompiler plan, milestone 2 task 8). Disposable.

Owner runtime results (2026-11-11): v03 (target thrown toward the attacker) is closer to MKT than
v02; the ball's palette is wrong and it spawns too far forward and too low. Save states (MKT and
v03, static analysis of runtime-captured state) explain both:

* palette: the MKT forceball object is created by the throw animation (token 11, frame
  ``0x2FD4``, whose descriptor carries palette ``0x800BECE4``); the flight frames have no palette
  of their own and keep it; the impact switches to ``0x800BEBD0`` (token 13). v02/v03 used
  Reptile's body palette. v04: flight ``0x800BECE4`` (indices 0..31), impact ``0x800BEBD0``
  (32..63);
* position: in the v03 state the projectile actor sits at Sub-Zero's origin with z -16 (copied
  from Quan Chi's spawn); the ball is drawn about 30 px above the feet, MKT's anchors put it near
  hand height. v04 drops the z shift and offsets the spawn by (``DX``, ``DY``) world units through
  ``0x80031208`` (facing-aware): a calibration to confirm by eye, not a derived value;
* reaction: ``knockback_arc`` toward the attacker, as v03, but the owner found the launch too
  weak. Host 0x25 (``0x80057C14``) launches with ``0x800321D0(-0x3999A, -0x5A3D7, 0x8EE1)``; the
  MKT arc (reaction 0x71: x 0x2CCCC toward, y -0x6CCCC, gravity 0x5199) converted with the
  standard-jump calibration (``physics``) is (-0x3B73B, -0x90623, 0x5A3C): a much higher, lighter
  arc. v04 copies 0x80057C14 (a leaf with no internal branches) into the payload with those three
  constants and installs it in the dummy reaction slot 0x2B (stock ``0x8004E0C0``).

Everything else as v02.
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
from mkmszr.fighter_import import effects, host, physics
from mkmszr.fighter_import.body_build import Donor
from mkmszr.fighter_import.mips import Assembler
from mkmszr.fighter_import.mipsdis import decode
from mkmszr.fighter_import.mkt_fighter import validate_mkt_n64_rev2


def _load(name: str):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(
        name, HERE / f"MKMSZR_build_generic-projectile_proof_{name}.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v01, v02 = _load("v01"), _load("v02")

FLIGHT_PALETTE = 0x800BECE4  # descriptor of frame 0x2FD4 (token 11 creates the ball from it)
IMPACT_PALETTE = v02.IMPACT_PALETTE
REACTION = 0x2B  # dummy slot -> lifted copy of host 0x25 with the MKT arc
REACTION_SRC, REACTION_LEN = 0x80057C14, 0x110
REACTION_TABLE, DUMMY_REACTION = 0x800A1190, 0x8004E0C0
DONOR_ARC = (
    0x2CCCC,
    -0x6CCCC,
    0x5199,
)  # MKT r_reptile forceball (0x80054830): x toward, y, gravity
ARC_X = -physics.convert_velocity(DONOR_ARC[0])  # host 0x25 convention: negative x = toward
ARC_Y = -physics.convert_velocity(-DONOR_ARC[1])
ARC_G = physics.convert_acceleration(DONOR_ARC[2])
DX, DY = -20, 72  # spawn calibration, whole world units (2 per sprite pixel), facing-aware


def art(mkt: bytes) -> tuple[effects.EffectArt, dict[int, int]]:
    donor = Donor(mkt, v02.REPTILE)
    flight = list(effects.mkt_palette(mkt, FLIGHT_PALETTE))
    impact = list(effects.mkt_palette(mkt, IMPACT_PALETTE))
    assert len(flight) == 32 and len(impact) == 32
    rels = sorted(set(v02.FLIGHT)) + sorted(set(v02.IMPACT))
    frames = [v02._frame(donor, r, 0) for r in sorted(set(v02.FLIGHT))]
    frames += [v02._frame(donor, r, 32) for r in sorted(set(v02.IMPACT))]
    index = {r: i for i, r in enumerate(rels)}
    return effects.EffectArt(tuple(frames), tuple(flight + impact), compressed=True), index


def emit_payload(info: dict[str, int]) -> tuple[bytes, dict[str, int]]:
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
    host.sleep_ticks(a, v01.THROW_TICKS, "throw_wait")
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
    a.label("fly")
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

    while (a.pc() - v01.PAYLOAD_VA) % 16:
        a.nop()
    a.label("record")
    record = v02.strike_record(REACTION)
    for i in range(0, 16, 4):
        a.raw(int.from_bytes(record[i : i + 4], "big"))
    a.label("reaction")
    for word in info["reaction_words"]:
        a.raw(word)
    return a.link(), dict(a.labels)


def lifted_reaction(clean: bytes) -> list[int]:
    """Host reaction 0x25 with the MKT arc: only the three jump constants change."""

    words = [
        v01.be32(clean, REACTION_SRC - v01.VA_TO_ROM + 4 * i) for i in range(REACTION_LEN // 4)
    ]
    for i, w in enumerate(words):
        ins = decode(w, REACTION_SRC + 4 * i)
        assert not ins.is_branch, hex(ins.pc)  # a straight leaf: copying is position independent
    patches = {  # word index: (stock, new)
        0x30: (0x3C05FFFC, 0x3C050000 | ((ARC_X >> 16) & 0xFFFF)),  # lui a1
        0x33: (0x34A56667, 0x34A50000 | (ARC_X & 0xFFFF)),  # ori a1
        0x34: (0x3C06FFFA, 0x3C060000 | ((ARC_Y >> 16) & 0xFFFF)),  # lui a2
        0x3B: (0x34C65C29, 0x34C60000 | (ARC_Y & 0xFFFF)),  # ori a2
        0x3D: (0x34078EE1, 0x34070000 | (ARC_G & 0xFFFF)),  # ori a3 (jal delay slot)
    }
    for i, (stock, new) in patches.items():
        assert words[i] == stock, (hex(REACTION_SRC + 4 * i), hex(words[i]))
        words[i] = new
    return words


def build(clean: bytes, mkt: bytes) -> tuple[bytes, dict[str, int]]:
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, (
        "not the clean MKMSZ USA Rev. 0 ROM"
    )
    validate_mkt_n64_rev2(mkt)
    rom = bytearray(clean)
    v01.proof_base(rom)
    v01.v6_infrastructure(rom)

    v02.art = art  # the file builder takes the art from this module
    f87, info = v02.enlarged_file87(clean, mkt)
    assert set(rom[v02.FILE87_NEW_ROM : v02.FILE87_NEW_ROM + len(f87)]) == {0xFF}
    rom[v02.FILE87_NEW_ROM : v02.FILE87_NEW_ROM + len(f87)] = f87
    v01.guarded(rom, v02.FILE_TABLE_87, "007489200078e300",
                f"{v02.FILE87_NEW_ROM:08x}{v02.FILE87_NEW_ROM + len(f87):08x}")  # fmt: skip

    info["reaction_words"] = lifted_reaction(clean)  # type: ignore[assignment]
    payload, labels = emit_payload(info)
    assert len(payload) <= v01.PAYLOAD_LIMIT, hex(len(payload))
    assert set(rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v01.PAYLOAD_LIMIT]) == {0xFF}
    rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v01.PAYLOAD_LIMIT] = payload + bytes(
        v01.PAYLOAD_LIMIT - len(payload)
    )

    v01.guarded(rom, REACTION_TABLE - v01.VA_TO_ROM + 4 * REACTION, f"{DUMMY_REACTION:08x}",
                f"{labels['reaction']:08x}")  # fmt: skip
    v01.guarded(rom, v01.TYPE_FILE_TABLE - v01.VA_TO_ROM + 4 * v01.PLAYER_TYPE, "00000000",
                f"{v01.PLAYER_FILE_BASE:08x}")  # fmt: skip
    stock_lk = v01.descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x80049CB0, 0x14, (8, 7), (9, 7))
    new_lk = v01.descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x800A1060, 0x18, (9, 9), (8, 8))
    v01.guarded(rom, 0xB1B68, stock_lk.hex(), new_lk.hex())

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {
        "payload_len": len(payload),
        "size": info["size"],
        "reaction": labels["reaction"],
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
    print("CRC", " / ".join(f"{v01.be32(rom, o):08X}" for o in (0x10, 0x14)))
    print("FILE87", hex(info["size"]), "PAYLOAD", hex(info["payload_len"]), "SPAWN", (DX, DY))
    print(
        "REACTION",
        hex(REACTION),
        "->",
        hex(info["reaction"]),
        "arc",
        hex(ARC_X),
        hex(ARC_Y),
        hex(ARC_G),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
