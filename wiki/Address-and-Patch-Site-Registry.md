# Address and patch-site registry

**Inventory-HUD v20 guard (2026-10-05):** exact v19 SHA `aafcc7e26ecd77b04a3882cee9569161f8059d92af1fce003ac3e68e08406277`; ROM `0x00074F08` / VA `0x80074308` / alias `0xA0074308`: expected `00000000` → `24041200` (`addiu a0,zero,0x1200`). This initializes the first-load HUD allocation size in the null-branch delay slot without changing allocation ownership. Exact v20 SHA `3461ed86540d51881f5f7d1b45c17dee9113484889370c8af750b819a11b1daa`; CRC1/CRC2 `479EDF13 / E1BE6C34`. **Runtime-confirmed bounded:** the user reports the TEST LAB Inventory hang is fixed on v20. See [TEST LAB Inventory diagnosis](Test-Lab-Inventory-Hang-Static-Diagnosis).

**2026-10-01 lifecycle production:** accepted v06 promotes the static-closure sites at ROM `0x172CC`, `0x36178`, `0x36934`, `0x36B38`, `0x36BC0`, `0x2F984`, and `0x367B4`, plus the HP overwrite suppression at `0x2FA44` and fresh-run configuration words at `0xA6BA8..0xA6BAD`. Exact four-word guards and the Runtime-confirmed helper blob are enforced by `run_lifecycle.py` and tests. ROM `0x364EC` remains prohibited for reset. Production XP/Mission Objective restoration and the four-box default-loader replacement retain their existing owners.

> **Scope:** This page is the canonical owner for **exact guarded ROM edits**: patch location, expected/original bytes or guard condition, replacement/effect, and the feature that performs the edit.
>
> It does **not** decide whether a continuous ROM/RDRAM interval is available or who owns a cave/reservation. Continuous ownership, lifecycle, conflicts, and production-safe bounds belong to [Memory and allocation map](Memory-and-Allocation-Map). Function meanings belong to [Function registry](Function-Registry).

All ROM offsets are for the clean USA Rev. 0 `.z64` image. “Production” means current browser/CLI pipeline ownership; proof-only sites are not written by the product. Multi-byte generated bodies may be validated by implementation/tests instead of reproducing every emitted word here, but their guarded write site and effect remain indexed here.

## Production guarded edits

