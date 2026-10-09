# Stage flow and selector

**Inventory-HUD TEST LAB closure (2026-10-05):** exact v16 enters TEST LAB but immediately hangs on Inventory before later pickup-manager additions. Static review identified the independent v14 HUD first-load size bug; **v20 Runtime-confirms the one-word size initialization correction removes the hang on the bounded route.** See [TEST LAB Inventory diagnosis](Test-Lab-Inventory-Hang-Static-Diagnosis).

**Lifecycle ownership (2026-10-01):** [Static death/Continue/constructor/terminal trace and unbuilt v05](Lifecycle-Static-Closure-v05). Ordinary remaining-life respawn schedules `0x80016080` after the decrement at `0x80035CA0`; accepted Continue alone reloads configured lives at `0x80035C8C`. Frontend `0x8000D260 -> 0x80016B10` is a separate configured-resource reload. Do not restore saved lives on all stage entries, or add lifecycle calls to Mission Objective/progression restore. The native constructor consumes HP before the pickup-manager restore; living re-entry requires an explicit constructor-local token.

> **Scope:** This page is the canonical owner for the safe stage selector, compact-to-native stage mapping, the title/frontend route used to enter the selector, the post-legal company/logo bypass, the selector-specific automatic-save bypass, rejected broad flow-bypass approaches, and the relevant bounded runtime evidence.
>
> Exact guarded ROM patch bytes, expected bytes, and replacement words remain canonical in the [Address and patch-site registry](Address-and-Patch-Site-Registry). This page owns the behavior and flow boundaries, not a duplicate byte registry.

## Current production flow

MKMSZR keeps the normal game stage-loader path and narrows only the frontend path used to choose a stage:

1. the legal/MKMSZR branding screen remains visible;
2. the two fixed company/logo presentations immediately after it are skipped;
3. fade normalization and the normal title handoff still run;
4. pressing **A** on the title-screen Start entry opens the native debug stage selector;
5. the selector exposes only eight safe destinations;
6. the compact selector result is mapped back to the game's native stage numbering;
7. that selector route arms the game's existing one-shot stage-entry save bypass so the immediate automatic save prompt is skipped;
8. normal manual, later, and post-stage save behavior remains unchanged.

The frontend/presentation content itself is outside this page's scope; this page owns only the route and bypass behavior relevant to stage selection.

## Safe stage selector

The title-screen A-button route originally calls `0x8002830C`; production redirects that route at ROM `0xE028` to the native debug selector at `0x8000D0B8`. The normal stage-loader path remains stock after selection, preserving its ordinary cinematics, overlay initialization, and stage-progression behavior.

The selector wrap/count sites at ROM `0xDD60` and `0xDD64` are bounded to eight entries. The pointer table at ROM `0x9B7DC` / VA `0x8009ABDC` retains only:

| Compact index | Label | Native stage |
|---:|---|---:|
| 0 | Temple | 0 |
| 1 | Wind | 1 |
| 2 | Water | 2 |
| 3 | Earth | 3 |
| 4 | Prison | 4 |
| 5 | Fire | 5 |
| 6 | Bridge | 8 |
| 7 | Fortress | 9 |

Stock entries excluded from production are **Unused**, **Fire God Room**, and **Test Characters**. The original eleven-label order was Temple, Wind, Water, Earth, Prison, Fire, Unused, Fire God Room, Bridge, Fortress, Test Characters.

### Blue cursor and movement sound — Runtime-confirmed

The accepted production presentation is the bounded **v03a** composition.

Static comparison of the clean USA Rev. 0 resources established that selector frames `0x352..0x35A` from global file `0x5F` and title-menu cursor frames `0x3CC..0x3D4` from file `0x5E` have byte-identical indexed pixel payloads for all nine corresponding frames. Both presentations use a 29-entry palette and collectively reference every palette index `0..28`. The selector therefore keeps its existing file `0x5F`, sprite IDs, slot `0x1C2`, registration path, and `0x8001D520` draw path; production changes only the selector-local 58-byte palette at ROM `0x000B21D8` to the title cursor palette from ROM `0x000B32E8`. Files `0x5E` and `0x5F` are not rewritten for this feature.

