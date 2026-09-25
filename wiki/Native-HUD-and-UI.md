# Native HUD and UI

> **Scope:** This page is the canonical owner for the gameplay HUD hook, native gameplay text, render-node usage, the production box indicator, generic renderer conclusions, and 1.0 randomizer-HUD implementation/reference material.
>
> Stable render-node structure grammar remains canonical in [Data structures and encodings](Data-Structures-and-Encodings). Title/legal branding belongs to [Presentation and branding](Presentation-and-Branding). The full Toasty visual diagnostic chronology belongs to [Toasty visual research](Toasty-Visual-Research).

## Current conclusion

The normal gameplay HUD path at `0x8005BFB0`, native text renderer `0x80073E74`, and the production `BOX n OF 4` indicator are **Runtime-confirmed**. The complete 1.0 randomizer HUD is still **Pending**.

The generic renderer boundary is now narrower and better established than the earlier mixed page implied: the `0x80073CEC -> 0x8001E578` family is real but context-specific, while the actual gameplay-HUD queue can accept MKMSZR-owned additional textured nodes. Toasty diagnostics v08-v16 are the proof source for those reusable conclusions; their version-by-version evidence and rejected controls are canonical in [Toasty visual research](Toasty-Visual-Research).

## Confirmed gameplay HUD path

The stable gameplay HUD function is `0x8005BFB0`. It contains 13 calls to node submitter `0x8001EAE4`. Production hooks one call at ROM `0x5D9CC`, executes the displaced submission first, then draws the box indicator.

Render nodes are allocated by `0x8002018C` and submitted by `0x8001EAE4`. The stable `0x58`-byte node structure grammar is canonical in [Data structures and encodings](Data-Structures-and-Encodings); this page owns how the gameplay HUD uses those nodes.

## Native text

| Purpose | Address |
|---|---:|
| Text draw | `0x80073E74` |
| Width calculation | `0x80074084` |
| Font data | `0x800B1E20` |

Arbitrary null-terminated strings placed in custom RDRAM were runtime-confirmed. This is the preferred path for small persistent gameplay labels.

The production wrapper occupies ROM `0xAFA24..0xAFA97`, begins at VA `0x800AEE24`, and stores its string at VA `0x800AEE80`. It reads active-box state, rewrites the digit in `BOX 1 OF 4`, and draws at `x=230`, `y=210`. This area was originally legal-screen text, but the exact stock bytes are guarded and boot branding owns the adjacent strings.

## Context-specific renderer family

The path beginning at `0x80073CEC` and calling `0x8001E578` is real, but evidence shows it is context-specific rather than a universal always-on HUD/sprite API. Its suitability as a generic presentation abstraction remains unproven.

## Gameplay render-node usage and generic conclusions

The canonical field layout for a native `0x58` render node is documented in [Data structures and encodings](Data-Structures-and-Encodings). The reusable UI conclusions are:

| Claim | Evidence | Limit |
|---|---|---|
| An added MKMSZR-owned textured node can be submitted through the normal gameplay-HUD queue | **Runtime-confirmed**, Toasty visual v08 | The proof cloned an already-built stock HUD node; it did not establish an arbitrary universal sprite API |
| Node halfword `+0x4A` selects the texture slot used by the gameplay HUD renderer | **Runtime-confirmed**, v09-v10 | v10 confirms clone-local rebinding without damaging the stock source node |
| The corrected fixed-slot record base is `0x802E83F0`; backing-pointer base is `0x800ED940` | **Runtime-confirmed control**, v14, with static audit | Earlier v12-v13 alias experiments used incorrect address formation and are rejected |
| A dynamic CI8 allocation can feed genuine imported image pixels to an added gameplay-HUD node | **Runtime-confirmed**, v15 | v15 intentionally inherited the wrong stock palette |
| Dynamic slot record `+0x08` is the DRAM source-image width consumed by `0x8001F7A8` `SetTextureImage` | **Static-confirmed**, post-v37 trace | `0x8001C2B4` can reuse a capacity-compatible record without refreshing this field; stock callers rewrite it after allocation |
| Node halfword `+0x4C` is the palette selector used by the gameplay renderer | **Static/implementation-confirmed**, v16 | v16 genuine-palette runtime validation is still Pending in the current chronology |

