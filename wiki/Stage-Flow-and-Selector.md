# Stage flow and selector

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


### Blue cursor + title-menu SFX proof status (bounded runtime, 2026-09-30)

The clean USA Rev. 0 cursor comparison resolves the visual change without importing file `0x5E` into the selector lifecycle:

- selector frames `0x352..0x35A` in global file `0x5F` and title frames `0x3CC..0x3D4` in global file `0x5E` have byte-identical indexed pixel payloads for all nine corresponding frames;
- both cursor presentations use all 29 palette indices `0..28`;
- selector palette source ROM `0x000B21D8` and title cursor palette source ROM `0x000B32E8` differ in 27 of 29 entries.

The proof therefore keeps selector file `0x5F`, sprite IDs `0x352..0x35A`, registration slot `0x1C2`, and the existing `0x8001D520` draw path unchanged, copying only the title cursor's 58-byte palette into the selector-local palette source. Files `0x5E` and `0x5F` remain byte-for-byte unchanged.

**Runtime-confirmed from proof v01:** the selector cursor is blue and animates correctly; the title-menu movement sound is audible on Up/Down navigation. This is bounded frontend evidence, not yet a production integration claim.

**Confirmation correction.** v02 incorrectly treated semantic A bit `0x0002` as the selector's commit control. Runtime showed A plays the requested chime but does not choose a stage. Static reconciliation identifies the actual selection owner as the Start-event callback table entry at ROM `0x0009B730`, which points to `0x80015088`; in state `0x18`, that callback runs the compact-stage commit path at `0x800150C8..0x800150F4`. A-based confirmation is therefore Rejected / failed.

**Audio-corruption warning.** After v02, the user observed delayed choppy/crunchy/noisy stage audio several seconds after stage load. This is treated as a possible regression/corruption symptom until isolated. Static binary audit found no unexpected ROM edits and no direct branch/jump/JAL targets into the reused helper span at `0x8000D67C..0x8000D6AC`; the added helper itself performs no arbitrary memory stores outside the native `0x80064C18` SFX path. That does not clear the audio lifecycle: a frontend voice or indirect SFX-state side effect may still survive incorrectly into stage teardown/load.

Two clean-ROM isolation controls are the next runtime gate:

- **v03a blue + MOVE only:** selector-local blue palette plus descriptor `0x1FC` on valid Up/Down edges; no `0x1FD` confirmation call and stock Start commit path untouched.
- **v03b blue only:** selector-local blue palette; no added SFX calls and stock Start commit path untouched.

Do not design another Start-confirmation hook until those controls establish whether the delayed audio defect follows the movement SFX path or only the rejected v02 `0x1FD` path.

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

The relocated compact-stage mapper also writes nonzero byte `0x15` to `0x80291C0C` when returning a selector choice. Stock stage-entry code already recognizes this byte as a one-shot bypass for the immediate automatic stage-entry save prompt.

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
