# Presentation and branding

> **Scope:** This page is the canonical owner for the legal/boot screen presentation, title-screen art and branding layout, configurable edition text, boot phrase presentation, and visual acceptance evidence.
>
> File `0x5E` packaging/loading mechanics belong to [Resource and overlay system](ROM-Overlay-and-Resource-Map). Literal ROM allocation ownership belongs to [Memory and allocation map](Memory-and-Allocation-Map). Gameplay HUD/text/render-node behavior belongs to [Native HUD and UI](Native-HUD-and-UI).

## Current conclusion

The redesigned legal/boot screen and the data-only Candidate-B title composition are **Runtime-confirmed** on their documented production routes. On 2026-09-27 the user also visually accepted a bounded 16-color title proof. The shared browser/CLI implementation now constrains Candidate B to that same 16-color visual budget while preserving the native CI8 storage/render path and configurable uppercase edition text.

The accepted title implementation is data-only: no title executable wrapper or title-menu code hook is required. The earlier executable-wrapper composition is **Rejected / failed** because it overlapped production pickup-persistence ownership.

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

## Boot phrase presentation

The seeded boot phrase occupies the two joke lines in the legal-screen layout above. This page owns its placement and visual presentation. Seed-domain selection and deterministic namespace behavior belong to [Web patcher and product behavior](Web-Patcher-and-Product); the browser intentionally does not reveal the selected boot phrase in its completion panel so it remains an in-game discovery.

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

### File 0x5E packaging boundary

The title art lives in global file ID `0x5E`. File-table/loading and compression/package mechanics are canonical in [Resource and overlay system](ROM-Overlay-and-Resource-Map), while literal high-ROM allocation ownership is canonical in [Memory and allocation map](Memory-and-Allocation-Map). This page owns the resulting branding design, generated art behavior, and visual acceptance rather than duplicating those mechanics.

### Accepted Randomizer title proof

The accepted image direction is the icy-metallic **MORTAL KOMBAT MYTHOLOGIES / RANDOMIZER** Candidate B. The original production path used the exact native 320x240 CI8 image with the corrected stock BGR555 palette. The user runtime-tested that art and reported it looks awesome. The later 16-color proof keeps the native CI8 path but limits visible title art to one near-black background plus 15 icy-blue BGR555 entries; the user reported that this reduced-color version still looks very good and requested it for production.

The final standalone title proof is:

- `MKMSZR_title-screen_candidate-b_with-edition_proof_v05.z64`
- SHA-256 `3f98e2d73fc66203a333d2b6a9f0861cc528201804e96349c2dce376f8f189d0`
- edition text centered at `x=160`, `y=114`
- displayed string `SUB-ZERO EDITION`

This is **Runtime-confirmed** for the title-screen route shown by the user. The proof's title art and final edition placement are accepted visually.

The proof itself is **not a production allocation**. It used a raw file-`0x5E` relocation overlapping the production payload region and used the bootstrap cave beginning at ROM `0x9AD84`, which production already owns. Those proof locations must not be copied into the browser/CLI pipeline.

### Accepted 16-color title update (2026-09-27)

The bounded proof `MKMSZR_title-16color_title-proof_v01.z64` is **Runtime-confirmed for visual acceptance only**: the user reported that the reduced-color title still looks very good. The proof preserved the native CI8 renderer and reduced the image to a 16-entry visual palette rather than changing the resource grammar to true packed CI4.

The production implementation keeps that conservative renderer contract:

- Candidate B is Floyd-Steinberg quantized at build time into exactly 16 CI8 indices;
- palette index `0xFF` remains the stock near-black background;
- the existing 15 edition-text indices become the dark-to-light icy-blue art/text ramp, so configurable `<NAME> EDITION` shares the same palette instead of adding colors;
- no title code hook, renderer change, or CI4 record-format assumption is introduced;
- the default `SUB-ZERO` generated file-`0x5E` package is about `0x2E5D4` bytes with the shared implementation, versus `0x3017F` for the earlier high-color production title: approximately `0x1BAB` = 7,083 bytes smaller.

The full `0x31000` high-ROM title allocation remains reserved for now. The smaller generated package therefore creates reclaimable headroom but does not silently transfer ownership of the tail to another feature.

### Edition text

Immediately after the six image submissions, vanilla draws `START` at `(160,160)` and `OPTIONS` at `(160,180)` through frontend text renderer `0x8001CA88`. The accepted proof inserts one centered line before those menu calls at `y=114`.

