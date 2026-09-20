> **Mirror notice:** This Wiki is a navigation-friendly adaptation of MKMSZR documentation. The ChatGPT Library folder `MKMSZR Research` remains the reverse-engineering/research source of truth; this repository remains the implementation/product source of truth. If the Wiki conflicts with an owning source, the owning source wins.

# MKMSZ Randomizer Wiki

Welcome to the working documentation for **MKMSZ Randomizer (MKMSZR)**, a native-ROM randomizer project for *Mortal Kombat Mythologies: Sub-Zero*.

## Current milestone

The standalone browser/CLI patcher is live and the current deployed web build is **v0.18**.

Production/runtime foundations now include:

- safe eight-stage selector;
- 1 KiB MKMSZR native runtime/state reservation;
- ordinary-pickup persistence across all eight main stages;
- four native 10-slot inventory boxes;
- stage-local foreign-key masking with inert placeholder `0x08`;
- native `BOX n OF 4` HUD text;
- boot/legal branding and deterministic seeded messages;
- optional deterministic Sub-Zero recoloring;
- post-legal company-logo bypass;
- Safe Stage Select automatic-save bypass;
- **native seeded ordinary-pickup randomization across all 84 catalogued ordinary locations**.

The first generated-layout runtime check also passed: seed `TEST153` produced the expected Shield at Fire's first ordinary pickup and the expected SQL-injection boot joke rendered correctly.

## Start here

| Area | Wiki page |
|---|---|
| Current project state | [[Project Status]] |
| Research rules / source of truth | [[Research Workflow]] |
| Cross-project synthesis | [[Complete Research Synthesis]] |
| N64 runtime, memory, loaders, shared addresses | [[Core Runtime and Address Database]] |
| Stage IDs, selector, transitions, save bypass | [[Stage Flow and Selector]] |
| Pickups, resources, native item randomization | [[Pickups and Item Randomization]] |
| Persistence, inventory boxes, Game Over | [[Persistence Inventory and Lifecycle]] |
| HUD, native text, boot presentation | [[Native UI and Presentation]] |
| Enemy streams and cross-stage fighter import | [[Enemy Randomization]] |
| PlayStation research | [[PS1 Research]] |
| MKT donor work / Reptile Reverse Elbow | [[Foreign Moves and Reptile]] |
| Browser/CLI/product architecture | [[Web Patcher and Product]] |
| Important addresses | [[Address Quick Reference]] |
| Runtime/static evidence matrix | [[Runtime Validation Status]] |
| Stage catalog navigation | [[Stage Catalogs]] |
| Major milestones | [[Milestone Timeline]] |

## Target

Primary target:

- **Nintendo 64, USA, NMYE, revision 0**
- 16 MiB big-endian `.z64`
- clean SHA-256: `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`

The clean ROM is never modified in place. Experiments and generated ROMs use verified disposable copies and corrected N64 CRC1/CRC2.
