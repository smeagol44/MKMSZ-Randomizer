# Global item materialization and solvability

> **Scope:** This page is the canonical technical owner for the **planned 1.0 global logical item model, cross-stage destination materializer, deterministic global retry contract, and whole-run solvability verifier**, including the bounded proofs and rejected materialization approaches that constrain that design.
>
> The current production shuffle remains stage-local and is documented in [Pickups and stage-local randomization](Pickups-and-Item-Randomization). Nothing on this page turns a disposable proof, proof allocation, or pipeline-disconnected planner into production behavior.

## Current conclusion

MKMSZR 1.0 requires one deterministic logical ordinary-item pool across the eight main stages, followed by a destination-stage materialization pass and a whole-run solvability check. The logical assignment and the physical representation are deliberately separate concerns.

Cross-stage feasibility is **Runtime-confirmed in bounded proofs**, including extension selectors, embedded foreign resources, external-to-embedded conversion, and five simultaneous imported visuals in Prison. The generalized pure resource planner exists but remains disconnected from the normal browser/CLI patch pipeline. Fortress composed stress validation and destination-safe key/crystal award handling remain Pending, as do the final global shuffle/solver and production integration gate.

The normative 1.0 acceptance requirements remain owned by [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap). This page owns the technical mechanism, evidence, limits, and unresolved design questions.

## Ownership boundary

| Information | Canonical owner |
|---|---|
| Current ordinary pickup behavior and stage-local shuffle | [Pickups and stage-local randomization](Pickups-and-Item-Randomization) |
| Ordinary `0x30`-byte record grammar | [Data structures and encodings](Data-Structures-and-Encodings) |
| Global logical pool, materializer, retries, solver, Map question | **This page** |
| File table, loader, selector/resource grammar | [Resource and overlay system](ROM-Overlay-and-Resource-Map) |
| Concrete per-stage pickup/resource records and stage-specific capacities | Eight pages under [Stage catalogs](Stage-Catalogs) |
| Release requirements / acceptance gates | [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) |
| Native XP tier behavior and progression persistence | [XP and progression](XP-and-Progression) |
| Literal ROM/RDRAM allocation ownership | [Memory and allocation map](Memory-and-Allocation-Map) |

A global item/resource-bundle catalog is intentionally **not** created yet. The materializer schema is still evolving; stage-relative resource truth stays in the stage catalogs until a stable normalized schema exists.

## Global logical item pool

The base global pool is formed from the **84 ordinary pickup locations** cataloged across Temple, Wind, Water, Earth, Prison, Fire, Bridge, and Fortress. A global assignment chooses a logical item identity independently of the item's original stage.

That logical identity must preserve the item's real gameplay and visual semantics. It cannot be represented by blindly copying a source stage's 28-byte movable tuple into a different stage, because that tuple includes a stage-local resource selector and award semantics that may not transfer safely.

For planning purposes, a logical ordinary item therefore needs enough information to materialize:

- award identity/semantics;
- source presentation identity and collision/extents where required;
- source resource bundle identity;
- a destination-safe callback/parameter plan;
- a destination-local selector plan;
- any imported resource bundle or deduplicated resident equivalent required by the destination.

Exactly how that logical schema is serialized is still Pending. The current stage catalogs remain the source for concrete native records and resource instances.

### Progression rewards in the global model

The 1.0 design retains **exactly nine progression rewards** in the world. In the current stage-local product these are derived as a callback overlay on generated Herbs identities rather than additional ordinary records. The global design must preserve the gameplay semantics without silently changing the 84 ordinary-location accounting.

The seed also determines how many of those nine rewards are required for completion; that target is separate from the physical count of nine rewards and is discussed below.

## Destination-stage materializer

A global logical assignment becomes a playable ROM only after every cross-stage item is converted into a destination-valid ordinary pickup identity.

The materializer must resolve, for each placed logical item:

