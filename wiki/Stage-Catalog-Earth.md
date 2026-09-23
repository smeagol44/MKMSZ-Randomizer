# Earth stage catalog

> **Scope:** Stage-local catalog for Earth, compact selector `3` / native stage ID `3`. Shared record grammar, resource notation, evidence labels, and safety rules are owned by [Stage catalogs](Stage-Catalogs).

## Stage identity and evidence

- **Static-confirmed:** all 20 ordinary pickup records, all 65 stock outer slots, and the recognized resource records below are decoded from the clean USA N64 ROM.
- **Runtime-confirmed:** the complete `0x225B0`-byte stage resource file was matched byte-for-byte at RDRAM `0x802434B8` during live Earth gameplay.
- **Runtime-confirmed:** the all-eight-stage persistence validation collected/restored a representative Earth ordinary pickup. The 20 Earth records have not been individually exhausted one by one in runtime testing.
- Earth's three stage key pickups use stage-qualified overlay callback VA `0x802F52B0`; this address is Earth-overlay evidence, not a globally resident callback identity.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `3` |
| Global resource file ID | `0x88` |
| File-table entry ROM | `0x000A5670` |
| Resource ROM range | `0x006BAEC0..0x006DD46F` |
| File size | `0x225B0` (140720 bytes) |
| File-table flag | `0` |
| Verified runtime base | `0x802434B8` |
| Outer slots | `65` |
| Outer-table end | `0x104` |
| First descriptor | `0x104` |
| Empty logical slots | `41, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64` |
| Unknown/nonstandard slots | `3, 35, 38, 43` |
| Pickup records | `20` |

## Ordinary pickup records

