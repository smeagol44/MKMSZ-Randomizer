> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Research Workflow

## Sources of truth

- **GitHub repository: `smeagol44/MKMSZ-Randomizer`** — implementation/product source of truth: reusable patch code, CLI, browser frontend, tests, CI, packaging, release-facing documentation, and version-controlled Wiki source.
- **This Wiki (`wiki/` + published GitHub Wiki)** — living/current documentation source of truth for project status, synthesized research conclusions, architecture, confirmed addresses, runtime-validation status, milestones, pending work, and research routing.
- **Library: `MKMSZR Research`** — durable research/evidence/archive source of truth: preserved Ghidra analysis, static-analysis exports, catalogs/manifests, screenshots, RAM evidence, experiment logs, handoffs, historical canonical reports, archives, and specialist datasets.

The Wiki is the current synthesis. The Library preserves the evidence and historical research record behind it.

## Research routing

Before new MKMSZR reverse engineering or research:

1. Read [[Research Workflow]].
2. Read [[Project Status]].
3. Read only the relevant owning Wiki topic page.
4. Then consult only the Library reports/evidence/static-analysis artifacts referenced by that topic or otherwise necessary.

Do **not** read the whole Library by default and do not repeat completed research.

Owning Wiki topics:

| Topic | Current Wiki owner | Library evidence / historical report |
|---|---|---|
| Core runtime, loader, memory, Ghidra | [[Core Runtime and Address Database]] | `MKMSZR_CORE_RUNTIME_AND_ADDRESS_DATABASE.md` |
| Stage flow and selector | [[Stage Flow and Selector]] | `MKMSZR_STAGE_FLOW_AND_SELECTOR.md` |
| Pickups/resources/randomization | [[Pickups and Item Randomization]] | `MKMSZR_PICKUPS_AND_RESOURCE_LOADING.md` + Stage Catalogs |
| Persistence/inventory/lifecycle | [[Persistence Inventory and Lifecycle]] | `MKMSZR_PERSISTENCE_INVENTORY_AND_LIFECYCLE.md` |
| Native HUD/text/presentation | [[Native UI and Presentation]] | `MKMSZR_NATIVE_UI_RENDERING_AND_TEXT.md` |
| Enemy randomization | [[Enemy Randomization]] | `MKMSZR_ENEMY_RANDOMIZATION.md` |
| PlayStation | [[PS1 Research]] | `MKMSZR_PS1_RESEARCH.md` |
| Cross-project synthesis | [[Complete Research Synthesis]] | `06-MKMSZR_COMPLETE_RESEARCH_REPORT.md` |

## Documentation cutover note

The Library's `START_HERE_MKMSZR_RESEARCH.md` and historical canonical reports were the project router/current documentation owners before the 2026-09-20 Wiki cutover. Their evidence and historical conclusions remain valuable, but any governance wording saying that the Library itself is still the current canonical documentation owner is now **superseded by the project instructions and this Wiki**.

Do not rewrite archival history merely to erase that earlier workflow. Use the Wiki for current conclusions and routing.

## Evidence labels

- **Runtime-confirmed** — manually observed in the game/emulator on a bounded identified route.
- **Static-confirmed** — established from ROM, Ghidra, symbolic source, or equivalent static analysis.
- **Implementation/CI-confirmed** — established by deterministic patch/generator code and automated tests, but not necessarily exercised in game runtime.
- **Hypothesis / strong inference** — supported but not confirmed.
- **Rejected / failed** — tested/analyzed and shown unsuitable.
- **Pending** — unresolved.

## Preserved Ghidra project

- manifest: `MKMSZR Research/05 - Static Analysis/GHIDRA_PROJECT_MANIFEST.md`
- archive: `MKMSZR Research/08 - Archives/MKMSZR-Ghidra-N64-Project-2026-09-17.zip`

Use the preserved analyzed project. Do not rebuild/re-import the ROM unless it is genuinely unusable.

## After new findings

When verified findings materially change project knowledge:

- update the owning Wiki page in the same normal chat when practical;
- update [[Project Status]], [[Runtime Validation Status]], [[Milestone Timeline]], or [[Address Quick Reference]] only when the change materially affects them;
- preserve evidence-status distinctions;
- do not create a new Wiki page for every experiment.

A Work chat is **not required solely to update documentation**.

Create/update Library material when new work produces durable evidence worth preserving: important static/Ghidra material, machine-readable catalogs, screenshots, RAM evidence, significant experiment logs, major proof-ROM documentation, important failed approaches, or major cross-domain research.

## Preservation rules

- never modify the clean ROM;
- use hash-verified disposable copies;
- guard known patch inputs/ranges;
- recompute N64 CRC1/CRC2;
- do not infer free memory from zero bytes alone;
- retain stage context for overlay addresses;
- do not silently erase superseded conclusions;
- do not run emulator automation unless a task explicitly calls for it.
