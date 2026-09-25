# Web patcher and product behavior

## Shared core

The browser frontend and developer CLI are configuration shells around `src/mkmszr/patcher.py`. The same `RandomizerConfig`, ROM validation, patch modules, output CRC update, deterministic seed behavior, and byte guards apply in both environments.

The browser build compiles the Python package to a wheel and serves it with the static `web/` application. The user supplies the ROM locally; the repository and deployed site do not contain copyrighted ROM data.

## Inputs and output guarantees

The web patcher is organized around an explicit **patch target**, not a list of every research or donor image the project may someday use.

Current supported web target:

- **Nintendo 64** — clean MKMSZ USA Rev. 0 big-endian `.z64` is the patch target.
- **MKT N64 donor** — Mortal Kombat Trilogy (USA) Rev. 2 big-endian `.z64` is required by the web UI and is read locally to extract the Runtime-confirmed Toasty visual/audio assets. The donor itself is never patched.
- **PlayStation** — shown only as a planned target. There is no PS1 file picker until a PS1 patch pipeline exists; future labels use **ISO**, not ROM.

The default web workflow therefore asks for exactly two game files: the MKMSZ N64 target and the MKT N64 donor. Additional donors should appear only when an enabled feature genuinely requires them.

- Clean USA Rev. 0 big-endian `.z64` target only.
- A new output is produced; the CLI refuses in-place patching and existing-output overwrite.
- Seed is trimmed; absent seed becomes a random 64-bit hex value.
- CLI output reports applied modules, notes, CRC1/CRC2, and SHA-256. The browser completion panel reports seed, SHA-256, CRC1/CRC2, applied patches, and pickup mode, but intentionally omits the generated boot message and title edition so those remain in-game discoveries.
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

The shared patch core includes the Runtime-confirmed Toasty production module at **80/1000 (8%)**. The browser now derives `ToastyAssets` directly from the user-supplied MKT USA Rev. 2 N64 donor and passes them into that module. The repository and deployed site contain no donor art/audio bytes. The developer CLI exposes the same path through optional `--mkt-rom`; without that option it retains the prior no-Toasty developer behavior.

## Deployment

`.github/workflows/pages.yml` runs on `main`, first compiles `src/mkmszr` with Python's `compileall`, then builds the wheel, copies the static frontend to `_site`, substitutes the run number into the displayed version, and deploys GitHub Pages. The compile gate was added after a 2026-09-22 title-branding packaging regression in which a malformed source header containing literal `\\n` escapes was packaged into a syntactically invalid wheel; Pyodide then failed before patching. A follow-up browser failure showed that reusing the same wheel URL could still serve the stale malformed package from cache even after the source was fixed. Pages now rewrites the wheel to a unique PEP 440 dev version per deployment (for example `mkmszr-0.1.0.dev371-py3-none-any.whl`) and cache-busts `app.js` with the same run number. The deployment artifact was manually inspected and `mkmszr.patcher` imported successfully from the unique wheel. `.github/workflows/wiki.yml` independently mirrors `wiki/` to the GitHub Wiki.

This separation matters: product deployment does not package research artifacts, ROMs, proof patches, or emulator state.


## 1.0 release boundary

This is a **non-exhaustive product-facing summary**. The canonical complete 1.0 requirements, acceptance criteria, blockers/non-blockers, dependency order, and final release gates are owned by [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap).

The current stage-local pickup mode is not the final 1.0 randomizer. From the product surface, the major unresolved 1.0 work includes the global cross-stage item model and solvability validation, the broader native randomizer HUD, run-lifecycle handling such as HP/lives/continues and reset behavior, and the Very Hard invariant before final full-seed validation. Refer to the Roadmap for the authoritative and complete requirement set.
