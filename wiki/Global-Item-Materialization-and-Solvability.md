# Global item materialization and solvability

> **Scope:** This page is the canonical technical owner for the **planned 1.0 global logical item model, cross-stage destination materializer, deterministic global retry contract, and whole-run solvability verifier**, including the bounded proofs and rejected materialization approaches that constrain that design.
>
> The current production shuffle remains stage-local and is documented in [Pickups and stage-local randomization](Pickups-and-Item-Randomization). Nothing on this page turns a disposable proof, proof allocation, or pipeline-disconnected planner into production behavior.

## Current conclusion

MKMSZR 1.0 requires one deterministic logical ordinary-item pool across the eight main stages, followed by a destination-stage materialization pass and a whole-run solvability check. The logical assignment and the physical representation are deliberately separate concerns.

Cross-stage feasibility is **Runtime-confirmed in bounded proofs**, including extension selectors, embedded foreign resources, external-to-embedded conversion, and five simultaneous imported visuals in Prison. The generalized pure resource planner exists but remains disconnected from the normal browser/CLI patch pipeline. Fortress five-import composed stress validation is Runtime-confirmed on a bounded route, and Kia -> Potion now Runtime-confirms that a Fortress boss-defeat trigger can retain ownership of activation while the spawned reward identity/resource changes to a non-crystal item. The representative production-shaped integration route is now Runtime-confirmed in v02. Remaining work is shared browser/CLI patch-pipeline integration with guarded allocation/tests and generalized emission, including all three assassin reward records, before global assignment is enabled.

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

With Powers as pickups ON, the 1.0 design retains **exactly nine progression rewards** in the world. In the current stage-local product these are derived as a callback overlay on generated Herbs identities rather than additional ordinary records. With it OFF, these nine callbacks are not replaced. The global design must preserve both mode-specific semantics without silently changing the 84 ordinary-location accounting.

The required-power setting is separate from that physical count and is discussed below. Seed mode derives a count; Vanilla and Custom do not.

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

### Foreign-key inventory-mask round trip v01/v02 — Runtime-confirmed closure (2026-09-30)

A bounded Fire -> Wind Circle composition used the established Fire destination materialization route together with production pickup persistence and four-box stage-local key masking. v01 confirmed that the foreign Wind Circle retains true inventory ID `0x0E` in authoritative backing storage, appears as inert Glass `0x08` outside Wind after a box/stage reconstruction, appears as the real Circle in Wind, and re-masks after leaving. v01 also isolated one acquisition-time defect: immediately after pickup in Fire, LIVE still exposed real `0x0E` until the next reconstruction boundary.

Disposable v02 closed that gap by composing the existing four-box paths immediately after the ordinary pickup callback: filtered LIVE -> active backing save, then active backing -> stage-masked LIVE reconstruction. Runtime validation confirmed the foreign Circle is Glass immediately in Fire with no intervening box/stage transition, restores to the real Circle in Wind, and can be used through the native Wind interaction while remaining in inventory.

This establishes the tested masking contract across **acquisition, box reconstruction, stage transition, native-stage reveal/use, and re-masking**. The bounded v02 hook/allocation remains proof-only until integrated through current production ownership and CI/runtime composition.

Key lifecycle correction: native key items are **used, not consumed**. Ordinary key use does not remove the key from inventory. Stage-completion cleanup/removal is a separate lifecycle concern and remains Pending.

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

### Prison L1 door scene-record trace and v08 runtime closure

**Static-confirmed:** the first configured Prison door actor group uses scene-record indices **`0xFB` and `0xFC`**. They are addressed as `*(0x80111FF8)+0x4698` and `+0x46E0`; in decompressed stage file `0x44` they begin at offsets `0x46B0` and `0x46F8`. File `0x44` is compressed in ROM at `0x3BCD20..0x3D6A0F`, so these records have no direct patchable ROM offsets.

The first configured group's process `0x802EE320` reads `0x802C0D54` at `0x802EE648` / ROM `0xC6488`. For this configuration, the panel entry resolves the test at `0x802EE6A4..0x802EE6B0` / ROM `0xC64E4..0xC64F0` to **bit 0 of `0x802C0D54`**. When set, `0x802EE6B8` assigns the enabled panel animation. The later opening path still requires the ordinary player/collision/input conditions; the decisive interaction branch is `0x802EE874..0x802EE888` / ROM `0xC66B4..0xC66C8`, and the physical movement updates both scene records, collision geometry, and visible actors at `0x802EE9F0..0x802EECE4`.

