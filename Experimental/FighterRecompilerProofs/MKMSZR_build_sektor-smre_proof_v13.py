"""Sektor SMRE proof v13 (SMRE step 3, Sektor's base on the generic build). Disposable.

Sektor built by the generic fighter build (``fighter_import.fighter_build.build``) from the
migration description ``fighters/sektor-smre.json``, with no special moves yet: the base the
moves are then added to one at a time (owner, 2026-11-27: "start with Sektor. Let's do 1 move
at a time"). The product Sektor (``fighters/sektor.json`` and its frozen legacy build) is not
touched. Harness: the specials proofs' (debug stage select, boot skip, max EXP, the payload
raw-loaded at 0x801AF420 from ROM 0xF10000 through file 0x1B: Rayden specials proof v31's).

What the generic build gives him, and how it differs from the accepted (legacy) Sektor:

* **body**: the computed layout (as Reptile and Rayden), his accepted 16-colour map and palette;
  the generic recipes (slide, death, long fall, pickup, grabbed) as before;
* **throw**: MKT's own throw script (table 0 slot 0x23). It draws his mechanical arm as a
  second actor (MKT token 11 creates it from frame 0x2300, tokens 12/14 step it), with its own
  palette MECARM_P (0x800BC310). New generic rule (``body_build.phase_slot_frames``): each step
  shows one flattened frame, the arm over his pose, the arm's colours mapped to his nearest body
  colours. New phase mode ``scale``: MKT's 4 windup, 4 arm-out and 8 swing frames scaled over
  the host's first 7 positions, the 8 retract frames over its last 2 (the legacy throw used
  seven hand-picked arm poses);
* **combos**: MKT's own combo graph (``HP, HP, HK, B+HK``; ``HP, HP, HK, HK, B+HK``; ``HP, HP,
  D+LP``; ``HK, HK``): seven records on the host's six, so the last option list goes into the
  payload (``combos.lower(overflow_va=...)``), as the legacy build kept his HK,HK record there;
  the legacy elbow-combo presentation (slot 0x10 hand-ordered) is now MKT table 0 slot 0x10;
* **voices**: the generic voice rule (as before);
* **specials**: none. Sub-Zero's Ice Blast, Directional Ice (up and down), Ice Clone and Freeze
  on Contact are removed (``remove_commands``); Slide, Super Slide and Polar Blast stay.

v02 (owner on v01, 2026-11-27: throw, combos and body "all looking good", but "the throw is
missing its sound"): MKT's throw table ``0x800A7ED8`` (by fighter id) gives Sektor's throw
``0x80042498``, which plays his sounds 0 (arm out), 1 (arm throw) and 2 (arm in) around the grab,
the throw and the victim's transfer; its start (``0x80042878``) plays the grab voice (voice group
3, event 0x67) for every fighter. The host voice rule leaves the throw's voice category silent.
New generic ``throw_sounds``: the throw routine's own sounds are read from MKT and played by
payload hooks on the host throw's three stages (the legacy build's sites and wrappers, proof
v41: grab voice call 0x8005BCD4, throw phase 0x8005BDC8, finish 0x8005BDF8), and
the build adds the grab voice at the grab (owner: on by default, for every fighter, when a
sound chain is free; Reptile's and Rayden's MKT throws play no sounds of their own).

v03 (owner, 2026-11-27: "If grab sounds are this problematic then let's drop them. We can get back
to them later"): MKT's grab voice is no longer played (Rayden had no sound chain for his; the
enlarged sound bank that would have given him one is parked, draft PR #220). His throw keeps its
own sounds: arm out at the grab, arm throw before the throw, arm in at the release.

v04 (owner, 2026-11-27: "Let's continue"): the first move, the **teleport uppercut** (F,F + LK, in
Directional Ice Down's slot as his legacy build; free: a movement ability), written by SMRE from
MKT (inline command 0x800AB2C0 -> do_body_propell(8) -> 0x80048368) and lowered generically:

* MKT, as generated: begin (action 0x208, facing the opponent), his sound 7, the last frame of
  table 0 slot 0x0D; **sink** (y 0x5F333, gravity 0x9599) past the screen's bottom line; behind
  the opponent by 12 px (MKT also leads by the opponent's x velocity: omitted, as the accepted
  legacy); face him; the **rise** (table 1 slot 3 at rate 5; y -0x7A666, gravity -0x5199) from
  the bottom line to the floor, its strike (MKT record +0x4C: box 73, -9, 73, 87; damage 16,
  chip 2; reaction 0x3D = the host uppercut) checked within 41 px of the floor; the **flight**
  on from that velocity (gravity 0xF000; 0xB000 once the strike was blocked: MKT's +0x3D0 holds
  the blocked flag), striking while rising (MKT's per-tick callback); the landing (slot 0x16
  from its second frame, 3 ticks a frame);
* the host has no floor clip, so the sink and the rise are descriptor-only aliases of the pose
  (image shared, anchor lowered by MKT's curve each host tick), as the accepted legacy teleport,
  a last far alias hiding him; the flight is the stock jump with a per-tick callback (controller
  +0x70C) that strikes while rising, once per move.

Differences from the accepted (legacy) teleport, owner to judge: pure MKT numbers (no 0.9 jump
scale or airtime retime), MKT's damage 16 / chip 2 (legacy 0x18 / 3, owner's 1.5x), MKT's 12 px
(legacy 40 units past him), no airborne start (the stock Directional Ice condition), MKT's
blocked-strike gravity (legacy read 0xB000 as "after a hit").

v05 (owner on v04's notes, 2026-11-27: "In MKT you can definitely start it in the air ... Can be
started from the ground, or from the air"): MKT's command and routine have no ground check (from
the air the sink goes on through the floor). The host gate of Directional Ice Down's slot and the
transfer's mode 0 refused an airborne start; the move now takes mode 1 and the gate without the
floor checks (``specials.teleport_uppercut.air_start``), and a sink that starts in the air first
falls on its own curve (MKT's velocity and gravity) to his floor, then goes on from the curve tick
it reached (the accepted legacy teleport's technique, v08).

v06 (owner on v05, 2026-11-27: "it's not doing anything. It's as if the move doesn't exist"): the Low
Kick record was garbage (window 8, no facing-right tokens). The command writer read the donor
command as a 0x2C-byte MKT record at the program's source, but an inline command's source is the
matcher's compact table (u16 window, six facing-right, six facing-left tokens), so the parser
never matched F,F. ``commands.donor_record`` now tells the two apart by the program's tokens and
window and builds the record from the compact table (window 24, F,F both ways). Nothing else
changes.

v07 (owner on v06, 2026-11-27, video: "almost good ... it looks as if Sektor touches the ground
'twice' when going down after the uppercut ... it feels 'slower'. In MKT, I can enter a standing LK
that combos after the uppercut"): the video shows the landing's second pose, a knee-up frame
that reads as airborne. MKT's teleport_land (0x80076ECC..0x80076F14) saves the animation cursor
(+0x440), skips a word, shows slot 0x16's second frame for 3 ticks, restores the cursor and shows
its *first* frame for 3 ticks. The decompiler forwards the saved value, so SMRE read the restore
as "the next frame" (the third, knee-up). SMRE now models the save and restore: frames 2, then
1. And sleeps with only instant steps between them are rounded on their running total (3 + 3
donor ticks -> 2 + 1 host ticks), so the landing takes MKT's 0.1 s, not 4 host ticks.

v08 (owner on v07, 2026-11-27: teleport uppercut accepted, "Next?"): the second move, the
**straight missile** (F,F + LP, in Ice Blast's slot as his legacy build; Ice Blast's cost), written
by SMRE from MKT (inline command 0x800AB250 -> rzap3 0x8007C068(routine, single)) and lowered
generically, nothing unknown:

* MKT, as generated: begin (action 9, stop); his sound 11 (chest open); table 1 slot 0 (RBCHEST1,
  RBCHEST2) to its phase end at 4 ticks a frame (2 while the opponent is in a reaction:
  ``rate_reacting``); the missile (rocket1_proc 0x8007C100): his sound 3 as it starts, art table 0
  slot 0x43 part 4 at rate 3, start speed 0x33333 (0x59999 while the opponent reacts), every
  donor tick v += v >> 4 up to 0xB3333 (the flight callback 0x8007C1E0), MKT's smoke (create_fx 4
  every other donor tick), the strike (box 16, -15, 35, 31; damage 20, chip 2; reaction 0x3B,
  stumble back, push 0x33333), on contact his sound 10 and the explosion (create_fx 5) at the
  missile, which ends; the recovery (32 ticks); the chest closing (MKT ani_backward(4): RBCHEST1);
* new generic backend: the projectile's launch sound, its speed tables (per host tick, two donor
  ticks each: the legacy rocket's, equal by test), the reacting start, a trail effect and an
  effect impact; MKT shared effects read from their own routines (``mkt_effects``: animation
  list, rate, in front / behind, placement entry: the smoke 19 px behind, as the legacy rocket)
  with art equal to the legacy rocket's (by test); animate ``rate_reacting`` and ``reverse``
  (``body.secondary_scripts`` ``:reverse``).

Differences from the accepted (legacy) rocket, owner to judge: the missile starts from the generic
projectile spawn (Reptile's and Rayden's -30, -36 px, chest height: MKT's (5, 38) is measured from
another origin), not the legacy +4 px correction; the chest hold is MKT's 32 donor ticks; MKT's
recovery action 0x604 is not set (the begin's is kept).

v09 (owner on v08, 2026-11-27, screenshot: "missile colors, it looks like a transparent red instead
of its grey, yellow and red"; "initial position behind and over Sektor"; "The smoke is way over
it"; "There's an initial ring of smoke in front of it"):

* **colours**: SMRE found no palette for the missile, so it took his body palette. MKT binds
  ROCKET_P (0x800BC3AC, 16 colours: grey body, red / orange / yellow exhaust) by the palette word
  of slot 0x43's first frame (the vertical rocket, heap 0x25EC), from which the object is made;
  SMRE's object palette rule now falls back to the art slot (``make_rocket`` sets no object
  selection). Reptile's and Rayden's palettes are unchanged;
* **spawn**: v08 started from the generic spawn (-30, -36 px) drawn at +0xD8 = 0x46. The stock
  projectile token (0x80030A0C..0x80030AB4, the legacy rocket's actor) copies the owner's
  position, facing, rotation and +0xD8; the legacy (5 + 4, 38) px was calibrated on that. A
  projectile placed by MKT's own offset (no ``offset_px``) is now drawn at the owner's +0xD8 and
  starts at MKT's (5, 38) px (pure MKT: without the legacy +4 px);
* **smoke**: effects are drawn at +0xD8 = 0x6C (the fighters'), 19 px apart from the missile's
  0x46; with the owner's +0xD8 they agree. Each puff now starts where the missile's own
  facing-aware offset (MKT multi_adjust_xy, the one that places it) puts 19 px behind it, the
  missile's position kept (v08 signed the offset by the facing bit for the effect's own offset,
  along a rotation the generic projectile does not have: puffs could start ahead of it).

v10 (owner on v09, 2026-11-27, screenshots: colour, position, explosion, speed, acceleration and hit
detection fine; "The first smoke ring is too 'on top' of the missile, it should be a bit behind";
"The missile itself should be drawn behind Sektor ... to give the effect of coming out of its
chest"; "I think there should be no smoke when it first appears on Sektor"):

* **depth**: MKT's make_rocket (0x8007C00C) sets the rocket object's depth (+0x1C) to 0, behind
  the fighters (the legacy build drew it behind him for the same reason). SMRE reads it
  (``behind``); the missile takes his priority (+0x5C) and the next sprite layer (+0xEC = his
  + 1, the stock idiom 0x80030D18; layers draw from high to low), so it comes out of his chest
  and each smoke puff (one layer behind the missile) is behind both;
* **first puff**: MKT's rocket_smoke toggles (+0x3D4 ^= 1, a puff when it was set), so the
  first flight tick has none; the host's first flight tick has none either.

v11 (owner on v10, 2026-11-27: depth, first ring and first-tick smoke fixed; save state
``smokepause``: "It's definitely smoke because it's only showing up when I pause ... only happens
in this stage when I'm standing to the left"): static analysis of the save state (v10's ROM, MD5
C464251868D1155074F6EB95BE31785B) shows six puffs on the missile's line (y 76, z -1, one layer
behind it); the newest (actor 0x8010DAA8) still has its render position +0x38/+0x3C/+0x40 at
0, 0, 0, which the others have equal to their position. The movement pass sets it each tick; the
pause stops that pass, so a puff inserted on the paused tick is drawn at the stage's origin, on
screen only where the camera shows the stage's left end, 38 px above the trail. The effect
process (for projectile effects) and the missile now set it as they are placed. Reptile's
invisibility fire uses the effect process as accepted (unchanged bytes).

v12 (owner on v11, 2026-11-27, screenshot: pause ring fixed; "I see the first ring too far ahead of
the missile's fire. The first smoke ring should start on the fire behind the missile"): in MKT's
art the rocket faces right with its flame on the left 20 px and the anchor on the body (26 px from
the left), so MKT's puff 19 px behind the anchor lands mid-flame. The host draws an actor at its
render position (+0x38..), the position before this tick's move; the v10 save state shows the
missile's +0x2C 44.8 units (one tick at full speed) ahead of it. v11 placed each puff from +0x2C,
so the newest showed that much too far forward, under the body. Each puff is now placed from the
missile's drawn position.

v13 (owner on v12, 2026-11-27: "It's good now. Let's quickly try the double missile"): the third move,
the **double missile** (B,B,F + LP, in Ice Clone's slot as his legacy build; Ice Clone's cost 0x60),
written by SMRE from MKT (inline command 0x800AB26C -> rzap3 mode 1), nothing unknown: the
straight missile's chest, then a missile, 10 donor ticks, a second missile, the recovery (48
donor ticks) and the chest closing. Both missiles are v12's (art, sounds, smoke, explosion shared).
First runtime test of two generic projectiles alive at once (Reptile's fast and slow forceballs
together were never tried; the v04 helper crash was attributed to two coexisting type-4 objects).

Usage::

    python3 MKMSZR_build_sektor-smre_proof_v13.py CLEAN.z64 MKT.z64 -o MKMSZR_sektor-smre_common_proof_v13.z64
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

_spec = importlib.util.spec_from_file_location("rayden_v31", HERE / "MKMSZR_build_rayden-specials_proof_v31.py")
assert _spec and _spec.loader
rayden_v31 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rayden_v31)
v01 = rayden_v31.v01

FIGHTER = "sektor"  # was "sektor-smre" (renamed when it replaced the legacy Sektor)


def build(clean: bytes, mkt: bytes) -> tuple[bytes, fb.Built]:
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, "not the clean MKMSZ USA Rev. 0 ROM"
    built = fb.build(clean, mkt, FIGHTER)
    rom = bytearray(built.rom)
    v01.proof_base(rom)
    rayden_v31.harness(rom)
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
    print("COMBOS", built.report["combos"], "THROW SOUNDS", built.report.get("throw_sounds"), "PAYLOAD", hex(len(built.payload)))
    print("TEST", "debug stage select, max EXP; straight missile F,F + LP: chest opens (faster on a reacting enemy), the missile "
          "with its launch sound, smoke behind it, speeding up; on an enemy: boom and explosion, the enemy stumbles back; "
          "blocked; past the screen edge; the chest closes; teleport uppercut F,F + LK still as v07; the missile out of his chest (behind him), smoke behind it, none on its first tick; pause while it flies (the stage's left end too): no ring on the wall; the newest ring on the flame; double missile B,B,F + LP: two missiles, both hitting, and both together on screen with no hang")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
