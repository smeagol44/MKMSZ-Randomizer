# Toasty visual research

> **Scope:** This page is the canonical owner for the Toasty visual target, donor presentation findings relevant to the image path, the complete v01-v16 visual proof chronology, rejected/superseded Toasty diagnostics, and the evidence provenance for generic renderer conclusions discovered during that investigation.
>
> Reusable gameplay-HUD/text/render behavior is canonical in [Native HUD and UI](Native-HUD-and-UI). Stable render-node grammar belongs to [Data structures and encodings](Data-Structures-and-Encodings). Toasty audio remains in [Toasty audio research](Toasty-Audio-Research) and is not modified by this page.

## Current unresolved boundary

**Current boundary:** v15 is **Runtime-confirmed** for genuine Toasty CI8 pixels through the gameplay-HUD textured-node path. v16 is **Runtime-confirmed as a palette-binding failure that nevertheless proves the clone-local palette-selector route is live**: changing only the clone to selector `0x11` changed the rendered colors substantially, but the image became pale/pink/green and visually corrupted rather than correctly colored.

Static reconciliation found the cause: the preserved v01 palette bytes are MKMSZ **source BGR555/A1B5G5R5 words**, while the gameplay renderer's runtime palette-pointer table points directly to already hardware-ready **RGBA5551 TLUT words**. v16 registered the source words directly and therefore bypassed the normal MKMSZ source-to-hardware palette conversion.

v17 is **Implementation/static-confirmed; runtime pending manual validation.** It keeps v16's selector/pointer/code/image/geometry paths byte-for-byte unchanged and changes only the 512 custom TLUT bytes by applying the exact BGR555-source -> RGBA5551-hardware channel/alpha conversion.

## Final evidence status by proof

| Proof | Final evidence status | Durable result / limit |
|---|---|---|
| v01 | **Runtime-confirmed failure on 2026-09-22.** | No visible image. With no independent marker, the failure could not distinguish hook execution, allocation, load/binding, palette, or renderer-context suitability. |
| v02 | **Runtime-confirmed on 2026-09-22.** | `V02 WRAPPER OK` proves the gameplay HUD hook/wrapper executes; visual failure is downstream. |
| v03 | **Runtime-confirmed failure on 2026-09-22; allocator conclusion remains unresolved.** | The diagnostic is rejected/intrusive because `V03 SLOT FAIL` coincided with loss of all normal music/SFX; it is not clean evidence against `0x8001C2B4`. |
| v04 | **Runtime-confirmed on 2026-09-22.** | Logo/selector/save-bypass test harness is valid and normal audio returns; image remains absent as expected for the baseline. |
| v05 | **Runtime-confirmed on 2026-09-22.** | Dynamic allocator returns an expected `0x200..0x2FF` ID on the tested HUD route; allocation is exonerated. |
| v06 | **Runtime-confirmed failure on 2026-09-22; no load conclusion accepted.** | Loader-wrapper plus selector-cave-tail instrumentation hangs after Mission Objective/music; reject this diagnostic. |
| v07 | **Runtime-confirmed failure on 2026-09-22; no load conclusion accepted.** | Post-load helper reproduces the same hang with the stock loader call intact; reject helper-based load instrumentation on this route. |
| v08 | **Runtime-confirmed on 2026-09-22.** | Gameplay-HUD queue renders an additional cloned textured node. |
| v09 | **Runtime-confirmed on 2026-09-22.** | Node halfword `+0x4A` is a live texture-slot binding. |
| v10 | **Runtime-confirmed on 2026-09-22.** | Clone-local `+0x4A` rebinding works without altering the stock source HUD node. |
| v11 | **Runtime-confirmed failure on 2026-09-22.** | Reject the second-`0x8001BF70` independent fixed-slot allocation recipe; renderer submission itself remains valid. |
| v12 | **Runtime-confirmed failure on 2026-09-22; implementation bug identified statically afterward.** | The alias implementation used the wrong backing-pointer table base; the result is not evidence that slot `0x17` is unusable. |
| v13 | **Runtime-confirmed failure on 2026-09-22; implementation bug identified statically afterward.** | A second signed-address bug used the wrong slot-record page; again not evidence against slot `0x17`. |
| v14 | **Runtime-confirmed on 2026-09-22.** | Corrected fixed-slot alias reproduces the v10 control and confirms record/backing bases. |
| v15 | **Runtime-confirmed on 2026-09-22.** | Genuine Toasty CI8 pixels render through a dynamic gameplay-HUD texture slot; wrong stock-HUD colors isolate palette selection as the remaining visible defect. |
| v16 | **Runtime-confirmed failure on 2026-09-23; useful selector evidence.** | The clone's colors changed strongly, proving the custom `+0x4C` selector/pointer route is live, but the palette was registered in MKMSZ source BGR555 form instead of hardware RGBA5551 form, producing the wrong colors/transparency. |
| v17 | **Implementation/static-confirmed; runtime pending manual validation.** | Identical v16 image/selector/pointer/render code; only the 512 custom TLUT bytes are converted from source BGR555/A1B5G5R5 to hardware RGBA5551. |

## Generic renderer conclusions produced by this investigation

These reusable conclusions are canonical in [Native HUD and UI](Native-HUD-and-UI); this page owns the Toasty proof provenance that established them.

| Generic conclusion | Toasty evidence |
|---|---|
| `0x80073CEC -> 0x8001E578` is real but context-specific and is not accepted as a universal gameplay sprite API | Preserved renderer correction after v07; v01-v05 renderer assumption superseded |
| The normal gameplay-HUD queue accepts an additional MKMSZR-owned textured node | v08 **Runtime-confirmed** |
| Node halfword `+0x4A` selects the texture slot, including clone-local rebinding | v09-v10 **Runtime-confirmed** |
| Fixed-slot record base is `0x802E83F0`; backing-pointer base is `0x800ED940` | v14 **Runtime-confirmed** control, supported by static audit |
| Dynamic CI8 allocation can feed genuine imported pixels into an added gameplay-HUD node | v15 **Runtime-confirmed** |
| Node halfword `+0x4C` is the gameplay renderer palette selector | v16 **Runtime-confirmed** that clone-local selector `0x11` changes palette resolution; v16's palette bytes themselves were in the wrong source representation |

## Rejected or superseded Toasty visual approaches

- **v01-v05 direct use of `0x80073CEC` as the final gameplay renderer:** superseded by preserved evidence showing that renderer family is context-specific. v02 wrapper execution and v05 allocator success remain valid independent findings.
- **v03 allocator-state diagnostic:** rejected because its expanded helper footprint also killed normal music/SFX; `SLOT FAIL` cannot be attributed cleanly to the allocator.
- **v06 loader wrapper / selector-cave-tail use:** rejected because it introduced a Mission Objective + music hang before gameplay.
- **v07 post-load helper instrumentation:** rejected because it reproduced the same hang while leaving the stock loader call intact; no raw-load conclusion is accepted.
- **v11 independent fixed-slot allocation recipe:** rejected because the new slot produced noisy/multicolored output despite the known-good node submission path.
- **v12 and v13 alias implementations:** rejected as implementation bugs caused by two separate address-base/sign-extension mistakes. Their failures do not establish that slot `0x17` is unusable.
- **Do not infer production safety from any proof cave/allocation.** The final feature still needs production-safe composition with existing MKMSZR runtime/HUD ownership.

## Complete visual chronology

## Toasty presentation target

The intended Toasty feature is now split into independently testable presentation and audio pieces.

**Static-confirmed donor behavior:** MKT's `forden_peek` creates the genuine 97x100 `TOASTY` image with its 64-color `TOASTY_P` palette, slides it in from the right for 6 ticks, stops it for `0x20` ticks while playing the Toasty voice, reverses horizontal velocity, slides it out for `0x10` ticks, then deletes it. The donor `randper(40)` gate is 40/1000 = 4%, approximately one qualifying event in 25.

**Runtime-confirmed audio:** Toasty audio proof v03 reproduces the intended retail voice and the user reported it as perfect. Audio is considered solved for this workstream and must remain untouched while the visual path is isolated. See [Toasty audio research](Toasty-Audio-Research).

**Historical pre-v08 boundary — superseded by v15/v16:** the remaining textured screen-space/object binding for the Toasty image was still unresolved at this point. The later v08-v15 diagnostics establish the gameplay textured-node/image path; v16 narrows the current boundary to runtime validation of the genuine palette. The already runtime-confirmed audio v03 remains outside these visual diagnostics.


### Toasty visual-only proof v01 — build intent before manual test

**Implementation/static-confirmed; runtime pending manual validation.**

Disposable proof files:

