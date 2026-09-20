# XP and progression

XP progression is a runtime-confirmed proof and proposed mode, not a production feature.

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

## Intended production semantics

The proposed mode has exactly nine rewards and uses a dedicated RNG namespace. Each reward advances to the next native threshold rather than adding an arbitrary fixed amount. A custom award callback avoids inventory insertion, evaluates/clamps the native tier, caps at the ninth value, and restores progression state once per appropriate lifecycle boundary.

Normal ordinary-pickup randomization must remain independent: progression rewards need their own catalog/state and must not consume ordinary pickup RNG or persistence bits.

## Blockers

The proof's temporary cave conflicts with current production ownership. Its resource placement and presentation are not production-safe, the final visual is not built, and save/new-game/Game Over behavior needs a defined versioned state contract. Do not copy the proof offsets directly into the patch pipeline.

A production change must allocate code/data through the native runtime layout, guard every hook, separate nine progression flags from the 84 ordinary pickup flags, preserve native save behavior, add deterministic tests, and complete a full nine-tier runtime run.


## Failed productionization attempt — 2026-09-20

**Rejected / failed:** the first attempted production integration (runtime-layout V2) was merged before manual runtime validation and was immediately rolled back.

The attempted layout expanded the reloadable payload from `0x200` to `0x300` bytes and moved persistent state from `0x801AF620` to `0x801AF720`, then added a progression restore call at the pickup-manager stage reconstruction boundary.

Manual Temple validation failed before gameplay became visible:

- the Mission Objective screen completed;
- Temple music loaded;
- the game then hung as the stage was about to be displayed;
- no progression pickup was collected, so the failure occurs before the new pickup callback is exercised.

The exact failing component is not yet established. The leading bounded candidates are the new stage-entry progression restore path versus the V2 code/state repartition itself. Do not treat either as confirmed until isolated by disposable proof ROMs.

The web/CLI production pipeline has been restored to the previously runtime-confirmed V1 allocation while this is investigated.

### Required promotion discipline

New native runtime behavior must now be validated in a disposable ROM supplied directly for manual testing **before** it is enabled in the normal browser/CLI patch pipeline. CI/static composition is not sufficient evidence that a new runtime hook is production-safe.


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

### Diagnostic B hypothesis

The restore helper wrote persistent XP, called native tier evaluator `0x80074FBC`, then ran the existing four-box reconstruction. The leading hypothesis is that the tier evaluator is unsafe this early in stage initialization.

Diagnostic B keeps the same restore helper entry and persistent-XP write but NOPs only the tier-evaluator setup/call. It then continues into the existing four-box reconstruction. This is a disposable proof ROM only and is not enabled in production.
