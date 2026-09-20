# Temple stage catalog

**Evidence status:** Static-confirmed from the clean USA N64 ROM; file-to-RDRAM mappings were also matched against captured runtime memory. Ordinary-pickup behavior and persistence are runtime-confirmed at representative locations, but the complete 84-record set has not been collected exhaustively one record at a time.

This page is the self-contained decoded catalog for native stage ID `0`. It includes every ordinary pickup record and every recognized resource slot/record. Values are big-endian. Unknown fields remain named by offset instead of being assigned unsupported semantics.

## Ordinary pickup records

A record is `0x30` bytes. Position and metadata (`+0x00..+0x0F`) and the collected flag (`+0x2C`) belong to the destination. The production randomizer moves the seven-word identity slice `+0x10..+0x2B`. `Token` and `Requires` are production logic metadata, not bytes stored in the native record.

| # | Decoded identity | ROM base | RDRAM base | X | Y | Z | +0C | +10 type | +14 parameter | +18 callback | +1C | +20 | +24 slot | +28 presentation | +2C collected | Token | Requires |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | Herbs | `0x000CEF6C` | — | `0xFFF1A560` | `0x00003200` | `0x00000000` | `0x00000002` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `15` | `0x800B1D38` | `0x00000000` | — | — |
| 2 | Herbs | `0x000CEF9C` | — | `0x00000000` | `0x00003200` | `0x00000000` | `0x00000002` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `15` | `0x800B1D38` | `0x00000000` | — | — |
| 3 | Herbs | `0x000CEFCC` | — | `0x0009FD11` | `0x0007B500` | `0x00000000` | `0x00000002` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `15` | `0x800B1D38` | `0x00000000` | — | — |
| 4 | Herbs | `0x000CEFFC` | — | `0xFFF27EAF` | `0x0007B500` | `0x00000000` | `0x00000002` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `15` | `0x800B1D38` | `0x00000000` | — | — |

## Resource-file catalog

Generated conservatively from the clean USA N64 ROM. Recognized bundles distinguish embedded model/data offsets from records that reference external resource IDs; `unknown/nonstandard` is intentionally not guessed.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `0` |
| File-table entry ROM | `0x000A5490` |
| Resource ROM range | `0x00513710..0x0052336F` |
| File size | `0xFC60` (64608 bytes) |
| File-table flag | `0` |
| Verified runtime base | `0x80226E28` |
| Outer slots | `17` |
| Outer-table end | `0x44` |
| First descriptor | `0x44` |
| Empty logical slots | `1, 2, 11, 12, 13` |
| Unknown/nonstandard slots | `none` |
| Pickup records | `4` |

## Outer slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Non-pickup/unknown resource | `0xD1C4` | embedded-data-bundle | 12 | 0 |
| 1 | Unused logical slot | `0` | empty | — | 0 |
| 2 | Unused logical slot | `0` | empty | — | 0 |
| 3 | Non-pickup/unknown resource | `0x44` | zero-terminated-record-list | 13 | 0 |
| 4 | Non-pickup/unknown resource | `0x7C` | zero-terminated-record-list | 15 | 0 |
| 5 | Non-pickup/unknown resource | `0xBC` | zero-terminated-record-list | 13 | 0 |
| 6 | Non-pickup/unknown resource | `0xCE74` | single-record-pointer | 1 | 0 |
| 7 | Non-pickup/unknown resource | `0x74BC` | zero-terminated-record-list | 5 | 0 |
| 8 | Non-pickup/unknown resource | `0x8C7C` | embedded-data-bundle-loop-selector | 18 | 0 |
| 9 | Non-pickup/unknown resource | `0x8CD0` | zero-terminated-record-list | 5 | 0 |
| 10 | Non-pickup/unknown resource | `0xADF4` | zero-terminated-record-list | 6 | 0 |
| 11 | Unused logical slot | `0` | empty | — | 0 |
| 12 | Unused logical slot | `0` | empty | — | 0 |
| 13 | Unused logical slot | `0` | empty | — | 0 |
| 14 | Non-pickup/unknown resource | `0xDF38` | embedded-data-bundle | 8 | 0 |
| 15 | Herbs | `0xF130` | embedded-data-bundle | 8 | 4 |
| 16 | Non-pickup/unknown resource | `0xCD60` | external-resource-id-bundle | 10 | 0 |

## Pickup usage

