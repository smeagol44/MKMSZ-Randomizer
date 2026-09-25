# Address and patch-site registry

> **Scope:** This page is the canonical owner for **exact guarded ROM edits**: patch location, expected/original bytes or guard condition, replacement/effect, and the feature that performs the edit.
>
> It does **not** decide whether a continuous ROM/RDRAM interval is available or who owns a cave/reservation. Continuous ownership, lifecycle, conflicts, and production-safe bounds belong to [Memory and allocation map](Memory-and-Allocation-Map). Function meanings belong to [Function registry](Function-Registry).

All ROM offsets are for the clean USA Rev. 0 `.z64` image. “Production” means current browser/CLI pipeline ownership; proof-only sites are not written by the product. Multi-byte generated bodies may be validated by implementation/tests instead of reproducing every emitted word here, but their guarded write site and effect remain indexed here.

## Production guarded edits

| ROM site | VA / context | Owner | Expected / guard | Replacement / effect |
|---:|---:|---|---|---|
| `0x0000DD60` | — | Stage selector | `0x2414000A` | Last compact menu index becomes `7` |
| `0x0000DD64` | — | Stage selector | `0x2A82000B` | Entry count becomes `8` |
| `0x0000E028` | — | Stage selector | JAL `0x8002830C` | JAL debug menu `0x8000D0B8` |
| `0x00015CD0` | — | Stage selector | load from `0x800C11E0` | JAL compact-index mapper |
| `0x0001674C` | — | Four-box input | `3C03802F 9463CE18` | Call switching action routine, then resume `0x80015B54` |
| `0x0001C9A0..0x0001C9AF` | `0x8001BDA0` | Rainbow outfit | guarded first four frame-setup instructions | `rainbow` mode only: tail-jump through uncached helper `0xA01AF700`, which replays displaced instructions and resumes `0x8001BDB0` |
| `0x0002EB28` | `0x8002DF28` | Toasty production trigger | `0C00B81E 03C02821` | JAL shared Toasty dispatcher; only qualifying successful/unblocked reactions arm the comment countdown |\n| `0x0005CCE0` | `0x8005C0E0` | Toasty stage init | `3C048029 8C841C10` | Jump through production-owned selector padding to load file `0x1A` and initialize Toasty |\n| `0x0005D2E0` | `0x8005C6E0` | Toasty HUD compositor | `0C007AB9 A0C20046` | JAL shared Toasty dispatcher while preserving the stock HUD submission path |\n| `0x000396CC` | `0x80038ACC` | Persistence | `3C03800A 8C63A910` | Restore collected flags, resume `0x80038AD4` |
| `0x0003A018` | `0x80039418` | Persistence | `ACA2002C` | Capture stage/ordinal after collected store while preserving displaced store |
| `0x0005D9CC` | HUD function | Box indicator | JAL `0x8001EAE4` | JAL native box-indicator wrapper |
| `0x00066F60..0x00066F67` | arena construction | Arena reservation | `3C02801B 2442F420` | `3C02801B 24423420` = floor `0x801B3420` |
| `0x00066FE0` | `0x800663E0` | Bootstrap | guarded native sequence | Call native bootstrap stub |
| `0x00066FE4..0x00066FEB` | second stock arena construction / bootstrap precondition | Arena reservation + bootstrap | `3C02801B 2442F420` | ArenaReservation guards the full pair and changes the low immediate to `0x3420`; the later bootstrap hook supersedes `0x66FE4` with its delay-slot NOP while the generated stub establishes the same `0x801B3420` floor |
| `0x0007A3F4` | `0x800797F4` | Logo bypass | `0C01F113 00000000 0C01F143 00000000 0C018576 24040080` | first word `0x10000003` (`beq zero,zero,+3`); preserves fade/title |
| `0x0007B900..0x0007B94B` | `0x8007AD00` | Four-box mask | guarded stock sanitizer body | Replace with stage-local key mask-copy routine |
| `0x0007B94C..0x0007B97F` | `0x8007AD4C` | Four-box load | guarded stock default-loader body | Rebuild live inventory from authoritative backing box |
| `0x0009B7DC` | `0x8009ABDC` | Stage selector | 12 stock pointers | Eight safe stage labels plus zeros |
| `0x000A5148` | file entry `0x1A` | Toasty production transport | guarded clean zero entry | Conditionally points to packed module at `0x00F68000..0x00F6B31F` when donor assets are supplied |\n| `0x000A5154` | file entry `0x1B` | Native payload | guarded stock file-table entry | Point file `0x1B` at the production payload source/destination descriptor |
| `0x000A6BE4..0x000A6C0B` | `0x800A5FE4..0x800A600B` | Four-box keys | guarded obsolete default-inventory template | Write item-`0x0D..0x22` stage map |
| `0x000A6C48..0x000A6CEF` | `0x800A6048..0x800A60EF` | Four-box state | guarded stock data | Four backing boxes, active state, and `MKBX` magic |
| `0x000A6E88` | item-use table | Glass mask | `0x80071F58` | Inert `0x80071F50` |
| `0x000AF998..0x000AFA23` | boot strings | Branding | guarded legal-text storage | Product title, spaced RANDOMIZER, configurable `<CHAR> EDITION`, 2026 credit, seeded joke, author |
| `0x000AFA24..0x000AFA97` | `0x800AEE24..` | Box indicator | guarded legal-text region | Native wrapper and `BOX 1 OF 4` text |
| `0x000AFA98..0x000AFABB` | boot strings | Branding | guarded license text | `NOT LICENSED BY NINTENDO` |
| `0x0078E16C..` | palette data | Outfit | guarded 64-color BGR555 source palette | Transform clothing indices `0x21..0x3F` |
| `0x0002EDA8` | `0x8002E1A8` | XP progression | `AC24200C` | NOP central XP store |
| `0x00054CE8` | `0x800540E8` | XP progression | `AC23200C` | NOP direct XP store |
| `0x00057D60` | `0x80057160` | XP progression | `AC23200C` | NOP direct XP store |
| `0x00057E2C` | `0x8005722C` | XP progression | `AC23200C` | NOP direct XP store |
| `0x00063704` | combo XP UI | XP progression UI | JAL native text renderer | Suppress combo EXPERIENCE label |
| `0x00063724` | combo XP UI | XP progression UI | JAL native text renderer | Suppress combo EXPERIENCE value |
| `0x000A6FFC..` | `0x800A63FC` | XP progression | guarded signed stage-cap halfwords | Main-stage caps become `20000` |
| `0x000A5478` | file entry `0x5E` | Title branding | guarded stock file-table entry | Repoint title package to generated high-ROM copy |
| `0x000A5664` | file entry `0x87` | Rainbow outfit | stock `0x00748920..0x0078E300`, raw flag `0` | `rainbow` mode only: repoint intact Sub-Zero file plus 64-palette bank to `0x00F20000..0x00F679E0` |
| `0x000B3364` palette base | `0x800B2764` | Title branding | selected guarded Candidate-B-unused CI8 entries | Replace 15 entries with grayscale antialias ramp |

