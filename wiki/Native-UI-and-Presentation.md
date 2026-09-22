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

### Production integration correction

The Candidate-B image itself and the accepted uppercase edition-line placement remain **Runtime-confirmed** presentation results. The first PR #41 browser/CLI implementation is **Rejected / failed** for composition, not for appearance.

It placed an edition-text wrapper at ROM `0x9ADE0` / VA `0x8009A1E0`. That address is not free after the current production pipeline has installed pickup persistence: the restore trampoline begins at `0x9ADD8`, the capture helper at `0x9ADE8`, descriptor data at `0x9AEC0`, Fire translation at `0x9AEE8`, and the relocated selector mapper at `0x9AEFC`. The browser correctly failed the wrapper's zero-byte guard and refused to overwrite this owned code/data.

The earlier title-only production-layout proof did not execute the full patch pipeline, so its successful title rendering did not establish composition safety. This supersedes the prior claim that `0x9ADE0` was an unused bootstrap tail.

The high-ROM compressed file-`0x5E` relocation beginning at `0xF90000` is not implicated by this failure. The corrective implementation under validation bakes the configurable uppercase `<NAME> EDITION` line directly into the title's CI8 pixels at patch time, removing the title code hook and executable-cave requirement entirely. The live webapp temporarily omits title branding until that full-pipeline proof is manually validated.

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

**Static-confirmed audio feasibility:** the retail MKT Toasty voice is a non-looping `0x2A54`-byte N64 ADPCM sample and MKMSZ uses a compatible native sound-bank grammar/playback family. A no-growth in-place sound proof is available through dormant raw sound ID 550. See [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer).

**Pending:** runtime validation of the imported sound, then the remaining textured screen-space/object binding for the 97x100 image. General textured-image rendering is still not claimed as solved until that bounded proof succeeds.
