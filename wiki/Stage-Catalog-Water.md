# Water stage catalog

> **Scope:** Stage-local catalog for Water, compact selector `2` / native stage ID `2`. Shared record grammar, resource notation, evidence labels, and safety rules are owned by [Stage catalogs](Stage-Catalogs). Cross-stage Health-urn materialization/conversion mechanics are deliberately not owned here.

## Stage identity and evidence

- **Static-confirmed:** all nine ordinary pickup records, all 29 stock outer slots, and the recognized resource records below are decoded from the clean USA N64 ROM.
- **Runtime-confirmed:** the complete `0x64E0`-byte stage resource file was matched byte-for-byte at RDRAM `0x802504A8` during live Water gameplay.
- **Runtime-confirmed:** the all-eight-stage persistence validation collected/restored a representative Water ordinary pickup. The nine Water records have not been individually exhausted one by one in runtime testing.
- Water's three stage key pickups use stage-qualified overlay callback VA `0x802F2448`; this address is Water-overlay evidence, not a globally resident callback identity.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `2` |
| Global resource file ID | `0x75` |
| File-table entry ROM | `0x000A558C` |
| Resource ROM range | `0x00611780..0x00617C5F` |
| File size | `0x64E0` (25824 bytes) |
| File-table flag | `0` |
| Verified runtime base | `0x802504A8` |
| Outer slots | `29` |
| Outer-table end | `0x74` |
| First descriptor | `0x74` |
| Empty logical slots | `8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19` |
| Unknown/nonstandard slots | `none` |
| Pickup records | `9` |

## Ordinary pickup records

| # | Decoded identity | ROM base | RDRAM base | X | Y | Z | +0C | +10 type | +14 parameter | +18 callback | +1C | +20 | +24 slot | +28 presentation | +2C collected | Token | Requires |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | Health urn | `0x000BAB14` | — | `0x000420EB` | `0x000EF100` | `0x00000000` | `0x00000004` | `0x00000006` | `0x00000000` | `0x800389EC` | `0x00000020` | `0x00000020` | `28` | `0x800B1D38` | `0x00000000` | — | — |
| 2 | Health urn | `0x000BAB44` | — | `0xFFF0A160` | `0x002CF900` | `0x00000000` | `0x00000004` | `0x00000006` | `0x00000000` | `0x800389EC` | `0x00000020` | `0x00000020` | `28` | `0x800B1D38` | `0x00000000` | — | water-moon |
| 3 | Mana pickup | `0x000BAB74` | — | `0xFFEF3DEF` | `0x001BF300` | `0x00000000` | `0x00000002` | `0x00000003` | `0x00000000` | `0x80038A58` | `0x00000020` | `0x00000020` | `26` | `0x800B1C14` | `0x00000000` | — | — |
| 4 | Herbs | `0x000BABA4` | — | `0xFFFC7C29` | `0x001BEF00` | `0x00000000` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `25` | `0x800B1D38` | `0x00000000` | — | — |
| 5 | Potion | `0x000BABD4` | — | `0x00032CC7` | `0x00157400` | `0x00000000` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800388FC` | `0x00000020` | `0x00000020` | `27` | `0x800B1BAC` | `0x00000000` | — | — |
| 6 | Extra-life urn | `0x000BAC04` | — | `0x0005B6D6` | `0xFFFFAD00` | `0x00000000` | `0x00000004` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `24` | `0x800B1D38` | `0x00000000` | — | — |
| 7 | Water Triangle | `0x000BAC34` | — | `0xFFFE4715` | `0xFFFFAE00` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000000` | `0x802F2448` | `0x00000020` | `0x00000020` | `4` | `0x800B1D18` | `0x00000000` | `water-triangle` | — |
| 8 | Water Three Bars | `0x000BAC64` | — | `0xFFDAFD0E` | `0x00297100` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000001` | `0x802F2448` | `0x00000020` | `0x00000020` | `5` | `0x800B1D18` | `0x00000000` | `water-three-bars` | water-triangle |
| 9 | Water Moon | `0x000BAC94` | — | `0xFFFDD5A4` | `0x0024B100` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000002` | `0x802F2448` | `0x00000020` | `0x00000020` | `6` | `0x800B1D18` | `0x00000000` | `water-moon` | water-three-bars |

## Pickup-to-resource usage

