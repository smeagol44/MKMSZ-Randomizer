# Web patcher and product behavior

## Shared core

The browser frontend and developer CLI are configuration shells around `src/mkmszr/patcher.py`. The same `RandomizerConfig`, ROM validation, patch modules, output CRC update, deterministic seed behavior, and byte guards apply in both environments.

The shared patch core now always installs the Runtime-confirmed complete native GAME SETTINGS frontend: `TURN`, `COMBOS`, `SPECIALS`, `JUMP`, and `EXIT`. These are intentionally **in-game** preferences, not browser/CLI build options. TURN gameplay is active; COMBOS/SPECIALS/JUMP currently provide persistent frontend state only. JUMP remains visible but greyed/fixed to DPAD unless COMBOS=ASSIST and SPECIALS=MODERN.

The browser build compiles the Python package to a wheel and serves it with the static `web/` application. The user supplies the ROM locally; the repository and deployed site do not contain copyrighted ROM data.

The browser runs Pyodide inside a dedicated Web Worker so the page remains responsive while the CPU-heavy patch pipeline executes. Selecting the MKMSZ target immediately sends the file to that worker for the same Python `RomImage.from_bytes(..., require_clean=True)` validation used by the shared core; the worker keeps the validated canonical source image in memory. Patching then starts from a fresh copy of that already-validated image, avoiding a second clean-ROM SHA-256/byte-order pass in the browser while leaving the CLI validation path unchanged. The optional MKT Rev. 2 donor is likewise validated and cached on selection.

## Inputs and output guarantees

The web patcher is organized around an explicit **patch target**, not a list of every research or donor image the project may someday use.

Current supported web target:

- **Nintendo 64** — clean MKMSZ USA Rev. 0 is the patch target. Standard `.z64` (big-endian), `.v64` (byte-swapped), and `.n64` (little-endian 32-bit-word) serializations are accepted. Detection uses the first four ROM bytes rather than the filename extension; input is normalized to canonical big-endian `.z64` before the existing clean-ROM SHA-256 and patch guards run. Generated output remains canonical `.z64`.
- **MKT N64 donor** — Mortal Kombat Trilogy (USA) Rev. 2 big-endian `.z64` is optional. When supplied, it is read locally as a donor source for supported donor-backed features; the donor itself is never patched.
- **PlayStation** — shown only as a planned target. There is no PS1 file picker until a PS1 patch pipeline exists; future labels use **ISO**, not ROM.

The default web workflow requires only the MKMSZ N64 target. The MKT N64 donor is presented as an optional second file and should remain optional unless a future user-selected feature explicitly requires it. Additional donors should appear only when an enabled feature genuinely needs them.

- Clean USA Rev. 0 big-endian `.z64` target only.
- A new output is produced; the CLI refuses in-place patching and existing-output overwrite.
- Browser target/donor validation begins immediately on file selection and displays the validated SHA-256 before patching can start. Both file controls support click/browse and drag/drop presentation; validated MKT donors explicitly show that donor-backed Toasty visual/audio and seeded Temple intro audio are enabled.
- The browser settings surface uses collapsible Randomizer Features, Run Settings, and Default Game Settings groups with live summaries. The Game Settings summary uses the native label `TURN: TOGGLE` whenever Turn Lock is disabled.
- A live Build Summary reflects seed, outfit, randomizer features, run settings, and initial GAME SETTINGS before patching; the seed field also exposes Randomize and Copy actions.
- During a browser build, an indeterminate progress bar stays animated on the main thread while an 80-message MKMSZR/Mortal Kombat/gaming flavor deck is shuffled and consumed without repeats; messages advance every 3.6 seconds, and only after all 80 are used is the deck reshuffled. These messages are presentation only; failures still surface the actual Python/worker diagnostic text and stack trace.
- Successful builds present a dedicated completion card with seed copy, primary ROM-save action, return-to-settings action, and collapsible technical SHA/CRC details. The current visual language remains the restrained dark UI with subtle ice accents and full-card highlighting for enabled toggles.
- Seed is trimmed; absent seed becomes a random 64-bit hex value.
- CLI output reports applied modules, notes, CRC1/CRC2, and SHA-256. The browser completion panel intentionally stays product-facing and reports only target, seed, SHA-256, and CRC1/CRC2 rather than enumerating internal patch modules or discovery-oriented features.
- Pickup layout, progression-reward selection, optional power-order shuffle, boot phrase, and seeded palette use independent deterministic domains.

## Current configuration surface

