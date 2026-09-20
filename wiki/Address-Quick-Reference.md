> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Address Quick Reference

Convenience index only. Current shared ownership is [[Core Runtime and Address Database]]; the Library Core Runtime report preserves the archival research record.

## Runtime/loading

| Item | Address |
|---|---:|
| global file table | `0x800A4410` / ROM `0x000A5010` |
| generic loader | `0x80065D64` |
| gameplay overlay base | `0x802ECE30` |
| reserved block | `0x801AF420..0x801AF81F` |
| V1 code | `0x801AF420..0x801AF61F` |
| V1 state | `0x801AF620..0x801AF81F` |
| current stage | `0x8009A910` |
| selector index | `0x800C11E0` |
| physical input | `0x8009A5A0` |

## UI

| Item | Address |
|---|---:|
| HUD callback | `0x8005BFB0` |
| render submit | `0x8001EAE4` |
| render allocator | `0x8002018C` |
| MKMSZR HUD hook | `0x8005CDCC` / ROM `0x0005D9CC` |
| native text | `0x80073E74` |
| string width | `0x80074084` |
| font descriptor | `0x800B1E20` |

## Stage flow

| Item | Address |
|---|---:|
| production selector mapper | `0x8009A2FC` / ROM `0x0009AEFC` |
| one-shot auto-save bypass | `0x80291C0C` |
| automatic stage-entry save | `0x800798A8` |
| post-legal logo bypass | ROM `0x0007A3F4` |

## XP / progression

| Item | Address |
|---|---:|
| current XP | `0x8011200C` |
| central XP award helper | `0x8002E104` / ROM `0x0002ED04` |
| XP tier evaluator / clamp | `0x80074FBC` / ROM `0x00075BBC` |
| stage XP-cap table | `0x800A63FC` / ROM `0x000A6FFC` |
| direct XP award store 1 | `0x800540E8` / ROM `0x00054CE8` |
| direct XP award store 2 | `0x80057160` / ROM `0x00057D60` |
| direct XP award store 3 | `0x8005722C` / ROM `0x00057E2C` |
| combo EXPERIENCE label render call | ROM `0x00063704` |
| combo EXPERIENCE value render call | ROM `0x00063724` |

## Special moves

| Item | Address |
|---|---:|
| Low Kick callback | `0x80014C60` |
| event handler | `0x8003C94C` |
| descriptor parser | `0x8004A0E0` |
| matcher | `0x80049E60` |
| transfer dispatcher | `0x80049D14` |
| Low Kick table | `0x800B0F68` / ROM `0x000B1B68` |

## Inventory

| Item | Address |
|---|---:|
| LIVE | `0x800A600C..0x800A6033` |
| Box 1 | `0x800A6048..0x800A606F` |
| Box 2 | `0x800A6070..0x800A6097` |
| Box 3 | `0x800A6098..0x800A60BF` |
| Box 4 | `0x800A60C0..0x800A60E7` |
| box state | `0x800A60E8` |
| `MKBX` magic | `0x800A60EC` |