Runtime testing corrected one earlier static assumption: mixed/lowercase text is not reliable with the exact title-font/style configuration copied from START/OPTIONS. The lowercase `Sub-Zero Edition` proof rendered corrupted/missing glyphs. The accepted behavior therefore uses **uppercase only**.

The hyphen byte in `SUB-ZERO` renders more like a colon with this title-font configuration. That presentation quirk is accepted for the current temporary freeform edition field.

### Production integration

The Candidate-B image, final visual spacing, and configurable edition-name path are **Runtime-confirmed** on the tested production route.

The accepted production implementation is data-only:

- no title executable wrapper;
- no title-menu code hook; stock title `START` setup at ROM `0x00079C24..0x00079C2B` / VA `0x80079024..0x8007902B` remains unchanged;
- uppercase `<NAME> EDITION` is rasterized into the Candidate-B 320x240 CI8 title at patch time;
- the 15 Candidate-B-unused palette indices are repurposed as the shared icy-blue 16-color art/edition ramp, with guarded stock words before replacement;
- compressed file `0x5E` is relocated from ROM `0xF90000` within a guarded `0x31000`-byte high-ROM allocation;
- the temporary browser/CLI field defaults to `SUB-ZERO`, accepts at most 12 name characters, normalizes to uppercase, and supports A-Z, 0-9, spaces and hyphens before appending ` EDITION`.

Runtime evidence:

- `MKMSZR_title-branding_full-pipeline-proof_v02.z64`, SHA-256 `8f86e6f50fcc068c66986681a57b18f9882cf8f1779376222a46b76f10b56382`, default `SUB-ZERO`; file `0x5E` compressed length `0x3017F`, end-exclusive ROM `0xFC017F`. User confirmed title rendering and title -> gameplay transition.
- `MKMSZR_title-branding_sektor-full-pipeline-proof_v03.z64`, SHA-256 `4401dc0ebfce1eb16e6c0b4eb1178dd2605e79a10c1a280cd7caa6307ca21c65`, non-default `SEKTOR`; file `0x5E` compressed length `0x3014F`, end-exclusive ROM `0xFC014F`. User confirmed the configurable subtitle and normal gameplay startup.

The old PR #41 wrapper at ROM `0x9ADE0` / VA `0x8009A1E0` remains **Rejected / failed** because the production pickup-persistence composition already owns that region. The browser's guard failure was the negative control that exposed the overlap. PR #42 merged the corrected no-cave implementation as `cebfe39c92e96590efbf571ee338467e2b7dc368`.

## Visual acceptance evidence

| Presentation | Evidence | Accepted observation / limit |
|---|---|---|
| Redesigned 2026 legal screen | **Runtime-confirmed** | Layout, configurable edition line, seeded joke placement, `BY SMEAG`, and `NOT LICENSED BY NINTENDO` were accepted in-game; non-default `SEKTOR EDITION` is also full-pipeline Implementation/CI-confirmed |
| Candidate-B standalone title proof v05 | **Runtime-confirmed** | Icy-metallic `MORTAL KOMBAT MYTHOLOGIES / RANDOMIZER` art and centered `SUB-ZERO EDITION` placement were visually accepted; proof allocations were not production-safe |
| Full-pipeline title proof v02 | **Runtime-confirmed** | Default `SUB-ZERO` title rendered correctly and transitioned normally into gameplay |
| Full-pipeline Sektor title proof v03 | **Runtime-confirmed** | Non-default `SEKTOR` edition rendered correctly and normal gameplay startup continued |
| Lowercase/free-mixed title-font experiment | **Rejected / failed** | Mixed/lowercase glyph rendering was unreliable with the tested title font/style; current edition presentation is uppercase only |
| PR #41 executable title wrapper | **Rejected / failed** | Guard failure exposed overlap with production pickup-persistence ownership; the accepted PR #42 path removed the cave requirement |

## Related canonical owners

- [Web patcher and product behavior](Web-Patcher-and-Product) — user-facing title-character configuration and deterministic boot-phrase namespace.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — global file `0x5E` package/loading mechanics.
- [Memory and allocation map](Memory-and-Allocation-Map) — production title-package and adjacent ROM allocation ownership.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded presentation patch sites.
- [Stage flow and selector](Stage-Flow-and-Selector) — post-legal logo bypass and title/selector routing behavior.
- [Native HUD and UI](Native-HUD-and-UI) — gameplay HUD/text/render-node behavior.
