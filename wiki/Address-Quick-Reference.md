# Address quick reference

> **Scope:** This page is a **derivative convenience subset** for orientation. It is not authoritative for allocation ownership, patch guards, function semantics, resource grammar, or feature behavior. Update the canonical owner first; this page should only mirror a small high-value subset.

| Purpose | N64 address | Canonical owner |
|---|---:|---|
| Global file table | VA `0x800A4410`; ROM `0x000A5010` | [Resource and overlay system](ROM-Overlay-and-Resource-Map) for table mechanics; [Memory map](Memory-and-Allocation-Map) for owned entries |
| Raw file loader | `0x80065D64` | [Function registry](Function-Registry) |
| Stage-overlay base | `0x802ECE30` | [Resource and overlay system](ROM-Overlay-and-Resource-Map); allocation qualification in [Memory map](Memory-and-Allocation-Map) |
| Current process/context pointer | `0x802ECE20` | [Memory map](Memory-and-Allocation-Map); lifecycle use in [Core runtime](Core-Runtime-and-Address-Database) |
| Reserved runtime block | `[0x801AF420,0x801B3420)` (16 KiB) | [Memory map](Memory-and-Allocation-Map) |
| Runtime V2 code/state split | code `[0x801AF420,0x801AF7D0)`; state `[0x801AF7D0,0x801AF820)` | [Memory map](Memory-and-Allocation-Map); composition in [Core runtime](Core-Runtime-and-Address-Database) |
| Native expansion pool | `[0x801AF820,0x801B3420)` (15 KiB, build-time managed) | [Memory map](Memory-and-Allocation-Map); allocator contract in [Core runtime](Core-Runtime-and-Address-Database) |
| Current native stage | `0x8009A910` | [Stage flow and selector](Stage-Flow-and-Selector) |
| Selector index | `0x800C11E0` | [Stage flow and selector](Stage-Flow-and-Selector) |
| Normalized action input | `0x800BF2EE` | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Live inventory | `[0x800A600C,0x800A6034)` | [Memory map](Memory-and-Allocation-Map); behavior in [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle) |
| Four backing boxes | `[0x800A6048,0x800A60E8)` | [Memory map](Memory-and-Allocation-Map); behavior in [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle) |
| Box state / magic | `0x800A60E8`, `0x800A60EC` | [Memory map](Memory-and-Allocation-Map) |
| Pickup manager | `0x80038ACC` | [Function registry](Function-Registry) |
| Pickup capture hook | VA `0x80039418`; ROM `0x0003A018` | [Patch-site registry](Address-and-Patch-Site-Registry) |
| Pickup renderer/loader | `0x8001C528` | [Function registry](Function-Registry) |
| Inventory insertion | `0x80075448` | [Function registry](Function-Registry) |
| Native text | `0x80073E74` | [Function registry](Function-Registry) |
| Text width | `0x80074084` | [Function registry](Function-Registry) |
| HUD function / hook | function `0x8005BFB0`; hook ROM `0x0005D9CC` | [Function registry](Function-Registry) / [Patch-site registry](Address-and-Patch-Site-Registry) |
| Render-node allocator / submit | `0x8002018C`; `0x8001EAE4` | [Function registry](Function-Registry) |
| XP word / central award | `0x8011200C`; `0x8002E104` | [Memory map](Memory-and-Allocation-Map) / [Function registry](Function-Registry) |
| Enemy stream interpreter | `0x80071500` | [Function registry](Function-Registry) |
| Enemy spawn/constructor/allocator | `0x800719F0`; `0x80071B20`; `0x8002FCDC` | [Function registry](Function-Registry) |
| Player velocity helper | `0x8002B1EC` | [Function registry](Function-Registry) |
| Special-action installer | `0x80032CD4` | [Function registry](Function-Registry) |
| Special scheduler transfer shim | `0x8004AA4C` | [Function registry](Function-Registry) |

Important corrections mirrored from their owners: a signed `0xCE20` low immediate paired with `lui 0x802F` resolves to `0x802ECE20`, not `0x802FCE20`; and `0x8004CC14` is projectile setup, not player movement.