- `MKMSZR_toasty-visual_common-proof_v01.z64`
- builder `MKMSZR_build_toasty_visual_v01.py`
- ROM SHA-256 `e248994470d1b05d275337fa0139ecdaa6af8c89be4968b8d7af0211dc8486f6`
- CRC1/CRC2 `92C82DEF / 82B2C418`

This proof isolates only the unresolved textured gameplay-presentation question. It contains **no Toasty audio, no uppercut/contact hook, and no RNG**.

The genuine decoded retail MKT Toasty art is remapped losslessly into a target-native CI8/BGR555 asset. The visible image is 78x85 pixels; the runtime texture allocation aligns the row stride to 96 pixels, for an 0x1FE0-byte indexed image. Transparent pixels and row padding use palette index zero.

The proof uses MKMSZ's native dynamic texture infrastructure rather than direct framebuffer drawing:

```text
HUD hook
  -> preserve displaced 0x8001EAE4 submission
  -> 0x8001C2B4(78,85) dynamic texture allocation
  -> file ID 0x1B raw-load into the texture backing store
  -> 0x80073CEC(custom palette, dynamic slot, x, y, flags=0)
```

The wrapper validates that its saved dynamic texture slot is still active and reallocates/reloads the image if the texture table has been reset.

Proof-only allocations:

- HUD hook ROM `0x5D9CC`;
- wrapper/code ROM `0x9AD84..0x9AEF3`;
- proof state ROM `0x9AF10..0x9AF1F`;
- custom 256-entry palette descriptor ROM `0xA1308..0xA150B`;
- clean/free file ID `0x1B` points to raw image ROM `0xF30000..0xF31FDF`.

These locations are **not production allocations**. In particular, the final feature must compose with the existing MKMSZR runtime/HUD ownership rather than copying this standalone cave layout.

The deterministic visual cycle intentionally avoids combat-trigger variables:

- slide in for 6 HUD frames from the right edge toward x=242;
- hold at x=242 for 32 frames;
- slide out to the right for 16 frames;
- repeat every 150 HUD frames;
- y=145.

The proof's only intended runtime question is whether the genuine Toasty CI8 image renders with correct palette/transparency and stable slide/lifetime behavior during normal gameplay. If successful, the next bounded composition can combine the already runtime-confirmed Toasty audio with this visual path before introducing the final uppercut-contact / cosmetic-RNG trigger.


### Toasty visual proof v01 — no visible output

Disposable proof:
- builder: `MKMSZR_build_toasty_visual_v01.py`
- ROM: `MKMSZR_toasty-visual_common-proof_v01.z64`

**Runtime-confirmed failure on 2026-09-22.** This proof was intended to display Toasty automatically during ordinary gameplay; no input, uppercut, RNG event, or sound trigger was required. The user observed that **nothing appeared on screen**.

The proof architecture was deliberately visual-only:
- HUD call at ROM `0x0005D9CC` redirected to wrapper VA `0x8009A184`;
- wrapper preserved the displaced HUD submit call;
- deterministic cycle: 6-frame slide in, 32-frame hold, 16-frame slide out, blank until frame 150, then repeat;
- dynamic CI8 texture slot requested through `0x8001C2B4`;
- raw image resource registered through clean-ROM file ID `0x1B`, ROM `0xF30000`;
- raw-file loader `0x80065D64` used for the image;
- textured renderer `0x80073CEC` used for draw submission;
- dedicated 256-entry palette descriptor at VA `0x800A0708`;
- image payload is the genuine retail MKT Toasty image converted to target-native CI8, visible 78x85 with stride 96;
- no Toasty sound import, combat hook, or RNG was present.

**Evidence limit:** because v01 had no independent diagnostic marker, the negative result does not distinguish among:
1. wrapper/hook not executing as intended;
2. dynamic texture-slot allocation failing;
3. raw image load/binding failing;
4. palette/descriptor incompatibility;
5. `0x80073CEC` being unsuitable from this gameplay HUD context.

Do not repeat v01 unchanged. The next bounded proof should first establish wrapper execution with an already-proven visible diagnostic (native text or simple render-node quad), then isolate texture-slot allocation/load from textured submission one variable at a time. The successful Toasty audio v03 result is unaffected by this visual failure.


### Toasty visual diagnostic v02 — wrapper confirmed

Disposable proof:
- builder: `MKMSZR_build_toasty_visual_v02.py`
- ROM: `MKMSZR_toasty-visual-marker_common-proof_v02.z64`

**Runtime-confirmed on 2026-09-22.** The user observed the native `V02 WRAPPER OK` marker continuously during normal gameplay, while the Toasty image still never appeared.

v02 changed only the wrapper's displaced HUD-submit call target so it passed through a tiny helper that:
1. executes the original `0x8001EAE4` submit;
2. preserves its return value;
3. draws the diagnostic through runtime-confirmed native text `0x80073E74`;
4. returns into the otherwise unchanged v01 texture path.

This closes the first v01 ambiguity: the HUD hook/wrapper **does execute** in gameplay. The unresolved visual failure is downstream of wrapper execution, beginning with dynamic texture allocation/state, raw-load/binding, palette compatibility, or `0x80073CEC` context suitability.

The Toasty audio v03 proof remains independently runtime-confirmed and is not modified by these visual diagnostics.


### Toasty visual diagnostic v03 — intrusive / rejected diagnostic

**Runtime-confirmed failure on 2026-09-22; allocator conclusion remains unresolved.**

The user observed persistent `V03 SLOT FAIL` during ordinary gameplay and the Toasty image remained absent. However, unlike v02, **all normal game music and sound effects were also absent** in this proof.

v03 had expanded the diagnostic helper beyond the v02 marker footprint so it could inspect the saved slot and dynamic-texture table before returning into the otherwise unchanged v01/v02 texture path. Because that diagnostic change introduced an unrelated global audio regression, its `SLOT FAIL` result is not accepted as clean evidence that `0x8001C2B4` itself fails. The diagnostic may be perturbing runtime state or occupying unsafe zero-initialized executable/data space.

Durable conclusions:
- v02 remains the clean runtime proof that the HUD hook/wrapper executes;
- v03 is a **Rejected / intrusive diagnostic** for allocator-state attribution;
- do not change the loader, palette, or `0x80073CEC` based on v03 alone;
- the next allocator diagnostic should return to the v02-known-good helper/allocation footprint and expose allocator success with a smaller, less intrusive method.

For faster manual iteration, future disposable Toasty proofs may include the already runtime-confirmed post-legal logo bypass and compact eight-stage A-button Safe Stage Select as a fixed test harness. Their guarded patches must remain separate from the visual diagnostic variable and must not claim the production bootstrap cave used by other systems.


### Toasty visual diagnostic v04 — test harness confirmed

**Runtime-confirmed on 2026-09-22.**

v04 returned to the v02-known-good marker/visual composition and added only the established disposable-test conveniences:
- post-legal two-logo bypass;
- compact eight-stage A-button Safe Stage Select;
- selector-entry one-shot auto-save bypass.

The user confirmed all three expected controls: the logos skip, A opens the safe selector, and normal music/SFX are present again. The Toasty image remains absent, as expected for this baseline.

This establishes the v04 convenience composition as the fixed manual-test harness for subsequent Toasty visual diagnostics. It also confirms that v03's global audio loss was introduced by the v03 diagnostic itself, not by the logo/selector harness.


### Toasty visual diagnostic v05 — allocator return confirmed

**Runtime-confirmed on 2026-09-22.**

The user observed persistent `V05 ALLOC 1` during ordinary gameplay; the marker did not fall back to zero, and the Toasty image remained absent.

This runtime-confirms that the dynamic allocator path is succeeding on the tested HUD route and returning an ID in the expected `0x200..0x2FF` range. Dynamic allocation itself is therefore exonerated for this failure. The remaining chain begins with the raw file load/backing-store contents, followed by palette/binding and `0x80073CEC` submission/context suitability.


### Toasty visual diagnostic v06 — rejected loader-wrapper diagnostic

**Runtime-confirmed failure on 2026-09-22; no load conclusion accepted.**

The user observed that Temple reached the Mission Objective screen and stage music started, but gameplay never appeared. Therefore v06 is rejected as an intrusive diagnostic and its load marker cannot be used as evidence.

v06 differed from the runtime-confirmed v05 baseline by interposing a 0x34-byte helper around `0x80065D64` and occupying the previously-unused tail `0x9A720..0x9A753` of the standalone selector cave. Even though that tail is zero in the clean ROM, the resulting runtime composition is not safe on this stage-entry route.

Durable conclusion: do not wrap the raw loader and do not expand into that selector-cave tail for this diagnostic.


### Toasty visual diagnostic v07 — rejected post-load helper

**Runtime-confirmed failure on 2026-09-22; no load conclusion accepted.**

