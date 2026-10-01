# N64 -> PS1 port planning and strategy

> **Purpose:** standing execution guide for a future PlayStation port of MKMSZR after the Nintendo 64 1.0 product is complete and has no pending release work.
>
> This page owns **port strategy, phase order, experiments, and exit gates**. It does not replace [PlayStation research](PS1-Research) for PS1 facts or [N64–PS1 comparison](N64-PS1-Comparison) for transfer limits.

## Core rule

**Transfer contracts and semantics; re-prove addresses, resources, memory ownership, lifecycle hooks, and runtime composition.**

The PS1 port is a platform implementation of an already-defined randomizer, not a second round of randomizer product design.

Portable examples:

- logical check/reward model;
- deterministic seed namespaces and retry policy;
- solver/access/completion rules;
- progression modes and constraints;
- Temple scripted-check semantics;
- inventory/lifecycle expectations;
- HUD information requirements;
- user-facing configuration and product behavior.

Platform-specific examples that must be re-established on PS1:

- executable and overlay addresses;
- patch sites and displaced instructions;
- resource/file identities and residency;
- safe executable/data allocation;
- runtime loader/injection mechanism;
- save/disc handling;
- graphics/audio formats and render hooks;
- control/action hooks;
- checksum/rebuild behavior.

## Standard per-feature workflow

For almost every ported subsystem, use the same bounded loop:

**Static mapping -> smallest guarded proof -> bounded manual runtime test -> document evidence -> production integration -> CI/composition check.**

Do not promote a PS1 implementation merely because its N64 equivalent is Runtime-confirmed.

---

## Phase 0 — Freeze the N64 1.0 contract

Before PS1 implementation begins, capture the final N64 1.0 behavior as platform-independent requirements.

Separate:

- what the product must do;
- what the N64 implementation happens to do.

The PS1 port should target the same product contract unless a later explicit PS1-specific product decision changes it.

**Exit gate:** every 1.0 feature can be described without depending on an N64 address, file ID, cave, KSEG rule, or N64-only storage mechanism.

---

## Phase 1 — Establish the PS1 target and build pipeline

Create safe PS1 build infrastructure before gameplay patches.

Tasks:

- lock the supported disc/executable revision and hashes;
- preserve clean inputs and generate disposable outputs only;
- implement guarded executable/resource writes;
- establish deterministic disc/file rebuilding;
- verify any required PS1 executable/disc metadata handling;
- create PS1-specific address/resource/allocation registries from the start.

Initial tests:

1. deterministic no-op rebuild;
2. one guarded data edit;
3. boot the rebuilt image;
4. verify the clean source remains unchanged;
5. reject unsupported input revisions before mutation.

**Exit gate:** supported PS1 images can be rebuilt reproducibly and safely.

---

## Phase 2 — Platform bring-up

Establish the minimum native PS1 substrate before porting higher-level systems.

Start with the already-mapped targets in [PlayStation research](PS1-Research):

1. guarded stage-selector activation;
2. safe eight-stage selector mapping;
3. runtime observation of stage/overlay memory;
4. one same-stage Fire enemy substitution;
5. one ordinary pickup/resource substitution;
6. one small native code-execution proof;
7. one persistent-state proof.

A major goal of this phase is to establish **production-safe executable/data storage**. The apparent RAM below the PS1 stack is not assumed free.

**Exit gate:** reliable PS1 native execution, known memory ownership, and a persistent runtime/state mechanism across the lifecycle boundaries required by the product.

---

## Phase 3 — Build authoritative PS1 catalogs

Use N64 findings as search signatures and semantic hypotheses, never as address truth.

Verify and catalog:

- all 84 ordinary pickup locations and callbacks;
- item IDs and special/key families;
- stage identities and resource ownership;
- scripted/special checks such as the Temple location;
- boss reward locations;
- ordinary enemy streams and preserved encounters;
- relevant native functions for inventory, progression, UI, save, controls, and stage flow.

Record shared lineage explicitly where demonstrated, and record PS1 divergence where it exists.

**Exit gate:** every 1.0 object the randomizer may manipulate has a stable PS1 identity and technical owner.

---

## Phase 4 — Port core run-state and lifecycle systems

Port persistence before global randomization.

Recommended order:

1. ordinary-pickup collected-state persistence;
2. inventory persistence/expansion;
3. stage-local key masking or PS1-equivalent handling;
4. Temple scripted special-check persistence;
5. XP/progression state;
6. HP/lives/continues lifecycle;
7. Game Over/new-run reset;
8. enforced difficulty invariant.

The existing PS1 save-format research should inform this work, but the implementation must follow PS1 lifecycle behavior rather than reproduce the N64 mechanism mechanically.

For each subsystem, test the relevant title, stage transition, death/checkpoint, save/load, and new-run boundaries.

**Exit gate:** PS1 run state obeys the same player-visible lifecycle contract as N64 1.0.

---

## Phase 5 — Build the PS1 item materializer

Keep the final N64 architectural separation:

**logical reward != physical location != location-owned stage effect != visual/resource materialization.**

Progress from small to broad proofs:

1. same-stage ordinary replacement;
2. representative cross-stage ordinary item;
3. key/special reward;
4. Temple scripted special check;
5. boss reward location;
6. worst-stage resource/capacity stress tests.