Movement sound is also Runtime-confirmed in v03a. At the selector input-loop hook, only a newly pressed single Up/Down direction plays title MOVE descriptor `0x1FC` (raw sound `0x0230`) through native wrapper `0x80064C18`. Holding a direction does not repeatedly retrigger the sound. The helper occupies guarded frontend-resident ROM `0x0000E27C..0x0000E2AF`, replacing an unreachable compiler epilogue whose clean bytes and direct-target absence are guarded/static-checked.

Manual v03a validation confirmed the blue animated cursor, movement SFX, normal stage selection, and normal stage audio after remaining in gameplay beyond the delay that had exposed the rejected v02 audio symptom. This runtime result is bounded to the tested selector/stage route rather than exhaustive frontend/audio coverage.

**Confirmation chime is intentionally deferred.** Stage choice inside the native selector is committed by **Start**, through the existing event/callback route to `0x80015088`; A is only the verified title-screen route used to enter Safe Stage Select. The v02 experiment incorrectly played descriptor `0x1FD` on an A edge inside the selector and was rejected: A produced the sound without choosing a stage, and after stage load the user observed delayed crunchy/choppy/noisy audio. The exact corruption mechanism was not proven, so production contains **no added confirmation-SFX hook**.

### Movement sound as audio-blocker control — guarded proof prepared (2026-10-09)

**Implementation/static-checked, runtime Pending.** The maintainer recalled v02 confirmation-SFX audio corruption while investigating later accelerating Fortress music. History confirms: v02 added descriptor `0x1FD` on the **wrong A input**, then delayed crunchy/choppy stage audio was observed; accepted v03a keeps **only Up/Down MOVE `0x1FC`**, which passed one bounded late-stage audio test. The prior v02 and v03a paths are distinct and neither proves the newer failure is caused by MOVE.

A strictly isolated **disposable** control is prepared from exact prefilled-Fortress audio proof SHA-256 `13346ae68efd99fb9d07929d2d1016eba1fd5d065170d58235522fd9a6e505b1`. Output `MKMSZR_selector-move-sfx-off_fortress_proof_v01.z64`, SHA-256 `3988da00cc1fda37d314f4b20452ac678ae17cc1bc2d078c9e0dc12a857dd98f`, CIC 6102 CRC1/CRC2 `6A853F7E / EFDDCE9E`. The *only* executable alteration is at ROM `0x0000DD70`: the injected `JAL 0x8000D67C` instruction `0C00359F` becomes the original unmodified menu drawing setup `24040050`; delay slot `0xDD74=24050014` is retained. The movement helper remains in its guarded owned space but has no selector entry call. Other diffs are header checksum bytes `0x10..0x17`; every non-header byte beyond `0xDD73` is unchanged. Both source and clean-ROM hash/expected instruction guards passed, output CRC verified. **No emulator was run. No ROM or production patch was merged/modified.**

This controls only the added selector movement SFX while preserving Safe Stage Select, blue cursor and all later production features and diagnostics. One manual negative-control test can compare this output against already established failing Trace (7) using same RMG v02 configuration and prefilled Fortress route: cold boot, enter stage via safe selector (now silent on Up/Down), Box 1 cursor sweep ~30s, idle up to ~2min; save four observer traces on normal exit. Because timing is sensitive and failure intermittent, *one clean result is supportive but not conclusive*: disabling a sound call also changes audio phase. A repeated FIFO burst **with MOVE disabled** would directly refute MOVE SFX being necessary on that route. **No approval to remove v03a production SFX or restore rejected v02 confirmation chime.**

### Trace (9) accepted single-site negative: MOVE SFX-off avoids severe music runaway (2026-10-09)

**User Runtime-confirmed absence of audible accelerated music in this route; trace-confirmed absence of sustained FIFO rejection / long fixed-buffer phase; cause not finally established.** Input ROM `MKMSZR_selector-move-sfx-off_fortress_proof_v01.z64`, SHA256 `3988da00cc1fda37d314f4b20452ac678ae17cc1bc2d078c9e0dc12a857dd98f`, differs from the exact Trace (7) failure ROM `13346ae68efd99fb9d07929d2d1016eba1fd5d065170d58235522fd9a6e505b1` only by reverting ROM `0xDD70` from `0C00359F` (JAL selector movement helper) to stock `24040050` (drawing parameter), and changed CIC6102 header CRC bytes. All other original prefilled Fortress production + rejection logger bytes remain identical. No other feature removed.