v07 left the stock `0x80065D64` raw-loader call and delay slot unchanged, but added one post-return helper call inside the Toasty wrapper to inspect backing bytes. The user observed the **same failure boundary as v06**: Mission Objective appears, stage music starts, but gameplay never becomes visible.

This exonerates the v06 loader interposition itself as the unique cause. The common new factor is extra helper-call instrumentation around the Toasty HUD wrapper. v07 is therefore rejected as an intrusive load diagnostic; no conclusion about the raw image bytes is accepted.

Do not continue instrumenting the loader from this branch. The raw global-file loader already has independent runtime confirmation elsewhere, and older preserved UI evidence already established a more important renderer boundary.


### Renderer correction from preserved UI evidence

**Runtime-confirmed historical evidence, re-integrated 2026-09-22.**

The earlier UI campaign had already established that `0x80073CEC -> 0x8001E578` is a real but context-specific 2D renderer family. Duplicating that family affected startup/title/inventory/PAUSED graphics, but did **not** duplicate the normal gameplay HUD, safe selector, stage-objective screen, or several other UI systems. A direct gameplay invocation of `0x80073CEC` also produced no visible sprite.

Therefore the v01-v05 assumption that `0x80073CEC` could serve as the final Toasty gameplay renderer is **Rejected / superseded**. The useful v02/v05 results still stand for wrapper execution and dynamic allocation, but further Toasty rendering work should use the actual gameplay-HUD queue.

Static re-audit of `0x8005BFB0` shows a native textured HUD path already present there:
- six HUD resources are decoded through `0x8000322C`;
- six corresponding texture slots are initialized through `0x8001BF70`, using slots `0x11..0x16`;
- textured 0x58-byte HUD nodes store the texture slot in halfword `+0x4A` and submit through the already runtime-confirmed `0x8001EAE4` queue.

At the first such submit, VA `0x8005C6E0` / ROM `0x5D2E0`, the stock node carries texture slot `0x12`.


### Toasty visual diagnostic v08 — stock textured HUD clone confirmed

**Runtime-confirmed on 2026-09-22.**

The user observed an additional small gold HUD-like textured fragment at the expected shifted gameplay position while the original top-left HUD remained intact. Gameplay loaded normally.

v08 contained no custom image, dynamic texture allocation, raw file load, palette replacement, diagnostic text, Toasty audio, RNG, or trigger. It only cloned one already-built stock textured 0x58-byte HUD node inline, shifted its XY coordinates by `+160,+80`, and submitted the clone through the same `0x8001EAE4` queue.

This runtime-confirms that the actual gameplay-HUD queue can render an additional textured MKMSZR-owned node. The exact texture-binding halfword is still being isolated; v08 copied the full stock node and therefore does not by itself prove that `+0x4A` alone selects the texture.


### Toasty visual diagnostic v09 — stock texture-slot binding confirmed

**Runtime-confirmed on 2026-09-22.**

v09 changed only the stock source-node selector from resident texture slot `0x12` to resident slot `0x13`, leaving the v08 clone wrapper byte-for-byte unchanged.

Observed result:
- the shifted clone changed visibly from the v08 C-like gold fragment to an equals-sign-like gold fragment;
- the original top-left HUD simultaneously lost a small two-pixel portion of its gold frame.

Because both source and clone inherited the same one-instruction slot change, the coupled visual change runtime-confirms that the node texture binding is live at halfword `+0x4A`. The small stock-HUD damage is an expected side effect of altering the source node before cloning; it is not treated as a new renderer failure.


### Toasty visual diagnostic v10 — clone-local texture binding confirmed

**Runtime-confirmed on 2026-09-22.**

The user observed the shifted equals-sign-like textured clone while the normal top-left HUD returned to its intact appearance. This cleanly separates clone-local texture selection from stock HUD state.

v10 leaves the stock source node on slot `0x12`, clones the full 0x58-byte textured HUD node inline, changes only the clone's halfword `+0x4A` to resident slot `0x13`, shifts it by `+160,+80`, and submits through `0x8001EAE4`.

This runtime-confirms that MKMSZR can rebind the texture of an added gameplay-HUD node independently without altering the source HUD node.


### Toasty visual diagnostic v11 — rejected independent fixed-slot allocation

**Runtime-confirmed failure on 2026-09-22.**

The normal stock HUD remained intact, but the shifted clone no longer matched the v10 equals-sign control. Instead it became a small multicolored/noisy fragment.

v11 had created fixed slot `0x17` by calling `0x8001BF70` a second time immediately after stock slot `0x13`, reusing the same decoded source and dimensions but allocating a new backing region. Because v10 already proved clone-local rebinding and the stock HUD stayed healthy, this result does **not** invalidate the gameplay textured-node renderer. It rejects only the assumption that this extra fixed-slot allocation is an equivalent independent copy of slot `0x13`.

Static re-audit confirms the renderer consumes the slot's format word, line-width field, and backing-pointer table entry. The failure can therefore be caused by fixed-slot reuse/overwrite or by the extra backing allocation/lifetime rather than by node submission itself.

Do not use v11's `0x17` allocation recipe for Toasty.


### Toasty visual diagnostic v12 — rejected alias implementation

**Runtime-confirmed failure on 2026-09-22; implementation bug identified statically afterward.**

The normal HUD remained intact, but the shifted clone changed again into a different bright/white fragmented pattern rather than the v10 equals-sign control.

A subsequent instruction-level audit found the v12 helper copied the slot backing pointer from the **wrong table base**. The gameplay renderer at `0x8001F7A8`, fixed-slot initializer `0x8001BF70`, and dynamic allocator `0x8001C2B4` all index the backing-pointer table as:

```text
lui ...,0x800F
... index * 4 ...
lw/sw ...,-0x26C0(...)
```

which resolves to **`0x800ED940`**, not `0x800FD940`. v12 used a `0x8010` high half and therefore aliased an unrelated address range. Its runtime image is not evidence that slot `0x17` itself is unusable.

The renderer directly consumes the node texture ID at `+0x4A`, record `0x802E83F0 + id*0x10` fields `+0x00` and `+0x08`, and backing pointer `0x800ED940[id]`. This static mapping also shows that the same renderer addressing arithmetic can represent dynamic IDs `0x200..0x2FF`; runtime use through the gameplay queue is still pending.


### Toasty visual diagnostic v13 — rejected alias implementation, second signed-address bug

**Runtime-confirmed failure on 2026-09-22; implementation bug identified statically afterward.**

The normal HUD remained intact, but the shifted clone became another distinct gold/white fragmented pattern rather than the v10 equals-sign control.

The v13 backing-pointer correction was real, but a second sign-extension error remained in the alias helper. The fixed/dynamic slot record base is formed by stock code as:

```text
lui   ...,0x802F
addiu ...,...,0x83F0   # signed immediate = -0x7C10
```

which resolves to **`0x802E83F0`**, not `0x802F83F0`. v13 still used the latter page for the copied slot metadata. Therefore it combined the correct slot-`0x13` backing pointer with unrelated format/stride metadata, explaining the changed but still incorrect fragment.

This result is not evidence against slot `0x17` itself.


### Toasty visual diagnostic v14 — fully corrected fixed-slot alias

**Runtime-confirmed on 2026-09-22.**

v14 is intentionally identical to v13 except for the single slot-table high-half instruction:
- v13 alias metadata page: `0x8030` plus signed negative offsets -> wrong `0x802Fxxxx` page;
- v14 alias metadata page: `0x802F` plus the same signed offsets -> correct `0x802Exxxx` page.

The exact copied records are now:
- slot `0x13`: `0x802E8520`;
- slot `0x17`: `0x802E8560`;
- backing pointers remain `0x800ED98C` -> `0x800ED99C`.

Relative to v13, v14 changes only one non-header ROM byte. No allocation, pixel copy, new cave, renderer change, audio change, or Toasty asset is introduced.

Observed result: intact normal HUD plus the same shifted equals-sign texture seen in runtime-confirmed v10. This confirms the corrected slot-record base `0x802E83F0` and backing-pointer base `0x800ED940`, and closes the fixed-slot alias control.


### Toasty visual diagnostic v15 — actual Toasty pixels confirmed

**Runtime-confirmed on 2026-09-22.**

The user observed a large, clearly non-HUD textured image at the intended shifted gameplay position. Its silhouette/pose matches the genuine Toasty CI8 source, while its colors are strongly blue/cyan/black because v15 intentionally inherited the stock HUD palette. The stock gameplay route remained functional.

This confirms the important composition boundary:
- dynamic CI8 allocation through `0x8001C2B4(78,85)` works with the gameplay HUD renderer;
- the 96-byte aligned backing stride is accepted;
- raw Toasty pixels loaded through file ID `0x1B` reach the allocated backing store;
- node `+0x4A` can point the added gameplay-HUD node at that dynamic texture.

