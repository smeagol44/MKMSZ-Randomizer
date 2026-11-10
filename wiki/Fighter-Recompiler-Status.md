# Fighter recompiler — status

> **Scope:** living progress page for the fixed [Fighter recompiler plan](Fighter-Recompiler-Plan). It records the current milestone, the task list and acceptance checklist agreed when each milestone starts, debt, owner decisions and baseline identities. Update it in the same PR as the work it records. The plan itself is not edited here.

## Current milestone

**Milestone 1 — Fighter description and generic body builder.** In progress (started 2026-11-10).

### Milestone 1 — agreed tasks (owner, 2026-11-10)

1. Inventory every Sektor-specific item and classify it — **done**: [Fighter recompiler inventory](Fighter-Recompiler-Inventory).
2. Fighter description format (body part), JSON with a validator; descriptions for Sektor and Reptile — **done** (`fighter_import/description.py`, `src/mkmszr/fighters/*.json`).
3. Generic body builder: split `sektor_build.py` into a generic builder plus Sektor's description, leaving the frozen move code untouched; only frames used by mapped animations and declared extras are imported — **done** (`fighter_import/body_build.py`; Sektor's accepted layout is data in `sektor.json` `body.layout`).
4. Codec 23 and a roster-wide decode test — pending (PR 3).
5. Size report and Reptile's body built statically, with the colour method `auto` — pending (PR 3).

### Milestone 1 — acceptance checklist

- [x] The inventory classifies every item; nothing is "unknown".
- [x] The validator accepts Sektor's and Reptile's descriptions and rejects broken ones (`tests/test_fighter_description.py`).
- [x] The generic builder plus Sektor's description reproduces the pinned Sektor build byte for byte (`ad2ceb4b…ed86`; `tests/test_fighter_swap.py`).
- [x] A test checks that no Sektor-only constant from the inventory remains in the generic builder (`tests/test_fighter_body_build.py`).
- [ ] The roster-wide decode test passes, or its documented exceptions are listed.
- [ ] Reptile's body builds; the size report says whether he fits, and if not, by how much and what would be trimmed (owner decision).
- [ ] Full suite passes, Sektor's pinned outputs are unchanged, and this page is updated in the same PR.

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
| 1 Fighter description and generic body builder | In progress | See above | PR 1 (#197): inventory and description format; PR 2: generic body builder |
| 2 Component library and MKMSZ backend v1 | Not started | — | — |
| 3 Reading aid for MKT moves | Not started | — | — |
| 4 Reptile | Not started | — | — |
| 5 Generic product integration | Not started | — | — |
| 6 Review and next fighters | Not started | — | — |

## Debt

Fighter- or move-specific code outside fighter descriptions and components (plan rule 3). At plan start: everything Sektor-specific in `fighter_import/` (including `sektor_build.py` and `actions/robo_*`, frozen legacy under rule 4) and `patches/fighter_swap.py`; milestone 1 itemises it.

## Owner decisions

- 2026-11-10: next fighter is **Reptile**. Owner's expectation for his specials (to verify in milestones 2–4):
  - acid spit is a normal projectile (data on the generic projectile);
  - forceballs work like MKMSZ Quan Chi's, possibly with the same visual effects and sprites;
  - invisibility copies the Eye item's effect;
  - slide is Sub-Zero's;
  - the elbow dash is the only fully new move.
- 2026-11-10: automatic recognition of MKT machine code is deferred to milestone 6; Sektor's move modules are frozen legacy.