The new Trace (9) captures **251.722s** (Fortress selected and begins at first-VI-relative t=13.158s), compared with **130.062s** in failing Trace (7) (Fortress starts t=10.284s). All four Trace (9) observer streams have no overwritten records: AI `707543354fe8e7faab77a1028a177420177b262ca511cc301d9c82c7f5d0ed08`, VI `65643baa1666ada3fde1484a29b207ea879254db2d351a79869b8c19cbe0c478`, RSP `5f1ea257b6bebb392dc4d2c087169e8a58be093bcda1e91c43f984faacd9b36a`, host `a7e3a31f927f95387f6a0175bbc7f4968b74a937bc65a48af9c886640b6b98c1`.

| Event | Baseline Sound-ON Trace (7) | MOVE-helper-OFF Trace (9) |
|---|---:|---:|
| User reports audible speed-up | Yes | **No** |
| Native FIFO rejected submissions (two logger FULL reads each) | 74 | **2 isolated** (t=123.288, 158.605s), no cluster |
| Longest uninterrupted 368-frame output | 2,383 / ~39.70s | **9 / 0.15s** |
| Host SDL threshold drops | 4 (2,832 bytes) | 22 (21,520 bytes); independent host queue channel |
| Sampled stage-9 highwater / static bound headroom | `0x8028CD48` / 15,432 bytes | **identical** |
| HUD data pointer | `0x801FEBA0` | **identical** |
| HUD/legend/materialized fixed-code region hashes | `21E410DE/2298F9CB/09615F1E` | **identical** |
| Sampled arena reset base, cursor/HUD coherence | No observed violations | No observed violations |

Both runs have the identical RMG AI duration rule `551 Count/byte`; Trace (9) accepted 14,798 submissions. Its two actual FULL attempts were isolated and recovered, similar to the clean-ROM Trace (8) behavior. **Eliminating the selector MOVE helper changes the full audio regime before the failure, not only its audibility.** This is our strongest isolated feature-composition control so far. It weakens a purely emulator-clock-only or always-on rich-HUD explanation, but does not prove the 0x1FC sound playback itself is defective: bypassing the helper also bypasses its edge logic, callee call, register/return handling and instruction-time cost; routes were not input-cycle matched; a single benign run cannot rule out stochastic phase.

**Next staged control, no gameplay change:** additional disposable `MKMSZR_selector-move-call-off_fortress_proof_v01.z64`, SHA `7ef2ce16bddcc5716df8aa030c5eaf367363a3bbdf882f6b63ceee2ba73bb25e`, retains the original selector JAL helper at `0xDD70` and all helper logic (including `s0` save/return) but replaces exactly its native sound wrapper `JAL 0x80064C18` at ROM `0xE29C:0C019306` with `00000000`, leaving delay slot `0xE2A0` intact; CRC1/2 recalculated `2A85F778/A8B71C2A`. Static byte-/checksum guards passed, **runtime Pending**. When tested with same unmodified RMG v02 prefilled Fortress route, if stable while helper still runs it points toward native SFX playback/voice-lifetime/audio-phase, rather than helper instructions alone; if repeated runaway persists without playback, focus on helper ABI/return state/instruction timing. This is a request for a *bounded single differential test*, not an approved removal of selector SFX from production. No production ROM modification, no CI/emulator run and no merge.

## Compact-to-native selection mapping

The debug menu writes its compact selection at `0x800C11E0`. The transition path at `0x80015088` ultimately stores the native stage at `0x8009A910`.

Production replaces the stock selection load at ROM `0x15CD0` with a call to a small mapper:

- compact values `0..5` pass through unchanged;
- compact values `6..7` gain `2`, producing native stages `8..9`.

The initial mapper occupied ROM `0x9A700` / VA `0x80099B00`. Four-box integration relocates it to ROM `0x9AEFC` / VA `0x8009A2FC`, because the former selector cave is repurposed for inventory code. The current tests enforce the relocated mapper and the selection hook.

