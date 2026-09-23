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
| File table, loader, selector/resource grammar | [ROM, overlay, and resource map](ROM-Overlay-and-Resource-Map) until Audit Task 6 refocuses it |
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

Manual testing confirmed that the tested early Herbs rendered, awarded, and appeared in inventory like vanilla Herbs. This proved that the ordinary pickup path accepts an extension selector outside the stock table without a loader hook.

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

The four raw Health-urn image payloads were extracted from Water's package and encoded into MKMSZ native type-4 embedded image blocks. The conversion was checked in two ways:

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

The proof file expanded from `0x2530` to `0x2BE8` and was relocated to ROM `0x00F00000..0x00F02BE7`. The foreign model rendered and awarded correctly while Fire's original Herbs resource remained intact.

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
- [ROM, overlay, and resource map](ROM-Overlay-and-Resource-Map) — current file/loader/resource grammar; deeper refactor is Audit Task 6.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and proof/production allocation boundaries.
- [Data structures and encodings](Data-Structures-and-Encodings) — canonical ordinary-record grammar.
- [Stage catalogs](Stage-Catalogs) — all 84 concrete ordinary records and stage-local resource instances.
- [XP and progression](XP-and-Progression) — native progression tiers, persistence, and current runtime evidence.
- [Runtime validation status](Runtime-Validation-Status) — concise evidence-scope matrix.
