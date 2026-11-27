"""Rayden specials proof v27 (Fighter recompiler plan, milestone 6): Lightning and Torpedo. Disposable.

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

v08 (owner, 2026-11-25: "Let's switch to MKT's version"): the torpedo follows MKT where the
move-program generator found the accepted program differed. The start sound is one of his sounds
10-12 at random (``randu(3) + 9``; sound steps gained ``random: k``, lowered through the host's
per-thousand gate 0x80016008). The speed is restored after the take-off phase, so he moves
during the lean. After the carry, and at once on a blocked hit, Rayden bounces back off the
wall (0x8004558C: his slot 0x1A from frame 1, do_jump(0x33333, -0x6CCCC, 0x5199): away from the
opponent, as the host jump's positive x; new body script 0x42). The victim is no longer thrown:
as MKT's 0x8005391C it drops where the carry left it into root 0x1E and gets up (the release
knockback with no push and no lift). The owner's other adjustments stay: no turning, the 40-tick
flight, air control (now also on the bounce), the grab point, no Ice cost.

v09 (owner, 2026-11-25: "Let's go as pure MKT as we can at first"; the auto-turn stays removed,
being MKT's engine rather than the move): the torpedo's owner calibrations are dropped (the
40-tick flight, air control, the grab point: the carried victim keeps its contact distance and
its own height, as MKT's shared velocity does, still without gravity until released). MKT's
screen shake is added (the new ``shake_screen`` step: MKT's algorithm on the host's vertical
camera offset 0x8009A928, which the host's own shakes use), and the bounce animates: ``jump``
gained ``rate`` (the stock jump steps the animation each air tick) and the flip script ends in
MKT's loop (``secondary_scripts`` ``:loop``). Lightning: ``donor_ticks: 2`` (MKT's 60 Hz timing
on the 30 Hz host: the 36-tick recovery took 1.2 s instead of MKT's 0.6 s, owner "stuck for too
long"; projectile frame rates now follow donor_ticks too: the impact burst played at half
speed, owner "too slow"), and no turn at the start (MKT's begin_special mode 1).

v10 (owner on v09, 2026-11-25: "Everything else, it's good"): the lightning's impact burst came
"from the other way" (video): MKT's flip_single places it, but the host then draws it mirrored.
New projectile tuning ``impact_mirror``: the facing is flipped back after the placement, so the
position stays MKT's (``impact_flip`` off, Acid Spit's setting, would also move it). The torpedo
gets air control again (``air_control``, owner: "re-add air control").

v11 (owner on v10, 2026-11-25, screenshot: the burst on a pillar far from the enemy hit): the
impact was placed on the projectile's opponent (+0x640, the player's at launch), which can be
another enemy. New projectile tuning ``impact_at_hit``: the burst goes to the enemy the bolt hit,
whose x and y the collision core writes to 0x802E83D8 / 0x802C1BA0 for a projectile attacker
(actor tag 0x700, 0x8002DCB0). Reptile's Acid Spit has the same placement and is left as it is
(owner: current projectiles stay until several fighters can be tested together).

v12 (owner on v11, screenshot, Wind: "still not fixed"): on a walkway the offset 0x80031208 moves
an actor with a path (+0xDC) along it from its path position (+0xE0) and derives x from that, so
copying the enemy's x and y left the burst at the bolt's path position, then offset. The burst
now takes the enemy's whole position (path, path position, x, y, z: as the teleport copies it),
from the player's +0x640, which the collision core sets to the victim right after recording
the hit position (0x8002DD18).

v13 (owner on v12, save state "badeffectspriteplacement": "still not fixed"): the state shows the
burst actor at exactly the hit position minus MKT's 115 px, so the placement was right; v10's
``impact_mirror`` was the cause. It flipped the actor's facing after placement, which mirrors
the image around its anchor, and the burst frames' anchors lie outside their boxes, so the
visible burst moved by about the offset (v09, the owner's video, was well placed but faced the
wrong way). ``impact_mirror`` now mirrors the impact frames within their own boxes in the art
(rows reversed, anchors kept) and the runtime flip is gone: v09's position, facing the other way.

v14 (owner on v13, screenshots: "as if I was hitting them from behind"): the burst frames' bright
core (the star) is off-centre, so mirroring within the box moved it to the far side of the
enemy. ``impact_mirror`` now mirrors each frame around its densest column (rows reversed, the
anchor moved by w - 1 - 2 * core): v09's star on the enemy, the streak and arcs facing the other
way (preview shown to the owner).

v15 (owner on v14, four screenshots: the first frames "too low and too far past the enemy, and
then it suddenly moves back ... but still too low"): two causes. Mirroring each frame around its
own core gave each frame a different axis, so the frames jumped against each other (the thin
first streak frame most). The whole impact animation is now mirrored around one axis, its
frames' common core (``lower_projectile.mirror_axis``). And the burst took the enemy's height,
his feet on the host, while the bolt flies raised by its spawn offset: ``impact_keep_y`` keeps
the bolt's own height, as MKT's object does (Acid Spit's setting since its proof v13).

v16 (owner on v15, 2026-11-26: "The animation is now good"):

* **the hit reaction**: MKT's reaction 0x80 (0x800539A8; MKT reaction table 0x800A8AE0) pushes the
  victim back at 0x26666 and plays its slot 0x20 twice with its per-fighter shock palette
  (0x800A38B0[fighter]): a stagger with a cyan blink, not the host roundhouse launch the
  lightning used as a stand-in ("throwing the enemy back and into the ground"). New reaction
  ``shock_stagger``: Acid Spit's lifted host stumble (the same push; it plays the victim's root
  0x20) started behind a blink helper process that alternates the victim's colour (actor
  +0xFC/+0xFE/+0x100) between cyan (0x20, 0xFF, 0xFF) and normal every 2 ticks, 8 times, and
  stops touching the victim if its controller holds another actor;
* **the somersault turn**: the host mirrors a sprite around its anchor, also on a mid-air turn,
  and Rayden's somersault frames (slot 0x1A/0x1B) sit 15-26 px in front of their anchors (mean
  21; Reptile 2, stock Sub-Zero about 4), so a turn threw him ~40 px. The body builder now moves
  a somersault slot's anchors by its frames' mean offset when it exceeds 8 px (preview shown).

v17 (owner on v16, 2026-11-26, video: "the bolt 'jitters' if it flies too far. The 'blink'
isn't working. I think the 'hit effect' should ... 'follow' the enemy as ... [it] is being
pushed back"):

* **the bolt jump**: not distance. In all three throws of the video the bolt leaps ~115 px ahead
  for two ticks at the same point of its loop, then returns. Donor frame 0x2024 ends the flight
  loop and opens the burst; the art builder keyed drawn frames by donor frame, so the burst's
  copy (mirrored by ``impact_mirror``, burst palette) replaced the flight's. Each part now has
  its own drawn frames (``place_art``). Only this move shares a frame among the built
  projectiles (Reptile's three share none);
* **the blink**: the host draw (0x80018A8C) tints an actor through its per-vertex colours
  (+0xA0..+0xAB: red, green, blue, four corners each) and reads +0xFC only as alpha (under
  +0x8C & 0x6000), so v16's writes did nothing. While actor +0x8C bit 0x1000 is set the draw
  recomputes the colours from the stage lighting (0x80024F74) each frame; the host's own flash
  (0x80034740 / 0x80034658, the shocked player's brightening at 0x80055858) clears the bit,
  writes the colours, and sets it again. The blink now does the same: cyan with the lighting
  paused, then the bit back as it was (or the unlit 0x80 colour for an unlit actor);
* **the burst follows the victim**: MKT's burst copies the opponent's x / y velocity into itself
  every tick (0x800781F0, ``impact.follow``: "opponent"). The host burst keeps its offset from
  the victim (path position, x, y, z) every tick, until the victim's controller holds another
  actor.

v18 (owner on v17, 2026-11-26: jitter fixed, the burst follows the enemy, stagger and
somersault turn okay; two adjustments):

* **the burst** "a bit too far past the enemy ... a few pixels before": new projectile tuning
  ``impact_toward_px`` (6): MKT's adjust -115 px becomes -109 px, toward Rayden;
* **the blink** at half speed: cyan and normal two frames each (every 4 ticks, still 8 changes),
  so it lasts twice as long.

v19 (owner, 2026-11-26, after the generator's projectile rules: "Yes, add the checks"): MKT's
bolt process checks close range before the flight (0x80078230, twice: one frame, then a strike
check with record 0x10, box 101, 36, 64, 16, on each of two ticks; a hit goes straight to the
burst). The accepted program had none, so an enemy inside the spawn point could be passed
through. The lightning's projectile gains two ``checks`` (the generic close-range checks Acid
Spit already uses: one frame and two ticks each, then the record's box, centred with the strike
box on the art). Nothing else changes.

v20 (generator step 5, 2026-11-26): the **reversed lightning** (D,B + LP), the first move program
written by the generator rather than by hand (``fighters/moves/rayden.json``, read from MKT's
special 0x36 -> ``0x80077DF8(1)``; Amendment 1: Air Ice Blast's slot). MKT, as generated:
begin (action 0x31, no turn), **turn around** (flip_single), his sound 2, the throw pose, the bolt
(the lightning's art, checks with record 0x12, flight record 0x13) and, after 48 ticks, face the
opponent. Its strikes use MKT reaction **0x81**: the shock stagger pushed towards the attacker
(the bolt comes from behind). The bolt's flight callback (0x80078070) **wraps it once**: when it
leaves the screen it re-enters past the opposite edge, and 10 ticks later the flight ends it at
the next exit as usual.

Host lowering: the wrap mirrors the bolt across the camera's vertical centre plane (the
offscreen test's view transform: rotation 0x8009A930, translation 0x8009A944), so a bolt just
past one edge is just past the other at the same depth, flying the same way. Owner decisions
(2026-11-26): MKT's wrap; at the end Rayden turns back (``turn_back``) instead of facing the
opponent. The lightning's tunings apply (donor ticks, offset, art box, burst 6 px nearer).
New in the backend: the ``flip`` step (the host's turn 0x8003188C), Air Ice Blast as a power slot
with a new LP record, projectile groups keyed by art and reaction (the art placed once).

v21 (owner on v20, 2026-11-26: animation, height, direction, speed, sounds, recovery and the
final exit right, the forward lightning unaffected; "The bolt passes through enemies, it never
hits"; "The bolt reappears at the right position only with a normal-zoom camera"):

* **the hits**: the host's enemy-victim scan (0x8002CC4C) skips an enemy that is not ahead of
  the *player* actor (0x802E73DC) by the player's facing and x. Projectiles that fly forward
  never notice; the wrapped bolt comes back towards enemies Rayden (still turned around) has
  behind him. For a wrapping projectile's strike checks the pointer now holds the projectile's
  actor (a clone of the player's: the scan's other read, the type +0x78, is the same), then the
  player's again: victims are judged ahead of the bolt;
* **the zoomed-out wrap**: the host's offscreen test judges every actor at one fixed depth
  (0x802C1BB4: 832 at normal zoom, the camera translation's depth there), which a zoomed-out
  camera does not follow. The wrap now triggers when the bolt is past the visible half-width at
  its own view depth (camera rows 0 and 2, 0x8009A930; depth * 80 / focal 0x8009A8E8) plus the
  same margin, and still moving out; then the mirror as before. Normal zoom: as v20.

v22 (owner on v21, 2026-11-26: "It now hits, and the effect is correct. The zoomed out is still
not"; a matched pair of save states on Wind, normal and zoomed out): the zoom is the camera's
depth, 400 normally and 832 zoomed out (T.z and 0x802C1BB4 both follow it; v21's reasoning took
832 for normal, the earlier save states being zoomed out). The visible half-width at a depth is
depth * 160 / focal (the projection 0x802C1148: m00 = focal / 160), but the host's offscreen
test compares with half that, depth * 80 / focal, plus 200: 40 units past the edge at depth
400, 133 units inside it at 832. The wrap now triggers 40 units past the real edge,
depth * 160 / focal: as v20/v21 at normal zoom, off screen when zoomed out. (The one-frame
"flip" the owner saw is the turn back after MKT's 48-tick hold, as decided; it stays.)

v23 (owner on v22: "It works now, let's move on to the teleport"): the **teleport** (D,U on the
stick), generated from MKT (record 0x800AB968 -> propell 0x1D -> 0x80045624), in Directional Ice
Up's slot (Amendment 1), free (a movement ability). As generated: begin (action 0x21F, no turn),
the cooldown stamp, his sound 6; an **afterimage**: a copy of Rayden left where he stood, playing
his silhouette (table-1 slot 1, rate 2; MKT 0x8006DA14 + process 0x80045854); **relocate** 67 px
behind the enemy (MKT: in front when the enemy is near an arena edge); face him (owner: the
teleport faces); his sound 7 and his reappear (slot 0x22, rate 2); stance; 8 ticks; end.

Host lowering (new, generic):

* ``afterimage``: an effect-class process (0x15, not a projectile, so other specials stay free)
  builds an actor from Rayden's (as a projectile's) with the art placed from his donor frames,
  shows it for its frames x rate, then removes it;
* ``relocate``: Sektor's runtime-confirmed teleport reposition as a subroutine: past the nearest
  enemy in range by 67 px (less by a wall), on its floor, snapped to the nearest probed floor,
  the near side when the far one has no floor (MKT's arena edges become the room there), a
  cornered enemy nudged out, then facing it. The condition refuses with no enemy in range (as
  Sektor's teleport), so it never teleports to nobody;
* the **cooldown**: MKT's condition ``ticks_since(0x8012C668) < 0x40`` refuses: the stamp keeps
  a word set for 0x40 donor ticks (32 host ticks) and the condition reads it (moves without a
  projectile; projectiles keep the host one-projectile rule);
* **D,U**: the stick table also runs on the Up event (its player callback was an empty stub),
  and a stick record ending in Up takes the Up/Down mask.

MKT also binds his cyan palette while he reappears; the host keeps his palette (noted).

v24 (owner on v23, 2026-11-26: "The teleport works as expected, but the animation and sounds are
not good"; screenshot):

* **one sound**: v23 played MKT's sound 6 at the start and 7 at the reappear; the owner wants
  only the getup's. ``specials.teleport.skip: ["sound"]`` (owner adjustment);
* **the reappear animation** is his getup, as after a tumble (owner), with its own sound 7
  (``body.script_sounds``): MKT plays slot 0x22 (the sweep getup, which jumps into 0x21) and
  v23's one-phase copy of it showed one frame. The backend can now play a body slot directly:
  host primary *k* holds MKT table-0 index *k* (the generic body rule), so (0, 0x22) and the
  stance (0, 0) select the body's own scripts (``("primary", k)`` animations);
* **the afterimage too low**: it took the projectile's vertical draw offset (+0xD8 = 0x46);
  it now takes its owner's (Rayden 0x6C);
* **the afterimage colours**: his silhouette frames name their own palette (0x800B9AF0, white
  to light cyan) and were drawn with his body palette (dark inside, cyan edges); the copy now
  takes the palette its first frame names.

v25 (owner, 2026-11-26: "It's working as expected now. Let's continue with the shocker"): the
Shocker (MKT 0x800AB9F4: High Punch held 0x38 donor ticks, then released; special 0x1D ->
0x80073228) in Ice Shatter's slot, the last of his five specials:

* **release commands**: the record goes into a release table run by the High Punch release
  event (record 0x800A0A6C, no stock player callback); the HP press callback (record
  0x800A049C, stock 0x8003C870) is wrapped: it zeroes a hold count, starts a counter process
  (class 0x100) that adds 1 each tick while HP is held, then runs the stock HP table. The
  Shocker's condition (MKT ``ticks_since`` of the press stamp, ``held_for`` 56 donor ticks)
  refuses below 28 host ticks; the stock gate checks follow;
* **the move** (hand-written program; the generator has no grab rule yet): begin (action
  0x122), sound 12, a one-tick strike up close (box 0,0,61,120; damage 32, Hypothesis) that on
  a hit plays sound 5 and his shocking pose (table 1 slot 2, three frames, secondary 0x43),
  advancing a frame every 3 donor ticks for 32 steps; a miss plays the pose briefly;
* **the victim** (new reaction ``shock_hold``, spare reaction byte 0x4E = blocked entry 0x0E,
  an unused stock endless sleep): it morphs, stops, shows root 0x20's first frame, is held at
  its height with a 4 px jiggle every 3 donor ticks for 96 donor ticks while a blink process
  flashes it cyan 16 times (MKT's palette on/off 8 times), then the lifted knockdown
  (``torpedo_carry_release``), as MKT's 0x80058728 drop.

Gaps (owner to judge): MKT's sound 5 has two tracks and is not ported yet (silent); the victim
stays where the strike found it, MKT pulls it to Rayden's hands.

v26 (owner on v25, 2026-11-26, screenshots: "Shocker is not working when done next to the
enemy, but it works if the enemy jumps"; "the animation is cut if I don't hit in the first
frame"):

* **the box was behind him**: the host's strike test takes a box's first value as its front
  edge and its width back from there (0x8002BD58: facing right, x - w .. x, scaled 0.9), as
  the accepted boxes read (elbow 43/34: 9..43 in front). v25's (0, 0, 61, 120) covered 0..55
  px behind Rayden, so only a jumping enemy passing over him was caught. Now (55, 0, 55, 120):
  0..55 px in front, MKT's grab range |dx| < 0x37 (the host box meets the victim's body, MKT
  compares anchors: Hypothesis, owner to judge the reach);
* **the miss**: MKT's 0x800734F8 shows table-1 slot 2 and steps it 15 frames at 3 ticks
  (0x8000E0C0(3, 0xF)), then its first frame, then exits: he shakes his hands forward about
  45 ticks whether or not he grabs. v25 played three frames. MKT checks the grab once, at the
  start; the shaking has no hit check (MKT fact, kept).

v27 (owner, 2026-11-26, v26 accepted; the gaps: "Let's try the other sound", "make the enemy
go to Rayden's hands", "fix the blocking problem ... make grabs like this cost 2x the normal ice
blast cost"):

* **sound 5** (MKT event 0x205, two tracks: patch 0x1A7 three notes, 0x1A8 one note after a
  delay): each track in its own chain, its header patch and every in-stream patch change
  (WESS opcode 07, little-endian) set to the chain's patch; both tracks after the samples, and
  the first chain's event definition (2 tracks, 0x6C bytes, offset from the track base) points
  at them. The sequence loader reads every event from ROM by that offset into a pool sized
  from the lengths at boot (0x800880EC, 0x80088B10; Static-confirmed). The chains come from
  the teleport's skipped sounds 6 and 7, which no longer take chains, and the getup sound 7,
  now shared with the moves;
* **the victim at his hands**: MKT 0x800733F8 gives it his position (match_ani_points), turns
  it to face him and moves it by its table entry (0x800AAF8C; common entry dx -44, dy -13, then
  dy - 8): 44 px in front of him and 21 px up. The host victim turns to face him and is held
  there each tick (with the 4 px jiggle), and drops from there;
* **unblockable**: the strike record's +0xC flags get bit 0x0002, which the block test
  0x80034888 reads as "cannot be blocked" (0x80034940; no stock record sets it);
* **grab cost**: a move program marked ``grab`` costs twice Ice Blast's Ice (0x40; owner rule).

Usage::

    python3 MKMSZR_build_rayden-specials_proof_v27.py CLEAN.z64 MKT.z64 -o MKMSZR_rayden-specials_common_proof_v27.z64
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
    print("TEST", "debug stage select, max EXP; Lightning D,F + LP; reversed Lightning D,B + LP; Teleport D,U (stick, an enemy in range); Torpedo B,B,F; Shocker: hold HP about a second, release up close (also on a blocking enemy)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
