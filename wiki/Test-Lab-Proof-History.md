# TEST LAB proof history

> **Scope:** This page owns the detailed disposable-proof chronology for the hidden Fire God Room / selected-Test-Characters composition that became the MKMSZR **TEST LAB**, including the 2026-09-28 pickup-placement and cross-stage materialization stress line. Current product state remains on [Project status](Project-Status); current materializer design remains on [Global item materialization and solvability](Global-Item-Materialization-and-Solvability). These proofs are not production allocations or browser/CLI features.

## Current conclusion

**Runtime-confirmed bounded result:** the hidden room can be composed as a stable empty TEST LAB by reusing the healthy Fire selector-5 shell, selected-Test-Characters helper behavior, and suppressing the test-fighter allocation. The room supports normal lighting, HUD, movement, attacks, Pause/Inventory, ordinary pickup-manager execution, controlled pickup placement, and bounded cross-stage resource experiments.

The strongest current materialization result is **v33**:

- 15 simultaneous **non-Earth** key pickups enter the room without the Mission Objective corruption seen on the rejected 21-item line;
- Wind, Water, Fire, Prison, and Bridge families are present;
- native Fire icons retain stock animation;
- imported families use a low-RAM coherent static native frame chosen for recognizable width;
- the user reported all displayed items recognizable;
- Earth resource data may be resident in the resource file in some proofs, but **direct cross-stage Earth-key rendering/award is still Pending**;
- no universal safe simultaneous-pickup count is established;
- no 21-live-item composition is accepted.

The proof line also establishes a negative architectural rule: **the destination stage's native resource-file architecture must be preserved.** The custom standalone-gallery route from v22-v25 is rejected for this workstream.

## Stable room construction

The successful room does **not** use native Stage-7 initialization as-is. Earlier Stage-7 experiments exposed missing lifecycle/setup behavior. The accepted proof composition instead keeps the healthy normal Fire selector-5 shell and uses selected Test Characters as a bounded helper route.

Key milestones:

- **v06 — Runtime-confirmed positive control:** stock Fire selector-5 composition enters cleanly, including the Fire God.
- **v07 — Rejected:** native Stage-7/debug-helper path reproduces the broken-control state.
- **v08 — Runtime-confirmed bounded control restoration:** normal lighting/HUD/controls/Pause/Inventory with selected test character index 0 and Fire-God stream suppressed; MONK1 death still hung.
- **v09 — Runtime-confirmed bounded terminal correction:** the MONK1 terminal route was redirected from the Fire selector-10 terminal choice to the native Stage-7 terminal helper; killing MONK1 no longer hung.
- **v10 — Runtime-confirmed empty TEST LAB baseline:** the selected fighter allocation JAL at VA `0x80065928` / ROM `0x00066528` was NOPed while preserving the healthy helper/common tail. The user reported an empty, stable room with normal controls and no hang. Disposable ROM SHA-256: `3a5bef3491daabd28a8610aba80521302117d8eb1d8e772be4b411ec216136d2`.

The floating background amulet stopped spinning once boss-specific scheduling was removed. That is presentation-only and is not a TEST LAB functional blocker.

## Pickup-manager bring-up and placement

Normal Fire selector 5 skips ordinary overlay entry `0x802ECE30`, so it does not naturally install the ordinary pickup manager/resource composition used by standard Fire routes. The TEST LAB proofs therefore had to materialize file ID `0x3C` and allocate an isolated class-`0x19` pickup manager explicitly.

### Rejected setup attempts

- **v11 — Rejected / failed:** overwrote parent `+0x6F4/+0x6F8` without safe restoration; hung at Mission Objective after music.
- **v12 — Rejected / failed:** moved three stock Fire records but no pickup manager existed; no pickups appeared.
- **v13 — Rejected / failed:** patched an ordinary-overlay manager wrapper that selector 5 never entered; no pickups.
- **v14 — Rejected / failed:** coordinate changes could not matter while the manager remained absent.

### Successful manager and visual controls