| # | Decoded identity | ROM base | RDRAM base | X | Y | Z | +0C | +10 type | +14 parameter | +18 callback | +1C | +20 | +24 slot | +28 presentation | +2C collected | Token | Requires |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | Earth Square | `0x000E1284` | — | `0x000D7E26` | `0x00003200` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00000000` | `0x802F52B0` | `0x0000000E` | `0x00000010` | `0` | `0x800B1D18` | `0x00000000` | `earth-square` | — |
| 2 | Earth Four Square | `0x000E12B4` | — | `0x001ED900` | `0x000BAA00` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00000001` | `0x802F52B0` | `0x00000012` | `0x0000000C` | `1` | `0x800B1D18` | `0x00000000` | `earth-four-square` | earth-square |
| 3 | Earth Triangle | `0x000E12E4` | — | `0xFFFBF558` | `0xFFFA3200` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00000002` | `0x802F52B0` | `0x00000010` | `0x0000000F` | `2` | `0x800B1D18` | `0x00000000` | `earth-triangle` | earth-four-square |
| 4 | Formula | `0x000E1314` | — | `0xFFDFF300` | `0x00003200` | `0x00000000` | `0x00000006` | `0x00000009` | `0x00000000` | `0x8003898C` | `0x00000020` | `0x00000020` | `20` | `0x800B1D38` | `0x00000000` | — | — |
| 5 | Extra-life urn | `0x000E1344` | — | `0xFFE08000` | `0x00001100` | `0x00000000` | `0x00000006` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `13` | `0x800B1D38` | `0x00000000` | — | — |
| 6 | Herbs | `0x000E1374` | — | `0xFFE10000` | `0x00003200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `14` | `0x800B1D38` | `0x00000000` | — | — |
| 7 | Extra-life urn | `0x000E13A4` | — | `0x0012BC00` | `0x00003200` | `0x00000000` | `0x00000006` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `13` | `0x800B1D38` | `0x00000000` | — | — |
| 8 | Mana pickup | `0x000E13D4` | — | `0x000E1200` | `0x000F3200` | `0x00000000` | `0x00000006` | `0x00000003` | `0x00000000` | `0x80038A58` | `0x00000020` | `0x00000020` | `15` | `0x800B1C14` | `0x00000000` | — | earth-square |
| 9 | Mana pickup | `0x000E1404` | — | `0x00150300` | `0x000F3200` | `0x00000000` | `0x00000006` | `0x00000003` | `0x00000000` | `0x80038A58` | `0x00000020` | `0x00000020` | `15` | `0x800B1C14` | `0x00000000` | — | earth-square |
| 10 | Extra-life urn | `0x000E1434` | — | `0x000D8000` | `0x000F0700` | `0x00000000` | `0x00000006` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `13` | `0x800B1D38` | `0x00000000` | — | earth-square |
| 11 | Herbs | `0x000E1464` | — | `0xFFE2FC00` | `0x00003200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `14` | `0x800B1D38` | `0x00000000` | — | earth-square |
| 12 | Herbs | `0x000E1494` | — | `0xFFE40E00` | `0x00003200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `14` | `0x800B1D38` | `0x00000000` | — | earth-square |
| 13 | Herbs | `0x000E14C4` | — | `0xFFF80500` | `0xFFFBB200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `14` | `0x800B1D38` | `0x00000000` | — | earth-four-square |
| 14 | Extra-life urn | `0x000E14F4` | — | `0xFFDCC100` | `0x00003200` | `0x00000000` | `0x00000006` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `13` | `0x800B1D38` | `0x00000000` | — | earth-four-square |
| 15 | Herbs | `0x000E1524` | — | `0x0012DF00` | `0xFFFA3200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `14` | `0x800B1D38` | `0x00000000` | — | earth-four-square |
| 16 | Herbs | `0x000E1554` | — | `0x00134300` | `0xFFFA3200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `14` | `0x800B1D38` | `0x00000000` | — | earth-four-square |
| 17 | Herbs | `0x000E1584` | — | `0x0013A700` | `0xFFFA3200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `14` | `0x800B1D38` | `0x00000000` | — | earth-four-square |
| 18 | Extra-life urn | `0x000E15B4` | — | `0x00140B00` | `0xFFFA3200` | `0x00000000` | `0x00000006` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `13` | `0x800B1D38` | `0x00000000` | — | earth-four-square |
| 19 | Eye | `0x000E15E4` | — | `0x00019070` | `0xFFFA3200` | `0x00000000` | `0x00000006` | `0x0000000A` | `0x00000000` | `0x8003895C` | `0x00000020` | `0x00000020` | `18` | `0x800B1D38` | `0x00000000` | — | earth-four-square |
| 20 | Shield | `0x000E1614` | — | `0x00049CF7` | `0xFFF2B200` | `0x00000000` | `0x00000006` | `0x00000007` | `0x00000000` | `0x8003892C` | `0x00000020` | `0x00000020` | `19` | `0x800B1D38` | `0x00000000` | — | earth-four-square |

## Pickup-to-resource usage

| ROM base | Callback | Parameter | Slot | Presentation |
|---:|---:|---:|---:|---:|
| `0x000E1284` | `0x802F52B0` | `0x00000000` | 0 | `0x800B1D18` |
| `0x000E12B4` | `0x802F52B0` | `0x00000001` | 1 | `0x800B1D18` |
| `0x000E12E4` | `0x802F52B0` | `0x00000002` | 2 | `0x800B1D18` |
| `0x000E1314` | `0x8003898C` | `0x00000000` | 20 | `0x800B1D38` |
| `0x000E1344` | `0x80038A1C` | `0x00000000` | 13 | `0x800B1D38` |
| `0x000E1374` | `0x800389BC` | `0x00000000` | 14 | `0x800B1D38` |
| `0x000E13A4` | `0x80038A1C` | `0x00000000` | 13 | `0x800B1D38` |
| `0x000E13D4` | `0x80038A58` | `0x00000000` | 15 | `0x800B1C14` |
| `0x000E1404` | `0x80038A58` | `0x00000000` | 15 | `0x800B1C14` |
| `0x000E1434` | `0x80038A1C` | `0x00000000` | 13 | `0x800B1D38` |
| `0x000E1464` | `0x800389BC` | `0x00000000` | 14 | `0x800B1D38` |
| `0x000E1494` | `0x800389BC` | `0x00000000` | 14 | `0x800B1D38` |
| `0x000E14C4` | `0x800389BC` | `0x00000000` | 14 | `0x800B1D38` |
| `0x000E14F4` | `0x80038A1C` | `0x00000000` | 13 | `0x800B1D38` |
| `0x000E1524` | `0x800389BC` | `0x00000000` | 14 | `0x800B1D38` |
| `0x000E1554` | `0x800389BC` | `0x00000000` | 14 | `0x800B1D38` |
| `0x000E1584` | `0x800389BC` | `0x00000000` | 14 | `0x800B1D38` |
| `0x000E15B4` | `0x80038A1C` | `0x00000000` | 13 | `0x800B1D38` |
| `0x000E15E4` | `0x8003895C` | `0x00000000` | 18 | `0x800B1D38` |
| `0x000E1614` | `0x8003892C` | `0x00000000` | 19 | `0x800B1D38` |

## Outer resource slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Earth icon, square | `0x104` | embedded-data-bundle | 12 | 1 |
| 1 | Earth icon, four squares | `0x184` | embedded-data-bundle | 9 | 1 |
| 2 | Earth icon, triangle | `0x1B0` | embedded-data-bundle | 9 | 1 |
| 3 | Unknown resource | `0x1DC` | unknown/nonstandard | — | 0 |
| 4 | Animated resource bundle | `0x1F0` | zero-terminated-record-list | 3 | 0 |
| 5 | Animated resource bundle | `0x200` | zero-terminated-record-list | 4 | 0 |
| 6 | Animated resource bundle | `0x200` | zero-terminated-record-list | 4 | 0 |
| 7 | Animated resource bundle | `0x200` | zero-terminated-record-list | 4 | 0 |
| 8 | Animated resource bundle | `0x214` | zero-terminated-record-list | 3 | 0 |
| 9 | Animated resource bundle | `0x214` | zero-terminated-record-list | 3 | 0 |
| 10 | Animated resource bundle | `0x214` | zero-terminated-record-list | 3 | 0 |
| 11 | Animated resource bundle | `0x214` | zero-terminated-record-list | 3 | 0 |
| 12 | Animated resource bundle | `0x26C` | zero-terminated-record-list | 3 | 0 |
| 13 | Extra-life urn | `0x4A4` | embedded-data-bundle | 7 | 5 |
| 14 | Herbs | `0x214` | zero-terminated-record-list | 3 | 7 |
| 15 | Mana urn (Lua substitutes Herbs) | `0x23C` | zero-terminated-record-list | 4 | 2 |
| 16 | Animated resource bundle | `0x26C` | zero-terminated-record-list | 3 | 0 |
| 17 | Animated resource bundle | `0x2A4` | embedded-data-bundle-mode0-selector | 6 | 0 |
| 18 | Eye | `0x27C` | zero-terminated-record-list | 7 | 1 |
| 19 | Shield | `0x2D8` | zero-terminated-record-list | 5 | 1 |
| 20 | Formula | `0x2D8` | zero-terminated-record-list | 5 | 1 |
| 21 | Animated resource bundle | `0x2D8` | zero-terminated-record-list | 5 | 0 |
| 22 | Animated resource bundle | `0x308` | zero-terminated-record-list | 3 | 0 |
| 23 | Animated resource bundle | `0x318` | zero-terminated-record-list | 4 | 0 |
| 24 | Animated resource bundle | `0x318` | zero-terminated-record-list | 4 | 0 |
| 25 | Animated resource bundle | `0x318` | zero-terminated-record-list | 4 | 0 |
| 26 | Animated resource bundle | `0x318` | zero-terminated-record-list | 4 | 0 |
| 27 | Animated resource bundle | `0x318` | zero-terminated-record-list | 4 | 0 |
| 28 | Animated resource bundle | `0x318` | zero-terminated-record-list | 4 | 0 |
| 29 | Animated resource bundle | `0x32C` | zero-terminated-record-list | 4 | 0 |
| 30 | Animated resource bundle | `0x3D8` | zero-terminated-record-list | 7 | 0 |
| 31 | Animated resource bundle | `0x41C` | embedded-data-bundle-mode0-selector | 7 | 0 |
| 32 | Animated resource bundle | `0x340` | embedded-data-bundle-mode0-selector | 6 | 0 |
| 33 | Animated resource bundle | `0x400` | zero-terminated-record-list | 6 | 0 |
| 34 | Animated resource bundle | `0x444` | zero-terminated-record-list | 7 | 0 |
| 35 | Unknown resource | `0x464` | unknown/nonstandard | — | 0 |
| 36 | Animated resource bundle | `0x4A4` | embedded-data-bundle | 7 | 0 |
| 37 | Animated resource bundle | `0x37C` | embedded-data-bundle-mode0-selector | 7 | 0 |
| 38 | Unknown resource | `0x464` | unknown/nonstandard | — | 0 |
| 39 | Animated resource bundle | `0x104` | embedded-data-bundle | 12 | 0 |
| 40 | Animated resource bundle | `0x184` | embedded-data-bundle | 9 | 0 |
| 41 | Unused logical slot | `0` | empty | — | 0 |
| 42 | Animated resource bundle | `0x3D8` | zero-terminated-record-list | 7 | 0 |
| 43 | Unknown resource | `0x13C` | unknown/nonstandard | — | 0 |
| 44 | Unused logical slot | `0` | empty | — | 0 |
| 45 | Unused logical slot | `0` | empty | — | 0 |
| 46 | Unused logical slot | `0` | empty | — | 0 |
| 47 | Unused logical slot | `0` | empty | — | 0 |
| 48 | Unused logical slot | `0` | empty | — | 0 |
| 49 | Unused logical slot | `0` | empty | — | 0 |
| 50 | Unused logical slot | `0` | empty | — | 0 |
| 51 | Unused logical slot | `0` | empty | — | 0 |
| 52 | Unused logical slot | `0` | empty | — | 0 |
| 53 | Unused logical slot | `0` | empty | — | 0 |
| 54 | Unused logical slot | `0` | empty | — | 0 |
| 55 | Unused logical slot | `0` | empty | — | 0 |
| 56 | Unused logical slot | `0` | empty | — | 0 |
| 57 | Unused logical slot | `0` | empty | — | 0 |
| 58 | Unused logical slot | `0` | empty | — | 0 |
| 59 | Unused logical slot | `0` | empty | — | 0 |
| 60 | Unused logical slot | `0` | empty | — | 0 |
| 61 | Unused logical slot | `0` | empty | — | 0 |
| 62 | Unused logical slot | `0` | empty | — | 0 |
| 63 | Unused logical slot | `0` | empty | — | 0 |
| 64 | Unused logical slot | `0` | empty | — | 0 |

## Recognized bundle records

| Slot | Frame | Record | Storage | Resource/data value | Inferred end | Dimensions words |
|---:|---:|---:|---|---:|---:|---|
| 0 | 0 | `0x1BC7C` | embedded-data | `0x1BC90` | `0x1BF64` | `0x0060006E` / `0x0028FFF8` |
| 0 | 1 | `0x1BF50` | embedded-data | `0x1BF64` | `0x1C23C` | `0x0060006E` / `0x0028FFF8` |
| 0 | 2 | `0x1C228` | embedded-data | `0x1C23C` | `0x1C50C` | `0x005C006E` / `0x0028FFF8` |
| 0 | 3 | `0x1C4F8` | embedded-data | `0x1C50C` | `0x1C7DC` | `0x005C006E` / `0x0028FFF8` |
| 0 | 4 | `0x1C7C8` | embedded-data | `0x1C7DC` | `0x1CAA8` | `0x005C006E` / `0x0028FFF8` |
| 0 | 5 | `0x1CA94` | embedded-data | `0x1CAA8` | `0x1CD74` | `0x0060006E` / `0x002CFFF8` |
| 0 | 6 | `0x1CD60` | embedded-data | `0x1CD74` | `0x1D038` | `0x005C006E` / `0x002CFFF8` |
| 0 | 7 | `0x1CA94` | embedded-data | `0x1CAA8` | `0x1CD74` | `0x0060006E` / `0x002CFFF8` |
| 0 | 8 | `0x1C7C8` | embedded-data | `0x1C7DC` | `0x1CAA8` | `0x005C006E` / `0x0028FFF8` |
| 0 | 9 | `0x1C4F8` | embedded-data | `0x1C50C` | `0x1C7DC` | `0x005C006E` / `0x0028FFF8` |
| 0 | 10 | `0x1C228` | embedded-data | `0x1C23C` | `0x1C50C` | `0x005C006E` / `0x0028FFF8` |
| 0 | 11 | `0x1BF50` | embedded-data | `0x1BF64` | `0x1C23C` | `0x0060006E` / `0x0028FFF8` |
| 1 | 0 | `0x2052C` | embedded-data | `0x20540` | `0x20808` | `0x0060006C` / `0x0028FFF8` |
| 1 | 1 | `0x207F4` | embedded-data | `0x20808` | `0x20ABC` | `0x0060006C` / `0x0028FFF8` |
| 1 | 2 | `0x20AA8` | embedded-data | `0x20ABC` | `0x20D24` | `0x0060006C` / `0x0028FFF8` |
| 1 | 3 | `0x20D10` | embedded-data | `0x20D24` | `0x20FA8` | `0x0060006A` / `0x0028FFF8` |
| 1 | 4 | `0x20F94` | embedded-data | `0x20FA8` | `0x2123C` | `0x005C006C` / `0x0028FFF8` |
| 1 | 5 | `0x21228` | embedded-data | `0x2123C` | `0x214B0` | `0x005C006C` / `0x0028FFF8` |
| 1 | 6 | `0x2149C` | embedded-data | `0x214B0` | `0x21748` | `0x005C006E` / `0x0028FFF8` |
| 1 | 7 | `0x21734` | embedded-data | `0x21748` | `0x219F8` | `0x0060006E` / `0x0028FFF8` |
| 1 | 8 | `0x219E4` | embedded-data | `0x219F8` | `0x21CC0` | `0x0060006E` / `0x0028FFF8` |
| 2 | 0 | `0x219E4` | embedded-data | `0x219F8` | `0x21CC0` | `0x0060006E` / `0x0028FFF8` |
| 2 | 1 | `0x21734` | embedded-data | `0x21748` | `0x219F8` | `0x0060006E` / `0x0028FFF8` |
| 2 | 2 | `0x2149C` | embedded-data | `0x214B0` | `0x21748` | `0x005C006E` / `0x0028FFF8` |
| 2 | 3 | `0x21228` | embedded-data | `0x2123C` | `0x214B0` | `0x005C006C` / `0x0028FFF8` |
| 2 | 4 | `0x20F94` | embedded-data | `0x20FA8` | `0x2123C` | `0x005C006C` / `0x0028FFF8` |
| 2 | 5 | `0x20D10` | embedded-data | `0x20D24` | `0x20FA8` | `0x0060006A` / `0x0028FFF8` |
| 2 | 6 | `0x20AA8` | embedded-data | `0x20ABC` | `0x20D24` | `0x0060006C` / `0x0028FFF8` |
| 2 | 7 | `0x207F4` | embedded-data | `0x20808` | `0x20ABC` | `0x0060006C` / `0x0028FFF8` |
| 2 | 8 | `0x2052C` | embedded-data | `0x20540` | `0x20808` | `0x0060006C` / `0x0028FFF8` |
| 4 | 0 | `0x11430` | embedded-data | `0x11444` | `0x116E4` | `0x006C0068` / `0x0030FFF2` |
| 4 | 1 | `0x116D0` | embedded-data | `0x116E4` | `0x1195C` | `0x006C0052` / `0x0030FFDC` |
| 4 | 2 | `0x11948` | embedded-data | `0x1195C` | `0x11B94` | `0x006C0044` / `0x0030FFCE` |
| 5 | 0 | `0x10BC8` | embedded-data | `0x10BDC` | `0x10E0C` | `0x006C004C` / `0x003CFFD6` |
| 5 | 1 | `0x10DF8` | embedded-data | `0x10E0C` | `0x11044` | `0x0068004C` / `0x0040FFD6` |
| 5 | 2 | `0x10BC8` | embedded-data | `0x10BDC` | `0x10E0C` | `0x006C004C` / `0x003CFFD6` |
| 5 | 3 | `0x109AC` | embedded-data | `0x109C0` | `0x10BDC` | `0x006C0048` / `0x0038FFD2` |
| 6 | 0 | `0x10BC8` | embedded-data | `0x10BDC` | `0x10E0C` | `0x006C004C` / `0x003CFFD6` |
| 6 | 1 | `0x10DF8` | embedded-data | `0x10E0C` | `0x11044` | `0x0068004C` / `0x0040FFD6` |
| 6 | 2 | `0x10BC8` | embedded-data | `0x10BDC` | `0x10E0C` | `0x006C004C` / `0x003CFFD6` |
| 6 | 3 | `0x109AC` | embedded-data | `0x109C0` | `0x10BDC` | `0x006C0048` / `0x0038FFD2` |
| 7 | 0 | `0x10BC8` | embedded-data | `0x10BDC` | `0x10E0C` | `0x006C004C` / `0x003CFFD6` |
| 7 | 1 | `0x10DF8` | embedded-data | `0x10E0C` | `0x11044` | `0x0068004C` / `0x0040FFD6` |
| 7 | 2 | `0x10BC8` | embedded-data | `0x10BDC` | `0x10E0C` | `0x006C004C` / `0x003CFFD6` |
| 7 | 3 | `0x109AC` | embedded-data | `0x109C0` | `0x10BDC` | `0x006C0048` / `0x0038FFD2` |
| 8 | 0 | `0x1326C` | embedded-data | `0x13280` | `0x13524` | `0x005C006E` / `0x0028FFF8` |
| 8 | 1 | `0x13510` | embedded-data | `0x13524` | `0x1375C` | `0x0030006E` / `0x0018FFF8` |
| 8 | 2 | `0x13748` | embedded-data | `0x1375C` | `0x139F8` | `0x0060006E` / `0x0024FFF8` |
| 9 | 0 | `0x1326C` | embedded-data | `0x13280` | `0x13524` | `0x005C006E` / `0x0028FFF8` |
| 9 | 1 | `0x13510` | embedded-data | `0x13524` | `0x1375C` | `0x0030006E` / `0x0018FFF8` |
| 9 | 2 | `0x13748` | embedded-data | `0x1375C` | `0x139F8` | `0x0060006E` / `0x0024FFF8` |
| 10 | 0 | `0x1326C` | embedded-data | `0x13280` | `0x13524` | `0x005C006E` / `0x0028FFF8` |
| 10 | 1 | `0x13510` | embedded-data | `0x13524` | `0x1375C` | `0x0030006E` / `0x0018FFF8` |
| 10 | 2 | `0x13748` | embedded-data | `0x1375C` | `0x139F8` | `0x0060006E` / `0x0024FFF8` |
| 11 | 0 | `0x1326C` | embedded-data | `0x13280` | `0x13524` | `0x005C006E` / `0x0028FFF8` |
| 11 | 1 | `0x13510` | embedded-data | `0x13524` | `0x1375C` | `0x0030006E` / `0x0018FFF8` |
| 11 | 2 | `0x13748` | embedded-data | `0x1375C` | `0x139F8` | `0x0060006E` / `0x0024FFF8` |
| 12 | 0 | `0xF788` | embedded-data | `0xF79C` | `0xFA70` | `0x003C0082` / `0x0018000C` |
| 12 | 1 | `0xFA5C` | embedded-data | `0xFA70` | `0xFD40` | `0x0030008C` / `0x00180016` |
| 12 | 2 | `0xFD2C` | embedded-data | `0xFD40` | `0x10010` | `0x0030008E` / `0x00180018` |
| 13 | 0 | `0x1BC7C` | embedded-data | `0x1BC90` | `0x1BF64` | `0x0060006E` / `0x0028FFF8` |
| 13 | 1 | `0x1BF50` | embedded-data | `0x1BF64` | `0x1C23C` | `0x0060006E` / `0x0028FFF8` |
| 13 | 2 | `0x1C228` | embedded-data | `0x1C23C` | `0x1C50C` | `0x005C006E` / `0x0028FFF8` |
| 13 | 3 | `0x1C4F8` | embedded-data | `0x1C50C` | `0x1C7DC` | `0x005C006E` / `0x0028FFF8` |
| 13 | 4 | `0x1C7C8` | embedded-data | `0x1C7DC` | `0x1CAA8` | `0x005C006E` / `0x0028FFF8` |
| 13 | 5 | `0x1CA94` | embedded-data | `0x1CAA8` | `0x1CD74` | `0x0060006E` / `0x002CFFF8` |
| 13 | 6 | `0x1CD60` | embedded-data | `0x1CD74` | `0x1D038` | `0x005C006E` / `0x002CFFF8` |
| 14 | 0 | `0x1326C` | embedded-data | `0x13280` | `0x13524` | `0x005C006E` / `0x0028FFF8` |
| 14 | 1 | `0x13510` | embedded-data | `0x13524` | `0x1375C` | `0x0030006E` / `0x0018FFF8` |
| 14 | 2 | `0x13748` | embedded-data | `0x1375C` | `0x139F8` | `0x0060006E` / `0x0024FFF8` |
| 15 | 0 | `0x179E0` | embedded-data | `0x179F4` | `0x17CD4` | `0x00500072` / `0x0020FFFC` |
| 15 | 1 | `0x17CC0` | embedded-data | `0x17CD4` | `0x17F4C` | `0x0038006E` / `0x0018FFF8` |
| 15 | 2 | `0x17F38` | embedded-data | `0x17F4C` | `0x18160` | `0x0034006A` / `0x0014FFF4` |
| 15 | 3 | `0x1814C` | embedded-data | `0x18160` | `0x183C8` | `0x00600066` / `0x002CFFF0` |
| 16 | 0 | `0xF788` | embedded-data | `0xF79C` | `0xFA70` | `0x003C0082` / `0x0018000C` |
| 16 | 1 | `0xFA5C` | embedded-data | `0xFA70` | `0xFD40` | `0x0030008C` / `0x00180016` |
| 16 | 2 | `0xFD2C` | embedded-data | `0xFD40` | `0x10010` | `0x0030008E` / `0x00180018` |
| 17 | 0 | `0x14C68` | embedded-data | `0x14C7C` | `0x14F28` | `0x002C0088` / `0x00140012` |
| 17 | 1 | `0x14F14` | embedded-data | `0x14F28` | `0x151D0` | `0x00280088` / `0x00080012` |
| 17 | 2 | `0x151BC` | embedded-data | `0x151D0` | `0x15478` | `0x00300082` / `0x0008000C` |
| 17 | 3 | `0x15464` | embedded-data | `0x15478` | `0x15734` | `0x003C0082` / `0x0008000C` |
| 17 | 4 | `0x15720` | embedded-data | `0x15734` | `0x159DC` | `0x004C0082` / `0x0008000C` |
| 17 | 5 | `0x159C8` | embedded-data | `0x159DC` | `0x15C98` | `0x00580082` / `0x0008000C` |
| 18 | 0 | `0x179E0` | embedded-data | `0x179F4` | `0x17CD4` | `0x00500072` / `0x0020FFFC` |
| 18 | 1 | `0x17CC0` | embedded-data | `0x17CD4` | `0x17F4C` | `0x0038006E` / `0x0018FFF8` |
| 18 | 2 | `0x17F38` | embedded-data | `0x17F4C` | `0x18160` | `0x0034006A` / `0x0014FFF4` |
| 18 | 3 | `0x183B4` | embedded-data | `0x183C8` | `0x185E8` | `0x002C0068` / `0x0018FFF2` |
| 18 | 4 | `0x185D4` | embedded-data | `0x185E8` | `0x18860` | `0x00500066` / `0x0018FFF0` |
| 18 | 5 | `0x1884C` | embedded-data | `0x18860` | `0x18B0C` | `0x00700060` / `0x0018FFEA` |
| 18 | 6 | `0x18AF8` | embedded-data | `0x18B0C` | `0x18D34` | `0x0034005E` / `0x0018FFE8` |
| 19 | 0 | `0x1E890` | embedded-data | `0x1E8A4` | `0x1EAE8` | `0x00540066` / `0x0020FFEE` |
| 19 | 1 | `0x1EAD4` | embedded-data | `0x1EAE8` | `0x1ED3C` | `0x00580060` / `0x0044FFE8` |
| 19 | 2 | `0x1ED28` | embedded-data | `0x1ED3C` | `0x1EF30` | `0x003C005C` / `0x0028FFE4` |
| 19 | 3 | `0x1EF1C` | embedded-data | `0x1EF30` | `0x1F150` | `0x0048005E` / `0x0018FFE4` |
| 19 | 4 | `0x1F13C` | embedded-data | `0x1F150` | `0x1F3EC` | `0x00780062` / `0x0018FFE8` |
| 20 | 0 | `0x1E890` | embedded-data | `0x1E8A4` | `0x1EAE8` | `0x00540066` / `0x0020FFEE` |
| 20 | 1 | `0x1EAD4` | embedded-data | `0x1EAE8` | `0x1ED3C` | `0x00580060` / `0x0044FFE8` |
| 20 | 2 | `0x1ED28` | embedded-data | `0x1ED3C` | `0x1EF30` | `0x003C005C` / `0x0028FFE4` |
| 20 | 3 | `0x1EF1C` | embedded-data | `0x1EF30` | `0x1F150` | `0x0048005E` / `0x0018FFE4` |
| 20 | 4 | `0x1F13C` | embedded-data | `0x1F150` | `0x1F3EC` | `0x00780062` / `0x0018FFE8` |
| 21 | 0 | `0x1E890` | embedded-data | `0x1E8A4` | `0x1EAE8` | `0x00540066` / `0x0020FFEE` |
| 21 | 1 | `0x1EAD4` | embedded-data | `0x1EAE8` | `0x1ED3C` | `0x00580060` / `0x0044FFE8` |
| 21 | 2 | `0x1ED28` | embedded-data | `0x1ED3C` | `0x1EF30` | `0x003C005C` / `0x0028FFE4` |
| 21 | 3 | `0x1EF1C` | embedded-data | `0x1EF30` | `0x1F150` | `0x0048005E` / `0x0018FFE4` |
| 21 | 4 | `0x1F13C` | embedded-data | `0x1F150` | `0x1F3EC` | `0x00780062` / `0x0018FFE8` |
| 22 | 0 | `0x15C84` | embedded-data | `0x15C98` | `0x15F30` | `0x005C0060` / `0x0028FFEA` |
| 22 | 1 | `0x15F1C` | embedded-data | `0x15F30` | `0x1623C` | `0x005C0082` / `0x00240012` |
| 22 | 2 | `0x16228` | embedded-data | `0x1623C` | `0x164F0` | `0x00580066` / `0x00240014` |
| 23 | 0 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 23 | 1 | `0x149C0` | embedded-data | `0x149D4` | `0x14C7C` | `0x0050007A` / `0x00280004` |
| 23 | 2 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 23 | 3 | `0x14424` | embedded-data | `0x14438` | `0x14710` | `0x0048007C` / `0x00200006` |
| 24 | 0 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 24 | 1 | `0x149C0` | embedded-data | `0x149D4` | `0x14C7C` | `0x0050007A` / `0x00280004` |
| 24 | 2 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 24 | 3 | `0x14424` | embedded-data | `0x14438` | `0x14710` | `0x0048007C` / `0x00200006` |
| 25 | 0 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 25 | 1 | `0x149C0` | embedded-data | `0x149D4` | `0x14C7C` | `0x0050007A` / `0x00280004` |
| 25 | 2 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 25 | 3 | `0x14424` | embedded-data | `0x14438` | `0x14710` | `0x0048007C` / `0x00200006` |
| 26 | 0 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 26 | 1 | `0x149C0` | embedded-data | `0x149D4` | `0x14C7C` | `0x0050007A` / `0x00280004` |
| 26 | 2 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 26 | 3 | `0x14424` | embedded-data | `0x14438` | `0x14710` | `0x0048007C` / `0x00200006` |
| 27 | 0 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 27 | 1 | `0x149C0` | embedded-data | `0x149D4` | `0x14C7C` | `0x0050007A` / `0x00280004` |
| 27 | 2 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 27 | 3 | `0x14424` | embedded-data | `0x14438` | `0x14710` | `0x0048007C` / `0x00200006` |
| 28 | 0 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 28 | 1 | `0x149C0` | embedded-data | `0x149D4` | `0x14C7C` | `0x0050007A` / `0x00280004` |
| 28 | 2 | `0x146FC` | embedded-data | `0x14710` | `0x149D4` | `0x004C007C` / `0x00240006` |
| 28 | 3 | `0x14424` | embedded-data | `0x14438` | `0x14710` | `0x0048007C` / `0x00200006` |
| 29 | 0 | `0x17530` | embedded-data | `0x17544` | `0x1779C` | `0x00440078` / `0x00240002` |
| 29 | 1 | `0x17788` | embedded-data | `0x1779C` | `0x179F4` | `0x00400076` / `0x00240000` |
| 29 | 2 | `0x17530` | embedded-data | `0x17544` | `0x1779C` | `0x00440078` / `0x00240002` |
| 29 | 3 | `0x17278` | embedded-data | `0x1728C` | `0x17544` | `0x004C007C` / `0x00240006` |
| 30 | 0 | `0x164DC` | embedded-data | `0x164F0` | `0x16760` | `0x0038007E` / `0x001C000A` |
| 30 | 1 | `0x1674C` | embedded-data | `0x16760` | `0x169AC` | `0x004C005A` / `0x001CFFFC` |
| 30 | 2 | `0x16998` | embedded-data | `0x169AC` | `0x16BA4` | `0x00540034` / `0x0020FFF2` |
| 30 | 3 | `0x16B90` | embedded-data | `0x16BA4` | `0x16D54` | `0x00500038` / `0x0024FFE4` |
| 30 | 4 | `0x16D40` | embedded-data | `0x16D54` | `0x16F24` | `0x0048004C` / `0x0024FFE4` |
| 30 | 5 | `0x16F10` | embedded-data | `0x16F24` | `0x170E0` | `0x0050004C` / `0x0030FFD4` |
| 30 | 6 | `0x170CC` | embedded-data | `0x170E0` | `0x1728C` | `0x00600032` / `0x0034FFBE` |
| 31 | 0 | `0x1D024` | embedded-data | `0x1D038` | `0x1D308` | `0x004C006E` / `0x0020FFFA` |
| 31 | 1 | `0x1D2F4` | embedded-data | `0x1D308` | `0x1D568` | `0x004C005E` / `0x0024FFF8` |
| 31 | 2 | `0x1D554` | embedded-data | `0x1D568` | `0x1D764` | `0x0058003C` / `0x0028FFEA` |
| 31 | 3 | `0x1D750` | embedded-data | `0x1D764` | `0x1D958` | `0x00580050` / `0x0028FFEE` |
| 31 | 4 | `0x1D944` | embedded-data | `0x1D958` | `0x1DB30` | `0x0054004A` / `0x0028FFDC` |
| 31 | 5 | `0x1DB1C` | embedded-data | `0x1DB30` | `0x1DC88` | `0x00540030` / `0x0028FFC0` |
| 31 | 6 | `0x1DC74` | embedded-data | `0x1DC88` | `0x1DE08` | `0x00540026` / `0x0024FFA8` |
| 32 | 0 | `0x1ACBC` | embedded-data | `0x1ACD0` | `0x1AF90` | `0x00500074` / `0x0028FFFE` |
| 32 | 1 | `0x1AF7C` | embedded-data | `0x1AF90` | `0x1B23C` | `0x005C006E` / `0x0030FFF8` |
| 32 | 2 | `0x1B228` | embedded-data | `0x1B23C` | `0x1B4DC` | `0x0064006C` / `0x0030FFF6` |
| 32 | 3 | `0x1B4C8` | embedded-data | `0x1B4DC` | `0x1B774` | `0x00640070` / `0x002CFFFA` |
| 32 | 4 | `0x1B760` | embedded-data | `0x1B774` | `0x1B9EC` | `0x005C006A` / `0x0028FFF4` |
| 32 | 5 | `0x1B9D8` | embedded-data | `0x1B9EC` | `0x1BC90` | `0x0058006A` / `0x0028FFF4` |
| 33 | 0 | `0x11D44` | embedded-data | `0x11D58` | `0x11F08` | `0x0054003C` / `0x0030FFC6` |
| 33 | 1 | `0x11EF4` | embedded-data | `0x11F08` | `0x12090` | `0x00380044` / `0x002CFFCC` |
| 33 | 2 | `0x1207C` | embedded-data | `0x12090` | `0x1223C` | `0x0050003A` / `0x002CFFCC` |
| 33 | 3 | `0x12228` | embedded-data | `0x1223C` | `0x12404` | `0x00400048` / `0x0030FFD0` |
| 33 | 4 | `0x123F0` | embedded-data | `0x12404` | `0x12630` | `0x0040005E` / `0x001CFFE6` |
| 33 | 5 | `0x1261C` | embedded-data | `0x12630` | `0x128FC` | `0x00380072` / `0x0014FFFC` |
| 34 | 0 | `0x1DC74` | embedded-data | `0x1DC88` | `0x1DE08` | `0x00540026` / `0x0024FFA8` |
| 34 | 1 | `0x1DDF4` | embedded-data | `0x1DE08` | `0x1DF70` | `0x0054002C` / `0x0024FFBA` |
| 34 | 2 | `0x1DF5C` | embedded-data | `0x1DF70` | `0x1E0E4` | `0x00540038` / `0x0024FFCA` |
| 34 | 3 | `0x1E0D0` | embedded-data | `0x1E0E4` | `0x1E2CC` | `0x00500054` / `0x0024FFEA` |
| 34 | 4 | `0x1E2B8` | embedded-data | `0x1E2CC` | `0x1E444` | `0x005C002E` / `0x002CFFC8` |
| 34 | 5 | `0x1E430` | embedded-data | `0x1E444` | `0x1E650` | `0x00480044` / `0x0020FFD0` |
| 34 | 6 | `0x1E63C` | embedded-data | `0x1E650` | `0x1E8A4` | `0x00340064` / `0x001CFFF2` |
| 36 | 0 | `0x1BC7C` | embedded-data | `0x1BC90` | `0x1BF64` | `0x0060006E` / `0x0028FFF8` |
| 36 | 1 | `0x1BF50` | embedded-data | `0x1BF64` | `0x1C23C` | `0x0060006E` / `0x0028FFF8` |
| 36 | 2 | `0x1C228` | embedded-data | `0x1C23C` | `0x1C50C` | `0x005C006E` / `0x0028FFF8` |
| 36 | 3 | `0x1C4F8` | embedded-data | `0x1C50C` | `0x1C7DC` | `0x005C006E` / `0x0028FFF8` |
| 36 | 4 | `0x1C7C8` | embedded-data | `0x1C7DC` | `0x1CAA8` | `0x005C006E` / `0x0028FFF8` |
| 36 | 5 | `0x1CA94` | embedded-data | `0x1CAA8` | `0x1CD74` | `0x0060006E` / `0x002CFFF8` |
| 36 | 6 | `0x1CD60` | embedded-data | `0x1CD74` | `0x1D038` | `0x005C006E` / `0x002CFFF8` |
| 37 | 0 | `0x1BC7C` | embedded-data | `0x1BC90` | `0x1BF64` | `0x0060006E` / `0x0028FFF8` |
| 37 | 1 | `0x1BF50` | embedded-data | `0x1BF64` | `0x1C23C` | `0x0060006E` / `0x0028FFF8` |
| 37 | 2 | `0x1C228` | embedded-data | `0x1C23C` | `0x1C50C` | `0x005C006E` / `0x0028FFF8` |
| 37 | 3 | `0x1C4F8` | embedded-data | `0x1C50C` | `0x1C7DC` | `0x005C006E` / `0x0028FFF8` |
| 37 | 4 | `0x1C7C8` | embedded-data | `0x1C7DC` | `0x1CAA8` | `0x005C006E` / `0x0028FFF8` |
| 37 | 5 | `0x1CA94` | embedded-data | `0x1CAA8` | `0x1CD74` | `0x0060006E` / `0x002CFFF8` |
| 37 | 6 | `0x1CD60` | embedded-data | `0x1CD74` | `0x1D038` | `0x005C006E` / `0x002CFFF8` |
| 39 | 0 | `0x1BC7C` | embedded-data | `0x1BC90` | `0x1BF64` | `0x0060006E` / `0x0028FFF8` |
| 39 | 1 | `0x1BF50` | embedded-data | `0x1BF64` | `0x1C23C` | `0x0060006E` / `0x0028FFF8` |
| 39 | 2 | `0x1C228` | embedded-data | `0x1C23C` | `0x1C50C` | `0x005C006E` / `0x0028FFF8` |
| 39 | 3 | `0x1C4F8` | embedded-data | `0x1C50C` | `0x1C7DC` | `0x005C006E` / `0x0028FFF8` |
| 39 | 4 | `0x1C7C8` | embedded-data | `0x1C7DC` | `0x1CAA8` | `0x005C006E` / `0x0028FFF8` |
| 39 | 5 | `0x1CA94` | embedded-data | `0x1CAA8` | `0x1CD74` | `0x0060006E` / `0x002CFFF8` |
| 39 | 6 | `0x1CD60` | embedded-data | `0x1CD74` | `0x1D038` | `0x005C006E` / `0x002CFFF8` |
| 39 | 7 | `0x1CA94` | embedded-data | `0x1CAA8` | `0x1CD74` | `0x0060006E` / `0x002CFFF8` |
| 39 | 8 | `0x1C7C8` | embedded-data | `0x1C7DC` | `0x1CAA8` | `0x005C006E` / `0x0028FFF8` |
| 39 | 9 | `0x1C4F8` | embedded-data | `0x1C50C` | `0x1C7DC` | `0x005C006E` / `0x0028FFF8` |
| 39 | 10 | `0x1C228` | embedded-data | `0x1C23C` | `0x1C50C` | `0x005C006E` / `0x0028FFF8` |
| 39 | 11 | `0x1BF50` | embedded-data | `0x1BF64` | `0x1C23C` | `0x0060006E` / `0x0028FFF8` |
| 40 | 0 | `0x2052C` | embedded-data | `0x20540` | `0x20808` | `0x0060006C` / `0x0028FFF8` |
| 40 | 1 | `0x207F4` | embedded-data | `0x20808` | `0x20ABC` | `0x0060006C` / `0x0028FFF8` |
| 40 | 2 | `0x20AA8` | embedded-data | `0x20ABC` | `0x20D24` | `0x0060006C` / `0x0028FFF8` |
| 40 | 3 | `0x20D10` | embedded-data | `0x20D24` | `0x20FA8` | `0x0060006A` / `0x0028FFF8` |
| 40 | 4 | `0x20F94` | embedded-data | `0x20FA8` | `0x2123C` | `0x005C006C` / `0x0028FFF8` |
| 40 | 5 | `0x21228` | embedded-data | `0x2123C` | `0x214B0` | `0x005C006C` / `0x0028FFF8` |
| 40 | 6 | `0x2149C` | embedded-data | `0x214B0` | `0x21748` | `0x005C006E` / `0x0028FFF8` |
| 40 | 7 | `0x21734` | embedded-data | `0x21748` | `0x219F8` | `0x0060006E` / `0x0028FFF8` |
| 40 | 8 | `0x219E4` | embedded-data | `0x219F8` | `0x21CC0` | `0x0060006E` / `0x0028FFF8` |
| 42 | 0 | `0x164DC` | embedded-data | `0x164F0` | `0x16760` | `0x0038007E` / `0x001C000A` |
| 42 | 1 | `0x1674C` | embedded-data | `0x16760` | `0x169AC` | `0x004C005A` / `0x001CFFFC` |
| 42 | 2 | `0x16998` | embedded-data | `0x169AC` | `0x16BA4` | `0x00540034` / `0x0020FFF2` |
| 42 | 3 | `0x16B90` | embedded-data | `0x16BA4` | `0x16D54` | `0x00500038` / `0x0024FFE4` |
| 42 | 4 | `0x16D40` | embedded-data | `0x16D54` | `0x16F24` | `0x0048004C` / `0x0024FFE4` |
| 42 | 5 | `0x16F10` | embedded-data | `0x16F24` | `0x170E0` | `0x0050004C` / `0x0030FFD4` |
| 42 | 6 | `0x170CC` | embedded-data | `0x170E0` | `0x1728C` | `0x00600032` / `0x0034FFBE` |

## Earth-specific notes, constraints, and pending questions

- The complete `0x225B0`-byte ROM resource file matches RDRAM at `0x802434B8` byte-for-byte in live Earth gameplay.
- All 20 standard `0x30`-byte pickup records are contiguous and mapped, including the three Earth icons and six ordinary item/resource slots.
- The supplied Lua comments identify the two slot-`15` pickups as mana and substitute Herbs in the virtual item pool; the native callback `0x80038A58` and presentation pointer `0x800B1C14` remain distinct from Herbs.
- Earth progression metadata remains stage-local: Earth Four Square requires `earth-square`; Earth Triangle requires `earth-four-square`; later location requirements are preserved row-by-row in the ordinary-pickup table.
- Many outer slots intentionally alias the same descriptor. Pickup-user absence and descriptor aliasing do not make an occupied selector safe to repurpose.
- Slots `3, 35, 38, 43` remain `unknown/nonstandard`; no gameplay owner or stronger structure meaning is inferred here.
- Empty stock selectors `41, 44..64` are logical selector capacity only. Per the shared schema, they are not evidence of free physical file bytes or production-safe allocation space.
- No Earth-specific cross-stage resource-import proof is promoted by this catalog; materialization feasibility in another destination must remain bounded to the proof and destination actually tested.

## Related owners

- [Stage catalogs](Stage-Catalogs) — shared schema, notation, safety rules, and eight-stage index.
- [Data structures and encodings](Data-Structures-and-Encodings) — ordinary `0x30`-byte record grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file-table, loader, overlay, and selector/resource grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and lifecycle.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded patch sites.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior and modeled Earth dependencies.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — generalized cross-stage materializer/solver rules, not Earth-local resource claims.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and stage-transition lifecycle.
