# Stage catalogs

These eight pages reproduce the decoded ordinary-pickup tables, outer resource slots, pickup-to-slot usage, stage notes, and every recognized per-frame resource record. They are the working catalogs; no external CSV or archive is required.

| Compact selector | Native ID | Stage | Pickups | Catalog |
|---:|---:|---|---:|---|
| 0 | 0 | Temple | 4 | [Temple](Stage-Catalog-Temple) |
| 1 | 1 | Wind | 6 | [Wind](Stage-Catalog-Wind) |
| 2 | 2 | Water | 9 | [Water](Stage-Catalog-Water) |
| 3 | 3 | Earth | 20 | [Earth](Stage-Catalog-Earth) |
| 4 | 4 | Prison | 10 | [Prison](Stage-Catalog-Prison) |
| 5 | 5 | Fire | 16 | [Fire](Stage-Catalog-Fire) |
| 6 | 8 | Bridge | 10 | [Bridge](Stage-Catalog-Bridge) |
| 7 | 9 | Fortress | 9 | [Fortress](Stage-Catalog-Fortress) |
|  |  | **Total** | **84** |  |

## What is complete

- All 84 ordinary `0x30`-byte records and every raw word are listed.
- Production progression tokens and location requirements are shown alongside native bytes.
- All eight resource-file ROM ranges and verified runtime bases are recorded.
- Every outer selector is classified as empty, recognized, or explicitly unknown/nonstandard.
- Recognized bundle/list records include frame, descriptor offset, storage kind, data/resource value, inferred end, and dimension words.

## What “complete catalog” does not mean

The tables are static-confirmed and the resource files were byte-matched in runtime captures. They do not claim that every occupied resource slot's gameplay owner is known or that every one of the 84 records has been collected individually. A slot with no ordinary-pickup user remains protected because another actor or script may own it. Zero outer entries are logical capacity, never proof of free physical bytes.

The Temple Map is a scripted/special actor and is intentionally absent from the four ordinary Temple records. Boss items and Shinnok's Amulet likewise use separate paths.
