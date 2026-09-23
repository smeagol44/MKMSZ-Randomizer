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
