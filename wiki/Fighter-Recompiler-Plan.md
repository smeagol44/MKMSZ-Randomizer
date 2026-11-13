# Fighter recompiler — master plan

> **This page is fixed.** It was agreed with the project owner on 2026-11-10 and is the charter, the guide and the starting point for all MKT → MKMSZ fighter work. **Do not edit it.** The only permitted change is appending a line to [Referenced pages](#referenced-pages) when a new related page is created.
>
> - **Progress** (current milestone, its agreed task list and acceptance checklist, debt, owner decisions) lives on [Fighter recompiler status](Fighter-Recompiler-Status), never here.
> - **A change to this charter** needs the owner's explicit approval and is written as a new page `Fighter-Recompiler-Amendment-NN` (what changes, why, the owner's decision, the date), then referenced here. An amendment overrides only the parts it names.
> - **Work that does not belong to a milestone below is out of plan:** stop and ask the owner before doing it.

## 1. Purpose

Build a **fighter recompiler**: a tool that brings a fighter from *Mortal Kombat Trilogy* (MKT, N64 USA Rev. 2) into *Mortal Kombat Mythologies: Sub-Zero* (MKMSZ, N64 USA Rev. 0). That means body, animations, sounds, presentation, progression and special moves. Sektor was the first fighter and is now the regression test. **Reptile is the next fighter and the proof that the tool is general.**

Starting point (2026-11-10):
- **Data is already rule-based.** Graphics, palettes, sounds and animation scripts are decoded and translated by rules. The generic animations (slide, death, falling to death, pickup, grabbed) work for any imported fighter.
- **The fighter build is Sektor-only.** `fighter_import/sektor_build.py` is one fighter-specific script.
- **Every special move is a hand-written module.** The straight rocket is word patches on a copy of Sub-Zero's Ice Blast code.

The work drifted toward "make Sektor work" more than once. This charter fixes the architecture, the principles and the order of work, and keeps each milestone producing something usable.

## 2. Architecture

```text
MKT ROM ──► reading ──► Fighter description ──► MKMSZ backend ──► MKMSZ ROM
           (decoders +    (data only: fighter spec   (emits assets, scripts,
            annotated      + one move program per     code and guarded edits)
            disassembly)   special, made of
                           micro-components)
```

- **Micro-component library (the middle).** Engine-neutral behaviours a move is made of. Examples:
  - play an animation, wait, play a sound;
  - set velocity and gravity, face the target, hide or show;
  - spawn a projectile, strike with a box, damage and reaction;
  - wait until landed, contact or timeout; branch on contact.

  A behaviour that is an algorithm rather than a sequence (homing steering, for example) is a component of its own, with parameters. Components carry no MKT or MKMSZ addresses, registers or tick rates.
