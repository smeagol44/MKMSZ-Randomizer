> **Mirror notice:** This Wiki is a navigation-friendly adaptation of MKMSZR documentation. The ChatGPT Library folder `MKMSZR Research` remains the reverse-engineering/research source of truth; this repository remains the implementation/product source of truth. If the Wiki conflicts with an owning source, the owning source wins.

# Research Workflow

## Sources of truth

- **Library: `MKMSZR Research`** — canonical reverse engineering, reports, preserved Ghidra/static-analysis material, catalogs, runtime evidence, RAM diffs, experiments and archives.
- **GitHub: `smeagol44/MKMSZ-Randomizer`** — reusable patch code, CLI, browser frontend, tests, CI, packaging and release-facing docs.
- **This Wiki** — easier navigation and reading. It deliberately duplicates/adapts important material, but is not the canonical research owner.

## Canonical research router

Before new reverse engineering, read:

`MKMSZR Research/START_HERE_MKMSZR_RESEARCH.md`

Then open only the relevant canonical report:

| Topic | Canonical Library report |
|---|---|
| Core runtime, loader, memory, Ghidra | `MKMSZR_CORE_RUNTIME_AND_ADDRESS_DATABASE.md` |
| Stage flow and selector | `MKMSZR_STAGE_FLOW_AND_SELECTOR.md` |
| Pickups and resources | `MKMSZR_PICKUPS_AND_RESOURCE_LOADING.md` |
| Persistence, inventory, lifecycle | `MKMSZR_PERSISTENCE_INVENTORY_AND_LIFECYCLE.md` |
| Native HUD/text/presentation | `MKMSZR_NATIVE_UI_RENDERING_AND_TEXT.md` |
| Enemy randomization | `MKMSZR_ENEMY_RANDOMIZATION.md` |
| PlayStation | `MKMSZR_PS1_RESEARCH.md` |
| Cross-domain synthesis | `06-MKMSZR_COMPLETE_RESEARCH_REPORT.md` |

The complete report is intentionally concise and is not the default starting point.

## Evidence labels

- **Runtime-confirmed** — manually observed on a bounded real game/emulator route.
- **Static-confirmed** — resolved from ROM/Ghidra/source analysis.
- **Implementation/CI-confirmed** — product code/tests establish generator or patch behavior, but game runtime may still be incomplete.
- **Hypothesis / strong inference** — plausible, not promoted.
- **Rejected / failed** — preserved to avoid repeating work.
- **Pending** — unresolved.

## Preserved Ghidra project

- manifest: `MKMSZR Research/05 - Static Analysis/GHIDRA_PROJECT_MANIFEST.md`
- archive: `MKMSZR Research/08 - Archives/MKMSZR-Ghidra-N64-Project-2026-09-17.zip`

Use the preserved analyzed project. Do not rebuild/re-import the ROM unless it is genuinely unusable.

## Preservation rules

- never modify the clean ROM;
- use hash-verified disposable copies;
- guard known patch inputs/ranges;
- recompute N64 CRC1/CRC2;
- do not infer free memory from zero bytes alone;
- keep stage context attached to overlay addresses;
- do not silently erase superseded conclusions;
- do not run emulator automation unless a task explicitly calls for it.