| ROM site | VA / context | Owner | Expected / guard | Replacement / effect |
|---:|---:|---|---|---|
| `0x0000DD60` | — | Stage selector | `0x2414000A` | Last compact menu index becomes `7` |
| `0x0000DD64` | — | Stage selector | `0x2A82000B` | Entry count becomes `8` |
| `0x0000DD70` | `0x8000D170` | Stage selector movement SFX | `24040050 24050014` | First word becomes JAL frontend-resident movement helper; original `li a1,0x14` remains in delay slot. Helper plays descriptor `0x1FC` only for a newly pressed single Up/Down edge and restores displaced draw arguments. |
| `0x0000E028` | — | Stage selector | JAL `0x8002830C` | JAL debug menu `0x8000D0B8` |
| `0x00015CD0` | — | Stage selector | load from `0x800C11E0` | JAL compact-index mapper |
| `0x0001674C` | — | Four-box input | `3C03802F 9463CE18` | Call switching action routine, then resume `0x80015B54` |
| `0x0001C9A0..0x0001C9AF` | `0x8001BDA0` | Rainbow outfit | guarded first four frame-setup instructions | `rainbow` mode only: tail-jump through uncached helper `0xA01AF700`, which replays displaced instructions and resumes `0x8001BDB0` |
| `0x0002EB28` | `0x8002DF28` | Toasty production trigger | `0C00B81E 03C02821` | JAL shared Toasty dispatcher; only qualifying successful/unblocked reactions arm the comment countdown |
| `0x0005CCE0` | `0x8005C0E0` | Toasty stage init | `3C048029 8C841C10` | Jump through production-owned selector padding to load file `0x1A` and initialize Toasty |
| `0x0005D2E0` | `0x8005C6E0` | Toasty HUD compositor | `0C007AB9 A0C20046` | JAL shared Toasty dispatcher while preserving the stock HUD submission path |
| `0x000396CC` | `0x80038ACC` | Persistence | `3C03800A 8C63A910` | Restore collected flags, resume `0x80038AD4` |
| `0x000172CC..0x000172DB` | `0x800166CC` | Lifecycle v06 Pause Quit | Guard stock four-word Quit->Yes teardown call | Transfer to uncached helper, snapshot living HP/resources/inventory, replay stock teardown contract |
| `0x00036178..0x00036187` | `0x80035578` | Lifecycle v06 failure root | Guard `27BDFFA0 AFB30044 00009821 AFBF005C` | Commit inventory, classify failure/demo, invalidate living HP token, preserve stock death/Continue graph |
| `0x00036934..0x00036943` | `0x80035D34` | Lifecycle v06 alternate reconstruction | Guard `27BDFFE0 AFB00010 00808021 3C02802F` | Classify living/failure reconstruction through uncached helper |
| `0x00036B38..0x00036B47` | `0x80035F38` | Lifecycle v06 valid-preserving reconstruction | Guard `3C02802F 8C42CE20 27BDFFE8 AFBF0010` | Capture living state before teardown/reconstruction |
| `0x00036BC0..0x00036BCF` | `0x80035FC0` | Lifecycle v06 stage completion | Guard `27BDFFE8 24040012 2402001A AFBF0010` | Capture living HP/resources, commit active inventory box, arm one-shot re-entry |
| `0x0002F984..0x0002F993` | `0x8002ED84` | Lifecycle v06 player constructor | Guard `3C04802C 8C841AC0 3C02800C 844211F8` | Consume one-shot living re-entry and seed native HP carrier before stock HP branch |
| `0x0002FA44` | `0x8002EE44` | Lifecycle v06 HP preservation | `A4A20654` | NOP redundant second full-HP store; fresh/death/Continue full HP remains at earlier stock constructor branch |
| `0x000367B4..0x000367C3` | `0x80035BB4` | Lifecycle v06 final Game Over | Guard `0C00A1E5 24040004 8FA7002C 00002021` | Classified terminal reset, then replay stock yield/title chain |
| `0x000A6BA8..0x000A6BAD` | `0x800A5FA8..0x800A5FAD` | Lifecycle run settings | Stock halfwords `2 / 3 / 1` | Build-time difficulty `0..4` (Very Easy..Very Hard), lives `1..10`, continues `0..5`; defaults `4 / 5 / 3`. Exact Runtime-confirmed v06 reference was `4 / 9 / 5`. |
| `0x00016354` | `0x80015754` | Production TURN action gate | `A62406DC 3C058003` | Jump to guarded v10/v06 action-install helper; suppress player states 23/24 only when effective LOCK is active |
| `0x00029FB0` | `0x800293B0` | Production TURN direction decision | `8C640704 24020305` | JAL production TURN decision trampoline; TOGGLE follows stock, LOCK uses accepted v10 facing correction while preserving stock forced-facing authority |
| `0x0002A0DC` | `0x800294DC` | Production TURN release path | `8C820638 94430000` | JAL leaf-only v06 release helper; forced-facing fallback uses bounded direct controller-list scan |
| `0x000770B8` | frontend OPTIONS -> GAME SETTINGS call | Production GAME SETTINGS wrapper | `0C01D9AF 02402021` | JAL frontend-resident wrapper; mirrors durable TURN bit into the stock editor and commits it on return; does not load gameplay expansion file |
| `0x00077480..0x000775DB` | GAME SETTINGS right-edit body | Production GAME SETTINGS frontend | guarded stock edit body | Five-setting TURN/ATTACK/SPECIALS/JUMP/RUN right-edit dispatcher plus JUMP/RUN draw helper |
| `0x00077600..0x0007769B` | GAME SETTINGS left-edit body | Production GAME SETTINGS frontend | guarded stock edit body | Five-setting TURN/ATTACK/SPECIALS/JUMP/RUN left-edit dispatcher |
| `0x00077888..0x0007790F` | GAME SETTINGS value draws | Production GAME SETTINGS frontend | guarded stock Lives/Continues draw bodies | Draw ATTACK and SPECIALS enum values at compact coordinates |
| `0x00077910..0x0007791B` | GAME SETTINGS loop tail | Production GAME SETTINGS frontend | `24080002 AFD006F4 AFC806F8` | JAL JUMP draw/cursor helper + NOPs; v04 owns all three words so stock cannot overwrite cursor type |
| `0x000AF824..0x000AF833` | GAME SETTINGS cursor coordinate table | Production GAME SETTINGS frontend | guarded stock type-2 four-entry table | Five-setting cursor coordinates; RUN/EXIT use stock OPTIONS cursor type 0 |
| `0x0003A018` | `0x80039418` | Persistence | `ACA2002C` | Capture stage/ordinal after collected store while preserving displaced store |
| `0x00039FD4..0x00039FDB` | `0x800393D4..0x800393DB` | Global materializer acquisition re-mask | `00121040 00521021` | PR #126 integration candidate: JAL shared file-`0x1A` acquisition-remask helper + replay first displaced instruction; helper commits LIVE inventory to backing then reconstructs stage-masked LIVE before replaying the second displaced instruction. v03 Runtime-confirmed at relocated helper `0x801B0970..0x801B0A5F`; merge pending. |
| `0x0005D9CC` | HUD function | Box indicator | JAL `0x8001EAE4` | JAL native box-indicator wrapper |
| `0x00066F60..0x00066F67` | arena construction | Arena reservation | `3C02801B 2442F420` | `3C02801B 24423420` = floor `0x801B3420` |
| `0x00066FE0` | `0x800663E0` | Bootstrap | guarded native sequence | Call native bootstrap stub |
| `0x00066FE4..0x00066FEB` | second stock arena construction / bootstrap precondition | Arena reservation + bootstrap | `3C02801B 2442F420` | ArenaReservation guards the full pair and changes the low immediate to `0x3420`; the later bootstrap hook supersedes `0x66FE4` with its delay-slot NOP while the generated stub establishes the same `0x801B3420` floor |
| `0x0007A3F4` | `0x800797F4` | Logo bypass | `0C01F113 00000000 0C01F143 00000000 0C018576 24040080` | first word `0x10000003` (`beq zero,zero,+3`); preserves fade/title |
| `0x0007B900..0x0007B94B` | `0x8007AD00` | Four-box mask | guarded stock sanitizer body | Replace with stage-local key mask-copy routine |
| `0x0007B94C..0x0007B97F` | `0x8007AD4C` | Four-box filtered SAVE | guarded stock default-loader body | Commit non-Glass LIVE slots to the active authoritative backing box; LIVE reconstruction is the separately owned mask wrapper/sanitizer |
| `0x0009B7DC` | `0x8009ABDC` | Stage selector | 12 stock pointers | Eight safe stage labels plus zeros |
| `0x000B21D8..0x000B2211` | selector cursor palette | Stage selector presentation | Guarded clean 29-entry orange palette; count word at `0x000B21D4 = 0x1D` | Replace all 29 BGR555 entries with the separately guarded title-cursor palette from `0x000B32E8`; selector file `0x5F` and sprite frames remain unchanged. |
| `0x0001645C`, `0x00029DDC`, `0x0002BDF8`, `0x0002BA5C` | SPECIALS / standing Jump / moving Jump / ledge | Modern controls | Guarded stock call/decision sequences | Route selected controls through file-`0x1A` helpers; Slide/Super Slide retain native progression recognizers |
| `0x0001674C`, `0x00029FD8`, `0x0002A0A0`, `0x0002A738`, `0x0002A7C4`, `0x0002A378` | input capture / Run calls and active Run loop | Modern RUN | Guarded stock hook/calls/back-edge | Snapshot physical Run after remap, interpose HOLD/AUTO predicate and preserve running Jump classifier |
| `0x00015738`, `0x0002A848`, `0x00033410`, `0x0004E3AC` | modern Attack event, steady Block, startup Block, combo | Modern ATTACK | Guarded stock hook/call sequences | Event translation, Block+Attack cancellation and native combo parser |
| `0x000A5148` | file entry `0x1A` | Shared TURN / modern controls / optional Toasty transport | guarded clean zero entry | Starts at `0x00F68000` for TURN; controls extend the low file through `0x00F69060`, and optional CI4 Toasty extends it through `0x00F6B5D0`. Loaded only at stage init. |
| `0x000A5154` | file entry `0x1B` | Native payload | guarded stock file-table entry | Point file `0x1B` at the production payload source/destination descriptor |
| `0x000A6BE4..0x000A6C0B` | `0x800A5FE4..0x800A600B` | Four-box keys | guarded obsolete default-inventory template | Write item-`0x0D..0x22` stage map |
| `0x000A6C48..0x000A6CEF` | `0x800A6048..0x800A60EF` | Four-box state | guarded stock data | Four backing boxes, active state, and `MKBX` magic |
| `0x000A6E88` | item-use table | SEALED mask (stock Glass ID `0x08`) | `0x80071F58` | Inert `0x80071F50` |
| `0x000AE40C..0x000AE413` | stock item-name text | Foreign-key placeholder label | `GLASS\0\0\0` | `SEALED\0\0`; native item identity remains `0x08` and its inert-use dispatch remains unchanged. |
| generated progression records `+0x28` | ordinary pickup presentation pointer | Power Upgrade Herbs visual | stock Herbs `0x800B1D38` | `0x800B1E68`, a stock-resident 16-color Ice Blue descriptor; stage-local Herbs resource/model selector remains unchanged. |
| `0x000B2A68..0x000B2A8B` / VA `0x800B1E68` | stock resident palette descriptor | Power Upgrade Herbs palette source | guarded retail 16-color descriptor | Read-only reuse; no palette bytes or allocation changed. |
| generated progression records `+0x18` | ordinary pickup callback pointer | Power Upgrade pickup feedback | existing progression callback `0xA01AF620` | production wrapper `0xA01B21E0`; wrapper calls the existing progression award first, then performs the Runtime-confirmed three 2-tick white pulses and returns. |
| `0x00615A14..0x00615A93` | Water resource palette data | Eel white-flash source | transparent index 0 + 63×`0x7FFF` white | Guarded read-only source copied into MKMSZR file-`0x1A`; no Water overlay code/state is imported. |
| `0x00F6A940..0x00F6AAEF` / runtime `0x801B2160..0x801B230F` | shared file `0x1A` | Power Upgrade flash module | clean ROM `0xFF` guarded suballocation inside reserved expansion pool | 128-byte white palette + 304-byte accepted v02 visual helper; no damage/stun/input-lock semantics. |
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
| `0x000A5664` | file entry `0x87` | Rainbow outfit | stock `0x00748920..0x0078E300`, raw flag `0` | Compact rainbow deliberately leaves this entry unchanged; guards verify retail ownership |
| `0x000B3364` palette base | `0x800B2764` | Title branding | selected guarded Candidate-B-unused CI8 entries | Replace 15 entries with the shared dark-to-light icy-blue art/edition ramp; index `0xFF` stays the stock background |

