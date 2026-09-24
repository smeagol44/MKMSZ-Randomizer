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
| `0x000396CC` | `0x80038ACC` | Persistence | `3C03800A 8C63A910` | Restore collected flags, resume `0x80038AD4` |
| `0x0003A018` | `0x80039418` | Persistence | `ACA2002C` | Capture stage/ordinal after collected store while preserving displaced store |
| `0x0005D9CC` | HUD function | Box indicator | JAL `0x8001EAE4` | JAL native box-indicator wrapper |
| `0x00066F60..0x00066F67` | arena construction | Arena reservation | `3C02801B 2442F420` | `3C02801B 24423420` = floor `0x801B3420` |
| `0x00066FE0` | `0x800663E0` | Bootstrap | guarded native sequence | Call native bootstrap stub |
| `0x00066FE4..0x00066FEB` | second stock arena construction / bootstrap precondition | Arena reservation + bootstrap | `3C02801B 2442F420` | ArenaReservation guards the full pair and changes the low immediate to `0x3420`; the later bootstrap hook supersedes `0x66FE4` with its delay-slot NOP while the generated stub establishes the same `0x801B3420` floor |
| `0x0007A3F4` | `0x800797F4` | Logo bypass | `0C01F113 00000000 0C01F143 00000000 0C018576 24040080` | first word `0x10000003` (`beq zero,zero,+3`); preserves fade/title |
| `0x0007B900..0x0007B94B` | `0x8007AD00` | Four-box mask | guarded stock sanitizer body | Replace with stage-local key mask-copy routine |
| `0x0007B94C..0x0007B97F` | `0x8007AD4C` | Four-box load | guarded stock default-loader body | Rebuild live inventory from authoritative backing box |
| `0x0009B7DC` | `0x8009ABDC` | Stage selector | 12 stock pointers | Eight safe stage labels plus zeros |
| `0x000A5154` | file entry `0x1B` | Native payload | guarded stock file-table entry | Point file `0x1B` at the production payload source/destination descriptor |
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
| ROM `0xB44AA` / RAM `0x800B38AA` | First ordinary Fire enemy type `0x0A -> 0x09` | Runtime-confirmed, not production |
| Fire resource entry ROM `0xA52E0` | Relocated/expanded Fire pickup resources | Runtime-confirmed architecture proof |
| VA `0x8008EAEC` / ROM `0x8F6EC` | Dedicated Prison-key award callback | Runtime-confirmed proof; conflicts with production allocation `rom.production.inventory_action_cave` |
| Fire overlay tail ROM `0xE2148..0xE216B` | Foreign fighter file load/allocation sequence | Runtime-confirmed monk import proof |
| Seven Fire type-`0x0A` halfwords | Replace ordinary Fire Hulk types with Temple monk type `0x01` | Runtime-confirmed bounded proof |
| ROM `0x00029FB0` / VA `0x800293B0` | Direction-facing v02 mismatch decision hook | Runtime-confirmed proof; replaces `8C640704 24020305` with JAL to static KSEG0 trampoline + NOP, then expansion KSEG1 helper preserves/changes the stock forward-vs-back decision |
| ROM `0x0002A0DC` / VA `0x800294DC` | Direction-facing v02 active-backward release hook | Runtime-confirmed proof; replaces `8C820638 94430000` with JAL trampoline + NOP so releasing Turn can leave backward mode without a direction repress |
| ROM `0x0002A658` / VA `0x80029A58` | Direction-facing v05 player-loop Turn suppression | Pending runtime; guarded stock `0x14400007` (`bne v0,zero,+7`) becomes `0x10000007` (`beq zero,zero,+7`). The delay slot still sets the stock `s8` Turn latch, but execution always skips the direct actor `+0x8C XOR 0x10` facing toggle. |
| ROM `0x0003E46C` / VA `0x8003D86C` | Direction-facing v02-v04 attempted Turn gate | **Rejected / failed for visible player Turn.** Player-gated and unconditional-return variants did not remove the observed turn; this site is not the player-loop facing toggle. |
| ROM `0x000A5148` / global file entry `0x1A` | Direction-facing expansion transport | v02 Runtime-confirmed with module `0x00F72000..0x00F72268`; v05 Pending runtime with smaller module `0x00F72000..0x00F72220`. Both raw-load at `0x801AF820` and execute through KSEG1. |
| ROM `0x0009ADB8` plus bounded former capture-helper footprint | Direction-facing proof loader/trampolines | v02 Runtime-confirmed bootstrap/file-`0x1A` transport. v05 retains loader + capture/decision/release trampolines but removes the disproven Turn trampoline; the capture helper remains inside the expansion module. |

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
