# Fighter recompiler — status

> **Scope:** living progress page for the fixed [Fighter recompiler plan](Fighter-Recompiler-Plan). It records the current step, each step's acceptance-criteria checklist, debt and baseline identities. Update it in the same PR as the work it records. The plan itself is not edited here.

## Current step

**Step 0 — Baseline and inventory.** Not started (plan agreed 2026-11-10).

## Baseline (2026-11-10, before step 0)

| Item | Identity |
|---|---|
| Sektor build (`fighter_import.sektor_build`, v61, fixed loader `0xA01B30F0`) | SHA-256 `ad2ceb4bfe80b4316338207baf49684d54c0ee7c570534692266c9751a88ed86` |
| CLI `--fighter sektor --seed SEKTOR-PROD-1 --debug-all-keys` | SHA-256 `7fe0ed360472359e28a81447d16b8c57762037e8fb877b71c57db06bd5601bda` |
| Pinned by | `tests/test_fighter_swap.py` (ROM-backed) |

## Step checklists

| Step | Status | AC met | Evidence / PR |
|---|---|---|---|
| 0 Baseline and inventory | Not started | — | — |
| 1 Component library and description format | Not started | — | — |
| 2 Generic body and asset builder | Not started | — | — |
| 3 MKMSZ backend | Not started | — | — |
| 4 MKT frontend | Not started | — | — |
| 5 Generic presentation and progression | Not started | — | — |
| 6 Sektor through the whole pipeline | Not started | — | — |
| 7 Reptile | Not started | — | — |
| 8 Roster coverage | Not started | — | — |

## Debt

Fighter- or move-specific code and hand-written move programs (plan rules 2 and 4). Existing debt at plan start is everything Sektor-specific in `fighter_import/` and `patches/fighter_swap.py`; step 0 itemises it.

## Owner decisions

None recorded yet.