Boot string pointer instructions live at ROM `0x7A22C`, `0x7A250`, `0x7A274`, `0x7A298`, `0x7A2BC`, `0x7A2E0`, `0x7A304`, `0x7A328`, `0x7A34C`, `0x7A370`, and `0x7A394`; every instruction is guarded before replacement.

The selector movement helper itself occupies production-owned ROM `[0x0000E27C,0x0000E2B0)`; continuous ownership is canonical in the Memory Map. Production intentionally has **no confirmation-SFX edit**: v02's A-edge `0x1FD` experiment is Rejected / failed and the Start-owned commit path remains stock apart from the established compact-index mapper/save-bypass behavior.

## Allocation-backed generated writes

The following production writers target continuous owned regions. Their **exact interval bounds, aliases, lifecycle, containment, and conflict status are deliberately not duplicated here**; use the named Memory Map region as the canonical allocation record.

| Memory Map region | Writer / guard | Patch effect |
|---|---|---|
| `rom.production.inventory_action_cave` | `inventory_boxes.py`; guarded cave bytes and CI bounds | Emit the four-box action routine |
| `rom.production.inventory_helper_cave` | `inventory_boxes.py`; guarded former selector-cave tail and CI bounds | Emit switch/mask helper composition |
| `rom.production.bootstrap_composite` | native payload/persistence/flow writers; guarded pre-production bytes and capacity checks | Emit bootstrap, persistence helpers/tables, relocated selector mapper, and selector-only save-bypass write |
| `rom.production.payload_source` | output-expansion guard plus exact Runtime V2 size checks | Emit the reloadable `0x3B0`-byte Runtime V2 code payload |
| `rom.production.rainbow_bank` | `rainbow_palette.py`; guarded stock file entry, all 15 allocation/load sites, file-`0x92` entry, controls→Toasty gap, and exact bank size | `rainbow` mode only: keep stock file `0x87` in place, allocate `+0x2000`, and append the dedicated 64-palette bank at runtime |
| `rom.production.title_high` | title builder capacity/clean-output guard | Emit the recompressed generated file `0x5E` package |

