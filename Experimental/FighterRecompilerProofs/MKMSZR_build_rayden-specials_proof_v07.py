"""Rayden specials proof v07 (Fighter recompiler plan, milestone 6): Lightning and Torpedo. Disposable.

The generic build of his description (``fighter_import.fighter_build.build``: body, combos,
throw, getup sound, voices, and his specials from ``fighters/moves/rayden.json``) plus the
specials proofs' harness (debug stage select, boot skip, max EXP, the payload raw-loaded at
0x801AF420 from ROM 0xF10000 through file 0x1B, 16 KiB arena: Reptile proof v22's).

Lightning (D,F + LP, MKT ``0x800ABA54`` -> special 0x2E -> ``0x80077DF8(0)``) in Ice Blast's
slot, with the generic projectile: his throw pose (table-0 slot 0x24, phase 1, rate 3) and
sound 2, the bolt (slot 0x43 part 3, looping) at speed 0x80000 rate 3 with palette 0x800B9B04,
strike 17 (box 133,36,60,16; damage 22, chip 4) and the impact burst (part 4, rate 4) at the
opponent. Stand-ins and gaps (owner to judge): the host roundhouse launch (0x0C) for MKT's
victim reaction 0x80, no forming sparks (parts 1-2), a silent impact (his layered hit sounds),
a first spawn offset. Also: the knockdown's later lying phase shows his flat frame (owner,
inputs v01).

v02 added the Torpedo (B,B,F, no button, also airborne; owner 2026-11-24) in Ice Clone's slot:

* **stick commands** (``commands``, program buttons ``"stick"``): the host raises events 8 Left
  and 9 Right on stick presses; their per-actor-type records (0x800A07E4 / 0x800A085C) have no
  callbacks, so the player's callback runs a stick table through the parser (masks 0xA000, no
  buttons; tokens B,B,F newest first: 9,8,8 facing right, 8,9,9 facing left; window 0x20);
* **airborne start**: transfer mode 1 (mode 0 refuses an airborne start) and a gate without
  the floor and fall-speed checks (``specials.torpedo.airborne``);
* **the flight**: begin (action 0x21E, facing the opponent), ``hover`` (no gravity, no y
  motion, the airborne counter kept), his sound 9, the take-off (table-1 slot 0, phase 1, rate
  3), the flying pose, velocity 0x80000, then a 26-tick strike window (box 80,45,90,24; damage
  30, chip 7) hovering every tick; on a hit he stops and plays sound 13;
* **the end**: stop, face, his recovery pose (slot 0x16), and MKT's slow drop to the floor
  (0x800321D0 with y 0xD999, gravity 0x6CCC; it returns on landing).

Stand-in (owner to judge): sound 9 for MKT's random 9-11.

v03 fixes the owner's v02 test (2026-11-24, save state "hang_torpedo_hit_close"):

* **the hang after a hit up close**: the stock jump 0x800321D0 copies controller +0x70C to +0x68C
  and calls it every air tick when non-zero; every stock caller clears it first, the ``jump``
  step did not. The save state's game thread faulted at 0x801125A0 (TLB miss) called from
  0x80032448: a stale +0x70C. The ``jump`` step now clears it;
* **the flying pose showed one frame, then a standing frame**: MKT's table-1 slot 3 starts at
  word 6 of slot 0, so the new script for slot 0 ended after two phases, and the ``pose`` at
  offset 6 read the next script's first frame. MKT also never shows word 6 (0x2114, a standing
  frame): it plays phase 1, then phase 2 (``mframew`` twice), and holds phase 2's last frame
  0x2100, the flat flight, through the flight. Now: take-off phase, ``finish`` (rate 3), no pose;
  the build refuses a pose offset past its script;
* **the carry** (owner: the torpedo always carries): MKT's hit 0x800452C4 takes the victim along
  for up to 0x20 donor ticks or until a wall, then his sound 13 and the victim is thrown back
  (do_jump(0x33333, -0x6CCCD, 0x5199)). New victim reaction ``torpedo_carry`` (a spare
  reaction-table entry): the victim morphs, stops, shows root 0x1E's first frame and stays at
  its contact distance in front of the player each tick while the attacker's ``carry`` step
  keeps a shared payload word set; it clears the word when its room to the wall ahead drops
  under 20 px, then runs the lifted knockback with MKT's release arc. The attacker plays his
  sound 8 on the hit, keeps flying (hover, no fighter collision) until the word clears or 16 host
  ticks pass, then stops and plays sound 13. MKT's screen shake has no host equivalent yet.

v04 (owner on v03, 2026-11-24: "almost good"; Rayden's hands should grab the victim's waist, and
an airborne torpedo must not carry the victim along the ground or push it off a ledge: it stays
airborne while held and falls only when released): the victim is pulled to a grab point, 72 px
in front of his anchor (the flat frame reaches 66 px) at his own y, the height a ground carry
already showed right, and held there each tick with no gravity or vertical speed, its previous
y set too (no landing by crossing), and its airborne counter counting while above its floor (no
stock fall, no ledge grab). Tunable as ``specials.torpedo.carry`` (``dx_px``, ``dy_px``).

v05 (owner on v04, 2026-11-24):

* **a carried enemy still fell at a ledge**: the per-tick floor check 0x80024BA8 also runs for
  enemies, and installs the stock fall where no floor region matches while controller +0x6B0
  is zero. v04 counted the held victim's airborne counter only above its floor, so a carry at
  ground level reached the ledge with the counter at zero. The victim's counter, and Rayden's in
  ``hover`` (a ground torpedo over a ledge), now count every tick;
* **the flight felt short** (owner calibration): the hit window is 40 donor ticks (MKT 26; 20 host
  ticks), ``specials.torpedo.strike_ticks``;
* **no Ice cost for movement abilities** (owner rule): move programs mark them ``"movement":
  true`` and the build charges nothing unless the description sets a cost. The torpedo is free
  (Ice Clone's slot cost 0x60 before); Reptile's elbow dash is marked too (already free).

v06 (owner, 2026-11-24: "remove the face opponent. That's up to the player"): the torpedo no
longer turns to the opponent, neither at the start (``specials.torpedo.face`` false: the begin
without the face call, as Acid Spit's) nor before the recovery (``specials.torpedo.skip``:
["face"]). The Lightning still turns, as MKT's does.

v07 (owner on v06, 2026-11-24: after the torpedo "I have no air control (unlike when you jump)"):
the stock jump steers from the held Left/Right each air tick unless the busy input map is active,
which the special holds. ``specials.torpedo.air_control``: the closing drop installs the stock
straight-air map 0x8009FA00 first. The special lock stays set, so no air attack can start and
the move still ends through its own exit.

Usage::

    python3 MKMSZR_build_rayden-specials_proof_v07.py CLEAN.z64 MKT.z64 -o MKMSZR_rayden-specials_common_proof_v07.z64
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
from mkmszr.fighter_import import fighter_build as fb

_spec = importlib.util.spec_from_file_location(
    "v01", HERE / "MKMSZR_build_generic-projectile_proof_v01.py"
)
assert _spec and _spec.loader
v01 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v01)

FIGHTER = "rayden"
ARENA_LO = f"{(fb.LINK_VA + fb.PAYLOAD_LIMIT) & 0xFFFF:04x}"


def harness(rom: bytearray) -> None:
    """The v6 harness of the specials proofs, less what the generic build already writes (the
    transfer selectors and their bound)."""

    v01.guarded(rom, 0x66F64, "2442f420", "2442" + ARENA_LO)  # arena prefix reservation
    v01.guarded(rom, 0x66FE0, "27bdffe83c02801b2442f420", "0802686100000000" + "2442" + ARENA_LO)
    v01.guarded(rom, 0x9AD84, "00" * 0x50, (
        "27bdffe83c02801b2442" + ARENA_LO + "afbf00103c04800fac82ecd00c0198e400000000"
        "2404001b3c05801b24a5f4200c01975900000000"
        "3c0880113409270fa509200e8fbf001027bd001803e0000800000000"
    ).ljust(0xA0, "0"))  # loader stub (+ max EXP)  # fmt: skip
    v01.guarded(rom, 0xA5154, "00" * 8, f"{fb.SCRATCH_ROM:08x}{fb.SCRATCH_ROM + fb.PAYLOAD_LIMIT:08x}")
    for off, old in ((0xA6FFC, "0104036b"), (0xA7000, "09470591"), (0xA7004, "11ad0d16"),
                     (0xA700C, "1ccf4e20")):  # fmt: skip
        v01.guarded(rom, off, old, "270f270f")


def build(clean: bytes, mkt: bytes) -> tuple[bytes, fb.Built]:
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, "not the clean MKMSZ USA Rev. 0 ROM"
    built = fb.build(clean, mkt, FIGHTER)
    rom = bytearray(built.rom)
    v01.proof_base(rom)
    harness(rom)
    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), built


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("clean", type=Path)
    parser.add_argument("mkt", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    rom, built = build(args.clean.read_bytes(), args.mkt.read_bytes())
    args.output.write_bytes(rom)
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    print("SELECTORS", built.selectors, "REACTIONS", built.reactions, "PAYLOAD", hex(len(built.payload)))
    print("TEST", "debug stage select, max EXP; Lightning D,F + LP; Torpedo B,B,F (stick only, also airborne; carries the victim)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