The traced opening branch does **not** directly read inventory `0x1A`, selector `0x802C18F8=7`, or stock collected flag `0x802F221C`. This explains why selector 7 can be treated as checkpoint/respawn state while acquired bit 0 remains the door credential.

### v08 door-safe checkpoint suppression

**Runtime-confirmed, bounded Prison L1 route.** v08 moves the full seven-word Prison L1 identity onto the first easy Herbs location, then:

1. preserves inventory award `0x1A`;
2. preserves the generic acquired-bit commit so `0x802C0D54` bit 0 becomes set;
3. suppresses the three direct generic-key `0x80062D60` presentation spawns;
4. suppresses only the Prison L1 selector-7 store at ROM `0x39454`;
5. leaves ordinary pickup persistence and door actor logic unchanged.

Observed runtime state after pickup was `TRACE KA`, `G4 S2 B1`: the key awarded, the door credential was present, and the stage selector remained at its pre-key value rather than becoming 7. The visible `CHECK POINT` banner did not appear. The Level-1 door opened normally. After death, the player respawned at the natural stage-start/no-checkpoint spawn, which the user independently verified matches entering Prison and dying before taking any checkpoint.

This closes the Prison-L1-specific checkpoint problem with a cleaner two-seam model than v07: **suppress the key-only presentation request and the key-only checkpoint-selector write; preserve the logical door/progression bit.**

Production/global scope remains Pending. Other stage keys/crystals may use different selector writes, acquired bits, boss-spawn semantics, or door consumers; do not generalize the exact Prison L1 bytes without tracing their corresponding progression owner.


### Fire key checkpoint suppression v01 — Runtime-confirmed bounded family proof (2026-09-29)

Fire provides the first successful non-Prison generalization of the two-seam model.

The stock Fire stage-icon callback is overlay VA `0x802F0EBC` / ROM `0x000E5C0C`. All three native Fire keys call this function with parameter `0..2`. The callback separates:

- the direct `0x8002830C(0x15, 0x80062D60)` checkpoint-presentation request at ROM `0x000E5C28`;
- the normal inventory award through `0x80075448(s0 + 0x17)` at ROM `0x000E5C30`;
- the pickup-created respawn-selector store `0x802C18F8 = s0 + 2` at ROM `0x000E5C50`;
- the remaining post-award helper path, which v01 leaves stock.

Disposable v01 NOPs only the presentation JAL at `0xE5C28` and the selector store at `0xE5C50`. It leaves the award, pickup sound/helper path, ordinary manager collected-state write, Fire overlay logic, and native inventory-USE progression path unchanged.

**Runtime-confirmed, bounded v01 route:** no key-created `CHECK POINT` event was observed; after death the player returned to Fire's natural stage-start spawn; the stage remained completable through the Fire God arena and boss; and transition to the next stage completed without reported gameplay issues. This establishes that, for Fire, pickup-created checkpoint presentation and pickup-created respawn relocation can both be removed while preserving the tested stage-completion path.

v01 disposable ROM SHA-256: `438f3d7f314bba3b7336b53239aa2cdbc026c800da36a5f930de42a05a19acff`.

#### Audio observation and bounded controls

One initial v01 run developed a crunchy/noisy audio symptom near the second-key area. It is **not reproducible at present** and is not attributed to the checkpoint edits:

- a same-selector control with the Fire callback completely stock (v02) was played through almost the entire stage without reproducing the symptom;
- split controls v03a (presentation suppression only) and v03b (selector-store suppression only) also did not reproduce it;
- a later cold v01 retest did not reproduce it either.

Therefore the audio symptom is retained only as an unresolved/non-reproducible observation, not as a confirmed regression and not as evidence against v01.

### Native key-use dispatch and checkpoint/progression split — static comparison (2026-09-29)

**Static-confirmed:** the permanent item-use dispatch table at ROM `0x000A6E68` maps the native key/crystal inventory IDs to progression handlers that are separate from the ordinary pickup callbacks:

- Wind IDs `0x0E..0x10` -> `0x800721D4 / 0x8007226C / 0x80072220`;
- Earth IDs `0x11..0x13` -> `0x800720F0 / 0x8007213C / 0x80072188`;
- Water IDs `0x14..0x16` -> `0x800722B8 / 0x80072304 / 0x80072350`;
- Fire IDs `0x17..0x19` -> shared all-three-present handler `0x8007206C`;
- Prison IDs `0x1A..0x1C` -> inert/no-consume handler `0x80071F50`; Prison progression remains owned by the separately traced acquired-bit/door path;
- Bridge IDs `0x1D..0x1F` -> shared all-three-present handler `0x80071FE8`;
- Fortress crystal IDs `0x20..0x22` -> position-gated handlers `0x8007239C / 0x80072400 / 0x80072464`.

Wind/Earth/Water per-key use handlers test the corresponding low gate bit in `0x800C2406`, OR that bit into `0x802C0D54`, and call `0x8007EF30`. Fire and Bridge instead require all three native IDs in the ten-slot LIVE inventory before committing completion state. Fortress crystal use handlers commit their own `0x08/0x10/0x20` progression bits. These paths establish a native **use-time progression owner** independent of pickup-time checkpoint presentation/respawn state.

The remaining ordinary-key pickup callbacks split as follows:

| Stage | Pickup-time checkpoint behavior | Progression state preserved by the candidate | Static conclusion |
|---|---|---|---|
| Wind | Parameters 0/1 request `0x80062D60` at ROM `0xD500C` and increment/store `0x802C18F8` at `0xD5024`; parameter 2 does neither | Keep explicit awards, generic callback/sound, and live parameter-2 flag `0x802F60A0` | Two-NOP checkpoint candidate is Static-confirmed; runtime Pending |
| Water | All three increment/store `0x802C18F8` at `0xBA60C` and request `0x80062D60` at `0xBA610` | Keep award, sound, and parameter-1 live state `0x802F2980` | Two-NOP checkpoint candidate is Static-confirmed; runtime Pending |
| Earth | Only parameter 0 (Square) requests `0x80062D60` at `0xE1034` and writes selector 2 at `0xE1044`; parameters 1/2 do not create that checkpoint | Keep awards/sound and live local states `0x802F5520` / `0x802F5E22` | Square-only two-NOP candidate is Static-confirmed; runtime Pending |
| Bridge | Overlay callback `0x802EF178` only awards `parameter+0x1D` and plays sound | Native all-three use handler remains stock | Stock pickup path is already checkpoint-free; no suppression patch is indicated |
| Fortress | Stock crystal records use generic callback `0x80038770`; stage-9 branch awards `0x20..0x22` / acquired bits while skipping direct presentation and pickup-created selector writes | Boss-defeat activation and crystal use handlers remain stock | Stock crystal award is already checkpoint-free; remaining problem is arbitrary logical reward materialization at boss-trigger locations |

The local Wind/Water/Earth fields above are not dead checkpoint bookkeeping: each has independent overlay readers. The bounded proof candidates therefore deliberately leave them untouched.

**Water ID correction:** Water callback `0x802F2448` awards `callback_parameter + 0x14`. The cataloged Triangle / Three Bars / Moon records use parameters `0/1/2`, so the native inventory mapping is Triangle=`0x14`, Three Bars=`0x15`, Moon=`0x16`. The earlier future-global logical catalog had Triangle and Three Bars inverted; the implementation mapping is corrected alongside this static closure.

**Current generalization boundary (revised after Wind v01 runtime failure):** Prison L1 and Fire remain Runtime-confirmed bounded successes, but Wind disproves the broader assumption that pickup-time selector stores can be removed merely because use-time progression has a separate owner. Wind `0x802C18F8` is both checkpoint/respawn state and live stage-segment state. Selector-assisted v01 skipped the stock key-created steps `3/5`; after death the player re-entered an earlier non-key world state while retaining later key/progression state, and a later upper-room fight produced an abrupt live drop/relocation to the lower bridge area with earlier bridge geometry present again. Wind v01 is **Rejected / failed** as a production model, and Water/Earth runtime proofs using the same assumption are paused.

The corrected architectural question is now **reward ownership vs. location/state ownership**, not simply “key checkpoints on/off.” A global logical reward must not carry arbitrary destination-stage checkpoint/segment mutations with it. Conversely, stock stage-location/segment transitions may still be required even when that location's randomized reward changes.