| ROM base | Callback | Parameter | Slot | Presentation |
|---:|---:|---:|---:|---:|
| `0x000BAB14` | `0x800389EC` | `0x00000000` | 28 | `0x800B1D38` |
| `0x000BAB44` | `0x800389EC` | `0x00000000` | 28 | `0x800B1D38` |
| `0x000BAB74` | `0x80038A58` | `0x00000000` | 26 | `0x800B1C14` |
| `0x000BABA4` | `0x800389BC` | `0x00000000` | 25 | `0x800B1D38` |
| `0x000BABD4` | `0x800388FC` | `0x00000000` | 27 | `0x800B1BAC` |
| `0x000BAC04` | `0x80038A1C` | `0x00000000` | 24 | `0x800B1D38` |
| `0x000BAC34` | `0x802F2448` | `0x00000000` | 4 | `0x800B1D18` |
| `0x000BAC64` | `0x802F2448` | `0x00000001` | 5 | `0x800B1D18` |
| `0x000BAC94` | `0x802F2448` | `0x00000002` | 6 | `0x800B1D18` |

## Outer resource slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Animated resource bundle | `0x74` | embedded-data-bundle-mode0-selector | 7 | 0 |
| 1 | Animated resource bundle | `0x94` | zero-terminated-record-list | 1 | 0 |
| 2 | Animated resource bundle | `0x9C` | external-resource-id-bundle | 5 | 0 |
| 3 | Animated resource bundle | `0x134` | zero-terminated-external-list | 14 | 0 |
| 4 | Water icon, triangle | `0xBC` | embedded-data-bundle | 8 | 1 |
| 5 | Water icon, three bars | `0xE4` | embedded-data-bundle | 8 | 1 |
| 6 | Water icon, moon | `0x10C` | embedded-data-bundle | 8 | 1 |
| 7 | Animated resource bundle | `0x10C` | embedded-data-bundle | 8 | 0 |
| 8 | Unused logical slot | `0` | empty | — | 0 |
| 9 | Unused logical slot | `0` | empty | — | 0 |
| 10 | Animated resource bundle | `0x4508` | zero-terminated-record-list | 6 | 0 |
| 11 | Unused logical slot | `0` | empty | — | 0 |
| 12 | Unused logical slot | `0` | empty | — | 0 |
| 13 | Unused logical slot | `0` | empty | — | 0 |
| 14 | Unused logical slot | `0` | empty | — | 0 |
| 15 | Unused logical slot | `0` | empty | — | 0 |
| 16 | Unused logical slot | `0` | empty | — | 0 |
| 17 | Unused logical slot | `0` | empty | — | 0 |
| 18 | Unused logical slot | `0` | empty | — | 0 |
| 19 | Unused logical slot | `0` | empty | — | 0 |
| 20 | Animated resource bundle | `0x170` | zero-terminated-external-list | 5 | 0 |
| 21 | Animated resource bundle | `0x190` | zero-terminated-external-list | 5 | 0 |
| 22 | Animated resource bundle | `0x1B0` | external-resource-id-bundle | 5 | 0 |
| 23 | Animated resource bundle | `0x1CC` | external-resource-id-bundle | 3 | 0 |
| 24 | Extra-life urn | `0x1E0` | embedded-data-bundle | 8 | 1 |
| 25 | Herbs | `0x208` | embedded-data-bundle | 8 | 1 |
| 26 | Mana urn (Lua substitutes Herbs) | `0x230` | embedded-data-bundle | 8 | 1 |
| 27 | Potion | `0x258` | embedded-data-bundle | 8 | 1 |
| 28 | Health urn | `0x6474` | external-resource-id-bundle | 4 | 2 |

## Recognized bundle records

