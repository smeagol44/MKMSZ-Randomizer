# Native UI and presentation

## Confirmed gameplay HUD path

The stable gameplay HUD function is `0x8005BFB0`. It contains 13 calls to node submitter `0x8001EAE4`. Production hooks one call at ROM `0x5D9CC`, executes the displaced submission first, then draws the box indicator.

Render nodes are allocated by `0x8002018C` and are `0x58` bytes/22 words. Vertex X/Y halfwords occur at `+0x08/+0x0A`, `+0x18/+0x1A`, `+0x28/+0x2A`, and `+0x38/+0x3A`; colors are at `+0x14`, `+0x24`, `+0x34`, and `+0x44`.

## Native text

| Purpose | Address |
|---|---:|
| Text draw | `0x80073E74` |
| Width calculation | `0x80074084` |
| Font data | `0x800B1E20` |

Arbitrary null-terminated strings placed in custom RDRAM were runtime-confirmed. This is the preferred path for small persistent gameplay labels.

The production wrapper occupies ROM `0xAFA24..0xAFA97`, begins at VA `0x800AEE24`, and stores its string at VA `0x800AEE80`. It reads active-box state, rewrites the digit in `BOX 1 OF 4`, and draws at `x=230`, `y=210`. This area was originally legal-screen text, but the exact stock bytes are guarded and boot branding owns the adjacent strings.

## Legal / boot branding

The legal-screen text path is reused rather than replaced. The stock screen has 13 text submissions; production repoints those existing calls into one guarded packed text region at ROM `0xAF998..0xAFA23` plus the final license slot at `0xAFA98..0xAFABB`.

The current MKMSZR layout is:

```text
MORTAL KOMBAT® MYTHOLOGIES
R A N D O M I Z E R
<CHAR> EDITION
©2026 LA PAVADA INC.


<seeded joke line 1>
<seeded joke line 2>


BY SMEAG

NOT LICENSED BY NINTENDO
```

`<CHAR>` uses the same configured title-character value as the title screen, so the browser/CLI field drives both places. It remains uppercase and bounded to 12 name characters before ` EDITION` is appended.

The stock legal font encodes the registered-sign glyph with ASCII `^` and the copyright glyph with ASCII `~`; production preserves that stock encoding rather than introducing a new font path. The packed region is exactly bounded for the worst-case 12-character edition name and leaves two zero bytes before the adjacent `BOX n OF 4` code allocation.

**Evidence:** the redesigned 2026 layout is **Runtime-confirmed**. The user confirmed the exact rearranged legal screen looks correct in-game, including the configurable edition line, seeded joke placement, `BY SMEAG`, and `NOT LICENSED BY NINTENDO`. The same layout is also full-pipeline Implementation/CI-confirmed, including a non-default `SEKTOR EDITION` build.

## Context-specific renderer family

The path beginning at `0x80073CEC` and calling `0x8001E578` is real, but evidence shows it is context-specific rather than a universal always-on HUD/sprite API. Its suitability as a generic presentation abstraction remains unproven.


## Title-menu branding audit

The title-menu path is now decoded far enough to support the accepted MKMSZR rebrand.

**Static-confirmed on the clean USA Rev. 0 ROM.** The normal title controller is `0x80078C40`. Its title artwork is a six-tile CI8 image submitted through the context-specific `0x80073CEC -> 0x8001E578` family. Earlier runtime instrumentation of that family visibly duplicated the title logo while leaving the `START` / `OPTIONS` menu text and cursor untouched.

The six title resources are:

| Resource | Size | Screen origin | File-0x5E decoded record |
|---:|---:|---:|---:|
| `0x3C6` | 120x120 | `(0,0)` | `+0x3B780` |
| `0x3C7` | 100x120 | `(120,0)` | `+0x3EFCC` |
| `0x3C8` | 100x120 | `(220,0)` | `+0x41EB8` |
| `0x3C9` | 120x120 | `(0,120)` | `+0x44DA4` |
| `0x3CA` | 100x120 | `(120,120)` | `+0x485F0` |
| `0x3CB` | 100x120 | `(220,120)` | `+0x4B4DC` |

Together they form one exact 320x240 indexed composite.

### Palette correction

The palette descriptor begins at `0x800B2760` / ROM `0xB3360`, but the earlier audit was four bytes early when interpreting palette entries. The word at `0xB3360` is the `0x100`-entry descriptor/count; the 256 16-bit palette entries begin at **ROM `0xB3364`**.

