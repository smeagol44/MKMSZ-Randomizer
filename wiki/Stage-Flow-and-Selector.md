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

### Hidden native stages 6 and 7 — static first pass

The common stage loader `0x80016080` dispatches native stage IDs through a 12-entry jump table at VA `0x800AA330` / ROM `0xAAF30`.

- **Native stage 6 / UNUSED:** its jump-table entry is `0x800162D8`, which is the loader's common cleanup/return tail. Unlike the normal stages, it schedules **no per-stage entry callback at all**. The generic >=2 spawn-pointer table also has a null stage-6 entry. A small default spawn row still exists in the selector<2 table, so some data survived, but there is no stock initialization path that reaches normal stage construction. This matches the historical softlock/freeze and makes stage 6 an abandoned placeholder rather than a ready-made hidden arena.
- **Native stage 7 / FIRE GOD ROOM:** its jump-table entry schedules `0x80011070`. Native mode 10 / TEST CHARACTERS converges on this exact same routine after a character selection; before selection, mode 10 schedules the 25-entry character selector instead. Thus stage 7 is not an empty placeholder: it owns substantial debug-arena/gameplay initialization and is the arena reused by Test Characters.
- `0x80011070` explicitly restores native stage ID `7`, sets the broader stage selector to `1`, constructs the normal Sub-Zero player, loads the ordinary gameplay HUD, and calls test-character loader `0x80065668`. Its resolved direct file-load set is `0x40, 0x5D, 0x3F, 0x87, 0x3D, 0x3E, 0x41, 0x3B`, all of which are also loaded by the normal Fire-stage entry path. It does **not** load one of the eight normal gameplay overlays at `0x802ECE30`.
- When no test-character selection exists, `0x80065668` takes a fallback path that loads global file `0x3C` into the current stage-resource pointer `0x802F82B8`. File `0x3C` is Fire's stage resource file. With a valid test-character selection, the same helper instead consumes the 25×`0x1C` test-character record table and loads/spawns the selected fighter resources.

#### Stage 7 identity versus the normal Fire boss room

A second static pass resolves the room identity much more strongly.

The normal Fire initializer `0x800108FC` has a dedicated branch when `0x802C18F8 == 5`. On the natural Fire path, Fire-overlay code at `0x802EE75C..0x802EE764` (ROM `0xE34AC..0xE34B4`) writes selector **5** before the special-area transition. That selector-5 reload uses the secondary Fire resource set:

`0x40, 0x5D, 0x3F, 0x87, 0x3D, 0x3E, 0x41, 0x3B`.

Native stage 7 / `FIRE GOD ROOM` initializer `0x80011070` loads **the exact same eight global files**.

More decisively, both routes call scene parser `0x80002588` with the same scene/collision inputs: file-`0x3D` allocation as the primary scene input, file-`0x41` allocation as the paired input, publication through `0x80111FF8`, auxiliary table `0x800BF28C`, and state block `0x802C1B60`. Therefore stage 7 and normal Fire selector 5 construct the same secondary Fire scene/collision package.

The spawn data independently agrees on the room's X coordinate. Normal Fire selector 5 resolves to spawn record `0x800A00CC`, whose X is `0xFFFD3DEB`; native stage 7's selector-1 default row at `0x800A02D8` uses the same X. Its Y/orientation fields differ, so the debug entry point is not byte-for-byte the normal boss spawn.

The encounter setup then deliberately diverges:

- **Normal Fire selector 5:** after player construction, `0x800108FC` calls `0x80065428`. That helper loads global file `0x21` into resource-pointer slot `0x800C25B4`; the fighter-type table maps type `0x0C` to that exact slot. The selector-5 enemy stream is `0x800B3A54`, the dedicated one-spawn type-`0x0C` encounter.
- **Native stage 7 / Test Characters:** after player construction, `0x80011070` calls `0x80065668` instead. That helper either loads/spawns the selected Test Characters fighter or, with no selection, takes its fallback resource path.

**Static conclusion:** `FIRE GOD ROOM` is the **same secondary Fire/boss-arena scene shell used by normal Fire selector 5**, entered through a separate debug initializer. It is not a distinct hidden Fire-themed room. It is also not literally the normal boss fight: the direct/debug route substitutes the Test Characters/debug-opponent setup for normal Fire's type-`0x0C` boss setup and uses a different spawn-state row.

#### Why direct FIRE GOD ROOM does not finish loading

