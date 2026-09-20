> **Mirror notice:** This Wiki is a navigation-friendly adaptation of MKMSZR documentation. The ChatGPT Library folder `MKMSZR Research` remains the reverse-engineering/research source of truth; this repository remains the implementation/product source of truth. If the Wiki conflicts with an owning source, the owning source wins.

# Web Patcher and Product

Implementation source of truth:

`smeagol44/MKMSZ-Randomizer`

## Architecture

A modular Python patching core is shared by:

- CLI;
- browser frontend through Pyodide;
- automated tests/CI.

ROMs are patched locally and are never distributed by the project.

## Current default pipeline

1. Safe Stage Select
2. arena reservation
3. native payload bootstrap
4. ordinary-pickup persistence
5. seeded ordinary-pickup randomization
6. four-box inventory
7. `BOX n OF 4`
8. boot branding
9. optional Sub-Zero palette patch

The logo/save-flow bypasses have been researched and runtime-confirmed; production GitHub integration should be kept visible in the normal patch pipeline when landed.

## Seed behavior

Browser:

- blank seed -> cryptographically generated 16-digit uppercase hex seed;
- generated seed is inserted into the input;
- result panel shows the effective seed;
- output filename includes it;
- manual seed can replay/share a layout.

Subsystems use separate deterministic domains, including:

- `MKMSZR:BOOT-PHRASE:V1`
- `MKMSZR:PICKUPS:STAGE-LOCAL:V1`

## Build number

Pages stamps:

`v0.<deploy-pages workflow run number>`

Current build after native item randomization: **v0.18**.

## Current pickup mode

Browser output reports:

`Stage-local ordinary pickups (84)`

The first `TEST153` generated Fire pickup runtime check passed.
