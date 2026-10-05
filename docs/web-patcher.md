# Browser patcher

The test web UI in `web/` is a static GitHub Pages application. It uses Pyodide
to execute the same `mkmszr` Python wheel used by the CLI.

The ROM never leaves the browser:

```text
local file picker
      |
      v
browser Web Worker
      |
      +--> validate/cache selected ROM SHA immediately
      |
      v
Pyodide virtual filesystem
      |
      v
mkmszr Python core
      |
      v
patched bytes -> main thread -> local browser download
```

The Pages workflow builds a pure-Python wheel, publishes it next to the static web
assets, and installs that wheel inside Pyodide at page load. Pyodide itself lives in
`web/patch-worker.js`, keeping the page responsive while patching. No patch logic is
duplicated in JavaScript.

When a target ROM is selected, the worker immediately runs the normal Python clean-ROM
validation and reports the canonical SHA-256 to the page. The validated `RomImage` is
kept in the worker and the patch build starts from `fresh_copy()`, so browser patching
does not repeat the clean-ROM SHA/byte-order validation pass. The CLI still enters
through `patch_file()` / `patch_bytes()` and therefore retains its normal validation.

The optional MKT Rev. 2 donor follows the same selection-time validate/cache flow. While
a build runs, the page shows an indeterminate animated progress bar and cycles through
an 80-message shuffled flavor deck at 3.6 seconds per message. Every message in the deck
is shown once before the deck is reshuffled; a reshuffle is guarded against repeating
the previous message immediately. Those messages deliberately do not claim technical
build phases; failures still report the real worker/Python diagnostics and stack trace.

## Always-applied patches

Every browser-generated ROM includes the core native infrastructure:

- the runtime-confirmed compact safe eight-stage selector;
- the runtime-tested 1 KiB MKMSZR arena-prefix reservation;
- the native payload bootstrap and V1 state block;
- runtime-confirmed persistence for all 84 catalogued ordinary pickup locations
  across the eight main stages.

These are implementation infrastructure for the randomizer, not user-facing options.

## Current browser options

- vanilla / red / green outfit;
- purple / orange / yellow / cyan / pink named colors;
- seed-derived outfit color (browser default);
- custom RGB tint;
- Powers as pickups (on by default; off retains stock XP awards and ordinary Herbs);
- required powers: Seed (browser default), Vanilla, or Custom (0–9), with the effective requirement shown after patching;
- Shuffle Power Progression (on by default in the browser), independently of the XP source;
- Enemy Randomization (on by default in the browser);

All currently exposed recolor modes have been visually validated in BizHawk through
ROMs produced by the browser patcher. Custom RGB mode has been validated as a mode;
this does not imply exhaustive testing of every possible RGB input.

The browser uses the same shared Python pipeline as the CLI, so the always-on stage
selector, arena reservation, pickup persistence, and all selected options are applied
by one implementation path. The Python core still performs clean-ROM SHA-256
validation and CIC-6102 checksum recalculation.

## Publishing

GitHub Pages deploys from `main` through `.github/workflows/pages.yml`.

For GitHub Free, the repository must be public. After changing visibility to public,
enable **Settings -> Pages -> Source: GitHub Actions** if GitHub has not already
selected the Actions publishing source. Merging the web-enabled branch to `main`
then triggers deployment.
