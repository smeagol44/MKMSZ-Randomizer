# Fighter recompiler — master plan

> **This page is fixed.** It was agreed with the project owner on 2026-11-10 and is the plan, the guide and the starting point for all MKT → MKMSZ fighter work. **Do not edit it.** The only permitted change is appending a line to [Referenced pages](#referenced-pages) when a new related page is created.
>
> - **Progress** (current step, acceptance checklist, debt) lives on [Fighter recompiler status](Fighter-Recompiler-Status), never here.
> - **A change to the plan** needs the owner's explicit approval and is written as a new page `Fighter-Recompiler-Amendment-NN` (what changes, why, the owner's decision, the date). It is then referenced here. Amendments override the parts of this page they name; everything else stays as written.
> - If a task does not belong to a step below, it is out of plan: stop and ask the owner before doing it.

## 1. Purpose and the problem this plan fixes

The goal is a **fighter recompiler**: it reads a fighter from *Mortal Kombat Trilogy* (MKT, N64 USA Rev. 2) and produces that fighter for *Mortal Kombat Mythologies: Sub-Zero* (MKMSZ, N64 USA Rev. 0). It covers body, animations, sounds, presentation and special moves. Sektor is the first fighter and the test case. The tool is meant to bring any MKT fighter, not to hand-build Sektor.

As of 2026-11-10 that goal has been reached for **data** but not for **moves**:

- Graphics, palettes, sounds and animation scripts are decoded and translated by rules. The generic animations (slide, death, falling to death, pickup, grabbed) work for any imported fighter.
- Every special move is a hand-written module. The straight rocket is word patches on a copy of Sub-Zero's Ice Blast code. The whole Sektor build is one fighter-specific script (`fighter_import/sektor_build.py`).

The work drifted toward "make Sektor work" more than once. This plan fixes the architecture, the order of work and the definition of done, so that each step moves the tool forward and not just Sektor.

## 2. Architecture (fixed)

```text
MKT ROM ──► MKT frontend ──► Fighter description ──► MKMSZ backend ──► MKMSZ ROM
            (reads data and      (engine-neutral:          (emits MKMSZ
             recognises move      fighter spec +            assets, scripts,
             machine code)        move programs made of     code, patches)
                                  micro-components)
```

