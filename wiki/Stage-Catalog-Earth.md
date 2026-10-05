# Earth stage catalog

> **Scope:** Stage-local catalog for Earth, compact selector `3` / native stage ID `3`. Shared record grammar, resource notation, evidence labels, and safety rules are owned by [Stage catalogs](Stage-Catalogs).

## Stage identity and evidence

- **Static-confirmed:** all 20 ordinary pickup records are decoded from the clean USA N64 ROM.
- **Static-confirmed:** Earth ordinary-pickup visuals resolve through global file `0x30`, whose 21-entry selector table and pickup-used bundles are cataloged below. The previous file-`0x88` pickup-resource mapping is Rejected / superseded.
- **Runtime-confirmed, v38:** all three Earth key visuals from file `0x30` render correctly when imported into TEST LAB through the Fire destination-resource architecture; the tested Earth key awards correctly in inventory.
- **Runtime-confirmed:** the all-eight-stage persistence validation collected/restored a representative Earth ordinary pickup. The 20 Earth records have not been individually exhausted one by one in runtime testing.
- Earth's three stage key pickups use stage-qualified overlay callback VA `0x802F52B0`; this address is Earth-overlay evidence, not a globally resident callback identity.

## File mapping

The Earth ordinary-pickup resource file is **global file ID `0x30`**, not file `0x88`. File `0x88` is the separate MONK1 fighter resource and is loaded into fighter-resource slot `0x801AE470`.

The Earth stage setup allocates file `0x30`, publishes that allocation through the ordinary-pickup resource-base slot `0x802E82B8` at `0x8000EA58`, then raw-loads file `0x30` at `0x8000EA5C`. This is the base consumed by the ordinary pickup selector path.

| Property | Value |
|---|---:|
| Stage ID | `3` |
| Ordinary-pickup resource file ID | `0x30` |
| File-table entry ROM | `0x000A5250` |
| Resource ROM range | `0x00305A30..0x0030A9FF` |
| File size | `0x4FD0` (20432 bytes) |
| File-table flag | `0` |
| Runtime publication slot | `0x802E82B8` |
| Outer slots | `21` |
| Outer-table end / first descriptor | `0x54` |
| Empty logical slots | `4, 5, 7, 9` |
| Pickup records | `20` |

**Superseded mapping:** the former catalog entry that treated file `0x88` (`0x006BAEC0..0x006DD46F`, size `0x225B0`) as the Earth ordinary-pickup resource is rejected. That file is MONK1 fighter data. The v34-v37 TEST LAB line exposed the error directly: importing selectors `0..2` from file `0x88` produced/hung on monk imagery rather than Earth icons.

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
| 0 | Earth icon, square | `0x3A4` | embedded-data-bundle | 8 | 1 |
| 1 | Earth icon, four squares | `0x3CC` | embedded-data-bundle | 8 | 1 |
| 2 | Earth icon, triangle | `0x3F4` | embedded-data-bundle | 8 | 1 |
| 3 | Non-pickup/unknown resource | `0x4DE0` | nonstandard/list | — | 0 |
| 4 | Unused logical slot | `0` | empty | — | 0 |
| 5 | Unused logical slot | `0` | empty | — | 0 |
| 6 | Non-pickup/unknown resource | `0x1088` | nonstandard/list | — | 0 |
| 7 | Unused logical slot | `0` | empty | — | 0 |
| 8 | Non-pickup/unknown resource | `0x46FC` | nonstandard/list | — | 0 |
| 9 | Unused logical slot | `0` | empty | — | 0 |
| 10 | Non-pickup/unknown resource | `0x4F34` | nonstandard/list | — | 0 |
| 11 | Non-pickup/unknown resource | `0x19BC` | external-resource-id-bundle | 10 | 0 |
| 12 | Non-pickup/unknown resource | `0x19EC` | nonstandard/list | — | 0 |
| 13 | Extra-life urn | `0x1BCC` | embedded-data-bundle | 8 | 5 |
| 14 | Herbs | `0x22F0` | embedded-data-bundle | 8 | 7 |
| 15 | Mana pickup | `0x2C00` | embedded-data-bundle | 8 | 2 |
| 16 | Non-pickup/unknown resource | `0x3C3C` | embedded-data-bundle | 8 | 0 |
| 17 | Non-pickup/unknown resource | `0x54` | external-resource-id-bundle | 10 | 0 |
| 18 | Eye | `0x14C` | external-resource-id-bundle | 8 | 1 |
| 19 | Shield | `0x214` | external-resource-id-bundle | 8 | 1 |
| 20 | Formula | `0x2DC` | external-resource-id-bundle | 8 | 1 |