These are generic renderer conclusions only. Full proof identities, failures, and supersession are canonical in [Toasty visual research](Toasty-Visual-Research).

## Pickup presentation descriptors

| Descriptor | ROM | Count/use |
|---:|---:|---|
| `0x800B1BAC` | `0xB27AC` | Potion, 16 entries |
| `0x800B1BD0` | `0xB27D0` | Generic A/crystals |
| `0x800B1D18` | `0xB2918` | Generic B/keys and icons, 14 entries |
| `0x800B1D38` | `0xB2938` | Jar/item presentation |

The resource selector in a pickup record is stage-local; its presentation descriptor alone does not import model data.

## Rejected or bounded renderer approaches

- Direct framebuffer drawing was unstable and remains rejected.
- Searching for one universal sprite API produced context-dependent candidates rather than a safe abstraction.
- An inline wrapper that allocates/submits multiple nodes is viable; the earlier over-generalized helper layer was not.
- Direct gameplay use of `0x80073CEC` is not accepted as a generic gameplay sprite path; preserved evidence and the Toasty v08+ line instead point to the actual gameplay-HUD queue.

## 1.0 randomizer HUD implementation/reference

[1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) is the canonical owner of the release requirement and acceptance criterion. The legacy Lua overlay is only the semantic reference for what run state the player needs; exact visual parity and Lua-style inventory paging are not requirements.

The reconciled 1.0 HUD must expose:

- current-stage check progress, including collected / total information useful for the current stage;
- required Power Upgrades and the player's current progression status;
- current native box/storage state;
- key-item progress by stage;
- useful temporary pickup feedback.

The existing Runtime-confirmed `BOX n OF 4` text satisfies only the storage-state part of that requirement. The native text path at `0x80073E74` remains the preferred basis for persistent labels. A text-first implementation is acceptable; geometric icons or textured elements should use the proven gameplay-HUD queue only where they materially improve the final HUD and have their own bounded validation.

## Frontend OPTIONS / Randomizer Settings architecture

### Static title -> OPTIONS trace

**Static-confirmed on the clean USA Rev. 0 ROM.** The title controller at `0x80078C40` dispatches the title `OPTIONS` choice through `0x800762C4`. The OPTIONS loop reads the remapping-independent frontend input word at `0x800BF2EE`, draws through frontend text renderer `0x8001CA88`, and uses the stock frontend background/render path.

The current selectable OPTIONS rows are:

| Index | Label | Handler |
|---:|---|---:|
| 0 | `CONTROLLER CONFIGURATION` | `0x8007739C` |
| 1 | `SOUND CONFIGURATION` | `0x80076D74` |
| 2 | `CONTROLLER PAK` | `0x8007816C` |
| 3 | `PASSWORD` | `0x8007550C` |
| 4 | `GAME SETTINGS` | `0x800766BC` |
| 5 | `EXIT` | returns from the OPTIONS loop |

The five real submenu handlers are selected through the five-word jump table at VA `0x800AEAB8` / ROM `0x000AF6B8..0x000AF6CB`. The next bytes at ROM `0x000AF6CC` begin the `VERY EASY` string, so the stock jump table cannot simply grow in place.

The observed frontend input masks are:

- `0x4000` / `0x1000`: previous/next row;
- `0x2000` / `0x8000`: right/left value edit inside GAME SETTINGS;
- `0x0002`: enter/confirm;
- `0x0001`: back/exit.

`GAME SETTINGS` at `0x800766BC` is the strongest native template for an MKMSZR settings page. It already implements a reusable three-row selection loop, per-row left/right value editing, highlighted text style, stock menu SFX, confirm/back handling, and redraw through `0x8001CA88`. Its stock rows are `DIFFICULTY`, `LIVES`, and `CONTINUES`, backed by halfwords `0x800A5FA8`, `0x800A5FAA`, and `0x800A5FAC`.

### Proposed Randomizer Settings architecture

