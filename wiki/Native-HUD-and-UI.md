# Native HUD and UI

**Rich Inventory upstream evidence (2026-10-08): presentation preserved; music closure Pending.** Materialization still draws/acquires native glyphs each frame. Paired diagnostic states have byte-identical HUDs, same 17 active dynamic palette sources/handles and stable memory cursors. Both render-node cursors are valid in the first native bank; the earlier audit's second-bank assumption does not apply. Partial 180/377 node counts are capture phases, not a measured workload ratio. No glyph/palette operation is causally assigned to audio rejection. See [upstream report and matched occupied/empty-box control](Production-Rich-Inventory-Music-Static-Investigation).

**Native four-box Inventory legend (2026-10-06): Runtime-confirmed bounded.** Focused legend v01 was manually accepted by the maintainer as working perfectly. It replaces only the stock legend text-emission block while preserving the native six-tile panel. Row 1 is dynamic `BOX n OF 4`. Items mode renders `LEFT-RIGHT BOX`, `A USE`, `B COMBINE`, `R POWERS`; Power Ups intentionally leaves the middle rows blank and renders `L-R POWER` plus `R ITEMS`. The helper appends after the promoted in-Inventory switch module and does not alter box switching, masking, Combine behavior, Power-Ups navigation, or lifecycle semantics. The later Inventory/loading hang investigation is separate and unresolved.

**In-Inventory four-box navigation (2026-10-06): Runtime-confirmed bounded in full production composition.** Items-mode Left/Right cycles all four authoritative boxes with wraparound while the native Inventory remains open. The accepted transaction reuses filtered save + stage-masked load, cancels Combine, repairs physical/visible selection, supports empty boxes, and leaves Power Ups Left/Right stock-owned. Production-composition v03 also retained the existing gameplay shortcut, complete Inventory HUD, `BOX n OF 4`, lifecycle v06, global materializer, modern controls, and donor-backed features. Final cosmetic work on the legend and box-indicator styling is separate from this runtime-confirmed interaction.

**Water Inventory portrait-order correction (2026-10-05): Implementation pending.** The maintainer reported that `WATER1` and `WATER2` showed each other's portraits in the production Inventory HUD. Static audit isolated the Water entry in `PORTRAIT_DONORS`: the atlas emits each donor tuple in item-ID order, so the file-`0x73` tuple is corrected from `0x3AE, 0x3AD, 0x3AC` to `0x3AD, 0x3AE, 0x3AC` for item IDs `0x14..0x16` / `WATER1..3`. This is presentation-only: Water item IDs, labels, titles, award semantics, checks, and progression rules are unchanged. Runtime recheck remains Pending.

**Production wording correction (2026-10-05): Runtime-confirmed closed.** The first webapp-generated full-product validation after PRs #146/#147 exposed a presentation regression: #146 promoted the later proof strings `REQUIRED POWERS X/Y` and `XX/85`, reintroducing plain `/`, which renders as an unexpected native-font glyph. This did not depend on Powers-as-pickups mode. PR #148 restored the previously accepted native-font-safe forms **`REQ. POWERS X-Y`** and right-aligned **`CHKS XX-85`**; Vanilla Required Powers uses **`REQ. XP 5100`**. The maintainer then generated a ROM from the deployed webapp and reported that the corrected display looks good. The change is presentation-only and does not alter the independent Powers-as-pickups / Required-Powers semantics.

