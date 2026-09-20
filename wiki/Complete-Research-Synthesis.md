# Complete research synthesis

## What exists now

MKMSZR has moved from Lua-era experiments to a guarded native patcher. Its production architecture validates one clean ROM, composes modular patches, reserves a versioned native block, persists and stage-locally shuffles all 84 ordinary pickups, keeps four native inventory boxes, exposes a safe eight-stage selector, integrates with native text and palettes, and preserves normal save/progression flow outside two narrow bypasses.

## Why stage-local randomization came first

Pickup resource selector `+0x24` is local to the loaded stage resource file. Same-stage identities can move as a unit. Cross-stage placement requires importing resource bundles, creating selector capacity, updating file bounds, preserving presentation/callback behavior, and budgeting the arena. A Fire/Prison-key proof established feasibility, but a general planner does not exist. The production boundary therefore remains a separate permutation per stage.

## Persistence and lifecycle conclusion

Ordinary collection state is best owned by a versioned runtime bitset rather than trusting reconstructed stage records. Inventory capacity is extended without replacing the game's ten-slot consumers: four backing boxes feed one live window. Foreign keys are masked in the live view and preserved in backing storage. These systems have representative runtime coverage across stages, but Game Over/new-game edges remain an explicit gap.

## Enemy conclusion

Ordinary encounters are stream-driven and share a constructor. Type-only substitution works when the destination stage already has the resource. Missing residency freezes construction. A bounded Temple-monk import into Fire proved foreign allocation and spawning, but missing death presentation shows that model residency is not the entire compatibility contract. Bosses use distinct scripts/constructors and are excluded.

## Progression conclusion

Native XP thresholds and award/save paths are mapped. A bounded Temple proof replaced three of the four ordinary Herbs with non-inventory progression pickups while leaving one vanilla Herbs control. The first two tested pickups advanced to `85` and `258`, unlocked the expected second tier, and combat/kill/combo XP stayed disabled. Production still targets nine total progression rewards through `7354`; the proof is not production-safe because of cave conflicts, state ownership, and unfinished art.

## Player-action conclusion

Reverse Elbow research exposed critical corrections: player velocity is `0x8002B1EC`; `0x8004B82C/0x8004CC14` are projectile paths; action callbacks installed through `0x80032CD4` cannot return normally; `0x8004AA4C` is a scheduler transfer shim; native action roots use lock `0x800BF308`. v6 achieved repeatable lifecycle stability. v8 did not achieve intended speed, pass-through, or diagnostics.

## Portability conclusion

PS1 shares the 84-record pickup boundary, `0x30` grammar, ten-slot inventory concept, enemy-stream architecture, and several fighter descriptor offsets. It has different functions, files, overlays, save layout, and free-space constraints. N64 discoveries are search signatures, not patches.

## Current decision boundaries

| Safe to build on | Requires a new bounded proof/planner |
|---|---|
| Guarded clean-ROM pipeline | Cross-stage/global item pool |
| Eight-stage selector and scoped flow bypasses | Enemy mixed-roster production |
| All 84 stage-local pickup records | Boss randomization |
| V1 pickup persistence and four-box backing | XP production allocation/state/art |
| Native text and source-palette transform | General textured UI |
| Corrected player-action primitives | Finished foreign special move |
| PS1 static architecture | PS1 runtime port |

Use the sidebar registries and stage catalogs for exact values; this page is the cross-domain model, not a substitute for their caveats.
