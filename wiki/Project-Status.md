> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Project Status

## Runtime-confirmed foundations

- Safe compact eight-stage selector.
- Reserved 1 KiB MKMSZR arena prefix and native file-ID `0x1B` loading/execution.
- Eight-stage ordinary-pickup persistence architecture.
- Four isolated native 10-slot inventory boxes.
- Stage-local foreign-key masking with inert placeholder `0x08`.
- Native gameplay geometry and arbitrary native ASCII text.
- `BOX n OF 4` gameplay indicator.
- Boot/legal branding.
- Post-legal logo bypass.
- Safe Stage Select one-shot automatic-save bypass.
- Same-stage and bounded cross-stage pickup/resource proofs.
- Ordinary-enemy stream architecture and bounded cross-stage fighter import.
- First generated native item layout: `TEST153` produced the expected Shield at Fire's first pickup.
- `TEST153` boot message `' OR 1==1 --` rendered correctly, adding punctuation-font evidence.

## Production / implementation-confirmed

- deterministic seed handling in browser and CLI;
- deterministic boot-message selection;
- deterministic Sub-Zero recoloring;
- browser build number `v0.<Pages run>`;
- stage-local seeded randomization of all 84 ordinary pickup records;
- post-legal logo bypass and selector-local automatic-save bypass in the default production pipeline.

The first generated layout is now runtime-confirmed at one Fire location; a full seeded run is still pending.

## Functionally viable / beta

### XP progression items

The native XP architecture is now static-mapped. The planned production design disables gameplay XP awards and replaces nine Herbs pickups with progression pickups that advance to the next stock move tier. Stage-cap and combo EXPERIENCE-render paths are also mapped. Implementation and runtime validation are pending.

### Enemy randomization

Cross-stage ordinary-enemy resource import works in the bounded Fire proof. Imported Temple monks render, move, fight and are killable, but normal death/despawn presentation is missing. Mixed rosters, broad compatibility and bosses/minibosses remain unresolved.

### Foreign moves

MKT Reptile's Reverse Elbow has an implementation-ready MKMSZ-side static design. The first proof-ROM experiment is separate from the production randomizer.

## Main remaining randomizer work

1. Broaden runtime validation of generated item layouts toward a complete seeded run.
2. Design production **global cross-stage** item placement/resource import.
3. Implement pickup-driven XP/move progression: no combat XP, nine next-tier pickups, static stage caps, and no combo EXPERIENCE line.
4. Add full Game Over run-state reset.
5. Define/preserve HP, lives and continues across intended lifecycle routes.
6. Add richer randomizer HUD/status text.
7. Build a production enemy randomization planner.
8. Resolve imported-enemy death/despawn presentation and compatibility.
9. Expand optional move/character replacement if Reverse Elbow succeeds.
