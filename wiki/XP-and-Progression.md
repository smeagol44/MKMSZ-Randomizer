# XP and progression

XP progression is a production feature built from the runtime-confirmed Temple proof and Diagnostic B lifecycle validation. The full nine-tier generated-run coverage is still pending.

## Native XP system

| Purpose | Address |
|---|---:|
| Current XP | `0x8011200C` |
| Central award function | `0x8002E104` / ROM `0x2ED04` |
| Direct store sites | `0x800540E8`, `0x80057160`, `0x8005722C` |
| Tier evaluator/clamp | `0x80074FBC` / ROM `0x75BBC` |
| Signed cap table | `0x800A63FC` / ROM `0xA6FFC` |
| Save-load restore | `0x80078A18`; save record `+0x7C` |

The confirmed thresholds are:

| Tier reached | XP |
|---:|---:|
| 1 | 85 |
| 2 | 258 |
| 3 | 834 |
| 4 | 1410 |
| 5 | 2323 |
| 6 | 3315 |
| 7 | 4503 |
| 8 | 5911 |
| 9 | 7354 |

The final value corrects a legacy Lua comment that said `7345`; the actual `0x1CBA` value is `7354`.

## Temple bounded proof

The disposable proof changed Temple ordinary Herbs #1, #3, and #4 into progression pickups while leaving Herbs #2 completely vanilla as a brown control. Only the first two progression pickups needed to be collected to validate the core behavior. Runtime results:

- defeating enemies, kills, and combos did **not** award XP;
- the combo `HITS` message remained while the `EXPERIENCE` line was removed;
- first tested progression pickup set XP to `85`;
- second tested progression pickup set XP to `258`;
- the second threshold activated the next expected special-move tier;
- progression pickups added nothing to inventory;
- the untouched Herbs control remained a normal inventory Herbs pickup;
- normal and progression pickups coexisted and were visually distinguishable;
- Temple displayed max XP `20000`.

The experimental progression model is pale blue-grey and visually Herbs-like. The intended final presentation is a bright-blue Herbs body while retaining the bronze/gold-looking handle. That visual refinement is separate from the confirmed progression logic.

## Production semantics

The production mode has exactly nine rewards and uses a dedicated RNG namespace. Each reward advances to the next native threshold rather than adding an arbitrary fixed amount. A custom award callback avoids inventory insertion, evaluates/clamps the native tier, and caps at the ninth value. A separate stage-init helper restores persistent XP without evaluating tiers at that boundary.

Normal ordinary-pickup randomization remains independent of progression selection and count/XP state. Acquisition still marks the physical ordinary location as collected; progression count/XP use separate words and progression selection uses its own RNG namespace.

## Production allocation and state

Production does not reuse the disposable proof cave. Runtime V2 keeps the existing 1 KiB reservation but repartitions it as:

- reloadable payload code: `0x801AF420..0x801AF71F` (0x300 bytes);
- persistent state: `0x801AF720..0x801AF81F` (0x100 bytes).

Progression uses state `+0x40` for acquired reward count and `+0x44` for persistent XP, separate from the 84 ordinary-pickup persistence bits at `+0x20..+0x3C`.

Nine rewards are selected only after the ordinary 84-location layout is finalized, using the independent domain `MKMSZR:PROGRESSION:HERBS:V1\0`. Only generated Herbs locations are eligible and only their callback word is replaced, so the ordinary shuffle is not perturbed and no foreign resource import is required.

The acquisition callback advances to the next threshold, stores count/XP, writes current XP, and calls native tier evaluator `0x80074FBC` at the safe pickup-acquisition point. It does not add an inventory item.

At stage initialization, production restores the persistent XP value and then performs the existing four-box reconstruction. It deliberately **does not** call the native tier evaluator there.


## Failed productionization attempt — 2026-09-20

**Rejected / failed:** the first attempted production integration (runtime-layout V2) was merged before manual runtime validation and was immediately rolled back.

