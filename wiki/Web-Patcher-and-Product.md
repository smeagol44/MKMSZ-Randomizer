# Web patcher and product behavior

## Shared core

The browser frontend and developer CLI are configuration shells around `src/mkmszr/patcher.py`. The same `RandomizerConfig`, ROM validation, patch modules, output CRC update, deterministic seed behavior, and byte guards apply in both environments.

The browser build compiles the Python package to a wheel and serves it with the static `web/` application. The user supplies the ROM locally; the repository and deployed site do not contain copyrighted ROM data.

## Inputs and output guarantees

- Clean USA Rev. 0 big-endian `.z64` only.
- A new output is produced; the CLI refuses in-place patching and existing-output overwrite.
- Seed is trimmed; absent seed becomes a random 64-bit hex value.
- Output reports applied modules, notes, CRC1/CRC2, and SHA-256.
- Pickup layout, progression-reward selection, boot phrase, and seeded palette use independent deterministic domains.

## Current configuration surface

| Option | Behavior |
|---|---|
| Seed | Drives stage-local pickup layouts, boot phrase, and seeded palette through isolated namespaces |
| Outfit `vanilla` | Leaves source TLUT untouched |
| Presets / red / green | Applies fixed hue behavior |
| `seeded` | Deterministic seed-derived clothing color |
| `hue` | Requires explicit degrees |
| `rgb` | Requires `RRGGBB` or `#RRGGBB` |

Core features such as selector, persistence, pickup shuffle, pickup-driven XP progression, four-box inventory, indicator, branding, and flow bypasses are always installed. Progression adds exactly nine deterministic generated-Herbs rewards and uses the runtime-confirmed Diagnostic B stage-restore behavior. There is not yet a user-facing toggle for global item pooling or enemies because those systems are not production-ready.

## Deployment

`.github/workflows/pages.yml` runs on `main`, builds the wheel, copies the static frontend to `_site`, substitutes the run number into the displayed version, and deploys GitHub Pages. `.github/workflows/wiki.yml` independently mirrors `wiki/` to the GitHub Wiki.

This separation matters: product deployment does not package research artifacts, ROMs, proof patches, or emulator state.