**Rich Inventory materialized-data stability closure (2026-10-07): Runtime-confirmed bounded.** A Fortress-only preload first removed the 100%-reliable post-Kia Inventory hang but later exposed the project's music-speed corruption symptom when the full rich row/paper/status paths continued rebuilding every frame. A no-rich-render control stayed healthy, proving the preload itself was not sufficient attribution. The accepted final proof keeps the exact previously working row, paper-title, portrait, font, palette, spacing and native text-renderer code, but prepares mutable `REQ. POWERS/CHKS` and `STG CHECKS KEYS` values once per Inventory session and reuses those prepared strings thereafter. Fortress still preloads the existing `0x1200` HUD allocation before its rewind anchor. The maintainer stress-tested Power/key/crystal changes, Kia, the post-Kia door, elevators, repeated open/close, consumable use, Combine, Items/Powers toggling and empty-box recovery without reproducing the hang or music-speed symptom. Proof SHA-256: `b73a9cba8c8a2ff0f6b96d9057dd30f36dc5b1e6e0b713d2f9d0eafb3b335c03`. The rejected prepared-glyph v01/v02 experiments are not part of this design; they replaced proven renderer behavior unnecessarily.\n\n**Inventory-HUD accepted closure (2026-10-05):** v21 is Runtime-confirmed on the bounded TEST LAB route with all nine Power pickups and the completed Inventory presentation: colored short credential labels, native/real paper titles, selected credential portraits, the eight-stage `STG CHECKS KEYS` table, ordinary-row native font/palette forwarding, with the production status wording restored to `REQ. POWERS X-Y` and right-aligned `CHKS XX-85` after the #146 webapp regression. It preserves the v20 first-load `0x1200` allocation correction. v23 then Runtime-confirms that Power feedback remains healthy under rapid adjacent pickup when progression awards synchronously and the white pulses run in a guarded child process. The production module derives portrait/font data from the clean ROM at build time, owns one fixed `0x500` file-`0x1A` tail plus generated-output atlas/package/data slots, and keeps the lazy HUD data request exactly `0x1200` bytes.

**Inventory-HUD proof-line correction (2026-10-05):** v16/v18/v19 share a concrete first-load allocation bug at `0x80074304`: the null branch skips `a0=0x1200` and calls `0x8006643C` with the incoming label pointer. v14 introduced this while compacting the reclaimed description span. v20 sets the size in delay slot `0x80074308`; **Runtime-confirmed bounded:** the user reports TEST LAB Inventory now opens instead of hanging. That proof also exposed an ordinary-item fifth font/palette forwarding defect; v21 corrects it and Runtime-confirms the completed presentation. See [exact calls, ownership, and proof](Test-Lab-Inventory-Hang-Static-Diagnosis).

> **Scope:** This page is the canonical owner for the gameplay HUD hook, native gameplay text, render-node usage, the production box indicator, generic renderer conclusions, and 1.0 randomizer-HUD implementation/reference material.
>
> Stable render-node structure grammar remains canonical in [Data structures and encodings](Data-Structures-and-Encodings). Title/legal branding belongs to [Presentation and branding](Presentation-and-Branding). The full Toasty visual diagnostic chronology belongs to [Toasty visual research](Toasty-Visual-Research).

## Current conclusion

The normal gameplay HUD path at `0x8005BFB0`, native text renderer `0x80073E74`, `BOX n OF 4`, **in-Inventory Left/Right four-box navigation**, and the mode-correct native four-box Inventory legend are **Runtime-confirmed bounded**. The complete Inventory-side 1.0 randomizer presentation is Runtime-confirmed in v21, and the storage-navigation interaction is additionally Runtime-confirmed in production-composition v03. Final representative full-seed/lifecycle validation remains Pending.

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

The shared browser/CLI builder now installs the accepted v02 five-setting composition. The six cursor positions are `TURN / ATTACK / SPECIALS / JUMP / RUN / EXIT`; the frontend remains title-resident, and gameplay helpers load at stage initialization.

| Setting | Values | Current behavior |
|---|---|---|
| `TURN` | `TOGGLE` / `LOCK` | Defaults to TOGGLE; native facing-lock gameplay when selected. |
| `ATTACK` | `CLASSIC` / `MODERN` | Modern event mapping, Block+Attack cancellation and stock combo parser. |
| `SPECIALS` | `CLASSIC` / `MODERN` | Modern mappings retain native move eligibility; Slide tier ≥2 and Super Slide tier ≥7 with resource ≥`0x60`. |
| `JUMP` | `DPAD` / `BUTTON` | BUTTON is editable only when ATTACK and SPECIALS are MODERN; includes ledge and locomotion behavior. |
| `RUN` | `HOLD` / `AUTO` | HOLD delegates to stock; AUTO uses the captured remapped physical button to choose Run/Walk. |
| `EXIT` | — | Returns to OPTIONS. |