## Post-legal company/logo bypass

The owning frontend routine at `0x80079510` normally performs, in order:

1. a fixed splash through `0x8007C44C` using resources `0x3B4/0x3B5`;
2. a second fixed splash through `0x8007C50C` using resources `0x3B2/0x3B3`;
3. fade/normalization through `0x800615D8(0x80)`;
4. title handoff through `0x80078C40`.

Production changes only the guarded branch at VA `0x800797F4` / ROM `0x7A3F4` so execution skips the two fixed splash calls. The legal/MKMSZR branding screen remains visible, and the fade normalization plus title initialization/handoff continue unchanged.

The exact guard sequence and replacement instruction belong to the [Address and patch-site registry](Address-and-Patch-Site-Registry).

## Selector-specific automatic-save bypass

The relocated compact-stage mapper also writes nonzero byte `0x15` to `0x80291C0C` when returning a selector choice. Static executable inspection shows that, while armed, the native one-shot path skips both the immediate `0x8000E000(0x19)` stage-entry save setup and the following `0x800798A8` automatic-save call. Later/manual save flows are not generalized from this bypass.

This is deliberately selector-specific:

- it is armed only by the Safe Stage Select mapper;
- it does not replace or disable the generic save routine at `0x800798A8`;
- manual saves, later save flows, and normal post-stage saves remain available.

The exact emitted mapper bytes and guards belong to the [Address and patch-site registry](Address-and-Patch-Site-Registry).

## Fire God Room / Stage 7 static composition differential (research, 2026-09-28)

**Boundary.** This is a clean USA Rev. 0 ROM disassembly comparison, not a new build or emulator test. Stage 7 remains excluded from the safe selector. The user's v01 observation is bounded to adding Fire overlay file `0x9D` at `0x802ECE30`: geometry and the ordinary Sub-Zero player render and the room is interactive, but the scene is dark, movement initially delayed, ordinary facing/attacks and Pause/Inventory fail, and a falling scream plays. v02–v05 are insufficient negative controls, not accepted behavior.

Effective addresses below resolve sign-extended `addiu` offsets: `lui 0x8003; addiu -0x7154` installs **`0x80028EAC`** as the class-1 player callback at `0x8002ED30`, *not* `0x80038EAC`; `lui 0x8006; addiu -0x4050` schedules HUD function `0x8005BFB0`; `lui 0x8005; addiu -0x2410` schedules a separate class-`0x17` process at `0x8004DBF0`. The `0x800707EC` and `0x800707FC` calls seen in both constructors are returns without side effects in this ROM.