| Slot | Frame | Record | Storage | Resource/data value | Inferred end | Dimensions words |
|---:|---:|---:|---|---:|---:|---|
| 0 | 0 | `0x280` | embedded-data | `0xA50` | `0xB70` | `0x00160010` / `0x000A0008` |
| 0 | 1 | `0x294` | embedded-data | `0xB70` | `0xCC4` | `0x00150015` / `0x000A000B` |
| 0 | 2 | `0x2A8` | embedded-data | `0xCC4` | `0xD88` | `0x000F000E` / `0x00080008` |
| 0 | 3 | `0x2BC` | embedded-data | `0xD88` | `0xE50` | `0x000F000F` / `0x00080008` |
| 0 | 4 | `0x2D0` | embedded-data | `0xE50` | `0xEE8` | `0x000C000C` / `0x00060006` |
| 0 | 5 | `0x2E4` | embedded-data | `0xEE8` | `0xFA8` | `0x0010000D` / `0x00090007` |
| 0 | 6 | `0x2F8` | embedded-data | `0xFA8` | `0x1020` | `0x00090009` / `0x00050005` |
| 1 | 0 | `0x2F8` | embedded-data | `0xFA8` | `0x1020` | `0x00090009` / `0x00050005` |
| 2 | 0 | `0x30C` | external-resource-id | `0x375` | `` | `0x00600040` / `0x005F003F` |
| 2 | 1 | `0x320` | external-resource-id | `0x376` | `` | `0x00600040` / `0x005F003F` |
| 2 | 2 | `0x334` | external-resource-id | `0x377` | `` | `0x00600040` / `0x005F003F` |
| 2 | 3 | `0x348` | external-resource-id | `0x378` | `` | `0x00600040` / `0x005F003F` |
| 2 | 4 | `0x35C` | external-resource-id | `0x379` | `` | `0x00600040` / `0x005F003F` |
| 3 | 0 | `0x370` | external-resource-id | `0x38E` | `` | `0x00280024` / `0x00160016` |
| 3 | 1 | `0x3FC` | external-resource-id | `0x38E` | `` | `0x00280024` / `0x00160016` |
| 3 | 2 | `0x384` | external-resource-id | `0x38F` | `` | `0x002E0028` / `0x001A0019` |
| 3 | 3 | `0x410` | external-resource-id | `0x38F` | `` | `0x002E0028` / `0x001A0019` |
| 3 | 4 | `0x398` | external-resource-id | `0x390` | `` | `0x00320031` / `0x001C001B` |
| 3 | 5 | `0x424` | external-resource-id | `0x390` | `` | `0x00320031` / `0x001C001B` |
| 3 | 6 | `0x3AC` | external-resource-id | `0x391` | `` | `0x00330036` / `0x001D001E` |
| 3 | 7 | `0x438` | external-resource-id | `0x391` | `` | `0x00330036` / `0x001D001E` |
| 3 | 8 | `0x3C0` | external-resource-id | `0x392` | `` | `0x00370039` / `0x00210021` |
| 3 | 9 | `0x44C` | external-resource-id | `0x392` | `` | `0x00370039` / `0x00210021` |
| 3 | 10 | `0x3D4` | external-resource-id | `0x393` | `` | `0x003A0039` / `0x00230023` |
| 3 | 11 | `0x460` | external-resource-id | `0x393` | `` | `0x003A0039` / `0x00230023` |
| 3 | 12 | `0x3E8` | external-resource-id | `0x394` | `` | `0x00380039` / `0x00220026` |
| 3 | 13 | `0x474` | external-resource-id | `0x394` | `` | `0x00380039` / `0x00220026` |
| 4 | 0 | `0x910` | embedded-data | `0x3A70` | `0x3AB8` | `0x0006000C` / `0x00020005` |
| 4 | 1 | `0x924` | embedded-data | `0x3AB8` | `0x3B24` | `0x000B000C` / `0x00050005` |
| 4 | 2 | `0x938` | embedded-data | `0x3B24` | `0x3BA0` | `0x000E000C` / `0x00060005` |
| 4 | 3 | `0x94C` | embedded-data | `0x3BA0` | `0x3C14` | `0x0011000B` / `0x00080005` |
| 4 | 4 | `0x960` | embedded-data | `0x3C14` | `0x3C8C` | `0x0012000A` / `0x00080004` |
| 4 | 5 | `0x974` | embedded-data | `0x3C8C` | `0x3CF8` | `0x0010000B` / `0x00070005` |
| 4 | 6 | `0x988` | embedded-data | `0x3CF8` | `0x3D74` | `0x000E000C` / `0x00060005` |
| 4 | 7 | `0x99C` | embedded-data | `0x3D74` | `0x3DE8` | `0x000B000C` / `0x00040005` |
| 5 | 0 | `0x9B0` | embedded-data | `0x3DE8` | `0x3E48` | `0x0006000F` / `0x00020007` |
| 5 | 1 | `0x9C4` | embedded-data | `0x3E48` | `0x3EBC` | `0x000A000F` / `0x00040007` |
| 5 | 2 | `0x9D8` | embedded-data | `0x3EBC` | `0x3F3C` | `0x000D000F` / `0x00060007` |
| 5 | 3 | `0x9EC` | embedded-data | `0x3F3C` | `0x3FC4` | `0x0010000F` / `0x00070007` |
| 5 | 4 | `0xA00` | embedded-data | `0x3FC4` | `0x4044` | `0x0010000F` / `0x00070007` |
| 5 | 5 | `0xA14` | embedded-data | `0x4044` | `0x40D0` | `0x0010000F` / `0x00070007` |
| 5 | 6 | `0xA28` | embedded-data | `0x40D0` | `0x4160` | `0x000D000F` / `0x00050007` |
| 5 | 7 | `0xA3C` | embedded-data | `0x4160` | `0x459C` | `0x000A000F` / `0x00040007` |
| 6 | 0 | `0x870` | embedded-data | `0x35B8` | `0x3628` | `0x00060010` / `0x00020008` |
| 6 | 1 | `0x884` | embedded-data | `0x3628` | `0x36C8` | `0x000B0010` / `0x00050008` |
| 6 | 2 | `0x898` | embedded-data | `0x36C8` | `0x3770` | `0x000E000F` / `0x00060007` |
| 6 | 3 | `0x8AC` | embedded-data | `0x3770` | `0x3810` | `0x0010000F` / `0x00070007` |
| 6 | 4 | `0x8C0` | embedded-data | `0x3810` | `0x38A0` | `0x0011000F` / `0x00080007` |
| 6 | 5 | `0x8D4` | embedded-data | `0x38A0` | `0x3930` | `0x0010000F` / `0x00070007` |
| 6 | 6 | `0x8E8` | embedded-data | `0x3930` | `0x39D0` | `0x000E000F` / `0x00060007` |
| 6 | 7 | `0x8FC` | embedded-data | `0x39D0` | `0x3A70` | `0x000B0010` / `0x00040008` |
| 7 | 0 | `0x870` | embedded-data | `0x35B8` | `0x3628` | `0x00060010` / `0x00020008` |
| 7 | 1 | `0x884` | embedded-data | `0x3628` | `0x36C8` | `0x000B0010` / `0x00050008` |
| 7 | 2 | `0x898` | embedded-data | `0x36C8` | `0x3770` | `0x000E000F` / `0x00060007` |
| 7 | 3 | `0x8AC` | embedded-data | `0x3770` | `0x3810` | `0x0010000F` / `0x00070007` |
| 7 | 4 | `0x8C0` | embedded-data | `0x3810` | `0x38A0` | `0x0011000F` / `0x00080007` |
| 7 | 5 | `0x8D4` | embedded-data | `0x38A0` | `0x3930` | `0x0010000F` / `0x00070007` |
| 7 | 6 | `0x8E8` | embedded-data | `0x3930` | `0x39D0` | `0x000E000F` / `0x00060007` |
| 7 | 7 | `0x8FC` | embedded-data | `0x39D0` | `0x3A70` | `0x000B0010` / `0x00040008` |
| 10 | 0 | `0x4524` | embedded-data | `0x459C` | `0x4C80` | `0x0062001A` / `0x0031FF9F` |
| 10 | 1 | `0x4538` | embedded-data | `0x4C80` | `0x52F4` | `0x00610018` / `0x0030FF9E` |
| 10 | 2 | `0x454C` | embedded-data | `0x52F4` | `0x58B0` | `0x00630016` / `0x0031FF9D` |
| 10 | 3 | `0x4560` | embedded-data | `0x58B0` | `0x5E40` | `0x00620018` / `0x0030FF9C` |
| 10 | 4 | `0x4574` | embedded-data | `0x5E40` | `0x6230` | `0x005F0015` / `0x002EFF9A` |
| 10 | 5 | `0x4588` | embedded-data | `0x6230` | `0x64E0` | `0x00600014` / `0x002FFF9A` |
| 20 | 0 | `0x488` | external-resource-id | `0x36B` | `` | `0x0025001C` / `0x0011000D` |
| 20 | 1 | `0x49C` | external-resource-id | `0x36C` | `` | `0x003C002D` / `0x001D0015` |
| 20 | 2 | `0x4B0` | external-resource-id | `0x36D` | `` | `0x003F0035` / `0x0020001A` |
| 20 | 3 | `0x4C4` | external-resource-id | `0x36E` | `` | `0x00400037` / `0x001F001A` |
| 20 | 4 | `0x4D8` | external-resource-id | `0x36F` | `` | `0x00400032` / `0x00200015` |
| 21 | 0 | `0x4EC` | external-resource-id | `0x370` | `` | `0x00140010` / `0x00090007` |
| 21 | 1 | `0x500` | external-resource-id | `0x371` | `` | `0x00200019` / `0x0010000B` |
| 21 | 2 | `0x514` | external-resource-id | `0x372` | `` | `0x0020001B` / `0x0010000D` |
| 21 | 3 | `0x528` | external-resource-id | `0x373` | `` | `0x0020001F` / `0x0010000E` |
| 21 | 4 | `0x53C` | external-resource-id | `0x374` | `` | `0x001F001B` / `0x000F000B` |
| 22 | 0 | `0x58C` | external-resource-id | `0x387` | `` | `0x005B000B` / `0x00380006` |
| 22 | 1 | `0x5A0` | external-resource-id | `0x388` | `` | `0x0059000B` / `0x00370006` |
| 22 | 2 | `0x5B4` | external-resource-id | `0x389` | `` | `0x0057000B` / `0x00360006` |
| 22 | 3 | `0x5C8` | external-resource-id | `0x38A` | `` | `0x0059000B` / `0x00380005` |
| 22 | 4 | `0x5DC` | external-resource-id | `0x38B` | `` | `0x0056000A` / `0x00330004` |
| 23 | 0 | `0x550` | external-resource-id | `0x384` | `` | `0x0066001A` / `0x003C000C` |
| 23 | 1 | `0x564` | external-resource-id | `0x385` | `` | `0x00750025` / `0x00420010` |
| 23 | 2 | `0x578` | external-resource-id | `0x386` | `` | `0x0067001C` / `0x003B000C` |
| 24 | 0 | `0x7D0` | embedded-data | `0x2F5C` | `0x3044` | `0x00110018` / `0x0008000D` |
| 24 | 1 | `0x7E4` | embedded-data | `0x3044` | `0x3124` | `0x00110018` / `0x0008000D` |
| 24 | 2 | `0x7F8` | embedded-data | `0x3124` | `0x31F8` | `0x00100018` / `0x0007000D` |
| 24 | 3 | `0x80C` | embedded-data | `0x31F8` | `0x32BC` | `0x00100018` / `0x0007000D` |
| 24 | 4 | `0x820` | embedded-data | `0x32BC` | `0x336C` | `0x000F0018` / `0x0007000D` |
| 24 | 5 | `0x834` | embedded-data | `0x336C` | `0x3414` | `0x000F0018` / `0x0008000D` |
| 24 | 6 | `0x848` | embedded-data | `0x3414` | `0x34D8` | `0x00100018` / `0x0008000D` |
| 24 | 7 | `0x85C` | embedded-data | `0x34D8` | `0x35B8` | `0x00110018` / `0x0008000D` |
| 25 | 0 | `0x730` | embedded-data | `0x2714` | `0x27F8` | `0x00110017` / `0x0008000F` |
| 25 | 1 | `0x744` | embedded-data | `0x27F8` | `0x28F8` | `0x00110017` / `0x0008000F` |
| 25 | 2 | `0x758` | embedded-data | `0x28F8` | `0x2A08` | `0x00100017` / `0x0007000F` |
| 25 | 3 | `0x76C` | embedded-data | `0x2A08` | `0x2B20` | `0x00100017` / `0x0008000F` |
| 25 | 4 | `0x780` | embedded-data | `0x2B20` | `0x2C44` | `0x00110017` / `0x0008000F` |
| 25 | 5 | `0x794` | embedded-data | `0x2C44` | `0x2D64` | `0x00100017` / `0x0007000F` |
| 25 | 6 | `0x7A8` | embedded-data | `0x2D64` | `0x2E70` | `0x00100017` / `0x0008000F` |
| 25 | 7 | `0x7BC` | embedded-data | `0x2E70` | `0x2F5C` | `0x00100017` / `0x0008000F` |
| 26 | 0 | `0x5F0` | embedded-data | `0x1020` | `0x1208` | `0x00160017` / `0x000B000B` |
| 26 | 1 | `0x604` | embedded-data | `0x1208` | `0x1400` | `0x00160017` / `0x000B000B` |
| 26 | 2 | `0x618` | embedded-data | `0x1400` | `0x15F4` | `0x00160017` / `0x000B000B` |
| 26 | 3 | `0x62C` | embedded-data | `0x15F4` | `0x17E4` | `0x00160017` / `0x000B000B` |
| 26 | 4 | `0x640` | embedded-data | `0x17E4` | `0x19CC` | `0x00160017` / `0x000B000B` |
| 26 | 5 | `0x654` | embedded-data | `0x19CC` | `0x1BB8` | `0x00160017` / `0x000B000B` |
| 26 | 6 | `0x668` | embedded-data | `0x1BB8` | `0x1DAC` | `0x00160017` / `0x000B000B` |
| 26 | 7 | `0x67C` | embedded-data | `0x1DAC` | `0x1F94` | `0x00160017` / `0x000B000B` |
| 27 | 0 | `0x690` | embedded-data | `0x1F94` | `0x208C` | `0x00110017` / `0x0008000F` |
| 27 | 1 | `0x6A4` | embedded-data | `0x208C` | `0x218C` | `0x00110017` / `0x0008000F` |
| 27 | 2 | `0x6B8` | embedded-data | `0x218C` | `0x2288` | `0x00100017` / `0x0007000F` |
| 27 | 3 | `0x6CC` | embedded-data | `0x2288` | `0x2370` | `0x000F0017` / `0x0007000F` |
| 27 | 4 | `0x6E0` | embedded-data | `0x2370` | `0x2460` | `0x000F0017` / `0x0007000F` |
| 27 | 5 | `0x6F4` | embedded-data | `0x2460` | `0x2540` | `0x000F0017` / `0x0007000F` |
| 27 | 6 | `0x708` | embedded-data | `0x2540` | `0x262C` | `0x00100017` / `0x0008000F` |
| 27 | 7 | `0x71C` | embedded-data | `0x262C` | `0x2714` | `0x00100017` / `0x0008000F` |
| 28 | 0 | `0x648C` | external-resource-id | `0x28F` | `` | `0x00110011` / `0x00070009` |
| 28 | 1 | `0x64A0` | external-resource-id | `0x290` | `` | `0x00100011` / `0x00060009` |
| 28 | 2 | `0x64B4` | external-resource-id | `0x291` | `` | `0x000F0011` / `0x00060009` |
| 28 | 3 | `0x64C8` | external-resource-id | `0x292` | `` | `0x00100011` / `0x00070009` |

