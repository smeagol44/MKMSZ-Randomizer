# MKMSZR technical knowledge base

This Wiki is the current, self-contained technical reference for the native-ROM **Mortal Kombat Mythologies: Sub-Zero Randomizer**. GitHub code describes the implemented product; the versioned `wiki/` tree and published Wiki contain current project knowledge; the `MKMSZR Research` Library archive preserves evidence and history. Project Instructions separately contain assistant operating rules. The Wiki includes technical facts, product requirements, methodology, contribution information, and pending work.

## Start here

- [Contributor start here](Contributor-Start-Here): build/test commands and documentation map.
- [Project status](Project-Status): what is production, proof-only, pending, or rejected.
- [Architecture overview](Architecture-Overview): ROM validation, patch pipeline, runtime reservation, and feature boundaries.
- [Complete research synthesis](Complete-Research-Synthesis): one-page domain map.
- [Runtime validation status](Runtime-Validation-Status): the exact scope of runtime, static, and CI evidence.

## Current product

The Python patcher accepts only the clean USA Rev. 0 big-endian ROM, writes a separate output, installs a native eight-stage selector and 1 KiB runtime block, persists and stage-locally randomizes all 84 ordinary pickups, adds nine pickup-driven progression rewards, provides four ten-slot inventory boxes, draws a native box indicator, brands and shortens the boot flow, and optionally recolors Sub-Zero. The browser and CLI use the same patching core.

The product is **beta**. Production means a guarded implementation is in the repository and covered by CI; it does not imply that every generated seed has completed a full hardware/emulator playthrough. XP progression uses the runtime-confirmed Diagnostic B behavior, with full nine-tier coverage pending. Global cross-stage item placement, production enemy randomization, and a finished foreign special move are not product features yet.

## Technical domains

| Domain | Canonical page |
|---|---|
| Runtime allocation and bootstrapping | [Core runtime and address database](Core-Runtime-and-Address-Database) |
| ROM/RDRAM/overlay/resource layout | [Runtime and memory map](Runtime-and-Memory-Map), [ROM and resource map](ROM-Overlay-and-Resource-Map) |
| Functions and patch sites | [Function registry](Function-Registry), [address and patch-site registry](Address-and-Patch-Site-Registry) |
| Native structures and encodings | [Data structures and encodings](Data-Structures-and-Encodings) |
| Pickups and seeded placement | [Pickups and item randomization](Pickups-and-Item-Randomization) |
| Persistence and four-box inventory | [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) |
| Stage resources and all 84 records | [Stage catalogs](Stage-Catalogs) |
| Stage selection and frontend flow | [Stage flow and selector](Stage-Flow-and-Selector), [flow bypasses](Flow-Bypasses) |
| Enemies and resource import | [Enemy randomization](Enemy-Randomization) |
| Pickup-driven XP and progression history | [XP and progression](XP-and-Progression) |
| HUD, text, and presentation | [Native UI and presentation](Native-UI-and-Presentation) |
| Player actions and Reverse Elbow | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| N64/PS1 comparison | [N64–PS1 comparison](N64-PS1-Comparison), [PS1 research](PS1-Research) |
| Product frontend and release behavior | [Web patcher and product](Web-Patcher-and-Product), [testing and CI](Testing-and-CI) |

## Evidence labels

- **Runtime-confirmed:** observed in game/emulator on a defined route, including user observations or supplied runtime captures; limited to the recorded scope.
- **Static-confirmed:** established from ROM/Ghidra/source/static analysis, including disassembly/decompilation or byte-identical memory mapping.
- **Implementation/CI-confirmed:** established by implementation or automated checks, without necessarily being observed at runtime; the surrounding evidence identifies which checks apply.
- **Hypothesis / strong inference:** supported interpretation that is not yet confirmed.
- **Rejected / failed:** tested or analyzed and shown unsuitable within the stated scope.
- **Pending:** defined work or validation that has not happened.

These labels describe evidence, not desirability. A runtime proof patch can be confirmed without being production-safe; a production implementation can be CI-confirmed while still awaiting exhaustive playthrough coverage.
