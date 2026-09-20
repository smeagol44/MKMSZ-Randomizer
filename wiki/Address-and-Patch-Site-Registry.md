# Address and patch-site registry

All ROM offsets are for the clean USA Rev. 0 `.z64` image. “Production” means current pipeline ownership; proof sites are not written by the product.

## Production hooks and code/data regions

| ROM | VA | Owner | Guard/original | Production effect |
|---:|---:|---|---|---|
| `0x0000DD60` | — | Stage selector | `0x2414000A` | Last compact menu index becomes `7` |
| `0x0000DD64` | — | Stage selector | `0x2A82000B` | Entry count becomes `8` |
| `0x0000E028` | — | Stage selector | JAL `0x8002830C` | JAL debug menu `0x8000D0B8` |
| `0x00015CD0` | — | Stage selector | load from `0x800C11E0` | JAL compact-index mapper |
| `0x0001674C` | — | Four-box input | `3C03802F 9463CE18` | Call switching action routine, then resume `0x80015B54` |
| `0x000396CC` | `0x80038ACC` | Persistence | `3C03800A 8C63A910` | Restore collected flags, resume `0x80038AD4` |
| `0x0003A018` | `0x80039418` | Persistence | `ACA2002C` | Capture stage/ordinal after collected store |
| `0x0005D9CC` | HUD function | Box indicator | JAL `0x8001EAE4` | JAL wrapper at `0x800AEE24` |
| `0x00066F64` | — | Arena | `0x2442F420` | `0x2442F820` |
| `0x00066FE0` | `0x800663E0` | Bootstrap | guarded native sequence | Call stub at `0x8009A184` |
| `0x00066FE8` | — | Arena | `0x2442F420` | `0x2442F820` |
| `0x0007A3F4` | `0x800797F4` | Logo bypass | two logo JAL pairs then fade JAL | `beq zero,zero,+3`; preserves fade/title |
| `0x0007B900..0x7B94B` | `0x8007AD00` | Four-box mask | stock sanitizer | Stage-local key mask-copy routine |
| `0x0007B94C..0x7B97F` | `0x8007AD4C` | Four-box load | stock default loader | Rebuild live inventory from backing box |
| `0x0008F6E8..` | `0x8008EAE8` | Four-box input | guarded cave | Switch action routine |
| `0x0009A6C8..` | `0x80099AC8` | Four-box helper | former selector cave tail | Switch/mask helper |
| `0x0009AD84..` | `0x8009A184` | Bootstrap | zero/free region | Stub; capacity `0x19C` |
| `0x0009AEFC` | `0x8009A2FC` | Selector/flow | relocated mapper | Compact mapping plus selector-save flag |
| `0x0009B7DC` | `0x8009ABDC` | Selector | 12 stock pointers | Eight safe stage labels plus zeros |
| `0x000A5154` | file entry `0x1B` | Native payload | guarded stock entry | Payload ROM/RDRAM descriptor |
| `0x000A6BE4` | `0x800A5FE4` | Four-box keys | obsolete default template | Item `0x0D..0x22` stage map |
| `0x000A6C48..0xA6CEF` | `0x800A6048..0x800A60EF` | Four-box state | guarded stock data | Four boxes, state, `MKBX` |
| `0x000A6E88` | item-use table | Glass mask | `0x80071F58` | Inert `0x80071F50` |
| `0x000AF9BE..0xAFA23` | boot strings | Branding | guarded legal text | Product title, phrase, author |
| `0x000AFA24..0xAFA97` | `0x800AEE24..` | Box indicator | guarded legal-text region | Wrapper and `BOX 1 OF 4` |
| `0x000AFA98..0xAFABB` | boot strings | Branding | guarded license text | Preserved Nintendo attribution |
| `0x0078E16C..` | palette data | Outfit | 64 BGR555 colors | Clothing indices `0x21..0x3F` transformed |
| `0x00F10000..` | `0x801AF420` | Native payload | output expansion | Code/state payload source |

Boot string pointer instructions live at ROM `0x7A22C`, `0x7A250`, `0x7A274`, `0x7A298`, `0x7A2BC`, `0x7A2E0`, `0x7A304`, `0x7A328`, `0x7A34C`, `0x7A370`, and `0x7A394`; every instruction is guarded before replacement.

## Proof-only sites

| ROM/VA | Proof | Status |
|---|---|---|
| ROM `0xB44AA` / RAM `0x800B38AA` | First ordinary Fire enemy type `0x0A -> 0x09` | Runtime-confirmed, not production |
| Fire resource entry ROM `0xA52E0` | Relocated/expanded Fire pickup resources | Runtime-confirmed architecture proof |
| VA `0x8008EAEC` / ROM `0x8F6EC` | Dedicated Prison-key award callback | Runtime-confirmed proof; conflicts with production cave ownership |
| Fire overlay tail ROM `0xE2148..0xE216B` | Foreign fighter file load/allocation sequence | Runtime-confirmed monk import proof |
| Seven Fire type-`0x0A` halfwords | Replace ordinary Fire Hulk types with Temple monk type `0x01` | Runtime-confirmed bounded proof |

## Frontend save-bypass payload

The relocated selector mapper at `0x8009A2FC` is exactly:

```text
3C03800C 8C6311E0 2C610006 50200001
24630002 3C028029 03E00008 A0441C0C
```

It reads the compact index, adds 2 for indices `6` and `7`, and writes nonzero byte `0x15` to `0x80291C0C` in the return delay slot. That is the game's native one-shot stage-entry save bypass; `0x800798A8` and all later/manual save flows remain unchanged.
