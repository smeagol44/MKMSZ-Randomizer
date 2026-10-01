# Memory and allocation map

> **Scope:** This page is the canonical owner for **continuous literal-space ownership** in the supported 16 MiB MKMSZ USA Rev. 0 ROM and its physical 4 MiB RDRAM. It records exact bounded intervals, aliases, lifecycle, ownership, evidence, production safety, and known conflicts.
>
> It does **not** replace the [patch-site registry](Address-and-Patch-Site-Registry) for individual guarded edits, the [function registry](Function-Registry) for function semantics, the [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) for loader/resource grammar, or the separate decomp-readiness view. Unknown space remains unknown.

The supported clean input is the 16 MiB big-endian USA Rev. 0 ROM, SHA-256 <code>9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6</code>.

**Missile proof ownership clarification:** exact v75/v80–v85 use file-`0x87` fixed projectile texture slot `0x24`; helper `0x80060A3C` allocates a separate dynamic texture slot in `0x200..0x2FF` and constructs two independently listed actors. Palette acquisition returns a handle whose selector is handle minus `0x80`; fixed selector zero does not own the resident player Sektor TLUT. Helper cleanup frees its dynamic texture and actors, with no traced palette release. These are native runtime resources, **not new free ROM/RDRAM ranges**. v85 suppresses insertion on normal straight flight and is statically rejected; it does not change the proof cave allocations or make them production-owned.

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
| <code>rom.production.safe_selector_move_helper</code> | <code>[0x0000E27C, 0x0000E2B0)</code> | <code>production</code> | Safe Stage Select movement-SFX helper | Global frontend code | Native selector frontend | Runtime-confirmed v03a; Static-confirmed clean unreachable compiler epilogue and no direct branch/jump/JAL targets into span; implementation guards exact clean bytes | yes | <code>stage_selector.py</code>; [Patch-site registry](Address-and-Patch-Site-Registry) | Plays only title MOVE descriptor <code>0x1FC</code> for valid Up/Down edges. Does not own or imply a confirmation hook. Rejected v01/v02 confirmation experiments must not be composed into this owner. |
| <code>rom.production.inventory_action_cave</code> | <code>[0x0008F6E8, 0x0008F750)</code> | <code>production</code> | Four-box action routine | Global code | Gameplay | Runtime-confirmed behavior; Implementation/CI-confirmed bounds | yes | <code>inventory_boxes.py</code>; [Patch-site registry](Address-and-Patch-Site-Registry) | Historical Prison-key callback entered at <code>0x8F6EC</code>; proof body is not a reusable allocation. |
| <code>rom.production.inventory_helper_cave</code> | <code>[0x0009A6C8, 0x0009A758)</code> | <code>production</code> | Four-box switch/mask helper composition | Global code | Gameplay / transition | Runtime-confirmed behavior; Implementation/CI-confirmed <code>0x90</code> reservation | yes | <code>inventory_boxes.py</code>; tests assert <code>SELECTOR_CAVE_SIZE == 0x90</code> | Toasty visual v06 used <code>[0x9A720,0x9A754)</code> and is rejected for that route; this tail is now production-owned. |
| <code>rom.production.bootstrap_composite</code> | <code>[0x0009AD84, 0x0009AF20)</code> | <code>production</code> | Native bootstrap + pickup persistence + relocated selector/flow data | Global code/data | Stage init / gameplay | Runtime-confirmed composition; Implementation/CI-confirmed capacity <code>0x19C</code> | yes | <code>native_payload.py</code>, <code>pickup_persistence.py</code>, <code>inventory_boxes.py</code>, <code>flow_bypass.py</code> | Conflicts with rejected title wrapper at <code>0x9ADE0</code> and Sektor v62 proof record <code>[0x9AD90,0x9ADA0)</code>. Final four bytes are reserved capacity, not free. |
| <code>rom.production.shared_file_entry_1a</code> | <code>[0x000A5148, 0x000A5154)</code> | <code>production</code> | Shared TURN/controls/Toasty expansion file-table entry <code>0x1A</code> | Global file table | Stage init | TURN production composition Runtime-confirmed; CI guards/bounds | yes | <code>game_settings_turn.py</code>, <code>toasty.py</code> | TURN owns the mandatory prefix; controls occupy the low extension and optional Toasty the high extension. Frontend does not load this file. |
| <code>rom.production.turn_shared_prefix</code> | <code>[0x00F68000, 0x00F68404)</code> | <code>production</code> | TURN native control module / shared file-0x1A prefix | Global high ROM | Stage init / gameplay | Runtime-confirmed production composition; CI-confirmed 0x404-byte module | yes | <code>game_settings_turn.py</code>, <code>tests/test_game_settings_turn.py</code> | Mandatory prefix of shared file 0x1A. Padding through Toasty source offset remains reserved by the shared transport when Toasty is present. |
| <code>rom.production.controls_extension</code> | <code>[0x00F68410, 0x00F69060)</code> | <code>production</code> | Guarded modern Attack/Specials/Jump/Run helpers; loaded file-0x1A extension | Global high ROM | Stage init / gameplay | Runtime-confirmed in accepted v02 composition; builder parity confirmed | yes | <code>controls_production.py</code> | Helpers start at runtime <code>0x801AFC30</code> and end below <code>0x801B0880</code>; ROM alignment gaps remain inside the shared file. |
| <code>rom.production.rainbow_loader_wrapper</code> | <code>[0x00F69060, 0x00F690B8)</code> | <code>production</code> | Optional compact-rainbow file-<code>0x87</code> loader wrapper in shared file <code>0x1A</code> | Global high ROM | Stage resource load | Runtime-confirmed by compact-tail all-stage proof; CI guards/bounds | conditional | <code>rainbow_palette.py</code>; [Patch-site registry](Address-and-Patch-Site-Registry) | Runtime mirror is <code>[0x801B0880,0x801B08D8)</code>; wrapper extends file <code>0x1A</code> only when needed and remains below the Temple special-check module. |
| <code>rom.production.temple_special_check</code> | <code>[0x00F690C0, 0x00F69150)</code> | <code>production</code> | Temple scripted-check re-entry + award helpers in shared file <code>0x1A</code> | Global high ROM | Temple gameplay / re-entry | v02 Runtime-confirmed mechanism; branch integration guarded by CI | yes | <code>temple_special_check.py</code>, <code>tests/test_temple_special_check.py</code> | Runtime mirror <code>[0x801B08E0,0x801B0970)</code>; deliberately starts after the optional rainbow wrapper and ends <code>0x690</code> bytes before Toasty. |
| <code>rom.production.toasty_module</code> | <code>[0x00F697E0, 0x00F6B5D0)</code> | <code>production</code> | Packed Toasty code/TLUT/tables/state/CI4 slices | Global high ROM | Stage init / gameplay | Runtime-confirmed in controls+Toasty v02 production composition | conditional | <code>toasty.py</code>, <code>toasty_codegen.py</code> | Optional module begins at the ROM offset corresponding to runtime <code>0x801B1000</code> inside shared file 0x1A. |
| <code>rom.production.toasty_audio_sample</code> | <code>[0x00F6B5D0, 0x00F6BDE6)</code> | <code>production</code> | Confirmed MKT Toasty encoded sample | Global high ROM | Gameplay audio | Runtime-confirmed in TURN+Toasty production composition | conditional | <code>toasty.py</code> | Donor bytes are supplied at build time and are not stored in the repository. |
| <code>rom.production.temple_intro_audio_sample</code> | <code>[0x00F6BDF0, 0x00F6D810)</code> | <code>production</code> | One seed-selected MKT Temple-intro encoded sample; maximum reserved size <code>0x1A20</code> | Global high ROM | Temple intro | **Runtime-confirmed bounded production composition** in v06; static/CI guards cover reservation and overlap checks | conditional | <code>temple_intro_audio.py</code> | Enabled only with valid MKT Rev. 2 donor. Clean supported ROM is <code>FF</code> throughout the reservation and file-table overlap is guarded. v06 seed <code>TEMPLE-PROD-CARRIER</code> selected Friendship and played correctly; only the selected sample is written. |
| <code>rom.stock.false_zero_cave</code> | <code>[0x000A1308, 0x000A1544)</code> | <code>stock-known</code> | Stock action/dispatch record area | Global stock data | Gameplay/input dispatch | Static-confirmed; Runtime-confirmed failure/correction in Sektor v08 | no | [Core runtime](Core-Runtime-and-Address-Database); [MKT compatibility](MKT-to-MKMSZ-Compatibility-Layer) | **Required negative example:** zero-filled semantic records were mistaken for a cave; overwriting them caused input-specific hangs. |
| <code>rom.production.file_entry_1b</code> | <code>[0x000A5154, 0x000A5160)</code> | <code>production</code> | Global file-table entry <code>0x1B</code> | Global file table | Stage init | Runtime-confirmed load/execute; Implementation/CI-confirmed guard | yes | <code>addresses.py</code>, <code>native_payload.py</code> | Points to current payload source <code>[0xF10000,0xF10300)</code>. |
| <code>rom.production.file_entry_5e</code> | <code>[0x000A5478, 0x000A5484)</code> | <code>production</code> | Global file-table entry <code>0x5E</code> | Global file table | Frontend/title | Earlier title route Runtime-confirmed; new end-pointer update Static/implementation-confirmed, runtime Pending | yes | <code>title_branding.py</code>; [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | Keeps stock start/flag; updates the end pointer to the in-place compressed package length. |
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
| <code>rom.production.file_5e_title</code> | <code>[0x004E3060, 0x00512440)</code> | <code>production</code> | In-place compressed title package, file <code>0x5E</code>; trailing stock bytes retained | Frontend/title resource | Title load | New typeset image Static/implementation-confirmed; runtime Pending | yes | <code>title_branding.py</code> clean-package SHA-256 guard; [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | Migrated from <code>rom.stock.file_5e_title</code>: generated <code>SUB-ZERO</code> end is <code>0x0051058E</code> (size <code>0x2D52E</code>); <code>[0x0051058E,0x00512440)</code> remains protected stock tail, not free. |
| <code>rom.stock.stage_resource.temple</code> | <code>[0x00513710, 0x00523370)</code> | <code>stock-known</code> | Temple stage resource file | Stage 0 resource | Temple load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | No gap/capacity inference is made. |
| <code>rom.stock.stage_resource.water</code> | <code>[0x00611780, 0x00617C60)</code> | <code>stock-known</code> | Water stage resource file | Stage 2 resource | Water load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | No gap/capacity inference is made. |
| <code>rom.stock.stage_resource.wind</code> | <code>[0x00698680, 0x0069A820)</code> | <code>stock-known</code> | Wind stage resource file | Stage 1 resource | Wind load/gameplay | Static-confirmed; runtime base matched | no | [ROM/overlay/resource map](ROM-Overlay-and-Resource-Map) | No gap/capacity inference is made. |
| <code>rom.stock.stage_resource.earth_pickups</code> | <code>[0x00305A30, 0x0030AA00)</code> | <code>stock-known</code> | Earth ordinary-pickup resource, global file <code>0x30</code> | Stage 3 ordinary pickup visuals | Earth load/gameplay | Static-confirmed from file table and stage setup; cross-stage use Runtime-confirmed in TEST LAB v38 | no | [Stage catalog — Earth](Stage-Catalog-Earth) | Stage setup publishes its allocation through <code>0x802F82B8</code>. Empty selectors are logical capacity only. |
| <code>rom.stock.file_88_monk1</code> | <code>[0x006BAEC0, 0x006DD470)</code> | <code>stock-known</code> | Earth MONK1 fighter resource, global file <code>0x88</code> | Fighter type <code>0x00</code> | Earth enemy construction/gameplay | Static-confirmed; prior live capture matched this file at <code>0x802434B8</code> | no | [Enemy randomization](Enemy-Randomization), [Stage catalog — Earth](Stage-Catalog-Earth) | Supersedes the former mislabel as Earth ordinary-pickup resource. Do not use selectors from this file as pickup visuals. |
| <code>rom.stock.file_87_subzero</code> | <code>[0x00748920, 0x0078E300)</code> | <code>stock-known</code> | Stock Sub-Zero fighter resource, file <code>0x87</code> | Global fighter resource | Gameplay | Static-confirmed; repeatedly used as donor-proof baseline | no | [Sektor mapping](Sub-Zero-to-Sektor-Animation-Mapping) | Optional outfit recolor edits a guarded palette subset inside this owned file; that does not make other bytes free. |
| <code>rom.production.payload_source</code> | <code>[0x00F10000,0x00F103B0)</code> | <code>production</code> | MKMSZR Runtime V2 reloadable code payload | Generated ROM output | Stage init reload; runtime code | Runtime-confirmed through the rainbow full-composition proof; Implementation/CI-confirmed exactly <code>0x3B0</code> bytes | yes | <code>native_payload.py</code>, <code>runtime_v2.py</code>, <code>xp_progression.py</code>, <code>rainbow_palette.py</code> | File <code>0x1B</code> points here. Source bytes being <code>FF</code> in the clean ROM are only a guard, not the reason this ownership is accepted. |
| <code>rom.production.rainbow_bank</code> | <code>[0x00F20000,0x00F22000)</code> | <code>production</code> | Optional 64-phase rainbow palette bank, raw file <code>0x92</code> | Generated ROM output | Rainbow gameplay only | Runtime-confirmed in compact-tail all-stage proof v01 | conditional | <code>rainbow_palette.py</code>; guarded zero file-<code>0x92</code> entry, exact <code>0x2000</code> bank, and all 15 stock file-<code>0x87</code> loader pairs | Stock file <code>0x87</code> remains at retail ROM and is not duplicated or repointed. This supersedes the former <code>[0xF20000,0xF679E0)</code> relocated-file owner. |
| <code>rom.stock.title_former_high</code> | <code>[0x00F90000, 0x00FC1000)</code> | <code>stock-unknown</code> | Former title relocation allocation; current title no longer writes it | Global high ROM | No current title lifecycle | Earlier title composition Runtime-confirmed; new in-place static integration | no | <code>title_branding.py</code>; historical <code>rom.production.title_high</code> | Retired title-owner interval; clean <code>FF</code> bytes and former reservation do not by themselves certify another owner or free space. |

### Production bootstrap composite sublayout

<code>rom.production.bootstrap_composite</code> is one ownership interval but has multiple current sub-owners. These subranges are descriptive containment, not additional top-level allocations.

| ROM subrange | Current content |
|---|---|
| <code>[0x9AD84,0x9ADD8)</code> | Native loader/call stub (<code>0x54</code> bytes in current V2 composition) |
| <code>[0x9ADD8,0x9ADE8)</code> | Pickup-restore trampoline |
| <code>[0x9ADE8,0x9AE18)</code> | Shared file-<code>0x1A</code> stage-init loader in the production TURN composition |
| <code>[0x9AE18,0x9AE28)</code> | Pickup-capture trampoline; the check-v01 disposable composition retargets this owned stub through a capture/event dispatcher without writing outside the owner |
| <code>[0x9AE28,0x9AE58)</code> | TURN decision, release, and action trampolines (three 16-byte entries) |
| <code>[0x9AE58,0x9AEC0)</code> | Frontend GAME SETTINGS wrapper |
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
| <code>rom.proof.sektor_v70_file_87</code> | <code>[0x00F40000,0x00F8E790)</code> | <code>proof-only</code> | Sektor v70 chest + straight-missile fighter file <code>0x87</code> | Partially Runtime-confirmed missile presentation/flight route | no | File size <code>0x4E790</code> is <code>0x24C</code> above the Runtime-confirmed v49 Fortress-working footprint. Fortress/Prison allocation safety was not revalidated; do not promote this as a new safe envelope. |
| <code>rom.proof.sektor_v75_file_87</code> | <code>[0x00F40000,0x00F8E790)</code> | <code>proof-only</code> | Sektor v75 relocated fighter file <code>0x87</code> | Runtime-confirmed bounded missile-flight route; endpoint verified in exact v75 file entry | no | Same file size as v70; no Fortress/Prison allocation-safety promotion. Its projectile helper code uses proof ROM <code>[0x9ADA0,0x9AF20)</code> inside current production bootstrap ownership, so the proof cannot be combined with production as-is. |
| <code>rom.proof.control_facing_v02_module</code> | <code>[0x00F72000,0x00F72268)</code> | <code>proof-only</code> | 616-byte direction-facing expansion module backing file <code>0x1A</code> | Runtime-confirmed on the bounded v02 control route | no | Source lies in a clean-ROM FF gap but is proof-only ownership, not a reusable free-space declaration. |
| <code>rom.proof.attack_modern_check_v01_low_extension</code> | <code>[0x00F68404,0x00F68600)</code> | <code>proof-only</code> | ATTACK helper/dispatch code and aligned gaps after production TURN inside shared file <code>0x1A</code> | User-reported Runtime-confirmed disposable full-composition check; builder guards/bounds statically checked | no | Loaded to cached <code>[0x801AFC24,0x801AFE20)</code>; starts with TURN-owned prefix intact and ends before Toasty source <code>0x00F687E0</code> / runtime <code>0x801B0000</code>. The low transport gap is owned, not generally free. |
| <code>rom.proof.attack_modern_check_v01_owned_stubs</code> | <code>[0x000775D0,0x000775DC)</code>, <code>[0x00077688,0x00077694)</code>, <code>[0x0009AE18,0x0009AE28)</code> | <code>proof-only</code> | Combo and Block stubs inside existing production GAME SETTINGS regions; retargeted capture stub inside production bootstrap composite | User-reported Runtime-confirmed disposable full-composition check | no | All three are guarded edits within existing owners for this artifact. In normal production the frontend tails remain padding and the capture stub still targets capture directly. The conflicting <code>0x9AEC0</code> proof trampoline is untouched. |
| <code>rom.proof.toasty_v43_feature</code> | <code>[0x00F73000,0x00F73780)</code> | <code>proof-only</code> | Toasty v43 compact feature file <code>0x12</code> | Implementation/static-confirmed; runtime Pending | no | Loads 0x780 bytes into the production-reserved expansion pool. The proof also retains v42's separate ROM-backed CI8 source files and v03 disposable audio-host edits; this interval is artifact-specific, not a production allocation. |


### Known rejected/conflicting ROM uses

| Use | Exact known footprint | Conflict / conclusion |
|---|---|---|
| Sektor v01-v07 “zero cave” helper | <code>[0xA1308,0xA1544)</code> | **Rejected / failed.** Overwrote live stock action/dispatch records. Restoring stock bytes in v08 removed the input-specific hangs. |
| Toasty visual v06 selector-cave tail | <code>[0x9A720,0x9A754)</code> | **Rejected / failed on that route.** The interval now also lies inside <code>rom.production.inventory_helper_cave</code>. |
| Sektor v62 standalone combo continuation | <code>[0x9AD90,0x9ADA0)</code> | Runtime-valid proof semantics, but **allocation conflicts** with <code>rom.production.bootstrap_composite</code>. Must be relocated before integration. |
| Toasty v43 reaction trampoline | small proof trampoline begins at <code>0x9ADD4</code> inside <code>rom.production.bootstrap_composite</code> | **Proof-only/conflicting.** The trigger semantics/hook are statically validated, but this trampoline location is already production-owned and must be reallocated/composed before product integration. |

| Sektor v65-v70 missile helper code | known entry begins at <code>0x9ADA0</code> inside <code>rom.production.bootstrap_composite</code>; full historical extent is not promoted here | **Proof-only/conflicting.** Runtime results validate bounded chest/projectile semantics, not this allocation. Reallocate before any integration. |
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
| <code>rdram.production.box_state</code> | <code>[0x0A60E8,0x0A60EC)</code> | KSEG0 <code>0x800A60E8</code>; KSEG1 <code>0xA00A60E8</code> | <code>production</code> | Active-box index/latch + durable TURN preference | Global mutable data | Frontend / gameplay / transition | Runtime-confirmed production composition | yes | <code>inventory_boxes.py</code>, <code>game_settings_turn.py</code> | Bits <code>0..1</code> active index; <code>0x100</code> switch latch; <code>0x0200</code> means TURN=LOCK. Box switching preserves the setting bit. |
| <code>rdram.production.box_magic</code> | <code>[0x0A60EC,0x0A60F0)</code> | KSEG0 <code>0x800A60EC</code>; KSEG1 <code>0xA00A60EC</code> | <code>production</code> | <code>MKBX</code> magic | Global mutable data | Run initialization / reconstruction | Implementation/CI-confirmed; exercised by runtime system | yes | <code>inventory_boxes.py</code> | Magic <code>0x4D4B4258</code>. |
| <code>rdram.stock.xp_cap_table</code> | <code>[0x0A63FC,0x0A6410)</code> | KSEG0 <code>[0x800A63FC,0x800A6410)</code>; KSEG1 <code>[0xA00A63FC,0xA00A6410)</code> | <code>stock-known</code> | Signed XP-cap table with production main-stage edits | Global data | Gameplay | Static-confirmed; production writes Implementation/CI-confirmed | conditional | <code>addresses.py</code>, <code>xp_progression.py</code> | Only selected halfwords are production-edited. |
| <code>rdram.production.boot_branding_text</code> | <code>[0x0AED98,0x0AEE24)</code> | KSEG0 <code>[0x800AED98,0x800AEE24)</code>; KSEG1 <code>[0xA00AED98,0xA00AEE24)</code> | <code>production</code> | MKMSZR legal/boot strings | Global data | Boot/legal screen | Runtime-confirmed | yes | <code>boot_branding.py</code> pointer targets | Established global-segment mapping; count physical bytes once. |
| <code>rdram.production.box_indicator</code> | <code>[0x0AEE24,0x0AEE98)</code> | KSEG0 <code>[0x800AEE24,0x800AEE98)</code>; KSEG1 <code>[0xA00AEE24,0xA00AEE98)</code> | <code>production</code> | Native box HUD wrapper/text | Global code/data | Gameplay HUD | Runtime-confirmed | yes | <code>box_indicator.py</code> | Exact region mirrors ROM owner. |
| <code>rdram.production.license_text</code> | <code>[0x0AEE98,0x0AEEBC)</code> | KSEG0 <code>[0x800AEE98,0x800AEEBC)</code>; KSEG1 <code>[0xA00AEE98,0xA00AEEBC)</code> | <code>production</code> | MKMSZR license string | Global data | Boot/legal screen | Runtime-confirmed | yes | <code>boot_branding.py</code> | Exact bounded string storage. |
| <code>rdram.stock.current_xp</code> | <code>[0x11200C,0x112010)</code> | KSEG0 <code>0x8011200C</code>; KSEG1 <code>0xA011200C</code> | <code>stock-known</code> | Native current-XP word used by production progression | Global mutable data | Gameplay / stage transition | Static-confirmed and Runtime-confirmed on progression routes | conditional | <code>addresses.py</code>; [XP/progression](XP-and-Progression) | Production owns behavior around the stock variable, not surrounding words. |
| <code>rdram.production.runtime_core</code> | <code>[0x1AF420,0x1AF5F4)</code> | KSEG0 <code>[0x801AF420,0x801AF5F4)</code>; KSEG1 <code>[0xA01AF420,0xA01AF5F4)</code> | <code>production</code> | Runtime V2 init + pickup-persistence code through actual <code>+0x1D4</code> core end | Reserved MKMSZR block | Reloaded at stage init; executes during init/gameplay hooks | Runtime-confirmed; exact emitted size CI-confirmed | yes | <code>runtime_v2.py</code>, <code>pickup_persistence.py</code>; actual persistence core size <code>0x1D4</code> | Subrange of the 1 KiB reservation. |
| <code>rdram.production.inventory_payload</code> | <code>[0x1AF5F4,0x1AF620)</code> | KSEG0 <code>[0x801AF5F4,0x801AF620)</code>; KSEG1 <code>[0xA01AF5F4,0xA01AF620)</code> | <code>production</code> | Four-box filtered-save helper | Reserved MKMSZR block | Gameplay / transition | Runtime-confirmed composition; CI-confirmed bounds | yes | <code>inventory_boxes.py</code> payload <code>+0x1D4..+0x200</code> | Reuses the production payload tail intentionally. |
| <code>rdram.production.xp_payload</code> | <code>[0x1AF620,0x1AF700)</code> | KSEG0 <code>[0x801AF620,0x801AF700)</code>; KSEG1 <code>[0xA01AF620,0xA01AF700)</code> | <code>production</code> | XP progression callback, threshold table, restore helper, and bounded padding | Reserved MKMSZR block | Pickup / stage transition | Runtime-confirmed Diagnostic B behavior; CI-confirmed meaningful content stays below <code>+0x2E0</code> | yes | <code>xp_progression.py</code> | The formerly zero <code>[+0x2E0,+0x300)</code> tail is intentionally released to the optional runtime-feature region below. |
| <code>rdram.production.optional_runtime_tail</code> | <code>[0x1AF700,0x1AF7D0)</code> | KSEG0 <code>[0x801AF700,0x801AF7D0)</code>; KSEG1 <code>[0xA01AF700,0xA01AF7D0)</code> | <code>production</code> | Optional Runtime V2 feature code tail | Reserved MKMSZR block | Gameplay | Runtime-confirmed by compact rainbow v01; CI-confirmed bounds | yes | <code>runtime_v2.py</code>, <code>rainbow_palette.py</code> | Rainbow owns the full <code>0xD0</code>-byte tail in rainbow builds; the compact helper adds the proof-validated defensive phase mask. In non-rainbow builds the interval remains reserved/zero. |
| <code>rdram.production.state_header</code> | <code>[0x1AF7D0,0x1AF7F0)</code> | KSEG0 <code>[0x801AF7D0,0x801AF7F0)</code>; KSEG1 <code>[0xA01AF7D0,0xA01AF7F0)</code> | <code>production</code> | <code>MKSV</code> V2 state header; flags bit <code>0x0001</code> owns Temple scripted-check collection | Persistent MKMSZR state | Survives payload reload / normal stage lifecycle | Header Runtime-confirmed through production compositions; Temple flag Runtime-confirmed in v02 | yes | <code>runtime_v2.py</code>, <code>temple_special_check.py</code> | Header validates magic/version/size/header-size; total state size is <code>0x50</code>. Temple special state is intentionally outside the ordinary pickup words. |
| <code>rdram.production.pickup_state</code> | <code>[0x1AF7F0,0x1AF810)</code> | KSEG0 <code>[0x801AF7F0,0x801AF810)</code>; KSEG1 <code>[0xA01AF7F0,0xA01AF810)</code> | <code>production</code> | Eight stage ordinary-pickup bitset words | Persistent MKMSZR state | Run lifecycle until reset boundary | Runtime-confirmed representative persistence in all eight stages and in the rainbow full composition | yes | <code>pickup_persistence.py</code> descriptors use state offsets <code>+0x20..+0x3C</code> | Scripted/special mechanisms are outside these bitsets. |
| <code>rdram.production.xp_state</code> | <code>[0x1AF810,0x1AF818)</code> | KSEG0 <code>[0x801AF810,0x801AF818)</code>; KSEG1 <code>[0xA01AF810,0xA01AF818)</code> | <code>production</code> | Progression acquired-count + persistent-XP words | Persistent MKMSZR state | Run lifecycle / stage transition | Runtime-confirmed on bounded Diagnostic B routes and rainbow full composition | yes | <code>xp_progression.py</code> state <code>+0x40/+0x44</code> | Full nine-tier run remains a validation limit, not an allocation ambiguity. |
| <code>rdram.production.rainbow_phase</code> | <code>[0x1AF818,0x1AF81C)</code> | KSEG0 <code>0x801AF818</code>; KSEG1 <code>0xA01AF818</code> | <code>production</code> | Optional rainbow phase word | Persistent MKMSZR state | Rainbow gameplay | Runtime-confirmed in full-composition v01 | conditional | <code>rainbow_palette.py</code> state offset <code>+0x48</code> | Used only in <code>rainbow</code> mode; initialized by the common V2 state initializer. |
| <code>rdram.production.state_reserved_tail</code> | <code>[0x1AF81C,0x1AF820)</code> | KSEG0 <code>[0x801AF81C,0x801AF820)</code>; KSEG1 <code>[0xA01AF81C,0xA01AF820)</code> | <code>production</code> | Runtime V2 reserved final word; transient TURN editor halfword use | Reserved MKMSZR state | Frontend editor / run lifecycle | Runtime-confirmed production composition for transient editor use; CI-confirmed reservation boundary | yes | <code>runtime_v2.py</code>, <code>game_settings_turn.py</code> | GAME SETTINGS uses KSEG1 <code>0xA01AF81C</code> transiently while open. Durable TURN ownership is <code>0x800A60E8 bit 0x0200</code>. **Not free.** |
| <code>rdram.production.expansion_pool</code> | <code>[0x1AF820,0x1B3420)</code> | KSEG0 <code>[0x801AF820,0x801B3420)</code>; KSEG1 <code>[0xA01AF820,0xA01B3420)</code> | <code>production</code> | MKMSZR native expansion pool parent reservation | Reserved MKMSZR block | Global reservation; feature slices are build-time assigned | 16 KiB arena-floor proof Runtime-confirmed across all eight safe stage loads; allocator/bounds Implementation/CI-confirmed | yes | <code>addresses.py</code>, <code>allocations.py</code>, <code>tests/test_expansion_allocations.py</code> | Parent owner remains reserved. TURN and modern controls own low named suballocations; Toasty conditionally owns the high named suballocation. |
| <code>rdram.production.turn_module</code> | <code>[0x1AF820,0x1AFC24)</code> | KSEG0 <code>[0x801AF820,0x801AFC24)</code>; KSEG1 <code>[0xA01AF820,0xA01AFC24)</code> | <code>production</code> | TURN v10/v06 native control module | Expansion-pool suballocation | Stage init / gameplay | Runtime-confirmed production composition; CI-confirmed 0x404-byte allocation | yes | <code>game_settings_turn.py</code>, <code>tests/test_game_settings_turn.py</code> | Loaded only at stage init through shared file 0x1A; never loaded from frontend. |
| <code>rdram.production.controls_extension</code> | <code>[0x1AFC30,0x1B0880)</code> | KSEG0 <code>[0x801AFC30,0x801B0880)</code>; KSEG1 <code>[0xA01AFC30,0xA01B0880)</code> | <code>production</code> | Modern controls helpers/state | Expansion-pool suballocation | Stage init / gameplay | Accepted v02 Runtime-confirmed; shared-builder byte parity | yes | <code>controls_production.py</code> | Ends <code>0x780</code> bytes before optional CI4 Toasty at <code>0x801B1000</code>. |
| <code>rdram.production.rainbow_loader_wrapper</code> | <code>[0x1B0880,0x1B08D8)</code> | KSEG0 <code>[0x801B0880,0x801B08D8)</code>; KSEG1 <code>[0xA01B0880,0xA01B08D8)</code> | <code>production</code> | Optional compact-rainbow file-<code>0x87</code> loader wrapper | Expansion-pool suballocation | Stage resource load | Runtime-confirmed by compact-tail all-stage proof; CI guards/bounds | conditional | <code>rainbow_palette.py</code> | Uses only the start of the established controls→Toasty gap. |
| <code>rdram.production.temple_special_check</code> | <code>[0x1B08E0,0x1B0970)</code> | KSEG0 <code>[0x801B08E0,0x801B0970)</code>; KSEG1 <code>[0xA01B08E0,0xA01B0970)</code> | <code>production</code> | Temple scripted-check check/award helpers | Expansion-pool suballocation | Temple gameplay / title-stage re-entry | v02 Runtime-confirmed mechanism; CI guards/bounds | yes | <code>temple_special_check.py</code> | 0x90 bytes. Leaves the remainder of the gap untouched; Toasty remains fixed at <code>0x801B1000</code>. |
| <code>rdram.production.toasty_module</code> | <code>[0x1B1000,0x1B2DF0)</code> | KSEG0 <code>[0x801B1000,0x801B2DF0)</code>; KSEG1 <code>[0xA01B1000,0xA01B2DF0)</code> | <code>production</code> | Toasty packed native module | Reserved MKMSZR expansion pool | Stage init / gameplay | v02 Runtime-confirmed controls/CI4 composition; builder byte parity | conditional | <code>toasty_codegen.py</code>, <code>tests/test_toasty.py</code> | Leaves <code>0x630</code> bytes before the parent pool boundary <code>0x1B3420</code>. |
| <code>rdram.proof.toasty_v43_feature</code> | <code>[0x1AF820,0x1AFFA0)</code> | KSEG0 <code>[0x801AF820,0x801AFFA0)</code>; KSEG1 <code>[0xA01AF820,0xA01AFFA0)</code> | <code>proof-only</code> | Toasty v43 loaded feature slice | Gameplay HUD / reaction trigger | Stage init -> gameplay | v42 presentation sublayout Runtime-confirmed; added 176-byte reaction wrapper Implementation/static-confirmed; v43 runtime Pending | no | [Toasty visual research](Toasty-Visual-Research) | Artifact-specific suballocation of the production-reserved pool: v42-owned content remains through <code>0x1AFEEF</code>; v43 wrapper is <code>[0x1AFEF0,0x1AFFA0)</code>. Does not convert this slice into a production feature allocation. |

| <code>rdram.stock.pickup_context_pointer</code> | <code>[0x2ECE20,0x2ECE24)</code> | KSEG0 <code>0x802ECE20</code>; KSEG1 <code>0xA02ECE20</code> | <code>stock-known</code> | Live pickup-manager process/context pointer slot | Stage runtime | Stage manager construction/gameplay | Static-confirmed; runtime use confirmed by persistence | conditional | <code>addresses.py</code>, <code>pickup_persistence.py</code> | Corrects superseded <code>0x802FCE20</code>; surrounding overlay/runtime space is not inferred from this word. |

### Display slices within the modern-controls extension

These four contiguous slices partition the existing <code>rdram.production.controls_extension</code> owner for the Atlas RDRAM capacity view. Their boundaries follow the emission order in <code>controls_production.py</code>; they are **views, not additional or independent allocations**. Alignment bytes within each slice remain reserved by the parent. The parent ROM owner <code>rom.production.controls_extension</code> and its bounds also remain unchanged.

| View | Physical RDRAM half-open interval | KSEG0 half-open interval | ROM half-open interval | Size | Contents at the boundaries |
|---|---|---|---|---:|---|
| ATTACK | <code>[0x1AFC30,0x1AFE90)</code> | <code>[0x801AFC30,0x801AFE90)</code> | <code>[0x00F68410,0x00F68670)</code> | 608 B | Event, attack wrapper, combo, steady-block helpers; the event helper is shared. |
| SPECIALS | <code>[0x1AFE90,0x1B0310)</code> | <code>[0x801AFE90,0x801B0310)</code> | <code>[0x00F68670,0x00F68AF0)</code> | 1,152 B | Specials helper and following alignment. |
| JUMP | <code>[0x1B0310,0x1B0690)</code> | <code>[0x801B0310,0x801B0690)</code> | <code>[0x00F68AF0,0x00F68E70)</code> | 896 B | Standing and moving Jump, block-start and ledge helpers; block-start also serves Attack. |
| RUN | <code>[0x1B0690,0x1B0880)</code> | <code>[0x801B0690,0x801B0880)</code> | <code>[0x00F68E70,0x00F69060)</code> | 496 B | Run decision/capture/loop, Run state and dispatcher, then shared capture/event dispatch. |

The sizes sum to <code>0xC50</code> = 3,152 bytes, exactly the combined controls owner. The labels indicate where the builder emits code, **not exclusive feature ownership**: in particular, the shared event helper appears in ATTACK's view and shared capture/event dispatch in RUN's view. TURN remains its separate <code>rdram.production.turn_module</code> allocation.

### The 16 KiB reservation and arena boundary

The production reservation is exactly physical <code>[0x1AF420,0x1B3420)</code>, KSEG0 <code>[0x801AF420,0x801B3420)</code>, KSEG1 <code>[0xA01AF420,0xA01B3420)</code>. The established first 1 KiB <code>[0x1AF420,0x1AF820)</code> remains fully accounted for by the Runtime V2 code/state sub-owners above. The additional <code>[0x1AF820,0x1B3420)</code> 15 KiB is the production expansion-pool owner and is deliberately unassigned to features until a build-time allocation is made.

The game originally constructed its main arena at KSEG0 <code>0x801AF420</code>. Production now moves the arena floor to KSEG0 <code>0x801B3420</code>. The arena-address constructions are guarded as full instruction pairs; exact patch behavior belongs to the [patch-site registry](Address-and-Patch-Site-Registry). <code>0x801B3420</code> is the stock-arena anchor after reservation, not a claim that later RDRAM is reusable.

Static tracing distinguishes the arena's persistent/reset floor from its transient cursor. <code>0x800EECD0</code> is the persistent/reset arena base, while <code>0x80111ECC</code> is the live bump cursor. Helper <code>0x80066390</code> copies the base into the cursor. The statically confirmed bump boundary is <code>0x80290990</code>; immediately adjacent fixed state begins at <code>0x80290998</code>. These are dynamic address/function facts, not reusable fixed intervals on this page.

## Dynamic and overlay-qualified runtime facts

These facts are important to allocation safety but are not promoted into bounded reusable intervals.

| Region/fact | Class | Established fact | What remains unknown |
|---|---|---|---|
| Main arena after <code>0x801B3420</code> | <code>dynamic</code> | Production moves the reset/base floor to <code>0x801B3420</code>. The base is held at <code>0x800EECD0</code>, live bump cursor at <code>0x80111ECC</code>, and the Static-confirmed bump boundary is <code>0x80290990</code>. Allocator <code>0x8006643C</code> has no internal bounds check. | Current/peak cursor and therefore real headroom vary with stage/resources/lifecycle. The 16 KiB reservation has bounded runtime evidence, but later feature allocations can still change pressure and require composition-aware validation. |
| Historical enemy-import headroom observation | <code>proof-only</code> / <code>dynamic</code> | In one Fire allocation chain, appending Temple fighter file <code>0x89</code> would advance the cursor to <code>0x80293A28</code>, exceeding the now-Static-confirmed <code>0x80290990</code> boundary by <code>0x3098</code>; replacing Fire file <code>0x20</code> instead ended at <code>0x802728C0</code>, leaving <code>0x1E0D0</code>. | The boundary is global allocator architecture; the observed cursor/headroom values are proof-specific and do not establish worst-case free capacity across stages/lifecycles. |
| Exact allocator-profiler runtime observations | <code>proof-only</code> / <code>dynamic</code> | A disposable 1 KiB-reservation proof recorded global peak <code>0x802857E8</code>, leaving <code>0xB1A8</code> = 45,480 bytes = 44.41 KiB. A follow-up proof moved the arena floor to <code>0x801B3420</code>, reserving 16 KiB total; all eight safe stages loaded and global peak reached <code>0x802893E8</code>, leaving <code>0x75A8</code> = 30,120 bytes = 29.41 KiB. The peak increase is exactly <code>0x3C00</code> (15 KiB), equal to the additional reservation. | Runtime-confirmed only for the exercised proof compositions/routes. These are measured headroom values, not <code>confirmed-free</code>. The exact `0x802893E8` high-water value comes from the disposable profiler proof; the same 16 KiB floor is now current production ownership after the bounded full-production validation. Per-stage attribution uses the current-stage field, which changes before some preload/transition work completes; global peak is the stronger measurement. |
| User-supplied Water enemy-pair observation | <code>proof-only</code> / <code>dynamic</code> | Water peak cursor <code>0x80284940</code> leaves <code>0xC050</code> below <code>0x80290990</code>. Replacing two native fighter payloads totaling <code>0x284D0</code> gives an observed-route replacement ceiling <code>0x34520</code>, assuming unchanged later allocations and no new auxiliary allocation. | User-reported runtime capture; no emulator run in the 2026-09-28 static audit. Route/composition identity and worst-case applicability remain bounded. The conditional <code>0x40B90</code> GRUNT pair still exceeds this ceiling by <code>0xC670</code>. Static Slide collision closure now certifies file-<code>0x22</code> root <code>0x1E</code> live for ordinary GRUNTs; it certifies no extra removable bytes. See [Enemy randomization](Enemy-Randomization). |
| Native ordinary-enemy family paging | <code>dynamic</code> / stage-overlay-qualified | Static direct-call census: Water overlay <code>0xA1</code> has zero calls to <code>0x80066478</code>; Prison <code>0x9F</code> has three, Bridge <code>0x9B</code> two, Fortress <code>0x9E</code> two. Prison uses rewinds to alternate resource families including <code>0x8F+0x8E</code>, file <code>0x22</code>, and <code>0x90+0x8E</code>; Bridge swaps a special <code>0x2D</code> allocation against ordinary <code>0x8E+0x91</code>; Fortress swaps its ordinary GRUNT tail against Assassin resources and restores <code>0x22+0x23</code>. | This proves native stack-like encounter/section paging exists, not that a foreign destination may rewind the same lifetime boundary. Randomizer use requires destination-specific proof that no surviving process/actor/pointer references the discarded tail and must include transient projectile/effect allocations in peak accounting. See [Enemy randomization](Enemy-Randomization). |
| PRIS GRUNT 16-color dry-repack sizing | <code>proof-only</code> / static-offline | Codec-valid dry pack of Water candidate files <code>0x8E+0x8F</code> reduces resident raw pair from <code>0x3B520</code> to <code>0x321FC</code>, saving <code>0x9324</code> = 37,668 B; all 253 Type-5 frames round-trip to the selected 16-color/exact-secondary target buffers with zero mismatches. Against the user-supplied Water observed-route pair ceiling <code>0x34520</code>, this leaves <code>0x2324</code> = 8,996 B. A separate Bridge-native <code>0x8E+0x91</code> dry pack reduces <code>0x32DB0</code> to <code>0x2B14C</code>, saving <code>0x7C64</code> = 31,844 B. | Static sizing only. Type-5 decode backing remains dimension-sized and transient projectile/effect/actor pressure is not included, so neither residual Water margin nor Bridge payload reduction is certified runtime headroom/performance improvement. See [Enemy randomization](Enemy-Randomization). |
| PRIS GRUNT accepted compact runtime footprint | <code>proof-only</code> / Runtime-confirmed bounded composition | Accepted v04 keeps the conservative runtime-proof sizes <code>0x8E=0x1B0B8</code>, <code>0x8F=0x17A04</code>, <code>0x91=0x1080C</code>. Water pair <code>0x8E+0x8F = 0x32ABC</code> = 207,548 B, saving <code>0x8A64</code> = 35,428 B and sitting <code>0x1A64</code> = 6,756 B below the user-supplied observed-route pair ceiling <code>0x34520</code>. Bridge pair <code>0x8E+0x91 = 0x2B8C4</code> = 178,372 B, saving <code>0x74EC</code> = 29,932 B. | Water v01/v04 demonstrate that this compact resident-file strategy can run the imported staff-grunt family on the exercised route; this does not convert the 6.60-KiB residual into certified universal free space. Bridge's approximately 29-KiB resident reduction did not visibly improve the tested stock slowdown. See [Enemy randomization](Enemy-Randomization). |
| Water × PRIS GRUNT4 stock-pair proof | `proof-only` / Implementation-confirmed, runtime Pending | Disposable Water proof replaces native `0x8C+0x8D` residency with stock `0x8E+0x91 = 0x32DB0` and all nine ordinary Water types with `0x17`. Against the user-supplied observed-route Water replacement ceiling `0x34520`, resident fighter payload leaves only `0x1770` = 6,000 B = 5.86 KiB before transient pressure. | This is deliberately narrower than the accepted compact `0x8E+0x91 = 0x2B8C4` control. No Water rewind is introduced; stock Water still has zero direct `0x80066478` calls. Runtime validation must cover projectile firing, hit reaction, disarm/detached weapon, terminal cleanup, and stage continuation. |
| Water × raw FAST MONK proof v01 | `proof-only` / **Runtime-confirmed bounded composition** | Water replaces the first native fighter allocation/load (`0x8C`) with untouched stock file `0x20` in FAST MONK slot `0x800C2560`; stock `0x8D` remains loaded to preserve the native allocation sequence. Resident fighter payload is `0x20+0x8D = 0x2B4D0`. | Against user-measured Water ceiling `0x34520`, leaves `0x9050` = 36.08 KiB before transient pressure. No compaction and no new rewind. Proof SHA-256 `e01e8ece94f642411afb9150b8a1ee9f74b7871945bcf029a469dcb9349c774f`. User manual validation passed spawn/AI, attacks, hit reactions, kill, full death/despawn, additional encounters, and continued Water progression. This remains bounded to the tested all-`0x0A` roster and does not certify universal transient headroom. |
| Water × compact PRIS GRUNT3 proof v01 | `proof-only` / **Runtime-confirmed bounded composition** | Compact `0x8E = 0x1A148` (8-byte aligned) plus compact `0x90 = 0x16AC0`; pair `0x30C08`, saving `0xB558` = 46,424 B (45.34 KiB) versus stock `0x3C160`. File `0x90` keeps all 17 native 4-bpp cannon/projectile frames exact and keeps the 16-color projectile palette byte-exact at a relocated offset. | Against the user-measured Water replacement ceiling `0x34520`, the pair leaves `0x3918` = 14,616 B = 14.27 KiB before transient projectile/effect pressure. Finished-ROM post-build audit decodes all 217 compact Type-5 frames successfully. Proof SHA-256 `665bf98d6c457853a30f66de00680e6de761d3773ce7108598a3050c856c7bed`. User manual validation passed cannon fire, projectile hit/reaction, disarm/detached weapon, kill, full death/despawn, and continued Water progression. |
| Water × raw HULK MONK proof v01 | `proof-only` / **Runtime-confirmed bounded composition** | Water redirects the first native fighter transaction from `0x8C` to untouched stock file `0x25` and stores it at exact HULK MONK slot `0x801AE578`; the now-unused second `0x8D` transaction at ROM `0xB58D8..0xB58F8` is NOPed. Resident fighter payload is only `0x2C210`. | Against user-measured Water ceiling `0x34520`, leaves `0x8310` = 32.77 KiB before transient pressure. No compaction and no new rewind. Proof SHA-256 `90e6ae1f97934d42ededeb0b861caa577bc86870f1df7b27be7dc49b5f6ed4c7`. User manual validation passed spawn/AI, ordinary attacks, hit reactions, kill, full death/despawn, continued Water progression, and additional encounters. |
| Water mixed PRIS `0x14+0x16` proof v01 | `proof-only` / **Runtime-confirmed bounded mixed roster** | Reuses the already Runtime-confirmed compact `0x8E+0x90 = 0x30C08` residency and all loader/palette rebasing from the Water × `0x16` proof; only ordinary Water type records change to an alternating `0x14/0x16` roster. | User manual validation passed coexistence of base `0x14` and armed `0x16`, cannon/projectile behavior, `0x16 -> 0x14` disarm while native-spawned `0x14` actors also exist, terminal cleanup, and continued Water progression. Proof SHA-256 `57d92254e24e644f9f26b6a43d3410562081e3f66daa9db613bc25a3ece95d50`. |
| Main stage overlay base <code>0x802ECE30</code> | <code>dynamic</code> | Main stage overlays load at this VA and are mutually exclusive by stage/source. | Overlay extent and owner at any subrange require the exact stage/source artifact. No global owner is assigned merely from the VA. |
| Current stage resource-file base slot <code>0x802F82B8</code> | <code>dynamic</code> | Stage-loading code stores the current resource-file base used by ordinary-pickup selector lookup. | The pointed-to allocation address/extent depends on the loaded stage/resource file. |
| Toasty dynamic texture proof | <code>proof-only</code> / <code>dynamic</code> | The proven CI8 path requested a dynamic 78x85 texture with 96-byte stride, <code>0x1FE0</code> image bytes. | Returned backing address and production lifetime are not a fixed reusable allocation; final feature integration remains pending. |
| Direction-facing v02 expansion slice | <code>proof-only</code> / reserved-pool suballocation | Build-time allocator assigns <code>[0x801AF820,0x801AFA88)</code>, 616 bytes, inside <code>rdram.production.expansion_pool</code>. File <code>0x1A</code> raw-loads the module there and control hooks enter its KSEG1 alias. | Runtime-confirmed only for the tested v02 control route. This is a proof suballocation, not a current production feature owner; the parent 15 KiB expansion pool remains the production owner until product integration is separately approved/validated. |

### TEST LAB cross-stage materialization stress evidence

The 2026-09-28 TEST LAB line provides bounded **runtime composition** evidence, not new production allocations. Detailed chronology belongs to [TEST LAB proof history](Test-Lab-Proof-History).

Proof-local high-ROM resource relocation used `0x00F00000` as disposable backing in the successful Fire-resource experiments. This address remains **proof-only**; the clean `0xFF` contents used by those builders do not establish production ownership.

Important runtime observations:

- v27's ten-key native-Fire-file composition entered successfully;
- v28's all-21 composition with resource size about `0x8F0C` progressed to an emulator-core SI/PIF DMA error and is Rejected as memory-unsafe;
- v29's all-21 low-RAM resource was only `0x4634`, yet still hung at Mission Objective and later exhibited music-speed corruption;
- v31 kept the same low-RAM resource family with 15 live non-Earth actors and entered successfully;
- v33's recognizable 15-live non-Earth proof used a resource size of `0x4BE4`.

These observations reject a simple rule of the form **resource bytes < historical arena headroom => safe**. The loaded stage resource, live pickup actors/processes, dynamic textures, render allocations, stage-entry temporaries, and other arena consumers compose at runtime.

No universal safe pickup-count threshold follows from the current data. Ten and fifteen have successful bounded routes; the rejected 21-item routes differ in more than count, and Earth remained a confound in v30.

Production materialization must therefore use explicit composition budgets and failure bounds rather than promoting any disposable TEST LAB size/count as a global limit.

## Confirmed-free status

**Reusable <code>confirmed-free</code> intervals currently exposed by this map: none.**

This is not evidence that the ROM or RDRAM has no free bytes. It means the current evidence reviewed for this task does not justify promoting an unowned interval to production-reusable <code>confirmed-free</code> under the required lifecycle/reference standard.

Notable examples:

- the former selector cave/tail is now part of <code>rom.production.inventory_helper_cave</code>;
- the bootstrap cave is fully reserved through <code>0x9AF20</code>;
- the former high-ROM title reservation <code>[0xF90000,0xFC1000)</code> is retired by the in-place typeset title; it is not promoted to <code>confirmed-free</code> merely because the title no longer writes it;
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

Expected containment such as the V2 sub-owners inside the first 1 KiB of the 16 KiB reservation is documented explicitly rather than represented as duplicate top-level coverage.

## Initial coverage and deliberate unknowns

Coverage here means only the union of the bounded **current stock/protected/production interval rows above**. It is not a claim that everything outside those rows is unused.

- ROM bounded current coverage: <code>0xF18E0</code> bytes (989,408 bytes), about **5.90%** of the 16 MiB image. The compact-rainbow change removes <code>0x459E0</code> bytes of duplicated fighter data and adds only the <code>0x58</code>-byte shared-file loader wrapper outside the 8 KiB bank, for a net bounded-coverage reduction of <code>0x45988</code> bytes.
- RDRAM bounded fixed coverage: <code>0x4720</code> physical bytes (18,208 bytes), about **0.434%** of 4 MiB.
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

## Relationship to MKMSZR Project Atlas

Allocation ownership and decomp/readiness answer different questions.

- Decompiled or well-understood stock bytes are still owned.
- Unknown/black decomp space is still protected; unknown does not mean free.
- A <code>confirmed-free</code> allocation claim, if one is added later, does not imply decompilation completeness.
- A production cave/allocation is an ownership overlay, not a decomp-readiness score.
- Overlay reuse remains stage-qualified.

[MKMSZR Project Atlas](https://github.com/smeagol44/MKMSZR-Project-Atlas) is a derivative visualization of this page and other canonical Wiki owners. Its ROM/RDRAM views snapshot bounded intervals from this page and retain the source commit for provenance; the Wiki remains authoritative. Atlas updates must not infer free space from gaps, padding, or unclassified cells.

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
