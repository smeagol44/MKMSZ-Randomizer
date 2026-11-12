# Fighter recompiler — status

> **Scope:** living progress page for the fixed [Fighter recompiler plan](Fighter-Recompiler-Plan). It records the current milestone, the task list and acceptance checklist agreed when each milestone starts, debt, owner decisions and baseline identities. Update it in the same PR as the work it records. The plan itself is not edited here.

## Current milestone

**Milestone 4 — Reptile**: in progress (started 2026-11-11).

### Milestone 4 — agreed tasks (owner, 2026-11-11)

1. **Body:** a test ROM with Reptile's body (generic body builder, computed layout, auto colour) and his MKT voice set. The owner checks poses, colours, the common animations and the voices.
2. **Inputs:** combos and the remaining easy animations. Reptile's MKT special commands are wired to Sub-Zero's stock specials for now. Split into 2a (combos, combo animation, throw) and 2b (special commands; the host HP table needs room for three records, and the forceballs need their both-buttons condition).
3. **Specials:** each step changes only the actions; the commands from step 2 stay. Order and replaced power slot:

   | Order | Reptile | Replaces (Sub-Zero slot) |
   |---|---|---|
   | 1 | Acid spit | Ice Blast (1) |
   | 2 | Slide | Slide (2) |
   | 3 | Forceball (fast) | Directional Ice, up/down Ice Blast (3) |
   | 4 | Forceball (slow) | Ice Clone (5) |
   | 5 | Reverse Elbow | Ice Shatter (6) |
   | 6 | Super Slide (host power, new for Reptile) | Super Slide (7) |
   | 7 | Invisibility (Eye stealth) | Freeze on Contact (8) |
   | 8 | Polar Blast (host power, new for Reptile) | Polar Blast (9) |

   Acid spit and both forceballs count as one step (shared projectile lowering). Air Ice Blast (slot 4) is not in the list: removed, as for Sektor, its slot left blank for now (owner-confirmed 2026-11-11).
4. **Description:** Reptile's fighter description: slots as above, costs reused from the replaced Sub-Zero powers for now, removals and presentation (title, power names and help text, icons, outfit colours).
5. **Full-seed run** through the production build path, then the Sektor regression check.

### Milestone 4 — acceptance checklist

- [ ] Reptile adds no code outside his description and reusable components (review and test).
- [x] The owner accepts at runtime (bounded) the body (proof v03, 2026-11-11).
- [x] The owner accepts at runtime (bounded) the inputs and combos (inputs proofs v03 and v05, 2026-11-11).
- [ ] The owner accepts at runtime (bounded) each special, in the agreed order.
- [ ] The owner accepts a full-seed run.
- [ ] Sektor regression unchanged, or the difference explained and re-accepted; full suite passes; this page updated in each PR.

### Milestone 4 — progress

**Step 1, body.** Builders in `Experimental/FighterRecompilerProofs/` (disposable test ROMs; MKMSZ USA Rev. 0 clean ROM plus MKT N64 USA Rev. 2).