The accepted production-facing design is to keep the existing top-level **`GAME SETTINGS`** entry and selector geometry unchanged, but replace the contents of that submenu with MKMSZR-owned settings. This is intentional: vanilla GAME SETTINGS only controls Difficulty, Lives, and Continues, while MKMSZR plans to own those run values/invariants itself. Once those values are hardcoded/managed by the randomizer, exposing the stock editor would be redundant and could allow the player to contradict MKMSZR run state. Keeping the familiar GAME SETTINGS label avoids unnecessary top-level menu changes while giving MKMSZR one native-looking settings home for future options.

The submenu should be table-driven rather than one-off code:

```text
setting row:
    label pointer
    state bit / enum descriptor
    value-string table
    visibility predicate
    optional on-change callback
```

A common menu loop can then own row navigation, left/right mutation, rendering, highlight style, sound, exit, and per-row **visibility**.

The accepted initial GAME SETTINGS model is:

| Setting | Values | Availability |
|---|---|---|
| `TURN` | `TOGGLE` / `LOCK` | Always |
| `COMBOS` | `CLASSIC` / `ASSIST` | Always |
| `SPECIALS` | `CLASSIC` / `MODERN` | Always |
| `JUMP` | `DPAD` / `BUTTON` | Visible only when `COMBOS != CLASSIC` **or** `SPECIALS != CLASSIC` |

`TURN: TOGGLE` means the stock control model: Turn performs the normal standing/crouched turn action and the v10 facing-lock policy is bypassed. `TURN: LOCK` means the v10 model: Left/Right follows world direction with immediate facing correction, while held Turn locks facing and uses vanilla backward movement. Releasing Turn while holding direction immediately returns to auto-facing/forward locomotion. The same TURN setting must gate all v10 behavior changes together: opposite-direction auto-facing, active-backward release, and pre-dispatch suppression of player Turn states 23/24. Semantic Turn/Combine bit `0x0001` remains untouched in both modes.

`COMBOS: CLASSIC / ASSIST`, `SPECIALS: CLASSIC / MODERN`, and `JUMP: DPAD / BUTTON` are accepted menu/product semantics, but their gameplay implementations are **Pending** and must not be inferred from these labels alone. `JUMP` is a **visibility dependency**: it is omitted when both COMBOS and SPECIALS are CLASSIC, and appears as soon as either alternate control system is enabled. Because only the highlighted row can be edited, changing COMBOS/SPECIALS changes JUMP visibility while the cursor remains on COMBOS or SPECIALS; no special cursor-recovery case is required.

The settings state should be a versioned MKMSZR bitfield, not individual ad-hoc globals. The first bit can represent the direction-facing preference and later bits/enums can be added without redesigning the menu. The preferred owner is the existing final Runtime V2 word `0x801AF81C..0x801AF81F`, promoted explicitly from **reserved** to a named `settings_flags` word when implementation begins. Runtime V2 initialization validates `MKSV`/version/size and returns without clearing a valid state block; only invalid/uninitialized state is zeroed. That makes this word suitable for title -> gameplay -> stage-transition/session persistence without inventing another lifecycle domain. The setting convention has an explicit user-facing default: `TURN = TOGGLE` (vanilla behavior) on fresh/uninitialized state, while `TURN = LOCK` is opt-in. The proof should validate a dedicated settings marker rather than relying on arbitrary RAM contents; invalid/uninitialized state is normalized to `TOGGLE`.

For the first proof, persistence should be **session/run-lifecycle only**: the value must survive leaving the submenu, title navigation, and stage transitions. Cold-boot/controller-pak persistence is desirable because this is a user preference, but is a separate gate. Static frontend/save tracing shows the stock GAME SETTINGS globals are copied into and restored from per-profile structures, so there is a native persistence model to study; no unused field or checksum-safe extension is currently proven safe for MKMSZR ownership. A production decision can therefore be made later between true save persistence and a ROM-generated default plus session override.

### Smallest first proof plan

Do **not** extend the top-level OPTIONS row count. Redirect the existing GAME SETTINGS handler slot to an MKMSZR settings proof page; if the proof succeeds, that same replacement becomes the production architecture. The stock top-level OPTIONS list, cursor bounds, EXIT index, and five-entry dispatch-table shape can remain unchanged.

