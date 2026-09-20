> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Core Runtime and Address Database

## Clean target

- platform: Nintendo 64
- USA `NMYE`, revision 0
- size: 16 MiB
- SHA-256: `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`

## File loading

Global file table:

- VA: `0x800A4410`
- ROM: `0x000A5010`
- entry size: 12 bytes — ROM start, ROM end, format flag

Shared loader:

`FUN_80065D64`

MKMSZR uses file ID `0x1B` for native payload loading.

## Runtime reservation

MKMSZR moves the original arena start from `0x801AF420` to `0x801AF820`, reserving exactly 1 KiB:

`0x801AF420..0x801AF81F`

Runtime Layout V1:

| Cached range | KSEG1 alias | Size | Purpose |
|---|---|---:|---|
| `0x801AF420..0x801AF61F` | `0xA01AF420..0xA01AF61F` | 0x200 | reloadable native code |
| `0x801AF620..0x801AF81F` | `0xA01AF620..0xA01AF81F` | 0x200 | persistent `MKSV` state |

## Shared runtime addresses

| Symbol | Address | Role |
|---|---:|---|
| current stage | `0x8009A910` | native stage |
| selector index | `0x800C11E0` | selector choice |
| normalized physical input | `0x8009A5A0` | input mirror |
| gameplay overlay base | `0x802ECE30` | shared stage overlay VA |
| HUD callback | `0x8005BFB0` | recurring gameplay HUD |
| render submit | `0x8001EAE4` | native render queue |
| render allocator | `0x8002018C` | custom geometry |
| MKMSZR UI hook | `0x8005CDCC` | stock HUD + MKMSZR work |
| native text | `0x80073E74` | gameplay ASCII |
| string width | `0x80074084` | matching measurement |
| one-shot stage-entry save bypass | `0x80291C0C` | consumed by entry callbacks |
| automatic stage-entry save | `FUN_800798A8` | generic save UI entry |

## Player special-move seam

Low Kick descriptor path:

- callback `0x80014C60`
- event handler `0x8003C94C`
- parser `0x8004A0E0`
- matcher `0x80049E60`
- transfer dispatcher `0x80049D14`
- table `0x800B0F68` / ROM `0x000B1B68`
- record size `0x2C`

See [[Foreign Moves and Reptile]].
