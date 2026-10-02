# Fortress stage catalog

> **Scope:** Stage-local catalog for Fortress, compact selector `7` / native stage ID `9`. Shared record grammar, resource notation, evidence labels, and safety rules are owned by [Stage catalogs](Stage-Catalogs). General extension-selector/materializer mechanics and composed-proof chronology remain owned by [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

## Stage identity and evidence

- **Static-confirmed:** all 9 ordinary pickup records, all 7 stock outer slots, and the recognized resource records below are decoded from the clean USA N64 ROM.
- **Runtime-confirmed:** the complete Fortress resource file was byte-matched against captured runtime memory at `0x801F4E20`.
- **Runtime-confirmed:** representative Fortress ordinary-pickup collection/persistence is established, but all 9 Fortress records have not been individually exhausted one by one in runtime testing.
- **Runtime/user-observed + Static-confirmed trigger ownership:** the three crystal reward records are spawned after defeating Kia, Jataaka, and Sareena. Fortress overlay file `0x9E` statically couples encounter indices 0/1/2 to the first three `0x30` pickup records and activates each record after the matching assassin encounter. For randomizer semantics these are three boss-defeat reward locations; the crystal identity is the stock reward, not a permanent binding between boss and reward.
- **Runtime-confirmed, proof-only (2026-09-30):** the Fortress five-import stress ROM replaced the first five stock Herbs locations with Potion, Urn of Vitality, Formula, Eye, and Shield while retaining the sixth Herbs record byte-for-byte as a control. Manual validation confirmed Fortress loaded normally; all five imported visuals rendered correctly and awarded the expected items; the control Herbs remained normal; and no rendering, audio, stability, or stage-progression regression was observed on the tested route.
- **Runtime-confirmed, proof-only (2026-09-30):** Kia's boss-defeat reward record `0xC4834` was changed from Crystal Kia to a Potion while preserving the boss-owned `0x8000` activation gate in `+0x14`. Manual validation confirmed no Potion reward existed before Kia's defeat; defeating Kia activated the replacement reward at the boss location; the model rendered as Potion; collection awarded Potion rather than Crystal Kia; and the encounter/stage remained healthy on the tested route. This confirms reward identity can change independently of the Fortress boss trigger on this bounded case.

## File mapping

| Property | Value |
|---|---:|
| Stage ID | `9` |
| Global resource file ID | `0x43` |
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

## Ordinary pickup records

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

## Pickup-to-resource usage

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

## Outer resource slots

| Slot | Name | Outer offset | Format | Frames | Pickup users |
|---:|---|---:|---|---:|---:|
| 0 | Crystal (Jataaka) | `0x48` | embedded-data-bundle | 8 | 1 |
| 1 | Crystal (Kia) | `0x1C` | embedded-data-bundle | 8 | 1 |
| 2 | Crystal (Sareena) | `0x74` | embedded-data-bundle | 8 | 1 |
| 3 | Herbs | `0x1338` | embedded-data-bundle | 8 | 6 |
| 4 | Non-pickup/unknown resource | `0x2490` | embedded-data-bundle | 8 | 0 |
| 5 | Non-pickup/unknown resource (aliases Herbs descriptor) | `0x1338` | embedded-data-bundle | 8 | 0 |
| 6 | Non-pickup/unknown resource | `0x1C48` | embedded-data-bundle | 8 | 0 |

## Recognized bundle/list records

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

## Fortress-specific notes, constraints, and proof-local evidence

- **Checkpoint/progression static closure (2026-09-29):** the stock Fortress crystal records use generic callback `0x80038770`, but its stage-9 branch awards IDs `0x20..0x22` and acquired bits without taking the generic direct `0x80062D60` presentation request or pickup-created `0x802C18F8` selector-write branches. Crystal USE dispatch entries map to position-gated progression handlers `0x8007239C / 0x80072400 / 0x80072464`, which commit bits `0x08/0x10/0x20` in `0x802C0D54`. The stock crystal award path is therefore Static-confirmed checkpoint-free. The remaining Fortress blocker is different: each boss-defeat reward location must materialize/award whichever logical item the global layout assigns while preserving the boss trigger.
- The stock resource file has exactly **7 occupied outer slots**. Its outer table occupies file-relative `0x0000..0x001B`; the first descriptor starts immediately at `0x1C`. There is no empty stock logical selector.
- Adding an eighth stock-table word in place would overwrite that first descriptor. This is a **Static-confirmed stock-layout fact**, not a claim that Fortress lacks all ordinary-pickup selector expansion paths.
- Slot `5` aliases the Herbs descriptor `0x1338` used by slot `3`. Slots `4` and `6` have no ordinary-pickup users, but all three remain protected until other Fortress actor/script references are resolved.
- **Bit-15 activation-gate closure (2026-10-02, Static-confirmed; Kia replacement Runtime-confirmed):** the crystal parameters `0x8000/0x8001/0x8002` use the same destination-record activation gate established generically in the Bridge audit. Pickup-manager setup consumes raw bit `0x8000`; callback dispatch masks it away. Fortress encounter manager `0x802EFDB0` clears that bit only on the indexed boss reward record after the corresponding assassin completes. The low 15 bits remain the logical crystal index/ID input to the stock callback.
- The first three catalog rows describe the **stock spawned rewards** for the Kia/Jataaka/Sareena boss checks. Static overlay trace now resolves the exact association: ASSASSIN1/type `0x0D` -> Kia record `0xC4834`, ASSASSIN3/type `0x13` -> Jataaka record `0xC4864`, and ASSASSIN2/type `0x1C` -> Sareena record `0xC4894`. The manager copies the defeated actor X into record `+0x00` and clears the `0x8000` bit in record `+0x14` to activate the indexed reward. The final global materializer must preserve this trigger while allowing any assigned logical item identity in the reward record.
- **Fortress selector/checkpoint ownership closure (2026-10-02, Static-confirmed):** raw Fortress overlay file `0x9E` is ROM `[0xC0330,0xC4C70)` at runtime base `0x802ECE30`. Direct global-selector writes in this overlay are: selector `9` during an initialization/re-entry path at ROM `0xC044C`; selector `5` at `0xC28FC`, selector `6` at `0xC2938`, selector `8` at `0xC2998`, and encounter-index-derived selector `s4+2` at `0xC38B0`. None of the nine ordinary pickup callbacks write `0x802C18F8`.
- **Boss-defeat checkpoint binding (2026-10-02, Static-confirmed):** encounter manager `0x802EFDB0` handles indices `s4=0/1/2`. On completion it writes selector `s4+2`, producing `2/3/4`, and separately records the completed encounter mask and activates the corresponding gated reward record. Fortress spawn-table selectors `2/3/4` at `0x800A01BC/0x800A01D0/0x800A01E4` have X/Y coordinates `0x00047300/-0x00054000`, `0x00194900/-0x000A8000`, and `0x00414E00/-0x000FC000`, exactly matching the three encounter-table centers in `0x802F15B8 + index*0x18`. Therefore those checkpoint/state advances are **boss-encounter-owned**, not reward-pickup-owned.
- **Crystal-use progression/checkpoint binding (2026-10-02, Static-confirmed):** permanent use handlers `0x8007239C / 0x80072400 / 0x80072464` commit progression bits `0x08/0x10/0x20` after player-position checks. Fortress overlay state machine `0x802EF30C` consumes `(0x802C0D54 >> 3) & 7` and maps progression states into later native selector/checkpoint states: `5`, `6`, and `8`, each through a stock `0x80062D60` presentation path where applicable. The position windows for the first two USE handlers center on selector-5 and selector-6 spawn coordinates (`X=0x000A8000` and `0x003C0000`); the third USE zone centers around `X≈0x0023FC00`, adjacent to selector-7 spawn `0x00240000`, while the completed third progression route advances onward to selector `8`. These are native progression/use semantics, not ordinary reward-location semantics.
- **Accepted Fortress destination contract (2026-10-02):** none of the nine ordinary Fortress locations needs a checkpoint wrapper. The six stock Herbs locations have no identified destination activation/checkpoint side effect. The first three boss-reward locations retain only their **destination-owned bit-15 activation gate and encounter-controlled X relocation**; the assigned logical reward is materialized/awarded independently. Logical crystals remain checkpoint-free inventory rewards; their later USE handlers and Fortress progression/checkpoint state remain stock-owned. The shared materializer's generic destination-gate preservation already represents this contract.
- **Composed five-import stress construction — Runtime-confirmed, proof-only:** the disposable proof replaces the first five stock Herbs locations with Potion, Urn of Vitality, Formula, Eye, and Shield, retains another Herbs record byte-for-byte as a control, and supplies five contiguous extension-selector entries plus self-contained imported bundles. Manual runtime validation confirmed the five models/awards and untouched Herbs control in Fortress with no observed rendering, audio, stability, or progression regression on the tested route. The generalized construction details remain on [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).
- **Fortress ordinary-location ownership is now statically closed for all nine records.** The shared materializer already generalizes destination bit-15 preservation across all three assassin reward records and keeps logical crystal awards separate; the Kia substituted-reward route is Runtime-confirmed bounded evidence. Remaining work belongs to whole-system wrapper/integration validation rather than more Fortress ownership research.

## Related owners

- [Stage catalogs](Stage-Catalogs) — shared schema, notation, safety rules, catalog lineage, and eight-stage index.
- [Data structures and encodings](Data-Structures-and-Encodings) — ordinary `0x30`-byte record grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file-table, loader, overlay, and selector/resource grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership, lifecycle, and proof/production allocation boundaries.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded ROM edit sites.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior and modeled stage dependencies.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — extension-selector/materializer mechanics, planner/deduplication, external-to-embedded conversion, solver rules, and full composed-proof chronology.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and stage-transition lifecycle.
