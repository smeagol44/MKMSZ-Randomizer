> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Foreign Moves and Reptile

Exploratory donor work; not part of the production randomizer yet.

## MKT Reptile Reverse Elbow

Command:

**Back -> Forward + Low Kick**

MKT choreography:

1. command recognition;
2. fast run toward opponent;
3. first zero-damage contact;
4. short grounded victim hold;
5. continue past victim;
6. stop and face opponent;
7. return animation;
8. second damaging strike;
9. recovery.

No projectile or persistent special effect is required.

## MKMSZ compatibility

MKMSZ has a closely compatible 0x2C-byte special-move descriptor grammar.

Low Kick path:

- callback `0x80014C60`
- event handler `0x8003C94C`
- parser `0x8004A0E0`
- matcher `0x80049E60`
- transfer dispatcher `0x80049D14`
- table `0x800B0F68` / ROM `0x000B1B68`

Useful native helpers:

| Operation | Address |
|---|---:|
| nearest opponent | `0x80031D00` |
| horizontal velocity | `0x8004CC14` |
| stop motion | `0x8002B1C0` |
| face opponent | `0x80031EF0` |
| select animation | `0x8002FE54` |
| advance animation | `0x800304C0` |
| strike dispatch | `0x8004CF3C` |
| collision/reaction | `0x8002BA04` |
| install callback | `0x80032CD4` |
| sleep | `0x80028794` |
| restore control | `0x800328FC` |

## Runtime experiment history

Early disposable proofs reached command dispatch but did not yet produce the complete move:

- v1: custom action dispatched; Sub-Zero moved only slightly; visible animation did not complete; facing/input interpretation was reversed.
- v2: Back -> Forward + Low Kick became correct on both facings; movement remained minimal; enemy contact could hard-hang the emulation due to an experimental victim callback.
- v3: a later revision immediately hung with or without enemies.

These failures motivated the tighter Work/Ghidra mapping of native action/combat helpers above.

## Long-term purpose

If a bounded Reverse Elbow replacement works, it validates the architecture for replacing native Sub-Zero abilities with foreign Mortal Kombat behavior. That is a stepping stone toward bonus moves, broader Reptile behavior and eventually—if later resource/control work supports it—whole-fighter replacement.