| Test ROM | SHA-256 | State |
|---|---|---|
| `MKMSZR_reptile-body_common_proof_v01.z64` | `452e6afe85fb1e8b0f3897a39d970c65f7917285c13096282fec0a9247ca6569` | **Rejected / failed** in part (owner, 2026-11-11): colours wrong; dead pose not lying flat; HP↔LP switch shows no animation; combos missing (step 2). Reproducible at commit `dc6cc5a` only. |
| `MKMSZR_reptile-body_common_proof_v02.z64` | `e5cd5d5149d1d16370fa92a10ea48c9ebea67c21c72b0c60901f5faacf62ccef` | **Runtime-confirmed (bounded)** by the owner for the lying pose (death and knockdowns) and the HP↔LP switch (both orders). **Rejected / failed** for colours ("as if the palette was mapped wrongly"; compared with MKT's character select). Pit-fall pose accepted as is. Reproducible at commit `fce72cf`. |
| `MKMSZR_reptile-body_common_proof_v03.z64` | `df6802800031d3b370354669b0173b7e749a5beafa6e5b5b23b781e1132487f2` | **Runtime-confirmed (bounded)** by the owner (2026-11-11): colours match MKT ("It's perfect now"). v02 with Reptile's own palette; differs from v02 only inside file `0x87`. **Body accepted (step 1 done).** |

v01 causes and the generic fixes in v02 (`fighter_import.body_build`; Sektor's explicit layout and palette are untouched and its pinned outputs are unchanged):

- **Colours** (Static-confirmed cause). Median cut merged across hues: black with the heavily used darkest green (the black undersuit turned green), and two greys with skin browns. MKT palettes are laid out as ramps (Reptile: 11 greys down to black, 7 greens, 13 browns). The `auto` method now keeps each ramp's colours apart: contiguous segments per ramp, 15 in all, with the least pixel-weighted error (exact arithmetic). A palette that is not laid out as ramps (3 of the 26 MKT fighters' palettes) falls back to median cut. The brown belt, flap and shin wraps are in the donor art.
- **Dead pose** (Static-confirmed cause). Host routes show only the first frame of the knockdown's second phase (`0x8005AC00`: `select_primary_phase2(0x1E)` and one `animation_advance`), and secondary 9 (lying) points at that phase. Stock Sub-Zero's phase is the single lying pose. Reptile's MKT landing is a bounce frame (`0x27C8`, legs up) and then lying (`0x27DC`). The computed layout now keeps only the landing's last frame there, so death and lying end flat. The bounce frame is dropped, and the knockdown now fits in place.
- **HP↔LP switch** (Static-confirmed cause). Stock primaries `0x0E`/`0x0F` carry host-only phases after their loop: retract, a single pose, and switch phases that go through one frame of each punch and jump into the other punch's script (`0x58C`, `0x57C`, `0x51C`, `0x50C`). MKT scripts end at the loop, so the computed layout left those phases empty. When the imported script has the stock shape up to the loop, it now keeps the stock tail (tokens, operands, jumps) and translates each stock frame to the imported frame in the same place. This gives the same roles as Sektor's hand layout.
- **Pit fall** (unchanged): the held pose is the knockdown's last fall frame (`0x27B4`), as for Sektor.
- **Palette, v03** (Static-confirmed cause). v01 and v02 read Reptile's palette from `0x800A1738[19]`. That table is not indexed by fighter id past 16: entry `17 + k` is the alternate palette of fighter `k`, so v01/v02 used another fighter's alternate (11 greys, 7 dark greens, 13 browns). The per-fighter table is `0x800A3660`. Its entry equals the palette that the fighter's first frame binds for every fighter with its own art (14 fighters, including 5 where `0x800A1738` differs). For fighters that share art (ninjas, robots) it holds the costume recolour in the shared layout. Reptile `0x800BE864`: entries 1–8 skin, 9–16 greys and black (16, the suit, is the most used), 17–31 green, which matches MKT's character select. Fighter 24 binds `0x800BB7EC`, but its entry `0x800B9AAC` has another layout (Pending; not an import target). Generic projectile proofs v01–v03 showed the same wrong palette for the forceball; v04 onwards bind the forceball's own palette and are unaffected.

**Step 2a, combos and throw.**

| Test ROM | SHA-256 | State |
|---|---|---|
| `MKMSZR_reptile-inputs_common_proof_v01.z64` | `fe87bb2af266d0cc6505c4b967f78403ddb5488ae2f323113df0c3f37b698603` | **Runtime-confirmed (bounded)** by the owner (2026-11-11): all three combos work, every hit is animated, and the finishers launch correctly with no corruption. The throw is "a bit off but acceptable". Reproducible at commit `b9d1c80`. |
| `MKMSZR_reptile-inputs_common_proof_v02.z64` | `51adc9d3c59af671062441020940541ca6d204375d84959a202a2ba5bec196a8` | Changes from v01: knockback finisher at 10 damage (owner decision, Sektor too: build v62); throw by Sektor's lead-in rule (`shift:-1`). Owner (2026-11-11): damage **Runtime-confirmed** ("very good", Reptile and Sektor); throw **Rejected / failed** ("actually worse ... earlier instead of later"). Reproducible at commit `e16c816`. |
| `MKMSZR_reptile-inputs_common_proof_v03.z64` | `a3c7e4487d9dd56d225877862f6e95c7bf6349bf7d4ce76f3030d73c9490e570` | **Runtime-confirmed (bounded)** by the owner (2026-11-11): the throw "looks much better now". v02 with the throw one place earlier than v01 (`shift:+1`); differs from v02 only inside file `0x87`. **Step 2a done.** |

v01 is the accepted body plus:

- Reptile's MKT combo strings through the generic `fighter_import.combos` ([record grammar](MKT-Adapter-Primitives#record-grammar-and-the-generic-component-2026-11-11)): `HP, HP, D+LP`, `HP, HP, HK, B+HK` and `HK, HK, B+HK`;
- his combo animation (MKT table-1 slot 0) in host primary `0x10` (`body.slot_sources`);
- his MKT throw poses in the host throw script (`body.phase_slots`; host tokens and timing kept).

Outside file `0x87`, v01 changes only the CRCs, the kick root (ROM `0xA1CE8`) and the records `0xB1CB0..0xB1D00`; v02 also changes the knockback damage byte at ROM `0xB1A3A`.

**Throw timing.** In every version the host keeps its throw script (tokens, phase ends, timing), and the donor frames are aligned with it:

- **v01** fitted the throw phase by phase: 2/6/7 MKT frames into the host's 2/5/2.
- **v02** used the rule Sektor's throw was accepted with. In proof v55 his visuals ran about one tick ahead of the grab, so the fix moved them later and started on the stance pose. For Reptile, this made the throw worse.
- **v03** uses `body.phase_slots` mode `shift:N`. Host position *p*, counted over all three phases, shows donor frame *p + N* of the grab and throw phases; the stance fills the positions before them, and the retract the ones after. v02 is `shift:-1`, Sektor's v55 corresponds to `shift:-2`, and Reptile v03 is `shift:+1`: his second reach frame, his six throw frames from the second position, then the retract's ends.

**Step 2b, special commands.**

| Test ROM | SHA-256 | State |
|---|---|---|
| `MKMSZR_reptile-inputs_common_proof_v04.z64` | `2b7de49257700fba35dddc4a56b8eb094fef9fae79b91f450085f3af0c48a30b` | Owner (2026-11-11): "everything else looking good". **Runtime-confirmed (bounded):** Acid Spit, Forceball fast, Invisibility and the kept commands. **Pending:** Forceball slow (see below). **Rejected:** the slide, which was still the generic duck-based recipe; ninjas have their own MKT slide. Reproducible at commit `469b725`. |
| `MKMSZR_reptile-inputs_common_proof_v05.z64` | `317d2099abc6e1947e8e0e4ada30ee39b00fb2b9ad67a49429607044ec5216a7` | **Runtime-confirmed (bounded)** by the owner (2026-11-11): the slide "looks fantastic", and Forceball slow outside Wind takes Ice. v04 with Reptile's MKT slide (table-1 slot 2: crouch and two slide poses) on host secondary 2 (Slide and Super Slide) through `body.secondary_slots`. **Step 2 done.** |

v04 is v03 plus Reptile's MKT commands through the generic `fighter_import.commands` (description `commands`), each calling the Sub-Zero power it replaces:

| Reptile command | Calls | Host table |
|---|---|---|
| Acid Spit, F,F + HP | Ice Blast | HP |
| Forceball fast, F,F + HP+LP | Directional Ice (down) | HP and LP, both buttons checked |
| Forceball slow, B,B + HP+LP | Ice Clone | HP and LP, both buttons checked |
| Invisibility, U,D + HK | Freeze on Contact | HK |
| Reverse Elbow, B,F + LK | nothing yet (Ice Shatter has no command record; from specials proof v15 its own special, `commands.COMMANDLESS_POWERS`) | LK emptied (v15: the elbow) |

The other powers and records:

- Directional Ice up is removed (D,F + HK).
- Spine Rip and Polar Blast keep their HP commands.
- Slide and Super Slide keep the host's own recognizers (Reptile's MKT slide is the same B + LP + BL + LK).

