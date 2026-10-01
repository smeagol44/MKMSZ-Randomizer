# Lifecycle static closure and v05 design

2026-10-01. **Static analysis / proposed, unbuilt v05.** No emulator was run and no ROM was built or modified. Runtime acceptance remains Pending.

## Evidence and scope

Current repository source: `main` at `62cf0e4d317779b6a75b9964cfc53d278476ddc1` (PR #126 merged). Read the current status first, then requirements and lifecycle/progression/registry/flow owners and relevant failure history. Addresses below come from the USA Rev. 0 clean image and the preserved Ghidra function inventory, checked against big-endian MIPS words. Permanent-image mapping for these sites is ROM = VA − `0x80000000` + `0xC00`; expansion-file addresses use their file-table mapping, not that formula.

| Input | SHA-256 |
|---|---|
| Clean USA Rev. 0 ROM | `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6` |
| Exact `MKMSZR_lifecycle_pause-quit_proof_v04.z64` recovered for inspection | `63357955a89e3059c405e42bf127c79cb6692395e7f730d2bad0c733123c47db` |

The v04 builder was not recovered. Its emitted instructions were inspected directly. [Machine-readable trace evidence](https://github.com/smeagol44/MKMSZ-Randomizer/blob/main/docs/research/lifecycle-static-v05.json) records mapped bytes/disassembly and production source hashes. This report does not attribute the intermittent music-speed corruption to a specific instruction: its cause is unresolved, and the entire v04 composition is rejected.

## Ordinary death and remaining-life reconstruction

The live player process runs `0x80028F3C`. At `0x80029038`, it reads its own HP halfword `+0x654`; zero HP with `+0x6B0 == 0` enters death handling. The handler selects the death animation, then compares the current process at `0x802ECE20` with the live player pointer `0x802C1AC0` at `0x80029114..1C`. Only the matching player calls `0x80035578` at `0x80029124` / ROM `0x29D24`. A dead non-player process does not use this life counter path.

Exact remaining-life chain:

1. `0x80029124 -> 0x80035578`.
2. `0x80035620/2C -> 0x80028488`: remove class `0x12`, then class `0x400` processes. Clear native HP-carrier-valid at `0x8003564C`.
3. Read **word** current lives `0x8010BCFC` at `0x8003565C`. `bnez` at `0x80035674` goes directly to `0x80035C90` when another replacement life remains.
4. `0x80035C94` reads the counter; `0x80035C98` subtracts one; **`0x80035CA0` / ROM `0x368A0` writes the decrement**. This route bypasses the configured-life reload at `0x80035C8C`.
5. Preserve the stock yield/fade ordering: `0x80035CA4 -> 0x80028794(30)`, class `0x101` fade callback `0x800615FC`, wait for that class, then `0x80035CE0 -> 0x8007F548`.
6. `0x80035CF0 -> 0x8002830C(class 0x15, callback 0x80016080)`.
7. `0x80016080`, including `0x800160AC -> 0x80028488(0,0)`, removes the old player/other processes and dispatches the stage through `0x800161D4..0x800162D0`. Process teardown returns slots to the native free list; it is not a life-counter reload.
8. The selected stage entry reloads its resources and calls `0x8002EC78 -> 0x8002ECF4` to construct a new player. The ordinary pickup-manager reconstruction at `0x80038ACC` subsequently runs production pickup/XP/LIVE restoration.

| Stage entry callback | Player-construction call |
|---|---|
| Temple `0x8000E0E0` | `0x8000E544` |
| Wind `0x8000E800` | `0x8000ECF4` |
| Water `0x8000F004` | `0x8000F5F4` |
| Earth `0x8000FF28` | `0x80010420` |
| Prison `0x8000F7D0` | `0x8000FD44` |
| Fire `0x800108FC` | `0x80010EBC` |
| Bridge `0x80011780` | `0x80011CD4` |
| Fortress `0x8001205C` | `0x800128B8` |

These are callback dispatches through the native scheduler, not nested synchronous calls through Mission Objective. The unsafe debug Fire entry has a separate constructor call at `0x80011650`; this lifecycle design does not repair that entry.

## Continue, fresh frontend entry, and route distinction

When current lives is zero, `0x80035578` falls through `0x80035674`, changes presentation state to `0x17`, saves/restores the old stage using `sp+0x2C`, and reads **signed halfword** continues `0x801AE45C` at `0x800356C0`. Positive continues permits the Continue prompt. Accepted Continue (`s2 != 0` at `0x80035BAC`) reaches `0x80035C2C`:

- `0x80035C64/74/84`: read, decrement, and store continues;
- `0x80035C6C`: read configured lives from signed halfword `0x800A5FAA`;
- `0x80035C8C`: reload current lives from configuration;
- join the same decrement at `0x80035CA0`, yielding configured lives minus one.

The current counter measures spare lives: configuration **9** produces current counter **8**, plus the active life. This is not a reason to clamp death decrements at 7.

The fresh/frontend root `0x8000D260` clears HP-valid at `0x8000D274` and calls `0x80016B10` at `0x8000D2A8`. That routine reads configured continues `0x800A5FAC` and configured lives `0x800A5FAA`; `0x80016BB8` subtracts one, `0x80016BC0` stores continues, and `0x80016BC8` stores current lives. The frontend GAME SETTINGS routine also rewrites these current values at `0x80076784/8C`. These frontend writes are distinct from an ordinary death.

The patched title A route reaches the Safe Stage Select callback at `0x8000D428`; selector commit in `0x80015088` (process state `0x18`) stores the chosen stage and schedules `0x80016080` at `0x800150F4`. Consequently, snapshots must survive frontend configuration writes, but must not be restored on every stage reconstruction.

Use explicit lifecycle reason state, not stage ID, current HP zero, or a broad stage-init callback:

| Reason | Resource/HP policy |
|---|---|
| Fresh run | 9 total lives, 5 continues, full HP, starter inventory |
| Pause -> Quit or living stage completion -> next/re-entered stage | Capture live HP and current counters; restore once in constructor |
| Ordinary death with lives remaining | Commit inventory; invalidate damaged-HP/re-entry token; stock decrements; constructor gives full HP |
| Accepted Continue | Same inventory protection; retain stock configured-life reload and continues decrement; full HP |
| Final no-continues terminal return | Reset run state only after terminal classification |
| Continue declined/timed out with continues remaining | No final-no-continues reset; do not reinterpret this as the requested terminal discriminator |

`0x80035D34` is another failure/reconstruction owner: it clears HP-valid at `0x80035D60`; states `0x16/0x1B` set valid and directly reconstruct at `0x80035E78/84`, while other states decrement current lives at `0x80035F04` or call `0x80035578` at `0x80035EA4` if none remain. These alternate routes require an explicit reason branch, not an unconditional saved-life restore. `0x80035F38` is a carrier-valid-preserving reconstruction owner (`0x80035F54`, then `0x80035FA8 -> 0x80016080`); its callback references are indirect.

## Inventory writer and reconstructor

The registry's former shorthand for `0x8007AD4C` was wrong for the current production implementation. It is **filtered LIVE -> active backing SAVE**, not LIVE reconstruction. Leave its body/ownership untouched.

| Operation | Exact current production chain |
|---|---|
| Commit active box | `0x8007AD4C -> 0xA01AF5F4`; compute box base `0x800A6048 + (state & 3)*40`; store at `0x801AF604` unless LIVE word is Glass `8` |
| Reconstruct masked LIVE | `0x80099B14 -> 0x8007AD00`; read active backing and write ten LIVE words at **`0x8007AD34` / ROM `0x7B934`** |
| Production manager resume | pickup persistence resume -> production XP restore -> existing load-mask wrapper -> original manager continuation |
| v04 manager resume | `0x801AF5DC -> 0x801AF6C0 -> 0x801B0A20 -> 0x80099B14 -> 0x8007AD00` |

The mask-copy writer's destination is only `0x800A600C..0x800A6033`; its source is one of the four authoritative boxes. It does not initialize/clear the backing region. Death processing and the inspected stage reconstruction do not introduce a four-box reset. The exact v04 lifecycle helpers contain **no death-time LIVE commit**. Native acquisition/use modifies LIVE, so uncommitted acquisitions can be replaced by an older backing image when this writer runs. A starter-only backing image makes that look like an inventory reset.

This is a **Static-confirmed writer/ordering defect and strong inference for the observed reset**, not a runtime measurement proving all four backing boxes were overwritten or stayed intact. No death-time four-box-clearing writer was found in the traced route. The bounded proof must separately sample the entire `0x800A6048..0x800A60E7` region and LIVE before/after death. If inactive committed boxes also change, the stale-LIVE explanation is insufficient; stop and trace that additional writer.

Smallest fix: at the failure owner **before process teardown**, call the existing filtered save contract once. Preserve inactive boxes, active index, settings and Glass-hidden identities. Let the unchanged production manager reconstruction rebuild LIVE after death. No additional manager/progression hook, no replacement default loader, and no second inventory authority is needed. This also captures consumable removals, which an acquisition-only commit cannot cover. Current `global_materialization.py` optionally commits ordinary acquisitions at ROM `0x39FD4`; it is not automatically present in every stage-local/pickup-XP composition and does not eliminate the death/use boundary.

## HP construction and carrier consumption

`0x8002EC78 -> 0x8002ECF4` allocates the actor and class-1 player process (`0x8002830C`, callback `0x80028EAC`). It publishes the controller at `0x8002ED50 -> 0x802C1AC0`, then zero-fills controller `+0x638..+0x6D7` through `0x8002ED7C -> 0x80070710`. HP must be restored **after that zero-fill and before the following branch**:

| Site | Native operation |
|---|---|
| `0x8002ED84/88` | Reload the newly published live controller into `a0` |
| `0x8002ED90/94` | Read signed HP-valid halfword `0x800C11F8`; zero takes full-health branch |
| `0x8002EDA0` | Read signed HP carrier halfword `0x801AE4C0` |
| `0x8002EDB0` | Store positive carrier into controller `+0x654` |
| `0x8002EDB4` | Nonpositive valid carrier becomes HP 1 |
| `0x8002EDBC` | Clear HP-valid after one-shot consumption |
| `0x8002EDCC` | Absent carrier: store full HP `0xA6` (166) |
| `0x8002EE3C` | Store max HP `0xA6` into controller `+0x656` |

**Constructor-local seam:** VA `0x8002ED84` / ROM `0x2F984`, guarded words `3C04802C 8C841AC0`. A leaf helper may prepare carrier/valid and resource counters, then replay both displaced controller-load instructions and resume at `0x8002ED8C`. Preserve every live register except the outputs of the displaced instructions. No scheduler, evaluator, allocator, raw loader or audio call belongs in this helper.

Stage roots and death processing clear `0x800C11F8`, so setting it only when leaving a stage is insufficient. At the constructor seam, an explicit one-shot living re-entry token sets carrier to saved positive HP (bounded to `1..166`) and valid to 1; consume the token there. A death/Continue token clears saved damaged-HP eligibility and native valid so the replacement gets full HP. Fresh run does the same. Do not infer re-entry from the still-zero new controller.

The stock **consumer** is closed. A stock producer for `0x801AE4C0` was not established by this trace; a literal/reference scan is not an exhaustive indirect-writer proof. The v05 producer is instead directly owned: capture live `*(0x802C1AC0)+0x654` before leaving/finishing and write the carrier only at the constructor seam. The stock valid-preserving reconstruction routes above must capture there if included; do not assume the existing carrier already contains current HP.

## Real terminal discriminator and reset

The discriminator is the control-flow conjunction: **current lives was zero at `0x80035674`, signed continues was `<= 0` at `0x800356C4`, and terminal choice `s2 == 0` reaches `0x80035BB4`**. The common terminal label also admits declining/time-out with positive continues; reaching that label alone is insufficient.

Proposed hook: **VA `0x80035BB4` / ROM `0x367B4`**, original `jal 0x80028794` with `li a0,4` delay slot (`0C00A1E5 24040004`). Guard current lives `== 0`, signed continues `<= 0`, a valid MKSV lifecycle header, and a latched real-run failure context. Clear only after classification, then replay the stock yield exactly once. Stock then restores the saved stage, destroys processes at `0x80035BCC`, schedules title callback `0x800144E8` at `0x80035C1C`, and exits through `0x80028564` at `0x80035C24`.

**ROM `0x364EC` is prohibited.** In this verified clean image it maps to VA `0x800358EC`, the stage-sensitive no-continues presentation subtree. That mapping does not rescue the rejected v01 reset composition or establish an exclusive final-reset hook: v01 runtime cleared state on stage entry. Use the classified later terminal seam instead; keep the reported v01 failure and the verified clean mapping distinct.

Demo protection must be latched before teardown. Stock demo input/timeout at `0x80015A74/7C` zeros lives/continues and at `0x80015A84/8C` clears demo indicators. Checking only `0x8009AFF6` at the terminal label is therefore unsafe. Demo entry sets it to `-1` at `0x80079498`; input processing changes it to `1/2`. Constructor context can latch demo/non-demo before the timeout. Never arm a run reset merely because an MKSV header exists from an earlier user run. Other direct `0x80035578` callers include `0x8000E0C8`, `0x8000FF9C`, `0x80035EA4`, `0x8003667C`, `0x8003B320`; preserve their stock presentation and classify supported real-run failures independently of the ordinary player callback.

Reset contract:

- Preserve MKSV schema `+0x00..+0x0F`; clear run flags at `+0x10` (including Temple special-check), lifecycle `+0x14..+0x1F`, all eight ordinary pickup words `+0x20..+0x3F`, progression count/XP `+0x40/+0x44`, and run rainbow index `+0x48`. Do **not** blindly clear the whole `0x50` bytes: `+0x4C` is the GAME SETTINGS transient editor.
- Clear native XP `0x8011200C`, tier state `0x802C1BA4`, and Power Ups count `0x800C1248` directly; do not call the tier evaluator.
- Clear lifecycle snapshots, current resources, carrier `0x801AE4C0`, valid `0x800C11F8`; suppress any stale later restore. No dereference of an already freed player is needed at the terminal hook.
- Empty all four backing boxes and LIVE with native empty sentinel `-1`, not item ID zero. Reset box index/latch while retaining **all five preference bits, mask `0x3E00`**: TURN `0x0200`, ATTACK `0x0400`, SPECIALS `0x0800`, JUMP `0x1000`, RUN `0x2000`. Keep/reestablish `MKBX` magic. The old inventory-only mask omits RUN; do not reuse it for reset.
- Stock terminal cleanup already zeros checkpoint selector `0x802C18F8` at `0x80035C10` and acquired-key word `0x802C0D54` at `0x80035C18`; retain those stores. MKMSZR-owned collected/key authority is the pickup/special state plus backing boxes, all cleared above. Do not blindly write unloaded Temple-overlay memory `0x8026E9A4`; clearing the persistent Temple flag makes the next valid Temple reconstruction start uncollected.
- The next real-run constructor initializes configuration Very Hard `0x800A5FA8=4`, total lives `0x800A5FAA=9`, continues `0x800A5FAC=5`; current spare lives 8, continues 5, native difficulty carrier `0x802E7DC8=4`, full HP. Box 1 and LIVE receive `[4,4,1,-1,-1,-1,-1,-1,-1,-1]`; boxes 2–4 remain empty. Preserve user control preferences and transient frontend ownership throughout.

## Single v05 design — no build authorization implied

Build a new composition from current guarded production source and the clean ROM. Do not extend v04 or copy its helper addresses. The following is one design, with boundary-specific entry points sharing leaf state operations:

| Hook / guarded clean bytes | Owned work |
|---|---|
| Pause Quit `0x800166CC` / ROM `0x172CC`: `0C00A122 00002821` | Capture living HP/current resources and one-shot re-entry reason before stock teardown; filtered inventory commit; retain only already-confirmed current-XP -> persistent `+0x44` save if required by XP mode; replay teardown once |
| Failure root `0x80035578` / ROM `0x36178`: `27BDFFA0 AFB30044` | Before teardown, classify real run/demo, commit LIVE, invalidate living re-entry/HP token; preserve stock decrement/Continue/UI graph |
| Alternate reconstruction `0x80035D34` / ROM `0x36934`: `27BDFFE0 AFB00010` | Commit before teardown; states `0x16/0x1B` capture living carry, other failure states invalidate it; no counter restoration |
| Valid-preserving reconstruction `0x80035F38` / ROM `0x36B38`: `3C02802F 8C42CE20` | Capture living HP/resources and commit before reconstruction; retain stock callback behavior |
| Stage completion `0x80035FC0` / ROM `0x36BC0`: `27BDFFE8 24040012` | Capture the live player before `0x80035FE4` teardown / `0x8003600C` pointer clear; commit active box; arm living transition token |
| Constructor `0x8002ED84` / ROM `0x2F984`: `3C04802C 8C841AC0` | Leaf-only: fresh init or explicit one-shot living restore; latch demo context; enforce Very Hard for real runs; replay displaced loads; stock carrier/full-HP branches do the HP store |
| Classified terminal `0x80035BB4` / ROM `0x367B4`: `0C00A1E5 24040004` | Conjunction guard, run reset, then stock yield/title chain once |

No death-time restoration of saved lives/continues. No hook at the stock decrement. No modification of production `xp_progression._build_restore()`, pickup-manager resume, Mission Objective, stock/default-loader replacement, or acquisition power evaluation. HP/resource and inventory work is owned by the direct boundaries above. External filtered-save calls occur only at teardown boundaries, not from the constructor leaf.

Proposed state uses the existing twelve reserved MKSV bytes: `+0x14` packs HP in bits `0..15`, `RUN_ACTIVE=0x00010000`, `LIVING_REENTRY=0x00020000`, `DEMO_CONTEXT=0x00040000`, and `REAL_FAILURE=0x00080000`; `+0x18` stores snapshot current spare lives; `+0x1C` stores snapshot continues as a word (native current continues remains a halfword). These are proposed v05 names, separate from Temple header flags and settings at `+0x4C`. A living token permits resource/HP restoration once; death invalidates it before stock mutation. `RUN_ACTIVE` distinguishes first construction/reset from already-active ordinary reconstruction. Demo construction updates context only and preserves the parked real-run snapshot. The terminal reset requires `RUN_ACTIVE|REAL_FAILURE` and rejects `DEMO_CONTEXT`; ordinary replacement construction clears `REAL_FAILURE` after consuming its route. Native counters remain authoritative while playing; snapshots are authority only for an explicitly armed living re-entry.

Existing shared file `0x1A` is loaded by the production `0x800663E0` arena/bootstrap boundary before the stage constructor (Temple example: bootstrap call `0x8000E1F0`, constructor `0x8000E544`). Candidate helpers must use uncached execution and guarded full-composition suballocation after current materializer end `0x801B0A60`, below Toasty `0x801B1000`; corresponding ROM candidate span is `[0xF69240,0xF697E0)`. This is **a proposed bounded suballocation**, not confirmed-free memory. Do not enlarge the existing 16-KiB reservation, reload file `0x1A` from the frontend, or reuse v04's `0x801B0970/0x801B0A20`, which overlap current materializer ownership.

Before emitting a ROM, require code-size/allocation guards, complete displaced-instruction/branch-delay/register preservation checks, real/demo reason guards, header validation, snapshot one-shot consumption, and byte identity of the production progression restore. The design is statically located; emitted helper size and composition are not Implementation-confirmed yet. A failure to fit this candidate span is a stop, not permission to borrow another owner's bytes.

One subsequent bounded manual proof should cover damaged HP + distinct inventory across four boxes -> Pause Quit/re-entry; several consecutive ordinary deaths through counter 7 to 6 and below; accepted Continue with its decrement; living stage completion; final no-continues return and fresh defaults/settings survival; then the parked-run/attract-demo negative control. Include pre/post death backing-vs-LIVE samples and sustained normal audio. Any music acceleration rejects the complete composition immediately. Neither this static report nor a passing bounded proof would establish exhaustive all-stage/save-load lifecycle acceptance.