For offline title reconstruction and re-quantization, interpreting those entries as **BGR555** reproduces the stock emulator appearance closely: dark maroon-black background, icy-blue upper plaque and blue `SUB-ZERO`. The older RGB interpretation is rejected for title-preview work because it produced misleading cyan/green/noisy previews.

### File 0x5E packaging

The six tiles live in global file ID `0x5E`. Its clean-ROM table entry points to compressed ROM `0x4E3060..0x51243F` (end-exclusive `0x512440`), flag `1`; the package expands to exactly `0x61494` bytes.

The package uses the game's MSB-first LZW-style stream. A matching encoder/decoder pair is **Static-confirmed** by byte-exact stock recompression: decoding the stock package and re-encoding it yields the original compressed size `0x2F3E0` and round-trips to the same `0x61494` decoded bytes.

The accepted Candidate-B artwork changes only the six title-tile pixel regions. Re-encoding that modified package produces `0x2FD95` bytes, which is `0x9B5` bytes larger than the stock slot. Production therefore cannot overwrite file `0x5E` in place; it needs a guarded relocation.

### Accepted Randomizer title proof

The accepted image direction is the icy-metallic **MORTAL KOMBAT MYTHOLOGIES / RANDOMIZER** Candidate B, converted to the exact native 320x240 CI8 image with the corrected stock BGR555 palette. The user runtime-tested the final art and reported it looks awesome.

The final standalone title proof is:

- `MKMSZR_title-screen_candidate-b_with-edition_proof_v05.z64`
- SHA-256 `3f98e2d73fc66203a333d2b6a9f0861cc528201804e96349c2dce376f8f189d0`
- edition text centered at `x=160`, `y=114`
- displayed string `SUB-ZERO EDITION`

This is **Runtime-confirmed** for the title-screen route shown by the user. The proof's title art and final edition placement are accepted visually.

The proof itself is **not a production allocation**. It used a raw file-`0x5E` relocation overlapping the production payload region and used the bootstrap cave beginning at ROM `0x9AD84`, which production already owns. Those proof locations must not be copied into the browser/CLI pipeline.

### Edition text

Immediately after the six image submissions, vanilla draws `START` at `(160,160)` and `OPTIONS` at `(160,180)` through frontend text renderer `0x8001CA88`. The accepted proof inserts one centered line before those menu calls at `y=114`.

Runtime testing corrected one earlier static assumption: mixed/lowercase text is not reliable with the exact title-font/style configuration copied from START/OPTIONS. The lowercase `Sub-Zero Edition` proof rendered corrupted/missing glyphs. The accepted behavior therefore uses **uppercase only**.

The hyphen byte in `SUB-ZERO` renders more like a colon with this title-font configuration. That presentation quirk is accepted for the current temporary freeform edition field.

### Production integration

The Candidate-B image, final visual spacing, and configurable edition-name path are **Runtime-confirmed** on the tested production route.

The accepted production implementation is data-only:

- no title executable wrapper;
- no title-menu code hook; stock ROM `0x79C24..0x79C2B` remains unchanged;
- uppercase `<NAME> EDITION` is rasterized into the Candidate-B 320x240 CI8 title at patch time;
- 15 Candidate-B-unused palette indices are reserved for grayscale antialias levels, with guarded stock words before replacement;
- compressed file `0x5E` is relocated from ROM `0xF90000` within a guarded `0x31000`-byte high-ROM allocation;
- the temporary browser/CLI field defaults to `SUB-ZERO`, accepts at most 12 name characters, normalizes to uppercase, and supports A-Z, 0-9, spaces and hyphens before appending ` EDITION`.

Runtime evidence:

- `MKMSZR_title-branding_full-pipeline-proof_v02.z64`, SHA-256 `8f86e6f50fcc068c66986681a57b18f9882cf8f1779376222a46b76f10b56382`, default `SUB-ZERO`; file `0x5E` compressed length `0x3017F`, end-exclusive ROM `0xFC017F`. User confirmed title rendering and title -> gameplay transition.
- `MKMSZR_title-branding_sektor-full-pipeline-proof_v03.z64`, SHA-256 `4401dc0ebfce1eb16e6c0b4eb1178dd2605e79a10c1a280cd7caa6307ca21c65`, non-default `SEKTOR`; file `0x5E` compressed length `0x3014F`, end-exclusive ROM `0xFC014F`. User confirmed the configurable subtitle and normal gameplay startup.