The remaining visible defect is palette selection, not the image source/stride/renderer socket.


### Toasty visual diagnostic v16 — selector live, TLUT representation wrong

**Runtime-confirmed failure on 2026-09-23; palette-selector route itself is confirmed.**

The user observed the same large Toasty pixel field in the same gameplay position, but its appearance changed from v15's blue/cyan stock-HUD coloring to a pale pink/green/black corrupted-looking image. Stock HUD/gameplay remained intact.

This is positive evidence that clone node `+0x4C = 0x11` successfully selects the custom palette path. The defect is the bytes supplied to that path.

The preserved v01 palette is a source-format descriptor: count `0x100` followed by 256 MKMSZ source words in BGR555/A1B5G5R5 form. That format is appropriate before MKMSZ's native source-to-hardware upload conversion, but v16 pointed the gameplay renderer's runtime TLUT pointer directly at those source words. The runtime pointer table instead references already hardware-ready RGBA5551 TLUT data.

This explains both symptoms: channel order is wrong and the source high alpha/control bit lands in the wrong hardware bit position, so color and transparency are both corrupted.

### Toasty visual diagnostic v17 — hardware-ready TLUT

**Implementation/static-confirmed; runtime pending manual validation.**

v17 is intentionally identical to v16 except for the 512-byte custom TLUT payload. Each source word is converted as:

```text
source BGR555/A1B5G5R5:
  A = bit15
  B = bits14..10
  G = bits9..5
  R = bits4..0

hardware RGBA5551:
  bits15..11 = R
  bits10..6  = G
  bits5..1   = B
  bit0       = A
```

The indexed Toasty image, dynamic slot, 96-byte stride, selector `0x11`, pointer registration, clone geometry, gameplay-HUD submission, logo skip, Safe Stage Select, and audio exclusion are unchanged from v16.

ROM-level comparison against a rebuilt v16 confirms every non-header difference is confined to the custom 0x200-byte TLUT region. Offline decode also round-trips every palette entry exactly at 5-bit channel/alpha precision.


### Toasty visual diagnostic v17 — hardware-ready TLUT confirmed

**Runtime-confirmed on 2026-09-23.**

The custom image became recognizably Toasty-colored after changing only the custom 0x200-byte palette payload from source BGR555/A1B5G5R5 words to hardware RGBA5551 TLUT words. The remaining image was still mosaicked, but color/transparency were substantially corrected.

This runtime-confirms the custom palette selector/pointer route and the hardware-TLUT representation. The residual defect was therefore texture footprint/addressing rather than palette selection.


### Toasty visual diagnostic v18 — 64x64 single-node crop

**Runtime-confirmed partial result on 2026-09-23.**

Reducing the custom image from the full 78x85 footprint to a 64x64 crop produced a clearly recognizable Toasty face, but the 64x64 content appeared twice vertically and the lower body was missing.

This was important positive evidence: the indexed pixels, corrected TLUT, dynamic-slot path, and gameplay-HUD submission all worked well enough to render a recognizable image. The remaining defect was tied to larger/taller texture layout rather than source identity.


### Toasty visual diagnostic v19 — two 64x32 slices

**Runtime-confirmed on 2026-09-23.**

v19 split the proven 64x64 crop into two independent 64x32 CI8 allocations/nodes stacked vertically. The user observed a coherent Toasty image rather than repeated/mosaicked blocks, establishing that the gameplay-HUD renderer can compose a larger custom image from multiple smaller nodes.

The visible result was still vertically cropped because only the original 64-row crop was represented.


### Toasty visual diagnostic v20 — three vertical slices, full 85px height

**Runtime-confirmed on 2026-09-23.**

v20 retained the 64-pixel-wide crop and extended it to the original 85-pixel height using three independent slices: 64x32, 64x32, and 64x21. The user observed a clean, coherent Toasty portrait with the expected full vertical extent.

This is the current strongest visual success. It runtime-confirms the multi-node composition strategy for the full height, with the image still intentionally cropped by 7 pixels on each horizontal side.


### Toasty visual diagnostic v21 — direct full-width 78px slices rejected

**Runtime-confirmed failure on 2026-09-23.**

Changing only the three slice widths from 64 to the full source width 78 caused severe horizontal striping/corruption across the image. The previously stable palette and vertical composition remained otherwise unchanged.

This rejects the direct 78-pixel-wide-node composition used by v21. It does not reject the source image or multi-node composition itself.


### Toasty visual diagnostic v22 — full-width side-column corruption

**Runtime-confirmed partial failure on 2026-09-23.**

v22 reconstructed the 78-pixel source width as three columns per vertical band: 7 + 64 + 7 pixels, producing nine textured HUD nodes total. The 64-pixel center column remained visually coherent, while both 7-pixel side columns were corrupted/glitchy.

This localizes the defect to the narrow-column backing layout rather than geometry, palette, or the center 64-pixel path. The v22 builder packed each 7-pixel row tightly as 7 bytes even though the dynamic CI8 allocator uses aligned backing rows.


### Toasty visual diagnostic v23 — narrow-column stride correction

**Runtime-confirmed partial success on 2026-09-23.**

v23 leaves v22's nine-node geometry, palette, dynamic allocations, file IDs, HUD compositor code, logo skip, and Safe Stage Select unchanged. It changes only the raw payload layout for the 7-pixel side columns.

The allocator's CI8 backing row pitch is 32-byte aligned: the already runtime-confirmed 78-pixel allocation uses stride 96, while 64 uses stride 64. Therefore a 7-pixel allocation uses a 32-byte backing row. v23 keeps the visible node width at 7 but pads every source row to 32 bytes before the raw load.

If the two side columns become clean while the center remains unchanged, this confirms row-pitch mismatch as the v22 defect and establishes a complete 78x85 Toasty image through nine composed HUD nodes.

## Related canonical owners

- [Native HUD and UI](Native-HUD-and-UI) — reusable gameplay HUD/text/render-node conclusions.
- [Data structures and encodings](Data-Structures-and-Encodings) — stable render-node structure grammar.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal proof/production allocation ownership; proof caves are not production allocations.
- [Runtime validation status](Runtime-Validation-Status) — concise cross-domain evidence matrix.
- [Project status](Project-Status) — current maturity and project priority only.
- [Toasty audio research](Toasty-Audio-Research) — current Toasty audio owner.
- [Native UI and presentation](Native-UI-and-Presentation) — old-slug compatibility/supersession index.


### Toasty visual diagnostic v24 — secondary-rectangle normalization

**Runtime-confirmed negative control on 2026-09-23; hypothesis rejected.**

v24 preserves the v23 image bytes, hardware TLUT, allocator-aligned side-row storage, nine-piece composition, texture-slot/palette bindings, placement, and test harness. The only renderer-side change is that the cloned nodes also receive explicit values for the second known pair of screen-space vertex coordinates at `+0x28/+0x2A/+0x38/+0x3A` instead of inheriting them from the live stock HUD source node.

Manual testing reproduced the **exact same corruption in the exact same stages** as v23: Fire and Earth retain their small edge artifacts, while the previously clean stages remain clean. Therefore those inherited secondary rectangle coordinates are not the cause of the stage-dependent variance.

The next bounded discriminator should keep the entire v23/v24 image/geometry/state layout fixed and change only dynamic texture allocation order. If the corruption moves or changes, it follows dynamic slot identity/lifecycle; if it remains on the same edge pixels, the suspect moves back toward narrow-piece renderer/data behavior rather than allocation identity.


### Toasty visual diagnostics v25-v31 — allocation-order sensitivity

**Runtime-confirmed on 2026-09-23; important but superseded by a later static bug finding.**

After v24 ruled out inherited secondary rectangle coordinates, v25-v31 changed only the order in which the nine dynamic CI8 pieces were allocated while preserving the image payloads, 7+64+7 geometry, row-pitch correction, palette, state-word layout, render submission, and test harness.

The visible corruption pattern changed repeatedly with allocation order:
- v25 changed the Temple/Earth/Fire artifact pattern.
- v26 also made Fortress visibly corrupted, demonstrating that a previously clean stage could become affected from allocation-order changes alone.
- v27 restored Fortress and gave one of the strongest broad results; Earth was reduced to barely visible corruption.
- v28-v29 changed the right-column sub-order but did not eliminate the remaining Fire/Temple/Earth defects.
- v30 changed the left-column sub-order; Temple lost its flying artifacts but showed a small lower-left missing patch, Earth retained about 1–2 pixels, Fire improved to a Temple-like lower-left defect plus a few stray pixels, and Fortress stayed clean.
- v31 tested the remaining left-column permutation. Temple still had a lower-left missing patch, Earth retained two pixels at a changed location, Fire retained the lower-left defect plus 2–3 floating pixels, and Fortress remained clean.

