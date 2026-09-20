# MKMSZR technical knowledge base

This Wiki is the current, self-contained technical reference for the native-ROM **Mortal Kombat Mythologies: Sub-Zero Randomizer**. The versioned repository and this `wiki/` tree are the product/documentation source of truth. The research archive is evidence and history; a contributor should not need it to understand the current system.

## Start here

- [Contributor start here](Contributor-Start-Here): build, test, and research order.
- [Project status](Project-Status): what is production, proof-only, pending, or rejected.
- [Architecture overview](Architecture-Overview): ROM validation, patch pipeline, runtime reservation, and feature boundaries.
- [Complete research synthesis](Complete-Research-Synthesis): one-page domain map.
- [Runtime validation status](Runtime-Validation-Status): the exact scope of runtime, static, and CI evidence.

## Current product

The Python patcher accepts only the clean USA Rev. 0 big-endian ROM, writes a separate output, installs a native eight-stage selector and 1 KiB runtime block, persists and stage-locally randomizes all 84 ordinary pickups, provides four ten-slot inventory boxes, draws a native box indicator, brands and shortens the boot flow, and optionally recolors Sub-Zero. The browser and CLI use the same patching core.

The product is **beta**. Production means a guarded implementation is in the repository and covered by CI; it does not imply that every generated seed has completed a full hardware/emulator playthrough. Global cross-stage item placement, production enemy randomization, XP progression mode, and a finished foreign special move are not product features yet.

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
| XP proof and proposed mode | [XP and progression](XP-and-Progression) |
| HUD, text, and presentation | [Native UI and presentation](Native-UI-and-Presentation) |
| Player actions and Reverse Elbow | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| N64/PS1 comparison | [N64–PS1 comparison](N64-PS1-Comparison), [PS1 research](PS1-Research) |
| Product frontend and release behavior | [Web patcher and product](Web-Patcher-and-Product), [testing and CI](Testing-and-CI) |

## Evidence labels

- **Runtime-confirmed:** observed in an emulator run or supplied runtime capture.
- **Static-confirmed:** established from the clean ROM, disassembly/decompilation, or byte-identical memory mapping.
- **Implementation/CI-confirmed:** guarded in current code and covered by automated tests.
- **Hypothesis:** plausible interpretation that is not yet proven.
- **Rejected:** tested or analyzed and shown unsuitable.
- **Pending:** defined work or validation that has not happened.

These labels describe evidence, not desirability. A runtime proof patch can be confirmed without being production-safe; a production implementation can be CI-confirmed while still awaiting exhaustive playthrough coverage.
