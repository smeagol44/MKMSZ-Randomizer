# Fighter recompiler — amendment 1 (milestone 6 decisions)

> **Scope:** the owner's milestone-6 decisions, as the [Fighter recompiler plan](Fighter-Recompiler-Plan) asks ("the decision is recorded as an amendment page"). Progress lives on [Fighter recompiler status](Fighter-Recompiler-Status).

**Date:** 2026-11-13, after Reptile shipped as a product Fighter option (PRs #209, #210).

## Decisions

| Question (plan, milestone 6) | Decision | Source |
|---|---|---|
| Which fighters come next | **Rayden** (MKT fighter 24) | Owner: "Can we continue with Rayden, now?" |
| Rayden's power slots | Lightning (D,F + LP) → Ice Blast; Teleport (D,U) → Directional Ice; reversed Lightning (D,B + LP) → Air Ice Blast; Torpedo (B,B,F) → Ice Clone; Shocker (hold HP, release) → Ice Shatter; Slide and Super Slide stay; Freeze on Contact removed; Polar Blast deferred (as for every fighter) | Assistant proposal, owner: "The Power slots are okay" |
| Ice cost of movement abilities | **None**, as a general rule for every fighter (move programs mark them `"movement": true`; first: Rayden's torpedo; Reptile's elbow dash and Sektor's teleport were already free) | Owner, 2026-11-24: "as a general rule, let's make moving abilities not consume mana/energy/ice" |
| Whether automatic recognition of MKT machine code is worth building | **Yes (2026-11-25).** Build a generator that writes move programs from MKT's code, checked against the accepted Reptile and Rayden programs; owner adjustments stay in the fighter descriptions. Rayden's remaining moves (teleport, reversed Lightning, Shocker) are its first unseen moves. Current projectiles stay as they are until the generator can build several fighters for testing them together (owner: Acid Spit's hit effect is sometimes misplaced). | Owner: "Let's go with option A" (2026-11-25; earlier default "not yet") |
| Rayden's reversed lightning: MKT's screen wrap (the bolt leaves one edge and re-enters past the other) on the host's 3D camera | **MKT's wrap** (2026-11-26) | Owner, generator step 5 |
| Facing at the end of Rayden's reversed lightning and after his teleport (MKT faces the opponent in both) | **The teleport faces the opponent; the reversed lightning turns back** to the way he faced before throwing (2026-11-26) | Owner, generator step 5 |
| Which Sektor legacy modules to migrate | **All of them** (2026-11-27): Sektor is to be built by the generic pipeline like Reptile and Rayden (SMRE step 3) | Owner: "before doing any new character, I want these 3 characters to be built entirely by the generator" |
| The generator's name | **Special Move Recompile Engine (SMRE)** (2026-11-27): the whole pipeline (MKT reading, the move-program language, the MKMSZ back end) | Owner |
| Reptile's Forceballs turning to the opponent at the start (the accepted hand-written programs did; MKT does not) | **Pure MKT: no turn** (2026-11-27) | Owner: "let's remove it and have it being pure MKT" |
| What comes before new fighters | **Sektor, Reptile and Rayden built entirely by SMRE** (2026-11-27), in three steps: (1) the build writes the programs and their command blocks with SMRE from the MKT command records; (2) a grab rule (Rayden's Shocker); (3) Sektor migrated from his legacy modules | Owner, assistant proposal: "Yes, please start" |

## Notes

- The plan's guidance was that fighters sharing images and behaviours with done ones (robots with Sektor, ninjas with Reptile) are cheaper. Rayden shares neither; his teleport can use Sektor's teleport as a reference and his lightning the generic projectile.
- Rayden follows Reptile's milestone-4 steps: body, inputs, specials one by one, icons and description, then the product option.