Boot string pointer instructions live at ROM `0x7A22C`, `0x7A250`, `0x7A274`, `0x7A298`, `0x7A2BC`, `0x7A2E0`, `0x7A304`, `0x7A328`, `0x7A34C`, `0x7A370`, and `0x7A394`; every instruction is guarded before replacement.

## Allocation-backed generated writes

The following production writers target continuous owned regions. Their **exact interval bounds, aliases, lifecycle, containment, and conflict status are deliberately not duplicated here**; use the named Memory Map region as the canonical allocation record.

| Memory Map region | Writer / guard | Patch effect |
|---|---|---|
| `rom.production.inventory_action_cave` | `inventory_boxes.py`; guarded cave bytes and CI bounds | Emit the four-box action routine |
| `rom.production.inventory_helper_cave` | `inventory_boxes.py`; guarded former selector-cave tail and CI bounds | Emit switch/mask helper composition |
| `rom.production.bootstrap_composite` | native payload/persistence/flow writers; guarded pre-production bytes and capacity checks | Emit bootstrap, persistence helpers/tables, relocated selector mapper, and selector-only save-bypass write |
| `rom.production.payload_source` | output-expansion guard plus exact Runtime V2 size checks | Emit the reloadable `0x3B0`-byte Runtime V2 code payload |
| `rom.production.rainbow_file_87` | `rainbow_palette.py`; guarded stock file entry, frame-setup bytes, destination `FF` capacity, and exact bank size | `rainbow` mode only: copy stock file `0x87` intact and append 64 full BGR555 palettes |
| `rom.production.title_high` | title builder capacity/clean-output guard | Emit the recompressed generated file `0x5E` package |

