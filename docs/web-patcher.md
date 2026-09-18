# Browser patcher

The test web UI in `web/` is a static GitHub Pages application. It uses Pyodide
to execute the same `mkmszr` Python wheel used by the CLI.

The ROM never leaves the browser:

```text
local file picker
      |
      v
Pyodide virtual filesystem
      |
      v
mkmszr Python core
      |
      v
patched bytes -> local browser download
```

The Pages workflow builds a pure-Python wheel, publishes it next to the static web
assets, and installs that wheel inside Pyodide at page load. No patch logic is
duplicated in JavaScript.

## Always-applied patches

Every browser-generated ROM includes the runtime-confirmed compact safe eight-stage
selector. It is part of the randomizer rather than an optional setting.

## Current browser options

- vanilla / red / green outfit;
- purple / orange / yellow / cyan / pink named colors;
- seed-derived outfit color;
- custom RGB tint;
- runtime-tested 1 KiB MKMSZR arena reservation.

All currently exposed recolor modes have been visually validated in BizHawk through
ROMs produced by the browser patcher. Custom RGB mode has been validated as a mode;
this does not imply exhaustive testing of every possible RGB input.

The browser uses the same shared Python pipeline as the CLI, so the always-on stage
selector and all selected options are applied by one implementation path. The Python
core still performs clean-ROM SHA-256 validation and CIC-6102 checksum recalculation.

## Publishing

GitHub Pages deploys from `main` through `.github/workflows/pages.yml`.

For GitHub Free, the repository must be public. After changing visibility to public,
enable **Settings -> Pages -> Source: GitHub Actions** if GitHub has not already
selected the Actions publishing source. Merging the web-enabled branch to `main`
then triggers deployment.
