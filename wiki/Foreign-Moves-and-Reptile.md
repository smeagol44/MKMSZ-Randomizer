# Foreign moves and Reptile

The selected donor concept is Mortal Kombat Trilogy N64 Reptile's Reverse Elbow/Elbow Dash. This is exploratory and not a production randomizer feature.

## Donor choreography

The MKT source-lineage descriptor uses Low Kick, a ground-only condition, input window `0x10`, and mirrored Back → Forward tokens. The action is a propelled fighter state rather than a projectile system:

1. run rapidly toward the opponent;
2. first contact has zero damage and holds/squeezes briefly;
3. continue past the victim;
4. stop and turn;
5. return with the damaging strike;
6. recover to normal control.

This makes it a smaller dependency test than Acid Spit, Force Ball, or Invisibility. It still depends on correct player action scheduling, collision/strike timing, opponent interaction, and animation selection.

## What transfers conceptually

The MKT source identifies the command and choreography, but donor retail ROM offsets were not certified. The MKMSZ implementation must use MKMSZ's own descriptor grammar, semantic input tokens, scheduler, velocity, animation, strike, and cleanup functions. No MKT binary code or resource is assumed compatible.

The exact MKMSZ descriptor layout, corrected action helpers, proof versions, and current blockers are in [Player actions and special moves](Player-Actions-and-Special-Moves).

## Long-term significance

A bounded, stable Reverse Elbow would validate adding a truly foreign behavior using native MKMSZ control and combat systems. It would not by itself prove whole-fighter replacement, imported animation compatibility, projectile specials, or playable Reptile.
