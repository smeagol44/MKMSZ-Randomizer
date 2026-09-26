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

## Production GAME SETTINGS frontend

The stock top-level `GAME SETTINGS` entry is now the complete MKMSZR control frontend. **Full-menu v04 is Runtime-confirmed** and is the accepted frontend baseline:

| Setting | Values | Frontend status |
|---|---|---|
| `TURN` | `TOGGLE` / `LOCK` | Runtime-confirmed gameplay + frontend. Defaults to TOGGLE. |
| `COMBOS` | `CLASSIC` / `ASSIST` | Runtime-confirmed production UI/state. Accepted proof semantics now replace this label with `ATTACK: CLASSIC / MODERN`; product integration remains Pending. |
| `SPECIALS` | `CLASSIC` / `MODERN` | Runtime-confirmed production UI/state. MODERN gameplay is now Runtime-confirmed in the accepted proof-only v06 control composition; product integration remains Pending. |
| `JUMP` | `DPAD` / `BUTTON` | Runtime-confirmed production UI/state. Visible at all times; greyed/fixed to DPAD unless **COMBOS=ASSIST AND SPECIALS=MODERN**. BUTTON gameplay is Runtime-confirmed in proof-only v05/v06; product integration remains Pending. |
| `EXIT` | — | Runtime-confirmed navigation/return. |

The compact layout reuses the stock font and frontend loop while reclaiming the old GAME SETTINGS edit/draw regions. Four setting rows fit above the stock EXIT position without introducing a new frontend allocation or title-time expansion load.

**Runtime-confirmed v04 frontend behavior:** cursor alignment is correct on all five logical rows; JUMP is selectable and its value becomes editable only under ASSIST+MODERN; the disabled DPAD state is visibly greyed; values survive the tested leave/re-enter, stage, and inventory activity routes; the accelerated/crunchy music observed in v02 does not reproduce.

The durable state word at `0x800A60E8` owns:
- `0x0200` TURN=LOCK;
- `0x0400` COMBOS=ASSIST;
- `0x0800` SPECIALS=MODERN;
- `0x1000` JUMP=BUTTON.

Box switching preserves all four settings bits. If COMBOS or SPECIALS is returned to its classic mode, the JUMP button bit is cleared back to DPAD.

Frontend proof history:
- **v01 — Rejected / failed:** custom JUMP draw helper failed to preserve `ra` across nested renderer calls; menu entry hard-hung.
- **v02 — Rejected / unsafe:** menu rendered but published logical index 4 into the stock four-entry GAME SETTINGS cursor contract, causing cursor corruption and accelerated/crunchy menu audio.
- **v03 — Superseded:** safe cursor-index mapping removed the music corruption, but a trailing displaced stock store still overwrote cursor type and produced wrong cursor positions.
- **v04 — Runtime-confirmed:** owns all three words at the JUMP draw/cursor hook, preserving the corrected cursor contract and final compact coordinates.

The first older production integration failure remains relevant: loading shared file `0x1A` from the title/frontend lifecycle hard-hung. The accepted frontend remains title-resident; file `0x1A` is loaded only at stage initialization.

A new requirement appeared after full-menu v04: **RUN: HOLD / AUTO**. Therefore the production v04 frontend remains the accepted baseline, but the frontend structure is no longer considered closed. Production still exposes the historical `COMBOS: CLASSIC / ASSIST` label and durable `0x0400` state bit; accepted proof semantics replace it with `ATTACK: CLASSIC / MODERN`. SPECIALS: MODERN and JUMP: BUTTON gameplay are now Runtime-confirmed in the accepted proof-only control-suite v06, but none of ATTACK/SPECIALS/JUMP gameplay is yet integrated into the normal browser/CLI patch core.

The disposable full-composition ATTACK check v01 displays `ATTACK: CLASSIC / MODERN` by changing only the row label and second value pointer while reusing bit `0x0400`. The user reported the check ROM working as expected on 2026-09-26. The later accepted proof-only gameplay baseline is `MKMSZR_controls-modern_ledge-extension-proof_v06.z64`, SHA-256 `7ea9cf1d606e303fe04a67bc40e76940a90a3ff6232a8f301a8a35eab809c411`; exact control semantics and bounded runtime scope are canonical in [Player actions and special moves](Player-Actions-and-Special-Moves).

### Five-setting RUN frontend experiments

The intended additional row is `RUN: HOLD / AUTO`, with candidate durable bit `0x2000`. The desired semantics are locomotion-local: HOLD is vanilla; AUTO defaults horizontal locomotion to Run while holding the configured Run button temporarily requests Walk. The physical/remapped Run semantic must remain intact for Run-based attacks/specials, and full analog deflection must preserve vanilla analog auto-run.

The first two five-setting frontend proofs are **Rejected / failed**:

- **RUN v07:** the menu rendered but the stacked label/value layout was visibly over-compressed. More importantly, Block hard-hung. Static post-test reconciliation found that the frontend rewrite had overwritten the two small proof-specific gameplay trampolines embedded at the ends of the reclaimed GAME SETTINGS edit regions, including the accepted Block trampoline. AUTO also failed to transition an already-running player to Walk on a new Run-button press, and full analog deflection stopped auto-running because the proof inverted the merged semantic Run signal.
- **RUN v08:** rebuilt from accepted control-suite v06 and preserved the Block/combo trampolines; Block no longer hung. The attempted AUTO logic separated physical Run-button state from vanilla analog-run synthesis and added a live Run->Walk transition. However, **entering GAME SETTINGS itself hard-hung**, so the proof is rejected and the RUN gameplay changes remain runtime-unvalidated.

The current UI task is therefore not another visual spacing tweak. It is a focused ownership/entry audit of a real five-setting frontend, comparing production full-menu v04 with v07/v08. The safe requirements are: preserve the accepted four-row cursor contract unless explicitly extended with proven ownership, preserve both ATTACK proof trampolines, keep frontend code title-resident, and do not load gameplay expansion file `0x1A` from the frontend lifecycle.
