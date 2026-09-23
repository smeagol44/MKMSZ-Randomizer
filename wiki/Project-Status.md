# Project status

Last consolidated: 2026-09-22.

> **Scope:** This page is the current-state dashboard for MKMSZR. It owns production/proof/pending maturity, current blockers, and priority order. It does **not** own full 1.0 requirements or long proof chronology.
>
> Canonical release requirements and acceptance gates: [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap). Detailed runtime evidence: [Runtime validation status](Runtime-Validation-Status). Detailed mechanisms and proof histories remain on their owning domain pages.
>
> Evidence labels retain the project meanings defined on [Home](Home) and [Research workflow](Research-Workflow): **Runtime-confirmed**, **Static-confirmed**, **Implementation/CI-confirmed**, **Hypothesis / strong inference**, **Rejected / failed**, and **Pending**.

## Production systems

| System | Product state | Current evidence / limit |
|---|---|---|
| Clean-ROM validation, guarded patching, separate output, N64 checksum update | **Production** | Implementation/CI-confirmed for the supported USA Rev. 0 ROM; output is separate from the clean input |
| Compact eight-stage selector | **Production** | Runtime-confirmed A-button route across all eight safe stages; unsafe stock entries are excluded |
| 1 KiB runtime reservation and native payload | **Production** | Runtime-confirmed load/execute path with guarded bounds and CI coverage |
| Ordinary-pickup persistence | **Production beta** | Representative Runtime-confirmed collection/restoration in all eight main stages; all 84 ordinary records are statically cataloged, not individually runtime-exhausted |
| Stage-local seeded pickup randomization | **Production beta** | All 84 ordinary records implemented; deterministic generation/access checks are Implementation/CI-confirmed; this is an interim stage-local mode, not the 1.0 global model |
| Pickup-driven XP progression | **Production beta** | Diagnostic B behavior is Runtime-confirmed through XP 85/258, Temple -> Wind, and title -> Fire. Stage entry restores XP but does not call the tier evaluator; full nine-tier runtime coverage remains Pending. See [XP and progression](XP-and-Progression) |
| Four inventory boxes and foreign-key masking | **Production beta** | Runtime-confirmed switching, transition preservation, and stage-local masking on documented routes; Game Over/new-run reset remains Pending |
| Native box indicator | **Production** | Runtime-confirmed `BOX n OF 4` through the native text path; the broader 1.0 randomizer HUD remains Pending. See [Native HUD and UI](Native-HUD-and-UI) |
| Boot branding and seeded phrase | **Production** | Redesigned legal-screen presentation is Runtime-confirmed; seeded phrase uses a separate deterministic namespace |
| Rebranded title screen | **Production beta** | Candidate-B art plus configurable uppercase `<NAME> EDITION` are Runtime-confirmed through the normal production composition. The accepted implementation is data-only; the earlier executable-wrapper allocation is Rejected / failed. See [Presentation and branding](Presentation-and-Branding) |
| Post-legal logo bypass and selector-only save bypass | **Production** | Runtime-confirmed bounded routes; legal text and later/manual saves remain intact |
| Outfit recoloring | **Production** | Runtime-confirmed palette modes; generated from guarded stock TLUT data |
| Browser/CLI shared patch core | **Production beta** | Both surfaces use the same patch core; CI covers build/import composition, but full gameplay behavior remains outside CI |

## Proof-only systems

These results are important feasibility evidence but are **not** normal browser/CLI product features unless stated above.

| Workstream | Current conclusion | Remaining gate / owner |
|---|---|---|
| Cross-stage ordinary-item materialization | **Runtime-confirmed in bounded proofs.** Prison renders and awards five simultaneous imported item visuals while an untouched Herbs control remains correct. External-to-embedded ordinary resource conversion is also Runtime-confirmed. | The pure planner is implemented but pipeline-disconnected. Fortress stress validation and destination-safe key/crystal award handling remain Pending before a guarded production integration proof. See [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |
| Cross-stage enemy import | **Runtime-confirmed proof.** A Temple monk can be imported into Fire and function in combat; a simpler Fire ordinary-enemy substitution also works. | Arbitrary roster/resource compatibility, death/despawn presentation, allocation policy, and deterministic product integration remain Pending. See [Enemy randomization](Enemy-Randomization) |
| MKT fighter / Sektor takeover | **Runtime-confirmed proof line.** Current v62 confirms the tested Sektor MKT combo-string behavior after translating donor reaction semantics to MKMSZ-native selectors. v58 Run and v59 completed combo visuals are also Runtime-confirmed on their bounded routes. | Still proof-only. The v62 standalone combo record uses production-owned bootstrap space and must be reallocated for any integration. Player-victim grab/throw reactions, specials, and rare presentation families remain Pending. See [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping), [Sektor takeover proof history](Sektor-Takeover-Proof-History), and [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer) |
| Toasty audio | **Runtime-confirmed proof.** Sound proof v03 plays the audibly confirmed MKT Toasty voice through MKMSZ's native audio path. | Final product trigger/allocation is Pending. See [Toasty audio research](Toasty-Audio-Research) |
| Toasty visual | **Partial proof.** v15 Runtime-confirms genuine Toasty CI8 pixels through a dynamic gameplay-HUD texture slot; v16 is Implementation/static-confirmed for the genuine palette-selector path and is still Pending manual runtime validation. | Final palette/runtime confirmation and production-safe trigger/composition remain Pending. See [Toasty visual research](Toasty-Visual-Research) |
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
- **Sektor:** v61 is **Rejected / failed** because donor reaction selector `0x02` was reused numerically. v62 changes only the affected reactions to MKMSZ-native semantics and is **Runtime-confirmed** on the tested combo route. Full version chronology is canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).
- **Toasty:** audio identification/playback is Runtime-confirmed in v03. Visual v15 confirms the image/texture path; v16 palette binding is not yet runtime-confirmed. Detailed visual diagnostics are canonical in [Toasty visual research](Toasty-Visual-Research); donor identification and audio proof chronology are canonical in [Toasty audio research](Toasty-Audio-Research), while MKMSZ host mechanics remain in [Audio system](Sounds-and-Music).
- **Cross-stage items:** a logical selector is not proof of free physical storage. Production integration must preserve explicit resource ownership, bounded allocation, deduplication, and destination-safe award semantics.

## Explicit exclusions and non-blockers

- Enemy randomization and Reverse Elbow / foreign-move completion are **not 1.0 blockers**.
- Bosses and scripted encounters are not ordinary-enemy entries.
- The Temple Map is not one of the 84 ordinary pickup records; its 1.0 inclusion policy is still explicit Pending work.
- Zero/unused-looking resource selectors are not automatically free physical storage.
- PS1 addresses and platform behavior do not transfer to N64 without demonstrated compatibility.
- Disposable proof ROM patches, proof caves, and archive handoffs are not silently part of the production pipeline.
- Runtime confirmation is always limited to the documented route; CI/static success does not imply exhaustive gameplay validation.