Do not copy N64 resource-slot/file assumptions. Build PS1-specific residency, allocation, visual, and callback rules.

Generation must fail closed when a reward cannot be materialized safely.

**Exit gate:** every item family required by the final logical pool has a bounded PS1 materialization route or an explicit generation rejection rule.

---

## Phase 6 — Reuse the global generator and solver

Only connect global generation after PS1 materialization rules are stable.

Prefer shared platform-independent code for:

- logical check/reward assignment;
- deterministic RNG namespaces;
- deterministic retry attempts;
- progression constraints;
- required-Power-Upgrades modes;
- optional power-order rules;
- fixed-point access/solvability validation;
- final completion predicate.

The PS1 backend should consume the logical layout and materialize it using PS1-specific catalogs/resources.

Run large deterministic static seed sweeps before full runtime-seed testing.

**Exit gate:** identical PS1 inputs/configuration produce the same accepted logical layout and solver result, and unsupported layouts fail deterministically.

---

## Phase 7 — Port player-facing 1.0 systems

Once the run itself is correct, port presentation and controls.

Target the finalized product behavior for:

- native randomizer HUD;
- inventory/box indicator and navigation;
- GAME SETTINGS;
- Modern ATTACK / SPECIALS / JUMP / RUN;
- safe stage-selector presentation;
- title/legal branding;
- outfit recoloring/rainbow where viable;
- other finalized N64 1.0 presentation behavior.

For controls, port **semantics**, not N64 hook addresses. Find PS1 input/action owners independently.

**Exit gate:** PS1 exposes the same required player-facing 1.0 behavior even where its implementation differs internally.

---

## Phase 8 — Whole-game PS1 validation

Move from subsystem proofs to actual product validation.

Use several deliberately chosen seeds plus at least one ordinary representative seed.

Exercise:

- all eight main stages;
- cross-stage randomized items;
- progression and required-power settings;
- deaths/checkpoints;
- inventory switching;
- title/re-entry;
- save/load;
- Game Over/new run;
- Temple scripted check;
- final completion.

Keep evidence categories separate:

- static/CI coverage;
- bounded subsystem Runtime-confirmed proofs;
- representative full-seed Runtime-confirmed integration.

**Exit gate:** a supported clean PS1 image can produce and complete a deterministic validated run through the normal product pipeline.

---

## Phase 9 — Productize the PS1 backend

Expose PS1 to users only after the gameplay pipeline is stable.

Architecture goal:

- shared configuration/generator/solver where semantics are genuinely common;
- separate N64 and PS1 patch/materialization backends;
- no broad platform-conditionals scattered through unrelated common code.

Add:

- PS1 input validation and errors;
- ISO/disc rebuild output;
- browser and CLI target selection;
- PS1-specific tests/fixtures;
- documentation and deployment.

**Exit gate:** browser and CLI produce byte-identical PS1 output for the same supported input and configuration.

---

## Phase 10 — Port post-1.0 and advanced features

Treat advanced features as new PS1 research tracks even when an N64 implementation exists.

Examples:

- ordinary-enemy randomization/materialization;
- donor-backed audio and Toasty equivalents;
- advanced presentation;
- MKT fighter import / Sektor;
- donor special moves and compatibility-layer work.

High-level planners or semantic mappings may transfer. Asset formats, loaders, callbacks, render ownership, memory lifetime, and runtime composition must be independently proven.

---

## Port-order summary

| Phase | Goal | Main gate |
|---:|---|---|
| 0 | Freeze portable 1.0 behavior | Platform-independent contract |
| 1 | Safe PS1 builder | Deterministic guarded rebuild |
| 2 | Native PS1 substrate | Code execution + safe persistent state |
| 3 | PS1 catalogs | Stable identities/owners |
| 4 | Run-state lifecycle | Persistence/reset parity |
| 5 | Item materializer | Destination-safe item families |
| 6 | Global generator/solver | Deterministic solvable layouts |
| 7 | UI/controls/presentation | Player-facing feature parity |
| 8 | Full runtime validation | Completable representative seeds |
| 9 | Product/web/CLI | Normal supported PS1 pipeline |
| 10 | Advanced/post-1.0 | Feature-specific PS1 research |

## Standing safety rules

- Never transplant N64 addresses, file IDs, allocation claims, or checksum logic directly.
- Do not infer free RAM or free disc/resource space from padding or apparent gaps.
- Preserve clean PS1 source images and produce disposable outputs.
- Guard every production edit with expected source data/instructions.
- Keep PS1 evidence labels independent from N64 evidence.
- Do not treat one stage/seed/item/enemy proof as universal coverage.
- Prefer the smallest proof that answers one platform question.
- Update the PS1 owner pages and registries whenever verified findings materially change the port model.
- Do not let early PS1 diagnostic shortcuts redefine the finalized N64 1.0 product contract.

## Starting references

When the port begins, read in this order:

1. [Project status](Project-Status) — confirm N64 1.0 is complete and PS1 work is now active.
2. [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) — frozen product behavior being ported.
3. [PlayStation research](PS1-Research) — current PS1 technical facts.
4. [N64–PS1 comparison](N64-PS1-Comparison) — what transfers conceptually and what does not.
5. This page — phase order and gates.
6. The relevant subsystem owner for the feature currently being ported.

Until N64 1.0 is complete, this page is a **future execution guide**, not the current Project Status priority order.
