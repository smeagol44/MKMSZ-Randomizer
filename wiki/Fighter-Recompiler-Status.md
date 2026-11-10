# Fighter recompiler — status

> **Scope:** living progress page for the fixed [Fighter recompiler plan](Fighter-Recompiler-Plan). It records the current milestone, the task list and acceptance checklist agreed when each milestone starts, debt, owner decisions and baseline identities. Update it in the same PR as the work it records. The plan itself is not edited here.

## Current milestone

**Milestone 1 — Fighter description and generic body builder.** Not started (plan agreed 2026-11-10). Its task list and acceptance checklist are agreed with the owner when it starts.

## Baseline (2026-11-10)

| Item | Identity |
|---|---|
| Sektor build (`fighter_import.sektor_build`, v61, fixed loader `0xA01B30F0`) | SHA-256 `ad2ceb4bfe80b4316338207baf49684d54c0ee7c570534692266c9751a88ed86` |
| CLI `--fighter sektor --seed SEKTOR-PROD-1 --debug-all-keys` | SHA-256 `7fe0ed360472359e28a81447d16b8c57762037e8fb877b71c57db06bd5601bda` |
| Pinned by | `tests/test_fighter_swap.py` (ROM-backed) |

## Milestones

| Milestone | Status | Agreed tasks / checklist | Evidence / PR |
|---|---|---|---|
| 1 Fighter description and generic body builder | Not started | — | — |
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
