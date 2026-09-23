# Fortress stage catalog

> **Scope:** Stage-local catalog for Fortress, compact selector `7` / native stage ID `9`. Shared record grammar, resource notation, evidence labels, and safety rules are owned by [Stage catalogs](Stage-Catalogs). General extension-selector/materializer mechanics and composed-proof chronology remain owned by [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

## Stage identity and evidence

- **Static-confirmed:** all 9 ordinary pickup records, all 7 stock outer slots, and the recognized resource records below are decoded from the clean USA N64 ROM.
- **Runtime-confirmed:** the complete Fortress resource file was byte-matched against captured runtime memory at `0x801F4E20`.
- **Runtime-confirmed:** representative Fortress ordinary-pickup collection/persistence is established, but all 9 Fortress records have not been individually exhausted one by one in runtime testing.
- **Implementation/static-confirmed, proof-only; runtime Pending:** the composed five-import stress ROM contains the equivalent Fortress construction for Potion, Urn of Vitality, Formula, Eye, and Shield, with another Herbs record retained byte-for-byte as a control. The Fortress half has not been manually runtime-tested and must not inherit Prison's Runtime-confirmed status.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `9` |
| Global resource file ID | `0x43` |
| File-table entry ROM | `0x000A5334` |
| Resource ROM range | `0x003B9700..0x003BCD1F` |
| File size | `0x3620` (13856 bytes) |
| File-table flag | `0` |
| Verified runtime base | `0x801F4E20` |
| Outer slots | `7` |
| Outer-table end | `0x1C` |
| First descriptor | `0x1C` |
| Empty logical slots | `none` |
| Unknown/nonstandard slots | `none` |
| Pickup records | `9` |

## Ordinary pickup records

| # | Decoded identity | ROM base | RDRAM base | X | Y | Z | +0C | +10 type | +14 parameter | +18 callback | +1C | +20 | +24 slot | +28 presentation | +2C collected | Token | Requires |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | Crystal Kia | `0x000C4834` | — | `0x00000000` | `0xFFFAF200` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00008001` | `0x80038770` | `0x00000012` | `0x00000014` | `1` | `0x800B1BD0` | `0x00000000` | `crystal-kia` | — |
| 2 | Crystal Jataaka | `0x000C4864` | — | `0x00000000` | `0xFFF5B200` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00008000` | `0x80038770` | `0x00000012` | `0x00000014` | `0` | `0x800B1BD0` | `0x00000000` | `crystal-jataaka` | — |
| 3 | Crystal Sareena | `0x000C4894` | — | `0x00000000` | `0xFFF07200` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00008002` | `0x80038770` | `0x00000012` | `0x00000014` | `2` | `0x800B1BD0` | `0x00000000` | `crystal-sareena` | — |
| 4 | Herbs | `0x000C48C4` | — | `0x00271800` | `0xFFFAF200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `3` | `0x800B1D38` | `0x00000000` | — | — |
| 5 | Herbs | `0x000C48F4` | — | `0x000D0200` | `0xFFF07200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `3` | `0x800B1D38` | `0x00000000` | — | — |
| 6 | Herbs | `0x000C4924` | — | `0x001C1000` | `0xFFF07200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `3` | `0x800B1D38` | `0x00000000` | — | — |
| 7 | Herbs | `0x000C4954` | — | `0x003AE500` | `0xFFF5B200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `3` | `0x800B1D38` | `0x00000000` | — | — |
| 8 | Herbs | `0x000C4984` | — | `0x0043ED00` | `0xFFFAF200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `3` | `0x800B1D38` | `0x00000000` | — | — |
| 9 | Herbs | `0x000C49B4` | — | `0x002F9C00` | `0xFFFAF200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `3` | `0x800B1D38` | `0x00000000` | — | — |

## Pickup-to-resource usage

| ROM base | Callback | Parameter | Slot | Presentation |
|---:|---:|---:|---:|---:|
| `0x000C4834` | `0x80038770` | `0x00008001` | 1 | `0x800B1BD0` |
| `0x000C4864` | `0x80038770` | `0x00008000` | 0 | `0x800B1BD0` |
| `0x000C4894` | `0x80038770` | `0x00008002` | 2 | `0x800B1BD0` |
| `0x000C48C4` | `0x800389BC` | `0x00000000` | 3 | `0x800B1D38` |
| `0x000C48F4` | `0x800389BC` | `0x00000000` | 3 | `0x800B1D38` |
| `0x000C4924` | `0x800389BC` | `0x00000000` | 3 | `0x800B1D38` |
| `0x000C4954` | `0x800389BC` | `0x00000000` | 3 | `0x800B1D38` |
| `0x000C4984` | `0x800389BC` | `0x00000000` | 3 | `0x800B1D38` |
| `0x000C49B4` | `0x800389BC` | `0x00000000` | 3 | `0x800B1D38` |

## Outer resource slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Crystal (Jataaka) | `0x48` | embedded-data-bundle | 8 | 1 |
| 1 | Crystal (Kia) | `0x1C` | embedded-data-bundle | 8 | 1 |
| 2 | Crystal (Sareena) | `0x74` | embedded-data-bundle | 8 | 1 |
| 3 | Herbs | `0x1338` | embedded-data-bundle | 8 | 6 |
| 4 | Non-pickup/unknown resource | `0x2490` | embedded-data-bundle | 8 | 0 |
| 5 | Non-pickup/unknown resource (aliases Herbs descriptor) | `0x1338` | embedded-data-bundle | 8 | 0 |
| 6 | Non-pickup/unknown resource | `0x1C48` | embedded-data-bundle | 8 | 0 |

## Recognized bundle/list records

| Slot | Frame | Record | Storage | Resource/data value | Inferred end | Dimensions words |
|---:|---:|---:|---|---:|---:|---|
| 0 | 0 | `0x140` | embedded-data | `0x7E0` | `0x860` | `0x00160008` / `0x00070004` |
| 0 | 1 | `0x154` | embedded-data | `0x860` | `0x8F0` | `0x00160009` / `0x00070005` |
| 0 | 2 | `0x168` | embedded-data | `0x8F0` | `0x9B0` | `0x0016000D` / `0x00070007` |
| 0 | 3 | `0x17C` | embedded-data | `0x9B0` | `0xA88` | `0x00160010` / `0x00070008` |
| 0 | 4 | `0x190` | embedded-data | `0xA88` | `0xB48` | `0x00160010` / `0x00070008` |
| 0 | 5 | `0x1A4` | embedded-data | `0xB48` | `0xC04` | `0x00160010` / `0x00070008` |
| 0 | 6 | `0x1B8` | embedded-data | `0xC04` | `0xCB8` | `0x0016000D` / `0x00070006` |
| 0 | 7 | `0x1CC` | embedded-data | `0xCB8` | `0xD3C` | `0x00160008` / `0x00070004` |
| 1 | 0 | `0xA0` | embedded-data | `0x280` | `0x300` | `0x00160008` / `0x000E0004` |
| 1 | 1 | `0xB4` | embedded-data | `0x300` | `0x390` | `0x00160009` / `0x000E0005` |
| 1 | 2 | `0xC8` | embedded-data | `0x390` | `0x450` | `0x0016000D` / `0x000E0007` |
| 1 | 3 | `0xDC` | embedded-data | `0x450` | `0x528` | `0x00160010` / `0x000E0008` |
| 1 | 4 | `0xF0` | embedded-data | `0x528` | `0x5E4` | `0x00160010` / `0x000E0008` |
| 1 | 5 | `0x104` | embedded-data | `0x5E4` | `0x6A8` | `0x00160010` / `0x000E0008` |
| 1 | 6 | `0x118` | embedded-data | `0x6A8` | `0x760` | `0x0016000D` / `0x000E0006` |
| 1 | 7 | `0x12C` | embedded-data | `0x760` | `0x7E0` | `0x00160008` / `0x000E0004` |
| 2 | 0 | `0x1E0` | embedded-data | `0xD3C` | `0xDD8` | `0x00080016` / `0x0003000E` |
| 2 | 1 | `0x1F4` | embedded-data | `0xDD8` | `0xE88` | `0x00090016` / `0x0004000E` |
| 2 | 2 | `0x208` | embedded-data | `0xE88` | `0xF60` | `0x000D0016` / `0x0006000E` |
| 2 | 3 | `0x21C` | embedded-data | `0xF60` | `0x1048` | `0x00100016` / `0x0007000E` |
| 2 | 4 | `0x230` | embedded-data | `0x1048` | `0x1118` | `0x00100016` / `0x0007000E` |
| 2 | 5 | `0x244` | embedded-data | `0x1118` | `0x11E4` | `0x00100016` / `0x0007000E` |
| 2 | 6 | `0x258` | embedded-data | `0x11E4` | `0x12A0` | `0x000D0016` / `0x0005000E` |
| 2 | 7 | `0x26C` | embedded-data | `0x12A0` | `0x1400` | `0x00080016` / `0x0003000E` |
| 3 | 0 | `0x1360` | embedded-data | `0x1400` | `0x14E4` | `0x00110017` / `0x0008000F` |
| 3 | 1 | `0x1374` | embedded-data | `0x14E4` | `0x15E4` | `0x00110017` / `0x0008000F` |
| 3 | 2 | `0x1388` | embedded-data | `0x15E4` | `0x16F4` | `0x00100017` / `0x0007000F` |
| 3 | 3 | `0x139C` | embedded-data | `0x16F4` | `0x180C` | `0x00100017` / `0x0008000F` |
| 3 | 4 | `0x13B0` | embedded-data | `0x180C` | `0x1930` | `0x00110017` / `0x0008000F` |
| 3 | 5 | `0x13C4` | embedded-data | `0x1930` | `0x1A50` | `0x00100017` / `0x0007000F` |
| 3 | 6 | `0x13D8` | embedded-data | `0x1A50` | `0x1B5C` | `0x00100017` / `0x0008000F` |
| 3 | 7 | `0x13EC` | embedded-data | `0x1B5C` | `0x1D10` | `0x00100017` / `0x0008000F` |
| 4 | 0 | `0x24B8` | embedded-data | `0x2558` | `0x2740` | `0x00160017` / `0x000B000B` |
| 4 | 1 | `0x24CC` | embedded-data | `0x2740` | `0x2938` | `0x00160017` / `0x000B000B` |
| 4 | 2 | `0x24E0` | embedded-data | `0x2938` | `0x2B2C` | `0x00160017` / `0x000B000B` |
| 4 | 3 | `0x24F4` | embedded-data | `0x2B2C` | `0x2D1C` | `0x00160017` / `0x000B000B` |
| 4 | 4 | `0x2508` | embedded-data | `0x2D1C` | `0x2F04` | `0x00160017` / `0x000B000B` |
| 4 | 5 | `0x251C` | embedded-data | `0x2F04` | `0x30F0` | `0x00160017` / `0x000B000B` |
| 4 | 6 | `0x2530` | embedded-data | `0x30F0` | `0x32E4` | `0x00160017` / `0x000B000B` |
| 4 | 7 | `0x2544` | embedded-data | `0x32E4` | `0x3620` | `0x00160017` / `0x000B000B` |
| 5 | 0 | `0x1360` | embedded-data | `0x1400` | `0x14E4` | `0x00110017` / `0x0008000F` |
| 5 | 1 | `0x1374` | embedded-data | `0x14E4` | `0x15E4` | `0x00110017` / `0x0008000F` |
| 5 | 2 | `0x1388` | embedded-data | `0x15E4` | `0x16F4` | `0x00100017` / `0x0007000F` |
| 5 | 3 | `0x139C` | embedded-data | `0x16F4` | `0x180C` | `0x00100017` / `0x0008000F` |
| 5 | 4 | `0x13B0` | embedded-data | `0x180C` | `0x1930` | `0x00110017` / `0x0008000F` |
| 5 | 5 | `0x13C4` | embedded-data | `0x1930` | `0x1A50` | `0x00100017` / `0x0007000F` |
| 5 | 6 | `0x13D8` | embedded-data | `0x1A50` | `0x1B5C` | `0x00100017` / `0x0008000F` |
| 5 | 7 | `0x13EC` | embedded-data | `0x1B5C` | `0x1D10` | `0x00100017` / `0x0008000F` |
| 6 | 0 | `0x1C70` | embedded-data | `0x1D10` | `0x1E08` | `0x00110017` / `0x0008000F` |
| 6 | 1 | `0x1C84` | embedded-data | `0x1E08` | `0x1F08` | `0x00110017` / `0x0008000F` |
| 6 | 2 | `0x1C98` | embedded-data | `0x1F08` | `0x2004` | `0x00100017` / `0x0007000F` |
| 6 | 3 | `0x1CAC` | embedded-data | `0x2004` | `0x20EC` | `0x000F0017` / `0x0007000F` |
| 6 | 4 | `0x1CC0` | embedded-data | `0x20EC` | `0x21DC` | `0x000F0017` / `0x0007000F` |
| 6 | 5 | `0x1CD4` | embedded-data | `0x21DC` | `0x22BC` | `0x000F0017` / `0x0007000F` |
| 6 | 6 | `0x1CE8` | embedded-data | `0x22BC` | `0x23A8` | `0x00100017` / `0x0008000F` |
| 6 | 7 | `0x1CFC` | embedded-data | `0x23A8` | `0x2558` | `0x00100017` / `0x0008000F` |

## Fortress-specific notes, constraints, and proof-local evidence

- The stock resource file has exactly **7 occupied outer slots**. Its outer table occupies file-relative `0x0000..0x001B`; the first descriptor starts immediately at `0x1C`. There is no empty stock logical selector.
- Adding an eighth stock-table word in place would overwrite that first descriptor. This is a **Static-confirmed stock-layout fact**, not a claim that Fortress lacks all ordinary-pickup selector expansion paths.
- Slot `5` aliases the Herbs descriptor `0x1338` used by slot `3`. Slots `4` and `6` have no ordinary-pickup users, but all three remain protected until other Fortress actor/script references are resolved.
- The crystal callback parameters are raw `0x00008000`, `0x00008001`, and `0x00008002`; their low selectors correspond to inventory IDs `0x20`, `0x21`, and `0x22` through the stage-dependent callback, while the high-bit meaning remains unresolved.
- **Composed five-import stress construction — Implementation/static-confirmed, proof-only; runtime Pending:** the disposable proof replaces the first five stock Herbs locations with Potion, Urn of Vitality, Formula, Eye, and Shield, retains another Herbs record byte-for-byte as a control, and supplies five contiguous extension-selector entries plus self-contained imported bundles. The generalized construction details remain on [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).
- The successful Prison half of that same stress ROM does **not** validate Fortress. No Fortress runtime observation has yet confirmed the five imported models, awards, control Herbs behavior, arena/headroom behavior, or the composed file/resource path.
- Current Fortress-specific Pending work is therefore explicit: manually validate the Fortress half of the five-import stress proof, preserve the untouched Herbs control, and keep any proof allocation/extension-selector placement separate from production ownership until the production-composition gate is satisfied.

## Related owners

- [Stage catalogs](Stage-Catalogs) — shared schema, notation, safety rules, catalog lineage, and eight-stage index.
- [Data structures and encodings](Data-Structures-and-Encodings) — ordinary `0x30`-byte record grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file-table, loader, overlay, and selector/resource grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership, lifecycle, and proof/production allocation boundaries.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded ROM edit sites.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior and modeled stage dependencies.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — extension-selector/materializer mechanics, planner/deduplication, external-to-embedded conversion, solver rules, and full composed-proof chronology.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and stage-transition lifecycle.