- **v15 — Runtime-confirmed actor construction, visual failure:** explicitly loaded Fire resource file `0x3C`, published it through `0x802F82B8`, saved/restored the parent controller fields, and allocated an isolated three-record manager. Three pickup actors appeared. Their external-resource-backed Potion/Formula/Extra-Life visuals were corrupted vertical strips. ROM SHA-256: `477f383a43c50f4cf343eefff320ad4b45825bebe13daa4533d47bfafec4bdb0`.
- **v16 — Runtime-confirmed embedded visual control:** copied the complete stock Fire Herbs identity slice into all three test records. All three Herbs rendered correctly, proving the manager/resource composition itself was healthy. They were still vertically unreachable. ROM SHA-256: `c35df94b1a8a95044c00981f81d9b236ca31f0ddb2d166dd594a71bbf91053b0`.
- **v17 — Rejected placement:** an incorrect large fixed-point Y value moved the pickups out of the visible/reachable plane.
- **v18 — Runtime observation / insufficient placement:** keeping live depth and setting the third coordinate to zero did not fix vertical pickup reachability.
- **v19 — Rejected placement inference:** using `0xFFFFCA00` from the Fire-God actor conversion moved the items even higher, proving the sign/direction interpretation was wrong for this placement purpose.
- **v20 — Runtime-confirmed calibration:** three different values on record/actor `+0x30` established the reachable neighborhood. The left Herbs at **+128 world units / `0x00008000`** was collectible; +192 and +256 were not.
- **v21 — Runtime-confirmed pickup baseline:** all three Herbs used +128 world units and 96-world-unit horizontal center spacing. The user collected all three successfully. ROM SHA-256: `7a70089478420ad5f1d8f56103336ed2a8a5b1047e949a0cff153d00849b8b34`.

Later materialization proofs moved the row slightly upward to **+120 world units** while preserving the accepted 96-unit spacing.

## Standalone-gallery experiment — rejected

v22-v25 attempted to replace the Fire resource representation with increasingly compact custom standalone galleries.

- **v22 — Rejected / failed:** 21 unique ordinary key/crystal visuals, expanded gallery `0xE4E8`; hung at Mission Objective. ROM SHA-256: `83ee6bf0e95ceb2e419d8122801c09cf8e92f3c4ff4831240e51a6c10ee08b02`.
- **v23 — Rejected / failed:** deduplicated compact gallery `0x98BC`; same Mission Objective hang despite a 19.5 KiB reduction. ROM SHA-256: `aa7d04294848106b0d7c4b6f124a434a2ba22495c55ebc50591c005137758959`.
- **v24 — Rejected / failed:** deferred gallery installation until the Fire finalizer had written gameplay-active state `0x802ECE18=2`, left ROM file-table entry `0x3C` stock during entry, and reduced the gallery to one frame per item. It still hung. ROM SHA-256: `34abd5490a09942494c507b59aa3c0a07cf3b4ef2b063d2f9065540407b98300`.
- **v25 — Rejected / failed:** reduced the same custom path to ten representative unique items; still hung. ROM SHA-256: `b84a355f1487f54e13c9dc058d3287ddc95447adc0d147da82d3c518e20c71ed`.

**Conclusion:** neither raw item count nor raw gallery byte size explains these failures. The common custom standalone-gallery representation/path is rejected for the TEST LAB materialization line.

## Return to native Fire resource architecture

### v26 — proven foreign-key control

v26 returned to the Runtime-confirmed v21 room and used the previously proven Fire→Prison Level-1-key materialization architecture:

- preserve the complete stock Fire resource-file layout;
- relocate/expand file `0x3C`;
- populate stock-empty Fire selector 5 with the full Prison L1 key bundle;
- use the dedicated destination-safe proof callback that awards inventory ID `0x1A`;
- retain two ordinary Herbs controls.

The room entered and the imported key rendered alongside the controls. This ruled out TEST LAB itself and Fire resource relocation as the cause of v22-v25. ROM SHA-256: `9a7411b356cd6d3c4c9ef0f39d8c9e54a39a101c1142059ad2dc9d3d01f26dae`.

### v27 — ten distinct items, Runtime-confirmed

v27 scaled the **native Fire-file** architecture rather than the rejected standalone gallery. It preserved Fire's native key selectors and populated stock-empty Fire selectors with full foreign embedded bundles. Ten distinct key/crystal visuals entered and rendered in TEST LAB.

The user reported the composition worked. The Fortress crystals looked visually wrong because their records were temporarily given the generic Fire-icon presentation shell rather than the Fortress crystal presentation pointer.

