# ROM, overlay, and resource map

## Global file mechanism

The global file table begins at ROM `0x000A5010` / VA `0x800A4410`. Entries are 12 bytes. Production claims file ID `0x1B` at ROM `0x000A5154` for the MKMSZR native payload, stored at ROM `0x00F10000`. The raw loader at `0x80065D64` is synchronous in the proven bootstrap path.

## Title-menu global resource

Global file ID `0x5E` owns the normal title-screen image package. Clean USA Rev. 0 stores it compressed at ROM `0x4E3060..0x51243F` (end-exclusive `0x512440`), with decoded size `0x61494`.

The accepted MKMSZR Candidate-B art modifies the six CI8 tile pixel regions and the corrected production patch also rasterizes the configurable uppercase edition line into that same image. The package is recompressed losslessly and relocated from ROM `0xF90000` within a guarded `0x31000`-byte allocation ending at `0xFC0FFF`. The final compressed end varies with the configured name: the runtime-confirmed `SUB-ZERO` proof ends at `0xFC017F` (exclusive) and the runtime-confirmed `SEKTOR` proof ends at `0xFC014F` (exclusive). No title executable cave is used.

The title palette descriptor is at ROM `0xB3360`; its count word is followed by the actual 256-entry palette at `0xB3364`. Offline reconstruction uses the verified BGR555 interpretation.

## Main stage resource files

| Stage | ID | File-table entry ROM | Resource ROM range | Size | Verified runtime base | Slots | Pickups |
|---|---:|---:|---:|---:|---:|---:|---:|
| Temple | `0` | `0xA5490` | `0x513710..0x52336F` | `0xFC60` | `0x80226E28` | 17 | 4 |
| Wind | `1` | `0xA561C` | `0x698680..0x69A81F` | `0x21A0` | `0x80264FC8` | 12 | 6 |
| Water | `2` | `0xA558C` | `0x611780..0x617C5F` | `0x64E0` | `0x802504A8` | 29 | 9 |
| Earth | `3` | `0xA5670` | `0x6BAEC0..0x6DD46F` | `0x225B0` | `0x802434B8` | 65 | 20 |
| Prison | `4` | `0xA537C` | `0x41C680..0x420F6F` | `0x48F0` | `0x801FB798` | 12 | 10 |
| Fire | `5` | `0xA52E0` | `0x388260..0x38A78F` | `0x2530` | `0x80224C88` | 27 | 16 |
| Bridge | `8` | `0xA51E4` | `0x296140..0x29A46F` | `0x4330` | `0x80243000` | 25 | 10 |
| Fortress | `9` | `0xA5334` | `0x3B9700..0x3BCD1F` | `0x3620` | `0x801F4E20` | 7 | 9 |

Every slot, pickup record, and recognized embedded/external resource record is reproduced under [Stage catalogs](Stage-Catalogs).

## Resource-table rules

The first words of a stage resource file form a stage-local outer selector table. A pickup's `+0x24` word indexes this table; it is not a global resource ID. Occupied entries can point to embedded-data bundles, external-resource-ID bundles, zero-terminated lists, aliases, or still-unresolved valid structures.

A zero entry gives selector capacity only. It does not reserve or reveal physical bytes in the file. Safe foreign import requires storage with explicit bounds, relocation/expansion or other proven ownership, updated file-table size/location, descriptor integrity, arena headroom, and runtime validation.

## Proven Fire expansion

The foreign Prison-key pickup proof relocated Fire's `0x2530`-byte file to ROM `0x00F00000`, expanded it through `0x00F02BE7` (`0x2BE8` bytes), made logical slot 5 point to an appended descriptor at file offset `0x2530`, stored resource records at `0x2558..0x25F7`, and appended data through `0x2BE7`. A dedicated callback at VA `0x8008EAEC` / ROM `0x0008F6EC` awarded inventory ID `0x1A`. This proves the architecture; those exact locations now overlap production cave planning and are not a reusable allocation promise.

## Overlay identity warning

Stage-overlay function identities include the loaded stage and source artifact as well as the VA. Different overlays occupy the same address region; an address observed in one stage does not establish a globally resident function. The stage-overlay base is documented in [Runtime and memory map](Runtime-and-Memory-Map).


## Global-randomizer exact visual materialization

> **Migration note:** [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) is now the canonical owner for the cross-stage planner, extension-selector/materialization proof history, deterministic global retries, and solver. This resource page intentionally retains its current detailed duplication until **Audit Task 6**, which will refocus it on file/overlay/resource grammar.

For 1.0, cross-stage randomization requires the placed pickup to use the randomized item's real graphics/resource identity.

The runtime-confirmed foreign Prison-key import establishes the required architecture: relocate/expand the destination stage resource file when necessary, append or deduplicate the source item's resource bundle, assign a destination-local selector, update file-table bounds/location, and patch the destination pickup to reference that selector together with the correct presentation/award semantics.

Keeping a destination pickup's old graphics while changing only its logical reward is **Rejected for 1.0**. Resource importing/remapping is core randomizer infrastructure, not optional presentation polish.

Stages with no free logical selector capacity, especially Fortress and Prison, therefore remain genuine planner cases. Their materialization policy must either create selector capacity safely, prove a reusable equivalent resident resource, or use another production-safe lookup design.


