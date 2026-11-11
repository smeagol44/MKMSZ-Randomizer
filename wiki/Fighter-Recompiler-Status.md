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
| Reverse Elbow, B,F + LK | nothing yet (Ice Shatter has no command record) | LK emptied |

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
| `MKMSZR_reptile-specials_common_proof_v07.z64` | `9dae0e937f958bec723cf95aa11bb4caa21ae6c2d142c9127ae4abac872c18e3` | v06 with the helper two poses ahead of MKT's script (`helper_lead=2`). Its own process runs about a pose behind the body: it is scheduled after the action and needs a frame to build. The tiny 6×7 spark `0x2FD4` drops out; `0x3000` shows with the first pose, then `0x3028`, then `0x3050` until the launch. The later "arc into ball" frame is in neither the throw script (table-1 slot 5, parts 1–2) nor the flight part (`0x3078/0x308C/0x30A0`); its source is Pending (owner to compare). | **Pending** owner test |

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