Empty slots `4,5,7,9` are logical selector capacity only. They do not prove free physical storage.

## Earth key bundle records

The three ordinary Earth keys are normal **8-frame embedded Type-4 bundles** in file `0x30`. This is the format used by the successful cross-stage v38 proof.

| Slot | Frame | Record | Embedded image | End | Dimensions words |
|---:|---:|---:|---:|---:|---|
| 0 | 0 | `0x41C` | `0x61C` | `0x66B` | `0x00060010` / `0x00020007` |
| 0 | 1 | `0x430` | `0x66C` | `0x6BD` | `0x00090010` / `0x00040007` |
| 0 | 2 | `0x444` | `0x6C0` | `0x717` | `0x000B000E` / `0x00050006` |
| 0 | 3 | `0x458` | `0x718` | `0x78B` | `0x000D000E` / `0x00060006` |
| 0 | 4 | `0x46C` | `0x78C` | `0x7F5` | `0x000E000E` / `0x00060006` |
| 0 | 5 | `0x480` | `0x7F8` | `0x871` | `0x000E000E` / `0x00060006` |
| 0 | 6 | `0x494` | `0x874` | `0x8E0` | `0x000B000E` / `0x00040006` |
| 0 | 7 | `0x4A8` | `0x8E0` | `0x942` | `0x00080010` / `0x00030007` |
| 1 | 0 | `0x4BC` | `0x944` | `0x98D` | `0x0006000C` / `0x00020005` |
| 1 | 1 | `0x4D0` | `0x990` | `0x9FA` | `0x000B000C` / `0x00050005` |
| 1 | 2 | `0x4E4` | `0x9FC` | `0xA7D` | `0x000E000C` / `0x00060005` |
| 1 | 3 | `0x4F8` | `0xA80` | `0xAFF` | `0x0011000B` / `0x00080005` |
| 1 | 4 | `0x50C` | `0xB00` | `0xB79` | `0x0012000A` / `0x00080004` |
| 1 | 5 | `0x520` | `0xB7C` | `0xC03` | `0x0010000B` / `0x00070005` |
| 1 | 6 | `0x534` | `0xC04` | `0xC89` | `0x000E000C` / `0x00060005` |
| 1 | 7 | `0x548` | `0xC8C` | `0xCFF` | `0x000B000C` / `0x00040005` |
| 2 | 0 | `0x55C` | `0xD00` | `0xD53` | `0x0006000F` / `0x00020007` |
| 2 | 1 | `0x570` | `0xD54` | `0xDB7` | `0x000A000F` / `0x00040007` |
| 2 | 2 | `0x584` | `0xDB8` | `0xE25` | `0x000D000F` / `0x00060007` |
| 2 | 3 | `0x598` | `0xE28` | `0xE9C` | `0x0010000F` / `0x00070007` |
| 2 | 4 | `0x5AC` | `0xE9C` | `0xF0C` | `0x0010000F` / `0x00070007` |
| 2 | 5 | `0x5C0` | `0xF0C` | `0xF8E` | `0x0010000F` / `0x00070007` |
| 2 | 6 | `0x5D4` | `0xF90` | `0x100A` | `0x000D000F` / `0x00050007` |
| 2 | 7 | `0x5E8` | `0x100C` | `0x1088` | `0x000A000F` / `0x00040007` |

All 24 key images have native image type `4`. The v34-v37 Type-5/monk interpretation is superseded because those proofs read selectors `0..2` from the wrong global file (`0x88`).

## Earth-specific notes, constraints, and current conclusion