The attempted layout expanded the reloadable payload from `0x200` to `0x300` bytes and moved persistent state from `0x801AF620` to `0x801AF720`, then added a progression restore call at the pickup-manager stage reconstruction boundary.

Manual Temple validation failed before gameplay became visible:

- the Mission Objective screen completed;
- Temple music loaded;
- the game then hung as the stage was about to be displayed;
- no progression pickup was collected, so the failure occurs before the new pickup callback is exercised.

At that point the exact failing component was not established. The leading candidates were the new stage-entry progression restore path and the V2 code/state repartition itself. Diagnostic A and B below subsequently isolated the stage-init tier-evaluator call.

The web/CLI pipeline was temporarily restored to the previously runtime-confirmed V1 allocation during that investigation. Diagnostic B later established the accepted V2 production behavior.

### Historical validation lesson

The failed integration passed static/CI composition checks but hung at a native stage-init boundary. Disposable Diagnostic A and B supplied the missing runtime evidence. This demonstrates the limit of CI as evidence for game-state-dependent behavior.


## Diagnostic A runtime isolation — 2026-09-20

**Runtime-confirmed:** disposable Diagnostic A using seed `BCBDBF` loaded Temple normally and exercised the production-style V2 progression generation/callback path without the new progression stage-entry restore helper.

Observed:
- Temple reached normal gameplay with no hang;
- first generated progression Herbs awarded XP 85 and unlocked the first progression special move;
- enemy combos showed `HITS` only, with no `EXPERIENCE` text;
- combos and enemy kills awarded no XP;
- the second Herbs was a normal Herbs pickup;
- the third Herbs awarded XP 258 and unlocked the second progression special move;
- all three Herbs used the same ordinary Herbs graphics;
- no other issue was observed during this bounded test.

Diagnostic A differs from the failed production integration at the stage-entry resume sequence only: the failed build JALs the progression restore helper, while Diagnostic A JALs the pre-existing four-box load/mask wrapper directly. V2 allocation, progression callbacks, reward generation, XP-store suppression, combo-text suppression and cap edits are otherwise unchanged.

Therefore the V2 repartition and pickup callback path are no longer implicated by this bounded route. The failure is isolated to the progression restore-helper path executed during pickup-manager stage initialization.

## Diagnostic B runtime confirmation — 2026-09-20

**Runtime-confirmed:** Diagnostic B removed only the tier-evaluator call from the stage-entry restore helper while keeping persistent-XP restoration and the normal four-box reconstruction.

Observed with seed `BCBDBF`:

- Temple loaded normally;
- first and third generated progression Herbs reached XP 85 and 258 and unlocked the first two special-move tiers;
- Temple completed normally;
- Wind loaded with XP still at 258 and both unlocked moves retained;
- after quitting to the title menu and entering Fire directly, XP remained 258 and both moves were still available;
- no issue was detected on this bounded route.

This isolates the original hang to invoking native tier evaluator `0x80074FBC` during pickup-manager stage initialization. That call is **Rejected / failed at stage-init timing**. The evaluator remains valid and runtime-confirmed on the progression-pickup acquisition path.

Diagnostic B behavior is the production design.

## Remaining limits

- All nine generated progression rewards are implementation/CI-confirmed, but a full nine-tier runtime run is still pending.
- Production progression pickups currently retain ordinary Herbs graphics. Bright-blue Herbs body with a bronze/gold-looking handle remains a visual refinement.
- Game Over/new-run reset behavior remains pending as part of the shared MKMSZR lifecycle work.


## 1.0 required-Power-Upgrades rule

The full randomizer should retain a seed-specific required number of Power Upgrades, as in the legacy Lua concept. This is separate from the fixed nine native thresholds/rewards that exist in the world.

Requirements:

- generate the required count deterministically from its own RNG namespace;
- do not let rejected global-layout attempts change that required count;
- show the requirement in the randomizer HUD;
- include the requirement in the whole-run solver's completion predicate;
- preserve the current runtime-confirmed threshold behavior for each collected reward.

The exact min/max policy remains to be finalized with the global solver.