Durable bits in the four-box state word at `0x800A60E8` are `0x0200` TURN=LOCK, `0x0400` ATTACK=MODERN, `0x0800` SPECIALS=MODERN, `0x1000` JUMP=BUTTON, and `0x2000` RUN=AUTO. All five survive box switching. Switching ATTACK or SPECIALS back to CLASSIC clears JUMP=BUTTON.

### Earlier four-setting frontend (v04)

The earlier production menu offered TURN/COMBOS/SPECIALS/JUMP/EXIT; it is superseded as a current product menu, while its runtime findings remain evidence for the v02 successor.

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

After v04, the project added RUN:HOLD/AUTO and promoted the old COMBOS state bit to ATTACK:MODERN. The v06 proof established earlier SPECIALS/JUMP gameplay and the later v09/v10 line established the full frontend and remaining gameplay before accepted v02 integration.

The disposable full-composition ATTACK check v01 displays `ATTACK: CLASSIC / MODERN` by changing only the row label and second value pointer while reusing bit `0x0400`. The user reported the check ROM working as expected on 2026-09-26. The later accepted proof-only gameplay baseline is `MKMSZR_controls-modern_ledge-extension-proof_v06.z64`, SHA-256 `7ea9cf1d606e303fe04a67bc40e76940a90a3ff6232a8f301a8a35eab809c411`; exact control semantics and bounded runtime scope are canonical in [Player actions and special moves](Player-Actions-and-Special-Moves).

### Five-setting controls frontend — v09 accepted proof

The five-setting successor is now **Runtime-confirmed in disposable proof v09**. It uses a clean one-line layout with `TURN`, `ATTACK`, `SPECIALS`, `JUMP`, `RUN`, then separated `EXIT`. The user reported that the menu works correctly and that the new layout “looks fantastic.”

The accepted proof keeps the stock GAME SETTINGS type-2 cursor table at exactly four entries: logical rows `0..3` use type 2, while RUN row `4` and EXIT row `5` map to existing type-0 coordinates. It preserves the proof-specific ATTACK gameplay tails at ROM `0x775D0..0x775DB` and `0x77688..0x77693`, keeps frontend code title-resident, and does not load gameplay file `0x1A` from the frontend lifecycle.

Durable proof settings are:
- `0x0200` TURN=LOCK;
- `0x0400` ATTACK=MODERN;
- `0x0800` SPECIALS=MODERN;
- `0x1000` JUMP=BUTTON;
- `0x2000` RUN=AUTO.

**v07 remains Rejected / failed:** its compressed presentation was visually rejected, its frontend rewrite overwrote ATTACK gameplay tails and caused the Block hang, and its global Run inversion broke analog auto-run and live Run->Walk behavior.

**v08 remains Rejected / failed:** preserving the ATTACK tails removed the Block hang, but GAME SETTINGS entry hard-hung. Static audit isolates the draw-helper cause: it relied on caller-saved `t0` across `0x8001CA88`, which clobbers it; a later `t5` carry was unsafe for the same reason.

**v09 Runtime-confirmed correction:** renderer-dependent code rebuilds volatile bases after renderer calls, preserves `ra`, stays within audited frontend ownership, and publishes only valid cursor type/index pairs. RUN toggling/persistence works; locomotion changes were intentionally absent in v09.

**v10 Runtime-confirmed gameplay successor:** v10 leaves the v09 frontend unchanged except two audited zero-padding trampolines and adds the accepted Block-startup and RUN gameplay fixes. Exact gameplay semantics and proof identity are canonical in [Player actions and special moves](Player-Actions-and-Special-Moves).

The shared browser/CLI product now uses this five-setting frontend and its complete controls gameplay. The accepted v02 composition puts controls below `0x801B0880` and CI4 Toasty at `0x801B1000`, under the same 16 KiB reservation. The user-accepted v02 ROM (SHA-256 `b12ed90201ab754aac542b7b89458735b5a756f480fffca89c129c0ed3173147`) remains the Runtime-confirmed baseline. Current builds intentionally differ only in the approved Toasty four-word TLUT purple polish; controls semantics and allocation are unchanged.