Runtime-only slices such as the Runtime V2 inventory/XP payload subranges and persistent state are **not ROM patch sites**. Their canonical bounds and ownership remain only in the Memory Map; Core Runtime owns how those slices compose.

## Title branding boundary

The corrected title implementation is **Runtime-confirmed** through the full production pipeline and is data-only. Its file-entry and palette edits are indexed above, while the generated package allocation is `rom.production.title_high` in the Memory Map.

The stock START setup at ROM `0x00079C24..0x00079C2B` is intentionally left untouched and therefore is not a patch-site row. The rejected executable-wrapper attempt beginning at `0x9ADE0` is documented as an allocation conflict in the Memory Map; it is not current production.

## Power-order proof sites

| ROM/VA | Proof | Status |
|---|---|---|
| ROM `0x0003D62C` / VA `0x8003CA2C` | Slide tier gate | v02 Runtime-confirmed bounded proof. Clean word `28420002` becomes `28420001`, moving Slide from tier >=2 to tier >=1 while preserving the stock recognizer/action path. |
| ROM `0x0004B018..0x0004B033` / VA `0x8004A418..0x8004A433` | Ground Ice Blast tier-condition tail | v02 Runtime-confirmed bounded proof. Guarded in-place replacement changes only the native condition result from tier >=1 to tier >=2; Ice callback/action/resource behavior remains stock. |
| ROM `0x000A6BB0..0x000A6BB7` / RAM `0x800A5FB0..0x800A5FB7` | First two native Power Ups icon IDs | v02 Runtime-confirmed presentation proof. Swap stock Ice Blast / Slide entries so the first N icon strip matches the shuffled gameplay order. |
| ROM `0x000A78A0..0x000A78A7` | First two native Power Ups move-help pointers | v02 Runtime-confirmed presentation proof. Swap stock Ice Blast / Slide help/detail records so selection text/details match the shuffled icon order. |

The first-two v02 proof was generalized by Runtime-confirmed v04. The complete mapped tier-gate set used by the production implementation is:

| ROM/VA | Power | Stock tier / production edit |
|---|---|---|
| ROM `0x0003D62C` / VA `0x8003CA2C` | Slide | Stock `slti v0,v0,2`; replace immediate with generated Slide slot |
| ROM `0x0004B018..0x0004B033` / VA `0x8004A418..0x8004A433` | Ground Ice Blast | Guarded seven-word stock tier-1 return tail; replace in place with arbitrary generated Ice Blast threshold while preserving `0x8000/0x4000` condition convention |
| ROM `0x0004B084` / VA `0x8004A484` | Directional Ice Up | Stock tier 3 compare -> generated Directional Ice slot |
| ROM `0x0004B0F4` / VA `0x8004A4F4` | Directional Ice Down | Stock tier 3 compare -> same generated Directional Ice slot |
| ROM `0x0004AFBC` / VA `0x8004A3BC` | Air Ice Blast | Stock tier 4 compare -> generated Air Ice Blast slot |
| ROM `0x0004AEA8` / VA `0x8004A2A8` | Ice Clone | Stock tier 5 compare -> generated Ice Clone slot |
| ROM `0x000515A0` / VA `0x800509A0` | Ice Shatter contextual gate A | Stock tier 6 compare -> generated Ice Shatter slot |
| ROM `0x000535C4` / VA `0x800529C4` | Ice Shatter contextual gate B | Stock tier 6 compare -> same generated Ice Shatter slot |
| ROM `0x0003D728` / VA `0x8003CB28` | Super Slide | Stock tier 7 compare -> generated Super Slide slot |
| ROM `0x0005B5DC` / VA `0x8005A9DC` | Freeze on Contact | Stock tier 8 compare -> generated Freeze on Contact slot |
| ROM `0x0004B2B4` / VA `0x8004A6B4` | Polar Blast | Stock tier 9 compare -> generated Polar Blast slot |
| ROM `0x000A6BB0..0x000A6BD3` / RAM `0x800A5FB0..0x800A5FD3` | Power Ups icon table | Reorder all nine icon IDs to the generated power order |
| ROM `0x000A78A0..0x000A78C3` | Power Ups help/detail pointer table | Reorder all nine pointers to the same generated power order |

v04 Runtime-confirmed the generalized mechanism on its tested nine-slot order. The production generator imposes exactly one ordering constraint: Ice Shatter must follow at least one of Ice Blast / Directional Ice / Air Ice Blast. Slide and Super Slide are independent. Final whole-product all-tier runtime validation remains a release gate.

## Proof-only sites