At face value this looked like strong evidence that dynamic slot identity/lifecycle mattered. However, reviewing the builders after v31 found a more direct implementation error in the saved-slot state accesses:

```text
intended state VAs: 0x800A9D40..0x800A9D60
builder pattern:      lui 0x800A
                      lw/sw ...,0x9Dxx(base)
```

MIPS load/store immediates are signed. Because `0x9Dxx >= 0x8000`, those instructions actually address `0x80099Dxx`, one 64-KiB page lower than the intended proof-state words. Both init writes and per-frame reads shared the same alias, so the builds could appear functional while unrelated stage-specific writes to `0x80099Dxx` changed which dynamic texture IDs the compositor later consumed. This bug explains why allocation-order permutations changed the visible corruption and why the affected stages varied.

### Toasty visual diagnostic v32 — saved-slot state-address alias correction

**Runtime-confirmed negative result on 2026-09-23.**

v32 returns to the v27 image/palette/allocation-order/render baseline and changes only the high-half used for the nine saved-slot state accesses. The instruction count, state-word ROM/VA ownership, image payloads, TLUT, file-table records, draw order, geometry, and dynamic allocation order remain unchanged.

The corrected address formation uses the carry-adjusted LUI high half for signed `0x9Dxx` load/store immediates, so the effective addresses are the intended `0x800A9D40..0x800A9D60` rather than the accidental `0x80099D40..0x80099D60`.

ROM comparison against a rebuilt v27 confirms every non-CRC difference is confined to the LUI immediates in the init and compositor code that access these saved slot IDs.

Manual testing in Temple, Earth, and Fire produced essentially the same residual edge corruption seen on the stronger pre-v32 builds; Fortress remained clean. Therefore the signed-address alias was a real builder bug but is **not accepted as the cause of the visible stage-dependent corruption**.


### Toasty visual diagnostic v33 — dynamic-slot lifecycle marker

**Implementation/static-confirmed; runtime pending manual validation.**

v33 preserves the v32/v27 image data, hardware TLUT, nine-piece geometry, allocator-aligned payloads, allocation order, corrected saved-state addresses, and render-node composition. It adds only a per-HUD-frame validation pass over the nine saved dynamic texture IDs.

For each piece the wrapper checks:
- saved ID is within allocator range `0x200..0x2FF`;
- slot record `0x802E83F0 + id*0x10` remains active at halfword `+0x0E == 1`;
- record `+0x08/+0x0A` still matches the piece's expected requested width/height.

If any invariant fails, the wrapper draws the proven native-text marker `V33 SLOT MUT` at the lower-left while continuing to render the Toasty image. A marker on the corrupt stages would directly support slot reset/reuse as the cause. If corruption remains without the marker, the next diagnostic should move down to backing-pointer/pixel-storage integrity rather than more allocation-order permutations.


### Toasty visual diagnostic v33 — slot-record lifecycle check

**Runtime-confirmed negative control on 2026-09-23.**

v33 preserves the v32/v27 visual/data/allocation path and adds only a per-HUD-frame validation pass over all nine saved dynamic texture slots. It checks that each saved ID remains within `0x200..0x2FF`, the allocator record remains active at `+0x0E == 1`, and the recorded width/height still match the piece request. Any mismatch would draw `V33 SLOT MUT`.

Manual testing reproduced the same Toasty corruption pattern as before without a reported `V33 SLOT MUT` marker. Therefore saved slot-ID range, active-state loss, and width/height mutation are not the cause on the tested routes.

### Toasty visual diagnostic v34 — backing-pointer identity check

**Runtime-confirmed negative control on 2026-09-23.**

v34 returns to the v32/v27 visual baseline and changes only diagnostic instrumentation. After all nine dynamic allocations/raw loads, a compact helper snapshots each saved slot's current backing pointer from `0x800ED940[id]`. Every HUD frame, the wrapper compares the current pointer for each saved slot against that captured value.

Any mismatch draws `V34 PTR MUT` through the proven native-text path while leaving the Toasty image rendering active. Image bytes, palette, nine-piece geometry, allocation order, saved slot IDs, render-node setup, and draw order are unchanged.

Interpretation:
- corruption + `V34 PTR MUT` -> backing-pointer replacement/reuse is implicated;
- corruption with no marker -> pointer identity is stable and the next bounded diagnostic should inspect the backing pixel bytes themselves.


Manual testing reproduced the same Temple/Earth/Fire corruption pattern as the preceding baseline and did not report `V34 PTR MUT`; Fortress remained clean. Therefore each saved dynamic slot continued to resolve through `0x800ED940[id]` to the same backing pointer captured after load on the tested routes. Backing-pointer replacement/reuse is rejected as the direct cause of the visible corruption.

### Toasty visual diagnostic v35 — narrow-buffer pixel-integrity check

**Implementation/static-confirmed; runtime pending manual validation.**

v35 returns to the v32/v27 visual baseline and adds only a per-HUD-frame integrity pass over the six narrow 7-pixel side-piece backing buffers. The existing allocator-aligned 32-byte row pitch is preserved. For each narrow buffer the builder computes two independent expected values from the exact padded payload written by the raw loader: a wrapping 32-bit word sum and a 32-bit word XOR.

At runtime the wrapper resolves each narrow piece's current backing pointer through the already-established saved slot ID and `0x800ED940[id]`, recomputes both checksums over the complete padded buffer, and compares them with the build-time values. Any mismatch draws the proven native-text marker `V35 PIX MUT` while the Toasty image remains active.

Interpretation:
- corruption + `V35 PIX MUT` -> actual backing CI8 bytes are changing after load;
- corruption with no marker -> the narrow backing bytes are intact, pushing the remaining defect into texture upload/cache/TMEM/render interpretation rather than slot record, backing pointer, or source-buffer integrity.


### Toasty visual diagnostic v35 — narrow-buffer pixel-integrity check

**Runtime-confirmed negative control on 2026-09-23.**

Manual testing in Temple, Earth, and Fire reproduced the same residual corruption pattern and did not show the `V35 PIX MUT` marker. Therefore the six narrow side buffers' padded CI8 contents remained equal to their build-time payloads under both the per-frame wrapping sum32 and xor32 checks on the tested routes. Together with v33-v34, this rejects saved-slot metadata loss, backing-pointer replacement, and post-load source-buffer mutation as the direct cause.

The surviving defect is now downstream of the backing bytes: texture upload/cache/TMEM/render interpretation of the 7-pixel-wide side pieces is the leading bounded hypothesis.

### Toasty visual diagnostic v36 — 32-pixel logical side nodes

**Implementation/static-confirmed; runtime pending manual validation.**

v36 returns to the v32/v27 visual baseline and changes only the six narrow side pieces' logical allocator/render width. Their payloads already use a 32-byte allocator row pitch after v23; v36 now requests and renders those rows as width 32 instead of width 7. The first 7 columns retain the genuine Toasty pixels and the remaining 25 columns are existing palette-index-0 padding. The proven custom TLUT maps index 0 to transparent, so these added logical columns are intended to be visually inert.

The center pieces remain width 64, all image bytes and file payloads are unchanged, placement is unchanged, allocation order remains the v27 arrangement, and the corrected saved-slot state addresses remain in use.

Interpretation:
- if Temple/Earth/Fire become clean, the residual defect is specifically tied to the renderer/TMEM path for 7-pixel logical textures rather than storage integrity;
- if corruption remains, the next work should inspect the renderer's tile/load-state derivation rather than return to allocation permutation or buffer-lifecycle hypotheses.


### Toasty visual diagnostic v36 — 32-pixel logical side nodes

**Runtime-confirmed negative result on 2026-09-24.**

Temple, Earth, and Fire still showed visible corruption, and the corruption pattern changed relative to the 7-pixel baseline. In Fire the artifact field extended farther to the right than before. Fortress remained the clean control.

This establishes that the residual defect is **width-sensitive**, but widening the six side nodes all the way to the allocator's 32-byte row pitch is not the correct fix. Because the payload bytes, palette, allocation order, and backing storage remained unchanged, the changed artifact reach is strong evidence that the renderer/TMEM path is consuming the side-node logical width directly.

### Toasty visual diagnostic v37 — 8-pixel logical side nodes

**Implementation/static-confirmed; runtime pending manual validation.**

v37 keeps the exact v36/v32 image bytes, TLUT, 32-byte-padded side payloads, allocation order, corrected saved-state accesses, positions, and nine-piece composition. The only runtime-critical change is the six side pieces' logical allocator/render width: `32 -> 8`.