The bounded proof should:

1. reuse the native GAME SETTINGS visual/input loop shape and stock frontend text renderer;
2. keep the submenu title/context as `GAME SETTINGS`; for the **smallest first proof**, expose only `TURN: TOGGLE / LOCK` plus `EXIT`, while using a descriptor shape that already supports the accepted COMBOS/SPECIALS/JUMP rows above;
3. store the TURN value in one explicitly named proof state word/byte whose title-stage lifecycle is independently marked/checked;
4. gate the v10 control-facing helpers on that state;
5. manually test `TOGGLE -> gameplay`, `LOCK -> gameplay`, return to title, and re-enter the page;
6. leave Inventory Combine on semantic Turn/Combine `0x0001` and verify it once in each mode.

After TURN is stable, the next UI-only proof should add COMBOS/SPECIALS/JUMP descriptors and validate JUMP's show/hide behavior and row layout across all four COMBOS/SPECIALS combinations before those control modes themselves are implemented.

After that succeeds, production should keep the existing OPTIONS topology and the displayed `GAME SETTINGS` label, while permanently replacing only handler index 4's submenu implementation. There is then no need to relocate or enlarge the top-level dispatch table, no need to change the selector maximum, and no need to move `EXIT`.

### TURN menu proof v02/v03

**v02 — Partially Runtime-confirmed.** The stock GAME SETTINGS presentation was successfully reduced to a visible `TURN` row with `TOGGLE / LOCK`, and both values correctly controlled gameplay: `TOGGLE` restored vanilla Turn behavior and `LOCK` activated the accepted v10 facing-lock behavior. The user reported the linked behavior as working excellently. B/Turn still exited the submenu normally.

v02 exposed one narrow navigation defect: the stock GAME SETTINGS selector uses indices 0/1/2 for its three settings and index 3 for `EXIT`. Reducing the down-bound to index 1 made an invisible former row selectable while making `EXIT` unreachable by cursor. This does **not** invalidate the menu->state->v10 linkage.

**v03 — Runtime-confirmed.** Keeping stock `EXIT` at index 3 while changing vertical navigation to jump directly `0 <-> 3` fixes the v02 cursor defect: TURN and EXIT are both selectable, EXIT returns normally, and the hidden former Lives/Continues rows are no longer reachable. The user reported the menu works perfectly. TURN/state/v10 behavior remains correct in both `TOGGLE` and `LOCK`; fresh/uninitialized state defaults to `TURN: TOGGLE` and `LOCK` remains opt-in.

**v04 — Runtime Pending boss-fallback proof.** v03 exposed one gameplay-composition issue: `TURN: LOCK` remained partially active during stock boss/special forced-facing, causing retreat movement to fight the game's own auto-facing. v04 keeps the v03 menu/state unchanged but makes the stock face-policy scanner at `0x8004A6E8` gate all three LOCK paths. When the scanner reports forced-facing (`0x8000`), gameplay temporarily uses stock/`TOGGLE` semantics without changing the saved menu value; LOCK resumes automatically when forced-facing ends. The first Scorpion encounter is the bounded manual runtime gate. Earth remains explicitly Pending because its custom type-`0x19` path is not statically proven to use the generic `+0x6BC & 0x0200` policy.

The stock GAME SETTINGS implementation remains the accepted native behavioral template even though its Difficulty/Lives/Continues editing behavior is no longer exposed.

## Related canonical owners

- [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) — normative HUD requirement and final acceptance gate.
- [Data structures and encodings](Data-Structures-and-Encodings) — stable render-node structure grammar.
- [Function registry](Function-Registry) — function semantics for native text, allocation, submission, and related helpers.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal production/proof allocation ownership.
- [Presentation and branding](Presentation-and-Branding) — legal screen, title art, edition text, boot phrase presentation, and visual acceptance.
- [Toasty visual research](Toasty-Visual-Research) — Toasty visual target, complete v01-v16 chronology, rejected diagnostics, and proof provenance.
