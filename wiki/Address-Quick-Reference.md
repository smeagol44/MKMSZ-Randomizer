# Address quick reference

Use this page for orientation; owning registries contain scope and caveats.

| Purpose | N64 address |
|---|---:|
| Global file table | VA `0x800A4410`; ROM `0x000A5010` |
| Raw file loader | `0x80065D64` |
| Stage-overlay base | `0x802ECE30` |
| Current process/context pointer | `0x802ECE20` |
| Reserved runtime block | `0x801AF420..0x801AF81F` |
| Runtime code/state split | code `0x801AF420..0x801AF61F`; state `0x801AF620..0x801AF81F` |
| Current native stage | `0x8009A910` |
| Selector index | `0x800C11E0` |
| Normalized action input | `0x800BF2EE` |
| Live inventory | `0x800A600C..0x800A6033` |
| Four backing boxes | `0x800A6048..0x800A60E7` |
| Box state/magic | `0x800A60E8`, `0x800A60EC` |
| Pickup manager | `0x80038ACC` |
| Pickup capture hook | VA `0x80039418`; ROM `0x0003A018` |
| Pickup renderer/loader | `0x8001C528` |
| Inventory insertion | `0x80075448` |
| Native text | `0x80073E74` |
| Text width | `0x80074084` |
| HUD function / hook | `0x8005BFB0`; hook ROM `0x0005D9CC` |
| Render-node allocator / submit | `0x8002018C`; `0x8001EAE4` |
| XP word / central award | `0x8011200C`; `0x8002E104` |
| Enemy stream interpreter | `0x80071500` |
| Enemy spawn/constructor/allocator | `0x800719F0`; `0x80071B20`; `0x8002FCDC` |
| Player velocity helper | `0x8002B1EC` |
| Special-action installer | `0x80032CD4` |
| Special scheduler transfer shim | `0x8004AA4C` |

Important correction: a signed `0xCE20` low immediate paired with `lui 0x802F` resolves to `0x802ECE20`, not `0x802FCE20`. Also, `0x8004CC14` is projectile setup, not player movement.
