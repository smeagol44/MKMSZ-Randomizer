# MKT compatibility overview

> **Scope:** This page owns the accepted **MKT -> MKMSZ porting strategy and current compatibility contract**. It is the architectural entry point, not a proof diary.
>
> Donor semantic translation belongs to [MKT adapter primitives](MKT-Adapter-Primitives). Fighter image/codec/palette/storage translation belongs to [MKT fighter asset translation](MKT-Fighter-Asset-Translation). The MKMSZ host action ABI belongs to [Player actions and special moves](Player-Actions-and-Special-Moves). Sektor slot mapping/current coverage belongs to [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping), while the canonical vNN chronology belongs to [Sektor takeover proof history](Sektor-Takeover-Proof-History).

## Current conclusion

The accepted direction is a **faithful source-level port through an MKMSZ compatibility adapter**.

The goal is not to imitate an MKT move with vaguely similar MKMSZ parts, and it is not to relocate MKT retail instructions directly. Preserve donor control flow and donor data wherever practical, then translate only the engine-facing interfaces that are not binary-compatible.

That means preserving, where established:

- donor phase ordering and loop counts;
- donor movement intent/constants;
- donor animation scripts and frame resources;
- donor strike geometry, damage, block behavior, and reaction meaning;
- donor no-repel behavior;
- donor hit/block/timeout/recovery branches;
- donor combo graph structure where the record grammar is proven compatible.

Translate:

- MKT PROCESS/OBJECT field accesses to MKMSZ controller/actor layouts;
- MKT scheduler/action entry and exit to the proven MKMSZ action lifecycle;
- MKT helper calls to semantically equivalent MKMSZ helpers;
- donor strike/reaction selectors to MKMSZ-native semantics;
- donor animation callbacks/control tokens when they are engine-local;
- donor fighter image formats/palettes/storage into target-consumable MKMSZ assets.

Direct relocation of donor retail instructions remains rejected as the general strategy. The games differ in process/object layouts, globals, scheduler ABI, strike/reaction tables, heap/resource bases, callback semantics, and texture codecs; a safe binary rewrite would require the same semantic knowledge as a source-level adapter while being more fragile.

## Evidence boundary

The primary N64 donor/target pair is:

| Role | Image | Identity |
|---|---|---|
| Donor | MKT USA Rev. 2 N64 | `0xC00000` bytes; SHA-256 `30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb` |
| Target | MKMSZ USA Rev. 0 N64 | SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6` |

The public MKT source tree is a symbolic guide. Exact donor addresses/tables are retail-binary findings unless a page explicitly labels them otherwise.

Supplemental PS1 MKT and preserved Midway source assets are donor/reference evidence only. Their addresses, storage formats, and runtime behavior do not transfer to MKMSZ N64 without demonstrated translation.

Runtime-confirmed proofs establish only their documented routes. They demonstrate compatibility patterns; they do not imply arbitrary MKT moves or fighter data are already portable.

## What transfers conceptually

Current evidence supports these **conceptual** transfers:

| Donor concept | Current compatibility conclusion | Canonical detail |
|---|---|---|
| Action phase ordering, bounded sleeps, movement/contact/recovery phases | Transfer as semantic control flow | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Movement intent: move, stop, face opponent | Target-native primitives exist; donor constants still need target calibration | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Animation selection and frame progression | Target-native primitives exist | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Fighter frame/shape structure | Conceptually compatible after pointer-base and dimension translation | [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| Donor indexed pixels/palettes | Transfer after deterministic decode/format and palette translation | [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| Normal-combo record structure | Compatible at the tested Sektor v62 scope | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Strike geometry/damage/reaction **meaning** | Transfer semantically, not by raw numeric IDs | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Three-tick no-repel behavior | Donor semantic is Static-confirmed; target shim is Pending | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Projectile actor/process split | Target-native resource-actor creation, facing-aware placement, and child-process binding are Static-confirmed; generic adapter wrappers remain Pending | [MKT adapter primitives](MKT-Adapter-Primitives), [Player actions and special moves](Player-Actions-and-Special-Moves) |

## What requires translation

The following are **not** assumed byte- or number-compatible:

- PROCESS/OBJECT/controller/actor field offsets;
- scheduler/action entry, callback lifetime, and cleanup;
- action locks and interruption rules;
- raw movement constants until target units/facing behavior are validated;
- strike-table indices;
- victim-reaction selectors;
- animation callback/control tokens;
- donor heap-relative pointers and resource bases;
- MKT N64 codecs 16/22/24/15;
- donor palette representation/binding;
- proof allocations or file-size envelopes.

A core rule from both Reverse Elbow and Sektor combo work is:

> **Numeric equality is not semantic compatibility.**

Donor table indices and selectors must be identified by meaning and mapped to MKMSZ-native semantics. The v61 -> v62 Sektor combo correction is the clearest Runtime-confirmed example: preserving the donor combo graph while translating only the incompatible reaction selector fixed the tested corruption without recreating the move.

## Current compatibility boundaries

### Established

- **Source-level adapter direction:** accepted architecture.
- **MKMSZ action lifecycle primitives:** sufficient for a stable bounded host-side proof path; exact ABI remains in [Player actions and special moves](Player-Actions-and-Special-Moves).
- **Movement / stop / face / animation selection / animation advance:** target primitives identified.
- **Fighter asset translation:** donor descriptors/pixels/palettes can be converted into MKMSZ-native target assets for proven formats; generated Type-5 is the accepted target storage direction.
- **Normal-combo grammar:** transferable at the bounded Sektor v62 scope when game-local reaction semantics are translated.
- **Animation-script grammar and special-move command record:** Static-confirmed as one shared lineage (same tokens, terminators, return codes, coordinate scaling and `0x2C`-byte command layout). Game-local differences are confined to the callback tables, sound tokens, fighter-ID branches, helper-actor palette binding (token `0x0B`) and robot-style imperative command handlers. See [Animation script grammar translation](MKT-Adapter-Primitives#animation-script-grammar-translation) and [Special-move command translation](MKT-Adapter-Primitives#special-move-command-translation).
- **Projectile host primitives:** resource-backed secondary-actor creation, facing-aware relative placement, child projectile-process binding, and the generic projectile collision/strike path are statically identified. v69 Runtime-confirms the resolved player-animation cursor path; v70 Runtime-confirms a genuine donor rocket frame can reach the live projectile.
- **Rejected-path lessons:** forced crossover, raw selector reuse, blind callback-token reuse, unsafe callback returns, and direct donor codec consumption all remain reusable architectural constraints.

### Translation-required or incomplete

- generic donor action-phase runner;
- generic donor movement-unit conversion policy;
- generic three-tick no-repel shim in MKMSZ;
- general donor strike/reaction semantic map;
- generic donor animation-control-token translator (rules Static-confirmed; a label-relocating assembler that preserves host phase layout is not yet built);
- generic projectile actor/process wrapper and donor projectile callback/state/effect translation;
- arbitrary donor special-move command/action integration;
- production-safe allocation/composition for imported fighters or moves.

### Not implied by current proofs

Current work does **not** establish:

- binary compatibility between MKT and MKMSZ executables;
- a universal MKT PROCESS/OBJECT ABI;
- direct donor-code relocation;
- arbitrary strike/reaction selector reuse;
- arbitrary donor animation-script token reuse;
- arbitrary MKT fighter-resource import without format translation;
- production readiness of Sektor takeover or donor special moves;
- a general PS1 -> N64 binary compatibility layer.

## Architecture boundaries and canonical owners

The compatibility work is intentionally split by information type:

- [MKT adapter primitives](MKT-Adapter-Primitives) owns donor -> MKMSZ semantic translation: scheduler/yield/control transfer, movement, animation operations, strike/reaction translation, no-repel, combo semantics, cleanup, coverage, and missing generic shims.
- [MKT fighter asset translation](MKT-Fighter-Asset-Translation) owns donor fighter descriptors, dimensions/anchors, codecs, palettes, MKMSZ Type-5 generation, storage/packing, and asset compatibility limits.
- [Player actions and special moves](Player-Actions-and-Special-Moves) owns the **host-side MKMSZ action ABI**, helper meanings, scheduler bridge, callback lifetime, action lock, cleanup, and Reverse Elbow host proof history.
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) owns the slot mapping, mapping policy, current coverage, and current gaps.
- [Sektor takeover proof history](Sektor-Takeover-Proof-History) owns the vNN proof/build chronology, final evidence statuses, artifact identities, routes, supersession, and proof-specific allocation conflicts.
- [Toasty audio research](Toasty-Audio-Research) owns Toasty donor-audio identity, rejected candidates, and audio proof chronology.
- [Toasty visual research](Toasty-Visual-Research) owns Toasty visual diagnostics and image/render proof chronology.
- [Audio system](Sounds-and-Music) owns generic MKMSZ host audio mechanics.
- [Function registry](Function-Registry) owns canonical target function semantics.

## Sektor proof-history boundary

[Sektor takeover proof history](Sektor-Takeover-Proof-History) is now the canonical version chronology. This overview keeps only the accepted cross-game strategy and compatibility contract.

[Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) retains the four slot tables, mapping policy, current coverage, and current gaps. [MKT fighter asset translation](MKT-Fighter-Asset-Translation) retains stable codec/palette/Type-5/storage conclusions and bounded packing evidence, but defers exact vNN identities/routes/status reconciliation to Proof History.

## Reusable rejected/superseded lessons

The architectural lessons are preserved here without keeping a second proof diary:

- behavioral recreation was a useful early experiment but is **not** the accepted final porting direction;
- forced-X crossover is not MKT pass-through; donor behavior uses normal movement plus temporary repulsion suppression;
- MKT strike/reaction numbers are game-local table semantics;
- donor animation callbacks/control words are not automatically MKMSZ-compatible;
- returning normally from an installed MKMSZ special-action callback can self-reenter;
- projectile setup is not the player-propulsion primitive;
- omitting native action lifecycle state can destabilize the action;
- imported fighter bytes must be translated into the target asset representation rather than copied as donor codecs.
- v70's hardcoded Ice-path spawn/acceleration tuning is superseded as the implementation strategy; donor projectile choreography should run through generic target actor/process primitives instead.

Detailed Reverse Elbow failures remain on [Player actions and special moves](Player-Actions-and-Special-Moves). Detailed donor semantic consequences are on [MKT adapter primitives](MKT-Adapter-Primitives). Sektor vNN failure/supersession chronology is canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).

## Current research direction

The compatibility layer should become more generic by filling semantic gaps, **not** by hardcoding additional donor choreography.

Useful next adapter research, after current project priorities permit it, is:

- a minimal generic projectile adapter over the now-identified MKMSZ resource-actor, relative-placement, and child-process primitives, validated first with Sektor `do_robo_zap -> rocket1_proc`;
- donor projectile callback/state/effect/palette translation without inheriting Ice presentation;
- a reusable donor phase/action runner over the proven MKMSZ lifecycle;
- a narrow MKMSZ no-repel hook implementing the donor three-tick semantics;
- one exact victim-reaction translation that preserves target interruption/cleanup;
- semantic expansion of normal-combo translation beyond the currently proven selectors;
- explicit translation of donor animation control tokens when needed.

These are proof/research goals, not current 1.0 product blockers.

## Sektor production integration plan (2026-11-09)

**Static audit only (no code changed, no runtime claims).** Sektor is complete as a clean-ROM proof (v46, [proof history](Sektor-Takeover-Proof-History#heat-seeking-rocket-r3-command-fixes-and-the-double-missile-v42v46)). This section records what putting him into the randomizer needs, in the order agreed with the user: (1) where his code lives, (2) the rainbow outfit, (3) sound and ROM space, (4) R4 power mapping, (5) the product option.

**What the proof adds** (v46): payload code `0x287C` bytes; fighter file `0x87` grown from `0x459E0` to `0x4C340` (+`0x6960`); donor samples `0x84BC` bytes; 16 isolated sound-host chains; four special records, the strike pointer, reaction entry `0x23`, three throw `jal` sites, the voice table, combo records, the knee root, the Run rate and the transfer table/bound.

### 1. Code location

- **The proof cannot be composed with production as built.** It loads its code through the same file `0x1B`, bootstrap stub `0x9AD84` and RDRAM `[0x801AF420,…)` that production's Runtime V2 and file `0x1A` own ([Memory map](Memory-and-Allocation-Map)).
- **The 16 KiB pool is full.** The last production slice (Inventory legend) ends at `0x801B30E6`; `0x33A` bytes remain before the floor `0x801B3420`.
- **Data can be heap-neutral.** The repacked Sektor body leaves one contiguous `0xD1EC`-byte block unused inside file `0x87` (builder `SLACK`). Everything the proof appends after the stock end (`0x6960` bytes: teleport scripts, chest, rocket, effects, homing art) fits there, so the Sektor file can keep the stock size `0x459E0`. Static; Pending a build.
- **Code needs fixed addresses** (stock `jal` sites, record actions/conditions, reaction and transfer table entries). Candidates:

| Option | Cost / risk | Evidence needed |
|---|---|---|
| **A. Grow the reserved prefix** (production `ARENA_START_PATCHES`, only with Sektor on) by about `0x2C00` | Heap shrinks by that much in every stage. With a heap-neutral file `0x87` this stays within the margin of the Fortress-working v49 footprint (+`0x8B64` over stock), but production's generated stage resources (PR #137) also use heap | One bounded production-composition proof over every stage, Fortress and Prison included |
| **B. Top of dynamic texture storage**: lower both `0x80400000` constants (stage reset `0x8001CA38`, release `0x8001C424`) by 16 KiB | Texture headroom. One production measurement gave a bump-to-top-down gap of `0x24D88`; no worst case. The bump side `0x8001BF70` has no bound check | Worst-case texture measurement across stages |
| **C. Inside the file-`0x87` slack** (`0xD1EC − 0x6960 = 0x688C` left) | Heap-neutral, but the file sits at a heap address: the code needs load-time relocation or position independence, plus small fixed trampolines (in the `0x33A` pool tail) for every stock entry | Most implementation work; same runtime gate |
| D. Expansion Pak RAM (`0x80400000+`) | Requires 8 MiB: a product requirement change | Not proposed |

**Decision (2026-11-09): C.** The enemy planner's Water profiles leave only `0x1770` bytes of their measured budget (`0x34520`), so A would exclude two runtime-confirmed profiles and cut every stage's headroom. C is **Runtime-confirmed bounded** in Sektor proofs v47 (file `0x87` at its stock size) and v48 (payload as a relocatable blob in the file, `0x268`-byte fixed loader on the 15 file-`0x87` load sites); see [proof history](Sektor-Takeover-Proof-History#option-c-heap-neutral-file-and-relocatable-payload-v47v48). Earlier recommendation, superseded: A, gated by a production-composition measurement proof; C if the heap proves too tight. The code would be one more raw file loaded at stage init by production's bootstrap, keeping the raw-loaded-code cache contract (KSEG1 execution; cached `jal` entries only for code-only, byte-identical payloads).

### 2. Rainbow outfit (user decision 2026-11-09: remove from production for now)

**Done (2026-11-09):** removed from production; see the [status log](Status-Update-Log#ps-25-2026-11-09).

Rainbow wraps every file-`0x87` load to append its bank, which conflicts with a replaced file `0x87`. Removing it frees the `0x58`-byte loader wrapper (`[0x801B0880,0x801B08D8)`), its `0xD0` helper in the Runtime V2 code tail, the phase word `0x801AF818`, file `0x92` and ROM `[0xF20000,0xF22000)`. The Temple scripted check and the global materializer are composed after the wrapper, so the removal is its own guarded change with tests (CLI/web outfit choice, pipeline order, Wiki rows). It may be re-added later.

The other outfit modes (`SubZeroPalettePatch`, hue/RGB presets, also used by the title branding) recolour entries `0x21..0x3F` of Sub-Zero's 64-colour palette inside file `0x87`. Sektor's body uses its own 16-colour palette, so with Sektor on they must be disabled or mapped (decision, step 4).

### 3. Sound and ROM space

**Done (2026-11-09):** proof v49 Runtime-confirms the placement: file `0x87` and every donor sample load and play from the generated-output tail above 16 MiB (candidate region `[0x01820000,0x0186E4C0)`); see the [proof history](Sektor-Takeover-Proof-History#option-c-heap-neutral-file-and-relocatable-payload-v47v48).

- **ROM:** the generated-output tail `[0x01819C00,0x02000000)` is unassigned (several MiB). Sektor's file `0x87` (repointed through its file-table entry, ROM `0xA5664`/`0xA5668`; stock `[0x748920,0x78E300)`), the samples and the code file go there as new owned rows; nothing goes in clean-input space.
- **Sound hosts:** the 16 chains (`fighter_import.sound.ISOLATED_CHAINS`) share no event, patch, subpatch or waveform with production's Toasty (`52 → 68 → 608 → 533`) or Temple intro (`486 → 329 → 319`) chains. The samples move off `0xF20000` (which overlapped the rainbow bank); the bank-record rewrites stay guarded against clean bytes.
- **Donor input:** production already takes an optional validated MKT Rev. 2 ROM (CLI `--mkt-rom`, web optional donor) for Toasty and the Temple intro; the Sektor option would require it and extract its assets the same way.

### 4. R4 power mapping (needs user decisions)

**User decisions (2026-11-09).** They apply when the Sektor option is on. **Gameplay done (2026-11-10):** tiers, removals and costs are Runtime-confirmed bounded in composition proofs v05/v08; v09 lowers the Homing Missile cost to `0x40` (user decision). **Presentation done (2026-11-10, composition v10–v11):** help text, outfit colour, and Power Ups icons generated from the donor art. Composition v12–v13 also add generic slide, death and falling-to-death animations, plus the production new-power popup on pickups ([history](Sektor-Takeover-Proof-History#r4-presentation-and-common-animations-sektor-builds-v59v60-composition-proofs-v10v13)). See the [proof history](Sektor-Takeover-Proof-History#r4-gameplay-and-the-rope-companion-sektor-builds-v54v58-composition-proofs-v05v09).

| Tier slot | Sub-Zero power | Sektor |
|---:|---|---|
| 1 | Ice Blast | Straight Missile (`F,F + LP`) |
| 2 | Slide | Slide (kept) |
| 3 | Directional Ice | Teleport Uppercut (`F,F + LK`) |
| 4 | Air Ice Blast | Homing Missile (`F,D,B + HP`) |
| 5 | Ice Clone | empty |
| 6 | Ice Shatter | Double Missile (`B,B,F + LP`) |
| 7 | Super Slide | empty |
| 8 | Freeze on Contact | Super Slide (kept) |
| 9 | Polar Blast | Polar Blast (kept) |

- **Removed for Sektor:** Directional Ice (up), Air Ice Blast (including the airborne `F,F + LP` path), Ice Shatter, Ice Clone and Freeze on Contact; Spine Rip unchanged. An empty slot keeps its power-up (it still counts toward the tier and the Fortress XP requirement) but unlocks no move; the presentation shows the label "—".
- **Shuffle:** the power-order shuffler is not changed. Each Sektor move checks the tier of its slot by reading that slot's stock gate (the instruction the shuffler writes), so a shuffled run moves Sektor's mapping exactly as Sub-Zero's. Implemented as run-time reads of the gate immediates for the Double and Homing Missiles, the stock conditions for the Straight Missile and Teleport, and a build-time copy of the Freeze on Contact threshold into Super Slide's gate. Ice Shatter's "after a freezing power" constraint stays in the shuffler although Sektor has no Shatter.
- **Costs (Ice resource, user decision):** Straight Missile as Ice Blast (`0x20`); Teleport Uppercut as Slide (free; correction: the proofs never charged it, since its payload action does not touch the meter); Double Missile 1.5× Ice Blast (`0x30`); Homing Missile `0x40` (user decision 2026-11-10, after `0x60`, the Directional Ice down cost, was tried in v05–v08). The proofs before v54 charged `0x20` for all three missiles.
- **Empty slots:** labelled "—" on the power-up screen and HUD.
- **MODERN:** choosing Sektor forces SPECIALS: CLASSIC (MODERN for Sektor may come later).
- **Presentation:** Sektor's move names on the power-up screen and HUD; the outfit colour option recolours Sektor's palette (needs a Sektor-specific mapping).

Analysis that led to these choices:

- **Power order:** `power_order.py` moves each power's tier gate inside that power's own stock condition (e.g. Ice Clone at ROM `0x4AEA8`). The proofs give the Double Missile and the homing rocket Ice Blast's condition, so they would unlock with Ice Blast. Using the replaced power's condition (Ice Clone `0x8004A22C`, Freeze on Contact `0x8005A9AC`; the teleport already uses the down-Ice LK condition) lets the shuffle apply unchanged. Costs differ per condition.
- **Unmapped Sub-Zero powers:** Slide, Super Slide, Directional Ice (up), Air Ice Blast, Ice Shatter, Polar Blast and Spine Rip stay Sub-Zero's unless replaced or removed. MKT Sektor has nothing for them.
- **MODERN SPECIALS** calls the stock Ice conditions/callbacks directly and references the LP records, so it needs Sektor targets.
- **Presentation:** the Power Ups icon/help tables (ROM `0xA6BB0` / `0xA78A0`) and the HUD show Sub-Zero names.
- No solver dependency on a specific power was found: required powers are an XP count (Fortress gate) and credentials.

### 5. Product option and gates

A "Fighter: Sub-Zero / Sektor" build option (off by default, requires the donor ROM), implemented as a guarded `src/mkmszr/patches` module built from the `fighter_import` library rather than a proof builder; CI guards for every site and allocation; then the usual gates: a disposable production-composition proof, bounded manual tests, and a full-seed run with Sektor on.

**Stage 1 done (2026-11-10): production-composition proofs v01–v04, Runtime-confirmed bounded (v02, v04).**
- **What they are.** A randomizer ROM built by the real CLI, with Sektor's classified changes transplanted in. Each changed word is either Sektor or proof infrastructure; unclassified words and owner conflicts fail the build. The fixed loader goes in the pool tail `[0x801B30F0,0x801B3360)` inside file `0x1A`, and file `0x87` plus the samples go in `[0x01820000,0x0186E4C0)`. No owner conflict was found in the tested seed.
- **What changed.** Composition exposed two defects the clean-ROM proofs could not. Stock code called from the KSEG1 payload made KSEG1 return addresses that production's Toasty hook did not recognise (v01 hang; stock calls now go through KSEG0). The teleport could reappear below a floor read from a falling target (v03; now snapped onto the nearest probed floor).
- **Details.** See the [proof history](Sektor-Takeover-Proof-History#production-composition-sektor-builds-v50v53-composition-proofs-v01v04).
- **Remaining stages.**
  - R4 gating, costs and presentation per the decisions above. **Done** (composition v05–v13, Runtime-confirmed bounded).
  - The product option (CLI/web) as a `patches` module with CI guards. **Done** (stage 2 below).
  - A full-seed run with Sektor on. **Pending** (user test of the first full-seed build).

**Stage 2 done (2026-11-10): the product option. Implementation/CI-confirmed.**
- **Option.** `RandomizerConfig.fighter` (`sub-zero` default, `sektor`); CLI `--fighter sektor` (requires `--mkt-rom`); web "Swap character" window ([web patcher](Web-Patcher-and-Product#fighter-swap-swap-character-window)). An imported fighter requires SPECIALS: CLASSIC at build time (the config rejects MODERN; the web app locks the toggle off).
- **Module.** `src/mkmszr/patches/fighter_swap.py` (`FighterSwapPatch`) is the production form of the composition v13 builder. It runs last in the pipeline: it builds Sektor from the clean ROM and the donor (`fighter_import/sektor_build.py`, the v60 builder as a library function), transplants the classified words with owner-conflict guards, recomputes the R4 stock edits from the randomizer ROM, and claims the output tail and the file-`0x1A` pool tail ([memory map](Memory-and-Allocation-Map)).
- **Evidence.** `--fighter sektor --seed SEKTOR-PROD-1 --debug-all-keys` reproduces composition v13 byte for byte (SHA-256 `e1f83b25cf0e323bce151f92f36a866fca57c25fc5bb807d86cc76f39e580248`), so v13's bounded runtime result carries to that exact build config. The browser (Pyodide) build of a web-default config matches the Python build byte for byte (seed `SEKTOR-WEB-1`, SHA-256 `14f166a079ccbd5ead5d64935ec76e6796e1d718b33561439887f6f01dea6795`, about 46 s in headless Chromium). `tests/test_fighter_swap.py` pins both when the ROMs are supplied.
- **Fixed in the library.** The Sektor build set an importer code-generation default (`fighter_import.mips.DEFAULT_CACHED_CALLS`) and never reset it, so a second build in one process (tests, the web worker) diverged; `build` now restores it around each call.
- **Open.** The in-game GAME SETTINGS menu can still switch SPECIALS to MODERN on a Sektor ROM; MODERN calls the stock Ice conditions/callbacks (see above). Locking that row for an imported fighter needs a native frontend change and its own proof. **Pending** (user decision).
- **Enemy randomization (user decision, 2026-11-10):** not a Sektor gate. The option is experimental and treated as broken with or without Sektor until it is re-implemented; a Sektor test with it on is deferred to that re-implementation.

## Related pages

- [MKT adapter primitives](MKT-Adapter-Primitives)
- [MKT fighter asset translation](MKT-Fighter-Asset-Translation)
- [Player actions and special moves](Player-Actions-and-Special-Moves)
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping)
- [Sektor takeover proof history](Sektor-Takeover-Proof-History)
- [Toasty audio research](Toasty-Audio-Research)
- [Toasty visual research](Toasty-Visual-Research)
- [Audio system](Sounds-and-Music)
- [Function registry](Function-Registry)
- [N64-PS1 comparison](N64-PS1-Comparison)
