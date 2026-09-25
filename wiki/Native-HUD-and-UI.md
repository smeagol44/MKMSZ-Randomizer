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

## Related canonical owners

- [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) — normative HUD requirement and final acceptance gate.
- [Data structures and encodings](Data-Structures-and-Encodings) — stable render-node structure grammar.
- [Function registry](Function-Registry) — function semantics for native text, allocation, submission, and related helpers.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal production/proof allocation ownership.
- [Presentation and branding](Presentation-and-Branding) — legal screen, title art, edition text, boot phrase presentation, and visual acceptance.
- [Toasty visual research](Toasty-Visual-Research) — Toasty visual target, complete v01-v16 chronology, rejected diagnostics, and proof provenance.

## Production GAME SETTINGS / TURN controls

The stock top-level `GAME SETTINGS` entry is now reused by the shared browser/CLI patch core for a native one-row MKMSZR settings page. The production page exposes `TURN: TOGGLE / LOCK` plus `EXIT`, defaults to `TOGGLE`, and keeps the stock frontend renderer/input loop rather than introducing a separate web-only option.

**Runtime-confirmed production composition:** menu entry/exit, TOGGLE and LOCK behavior, inventory-box switching, a stage transition, both former Temple hang regressions, and first-Scorpion forced-facing fallback were manually validated in the full production build with optional Toasty composition. During a detected forced-facing encounter, a selected `LOCK` temporarily behaves as stock/TOGGLE without changing the stored preference; LOCK resumes afterward. Earth type `0x19` remains outside this runtime claim.

The first production integration attempt is **Rejected / failed**: it tried to raw-load shared file `0x1A` into the gameplay expansion pool while still in the title/frontend lifecycle and hard-hung immediately on entering GAME SETTINGS. The accepted implementation keeps the menu wrapper in global/title-resident code and loads file `0x1A` only at stage initialization.

The durable TURN preference is bit `0x0200` in the already-owned four-box state word at `0x800A60E8`. The reserved Runtime V2 word at `0xA01AF81C` is only transient editor storage while GAME SETTINGS is open; it is not the durable owner.

### Accepted future GAME SETTINGS rows

The accepted follow-on menu architecture is **not yet implemented gameplay behavior**. It is the current design contract for extending the production GAME SETTINGS page without changing its top-level OPTIONS slot:

| Setting | Values | Current status / rule |
|---|---|---|
| `TURN` | `TOGGLE` / `LOCK` | **Production / Runtime-confirmed.** Defaults to `TOGGLE`. |
| `COMBOS` | `CLASSIC` / `ASSIST` | **Pending.** Next menu item. `CLASSIC` is the intended default; exact ASSIST gameplay semantics still require their own design/proof. |
| `SPECIALS` | `CLASSIC` / `MODERN` | **Pending.** `CLASSIC` is the intended default; exact MODERN gameplay semantics still require their own design/proof. |
| `JUMP` | `DPAD` / `BUTTON` | **Pending and conditional.** Visible only when `COMBOS != CLASSIC` **or** `SPECIALS != CLASSIC`. |

`JUMP` is a **visibility dependency**, not a disabled row. When both COMBOS and SPECIALS are CLASSIC, JUMP is omitted entirely. As soon as either alternate control mode is selected, JUMP appears. Because left/right only edits the currently highlighted row, changing COMBOS or SPECIALS changes JUMP visibility while the cursor remains on COMBOS/SPECIALS; there is no separate cursor-recovery case.

The next bounded implementation step is intentionally **UI/state only**:

1. extend the current production GAME SETTINGS page with `COMBOS: CLASSIC / ASSIST`;
2. default to `CLASSIC`;
3. make row navigation, EXIT behavior, state mutation, and session/stage persistence work with two rows;
4. do **not** change combo gameplay yet;
5. only after that menu/state proof is Runtime-confirmed, define and implement ASSIST semantics in a separate guarded gameplay proof.

After COMBOS is stable, follow the same pattern for SPECIALS. JUMP should be added as a UI/state row only after COMBOS/SPECIALS exist, so its four visibility combinations can be validated before any jump-control gameplay change is attempted.

This future-control menu work remains outside the 1.0 release blocker chain unless explicitly promoted later. It must not silently redefine existing combo, special-move, or jump semantics.

### Full frontend proof v01/v02

**Full frontend proof v01 — Rejected / failed.** The first compact four-setting layout (`TURN`, `COMBOS`, `SPECIALS`, `JUMP`, then `EXIT`) hard-hung immediately on entering GAME SETTINGS. Static reconciliation identified an exact ABI error in the custom JUMP draw helper: the helper was entered by `jal`, then called the frontend renderer with nested `jal` instructions without preserving its incoming `ra`. The first nested call therefore destroyed the helper return address and guaranteed invalid control flow before the menu could finish drawing.

**Full frontend proof v02 — Runtime Pending.** Preserve/restore `ra` in a private helper stack frame around the nested frontend-renderer calls. No other full-menu behavior is promoted by this correction until manual validation. The COMBOS-only v01 UI/state proof remains independently Runtime-confirmed on its tested routes.