## Static-confirmed ordinary-pickup selector lookup

The exact ordinary-pickup construction path is now decoded.

At pickup manager `0x80038ACC`, for each uncollected ordinary record:

```text
0x80038BE4  lw   v0, +0x24(s0)      ; selector from pickup record
0x80038BE8  lui  a2, 0x802F
0x80038BEC  lw   a2, 0x82B8(a2)     ; current stage resource-file base
0x80038BF8  sll  v0, v0, 2
0x80038BFC  addu s1, a2, v0         ; entry_ptr = base + selector*4
0x80038C00  jal  0x800281A0
0x80038C04  move a0, s1
```

`0x800281A0` then performs:

```text
lw   a0, 0(s3)       ; relative descriptor offset from selected entry
...
jal  0x80028128
addu a0, a0, s2      ; direct descriptor pointer = base + relative offset
```

Later in the same pickup-manager iteration, the selected entry is read again and resolved as `base + *entry_ptr` before actor setup continues.

**No selector-count or stock-table-size check exists on this path.** The selector is used directly as a 32-bit word index from the stage resource-file base.

This creates a promising extension mechanism without patching the lookup code: relocate/expand a stage resource file, append one or more new selector words at an aligned file offset, and encode `pickup +0x24 = appended_entry_offset / 4`. The stock lookup will address that appended word directly. The appended entry can then point to an appended foreign descriptor/resource bundle.

This is **Runtime-confirmed** through disposable Proof D. Prison's resource file was relocated/expanded by four bytes, an appended selector entry at file offset `0x48F0` pointed back to the stock Herbs descriptor `0x255C`, and all six Herbs records used selector `0x123C` (`0x48F0 / 4`). Two early Herbs were manually collected and were visually/functionally indistinguishable from vanilla, including normal inventory behavior.

Disposable Proof F then confirmed the mechanism with a real foreign embedded resource. Prison's stock selectors `0..11` remained unchanged; an extension entry at `+0x48F0` used selector `0x123C` and pointed to an appended/rebased copy of Water's embedded Potion descriptor/records/model data. Only one early Prison Herbs location was changed to that Potion identity. Runtime testing showed the imported Potion rendered cleanly and awarded Potion, while another untouched Prison Herbs still rendered/awarded normally and both appeared correctly in inventory. This is **Runtime-confirmed coexistence of vanilla stage resources with an appended foreign embedded-data bundle**.

The current stage resource-file base is held at `0x802F82B8` on this path. Stage-loading code writes allocator/loader results there before the resource file is consumed.


## External-resource IDs and embedded-image conversion

**Static-confirmed, 2026-09-20.**

The stage resource record format supports two materially different storage forms:

- embedded: record `+0x04 = 0`, record `+0x08 = stage-file-relative compressed-image offset`;
- external-resource ID: record `+0x04 = cache resource ID`, record `+0x08 = 0`.

Water/Fire/Bridge Health urn records use external IDs `0x28F..0x292`. Disposable Proof G copied Water's Health descriptor/records into Prison through the already-confirmed extension selector but left those IDs external. Runtime result: the Health urn rendered corrupted. Therefore the numeric external IDs are not self-sufficient in Prison; their cache dependencies are stage/package dependent.

The raw image payloads behind `0x28F..0x292` were statically extracted from Water's compressed package file ID `0x73`. Their raw byte lengths are `340, 272, 272, 272`. Fire and Bridge contain matching Health-urn image payloads for the same IDs.

The native embedded-image path calls `0x8000322C`. Compression type 4 dispatches to `0x80003428`, which uses a 1024-byte ring buffer and separate MSB-first control/token streams. Correcting the back-reference loop to the native inclusive count `(low6 + 2)` reproduces every Water embedded Potion frame byte-for-byte against the corresponding Fire external Potion payload IDs `0x27F..0x286`.

This establishes a conversion path: an external raw image payload can be encoded as a self-contained type-4 block and referenced through the normal embedded record form. A deterministic literal-only type-4 encoder was round-trip checked against all four Health-urn payloads. Disposable Proof H then applied exactly that conversion to one Health urn imported into Prison through extension selector `0x123C`. Runtime testing showed a clean Urn of Vitality that awarded correctly, while an untouched vanilla Herbs pickup in the same stage also remained correct. Therefore the external-to-embedded conversion is **Runtime-confirmed** for this ordinary-item family.


## Composed extension-selector stress validation

The pipeline-disconnected cross-stage planner now supports deterministic deduplicated extension-selector tables and self-contained imported visual bundles. A disposable stress ROM applied five distinct imported visuals simultaneously to each of Prison and Fortress: Potion, Urn of Vitality, Formula, Eye, and Shield, while leaving a sixth Herbs pickup on its original stock selector.

For Prison, the stock resource file expanded from `0x48F0` to `0x7CB4`; five extension selectors occupied file-relative words beginning at `0x48F0`, yielding selectors `0x123C..0x1240`. Manual runtime testing confirmed all five imported models and awards, plus the untouched Herbs control. This is **Runtime-confirmed** composed multi-bundle coexistence in Prison.

The Fortress half of the same proof is still **Pending** runtime validation. Its presence in the ROM and static construction must not be described as runtime-confirmed until manually tested.
