# Project status

Last consolidated: 2026-09-24.

> **Scope:** This page is the current-state dashboard for MKMSZR. It owns production/proof/pending maturity, current blockers, and priority order. It does **not** own full 1.0 requirements or long proof chronology.
>
> Canonical release requirements and acceptance gates: [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap). Detailed runtime evidence: [Runtime validation status](Runtime-Validation-Status). Detailed mechanisms and proof histories remain on their owning domain pages.
>
> Evidence labels are listed concisely on [Home](Home) and applied under the methodology in [Research workflow](Research-Workflow): **Runtime-confirmed**, **Static-confirmed**, **Implementation/CI-confirmed**, **Hypothesis / strong inference**, **Rejected / failed**, and **Pending**.

## Production systems

| System | Product state | Current evidence / limit |
|---|---|---|
| Clean-ROM validation, guarded patching, separate output, N64 checksum update | **Production** | Implementation/CI-confirmed for the supported USA Rev. 0 ROM; output is separate from the clean input |
| Compact eight-stage selector | **Production** | Runtime-confirmed A-button route across all eight safe stages; unsafe stock entries are excluded |
| 16 KiB runtime reservation and native payload | **Production** | Runtime-confirmed 16 KiB arena floor on the bounded all-stage profiler proof and no regressions reported on the tested full-production `TEST 16KB` + `rainbow` composition. The established Runtime V2 layout remains in the first 1 KiB; the remaining 15 KiB is an unassigned build-time expansion pool with CI-enforced bounds. |
| Ordinary-pickup persistence | **Production beta** | Representative Runtime-confirmed collection/restoration in all eight main stages; all 84 ordinary records are statically cataloged, not individually runtime-exhausted |
| Stage-local seeded pickup randomization | **Production beta** | All 84 ordinary records implemented; deterministic generation/access checks are Implementation/CI-confirmed; this is an interim stage-local mode, not the 1.0 global model |
| Pickup-driven XP progression | **Production beta** | Diagnostic B behavior is Runtime-confirmed through XP 85/258, Temple -> Wind, and title -> Fire. Stage entry restores XP but does not call the tier evaluator; full nine-tier runtime coverage remains Pending. See [XP and progression](XP-and-Progression) |
| Four inventory boxes and foreign-key masking | **Production beta** | Runtime-confirmed switching, transition preservation, and stage-local masking on documented routes; Game Over/new-run reset remains Pending |
| GAME SETTINGS frontend | **Production beta / Runtime-confirmed frontend.** | The complete in-game frontend is Runtime-confirmed. The accepted naming is now `TURN`, `ATTACK`, `SPECIALS`, `JUMP`, and `EXIT`; the current runtime menu still displays legacy `COMBOS` until the next ROM build performs the text-only rename. TURN gameplay is functional; ATTACK/SPECIALS/JUMP are persistent UI/state only. JUMP remains visible/greyed unless **ATTACK=MODERN AND SPECIALS=MODERN**, at which point `DPAD / BUTTON` becomes editable. Full-menu v04 is the accepted runtime baseline. See [Native HUD and UI](Native-HUD-and-UI) and [Player actions and special moves](Player-Actions-and-Special-Moves). |
| Native box indicator | **Production** | Runtime-confirmed `BOX n OF 4` through the native text path; the broader 1.0 randomizer HUD remains Pending. See [Native HUD and UI](Native-HUD-and-UI) |
| Boot branding and seeded phrase | **Production** | Redesigned legal-screen presentation is Runtime-confirmed; seeded phrase uses a separate deterministic namespace |
| Rebranded title screen | **Production beta** | Candidate-B art plus configurable uppercase `<NAME> EDITION` are Runtime-confirmed through the normal production composition. The accepted implementation is data-only; the earlier executable-wrapper allocation is Rejected / failed. See [Presentation and branding](Presentation-and-Branding) |
| Post-legal logo bypass and selector-only save bypass | **Production** | Runtime-confirmed bounded routes; legal text and later/manual saves remain intact |
| Outfit recoloring | **Production** | Static modes remain guarded source-TLUT transforms. `rainbow` is now a normal browser/CLI option using the Runtime-confirmed 64-phase native palette path; seed `RAINBOW64` production output is byte-identical to the manually validated proof v01. See [Palette and recoloring](Palette-and-Recoloring) |
| Browser/CLI shared patch core | **Production beta** | Both surfaces use the same patch core. Every generated ROM now includes the Runtime-confirmed in-game `GAME SETTINGS -> TURN: TOGGLE / LOCK` control option; this is configured in-game, not by a separate browser toggle. The web requires only the MKMSZ N64 target and presents MKT Rev. 2 N64 as an optional donor for supported donor-backed features. CI covers donor extraction/build composition; gameplay claims remain bounded to documented runtime routes. |

## Proof-only systems

These results are important feasibility evidence but are **not** normal browser/CLI product features unless stated above.