This is the smallest byte-aligned CI8 width above the seven visible side pixels. Each side row therefore contains the seven real Toasty pixels plus exactly one transparent palette-index-0 column while still retaining the same 32-byte backing pitch.

Interpretation:
- if the stage-specific artifacts disappear, the renderer/TMEM path likely requires at least 8-pixel logical CI8 width even though backing allocation remains 32-byte aligned;
- if artifacts remain, the next renderer-side investigation should trace the tile/load-line derivation rather than widen the logical rectangle further.


### Post-v37 static renderer trace — dynamic-slot source-width ownership

**Static-confirmed mechanism; causal link is a strong inference pending one bounded runtime fix.**

After v37 remained corrupted, the next step stopped parameter permutation and traced the actual dynamic-texture allocator, stock callers, and gameplay textured-node renderer.

#### Dynamic slot record semantics

`0x8001C2B4` searches dynamic IDs `0x200..0x2FF` using 16-byte records at `0x802E83F0 + id*0x10`.

For a new allocation:
- requested width is rounded up to 32 pixels/bytes for backing-capacity allocation;
- record `+0x04` receives the aligned capacity width;
- record `+0x06` receives capacity height;
- record `+0x08` is initially set to the same aligned width;
- record `+0x0A` receives height;
- record `+0x0E` becomes active;
- `0x800ED940[id]` receives the backing pointer.

The allocator also has a reuse path. It may return an inactive existing record whose `+0x04/+0x06` capacity is large enough. That path sets `+0x0E = 1` and returns the ID **without rewriting `+0x08`**.

Stock callers demonstrate that `+0x08` is caller-owned texture-image width state, not merely allocator capacity metadata. Multiple direct callers immediately compute `record = 0x802E83F0 + id*0x10` after `0x8001C2B4` and store the current source-image width to `record+0x08`; examples include the allocation sequences beginning at `0x8002049C`, `0x80020538`, and `0x800205AC`. The fixed-slot initializer `0x8001BF70` likewise distinguishes record `+0x04` from `+0x08`.

#### Renderer consumption

`0x8001F7A8` reads texture slot `node+0x4A`, indexes the same record table, loads halfword `record+0x08`, subtracts one, and encodes that value into the RDP `SetTextureImage` command (`FD48....`) as the DRAM texture-image width. The backing pointer comes from `0x800ED940[id]`.

For the CI8 path it then emits the expected `SetTile(load tile 7) -> LoadSync -> LoadTile -> PipeSync -> SetTile(render tile 0) -> SetTileSize` sequence. Node `+0x10/+0x12` and `+0x20/+0x22` provide the loaded source rectangle. The stock HUD node used by the Toasty wrapper initializes `+0x30/+0x32 = 0` and `+0x40/+0x42 = 1`, so the inherited initial S/T and 1:1 texture steps are not random stage state. Its render-mode word `0x0C087008` selects the point-filter path; bilinear edge sampling is therefore not the leading explanation.

Nintendo's RDP documentation defines `SetTextureImage` width as the width of the original DRAM texture image and `LoadTile` as a rectangular subregion of that image. The tile `line` field is the TMEM row width in 64-bit words; LoadTile pads non-64-bit rows in TMEM.

#### Builder omission through v37

The Toasty builders allocate each piece and load raw CI8 bytes into the returned backing pointer, but they never perform the stock caller's post-allocation write to `record+0x08`.

This matters specifically on reused dynamic records:
- the six side payloads use a real DRAM row pitch of 32 bytes after v23;
- center payloads use a 64-byte row pitch;
- a fresh allocation happens to initialize `+0x08` to the matching aligned width;
- a reused record can retain a previous texture's `+0x08` width even though its capacity is large enough for the new piece.

If `+0x08` is stale, `0x8001F7A8` tells the RDP the wrong DRAM row width. `LoadTile` then advances each source row using the wrong stride. That can simultaneously:
- omit genuine edge texels by fetching transparent padding or the wrong source row;
- place nonzero Toasty texels in locations that should be transparent;
- produce different corruption by stage because the reusable dynamic-slot population differs;
- move the corruption when allocation order changes because different pieces inherit different reused records.

This mechanism fits the observed screenshots, including the missing lower-left Toasty data in Fire as well as the floating colored pixels. Fortress remaining clean is consistent with fresh or width-compatible records, but that stage-specific explanation remains inference until the corrected record-width proof is run.

#### Reinterpretation of v33 and v36-v37

The earlier v33 diagnostic described record `+0x08` as the allocator's requested width and compared it against the visible piece width. The static trace supersedes that interpretation: `+0x08` is the source-image width consumed by `SetTextureImage`, and stock callers may rewrite it after allocation. Therefore v33 remains useful for its slot-ID/active checks but is **not** clean evidence that texture-image width state was correct.

Likewise, v36/v37 did not isolate one pure RDP width field: they changed the allocator request and the node source/destination width together, which can also change which reusable capacity record is selected. Their runtime results remain valid observations, but the earlier conclusion that they directly proved a 7-pixel TMEM-width defect is superseded.

#### Next bounded proof

The next disposable ROM should return to the v32/v27 visible geometry and allocation order, keep side source/destination width at 7, keep the existing 32-byte-padded side payloads, and add exactly one stock-convention operation after each dynamic allocation:

- write `record+0x08 = 32` for TL/TR/ML/MR/BL/BR;
- write `record+0x08 = 64` for TC/MC/BC.

No allocation-order, node-geometry, palette, payload, audio, trigger, or stage-flow change should accompany that proof. If the stage-specific missing/extra edge pixels disappear, the causal link is Runtime-confirmed.


### Toasty visual diagnostic v38 — source-image width normalization

**Runtime-confirmed on 2026-09-24 across all eight safe stages.**

v38 returns to the v32/v27 visual baseline. It preserves the nine-piece image bytes, hardware TLUT, visible 7+64+7 geometry, 32-byte-padded side payloads, allocation order, corrected saved-slot state addresses, logos-skip/safe-selector harness, and gameplay render composition.

The only runtime-critical change is restoration of the stock dynamic-texture convention identified by the post-v37 static trace. After all nine dynamic slots are allocated/loaded and before any Toasty rendering, v38 writes slot-record `+0x08` to the actual DRAM source row width:
- side pieces TL/TR/ML/MR/BL/BR: `32`;
- center pieces TC/MC/BC: `64`.

The helper is called by replacing two palette-setup instructions in the fixed-size init stub; it recreates those displaced instructions before returning, so palette setup semantics remain unchanged. A bytewise comparison against a rebuilt v32 ROM confirms that every non-CRC difference is confined to that two-instruction helper call and the new width-normalization helper in the existing guarded zero-filled proof cave.

Disposable ROM SHA-256: `ac5c1bd2675347ad549de9d2da4fe583cf84edd0d668936ee59ecc1c0543ba4b`.

Runtime acceptance test: Temple, Earth, Fire, and Fortress. If the previously stage-dependent missing/extra edge pixels disappear while Fortress remains clean, the stale `record+0x08` source-width mechanism is Runtime-confirmed as the cause. Any remaining corruption should be treated as evidence against that causal conclusion rather than prompting further allocation-order permutations.


### v38 runtime result — stage-stable full image

**Runtime-confirmed on 2026-09-24.**

The user manually tested the v38 source-width-normalization ROM across all eight safe stages and reported the Toasty image as visually perfect in every stage. The earlier stage-dependent extra pixels and missing edge data were absent, including the Temple/Earth/Fire failure patterns that had persisted through v23-v37; Fortress remained clean.

This confirms the causal mechanism established by the post-v37 static trace: after each dynamic texture allocation, the Toasty path must initialize slot-record `+0x08` to the actual DRAM source row width consumed by `0x8001F7A8` / RDP `SetTextureImage`:
- 32 bytes/pixels for the six side pieces;
- 64 bytes/pixels for the three center pieces.

The nine-piece visual renderer, corrected hardware TLUT, allocator-aligned payloads, dynamic slot bindings, and stage-stable presentation are therefore now Runtime-confirmed as a bounded proof line.

The remaining Toasty work is no longer image-correctness research. It is production composition:
1. allocate the visual code/state/assets from production-owned storage rather than proof caves;
2. compose the already Runtime-confirmed Toasty audio route with the visual effect;
3. implement the slide/lifetime state machine;
4. resolve and validate the final qualifying uppercut/contact trigger plus 4% cosmetic gate;
5. run a guarded full-production composition proof.

### Toasty visual production-layout proof v39

**Rejected / failed at runtime on 2026-09-24.**

v39 is the first bounded move from the disposable v38 cave layout toward the current production runtime architecture. It deliberately preserves the v38 visual behavior while changing only storage/transport ownership.

