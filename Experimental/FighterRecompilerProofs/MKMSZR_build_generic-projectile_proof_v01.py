"""Generic projectile proof v01 (Fighter recompiler plan, milestone 2 task 8). Disposable.

Tests the *native enemy-projectile path* for a player projectile, with no Ice-root patching
(Wiki ``Fighter-Recompiler-Components#generic-projectile-lowering-planned``). Mechanics only:
Sub-Zero (clean ROM) gets ``F,F + LK``, which throws the stock Ice-ball art (file 0x87 script
``+0xD90``, now also table-1 slot 0x0D) along the ground plane; on contact the victim takes the
host projectile knock-back reaction 0x39 (as Quan Chi's projectile) and the ball vanishes.

Host path under test (Static-confirmed, runtime Pending):

* child process ``controller_clone_alloc(0x700, child)``: class 0x700 is what the collision
  core treats as a player projectile (gate at 0x8002BB40), as Ice's 0x8004CBC4 does;
* ``projectile_build`` 0x80047160 with type 4 (player) after the guarded table edit
  ``0x800A0324[4] = 0x80291C10`` (player file-0x87 base); palette = file 0x87 +0x45848;
* placement copied from the stock Ice root (0x8004AEE4..0x8004B004);
* collision ``0x8002BA04(record, 0)`` each tick with a KSEG0 record in the payload; animation
  ``0x800304C0``; lifetime ``0x80035088(actor, 200)``; exit as Quan Chi's projectile.

Infrastructure: the Runtime-confirmed Reverse Elbow v6 / teleport v01 proof base (debug stage
select, file 0x1B payload at 0x801AF420, selector-3 bridge, EXP caps), copied from
``Experimental/SektorTransplantBuilders/teleport/MKMSZR_build_sektor_teleport_v01.py``.

Usage::

    python3 MKMSZR_build_generic-projectile_proof_v01.py CLEAN.z64 -o MKMSZR_generic-projectile_common_proof_v01.z64
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from mkmszr.checksum import calculate_crc_6102
from mkmszr.fighter_import import host
from mkmszr.fighter_import.mips import Assembler

CLEAN_SHA256 = "9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6"
VA_TO_ROM = 0x7FFFF400

PAYLOAD_VA = 0xA01AF420  # KSEG1 execution alias (v6 infrastructure)
KSEG0_DELTA = 0x20000000  # payload data read through its KSEG0 alias (strike record)
PAYLOAD_ROM = 0x00F10000
PAYLOAD_LIMIT = 0x400

FILE87_ROM = 0x00748920
TABLE1_SLOT = 0x0D  # empty in stock (Wiki Sub-Zero-to-Sektor-Animation-Mapping)
ICE_BALL_SCRIPT = 0xD90  # stock Ice projectile loop (primary 0x0D, file +0xFD0)
ICE_BALL_W, ICE_BALL_H = 84, 28  # its two frames (Type 5), anchor (80, 14)
PALETTE_OFF = 0x45848  # file-0x87 palette record header (count 0x40), colours at +4
TYPE_FILE_TABLE = 0x800A0324
PLAYER_FILE_BASE = 0x80291C10
PLAYER_TYPE = 4

F_CLONE = 0x8002830C
F_PROJ_BUILD = 0x80047160
F_SELECT = 0x8002FE54
F_ADVANCE = 0x800304C0
F_SLEEP = 0x80028794
F_OFFSCREEN = 0x80035088
F_COLLIDE = 0x8002BA04
F_ACTOR_REMOVE = 0x80024B00
F_TEX_RELEASE = 0x8001C424
F_EXIT = 0x80028564
F_OFFSET = 0x80031208
ACTOR_LIST = 0x80111C98
CAMERA_MODE = 0x80111F98  # read by the stock Ice placement

SPEED = 0x60000  # Quan Chi's projectile speed (host units, 0x80049720)
OFFSCREEN_MARGIN = 200
ICE_ACTION_ID = 0x603  # as the teleport proofs (stock special action id)
THROW_SCRIPT = 0xDA0  # primary 0x24, the stock Ice throw pose script
THROW_TICKS = 24

# 16-byte host strike record: Ice-ball box (0x800AF634), Quan Chi projectile reaction 0x39
# (push back) / blocked 0x01 and damage 28 / block 4 (0x800B08F4), stock trailer.
STRIKE_RECORD = bytes.fromhex("0004 fff3 0050 0014 3901 1c04 0001 0000".replace(" ", ""))


def be32(data: bytes | bytearray, off: int) -> int:
    return int.from_bytes(data[off : off + 4], "big")


def put32(data: bytearray, off: int, value: int) -> None:
    data[off : off + 4] = (value & 0xFFFFFFFF).to_bytes(4, "big")


def guarded(rom: bytearray, off: int, old_hex: str, new_hex: str) -> None:
    old, new = bytes.fromhex(old_hex), bytes.fromhex(new_hex)
    assert bytes(rom[off : off + len(old)]) == old, hex(off)
    rom[off : off + len(new)] = new


def jal(va: int) -> int:
    return 0x0C000000 | ((va >> 2) & 0x03FFFFFF)


def proof_base(rom: bytearray) -> None:
    """Debug stage select + boot skip (teleport v01 builder, lines 421-440)."""

    words = lambda vals: b"".join(int(v & 0xFFFFFFFF).to_bytes(4, "big") for v in vals)
    debug_menu_va, a_route_jal, wrap_last, count = 0x8000D0B8, 0xE028, 0xDD60, 0xDD64
    menu_table, selection_load, mapper_rom, mapper_va = 0x9B7DC, 0x15CD0, 0x9A700, 0x80099B00
    original = (0x800AA034, 0x800AA02C, 0x800AA024, 0x800AA01C, 0x800AA014, 0x800AA00C,
                0x800AA004, 0x800A9FF4, 0x800A9FEC, 0x800A9FE0, 0x800A9FD0, 0)  # fmt: skip
    safe = (0x800AA034, 0x800AA02C, 0x800AA024, 0x800AA01C, 0x800AA014, 0x800AA00C,
            0x800A9FEC, 0x800A9FE0, 0, 0, 0, 0)  # fmt: skip
    mapper = bytes.fromhex("3C03800C8C6311E02C61000650200001246300023C02802903E00008A0441C0C")
    assert be32(rom, a_route_jal) == 0x0C00A0C3 and be32(rom, wrap_last) == 0x2414000A
    assert be32(rom, count) == 0x2A82000B
    assert bytes(rom[menu_table : menu_table + 48]) == words(original)
    put32(rom, a_route_jal, jal(debug_menu_va))
    put32(rom, wrap_last, 0x24140007)
    put32(rom, count, 0x2A820008)
    rom[menu_table : menu_table + 48] = words(safe)
    put32(rom, selection_load, jal(mapper_va))
    put32(rom, selection_load + 4, 0)
    assert set(rom[mapper_rom : mapper_rom + len(mapper)]) <= {0}
    rom[mapper_rom : mapper_rom + len(mapper)] = mapper
    boot = 0x7A3F4
    assert bytes(rom[boot : boot + 24]) == bytes.fromhex(
        "0C01F113000000000C01F143000000000C01857624040080"
    )
    put32(rom, boot, 0x10000003)


def v6_infrastructure(rom: bytearray) -> None:
    """Payload arena, loader hook/stub, selector 3, file 0x1B, EXP caps (teleport v01)."""

    guarded(rom, 0x4B654, "2cc20003", "2cc20004")  # permit selector 3
    guarded(rom, 0x66F64, "2442f420", "2442f820")  # arena prefix reservation
    guarded(rom, 0x66FE0, "27bdffe83c02801b2442f420", "08026861000000002442f820")  # loader hook
    guarded(rom, 0x9AD84, "00" * 0x50, (
        "27bdffe83c02801b2442f820afbf00103c04800fac82ecd00c0198e400000000"
        "2404001b3c05801b24a5f4200c01975900000000"
        "3c0880113409270fa509200e8fbf001027bd001803e0000800000000"
    ).ljust(0xA0, "0"))  # loader stub (+ v6 max EXP)  # fmt: skip
    guarded(
        rom, 0xA1C5C, "00" * 16, "a01af42024040003" + "08012a93" + "00000000"
    )  # table[3] + thunk
    guarded(
        rom, 0xA5154, "00" * 8, f"{PAYLOAD_ROM:08x}{PAYLOAD_ROM + PAYLOAD_LIMIT:08x}"
    )  # file 0x1B
    for off, old in ((0xA6FFC, "0104036b"), (0xA7000, "09470591"), (0xA7004, "11ad0d16"),
                     (0xA700C, "1ccf4e20")):  # fmt: skip
        guarded(rom, off, old, "270f270f")  # v6 EXP caps


def descriptor(masks, sel, cond, action, window, right, left) -> bytes:  # type: ignore[no-untyped-def]
    b = bytearray(0x2C)
    b[0:2], b[2:4] = masks[0].to_bytes(2, "big"), masks[1].to_bytes(2, "big")
    b[4:8], b[8:12], b[12:16] = (
        sel.to_bytes(4, "big"),
        cond.to_bytes(4, "big"),
        action.to_bytes(4, "big"),
    )
    b[16:18] = window.to_bytes(2, "big")
    for n, t in enumerate(right):
        b[0x12 + 2 * n : 0x14 + 2 * n] = t.to_bytes(2, "big")
    for n, t in enumerate(left):
        b[0x1E + 2 * n : 0x20 + 2 * n] = t.to_bytes(2, "big")
    return bytes(b)


def emit_payload() -> tuple[bytes, dict[str, int]]:
    a = Assembler(PAYLOAD_VA)
    frame = host.Frame(size=0x40, strike_offset=0x30)

    # -- action root (selector 3, runs as the player's controller) ------------------------
    host.enter_action(a, frame, ())
    host.load_controller(a)
    host.set_special_lock(a)
    host.set_action_id(a, ICE_ACTION_ID)
    host.special_begin(a)
    host.start_animation(a, THROW_SCRIPT, 3)
    # child = controller_clone_alloc(0x700, projectile); copy the opponent links as 0x8004CBC4
    a.li("a0", 0x700)
    a.la("a1", "projectile")
    a.jal(F_CLONE)
    a.beqz("v0", "after_spawn")
    a.lw("t0", 0x63C, "s0")
    a.sw("t0", 0x63C, "v0")
    a.lw("t0", 0x640, "s0")
    a.sw("t0", 0x640, "v0")
    a.sw("zero", 0x638, "v0")
    a.label("after_spawn")
    host.sleep_ticks(a, THROW_TICKS, "throw_wait")
    host.exit_action(a)

    # -- projectile process (class 0x700) ------------------------------------------------
    a.label("projectile")
    a.addiu("sp", "sp", -0x40)
    host.load_controller(a)  # s0 = this child, s1 = the cloned owner actor (player)
    a.lhu("a0", 0x78, "s1")  # owner type (4)
    a.li("a1", TABLE1_SLOT)
    a.li("a2", 0x46)  # actor +0xD8, as Quan Chi
    a.li("a3", ICE_BALL_W)
    a.li("t0", ICE_BALL_H)
    a.sw("t0", 0x10, "sp")
    a.addiu("t0", "sp", 0x20)  # texture handle out
    a.sw("t0", 0x14, "sp")
    a.li("t0", PALETTE_OFF)
    a.sw("t0", 0x18, "sp")
    a.jal(F_PROJ_BUILD)
    host.load_controller(a)  # s1 = the projectile actor
    a.li("t0", 0x700)
    a.sh("t0", 0x72, "s1")  # projectile actor tag, as 0x8004CBC4
    # placement: stock Ice root, by camera mode 0x80111F98 (0: 216,84; 1: 184,22; 2: -124,0)
    a.li("t9", CAMERA_MODE)
    a.lh("t1", 0, "t9")
    a.li("s2", 216)
    a.li("s3", 84)
    a.beqz("t1", "place")
    a.li("t0", -108)
    a.sw("t0", 0x50, "s1")
    a.sw("zero", 0x54, "s1")
    a.li("t2", 1)
    a.bne("t1", "t2", "mode2")
    a.li("t0", -512)  # mode 1
    a.li("s2", 184)
    a.li("s3", 22)
    a.lhu("t3", 0x8C, "s1")
    a.andi("t3", "t3", 0x10)
    a.beqz("t3", "set_yaw")
    a.li("t0", 512)
    a.beq("zero", "zero", "set_yaw")
    a.label("mode2")
    a.li("t0", 512)
    a.li("s2", -124)
    a.li("s3", 0)
    a.lhu("t3", 0x8C, "s1")
    a.andi("t3", "t3", 0x10)
    a.beqz("t3", "set_yaw")
    a.li("t0", -512)
    a.label("set_yaw")
    a.sh("t0", 0x4C, "s1")
    a.label("place")
    a.move("a0", "s1")
    a.move("a1", "s2")
    a.move("a2", "s3")
    a.jal(F_OFFSET)
    host.load_controller(a)
    # velocity along the facing (0x80046F74 copies the owner's facing to controller +0x700)
    a.li("t0", SPEED)
    a.lw("t1", 0x700, "s0")
    a.li("t2", 0x10)
    a.bne("t1", "t2", "set_vel")
    a.subu("t0", "zero", "t0")
    a.label("set_vel")
    a.sw("t0", 0x14, "s1")
    a.lw("t0", 0x34, "s1")
    a.addiu("t0", "t0", -0x1000)  # draw in front, as Quan Chi
    a.sw("t0", 0x34, "s1")
    a.li("a0", 1)
    a.li("a1", TABLE1_SLOT)
    a.jal(F_SELECT)
    a.label("fly")
    host.load_controller(a)
    a.la("a0", "record")
    a.lui("t0", KSEG0_DELTA >> 16)
    a.subu("a0", "a0", "t0")  # KSEG0 alias: the collision core rejects KSEG1 records
    a.sw("a0", 0x638, "s0")  # current strike record, as 0x8004CE6C
    a.move("a1", "zero")
    a.jal(F_COLLIDE)
    a.andi("v0", "v0", 0xFFFF)
    a.li("t0", 0x8000)
    a.beq("v0", "t0", "done")
    host.load_controller(a)
    a.move("a0", "s1")
    a.jal(F_ADVANCE)
    a.li("a0", 1)
    a.jal(F_SLEEP)
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", OFFSCREEN_MARGIN)
    a.jal(F_OFFSCREEN)
    a.beqz("v0", "fly")
    a.label("done")
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", ACTOR_LIST)
    a.jal(F_ACTOR_REMOVE)
    a.lw("a0", 0x20, "sp")
    a.jal(F_TEX_RELEASE)
    a.jal(F_EXIT)
    a.label("child_hang")
    a.beq("zero", "zero", "child_hang")

    # -- data ----------------------------------------------------------------------------
    while (a.pc() - PAYLOAD_VA) % 16:
        a.nop()
    a.label("record")
    for i in range(0, 16, 4):
        a.raw(int.from_bytes(STRIKE_RECORD[i : i + 4], "big"))
    return a.link(), dict(a.labels)


def build(clean: bytes) -> tuple[bytes, dict[str, int]]:
    assert hashlib.sha256(clean).hexdigest() == CLEAN_SHA256, "not the clean MKMSZ USA Rev. 0 ROM"
    rom = bytearray(clean)
    proof_base(rom)
    v6_infrastructure(rom)
    payload, labels = emit_payload()
    assert len(payload) <= PAYLOAD_LIMIT, hex(len(payload))
    assert set(rom[PAYLOAD_ROM : PAYLOAD_ROM + PAYLOAD_LIMIT]) == {0xFF}
    rom[PAYLOAD_ROM : PAYLOAD_ROM + PAYLOAD_LIMIT] = payload + bytes(PAYLOAD_LIMIT - len(payload))

    # player entry of the per-type fighter-file table (only reader: 0x80046F74)
    guarded(
        rom, TYPE_FILE_TABLE - VA_TO_ROM + 4 * PLAYER_TYPE, "00000000", f"{PLAYER_FILE_BASE:08x}"
    )
    # file 0x87 table-1 slot 0x0D (empty) -> the stock Ice-ball script
    guarded(rom, FILE87_ROM + 0x104 + 4 * TABLE1_SLOT, "00000000", f"{ICE_BALL_SCRIPT:08x}")
    assert be32(rom, FILE87_ROM + 4 * 0x0D) == ICE_BALL_SCRIPT  # primary 0x0D, same script

    # Low Kick descriptor -> F,F + LK (stock condition kept, as the teleport proofs)
    stock_lk = descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x80049CB0, 0x14, (8, 7), (9, 7))
    new_lk = descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x800A1060, 0x18, (9, 9), (8, 8))
    guarded(rom, 0xB1B68, stock_lk.hex(), new_lk.hex())
    assert int.from_bytes(rom[0xB1B94:0xB1B96], "big") == 0

    crc1, crc2 = calculate_crc_6102(rom)
    put32(rom, 0x10, crc1)
    put32(rom, 0x14, crc2)
    return bytes(rom), {"payload_len": len(payload), **labels}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("clean", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    rom, info = build(args.clean.read_bytes())
    args.output.write_bytes(rom)
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    print("CRC", " / ".join(f"{be32(rom, o):08X}" for o in (0x10, 0x14)))
    print("PAYLOAD", hex(info["payload_len"]), "bytes; projectile", hex(info["projectile"]),
          "record", hex(info["record"] - KSEG0_DELTA))  # fmt: skip
    print("TEST", "Sub-Zero, classic controls: Forward, Forward + Low Kick, facing an enemy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