### Wind location/reward ownership trace — Static-confirmed (2026-09-30)

The focused Wind trace resolves the central split far enough to constrain the materializer design:

| Semantic responsibility | Wind owner | Evidence / implication |
|---|---|---|
| Physical checkpoint/segment transition | Destination Wind location/event | Circle/Triangle stock callback parameters inject selector steps `3/5`, whose spawn-table coordinates match those physical pickup locations; independent spatial triggers supply `2/4/6/7/8/9`. These selector values are consumed by live Wind scene/setup logic. |
| Logical reward award | Logical item | Wind callback maps the key parameter to item ID and inserts it through `0x80075448`; that helper itself has no identified Wind selector effect. A foreign/randomized key therefore does not need to import the source stage's pickup callback merely to award its inventory identity. |
| Key-use permission | Physical Wind interaction zone | Wind spatial events set the low gate bits in `0x800C2406`. |
| Key progression commit | Logical key USE handler, conditioned by the physical gate | Permanent item-use handlers for IDs `0x0E..0x10` test those gate bits and OR matching progression bits into `0x802C0D54`. |
| Wind Three-Bars pickup-local state | Destination Wind stage/location state | `0x802F60A0` is written only by stock callback parameter 2 in the identified code and has multiple independent Wind-overlay readers. It is therefore not safe to attach this write to a globally movable logical Three-Bars reward. Exact reader semantics remain Pending. |

The ordinary manager's native callback ABI reinforces the need for an explicit destination-aware composition layer: at `0x800393BC..0x800393D0` it passes only record type and masked callback parameter, then calls the pointer at record `+0x18`; it does **not** pass destination ordinal. A production dispatcher will need a stable way to recover/encode destination identity if it is to run location-owned state effects independently of the randomized logical award.

This also reveals a limitation in current stage-local-v1: shuffling all seven words `+0x10..+0x2B` moves Wind's mixed callback/parameter along with the reward. That is **Static-confirmed as an ownership mismatch**, but a specific seeded runtime regression is not claimed without a bounded test.

**Wind v02 runtime refinement:** preserving the destination pickup callback unchanged is also insufficient. Wind key callback parameters 0/1 perform relative `selector += 1` transitions. In the bounded v02 route, tornado activation advanced the stage before the player backtracked to the stock Circle location; collecting that location then advanced into the future, unvisited Triangle checkpoint. The production candidate is therefore **destination-owned, order-guarded checkpoint semantics**: Circle checkpoint behavior only on predecessor selector `2` (commit `3`), Triangle only on predecessor selector `4` (commit `5`); otherwise skip both checkpoint presentation and selector write while still awarding the logical reward. This remains Pending runtime proof.
**Wind v04 runtime update:** the guarded Circle transition passed the targeted late-backtrack route: after tornado activation, revisiting the old Circle location no longer advanced into an unvisited future checkpoint, and death reconstructed at the tornado checkpoint. Triangle's guarded pickup checkpoint also behaved coherently on the tested route. Triangle USE is independently confirmed as progression-only; the door remained open after death while respawn stayed at selector 5. Static trace places selector 6 at a later physical subtype-6 trigger gated by Three-Bars pickup flag `0x802F60A0`, not at Triangle USE. The architecture is therefore materially supported, but v04 is not a clean success because the proof split omitted pickup sound on both moved rewards. Audio restoration is the next bounded correction. Two candidate directions remain Pending and require explicit design/proof before product integration:

1. **Location-owned stage/checkpoint semantics:** detach logical award identity from the stock location's stage-state effects, so randomized rewards award only their logical item while destination checkpoint/segment transitions remain attached to the appropriate physical stage locations/events.
2. **No-checkpoint/full-stage-restart policy:** if checkpoints are intentionally disabled, death must restart/reinitialize the whole stage coherently rather than merely forcing spawn coordinates or freezing `0x802C18F8`; stage-local geometry/scripts and authoritative randomizer inventory/persistence would need a bounded lifecycle proof together.

Do **not** implement “disable all checkpoints” by globally blocking `0x802C18F8` writes: Wind statically reads that selector in live stage logic, and v01 demonstrates that desynchronizing it from world progression is unsafe. Bridge and stock Fortress crystal awards remain Static-confirmed checkpoint-free; Fortress boss-reward materialization remains a separate problem.