- All 20 ordinary `0x30`-byte pickup records remain correct and contiguous at the existing overlay addresses.
- Earth progression metadata remains stage-local: Four Squares requires Square; Triangle requires Four Squares; later location requirements remain as listed in the ordinary-pickup table.
- **Checkpoint/progression static split (2026-09-29):** native callback `0x802F52B0` creates pickup-time checkpoint state only for parameter `0` / Earth Square: direct `0x80062D60` request at ROM `0xE1034` and selector-2 store at `0xE1044`. Parameters `1/2` instead update live overlay state `0x802F5520` / `0x802F5E22`, both independently read elsewhere and therefore preserved. Permanent item-use handlers `0x800720F0 / 0x8007213C / 0x80072188` commit progression bits separately. Minimal Square-only checkpoint candidate NOPs `0xE1034` and `0xE1044`. Static-confirmed; runtime Pending.
- **Earth selector/location ownership closure (2026-10-01, Static-confirmed):** Earth raw overlay file `0x9C` (ROM `[0xD8B90,0xE1B80)`, runtime base `0x802ECE30`) has direct absolute selector writers for `2`, `3`, `5`, `6`, and `8`. Selector `2` is the Square pickup callback store at ROM `0xE1044`; selector `3` is committed by a later Earth progression sequence after `0x802C0D54 & 0x01`; selector `5` is a separate physical/scripted checkpoint event; selector `6` is committed by a later progression sequence after `0x802C0D54 & 0x02` and its stock path already skips the write when current selector is `>=6`; selector `8` belongs to a later Earth set-piece completion path. Selector `4` is established by a separate Earth scripted transition/process and is recognized explicitly on re-entry. Selector `7` is owned by permanent routine `0x8003B004`, which first requires native stage `3` and current selector exactly `6` before writing `7` and spawning the checkpoint process. Direct Earth readers also test selector ranges such as `<3`, `<4`, `==4`, `<5`, `<6`, `<7`, and `>=7`, confirming `0x802C18F8` is live Earth world/scene state rather than a respawn-only value.
- **Accepted Earth destination-wrapper rule (2026-10-01):** logical Earth Square / Four Squares / Triangle rewards are checkpoint-free. Of the three ordinary Earth key locations, only the stock Square physical location directly owns a checkpoint selector transition. Under randomization that location retains destination-owned checkpoint target `2`, but the wrapper must be **monotonic**: if current Earth selector is below `2`, commit absolute selector `2` and request checkpoint presentation; if current selector is already `2` or later, award the randomized logical reward but do not lower the selector or replay the checkpoint. Four Squares and Triangle do not own `0x802C18F8` transitions; their Earth-local state writes remain destination-owned. Do not generalize `max(current,target)` to native scripted selectors `3..8`, which retain their stock prerequisites/order guards. **Runtime update (2026-10-01):** TEST LAB remaining-key no-checkpoint v01 Runtime-confirms checkpoint-free logical awards for Square / Four Squares / Triangle with correct inventory identity. The product rule is closed: Earth key pickup itself must not create a checkpoint. The live local states `0x802F5520` / `0x802F5E22` remain destination/progression state and must be preserved separately where required.
- The ordinary pickup visual selector is resolved against file `0x30` through the current-stage resource pointer at `0x802E82B8`.
- File `0x88` remains valid Earth-stage evidence for MONK1/enemy work only; it is **not** the pickup visual catalog.
- v34-v36 Mission Objective hangs and v37 monk/glitched imagery are now explained by the wrong donor file. They are retained as negative controls, not as evidence that Earth keys use an exotic pickup format.
- **Runtime-confirmed, v38:** all three real Earth key visuals imported into TEST LAB through the destination-native Fire resource architecture, displayed correctly, retained their native animation, and the tested Earth key award appeared correctly in inventory. The native Herbs control remained correct.
- **Difficulty-gated wall-spike result (2026-10-05): Runtime-confirmed bounded.** In the inventory-HUD proof line, the photographed horizontal climbing-wall spikes were inactive at difficulty value `2`; an otherwise identical control changing only ROM `0x000A6BA8` from `0002` to `0004` made them active. Static trace at Earth VA `0x802F078C` contains a difficulty-dependent path that terminates its current process through `0x80028564` when the copied difficulty is below `3`. This supports a native difficulty gate, but the exact process identity is not promoted to a universal "all Earth hazards" rule and difficulty `3` was not separately runtime-tested.
- Earth is therefore closed as a cross-stage ordinary-item visual donor family at the bounded v38 scope. The next global-materializer gates are generalized checkpoint-safe award semantics, composed foreign-key masking, Fortress destination stress/capacity, and production allocation/composition.

## Related owners

- [Stage catalogs](Stage-Catalogs) — shared schema, notation, safety rules, and eight-stage index.
- [Data structures and encodings](Data-Structures-and-Encodings) — ordinary `0x30`-byte record grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file-table, loader, overlay, and selector/resource grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and lifecycle.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded patch sites.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior and modeled Earth dependencies.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — generalized cross-stage materializer/solver rules, not Earth-local resource claims.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and stage-transition lifecycle.