| Option | Behavior |
|---|---|
| Seed | Drives global pickup layouts, boot phrase, seeded palette, and donor-backed Temple intro audio through isolated namespaces |
| Outfit `vanilla` | Leaves source clothing TLUT and the accepted icy-blue title palette unchanged |
| Presets / red / green | Applies fixed hue behavior |
| `rainbow` | Runtime-confirmed 64-phase clothing hue cycle; fixed five-hue title word/edition treatment (the title itself does not animate) |
| `seeded` | Deterministic seed-derived clothing color; **browser default** |
| `hue` | Requires explicit degrees |
| `rgb` | Requires `RRGGBB` or `#RRGGBB` |
| Title character | Temporary freeform uppercase name, default `SUB-ZERO`, max 12 characters; patcher appends ` EDITION` and rasterizes it into the typeset CI8 title. Its 16-color palette follows every non-vanilla outfit color option, including the same seed-derived hue for `seeded`; `rainbow` uses a fixed multicolor title. See [Presentation and branding](Presentation-and-Branding). |
| Shuffle Power Progression | **Browser default on**. When enabled, deterministically shuffles the nine native Power Up slots while preserving the single Ice Shatter prerequisite rule; Slide and Super Slide are independent. The shared configuration still permits disabling it. |
| Difficulty | Build-time run setting: Very Easy / Easy / Medium / Hard / Very Hard. Default **Very Hard**. The lifecycle patch restores the selected value on fresh-run/reset boundaries. |
| Lives | Total starting lives, integer **1..10**. Default **5**. Game Over/new-run reset uses the same configured value. |
| Continues | Starting continues, integer **0..5**. Default **3**. Game Over/new-run reset uses the same configured value. |
| Required powers for Fortress | Browser default **Seed**; user-selectable `Seed`, `Vanilla`, or `Custom`. Seed chooses a deterministic 0..9 requirement from its independent namespace. |
| Persistent HP | Default **on**. On: damaged HP survives living stage exit/re-entry. Off: living re-entry receives full HP; ordinary death/Continue always receive full replacement HP in either mode. |
| Seed completion rule | **All 85 available** (default) or **Game beatable** in the shared global item path. All 85 requires every shuffled check reachable; Game beatable requires all 21 progression credentials plus the selected shuffled-upgrade count when pickup mode is ON. OFF retains stock XP with its independent Fortress gate. Generated output is 32 MiB; supported clean input remains 16 MiB. |

Core features such as selector, persistence, pickup shuffle, pickup-driven XP progression, four-box inventory, indicator, branding, and flow bypasses are always installed. Progression adds exactly nine deterministic generated-Herbs rewards and uses the runtime-confirmed Diagnostic B stage-restore behavior. There is not yet a user-facing toggle for global item pooling or enemies because those systems are not production-ready.

The shared patch core includes donor-backed production features without embedding donor game data in the repository or deployed site. When the optional MKT USA Rev. 2 N64 donor is supplied, the browser derives the currently supported donor assets locally and passes them into the shared patch core. This enables both production Toasty and the seeded Temple-intro audio replacement. Temple audio uses its own deterministic namespace, replaces exactly one of the two intro audio positions, and materializes only the selected donor sample. The developer CLI exposes the same optional path through `--mkt-rom`; without a donor, both donor-backed paths are skipped and the normal MKMSZR build remains valid.

## Enemy Randomization option

The shared product configuration exposes **Enemy Randomization** as a seeded option in both browser and CLI. The browser now defaults this option **ON**; the underlying shared configuration/CLI behavior remains user-selectable and is not redefined by the browser default.

- Browser: `Randomizer Features -> Enemy Randomization`, default **ON**.
- CLI: `--enemy-randomization`.
- Both surfaces set the same `RandomizerConfig.enemy_randomization` field and therefore use the same shared patch pipeline.
- Enabling the option invokes the guarded `EnemyRandomizationPatch`, which consumes the deterministic 104-record planner/materializer and remains fail-closed to registered materializable profiles.
- Bosses and the five gated/special encounters remain excluded/fixed.
- The normal build seed drives enemy planning through the isolated `MKMSZR:ENEMIES:RESOURCE-PLANNER:V1` domain.
- Disabling the option leaves enemy-randomization patching absent from the shared pipeline.

The underlying planner/materializer has bounded Runtime-confirmed representative all-stage evidence. The new product composition still requires repository CI plus one normal browser/CLI production-build runtime gate with the option enabled.

## Deployment

`.github/workflows/pages.yml` runs on `main`, first compiles `src/mkmszr` with Python's `compileall`, then builds the wheel, copies the static frontend to `_site`, substitutes the run number into the displayed version, and deploys GitHub Pages. The compile gate was added after a 2026-09-22 title-branding packaging regression in which a malformed source header containing literal `\\n` escapes was packaged into a syntactically invalid wheel; Pyodide then failed before patching. A follow-up browser failure showed that reusing the same wheel URL could still serve the stale malformed package from cache even after the source was fixed. Pages now rewrites the wheel to a unique PEP 440 dev version per deployment (for example `mkmszr-0.1.0.dev371-py3-none-any.whl`) and cache-busts `app.js` with the same run number. The app passes that deployment query string to `patch-worker.js`, so the worker cannot remain stale across Pages releases. The deployment artifact was manually inspected and `mkmszr.patcher` imported successfully from the unique wheel. `.github/workflows/wiki.yml` independently mirrors `wiki/` to the GitHub Wiki.

This separation matters: product deployment does not package research artifacts, ROMs, proof patches, or emulator state.


## 1.0 release boundary

This is a **non-exhaustive product-facing summary**. The canonical complete 1.0 requirements, acceptance criteria, blockers/non-blockers, dependency order, and final release gates are owned by [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap).

PR #137 integrates the 85-check global item path and configurable fixed-point completion rule into the normal browser/CLI build. The maintainer approved promotion after bounded global-v2 gameplay; exhaustive runtime coverage is not claimed. Run lifecycle remains integrated, with the Very Hard / 9 / 5 / HP-ON v06 baseline Runtime-confirmed and other configurations pending representative sampling. Remaining 1.0 work includes the broader native randomizer HUD and final representative full-seed validation. See the Roadmap for release requirements.