The current production 16 KiB arena reservation remains the governing memory contract. v39 uses the build-time `ExpansionPoolAllocator` semantics for the 15 KiB expansion pool and packs only native Toasty code/state/TLUT there:

| Slice | RDRAM interval | Size |
|---|---:|---:|
| compositor | `0x801AF820..0x801B034B` | 2,860 bytes |
| init + transparent-fill helper | `0x801B0350..0x801B065B` | 780 bytes |
| nine saved dynamic-slot IDs | `0x801B0660..0x801B0683` | 36 bytes |
| hardware-ready Toasty TLUT | `0x801B0690..0x801B088F` | 512 bytes |

Total expansion-pool use is 4,208 bytes, leaving `0x2B90` (11,152 bytes) of the current 15 KiB pool unconsumed by this proof layout.

The CI8 source slices are **not duplicated into the expansion pool**. Three v38 pieces (TL, TR, ML) are entirely palette-index-0/transparent after allocator padding, so v39 zero-fills those dynamic backing buffers directly. The six nonzero padded CI8 slices remain ROM-backed and raw-load directly into the same dynamic texture allocations through six clean-table proof IDs `0x13..0x18`. One packed feature file uses proof ID `0x1A` and loads the native feature blob to `0x801AF820`.

Proof-only high-ROM source:
- six nonzero CI8 slices: `0x00F70000..0x00F71E7F`, 7,808 bytes total;
- packed native feature file: `0x00F72000..0x00F7306F`, 4,208 bytes.

The stage-reset proof stub uses the established 16 KiB arena-floor mechanism, synchronizes the arena base, and loads file `0x1A` into the expansion pool before the existing v38 post-HUD-init hook runs. v38 draw geometry, palette selector/TLUT contents, dynamic allocation order, 7+64+7 visible composition, and the confirmed slot-record `+0x08 = 32/64` source-row-width rule are unchanged.

The fast logos-skip/safe-stage-selector route is retained only as a disposable manual-test harness. Its old selector-cave use is **not** part of the proposed Toasty production allocation. Likewise, v39's standalone stage-reset stub is a composition proof: final product integration must merge the extra feature-file load into the existing production bootstrap rather than treat the bootstrap composite as newly free space.

Disposable ROM SHA-256: `3d8409e1e56ea307c6072500588498025586a5824dc0189b44c405849547c50e`.

Runtime acceptance test: verify the same stage-stable v38 image in Temple, Earth, Fire, and Fortress at minimum, preferably all eight safe stages. A pass establishes the expansion-pool storage/transport layout; it does not yet establish audio, slide/lifetime, or the final uppercut/contact + 4% trigger.
#### v39 failure diagnosis

The first runtime test showed broad rendering corruption: the stock HUD, Sub-Zero, and the Toasty image were all visibly damaged. This is not a Toasty-edge regression; it is a failure of the v39 execution/layout proof itself.

Static re-audit found a concrete architectural mistake. v39 raw-loaded the new native code into the expansion-pool physical range but patched the HUD/init hooks to execute the freshly loaded code through its **cached KSEG0 aliases** (`0x801AF.../0x801B...`). The established MKMSZR native-payload contract intentionally executes freshly raw-loaded native code through the **uncached KSEG1 alias** (`0xA01AF...`) and uses uncached state aliases. v39 violated that contract. Direct J/JAL cannot switch from the `0x8...` segment to `0xA...`, so any future expansion-pool execution proof needs a small static KSEG0 trampoline that performs an indirect `JR/JALR` to the KSEG1 entry.

The v39 allocation size is also rejected as a production target. It copied the v38 proof implementation almost verbatim: the nine-piece compositor alone is 2,860 bytes because it unrolls the full 0x58-byte node clone and patch sequence nine times; init/helper code adds about 780 bytes; the TLUT adds 512 bytes; state/alignment brings the proof slice to 4,208 bytes. No CI8 image pixels were stored in the expansion pool, but promoting the unoptimized proof compositor wholesale was still inappropriate. Production work should replace it with a compact table-driven compositor/init before claiming a feature allocation.

v38 remains the accepted Runtime-confirmed image-correctness baseline. v39 must not be used as production-allocation evidence.


### Toasty visual production-layout proof v40

**Runtime-confirmed on the user-tested gameplay route on 2026-09-24.**

v40 supersedes rejected v39 and returns to the Runtime-confirmed v38 visual semantics while fixing both v39 architectural mistakes.

Execution:
- the feature file is still raw-loaded into the reserved expansion-pool base;
- freshly loaded native code is entered only through uncached KSEG1 aliases;
- the existing direct gameplay hooks target two 16-byte static KSEG0 trampolines at the old v38 proof cave;
- each trampoline performs an absolute indirect jump into the KSEG1 compositor/init entry;
- all calls from expansion code into stock engine functions use `JALR` to explicit KSEG0 addresses, and init resumes stock through an explicit KSEG0 `JR`.

Layout is table-driven rather than nine-times-unrolled:

| Expansion slice | Size |
|---|---:|
| compositor code | 336 bytes |
| init code | 292 bytes |
| draw table | 72 bytes |
| allocation/init table | 72 bytes |
| nine saved dynamic-slot IDs | 36 bytes |
| hardware-ready CI8 TLUT | 512 bytes |

Alignment brings total expansion-pool use to **1,360 bytes (`0x550`)**, leaving **`0x36B0` bytes (14,000 bytes)** of the 15 KiB pool. Executable Toasty code itself is **628 bytes**. The CI8 image slices remain ROM-backed and are not stored in the expansion pool.

v40 preserves all nine exact v38 padded CI8 source slices, their file IDs `0x13..0x1B`, allocation order, 7+64+7 visible geometry, custom palette, and the Runtime-confirmed slot-record `+0x08 = 32/64` source-row-width normalization. A separate proof-only feature file uses clean file ID `0x12`.

Static guards cover the clean-ROM hook bytes, arena-floor patch pairs, file-table entries, high-ROM source ranges, the 32-byte static trampoline cave, bootstrap stub capacity, and an explicit ROM-diff allowlist.

Disposable ROM SHA-256: `556fe0f909c50121dcf7aa8e4069955ad7cbaa4cfbd54d46cb1266940c35b7a2`.

Runtime result: the user reported v40 working normally, with no recurrence of v39's stock-HUD/player/Toasty corruption. This confirms the compact uncached expansion-code architecture on the tested route. v38 remains the exhaustive eight-safe-stage image-correctness proof.

### Toasty feature-core composition proof v41

**Runtime-confirmed on the user-tested gameplay route on 2026-09-24.**

v41 builds directly on the Runtime-confirmed v40 compact uncached layout and starts the actual feature behavior rather than another image diagnostic.

The gameplay-HUD compositor now owns a stage-local four-word presentation state: phase, remaining ticks, signed horizontal shift, and trigger latch. Idle rendering submits no Toasty nodes. Temporary test trigger is remapping-aware **Block+Use**; the trigger frame clears the semantic input halfword so the chord itself does not also perform a gameplay action.

Presentation timing follows the statically confirmed donor behavior:
- slide in for 6 HUD ticks, using 13 pixels/tick from +78 horizontal offset to the v38 hold position;
- enter a 32-tick hold at the v38 position and play the Toasty voice exactly once at hold entry;
- reverse horizontal motion for 16 ticks, then return to idle;
- trigger latch requires release before a later activation.

The visual path remains v40/v38: nine exact CI8 source slices, same draw geometry, same palette/TLUT, same allocation order, and the Runtime-confirmed slot-record `+0x08 = 32/64` normalization.

Expansion-pool use rises from v40's `0x550` to **`0x6D0` (1,744 bytes)** because the state machine expands compositor code to 684 bytes, init to 320 bytes, and adds 16 bytes of presentation state. CI8 pixels remain ROM-backed. Remaining expansion-pool capacity is **`0x3530` (13,616 bytes)**.

Audio uses the already Runtime-confirmed v03 Toasty transplant and fires the native gameplay SFX wrapper at the slide-in -> hold boundary. **Important proof limitation:** v41 still uses v03's disposable event-524/subpatch replacement, so ordinary pickup sound is also Toasty in this ROM. This is intentional only for the combined feature-core validation; a dedicated production audio definition/route remains required before final integration.

Disposable ROM SHA-256: `927aff6127ce35aef9ee7f1b9fa57ce0a2709cdbb2a6dcf8d7deca831d831623`.

Runtime result: the temporary Block+Use trigger successfully produced the complete composed effect: Toasty slid in, the confirmed voice played, the image held, and it slid back out while stock HUD/player rendering remained normal. The user judged the behavior almost correct but requested two presentation changes before trigger integration: align the 78x85 image to the actual lower-right screen edge and make the complete presentation half as long, with slide-in/out twice as fast. No uppercut/contact or 4% gate is present yet.