### Fortress boss-defeat reward trigger ownership — static closure (2026-09-27)

**Static-confirmed:** Fortress overlay file `0x9E` directly couples the three assassin encounters to the first three ordinary pickup records. The encounter manager uses index `s4 = 0,1,2`; its table at VA `0x802F15C4` / ROM `0xC4AC4` resolves those indices to **ASSASSIN1 / type `0x0D`**, **ASSASSIN3 / type `0x13`**, and **ASSASSIN2 / type `0x1C`**. It writes `1 << s4` to the shared gated-enemy state `0x802C1140`, matching the three singleton ordinary-stream masks `1,2,4`.

After the corresponding encounter actor reaches the manager's completion path, the code computes `s4 * 0x30` and updates ordinary pickup record `0x802F1334 + s4*0x30`. At VA `0x802F043C` it copies the defeated actor's X coordinate into record `+0x00`; at `0x802F0454..046C` it reads record `+0x14`, clears bit `0x8000`, and writes it back. The three target records are:

| Encounter index | Fighter | Reward record | Stock reward |
|---:|---|---:|---|
| 0 | ASSASSIN1 / type `0x0D` = **Kia** | ROM `0xC4834` / RDRAM `0x802F1334` | Crystal Kia |
| 1 | ASSASSIN3 / type `0x13` = **Jataaka** | ROM `0xC4864` / RDRAM `0x802F1364` | Crystal Jataaka |
| 2 | ASSASSIN2 / type `0x1C` = **Sareena** | ROM `0xC4894` / RDRAM `0x802F1394` | Crystal Sareena |

This closes the previously Pending trigger-ownership question: **the boss/assassin encounter index owns when and where the reward record is activated; the crystal identity is merely the stock contents of that record.** A global assignment must preserve the indexed encounter-to-record activation and may replace the seven-word reward identity with whatever logical item is assigned to that location. The crystal IDs remain independently movable rewards.

This is a static closure of trigger ownership, not runtime validation of arbitrary replacement rewards at those three locations. Destination-safe award semantics and the composed Fortress materializer runtime gate remain Pending.

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

## TEST LAB cross-stage stress line (2026-09-28)

The proof-only TEST LAB materially strengthens the destination-materializer evidence while also rejecting one tempting implementation direction. Detailed vNN chronology is on [TEST LAB proof history](Test-Lab-Proof-History).

### Runtime-confirmed positive controls

- **v21:** three native Fire Herbs rendered and were all collectible through an explicitly loaded Fire resource file and isolated ordinary pickup manager.
- **v26:** the previously proven Fire -> Prison Level-1-key import also works inside TEST LAB beside native Herbs controls. This confirms that the hidden-room harness and relocated/expanded Fire resource-file path are compatible.
- **v27:** ten distinct key/crystal visuals coexisted in TEST LAB when Fire's **native resource-file/table architecture** was preserved and stock-empty Fire selectors were populated with full foreign bundles. The room entered normally. Fortress crystals required their crystal-specific presentation rather than the generic Fire-icon shell.
- **v31:** fifteen simultaneous **non-Earth** key actors entered without the Mission Objective corruption. This rejects a blanket claim that 15 live pickups alone are unsafe.
- **v33:** the same 15-live non-Earth composition rendered recognizably with a coherent low-RAM static native poster frame per imported item. Native Fire keys remained animated because their stock selectors/resources were untouched.

These are bounded proof results, not a production-safe universal capacity declaration.

### Rejected standalone-gallery path

v22-v25 replaced or bypassed too much of the destination-native resource representation. Twenty-one, compact-deduplicated, post-intro, and ten-item variants all hung at Mission Objective. Reducing bytes and delaying setup did not rescue the route. For this workstream, the custom standalone-gallery representation/path is **Rejected / failed**.

The accepted design direction is therefore to **preserve the destination stage's native resource-file/table grammar and extend it**, rather than synthesize a different top-level resource-file shape.

### Runtime-memory limits exposed by the stress proofs

The all-21 line is not accepted:

- v28 loaded an approximately `0x8F0C` Fire resource and produced an emulator-core `Unknown SI DMA PIF address: 00000000` failure;
- v29 reduced the resource to `0x4634`, avoided the core crash, but hung at Mission Objective and later produced the project's known music-speed corruption symptom;
- v30 instantiated only 15 records but still included Earth and still hung, so it did not isolate actor count cleanly;
- v31 kept 15 live actors but excluded Earth and entered successfully.

Accordingly, **resource-file byte size is not a standalone safety metric**, and no universal simultaneous-pickup ceiling is established. Production planning must budget the resource allocation together with actor/process, dynamic-texture, render-node, stage-entry, and other arena users.

### Frame-coherence rule for deduplication

v31 also exposed a concrete deduplication hazard: reusing one image payload while retaining metadata from different native frames produced striped/corrupted pickup art.

v32 fixed corruption by repeating one **complete native frame** — metadata plus image — across the descriptor's frame count. v33 improved recognizability by choosing a wider native frame per imported item before repetition.

Therefore, any production resource deduplication must preserve descriptor/frame/data coherence. Sharing image data is valid only when every consumer frame's metadata is compatible with that shared payload.

The v33 static-poster technique is proof evidence and a possible capacity fallback, not an approved 1.0 presentation change. Full native animation remains preferable where the destination budget permits it.

### Earth donor-family closure

**Runtime-confirmed, v38.** Earth Square / Four Squares / Triangle are ordinary 8-frame Type-4 pickup visuals in Earth ordinary-pickup resource file **0x30**. The earlier file-0x88 mapping was wrong: file 0x88 is MONK1 fighter data.

The v34-v36 Mission Objective hangs and v37 monk-like corrupted pickup are retained as negative controls for that mapping error. After tracing Earth stage setup, the materializer was corrected to use file-table entry `0x000A5250`, ROM `0x00305A30..0x0030A9FF`. v38 imported all three real Earth key bundles into TEST LAB through the destination-native Fire-file architecture; all three visuals were correct and the tested Earth key awarded correctly in inventory. The proof uses each key's native eight-frame descriptor; animation cadence was not separately instrumented.

Earth is therefore **closed as a bounded cross-stage visual donor family**. Remaining production gates are checkpoint-safe progression award semantics, composed foreign-key masking, Fortress destination stress/capacity, and production allocation/composition.

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

### Fortress — Runtime-confirmed bounded proof

The Fortress five-import stress construction is now manually Runtime-confirmed on the bounded 2026-09-30 route. The first five stock Herbs locations were materialized as Potion, Urn of Vitality, Formula, Eye, and Shield, while a sixth Herbs record remained untouched as a vanilla control. Fortress loaded normally; all five imported visuals rendered correctly and awarded the expected items; the control Herbs remained normal; and no rendering, audio, stability, or stage-progression regression was observed on the tested route.

This closes the pending Fortress destination-resource stress/capacity check for this five-import composition. It does **not** yet close arbitrary boss-defeat reward materialization, production allocation ownership, or exhaustive Fortress capacity.

### Fortress boss-defeat reward substitution — Runtime-confirmed bounded proof

A disposable Kia -> Potion proof retained Kia reward record `0xC4834` as the encounter-owned physical reward location and preserved the high `0x8000` activation bit in `+0x14`. Only the logical reward identity/resource path was changed to Potion. Runtime validation confirmed the replacement reward was absent before Kia's defeat, appeared only after Kia died, rendered as Potion, awarded Potion rather than Crystal Kia, and did not disrupt the tested encounter/stage continuation.

This is direct bounded evidence for the required architecture: **boss trigger/location semantics stay with the Fortress destination check while logical reward identity is independently materialized**. Jataaka/Sareena were not separately runtime-tested, but the static trigger manager uses the same indexed-record activation pattern for all three. Production still needs guarded allocation/ownership and generalized emission rather than copying this proof-local construction verbatim.

### Production-composition transport v01/v02 — v02 Runtime-confirmed

The first production-composition attempt placed the acquisition-mask/generic-award helper at the intended expansion-pool address but introduced a **second raw file (`0x19`) load from the pickup-manager stage-init resume path**. Manual runtime validation failed broadly at the mission-objective -> stage-entry boundary: stages hung, some reached music, and Fire did not complete load. That v01 transport is **Rejected / failed**.

