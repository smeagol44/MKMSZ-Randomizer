# Fighter recompiler — status

> **Scope:** living progress page for the fixed [Fighter recompiler plan](Fighter-Recompiler-Plan). It records the current milestone, the task list and acceptance checklist agreed when each milestone starts, debt, owner decisions and baseline identities. Update it in the same PR as the work it records. The plan itself is not edited here.

## Current milestone

**Milestone 4 — Reptile**: in progress (started 2026-11-11).

### Milestone 4 — agreed tasks (owner, 2026-11-11)

1. **Body:** a test ROM with Reptile's body (generic body builder, computed layout, auto colour) and his MKT voice set. The owner checks poses, colours, the common animations and the voices.
2. **Inputs:** combos and the remaining easy animations. Reptile's MKT special commands are wired to Sub-Zero's stock specials for now.
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

   Acid spit and both forceballs count as one step (shared projectile lowering). Air Ice Blast (slot 4) is not in the list: removed, as for Sektor (assumption, to confirm).
4. **Description:** Reptile's fighter description: slots as above, costs reused from the replaced Sub-Zero powers for now, removals and presentation (title, power names and help text, icons, outfit colours).
5. **Full-seed run** through the production build path, then the Sektor regression check.

### Milestone 4 — acceptance checklist

- [ ] Reptile adds no code outside his description and reusable components (review and test).
- [ ] The owner accepts at runtime (bounded) the body.
- [ ] The owner accepts at runtime (bounded) the inputs and combos.
- [ ] The owner accepts at runtime (bounded) each special, in the agreed order.
- [ ] The owner accepts a full-seed run.
- [ ] Sektor regression unchanged, or the difference explained and re-accepted; full suite passes; this page updated in each PR.

### Milestone 4 — progress

**Step 1, body.** Builders in `Experimental/FighterRecompilerProofs/` (disposable test ROMs; MKMSZ USA Rev. 0 clean ROM plus MKT N64 USA Rev. 2).

| Test ROM | SHA-256 | State |
|---|---|---|
| `MKMSZR_reptile-body_common_proof_v01.z64` | `452e6afe85fb1e8b0f3897a39d970c65f7917285c13096282fec0a9247ca6569` | **Rejected / failed** in part (owner, 2026-11-11): colours wrong; dead pose not lying flat; HP↔LP switch shows no animation; combos missing (step 2). Reproducible at commit `dc6cc5a` only. |
| `MKMSZR_reptile-body_common_proof_v02.z64` | `e5cd5d5149d1d16370fa92a10ea48c9ebea67c21c72b0c60901f5faacf62ccef` | **Runtime-confirmed (bounded)** by the owner for the lying pose (death and knockdowns) and the HP↔LP switch (both orders). **Rejected / failed** for colours ("as if the palette was mapped wrongly"; compared with MKT's character select). Pit-fall pose accepted as is. Reproducible at commit `fce72cf`. |
| `MKMSZR_reptile-body_common_proof_v03.z64` | `df6802800031d3b370354669b0173b7e749a5beafa6e5b5b23b781e1132487f2` | **Pending** owner test of the colours. v02 with Reptile's own palette; differs from v02 only inside file `0x87`. |

v01 causes and the generic fixes in v02 (`fighter_import.body_build`; Sektor's explicit layout and palette are untouched and its pinned outputs are unchanged):

- **Colours** (Static-confirmed cause). Median cut merged across hues: black with the heavily used darkest green (the black undersuit turned green), and two greys with skin browns. MKT palettes are laid out as ramps (Reptile: 11 greys down to black, 7 greens, 13 browns). The `auto` method now keeps each ramp's colours apart: contiguous segments per ramp, 15 in all, with the least pixel-weighted error (exact arithmetic). A palette that is not laid out as ramps (3 of the 26 MKT fighters' palettes) falls back to median cut. The brown belt, flap and shin wraps are in the donor art.
- **Dead pose** (Static-confirmed cause). Host routes show only the first frame of the knockdown's second phase (`0x8005AC00`: `select_primary_phase2(0x1E)` and one `animation_advance`), and secondary 9 (lying) points at that phase. Stock Sub-Zero's phase is the single lying pose. Reptile's MKT landing is a bounce frame (`0x27C8`, legs up) and then lying (`0x27DC`). The computed layout now keeps only the landing's last frame there, so death and lying end flat. The bounce frame is dropped, and the knockdown now fits in place.
- **HP↔LP switch** (Static-confirmed cause). Stock primaries `0x0E`/`0x0F` carry host-only phases after their loop: retract, a single pose, and switch phases that go through one frame of each punch and jump into the other punch's script (`0x58C`, `0x57C`, `0x51C`, `0x50C`). MKT scripts end at the loop, so the computed layout left those phases empty. When the imported script has the stock shape up to the loop, it now keeps the stock tail (tokens, operands, jumps) and translates each stock frame to the imported frame in the same place. This gives the same roles as Sektor's hand layout.
- **Pit fall** (unchanged): the held pose is the knockdown's last fall frame (`0x27B4`), as for Sektor.
- **Palette, v03** (Static-confirmed cause). v01 and v02 read Reptile's palette from `0x800A1738[19]`. That table is not indexed by fighter id past 16: entry `17 + k` is the alternate palette of fighter `k`, so v01/v02 used another fighter's alternate (11 greys, 7 dark greens, 13 browns). The per-fighter table is `0x800A3660`. Its entry equals the palette that the fighter's first frame binds for every fighter with its own art (14 fighters, including 5 where `0x800A1738` differs). For fighters that share art (ninjas, robots) it holds the costume recolour in the shared layout. Reptile `0x800BE864`: entries 1–8 skin, 9–16 greys and black (16, the suit, is the most used), 17–31 green, which matches MKT's character select. Fighter 24 binds `0x800BB7EC`, but its entry `0x800B9AAC` has another layout (Pending; not an import target). Generic projectile proofs v01–v03 showed the same wrong palette for the forceball; v04 onwards bind the forceball's own palette and are unaffected.

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

- Reptile's body (computed layout, auto colour) is static only; its runtime acceptance is part of milestone 4.
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
