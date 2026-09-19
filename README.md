# MKMSZ Randomizer

Development repository for the native-ROM version of the **Mortal Kombat Mythologies: Sub-Zero** randomizer.

The codebase is built around a modular Python patching core. ROMs are never stored in this repository; users must supply their own clean USA `.z64` image.

## Current development goals

- one reusable ROM patching core instead of one-off patch scripts;
- independently testable patch modules;
- deterministic configuration shared by CLI and browser frontend;
- preserve known-good native patches while the Lua-era randomizer logic is progressively replaced;
- include the runtime-confirmed compact safe eight-stage selector in every patched ROM;
- reserve the runtime-tested 1 KiB MKMSZR native memory block in every patched ROM;
- persist all 84 catalogued ordinary pickup locations across the eight main stages;
- provide four native 10-slot inventory boxes with remapping-aware switching and title-menu transition persistence;
- show the active inventory box through the native gameplay text path;
- brand the boot/legal screen for MKMSZR while preserving original Midway/Nintendo attribution;
- choose a deterministic two-line boot joke/quote from a 100+ message pool when a seed is supplied;
- deterministic Sub-Zero outfit recoloring, including seed-derived colors.

## Development status

Early development. The browser patcher is available as a beta, but the randomizer feature set is still expanding.

The original Lua implementation is preserved under `legacy/` for reference only.