The old PR #41 wrapper at ROM `0x9ADE0` / VA `0x8009A1E0` remains **Rejected / failed** because the production pickup-persistence composition already owns that region. The browser's guard failure was the negative control that exposed the overlap. PR #42 merged the corrected no-cave implementation as `cebfe39c92e96590efbf571ee338467e2b7dc368`.

## Pickup presentation descriptors

| Descriptor | ROM | Count/use |
|---:|---:|---|
| `0x800B1BAC` | `0xB27AC` | Potion, 16 entries |
| `0x800B1BD0` | `0xB27D0` | Generic A/crystals |
| `0x800B1D18` | `0xB2918` | Generic B/keys and icons, 14 entries |
| `0x800B1D38` | `0xB2938` | Jar/item presentation |

The resource selector in a pickup record is stage-local; its presentation descriptor alone does not import model data.

## Failed approaches and open work

- Direct framebuffer drawing was unstable and is rejected.
- Searching for one universal sprite API produced context-dependent candidates, not a safe abstraction.
- An inline wrapper that allocates and submits multiple nodes works; an over-generalized helper layer did not.
- General textured-image rendering remains unresolved.
- The Temple XP proof currently reuses a pale blue-grey Herbs-like model. Desired final art is a bright-blue body with bronze handle and still needs a production resource path.


## 1.0 randomizer HUD requirement

The legacy Lua overlay is the behavioral reference for the information a player needs while hunting a seed. It displayed:

- progression/power requirement;
- inventory page number;
- current-stage checks collected / total;
- key-item progress by stage;
- temporary `Picked up: <item>` feedback.

The native product currently implements only `BOX n OF 4`. 1.0 requires a native randomizer HUD that exposes equivalent useful run-state information. Exact visual parity with the emulator overlay is not required, but the gameplay information is.

The runtime-confirmed native text path at `0x80073E74` is the preferred basis for text elements. Geometric key-progress icons may use native render nodes only after a bounded proof; a text-first representation is acceptable if it conveys the same state reliably.


## Toasty presentation target

The intended Toasty feature is now split into independently testable presentation and audio pieces.

**Static-confirmed donor behavior:** MKT's `forden_peek` creates the genuine 97x100 `TOASTY` image with its 64-color `TOASTY_P` palette, slides it in from the right for 6 ticks, stops it for `0x20` ticks while playing the Toasty voice, reverses horizontal velocity, slides it out for `0x10` ticks, then deletes it. The donor `randper(40)` gate is 40/1000 = 4%, approximately one qualifying event in 25.

**Runtime-confirmed audio:** Toasty audio proof v03 reproduces the intended retail voice and the user reported it as perfect. Audio is considered solved for this workstream and must remain untouched while the visual path is isolated. See [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer).

**Pending:** the remaining textured screen-space/object binding for the Toasty image. General textured-image rendering is still not claimed as solved until that bounded proof succeeds; the already runtime-confirmed audio v03 is not part of these visual diagnostics.


### Toasty visual-only proof v01

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


### Toasty visual diagnostic v11 — independent extra fixed slot

**Implementation/static-confirmed; runtime pending manual validation.**

v11 keeps the runtime-confirmed v10 renderer/clone behavior but introduces one new texture-lifecycle variable: an additional fixed HUD texture slot `0x17`.

Immediately after stock slot `0x13` has been initialized, a 48-byte trampoline in the final unused bytes of the same standalone proof cave:
1. reads the exact width/height from the already-initialized slot-`0x13` record;
2. reuses the same decoded source pointer;
3. calls stock HUD slot initializer `0x8001BF70` once for new slot `0x17`;
4. reproduces the two displaced stock instructions and resumes normal HUD initialization.

The stock HUD remains on its original slots. The shifted clone now binds only to slot `0x17`.

No custom Toasty pixels, file-ID load, dynamic allocator, palette replacement, `0x80073CEC`, text diagnostic, audio, RNG, or trigger are present.

Expected result: the normal HUD stays intact and the shifted clone still looks like the v10 equals-sign-like fragment. Success would prove that MKMSZR can own an independent gameplay-HUD texture slot before custom Toasty content is introduced.
