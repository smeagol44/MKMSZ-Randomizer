# Memory and allocation map

> **Scope:** This page is the canonical owner for **continuous literal-space ownership** in the supported 16 MiB MKMSZ USA Rev. 0 ROM and its physical 4 MiB RDRAM. It records exact bounded intervals, aliases, lifecycle, ownership, evidence, production safety, and known conflicts.
>
> It does **not** replace the [patch-site registry](Address-and-Patch-Site-Registry) for individual guarded edits, the [function registry](Function-Registry) for function semantics, the [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) for loader/resource grammar, or the separate decomp-readiness view. Unknown space remains unknown.

The supported clean input is the 16 MiB big-endian USA Rev. 0 ROM, SHA-256 <code>9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6</code>.

## Coordinate conventions

All bounded intervals on this page are **end-exclusive**: <code>[start, end_exclusive)</code>. Size is therefore <code>end_exclusive - start</code>.

### ROM

- Canonical ROM space is <code>0x00000000..0x01000000</code> (16 MiB).
- A ROM offset is never silently treated as a runtime VA.
- File-relative, overlay-relative, decoded-resource, and proof-artifact offsets are different coordinate spaces and must be labeled as such.
- A ROM↔VA relationship is displayed only where that mapping is established for that specific global segment or object.

### RDRAM and aliases

Canonical RDRAM records use **physical** addresses <code>0x000000..0x400000</code> (4 MiB).

For a physical address <code>P</code> in that range:

- cached KSEG0 alias = <code>0x80000000 + P</code>;
- uncached KSEG1 alias = <code>0xA0000000 + P</code>.

KSEG0 and KSEG1 are two views of the **same physical bytes**. They are not two allocations and must never be counted twice.

A stage-overlay VA is not globally unique ownership. Overlay records must include the loaded stage/source identity because the same VA can hold mutually exclusive stage content.

## Classification legend

| Class | Meaning |
|---|---|
| <code>stock-known</code> | Bounded stock code/data/resource ownership is established. It is protected unless deliberately patched. |
| <code>stock-unknown</code> | A bounded stock region is known to exist but ownership/meaning is not sufficiently decoded. Protected, not free. |
| <code>production</code> | Current MKMSZR browser/CLI composition owns the interval. |
| <code>confirmed-free</code> | Reference/lifecycle evidence establishes that the exact interval is reusable for the stated lifecycle. |
| <code>candidate-free</code> | Incomplete reference/lifecycle evidence suggests possible reuse. **Not production-safe.** |
| <code>dynamic</code> | Allocator/loader-owned runtime space; a fixed reusable interval is not implied. |
| <code>proof-only</code> | A disposable proof used the interval. This never establishes current production ownership or free space. |
| <code>rejected/conflict</code> | A tested or analyzed use conflicts with live stock data or current production ownership. |
| <code>alias/view</code> | A displayed coordinate alias only; never an independent allocation row. |

**No current interval is promoted to reusable <code>confirmed-free</code> status in this first map.** Several places that were historically described as free tails/caves are now production-owned or were disproven. That is intentional.

The following are never sufficient evidence for <code>confirmed-free</code>:

- bytes read as <code>00</code>;
- bytes read as <code>FF</code>;
- one proof ROM happened to work there;
- one stage overlay did not use the address;
- a proof file was able to extend into a ROM tail.

## Canonical interval-record schema

Every future structured record must preserve these fields one-to-one.

| Field | Required meaning |
|---|---|
| <code>region_id</code> | Stable identifier. Renaming requires an explicit migration. |
| <code>space</code> | <code>rom</code>, <code>rdram-physical</code>, <code>overlay-rom</code>, <code>file-relative</code>, or <code>decoded-resource</code>. |
| <code>start</code> | Inclusive start in the declared coordinate space. |
| <code>end_exclusive</code> | Exclusive end in the same space. |
| <code>display_aliases</code> | Proven alternate views such as KSEG0/KSEG1 or a specific ROM/VA mapping. Never a second allocation. |
| <code>class</code> | One classification from the legend above. |
| <code>owner</code> | Stock subsystem, MKMSZR feature/module, file, or proof artifact that owns the bytes. |
| <code>scope</code> | Global, frontend, gameplay, stage/overlay identity, proof ROM, generated output, etc. |
| <code>lifecycle</code> | When the ownership or availability statement is valid. |
| <code>evidence</code> | Project evidence label plus the bounded route/limit when relevant. |
| <code>production_safe</code> | <code>yes</code>, <code>no</code>, or <code>conditional</code> **for the documented owner/use**. <code>yes</code> never means free for another owner. |
| <code>guard_or_reference</code> | Expected-byte guard, file-table entry, allocator trace, source constant/test, or reference analysis. |
| <code>conflicts_with</code> | Other <code>region_id</code> values or named proof uses that cannot coexist. |
| <code>canonical_source</code> | This page for continuous interval ownership; supporting domain/code references go in <code>guard_or_reference</code>. |
| <code>notes</code> | Only caveats needed to interpret the record safely. |

## Lifecycle and scope rules