Runtime-only slices such as the Runtime V2 inventory/XP payload subranges and persistent state are **not ROM patch sites**. Their canonical bounds and ownership remain only in the Memory Map; Core Runtime owns how those slices compose.

## Title branding boundary

The corrected title implementation is **Runtime-confirmed** through the full production pipeline and is data-only. Its file-entry and palette edits are indexed above, while the generated package allocation is `rom.production.title_high` in the Memory Map.

The stock START setup at ROM `0x00079C24..0x00079C2B` is intentionally left untouched and therefore is not a patch-site row. The rejected executable-wrapper attempt beginning at `0x9ADE0` is documented as an allocation conflict in the Memory Map; it is not current production.

## Proof-only sites

| ROM/VA | Proof | Status |
|---|---|---|
| ROM `0x0002EB28` / VA `0x8002DF28` | Toasty v43 successful-reaction hook | Implementation/static-confirmed; runtime Pending. Guard: `0C00B81E 03C02821` (`jal 0x8002E078`; `move a1,fp`). v43 replaces only the JAL with a proof trampoline and preserves the delay instruction; wrapper filters resolved callbacks `08/0E/12/13/14/15/17` then calls the original transfer unchanged. |
| ROM `0xB44AA` / RAM `0x800B38AA` | First ordinary Fire enemy type `0x0A -> 0x09` | Runtime-confirmed, not production |
| Fire resource entry ROM `0xA52E0` | Relocated/expanded Fire pickup resources | Runtime-confirmed architecture proof |
| VA `0x8008EAEC` / ROM `0x8F6EC` | Dedicated Prison-key award callback | Runtime-confirmed proof; conflicts with production allocation `rom.production.inventory_action_cave` |
| Fire overlay tail ROM `0xE2148..0xE216B` | Foreign fighter file load/allocation sequence | Runtime-confirmed monk import proof |
| Seven Fire type-`0x0A` halfwords | Replace ordinary Fire Hulk types with Temple monk type `0x01` | Runtime-confirmed bounded proof |
| ROM `0x00029FB0` / VA `0x800293B0` | Direction-facing v02 mismatch decision hook | Runtime-confirmed proof; replaces `8C640704 24020305` with JAL to static KSEG0 trampoline + NOP, then expansion KSEG1 helper preserves/changes the stock forward-vs-back decision |
| ROM `0x0002A0DC` / VA `0x800294DC` | Direction-facing v02 active-backward release hook | Runtime-confirmed proof; replaces `8C820638 94430000` with JAL trampoline + NOP so releasing Turn can leave backward mode without a direction repress |
| ROM `0x0003E46C` / VA `0x8003D86C` | Direction-facing v02 standalone Turn gate | Runtime-confirmed proof; replaces `27BDFFE0 24040001` with a jump to a static trampoline that suppresses standalone Turn only for the player semantic controller |
| ROM `0x000A5148` / global file entry `0x1A` | Direction-facing v02 expansion transport | Runtime-confirmed proof; clean zero entry points to proof module ROM `0x00F72000..0x00F72268`, raw-loaded to `0x801AF820` and executed via KSEG1 |
| ROM `0x0009ADB8` plus `0x0009ADE8..0x0009AEBF` | Direction-facing v02 proof loader/trampolines | Runtime-confirmed proof composition; bootstrap temporarily loads file `0x1A`, and the former static pickup-capture-helper footprint becomes bounded loader/trampoline storage while the capture helper itself moves into the expansion module |
| ROM `0x4BBF0`, `0x4BBFC`, `0x4BC00` (v75) | Sektor projectile placement | Runtime-confirmed bounded v75: `addiu a1,zero,5`; `addiu a2,zero,38`; JAL `0x80031208`. v78 redirected the call to its `0x80031394` shim and hard-hung; no placement production edit is accepted |
| ROM `0x4C484..0x4C488` and `0x9AE90..0x9AF1F` (v75) | Sektor child entry and per-tick velocity | Runtime-confirmed bounded v75: child jump `0x8009A290`, delay preload `lui t2,0x800A`, child callback `0x8009A2C8`, initial `0x46666`, cap `0xEEEEE`; the source interval conflicts with production bootstrap ownership. Guarded by exact v73 hash in the builder |
| ROM `0x9ADEC`, `0x9AE2C..0x9AE54`, `0x4BD14/30/4C/68/84/A0`, `0x4B728`, `0xB0234..0xB0243` (v79) | Combined chest cursor, projectile selector, sleeps, screen tint and strike-record proof | Rejected / failed hard hang. These are proof-only edits from exact v75, with individual causes unresolved. See [Sektor takeover proof history](Sektor-Takeover-Proof-History); do not reuse these as independently verified edits |
| Relocated file-`0x87` ROM `0xF40DBC` (v80/v81) | Live slot-`0x24` token-`0x0B` resource-actor constructor operand | Exact v75 guard `0x00034A58`; v80/v81 set `0x0004E6E4` (genuine imported rocket entry). v80 is Runtime-confirmed stable but visually ineffective by itself; this proves only that descriptor replacement alone is insufficient. |
| ROM `0x315E8` / VA `0x800309E8` (v81/v82 diagnostic) | Token-`0x0B` newly constructed actor selector store before insertion | Exact v75 `A602009E` = `sh v0,0x9E(s0)`; v81/v82 use `A600009E` = `sh zero,0x9E(s0)` while preserving the preceding `0x8001C528` call. v81 Runtime-confirms this removes the one-frame blue projectile fallback but leaves the rocket corrupted, proving selector-only rebinding is incomplete. Disposable diagnostic only; not an accepted production/global edit. |
| ROM `0x315EC..0x31603` / VA `0x800309EC..0x80030A03` (v82 diagnostic) | Pre-insertion selector-0 active-handle coherence | Runtime-confirmed stable negative control: no visible change from v81. Stale `+0x80` alone is rejected as the corruption cause. This edit is superseded and not reusable as an independently validated palette fix. |
| ROM `0x316C8` / VA `0x80030AC8` plus proof ROM `[0x9AE10,0x9AE90)` (v83) | Post-init/pre-insertion raw frame bind | Runtime-confirmed stable negative result: direct `0x8001BDA0` rocket bind before insertion leaves the initial Ice/Sektor projectile frame and Ice-blue missile unchanged. This raw frame-setup seam is insufficient. |
| ROM `0x316C8` / VA `0x80030AC8` plus proof ROM `[0x9AE10,0x9AE90)` (v84) | Contextual pre-insertion rocket bind | Redirects token insertion through a shim that invokes the same contextual first-frame transaction used later by v75: projectile current at controller `+0x6E0`, selector 0, controller cursor `+0x6E4 = actor+0x98+0xD90`, full `0x800304C0` advance, cursor restore, owner restore, then original `0x80024650`. Child code at `0x9AE90..` is byte-preserved. Implementation/static-confirmed; Runtime Pending. |

Proof rows identify exact edits useful for reproduction; they do not grant allocation ownership. Where a proof overlaps current production, the Memory Map owns that conflict statement.

## Frontend save-bypass payload

The relocated selector mapper emitted inside `rom.production.bootstrap_composite` is exactly:

```text
3C03800C 8C6311E0 2C610006 50200001
24630002 3C028029 03E00008 A0441C0C
```

It reads the compact index, adds 2 for indices `6` and `7`, and writes nonzero byte `0x15` to `0x80291C0C` in the return delay slot. That is the game's native one-shot stage-entry save bypass; `0x800798A8` and all later/manual save flows remain unchanged.

## Related canonical owners

- [Memory and allocation map](Memory-and-Allocation-Map) — continuous ROM/RDRAM intervals, availability, lifecycle, conflicts, and production ownership.
- [Core runtime and native payload](Core-Runtime-and-Address-Database) — bootstrap/payload architecture and runtime composition.
- [Function registry](Function-Registry) — function semantics.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — file-table, overlay, and resource-loading grammar.
- [Address quick reference](Address-Quick-Reference) — derivative convenience subset only.