| ROM base | Callback | Parameter | Slot | Presentation |
|---:|---:|---:|---:|---:|
| `0x000CEF6C` | `0x800389BC` | `0x00000000` | 15 | `0x800B1D38` |
| `0x000CEF9C` | `0x800389BC` | `0x00000000` | 15 | `0x800B1D38` |
| `0x000CEFCC` | `0x800389BC` | `0x00000000` | 15 | `0x800B1D38` |
| `0x000CEFFC` | `0x800389BC` | `0x00000000` | 15 | `0x800B1D38` |

## Stage-specific notes

- The four standard 0x30-byte pickup records are all Herbs and all use slot 15.
- The stage Map is tracked at runtime collected flag 0x8026E9A4 by the supplied Lua script, but it is not one of these standard pickup records. Its scripted/special actor path remains separate and is not assigned to a resource slot here.

## Recognized bundle records

Offsets below are relative to the stage resource-file base.

| Slot | Frame | Record | Storage | Resource/data value | Inferred end | Dimensions words |
|---:|---:|---:|---|---:|---:|---|
| 0 | 0 | `0xD1FC` | embedded-data | `0xD310` | `0xD4A0` | `0x001C0021` / `0x00100010` |
| 0 | 1 | `0xD210` | embedded-data | `0xD4A0` | `0xD604` | `0x00180022` / `0x000D0010` |
| 0 | 2 | `0xD224` | embedded-data | `0xD604` | `0xD720` | `0x00100022` / `0x00070010` |
| 0 | 3 | `0xD238` | embedded-data | `0xD720` | `0xD79C` | `0x00060022` / `0x00020010` |
| 0 | 4 | `0xD24C` | embedded-data | `0xD79C` | `0xD864` | `0x00100021` / `0x00070010` |
| 0 | 5 | `0xD260` | embedded-data | `0xD864` | `0xD978` | `0x001C0021` / `0x000E0010` |
| 0 | 6 | `0xD274` | embedded-data | `0xD978` | `0xDA94` | `0x001A0021` / `0x000D0010` |
| 0 | 7 | `0xD288` | embedded-data | `0xDA94` | `0xDB7C` | `0x00140022` / `0x000B0010` |
| 0 | 8 | `0xD29C` | embedded-data | `0xDB7C` | `0xDC58` | `0x00100022` / `0x00090010` |
| 0 | 9 | `0xD2B0` | embedded-data | `0xDC58` | `0xDCD0` | `0x00060022` / `0x00020010` |
| 0 | 10 | `0xD2C4` | embedded-data | `0xDCD0` | `0xDDD4` | `0x00100022` / `0x00090010` |
| 0 | 11 | `0xD2D8` | embedded-data | `0xDDD4` | `0xE000` | `0x00180022` / `0x000D0010` |
| 3 | 0 | `0xF4` | embedded-data | `0x428` | `0x750` | `0x00280024` / `0x00160016` |
| 3 | 1 | `0x108` | embedded-data | `0x750` | `0xAD8` | `0x002B0025` / `0x00180017` |
| 3 | 2 | `0x11C` | embedded-data | `0xAD8` | `0xEDC` | `0x002E0028` / `0x001A0019` |
| 3 | 3 | `0x130` | embedded-data | `0xEDC` | `0x1388` | `0x002F002E` / `0x001B001A` |
| 3 | 4 | `0x144` | embedded-data | `0x1388` | `0x1860` | `0x00320031` / `0x001C001B` |
| 3 | 5 | `0x158` | embedded-data | `0x1860` | `0x1D74` | `0x00330035` / `0x001D001D` |
| 3 | 6 | `0x16C` | embedded-data | `0x1D74` | `0x226C` | `0x00330036` / `0x001D001E` |
| 3 | 7 | `0x180` | embedded-data | `0x226C` | `0x2724` | `0x00340038` / `0x001E0020` |
| 3 | 8 | `0x194` | embedded-data | `0x2724` | `0x2BA4` | `0x00370039` / `0x00210021` |
| 3 | 9 | `0x1A8` | embedded-data | `0x2BA4` | `0x2FB4` | `0x00390039` / `0x00220022` |
| 3 | 10 | `0x1BC` | embedded-data | `0x2FB4` | `0x3340` | `0x003A0039` / `0x00230023` |
| 3 | 11 | `0x1D0` | embedded-data | `0x3340` | `0x3630` | `0x003A003A` / `0x00230025` |
| 3 | 12 | `0x1E4` | embedded-data | `0x3630` | `0x383C` | `0x00380039` / `0x00220026` |
| 4 | 0 | `0x1F8` | embedded-data | `0x383C` | `0x39C8` | `0x001B0018` / `0x0011000D` |
| 4 | 1 | `0x20C` | embedded-data | `0x39C8` | `0x3BAC` | `0x001F001C` / `0x0014000C` |
| 4 | 2 | `0x220` | embedded-data | `0x3BAC` | `0x3DF0` | `0x00240020` / `0x0017000D` |
| 4 | 3 | `0x234` | embedded-data | `0x3DF0` | `0x407C` | `0x00290024` / `0x001B000E` |
| 4 | 4 | `0x248` | embedded-data | `0x407C` | `0x4348` | `0x002E0028` / `0x001E0010` |
| 4 | 5 | `0x25C` | embedded-data | `0x4348` | `0x4644` | `0x00310030` / `0x001F0013` |
| 4 | 6 | `0x270` | embedded-data | `0x4644` | `0x4924` | `0x00320034` / `0x001F0014` |
| 4 | 7 | `0x284` | embedded-data | `0x4924` | `0x4C1C` | `0x00310038` / `0x001E0016` |
| 4 | 8 | `0x298` | embedded-data | `0x4C1C` | `0x4F00` | `0x002F0038` / `0x001C0016` |
| 4 | 9 | `0x2AC` | embedded-data | `0x4F00` | `0x51C8` | `0x002E0037` / `0x001B0018` |
| 4 | 10 | `0x2C0` | embedded-data | `0x51C8` | `0x544C` | `0x002A003C` / `0x0019001B` |
| 4 | 11 | `0x2D4` | embedded-data | `0x544C` | `0x5694` | `0x0029003A` / `0x0018001E` |
| 4 | 12 | `0x2E8` | embedded-data | `0x5694` | `0x58E0` | `0x002B003F` / `0x00180023` |
| 4 | 13 | `0x2FC` | embedded-data | `0x58E0` | `0x5A94` | `0x002C0036` / `0x00170025` |
| 4 | 14 | `0x310` | embedded-data | `0x5A94` | `0x5BCC` | `0x002F0037` / `0x00170026` |
| 5 | 0 | `0x324` | embedded-data | `0x5BCC` | `0x5D10` | `0x00150018` / `0x0009000F` |
| 5 | 1 | `0x338` | embedded-data | `0x5D10` | `0x5EE8` | `0x001F001E` / `0x00110014` |
| 5 | 2 | `0x34C` | embedded-data | `0x5EE8` | `0x6118` | `0x00220022` / `0x00120017` |
| 5 | 3 | `0x360` | embedded-data | `0x6118` | `0x63BC` | `0x00270028` / `0x0014001C` |
| 5 | 4 | `0x374` | embedded-data | `0x63BC` | `0x666C` | `0x002A0028` / `0x0015001D` |
| 5 | 5 | `0x388` | embedded-data | `0x666C` | `0x68F8` | `0x002D0027` / `0x0016001E` |
| 5 | 6 | `0x39C` | embedded-data | `0x68F8` | `0x6B78` | `0x00300027` / `0x0016001F` |
| 5 | 7 | `0x3B0` | embedded-data | `0x6B78` | `0x6DC0` | `0x002F0025` / `0x00160020` |
| 5 | 8 | `0x3C4` | embedded-data | `0x6DC0` | `0x6FE0` | `0x002C0026` / `0x00140023` |
| 5 | 9 | `0x3D8` | embedded-data | `0x6FE0` | `0x71A4` | `0x002D0024` / `0x00140024` |
| 5 | 10 | `0x3EC` | embedded-data | `0x71A4` | `0x7308` | `0x002B0023` / `0x00130026` |
| 5 | 11 | `0x400` | embedded-data | `0x7308` | `0x7408` | `0x0021001B` / `0x000E0022` |
| 5 | 12 | `0x414` | embedded-data | `0x7408` | `0x75BC` | `0x00200019` / `0x000D0024` |
| 6 | 0 | `0xCE78` | embedded-data | `0xCE8C` | `0xD310` | `0x00B60026` / `0x00000000` |
| 7 | 0 | `0x74D4` | embedded-data | `0x75BC` | `0x7A5C` | `0x00230049` / `0xFFF5FFD4` |
| 7 | 1 | `0x74E8` | embedded-data | `0x7A5C` | `0x7F34` | `0x00340041` / `0xFFF2FFCD` |
| 7 | 2 | `0x74FC` | embedded-data | `0x7F34` | `0x83BC` | `0x004C0033` / `0xFFF8FFC1` |
| 7 | 3 | `0x7510` | embedded-data | `0x83BC` | `0x8830` | `0x0064001E` / `0x0002FFA5` |
| 7 | 4 | `0x7524` | embedded-data | `0x8830` | `0x8E98` | `0x00640016` / `0x0001FF9D` |
| 8 | 0 | `0x8D38` | embedded-data | `0x9770` | `0x99AC` | `0x000E0042` / `0x0009000F` |
| 8 | 1 | `0x8D4C` | embedded-data | `0x99AC` | `0x9BD8` | `0x000E0040` / `0x0009000F` |
| 8 | 2 | `0x8D60` | embedded-data | `0x9BD8` | `0x9E04` | `0x000E003C` / `0x0009000F` |
| 8 | 3 | `0x8D74` | embedded-data | `0x9E04` | `0x9FFC` | `0x000F0036` / `0x0009000F` |
| 8 | 4 | `0x8D88` | embedded-data | `0x9FFC` | `0xA1DC` | `0x000F0031` / `0x0009000F` |
| 8 | 5 | `0x8D9C` | embedded-data | `0xA1DC` | `0xA3B8` | `0x0010002E` / `0x0009000F` |
| 8 | 6 | `0x8D88` | embedded-data | `0x9FFC` | `0xA1DC` | `0x000F0031` / `0x0009000F` |
| 8 | 7 | `0x8D74` | embedded-data | `0x9E04` | `0x9FFC` | `0x000F0036` / `0x0009000F` |
| 8 | 8 | `0x8D60` | embedded-data | `0x9BD8` | `0x9E04` | `0x000E003C` / `0x0009000F` |
| 8 | 9 | `0x8D4C` | embedded-data | `0x99AC` | `0x9BD8` | `0x000E0040` / `0x0009000F` |
| 8 | 10 | `0x8D38` | embedded-data | `0x9770` | `0x99AC` | `0x000E0042` / `0x0009000F` |
| 8 | 11 | `0x8D24` | embedded-data | `0x9530` | `0x9770` | `0x000E0043` / `0x0009000F` |
| 8 | 12 | `0x8D10` | embedded-data | `0x92FC` | `0x9530` | `0x000E0042` / `0x0009000F` |
| 8 | 13 | `0x8CFC` | embedded-data | `0x90C4` | `0x92FC` | `0x000F0041` / `0x0009000F` |
| 8 | 14 | `0x8CE8` | embedded-data | `0x8E98` | `0x90C4` | `0x00110040` / `0x0009000F` |
| 8 | 15 | `0x8CFC` | embedded-data | `0x90C4` | `0x92FC` | `0x000F0041` / `0x0009000F` |
| 8 | 16 | `0x8D10` | embedded-data | `0x92FC` | `0x9530` | `0x000E0042` / `0x0009000F` |
| 8 | 17 | `0x8D24` | embedded-data | `0x9530` | `0x9770` | `0x000E0043` / `0x0009000F` |
| 9 | 0 | `0x8DB0` | embedded-data | `0xA3B8` | `0xA600` | `0x000E0044` / `0x0009000F` |
| 9 | 1 | `0x8DC4` | embedded-data | `0xA600` | `0xA834` | `0x00180040` / `0x0008000F` |
| 9 | 2 | `0x8DD8` | embedded-data | `0xA834` | `0xAA34` | `0x0024002B` / `0x0008000F` |
| 9 | 3 | `0x8DEC` | embedded-data | `0xAA34` | `0xAC1C` | `0x001D001F` / `0x0008000F` |
| 9 | 4 | `0x8E00` | embedded-data | `0xAC1C` | `0xAE88` | `0x00410011` / `0x000F0009` |
| 10 | 0 | `0xAE10` | embedded-data | `0xAE88` | `0xB56C` | `0x0062001A` / `0x0031FF9F` |
| 10 | 1 | `0xAE24` | embedded-data | `0xB56C` | `0xBBE0` | `0x00610018` / `0x0030FF9E` |
| 10 | 2 | `0xAE38` | embedded-data | `0xBBE0` | `0xC19C` | `0x00630016` / `0x0031FF9D` |
| 10 | 3 | `0xAE4C` | embedded-data | `0xC19C` | `0xC72C` | `0x00620018` / `0x0030FF9C` |
| 10 | 4 | `0xAE60` | embedded-data | `0xC72C` | `0xCB1C` | `0x005F0015` / `0x002EFF9A` |
| 10 | 5 | `0xAE74` | embedded-data | `0xCB1C` | `0xCE8C` | `0x00600014` / `0x002FFF9A` |
| 14 | 0 | `0xDF60` | embedded-data | `0xE000` | `0xE220` | `0x00160017` / `0x000B000B` |
| 14 | 1 | `0xDF74` | embedded-data | `0xE220` | `0xE450` | `0x00160017` / `0x000B000B` |
| 14 | 2 | `0xDF88` | embedded-data | `0xE450` | `0xE674` | `0x00160017` / `0x000B000B` |
| 14 | 3 | `0xDF9C` | embedded-data | `0xE674` | `0xE89C` | `0x00160017` / `0x000B000B` |
| 14 | 4 | `0xDFB0` | embedded-data | `0xE89C` | `0xEAC0` | `0x00160017` / `0x000B000B` |
| 14 | 5 | `0xDFC4` | embedded-data | `0xEAC0` | `0xECE8` | `0x00160017` / `0x000B000B` |
| 14 | 6 | `0xDFD8` | embedded-data | `0xECE8` | `0xEF0C` | `0x00160017` / `0x000B000B` |
| 14 | 7 | `0xDFEC` | embedded-data | `0xEF0C` | `0xF1F8` | `0x00160017` / `0x000B000B` |
| 15 | 0 | `0xF158` | embedded-data | `0xF1F8` | `0xF324` | `0x00110017` / `0x0008000F` |
| 15 | 1 | `0xF16C` | embedded-data | `0xF324` | `0xF46C` | `0x00110017` / `0x0008000F` |
| 15 | 2 | `0xF180` | embedded-data | `0xF46C` | `0xF5D4` | `0x00100017` / `0x0007000F` |
| 15 | 3 | `0xF194` | embedded-data | `0xF5D4` | `0xF73C` | `0x00100017` / `0x0008000F` |
| 15 | 4 | `0xF1A8` | embedded-data | `0xF73C` | `0xF8B8` | `0x00110017` / `0x0008000F` |
| 15 | 5 | `0xF1BC` | embedded-data | `0xF8B8` | `0xFA04` | `0x00100017` / `0x0007000F` |
| 15 | 6 | `0xF1D0` | embedded-data | `0xFA04` | `0xFB48` | `0x00100017` / `0x0008000F` |
| 15 | 7 | `0xF1E4` | embedded-data | `0xFB48` | `0xFC60` | `0x00100017` / `0x0008000F` |
| 16 | 0 | `0xCD90` | external-resource-id | `0x25D` | `` | `0x00100017` / `0x0007000B` |
| 16 | 1 | `0xCDA4` | external-resource-id | `0x25E` | `` | `0x00100017` / `0x0007000B` |
| 16 | 2 | `0xCDB8` | external-resource-id | `0x25F` | `` | `0x000F0017` / `0x0006000B` |
| 16 | 3 | `0xCDCC` | external-resource-id | `0x260` | `` | `0x000E0017` / `0x0006000B` |
| 16 | 4 | `0xCDE0` | external-resource-id | `0x261` | `` | `0x000B0017` / `0x0005000B` |
| 16 | 5 | `0xCDF4` | external-resource-id | `0x262` | `` | `0x00070017` / `0x0003000B` |
| 16 | 6 | `0xCE08` | external-resource-id | `0x263` | `` | `0x00050018` / `0x0002000B` |
| 16 | 7 | `0xCE1C` | external-resource-id | `0x264` | `` | `0x000A0018` / `0x0005000B` |
| 16 | 8 | `0xCE30` | external-resource-id | `0x265` | `` | `0x000E0017` / `0x0006000B` |
| 16 | 9 | `0xCE44` | external-resource-id | `0x266` | `` | `0x000F0017` / `0x0007000B` |

## Safety interpretation

Zero outer entries are free logical selectors only. They do not imply unused physical bytes inside the original file. New payload data must be appended to an expanded/relocated file or placed in storage proven safe by a complete reference analysis. Inferred model/data ends use the next discovered model-data start and are boundaries for analysis, not yet proof that trailing bytes are independently movable.

## Interpretation boundaries

- A zero outer-table entry is a free logical selector, not proof of unused physical bytes.
- An occupied slot with no ordinary-pickup user can still be referenced by another actor or script and is protected until traced.
- Inferred data ends support cataloging; they do not prove that trailing ranges are independently movable.
- Foreign resources require bounded storage, loader/arena validation, guarded references, and runtime testing.

Catalog lineage: generated from the preserved clean-ROM catalog artifacts and checked against the production pickup definitions in `src/mkmszr/data/pickups.py`. The tables above are reproduced here so this Wiki does not depend on an external archive for current technical facts.