### Toasty feature-core presentation adjustment v42

**Runtime-confirmed on 2026-09-24.**

v42 changes only presentation geometry/timing from the Runtime-confirmed v41 core.

The v41 screenshot plus the established 78x85 geometry places the effective hold rectangle at approximately `(200,100)..(278,185)` in the 320x240 gameplay coordinate space. v42 moves all nine draw-table entries by `+42 X / +55 Y`, giving the intended lower-right hold rectangle:

`(242,155)..(320,240)`.

Timing is exactly halved while preserving the same total slide distances:
- slide-in: `6 -> 3` HUD ticks;
- hold: `32 -> 16` HUD ticks;
- slide-out: `16 -> 8` HUD ticks;
- slide step: `13 -> 26` pixels/tick.

Total presentation lifetime therefore changes from 54 to 27 HUD ticks. Audio still fires exactly once at hold entry. The temporary Block+Use trigger, v03 proof audio host, compact KSEG1 layout, image/TLUT/slot setup, and expansion footprint remain unchanged.

A rebuilt v41-to-v42 ROM comparison finds only 26 changed bytes, all inside the packed Toasty feature file; no unrelated ROM range changes.

Disposable ROM SHA-256: `346b03646b0634619284f9191171d70827c4092b00f1e9e8bc506cfaf356ce60`.

Runtime result: the user reported v42 as **perfect**. The image lands flush at the lower-right edge, the 3/16/8 presentation timing feels correct, the Toasty voice fires once, and stock HUD/player rendering remains intact on the tested route. v42 is therefore the current accepted presentation baseline.


### Gameplay-trigger reconciliation and proof v43

**Donor retail/static reconciliation complete; v43 Implementation/static-confirmed, runtime Pending.**

The final trigger is **not uppercut-only**. The supplied MKT USA Rev. 2 retail reaction table at `0x800A8AE0` resolves the exact comment-worthy family to:

- selector `0x08` -> `r_uppercut` at `0x80056270`;
- selector `0x0E` -> `r_combo2_stab` at `0x800594E8`, which reaches shared `combo2`;
- selector `0x12` -> `r_combo2` at `0x80059578`, which reaches shared `combo2`;
- selector `0x13` -> `r_combo3` at `0x80059690`;
- selector `0x14` -> `r_combo4` at `0x800597B4`, which reaches shared `combo43`;
- selector `0x15` -> `r_combo5` at `0x800560A0`;
- selector `0x17` -> `r_combo6` at `0x80055FE8`.

Those retail routines reach `create_fx(FX_COMMENT)` with effect index `0x0E` at the corresponding direct/shared callsites. This matches the preserved MKT source family and supersedes the former uppercut-only shorthand.

#### Exact supplied-retail probability

The supplied Rev. 2 effect table resolves `FX_COMMENT = 0x0E` to `0x8002D810`. That routine waits `0x13` ticks, then calls retail `randper` at `0x8006E50C` with:

- `0x40` normally -> 64/1000 = **6.4%**;
- `0xA0` when background ID is `0x1B` (`BKGD_MK2PITSTAR_MOD`) -> 160/1000 = **16%**.

The helper is per-thousand: it reduces its random value modulo `0x3E8` and succeeds when the result is below the argument.

The earlier retail `randper(40)` / immediate-`0x28` site at `0x80039BF4` is a **different Toasty-capable path**, not the reaction-driven `FX_COMMENT` process. Treating that site as the final reaction probability is superseded. For MKMSZ, which has no semantic equivalent of MKT's MK2 Pit Star background, the bounded proof uses the normal retail probability `0x40` universally; adding a special MKMSZ stage bonus would be a separate product/design choice.

#### MKMSZ reaction mapping and hook

MKMSZ's global reaction table at `0x800A1190` preserves the same qualifying semantic selector family:

`0x08, 0x0E, 0x12, 0x13, 0x14, 0x15, 0x17`.

For fighter type `0x04`, stock strike selector `0x08` resolves to a record whose unblocked reaction byte is `0x08`, independently confirming the native Uppercut -> uppercut-reaction chain. The v62 combo proof separately runtime-confirms translated combo-finisher behavior in the same inherited combo-reaction family.

The narrow host seam is **VA `0x8002DF28` / ROM `0x0002EB28`**, after collision success and after the blocked branch has already separated. Immediately before that call, stock code reads the strike record's unblocked reaction byte at `+0x08`, indexes the reaction table, and places the resolved victim-reaction callback in `a0`. The stock call transfers the victim through `0x8002E078`.

This seam is narrower than `0x8002BA04`: misses and ordinary blocked contacts never reach it. The proof wrapper compares the already-resolved reaction callback against the seven qualifying callback addresses, arms Toasty's pending-comment countdown only on a match, then invokes the original `0x8002E078` transfer unchanged.

MKMSZ also has an inherited per-thousand `randper` helper at **`0x80016008`**. v43 uses `randper(0x40)` rather than introducing a custom RNG path.

#### v43 disposable gameplay-trigger proof

`MKMSZR_toasty-gameplay-trigger_common-proof_v43.z64`

Identity:

- SHA-256 `53523d1daad76f47303e95e200e5b5fbe2dc0c62a8c2ed7fb281d645ddd30128`;
- CRC1/CRC2 `6CD9998E / 657F064A`.

v43 is built from the exact supported clean ROM and preserves v42's image, TLUT, dynamic-slot setup, lower-right geometry, **3/16/8** presentation timing, 26-pixel slide steps, and one-shot voice call at hold entry. Static comparison confirms the active v42 presentation path from compositor offset `+0xC8` onward is byte-identical; only the former temporary-trigger/idle block and the new reaction hook/wrapper are changed.

The existing four-word feature state is reused: `+0x0C`, formerly v42's Block+Use latch, becomes a pending-comment countdown. A qualifying unblocked reaction arms it to `0x13`; expiration rolls native `randper(0x40)`; success enters the unchanged v42 presentation state machine.

The new reaction wrapper occupies 176 bytes at `0x801AFEF0..0x801AFF9F`. Total Toasty expansion-pool use is therefore `0x780` (1,920 bytes) from `0x801AF820..0x801AFF9F`, leaving `0x3480` bytes. The wrapper is entered through a small KSEG0 trampoline in the already-owned proof bootstrap cave; no new zero-filled region is promoted to free storage.

v43 rebuilt byte-for-byte identically in an independent second build. **No emulator automation was run.** Runtime status remains Pending until manual validation.

Proof limitations remain explicit:

- the v03 disposable pickup-audio host is still present, so ordinary pickup audio is still Toasty in this proof;
- the MKT special-background 16% case is not mapped because MKMSZ has no equivalent background semantic;
- if another qualifying reaction arrives while Toasty is already visibly active, the proof retains the pending countdown until the presentation returns idle; exact donor concurrent-process behavior is not claimed.

v42 remains the accepted Runtime-confirmed presentation baseline. v43 changes only trigger semantics around that baseline.


### v44 trigger validation and v47 production-composition gate

**v44 Runtime-confirmed.** The 50% diagnostic build changed only the per-thousand probability immediate from the reconciled v43 trigger proof. The user confirmed the real successful-reaction trigger works and the complete effect is correct. This promotes the `08/0E/12/13/14/15/17` successful/unblocked reaction-family trigger on the tested route; 50% was diagnostic only.

**v46 Runtime-confirmed.** The dedicated-audio successor restores ordinary pickup sound and keeps the accepted v42 image/timing/voice presentation intact.

**v47 Runtime-confirmed on 2026-09-25.** The user reported the full production-composition ROM works perfectly. v47 is the first bounded composition against the exact current production patcher rather than the disposable proof harness. It packs Toasty code, TLUT, tables/state, and all nine Runtime-confirmed padded CI8 slices into one raw expansion module loaded through file ID `0x1A` at RDRAM `0x801B0000`. The packed module is `0x3320` bytes and ends at `0x801B331F`, leaving `0x100` bytes before the reserved-pool boundary `0x801B3420`.

High-ROM layout for the integration proof is `0xF68000..0xF6B31F` for the module and `0xF6B320..0xF6BB35` for the confirmed Toasty sample. This starts after optional rainbow file-87 ownership ending at `0xF679E0` and remains below title ownership beginning at `0xF90000`. Tiny entry stubs compose only inside padding already owned by the production four-box selector helper and box-indicator regions; no old proof cave is promoted to production-free storage.

The vanilla and rainbow compositions pass guards/bounds checks, and the manually exercised v47 production composition is Runtime-confirmed. The v47 ROM intentionally used 500/1000 only for fast validation. The merged production tuning is now 80/1000 = **8%**; no presentation, trigger-family, audio-route, or allocation semantic changes accompany that tuning change.
