# Fortress stage catalog

**Evidence status:** Static-confirmed from the clean USA N64 ROM; file-to-RDRAM mappings were also matched against captured runtime memory. Ordinary-pickup behavior and persistence are runtime-confirmed at representative locations, but the complete 84-record set has not been collected exhaustively one record at a time.

This page is the self-contained decoded catalog for native stage ID `9`. It includes every ordinary pickup record and every recognized resource slot/record. Values are big-endian. Unknown fields remain named by offset instead of being assigned unsupported semantics.

## Ordinary pickup records

A record is `0x30` bytes. Position and metadata (`+0x00..+0x0F`) and the collected flag (`+0x2C`) belong to the destination. The production randomizer moves the seven-word identity slice `+0x10..+0x2B`. `Token` and `Requires` are production logic metadata, not bytes stored in the native record.

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

## Resource-file catalog

Generated conservatively from the clean USA N64 ROM. Recognized bundles distinguish embedded model/data offsets from records that reference external resource IDs; `unknown/nonstandard` is intentionally not guessed.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `9` |
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

## Outer slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Crystal (Jataaka) | `0x48` | embedded-data-bundle | 8 | 1 |
| 1 | Crystal (Kia) | `0x1C` | embedded-data-bundle | 8 | 1 |
| 2 | Crystal (Sareena) | `0x74` | embedded-data-bundle | 8 | 1 |
| 3 | Herbs | `0x1338` | embedded-data-bundle | 8 | 6 |
| 4 | Non-pickup/unknown resource | `0x2490` | embedded-data-bundle | 8 | 0 |
| 5 | Non-pickup/unknown resource (aliases Herbs descriptor) | `0x1338` | embedded-data-bundle | 8 | 0 |
| 6 | Non-pickup/unknown resource | `0x1C48` | embedded-data-bundle | 8 | 0 |

## Pickup usage

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

## Stage-specific notes

- The complete 0x3620-byte ROM resource file matches RDRAM at 0x801F4E20 byte-for-byte in live Fortress gameplay.
- All nine standard 0x30-byte pickup records are contiguous and mapped: the Jataaka, Kia, and Sareena crystals plus six Herbs pickups.
- The crystal callback parameters are raw 0x00008000, 0x00008001, and 0x00008002; their low selectors correspond to inventory IDs 0x20, 0x21, and 0x22 through the stage-dependent callback, while the high-bit meaning remains unresolved.
- All seven selectors are occupied. Slot 5 aliases the Herbs descriptor used by slot 3, while slots 4 and 6 have no ordinary pickup users; none is considered safe to repurpose without tracing other Fortress actors or scripts.

## Recognized bundle records

Offsets below are relative to the stage resource-file base.

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

## Expansion capacity

This stage has no empty logical resource slots. Its 7-entry outer table ends at `0x1C`, exactly where the first descriptor begins. Appending payload bytes to a relocated copy would enlarge the file physically, but it would not by itself create a new selector: adding another outer entry would overwrite the first descriptor. A safe expansion therefore requires either relocating/rebasing the descriptor region (and every affected relative reference), changing the lookup design, or first proving that an existing non-pickup slot is globally unused and safe to repurpose.

## Safety interpretation

Zero outer entries are free logical selectors only. They do not imply unused physical bytes inside the original file. New payload data must be appended to an expanded/relocated file or placed in storage proven safe by a complete reference analysis. Inferred model/data ends use the next discovered model-data start and are boundaries for analysis, not yet proof that trailing bytes are independently movable.

## Interpretation boundaries

- A zero outer-table entry is a free logical selector, not proof of unused physical bytes.
- An occupied slot with no ordinary-pickup user can still be referenced by another actor or script and is protected until traced.
- Inferred data ends support cataloging; they do not prove that trailing ranges are independently movable.
- Foreign resources require bounded storage, loader/arena validation, guarded references, and runtime testing.

Catalog lineage: generated from the preserved clean-ROM catalog artifacts and checked against the production pickup definitions in `src/mkmszr/data/pickups.py`. The tables above are reproduced here so this Wiki does not depend on an external archive for current technical facts.