| ROM/VA | Proof | Status |
|---|---|---|
| ROM `0x000CC540` / VA `0x802EEE60` | Temple scripted Map logical-award isolation | **Runtime-confirmed bounded v01.** Clean word `2404000D` loads Map item `0x0D` in the delay slot of the `jal 0x80075448` at ROM `0x000CC53C` / VA `0x802EEE5C`. v01 changes only this word to `24040004` (Herbs), preserving the scripted actor and later Temple progression path. User observed Herbs award and normal elevator/platform movement; Map visual remained stock by design. Proof SHA-256 `c9334451576af3b5b5492e4c9c1b8e514da1b35686cf3c7fb5c13cca9d58900e`, CRC1/CRC2 `C34304BE / 5C014BB5`. Proof establishes reward/progression separation, not arbitrary-reward visuals or production integration. |
| ROM `0x000CC358..0x000CC42B`, `0x000CC53C..0x000CC543` / Temple overlay VA `0x802EEC78..0x802EED4B`, `0x802EEE5C..0x802EEE63` | Temple scripted special-check v02 visual/persistence composition | **Runtime-confirmed bounded v02; promoted architecture.** The entry hook at `0xCC358` branches to dedicated special-state logic; visual edits retarget the scripted actor to Temple native Herbs palette/resource selector `15`; award call `0xCC53C` wraps `0x80075448` while delay slot `0xCC540` supplies item `0x04`. Collection commits MKSV flags bit `0x0001` and stock local word `0x8026E9A4=0x100`; re-entry resumes stock post-award loop `0x802EEE94` without re-award. User confirmed correct Herbs visual/award, elevator/rope, title re-entry persistence, and Temple -> Wind. Proof SHA-256 `d14380afe698d7daa9173a3295882e04f58e1bb747a88e33df33b32720118f66`. |
| ROM `0x00011C70..0x00011C83` / VA `0x80011070..0x80011083` | Proposed Stage-7 → normal Fire selector-5 composition positive control, **unbuilt** | Guard five clean words `27BDFF98 24020001 AFB3005C 24130001 24040007`; proposed replacement `24020005 3C01802C A42218F8 0800423F 00000000` sets `0x802C18F8=5` and tail-jumps to `0x800108FC`. This aliases Stage 7 to ordinary Fire and intentionally loses the debug opponent; it is not a native Stage-7 repair, not Runtime-confirmed, and not production. See [Stage flow and selector](Stage-Flow-and-Selector). |
| ROM `0x00039454` / VA `0x80038854` | Prison L1 key checkpoint-selector suppression | **Runtime-confirmed bounded v08.** Stock instruction commits selector `7` to `0x802C18F8`. v08 NOPs only this store while preserving inventory award and acquired bit 0; combined with the three direct generic-key presentation-spawn suppressions, runtime shows `G4 S2 B1`, normal L1 door opening, and natural no-checkpoint respawn after death. Prison-L1-specific proof only; not yet a generic key policy. |
| ROM `0x000E5C28` / VA `0x802F0ED8` | Fire key checkpoint-presentation suppression | **Runtime-confirmed bounded Fire v01.** Stock JAL requests `0x8002830C(0x15,0x80062D60)` from the shared Fire key callback. v01 NOPs only this JAL while retaining the award path. Used together with the Fire respawn-selector suppression below. Proof-only; do not generalize to other overlay callbacks. |
| ROM `0x000E5C50` / VA `0x802F0F00` | Fire key pickup-created respawn-selector suppression | **Runtime-confirmed bounded Fire v01.** Stock halfword store commits `s0+2` to `0x802C18F8`; v01 NOPs only this store. Combined v01 produced no key-created checkpoint event, natural stage-start respawn after death, successful Fire God completion, and next-stage transition. |
| ROM `0x000D500C` / VA `0x802F2CDC` | Wind key checkpoint-presentation candidate | **Static-confirmed candidate; runtime Pending.** Clean word `0C00A0C3` JALs `0x8002830C`; the callback supplies class `0x15` / process `0x80062D60` for parameters `0/1`. Candidate proof replaces only this JAL with NOP. Preserve the parameter-2 `0x802F60A0` write and all award/use logic. |
| ROM `0x000D5024` / VA `0x802F2CF4` | Wind key pickup-created respawn-selector candidate | **Static-confirmed candidate; runtime Pending.** Clean word `A42218F8` stores the callback-incremented selector to `0x802C18F8` for parameters `0/1`. Candidate proof NOPs only this store. |
| ROM `0x000BA60C` / VA `0x802F247C` | Water key pickup-created respawn-selector candidate | **Static-confirmed candidate; runtime Pending.** Clean word `A42218F8` stores `selector+1` to `0x802C18F8` for all three Water keys. Candidate proof NOPs only this store; preserve the parameter-1 `0x802F2980` update. |
| ROM `0x000BA610` / VA `0x802F2480` | Water key checkpoint-presentation candidate | **Static-confirmed candidate; runtime Pending.** Clean word `0C00A0C3` JALs `0x8002830C` with class `0x15` / process `0x80062D60`. Candidate proof replaces only this JAL with NOP. |
| ROM `0x000E1034` / VA `0x802F52D4` | Earth Square checkpoint-presentation candidate | **Static-confirmed candidate; runtime Pending.** Clean word `0C00A0C3` JALs `0x8002830C` only for callback parameter `0` (Earth Square). Candidate proof replaces only this JAL with NOP. Parameters `1/2` do not take this branch. |
| ROM `0x000E1044` / VA `0x802F52E4` | Earth Square pickup-created respawn-selector candidate | **Static-confirmed candidate; runtime Pending.** Clean word `A42218F8` stores selector `2` to `0x802C18F8` only on the parameter-0 branch. Candidate proof NOPs only this store; preserve the parameter-1/2 local-state writes. |
| ROM `0x0003CB50..0x0003CB57` / VA `0x8003BF50..0x8003BF57` | Player respawn-coordinate selector proposal | **Static site; banner suppression rejected.** Clean guard `3C04802C 848418F8` loads `0x802C18F8` for the spawn-table lookup in `0x8003BF4C`. v03 substituted selector `0` for Prison player selector `7` and the visible `CHECK POINT` event still appeared. A death/respawn comparison was not reported, so the site remains only a separate respawn-coordinate proposal. Any future proof must be player-only, preserve `ra`/`a2`, use a valid saved non-key selector, and define reset/invalidation rules. |
| ROM `0x00039AF8` / VA `0x80038EF8` | Ice Blast -> Pickup action-eligibility hook | **Runtime-confirmed bounded v01; Post-1.0 / 4Fun.** Guard `948306AA 14620034 00000000` (`lhu v1,+0x6AA(a0)` / reject non-stock pickup state). Proof JALs a helper that preserves stock `0x303` acceptance and additionally accepts only controller `+0x6F0 == 0x8004AB84` with native Ice mode `0x80111F98 == 0`; stock Pickup input/proximity/facing checks still run. |
| ROM `0x00039BA4` / VA `0x80038FA4` | Ice Blast -> Pickup commit hook | **Runtime-confirmed bounded v01; Post-1.0 / 4Fun.** Guard `3C04802C 8C841AC0` (load published player controller). Proof JALs a helper that replays the displaced load, rechecks normal Ice, and clears special lock `0x800BF308` only after stock pickup gates have passed. Stock pickup transition/award remains authoritative. |
| ROM `[0x0009AE00,0x0009AE84)` / VA `[0x8009A200,0x8009A284)` | Ice Blast -> Pickup proof helpers | **Runtime-confirmed bounded v01 proof storage only.** Exact Wind v04-base proof used zero tail bytes for the two helpers. This interval is not promoted as reusable/production-free space; reproduce only through `tools/build_iceblast_pickup_cancel_proof.py` against its exact guarded base SHA. |
| ROM `0x00015738` / VA `0x80014B38` | ATTACK check v01 event-0 seam | User-reported Runtime-confirmed bounded full-composition check. Guard `0C005570 24070001`; replace the JAL with the production-owned capture/event trampoline at `0x8009A218`, retaining the stock delay instruction. The KSEG1 dispatcher distinguishes callers by return address and preserves capture's `t0`. Not yet in the product patch core. |
| ROM `0x0002A848` / VA `0x80029C48` | ATTACK check v01 Block seam | Guard `30624000 1440FF23`; jump via proof stub at ROM `[0x77688,0x77694)`, preloading the KSEG1 helper target's high word in the hook delay slot. CLASSIC helper replays the stock Down/Turn decisions; MODERN schedules native LP. Proof-only. |
| ROM `0x0004E3AC` / VA `0x8004D7AC` | ATTACK check v01 stock combo-parser seam | Guard `000210C0 8CA306E0`; JAL via proof stub at ROM `[0x775D0,0x775DC)`, preloading target high word in the delay slot. The v04 helper replays the displaced actor load; CLASSIC also replays the original semantic shift. Proof-only. |
| ROM `[0x0009AE18,0x0009AE28)`, `[0x000775D0,0x000775DC)`, `[0x00077688,0x00077694)` | ATTACK check v01 owned trampoline composition | Guard the generated production capture stub and zero-filled tails inside the already-owned GAME SETTINGS regions; retarget the first to shared capture/event KSEG1 dispatch and emit combo/Block entry stubs in the tails. Exact bounds/overlap: [Memory and allocation map](Memory-and-Allocation-Map). The `0x9AEC0` proof trampoline remains untouched. |
| ROM `0x000AF71C`, `0x000AF708` | ATTACK check v01 disposable frontend name/value | Guard `COMBOS` row label and pointer `0x800AEAD8` (ASSIST); change label to `ATTACK` and point the second value to existing `MODERN` at `0x800AEAE8`. Durable bit `0x0400` and JUMP dependency are unchanged. Production still displays COMBOS/ASSIST. |
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
| ROM `0x315E8` / VA `0x800309E8` (v81/v82 diagnostic) | Token-`0x0B` newly constructed actor selector store before insertion | Exact v75 `A602009E` = `sh v0,0x9E(s0)`; v81/v82 use `A600009E` = `sh zero,0x9E(s0)` while preserving the preceding `0x8001C528` call. v81 Runtime-confirms this removes the one-frame blue projectile fallback but leaves the rocket corrupted, selector zero names fixed handle `0x80`, not the dynamically acquired Sektor source; exact slot-zero contents unobserved. Disposable diagnostic only; not an accepted production/global edit. |
| ROM `0x315EC..0x31603` / VA `0x800309EC..0x80030A03` (v82 diagnostic) | Pre-insertion selector-0 active-handle coherence | Runtime-confirmed stable negative control: no visible change from v81. Stale `+0x80` alone is rejected as the corruption cause. This edit is superseded and not reusable as an independently validated palette fix. |
| ROM `0x316C8` / VA `0x80030AC8` plus proof ROM `[0x9AE10,0x9AE90)` (v83) | Post-init/pre-insertion raw frame bind | Runtime-confirmed stable negative result: direct `0x8001BDA0` rocket bind before insertion leaves the initial Ice/Sektor projectile frame and Ice-blue missile unchanged. Parent `0x8004B584` subsequently advances the stock Ice entry, overwriting the early bind before flight. |
| ROM `0x316C8` / VA `0x80030AC8` plus proof ROM `[0x9AE10,0x9AE90)` (v84) | Contextual pre-insertion rocket bind | Partial Runtime-confirmed: removes the initial Ice/Sektor projectile fallback but leaves the missile graphically glitched. The zero-selector source and subsequent parent/child frame schedule remain unresolved by this early bind; same-shape rebuild is not the cause. |
| ROM `0x316C8` / VA `0x80030AC8` and proof ROM `[0x9AE10,0x9AE90)` (v85) | Deferred projectile list publication | Exact-v75 token `jal 0x80024650` is NOPed while delay-slot `sh v0,0xAE(a0)` remains. The proposed wrapper would bind ROCKETD1 and call `0x80024650` with a temporary owner-Y sort key; this wrapper is bypassed on the ordinary straight branch. Built, Runtime untested, **statically rejected** on ordinary mode-zero straight flight: branch `0x8004B028` skips the only wrapper reinsertion. Active movement/render processing and `0x80024B00` free-list return both require listing; global token suppression is unsafe. |
| ROM `0x315C8` / VA `0x800309C8` plus proof wrapper interval `[0x9AE10,0x9AE90)` (v86) | Straight-token palette-source acquisition | Retargets only the guarded mode-zero projectile palette acquisition from stock Ice `0x800B1A24` to file-`0x87 +0x4584C` through stock `0x8001C528`; selector store, insertion, frame schedule, helpers, child and flight remain v75. Partial Runtime-confirmed: rocket becomes materially more coherent but remains donor-inaccurate because the imported asset indices were previously remapped into grayscale Sektor TLUT entries. |
| File-`0x87` rocket/palette append + ROM `0x315C8`, `0x316C8`, `0xF40DBC`, `0xF40DC4`, proof `[0x9AE10,0x9AE90)` (v89) | Synchronous pre-publication projectile texture-slot preparation | Keeps v87 exact ROCKETD1/ROCKET_P asset pair and dynamic selector; sets live constructor operand `+0xDBC` and ordinary-parent next frame `+0xDC4` to ROCKETD1; wrapper at token insertion uses finalized actor slot `+0x9C` with native `0x8001BF70` to synchronously load the raw rocket, refreshes with `0x8001BDA0`, then tail-calls stock `0x80024650`. Runtime-confirmed for the bounded v89 route: removes the one-frame corrupted Sektor and preserves the correct rocket/flight. One-shot proof only because texture-storage advancement and release ownership are not productionized. |

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


