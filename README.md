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
- reserve the runtime-tested 16 KiB MKMSZR native memory block in every patched ROM;
- persist all 84 catalogued ordinary pickup locations across the eight main stages;
- deterministically randomize and solve 85 global checks, including 84 ordinary records and the scripted Temple special check;
- provide four native 10-slot inventory boxes with remapping-aware switching and title-menu transition persistence;
- show the active inventory box through the native gameplay text path;
- brand the boot/legal screen as MKMSZR with the configured character edition, seeded joke text, `BY SMEAG`, and `NOT LICENSED BY NINTENDO`;
- choose a deterministic two-line boot joke/quote from a 100+ message pool;
- deterministic Sub-Zero outfit recoloring, including seed-derived colors;
- the accepted in-game `TURN / ATTACK / SPECIALS / JUMP / RUN` control suite;
- optional MKT Rev. 2 donor-backed 16-color CI4 Toasty effect;
- optional MKT Rev. 2 donor-backed, seed-deterministic Temple intro audio replacement.

## Native pickup randomization milestone

The shared browser/CLI patcher generates a deterministic global layout across
**85 checks**: 84 ordinary pickups plus the scripted Temple special check.
Logical Map is excluded. Powers as pickups ON converts nine Herbs rewards into
explicit Power Upgrades before shuffling; OFF retains vanilla earned XP.
Required powers remains an independent Fortress XP-gate setting in both modes.

A fixed-point solver accepts layouts under **All 85 available** (default) or
**Game beatable** (all 21 progression credentials plus required shuffled upgrades
when pickup mode is ON). Rejected layouts retry deterministically, with a
10,000-attempt ceiling. Destination materialization preserves native location,
checkpoint, activation, and persistence behavior separately from reward identity.

Supported clean input remains 16 MiB. Generated output is 32 MiB with eight
explicit 1 MiB stage-resource slots. Loader and gameplay evidence are bounded;
representative full-seed/all-tier release validation and the broader native HUD
remain pending. See the [public Wiki](https://github.com/smeagol44/MKMSZ-Randomizer/wiki/Global-Item-Materialization-and-Solvability)
for current evidence and limitations.

## Development status

Beta. The browser patcher now includes native seeded ordinary-pickup
randomization plus the established persistence, four-box inventory, stage
selector, presentation, and palette features. The broader native randomizer
HUD, runtime coverage, and other randomizer systems are still expanding.

The original Lua implementation is preserved under `legacy/` for reference only.
