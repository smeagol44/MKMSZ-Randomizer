# Milestone Timeline

> **Scope:** This page records major project/research milestones only. Current maturity, requirements, and detailed proof chronology belong to their canonical owners.

## 2026-09-17

- Native Sub-Zero palette recoloring runtime-confirmed.
- Persistent 1 KiB MKMSZR arena-prefix reservation runtime-confirmed.
- Preserved Ghidra project established as the supported static workspace.
- Native file-table loading path narrowed toward production use.

## 2026-09-18

- File-ID `0x1B` payload loading and bounded loaded-code execution confirmed.
- Runtime Layout V1 formalized: 0x200 code + 0x200 state.
- Ordinary-pickup persistence generalized to all eight main stages.
- Four-box inventory architecture reached production/runtime-confirmed state.
- Browser patcher/product repository matured.

## 2026-09-19

- Native gameplay HUD geometry and arbitrary text confirmed.
- `BOX n OF 4` and boot branding productionized.
- Seeded 100+ boot-message pool productionized.
- Automatic seed generation and web build-number convention productionized.
- Cross-stage ordinary enemy import runtime-confirmed in Fire.
- MKT Reptile Reverse Elbow architecture mapped deeply enough for a bounded MKMSZ proof design.
- PS1 static resource/fighter/selector work expanded.

## 2026-09-20

- Two post-legal company/logo screens bypassed with one guarded branch; runtime-confirmed.
- Safe Stage Select automatic entry-save prompt bypassed through the game's native one-shot flag; Temple completed and later normal save still occurred.
- Production native stage-local item randomization merged in PR #16; web build **v0.18**.
- Seed `TEST153` runtime-confirmed: Fire's first ordinary pickup became Shield as predicted.
- `TEST153` boot phrase `' OR 1==1 --` rendered correctly.
- GitHub Wiki introduced with automatic repository-to-Wiki synchronization.
- After the final Library-canonical synchronization, the Wiki became the living/current documentation source and the Library became the durable evidence/archive source.
- Runtime-confirmed logo and selector-save bypasses productionized in PR #18; first shipped in web build **v0.20**.
- Temple XP-progression proof runtime-confirmed: combat/kill XP suppressed, combo EXPERIENCE text removed while HITS remains, progression pickups advanced XP 85→258 and unlocked the second move tier, max XP displayed as 20000, and progression pickups remained inventory-free.
- Reverse Elbow v6 established a repeatable non-hanging scheduler/action lifecycle with the corrected player-velocity helper. Later v8 runtime testing did not confirm intended speed, pass-through, or expanded diagnostics.
- Genuine cross-game fighter-sprite transplantation runtime-confirmed: proof v08/A1.7 renders the actual MKT Rev. 2 SCCOMBO10 Reptile/male-ninja frame inside MKMSZ after deterministic descriptor, codec, palette, opacity, and 4-byte CI row-stride conversion; stock Sub-Zero restores cleanly.
- The Wiki was consolidated into a self-contained technical knowledge base with all 84 ordinary pickup records, all eight decoded resource catalogs, and dedicated function, patch-site, memory, structure, failure, and N64/PS1 registries.

## 2026-09-21

- Sektor takeover v58 runtime-confirmed the corrected twelve-pose Run after fixing aligned WIMP source-row pitch.
- v59 runtime-confirmed the completed middle Combo visuals without enlarging the transplanted fighter resource.
- v60 runtime-confirmed the first Scorpion/type-`0x12` alternate palette as the intended yellow/gold Cyrax-style robot on its tested route.
- v61 exposed a donor-to-target reaction-selector incompatibility; v62 translated the affected reaction semantics into MKMSZ-native values and was runtime-confirmed on the tested MKT combo-string route.
- The Sektor line therefore established a reusable distinction between transferable donor assets/semantics and engine-local callback/reaction/control encodings.

## 2026-09-22

- MKT Toasty audio was identified through anchored source-to-retail selector mapping: source/retail slot `0x1B` -> event `0x0160` -> patch 65 -> subpatch 111 -> waveform 77, with the user directly confirming the intended Dan Forden voice.
- Toasty sound proof v03 runtime-confirmed that the accepted donor voice plays correctly through MKMSZ's native audio path on the tested route.
- Toasty visual work runtime-confirmed the gameplay-HUD textured-node path through v08-v10, corrected fixed-slot aliasing in v14, and genuine Toasty CI8 pixels through a dynamic texture slot in v15. v16's genuine-palette binding remained implementation/static-confirmed and pending manual runtime validation.
- The Wiki refactor audit established a one-owner-per-fact migration plan and a small-task execution sequence for separating current truth, requirements, proof chronology, failures, and provenance.

## 2026-09-23

- The Wiki refactor completed the planned ownership splits through Task 22: current status/requirements, memory/allocation, global materialization, HUD/presentation, Toasty audio/visual, MKT adapter/asset translation, Sektor proof history, stage catalogs, failure history, and final navigation now have dedicated owners.
- `Complete-Research-Synthesis.md` was retired in place as a historical/supersession index rather than remaining an alternate current knowledge base.
- The history/provenance layer was reduced to major chronology, archive routing, and bounded supersession context while preserving stable old URLs.

## Related history owners

- [Sektor takeover proof history](Sektor-Takeover-Proof-History) — detailed vNN chronology, identities, allocations, routes, and supersession.
- [Toasty audio research](Toasty-Audio-Research) and [Toasty visual research](Toasty-Visual-Research) — detailed Toasty proof chronologies.
- [Experiments, failures and superseded findings](Experiments-Failures-and-Superseded-Findings) — durable cross-domain rejected/superseded index.
- [Historical artifact index](Library-Artifact-Index) — preserved Library/archive provenance.
- [Project status](Project-Status) — current maturity and priorities, not chronology.