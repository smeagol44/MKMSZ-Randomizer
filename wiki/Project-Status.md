# Project status

Last consolidated: 2026-09-20.

## Production pipeline

| System | Status | Evidence and limit |
|---|---|---|
| Clean-ROM validation and separate output | Production | Implementation/CI-confirmed; exact USA Rev. 0 hash only |
| Header checksum update | Production | Implementation/CI-confirmed |
| Compact eight-stage selector | Production | Runtime-confirmed A-button route; compact index maps to native `0,1,2,3,4,5,8,9` |
| 1 KiB arena reservation and native payload | Production | Runtime-confirmed load/execute; guarded bounds and tests |
| Ordinary-pickup persistence | Production beta | All eight stages runtime-confirmed at representative locations; all 84 are statically cataloged, not individually exhausted |
| Stage-local pickup randomization | Production beta | All 84 implemented and tested over 250 seeds; seed `TEST153` first Fire location predicted/rendered/awarded Shield; full run pending |
| Pickup-driven XP progression | Production beta | Diagnostic B runtime-confirmed V2 allocation, XP restore, 85/258 rewards, Temple -> Wind transition and title -> Fire retention; nine-reward/full-tier run pending |
| Four inventory boxes | Production beta | Runtime-confirmed switching, transition preservation, stage-key masking; Game Over/reset edge still pending |
| `BOX n OF 4` HUD text | Production | Runtime-confirmed native text path |
| Boot branding and seed phrase | Production | Guarded and CI-confirmed; phrase uses a dedicated deterministic namespace |
| Logo and selector-save bypasses | Production | Runtime-confirmed, legal screen and later/manual saves preserved |
| Outfit recoloring | Production | Runtime-confirmed palette modes; static TLUT source transform |
| Browser/CLI shared patch core | Production beta | CI builds/tests; release UX continues to mature |

## Confirmed proofs, not product features

| Proof | Result | Remaining work |
|---|---|---|
| Same-stage pickup substitution | Full identity tuple changes award and art | Generalized in current stage-local mode |
| Fire foreign Prison-key import | Relocated/expanded resource file plus dedicated callback works | Production resource planner, allocation policy, compatibility matrix |
| Fire ordinary enemy `0x0A -> 0x09` | Spawns and plays normally | Production policy and broader coverage |
| Temple monk imported into Fire | Model loads, enemy moves/fights/dies | Death/despawn presentation missing; arbitrary rosters unresolved |
| Temple XP progression proof | Three proof pickups plus one vanilla Herbs control established no-combat-XP and pickup-driven tiers | Generalized into the production Diagnostic B architecture; full nine-tier coverage and final art remain |
| Reverse Elbow v6 | Repeated execution without whole-game hang | Movement, exclusivity, hit behavior, animation, pass-through, and UI diagnostics remain incomplete |

## Latest runtime findings

The Temple XP proof is confirmed: combat does not award XP; collecting the proof rewards sets XP to `85` and then `258`; the second threshold activates the next tier; nothing is added to inventory; ordinary pickups and progression rewards coexist. The proof model appears pale blue-grey and Herbs-like. The desired final presentation is a bright-blue body with a bronze handle.

A first production-layout attempt was **Rejected / failed** on 2026-09-20: Temple reached the Mission Objective screen and loaded stage music, then hung just before gameplay appeared. Production was rolled back to runtime V1.

Follow-up Diagnostic A is **Runtime-confirmed**: with the progression stage-entry restore helper bypassed, the same V2 allocation and generated progression callbacks loaded Temple normally. XP 85 and 258 rewards worked, special-move tiers unlocked, combo EXPERIENCE stayed suppressed, combat awarded no XP, and normal/progression Herbs coexisted with identical Herbs graphics.

Diagnostic B then removed only the early tier-evaluator call from the restore helper. It is **Runtime-confirmed** through Temple completion, Temple -> Wind with XP 258/two moves retained, and title-menu -> Fire with the same XP/moves retained. The original hang is therefore attributed to calling the native tier evaluator too early during stage initialization. Production now uses Diagnostic B behavior: restore XP at stage entry, but evaluate tiers only when a progression pickup is collected.

Reverse Elbow v8 did not visibly deliver the intended changes. Sub-Zero still does not pass through enemies, forward motion stops when attacking even though the `L 1` diagnostic remains unchanged, direction/jump/crouch are locked while attacks remain possible, the Y gate behaves normally against a jumping enemy, speed still appears very slow rather than four times faster, and the expanded HUD text did not appear. Treat v6 lifecycle stability as the durable result; v7/v8 movement and diagnostic claims are not confirmed.

## 1.0 required scope

The 1.0 randomizer is not considered complete with stage-local shuffling alone. Required before 1.0:

1. **Global cross-stage item randomization.** Items must be able to appear in other main stages, requiring a production resource-import/materialization planner rather than copying stage-local resource selectors verbatim.
2. **Global deterministic shuffling.** Keep the current stable seeded Fisher-Yates approach, but apply it to the global logical item pool rather than eight independent stage pools.
3. **Whole-run solvability validation.** Reject seeds whose progression graph cannot reach the required end-state. Use current stage/location requirements as source of truth; the legacy Lua fixed-point solver is a useful design reference but its location rules are stale/incomplete. Rejected attempts must be derived deterministically from the original seed plus an explicit attempt index, so regenerating the same seed always produces the same accepted layout even when several attempts are required.
4. **Randomizer HUD/UI.** At minimum expose the run information needed to play the seed: check progress, required Power Upgrades/current progression status, inventory-box/page state, and useful pickup feedback. The legacy Lua overlay is a reference for semantics, not a native renderer implementation.
5. **Run-resource lifecycle.** Determine and preserve HP, lives, and continues correctly across stage transitions and direct selector routes; define intended Game Over/new-run resets.
6. **Difficulty hard-lock.** Very Hard must be enforced as a run invariant rather than only selected as a startup default.
7. **Final runtime coverage.** Complete a representative full global seed, including all nine progression tiers and the major lifecycle boundaries.

Open Temple Map work: the legacy Lua global pool included the scripted Map as an 85th check. For 1.0, investigate separating the Map inventory reward from the Temple elevator/exit trigger so the elevator can still be raised correctly even when the Map item itself is shuffled elsewhere. Also prevent the Map item from being removed on the Temple -> Wind transition, which is stock behavior today.

## Pending priorities

1. Build the production cross-stage item materializer so every randomized pickup uses the actual randomized item's graphics/resource bundle and award behavior. Current next proof: recycle a pickup-owned Prison selector after removing all of its Herbs users, then import Water's self-contained embedded Potion bundle. External-resource-ID transplantation remains unresolved after a glitched Fire-Potion proof.
2. Replace stage-local generation with a global deterministic shuffle plus whole-run solver, including deterministic retry attempts and a deterministic per-seed required-Power-Upgrades target.
3. Build the native randomizer HUD around the finalized global-run state.
4. Resolve Temple Map trigger/item separation and cross-stage persistence; then HP/lives/continues persistence, Game Over/new-run reset, and Very Hard enforcement.
5. Run full-seed 1.0 validation.
6. Post-1.0: enemy randomization/resource compatibility, imported-enemy death/despawn, and Reverse Elbow.

## Explicit exclusions

Bosses and scripted encounters are not ordinary-enemy entries. The Temple Map is not an ordinary pickup and needs an explicit 1.0 inclusion decision if it is to become a global check. Zero resource slots are logical selectors, not free physical storage. PS1 addresses are not N64 addresses. Proof ROM patches and archive handoffs are not silently part of the product pipeline. Enemy randomization and Reverse Elbow are not 1.0 blockers.