1. a destination-safe award callback/parameter path;
2. the source item's intended collision/extents and presentation identity;
3. a resource bundle already resident in the destination or a guarded imported equivalent;
4. a destination-local selector that resolves to that resource;
5. any stage-file relocation/expansion and file-table update required by the import;
6. deduplication and capacity/accounting so repeated logical resources do not create unnecessary copies;
7. allocation and arena bounds that are valid for the production composition rather than merely for a disposable proof.

A pickup that awards the randomized item but deliberately keeps the destination item's old graphics is **Rejected for 1.0**. Correct visual identity is part of materialization, not optional polish.

### Destination-safe key/crystal awards

The ordinary key/crystal callback family is stage/parameter dependent. A source callback/parameter tuple therefore cannot be assumed safe in an arbitrary destination stage.

The early Fire foreign-key proof used a dedicated native callback at VA `0x8008EAEC` / ROM `0x0008F6EC` to award Prison Level 1 key item `0x1A` in Fire. That is useful feasibility evidence, but it is not a generic production solution.

A reusable destination-safe path for the full key/crystal set remains **Pending** and is a gate before the global materializer can enter the normal browser/CLI pipeline.

#### Key-triggered respawn relocation: static trace (2026-09-27)

The clean USA Rev. 0 ROM (SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`) separates inventory award from a stage-state write in generic pickup callback `0x80038770` (ROM `0x39370`). On `a0=0`, its stage-4 branch calls `0x80075448(s0+0x1A)` and writes `0x802C18F8=7` for `s0=0` or `8` for `s0=1` at VA `0x80038854` / ROM `0x39454` and VA `0x80038878` / ROM `0x39478`. Its stage-3 `s0=0` branch writes `0x802C18F8=2` at VA `0x800387F8` / ROM `0x393F8`. Other stage mappings award `s0+0x11` or `s0+0x20` through `0x80075448`; callback sound is `0x80064C18(0x3B,0,0x40)`. The three `0x8002830C(0x15,0x80062D60)` spawns are separate. Checkpoint-suppression v01/v02 NOPed those spawns and still relocated respawn at runtime: **Rejected / failed** as a suppression seam. Do not patch `0x80062D60` globally.

`0x802C18F8` is a broader stage segment/state selector, not a dedicated key flag. Player construction (`0x8002EC78 -> 0x8002ECF4 -> 0x8002EDFC -> 0x8003BF4C`) reads it at `0x8003BF54` (ROM `0x3CB54`) and selects a 20-byte stage spawn-table entry through the stage-ID pointer at `0x800A025C`. That function writes the chosen X/Y/Z to actor `+0x2C/+0x30/+0x34` and the paired initial coordinates to `+0x38/+0x3C/+0x40`. A second actor-construction path calls it at `0x8002EF08`; a player-only guard matters. Stage loops read the same selector for room/overlay/progression branches, and non-key scripts also write it, so suppressing the key callback stores would risk door and stage flow. The stage-4 entries selected by key indices 7 and 8 begin at `0x8009FFB4` and `0x8009FFC8` (ROM `0xA0BB4` / `0xA0BC8`); their X coordinates are `0x00788000` and `0x00848400`. Stage-3 index 2 begins at `0x8009FE88` (ROM `0xA0A88`), X `0x000C9400`.

The callback also ORs `1<<s0` into `0x802C0D54` for stages other than 1 and 3 (`0x800388C0..D4`, ROM `0x394C0..D4`). Stage/script routines around `0x80072000..0x800724CC` set more bits there after inventory or position conditions; stage-reset paths clear it. No direct read of this address was located in the scanned base executable. It is **not established as the spawn-coordinate consumer**; indirect stage/overlay use is still possible. `0x80073588` reads `0x802C18F8` only for its Fortress menu/display setup and is not the coordinate-selection function.

**Runtime negatives after the static trace:**
- **v03:** the proof substituted selector `0` only at the Prison player spawn-coordinate lookup when the live selector was `7`. The visible `CHECK POINT` event still appeared on L1-key pickup. This rejects that consumer-side override as a way to suppress the banner. The reported test did **not** include dying afterward, so it does not establish whether the respawn-coordinate substitution itself failed.
- **v04:** the proof moved Prison L1 key identity to the first easy Prison Herbs location and NOPed only the L1-specific `0x802C18F8 = 7` store at ROM `0x39454`. The visible `CHECK POINT` event still appeared. Therefore that selector write is not the banner trigger.
- Moving the L1 key identity to an easy location preserved the checkpoint behavior, confirming the unwanted event follows the **key reward identity/callback path**, not the stock map location.

**v05 runtime result:** NOPing only the generic key callback's acquired-bit commit to `0x802C0D54` at ROM `0x394D4` still leaves the visible `CHECK POINT` event. That store is therefore also rejected as a banner-suppression seam and remains progression state that should be preserved.

### Final static checkpoint reconciliation (2026-09-27)

The relevant Prison main-stage overlay is **raw file `0x9F`**, file-table entry ROM `0xA5784`, raw ROM `[0xC4C70,0xCA510)`, loaded to `0x802ECE30`. Permanent stage dispatch `0x8003B004` calls loaded overlay VA `0x802F02C0` from `0x8003B028` when native stage ID is 4. A previously noticed acquired-bit/presentation path in raw file `0xA2` is real code but is **not Prison evidence** and must not be used to explain the tested pickup.

`0x80062D60` is now statically characterized as a candidate timed presentation process: it plays sound `0x3B`, creates a presentation object, submits sprite ID `0x398` through `0x8001D520` in a 60-iteration loop, then releases the handle. `0x8001D520` is a generic sprite-node builder that allocates a `0x58` node, sets the sprite ID, and submits it through `0x8001EAE4`. **Sprite `0x398` has not been decoded/visually matched to the user's `CHECK POINT` banner**, so this remains a candidate presentation path, not a proven banner identity.

Prison file `0x9F` contains one additional direct `0x80062D60` spawn at overlay VA `0x802ED484` / ROM `0xC52C4`, immediately after selector `0x802C18F8 = 3`. Its surrounding script waits for case `s0=0xE1` and player X beyond `0x0025FA9B`; the easy first Herbs location has stock X `0x000D0600`, so this direct scripted checkpoint does not explain the relocated-key banner by simple location coincidence.

The exact v04/v05 builders resolve one uncertainty from the static report: the relocation swaps exactly the seven-word identity slice `record+0x10..+0x2B` (type, parameter, callback, extents, stage-local resource slot, and presentation descriptor) onto the easy Herbs destination. Thus runtime evidence establishes that the event follows the **complete key reward identity tuple**, not the stock L1 world position. It does **not** yet isolate callback semantics from type/resource/presentation fields.

### Self-reporting v06 runtime result

**Runtime-confirmed, bounded Prison L1 route:** the self-reporting v06 proof moved the full seven-word L1 identity to first Herbs, suppressed the three direct generic-key spawns of `0x80062D60`, and instrumented key callback/award plus known presentation/checkpoint request paths. On pickup, the native HUD showed `TRACE KA` with live state `G4 S7 B1`. The visible `CHECK POINT` banner did **not** appear. No `E`, `O`, or `C` event was logged after the key callback.

The user then died and confirmed that the checkpoint relocation **still occurred**. Thus v06 separates the two effects:

- **presentation/banner:** suppressed on this route when the three direct generic-key `0x80062D60` spawns are removed;
- **respawn/checkpoint state:** still committed through the normal stage/key state (`S7/B1`) and consumed later by player reconstruction.

This is stronger than the earlier v01/v02 interpretation and conflicts with their reported visible-banner result. Preserve that discrepancy as artifact-specific evidence rather than deleting it. Before production, confirm the banner result again in a minimal de-instrumented composition.

### v07 combined banner + respawn proof

**Partial Runtime-confirmed / not production-safe.** v07 kept the v06 banner suppression and added the bounded player-only Prison selector `7 -> 0` substitution at the spawn-coordinate consumer. After L1 pickup the trace remained `KA` with `G4 S7 B1`; after death/reconstruction it became `KAR`, proving the respawn-side override actually executed while the global selector and key-bit state remained `S7/B1`.

The Level-1 door did **not** open. Therefore preserving inventory award `0x1A`, selector `7`, and key bit `B1` is not by itself sufficient to claim preserved Prison progression under this randomized-location proof.

Two explanations remain materially plausible and must be distinguished before another production candidate:
- **Location-bound progression state (strong hypothesis):** the stock L1 record at ROM `0xCA030` / RDRAM `0x802F21F0` has collected flag `0x802F221C`. The randomizer moves the seven-word identity slice but deliberately leaves `+0x2C` collected state attached to the destination location. A Prison script/door that reads the stock record or a derivative location state would therefore still see the native L1 location as uncollected.
- **Respawn room/state mismatch (hypothesis):** if the door was tested only after death, spawning at selector-0 coordinates while the global stage selector remains `7` may reconstruct an inconsistent room/script context even though key progression variables remain set.

### Prison L1 door backward trace

**Static-confirmed limits:** the first-door predicate is still not closed, but several candidate interpretations are rejected or narrowed:

- Inventory item `0x1A` is awarded through `0x80075448`; its inventory-use dispatch entry at ROM `0xA6ED0` points to `0x80071F50`, which returns zero without an opening action. This rules out **using the inventory item** as the door-open action, while leaving an indirect possession check elsewhere possible.
- L1 writes selector `7` to `0x802C18F8`. Prison setup reads that selector, including at overlay VA `0x802EE010` / ROM `0xC5E50`, but the located reads do not establish a direct selector-7 door comparison.
- The generic key callback sets bit 0 in `0x802C0D54`. Prison reads this word at `0x802EE648` / ROM `0xC6488`, but the configured index-zero actor takes a special branch at `0x802EE690..0x802EE6A0` / ROM `0xC64D0..0xC64E0` **before** the bit test. Therefore this reader is a key-related actor-state mechanism, not proof that bit 0 directly opens the L1 door.
- Stock L1 collected flag `0x802F221C` is cleared by the Prison overlay reset loop at `0x802ED544` / ROM `0xC5384`. No direct Prison-overlay read of this exact address was found. Generic indexed pickup-manager use remains possible, but a direct door predicate is unproven.
- Prison actor routine `0x802EE320` manipulates scene actors/positions and later changes animation/geometry at `0x802EE9F0..0x802EECF0` / ROM `0xC6830..0xC6B30`. Stage trigger dispatcher `0x802F1E44` / ROM `0xC9C84` selects callbacks from scene-record flags and player position. The first L1 door's scene-record index has not yet been mapped to either path.

One static false lead is explicitly rejected: calls to `0x8001C2B4(0x1B,0x1A)` at ROM `0xC5D2C..0xC5D68` allocate geometry/collision entries; those constants are coordinates/dimensions in that helper, **not** an inventory-`0x1A` test.

**Remaining exact task:** resolve the first Prison L1 door's scene-record index in the data addressed through `0x80111FF8`, then follow that record's collision/animation callback to its final branch condition. Only after that branch is identified should another randomized-key progression proof be built.

The next justified runtime diagnostic is instrumentation, not another blind suppression patch: use a bounded in-ROM write-only ring buffer at specific candidate request sites, then poll that buffer from ordinary per-frame Lua RAM reads (Ares64 execute callbacks are not required). Compare exactly three cases through the first banner frame: relocated Prison L1 key at the easy Herbs location, untouched Herbs, and one ordinary checkpoint. Record site ID, stage, current pickup identity, `0x802C18F8`, and `0x802C0D54`; then perform one death/re-entry comparison for relocation separately.

#### Fortress defeat-trigger locations

The three Fortress ordinary records at ROM `0xC4834` (Kia), `0xC4864` (Jataaka), and `0xC4894` (Sareena) are **reward locations**. Defeating the corresponding boss is the location trigger; the stock crystal is the location's current reward. A global assignment must leave each boss-defeat trigger at its own location and materialize **whatever item is assigned there** as the spawned, correctly rendered, collectible reward. Crystal IDs `0x20..0x22` remain independently movable logical rewards and need destination-safe award handling outside Fortress. The records' parameters `0x8001/0x8000/0x8002` and callback `0x80038770` describe stock crystal awards, not immutable boss-trigger identity. The exact boss-death-to-record activation call chain has not been statically established here; preserve that trigger in a bounded Fortress proof.

## Extension-selector mechanism

Static analysis of the ordinary-pickup manager established the lookup shape:

```text
entry_ptr      = stage_resource_base + (selector << 2)
descriptor_ptr = stage_resource_base + *entry_ptr
```

On this ordinary-pickup path, no selector-count or stock outer-table-width check occurs before the selector is used as a word index. This means a relocated/expanded stage resource file can append an **extension selector table** elsewhere in the file and use:

```text
pickup +0x24 = appended_selector_entry_offset / 4
```

The appended entry can then point to an appended descriptor/resource bundle. This does not require inserting a new word into the original outer table.

This result superseded the earlier assumption that a stage with no empty stock outer-table entries necessarily had to shift/rebase the original descriptor region merely to create selector capacity. It does **not** prove that arbitrary out-of-range selectors are safe for every other resource consumer; the confirmed scope is the ordinary-pickup lookup path and the tested materialization proofs below.

### Disposable Proof D — extension selector, Runtime-confirmed

Prison's stock resource file was relocated/expanded by four bytes. An appended selector word at file offset `0x48F0` pointed to the existing Herbs descriptor `0x255C`, and all six Prison Herbs ordinary records were changed from selector `8` to selector `0x123C` (`0x48F0 / 4`).

All six Prison Herbs ordinary records used extension selector `0x123C`. Manual testing then collected **two early Herbs** successfully; those two rendered, awarded, and appeared in inventory like vanilla Herbs. This proved that the ordinary pickup path accepts an extension selector outside the stock table without a loader hook. This runtime scope is limited to those two tested pickups.

### Disposable Proof F — foreign embedded resource, Runtime-confirmed

Proof F kept all stock Prison selectors intact. Extension selector `0x123C` pointed to an appended, file-relative-pointer-rebased copy of Water's embedded Potion descriptor/records/model data. One early Prison Herbs location was changed to the imported Potion identity while the remaining Herbs records stayed stock.

Manual testing confirmed:

- the imported Potion rendered correctly;
- collecting it awarded Potion;
- an untouched Herbs pickup still rendered and awarded normally;
- both Potion and Herbs appeared correctly in inventory.

This established coexistence between stock stage resources and an appended foreign **embedded-data** bundle through an extension selector.

## External-resource IDs and external-to-embedded conversion

Stage resource records can represent image/model data in materially different ways:

- **embedded form:** record `+0x04 = 0`, with `+0x08` holding a stage-file-relative compressed-data offset;
- **external-resource-ID form:** record `+0x04` holds a cache/resource ID and `+0x08 = 0`.

A numeric external resource ID is not automatically portable across stages. An earlier external-ID-only Fire Potion transplant also produced corrupted graphics; that failure remained unresolved until the conversion work below established a self-contained embedded route.

### Disposable Proof G — external-ID-only transplant, Rejected / failed

Proof G reused the confirmed extension-selector path but imported Water's Health-urn descriptor/records into Prison while retaining external IDs `0x28F..0x292`.

The actor appeared, but its graphics were corrupted. Because the extension-selector and pickup paths were already proven, this isolated the failure to external-resource dependency handling. **Copying external IDs alone is Rejected as a cross-stage materialization strategy.**

### Static conversion work

Health urn is an important ordinary-item case because its cataloged Water, Fire, and Bridge variants all use external IDs `0x28F..0x292`; there is no known embedded donor for that family.

The four raw Health-urn image payloads behind external IDs `0x28F..0x292` were statically extracted from Water's compressed package file ID `0x73`. Their raw byte lengths are `340, 272, 272, 272`. Fire and Bridge contain matching Health-urn image payloads for the same IDs. The Water payloads were then encoded into MKMSZ native type-4 embedded image blocks. The conversion was checked in two ways:

1. Water's existing embedded Potion frames decode byte-for-byte to Fire's external Potion payloads `0x27F..0x286`, establishing equivalence between the two storage forms for a known paired item.
2. A conservative literal-only type-4 encoder round-trips all four Health-urn payloads exactly through a software model of native decoder `0x80003428`.

### Disposable Proof H — converted external family, Runtime-confirmed

Proof H kept Prison's stock selectors unchanged and made extension selector `0x123C` point to an appended Health-urn descriptor with four self-contained embedded-data records. The original external IDs were removed; each record instead referenced a generated type-4 block containing the exact Health-urn image payload.

One early Prison Herbs became the Health urn while the remaining Herbs stayed stock.

Manual testing confirmed a clean Urn of Vitality model and correct award, plus a normal untouched Herbs control. This establishes the required **external-to-embedded conversion** path for this ordinary-item family.

The scope remains bounded: one converted Health urn in Prison plus the vanilla control does not by itself prove every external ordinary-item family or every destination stage.

## Materialization deduplication and capacity

Logical selector capacity and physical storage capacity are different concerns.

A zero stock outer-table entry is only an available logical selector in that stock table; it is not evidence that free physical bytes exist in the resource file. Conversely, the extension-selector mechanism means a stage with no empty stock selectors can still gain pickup selectors by appending selector words to a relocated/expanded file.

A production planner therefore needs to track at least:

- destination stage and expanded-file bounds;
- extension-selector table location/count;
- normalized resource-bundle identity for deterministic deduplication;
- descriptor/record/data relocation and pointer rebasing;
- external-to-embedded conversion output where needed;
- file-table location/size changes;
- ROM allocation ownership;
- runtime arena/headroom implications;
- duplicate logical items that can share one imported destination bundle.

The current pure planner supports deterministic deduplicated extension-selector tables and self-contained imported visual bundles, but it remains **pipeline-disconnected**.

Stage-specific source records and capacities remain in the stage catalogs. There is intentionally no second global resource-bundle catalog yet.

## Composed five-visual stress proof

A disposable stress ROM composed five distinct imported visuals in both Prison and Fortress at once: **Potion, Urn of Vitality, Formula, Eye, and Shield**. In each destination, the first five stock Herbs records were replaced; another Herbs record remained byte-for-byte vanilla as a control.

The planner created five contiguous extension-selector entries per stage and appended self-contained descriptor/record/image bundles. Normal embedded donors and resources converted from external IDs to native type-4 embedded blocks were composed in the same expanded file.

### Prison — Runtime-confirmed

Prison's stock resource file expanded from `0x48F0` to `0x7CB4`. Five extension selectors occupied file-relative words beginning at `0x48F0`, giving selectors `0x123C..0x1240`.

Manual testing confirmed all five imported models and expected awards, plus the untouched Herbs control. This is strong bounded evidence that multiple deduplicated/imported resource families can coexist in one destination stage.

### Fortress — Pending

The same proof ROM contains the equivalent five-import Fortress construction, but that half has not been manually runtime-tested. Its static presence and planner construction must **not** be described as Runtime-confirmed.

## Early Fire foreign-key proof

Before the extension-selector work, a direct raw Prison-to-Fire identity copy produced no usable item because the source selector was not meaningful in Fire. The successful follow-up demonstrated the broader architecture by relocating Fire's resource file, populating stock logical slot 5 with a Prison Level 1 key bundle, and using a dedicated award callback for item `0x1A`.

The proof file expanded from `0x2530` to `0x2BE8` and was relocated to ROM `0x00F00000..0x00F02BE7`. Appended file-relative resource records occupied `0x2558..0x25F7`. The foreign model rendered and awarded correctly while Fire's original Herbs resource remained intact.

This is **Runtime-confirmed feasibility evidence only**. Those exact ROM/callback placements are proof-era locations and do not constitute reusable production allocations; current allocation ownership belongs to [Memory and allocation map](Memory-and-Allocation-Map).

## Deterministic global shuffle

The legacy Lua prototype already had the high-level shape of a global shuffle:

1. flatten locations across all eight stages;
2. flatten the logical item multiset;
3. place nine progression rewards into the run model;
4. shuffle globally;
5. assign back to locations;
6. simulate reachable checks to a fixed point;
7. accept only a layout that satisfies the completion predicate.

That shape is useful, but the Lua implementation is **not** authoritative for 1.0. Its access rules are stale relative to current catalogs/research, it intentionally substituted some native item semantics, and its final beatability predicate was narrow.

The global implementation should retain MKMSZR's current deterministic SHA-256 namespace model rather than Lua `math.random`.

## Deterministic retry attempts

The legacy Lua also had a retry/reseeding flaw: after rejecting an unwinnable candidate, later candidates were not guaranteed to regenerate identically from the same displayed seed.

The 1.0 contract makes retry state explicit and derives each candidate from the **original displayed/user seed** plus the attempt index and counter:

```text
candidate = H(namespace || original_user_seed || attempt_index || counter)
```

The solver tests attempt 0, then 1, then 2, and so on. Under the same MKMSZR version and rules, the accepted attempt number and accepted logical layout must be pure functions of the original user seed.

The attempt index must be isolated from unrelated deterministic namespaces, including:

- boot phrases;
- palettes;
- HUD flavor text;
- progression-reward selection details;
- required-Power-Upgrades target generation.

The interim stage-local implementation's 1,000-attempt ceiling is **not** automatically the global 1.0 retry limit. No final global retry ceiling is currently established.

## Whole-run solvability verifier

A global candidate must be validated before physical materialization becomes the final emitted run.

The intended algorithmic shape is a fixed-point reachability simulation:

1. start with the run's initial logical state;
2. enumerate every currently reachable check under the current progression graph;
3. collect the logical rewards at those checks into simulated state;
4. update newly satisfied access predicates;
5. repeat until no new check becomes reachable;
6. evaluate the final completion predicate.

The **current stage-local** access model is useful input, but it is not a complete whole-run graph. The native global verifier must use the finalized current stage/location requirements rather than the legacy Lua tables.

### Progression graph ownership

This page owns the global graph/solver semantics, but concrete stage facts stay with their stage catalogs. The graph should reference stage/location identifiers and current requirement tokens rather than duplicate the eight raw record tables.

The final graph still needs to resolve any access rules that are incomplete or only inherited from legacy logic. Until that work is complete, a fixed-point algorithm by itself is not evidence that emitted global seeds are valid.

### Completion predicate

The final 1.0 completion predicate is still **Pending**. At minimum it must include the seed-specific required-Power-Ups target described below and all finalized progression conditions needed to complete the run.

The legacy Lua predicate required its chosen Power-Upgrades count plus the three Fortress crystals. That is historical design evidence only; it must not be copied as the authoritative native predicate without reconciling the current stage graph and completion route.

## Required Power Upgrades

1.0 retains the concept of exactly **nine progression rewards existing in the world**, while each seed independently determines how many of those nine are required for completion.

The required count must:

- be generated deterministically from its own RNG namespace;
- be independent of how many global layout candidates were rejected;
- be part of the whole-run solver's completion predicate;
- be displayed by the randomizer HUD;
- preserve the current native threshold behavior for each collected progression reward.

The exact allowed minimum/maximum policy is **Pending** and must be finalized with the global solver. The current evidence does not justify inventing a range.

Native progression mechanics and current runtime evidence through XP 85/258 belong to [XP and progression](XP-and-Progression).

## Temple Map and the possible 85th check

The Temple Map is **not** one of the 84 ordinary `0x30`-byte records. It follows a scripted/special actor path and is deliberately absent from the ordinary stage catalog count.

The current sources do not settle whether the Map should become a randomized **85th check**. Two concerns must be separated:

### Trigger versus reward

The Map's logical inventory reward is coupled to Temple-specific progression behavior, including the elevator/exit path. Before the logical Map reward can be shuffled elsewhere, research must establish whether the inventory award can be separated from the Temple trigger so Temple remains completable regardless of where the logical reward is placed.

The solver must model the Temple trigger and the logical reward as separate concepts unless/until a safe unified design is proven.

### Cross-stage lifecycle

Stock behavior removes the Map on Temple -> Wind. If the Map becomes a true randomized logical inventory item, that cleanup must be suppressed or replaced by explicit randomizer lifecycle handling, and later-stage side effects must be checked.

Until these questions are resolved, the Map remains separate from the ordinary 84-location global pool and must not be silently counted as an ordinary record.

## Rejected, failed, and superseded materialization approaches

These findings remain part of the canonical design history because they prevent repeating unsafe shortcuts:

- **Blind cross-stage tuple copy — Rejected.** The source `+0x24` selector is stage-local. The early raw Prison-to-Fire copy produced no usable item before destination resource materialization was added.
- **Destination graphics with a different logical award — Rejected for 1.0.** The randomized pickup must visually represent the item it awards.
- **External-resource-ID-only transplant — Rejected / failed.** An earlier Fire Potion transplant corrupted graphics, and Proof G's Health urn also rendered corrupted in Prison even though the extension selector itself was working.
- **Treating zero selector entries as physical storage — Rejected.** Logical selector capacity says nothing about free payload bytes.
- **Assuming “no empty stock selector” blocks extension — Superseded.** Proof D established out-of-stock-range extension selectors for the ordinary-pickup lookup, so Prison/Fortress do not need an inserted stock-table word merely to gain pickup selector capacity.
- **Earlier nested-table/recursive-loader idea — Rejected.** The vanilla ordinary lookup does not recursively interpret another selector table; the successful mechanism is direct indexing of an appended selector word.
- **Literal port of the legacy Lua global solver — Rejected as an implementation plan.** Its high-level fixed-point idea is useful, but its access rules, item substitutions, narrow final predicate, and retry/reseeding behavior are not current 1.0 truth.
- **Reusing proof allocations as production allocations — Rejected.** Runtime success of a disposable cave/file placement does not establish production ownership or composition safety.

## Current integration gates

The following remain unresolved before global item materialization/solvability can become normal product behavior:

- complete the pending Fortress half of the composed five-import stress proof;
- implement and runtime-validate a generic destination-safe key/crystal award path;
- compose the materializer with production ROM allocation/file-table ownership and runtime arena bounds;
- finalize the logical materializer schema and deterministic deduplication/capacity rules across the complete item pool;
- implement the deterministic global shuffle and explicit retry sequence;
- finalize the whole-run progression graph and completion predicate;
- finalize the seed-specific required-Power-Ups range/policy;
- resolve the Temple Map 85th-check / trigger-reward / persistence policy;
- build a guarded disposable production-composition proof before enabling the new path in browser/CLI;
- perform representative full-seed runtime validation after integration.

## Related pages

- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary pickup behavior.
- [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) — normative release requirements and acceptance gates.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — canonical global file-table, loader, overlay, and resource-selector grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and proof/production allocation boundaries.
- [Data structures and encodings](Data-Structures-and-Encodings) — canonical ordinary-record grammar.
- [Stage catalogs](Stage-Catalogs) — all 84 concrete ordinary records and stage-local resource instances.
- [XP and progression](XP-and-Progression) — native progression tiers, persistence, and current runtime evidence.
- [Runtime validation status](Runtime-Validation-Status) — concise evidence-scope matrix.