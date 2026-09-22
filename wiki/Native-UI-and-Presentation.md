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

**Static-confirmed on the clean USA Rev. 0 ROM.** The normal title controller is `0x80078C40`. Its title artwork is a six-tile indexed image submitted through the context-specific `0x80073CEC -> 0x8001E578` family. Earlier runtime instrumentation of that family visibly duplicated the title logo while leaving the `START` / `OPTIONS` menu text and cursor untouched, so the static split below agrees with runtime evidence.

The six title resources are drawn with palette descriptor `0x800B2760` (ROM `0xB3360`, 256 BGR/RGBA5551-style entries) at these fixed positions:

| Resource | Size | Screen origin | File-0x5E decoded record |
|---:|---:|---:|---:|
| `0x3C6` | 120x120 | `(0,0)` | `+0x3B780` |
| `0x3C7` | 100x120 | `(120,0)` | `+0x3EFCC` |
| `0x3C8` | 100x120 | `(220,0)` | `+0x41EB8` |
| `0x3C9` | 120x120 | `(0,120)` | `+0x44DA4` |
| `0x3CA` | 100x120 | `(120,120)` | `+0x485F0` |
| `0x3CB` | 100x120 | `(220,120)` | `+0x4B4DC` |

Together they form one exact 320x240 indexed composite. The stock visible logo occupies approximately `x=19..297`, `y=71..145`; the rest is black/transparent-looking background. The six direct palette loads in the executable are the only direct code references found to `0x800B2760`.

The tiles live in global file ID `0x5E`. Its clean-ROM file-table entry points to compressed ROM `0x4E3060..0x51243F` (end-exclusive `0x512440`), flag `1`; the package expands to exactly `0x61494` bytes. The native loader uses the game's LZW-style package decompressor before parsing the image archive. Static decoding reproduced the full package and allowed lossless extraction of the six indexed title tiles and the complete stock title composite without emulator capture.

Immediately after the six image submissions, the controller draws `START` at `(160,160)` and `OPTIONS` at `(160,180)` through frontend text renderer `0x8001CA88`. Static inspection of that renderer confirms mappings for uppercase A-Z, lowercase a-z, digits, spaces, hyphen and the punctuation needed by `Sub-Zero Edition`. Its centered-title calling form therefore provides a strong static basis for a build-selected `<character> Edition` line.

**Implementation direction, pending runtime proof:** keep the six-tile geometry/layout stable and modify the 320x240 indexed composite offline: move the existing Mortal Kombat Mythologies/Sub-Zero artwork upward inside the composite and add the new `RANDOMIZER` graphic beneath it. Quantizing the added graphic to the existing 256-color title palette avoids changing palette behavior. Add the character-specific edition line through `0x8001CA88` between the final tile submission and the existing START/OPTIONS draws. A wrapper at the final `0x3CB` submission site is a clean hook candidate because it can reproduce the displaced image draw, render the edition line, return, and then let vanilla START/OPTIONS execute unchanged.

Do not yet treat the wrapper as production-ready: current permanent caves are already composed among bootstrap, persistence, selector and inventory systems, so code/string storage must receive an explicit non-conflicting allocation and a guarded disposable title proof before pipeline integration. Repacking or relocating modified file `0x5E` also requires its own guarded allocation/loader proof; static feasibility is not runtime confirmation.

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