## Water-specific notes, constraints, and pending questions

- The complete `0x64E0`-byte ROM resource file matches RDRAM at `0x802504A8` byte-for-byte in live Water gameplay.
- All nine standard `0x30`-byte pickup records are contiguous and mapped: three Water icons, two Health urns, and one each of Extra-life urn, Herbs, mana, and Potion.
- The supplied Lua comments identify slot `26` as mana and substitute Herbs in the virtual item pool; the native callback `0x80038A58` and presentation pointer `0x800B1C14` remain distinct from Herbs.
- Water's progression metadata remains stage-local: Water Three Bars requires `water-triangle`; Water Moon requires `water-three-bars`; the second Health urn requires `water-moon`.
- Slot `28` is Water's Health-urn resource: an `external-resource-id-bundle` with four records using external IDs `0x28F..0x292`; both Water Health-urn pickup records select this slot.
- **Static-confirmed Water source fact:** the raw payloads behind Health-urn IDs `0x28F..0x292` were located in Water's compressed source package, global file ID `0x73` (file-table entry ROM `0x000A5574`), with raw byte lengths `340, 272, 272, 272`. The cross-stage conversion method and Proof G/H outcomes are owned by [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).
- Water's slot-`27` Potion is an embedded-data bundle. Its embedded frames supplied the Water side of the storage-form equivalence check against Fire external Potion payloads `0x27F..0x286`; the generalized conclusion remains on [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).
- Occupied selectors without ordinary pickup users remain protected because other Water actors or scripts may reference them. Slot `7`, for example, aliases outer offset `0x10C` used by the Water Moon bundle but has no ordinary-pickup user.
- Empty stock selectors `8, 9, 11..19` are logical selector capacity only. Per the shared schema, they are not evidence of free physical file bytes or production-safe allocation space.

## Related owners

- [Stage catalogs](Stage-Catalogs) — shared schema, notation, safety rules, and eight-stage index.
- [Data structures and encodings](Data-Structures-and-Encodings) — ordinary `0x30`-byte record grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file-table, loader, overlay, and selector/resource grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and lifecycle.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded patch sites.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior and modeled Water dependencies.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — cross-stage materializer, external-to-embedded conversion, proof history, solver, and production gates.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and stage-transition lifecycle.
