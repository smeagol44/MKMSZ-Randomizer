# Fire stage catalog

> **Scope:** Stage-local catalog for Fire, compact selector `5` / native stage ID `5`. Shared record grammar, resource notation, evidence labels, and safety rules are owned by [Stage catalogs](Stage-Catalogs). Global loader/materializer conclusions and literal allocation ownership are deliberately linked rather than redefined here.

## Stage identity and evidence

- **Static-confirmed:** all 16 ordinary pickup records, all 27 stock outer slots, and the recognized resource records below are decoded from the clean USA N64 ROM.
- **Runtime-confirmed:** the Fire resource-file mapping was matched against captured runtime memory at `0x80224C88`.
- **Runtime-confirmed:** representative Fire ordinary-pickup collection/persistence is established, but all 16 Fire records have not been individually exhausted one by one in runtime testing.
- Fire's three icon pickups call stage-qualified overlay VA `0x802F0EBC`. That address is Fire-overlay evidence and must not be treated as a globally resident callback identity.
- **Runtime-confirmed, proof-only:** a bounded Fire foreign-item proof populated stock logical slot `5` with a Prison Level 1 key resource and relocated/expanded the Fire resource file. Its exact Fire-local ranges are preserved below.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `5` |
| Global resource file ID | `0x3C` |
| File-table entry ROM | `0x000A52E0` |
| Resource ROM range | `0x00388260..0x0038A78F` |
| File size | `0x2530` (9520 bytes) |
| File-table flag | `0` |
| Verified runtime base | `0x80224C88` |
| Outer slots | `27` |
| Outer-table end | `0x6C` |
| First descriptor | `0x6C` |
| Empty logical slots | `5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19` |
| Unknown/nonstandard slots | `none` |
| Pickup records | `16` |

## Ordinary pickup records

