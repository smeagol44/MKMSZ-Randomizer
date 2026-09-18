# MKMSZ True Randomizer

Development repository for the native-ROM version of the **Mortal Kombat Mythologies: Sub-Zero** randomizer.

The current codebase is being rebuilt around a modular Python patching core. ROMs are never stored in this repository; users must supply their own clean USA `.z64` image.

## Current development goals

- one reusable ROM patching core instead of one-off patch scripts;
- independently testable patch modules;
- deterministic configuration suitable for CLI, future GUI, and future web frontend;
- preserve known-good native patches while the Lua-era randomizer logic is progressively replaced;
- include the runtime-confirmed compact safe eight-stage selector in every patched ROM;
- deterministic Sub-Zero outfit recoloring, including seed-derived colors.

## Development status

Early private development. The repository is not ready for release yet.

The original Lua implementation is preserved under `legacy/` for reference only.