ROM SHA-256: `6d1eb8ba5d355b275caeb292e2545401813bef68b79815a2b7ac43c9a3aa8ffa`.

### v28-v30 — unsafe 21-item line

- **v28 — Rejected / failed:** all 21 unique ordinary key/crystal tokens were composed through the Fire-file architecture with a resource size of `0x8F0C`. The emulator core reported `Unknown SI DMA PIF address: 00000000`; treat this as severe runtime corruption, not a normal gameplay hang. ROM SHA-256: `5cce9aca2086523525ec57a09f47796d1f396749f115b047179cf3a8577a61fe`.
- **v29 — Rejected / failed:** reduced the 21-item resource to `0x4634` by reusing one image per imported item. It no longer produced the emulator-core crash, but hung at Mission Objective and the user reported music speeding up after several seconds, a repeated project symptom of memory/runtime corruption. ROM SHA-256: `ddda99b32c3d01c4de950f6c90d0eb11186963460210cb6d9ea0ff3ab1040b02`.
- **v30 — Rejected / inconclusive actor-threshold test:** kept the v29 resource bytes and instantiated only the first 15 records. It still hung, but those first 15 included all three Earth keys, so it did not cleanly isolate actor count. ROM SHA-256: `c35a910aeafca8f4f311005dd21bad976c8cf200d9f110a2336c950686486b66`.

No production or generic safety threshold should be inferred from 10 working and 21 failing. Resource payload, frame grammar, dynamic texture/render allocations, actor count, and stage-entry composition all contribute.

## Fifteen-item non-Earth closure

### v31 — Runtime-confirmed stable composition, corrupted art

v31 retained the same low-RAM 21-item resource payload but reordered the dedicated proof records so the **15 live actors excluded Earth**:

- Wind ×3
- Water ×3
- Fire ×3
- Prison ×3
- Bridge ×3

Earth ×3 and Fortress crystals ×3 remained resident but uninstantiated. TEST LAB entered without the Mission Objective hang. Several imported pickups rendered as striped/glitched graphics.

This proves that **15 live pickups alone are not sufficient to reproduce the v29/v30 corruption** on this route. It does not establish a universal 15-actor safety ceiling.

ROM SHA-256: `32e2ada08fc631a5aa8e6b970118ccf40a769b83b3342deef09c1db342d9ad23`.

### v32 — coherent static frame

The low-RAM importer had reused each item's first image payload while preserving later frames' metadata. That paired incompatible frame geometry/presentation metadata with one image and explained the v31 striping.

v32 repeated the **complete first native frame** — metadata plus image block — across the donor's original frame count. The corruption was removed, but most imported spinning keys froze on an edge-on first frame and looked like similar narrow slivers.

ROM SHA-256: `187eac6a3469dce698558c806e2049793f2634829dd2ef9144e76f8f3e9295e4`.

### v33 — Runtime-confirmed recognizable static presentation

v33 selects one static native poster frame independently per imported item:

1. maximize the first big-endian `u16` in the native frame metadata, used here as the display-width discriminator;
2. break equal-width ties by larger native image payload;
3. repeat that entire selected frame — metadata and image — across the original descriptor frame count.

The user reported that all displayed pickups were recognizable. The three items still visibly animating were the native Fire-stage keys, whose stock selectors/resources were intentionally left untouched.

v33 resource size: `0x4BE4` / 19,428 bytes. ROM SHA-256: `b09a254a173a77f2f41f60ccaa5c5a1f8c45d22dd8b858c2fab7bed75e53e0c8`.

This static-poster technique is **proof evidence / possible low-memory fallback**, not yet a 1.0 product decision. 1.0 still requires the randomized pickup to visually represent its actual item; whether imported keys must retain full native spin animation is a separate presentation/capacity decision.

## Earth boundary

Earth's three keys are ordinary logical pickups, but their native image-block framing differs from the convenient little-endian embedded-size grammar used by the generic non-Earth extractor. Their descriptors are normal embedded-data bundles with native frame counts:

- Earth Square: 12 frames;
- Earth Four Squares: 9 frames;
- Earth Triangle: 9 frames.

