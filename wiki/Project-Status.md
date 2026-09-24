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
| Native box indicator | **Production** | Runtime-confirmed `BOX n OF 4` through the native text path; the broader 1.0 randomizer HUD remains Pending. See [Native HUD and UI](Native-HUD-and-UI) |
| Boot branding and seeded phrase | **Production** | Redesigned legal-screen presentation is Runtime-confirmed; seeded phrase uses a separate deterministic namespace |
| Rebranded title screen | **Production beta** | Candidate-B art plus configurable uppercase `<NAME> EDITION` are Runtime-confirmed through the normal production composition. The accepted implementation is data-only; the earlier executable-wrapper allocation is Rejected / failed. See [Presentation and branding](Presentation-and-Branding) |
| Post-legal logo bypass and selector-only save bypass | **Production** | Runtime-confirmed bounded routes; legal text and later/manual saves remain intact |
| Outfit recoloring | **Production** | Static modes remain guarded source-TLUT transforms. `rainbow` is now a normal browser/CLI option using the Runtime-confirmed 64-phase native palette path; seed `RAINBOW64` production output is byte-identical to the manually validated proof v01. See [Palette and recoloring](Palette-and-Recoloring) |
| Browser/CLI shared patch core | **Production beta** | Both surfaces use the same patch core; CI covers build/import composition, but full gameplay behavior remains outside CI |

## Proof-only systems

These results are important feasibility evidence but are **not** normal browser/CLI product features unless stated above.

| Workstream | Current conclusion | Remaining gate / owner |
|---|---|---|
| Cross-stage ordinary-item materialization | **Runtime-confirmed in bounded proofs.** Prison renders and awards five simultaneous imported item visuals while an untouched Herbs control remains correct. External-to-embedded ordinary resource conversion is also Runtime-confirmed. | The pure planner is implemented but pipeline-disconnected. Fortress stress validation and destination-safe key/crystal award handling remain Pending before a guarded production integration proof. See [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |
| Cross-stage enemy import | **Runtime-confirmed proof.** A Temple monk can be imported into Fire and function in combat; a simpler Fire ordinary-enemy substitution also works. | Arbitrary roster/resource compatibility, death/despawn presentation, allocation policy, and deterministic product integration remain Pending. See [Enemy randomization](Enemy-Randomization) |
| MKT fighter / Sektor takeover | **Runtime-confirmed proof line with missile experiments through v74.** v62 remains the stable tested combo baseline; v69 Runtime-confirms a safe one-frame genuine chest-open player pose, v70 Runtime-confirms a genuine horizontal rocket frame reaching/travelling as the projectile, v72 Runtime-confirms stable mirrored native placement, v73 Runtime-confirms direct per-tick acceleration, and v74 Runtime-confirms the folded 60->30 Hz resampler is stable. Comparative 60-fps MKT/v74 video shows the temporal ramp is now broadly similar but v74 late visible speed is only about half the donor's on the tested route, so a separate donor-local -> target-world spatial scale remains Pending. Smoke/effects, audio, palette/helper cleanup, reacting-target branch, strike/reaction translation, and final lifecycle composition also remain Pending. | Still proof-only. v62 and v65-v70 use proof code inside production-owned bootstrap space and require reallocation for any integration. The accepted special-move direction is now the generic donor→MKMSZ projectile adapter, not further Ice-path tuning. See [Sektor takeover proof history](Sektor-Takeover-Proof-History), [MKT adapter primitives](MKT-Adapter-Primitives), and [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer). |
| Toasty audio | **Runtime-confirmed proof.** Sound proof v03 plays the audibly confirmed MKT Toasty voice through MKMSZ's native audio path. | Final product trigger/allocation is Pending. See [Toasty audio research](Toasty-Audio-Research) |
| Toasty visual | **Runtime-confirmed image proof; compact production-layout proof pending runtime.** v38 is perfect across all eight safe stages. v39 is Rejected / failed. v40 fixes the execution architecture with two tiny KSEG0→KSEG1 trampolines and compacts the unrolled proof into 628 bytes of executable code plus 144 bytes of tables, 36 bytes of slot state, and the 512-byte TLUT; aligned expansion use is 1,360 bytes. | Runtime validation of v40 is Pending. On pass, proceed directly to audio + slide/lifetime composition, then the final uppercut/contact + 4% trigger. See [Toasty visual research](Toasty-Visual-Research) |
| Direction-facing / facing-lock controls | **Partially Runtime-confirmed proof.** v02 proves opposite-direction auto-flip + stock forward locomotion and held-Turn backpedal behavior, but standalone Turn still fires once. v01 is Rejected / failed for the wrong `0x802FCE20` pointer; v03 is Rejected / failed because actor-identity gating still did not suppress the turn. v04 makes the gameplay Turn routine an unconditional no-op as the next bounded diagnostic; runtime validation is Pending. | Still proof-only and outside 1.0 scope. Confirm the actual standalone-Turn suppression point, then broaden action-state/inventory/boss coverage before settings or production integration. See [Player actions and special moves](Player-Actions-and-Special-Moves). |
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
- **Sektor:** v61 is **Rejected / failed** because donor reaction selector `0x02` was reused numerically; v62 fixes that combo route. The later missile line is documented through v74: v63 rejects an unsafe file-`0x87` liveness assumption, v65-v67 reject intrusive lifecycle replacements, v68 is the stable stock-lifecycle control, v69 proves the resolved chest-pose cursor hook, v70 proves genuine rocket presentation while rejecting Ice-path tuning as the final adapter strategy, v71 rejects a combined placement/movement revision after an immediate hard hang, v72 Runtime-confirms direct `(+5,+38)` native placement with correct facing mirroring, v73 Runtime-confirms stable visible acceleration; the subsequent static trace derives 60 Hz donor -> 30 Hz target resampling, and v74 Runtime-confirms that cadence path is stable while comparative donor/target video rejects the earlier 1:1 spatial-unit assumption as a complete fidelity conversion. Full chronology remains canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).
- **Toasty:** audio identification/playback is Runtime-confirmed in v03 and visual v38 is Runtime-confirmed perfect across all eight safe stages. v39 is Rejected / failed. v40 is the corrected compact layout: 628 bytes of table-driven native code, 144 bytes of tables, 36 bytes of slot state, and a 512-byte TLUT use 1,360 aligned expansion bytes total; freshly loaded code is entered only through KSEG1 via two 16-byte static trampolines. Runtime validation is Pending. Detailed evidence is canonical in [Toasty visual research](Toasty-Visual-Research).
- **Cross-stage items:** a logical selector is not proof of free physical storage. Production integration must preserve explicit resource ownership, bounded allocation, deduplication, and destination-safe award semantics.

## Explicit exclusions and non-blockers

- Enemy randomization and Reverse Elbow / foreign-move completion are **not 1.0 blockers**.
- Bosses and scripted encounters are not ordinary-enemy entries.
- The Temple Map is not one of the 84 ordinary pickup records; its 1.0 inclusion policy is still explicit Pending work.
- Zero/unused-looking resource selectors are not automatically free physical storage.
- PS1 addresses and platform behavior do not transfer to N64 without demonstrated compatibility.
- Disposable proof ROM patches, proof caves, and archive handoffs are not silently part of the production pipeline.
- Runtime confirmation is always limited to the documented route; CI/static success does not imply exhaustive gameplay validation.
