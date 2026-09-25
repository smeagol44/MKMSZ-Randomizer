# MKT fighter asset translation

> **Scope:** This page owns stable donor-to-target fighter-asset translation for the MKT/Sektor work: donor frame descriptors, dimensions and anchors, donor image formats, palette conversion/binding, MKMSZ Type-5 generation, and fighter-resource storage/packing strategy.
>
> It does **not** own the normative MKMSZ Type-5 grammar, which remains in [Data structures and encodings](Data-Structures-and-Encodings); animation-slot mapping/current coverage, which remains in [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping); or the full version-by-version proof diary, which is canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).

## Current conclusion

The fighter-art path is a **translation pipeline**, not a binary transplant:

```text
donor frame descriptor + donor compressed/raw pixels + donor palette
-> decode donor representation offline
-> normalize row pitch, dimensions, anchors, and palette indices
-> generate MKMSZ-native indexed target buffers
-> encode those buffers as native MKMSZ Type-5
-> rebuild target shape/descriptor pointers for file 0x87
```

The stable compatibility conclusions are:

- MKT fighter frame structure is conceptually compatible with MKMSZ, but pointer bases and dimension ordering are not byte-compatible and must be rebuilt.
- MKT N64 codecs `16`, `22`, and `24`, plus the codec-`15` mechanical-arm path, are donor formats only. Their bytes are decoded offline; MKMSZ does not consume those streams directly. Codec `16` is now losslessly decoded for the Sektor straight-missile horizontal rocket frames.
- Four-byte row pitch is part of both the proven imported N64 fighter path and preserved Midway WIMP raw-image storage. Visible width and stored row pitch must be kept distinct.
- Donor palettes must be translated into MKMSZ source-palette semantics before rendering. Palette binding is a resource-lifetime problem as well as a color-conversion problem.
- Generated native Type-5 is the accepted target storage format for imported fighter art. Its format contract remains canonical in [Data structures and encodings](Data-Structures-and-Encodings).
- Fighter-resource file size is gameplay-sensitive. Proof footprints establish bounded working/failing envelopes, not a universal production-safe threshold.

## Evidence boundary

The primary retail donor/target pair for the current compatibility work is:

| Role | Image | Identity |
|---|---|---|
| Donor | MKT USA Rev. 2 N64 | SHA-256 `30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb` |
| Target | MKMSZ USA Rev. 0 N64 | SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6` |

Supplemental evidence also uses unpacked USA PS1 MKT resources and preserved Midway MK3/WIMP source assets. Those are donor/reference sources only; their addresses and binary layouts do not transfer to MKMSZ N64 without an explicit conversion.

[PS1 research](PS1-Research) remains the owner for **MKMSZ PS1 platform facts**. The PS1 material on this page is specifically the MKT PS1 robot bank used as supplemental fighter-asset evidence.

## Donor fighter descriptors, dimensions, and anchors

### Retail MKT N64 descriptor compatibility

The retail MKT fighter path is conceptually:

```text
heap-relative shape list
-> per-frame descriptor
-> donor texture offset + geometry/anchor metadata
```

The target resource can preserve the semantic frame/anchor result, but donor offsets must be rebuilt relative to the MKMSZ resource.

A concrete male-ninja example is the Reverse Elbow return sequence:

Retail provenance for that sequence is exact: male-ninja table 2 begins at donor heap offset `+0x168`; slot `0x0B` points to heap offset `+0x664`; and the retail script occupies ROM `0x629F04..0x629F1F`. Its visual order is `SCCOMBO10 -> SCCOMBO11 -> SCCOMBO12 -> 0 -> SCCOMBO11 -> SCCOMBO10 -> 0`.

| Frame | Record ROM | Visible geometry | Donor anchor | Donor texture offset |
|---|---:|---:|---:|---:|
| `SCCOMBO10` | `0x62BB40..0x62BB53` | `42x95` | `(+15,-19)` | `0x282C4` |
| `SCCOMBO11` | `0x62BB54..0x62BB67` | `50x102` | `(+15,-13)` | `0x28724` |
| `SCCOMBO12` | `0x62BB68..0x62BB7B` | `82x106` | `(+25,-8)` | `0x28BE4` |

MKT N64 was built with `ENDIAN=1`; its packed `XYTYPE` is physically `ypos, xpos`. For size words this means donor **Y:X**. MKMSZ frame setup uses the first size halfword as X/width and the second as Y/height, so conversion must swap the donor size halfwords to target **X:Y**.

For `SCCOMBO10`, packed size word `0x005F002A` is therefore **height 95, width 42**, not 95x42 target ordering.

The correction is independently supported by the decoded SCCOMBO stream sizes:

- `SCCOMBO10`: `0x1054 = 95 * align4(42)`;
- `SCCOMBO11`: `0x14B8 = 102 * align4(50)`;
- `SCCOMBO12`: `0x22C8 = 106 * align4(82)`.

### Backing dimensions versus visible dimensions

The target fighter descriptor owns the visible dimensions and anchors. The target Type-5 wrapper owns decode/backing dimensions. They need not be identical.

The first native Type-5 Sektor proof retained a visible `55x113` descriptor while encoding a transparently padded `56x114` backing buffer. That separation is now part of the asset adapter contract: pad storage for decoder geometry without silently changing the visible fighter box.

### Preserved WIMP/MK3 calibration for cut Run poses

After the PS1 MKT pixel path was rejected, preserved Midway `video/supermk3/ROBO8.IMG` became the clean supplemental source for `RBRUN1..RBRUN12`. Its source images are larger than the N64 retail assets, so they require a calibrated conversion rather than direct copying.

For the retained robot Run/Stance/Air-Punch comparisons used in this work, the bounded conversion is approximately:

- target width = `round(source_width * 0.80)`;
- target height = `round(source_height * 0.85)`;
- target X anchor follows the same `0.80` reduction on the checked pairs;
- target Y anchor is calibrated from retained N64 descriptors.

This is **not** a universal MKT/MK3 scaling law. It is a checked conversion rule for the current robot-source family.

The six N64-cut even Run poses used by the runtime-confirmed v58 composition are:

| Pose | WIMP source | Derived target | Target anchor |
|---|---:|---:|---:|
| `RBRUN2` | `96x131` | `77x111` | `(+43,-8)` |
| `RBRUN4` | `63x127` | `50x108` | `(+17,-12)` |
| `RBRUN6` | `89x131` | `71x111` | `(+29,-8)` |
| `RBRUN8` | `108x135` | `86x115` | `(+46,-8)` |
| `RBRUN10` | `74x131` | `59x111` | `(+26,-9)` |
| `RBRUN12` | `81x137` | `65x116` | `(+24,-4)` |

The v58 runtime result validates the composed Run route using these target descriptors; it does not turn this calibration into a general rule for unrelated source banks.

## Donor codecs and conversion boundaries

### MKT N64 codecs 22 and 24

Retail MKT `SCCOMBO10/11/12` use donor codecs `22/22/24`. They decode deterministically to 5-bit palette indices `0..31` using the male-ninja `0x100`-byte dictionary at ROM `0x6B8550..0x6B864F`.

| Frame | Donor stream ROM | Codec | Decoded bytes |
|---|---:|---:|---:|
| `SCCOMBO10` | `0x651B64..0x651FC3` | `22` | `0x1054` |
| `SCCOMBO11` | `0x651FC4..0x652482` | `22` | `0x14B8` |
| `SCCOMBO12` | `0x652484..0x652A0A` | `24` | `0x22C8` |

Decoded-buffer SHA-256 identities from the exact donor decoder are:

- `SCCOMBO10`: `62cecad0f400fc6b88cf3236c83000ed1fa7f6ec42c5eaadb55dfaca8e44b3ff`;
- `SCCOMBO11`: `9ce4770a2062d8f990e602c69e367143a1a088c7bba26780b344ca36fc7d1ea1`;
- `SCCOMBO12`: `d8c7104ac6bbe31e494ef5b06d37c32f5b565b1dc88dbc92ff4ea7939957074c`.

The decoded buffers are row-major with `align4(visible_width)` source stride. For `SCCOMBO10`, for example, each 42-pixel visible row occupies 44 bytes. Removing the two padding bytes per row produces the deterministic staircase/shear failure; preserving the 44-byte pitch renders the coherent donor fighter.

The accepted boundary is therefore:

```text
MKT codec 22/24 bytes
-> exact donor decoder
-> aligned indexed-pixel buffer
-> palette translation
-> MKMSZ Type-5 generation
```

Direct donor-stream copying is not supported.

A prior raw-wrapper attempt wrote decoded byte lengths such as `0x00000FEA` or `0x00001054` into the MKMSZ wrapper header. That is **Rejected / failed**: the target decoder reads the compression type from header byte `+3`, masked with `0x3F`, so those words leave type 0 instead of describing raw length.

### First genuine MKT fighter import proof

The first successful runtime rendering of a genuine retail MKT fighter frame inside MKMSZ was the SCCOMBO10 A1.7/v08 proof:

- file: `MKMSZR_mkt-scc10-import_global_proof_v08.z64`;
- SHA-256: `1ea40452cdf6e8866b48544fc57f27b065dace75fa0416d52fb4987db61f936d`;
- CRC1/CRC2: `70135E41 / BB4C161F`.

**Runtime-confirmed:** the proof rendered the coherent 42x95 SCCOMBO10 donor frame with the aligned 44-byte source row pitch and isolated donor palette, then restored stock Sub-Zero correctly. This is asset/codec compatibility evidence, not Sektor takeover chronology or production integration.

### MKT codec 15 and composite assets

Sektor's mechanical-arm throw uses a donor codec-`15` arm path plus holder/body art. The current adapter decodes the arm sprites offline using the donor `uncompress_8` grammar, composites them with `RBSHOLDER4` using donor anchors, and encodes the flattened result as ordinary MKMSZ Type-5 frames.

The important compatibility boundary is structural: MKMSZ does not import the incompatible MKT slave-animation ABI merely to display the composite. The donor multi-object presentation can be flattened into a target-native fighter frame when target gameplay timing must remain stock.

### MKT codec 16 and Sektor straight-missile assets

**Static-confirmed.** Retail MKT's image decompression dispatcher masks the top header byte with `0x3F`; codec `16` dispatches to the compact four-bit/RLE decoder at donor VA `0x80082820`. The decoder grammar is:

- header low 24 bits: decoded byte count;
- command bit 7 set: zero run of `(cmd & 0x7F) + 7`;
- high nibble 0: low nibble is the palette index and the next byte is the run count;
- high nibble 1..6: repeat the low-nibble palette index that many times;
- high nibble 7: literal run of `low_nibble + 3` pixels, packed two four-bit indices per following byte.

Sektor's straight missile uses the **horizontal rocket pair** selected by donor animation part 4 rather than the full directional rocket family:

| Donor shape | Visible geometry | Anchor | Image | Codec | Exact donor decode |
|---:|---:|---:|---:|---:|---:|
| robot `+0x2668` / `ROCKETD1` | `39x9` | `(+26,+3)` | `+0x49700` | 16 | 360 bytes = `9 * align4(39)`; 130 codec bytes including header |
| robot `+0x267C` / `ROCKETD2` | `42x10` | `(+30,+4)` | `+0x49784` | 16 | 440 bytes = `10 * align4(42)`; 141 codec bytes including header |

Both decode losslessly to palette indices `0..15`. For MKMSZ Type-5 generation the odd-height `39x9` image uses a transparently padded even backing height while retaining its visible descriptor.

The donor has a dedicated `ROCKET_P` palette. **Retail Rev. 2 static correction:** exact donor ROM `0xBC3AC` is the `ROCKET_P` record (`u32 count = 16`), followed at `0xBC3B0` by `07C0 F7BD F7A7 BDEF 9CE7 8C63 5AD7 318D F5C1 F381 F1C1 D801 9801 7001 6001 4001`; this uniquely matches the current robot-source `ROCKET_P` definition and yields the gray body plus red/orange/yellow exhaust. The earlier v70 builder constant beginning `001F 7FFF ...` is therefore **superseded as a ROCKET_P identity**. v70/v75 also remapped rocket indices into resident Sektor TLUT entries `18,19,21,22,23,24,25`, producing a grayscale approximation. v86 Runtime-confirms that acquiring the resident source improves coherence but still cannot reproduce the donor. A faithful adapter needs a projectile-local converted retail `ROCKET_P` source together with rocket pixels retaining donor indices `0..15`, plus balanced palette lifetime.

**Projectile palette, frame and texture-slot ownership (v75–v89 reconciliation):** The donor rocket pixels are indexed; their color depends on the **projectile actor's** selector, not the player's source data merely being resident in file `0x87`. Player type-4 source `file-0x87 +0x4584C` is acquired through `0x8001C528`, returning a dynamic handle; actor `+0x9E` stores handle minus `0x80`. The stock projectile token instead acquires the fixed Ice source at `0x800B1A24`. Selector zero maps to handle `0x80`, not the player palette. Hence v81/v82/v84 do not establish a coherent donor palette bind. v82's active `+0x80` rebind selects the same zero slot and cannot change the source. v86 instead acquires the resident Sektor source dynamically through `0x8001C528` and Runtime-confirms a materially more coherent rocket, establishing that projectile-local palette-source ownership matters. However, the compact missile asset itself was deliberately pre-remapped: donor rocket indices `1..15` map into resident Sektor TLUT indices `{18,19,21,22,23,24,25}`, which are grayscale entries in the Runtime-confirmed Sektor source palette. Therefore v86 is not a donor-faithful palette proof; it validates the ownership mechanism while exposing the loss introduced by the earlier resident-TLUT approximation. v87 Runtime-confirms that donor-faithful asset pair: exact ROCKETD1 indices plus dynamically acquired converted retail ROCKET_P render the flying missile with the expected gray body and red/orange/yellow exhaust. Its remaining one-frame corruption is not an asset-conversion failure: the earlier Ice-derived projectile descriptor is still rendered once, but now through ROCKET_P, producing the glitched Sektor-like frame. v88 keeps the validated v87 asset/palette pair and adds an early contextual rocket advance while preserving the dynamic selector, but Runtime still shows one frame of corrupted Sektor-like texture. v89 adds synchronous native preparation of the finalized projectile texture slot before actor publication and Runtime-confirms that the corrupt frame disappears while the donor-faithful missile remains. The adapter therefore has three distinct presentation obligations: preserve donor image indices/content, own the correct projectile-local palette, and make the finalized texture-slot pixels resident before first publication.

The rocket entry `+0x4E6E4` resolves to descriptor `+0x4E6EC` and native Type-5 image `+0x4E6F8`; Ice-derived entry `+0x34A58` resolves to `+0x34A60`. Their descriptor preceding words are zero. On initialized actors both a repeated entry and an entry change mark `+0xFA` dirty for later record decode/upload. v83's early raw rocket bind is overwritten by the parent's next stock Ice frame; v84 instead moves the controller cursor to the rocket loop before that same parent advance. In normal v75 the rocket is bound by the child after the animation timer expires. The relevant difference is frame schedule plus separately acquired palette ownership, not a supposed missing same-shape rebuild. The host decode/queue path belongs to [Player actions and special moves](Player-Actions-and-Special-Moves).

### Chest-open launch art

The MKT robot-family secondary animation slot 0 is the chest-open family. The first audited launch shapes are:

| Donor shape | Visible geometry | Anchor | Codec |
|---:|---:|---:|---:|
| robot `+0x29A0` / `RBCHEST1` | `46x115` | `(+19,-5)` | 22 |
| robot `+0x29B4` / `RBCHEST2A` | `47x113` | `(+20,-7)` | 22 |

The fully-open donor visual is multipart: `RBCHEST2A` is accompanied by `RBCHEST2B` at robot `+0x29C8`. The first missile proofs intentionally reduced the runtime gate to one flattened/representative fully-open chest pose rather than importing the complete open/close choreography. Donor animation/lifecycle semantics remain owned by [MKT adapter primitives](MKT-Adapter-Primitives).

### v63-v70 missile storage audit

The v59/v62 takeover corpus contains 158 generated frames, 64 entropy models, 40,737 shared patterns, a `0x335A9` table/dictionary, and file `0x87 = 0x4E3FC`.

An exact dry pack of **four** new lossless frames — two chest codec-22 poses plus both horizontal codec-16 missile poses — produced:
- 1,485 extra `2x4` blocks;
- 604 genuinely new shared patterns;
- dictionary growth `0xBCC`;
- best-fit existing entropy group 56;
- stream delta `0x560`;
- predicted file `0x87 = 0x4F5A8`.

That is `0x11AC` larger than v59/v62 and `0x1064` above the Runtime-confirmed v49 Fortress-working footprint `0x4E544`. It did **not** prove that `0x4F5A8` fails; it established that naive lossless four-frame growth leaves the known working envelope.

The compact proof therefore reduced the first runtime requirement to **one fully-open chest pose + one horizontal rocket pose** and quantized those two target buffers only against the existing 40,737-pattern dictionary with exact transparency masks. v64 reaches file `0x87 = 0x4E788`, only `0x244` above the v49 working footprint. v69/v70 then refine the code/lifecycle side while retaining the compact asset strategy. Fortress/Prison allocation boundaries were not revalidated for v64-v70, so these larger footprints remain **proof-specific**, not new safe-size ceilings.


### Preserved WIMP raw images

Midway WIMP raw 8-bit fighter images use the header's visible `xsize`, but each stored source row advances by:

```text
source_stride = align4(xsize)
```

The v57 extractor incorrectly treated storage as tightly packed `xsize * ysize`, causing diagonal/slashed frames whenever width was not already divisible by four. The stride-corrected v58 path is Runtime-confirmed for ordinary Run.

`ROBO8.IMG` also provides `ROBO_P`, a 64-color RGB555 source palette. The current robot conversion reduces it deterministically into the already-proven 32-color N64 Sektor target palette rather than adding a separate runtime palette system.

## PS1 MKT supplemental conversion history

PS1 MKT is useful as an **independent sequence/descriptor reference**, not as an N64 byte/layout oracle.

Relevant donor files are:

- `CODE/ROBOT.BIN` — robot animation tables/scripts;
- `CHARS1/ROBOT.DAT` — ordinary robot fighter graphics/resource bank;
- `CHARS2/ROBOTBQ.DAT` and `CHARS3/ROBOFAT.DAT` — supplemental robot banks.

The PS1 robot primary Run entry at slot `0x46` points to `ROBOT.BIN +0x140C` and preserves twelve distinct Run poses. Its twelve 12-byte frame descriptors are consecutive at `ROBOT.DAT +0xA6C..+0xAFB`. That sequence remains useful evidence that the six even Run poses existed even though the N64 retail robot set cut them.

The PS1 Throw entry is also present at primary slot `0x23 -> ROBOT.BIN +0x112C` and retains the holder/slave mechanical-arm structure. It is supplemental structural evidence only; the PS1 binary/layout is not assumed compatible with MKMSZ N64.

The attempted PS1 pixel donor path used the platform-specific POVBQ representation: 12-byte descriptors, padded width, palette ID, shared table, a 6-bit model selector, seven normal symbols, and two transparent-run symbols. Two corrections are important to preserve:

1. The first importer omitted the four-pixel horizontal advance after each decoded `2x4` vector, collapsing rows into a four-column strip. The earlier v55 “18 supplemental patterns / lossless” conclusion was therefore invalid because both validation and encoding consumed the same malformed target buffers.
2. v56 fixed that output-cursor bug and independently matched the separate PS1 decoder, but the resulting full-body frames still rendered as speckled/checkerboard bodies. Re-rendering PS1 odd poses reproduced the same internal corruption before Type-5 packing.

The superseded packing measurements remain useful only as history of the failed source interpretation:

| Proof | Supplemental packing result | Interpretation |
|---|---|---|
| v55 | 18 supplemental `2x4` patterns; 40,595-pattern shared dictionary; 52 Type-5 models; reported zero RMSE / 100% exact opaque indices | **Rejected** because the target buffers themselves were the malformed four-column decode |
| v56 | 256 representative supplemental patterns; 40,833 total patterns; 64 Type-5 models; file `0x87 = 0x4E414`; ~4.504 RGB RMSE and 36.3% exact opaque indices with exact transparency masks | Packing measurement is valid only against the selected v56 buffers; those buffers are **Rejected** as faithful PS1 source images |

**Rejected / unresolved:** the current POVBQ interpretation of the PS1 robot Run bank is not an accepted pixel source for N64 fighter translation. Its VQ/codebook metrics must not be treated as image-quality evidence. PS1 MKT remains useful for sequence, descriptor, and cross-port reference only unless that source decode is independently resolved.

The replacement source for the missing even Run pixels is preserved Midway `ROBO8.IMG`, whose stride-corrected path is Runtime-confirmed in v58.

## Palette translation and binding

### Donor-to-target color conversion

MKT N64 fighter palettes are RGBA5551. MKMSZ source palettes are BGR555 words that the native upload path converts for hardware use.

The Reptile primary palette used by the SCCOMBO import is at retail MKT ROM `0xBE864..0xBE8A7`: a u32 count of 32 followed by 32 big-endian RGBA5551 colors.

The established conversion is:

```text
MKT RGBA5551
-> preserve the 5-bit RGB channels
-> reorder into MKMSZ BGR555 source words
-> donor alpha = 0 becomes source word 0
```

For isolated imported-frame work, the native target path is:

Static tracing observed native allocated palette handles in the `0x140..0x23F` family; that observed handle family is provenance for the isolated-binding proof, not a promise that every value in the range is generally allocatable.

```text
0x8001C528 palette find/allocate
-> actor +0x9E selector
-> 0x8001BDA0 frame setup / bind
-> actor +0x80 active handle
-> 0x8001C64C release
```

The source-to-hardware upload path is `0x8001D9B4..0x8001DA58`.

The earlier strategy of copying a donor palette directly over Sub-Zero's stock source palette is rejected for isolated imports because ordinary Sub-Zero frames inherit the donor colors.

### Sektor takeover palette

For the Sektor-first takeover, all imported Sektor images are 5-bpp and address indices `0..31`. The runtime-proven takeover architecture keeps the stock 64-entry player TLUT structure, replaces its lower 32 entries with the converted Sektor palette, leaves the upper 32 entries valid, and removes the dynamic donor-palette helper.

This resident-TLUT strategy is appropriate for a whole-character takeover. The temporary allocate/bind/release path above remains the safer model when donor and stock fighter palettes must coexist per actor/frame.

The later alternate-palette proof establishes an additional stable compatibility boundary: replacing only the normal player TLUT is insufficient when another reachable actor path reuses the transplanted 5-bpp pixels through a different source palette. The first visible `SCORPION` / fighter type `0x12` uses a Sub-Zero-family alternate palette, while the separate genuine Undead Scorpion/type-`0x11` resource is a different route. Because the transplanted Sektor pixels use only indices `0..31`, the relevant alternate TLUT also needs a compatible lower-32 mapping.

That first type-`0x12` route is **Runtime-confirmed** by the v60 proof. The durable adapter lesson is to inventory every reachable palette-binding path for a whole-character takeover and translate each required TLUT deliberately; one working normal-player palette does not prove arbitrary alternate/enemy palettes. Exact v60 ROM identities, proof offsets, byte-diff counts, and the bounded manual result remain canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).

### Accepted generic 16-color normalization direction

**Design-accepted 2026-09-25; bounded visual proof accepted by the user.** For the generic N64 MKT -> MKMSZ fighter importer, normalize donor fighter art to a **16-color indexed palette** by default. The Sektor 16-color proof was judged visually successful, so restoring a 32-color body palette is **not** a fidelity goal by itself.

This is an importer policy, not a claim that historical Sektor proofs used only 16 colors. The v53/v60 32-color resident-TLUT line remains valid runtime evidence for palette ownership and alternate-palette binding. The generic route should preserve those semantic lessons while quantizing/remapping the imported fighter body to 16 colors unless new technical evidence shows unacceptable quality, animation-specific palette breakage, collision with required effect/attachment colors, or another concrete incompatibility.

The 16-color decision also does **not** change the target storage contract: imported frames must still be emitted as valid MKMSZ-native Type-5 assets with correct dimensions, anchors, dictionary/model encoding, palette binding, and lifecycle ownership. Do not infer a new raw 4-bpp target format merely from the 16-color palette policy.

### Mechanical-arm palette

The flattened Sektor throw cannot interpret codec-15 arm indices through the body palette. The donor `MECARM_P` metal ramp is translated into resident Sektor TLUT indices as:

```text
1->17, 2->19, 3->20, 4->22, 5->24, 6->25, 7->26
```

This preserves the gray-metal arm appearance while keeping one resident target TLUT.

## MKMSZ Type-5 generation

The normative Type-5 wrapper/model/stream grammar is intentionally not duplicated here; see [Data structures and encodings](Data-Structures-and-Encodings).

For donor fighter assets, the stable generation contract is:

1. decode the donor representation into an indexed buffer using the donor's real row pitch;
2. convert dimensions/anchors into target order and choose aligned backing dimensions independently from visible dimensions;
3. translate the donor palette into the selected MKMSZ target TLUT;
4. encode the target indexed buffer into native Type-5;
5. place every generated fighter shape on a 4-byte boundary;
6. independently decode the emitted Type-5 stream and compare it with the selected target buffer;
7. keep generated normal-class widths at `>= 1` until zero-bit normal classes are independently established safe.

Type-5 model records can share one physical pattern dictionary while carrying independent entropy-class widths/bases. That property is central to the later Sektor packing strategy: more entropy models can reduce stream cost without duplicating the entire physical pattern table.

Lossless round-trip is the default contract. Some bounded proof builds deliberately selected a smaller codebook for supplemental source poses to stay within a known runtime footprint. Those approximations are proof-specific choices, not a relaxation of the Type-5 format itself.

## Fighter-resource storage and packing strategy

### Stock Type-5 corpus and encoder benchmark

Clean MKMSZ file ID `0x87` contains **341** stock Sub-Zero Type-5 fighter frames sharing the table at `+0x14AC`. The scanned Type-5-owned corpus occupies `+0x14AC..+0x41684` end-exclusive and decodes to **1,418,312** indexed-pixel bytes.

For that exact stock corpus:

| Component | Midway stock | MKMSZR generalized encoder-v2 |
|---|---:|---:|
| Shared table/dictionaries | 112,636 bytes | 111,878 bytes |
| Padded compressed streams | 139,068 bytes | 139,008 bytes |
| Shape/descriptor/wrapper overhead | 10,912 bytes | 10,912 bytes |
| Total | 262,616 bytes (`0x401D8`) | 261,798 bytes (`0x3FEA6`) |

The stock total is approximately **5.4007× smaller** than the decoded pixels, while the generated total is approximately **5.4176× smaller**. The generated result is **818 bytes (0.311%) smaller** on identical decoded art. Stream coding differs by only 466 bits across all 341 frames. Most of the measured 818-byte improvement comes from omitting **128 stock dictionary patterns unused by the scanned corpus**. This establishes that the project encoder is approximately at stock codec efficiency; the major remaining storage opportunities are dictionary/model grouping, cross-animation pattern sharing, dead-stock reclamation, and whole-resource packing rather than a missing radically better Type-5 bitstream algorithm.

Reproducible benchmark tool: `tools/benchmark_type5_encoder.py`.

### Whole-character reclamation

A Sektor-first takeover can reclaim the stock Type-5 corpus only after all remaining direct stock Type-5 references are redirected or otherwise proven dead. The v53 strategy redirects unported states to a safe Sektor stance placeholder, preserving their control grammar while removing their dependency on Sub-Zero frame art.

That makes the stock Type-5 region reusable for Sektor-generated content. This is a **resource-liveness conclusion**, not a declaration that arbitrary bytes in file `0x87` are free. Literal production allocation ownership remains with [Memory and allocation map](Memory-and-Allocation-Map).

### Shared dictionaries and entropy models

The v54 packing proof established that multiple generated Type-5 model records may point to one physical 5-bpp dictionary. Its 152-frame composition used one shared dictionary with 16 entropy models. Later Run-repair proofs increased the model count while retaining one physical dictionary.

This is the preferred packing direction when additional donor frames are required: optimize entropy grouping and shared-pattern reuse before enlarging the loaded fighter resource.

### Representative packing snapshots

These figures are proof-instance data, not format requirements or production allocations:

| Proof | Generated corpus / models | Shared-pattern / stream data | File `0x87` | Asset/storage conclusion |
|---|---|---|---:|---|
| v53 | 129 Sektor frames; two shared 5-bpp models | model pattern counts 19,939 and 15,869; 118 frames placed in reclaimed stock Type-5 space, 11 in the tail | `0x473D8` | Full stock Type-5 corpus can be reclaimed after direct references are redirected |
| v54 | 152 frames; 16 entropy models over one physical dictionary | 40,594 patterns; table/dictionary `0x31F5E`; padded streams `0x156B8` | `0x4E154` | Shared-dictionary/multi-model packing can retain Run/Combo/flattened Throw content inside the then-working footprint envelope |
| v55 | 158 frames; 52 models | 40,595 patterns; table/dictionary `0x32E03`; padded streams `0x136A4` | `0x4D0A4` | Nonzero normal-class guard plus compact packing; PS1 Run pixels later rejected |
| v56 | 158 frames; 64 models | 40,833 patterns; table `0x33789`; padded streams `0x1408C` | `0x4E414` | Corrected-cursor PS1 buffers increased real pattern pressure, but the source interpretation still failed visually |
| v58 | 158 frames; 64 models | 40,737 patterns; table `0x335A9`; padded streams `0x14254`; 160 supplemental WIMP patterns | `0x4E3FC` | Stride-corrected WIMP Run composition is Runtime-confirmed and remains below the v49 working footprint |
| v64 | 160 frames; 64 models | one chest + one rocket frame quantized into the existing dictionary/model structure | `0x4E788` | Compact missile/chest asset proof; above the v49 working footprint and not Fortress-revalidated |
| v69 | 159 frames; compact chest-only diagnostic | single chest pose retained; missile asset omitted | `0x4E71C` | Runtime-confirmed safe one-frame chest presentation on the tested route |
| v70 | 160 frames; compact chest + rocket diagnostic | genuine horizontal rocket frame added back | `0x4E790` | Runtime-confirmed rocket presentation/flight path on the tested route; spawn/palette/flight semantics remain wrong |

### Bounded file-size evidence

The Sektor proof line demonstrates that **loaded file footprint alone can break stage initialization**, especially Fortress. These are route-specific proof bounds, not a universal safe-size constant:

| Proof footprint | Bounded result |
|---:|---|
| file `0x87 = 0x52740` | Runtime-confirmed Fortress failure from footprint alone |
| file `0x87 = 0x5100C` | Runtime-confirmed later Fortress failure from footprint alone |
| file `0x87 = 0x4E544` | Runtime-confirmed Fortress gameplay + Inventory in v49 |
| file `0x87 = 0x4E3FC` | v58 remains below the proven v49 working footprint; ordinary Run is Runtime-confirmed |
| file `0x87 = 0x4E71C..0x4E790` | v69/v70 run on the tested missile route, but Fortress/Prison memory boundaries were not revalidated; do **not** promote these as general safe footprints |

The practical rule is to treat resource footprint as a guarded runtime constraint, keep proof allocations separate from production ownership, and prefer compaction/reclamation over assuming a larger fighter file will be safe.

## Asset-translation proof chronology

This table is intentionally limited to **stable asset/codec/storage conclusions**. Full per-version identities, routes, final statuses, animation/gameplay results, and supersession are canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).

| Proof | Asset-translation result |
|---|---|
| v42 | Runtime-confirmed one generated Type-5 Sektor frame; aligned backing dimensions can differ from visible descriptor dimensions |
| v43 | Runtime-confirmed five-frame native Type-5 idle compaction; proves generated Type-5 can shrink the fighter resource |
| v44 | Shared Type-5 dictionary works for multiple animations, but unaligned generated shapes caused a Crouch hard hang |
| v45 | Runtime-confirmed correction: every generated fighter shape is 4-byte aligned |
| v46 | Runtime-confirmed generated wider Type-5 class/zero-run path for the mapped animation set; later Prison/Inventory behavior exposed resource-headroom sensitivity |
| v47 | Runtime-confirmed conservative dead-stock stream reclamation on the tested Prison route |
| v48 | Runtime-confirmed that an enlarged file-`0x87` footprint alone can break Fortress |
| v49/v50 | Runtime-confirmed compressed locomotion and conservative stock-hole reuse below the Fortress failure region |
| v51/v52 | Runtime-confirmed second Fortress footprint failure at `0x5100C`; content expansion is not required to reproduce it |
| v53 | Sektor-first resource strategy: resident 32-color Sektor palette, full stock Type-5 reclamation, and common-animation takeover; later proof work treats this architecture as the runtime-confirmed baseline |
| v54 | One physical dictionary with multiple entropy models; zero-bit normal-class use coincides with the Sweep-Fall hard-hang and is not accepted as safe |
| v55 | Adds the `normal_bits >= 1` compatibility guard; the optimizer searches normal-class widths from **1 through 16 bits** across all 52 emitted model records. The first PS1 Run import is rejected because its POVBQ output cursor collapsed each row pair into four columns |
| v56 | Cursor-corrected PS1 decode still produces invalid speckled bodies; PS1 POVBQ Run pixels are rejected as the current N64 donor source |
| v57 | Preserved WIMP/MK3 source selected; first extraction is rejected because it ignored `align4(xsize)` source stride |
| v58 | Runtime-confirmed stride-corrected full twelve-pose Run; preserves WIMP-derived even poses and native Type-5 packing inside the bounded working footprint. **Superseded as the intended final Run composition:** the accepted 2026-09-25 design uses only retail N64 poses `1,3,5,7,9,11` and physically removes the six even-pose assets. Later static cadence reconciliation shows those six poses should run at MKMSZ Run rate **3**, not be duplicated at stock rate 2. |
| v63 | Rejected storage assumption: replacing a file-`0x87` bank classified as dead caused normal hit/blood corruption and a hard hang |
| v64 | Compact one-chest/one-rocket Type-5 composition reaches the special path at `0x4E788`; presentation/lifecycle remains wrong |
| v69 | Runtime-confirms the single chest asset itself can be installed safely for one frame through the resolved target cursor |
| v70 | Runtime-confirms the genuine horizontal rocket asset reaches and travels as the live projectile; target palette/spawn/flight translation remains incomplete |

For exact proof ROM identities and the broader animation/gameplay chronology, see [Sektor takeover proof history](Sektor-Takeover-Proof-History). Pre-test wording is retained there only as explicitly superseded historical context.

## Accepted Run simplification

The current Sektor direction no longer needs a twelve-physical-pose Run. The accepted asset set is the six retail N64 MKT poses `RBRUN1,3,5,7,9,11`; the six WIMP-derived even poses are intentionally omitted.

A later cadence audit supersedes the earlier “hold each pose twice” timing rule. Retail MKT advances Sektor Run at rate 6 on a 60-Hz scheduler (~100 ms/pose), while stock MKMSZ Run advances rate-2 script entries on the ~30-Hz gameplay scheduler (~66.7 ms/entry). The cadence-equivalent target setting is therefore **MKMSZ Run rate 3 with one visual entry per retained pose**. Exact timing/control details are owned by [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) and [MKT adapter primitives](MKT-Adapter-Primitives).

Consequences for the converter/build pipeline:

- physically omit the six WIMP-derived even Run poses;
- remove the PS1 Run extraction/POVBQ decode path from the active Sektor build, because it is historical/rejected and no longer needed by any accepted Run asset;
- remove the Run-only WIMP supplemental dependency when the physical six-pose repack is integrated;
- retain the v55-v58 PS1/WIMP history as provenance only, not as current build requirements;
- do not synthesize intermediate Run poses merely to fill MKMSZ's historical twelve visual positions;
- keep all non-Run Sektor asset conversion behavior unchanged.

The analyzed physical repack reduces file `0x87` from `0x4E3FC` to `0x4CD68`: **5,780 bytes (`0x1694`) saved**. Against the established v49 working bound, headroom increases from `0x148` to `0x17DC`. This repack is Implementation/static-confirmed; its asset-removal result remains valid independently of the later rate-3 cadence correction. A bounded runtime regression is still required before promoting it as the new common-animation baseline.

## Current compatibility boundaries

- **Supported:** offline decode of known donor fighter formats into indexed pixels, explicit dimension/anchor conversion, palette translation, native Type-5 generation, shared-dictionary packing, and bounded dead-stock reclamation after liveness proof.
- **Supported with scope limits:** WIMP/MK3 robot-source calibration for the checked Sektor Run family; it is not a universal cross-game scaler.
- **Rejected as direct paths:** copying MKT codec streams into MKMSZ, tightly packing rows whose donor storage uses aligned pitch, overwriting the stock palette for isolated imports, unaligned generated shapes, and the current PS1 POVBQ robot Run pixel interpretation.
- **Pending for production:** conflict-free final fighter-resource allocation/composition if Sektor becomes a product feature. Existing proof footprints validate feasibility and failure boundaries only.

## Related pages

- [Data structures and encodings](Data-Structures-and-Encodings) — canonical MKMSZ record and Type-5 format grammar.
- [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer) — current genuine donor-port strategy and compatibility contract.
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) — slot mapping, mapping policy, current coverage, and gaps.
- [Sektor takeover proof history](Sektor-Takeover-Proof-History) — canonical vNN identities, routes, results, supersession, and proof-specific allocation history.
- [Player actions and special moves](Player-Actions-and-Special-Moves) — target action/control ABI; not asset encoding.
- [PS1 research](PS1-Research) — MKMSZ PS1 platform facts.
- [N64–PS1 comparison](N64-PS1-Comparison) — transfer-safety rules across platforms.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership; proof file-size bounds here are not allocation claims.