The stage catalog already owns exact Earth frame/image bounds. Some later TEST LAB resource files included Earth resource data, but **no accepted proof directly instantiated all three Earth keys outside Earth**. The next bounded materialization task is therefore a three-Earth-key TEST LAB proof using the proven native Fire-file architecture and cataloged Earth bounds.

No new deep Ghidra trace is required unless that bounded proof fails.


## Earth-key closure — v34-v38

The first Earth-key TEST LAB attempt exposed a catalog/source error rather than a special pickup format.

- **v34 — Rejected / failed:** imported all three apparent Earth bundles from file `0x88`; hung at Mission Objective.
- **v35 — Rejected / failed:** corrected pickup record `+0x0C` from Earth value `6` to Fire destination value `4`; still hung. This correctly preserved destination-attached location metadata but did not address the actual visual-source error.
- **v36 — Rejected / failed:** kept all three apparent bundles resident but instantiated only Earth Square + Herbs; still hung. This ruled out live actor count and the other two Earth keys as the primary cause.
- **v37 — Runtime-confirmed award / Rejected visual source:** converted the apparent Earth Square Type-5 frame to a self-contained raw Type-0 image. TEST LAB entered, Earth Square and Herbs were both collectible, and Earth Square awarded correctly in inventory. The rendered pickup was corrupted and visibly contained MONK1 imagery.
- The v37 visual was the decisive clue: file `0x88` is the Earth MONK1 fighter resource, not the ordinary-pickup resource.
- Static stage-setup tracing then resolved the real ordinary-pickup resource as **global file `0x30`**, file-table entry `0x000A5250`, ROM `0x00305A30..0x0030A9FF`. Earth setup publishes the allocated file-`0x30` base through `0x802F82B8` before the ordinary pickup manager consumes selectors.
- File `0x30` selectors `0,1,2` are the real Earth Square / Four Squares / Triangle visuals: **8 native Type-4 embedded frames each**.
- **v38 — Runtime-confirmed Earth donor closure:** imported all three real file-`0x30` Earth key bundles into Fire selectors `5,6,7`, with one untouched native Herbs control. The user reported the result “Perfect. Just perfect.” The screenshot shows all three recognizable Earth symbols plus Herbs, and inventory shows the Earth key awarded correctly. The three Earth visuals retain their native animation in this proof.

v38 disposable ROM SHA-256: `db7431256a7ff7fdb95c71ce386db35ce102f32f5488df0113665f2b11757fb4`.

**Conclusion:** Earth is not a special Type-5 pickup family. The v34-v37 failures came from using the wrong global file. Earth is now Runtime-confirmed as a normal cross-stage ordinary-item visual donor family at the bounded v38 scope.

## Production implications

The TEST LAB line changes the implementation guidance for the global materializer:

- preserve the destination stage's native resource-file/table grammar;
- distinguish logical selector capacity from physical payload storage;
- use stock-empty selectors only as selector indices; relocate/expand the file for payload bytes;
- use extension selectors where stock selector capacity is exhausted;
- normalize external-resource-backed visuals to self-contained embedded form where required;
- deduplicate only when descriptor/frame/data semantics remain coherent;
- never reuse an image payload with incompatible frame metadata;
- budget the loaded resource **together with** dynamic pickup actors, texture/render allocations, stage-entry temporaries, and other arena users;
- do not treat the clean-era allocator-headroom number as a per-file safe budget;
- retain explicit negative controls for corruption symptoms such as Mission Objective hangs, music-speed anomalies, and emulator-core DMA failures;
- keep Earth as a separate donor-family runtime gate until its cross-stage proof passes;
- keep checkpoint suppression, foreign-key inventory masking, Fortress boss-reward trigger ownership, and Temple Map behavior as separate composition gates.

## Related owners

- [Stage flow and selector](Stage-Flow-and-Selector) — hidden-stage/Fire composition and TEST LAB route.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — current materializer design and 1.0 gates.
- [Memory and allocation map](Memory-and-Allocation-Map) — ownership and runtime-allocation safety.
- [Stage catalog — Fire](Stage-Catalog-Fire) and [Stage catalog — Earth](Stage-Catalog-Earth) — stage-specific selector/resource facts.
- [Experiments, failures and superseded findings](Experiments-Failures-and-Superseded-Findings) — rejected approaches index.
- [Runtime validation status](Runtime-Validation-Status) — concise evidence matrix.