| Order / owner | Normal Fire selector `5` | Native Stage 7 / TEST LAB | Divergence classification and consumer |
|---|---|---|---|
| Entry and initial globals | `0x800108FC` invokes `0x80016D1C`: clears `0x800EEC1C`, initializes `0x800BF2A0..B0` lighting defaults, `0x800EED78=4`, `0x802E6E4C=0x40`, `0x802C100A=1`, `0x802ECE18=6`, `0x802C1A04=0`, then sets `0x800EEC1C=1`. At `0x80010994`, native stage becomes `5`, count `0x8009A9C8=0x1E`. | `0x80011070` omits the reset call. Immediately sets `0x800EEC1C=1`, `0x8009A90C=1`, `0x8009A910=7`, `0x8009A914=2`, selector `0x802C18F8=1`, count `0x8009A9C8=3`, and `0x802C1BB4=0x258`; it sets `0x802C1A04=1` at `0x8001150C`. Its player type and related defaults are written **after** player construction at `0x80011698..C0`. | **Player-control / lifecycle critical.** Type and stage/selector are consumed at `0x8002EC78/0x8002EF3C` and `0x8003BF4C` before the Stage-7 late write. Whether the pre-existing type happens to be `4` depends on preceding state; current observation shows a normal-looking player, not proof of identical preconstruction state. |
| Preliminary process and overlay | Fire at `0x80010978..88` allocates class `0x15`, callback `0x8000D940`, with process `+0x6F4` set to `5` or `-1`; on its fresh-load branch `0x800109E4..F4` loads Fire overlay `0x9D`. | Does neither in `0x80011070`; the v01 proof independently materialized file `0x9D` before Stage-7 init. | **Lifecycle / overlay critical.** The missing overlay accounts for the original hard failure; the preliminary process has not been proven to own the remaining input defects. |
| Scene and collision | Fire selector-5 branch at `0x80010B38..0x80010DAC` loads `0x40,0x5D,0x3F,0x87,0x3D,0x3E,0x41,0x3B` and calls `0x80002588` with `0x80111FF8`, `0x800BF28C` and `0x802C1B60`. | `0x80011180..0x80011368` uses the same files and parser inputs; `0x80011394` likewise calls `0x8000D080`. | **Shared.** Scene-package absence cannot explain the remaining v01 symptoms. Stage `7` and selector `1` still alter downstream stage/selector-indexed lookups, including player spawn `0x8003BF4C`. |
| Lighting, camera and timer preparation | `0x80016D1C` writes the baseline lighting vectors; `0x80010DE4..0x80010E2C` installs the Fire stage-indexed value at `0x800BF298`, zeros `0x800BF29C`, uses normal camera/scene globals. | `0x800113E0..0x80011464` writes essentially the same baseline vector constants and stage-indexed `0x800BF298` but with stage `7`, and `0x80011470..0x800114F0` does the ordinary matrix setup. | **Lighting/camera unresolved.** “No baseline light-vector initialization” is rejected. The direct read at `0x8001329C` of stage-indexed `0x800BF298` is in the `0x8009A914==0` branch; both entries set `0x8009A914=2`, so that read alone cannot explain darkness. Indirect lighting/render consumers remain to trace. The calls to `0x800707EC/FC` cannot themselves fix lighting. |
| Player construction / controller | `0x80010EBC` calls `0x8002EC78 -> 0x8002ECF4`, with the reset type `4` already set. This allocates class `1`, callback `0x80028EAC`, publishes `0x802C1AC0`, binds semantic input `0x800BF2EE` at controller `+0x638`, and publishes actor `0x802E73DC`. | Same constructor at `0x80011650`, same class `1`, callback and input binding, but its type `4` write is at `0x800116A0`. Both schedule class `0x15` `0x80063E90` and `0x80064788` afterward. | **Player-control critical / shared allocation.** No dummy-player explanation. `0x80028EAC` switches the live callback to `0x80028F3C` in controller `+0x6F0/+0x08`; the latter reads `0x800EEC1C` and dispatches input only through its permitted state paths. |
| Opponent and room helper | `0x80010F00` calls `0x80065428`: loads file `0x21`, initializes shared slot flags, schedules class `0x1E` `0x802EE34C`, class `0x50` `0x800653B0`, class `0x15` `0x802EDCE0`, class `0x15` `0x800655EC`, class `0x50` `0x8003BE94`, and sets `0x800C2564=1`. | `0x80011680` calls `0x80065668`; the debug index `0x800C1F64` is initialized `-1` by the debug selector (`0x8000D120`). Its negative branch at `0x8006594C` clears `0x802C1A04`, loads file `0x3C`, creates scene opponents and schedules class `0x15` `0x80065C38`, omitting the normal boss class-`0x50` pair. A nonnegative index takes a *different* test-character branch and clears `0x800EEC1C` instead. | **Boss/debug-opponent and player-control critical.** The negative branch's `0x802C1A04=0` directly gates live input at `0x80029190`. The nonnegative branch cannot be substituted as an explanation for this native Stage-7 route without evidence that its selector was entered. |
| HUD setup and frame predicate | `0x80010F40..54` schedules class `0x15` HUD `0x8005BFB0` and class `0x17` `0x8004DBF0`; HUD initializes slots `0x11..0x16`, then on each iteration reads player controller `0x802C1AC0`, player health `+0x654/+0x656`, and submits nodes only after its vertical-position test `0x8005C5A0`. | `0x800116FC..0x80011710` schedules the **same** HUD and class-`0x17` process. | **HUD: common initializer, visibility still unproven.** Scheduling is not evidence that nodes actually reached the render queue. No Stage-7-only HUD disable branch has been established; test the HUD position/render predicate before attributing it to a missing constructor. |
| Script, Pause/Inventory and synchronization | Fire sets stage script `0x800C11E4=0x800B3A54`, sentinel stream entries, class `0x70` `0x80071500`, class `0x101` `0x80061678`, then class `0x75` `0x80017024`; it clears `0x800C255A` before scheduling class `0x101`. The class-`0x75` callback waits eight ticks, waits for class `0x101` and stage count, sets `0x800EEC1C=0`, `0x802C1A04=1` for stage `5`, and updates process state. | Lacks the class `0x70` stage script and class `0x75` transition, but does schedule class `0x101` `0x80061678`; there is no matching `0x800C255A` clear in its entry routine. Debug helper's negative branch suppresses `0x802C1A04` without the normal transition to restore it. | **Lifecycle/timing and player-control critical; Pause/Inventory gates traced.** `0x80028F3C` polls `0x802C1A04` at `0x80029190`; zero loops into the suppressed path instead of ordinary action dispatch. `0x800EEC1C` is read by `0x80028F3C/0x80028DEC` and gates dispatch at `0x800156E0`. Pause entry `0x80015088` exits if `0x800C255A` is nonzero; at process state `0x802ECE18=2` it otherwise allocates class `0x400` `0x80016300` (PAUSED). Inventory entry `0x80014FC0` checks state `2`, semantic input `0x800BF2EE & 0x800`, stage and selector, player HP, and player action `+0x6AA` (`0x302/0x303/0x30F`) or `+0x6B0` before allocating class `0x100` `0x80073588`. The Stage-7 live values and upstream input-event dispatch remain unmeasured; either menu's reported inactivity cannot be assigned to one flag. |
| Sound, finalization | Normal helper schedules delayed `0x800655EC` (60-tick music event), the main branch emits resource `0x1C1`, marks `0x8009A9D0=1` and exits through `0x80028564`. | Debug helper immediately calls `0x80080A88(0x22E)` at `0x80065BE4`, then Stage 7 emits `0x8A/0x8B`, calls `0x80000A48(0)`, marks the same `0x8009A9D0=1` and exits through `0x80028564`. | **Presentation-only audio.** The immediate debug audio explains the initial scream; v03 adding delayed `0x800655EC` duplicated audio/music without restoring gameplay. The stage-active finalizer is shared. |