| Workstream | Current conclusion | Remaining gate / owner |
|---|---|---|
| Cross-stage ordinary-item materialization | **Runtime-confirmed in bounded proofs.** Prison renders and awards five simultaneous imported item visuals while an untouched Herbs control remains correct. External-to-embedded ordinary resource conversion is also Runtime-confirmed. | The pure planner is implemented but pipeline-disconnected. Fortress stress validation and destination-safe key/crystal award handling remain Pending before a guarded production integration proof. See [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |
| Cross-stage enemy import | **Runtime-confirmed proof.** A Temple monk can be imported into Fire and function in combat; a simpler Fire ordinary-enemy substitution also works. | Arbitrary roster/resource compatibility, death/despawn presentation, allocation policy, and deterministic product integration remain Pending. See [Enemy randomization](Enemy-Randomization) |
| MKT fighter / Sektor takeover | **Runtime-confirmed proof line through v89; v85 remains built but untested and statically rejected for the ordinary straight branch.** v62 remains the stable combo baseline; v75 remains the stable missile-flight baseline. v87 Runtime-confirms the donor-faithful ROCKETD1 + ROCKET_P asset/palette pair for the flying missile. v88 keeps that correct rocket but still shows one frame of stale Sektor-like texture before it, disproving the earlier interpretation that v84 had established synchronous first-frame texture readiness. Static render tracing now separates descriptor binding from texture-slot publication: `0x8001BDA0/0x800304C0` mark `+0xFA` dirty, `0x800185B8` later queues the slot upload through `0x8001D6EC`, and the upload is drained separately. v89 Runtime-confirms the missing pre-publication texture-slot seam: synchronous native `0x8001BF70` preparation before stock actor-list insertion removes the one-frame corrupted Sektor while preserving the correct v87 rocket and v75 flight. This validates first-visible composition as **descriptor/frame state + correct dynamic ROCKET_P + texture-slot readiness before publication**. The v89 storage/allocation recipe is still a bounded one-shot proof, not production-ready. Helpers, strike/effects/audio, balanced palette/texture release and final integration remain pending. | Proof-only, including bootstrap allocation overlap. Preserve the generic donor→MKMSZ adapter; see [Sektor takeover proof history](Sektor-Takeover-Proof-History), [MKT adapter primitives](MKT-Adapter-Primitives), and [Player actions and special moves](Player-Actions-and-Special-Moves). |
| Toasty audio | **Runtime-confirmed production composition.** v46 confirms the dedicated MKT Toasty voice route with ordinary pickup audio restored to stock; v47 confirms that same route in the full current production composition. | Production keeps stock pickup `524 -> 681 -> 524 -> 133` untouched and uses dedicated Toasty event `52 -> 68 -> 608 -> 533`. The product probability is **80/1000 (8%)**. See [Toasty audio research](Toasty-Audio-Research). |
| Toasty visual | **Runtime-confirmed production composition.** v38 is perfect across all eight safe stages; v40 validates compact uncached execution; v42 is the accepted lower-right 3/16/8 presentation baseline; v44 confirms the successful-reaction trigger; v46 confirms dedicated audio with stock pickup sound; v47 confirms the complete effect in the full current production composition. | Production uses the reconciled `08/0E/12/13/14/15/17` successful/unblocked reaction family and **80/1000 (8%)**. The donor-aware patch module is on the shared patch core; browser extraction from the user-supplied MKT Rev. 2 ROM and optional CLI `--mkt-rom` wiring are Implementation/CI-confirmed. See [Toasty visual research](Toasty-Visual-Research) and [Toasty audio research](Toasty-Audio-Research). |
| Reverse Elbow / donor move adapter research | **Proof/research only.** Earlier host-action work established useful MKMSZ action primitives; the accepted direction is genuine donor-to-MKMSZ semantic translation rather than behavioral approximation. | Not a 1.0 blocker. Current donor translation work belongs to [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer) and [Player actions and special moves](Player-Actions-and-Special-Moves) |

## Current 1.0 blockers

[1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) is the canonical owner of the complete requirement text, acceptance criteria, ambiguities, and final release gate. The current blocker summary is:

| Blocker | Current state |
|---|---|
| Production-safe global cross-stage item materialization | **Pending.** Finish the composed planner gate, destination-safe key/crystal award path, guarded allocation/composition, and a disposable integration proof before enabling it in the product pipeline |
| Deterministic global shuffle and retry model | **Pending.** Replace the interim eight stage-local pools with one deterministic global logical run and explicit deterministic retry attempts |
| Whole-run solvability validation | **Pending.** Finalize current access rules, completion predicate, and seed-specific required-Power-Upgrades policy |
| Native randomizer HUD | **Partial.** Native text and box state are proven; checks/progression/key/pickup run-state display is still required |
| Temple Map and run lifecycle invariants | **Pending.** Resolve Map inclusion/trigger separation/persistence, then HP/lives/continues preservation, Game Over/new-run reset, and Very Hard enforcement |
| Final production-composition runtime gate | **Pending.** Run a representative full global seed after the above are integrated, including all nine progression tiers and the major lifecycle boundaries |

## Current priority order

1. Finish the cross-stage resource/materialization production gate: complete the pending composed stress validation, add destination-safe key/crystal award handling, then build and manually validate the smallest guarded integration proof.
2. Replace stage-local generation with deterministic global shuffle plus whole-run solver, including explicit deterministic retry attempts and a deterministic per-seed required-Power-Upgrades target.
3. Build the native randomizer HUD around the finalized global-run state.
4. Resolve Temple Map behavior, then HP/lives/continues lifecycle, Game Over/new-run reset, and the Very Hard invariant.
5. Run the final representative full-seed 1.0 validation.
6. Post-1.0: ordinary-enemy randomization/resource compatibility, imported-enemy death/despawn work, and donor-move/Sektor expansion.

This order mirrors the current release dependency chain; it is not permission to treat later proof work as production before its own validation gate.

## Current evidence notes

- **XP:** the first V2 productionization attempt is **Rejected / failed** because stage initialization called the native tier evaluator too early. Diagnostic B isolated that timing error and is the current production behavior: restore persistent XP at stage entry, evaluate tiers only when a progression pickup is collected. Detailed Diagnostics A/B remain in [XP and progression](XP-and-Progression).
- **Title:** current production uses the Runtime-confirmed data-only Candidate-B composition. The old executable wrapper that overlapped pickup-persistence ownership remains **Rejected / failed**; proof hashes and integration history remain in [Presentation and branding](Presentation-and-Branding).
- **Sektor:** v62 remains the tested combo baseline; v75 the last stable tested straight-missile flight. v76–v79 remain negative/failed controls; v85 is statically rejected and untested. v87 Runtime-confirms exact retail rocket pixels/colors. v88 preserves the good rocket but still exposes a one-frame corrupted Sektor-like texture, showing that early descriptor/cursor binding alone does not synchronously replace the finalized projectile texture slot before publication. v84's earlier apparent first-frame suppression is therefore reinterpreted as a selector-zero presentation artifact, not proof of ready rocket texture. v89 Runtime-confirms the synchronous pre-publication slot-load proof: the corrupted first-frame Sektor is gone and the correct rocket remains. Next work is lifecycle/ownership productionization, not further first-frame cosmetic iteration.
- **Sektor Run — accepted integration directive (2026-09-25):** replace the v58 twelve-physical-pose Run with the six retail N64 MKT poses `RBRUN1,3,5,7,9,11`, each held for two MKMSZ visual ticks: `1,1,3,3,5,5,7,7,9,9,11,11`. Branch proof `MKMSZR_sektor-run-six-pose_common-proof_v01.z64` (SHA-256 `7f8dc72a…`) was manually preferred over the tested double-loop alternative `1,3,5,7,9,11,1,3,5,7,9,11`; do **not** adopt the double-loop variant. The accepted integration should physically omit the six supplemental WIMP even poses and remove the inherited PS1 Run input/decoder path, which is dead on the current v58 line. A full repack analysis is Implementation/static-confirmed at file-`0x87 = 0x4CD68`, saving `0x1694` / 5,780 bytes versus `0x4E3FC` and increasing v49-bound headroom from `0x148` to `0x17DC`; the physical-removal composition still needs bounded runtime regression before becoming the new Sektor baseline.
- **Toasty:** v47 is Runtime-confirmed in the full current production composition. It preserves the accepted v42 3/16/8 lower-right presentation, the v44 successful-reaction family, and the v46 dedicated-audio route with stock pickup sound unchanged. Production packs the Toasty module at `0x801B0000..0x801B331F`, leaving `0x100` bytes before the reserved-pool boundary; the selected product probability is **80/1000 (8%)**. Browser donor-asset extraction is wired through the optional MKT Rev. 2 input, while ordinary builds remain valid without that donor. Detailed evidence is canonical in [Toasty visual research](Toasty-Visual-Research) and [Toasty audio research](Toasty-Audio-Research).
- **Cross-stage items:** a logical selector is not proof of free physical storage. Production integration must preserve explicit resource ownership, bounded allocation, deduplication, and destination-safe award semantics.

## Explicit exclusions and non-blockers

- Enemy randomization and Reverse Elbow / foreign-move completion are **not 1.0 blockers**.
- Bosses and scripted encounters are not ordinary-enemy entries.
- The Temple Map is not one of the 84 ordinary pickup records; its 1.0 inclusion policy is still explicit Pending work.
- Zero/unused-looking resource selectors are not automatically free physical storage.
- PS1 addresses and platform behavior do not transfer to N64 without demonstrated compatibility.
- Disposable proof ROM patches, proof caves, and archive handoffs are not silently part of the production pipeline.
- Runtime confirmation is always limited to the documented route; CI/static success does not imply exhaustive gameplay validation.
