# Wind stage catalog

> **Scope:** Stage-local catalog for Wind, compact selector `1` / native stage ID `1`. Shared record grammar, resource notation, evidence labels, and safety rules are owned by [Stage catalogs](Stage-Catalogs).

## Stage identity and evidence

- **Static-confirmed:** all six ordinary pickup records, the 12 stock outer slots, and the recognized resource records below are decoded from the clean USA N64 ROM.
- **Runtime-confirmed:** the complete `0x21A0`-byte resource file was matched byte-for-byte at RDRAM `0x80264FC8` during live Wind gameplay.
- **Runtime-confirmed:** the all-eight-stage persistence test collected/restored a representative Wind ordinary pickup. The six Wind records have not been individually exhausted one by one in runtime testing.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `1` |
| File-table entry ROM | `0x000A561C` |
| Resource ROM range | `0x00698680..0x0069A81F` |
| File size | `0x21A0` (8608 bytes) |
| File-table flag | `0` |
| Verified runtime base | `0x80264FC8` |
| Outer slots | `12` |
| Outer-table end | `0x30` |
| First descriptor | `0x30` |
| Empty logical slots | `6, 7, 8, 9` |
| Unknown/nonstandard slots | `none` |
| Pickup records | `6` |

## Ordinary pickup records

| # | Decoded identity | ROM base | RDRAM base | X | Y | Z | +0C | +10 type | +14 parameter | +18 callback | +1C | +20 | +24 slot | +28 presentation | +2C collected | Token | Requires |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | Herbs | `0x000D8424` | — | `0x001C2209` | `0xFFFE1100` | `0x00058700` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `5` | `0x800B1D38` | `0x00000000` | — | — |
| 2 | Herbs | `0x000D8454` | — | `0x00246B92` | `0xFFFF0600` | `0x00058700` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `5` | `0x800B1D38` | `0x00000000` | — | — |
| 3 | Extra-life urn | `0x000D8484` | — | `0x00437B5C` | `0x0000C700` | `0xFFFFFF00` | `0x00000004` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `4` | `0x800B1D38` | `0x00000000` | — | — |
| 4 | Wind Circle | `0x000D84B4` | — | `0x003AC07C` | `0xFFF96F00` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000000` | `0x802F2CB4` | `0x00000020` | `0x00000020` | `0` | `0x800B1D18` | `0x00000000` | `wind-circle` | — |
| 5 | Wind Triangle | `0x000D84E4` | — | `0x006A5C68` | `0xFFFFCE00` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000001` | `0x802F2CB4` | `0x00000020` | `0x00000020` | `2` | `0x800B1D18` | `0x00000000` | `wind-triangle` | wind-circle |
| 6 | Wind Three Bars | `0x000D8514` | — | `0x007475CA` | `0xFFF62F00` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000002` | `0x802F2CB4` | `0x00000020` | `0x00000020` | `1` | `0x800B1D18` | `0x00000000` | `wind-three-bars` | wind-triangle |

## Pickup-to-resource usage

| ROM base | Callback | Parameter | Slot | Presentation |
|---:|---:|---:|---:|---:|
| `0x000D8424` | `0x800389BC` | `0x00000000` | 5 | `0x800B1D38` |
| `0x000D8454` | `0x800389BC` | `0x00000000` | 5 | `0x800B1D38` |
| `0x000D8484` | `0x80038A1C` | `0x00000000` | 4 | `0x800B1D38` |
| `0x000D84B4` | `0x802F2CB4` | `0x00000000` | 0 | `0x800B1D18` |
| `0x000D84E4` | `0x802F2CB4` | `0x00000001` | 2 | `0x800B1D18` |
| `0x000D8514` | `0x802F2CB4` | `0x00000002` | 1 | `0x800B1D18` |

## Outer resource slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Wind icon, circle | `0x30` | embedded-data-bundle | 8 | 1 |
| 1 | Wind icon, three bars | `0x58` | embedded-data-bundle | 8 | 1 |
| 2 | Wind icon, triangle | `0x80` | embedded-data-bundle | 8 | 1 |
| 3 | Non-pickup/unknown resource | `0xA8` | zero-terminated-external-list | 14 | 0 |
| 4 | Extra-life urn | `0xE4` | embedded-data-bundle | 8 | 1 |
| 5 | Herbs | `0x10C` | embedded-data-bundle | 8 | 2 |
| 6 | Unused logical slot | `0` | empty | — | 0 |
| 7 | Unused logical slot | `0` | empty | — | 0 |
| 8 | Unused logical slot | `0` | empty | — | 0 |
| 9 | Unused logical slot | `0` | empty | — | 0 |
| 10 | Animated resource bundle | `0x56C` | zero-terminated-external-list | 6 | 0 |
| 11 | Animated resource bundle | `0x600` | external-resource-id-bundle | 10 | 0 |

## Recognized bundle records

| Slot | Frame | Record | Storage | Resource/data value | Inferred end | Dimensions words |
|---:|---:|---:|---|---:|---:|---|
| 0 | 0 | `0x134` | embedded-data | `0x6F8` | `0x73C` | `0x00040011` / `0x00010008` |
| 0 | 1 | `0x148` | embedded-data | `0x73C` | `0x7B0` | `0x00090011` / `0x00040008` |
| 0 | 2 | `0x15C` | embedded-data | `0x7B0` | `0x85C` | `0x000D0012` / `0x00060008` |
| 0 | 3 | `0x170` | embedded-data | `0x85C` | `0x90C` | `0x00100011` / `0x00070008` |
| 0 | 4 | `0x184` | embedded-data | `0x90C` | `0x9B0` | `0x00110011` / `0x00080008` |
| 0 | 5 | `0x198` | embedded-data | `0x9B0` | `0xA60` | `0x00100011` / `0x00070008` |
| 0 | 6 | `0x1AC` | embedded-data | `0xA60` | `0xAFC` | `0x000D0011` / `0x00050008` |
| 0 | 7 | `0x1C0` | embedded-data | `0xAFC` | `0xB80` | `0x00090012` / `0x00030008` |
| 1 | 0 | `0x1D4` | embedded-data | `0xB80` | `0xBC8` | `0x0006000C` / `0x00020005` |
| 1 | 1 | `0x1E8` | embedded-data | `0xBC8` | `0xC2C` | `0x000B000C` / `0x00050005` |
| 1 | 2 | `0x1FC` | embedded-data | `0xC2C` | `0xCAC` | `0x000E000C` / `0x00060005` |
| 1 | 3 | `0x210` | embedded-data | `0xCAC` | `0xD34` | `0x0011000B` / `0x00080005` |
| 1 | 4 | `0x224` | embedded-data | `0xD34` | `0xDA8` | `0x0012000A` / `0x00080004` |
| 1 | 5 | `0x238` | embedded-data | `0xDA8` | `0xE18` | `0x0010000A` / `0x00070004` |
| 1 | 6 | `0x24C` | embedded-data | `0xE18` | `0xE98` | `0x000E000C` / `0x00060005` |
| 1 | 7 | `0x260` | embedded-data | `0xE98` | `0xF10` | `0x000B000C` / `0x00040005` |
| 2 | 0 | `0x274` | embedded-data | `0xF10` | `0xF64` | `0x0006000F` / `0x00020006` |
| 2 | 1 | `0x288` | embedded-data | `0xF64` | `0xFD4` | `0x0009000F` / `0x00040006` |
| 2 | 2 | `0x29C` | embedded-data | `0xFD4` | `0x105C` | `0x000D000F` / `0x00060006` |
| 2 | 3 | `0x2B0` | embedded-data | `0x105C` | `0x10E0` | `0x0010000F` / `0x00070006` |
| 2 | 4 | `0x2C4` | embedded-data | `0x10E0` | `0x1160` | `0x0010000E` / `0x00070006` |
| 2 | 5 | `0x2D8` | embedded-data | `0x1160` | `0x11F0` | `0x0010000F` / `0x00070006` |
| 2 | 6 | `0x2EC` | embedded-data | `0x11F0` | `0x1278` | `0x000D000F` / `0x00050006` |
| 2 | 7 | `0x300` | embedded-data | `0x1278` | `0x12F8` | `0x000A000F` / `0x00040006` |
| 3 | 0 | `0x454` | external-resource-id | `0x38E` | `` | `0x00280024` / `0x00160016` |
| 3 | 1 | `0x4E0` | external-resource-id | `0x38E` | `` | `0x00280024` / `0x00160016` |
| 3 | 2 | `0x468` | external-resource-id | `0x38F` | `` | `0x002E0028` / `0x001A0019` |
| 3 | 3 | `0x4F4` | external-resource-id | `0x38F` | `` | `0x002E0028` / `0x001A0019` |
| 3 | 4 | `0x47C` | external-resource-id | `0x390` | `` | `0x00320031` / `0x001C001B` |
| 3 | 5 | `0x508` | external-resource-id | `0x390` | `` | `0x00320031` / `0x001C001B` |
| 3 | 6 | `0x490` | external-resource-id | `0x391` | `` | `0x00330036` / `0x001D001E` |
| 3 | 7 | `0x51C` | external-resource-id | `0x391` | `` | `0x00330036` / `0x001D001E` |
| 3 | 8 | `0x4A4` | external-resource-id | `0x392` | `` | `0x00370039` / `0x00210021` |
| 3 | 9 | `0x530` | external-resource-id | `0x392` | `` | `0x00370039` / `0x00210021` |
| 3 | 10 | `0x4B8` | external-resource-id | `0x393` | `` | `0x003A0039` / `0x00230023` |
| 3 | 11 | `0x544` | external-resource-id | `0x393` | `` | `0x003A0039` / `0x00230023` |
| 3 | 12 | `0x4CC` | external-resource-id | `0x394` | `` | `0x00380039` / `0x00220026` |
| 3 | 13 | `0x558` | external-resource-id | `0x394` | `` | `0x00380039` / `0x00220026` |
| 4 | 0 | `0x314` | embedded-data | `0x12F8` | `0x13E0` | `0x00110018` / `0x0008000D` |
| 4 | 1 | `0x328` | embedded-data | `0x13E0` | `0x14C0` | `0x00110018` / `0x0008000D` |
| 4 | 2 | `0x33C` | embedded-data | `0x14C0` | `0x1594` | `0x00100018` / `0x0007000D` |
| 4 | 3 | `0x350` | embedded-data | `0x1594` | `0x1658` | `0x00100018` / `0x0007000D` |
| 4 | 4 | `0x364` | embedded-data | `0x1658` | `0x1708` | `0x000F0018` / `0x0007000D` |
| 4 | 5 | `0x378` | embedded-data | `0x1708` | `0x17B0` | `0x000F0018` / `0x0008000D` |
| 4 | 6 | `0x38C` | embedded-data | `0x17B0` | `0x1874` | `0x00100018` / `0x0008000D` |
| 4 | 7 | `0x3A0` | embedded-data | `0x1874` | `0x1954` | `0x00110018` / `0x0008000D` |
| 5 | 0 | `0x3B4` | embedded-data | `0x1954` | `0x1A38` | `0x00110017` / `0x0008000F` |
| 5 | 1 | `0x3C8` | embedded-data | `0x1A38` | `0x1B38` | `0x00110017` / `0x0008000F` |
| 5 | 2 | `0x3DC` | embedded-data | `0x1B38` | `0x1C48` | `0x00100017` / `0x0007000F` |
| 5 | 3 | `0x3F0` | embedded-data | `0x1C48` | `0x1D60` | `0x00100017` / `0x0008000F` |
| 5 | 4 | `0x404` | embedded-data | `0x1D60` | `0x1E84` | `0x00110017` / `0x0008000F` |
| 5 | 5 | `0x418` | embedded-data | `0x1E84` | `0x1FA4` | `0x00100017` / `0x0007000F` |
| 5 | 6 | `0x42C` | embedded-data | `0x1FA4` | `0x20B0` | `0x00100017` / `0x0008000F` |
| 5 | 7 | `0x440` | embedded-data | `0x20B0` | `0x21A0` | `0x00100017` / `0x0008000F` |
| 10 | 0 | `0x588` | external-resource-id | `0x37A` | `` | `0x0062001A` / `0x0031FF9F` |
| 10 | 1 | `0x59C` | external-resource-id | `0x37B` | `` | `0x00610018` / `0x0030FF9E` |
| 10 | 2 | `0x5B0` | external-resource-id | `0x37C` | `` | `0x00630016` / `0x0031FF9D` |
| 10 | 3 | `0x5C4` | external-resource-id | `0x37D` | `` | `0x00620018` / `0x0030FF9C` |
| 10 | 4 | `0x5D8` | external-resource-id | `0x37E` | `` | `0x005F0015` / `0x002EFF9A` |
| 10 | 5 | `0x5EC` | external-resource-id | `0x37F` | `` | `0x00600014` / `0x002FFF9A` |
| 11 | 0 | `0x630` | external-resource-id | `0x25D` | `` | `0x00100017` / `0x0007000B` |
| 11 | 1 | `0x644` | external-resource-id | `0x25E` | `` | `0x00100017` / `0x0007000B` |
| 11 | 2 | `0x658` | external-resource-id | `0x25F` | `` | `0x000F0017` / `0x0006000B` |
| 11 | 3 | `0x66C` | external-resource-id | `0x260` | `` | `0x000E0017` / `0x0006000B` |
| 11 | 4 | `0x680` | external-resource-id | `0x261` | `` | `0x000B0017` / `0x0005000B` |
| 11 | 5 | `0x694` | external-resource-id | `0x262` | `` | `0x00070017` / `0x0003000B` |
| 11 | 6 | `0x6A8` | external-resource-id | `0x263` | `` | `0x00050018` / `0x0002000B` |
| 11 | 7 | `0x6BC` | external-resource-id | `0x264` | `` | `0x000A0018` / `0x0005000B` |
| 11 | 8 | `0x6D0` | external-resource-id | `0x265` | `` | `0x000E0017` / `0x0006000B` |
| 11 | 9 | `0x6E4` | external-resource-id | `0x266` | `` | `0x000F0017` / `0x0007000B` |

## Wind-specific notes, constraints, and pending questions

- The six ordinary records are two Herbs, one Extra-life urn, and the three Wind icons.
- The progression metadata remains stage-local: Wind Triangle requires `wind-circle`; Wind Three Bars requires `wind-triangle`.
- Occupied slot `3` has no user among the six ordinary pickup records. Its non-pickup gameplay owner remains unresolved; the slot stays protected rather than being treated as available.
- No outer slot is currently classified `unknown/nonstandard`; empty stock slots are `6, 7, 8, 9`. Per the shared schema, those zeros are logical selector capacity only and do not establish free physical storage.

## Related owners

- [Stage catalogs](Stage-Catalogs) — shared schema, notation, safety rules, and eight-stage index.
- [Data structures and encodings](Data-Structures-and-Encodings) — ordinary `0x30`-byte record grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file-table, loader, overlay, and selector/resource grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and lifecycle.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded patch sites.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior and modeled Wind dependencies.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — cross-stage materializer/solver rules rather than Wind-local records.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and stage-transition lifecycle.