### Compact rainbow loader sites

The Runtime-confirmed compact-tail v01 architecture edits all 15 stock Sub-Zero file-`0x87` allocation/load pairs. Each allocation delay changes from `addu a0,v0,zero` to `addiu a0,v0,0x2000`; each raw-loader JAL is redirected to the production rainbow wrapper. The paired allocation ROM sites are `0xDF40, 0xE384, 0xEF00, 0xF628, 0xFEB0, 0x105B0, 0x106B0, 0x10DBC, 0x116DC, 0x117DC, 0x11EA4, 0x125B4, 0x12F70, 0x13068, 0x24768`; paired loader JAL sites are `0xDF50, 0xE394, 0xEF10, 0xF638, 0xFEC0, 0x105C0, 0x106C0, 0x10DCC, 0x116EC, 0x117EC, 0x11EB4, 0x125C4, 0x12F80, 0x13078, 0x24778`. File-table entry `0x92` at ROM `0xA56E8` becomes the optional raw rainbow-bank transport; ROM `0xF20000..0xF21FFF` stores only the 8 KiB bank. The wrapper starts at runtime `0x801B0880` / ROM `0xF69060`, inside the guarded controls→Toasty gap.


## Temple intro seeded audio

| Address | Ownership / edit | Evidence / guard |
|---|---|---|
| ROM `0x000CB274` / VA `0x802EDB94` | Temple Audio-1 stock descriptor-A immediate | Stock `24040041`; **remains stock** in the corrected isolated architecture |
| ROM `0x000CB280` / VA `0x802EDBA0` | Temple Audio-1 stock descriptor-B immediate | Stock `24040042`; **remains stock** in the corrected isolated architecture |
| ROM `0x000CB2F8` / VA `0x802EDC18` | Temple Audio-2 stock laugh descriptor immediate | Stock `24040043`; **remains stock** in the corrected isolated architecture |
| ROM `0x0097A200` | Temple event 123 / descriptor `0x41` | Replaced with selected donor 32-byte one-shot event rebased to patch 486 only when Audio 1 is selected |
| ROM `0x0097A220` | Temple event 124 / descriptor `0x42` | Same Audio-1 replacement as event 123 so stock alternation still resolves to the same selected donor clip |
| ROM `0x0097A240` | Temple event 125 / descriptor `0x43` | Replaced with selected donor 32-byte one-shot event rebased to patch 486 only when Audio 2 is selected |
| ROM `0x00948450` | Isolated host patch 486 | Stock `01000149`; event 329 is its only initial-patch user and no stock in-stream program change selects 486 |
| ROM `0x0094A11C` | Isolated host subpatch 329 | Guarded; uniquely owned by patch 486; donor subpatch copied with waveform ID rebased to 319 |
| ROM `0x0094DF20` | Isolated host waveform 319 | Guarded; uniquely owned by subpatch 329; donor waveform copied with sample pointer rebased to Temple sample storage |
| ROM `0x00964D88..0x00964E8F` | Isolated host predictor 319 | Guarded by stock SHA-256; replaced by selected donor predictor |
| ROM `0x000A3794`, `0x0097C7D8`, `0x009485C4`, `0x0094A860`, `0x0094E7D8` | Superseded `0x20A -> 0x1A6 -> 579 -> 422 -> 412` carrier | **Rejected / leave stock.** Runtime showed unrelated Bridge/Prison robot/miniboss audio reaches this route; regression tests require these bytes to remain unchanged. |
| ROM `0x00F6BDF0..0x00F6D80F` | Conditional selected Temple donor sample | Production-owned only when valid MKT donor is supplied; clean region must be `FF` and stock file-table overlap is rejected |

