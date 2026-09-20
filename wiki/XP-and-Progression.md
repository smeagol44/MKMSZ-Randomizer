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

## Temple nine-reward proof

The proof introduced nine separate Herbs-like progression rewards while retaining the stage's ordinary pickups. Runtime results:

- defeating enemies did **not** award XP;
- first reward set XP to `85`;
- second reward set XP to `258`;
- the second threshold activated the next progression tier;
- rewards added nothing to inventory;
- ordinary and progression pickups coexisted in the stage;
- proof collection/state behavior worked through the tested sequence.

The current model is pale blue-grey and visually Herbs-like. The intended final asset is a bright-blue body with a bronze handle.

## Intended production semantics

The proposed mode has exactly nine rewards and uses a dedicated RNG namespace. Each reward advances to the next native threshold rather than adding an arbitrary fixed amount. A custom award callback avoids inventory insertion, evaluates/clamps the native tier, caps at the ninth value, and restores progression state once per appropriate lifecycle boundary.

Normal ordinary-pickup randomization must remain independent: progression rewards need their own catalog/state and must not consume ordinary pickup RNG or persistence bits.

## Blockers

The proof's temporary cave conflicts with current production ownership. Its resource placement and presentation are not production-safe, the final visual is not built, and save/new-game/Game Over behavior needs a defined versioned state contract. Do not copy the proof offsets directly into the patch pipeline.

A production change must allocate code/data through the native runtime layout, guard every hook, separate nine progression flags from the 84 ordinary pickup flags, preserve native save behavior, add deterministic tests, and complete a full nine-tier runtime run.
