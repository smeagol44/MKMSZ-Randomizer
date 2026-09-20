> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Complete Research Synthesis

This page is the current concise cross-project synthesis. Detailed technical ownership stays with the topic pages; the Library preserves the deeper historical/evidentiary record.

## N64 architecture

- Main stage overlays share a common gameplay overlay base at `0x802ECE30`.
- A global 12-byte-entry file table at ROM `0x000A5010` / VA `0x800A4410` feeds native loading.
- MKMSZR reserves `0x801AF420..0x801AF81F` by moving the game's arena start to `0x801AF820`.
- Runtime Layout V1 splits that 1 KiB into 0x200 bytes of reloadable code and 0x200 bytes of persistent state.
- Ordinary pickups are data-driven 0x30-byte records with understood callbacks, resource selectors, presentation descriptors and collected flags.
- Ordinary enemies are stage command-stream driven and share fighter construction/resource infrastructure.
- Native gameplay HUD geometry and native ASCII text are available to MKMSZR.

## Major milestones

| Milestone | State |
|---|---|
| clean N64 target + preserved Ghidra project | Confirmed |
| safe eight-stage selector | Runtime-confirmed A-route |
| all eight pickup/resource catalogs | Complete |
| same-stage + bounded cross-stage item-resource proofs | Runtime-confirmed |
| file-ID `0x1B` loading and code execution | Runtime-confirmed |
| eight-stage ordinary-pickup persistence | Runtime-confirmed architecture |
| four-box native inventory | Runtime-confirmed |
| foreign-key LIVE masking / inert `0x08` | Runtime-confirmed |
| native gameplay rectangles + arbitrary text | Runtime-confirmed |
| boot logo bypass | Runtime-confirmed |
| selector-entry automatic-save bypass | Runtime-confirmed on Temple route |
| stage-local seeded ordinary-pickup randomization | Runtime-confirmed on first generated TEST153 route; broader playthrough coverage pending |
| cross-stage ordinary-enemy import | Runtime-confirmed bounded Fire proof |
| PS1 executable/overlay/selector map | Strong static baseline |

## Main unresolved areas

- full Game Over run-state reset;
- player-stat lifecycle policy;
- global cross-stage item resource planning;
- richer randomizer HUD;
- custom textured-image rendering;
- production enemy planner and compatibility matrix;
- imported-enemy death/despawn presentation;
- bosses/minibosses;
- PS1 runtime activation/memory validation;
- optional foreign-move / character replacement.