The earlier proof carrier descriptor `0x220` / event `0x1B8` is **not a production edit site**. Whole-ROM audit found live stock callers for descriptor `0x220`; it remains proof history only.

### Global materializer wrapper integration — PR #129 (2026-10-02)

| Site | Ownership / edit | Evidence |
|---|---|---|
| ROM `0x00010E64` | Stock Prison-entry JAL to `0x802ED538` is replaced by a JAL to the PR #129 reconstruction wrapper. The wrapper calls stock `0x802ED538` first, then rebuilds `0x802C0D54` bits 0..2 from authoritative four-box IDs `0x1A..0x1C`. | Implementation/CI-confirmed (#1583); Runtime Pending |
| ROM `0x00F6AAF0..0x00F6B0CF` / RDRAM `0x801B2310..0x801B28EF` | Shared file-`0x1A` materializer helper containing logical-award dispatcher, destination actions, immediate re-mask helper, and Prison reconstruction. | Implementation/CI-confirmed (#1583); Runtime Pending |
| Ordinary pickup record `+0x14` | Low 15 bits encode logical award + destination action for wrapper-owned locations; raw bit `0x8000` remains destination activation state and is masked before callback dispatch. | Static-confirmed ownership; Implementation/CI-confirmed emission |

Native per-stage selector writer sites are not globally NOPed or rewritten by this integration. Destination wrappers invoke only the separately researched location-owned transition/state effects.