| # | Decoded identity | ROM base | RDRAM base | X | Y | Z | +0C | +10 type | +14 parameter | +18 callback | +1C | +20 | +24 slot | +28 presentation | +2C collected | Token | Requires |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | Potion | `0x000E6218` | `0x802F14C8` | `0xFFFE0ADF` | `0xFFFFAD00` | `0x00000000` | `0x00000004` | `0x0000000B` | `0x00000000` | `0x800388FC` | `0x00000020` | `0x00000020` | `0x00000018` | `0x800B1BAC` | `0x00000000` | — | — |
| 2 | Formula | `0x000E6248` | `0x802F14F8` | `0x000C8E72` | `0xFFFFAD00` | `0x00000000` | `0x00000004` | `0x00000009` | `0x00000000` | `0x8003898C` | `0x00000020` | `0x00000020` | `0x00000019` | `0x800B1D38` | `0x00000000` | — | — |
| 3 | Health urn | `0x000E6098` | `0x802F1348` | `0x001925CA` | `0xFFFFAD00` | `0x00000000` | `0x00000004` | `0x00000006` | `0x00000000` | `0x800389EC` | `0x00000020` | `0x00000020` | `0x0000001A` | `0x800B1D38` | `0x00000000` | — | — |
| 4 | Herbs | `0x000E6308` | `0x802F15B8` | `0x001F25E6` | `0xFFFF2B00` | `0x00000000` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `0x00000015` | `0x800B1D38` | `0x00000000` | — | — |
| 5 | Fire icon param 0 | `0x000E60F8` | `0x802F13A8` | `0x0024B2E6` | `0xFFFE4500` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000000` | `0x802F0EBC` | `0x00000020` | `0x00000020` | `0x00000000` | `0x800B1D18` | `0x00000000` | `fire-triangle-up` | — |
| 6 | Health urn | `0x000E60C8` | `0x802F1378` | `0x00342508` | `0xFFFFA918` | `0x00000000` | `0x00000004` | `0x00000006` | `0x00000000` | `0x800389EC` | `0x00000020` | `0x00000020` | `0x0000001A` | `0x800B1D38` | `0x00000000` | — | — |
| 7 | Shield | `0x000E6368` | `0x802F1618` | `0x005BCA4F` | `0x00019100` | `0x00000000` | `0x00000004` | `0x00000007` | `0x00000000` | `0x8003892C` | `0x00000020` | `0x00000020` | `0x00000016` | `0x800B1D38` | `0x00000000` | — | — |
| 8 | Herbs | `0x000E6338` | `0x802F15E8` | `0x005D2E1D` | `0x00019100` | `0x00000000` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `0x00000015` | `0x800B1D38` | `0x00000000` | — | — |
| 9 | Extra life | `0x000E6278` | `0x802F1528` | `0x0059085E` | `0x00037D00` | `0x00000000` | `0x00000004` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `0x00000014` | `0x800B1D38` | `0x00000000` | — | — |
| 10 | Fire icon param 1 | `0x000E61B8` | `0x802F1468` | `0x004FC5F6` | `0x00037D00` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000001` | `0x802F0EBC` | `0x00000020` | `0x00000020` | `0x00000001` | `0x800B1D18` | `0x00000000` | `fire-two-bars` | — |
| 11 | Extra life | `0x000E6398` | `0x802F1648` | `0x006D7ADF` | `0x00013100` | `0x00000000` | `0x00000004` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `0x00000014` | `0x800B1D38` | `0x00000000` | — | — |
| 12 | Eye | `0x000E62A8` | `0x802F1558` | `0x007EBAAB` | `0xFFFFAD00` | `0x00000000` | `0x00000004` | `0x0000000A` | `0x00000000` | `0x8003895C` | `0x00000020` | `0x00000020` | `0x00000017` | `0x800B1D38` | `0x00000000` | — | — |
| 13 | Potion | `0x000E62D8` | `0x802F1588` | `0x00B06090` | `0xFFFF7600` | `0x00000000` | `0x00000004` | `0x0000000B` | `0x00000000` | `0x800388FC` | `0x00000020` | `0x00000020` | `0x00000018` | `0x800B1BAC` | `0x00000000` | — | — |
| 14 | Herbs | `0x000E63C8` | `0x802F1678` | `0x00A76398` | `0xFFFFB100` | `0x00000000` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `0x00000015` | `0x800B1D38` | `0x00000000` | — | — |
| 15 | Fire icon param 2 | `0x000E61E8` | `0x802F1498` | `0x00A5E5F0` | `0xFFFFB100` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00000002` | `0x802F0EBC` | `0x00000020` | `0x00000020` | `0x00000002` | `0x800B1D18` | `0x00000000` | `fire-triangle-down` | — |
| 16 | Herbs | `0x000E63F8` | `0x802F16A8` | `0x00BAE3A4` | `0xFFFDC700` | `0x00000000` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `0x00000015` | `0x800B1D38` | `0x00000000` | — | — |

## Pickup-to-resource usage

| ROM base | Callback | Parameter | Slot | Presentation |
|---:|---:|---:|---:|---:|
| `0x000E6218` | `0x800388FC` | `0x00000000` | `0x00000018` | `0x800B1BAC` |
| `0x000E6248` | `0x8003898C` | `0x00000000` | `0x00000019` | `0x800B1D38` |
| `0x000E6098` | `0x800389EC` | `0x00000000` | `0x0000001A` | `0x800B1D38` |
| `0x000E6308` | `0x800389BC` | `0x00000000` | `0x00000015` | `0x800B1D38` |
| `0x000E60F8` | `0x802F0EBC` | `0x00000000` | `0x00000000` | `0x800B1D18` |
| `0x000E60C8` | `0x800389EC` | `0x00000000` | `0x0000001A` | `0x800B1D38` |
| `0x000E6368` | `0x8003892C` | `0x00000000` | `0x00000016` | `0x800B1D38` |
| `0x000E6338` | `0x800389BC` | `0x00000000` | `0x00000015` | `0x800B1D38` |
| `0x000E6278` | `0x80038A1C` | `0x00000000` | `0x00000014` | `0x800B1D38` |
| `0x000E61B8` | `0x802F0EBC` | `0x00000001` | `0x00000001` | `0x800B1D18` |
| `0x000E6398` | `0x80038A1C` | `0x00000000` | `0x00000014` | `0x800B1D38` |
| `0x000E62A8` | `0x8003895C` | `0x00000000` | `0x00000017` | `0x800B1D38` |
| `0x000E62D8` | `0x800388FC` | `0x00000000` | `0x00000018` | `0x800B1BAC` |
| `0x000E63C8` | `0x800389BC` | `0x00000000` | `0x00000015` | `0x800B1D38` |
| `0x000E61E8` | `0x802F0EBC` | `0x00000002` | `0x00000002` | `0x800B1D18` |
| `0x000E63F8` | `0x800389BC` | `0x00000000` | `0x00000015` | `0x800B1D38` |

## Outer resource slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Fire icon, parameter 0 | `0x6C` | embedded-data-bundle | 8 | 1 |
| 1 | Fire icon, parameter 1 | `0x94` | embedded-data-bundle | 8 | 1 |
| 2 | Fire icon, parameter 2 | `0xBC` | embedded-data-bundle | 8 | 1 |
| 3 | Non-pickup/unknown resource | `0x128` | zero-terminated-external-list | 7 | 0 |
| 4 | Non-pickup/unknown resource | `0xE4` | embedded-data-bundle-mode0-selector | 8 | 0 |
| 5 | Unused logical slot | `0` | empty | — | 0 |
| 6 | Unused logical slot | `0` | empty | — | 0 |
| 7 | Unused logical slot | `0` | empty | — | 0 |
| 8 | Unused logical slot | `0` | empty | — | 0 |
| 9 | Unused logical slot | `0` | empty | — | 0 |
| 10 | Unused logical slot | `0` | empty | — | 0 |
| 11 | Unused logical slot | `0` | empty | — | 0 |
| 12 | Unused logical slot | `0` | empty | — | 0 |
| 13 | Unused logical slot | `0` | empty | — | 0 |
| 14 | Unused logical slot | `0` | empty | — | 0 |
| 15 | Unused logical slot | `0` | empty | — | 0 |
| 16 | Unused logical slot | `0` | empty | — | 0 |
| 17 | Unused logical slot | `0` | empty | — | 0 |
| 18 | Unused logical slot | `0` | empty | — | 0 |
| 19 | Unused logical slot | `0` | empty | — | 0 |
| 20 | Extra-life urn | `0x83C` | external-resource-id-bundle | 8 | 2 |
| 21 | Herbs | `0x148` | embedded-data-bundle | 8 | 4 |
| 22 | Shield | `0x6AC` | external-resource-id-bundle | 8 | 1 |
| 23 | Eye | `0x5E4` | external-resource-id-bundle | 8 | 1 |
| 24 | Potion | `0x774` | external-resource-id-bundle | 8 | 2 |
| 25 | Formula | `0x51C` | external-resource-id-bundle | 8 | 1 |
| 26 | Health urn | `0x904` | external-resource-id-bundle | 4 | 2 |

## Recognized bundle/list records

| Slot | Frame | Record | Storage | Resource/data value | Inferred end | Dimensions words |
|---:|---:|---:|---|---:|---:|---|
| 0 | 0 | `0x170` | embedded-data | `0x11A0` | `0x1200` | `0x0006000F` / `0x00020007` |
| 0 | 1 | `0x184` | embedded-data | `0x1200` | `0x1274` | `0x000A000F` / `0x00040007` |
| 0 | 2 | `0x198` | embedded-data | `0x1274` | `0x12F4` | `0x000D000F` / `0x00060007` |
| 0 | 3 | `0x1AC` | embedded-data | `0x12F4` | `0x137C` | `0x0010000F` / `0x00070007` |
| 0 | 4 | `0x1C0` | embedded-data | `0x137C` | `0x13FC` | `0x0010000F` / `0x00070007` |
| 0 | 5 | `0x1D4` | embedded-data | `0x13FC` | `0x1488` | `0x0010000F` / `0x00070007` |
| 0 | 6 | `0x1E8` | embedded-data | `0x1488` | `0x1518` | `0x000D000F` / `0x00050007` |
| 0 | 7 | `0x1FC` | embedded-data | `0x1518` | `0x1598` | `0x000A000F` / `0x00040007` |
| 1 | 0 | `0x210` | embedded-data | `0x1598` | `0x15E0` | `0x0006000C` / `0x00020005` |
| 1 | 1 | `0x224` | embedded-data | `0x15E0` | `0x163C` | `0x000B000C` / `0x00050005` |
| 1 | 2 | `0x238` | embedded-data | `0x163C` | `0x16AC` | `0x000E000C` / `0x00060005` |
| 1 | 3 | `0x24C` | embedded-data | `0x16AC` | `0x170C` | `0x0010000B` / `0x00070005` |
| 1 | 4 | `0x260` | embedded-data | `0x170C` | `0x1770` | `0x0012000A` / `0x00080004` |
| 1 | 5 | `0x274` | embedded-data | `0x1770` | `0x17D0` | `0x0010000B` / `0x00070005` |
| 1 | 6 | `0x288` | embedded-data | `0x17D0` | `0x1840` | `0x000E000C` / `0x00060005` |
| 1 | 7 | `0x29C` | embedded-data | `0x1840` | `0x18B8` | `0x000B000C` / `0x00040005` |
| 2 | 0 | `0x2B0` | embedded-data | `0x18B8` | `0x1900` | `0x0006000F` / `0x00020007` |
| 2 | 1 | `0x2C4` | embedded-data | `0x1900` | `0x196C` | `0x0009000F` / `0x00040007` |
| 2 | 2 | `0x2D8` | embedded-data | `0x196C` | `0x19F4` | `0x000D000F` / `0x00060007` |
| 2 | 3 | `0x2EC` | embedded-data | `0x19F4` | `0x1A80` | `0x0010000F` / `0x00070007` |
| 2 | 4 | `0x300` | embedded-data | `0x1A80` | `0x1AFC` | `0x0010000E` / `0x00070007` |
| 2 | 5 | `0x314` | embedded-data | `0x1AFC` | `0x1B80` | `0x0010000F` / `0x00070007` |
| 2 | 6 | `0x328` | embedded-data | `0x1B80` | `0x1C08` | `0x000D000F` / `0x00050007` |
| 2 | 7 | `0x33C` | embedded-data | `0x1C08` | `0x1C88` | `0x000A000F` / `0x00040007` |
| 3 | 0 | `0x3F0` | external-resource-id | `0x38E` | `` | `0x00280024` / `0x00160016` |
| 3 | 1 | `0x404` | external-resource-id | `0x38F` | `` | `0x002E0028` / `0x001A0019` |
| 3 | 2 | `0x418` | external-resource-id | `0x390` | `` | `0x00320031` / `0x001C001B` |
| 3 | 3 | `0x42C` | external-resource-id | `0x391` | `` | `0x00330036` / `0x001D001E` |
| 3 | 4 | `0x440` | external-resource-id | `0x392` | `` | `0x00370039` / `0x00210021` |
| 3 | 5 | `0x454` | external-resource-id | `0x393` | `` | `0x003A0039` / `0x00230023` |
| 3 | 6 | `0x468` | external-resource-id | `0x394` | `` | `0x00380039` / `0x00220026` |
| 4 | 0 | `0x350` | embedded-data | `0x96C` | `0xA70` | `0x00160016` / `0x000A000A` |
| 4 | 1 | `0x364` | embedded-data | `0xA70` | `0xB8C` | `0x00160015` / `0x000A000A` |
| 4 | 2 | `0x378` | embedded-data | `0xB8C` | `0xC7C` | `0x00160013` / `0x000A000A` |
| 4 | 3 | `0x38C` | embedded-data | `0xC7C` | `0xD5C` | `0x00160013` / `0x000A000A` |
| 4 | 4 | `0x3A0` | embedded-data | `0xD5C` | `0xE40` | `0x00160013` / `0x000A000A` |
| 4 | 5 | `0x3B4` | embedded-data | `0xE40` | `0xF3C` | `0x00160014` / `0x000A000B` |
| 4 | 6 | `0x3C8` | embedded-data | `0xF3C` | `0x1074` | `0x00160017` / `0x000A000E` |
| 4 | 7 | `0x3DC` | embedded-data | `0x1074` | `0x11A0` | `0x00160017` / `0x000A000E` |
| 20 | 0 | `0x864` | external-resource-id | `0x287` | `` | `0x00110018` / `0x0008000D` |
| 20 | 1 | `0x878` | external-resource-id | `0x288` | `` | `0x00110018` / `0x0008000D` |
| 20 | 2 | `0x88C` | external-resource-id | `0x289` | `` | `0x00100018` / `0x0007000D` |
| 20 | 3 | `0x8A0` | external-resource-id | `0x28A` | `` | `0x00100018` / `0x0007000D` |
| 20 | 4 | `0x8B4` | external-resource-id | `0x28B` | `` | `0x000F0018` / `0x0007000D` |
| 20 | 5 | `0x8C8` | external-resource-id | `0x28C` | `` | `0x000F0018` / `0x0008000D` |
| 20 | 6 | `0x8DC` | external-resource-id | `0x28D` | `` | `0x00100018` / `0x0008000D` |
| 20 | 7 | `0x8F0` | external-resource-id | `0x28E` | `` | `0x00110018` / `0x0008000D` |
| 21 | 0 | `0x47C` | embedded-data | `0x1C88` | `0x1D6C` | `0x00110017` / `0x0008000F` |
| 21 | 1 | `0x490` | embedded-data | `0x1D6C` | `0x1E6C` | `0x00110017` / `0x0008000F` |
| 21 | 2 | `0x4A4` | embedded-data | `0x1E6C` | `0x1F7C` | `0x00100017` / `0x0007000F` |
| 21 | 3 | `0x4B8` | embedded-data | `0x1F7C` | `0x2094` | `0x00100017` / `0x0008000F` |
| 21 | 4 | `0x4CC` | embedded-data | `0x2094` | `0x21B8` | `0x00110017` / `0x0008000F` |
| 21 | 5 | `0x4E0` | embedded-data | `0x21B8` | `0x22D8` | `0x00100017` / `0x0007000F` |
| 21 | 6 | `0x4F4` | embedded-data | `0x22D8` | `0x23E4` | `0x00100017` / `0x0008000F` |
| 21 | 7 | `0x508` | embedded-data | `0x23E4` | `0x2530` | `0x00100017` / `0x0008000F` |
| 22 | 0 | `0x6D4` | external-resource-id | `0x26F` | `` | `0x0009001A` / `0x0004000D` |
| 22 | 1 | `0x6E8` | external-resource-id | `0x270` | `` | `0x0009001A` / `0x0004000D` |
| 22 | 2 | `0x6FC` | external-resource-id | `0x271` | `` | `0x000C001A` / `0x0006000D` |
| 22 | 3 | `0x710` | external-resource-id | `0x272` | `` | `0x0010001A` / `0x0007000D` |
| 22 | 4 | `0x724` | external-resource-id | `0x273` | `` | `0x0011001A` / `0x0007000D` |
| 22 | 5 | `0x738` | external-resource-id | `0x274` | `` | `0x000F001A` / `0x0006000D` |
| 22 | 6 | `0x74C` | external-resource-id | `0x275` | `` | `0x000C001A` / `0x0005000D` |
| 22 | 7 | `0x760` | external-resource-id | `0x276` | `` | `0x0009001A` / `0x0004000D` |
| 23 | 0 | `0x60C` | external-resource-id | `0x267` | `` | `0x0012000E` / `0x00080006` |
| 23 | 1 | `0x620` | external-resource-id | `0x268` | `` | `0x0011000E` / `0x00070006` |
| 23 | 2 | `0x634` | external-resource-id | `0x269` | `` | `0x0010000E` / `0x00060006` |
| 23 | 3 | `0x648` | external-resource-id | `0x26A` | `` | `0x000D000E` / `0x00050006` |
| 23 | 4 | `0x65C` | external-resource-id | `0x26B` | `` | `0x000C000E` / `0x00050006` |
| 23 | 5 | `0x670` | external-resource-id | `0x26C` | `` | `0x000D000E` / `0x00060006` |
| 23 | 6 | `0x684` | external-resource-id | `0x26D` | `` | `0x0010000E` / `0x00070006` |
| 23 | 7 | `0x698` | external-resource-id | `0x26E` | `` | `0x0012000E` / `0x00080006` |
| 24 | 0 | `0x79C` | external-resource-id | `0x27F` | `` | `0x00110017` / `0x0008000F` |
| 24 | 1 | `0x7B0` | external-resource-id | `0x280` | `` | `0x00110017` / `0x0008000F` |
| 24 | 2 | `0x7C4` | external-resource-id | `0x281` | `` | `0x00100017` / `0x0007000F` |
| 24 | 3 | `0x7D8` | external-resource-id | `0x282` | `` | `0x000F0017` / `0x0007000F` |
| 24 | 4 | `0x7EC` | external-resource-id | `0x283` | `` | `0x000F0017` / `0x0007000F` |
| 24 | 5 | `0x800` | external-resource-id | `0x284` | `` | `0x000F0017` / `0x0007000F` |
| 24 | 6 | `0x814` | external-resource-id | `0x285` | `` | `0x00100017` / `0x0008000F` |
| 24 | 7 | `0x828` | external-resource-id | `0x286` | `` | `0x00100017` / `0x0008000F` |
| 25 | 0 | `0x544` | external-resource-id | `0x277` | `` | `0x000C0018` / `0x0006000D` |
| 25 | 1 | `0x558` | external-resource-id | `0x278` | `` | `0x000D0018` / `0x0007000D` |
| 25 | 2 | `0x56C` | external-resource-id | `0x279` | `` | `0x000E0019` / `0x0008000D` |
| 25 | 3 | `0x580` | external-resource-id | `0x27A` | `` | `0x000F0019` / `0x0008000D` |
| 25 | 4 | `0x594` | external-resource-id | `0x27B` | `` | `0x000F0019` / `0x0008000D` |
| 25 | 5 | `0x5A8` | external-resource-id | `0x27C` | `` | `0x000E0019` / `0x0007000D` |
| 25 | 6 | `0x5BC` | external-resource-id | `0x27D` | `` | `0x000D0019` / `0x0006000D` |
| 25 | 7 | `0x5D0` | external-resource-id | `0x27E` | `` | `0x000C0018` / `0x0006000D` |
| 26 | 0 | `0x91C` | external-resource-id | `0x28F` | `` | `0x00110011` / `0x00070009` |
| 26 | 1 | `0x930` | external-resource-id | `0x290` | `` | `0x00100011` / `0x00060009` |
| 26 | 2 | `0x944` | external-resource-id | `0x291` | `` | `0x000F0011` / `0x00060009` |
| 26 | 3 | `0x958` | external-resource-id | `0x292` | `` | `0x00100011` / `0x00070009` |

## Fire-specific notes, constraints, and proof-local evidence

- Stock Fire has **15 empty logical outer slots**, selectors `5..19`, in the 27-word table. This is **Static-confirmed selector-table capacity only**. It is not evidence of 15 free physical payload regions, unused RDRAM, or production-safe allocation space, and the foreign-key proof below runtime-tested only one of those logical slots.
- Slots `20..26` are stock ordinary-item resources. Fire Potion (slot `24`) uses external IDs `0x27F..0x286`; Fire Health urn (slot `26`) uses external IDs `0x28F..0x292`. Formula, Eye, Shield, Extra-life urn, and Health urn also preserve their exact external-ID records in the table above. Cross-stage storage-form equivalence and external-to-embedded conversion are owned by [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).
- **Early raw Prison-to-Fire identity copy — Rejected / failed in this bounded route:** copying the Prison identity without destination resource materialization produced no usable item because the source selector was not meaningful against Fire's stage resource file.
- **Foreign Prison Level 1 key proof — Runtime-confirmed, proof-only:** clean stock slot `5` was populated with the imported key bundle. The appended descriptor began at file-relative `0x2530`; appended resource records occupied exact file-relative interval `0x2558..0x25F7`. The proof resource file expanded from stock size `0x2530` to `0x2BE8`, so the full appended proof-only file-relative region is `0x2530..0x2BE7`.
- That expanded proof file was relocated to ROM `0x00F00000..0x00F02BE7`. A dedicated native callback at VA `0x8008EAEC` / ROM `0x0008F6EC` awarded Prison Level 1 key inventory ID `0x1A`. The foreign model rendered and awarded correctly while Fire's original Herbs resource remained intact.
- The foreign-key proof reused **one existing empty stock selector**; it did not add a 28th stock-table entry and did not establish selectors `6..19` as runtime-proven import slots. The ROM relocation, appended `0x2530..0x2BE7` region, and callback placement are disposable proof facts, **not production allocations**.
- **External-ID-only Potion transplant — Rejected / failed:** an earlier Fire Potion transplant that relied on external-resource IDs produced corrupted graphics. The generalized reason and the successful self-contained conversion strategy are owned by the global materialization page.
- Fire ordinary-enemy stream/resource-loading research is canonically owned by [Enemy randomization](Enemy-Randomization). This catalog does not duplicate the global constructor/resource-table mechanics or turn the enemy-import proof's arena arithmetic into Fire resource-file allocation claims.
- Current limits remain bounded: the foreign-key proof establishes one imported key/resource/callback composition in Fire, not arbitrary foreign item families, generic destination-safe key/crystal awards, or production-safe reuse of the proof ROM placement. The 15 stock empty selectors remain logical-capacity facts only.

## Related owners

- [Stage catalogs](Stage-Catalogs) — shared schema, notation, safety rules, and eight-stage index.
- [Data structures and encodings](Data-Structures-and-Encodings) — ordinary `0x30`-byte record grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file-table, loader, overlay, and selector/resource grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership, lifecycle, and proof/production allocation boundaries.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded ROM edit sites.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior and modeled stage dependencies.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — extension-selector/materializer mechanics, external-to-embedded interpretation, planner/deduplication, solver rules, and full proof chronology.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and stage-transition lifecycle.
- [Enemy randomization](Enemy-Randomization) — Fire ordinary-enemy stream/resource-import architecture and proof history.