1. **Production ownership is compositional.** A range proven in isolation does not become production-safe until it composes with the current pipeline.
2. **Availability is lifecycle-qualified.** Frontend-only, stage-init, gameplay, transition, and stage-specific observations do not automatically transfer to one another.
3. **Overlay identity is mandatory.** A stage-overlay VA without stage/source identity is incomplete evidence.
4. **Dynamic allocation is not a cave.** A known arena base, allocator result, high-water mark, or allocation size does not imply that the surrounding address space is reusable.
5. **Proof scope is artifact-specific.** Two proof ROMs may intentionally use overlapping ROM offsets because they are mutually exclusive artifacts; neither becomes a production allocation.
6. **Production-reserved tails remain owned.** Unfilled capacity inside a production reservation is not <code>confirmed-free</code>.
7. **Exact patch sites stay in the patch registry.** This page records continuous ownership ranges; isolated hooks/words are linked rather than copied into a second patch-site database.

## ROM ownership and allocation

The table below records only bounded intervals supported by current evidence. It is **not** a partition of the ROM.

<code>production_safe=yes</code> means the current documented owner is accepted in the current composition. It does not authorize reuse by another feature.

| <code>region_id</code> | <code>[start, end_exclusive)</code> | Class | Owner | Scope | Lifecycle | Evidence | Production safe | Guard / reference | Conflicts / notes |
|---|---:|---|---|---|---|---|---|---|---|
| <code>rom.production.inventory_action_cave</code> | <code>[0x0008F6E8, 0x0008F750)</code> | <code>production</code> | Four-box action routine | Global code | Gameplay | Runtime-confirmed behavior; Implementation/CI-confirmed bounds | yes | <code>inventory_boxes.py</code>; [Patch-site registry](Address-and-Patch-Site-Registry) | Historical Prison-key callback entered at <code>0x8F6EC</code>; proof body is not a reusable allocation. |
| <code>rom.production.inventory_helper_cave</code> | <code>[0x0009A6C8, 0x0009A758)</code> | <code>production</code> | Four-box switch/mask helper composition | Global code | Gameplay / transition | Runtime-confirmed behavior; Implementation/CI-confirmed <code>0x90</code> reservation | yes | <code>inventory_boxes.py</code>; tests assert <code>SELECTOR_CAVE_SIZE == 0x90</code> | Toasty visual v06 used <code>[0x9A720,0x9A754)</code> and is rejected for that route; this tail is now production-owned. |
| <code>rom.production.bootstrap_composite</code> | <code>[0x0009AD84, 0x0009AF20)</code> | <code>production</code> | Native bootstrap + pickup persistence + relocated selector/flow data | Global code/data | Stage init / gameplay | Runtime-confirmed composition; Implementation/CI-confirmed capacity <code>0x19C</code> | yes | <code>native_payload.py</code>, <code>pickup_persistence.py</code>, <code>inventory_boxes.py</code>, <code>flow_bypass.py</code> | Conflicts with rejected title wrapper at <code>0x9ADE0</code> and Sektor v62 proof record <code>[0x9AD90,0x9ADA0)</code>. Final four bytes are reserved capacity, not free. |
| <code>rom.stock.false_zero_cave</code> | <code>[0x000A1308, 0x000A1544)</code> | <code>stock-known</code> | Stock action/dispatch record area | Global stock data | Gameplay/input dispatch | Static-confirmed; Runtime-confirmed failure/correction in Sektor v08 | no | [Core runtime](Core-Runtime-and-Address-Database); [MKT compatibility](MKT-to-MKMSZ-Compatibility-Layer) | **Required negative example:** zero-filled semantic records were mistaken for a cave; overwriting them caused input-specific hangs. |
| <code>rom.production.file_entry_1b</code> | <code>[0x000A5154, 0x000A5160)</code> | <code>production</code> | Global file-table entry <code>0x1B</code> | Global file table | Stage init | Runtime-confirmed load/execute; Implementation/CI-confirmed guard | yes | <code>addresses.py</code>, <code>native_payload.py</code> | Points to current payload source <code>[0xF10000,0xF10300)</code>. |
| <code>rom.production.file_entry_5e</code> | <code>[0x000A5478, 0x000A5484)</code> | <code>production</code> | Global file-table entry <code>0x5E</code> | Global file table | Frontend/title | Runtime-confirmed title route; Implementation/CI-confirmed guard | yes | <code>title_branding.py</code>; [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | Repoints title package to high-ROM allocation. |
| <code>rom.production.key_stage_table</code> | <code>[0x000A6BE4, 0x000A6C0C)</code> | <code>production</code> | Four-box key-to-stage map | Global data | Gameplay / transition | Runtime-confirmed masking behavior; Implementation/CI-confirmed 40-byte table | yes | <code>inventory_boxes.py</code> | Reuses the obsolete stock default-inventory template after loader replacement. |
| <code>rom.production.live_inventory_initializer</code> | <code>[0x000A6C0C, 0x000A6C34)</code> | <code>production</code> | Ten-word live-inventory initializer | Global data | Run init / inventory | Runtime-confirmed four-box system; Implementation/CI-confirmed 40 bytes | yes | <code>inventory_boxes.py</code> | Runtime authoritative live window is mapped separately in RDRAM. |
| <code>rom.production.four_box_data</code> | <code>[0x000A6C48, 0x000A6CF0)</code> | <code>production</code> | Four backing boxes + state + <code>MKBX</code> magic | Global data | Run init / gameplay / transition | Runtime-confirmed boxes; Implementation/CI-confirmed <code>0xA8</code> bytes | yes | <code>inventory_boxes.py</code>; tests assert exact size | Gap <code>[0xA6C34,0xA6C48)</code> is deliberately **unknown**, not absorbed into this owner. |
| <code>rom.stock.xp_cap_table</code> | <code>[0x000A6FFC, 0x000A7010)</code> | <code>stock-known</code> | Signed XP-cap halfword table | Global data | Gameplay | Static-confirmed table; current main-stage edits Implementation/CI-confirmed | conditional | <code>addresses.py</code>, <code>xp_progression.py</code> | Current production changes only native stage IDs <code>0,1,2,3,4,5,8,9</code>; the bounded stock table remains protected as a whole. |
| <code>rom.production.boot_branding_text</code> | <code>[0x000AF998, 0x000AFA24)</code> | <code>production</code> | MKMSZR legal/boot branding strings | Frontend | Boot/legal screen | Runtime-confirmed | yes | <code>boot_branding.py</code> exact bounds and guards | Adjacent to, but distinct from, HUD wrapper allocation. |
| <code>rom.production.box_indicator</code> | <code>[0x000AFA24, 0x000AFA98)</code> | <code>production</code> | Native <code>BOX n OF 4</code> wrapper + text | Global code/data | Gameplay HUD | Runtime-confirmed | yes | <code>box_indicator.py</code> exact <code>0x74</code>-byte region | Entire region is owned even where emitted bytes are zero padding. |
| <code>rom.production.license_text</code> | <code>[0x000AFA98, 0x000AFABC)</code> | <code>production</code> | MKMSZR license line | Frontend | Boot/legal screen | Runtime-confirmed | yes | <code>boot_branding.py</code> exact bounds and guard | Do not merge trailing bytes outside <code>0xAFABC</code> without evidence. |
| <code>rom.stock.stage_resource.bridge</code> | <code>[0x00296140, 0x0029A470)</code> | <code>stock-known</code> | Bridge stage resource file | Stage 8 resource | Bridge load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | Resource ownership does not make unused-looking selector/data bytes free. |
| <code>rom.stock.stage_resource.fire</code> | <code>[0x00388260, 0x0038A790)</code> | <code>stock-known</code> | Fire stage resource file | Stage 5 resource | Fire load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | A separate disposable proof relocation exists below. |
| <code>rom.stock.stage_resource.fortress</code> | <code>[0x003B9700, 0x003BCD20)</code> | <code>stock-known</code> | Fortress stage resource file | Stage 9 resource | Fortress load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | No gap/capacity inference is made. |
| <code>rom.stock.stage_resource.prison</code> | <code>[0x0041C680, 0x00420F70)</code> | <code>stock-known</code> | Prison stage resource file | Stage 4 resource | Prison load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | Extension-selector proofs relocate/expand a copy; stock bytes remain protected. |
| <code>rom.stock.file_5e_title</code> | <code>[0x004E3060, 0x00512440)</code> | <code>stock-known</code> | Stock compressed title package, file <code>0x5E</code> | Frontend/title resource | Title load | Static-confirmed | no | <code>title_branding.py</code>; [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | Current production retains this stock source but repoints the live file entry to high ROM. Retained bytes are not declared free. |
| <code>rom.stock.stage_resource.temple</code> | <code>[0x00513710, 0x00523370)</code> | <code>stock-known</code> | Temple stage resource file | Stage 0 resource | Temple load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | No gap/capacity inference is made. |
| <code>rom.stock.stage_resource.water</code> | <code>[0x00611780, 0x00617C60)</code> | <code>stock-known</code> | Water stage resource file | Stage 2 resource | Water load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | No gap/capacity inference is made. |
| <code>rom.stock.stage_resource.wind</code> | <code>[0x00698680, 0x0069A820)</code> | <code>stock-known</code> | Wind stage resource file | Stage 1 resource | Wind load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | No gap/capacity inference is made. |
| <code>rom.stock.stage_resource.earth</code> | <code>[0x006BAEC0, 0x006DD470)</code> | <code>stock-known</code> | Earth stage resource file | Stage 3 resource | Earth load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | No gap/capacity inference is made. |
| <code>rom.stock.file_87_subzero</code> | <code>[0x00748920, 0x0078E300)</code> | <code>stock-known</code> | Stock Sub-Zero fighter resource, file <code>0x87</code> | Global fighter resource | Gameplay | Static-confirmed; repeatedly used as donor-proof baseline | no | [Sektor mapping](Sub-Zero-to-Sektor-Animation-Mapping) | Optional outfit recolor edits a guarded palette subset inside this owned file; that does not make other bytes free. |
| <code>rom.production.payload_source</code> | <code>[0x00F10000,0x00F103B0)</code> | <code>production</code> | MKMSZR Runtime V2 reloadable code payload | Generated ROM output | Stage init reload; runtime code | Runtime-confirmed through the rainbow full-composition proof; Implementation/CI-confirmed exactly <code>0x3B0</code> bytes | yes | <code>native_payload.py</code>, <code>runtime_v2.py</code>, <code>xp_progression.py</code>, <code>rainbow_palette.py</code> | File <code>0x1B</code> points here. Source bytes being <code>FF</code> in the clean ROM are only a guard, not the reason this ownership is accepted. |
| <code>rom.production.rainbow_file_87</code> | <code>[0x00F20000,0x00F679E0)</code> | <code>production</code> | Optional rainbow outfit relocated Sub-Zero file <code>0x87</code> plus 64-palette bank | Generated ROM output | Rainbow gameplay only | Runtime-confirmed; production output for seed <code>RAINBOW64</code> is byte-identical to proof v01 | conditional | <code>rainbow_palette.py</code>; guarded stock file entry and destination <code>FF</code> capacity | Owned only when outfit mode is <code>rainbow</code>; stock file body is copied intact before the appended <code>0x2000</code>-byte palette bank. |
| <code>rom.production.title_high</code> | <code>[0x00F90000, 0x00FC1000)</code> | <code>production</code> | Generated compressed title file <code>0x5E</code> | Generated ROM output | Frontend/title | Runtime-confirmed full production composition | yes | <code>title_branding.py</code> capacity <code>0x31000</code> | Actual compressed end is build-dependent (<code>SUB-ZERO</code>: <code>0xFC017F</code>; <code>SEKTOR</code>: <code>0xFC014F</code>). Remaining capacity stays reserved, not free. |

### Production bootstrap composite sublayout

<code>rom.production.bootstrap_composite</code> is one ownership interval but has multiple current sub-owners. These subranges are descriptive containment, not additional top-level allocations.

| ROM subrange | Current content |
|---|---|
| <code>[0x9AD84,0x9ADD8)</code> | Native loader/call stub (<code>0x54</code> bytes in current V2 composition) |
| <code>[0x9ADD8,0x9ADE8)</code> | Pickup-restore trampoline |
| <code>[0x9ADE8,0x9AEC0)</code> | Pickup-capture helper |
| <code>[0x9AEC0,0x9AEE8)</code> | Ten-entry stage descriptor table |
| <code>[0x9AEE8,0x9AEFC)</code> | Fire manager-ordinal translation table |
| <code>[0x9AEFC,0x9AF1C)</code> | Relocated compact selector mapper + selector-only save-bypass write |
| <code>[0x9AF1C,0x9AF20)</code> | Reserved tail inside the production <code>0x19C</code> bootstrap capacity; **not free** |

### Proof-only ROM footprints

These rows describe specific disposable artifacts. They do not classify the same bytes as free in the clean ROM or in current production.

| <code>region_id</code> | <code>[start, end_exclusive)</code> | Class | Owner/scope | Evidence | Production safe | Conflicts / limit |
|---|---:|---|---|---|---|---|
| <code>rom.proof.fire_resource_relocation</code> | <code>[0x00F00000,0x00F02BE8)</code> | <code>proof-only</code> | Foreign Prison-key-in-Fire resource proof | Runtime-confirmed bounded proof | no | Architecture evidence only. The location is not a production allocation promise. |
| <code>rom.proof.sektor_v62_file_87</code> | <code>[0x00F40000,0x00F8E3FC)</code> | <code>proof-only</code> | Sektor v62 relocated fighter file <code>0x87</code> | Runtime-confirmed bounded combo route | no | Does not overlap current title allocation, but larger historical Sektor proof footprints crossed into the later title-owned high-ROM area; proof-history bounds remain artifact-specific. |

### Known rejected/conflicting ROM uses

| Use | Exact known footprint | Conflict / conclusion |
|---|---|---|
| Sektor v01-v07 “zero cave” helper | <code>[0xA1308,0xA1544)</code> | **Rejected / failed.** Overwrote live stock action/dispatch records. Restoring stock bytes in v08 removed the input-specific hangs. |
| Toasty visual v06 selector-cave tail | <code>[0x9A720,0x9A754)</code> | **Rejected / failed on that route.** The interval now also lies inside <code>rom.production.inventory_helper_cave</code>. |
| Sektor v62 standalone combo continuation | <code>[0x9AD90,0x9ADA0)</code> | Runtime-valid proof semantics, but **allocation conflicts** with <code>rom.production.bootstrap_composite</code>. Must be relocated before integration. |
| Old title executable wrapper | starts at <code>0x9ADE0</code>; full historical extent is not promoted here | **Rejected / failed composition.** Its entry lies inside <code>rom.production.bootstrap_composite</code>; current title implementation is data-only. |
| Prison-key award callback proof | entry at <code>0x8F6EC</code>; full proof body is not promoted here | Runtime-confirmed proof result, but its entry lies inside <code>rom.production.inventory_action_cave</code>; not reusable without reallocation/revalidation. |

The intentionally incomplete extents above remain incomplete. A conflict can be established from a known entry point inside a current owner without inventing the rest of an old proof allocation.

## RDRAM ownership and allocation

The canonical coordinate in this table is the **physical** interval. <code>display_aliases</code> lists KSEG0/KSEG1 views of those same bytes.

| <code>region_id</code> | Physical <code>[start, end_exclusive)</code> | <code>display_aliases</code> | Class | Owner | Scope | Lifecycle | Evidence | Production safe | Guard / reference | Conflicts / notes |
|---|---:|---|---|---|---|---|---|---|---|---|
| <code>rdram.production.inventory_action_cave</code> | <code>[0x08EAE8,0x08EB50)</code> | KSEG0 <code>[0x8008EAE8,0x8008EB50)</code>; KSEG1 <code>[0xA008EAE8,0xA008EB50)</code> | <code>production</code> | Four-box action routine | Global code | Gameplay | Runtime-confirmed behavior; CI-confirmed bounds | yes | <code>inventory_boxes.py</code> | Same physical bytes as the displayed aliases; count once. |
| <code>rdram.production.inventory_helper_cave</code> | <code>[0x099AC8,0x099B58)</code> | KSEG0 <code>[0x80099AC8,0x80099B58)</code>; KSEG1 <code>[0xA0099AC8,0xA0099B58)</code> | <code>production</code> | Four-box helper composition | Global code | Gameplay / transition | Runtime-confirmed behavior; CI-confirmed bounds | yes | <code>inventory_boxes.py</code> | Historical proof tail use is not reusable. |
| <code>rdram.production.bootstrap_composite</code> | <code>[0x09A184,0x09A320)</code> | KSEG0 <code>[0x8009A184,0x8009A320)</code>; KSEG1 <code>[0xA009A184,0xA009A320)</code> | <code>production</code> | Bootstrap/persistence/selector composite | Global code/data | Stage init / gameplay | Runtime-confirmed composition; CI-confirmed <code>0x19C</code> capacity | yes | <code>native_payload.py</code>, <code>pickup_persistence.py</code>, <code>inventory_boxes.py</code> | Mirrors the current global-code ROM owner <code>rom.production.bootstrap_composite</code>; this is not a ROM=VA assumption but an established segment mapping. |
| <code>rdram.stock.false_zero_cave</code> | <code>[0x0A0708,0x0A0944)</code> | KSEG0 <code>[0x800A0708,0x800A0944)</code>; KSEG1 <code>[0xA00A0708,0xA00A0944)</code> | <code>stock-known</code> | Stock action/dispatch data | Global data | Gameplay/input dispatch | Static-confirmed; Runtime-confirmed negative control | no | [MKT compatibility](MKT-to-MKMSZ-Compatibility-Layer) | Zero-filled records are semantic live data, not padding. |
| <code>rdram.production.file_entry_1b</code> | <code>[0x0A4554,0x0A4560)</code> | KSEG0 <code>[0x800A4554,0x800A4560)</code>; KSEG1 <code>[0xA00A4554,0xA00A4560)</code> | <code>production</code> | Runtime global file-table entry <code>0x1B</code> | Global data | Stage init | Runtime-confirmed loader path | yes | Global table base <code>0x800A4410</code>, 12-byte entries | Alias of one physical table entry, not a separate allocation. |
| <code>rdram.production.file_entry_5e</code> | <code>[0x0A4878,0x0A4884)</code> | KSEG0 <code>[0x800A4878,0x800A4884)</code>; KSEG1 <code>[0xA00A4878,0xA00A4884)</code> | <code>production</code> | Runtime global file-table entry <code>0x5E</code> | Global data | Frontend/title load | Runtime-confirmed title route | yes | Global table base <code>0x800A4410</code>, 12-byte entries | Runtime table reflects the patched file descriptor. |
| <code>rdram.production.key_stage_table</code> | <code>[0x0A5FE4,0x0A600C)</code> | KSEG0 <code>[0x800A5FE4,0x800A600C)</code>; KSEG1 <code>[0xA00A5FE4,0xA00A600C)</code> | <code>production</code> | Key-to-stage map | Global data | Gameplay / transition | Runtime-confirmed masking; CI-confirmed 40 bytes | yes | <code>inventory_boxes.py</code> | Directly precedes live inventory but is a separate owner. |
| <code>rdram.production.live_inventory</code> | <code>[0x0A600C,0x0A6034)</code> | KSEG0 <code>[0x800A600C,0x800A6034)</code>; KSEG1 <code>[0xA00A600C,0xA00A6034)</code> | <code>production</code> | Native ten-slot live inventory window | Global mutable data | Gameplay / inventory | Runtime-confirmed | yes | <code>inventory_boxes.py</code>; [Persistence/inventory](Persistence-Inventory-and-Lifecycle) | Live window is not authoritative across box switching; backing boxes are. |
| <code>rdram.production.four_boxes</code> | <code>[0x0A6048,0x0A60E8)</code> | KSEG0 <code>[0x800A6048,0x800A60E8)</code>; KSEG1 <code>[0xA00A6048,0xA00A60E8)</code> | <code>production</code> | Four authoritative ten-word backing boxes | Global mutable data | Run gameplay / transitions | Runtime-confirmed | yes | <code>inventory_boxes.py</code> | Gap <code>[0x0A6034,0x0A6048)</code> remains unknown. |
| <code>rdram.production.box_state</code> | <code>[0x0A60E8,0x0A60EC)</code> | KSEG0 <code>0x800A60E8</code>; KSEG1 <code>0xA00A60E8</code> | <code>production</code> | Active-box index/latch word | Global mutable data | Run gameplay | Runtime-confirmed | yes | <code>inventory_boxes.py</code> | Bits <code>0..1</code> active index; latch includes <code>0x100</code>. |
| <code>rdram.production.box_magic</code> | <code>[0x0A60EC,0x0A60F0)</code> | KSEG0 <code>0x800A60EC</code>; KSEG1 <code>0xA00A60EC</code> | <code>production</code> | <code>MKBX</code> magic | Global mutable data | Run initialization / reconstruction | Implementation/CI-confirmed; exercised by runtime system | yes | <code>inventory_boxes.py</code> | Magic <code>0x4D4B4258</code>. |
| <code>rdram.stock.xp_cap_table</code> | <code>[0x0A63FC,0x0A6410)</code> | KSEG0 <code>[0x800A63FC,0x800A6410)</code>; KSEG1 <code>[0xA00A63FC,0xA00A6410)</code> | <code>stock-known</code> | Signed XP-cap table with production main-stage edits | Global data | Gameplay | Static-confirmed; production writes Implementation/CI-confirmed | conditional | <code>addresses.py</code>, <code>xp_progression.py</code> | Only selected halfwords are production-edited. |
| <code>rdram.production.boot_branding_text</code> | <code>[0x0AED98,0x0AEE24)</code> | KSEG0 <code>[0x800AED98,0x800AEE24)</code>; KSEG1 <code>[0xA00AED98,0xA00AEE24)</code> | <code>production</code> | MKMSZR legal/boot strings | Global data | Boot/legal screen | Runtime-confirmed | yes | <code>boot_branding.py</code> pointer targets | Established global-segment mapping; count physical bytes once. |
| <code>rdram.production.box_indicator</code> | <code>[0x0AEE24,0x0AEE98)</code> | KSEG0 <code>[0x800AEE24,0x800AEE98)</code>; KSEG1 <code>[0xA00AEE24,0xA00AEE98)</code> | <code>production</code> | Native box HUD wrapper/text | Global code/data | Gameplay HUD | Runtime-confirmed | yes | <code>box_indicator.py</code> | Exact region mirrors ROM owner. |
| <code>rdram.production.license_text</code> | <code>[0x0AEE98,0x0AEEBC)</code> | KSEG0 <code>[0x800AEE98,0x800AEEBC)</code>; KSEG1 <code>[0xA00AEE98,0xA00AEEBC)</code> | <code>production</code> | MKMSZR license string | Global data | Boot/legal screen | Runtime-confirmed | yes | <code>boot_branding.py</code> | Exact bounded string storage. |
| <code>rdram.stock.current_xp</code> | <code>[0x11200C,0x112010)</code> | KSEG0 <code>0x8011200C</code>; KSEG1 <code>0xA011200C</code> | <code>stock-known</code> | Native current-XP word used by production progression | Global mutable data | Gameplay / stage transition | Static-confirmed and Runtime-confirmed on progression routes | conditional | <code>addresses.py</code>; [XP/progression](XP-and-Progression) | Production owns behavior around the stock variable, not surrounding words. |
| <code>rdram.production.runtime_core</code> | <code>[0x1AF420,0x1AF5F4)</code> | KSEG0 <code>[0x801AF420,0x801AF5F4)</code>; KSEG1 <code>[0xA01AF420,0xA01AF5F4)</code> | <code>production</code> | Runtime V2 init + pickup-persistence code through actual <code>+0x1D4</code> core end | Reserved MKMSZR block | Reloaded at stage init; executes during init/gameplay hooks | Runtime-confirmed; exact emitted size CI-confirmed | yes | <code>runtime_v2.py</code>, <code>pickup_persistence.py</code>; actual persistence core size <code>0x1D4</code> | Subrange of the 1 KiB reservation. |
| <code>rdram.production.inventory_payload</code> | <code>[0x1AF5F4,0x1AF620)</code> | KSEG0 <code>[0x801AF5F4,0x801AF620)</code>; KSEG1 <code>[0xA01AF5F4,0xA01AF620)</code> | <code>production</code> | Four-box filtered-save helper | Reserved MKMSZR block | Gameplay / transition | Runtime-confirmed composition; CI-confirmed bounds | yes | <code>inventory_boxes.py</code> payload <code>+0x1D4..+0x200</code> | Reuses the production payload tail intentionally. |
| <code>rdram.production.xp_payload</code> | <code>[0x1AF620,0x1AF700)</code> | KSEG0 <code>[0x801AF620,0x801AF700)</code>; KSEG1 <code>[0xA01AF620,0xA01AF700)</code> | <code>production</code> | XP progression callback, threshold table, restore helper, and bounded padding | Reserved MKMSZR block | Pickup / stage transition | Runtime-confirmed Diagnostic B behavior; CI-confirmed meaningful content stays below <code>+0x2E0</code> | yes | <code>xp_progression.py</code> | The formerly zero <code>[+0x2E0,+0x300)</code> tail is intentionally released to the optional runtime-feature region below. |
| <code>rdram.production.optional_runtime_tail</code> | <code>[0x1AF700,0x1AF7D0)</code> | KSEG0 <code>[0x801AF700,0x801AF7D0)</code>; KSEG1 <code>[0xA01AF700,0xA01AF7D0)</code> | <code>production</code> | Optional Runtime V2 feature code tail | Reserved MKMSZR block | Gameplay | Runtime-confirmed by rainbow v01; CI-confirmed bounds | yes | <code>runtime_v2.py</code>, <code>rainbow_palette.py</code> | Rainbow owns <code>[0x1AF700,0x1AF7CC)</code> with its <code>0xCC</code>-byte helper; <code>[0x1AF7CC,0x1AF7D0)</code> remains reserved. In non-rainbow builds the whole interval remains reserved/zero. |
| <code>rdram.production.state_header</code> | <code>[0x1AF7D0,0x1AF7F0)</code> | KSEG0 <code>[0x801AF7D0,0x801AF7F0)</code>; KSEG1 <code>[0xA01AF7D0,0xA01AF7F0)</code> | <code>production</code> | <code>MKSV</code> V2 state header | Persistent MKMSZR state | Survives payload reload / normal stage lifecycle | Runtime-confirmed through rainbow full composition; CI-confirmed layout | yes | <code>runtime_v2.py</code> header size <code>0x20</code> | Header validates magic/version/size/header-size; total state size is <code>0x50</code>. |
| <code>rdram.production.pickup_state</code> | <code>[0x1AF7F0,0x1AF810)</code> | KSEG0 <code>[0x801AF7F0,0x801AF810)</code>; KSEG1 <code>[0xA01AF7F0,0xA01AF810)</code> | <code>production</code> | Eight stage ordinary-pickup bitset words | Persistent MKMSZR state | Run lifecycle until reset boundary | Runtime-confirmed representative persistence in all eight stages and in the rainbow full composition | yes | <code>pickup_persistence.py</code> descriptors use state offsets <code>+0x20..+0x3C</code> | Scripted/special mechanisms are outside these bitsets. |
| <code>rdram.production.xp_state</code> | <code>[0x1AF810,0x1AF818)</code> | KSEG0 <code>[0x801AF810,0x801AF818)</code>; KSEG1 <code>[0xA01AF810,0xA01AF818)</code> | <code>production</code> | Progression acquired-count + persistent-XP words | Persistent MKMSZR state | Run lifecycle / stage transition | Runtime-confirmed on bounded Diagnostic B routes and rainbow full composition | yes | <code>xp_progression.py</code> state <code>+0x40/+0x44</code> | Full nine-tier run remains a validation limit, not an allocation ambiguity. |
| <code>rdram.production.rainbow_phase</code> | <code>[0x1AF818,0x1AF81C)</code> | KSEG0 <code>0x801AF818</code>; KSEG1 <code>0xA01AF818</code> | <code>production</code> | Optional rainbow phase word | Persistent MKMSZR state | Rainbow gameplay | Runtime-confirmed in full-composition v01 | conditional | <code>rainbow_palette.py</code> state offset <code>+0x48</code> | Used only in <code>rainbow</code> mode; initialized by the common V2 state initializer. |
| <code>rdram.production.state_reserved_tail</code> | <code>[0x1AF81C,0x1AF820)</code> | KSEG0 <code>[0x801AF81C,0x801AF820)</code>; KSEG1 <code>[0xA01AF81C,0xA01AF820)</code> | <code>production</code> | Reserved final word of the versioned V2 state reservation | Persistent MKMSZR state | Run lifecycle | Implementation/CI-confirmed reservation boundary | yes | <code>runtime_v2.py</code> owns full state <code>[0x1AF7D0,0x1AF820)</code> | **Reserved, not free.** |
| <code>rdram.stock.pickup_context_pointer</code> | <code>[0x2ECE20,0x2ECE24)</code> | KSEG0 <code>0x802ECE20</code>; KSEG1 <code>0xA02ECE20</code> | <code>stock-known</code> | Live pickup-manager process/context pointer slot | Stage runtime | Stage manager construction/gameplay | Static-confirmed; runtime use confirmed by persistence | conditional | <code>addresses.py</code>, <code>pickup_persistence.py</code> | Corrects superseded <code>0x802FCE20</code>; surrounding overlay/runtime space is not inferred from this word. |

### The 1 KiB reservation and arena boundary

The production reservation is exactly physical <code>[0x1AF420,0x1AF820)</code>, KSEG0 <code>[0x801AF420,0x801AF820)</code>, KSEG1 <code>[0xA01AF420,0xA01AF820)</code>. It is fully accounted for above as V2 code/state sub-owners.

The game originally constructed its main arena at KSEG0 <code>0x801AF420</code>. Production changes both guarded construction sites at ROM <code>0x66F64</code> and <code>0x66FE8</code> so the arena begins at KSEG0 <code>0x801AF820</code> instead. <code>0x801AF820</code> is an **anchor**, not a claim that every later byte through the top of RDRAM is one reusable interval.

The arena-pointer global is <code>0x800EECD0</code>; the synchronization helper is <code>0x80066390</code>. Those are address/function facts, not additional owned intervals on this page.

## Dynamic and overlay-qualified runtime facts

These facts are important to allocation safety but are not promoted into bounded reusable intervals.

| Region/fact | Class | Established fact | What remains unknown |
|---|---|---|---|
| Main arena after <code>0x801AF820</code> | <code>dynamic</code> | Production moves the arena start past the 1 KiB reservation and synchronizes the arena pointer. | Current allocation sequence, endpoint, and free headroom vary with stage/resources/lifecycle. No generic end is asserted. |
| Historical enemy-import high-water observation | <code>proof-only</code> / <code>dynamic</code> | One analyzed route had original high-water endpoint <code>0x80290990</code>; adding Temple fighter file after stock Fire allocations would exceed it by <code>0x3098</code>, while replacing Fire file <code>0x20</code> left about <code>0x1E0D0</code>. | This is proof-specific arithmetic, not a global allocator boundary or confirmed-free interval. |
| Main stage overlay base <code>0x802ECE30</code> | <code>dynamic</code> | Main stage overlays load at this VA and are mutually exclusive by stage/source. | Overlay extent and owner at any subrange require the exact stage/source artifact. No global owner is assigned merely from the VA. |
| Current stage resource-file base slot <code>0x802F82B8</code> | <code>dynamic</code> | Stage-loading code stores the current resource-file base used by ordinary-pickup selector lookup. | The pointed-to allocation address/extent depends on the loaded stage/resource file. |
| Toasty dynamic texture proof | <code>proof-only</code> / <code>dynamic</code> | The proven CI8 path requested a dynamic 78x85 texture with 96-byte stride, <code>0x1FE0</code> image bytes. | Returned backing address and production lifetime are not a fixed reusable allocation; final feature integration remains pending. |

## Confirmed-free status

**Reusable <code>confirmed-free</code> intervals currently exposed by this map: none.**

This is not evidence that the ROM or RDRAM has no free bytes. It means the current evidence reviewed for this task does not justify promoting an unowned interval to production-reusable <code>confirmed-free</code> under the required lifecycle/reference standard.

Notable examples:

- the former selector cave/tail is now part of <code>rom.production.inventory_helper_cave</code>;
- the bootstrap cave is fully reserved through <code>0x9AF20</code>;
- the high-ROM title allocation owns its full <code>0x31000</code> capacity, even when a generated title file ends earlier;
- clean <code>FF</code> tails used by disposable fighter/resource proofs remain proof evidence only;
- the <code>0xA1308..0xA1544</code> zero-filled area is positively known **not** to be free.

## Overlap and validation rules

A future structured representation should fail validation when:

- an interval is outside the declared address-space bounds;
- <code>end_exclusive <= start</code>;
- a declared size disagrees with <code>end_exclusive - start</code>;
- two simultaneously live production owners overlap without an explicit containment/composition relationship;
- KSEG0 and KSEG1 aliases are represented as independent RDRAM allocations;
- an overlay VA lacks stage/source identity;
- <code>confirmed-free</code> lacks explicit lifecycle and evidence;
- a <code>proof-only</code> interval is marked production-safe without a separately validated production composition;
- a ROM offset and runtime VA are related without a declared proven mapping;
- a current owner lacks a canonical page/module/reference.

Expected containment such as the V2 sub-owners inside the 1 KiB reservation is documented explicitly rather than represented as duplicate top-level coverage.

## Initial coverage and deliberate unknowns

Coverage here means only the union of the bounded **current stock/protected/production interval rows above**. It is not a claim that everything outside those rows is unused.

- ROM bounded current coverage: <code>0x137268</code> bytes (1,274,472 bytes), about **7.60%** of the 16 MiB image.
- RDRAM bounded fixed coverage: <code>0xB20</code> physical bytes (2,848 bytes), about **0.068%** of 4 MiB.
- Additional proof-only ROM footprints listed separately: <code>0x50FE4</code> bytes across the two bounded examples; these are excluded from current ownership coverage.

The low percentages are intentional. Large parts of both spaces remain **unclassified/unknown** because this task does not infer ownership from byte patterns or missing references.

In particular, this first map deliberately leaves unclassified:

- all ROM gaps not covered by an established interval above;
- all RDRAM gaps between the fixed records above;
- arena/heap contents after the established arena-start anchor;
- stage-overlay subranges without exact stage/source identity;
- per-stage dynamic resource allocations beyond established file/source sizes;
- historical proof extents whose exact bounds were not preserved well enough to promote;
- sparse individual patch sites that are already canonically guarded by the [patch-site registry](Address-and-Patch-Site-Registry).

## Relationship to the decomp map

Allocation ownership and decomp/readiness answer different questions.

- Decompiled or well-understood stock bytes are still owned.
- Unknown/black decomp space is still protected; unknown does not mean free.
- A <code>confirmed-free</code> allocation claim, if one is added later, does not imply decompilation completeness.
- A production cave/allocation is an ownership overlay, not a decomp-readiness score.
- Overlay reuse remains stage-qualified.

No <code>MKMSZ-Decomp-Map</code> data or repository is changed by this task. Structured export/integration is a later phase only after this human-readable schema survives normal maintenance.

## Related canonical references

- [Project status](Project-Status) — current production/proof/pending dashboard.
- [Core runtime and address database](Core-Runtime-and-Address-Database) — bootstrap/payload mechanism and runtime design.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded edits and expected bytes.
- [ROM, overlay, and resource map](ROM-Overlay-and-Resource-Map) — file table, overlay/resource loading, and stage resource grammar.
- [Address quick reference](Address-Quick-Reference) — derivative orientation-only lookup.
- [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle) — four-box and run-lifecycle behavior.
- [XP and progression](XP-and-Progression) — progression semantics and runtime evidence.
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) — canonical slot mapping/current coverage.
- [Sektor takeover proof history](Sektor-Takeover-Proof-History) — fighter proof footprints, versioned allocation-boundary evidence, and supersession.
- [Experiments, failures and superseded findings](Experiments-Failures-and-Superseded-Findings) — failure index and proof/production conflict history.
