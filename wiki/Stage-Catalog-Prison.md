# Prison stage catalog

**Evidence status:** Static-confirmed from the clean USA N64 ROM; file-to-RDRAM mappings were also matched against captured runtime memory. Ordinary-pickup behavior and persistence are runtime-confirmed at representative locations, but the complete 84-record set has not been collected exhaustively one record at a time.

This page is the self-contained decoded catalog for native stage ID `4`. It includes every ordinary pickup record and every recognized resource slot/record. Values are big-endian. Unknown fields remain named by offset instead of being assigned unsupported semantics.

## Ordinary pickup records

A record is `0x30` bytes. Position and metadata (`+0x00..+0x0F`) and the collected flag (`+0x2C`) belong to the destination. The production randomizer moves the seven-word identity slice `+0x10..+0x2B`. `Token` and `Requires` are production logic metadata, not bytes stored in the native record.

| # | Decoded identity | ROM base | RDRAM base | X | Y | Z | +0C | +10 type | +14 parameter | +18 callback | +1C | +20 | +24 slot | +28 presentation | +2C collected | Token | Requires |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | Prison L1 | `0x000CA030` | — | `0x00788000` | `0x00039F00` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00000000` | `0x80038770` | `0x00000012` | `0x00000014` | `0` | `0x800B1D18` | `0x00000000` | `prison-l1` | — |
| 2 | Prison L2 | `0x000CA060` | — | `0x00848000` | `0x0001CC00` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00000001` | `0x80038770` | `0x00000012` | `0x00000014` | `1` | `0x800B1D18` | `0x00000000` | `prison-l2` | prison-l1 |
| 3 | Prison L3 | `0x000CA090` | — | `0x008E8000` | `0x00000500` | `0x00000000` | `0x00000006` | `0x00000000` | `0x00008002` | `0x80038770` | `0x00000012` | `0x00000014` | `2` | `0x800B1D18` | `0x00000000` | `prison-l3` | prison-l1, prison-l2 |
| 4 | Strength urn | `0x000CA0C0` | — | `0x00730400` | `0xFFFE3200` | `0x00000000` | `0x00000006` | `0x00000005` | `0x00000000` | `0x80038A90` | `0x00000012` | `0x00000015` | `11` | `0x800B1D38` | `0x00000000` | — | prison-l1, prison-l2 |
| 5 | Herbs | `0x000CA0F0` | — | `0x000D0600` | `0x0000F200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `8` | `0x800B1D38` | `0x00000000` | — | — |
| 6 | Herbs | `0x000CA120` | — | `0x0023FA00` | `0x0000F200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `8` | `0x800B1D38` | `0x00000000` | — | — |
| 7 | Herbs | `0x000CA150` | — | `0x00396D00` | `0x0000F200` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `8` | `0x800B1D38` | `0x00000000` | — | — |
| 8 | Herbs | `0x000CA180` | — | `0x00658100` | `0x0004DF00` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `8` | `0x800B1D38` | `0x00000000` | — | — |
| 9 | Herbs | `0x000CA1B0` | — | `0x00680700` | `0x0001CC00` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `8` | `0x800B1D38` | `0x00000000` | — | prison-l1, prison-l2, prison-l3 |
| 10 | Herbs | `0x000CA1E0` | — | `0x007A8000` | `0x0001CC00` | `0x00000000` | `0x00000006` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `8` | `0x800B1D38` | `0x00000000` | — | prison-l1 |

## Resource-file catalog

Generated conservatively from the clean USA N64 ROM. Recognized bundles distinguish embedded model/data offsets from records that reference external resource IDs; `unknown/nonstandard` is intentionally not guessed.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `4` |
| File-table entry ROM | `0x000A537C` |
| Resource ROM range | `0x0041C680..0x00420F6F` |
| File size | `0x48F0` (18672 bytes) |
| File-table flag | `0` |
| Verified runtime base | `0x801FB798` |
| Outer slots | `12` |
| Outer-table end | `0x30` |
| First descriptor | `0x30` |
| Empty logical slots | `none` |
| Unknown/nonstandard slots | `none` |
| Pickup records | `10` |

## Outer slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Prison Level 1 key | `0x30` | embedded-data-bundle | 8 | 1 |
| 1 | Prison Level 2 key | `0x58` | embedded-data-bundle | 8 | 1 |
| 2 | Prison Level 3 key | `0x80` | embedded-data-bundle | 8 | 1 |
| 3 | Non-pickup/unknown resource | `0x483C` | zero-terminated-external-list | 7 | 0 |
| 4 | Non-pickup/unknown resource | `0xA8` | zero-terminated-record-list | 1 | 0 |
| 5 | Non-pickup/unknown resource | `0xB0` | zero-terminated-record-list | 1 | 0 |
| 6 | Non-pickup/unknown resource | `0xB8` | zero-terminated-record-list | 1 | 0 |
| 7 | Non-pickup/unknown resource | `0xC0` | zero-terminated-record-list | 1 | 0 |
| 8 | Herbs | `0x255C` | embedded-data-bundle | 8 | 6 |
| 9 | Non-pickup/unknown resource | `0x36B4` | embedded-data-bundle | 8 | 0 |
| 10 | Non-pickup/unknown resource | `0x2E6C` | embedded-data-bundle | 8 | 0 |
| 11 | Strength urn | `0x1C68` | embedded-data-bundle | 8 | 1 |

## Pickup usage

| ROM base | Callback | Parameter | Slot | Presentation |
|---:|---:|---:|---:|---:|
| `0x000CA030` | `0x80038770` | `0x00000000` | 0 | `0x800B1D18` |
| `0x000CA060` | `0x80038770` | `0x00000001` | 1 | `0x800B1D18` |
| `0x000CA090` | `0x80038770` | `0x00008002` | 2 | `0x800B1D18` |
| `0x000CA0C0` | `0x80038A90` | `0x00000000` | 11 | `0x800B1D38` |
| `0x000CA0F0` | `0x800389BC` | `0x00000000` | 8 | `0x800B1D38` |
| `0x000CA120` | `0x800389BC` | `0x00000000` | 8 | `0x800B1D38` |
| `0x000CA150` | `0x800389BC` | `0x00000000` | 8 | `0x800B1D38` |
| `0x000CA180` | `0x800389BC` | `0x00000000` | 8 | `0x800B1D38` |
| `0x000CA1B0` | `0x800389BC` | `0x00000000` | 8 | `0x800B1D38` |
| `0x000CA1E0` | `0x800389BC` | `0x00000000` | 8 | `0x800B1D38` |

## Recognized bundle records

Offsets below are relative to the stage resource-file base.

| Slot | Frame | Record | Storage | Resource/data value | Inferred end | Dimensions words |
|---:|---:|---:|---|---:|---:|---|
| 0 | 0 | `0xC8` | embedded-data | `0x364` | `0x3B0` | `0x00040014` / `0x00010007` |
| 0 | 1 | `0xDC` | embedded-data | `0x3B0` | `0x43C` | `0x00090014` / `0x00040007` |
| 0 | 2 | `0xF0` | embedded-data | `0x43C` | `0x4F8` | `0x000D0014` / `0x00060007` |
| 0 | 3 | `0x104` | embedded-data | `0x4F8` | `0x5E0` | `0x00100013` / `0x00070007` |
| 0 | 4 | `0x118` | embedded-data | `0x5E0` | `0x6D0` | `0x00120012` / `0x00080006` |
| 0 | 5 | `0x12C` | embedded-data | `0x6D0` | `0x7C0` | `0x00100013` / `0x00070007` |
| 0 | 6 | `0x140` | embedded-data | `0x7C0` | `0x8A8` | `0x000D0014` / `0x00050007` |
| 0 | 7 | `0x154` | embedded-data | `0x8A8` | `0x954` | `0x00090014` / `0x00030007` |
| 1 | 0 | `0x168` | embedded-data | `0x954` | `0x9A0` | `0x00040014` / `0x00010007` |
| 1 | 1 | `0x17C` | embedded-data | `0x9A0` | `0xA40` | `0x00090014` / `0x00040007` |
| 1 | 2 | `0x190` | embedded-data | `0xA40` | `0xB1C` | `0x000D0014` / `0x00060007` |
| 1 | 3 | `0x1A4` | embedded-data | `0xB1C` | `0xC14` | `0x00100013` / `0x00070007` |
| 1 | 4 | `0x1B8` | embedded-data | `0xC14` | `0xD2C` | `0x00120012` / `0x00080006` |
| 1 | 5 | `0x1CC` | embedded-data | `0xD2C` | `0xE38` | `0x00100013` / `0x00070007` |
| 1 | 6 | `0x1E0` | embedded-data | `0xE38` | `0xF34` | `0x000D0014` / `0x00050007` |
| 1 | 7 | `0x1F4` | embedded-data | `0xF34` | `0xFE8` | `0x00090014` / `0x00030007` |
| 2 | 0 | `0x208` | embedded-data | `0xFE8` | `0x103C` | `0x00050014` / `0x00020007` |
| 2 | 1 | `0x21C` | embedded-data | `0x103C` | `0x10D8` | `0x00090014` / `0x00040007` |
| 2 | 2 | `0x230` | embedded-data | `0x10D8` | `0x11B0` | `0x000D0014` / `0x00060007` |
| 2 | 3 | `0x244` | embedded-data | `0x11B0` | `0x12C0` | `0x00100013` / `0x00070007` |
| 2 | 4 | `0x258` | embedded-data | `0x12C0` | `0x13E0` | `0x00120012` / `0x00080006` |
| 2 | 5 | `0x26C` | embedded-data | `0x13E0` | `0x14F4` | `0x00100013` / `0x00070007` |
| 2 | 6 | `0x280` | embedded-data | `0x14F4` | `0x15F0` | `0x000D0014` / `0x00050007` |
| 2 | 7 | `0x294` | embedded-data | `0x15F0` | `0x16B0` | `0x00090014` / `0x00030007` |
| 3 | 0 | `0x485C` | external-resource-id | `0x38E` | `` | `0x00280024` / `0x00160016` |
| 3 | 1 | `0x4870` | external-resource-id | `0x38F` | `` | `0x002E0028` / `0x001A0019` |
| 3 | 2 | `0x4884` | external-resource-id | `0x390` | `` | `0x00320031` / `0x001C001B` |
| 3 | 3 | `0x4898` | external-resource-id | `0x391` | `` | `0x00330036` / `0x001D001E` |
| 3 | 4 | `0x48AC` | external-resource-id | `0x392` | `` | `0x00370039` / `0x00210021` |
| 3 | 5 | `0x48C0` | external-resource-id | `0x393` | `` | `0x003A0039` / `0x00230023` |
| 3 | 6 | `0x48D4` | external-resource-id | `0x394` | `` | `0x00380039` / `0x00220026` |
| 4 | 0 | `0x2E4` | embedded-data | `0x1AE4` | `0x1D54` | `0x001B001A` / `0x000E000A` |
| 5 | 0 | `0x2A8` | embedded-data | `0x16B0` | `0x17F0` | `0x001B001A` / `0x000E000A` |
| 6 | 0 | `0x2BC` | embedded-data | `0x17F0` | `0x1964` | `0x001B001A` / `0x000E000A` |
| 7 | 0 | `0x2D0` | embedded-data | `0x1964` | `0x1AE4` | `0x001B001A` / `0x000E000A` |
| 8 | 0 | `0x2584` | embedded-data | `0x2624` | `0x2708` | `0x00110017` / `0x0008000F` |
| 8 | 1 | `0x2598` | embedded-data | `0x2708` | `0x2808` | `0x00110017` / `0x0008000F` |
| 8 | 2 | `0x25AC` | embedded-data | `0x2808` | `0x2918` | `0x00100017` / `0x0007000F` |
| 8 | 3 | `0x25C0` | embedded-data | `0x2918` | `0x2A30` | `0x00100017` / `0x0008000F` |
| 8 | 4 | `0x25D4` | embedded-data | `0x2A30` | `0x2B54` | `0x00110017` / `0x0008000F` |
| 8 | 5 | `0x25E8` | embedded-data | `0x2B54` | `0x2C74` | `0x00100017` / `0x0007000F` |
| 8 | 6 | `0x25FC` | embedded-data | `0x2C74` | `0x2D80` | `0x00100017` / `0x0008000F` |
| 8 | 7 | `0x2610` | embedded-data | `0x2D80` | `0x2F34` | `0x00100017` / `0x0008000F` |
| 9 | 0 | `0x36DC` | embedded-data | `0x377C` | `0x3964` | `0x00160017` / `0x000B000B` |
| 9 | 1 | `0x36F0` | embedded-data | `0x3964` | `0x3B5C` | `0x00160017` / `0x000B000B` |
| 9 | 2 | `0x3704` | embedded-data | `0x3B5C` | `0x3D50` | `0x00160017` / `0x000B000B` |
| 9 | 3 | `0x3718` | embedded-data | `0x3D50` | `0x3F40` | `0x00160017` / `0x000B000B` |
| 9 | 4 | `0x372C` | embedded-data | `0x3F40` | `0x4128` | `0x00160017` / `0x000B000B` |
| 9 | 5 | `0x3740` | embedded-data | `0x4128` | `0x4314` | `0x00160017` / `0x000B000B` |
| 9 | 6 | `0x3754` | embedded-data | `0x4314` | `0x4508` | `0x00160017` / `0x000B000B` |
| 9 | 7 | `0x3768` | embedded-data | `0x4508` | `0x48F0` | `0x00160017` / `0x000B000B` |
| 10 | 0 | `0x2E94` | embedded-data | `0x2F34` | `0x302C` | `0x00110017` / `0x0008000F` |
| 10 | 1 | `0x2EA8` | embedded-data | `0x302C` | `0x312C` | `0x00110017` / `0x0008000F` |
| 10 | 2 | `0x2EBC` | embedded-data | `0x312C` | `0x3228` | `0x00100017` / `0x0007000F` |
| 10 | 3 | `0x2ED0` | embedded-data | `0x3228` | `0x3310` | `0x000F0017` / `0x0007000F` |
| 10 | 4 | `0x2EE4` | embedded-data | `0x3310` | `0x3400` | `0x000F0017` / `0x0007000F` |
| 10 | 5 | `0x2EF8` | embedded-data | `0x3400` | `0x34E0` | `0x000F0017` / `0x0007000F` |
| 10 | 6 | `0x2F0C` | embedded-data | `0x34E0` | `0x35CC` | `0x00100017` / `0x0008000F` |
| 10 | 7 | `0x2F20` | embedded-data | `0x35CC` | `0x377C` | `0x00100017` / `0x0008000F` |
| 11 | 0 | `0x1C90` | embedded-data | `0x1D54` | `0x1E58` | `0x00120015` / `0x0009000C` |
| 11 | 1 | `0x1CA4` | embedded-data | `0x1E58` | `0x1F58` | `0x00120015` / `0x0009000C` |
| 11 | 2 | `0x1CB8` | embedded-data | `0x1F58` | `0x2054` | `0x00110015` / `0x0008000C` |
| 11 | 3 | `0x1CCC` | embedded-data | `0x2054` | `0x2150` | `0x00110015` / `0x0008000C` |
| 11 | 4 | `0x1CE0` | embedded-data | `0x2150` | `0x2250` | `0x00110015` / `0x0008000C` |
| 11 | 5 | `0x1CF4` | embedded-data | `0x2250` | `0x234C` | `0x00110015` / `0x0008000C` |
| 11 | 6 | `0x1D08` | embedded-data | `0x234C` | `0x2450` | `0x00110015` / `0x0009000C` |
| 11 | 7 | `0x1D1C` | embedded-data | `0x2450` | `0x2624` | `0x00120015` / `0x0009000C` |

## Expansion capacity

This stage has no empty logical resource slots. Its 12-entry outer table ends at `0x30`, exactly where the first descriptor begins. Appending payload bytes to a relocated copy would enlarge the file physically, but it would not by itself create a new selector: adding another outer entry would overwrite the first descriptor. A safe expansion therefore requires either relocating/rebasing the descriptor region (and every affected relative reference), changing the lookup design, or first proving that an existing non-pickup slot is globally unused and safe to repurpose.

## Safety interpretation

Zero outer entries are free logical selectors only. They do not imply unused physical bytes inside the original file. New payload data must be appended to an expanded/relocated file or placed in storage proven safe by a complete reference analysis. Inferred model/data ends use the next discovered model-data start and are boundaries for analysis, not yet proof that trailing bytes are independently movable.

## Interpretation boundaries

- A zero outer-table entry is a free logical selector, not proof of unused physical bytes.
- An occupied slot with no ordinary-pickup user can still be referenced by another actor or script and is protected until traced.
- Inferred data ends support cataloging; they do not prove that trailing ranges are independently movable.
- Foreign resources require bounded storage, loader/arena validation, guarded references, and runtime testing.

Catalog lineage: generated from the preserved clean-ROM catalog artifacts and checked against the production pickup definitions in `src/mkmszr/data/pickups.py`. The tables above are reproduced here so this Wiki does not depend on an external archive for current technical facts.
