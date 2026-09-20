> **Mirror notice:** This Wiki is a navigation-friendly adaptation of MKMSZR documentation. The ChatGPT Library folder `MKMSZR Research` remains the reverse-engineering/research source of truth; this repository remains the implementation/product source of truth. If the Wiki conflicts with an owning source, the owning source wins.

# Address Quick Reference

Convenience index only. Canonical shared ownership remains the Core Runtime report.

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
