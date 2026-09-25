# Web patcher and product behavior

## Shared core

The browser frontend and developer CLI are configuration shells around `src/mkmszr/patcher.py`. The same `RandomizerConfig`, ROM validation, patch modules, output CRC update, deterministic seed behavior, and byte guards apply in both environments.

The shared patch core now always installs the Runtime-confirmed native `GAME SETTINGS -> TURN: TOGGLE / LOCK` menu. This is intentionally an **in-game** preference, not a browser/CLI build option: generated ROMs default to stock `TOGGLE`, while players can opt into `LOCK` from the game's own frontend.

The browser build compiles the Python package to a wheel and serves it with the static `web/` application. The user supplies the ROM locally; the repository and deployed site do not contain copyrighted ROM data.

## Inputs and output guarantees

The web patcher is organized around an explicit **patch target**, not a list of every research or donor image the project may someday use.

Current supported web target:

- **Nintendo 64** — clean MKMSZ USA Rev. 0 big-endian `.z64` is the patch target.
- **MKT N64 donor** — Mortal Kombat Trilogy (USA) Rev. 2 big-endian `.z64` is optional. When supplied, it is read locally as a donor source for supported donor-backed features; the donor itself is never patched.
- **PlayStation** — shown only as a planned target. There is no PS1 file picker until a PS1 patch pipeline exists; future labels use **ISO**, not ROM.

The default web workflow requires only the MKMSZ N64 target. The MKT N64 donor is presented as an optional second file and should remain optional unless a future user-selected feature explicitly requires it. Additional donors should appear only when an enabled feature genuinely needs them.

- Clean USA Rev. 0 big-endian `.z64` target only.
- A new output is produced; the CLI refuses in-place patching and existing-output overwrite.
- Seed is trimmed; absent seed becomes a random 64-bit hex value.
- CLI output reports applied modules, notes, CRC1/CRC2, and SHA-256. The browser completion panel intentionally stays product-facing and reports only target, seed, SHA-256, and CRC1/CRC2 rather than enumerating internal patch modules or discovery-oriented features.
- Pickup layout, progression-reward selection, boot phrase, and seeded palette use independent deterministic domains.

## Current configuration surface

| Option | Behavior |
|---|---|
| Seed | Drives stage-local pickup layouts, boot phrase, and seeded palette through isolated namespaces |
| Outfit `vanilla` | Leaves source TLUT untouched |
| Presets / red / green | Applies fixed hue behavior |
| `rainbow` | Runtime-confirmed 64-phase clothing hue cycle; preserves non-clothing palette entries |
| `seeded` | Deterministic seed-derived clothing color |
| `hue` | Requires explicit degrees |
| `rgb` | Requires `RRGGBB` or `#RRGGBB` |
| Title character | Temporary freeform uppercase name, default `SUB-ZERO`, max 12 characters; patcher appends ` EDITION` and rasterizes it into the generated title CI8 image |

Core features such as selector, persistence, pickup shuffle, pickup-driven XP progression, four-box inventory, indicator, branding, and flow bypasses are always installed. Progression adds exactly nine deterministic generated-Herbs rewards and uses the runtime-confirmed Diagnostic B stage-restore behavior. There is not yet a user-facing toggle for global item pooling or enemies because those systems are not production-ready.

The shared patch core includes donor-backed production features without embedding donor game data in the repository or deployed site. When the optional MKT USA Rev. 2 N64 donor is supplied, the browser derives the currently supported donor assets locally and passes them into the shared patch core. The developer CLI exposes the same optional path through `--mkt-rom`; without a donor, the normal MKMSZR build remains valid.

## Deployment

`.github/workflows/pages.yml` runs on `main`, first compiles `src/mkmszr` with Python's `compileall`, then builds the wheel, copies the static frontend to `_site`, substitutes the run number into the displayed version, and deploys GitHub Pages. The compile gate was added after a 2026-09-22 title-branding packaging regression in which a malformed source header containing literal `\\n` escapes was packaged into a syntactically invalid wheel; Pyodide then failed before patching. A follow-up browser failure showed that reusing the same wheel URL could still serve the stale malformed package from cache even after the source was fixed. Pages now rewrites the wheel to a unique PEP 440 dev version per deployment (for example `mkmszr-0.1.0.dev371-py3-none-any.whl`) and cache-busts `app.js` with the same run number. The deployment artifact was manually inspected and `mkmszr.patcher` imported successfully from the unique wheel. `.github/workflows/wiki.yml` independently mirrors `wiki/` to the GitHub Wiki.

This separation matters: product deployment does not package research artifacts, ROMs, proof patches, or emulator state.


## 1.0 release boundary

This is a **non-exhaustive product-facing summary**. The canonical complete 1.0 requirements, acceptance criteria, blockers/non-blockers, dependency order, and final release gates are owned by [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap).

The current stage-local pickup mode is not the final 1.0 randomizer. From the product surface, the major unresolved 1.0 work includes the global cross-stage item model and solvability validation, the broader native randomizer HUD, run-lifecycle handling such as HP/lives/continues and reset behavior, and the Very Hard invariant before final full-seed validation. Refer to the Roadmap for the authoritative and complete requirement set.