Corrected v02 removes the second stage-init loader entirely. Pickup-manager resume stays on the previously Runtime-confirmed four-box reconstruction path, while helper transport uses the established shared file-`0x1A` bootstrap expansion-load architecture. The bounded proof places the materializer helper at `0x801B0900..0x801B09EF`, after the current controls runtime end and below Toasty's fixed base.

Manual runtime validation reported the composed route fully working: stage entry is healthy; Fire's first pickup materializes as Wind Circle and immediately masks to Glass; Wind reveals/uses the real Circle while ownership persists and re-masks outside Wind; and Kia's boss-owned reward trigger produces a Potion only after her defeat with correct visual/award behavior and healthy Fortress continuation.

This closes the **production-shaped materializer runtime-composition architecture gate** for the tested representative route. The proof's generated resource backing and helper bytes are still disposable evidence, not automatic browser/CLI product ownership. The next implementation step is to express the proven allocation/transport/materializer contract in the shared patch pipeline with guards/tests, then proceed to deterministic global assignment and solver work.

## Early Fire foreign-key proof

Before the extension-selector work, a direct raw Prison-to-Fire identity copy produced no usable item because the source selector was not meaningful in Fire. The successful follow-up demonstrated the broader architecture by relocating Fire's resource file, populating stock logical slot 5 with a Prison Level 1 key bundle, and using a dedicated award callback for item `0x1A`.

The proof file expanded from `0x2530` to `0x2BE8` and was relocated to ROM `0x00F00000..0x00F02BE7`. Appended file-relative resource records occupied `0x2558..0x25F7`. The foreign model rendered and awarded correctly while Fire's original Herbs resource remained intact.

This is **Runtime-confirmed feasibility evidence only**. Those exact ROM/callback placements are proof-era locations and do not constitute reusable production allocations; current allocation ownership belongs to [Memory and allocation map](Memory-and-Allocation-Map).

## Deterministic global shuffle

The legacy Lua prototype already had the high-level shape of a global shuffle:

1. flatten locations across all eight stages;
2. flatten the logical item multiset;
3. place nine progression rewards only when Powers as pickups is ON; otherwise model earnable XP;
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

The final 1.0 completion predicate is still **Pending**. At minimum it must include the selected Vanilla / Custom / Seed required-power condition described below and all finalized progression conditions needed to complete the run.

The legacy Lua predicate required its chosen Power-Upgrades count plus the three Fortress crystals. That is historical design evidence only; it must not be copied as the authoritative native predicate without reconciling the current stage graph and completion route.

## Required Power Upgrades

With **Powers as pickups** ON (the default), exactly **nine progression rewards exist in the world**. With it OFF, those nine generated Herbs retain their ordinary award and powers are earned from stock XP instead. The required number of powers remains an independent build setting in either mode; the whole-run solver must model the correct reward/XP source for the chosen mode.

The required count must:

- use Vanilla (stock Fortress XP gate `5100`, not an exact normal-XP tier count), Custom (`0..9`), or Seed (`0..9` from an independent deterministic RNG namespace);
- be independent of how many global layout candidates were rejected;
- be part of the whole-run solver's completion predicate;
- be displayed by the randomizer HUD;
- preserve native thresholds for pickup-driven rewards and use earnable XP/tier state when pickups are OFF.

The build-time range for Custom/Seed is `0..9`. Global mode-aware solver reachability and the final HUD remain Pending; an OFF-mode seed cannot be declared beatable merely because the Fortress gate patch is valid.

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

- complete the pending Fortress destination-stage composed stress proof;
- implement and runtime-validate a generic destination-safe key/crystal award path that preserves required progression/door state while suppressing pickup-created checkpoint/respawn relocation;
- compose the materializer with production ROM allocation/file-table ownership and runtime arena bounds, including actor/texture/render allocations rather than treating resource-file bytes as the whole budget;
- integrate the Runtime-confirmed foreign-key acquisition/reconstruction mask contract through guarded production ownership; the Fire -> Wind Circle v02 proof is green, but its proof-local hook is not yet normal browser/CLI composition;
- finalize the logical materializer schema and deterministic deduplication/capacity rules across the complete item pool;
- implement the deterministic global shuffle and explicit retry sequence;
- finalize the whole-run progression graph and completion predicate;
- integrate the selected required-power mode and both XP sources into the final solver/HUD;
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