The HP table grows to five records, so it moves to the v6 proof arena ([allocations](Memory-and-Allocation-Map#proof-only-allocations-generic-projectile-v01v06-2026-11-11)). The arena's loader also sets maximum EXP, so every power is unlocked. Until step 4 removes Air Ice Blast, Acid Spit uses Ice Blast's stock condition, so an airborne F,F + HP still gives Air Ice Blast from tier 4.

**Forceball slow (v04: "didn't seem to work").** Statically, every input order reaches Ice Clone's stock condition `0x8004A22C`, as Forceball fast reaches Directional Ice's:

- the held check needs HP and LP at `0x800BF2EE`;
- the HP and LP tables scan on from the next record when it fails;
- the run double-taps accept forward only;
- Super Slide's check needs exactly LP+HP+Block.

That condition refuses in native stage 1 (**Wind**, `0x8009A910 == 1`), within 320 ticks of the timestamp `0x80111FD4`, with Ice below `0x60`, while airborne, or without a free 128×128 texture. Outside Wind (v05, owner) the command works and takes Ice Clone's Ice, so the v04 report was the stock Wind refusal. No clone appears with Reptile's body. The clone's own presentation with an imported body is not investigated (Pending, low value), because step 3 replaces the action.

**Step 3, specials.** Test ROMs build on inputs v05:

| Test ROM | SHA-256 | Contents | State |
|---|---|---|---|
| `MKMSZR_reptile-specials_common_proof_v01.z64` | `a0b8f788c8100b5fce48125daf399543770e486922f39b0fc3e9a354ea63f6fd` | Both forceballs as Reptile's own specials ([special actions](Fighter-Recompiler-Components#special-actions-milestone-4-step-3-2026-11-11)). Forceball fast is in Directional Ice's slot (tier gate `0x8004A4F4`, Ice `0x60`); Forceball slow is in Ice Clone's (gate `0x8004A2A8`, Ice `0x60`). His MKT throw (table-1 slot 5, phases 1–2) is in host secondary `0x25`. The projectile is backend v1 at MKT speeds (fast `0x59999`, slow `0x26666`) with the accepted strike, arc and sounds. Acid Spit is still Ice Blast. The MKT cooldown and opponent-state conditions are not lowered yet; the host's one-live-projectile rule applies instead. | **Runtime-confirmed (bounded)** by the owner (2026-11-11): commands, both facings, speeds, throw timing and position, the toward-arc, sounds, Ice cost and refusals ("looks amazing"). **Rejected / failed** in one detail: Reptile "blinks" invisible several times while firing. Reproducible at commit `d39cd75`. |
| `MKMSZR_reptile-specials_common_proof_v02.z64` | `a5536f176e1ded86b3923a9822ab3969358f7473b611d63c48a69a6fa1549faf` | v01 without the blink. Cause (Static-confirmed): in MKT's throw, the frame after token 12 belongs to the helper object token 11 creates (the ball forming in his hands, frames `0x3000`, `0x3028`, `0x3050`). The frames-only reader had taken them as body poses, so the small glow replaced Reptile for those frames. The reader now skips the frame after tokens 12 and 14. The throw is his five body poses (`2FBC 2FEC 3014 303C 3064`) and the retract. The ball-in-hand glow is not shown. | Owner (2026-11-11): blink gone (**Runtime-confirmed**, bounded); the owner wants the forming ball shown. Reproducible at commit `9c5d63f`. |
| `MKMSZR_reptile-specials_common_proof_v03.z64` | `94ebebe615cd7ce828eb39eb9dc84ef353f533e44547096c8c2f7e668f1aeb94` | v02 plus MKT's throw helper, the ball forming in his hands:<ul><li>`lower_projectile.donor_helper` reads it from the script. Token 11 creates it from `0x2FD4` with the second body pose, and each token 12 steps it (`0x3000`, `0x3028`, `0x3050`).</li><li>Its frames go into the ball's art with the flight palette, in table-1 slot `0x26`.</li><li>`emit_helper`, started with the throw, waits 3 ticks, shows one frame per body pose (12 ticks) at the ball's spawn point (MKT launches this same object), then removes itself. It has no collision.</li></ul>Payload `0xF30` bytes. | Owner (2026-11-11): shown, but **Rejected / failed** on placement and timing: it formed over his chest ("more to Reptile's front") and too late ("sooner"). Reproducible at commit `cf45a90`. |
| `MKMSZR_reptile-specials_common_proof_v04.z64` | `9f007285862837657bae6d8db47c6baf9ec711e19a92f7611c051968bc6d1677` | v03 with the helper aligned to Reptile and earlier:<ul><li>**Placement:** offset 0. MKT aligns the helper to its owner, and its frames' anchors put it in his hands. v03 used the ball's tuned spawn offset, 30 px back and 36 px up.</li><li>**Timing:** it starts with the throw, one pose before MKT's script (`place_art(helper_lead=1)`), and holds its last frame until the launch (15 ticks).</li></ul> | **Rejected / failed** (owner, 2026-11-11): still not in the right place, now low in front of his knees. After the forming ball and the flying ball were both on screen, the game **crashed** (black screen, artifacts, emulation stopped). Reproducible at commit `c5dfc7f`. |
| `MKMSZR_reptile-specials_common_proof_v05.z64` | `b080dafc3796e952bc4c4985e4c788c2b6faddbd6e2822fdf7cb513ec437f8d1` | v04 with a handover and a height fix:<ul><li>**Crash (Hypothesis, strong inference):** two type-4 projectile objects must not coexist. v04's helper outlived the launch by a few ticks; v03's ended about when the ball spawned.</li><li>**Handover:** the helper now stays until the action asks for the launch through a payload state word. It removes itself and releases its texture, and only then is the ball spawned (`emit_helper_handover`, 120-tick cap).</li><li>**Height:** the helper is at (0, the ball's dy = 36 px up). v03's (−30, −36) px was over his chest; v04's (0, 0) was low in front of his knees.</li></ul>The payload is `0x1010` bytes, in a 6 KiB arena: ROM `[0xF10000,0xF11800)`, heap floor `0x801B0C20`. | **Runtime-confirmed (bounded)** by the owner (2026-11-11): no crash. The forming ball was "still a bit too slow": at the arm-up pose MKT shows the large crescent `0x3050` and v05 a thinner, earlier frame. Reproducible at commit `077d8b1`. |
| `MKMSZR_reptile-specials_common_proof_v06.z64` | `4f7803ee2deb4fccb24a612804dd3cfd9473eaecdab943e0962bb4bb1b8d2f34` | v05 with the helper at the body's real pace. Cause (Static-confirmed): the host's animate-to-phase-end `0x80031070` sleeps `rate - 1` for an odd rate ≥ 2 (`0x80031094..0x800310AC`), so at rate 3 the throw changes pose every 2 ticks, while the helper stepped every 3. The helper now steps at `phase_end_ticks(rate)`: 2 ticks per frame, 10 ticks in all. | **Rejected / failed** (owner, 2026-11-11): the big crescent `0x3050` (the arc spanning both hands with a bright end at each, as in MKT) still never shows; at the arm-up pose the thinner `0x3028` is on screen. The owner also recalls a later MKT frame (the arc mid-way into the ball) that is missing. Reproducible at commit `538a241`. |
| `MKMSZR_reptile-specials_common_proof_v07.z64` | `9dae0e937f958bec723cf95aa11bb4caa21ae6c2d142c9127ae4abac872c18e3` | v06 with the helper two poses ahead of MKT's script (`helper_lead=2`). Its own process runs about a pose behind the body: it is scheduled after the action and needs a frame to build. The tiny 6×7 spark `0x2FD4` drops out; `0x3000` shows with the first pose, then `0x3028`, then `0x3050` until the launch. The later "arc into ball" frame is in neither the throw script (table-1 slot 5, parts 1–2) nor the flight part (`0x3078/0x308C/0x30A0`); its source is Pending (owner to compare). | **Rejected / failed** (owner, 2026-11-11, five screenshots). The target per body pose is: nothing, nothing, small arc, big arc, broken arc. v07 showed arcs from the first pose, the big arc a pose early, and no broken arc. Reading of the owner's sequence against the script: the spark `2FD4` (6×7) is "nothing", `3000` the small arc, `3028` the big arc, `3050` the broken arc. That is MKT's exact script order, one helper step per body pose. Reproducible at commit `a8ef922`. |
| `MKMSZR_reptile-specials_common_proof_v08.z64` | `77bf582d70e3ace08bf6267a20b7260560a0d42821f9988c375d32357de391ae` | The helper follows the body instead of a clock (`emit_helper(body_slot=...)`). Each tick it reads the player's cursor in the throw script (S25): after body pose *k* is shown, the cursor is `start + 4(k+1)` (`animation_advance` `0x800304C0` reads the word, then advances; Static-confirmed). It then shows that pose's helper frame: `2FD4` with pose 2, `3000` with 3, `3028` with 4, `3050` with 5. It is built when pose 2 comes up and goes at the launch handover. The helper script is one word per frame. Payload `0x1080` bytes. | **Runtime-confirmed (bounded)** by the owner (2026-11-11) for timing and frames: "almost perfect". Only the height is off, "1 or 2 pixels down". Reproducible at commit `f04ad00`. |
| `MKMSZR_reptile-specials_common_proof_v09.z64` | `b5ebb1d74a27fb715cd87334b92d12789104c9fead9663848bd4fe5496f2bf0b` | v08 with the helper 2 px higher (owner fine-tune `HELPER_DY_PX = -2` on the ball's height). | **Runtime-confirmed (bounded)**, accepted by the owner (2026-11-11). Both forceballs are done, with the forming ball. Accepted detail: the flying ball starts "2–3 pixels too close" to Reptile (spawn x offset; revisit later if wanted). |

**Step 3.2, Acid Spit.**

| Test ROM | SHA-256 | Contents | State |
|---|---|---|---|
| `MKMSZR_reptile-specials_common_proof_v10.z64` | `7a9394536b68fef282799083c59a7a04045afa229187ee29fed13b038e80b61d` | <ul><li>**Base:** the accepted forceballs.</li><li>**Slot and command:** Acid Spit (F,F + HP) in Ice Blast's slot. The tier is the ground Ice tail (1 unless the power-order shuffle rewrote it), Ice `0x20`, ground only, so Air Ice Blast is unreachable.</li><li>**Throw:** his MKT acid throw as a virtual body script, plus the mouth helper `0x315C`.</li><li>**Projectile:** palette `0x800BEC14`; two close-range checks on its first frames; flight at `0x66666`; the splash (slot 6 part 4) on the opponent, facing the attacker, with MKT's −153 px adjust. Strike box (193, 27, 64, 12), damage 15 / chip 4.</li><li>**Reaction:** stagger `acid_stagger`, push `0x40CCC`.</li><li>**Sounds:** the spit (fighter sound 8) and the sizzle (`0x10`).</li><li>**Not yet:** placement starts from the forceball's host correction (projectile (−30, −36) px, helper (0, −38) px), so calibration is expected. `create_fx(0x2F)` droplets and the reaction's per-tick victim effect are not lowered yet.</li></ul> | **Rejected / failed** (owner, 2026-11-11):<ul><li>it turned Reptile to an enemy;</li><li>the last frames looked janky;</li><li>Reptile was locked about twice too long;</li><li>most spits went through enemies (the height looked right);</li><li>the green splash was mirrored;</li><li>once (a fast monk) the splash never cleared.</li></ul>Reproducible at commit `6fde7ac`. |
| `MKMSZR_reptile-specials_common_proof_v11.z64` | `2e885824419c6aa061d793d9466892d42ea714a210cf07c8edfa066f1cd17a85` | v10 with the owner's Acid Spit report (2026-11-11) addressed, and both forceballs at once:<ul><li>**Turning:** the acid keeps Reptile's facing. The special start is the stock one (`0x80049F90`) without its `face_opponent` call (`special_begin(face=False)`). The host turned him to the nearest enemy.</li><li>**Lock time:** the recovery sleep after the launch is 15 ticks, not MKT's 31 (owner: "should be half").</li><li>**Janky frames:** the arc frames show once each, and the flight loops from `0x31B0` (`DonorPart.loop_from`). v10 replayed the whole flight part, arc included.</li><li>**Missed hits (Hypothesis):** MKT's box is only 12 units tall (y 27..39), and the host's enemy boxes differ from MKT's. The box keeps MKT's x and width and spans y 27..105, MKT's band plus the forceball's (44..105), which hits at the same projectile height. The close-range checks get the same span.</li><li>**Mirrored splash:** MKT's `flip_single` is dropped (`impact_flip=False`).</li><li>**Forceballs (owner request):** one fast and one slow may be alive together. Each ball process sets its own word while it lives and clears it before it exits. A forceball's condition refuses only while its own ball or an acid spit lives (`emit_gate_condition(alive=...)`). A set word with no live projectile process is treated as stale and cleared. Acid Spit still refuses while any projectile lives. Each ball builds its own texture slot (`0x80046F74` → `0x8001C2B4`), and the palette bind is shared and reference-counted by source (`0x8001C528`) (Static-confirmed). Two coexisting stock projectiles are Runtime-confirmed (Sektor's Double Missile, v46). The v04 crash (forming ball and ball together) is still unexplained.</li><li>**Not fixed:** the splash that once stayed on screen (fast monk). The impact loop is bounded, and no stock kill of class `0x700` processes was found (callers of `0x80028488`). Pending.</li></ul> | **Rejected / failed** for the hitbox (owner, 2026-11-12): now "too wide, it's kinda hitting everywhere". The other fixes are still to be confirmed. |
| `MKMSZR_reptile-specials_common_proof_v12a.z64` | `3d59a6af6c36a42421397dbabc7ead0002b5c5fa5927c4d2fd28f3896a088b83` | v11 with a shorter acid strike band (strike box and both close-range checks): y 21..61, 40 units, half of v11's. That is MKT's band plus 22 units below it. MKT's x and width are kept. The spit's visible flight pixels are y 25..29 in the object's frame. | **Superseded** by v13 before testing: the box analysis predicts no hits (see v13). |
| `MKMSZR_reptile-specials_common_proof_v12b.z64` | `adade81d904865ab30e620a6d5407dd5ab9dd678558be05c8e8f84179aecd5ff` | Same as v12a with y 21..45: 24 units, twice MKT's, which is MKT's band plus 6 units on each side. | **Rejected / failed** (owner, 2026-11-12): "not hitting at all". |
| `MKMSZR_reptile-specials_common_proof_v13.z64` | `b506bdf0da9d2de06150af37339187bde18dad9500cb6e6136abae6aadc488d9` | v11 with the acid box placed on the drawn spit (`lower_projectile.centre_on_art`):<ul><li>**Box placement (Static-confirmed):** the host collision core puts box y at the projectile actor's y − `0xD8` world units, 1.8 world units per box unit, growing downward (victim scan `0x8002CE24..0x8002D0E0`).</li><li>**Where the spit is drawn:** the host draws the spit's flight rows (anchor y −25, rows 0–4) at box y 92..97 (2 world units per pixel).</li><li>**Why the earlier boxes failed:** MKT's box (27..39), v12a's (21..61) and v12b's (21..45) never reach those rows. v11's 27..105 reached them only by being 78 units tall. This matches all four owner reports.</li><li>**Fix (Hypothesis until tested):** the strike box and both close-range checks move down 61 units. The strike box is now y 88..100, keeping MKT's height (12), x and width. The checks are y 84..94.</li><li>**Forceball:** its accepted box (44..105) already overlaps its drawn rows (78..111) and is unchanged.</li></ul> | **Runtime-confirmed (bounded)** for the hitbox (owner, 2026-11-12): "feels better". The splash showed "way lower" than the hit (fixed in v14). |
| `MKMSZR_reptile-specials_common_proof_v14.z64` | `1a8e7409f445ccd4ce0ac32c4ed5d7012b0a612da81b3d1e71e592a3fb9def4a` | v13 with the acid splash at the height of the hit.<ul><li>**Cause:** in MKT the spit and splash objects share the fighters' ground y, and the splash's first frame is drawn at the spit's height (rows −23 vs −25 px). The host spit is raised 36 px (its offset), but the splash took the opponent's y, so it was drawn about 36 px below the hit.</li><li>**Fix:** the splash takes the opponent's x and keeps the spit's own y (`Lowered.impact_keep_y`).</li></ul> | **Runtime-confirmed (bounded)**, accepted by the owner (2026-11-12): "looks good". It includes v11's fixes (no turning, 15-tick recovery, arc frames once, splash not mirrored) and v13's box. Still open:<ul><li>whether one fast and one slow forceball together were tried (the v04 crash scenario);</li><li>the lower-floor hit, not compared with a stock projectile yet;</li><li>the splash that once stayed on screen;</li><li>the droplets (`create_fx(0x2F)`) and the reaction's per-tick victim effect, not lowered yet.</li></ul> |

**Step 3.3, Reverse Elbow.**

| Test ROM | SHA-256 | Contents | State |
|---|---|---|---|
| `MKMSZR_reptile-specials_common_proof_v15.z64` | `04bef2c418dadb36b5a9b4d82795655e5ca33fe994077f30883f83badcad6c01` | v14 plus Reverse Elbow (B,F + LK) as Reptile's own special.<ul><li>**Slot and cost:** Ice Shatter's slot. Ice Shatter has no command record, so the move brings its own (`commands.COMMANDLESS_POWERS`). Its tier is Ice Shatter's contextual gate `0x800509A0` (6 unless the power-order shuffle moved it). No Ice cost.</li><li>**Timing:** MKT's game logic runs at 60 ticks a second, the host at 30, so donor tick counts are halved (`emit_action(donor_ticks=2)`). Sleeps, windows, repeat counts and animation rates are halved, and per-tick frame advances happen twice per host tick.</li><li>**Dash:** his Run animation (the host Run script). Speed `0xA6666` becomes `0xDDDDD`. An 8-tick contact window (MKT 16). No turning at the start (the owner's Acid Spit preference).</li><li>**First contact:** MKT strike `0x15`, box (43, 9, 34, 110), no damage. The victim is held (`elbow_hold`): the host hit pose, still for 10 ticks (MKT 20). The reaction is the stock hit reaction `0x80054B20` without its voices and flinch, through reaction byte `0x4C`.</li><li>**Return hit:** the dash carries on 7 ticks (MKT 14), stop, 3 ticks, turn to the opponent, then his MKT elbow (table-1 slot 11, body script key `0x41`) with speed again. A 10-tick window for MKT strike `0x16`, box (68, 11, 39, 60), damage 13 / chip 3, with the host uppercut launch (reaction `0x08`). Then stop, 10 ticks, the rest of the elbow.</li><li>**Blocked:** stop, Run pose 4, a 4-unit shake 4 times. **Missed:** stop and return control.</li><li>**Not lowered:** MKT's `sans_repell_3` (pass through the opponent). The host's fighter-separation code is not located, so this proof shows whether the host lets him through. Also not lowered: the "opponent settled" guard.</li><li>**Payload:** the arena is now 12 KiB, `0x27A0` bytes used.</li></ul> | **Runtime-confirmed (bounded)**, "almost perfect" (owner, 2026-11-12), except:<ul><li>he did not pass through the enemy;</li><li>the hold looked like a hit;</li><li>the launcher should be the roundhouse kick's, not the uppercut's.</li></ul>Reproducible at commit `e36d487`. |
| `MKMSZR_reptile-specials_common_proof_v16.z64` | `4d445b0a41dbfd01b24aa08032463263417fede0d3d82b8a0dc0c609e98963c5` | v15 with the report addressed:<ul><li>**Pass through (Hypothesis):** stock Freeze on Contact runs Sub-Zero through enemies (owner). It clears the player actor's `+0x8C` bit `0x1000` at the start (`0x80034740`, which also swaps to the icy palette) and sets it again at the end (`0x80034658`). Its only reader found is a call to `0x80024F74` in the render/integrator pass (`0x800188B4`), which looks like a ground lookup, so the bit's meaning is unconfirmed. Each `pass_through` tick now clears the bit and re-applies the dash speed, in case the contact stopped him; `end` sets the bit again.</li><li>**Hold:** the held enemy keeps its current frame. MKT's `r_reptile_dash` selects no animation; v15 showed the hit-flinch pose (slot `0x1C`).</li><li>**Launcher:** the stock roundhouse's reaction `0x0C` (owner). The roundhouse is player strike index `0x0D` → record `0x800AF5E4`: box (74, 0, 66, 48), damage `0x1D`, chip 4, through `0x8002E978` with animation slot `0x15` (`0x800334B4`). Reaction `0x0C` also holds Ice Shatter's contextual tier gate (`0x800529C4`).</li></ul>Ruled out as fighter separation (static): the hit seam (`0x8002DF28..0x8002DF4C`; `0x8002E104` awards XP from strike-record byte `+0x0E`, which our special strikes leave at 0), the reaction preamble `0x80053028` / `0x80053520`, the generic special start `0x80032880`, and the per-tick floor and platform check `0x80024BA8`. | **Runtime-confirmed (bounded)** (owner, 2026-11-12): "almost perfect ... looks marvelous". Pass-through, the still hold and the roundhouse launch work. Clearing actor bit `0x1000` plus re-applying the speed lets him through; which of the two is needed is not isolated. Two details remained: a blood effect while passing through, and no footsteps. Reproducible at commit `926127f`. |
| `MKMSZR_reptile-specials_common_proof_v17.z64` | `942c18809e8add0094f0cb5b500d26819da968f11c37489cfff519e904ec1bc5` | v16 with:<ul><li>**No blood:** the hold no longer calls `0x800504C4`, the stock hit reaction's first call, which starts a class-`0x15` hit-effect process at the victim's position + `0x1900`. `0x800556A4` (a single class-`0x103` process) stays.</li><li>**Footsteps:** MKT's Run plays callback 8 (`0x8000518C`, a random one of group `0x800A1A3C`: events `0x90`–`0x93`) before frames 3 and 7 of 9 (`lower_special.donor_footsteps`). The dash plays MKT events `0x90` and `0x91` alternately at those frames (`emit_action(footsteps=...)`), in isolated chains 14 and 15 (host events 459, 478; samples to ROM `0xF24E60`). The stock host Run script has no sound tokens.</li></ul> | **Runtime-confirmed (bounded)**, accepted by the owner (2026-11-12): "it worked perfectly". Reverse Elbow is done. Merged in PR #206. |

**Step 3, Slide and Super Slide:** Runtime-confirmed (bounded) by the owner (2026-11-12): "Slide and Super Slide work perfectly". Both keep the host's moves with Reptile's MKT slide animation (secondary slot 2, inputs proof v05); no further work.

**Step 3, Invisibility.**

| Test ROM | SHA-256 | Contents | State |
|---|---|---|---|
| `MKMSZR_reptile-specials_common_proof_v18.z64` | `41e4f3f3e2344520057c6449df9f8acd1d69b51ee027bd6aed67750fc57b2a5c` | v17 plus Invisibility (U,D + HK) as Reptile's own special in Freeze on Contact's slot.<ul><li>**Slot and cost:** tier gate `0x8005A9DC`, Ice `0x80`. Refused while already stealthed (player controller `+0x6BC` bit `0x1000`, `emit_gate_condition(refuse_if=...)`).</li><li>**Sequence:** his MKT animation (table-1 slot 1, one phase, body script key `0x42`) with no turning at the start. Then his fighter sound 9 (MKT event 456), placed in voice chain 7 (host event 175), which his voice set leaves unused. Then 5 ticks (MKT 10).</li><li>**Stealth:** the Eye item's effect (enemy AI ignores him, dark tint) for the Eye's 1200 ticks (owner). `0x80072584` sets it. The special clears the Inventory's timer request bit `0x802ECCC6` itself, or the next Inventory visit would start a stray timer. Its own timer process (class `0x100`) undoes the effect, as the stock timer `0x80072644` does, only if no newer stealth started: a hit ends stealth early (`0x80053594..0x800535F8`), so a recast must not be cut short by an older timer.</li><li>**Not lowered yet:** MKT's `create_fx(30)` (`0x8002DFF4` → `0x8002E050`, an animated effect object built from MKT's shared art with `0x8006DA14`).</li><li>Transfer selector 7 (entry `0x800A106C`); payload `0x2E20` of 12 KiB.</li></ul> | **Runtime-confirmed (bounded)**, "very good" (owner, 2026-11-12), with three requests:<ul><li>the "fire effect" when he goes invisible was missing;</li><li>stealth should consume Ice periodically instead of lasting a fixed time;</li><li>the forceballs and Invisibility should cost half.</li></ul> |
| `MKMSZR_reptile-specials_common_proof_v19.z64` | `89329394fb1fd0f9cae06b01a315b99d6ea6b3b96fb15fd708c346e6e8ca09fd` | v18 with the owner's requests:<ul><li>**The fire:** MKT's `create_fx(30)` (`0x8002E050`), the 9 frames of the shared animation `0x800CC77C` (codec 19, dictionary `0x800CCA88`, palette `0x800BC65C`; `effects.mkt_animation_art`), at most 100×137. It plays as a host effect process (`effects.emit_spawn` / `emit_process`, Sektor's explosion path) in front of him, at his feet, 2 host ticks a frame (MKT rate 3). The art is in the free body tail of file `0x87`. MKT offsets Reptile's flames by `0x71` from its own origin (`0x8002E108`); the host start at his feet is a first placement.</li><li>**Stealth paid over time:** no fixed time. Every 3 ticks it takes 1 Ice, and it ends when the meter cannot pay. The meter refills 1 every 5 ticks up to `0xA6` (`0x8005C3A4..0x8005C3D4`) (static estimate: a full bar after the cast would last about 25 s; see the runtime result). The process stops without undoing when a hit or a newer cast already ended the stealth.</li><li>**Costs (owner decision):** both forceballs `0x30` (half of `0x60`), Invisibility `0x40` (half of `0x80`). Step 4 (description) will carry these per-move costs.</li><li>**Payload:** the arena is now 16 KiB (`0x31E0` used), the size Sektor's line ran.</li></ul> | **Runtime-confirmed (bounded)** except two details (owner, 2026-11-12):<ul><li>the fire was drawn about a fighter's height too high (it should be at his feet);</li><li>stealth lasted about 5 s, not the estimated 25 s; the owner wants about double (half the drain).</li></ul>The 5 s means the bar emptied about four times faster than the static estimate. The meter's real refill and process sleep timing are Pending; the drain is tuned from the observation. Everything else is accepted: the halved costs, Ice-paid stealth, and the fire's look. |
| `MKMSZR_reptile-specials_common_proof_v20.z64` | `2e9ab9c6beb2fcc2e4f42af5590d0b4534b5705d297d08af3493d18699970d59` | v19 with:<ul><li>**Fire at his feet:** MKT's own offset for Reptile, `0x71` px down from the fighter's origin (`0x8002E108`), is 226 units on the host (`0x80031208`, positive is down).</li><li>**Twice the duration:** 1 Ice every 6 ticks.</li></ul> | **Runtime-confirmed (bounded)** (owner, 2026-11-12): no further Invisibility notes; "Reptile is almost fully done". Invisibility is done. |

**Polar Blast (owner, 2026-11-12):** deferred to a later stage for every fighter, Sektor included ("not sure what to do with that one"). It keeps the stock power and icon.

**Step 4, Power Ups icons.**

| Test ROM | SHA-256 | Contents | State |
|---|---|---|---|
| `MKMSZR_reptile-specials_common_proof_v21.z64` | `7e96c139341af99bfa2fef1ee0c5f5f61e9d91a3308a5243f61c0ffceba8014e` | v20 plus Reptile's Power Ups icons, from the `icons` recipe in his fighter description, built by the reusable `fighter_import.fighter_icons`.<ul><li>**Method:** MKT frames composed at MKT's fighter origin (the top of the head; body and move art share it, so the acid and the forceball land at his mouth and hands), on a green radial background. The result is box-averaged to 28×28, clipped to the stock circle, and all nine icons share one 63-colour palette.</li><li>**Acid Spit:** the spit pose and the acid arc.</li><li>**Slide:** the slide pose. **Super Slide:** the slide pose with two fading copies.</li><li>**Forceball fast:** the throw pose and the ball with two fading copies. **Forceball slow:** the throw pose and the ball.</li><li>**Reverse Elbow:** the elbow pose with two fading copies.</li><li>**Invisibility:** MKT's vanishing fire behind a darkened stance.</li><li>**Air Ice Blast:** the removed-power disc. **Polar Blast:** stock.</li><li>**Storage:** file `0x5D` is re-packed in its stock slot (ROM `0x4D9780..0x4E2BA4`).</li><li>Every layer lies at least 98% inside its crop (test).</li></ul> | **Pending** owner test |

Other stand-in poses left after the body: relocated stock scripts that nothing points to any more, and host-only states with no MKT counterpart established: the Ice projectile script P24, inherited "flipped by" labels P28–P31, and secondary slots S05–S0C and S2A. These are not "easy" animations; reachability is Pending.

**Milestones 2 and 3: done (2026-11-11).**

### Milestones 2 and 3 — agreed tasks (owner, 2026-11-10)

Milestone 3:

1. Reading aid: command record → MKT routine → annotated disassembly, with known engine calls named, constant arguments resolved and unknown calls flagged — **done** ([MKT move readings](Fighter-Recompiler-MKT-Moves); `fighter_import/reading.py`, `mipsdis.py`).
2. Registry of the MKT engine routines that Sektor's and Reptile's specials use — **done** (`fighter_import/mkt_registry.py`).
3. Annotated readings of all Reptile specials (acid spit, both forceballs, invisibility, slide, elbow dash) — **done** for the move bodies; Pending: the readers of the invisibility flag and of the slide stamp.

Milestone 2:

4. Component catalogue page: meaning, parameters, neutral units, ending and MKMSZ lowering — **draft done** ([components](Fighter-Recompiler-Components); `fighter_import/components.py`), awaiting owner review (task 7).
5. **Done (static):** RE check of the reuse ideas, both host-side: MKMSZ Quan Chi's forceball and the Eye item's effect for invisibility. Quan Chi's forceball is a **code/gameplay reference** for projectile creation, hit triggers, the launch effect and sound; the assets still come from MKT (owner, 2026-11-10). Findings on [components](Fighter-Recompiler-Components#host-references): Quan Chi's projectile uses the native enemy-projectile build and collision path, which a type-4 (player) projectile can use after one guarded table edit; the Eye is a timed stealth-from-AI state with a dark tint.
6. Move-program format and validator; Reptile's and Sektor's moves written as data; gaps listed — **done** (`src/mkmszr/fighters/moves/*.json`, 12 gaps listed).
7. Owner review of the catalogue.
8. Backend v1, starting with the generic projectile (no Ice Blast patching) — **proof line done**: [generic projectile lowering](Fighter-Recompiler-Components#generic-projectile-lowering), Runtime-confirmed bounded in proof v06 (Sub-Zero throws Reptile's MKT forceball; owner: "really good"). Backend v1: `fighter_import/lower_projectile.py` builds it from the move program; proof v07 (backend, from `reptile.json`) is byte-identical to v06.

### Milestones 2 and 3 — acceptance checklist

- [x] Every special of Sektor and Reptile is read, with unknown calls flagged and nothing guessed (`tests/test_fighter_reading.py`: no unknown calls, ROM-backed).
- [x] The registry covers every routine those moves call.
- [x] Provenance convention agreed (owner, 2026-11-11; enforced by the program validator).
- [x] Component catalogue reviewed by the owner (2026-11-11; answers under Owner decisions).
- [x] Every Reptile special and every Sektor move expressible as a move program; gaps listed (`tests/test_fighter_components.py`). New components follow the owner review.
- [x] Each implemented component has a lowering test (`projectile`: `tests/test_lower_projectile.py`).
- [x] Generic projectile built without Ice-root patches (backend `lower_projectile`; v07 = v06 byte for byte, Runtime-confirmed bounded).
- [x] Sektor's pinned outputs unchanged (`tests/test_fighter_swap.py`, ROM-backed); full suite passes; this page updated in the same PR.

**Milestone 1 — Fighter description and generic body builder: done (2026-11-10).**

### Milestone 1 — agreed tasks (owner, 2026-11-10)

1. Inventory every Sektor-specific item and classify it — **done**: [Fighter recompiler inventory](Fighter-Recompiler-Inventory).
2. Fighter description format (body part), JSON with a validator; descriptions for Sektor and Reptile — **done** (`fighter_import/description.py`, `src/mkmszr/fighters/*.json`).
3. Generic body builder: split `sektor_build.py` into a generic builder plus Sektor's description, leaving the frozen move code untouched; only frames used by mapped animations and declared extras are imported — **done** (`fighter_import/body_build.py`; Sektor's accepted layout is data in `sektor.json` `body.layout`).
4. Codec 23 and a roster-wide decode test — **done** (also codec 16, even-height storage and multi-part records; [findings](MKT-Fighter-Asset-Translation#roster-body-frame-survey-and-palettes-2026-11-10)).
5. Size report and Reptile's body built statically, with the colour method `auto` — **done** (computed layout; Reptile fits with `0x13E88` bytes free for moves).

### Milestone 1 — acceptance checklist

- [x] The inventory classifies every item; nothing is "unknown".
- [x] The validator accepts Sektor's and Reptile's descriptions and rejects broken ones (`tests/test_fighter_description.py`).
- [x] The generic builder plus Sektor's description reproduces the pinned Sektor build byte for byte (`ad2ceb4b…ed86`; `tests/test_fighter_swap.py`).
- [x] A test checks that no Sektor-only constant from the inventory remains in the generic builder (`tests/test_fighter_body_build.py`).
- [x] The roster-wide decode test passes, or its documented exceptions are listed (Sonya slot `0x15` object descriptors; ids 26–30 are not fighters).
- [x] Reptile's body builds; the size report says whether he fits (yes: stock-size file, `0x13E88` bytes free; no trimming needed).
- [x] Full suite passes, Sektor's pinned outputs are unchanged, and this page is updated in the same PR.

PRs: 1 inventory and description format; 2 generic builder; 3 codec 23, roster decode, Reptile body and size report.

## Baseline (2026-11-10)

| Item | Identity |
|---|---|
| Sektor build (`fighter_import.sektor_build`, v61, fixed loader `0xA01B30F0`) | SHA-256 `ad2ceb4bfe80b4316338207baf49684d54c0ee7c570534692266c9751a88ed86` |
| CLI `--fighter sektor --seed SEKTOR-PROD-1 --debug-all-keys` | SHA-256 `7fe0ed360472359e28a81447d16b8c57762037e8fb877b71c57db06bd5601bda` |
| Pinned by | `tests/test_fighter_swap.py` (ROM-backed) |

## Milestones

| Milestone | Status | Agreed tasks / checklist | Evidence / PR |
|---|---|---|---|
| 1 Fighter description and generic body builder | **Done** (2026-11-10) | See above | #197 inventory and format; #198 generic builder; PR 3 roster decode, computed layout, auto colour, Reptile body |
| 2 Component library and MKMSZ backend v1 | **Done** (2026-11-11) | See above | #201 components, programs, host references; #202 review, projectile proofs v01–v07, backend `lower_projectile` |
| 3 Reading aid for MKT moves | **Done** (2026-11-11) | See above | #200 reading aid, registry, readings |
| 4 Reptile | In progress | See above | — |
| 5 Generic product integration | Not started | — | — |
| 6 Review and next fighters | Not started | — | — |

## Debt

Fighter- or move-specific code outside fighter descriptions and components (plan rule 3). At plan start: everything Sektor-specific in `fighter_import/` (including `sektor_build.py` and `actions/robo_*`, frozen legacy under rule 4) and `patches/fighter_swap.py`; milestone 1 itemises it.

## Open items carried forward

- The readers of Reptile's MKT invisibility flag (object `+0x24` bit `0x20`) and of the slide stamp are not traced (milestone 3 leftovers; not needed while invisibility lowers to the Eye).
- Backend v1 lowers only `projectile`; the other components lower with milestone 4. Production placement of move code and art (fighter file, fixed loader) is milestone 5; the proofs use proof-only allocations.
- MKT timing: frames and sound cadence convert one host tick per MKT tick (projectile proofs); the rocket speed conversion is to be revisited (owner: slightly off, not twice).

- Reptile's body (computed layout, auto colour) is Runtime-confirmed (bounded, body proof v03). The owner did not comment on the voices separately, and slide was not tested (no powers unlocked); both are rechecked with the specials.
- Codec-16 frames in some fighters' body slots: palette semantics Pending (not needed for Reptile).

## Owner decisions

- 2026-11-10: next fighter is **Reptile**. Owner's expectation for his specials (to verify in milestones 2–4):
  - acid spit is a normal projectile (data on the generic projectile);
  - forceballs work like MKMSZ Quan Chi's, possibly with the same visual effects and sprites;
  - invisibility copies the Eye item's effect;
  - slide is Sub-Zero's;
  - the elbow dash is the only fully new move.
- 2026-11-10: automatic recognition of MKT machine code is deferred to milestone 6; Sektor's move modules are frozen legacy.
- 2026-11-11 (projectile proofs): Reptile's forceball launches its victim toward him (v03 over v02); MKT frames and sound cadence convert at one host tick per MKT tick; the rocket speed conversion stays for now (owner: slightly off, not twice) and is to be revisited later.
- 2026-11-11 (catalogue review): the component list is accepted and grows as needed; Reptile's invisibility uses the Eye's stealth for now (a mana-draining version is a later idea); Quan Chi's projectile confirmed as the reference move; the generic-projectile direction is still being discussed.
- 2026-11-11: provenance convention accepted: every move-program value names its source (`MKT 0x…`, `host`, `owner`).
- 2026-11-10: MKMSZ Quan Chi's forceball is a code/gameplay reference (projectile creation, hit triggers, launch effect, sound) so the host side is not reinvented; Reptile's forceball art and sounds still come from MKT.