- **Fighter description.** One data file per fighter, checked against a schema. It holds the fighter spec (donor identity, body slot mapping, palette policy, sounds, presentation, progression and the owner's design decisions) and one move program per special, made only of components.
- **Reading MKT.** Today's decoders cover data. For special moves, an **annotated-disassembly aid** names the MKT engine routines a move calls, with their arguments. A person (normally the assistant) writes the move program from that, recording which donor address each value came from. Fully automatic recognition of MKT machine code is **not** a goal of this charter; milestone 6 decides whether it is worth building.
- **MKMSZ backend.** Lowers each component to MKMSZ code and data (absorbing today's host primitives), assembles the fighter file and the move payload, and produces the guarded ROM edits.
- **Native reuse.** A component may lower to an MKMSZ behaviour that already exists when it does the same thing: Sub-Zero's slide, an enemy's projectile, an item's effect. Reuse must be established by reverse engineering first, never assumed.
- **Out of scope:** MKMSZ → MKT, and PS1.

## 3. Rules

1. **Milestones in order**, except where a milestone says it may run in parallel. A milestone is done when its done-criteria are met and recorded on the status page.
2. **The milestone's task list and acceptance checklist are agreed with the owner when the milestone starts** and recorded on the status page. This charter fixes only the done-criteria.
3. **New per-fighter content is data** in the fighter description; **new behaviour is a reusable component.** No new fighter-specific or move-specific code modules.
4. **Sektor's existing move modules are frozen legacy:** bug fixes only, no rewrites for purity. A legacy piece is migrated only when a component that replaces it already exists for another reason (for example, Reptile's acid spit producing the generic projectile) and the owner accepts the runtime retest.
5. **Sektor is the regression gate.** Every milestone keeps Sektor's pinned output identical, or documents and tests the difference with the owner's acceptance.
6. **Design decisions are the owner's** (power slots, costs, removals, presentation) and are recorded in the fighter description and on the status page.
7. **Project rules apply** ([AGENTS.md](https://github.com/smeagol44/MKMSZ-Randomizer/blob/main/AGENTS.md)): evidence labels, ROM safety, guarded patches, smallest proof before integration, runtime gates passed only by the owner's observation, one PR per task with its Wiki update. The status page is updated in the same PR.

## 4. Milestones

### Milestone 1 — Fighter description and generic body builder

The biggest single gain: every fighter needs it, and today even the body is Sektor-only.

- Inventory everything Sektor-specific in `fighter_import/` and `patches/fighter_swap.py`, and classify it (fighter data, component or backend, donor fact, obsolete).
- Define the fighter-description schema (body part).
- Split `sektor_build.py` into a generic builder plus Sektor's description.
- Decode every image codec the roster uses (including codec 23 and the male-ninja image bank).
- Report the fighter-file budget per fighter.

**Done when:**
- the generic builder reproduces today's Sektor build **byte for byte**;
- no Sektor constant remains in generic code (test);
- every frame of every MKT fighter decodes, or the exceptions are documented as non-image data;
- Reptile's body builds statically and his budget is known (fits, or what must change).

### Milestone 2 — Component library and MKMSZ backend, version 1

May overlap milestone 1.

- Write the component catalogue (a new page): meaning, parameters, engine-neutral units anchored on documented calibrations, how each component ends, and its MKMSZ lowering.
- Define the move-program format. Build the backend for the components Reptile's specials and Sektor's existing moves need, starting from the code that already exists (teleport building blocks, projectile, effects, physics, sounds).
- Build a **generic projectile** that does not patch Sub-Zero's Ice code.
- Write Reptile's specials and Sektor's moves as move programs (data) to prove the vocabulary covers them.

**Done when:**
- the catalogue is reviewed by the owner;
- every Reptile special and every Sektor move is expressible as a move program, with gaps listed as new components;
- each implemented component has a lowering test;
- the generic projectile is built without Ice-root patches;
- Sektor's pinned output is unchanged.

### Milestone 3 — Reading aid for MKT moves

May run in parallel with milestone 2.

- Build the annotated-disassembly aid: from a command record to the MKT routine, with known engine calls named and their constant arguments resolved.
- Keep a registry of MKT engine routines (address, name, arguments, effect, evidence).
- Agree a provenance convention: every value in a move program cites its donor address.

**Done when:**
- the aid annotates every special of Sektor and Reptile, with unknown calls flagged rather than guessed;
- the registry covers every routine those moves call.

### Milestone 4 — Reptile

The proof that the tool is general.

- Write Reptile's fighter description, with the owner's design decisions (power slots, costs, removals, presentation).
- **Body first** (slot mapping, palette, sounds, common animations), then each special in owner-agreed order. The current expectation (to verify):
  - acid spit — generic projectile, data only;
  - slide — host slide;
  - forceball — native reuse of the MKMSZ Quan Chi projectile if established, else generic projectile;
  - invisibility — native reuse of the Eye item's effect if established;
  - elbow dash — new components, including the no-repel gate.
- Missing behaviour becomes a component, never Reptile-specific code.

**Done when:**
- Reptile adds no code outside his description and reusable components (review and test);
- the owner has accepted at runtime (bounded) the body, each special, and a full-seed run;
- Sektor regression is unchanged, or the difference is explained and re-accepted.

### Milestone 5 — Generic product integration

May run in parallel with milestone 4; must be done before Reptile ships.

- The production patch's guarded edits come from the build manifest, not from hardcoded Sektor lists.
- Presentation is generated from the description: help text, icons, outfit recolour entries, tier and cost mapping.
- The web "Swap character" window lists every valid fighter description.

**Done when:**
- `patches/fighter_swap.py` contains no Sektor constant (test);
- Sektor's accepted presentation comes out identical from his description;
- Reptile is selectable in the web window with no web code change.

### Milestone 6 — Review and next fighters

After Reptile ships, the owner decides on three questions with evidence from two real fighters:
- whether automatic recognition of MKT machine code is worth building;
- which Sektor legacy modules to migrate;
- which fighters come next. Fighters that share images and behaviours with ones already done are the cheaper ones: robots with Sektor, ninjas with Reptile.

The decision is recorded as an amendment page.

## 5. How to resume in a new conversation

1. Read this page, then [Fighter recompiler status](Fighter-Recompiler-Status) (current milestone, agreed tasks, open checklist items, debt, decisions), then [Project status](Project-Status).
2. Continue the current milestone only. If the owner asks for something outside the plan, say so and propose an amendment instead of doing it silently.
3. Domain facts live on the owner pages below; this charter does not duplicate them.

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
- [Fighter recompiler inventory](Fighter-Recompiler-Inventory) — milestone 1 inventory of Sektor-specific items (2026-11-10).
- [Fighter recompiler MKT move readings](Fighter-Recompiler-MKT-Moves) — milestone 3 reading aid, MKT routine registry and the readings of Reptile's and Sektor's specials (2026-11-10).
- [Fighter recompiler components](Fighter-Recompiler-Components) — milestone 2 component catalogue, move-program format and host references (Quan Chi projectile, Eye) (2026-11-11).
- [Fighter recompiler amendment 1](Fighter-Recompiler-Amendment-1) — milestone 6 decisions: Rayden next, his power slots (2026-11-13).