**Direct dependency chain:** selector `0x800C1F64=-1` → debug helper negative branch → `0x802C1A04=0` → live player callback `0x80028F3C` at `0x80029190` enters suppression loop → ordinary action/facing dispatch is not reached by that path. Normal Fire instead runs class `0x75` `0x80017024` → after intro/class-`0x101`/stage-count synchronization, `0x800EEC1C=0` and `0x802C1A04=1` → player action path eligible. The callback swaps from `0x80028EAC` to `0x80028F3C` during startup; preconstruction actor type/spawn and already-entered action/animation paths are also latched. These static gates explain why a **late** write need not reproduce the normal initialization, but do **not** prove that a particular latch caused the v05 negative result.

**Rejected / insufficient diagnostics.** v02 cleared only `0x800EEC1C` after the debug helper (no change); v03 added normal delayed `0x800655EC` (second scream, duplicated music, controls unchanged); v04 added `0x80016D1C` and class-`0x75` `0x80017024` after debug setup (no change); v05 restored both `0x802C1A04=1` and `0x800EEC1C=0` after helper (no change). These do not establish that the correct *entry-order* composition fails. No Stage-7 production patch is justified by the two gate values alone.

**Next bounded proof design (proposed, unbuilt).** A one-site composition *positive control* changes Stage-7 entry at `0x80011070` to set selector `0x802C18F8=5` and tail-jump to normal Fire entry `0x800108FC`; its exact clean-ROM guard and five replacement words are in the [Address and patch-site registry](Address-and-Patch-Site-Registry). The normal Fire entry sets native stage `5` at `0x80010994` and on its fresh-load branch loads overlay file `0x9D` at `0x800109E4..F4`. Build this as a separate clean-ROM v06 positive control rather than layering v01–v05 writes; no such ROM has been built. Success would localize the missing *composition* but would **not** retain Stage-7's debug opponent, identify the darkness cause, or prove a native Stage-7 repair. Before a native Stage-7 repair is specified, resolve the runtime values at the Pause and Inventory gates, the lighting consumer, and preconstruction `0x800EED78`. No emulator was run for this analysis.

