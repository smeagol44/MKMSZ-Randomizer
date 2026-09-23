# Prison stage catalog

> **Scope:** Stage-local catalog for Prison, compact selector `4` / native stage ID `4`. Shared record grammar, resource notation, evidence labels, and safety rules are owned by [Stage catalogs](Stage-Catalogs). General extension-selector/materializer interpretation and proof chronology remain owned by [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

## Stage identity and evidence

- **Static-confirmed:** all 10 ordinary pickup records, all 12 stock outer slots, and the recognized resource records below are decoded from the clean USA N64 ROM.
- **Runtime-confirmed:** the Prison resource-file mapping was matched against captured runtime memory at `0x801FB798`.
- **Runtime-confirmed:** representative Prison ordinary-pickup collection/persistence is established, but all 10 Prison records have not been individually exhausted one by one in runtime testing.
- **Runtime-confirmed, proof-only:** Prison is the destination used for the six-Herbs extension-selector proof, single imported embedded Potion proof, converted Health-urn proof, and the composed five-import visual stress proof. Exact stage-local configurations are preserved below; the generalized conclusions remain with the global materialization owner.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `4` |
| Global resource file ID | `0x49` |
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

## Ordinary pickup records

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

## Pickup-to-resource usage

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

## Outer resource slots

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

## Recognized bundle/list records

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

## Prison-specific notes, constraints, and proof-local evidence

- The stock resource file has exactly 12 outer slots. Its outer table occupies file-relative `0x0000..0x002F`; the first descriptor starts immediately at `0x30`. **No stock outer slot is empty.** Inserting a 13th stock-table word in place would overwrite the first descriptor.
- That stock-table layout does **not** mean Prison lacks ordinary-pickup selector expansion capacity. The later extension-selector mechanism avoids inserting into the stock table. The lookup mechanics and their interpretation are canonical in [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).
- **Disposable Proof D — Runtime-confirmed, proof-only:** the stock `0x48F0`-byte Prison resource file was relocated/expanded by four bytes. A selector word appended at file-relative `0x48F0` pointed to the existing Herbs descriptor `0x255C`, producing selector `0x123C` (`0x48F0 / 4`). All six Prison Herbs ordinary records were changed from stock selector `8` to `0x123C`. Two early Herbs were manually collected and rendered/awarded like vanilla Herbs; the other four were not individually runtime-tested in that proof.
- **Disposable Proof F — Runtime-confirmed, proof-only:** stock Prison selectors remained intact. Extension selector `0x123C` pointed to an appended, file-relative-pointer-rebased copy of Water's embedded Potion bundle. One early Prison Herbs location became Potion while the remaining Herbs records stayed stock. The imported Potion and an untouched Herbs control both rendered and awarded correctly.
- **Disposable Proof H — Runtime-confirmed, proof-only:** extension selector `0x123C` pointed to an appended self-contained Health-urn bundle converted from external-resource IDs to embedded type-4 blocks. One early Prison Herbs became an Urn of Vitality while another Herbs remained untouched; both rendered and awarded correctly. The generalized external-to-embedded conversion conclusion is not owned by this stage page.
- **Composed five-import stress proof — Runtime-confirmed, proof-only:** Prison's resource file expanded from `0x48F0` to `0x7CB4`. Five contiguous extension-selector words began at file-relative `0x48F0`, yielding selectors `0x123C..0x1240`. The first five stock Herbs locations were replaced by Potion, Urn of Vitality, Formula, Eye, and Shield; another Herbs record remained byte-for-byte vanilla as a control. All five imported models and expected awards, plus the untouched Herbs control, were manually confirmed in Prison.
- The Proof D/F/H and five-import constructions expand a **relocated proof copy** of the stage resource file. They do not convert any ROM range, appended selector word, or appended payload region into a production allocation.
- Occupied stock slots with zero ordinary-pickup users remain protected. Prison-specific proof success does not establish those selectors as repurposable for production or prove that another stage can use the same resource layout.
- Current limits remain bounded to the documented routes: the six-Herbs proof observed two of six modified pickups; the single-import proofs observed their chosen location plus a stock control; the composed proof observed five imported visuals plus a stock control. These results do not constitute exhaustive runtime validation of all Prison pickup/resource combinations.

## Related owners

- [Stage catalogs](Stage-Catalogs) — shared schema, notation, safety rules, and eight-stage index.
- [Data structures and encodings](Data-Structures-and-Encodings) — ordinary `0x30`-byte record grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file-table, loader, overlay, and selector/resource grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership, lifecycle, and proof/production allocation boundaries.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded ROM edit sites.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior and modeled stage dependencies.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — extension-selector/materializer mechanics, external-to-embedded interpretation, planner/deduplication, solver rules, and full proof chronology.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and stage-transition lifecycle.