The direct-entry failure now has a concrete static owner.

The native debug stage-select routine resets Test Characters selection state `0x800C1F64` to `-1` before a stage is chosen. Therefore selecting native stage 7 reaches `0x80011070 -> 0x80065668` with a negative test-character index and necessarily takes `0x80065668`'s fallback branch.

That fallback constructs the Fire-derived scene/resource state, but it also schedules two callbacks whose addresses are **inside the Fire gameplay overlay**:

- `0x802EE34C` — scheduled by the negative-selection branch;
- `0x802EDCE0` — scheduled by the common tail.

Fire overlay file `0x9D` is raw ROM `[0xE1B80,0xE6610)` and normally owns runtime `0x802ECE30..`. Thus those two callback addresses correspond to Fire-overlay ROM `0xE309C` and `0xE2A30` respectively. `0x80011070` never loads file `0x9D` into `0x802ECE30`.

The normal Fire selector-5 boss route proves this dependency rather than merely suggesting it. Normal Fire loads file `0x9D` to `0x802ECE30` before branching on selector 5. Its boss helper `0x80065428` then schedules the **same** `0x802EE34C` and `0x802EDCE0` overlay callbacks. In normal Fire their code owner is resident; in direct stage 7 it is not.

**Static-confirmed structural failure:** FIRE GOD ROOM reuses Fire-overlay callbacks without loading the Fire overlay that contains them. The shared overlay region can therefore contain stale/unrelated bytes when those processes run. This is sufficient to explain why the retail direct-entry route cannot complete reliably.

The selected Test Characters route is not a clean counterexample: although its positive-index branch differs, `0x80065668` still reaches the common tail and schedules `0x802EDCE0`, while `0x80011070` still has not loaded file `0x9D`. This is consistent with native Test Characters also being unsafe in the retail build.

**Minimal repair candidate — Static-confirmed design / Runtime Pending:** load raw Fire overlay file `0x9D` to its stock fixed destination `0x802ECE30` early in `0x80011070`, before `0x80065668` can publish either overlay callback. This is a fixed overlay load, not a new stage-arena bump allocation. The scene/resource shell is already constructed by the existing stage-7 initializer. A disposable proof still needs guarded integration and manual runtime validation before the room can be called usable.

This makes stage 7 a strong future MKMSZR laboratory candidate: the room geometry/collision already exists and is shared with the real Fire boss area, and the first structural repair is narrowly identified. Stage 6 remains materially less promising unless MKMSZR supplies a new stage-entry implementation.

#### TEST LAB v01 runtime result and control-gate follow-up

Disposable proof `MKMSZR_test-lab_firegod-proof_v01.z64` (SHA-256 `3a824917e334ec526553a820e435771f4b81bbaa33b3934efb120d5c27260ec8`) added the missing file-`0x9D` load, exposed native stage 7 as **TEST LAB**, and preserved the compact selector/logo-skip test harness.

**Runtime-confirmed:** the arena now loads far enough to render the Fire boss-room scene and Sub-Zero and remain interactive rather than hanging. The user observed that the room was extremely dark; initial movement was delayed for several seconds; ordinary turning did not change facing unless blocking; Pause/Inventory and HP/LP/HK/LK were inert. Therefore the overlay-owner repair fixes the original hard entry failure but does not make the retail debug composition a normal gameplay stage.

Static follow-up isolates a strong control-state cause. `0x80011070` sets `0x800EEC1C = 1`. In `0x80065668`, the **selected Test Characters** branch clears that word back to zero, while the **negative-selection** branch used by direct TEST LAB does not. Generic fighter semantic-event dispatcher `0x800155C0` checks `0x800EEC1C` and returns early from normal event dispatch while it is nonzero. This matches the dead attack/ordinary-turn symptom family; block-facing can use a different live-action path.

Normal Fire additionally schedules `0x80017024`, which eventually clears `0x800EEC1C` after its intro/process conditions. Stage 7 does not schedule that process. For a laboratory route, copying the entire normal Fire boss-intro process would add unrelated behavior, so the smallest diagnostic is to mirror Test Characters' explicit control unlock instead.

Disposable v02 therefore preserves v01 and changes only the stage-7 call to `0x80065668`: a proof helper calls the stock function, clears `0x800EEC1C`, then resumes at `0x80011688`. Lighting is deliberately unchanged. Runtime validation is Pending.

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