## Functional TEST LAB proof harness (Runtime-confirmed, 2026-09-28)

The hidden Fire God Room research was extended into a **proof-only TEST LAB**. This does **not** add native Stage 7 to the production safe selector. The accepted disposable composition uses the healthy normal Fire selector-5 shell plus selected-Test-Characters helper behavior, suppresses the selected fighter allocation, and preserves the normal Fire lifecycle that restores controls/HUD/Pause/Inventory.

Current bounded state:

- v10 is the stable empty-room baseline: normal lighting, HUD, movement, attacks, Pause/Inventory, and no opponent allocation;
- selector 5 skips ordinary overlay entry `0x802ECE30`, so ordinary pickup/resource setup must be installed explicitly for TEST LAB;
- v15 established explicit Fire file-`0x3C` loading plus an isolated class-`0x19` pickup manager with safe parent `+0x6F4/+0x6F8` save/restore;
- v21 Runtime-confirmed three correctly rendered Herbs at 96-world-unit spacing, all three collectible;
- later proofs reused the room as a bounded cross-stage item-materialization stress harness;
- v33 Runtime-confirmed a stable, recognizable 15-live non-Earth key composition using the native Fire resource-file architecture.

The detailed v01-v33 chronology, including rejected custom-gallery builds and corruption controls, is owned by [TEST LAB proof history](Test-Lab-Proof-History).

The harness remains disposable proof infrastructure. Its proof caves, high-ROM resource relocation, selector changes, and item-manager setup are not production allocations and must not be copied into the browser/CLI pipeline without normal allocation/composition gates.

## Rejected or superseded flow approaches

- **Start-button selector shortcut — Rejected / failed.** The attempted shortcut behaved intermittently. Start is not a supported alternate selector entry; the production route is the A-button title path.
- **Remove/bypass the entire owning frontend routine — Rejected.** That would also skip required fade normalization and title state instead of only the two fixed logo presentations.
- **Patch generic save code — Rejected.** Suppressing the generic save routine would affect unrelated save flows and unnecessarily expand lifecycle risk.
- **Global “never save on entry” state — Rejected as unnecessary.** The game already exposes a scoped one-shot byte, so the selector uses that native mechanism instead of inventing a broader policy.

The accepted implementation therefore keeps the normal loader/save machinery and changes only the smallest guarded frontend branch plus the existing selector mapper behavior.

## Runtime and implementation evidence

| Claim | Evidence | Scope / limit |
|---|---|---|
| A-button Safe Stage Select route reaches all eight allowed stages | **Runtime-confirmed** | Tested across Temple, Wind, Water, Earth, Prison, Fire, Bridge, and Fortress; excluded stock entries are not exposed |
| Compact/native mapping preserves the eight intended destinations | **Runtime-confirmed** with static/CI support | Runtime coverage is the eight safe destinations; tests enforce the table, hook, mapper, and relocation |
| Post-legal company/logo presentations are skipped while legal screen and later title flow remain intact | **Runtime-confirmed** | Bounded boot/frontend route |
| Selector entry skips only the immediate automatic stage-entry save prompt | **Runtime-confirmed** | Normal manual/later/post-stage save behavior remains intact on the validated routes |
| Guarded patch scope matches the intended branch/mapper-only changes | **Implementation/CI-confirmed** | `test_stage_selector.py` and `test_flow_bypass.py`; CI does not replace runtime validation |

For the concise cross-domain evidence matrix, see [Runtime validation status](Runtime-Validation-Status).

## Related canonical owners

- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded patch sites, expected bytes, and replacement effects.
- [Function registry](Function-Registry) — function semantics such as the native debug selector and relevant frontend/save routines.
- [Memory and allocation map](Memory-and-Allocation-Map) — ownership of the relocated mapper/bootstrap regions; a historical proof cave is not implied to be production-safe.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — broader save/inventory lifecycle behavior outside the selector-only bypass.
- [Runtime validation status](Runtime-Validation-Status) — concise evidence scope by subsystem.
