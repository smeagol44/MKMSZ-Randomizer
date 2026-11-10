# Fighter recompiler — status

> **Scope:** living progress page for the fixed [Fighter recompiler plan](Fighter-Recompiler-Plan). It records the current milestone, the task list and acceptance checklist agreed when each milestone starts, debt, owner decisions and baseline identities. Update it in the same PR as the work it records. The plan itself is not edited here.

## Current milestone

**Milestone 3 — Reading aid for MKT moves** and **milestone 2 — Component library and MKMSZ backend v1**: in progress (started 2026-11-10, run in parallel).

### Milestones 2 and 3 — agreed tasks (owner, 2026-11-10)

Milestone 3:

1. Reading aid: command record → MKT routine → annotated disassembly, with known engine calls named, constant arguments resolved and unknown calls flagged — **done** ([MKT move readings](Fighter-Recompiler-MKT-Moves); `fighter_import/reading.py`, `mipsdis.py`).
2. Registry of the MKT engine routines that Sektor's and Reptile's specials use — **done** (`fighter_import/mkt_registry.py`).
3. Annotated readings of all Reptile specials (acid spit, both forceballs, invisibility, slide, elbow dash) — **done** for the move bodies; Pending: the readers of the invisibility flag and of the slide stamp.

Milestone 2:

4. Component catalogue page: meaning, parameters, neutral units, ending and MKMSZ lowering.
5. RE check of the reuse ideas, both host-side: MKMSZ Quan Chi's forceball and the Eye item's effect for invisibility. Quan Chi's forceball is a **code/gameplay reference** for projectile creation, hit triggers, the launch effect and sound; the assets still come from MKT (owner, 2026-11-10).
6. Move-program format and validator; Reptile's and Sektor's moves written as data; gaps listed.
7. Owner review of the catalogue.
8. Backend v1, starting with the generic projectile (no Ice Blast patching).

### Milestones 2 and 3 — acceptance checklist

- [x] Every special of Sektor and Reptile is read, with unknown calls flagged and nothing guessed (`tests/test_fighter_reading.py`: no unknown calls, ROM-backed).
- [x] The registry covers every routine those moves call.
- [ ] Provenance convention agreed (proposal on [MKT move readings](Fighter-Recompiler-MKT-Moves#provenance-convention-proposal-owner-agreement-pending)).
- [ ] Component catalogue reviewed by the owner.
- [ ] Every Reptile special and every Sektor move expressible as a move program; gaps listed as new components.
- [ ] Each implemented component has a lowering test.
- [ ] Generic projectile built without Ice-root patches.
- [ ] Sektor's pinned outputs unchanged; full suite passes; this page updated in the same PR.

**Milestone 1 — Fighter description and generic body builder: done (2026-11-10).**

### Milestone 1 — agreed tasks (owner, 2026-11-10)

1. Inventory every Sektor-specific item and classify it — **done**: [Fighter recompiler inventory](Fighter-Recompiler-Inventory).
2. Fighter description format (body part), JSON with a validator; descriptions for Sektor and Reptile — **done** (`fighter_import/description.py`, `src/mkmszr/fighters/*.json`).
3. Generic body builder: split `sektor_build.py` into a generic builder plus Sektor's description, leaving the frozen move code untouched; only frames used by mapped animations and declared extras are imported — **done** (`fighter_import/body_build.py`; Sektor's accepted layout is data in `sektor.json` `body.layout`).
4. Codec 23 and a roster-wide decode test — **done** (also codec 16, even-height storage and multi-part records; [findings](MKT-Fighter-Asset-Translation#roster-body-frame-survey-and-palettes-2026-11-10)).
5. Size report and Reptile's body built statically, with the colour method `auto` — **done** (computed layout; Reptile fits with `0x13E88` bytes free for moves).

### Milestone 1 — acceptance checklist

- [x] The inventory classifies every item; nothing is "unknown".
- [x] The validator accepts Sektor's and Reptile's descriptions and rejects broken ones (`tests/test_fighter_description.py`).
- [x] The generic builder plus Sektor's description reproduces the pinned Sektor build byte for byte (`ad2ceb4b…ed86`; `tests/test_fighter_swap.py`).
- [x] A test checks that no Sektor-only constant from the inventory remains in the generic builder (`tests/test_fighter_body_build.py`).
- [x] The roster-wide decode test passes, or its documented exceptions are listed (Sonya slot `0x15` object descriptors; ids 26–30 are not fighters).
- [x] Reptile's body builds; the size report says whether he fits (yes: stock-size file, `0x13E88` bytes free; no trimming needed).
- [x] Full suite passes, Sektor's pinned outputs are unchanged, and this page is updated in the same PR.

PRs: 1 inventory and description format; 2 generic builder; 3 codec 23, roster decode, Reptile body and size report.

## Baseline (2026-11-10)

| Item | Identity |
|---|---|
| Sektor build (`fighter_import.sektor_build`, v61, fixed loader `0xA01B30F0`) | SHA-256 `ad2ceb4bfe80b4316338207baf49684d54c0ee7c570534692266c9751a88ed86` |
| CLI `--fighter sektor --seed SEKTOR-PROD-1 --debug-all-keys` | SHA-256 `7fe0ed360472359e28a81447d16b8c57762037e8fb877b71c57db06bd5601bda` |
| Pinned by | `tests/test_fighter_swap.py` (ROM-backed) |

## Milestones

| Milestone | Status | Agreed tasks / checklist | Evidence / PR |
|---|---|---|---|
| 1 Fighter description and generic body builder | **Done** (2026-11-10) | See above | #197 inventory and format; #198 generic builder; PR 3 roster decode, computed layout, auto colour, Reptile body |
| 2 Component library and MKMSZ backend v1 | In progress | See above | — |
| 3 Reading aid for MKT moves | In progress (tasks 1–3 done) | See above | PR: reading aid, registry, readings |
| 4 Reptile | Not started | — | — |
| 5 Generic product integration | Not started | — | — |
| 6 Review and next fighters | Not started | — | — |

## Debt

Fighter- or move-specific code outside fighter descriptions and components (plan rule 3). At plan start: everything Sektor-specific in `fighter_import/` (including `sektor_build.py` and `actions/robo_*`, frozen legacy under rule 4) and `patches/fighter_swap.py`; milestone 1 itemises it.

## Open items carried forward

- Reptile's body (computed layout, auto colour) is static only; its runtime acceptance is part of milestone 4.
- Codec-16 frames in some fighters' body slots: palette semantics Pending (not needed for Reptile).

## Owner decisions

- 2026-11-10: next fighter is **Reptile**. Owner's expectation for his specials (to verify in milestones 2–4):
  - acid spit is a normal projectile (data on the generic projectile);
  - forceballs work like MKMSZ Quan Chi's, possibly with the same visual effects and sprites;
  - invisibility copies the Eye item's effect;
  - slide is Sub-Zero's;
  - the elbow dash is the only fully new move.
- 2026-11-10: automatic recognition of MKT machine code is deferred to milestone 6; Sektor's move modules are frozen legacy.
- 2026-11-10: MKMSZ Quan Chi's forceball is a code/gameplay reference (projectile creation, hit triggers, launch effect, sound) so the host side is not reinvented; Reptile's forceball art and sounds still come from MKT.
