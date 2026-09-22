# MKMSZ Randomizer

Development repository for the native-ROM version of the **Mortal Kombat Mythologies: Sub-Zero** randomizer.

The codebase is built around a modular Python patching core. ROMs are never stored in this repository; users must supply their own clean USA `.z64` image.

## Current development goals

- one reusable ROM patching core instead of one-off patch scripts;
- independently testable patch modules;
- deterministic configuration shared by CLI and browser frontend;
- preserve known-good native patches while the Lua-era randomizer logic is progressively replaced;
- include the runtime-confirmed compact safe eight-stage selector in every patched ROM;
- skip the two mandatory post-legal company/logo screens while preserving the legal/branding screen and normal title initialization;
- skip only the Safe Stage Select automatic stage-entry save prompt while preserving normal later/manual saves;
- reserve the runtime-tested 1 KiB MKMSZR native memory block in every patched ROM;
- persist all 84 catalogued ordinary pickup locations across the eight main stages;
- deterministically randomize the 84 ordinary pickup records from the run seed;
- provide four native 10-slot inventory boxes with remapping-aware switching and title-menu transition persistence;
- show the active inventory box through the native gameplay text path;
- brand the boot/legal screen as MKMSZR with the configured character edition, seeded joke text, `BY SMEAG`, and `NOT LICENSED BY NINTENDO`;
- choose a deterministic two-line boot joke/quote from a 100+ message pool;
- deterministic Sub-Zero outfit recoloring, including seed-derived colors.

## Native pickup randomization milestone

The browser/CLI patcher now performs the first native item-randomization mode.

For each main stage, the complete native pickup identity tuple at record
`+0x10..+0x2B` is shuffled among that stage's ordinary pickup locations.
This moves the pickup behavior, award callback, callback parameter, collision
extents, stage-local model/resource selector, and presentation descriptor
together while leaving the destination position and collected flag intact.

The layout is deterministic from the run seed and uses a dedicated pickup RNG
namespace, so unrelated seeded features do not consume its random state.
The legacy randomizer's Wind, Earth, Water, and Prison access rules are ported
into the generator and layouts that fail that model are deterministically
rejected before the ROM is written. Those access rules still need a native
runtime playthrough validation in this implementation.

Current scope is intentionally conservative:

- all **84 ordinary pickup records** are covered;
- item pools are preserved **within each stage**;
- the scripted Temple Map is excluded;
- scripted/special mechanisms are excluded;
- global cross-stage item placement is not enabled yet because pickup resource
  selectors are stage-local and foreign resources need a production import
  planner;
- native mana pickups remain native mana rather than using the legacy Lua
  workaround that substituted Herbs.

Seed `TEST153` has now provided the first bounded runtime validation of this production mode: Fire's first ordinary location became the predicted Shield and behaved normally. A complete seeded run and broader arbitrary-layout coverage are still pending.

## Development status

Beta. The browser patcher now includes native seeded ordinary-pickup
randomization plus the established persistence, four-box inventory, stage
selector, presentation, and palette features. Broader cross-stage item
randomization, enemy planning, lifecycle polish, and other randomizer systems
are still expanding.

The original Lua implementation is preserved under `legacy/` for reference only.
