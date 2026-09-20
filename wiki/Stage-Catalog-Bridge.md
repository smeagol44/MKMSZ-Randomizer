# Bridge stage catalog

**Evidence status:** Static-confirmed from the clean USA N64 ROM; file-to-RDRAM mappings were also matched against captured runtime memory. Ordinary-pickup behavior and persistence are runtime-confirmed at representative locations, but the complete 84-record set has not been collected exhaustively one record at a time.

This page is the self-contained decoded catalog for native stage ID `8`. It includes every ordinary pickup record and every recognized resource slot/record. Values are big-endian. Unknown fields remain named by offset instead of being assigned unsupported semantics.

## Ordinary pickup records

A record is `0x30` bytes. Position and metadata (`+0x00..+0x0F`) and the collected flag (`+0x2C`) belong to the destination. The production randomizer moves the seven-word identity slice `+0x10..+0x2B`. `Token` and `Requires` are production logic metadata, not bytes stored in the native record.

| # | Decoded identity | ROM base | RDRAM base | X | Y | Z | +0C | +10 type | +14 parameter | +18 callback | +1C | +20 | +24 slot | +28 presentation | +2C collected | Token | Requires |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | Bridge Omega | `0x000BFFD8` | — | `0x00090DDD` | `0x0009A700` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00008000` | `0x802EF178` | `0x00000020` | `0x00000020` | `0` | `0x800B1D18` | `0x00000000` | `bridge-omega` | — |
| 2 | Bridge Rings | `0x000C0008` | — | `0x00154A79` | `0x00002400` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00008001` | `0x802EF178` | `0x00000020` | `0x00000020` | `1` | `0x800B1D18` | `0x00000000` | `bridge-rings` | — |
| 3 | Bridge Arrow | `0x000C0038` | — | `0x002D6D54` | `0x0003E200` | `0x00000000` | `0x00000004` | `0x00000000` | `0x00008002` | `0x802EF178` | `0x00000020` | `0x00000020` | `2` | `0x800B1D18` | `0x00000000` | `bridge-arrow` | — |
| 4 | Health urn | `0x000C0068` | — | `0x002D6D54` | `0x00002D00` | `0x00000000` | `0x00000004` | `0x00000006` | `0x00008000` | `0x800389EC` | `0x00000020` | `0x00000020` | `24` | `0x800B1D38` | `0x00000000` | — | — |
| 5 | Potion | `0x000C0098` | — | `0x000DE7DD` | `0x00002400` | `0x00000000` | `0x00000004` | `0x0000000B` | `0x00000000` | `0x800388FC` | `0x00000020` | `0x00000020` | `23` | `0x800B1BAC` | `0x00000000` | — | — |
| 6 | Herbs | `0x000C00C8` | — | `0x001107AB` | `0x00002400` | `0x00000000` | `0x00000004` | `0x00000001` | `0x00000000` | `0x800389BC` | `0x00000020` | `0x00000020` | `21` | `0x800B1D38` | `0x00000000` | — | — |
| 7 | Extra-life urn | `0x000C00F8` | — | `0x0019F556` | `0x00015B00` | `0x00000000` | `0x00000004` | `0x00000002` | `0x00000000` | `0x80038A1C` | `0x00000020` | `0x00000020` | `22` | `0x800B1D38` | `0x00000000` | — | — |
| 8 | Health urn | `0x000C0128` | — | `0x002335A7` | `0xFFFE3700` | `0x00000000` | `0x00000004` | `0x00000006` | `0x00000000` | `0x800389EC` | `0x00000020` | `0x00000020` | `24` | `0x800B1D38` | `0x00000000` | — | — |
| 9 | Health urn | `0x000C0158` | — | `0x00243C9F` | `0xFFFE3700` | `0x00000000` | `0x00000004` | `0x00000006` | `0x00000000` | `0x800389EC` | `0x00000020` | `0x00000020` | `24` | `0x800B1D38` | `0x00000000` | — | — |
| 10 | Health urn | `0x000C0188` | — | `0x0025C713` | `0xFFFE3700` | `0x00000000` | `0x00000004` | `0x00000006` | `0x00000000` | `0x800389EC` | `0x00000020` | `0x00000020` | `24` | `0x800B1D38` | `0x00000000` | — | — |

## Resource-file catalog

Generated conservatively from the clean USA N64 ROM. Recognized bundles distinguish embedded model/data offsets from records that reference external resource IDs; `unknown/nonstandard` is intentionally not guessed.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `8` |
| File-table entry ROM | `0x000A51E4` |
| Resource ROM range | `0x00296140..0x0029A46F` |
| File size | `0x4330` (17200 bytes) |
| File-table flag | `0` |
| Verified runtime base | `0x80243000` |
| Outer slots | `25` |
| Outer-table end | `0x64` |
| First descriptor | `0x64` |
| Empty logical slots | `4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20` |
| Unknown/nonstandard slots | `none` |
| Pickup records | `10` |

## Outer slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Fortress icon, omega | `0x64` | embedded-data-bundle | 8 | 1 |
| 1 | Fortress icon, rings | `0x8C` | embedded-data-bundle | 8 | 1 |
| 2 | Fortress icon, arrow | `0xB4` | embedded-data-bundle | 8 | 1 |
| 3 | Non-pickup/unknown resource | `0xDC` | zero-terminated-record-list | 14 | 0 |
| 4 | Unused logical slot | `0` | empty | — | 0 |
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
| 20 | Unused logical slot | `0` | empty | — | 0 |
| 21 | Herbs | `0x118` | embedded-data-bundle | 8 | 1 |
| 22 | Extra-life urn | `0x140` | embedded-data-bundle | 8 | 1 |
| 23 | Potion | `0x57C` | external-resource-id-bundle | 8 | 1 |
| 24 | Health urn | `0x514` | external-resource-id-bundle | 4 | 4 |

## Pickup usage

| ROM base | Callback | Parameter | Slot | Presentation |
|---:|---:|---:|---:|---:|
| `0x000BFFD8` | `0x802EF178` | `0x00008000` | 0 | `0x800B1D18` |
| `0x000C0008` | `0x802EF178` | `0x00008001` | 1 | `0x800B1D18` |
| `0x000C0038` | `0x802EF178` | `0x00008002` | 2 | `0x800B1D18` |
| `0x000C0068` | `0x800389EC` | `0x00008000` | 24 | `0x800B1D38` |
| `0x000C0098` | `0x800388FC` | `0x00000000` | 23 | `0x800B1BAC` |
| `0x000C00C8` | `0x800389BC` | `0x00000000` | 21 | `0x800B1D38` |
| `0x000C00F8` | `0x80038A1C` | `0x00000000` | 22 | `0x800B1D38` |
| `0x000C0128` | `0x800389EC` | `0x00000000` | 24 | `0x800B1D38` |
| `0x000C0158` | `0x800389EC` | `0x00000000` | 24 | `0x800B1D38` |
| `0x000C0188` | `0x800389EC` | `0x00000000` | 24 | `0x800B1D38` |

## Stage-specific notes

- The complete 0x4330-byte ROM resource file matches RDRAM at 0x80243000 byte-for-byte in live Bridge gameplay.
- All ten standard 0x30-byte pickup records are contiguous and mapped: three Fortress icons, four Health urns, and one each of Herbs, Extra-life urn, and Potion.
- The three icon callback parameters are raw 0x00008000, 0x00008001, and 0x00008002; their low selectors remain 0, 1, and 2, while the high-bit meaning is unresolved.
- The first Health urn record also carries callback parameter 0x00008000 while the other three use zero; this difference is preserved without assigning a meaning.
- Occupied slot 3 has no user among the ten ordinary pickup records and remains protected from reuse.

## Recognized bundle records

Offsets below are relative to the stage resource-file base.

| Slot | Frame | Record | Storage | Resource/data value | Inferred end | Dimensions words |
|---:|---:|---:|---|---:|---:|---|
| 0 | 0 | `0x334` | embedded-data | `0x29A0` | `0x2A38` | `0x00120012` / `0x00080008` |
| 0 | 1 | `0x348` | embedded-data | `0x2A38` | `0x2AF0` | `0x00120012` / `0x00080008` |
| 0 | 2 | `0x35C` | embedded-data | `0x2AF0` | `0x2BC4` | `0x00100012` / `0x00070008` |
| 0 | 3 | `0x370` | embedded-data | `0x2BC4` | `0x2C7C` | `0x000E0012` / `0x00060008` |
| 0 | 4 | `0x384` | embedded-data | `0x2C7C` | `0x2D0C` | `0x000E0012` / `0x00060008` |
| 0 | 5 | `0x398` | embedded-data | `0x2D0C` | `0x2DB8` | `0x000E0012` / `0x00060008` |
| 0 | 6 | `0x3AC` | embedded-data | `0x2DB8` | `0x2E7C` | `0x00100012` / `0x00070008` |
| 0 | 7 | `0x3C0` | embedded-data | `0x2E7C` | `0x2F40` | `0x00120012` / `0x00080008` |
| 1 | 0 | `0x3D4` | embedded-data | `0x2F40` | `0x2FE4` | `0x0012000E` / `0x00080007` |
| 1 | 1 | `0x3E8` | embedded-data | `0x2FE4` | `0x30D4` | `0x0015000E` / `0x000A0007` |
| 1 | 2 | `0x3FC` | embedded-data | `0x30D4` | `0x31F4` | `0x0018000E` / `0x000B0007` |
| 1 | 3 | `0x410` | embedded-data | `0x31F4` | `0x32F8` | `0x0015000E` / `0x00090007` |
| 1 | 4 | `0x424` | embedded-data | `0x32F8` | `0x33C0` | `0x0012000E` / `0x00080007` |
| 1 | 5 | `0x438` | embedded-data | `0x33C0` | `0x34D0` | `0x0016000E` / `0x000B0007` |
| 1 | 6 | `0x44C` | embedded-data | `0x34D0` | `0x35EC` | `0x0018000E` / `0x000B0007` |
| 1 | 7 | `0x460` | embedded-data | `0x35EC` | `0x36DC` | `0x0015000E` / `0x00090007` |
| 2 | 0 | `0x474` | embedded-data | `0x36DC` | `0x3724` | `0x00040013` / `0x0001000A` |
| 2 | 1 | `0x488` | embedded-data | `0x3724` | `0x37AC` | `0x00080013` / `0x0003000A` |
| 2 | 2 | `0x49C` | embedded-data | `0x37AC` | `0x3874` | `0x000D0013` / `0x0006000A` |
| 2 | 3 | `0x4B0` | embedded-data | `0x3874` | `0x3954` | `0x00100013` / `0x0007000A` |
| 2 | 4 | `0x4C4` | embedded-data | `0x3954` | `0x3A24` | `0x00120012` / `0x0008000A` |
| 2 | 5 | `0x4D8` | embedded-data | `0x3A24` | `0x3AFC` | `0x00100013` / `0x0007000A` |
| 2 | 6 | `0x4EC` | embedded-data | `0x3AFC` | `0x3BBC` | `0x000D0013` / `0x0005000A` |
| 2 | 7 | `0x500` | embedded-data | `0x3BBC` | `0x3C50` | `0x00080013` / `0x0003000A` |
| 3 | 0 | `0x208` | embedded-data | `0x644` | `0x96C` | `0x00280024` / `0x00160016` |
| 3 | 1 | `0x208` | embedded-data | `0x644` | `0x96C` | `0x00280024` / `0x00160016` |
| 3 | 2 | `0x21C` | embedded-data | `0x96C` | `0xD70` | `0x002E0028` / `0x001A0019` |
| 3 | 3 | `0x21C` | embedded-data | `0x96C` | `0xD70` | `0x002E0028` / `0x001A0019` |
| 3 | 4 | `0x230` | embedded-data | `0xD70` | `0x1248` | `0x00320031` / `0x001C001B` |
| 3 | 5 | `0x230` | embedded-data | `0xD70` | `0x1248` | `0x00320031` / `0x001C001B` |
| 3 | 6 | `0x244` | embedded-data | `0x1248` | `0x1740` | `0x00330036` / `0x001D001E` |
| 3 | 7 | `0x244` | embedded-data | `0x1248` | `0x1740` | `0x00330036` / `0x001D001E` |
| 3 | 8 | `0x258` | embedded-data | `0x1740` | `0x1BC0` | `0x00370039` / `0x00210021` |
| 3 | 9 | `0x258` | embedded-data | `0x1740` | `0x1BC0` | `0x00370039` / `0x00210021` |
| 3 | 10 | `0x26C` | embedded-data | `0x1BC0` | `0x1F4C` | `0x003A0039` / `0x00230023` |
| 3 | 11 | `0x26C` | embedded-data | `0x1BC0` | `0x1F4C` | `0x003A0039` / `0x00230023` |
| 3 | 12 | `0x280` | embedded-data | `0x1F4C` | `0x2158` | `0x00380039` / `0x00220026` |
| 3 | 13 | `0x280` | embedded-data | `0x1F4C` | `0x2158` | `0x00380039` / `0x00220026` |
| 21 | 0 | `0x294` | embedded-data | `0x2158` | `0x223C` | `0x00110017` / `0x0008000F` |
| 21 | 1 | `0x2A8` | embedded-data | `0x223C` | `0x233C` | `0x00110017` / `0x0008000F` |
| 21 | 2 | `0x2BC` | embedded-data | `0x233C` | `0x244C` | `0x00100017` / `0x0007000F` |
| 21 | 3 | `0x2D0` | embedded-data | `0x244C` | `0x2564` | `0x00100017` / `0x0008000F` |
| 21 | 4 | `0x2E4` | embedded-data | `0x2564` | `0x2688` | `0x00110017` / `0x0008000F` |
| 21 | 5 | `0x2F8` | embedded-data | `0x2688` | `0x27A8` | `0x00100017` / `0x0007000F` |
| 21 | 6 | `0x30C` | embedded-data | `0x27A8` | `0x28B4` | `0x00100017` / `0x0008000F` |
| 21 | 7 | `0x320` | embedded-data | `0x28B4` | `0x29A0` | `0x00100017` / `0x0008000F` |
| 22 | 0 | `0x168` | embedded-data | `0x3C50` | `0x3D38` | `0x00110018` / `0x0008000D` |
| 22 | 1 | `0x17C` | embedded-data | `0x3D38` | `0x3E18` | `0x00110018` / `0x0008000D` |
| 22 | 2 | `0x190` | embedded-data | `0x3E18` | `0x3EEC` | `0x00100018` / `0x0007000D` |
| 22 | 3 | `0x1A4` | embedded-data | `0x3EEC` | `0x3FB0` | `0x00100018` / `0x0007000D` |
| 22 | 4 | `0x1B8` | embedded-data | `0x3FB0` | `0x4060` | `0x000F0018` / `0x0007000D` |
| 22 | 5 | `0x1CC` | embedded-data | `0x4060` | `0x4108` | `0x000F0018` / `0x0008000D` |
| 22 | 6 | `0x1E0` | embedded-data | `0x4108` | `0x41CC` | `0x00100018` / `0x0008000D` |
| 22 | 7 | `0x1F4` | embedded-data | `0x41CC` | `0x4330` | `0x00110018` / `0x0008000D` |
| 23 | 0 | `0x5A4` | external-resource-id | `0x27F` | `` | `0x00110017` / `0x0008000F` |
| 23 | 1 | `0x5B8` | external-resource-id | `0x280` | `` | `0x00110017` / `0x0008000F` |
| 23 | 2 | `0x5CC` | external-resource-id | `0x281` | `` | `0x00100017` / `0x0007000F` |
| 23 | 3 | `0x5E0` | external-resource-id | `0x282` | `` | `0x000F0017` / `0x0007000F` |
| 23 | 4 | `0x5F4` | external-resource-id | `0x283` | `` | `0x000F0017` / `0x0007000F` |
| 23 | 5 | `0x608` | external-resource-id | `0x284` | `` | `0x000F0017` / `0x0007000F` |
| 23 | 6 | `0x61C` | external-resource-id | `0x285` | `` | `0x00100017` / `0x0008000F` |
| 23 | 7 | `0x630` | external-resource-id | `0x286` | `` | `0x00100017` / `0x0008000F` |
| 24 | 0 | `0x52C` | external-resource-id | `0x28F` | `` | `0x00110011` / `0x00070009` |
| 24 | 1 | `0x540` | external-resource-id | `0x290` | `` | `0x00100011` / `0x00060009` |
| 24 | 2 | `0x554` | external-resource-id | `0x291` | `` | `0x000F0011` / `0x00060009` |
| 24 | 3 | `0x568` | external-resource-id | `0x292` | `` | `0x00100011` / `0x00070009` |

## Safety interpretation

Zero outer entries are free logical selectors only. They do not imply unused physical bytes inside the original file. New payload data must be appended to an expanded/relocated file or placed in storage proven safe by a complete reference analysis. Inferred model/data ends use the next discovered model-data start and are boundaries for analysis, not yet proof that trailing bytes are independently movable.

## Interpretation boundaries

- A zero outer-table entry is a free logical selector, not proof of unused physical bytes.
- An occupied slot with no ordinary-pickup user can still be referenced by another actor or script and is protected until traced.
- Inferred data ends support cataloging; they do not prove that trailing ranges are independently movable.
- Foreign resources require bounded storage, loader/arena validation, guarded references, and runtime testing.

Catalog lineage: generated from the preserved clean-ROM catalog artifacts and checked against the production pickup definitions in `src/mkmszr/data/pickups.py`. The tables above are reproduced here so this Wiki does not depend on an external archive for current technical facts.
