# Fighter recompiler — amendment 1 (milestone 6 decisions)

> **Scope:** the owner's milestone-6 decisions, as the [Fighter recompiler plan](Fighter-Recompiler-Plan) asks ("the decision is recorded as an amendment page"). Progress lives on [Fighter recompiler status](Fighter-Recompiler-Status).

**Date:** 2026-11-13, after Reptile shipped as a product Fighter option (PRs #209, #210).

## Decisions

| Question (plan, milestone 6) | Decision | Source |
|---|---|---|
| Which fighters come next | **Rayden** (MKT fighter 24) | Owner: "Can we continue with Rayden, now?" |
| Rayden's power slots | Lightning (D,F + LP) → Ice Blast; Teleport (D,U) → Directional Ice; reversed Lightning (D,B + LP) → Air Ice Blast; Torpedo (B,B,F) → Ice Clone; Shocker (hold HP, release) → Ice Shatter; Slide and Super Slide stay; Freeze on Contact removed; Polar Blast deferred (as for every fighter) | Assistant proposal, owner: "The Power slots are okay" |
| Whether automatic recognition of MKT machine code is worth building | Not decided; default **not yet** (moves keep being read with the reading aid and written as data) | Assistant proposal; no owner answer yet |
| Which Sektor legacy modules to migrate | Not decided; default **not yet** | Assistant proposal; no owner answer yet |

## Notes

- The plan's guidance was that fighters sharing images and behaviours with done ones (robots with Sektor, ninjas with Reptile) are cheaper. Rayden shares neither; his teleport can use Sektor's teleport as a reference and his lightning the generic projectile.
- Rayden follows Reptile's milestone-4 steps: body, inputs, specials one by one, icons and description, then the product option.
