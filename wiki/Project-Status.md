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
| Temple XP progression | Three proof pickups plus one vanilla Herbs control; no combat XP; tested pickups reached `85` then `258`; second tier unlocked; no inventory award; normal and progression pickups coexist | Production-safe storage, nine-reward generation, final art, seed integration, persistence/lifecycle design |
| Reverse Elbow v6 | Repeated execution without whole-game hang | Movement, exclusivity, hit behavior, animation, pass-through, and UI diagnostics remain incomplete |

## Latest runtime findings

The Temple XP proof is confirmed: combat does not award XP; collecting the proof rewards sets XP to `85` and then `258`; the second threshold activates the next tier; nothing is added to inventory; ordinary pickups and progression rewards coexist. The proof model appears pale blue-grey and Herbs-like. The desired final presentation is a bright-blue body with a bronze handle.

A first production-layout attempt was **Rejected / failed** on 2026-09-20: Temple reached the Mission Objective screen and loaded stage music, then hung just before gameplay appeared. Production was rolled back to runtime V1.

Follow-up Diagnostic A is **Runtime-confirmed**: with the progression stage-entry restore helper bypassed, the same V2 allocation and generated progression callbacks loaded Temple normally. XP 85 and 258 rewards worked, special-move tiers unlocked, combo EXPERIENCE stayed suppressed, combat awarded no XP, and normal/progression Herbs coexisted with identical Herbs graphics. The failure is therefore isolated to the progression restore-helper path, not the V2 allocation or pickup callback path.

Reverse Elbow v8 did not visibly deliver the intended changes. Sub-Zero still does not pass through enemies, forward motion stops when attacking even though the `L 1` diagnostic remains unchanged, direction/jump/crouch are locked while attacks remain possible, the Y gate behaves normally against a jumping enemy, speed still appears very slow rather than four times faster, and the expanded HUD text did not appear. Treat v6 lifecycle stability as the durable result; v7/v8 movement and diagnostic claims are not confirmed.

## Pending priorities

1. Full seeded native pickup playthrough and lifecycle edge coverage.
2. Isolate the failed XP productionization with disposable ROMs; do not re-enable it in browser/CLI until manual runtime validation passes.
3. Build an explicit resource-import planner before cross-stage item or enemy pools.
4. Trace imported-enemy death/despawn dependencies.
5. Rework Reverse Elbow from confirmed scheduler/action primitives and observable diagnostics.
6. Validate Game Over/new-game behavior for persistence and four-box state.

## Explicit exclusions

Bosses and scripted encounters are not ordinary-enemy entries. The Temple Map is not an ordinary pickup. Zero resource slots are logical selectors, not free physical storage. PS1 addresses are not N64 addresses. Proof ROM patches and archive handoffs are not silently part of the product pipeline.
