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
| Pickup-driven XP progression | Production beta | Bounded Temple behavior runtime-confirmed; production V2 allocation, nine deterministic Herbs rewards, XP suppression/caps and persistence composition are Implementation/CI-confirmed; manual production runtime validation pending |
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
| Temple XP progression proof | Three proof pickups plus one vanilla Herbs control; no combat XP; tested pickups reached `85` then `258`; second tier unlocked; no inventory award | Generalized into production; final art and full nine-tier runtime coverage pending |
| Reverse Elbow v6 | Repeated execution without whole-game hang | Movement, exclusivity, hit behavior, animation, pass-through, and UI diagnostics remain incomplete |

## Latest runtime findings

The Temple XP proof remains the runtime basis: combat does not award XP; collecting proof rewards sets XP to 85 then 258; the second threshold activates the next tier; nothing enters inventory. Production no longer uses the proof cave. Runtime V2 stays inside the existing 1 KiB reservation, adds exactly nine deterministic post-shuffle Herbs rewards in an isolated RNG namespace, stores progression separately from ordinary pickup bits, raises main-stage caps to 20000, and composes XP restore with four-box stage reconstruction. The initial production rewards retain normal Herbs presentation; bright-blue-with-bronze-handle art remains pending.

Reverse Elbow v8 did not visibly deliver the intended changes. Sub-Zero still does not pass through enemies, forward motion stops when attacking even though the `L 1` diagnostic remains unchanged, direction/jump/crouch are locked while attacks remain possible, the Y gate behaves normally against a jumping enemy, speed still appears very slow rather than four times faster, and the expanded HUD text did not appear. Treat v6 lifecycle stability as the durable result; v7/v8 movement and diagnostic claims are not confirmed.

## Pending priorities

1. Full seeded native pickup playthrough and lifecycle edge coverage.
2. Manually runtime-validate the production V2 XP progression path across one normal stage transition.
3. Build an explicit resource-import planner before cross-stage item or enemy pools.
4. Trace imported-enemy death/despawn dependencies.
5. Rework Reverse Elbow from confirmed scheduler/action primitives and observable diagnostics.
6. Establish and validate one shared Game Over/new-run reset hook for pickup persistence, progression and four-box/run state.

## Explicit exclusions

Bosses and scripted encounters are not ordinary-enemy entries. The Temple Map is not an ordinary pickup. Zero resource slots are logical selectors, not free physical storage. PS1 addresses are not N64 addresses. Proof ROM patches and archive handoffs are not silently part of the product pipeline.
