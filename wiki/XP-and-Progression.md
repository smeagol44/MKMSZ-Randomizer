# XP and progression

The pickup-driven XP system has a runtime-confirmed bounded Temple proof and is now implemented in the production patch pipeline. The production composition is **Implementation/CI-confirmed** until the manual runtime test below is completed.

## Native XP system

| Purpose | Address |
|---|---:|
| Current XP | `0x8011200C` |
| Central award function | `0x8002E104` / ROM `0x2ED04` |
| Central XP store | ROM `0x2EDA8` |
| Direct XP stores | ROM `0x54CE8`, `0x57D60`, `0x57E2C` |
| Tier evaluator/clamp | `0x80074FBC` / ROM `0x75BBC` |
| Signed cap table | `0x800A63FC` / ROM `0xA6FFC` |
| Combo EXPERIENCE label/value calls | ROM `0x63704`, `0x63724` |
| Save-load restore | `0x80078A18`; save record `+0x7C` |

Native tier thresholds are `85, 258, 834, 1410, 2323, 3315, 4503, 5911, 7354`. The final value is `0x1CBA = 7354`; the legacy Lua comment saying 7345 is incorrect.

## Runtime-confirmed Temple proof

The disposable proof changed Temple ordinary Herbs #1, #3, and #4 into progression pickups while leaving Herbs #2 vanilla. Only the first two progression pickups were required to validate the core behavior.

Runtime-confirmed:
- combat, enemy kills and combos awarded no XP;
- combo `HITS` remained while the `EXPERIENCE` line was removed;
- the first tested progression pickup advanced XP to 85;
- the second advanced XP to 258 and unlocked the expected second special-move tier;
- progression pickups did not enter inventory;
- normal Herbs and progression pickups coexisted;
- Temple displayed max XP 20000;
- fighting after the progression pickups still did not change XP.

The proof's pale blue-grey Herbs-like presentation remains only a visual experiment. Desired later art is a bright-blue Herbs body with a bronze/gold-looking handle.

## Production implementation

Production does **not** reuse the proof cave. Runtime V2 repartitions only the already-reserved 1 KiB arena prefix:
- reloadable code: `0x801AF420..0x801AF71F` (0x300 bytes);
- persistent state: `0x801AF720..0x801AF81F` (0x100 bytes).

The progression extension occupies payload `+0x200..+0x2FF`. Persistent progression state is separate from ordinary pickup bits:
- state `+0x40`: number of progression rewards acquired;
- state `+0x44`: persistent XP value.

Generation order is deliberate:
1. generate the normal stage-local 84-pickup layout unchanged;
2. enumerate locations whose generated identity is Herbs;
3. shuffle only that candidate list with domain `MKMSZR:PROGRESSION:HERBS:V1\0`;
4. select exactly nine;
5. change only their callback pointer to the MKMSZR progression callback.

This cannot perturb the ordinary pickup permutation. Each selected pickup retains its destination-stage Herbs type/resource/presentation tuple, so no cross-stage resource import is needed. The first production version therefore looks like ordinary Herbs; visual differentiation is a separate pending refinement.

The callback advances by acquisition count to the next threshold, stores both count and XP, writes native current XP, invokes the native tier evaluator, and plays the normal pickup sound without calling the inventory-add routine. Ordinary pickup persistence independently records that physical location as collected.

At the existing stage reconstruction boundary, MKMSZR restores progression XP, refreshes the native tier state, then preserves the four-box live-inventory reconstruction before the pickup manager resumes.

## Static patches

Production guards and NOPs all four mapped normal gameplay XP stores:
- ROM `0x2EDA8`;
- ROM `0x54CE8`;
- ROM `0x57D60`;
- ROM `0x57E2C`.

Only the two combo EXPERIENCE render calls at `0x63704` and `0x63724` are suppressed. The earlier HITS render path is untouched.

Main-stage cap entries for native stages `0,1,2,3,4,5,8,9` are guarded and set to 20000, safely above the final threshold 7354.

## Lifecycle status

Normal stage-transition restoration is implemented through the existing stage reconstruction path.

Runtime V2 is versioned as state version 2; an invalid/old header clears the V2 state and initializes a fresh header. This safely handles incompatible runtime-state layouts.

A dedicated Game Over/new-run reset hook is still **Pending** project-wide. There is not yet a proven production-safe boundary that should clear MKMSZR persistent state without risking normal transitions or selector routes. The progression implementation therefore does not invent one; it shares the same documented lifecycle limitation as ordinary pickup persistence and four-box state.

## Validation status

Implementation/CI-confirmed:
- isolated deterministic nine-reward generation;
- exact thresholds;
- callback-only Herbs conversion;
- separate state layout;
- cap/store/render guards;
- patch ordering after ordinary shuffle and four-box composition;
- browser/CLI use of the same production pipeline.

Pending runtime confirmation:
- production V2 payload/state behavior in emulator;
- progression XP restoration across a normal stage transition;
- all nine tiers in a generated run;
- Game Over/new-run reset once the shared lifecycle hook is implemented.