- **Micro-component library (the middle).** An engine-neutral vocabulary for what a fighter does: play an animation, wait, play a sound, set velocity and gravity, face the target, hide/show, spawn a projectile, strike with a box/damage/reaction, wait until landed/contact/timeout, branch on contact, and so on. Algorithms that are not plain call sequences (homing steering, for example) are components of their own, with parameters. Components carry **no** MKT or MKMSZ addresses, registers, tick rates or units.
- **Fighter description.** One data file per fighter: the fighter spec (donor identity, body slot mapping, palette policy, sounds, presentation, progression) plus one **move program** per special move, made only of components. It is data, not code: it is serialisable and checked against a schema.
- **MKT frontend.** Reads MKT data (images, palettes, scripts, sounds, command records) and **recognises MKT special-move machine code**. It follows calls to MKT engine routines and constants, and turns them into a move program. When it meets something it does not recognise, it stops with a report naming it. It never guesses.
- **MKMSZ backend.** Lowers each component to MKMSZ code and data (reusing today's host primitives). It assembles the fighter file and the move payload, and produces the guarded ROM edits for the production patch.
- **The reverse direction** (MKMSZ → MKT) is out of scope.

## 3. Rules that hold for every step

1. **One step at a time, in order,** except where a step says it may run in parallel. A step is done only when all its acceptance criteria are met and recorded on the status page.
2. **No fighter-specific or move-specific code** outside fighter descriptions and the component library, once step 6 is done. Before that, any new fighter- or move-specific code is listed on the status page as **debt**, with the step that removes it.
3. **New behaviour enters as a component,** never as a one-off patch. A component is added once and reused by every fighter.
4. **Hand-written move programs are allowed only as data** (a move program written by a person when the frontend cannot yet recognise a move). Each is recorded as frontend debt; the goal is zero.
5. **Sektor is the regression gate.** Every step keeps Sektor's output identical or, where a step allows a difference, documents and tests it. Sektor's accepted runtime behaviour (the Runtime-confirmed composition proofs and production builds) must not regress.
6. **Project rules still apply.** These are [AGENTS.md](https://github.com/smeagol44/MKMSZ-Randomizer/blob/main/AGENTS.md): evidence labels, ROM safety, guarded patches, smallest proof before integration, user runtime validation, one PR per task with its Wiki update. A runtime gate is passed only by the owner's observation.
7. **The status page is updated in the same PR** as the work it records.

## 4. Steps

Each step lists its goal, the work, the deliverables and the **acceptance criteria (AC)**. "ROM-backed test" means a test that runs when `MKMSZR_CLEAN_ROM` / `MKMSZR_MKT_ROM` are set (CI has no ROMs).

### Step 0 — Baseline and inventory

**Goal.** Know exactly what exists and pin it, so later steps can prove they did not break it.

**Work.**
- Pin current outputs with ROM-backed tests: Sektor build hash, CLI `--fighter sektor` hash, web/CLI parity (most already exist).
- Inventory every fighter-specific and move-specific item in `src/mkmszr/fighter_import/` (including `sektor_build.py` and `actions/`) and `src/mkmszr/patches/fighter_swap.py`. That means constants, slot tables, hardcoded MKT offsets, MKMSZ addresses and word patches. Classify each as **(a)** fighter data (belongs in the fighter spec), **(b)** a component or backend concern, **(c)** an MKT-frontend concern (an MKT engine fact), or **(d)** obsolete.
- Inventory the MKT engine routines Sektor's moves call (address, name if known, arguments, effect).

**Deliverables.** The inventory on a new page `Fighter-Recompiler-Inventory`. Baseline hashes on the status page.

**AC.**
- Every item in the listed files is classified; nothing is left "unknown".
- ROM-backed tests pin the Sektor build and the CLI build; the full suite passes.
- No behaviour change: all pinned hashes are unchanged by this step.

### Step 1 — Component library and fighter-description format

**Goal.** Define the middle layer before writing more code around it.

**Work.**
- Define each micro-component: name, meaning, parameters, **engine-neutral units**, preconditions, effects, and how it ends (normally, on contact, on timeout, when interrupted). Units must be exact, deterministic and anchored on documented semantic calibrations (as `physics.py` anchors motion on the standard jump), never on one engine's tick rate.
- Define the move-program structure: a sequence with branches, loops and waits over components, plus the move's input command, condition and cost.
- Define the fighter-spec schema: donor identity, body slot mapping, frame policy (colour depth, palette normalisation), common-animation recipes, sounds and voice mapping, presentation (move names, help text, icons, outfit recolour entries), progression (tiers, costs, removed powers), move list.
- Write a reference interpreter in Python that runs a move program abstractly (time, positions, events), for tests.
- Express **Sektor's four moves and Reptile's specials** in this format on paper (as data), to prove the vocabulary is enough. Do this before any backend or frontend code.

**Deliverables.** A new page `Fighter-Recompiler-Components` (the component catalogue). Schema and validator in code. The Sektor and Reptile move programs as draft data.

**AC.**
- Every component has a complete catalogue entry; no MKT or MKMSZ address, register or tick rate appears in any component definition.
- Sektor's teleport, straight missile, double missile, homing missile and throw, and every Reptile special, are expressible as move programs. Any gap is a listed new component, not a workaround.
- The schema validator accepts the Sektor spec and rejects malformed specs (tests).
- The reference interpreter runs the Sektor move programs and its tests pass.
- Owner review of the component catalogue before step 3 starts.

### Step 2 — Generic body and asset builder

**Goal.** Replace the Sektor-only build with a builder driven by the fighter spec. May run in parallel with step 1.

**Work.**
- Split `sektor_build.py` into a generic `fighter_build(spec, clean ROM, MKT ROM)` and Sektor's spec. Generic code covers:
  - frame selection from the slot mapping;
  - decoding every MKT image codec the roster uses, including codec 23 and the male-ninja heap;
  - colour normalisation;
  - Type-5 encoding and packing within the fighter-file budget;
  - script translation;
  - the common-animation recipes;
  - sounds;
  - the relocation/loader layout.
- Move every Sektor-only choice into Sektor's spec. Examples: the Run poses, the arm composite and the palette map.
- Report the fighter-file budget per fighter (used, free) and fail clearly when a fighter does not fit.

**AC.**
- `fighter_build(Sektor spec)` reproduces the current Sektor build **byte for byte** (the pinned hash).
- No Sektor or robot constant remains in generic code. A test scans for the inventory's Sektor items.
- Every frame of every MKT fighter heap decodes without error (ROM-backed test), or the exceptions are listed as known non-image data with evidence.
- The body build for at least one more fighter (Reptile) completes and reports its budget (static only; no runtime claim).

### Step 3 — MKMSZ backend

**Goal.** Compile move programs to MKMSZ.

**Work.**
- Implement the lowering of every catalogue component to MKMSZ code and data, reusing and absorbing today's host primitives (`host.py`, `projectile.py`, `effects.py`, `physics.py`, `relocate.py`, `lifter.py` where still needed).
- Lower move programs to an assembled payload, command records, conditions and costs.
- The stock Ice root must not be patched for imported moves: projectiles are built from projectile components, not from Ice Blast copies.

**AC.**
- Each component has a unit test of its lowering (assembled words or emulated behaviour with `tests/mips_eval`).
- The teleport move program compiles byte for byte to today's Runtime-confirmed teleport, or every difference is explained and tested.
- The straight-missile program compiles without any word patch on a copy of Sub-Zero's Ice code. Its behaviour against today's accepted missile (speed table, strike, smoke, explosion, palette, sounds) is documented, and it passes a bounded owner runtime test.

### Step 4 — MKT frontend (move recognition)

**Goal.** Turn MKT special-move machine code into move programs.

**Work.**
- Catalogue the MKT engine routines and data the specials use: a donor function registry with names, arguments and effects. It is seeded from step 0 and from the arcade-source lineage where it matches the retail N64 code.
- Starting from each command record's action, decode the MKT routine. Follow calls and propagate constants into arguments. Recognise engine calls, loops, waits, branches on contact or timeout, and spawned child processes, then emit components.
- Unknown routine or pattern: stop with a report (address, context, what is missing).
- Produce a coverage report for all MKT fighters: per special, recognised fully, partly (with the missing items) or not at all.

**AC.**
- For Sektor's moves, the frontend output equals the step-1 move programs (or the differences are reviewed and the step-1 programs corrected with evidence).
- No guessing: a ROM-backed test shows that an unknown routine produces an error report, not a program.
- The roster coverage report is generated by a script and recorded on the status page.

### Step 5 — Generic presentation and progression

**Goal.** Presentation and progression come from the fighter spec. May run in parallel with steps 3–4.

**Work.**
- Generate the Power Ups help text from the spec (move names, commands, descriptions within the native character set and line limits).
- Generate the icons from donor art per a spec policy.
- Generate the outfit recolour entries from palette analysis or spec data.
- Map tiers and costs onto the host Power Up slots with the shuffle-safe gate rules.
- Generate the production patch's guarded edits from the build manifest, not from hardcoded lists. This covers the transplant classification and the R4 stock edits.
- Drive the web "Swap character" window's selectable fighters from the available, valid fighter specs.

**AC.**
- Sektor's accepted presentation and progression come out identical from his spec.
- `patches/fighter_swap.py` contains no Sektor constant (test).
- A new valid fighter spec becomes selectable in the web window with no web code change (test).

### Step 6 — Sektor through the whole pipeline

**Goal.** Sektor is built only from MKT ROM → frontend → fighter description → backend. Nothing is hand-written.

**Work.**
- Build Sektor's moves from the frontend output; remove `fighter_import/actions/robo_*` and every other hand-written move module.
- Retire the proof-era paths the inventory marked obsolete.

**AC.**
- No hand-written move module remains (test on the package contents). Any hand-written move program left is listed as frontend debt.
- Owner runtime retest, bounded, of every Sektor move, the throw, tiers and costs, presentation, pickup and grabbed poses: accepted. Differences from the previous build are documented with the owner's acceptance.
- CLI and web builds match; the full suite passes.

### Step 7 — Reptile, the first new fighter

**Goal.** Prove the tool brings a new fighter without fighter-specific code.

**Work.** Write Reptile's fighter spec (data only), then:
1. **Body** first: slot mapping, palette, sounds, common animations; with the owner's decision on what happens to Sub-Zero's specials.
2. Then each special from the frontend; any missing behaviour is added as a component (step 1 catalogue update, step 3 lowering, step 4 recognition), never as Reptile code.
3. Then presentation and progression from the spec.

**AC.**
- Reptile adds no code outside his spec and new reusable components (review plus test).
- Owner runtime acceptance, bounded: body; then each special; then a full-seed run with Reptile.
- Sektor regression: unchanged or explained and re-accepted.

### Step 8 — Roster coverage (ongoing)

**Goal.** Grow coverage by components, not by fighters.

**Work.** Keep the roster coverage report current. Pick the next components by how many fighters they unlock. Add fighters when their report is complete, each with its own owner runtime acceptance.

**AC (per fighter).** As step 7.

## 5. How to resume in a new conversation

1. Read this page, then [Fighter recompiler status](Fighter-Recompiler-Status) (current step, open AC, debt), then [Project status](Project-Status).
2. Continue the current step only. If the owner asks for something outside the plan, say so and propose an amendment page instead of doing it silently.
3. Domain facts live on the owner pages (below). This plan does not duplicate them.

## 6. Domain owners used by this plan

- [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer) — porting contract and Sektor production integration.
- [MKT adapter primitives](MKT-Adapter-Primitives) — donor behaviour, script grammar translation, known missing generic adapters.
- [MKT fighter asset translation](MKT-Fighter-Asset-Translation) — donor codecs, frames, palettes, packing.
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) — host slot semantics and generic animation recipes.
- [Player actions and special moves](Player-Actions-and-Special-Moves) — MKMSZ host action ABI.
- [Sektor takeover proof history](Sektor-Takeover-Proof-History) — Sektor chronology.
- [Web patcher and product](Web-Patcher-and-Product) — the fighter option and the "Swap character" window.

## Referenced pages

Append-only. Add one line per new page related to this plan (inventory, component catalogue, amendments, …).

- [Fighter recompiler status](Fighter-Recompiler-Status) — living progress page (2026-11-10).
