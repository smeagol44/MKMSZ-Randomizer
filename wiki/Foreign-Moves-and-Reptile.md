# (Old) Foreign moves and Reptile

> **Historical/superseded direction:** this page documents the behavioral-recreation phase. Current genuine donor-port findings and the MKT→MKMSZ adapter design are owned by [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer). Retain this page as proof history; do not treat its "conceptual transfer only" boundary as current.

The selected donor concept is Mortal Kombat Trilogy N64 Reptile's Reverse Elbow / Elbow Dash. This is exploratory and not a production randomizer feature.

## Why Reverse Elbow was chosen

Slide was rejected as the first donor proof because MKMSZ already has a native Slide. Reverse Elbow is genuinely foreign to Mythologies while avoiding the extra dependencies of Acid Spit, Force Ball, Invisibility, or other projectile/effect-heavy moves.

Its dependency footprint is mostly:

1. command recognition;
2. horizontal player motion;
3. one zero-damage first contact;
4. a short victim hold;
5. pass-through / crossover;
6. facing reversal;
7. a return animation;
8. one damaging return strike;
9. normal action cleanup.

## MKT donor command

Source-lineage material in the public `Zoltan45/mktrilogy` tree identifies the Reptile Low Kick special descriptor as:

- button: Low Kick;
- condition: ground-only;
- extra condition callback: none;
- input window: `0x10`;
- one facing: Right, Left;
- opposite facing: Left, Right.

Because the matcher mirrors these direction tokens by fighter facing, the semantic command is:

**Back → Forward + Low Kick**

The source-level recognition chain is:

```text
Reptile Low Kick close handler
-> secret-move search
-> facing-aware history match
-> restricted transfer
-> do_reptile_dash
-> body-propell action PROP_REP_DASH
```

Donor action constants:

| Meaning | Value |
|---|---:|
| propelled action | `PROP_REP_DASH = 0x17` |
| fighter action/state | `ACT_REPTILE_DASH = 0x216` |
| return animation index | `ANIM_REP_DASH = 0x0B` in animation table 2 |

## Donor choreography

The MKT behavior is:

```text
set Reptile dash action
-> use ordinary run animation
-> accelerate toward opponent
-> strike/contact 0x15
-> on contact, continue past victim
-> stop / brief pause
-> face opponent
-> select ANIM_REP_DASH
-> accelerate back
-> strike/contact 0x16
-> stop
-> recover
```

The first contact is intentionally **zero damage**. Its strike record uses an approximately `0x2B,0x09` offset, `0x22 x 0x6E` box, reaction selector `0x74`, zero damage, and squeeze-style flags. Reaction `0x74` routes to a Reptile-specific victim hold: airborne victims are rejected, grounded victims enter reaction/stance state for about 20 ticks, then recover normally.

The return strike is the damaging hit. Its record uses an approximately `0x44,0x0B` offset, `0x27 x 0x3C` box, reaction selector `0x24`, damage encoding `0x0D03`, and squeeze-style flags. Reaction `0x24` is shared/generic rather than Reptile-exclusive.

## Donor animation dependency

The return animation is favorable for transplantation because the source builds it from shared male-ninja combo frames rather than Reptile-only art:

```text
SCCOMBO10
SCCOMBO11
SCCOMBO12
end
SCCOMBO11
SCCOMBO10
end
```

This does **not** prove MKMSZ has byte-identical animation resources, but it means the donor move is conceptually closer to shared male-ninja behavior than to a Reptile-only effect stack.

## Shared MKT male-ninja architecture

MKT distinguishes male ninjas through a combination of:

- fighter/character ID;
- character-specific close/special handlers;
- shared male-ninja strike tables;
- shared animation heaps with special indices;
- generic fighter movement/reaction machinery.

The shared strike table includes entries for Slide, orb/spit, Scorpion spear/teleport, and the two Reptile dash contacts. This is one reason selective special-move adaptation is more plausible than copying an entire donor binary.

## Donor evidence boundary

The donor-side information above comes from symbolic/source-lineage material. Exact retail-ROM offsets in the supplied MKT Rev. 2 binary were not required for this proof and are not claimed here. A dedicated MKT Ghidra project becomes useful only if later work needs exact retail resource tables, animation layout, multiple Reptile moves, or whole-fighter transplantation.

## What transfers conceptually

The MKT command/choreography transfers as a behavioral specification. MKMSZ must use its own:

- special-move descriptor grammar;
- semantic input tokens;
- scheduler/context transfer;
- player velocity;
- animation selection;
- collision/strike dispatch;
- victim reaction machinery;
- action lock and cleanup.

No MKT machine code or resource blob is assumed binary-compatible.

The exact MKMSZ descriptor layout, corrected action helpers, scheduler semantics, proof versions, and current blockers are in [Player actions and special moves](Player-Actions-and-Special-Moves).

## Long-term significance

A bounded, stable Reverse Elbow would validate adding truly foreign Mortal Kombat behavior through native MKMSZ control/combat systems. It would be a stepping stone toward other moves and possibly whole-fighter work, but it would **not** by itself prove:

- imported projectile/effect resources;
- Invisibility/palette-state cleanup;
- exact MKT animation transplantation;
- arbitrary special-command tables;
- playable Reptile;
- whole-character replacement.

Those require separate resource, state, input, animation, and lifecycle proofs.
