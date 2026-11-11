"""Generic projectile proof v02 (Fighter recompiler plan, milestone 2 task 8). Disposable.

v01 (runtime: spawned, flew, hit and pushed back; wrong palette, as expected) proved the native
enemy-projectile path for a player projectile. v02 keeps that path and swaps in Reptile's MKT
forceball as data from the move program (``fighters/moves/reptile.json``, ``forceball_fast``):

* art: MKT table 1 slot 5, part 3 (flight loop ``0x3078 0x308C 0x30A0 0x308C``, rate 3) and part
  4 (impact, 7 frames, rate 3, its own palette ``0x800BEBD0`` bound by token 13), type-4 images
  in an enlarged file 0x87 (relocated to ROM 0xF20000), host table-1 slots 0x0D (flight) and
  0x12 (impact), both empty in stock; one 64-colour palette: Reptile's 32 colours (0x800B9F3C)
  then the impact palette's 32 (impact indices shifted by 32);
* frames per host tick resampled from the donor rate (``physics.resample_frame_cycle``);
* speed: donor 0x59999 -> host 0x77776 (the conversion of Sektor's accepted rocket);
* no placement offset: the MKT frame anchors place the ball, as in MKT (match_ani_points);
* strike: the MKT box (99, 44, 47, 61) verbatim (as the accepted rocket), damage 18 / chip 2;
  victim reaction by meaning ``knockback_arc`` -> host 0x1A (``0x80057B04``: hit sound 0x185, hit
  effect process 0x8005ED88, arc ``0x800321D0(0x39999, -0x5A3D7, 0x8EE1)`` away from the
  attacker), blocked -> host 0x05. v03 uses its mirror 0x25 (``0x80057C14``, identical but
  ``-0x3999A``: toward the attacker), so the owner can compare the two directions;
* on contact the ball stops and plays the impact frames, then is removed.

Usage (v03 is the same build with ``--reaction toward``)::

    python3 MKMSZR_build_generic-projectile_proof_v02.py CLEAN.z64 MKT.z64 -o MKMSZR_generic-projectile_common_proof_v02.z64
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
from mkmszr.fighter_import.mkt_fighter import validate_mkt_n64_rev2
from mkmszr.fighter_import.projectile import mkt_color_to_host

_spec = importlib.util.spec_from_file_location(
    "v01", HERE / "MKMSZR_build_generic-projectile_proof_v01.py"
)
assert _spec and _spec.loader
v01 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v01)

REPTILE = 19
FLIGHT = (0x3078, 0x308C, 0x30A0, 0x308C)  # MKT table 1 slot 5 part 3 (loop)
IMPACT = (0x30B4, 0x30CC, 0x30CC, 0x30E0, 0x30F4, 0x3108, 0x311C)  # part 4
DONOR_RATE = 3  # forceball_proc: proj_set_xvel(.., 3); impact mframew(3)
IMPACT_PALETTE = 0x800BEBD0  # token 13 before part 4
SLOT_FLIGHT, SLOT_IMPACT = 0x0D, 0x12  # empty host table-1 slots
SPEED = 0x77776  # physics.fold_donor_speeds(0x59999) with 2 units per texel

FILE87_NEW_ROM = 0x00F20000
FILE87_SIZE = 0x459E0
SAFE_END = 0x4E544  # largest runtime-confirmed file 0x87 (v49 budget)
FILE_TABLE_87 = 0xA5664

# box (99, 44, 47, 61) from MKT strike 0x11 (0x800B03CC); reaction 0x0C / blocked 0x05;
# damage 18 / chip 2 (MKT); stock trailer.
# Mirrored host reactions: same sound, effect and arc; only the x direction differs.
REACTIONS = {"away": 0x1A, "toward": 0x25}


def strike_record(reaction: int) -> bytes:
    return bytes.fromhex("0063002c002f003d" + f"{reaction:02x}05" + "1202" + "00010000")


def _frame(donor: Donor, rel: int, shift: int) -> effects.EffectFrame:
    f = donor.frame(rel)
    indices = bytes(0 if v == 0 else v + shift for v in f["padded"])
    return effects.EffectFrame(f["w"], f["eh"], f["x"], f["y"], indices)


def art(mkt: bytes) -> tuple[effects.EffectArt, dict[int, int]]:
    donor = Donor(mkt, REPTILE)
    body = [mkt_color_to_host(c) for c in donor.palette()]
    impact = list(effects.mkt_palette(mkt, IMPACT_PALETTE))
    assert len(body) == 32 and len(impact) == 32
    rels = sorted(set(FLIGHT)) + sorted(set(IMPACT))
    frames = [_frame(donor, r, 0) for r in sorted(set(FLIGHT))]
    frames += [_frame(donor, r, 32) for r in sorted(set(IMPACT))]
    index = {r: i for i, r in enumerate(rels)}
    return effects.EffectArt(tuple(frames), tuple(body + impact), compressed=True), index


def enlarged_file87(clean: bytes, mkt: bytes) -> tuple[bytes, dict[str, int]]:
    f87 = bytearray(clean[v01.FILE87_ROM : v01.FILE87_ROM + FILE87_SIZE])
    effect_art, index = art(mkt)
    placed = effects.layout(effect_art, (FILE87_SIZE + 3) & ~3)
    f87 += bytes(placed.offset - len(f87)) + placed.data
    # shape offsets of each placed frame: layout's script lists them in frame order
    shapes = [int.from_bytes(placed.data[placed.script - placed.offset + 4 * i :][:4], "big")
              for i in range(len(index))]  # fmt: skip
    shape = {rel: shapes[i] for rel, i in index.items()}

    def script(words: list[int]) -> int:
        nonlocal f87
        at = len(f87)
        f87 += b"".join(w.to_bytes(4, "big") for w in words)
        return at

    flight_ticks = physics.resample_frame_cycle([shape[r] for r in FLIGHT], DONOR_RATE)
    flight_at = len(f87)
    script(flight_ticks + [1, flight_at])  # loop
    impact_ticks = [
        shape[IMPACT[(2 * k) // DONOR_RATE]] for k in range((len(IMPACT) * DONOR_RATE + 1) // 2)
    ]
    impact_at = len(f87)
    script(impact_ticks + [1, impact_at + 4 * (len(impact_ticks) - 1)])  # hold the last frame
    assert len(f87) <= SAFE_END, hex(len(f87))
    for slot, at in ((SLOT_FLIGHT, flight_at), (SLOT_IMPACT, impact_at)):
        off = 0x104 + 4 * slot
        assert f87[off : off + 4] == bytes(4), hex(slot)
        f87[off : off + 4] = at.to_bytes(4, "big")
    w, h = effect_art.slot_size
    return bytes(f87), {"palette_record": placed.offset, "flight": flight_at, "impact": impact_at,
                        "impact_ticks": len(impact_ticks), "tex_w": w, "tex_h": h, "size": len(f87)}  # fmt: skip


def emit_payload(info: dict[str, int], reaction: int) -> tuple[bytes, dict[str, int]]:
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
    a.li("a1", SLOT_FLIGHT)
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
    a.li("t0", SPEED)
    a.lw("t1", 0x700, "s0")
    a.li("t2", 0x10)
    a.bne("t1", "t2", "set_vel")
    a.subu("t0", "zero", "t0")
    a.label("set_vel")
    a.sw("t0", 0x14, "s1")
    a.lw("t0", 0x34, "s1")
    a.addiu("t0", "t0", -0x1000)
    a.sw("t0", 0x34, "s1")
    a.li("a0", 1)
    a.li("a1", SLOT_FLIGHT)
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
    a.sw("zero", 0x14, "s1")  # the ball stops (MKT forceball_proc)
    a.li("a0", 1)
    a.li("a1", SLOT_IMPACT)
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
    for i in range(0, 16, 4):
        a.raw(int.from_bytes(strike_record(reaction)[i : i + 4], "big"))
    return a.link(), dict(a.labels)


def build(clean: bytes, mkt: bytes, reaction: str = "away") -> tuple[bytes, dict[str, int]]:
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, (
        "not the clean MKMSZ USA Rev. 0 ROM"
    )
    validate_mkt_n64_rev2(mkt)
    rom = bytearray(clean)
    v01.proof_base(rom)
    v01.v6_infrastructure(rom)

    f87, info = enlarged_file87(clean, mkt)
    assert set(rom[FILE87_NEW_ROM : FILE87_NEW_ROM + len(f87)]) == {0xFF}
    rom[FILE87_NEW_ROM : FILE87_NEW_ROM + len(f87)] = f87
    v01.guarded(rom, FILE_TABLE_87, "007489200078e300",
                f"{FILE87_NEW_ROM:08x}{FILE87_NEW_ROM + len(f87):08x}")  # fmt: skip

    payload, labels = emit_payload(info, REACTIONS[reaction])
    assert len(payload) <= v01.PAYLOAD_LIMIT, hex(len(payload))
    assert set(rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v01.PAYLOAD_LIMIT]) == {0xFF}
    rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v01.PAYLOAD_LIMIT] = payload + bytes(
        v01.PAYLOAD_LIMIT - len(payload)
    )

    v01.guarded(rom, v01.TYPE_FILE_TABLE - v01.VA_TO_ROM + 4 * v01.PLAYER_TYPE, "00000000",
                f"{v01.PLAYER_FILE_BASE:08x}")  # fmt: skip
    stock_lk = v01.descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x80049CB0, 0x14, (8, 7), (9, 7))
    new_lk = v01.descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x800A1060, 0x18, (9, 9), (8, 8))
    v01.guarded(rom, 0xB1B68, stock_lk.hex(), new_lk.hex())

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {"payload_len": len(payload), **info, **labels}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("clean", type=Path)
    parser.add_argument("mkt", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--reaction", choices=sorted(REACTIONS), default="away")
    args = parser.parse_args()
    rom, info = build(args.clean.read_bytes(), args.mkt.read_bytes(), args.reaction)
    args.output.write_bytes(rom)
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    print("CRC", " / ".join(f"{v01.be32(rom, o):08X}" for o in (0x10, 0x14)))
    print("FILE87", hex(info["size"]), "at", hex(FILE87_NEW_ROM), "budget", hex(SAFE_END))
    print("ART", {k: hex(info[k]) for k in ("palette_record", "flight", "impact")},
          "texture", info["tex_w"], "x", info["tex_h"], "impact ticks", info["impact_ticks"])  # fmt: skip
    print("PAYLOAD", hex(info["payload_len"]), "bytes")
    print("TEST", "Sub-Zero, classic controls: Forward, Forward + Low Kick, facing an enemy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
