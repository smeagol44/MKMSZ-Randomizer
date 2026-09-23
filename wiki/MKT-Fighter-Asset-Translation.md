# MKT fighter asset translation

> **Scope:** This page owns stable donor-to-target fighter-asset translation for the MKT/Sektor work: donor frame descriptors, dimensions and anchors, donor image formats, palette conversion/binding, MKMSZ Type-5 generation, and fighter-resource storage/packing strategy.
>
> It does **not** own the normative MKMSZ Type-5 grammar, which remains in [Data structures and encodings](Data-Structures-and-Encodings); animation-slot mapping, which remains in [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping); or the full version-by-version proof diary. Until Audit Task 14 creates the dedicated Sektor proof-history owner, detailed vNN chronology remains in [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer) and [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping).

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
- MKT N64 codecs `22` and `24`, and the codec-`15` mechanical-arm path, are donor formats only. Their bytes are decoded offline; MKMSZ does not consume those streams directly.
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

| Frame | Record ROM | Visible geometry | Donor anchor | Donor texture offset |
|---|---:|---:|---:|---:|
| `SCCOMBO10` | `0x62BB40..0x62BB53` | `42x95` | `(+15,-19)` | `0x282C4` |
| `SCCOMBO11` | `0x62BB54..0x62BB67` | `50x102` | `(+15,-13)` | `0x28724` |
| `SCCOMBO12` | `0x62BB68..0x62BB7B` | `82x106` | `(+25,-8)` | `0x28BE4` |

MKT N64 was built with `ENDIAN=1`; its packed `XYTYPE` is physically `ypos, xpos`. For size words this means donor **Y:X**. MKMSZ frame setup uses the first size halfword as X/width and the second as Y/height, so conversion must swap the donor size halfwords to target **X:Y**.

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

### MKT codec 15 and composite assets

Sektor's mechanical-arm throw uses a donor codec-`15` arm path plus holder/body art. The current adapter decodes the arm sprites offline using the donor `uncompress_8` grammar, composites them with `RBSHOLDER4` using donor anchors, and encodes the flattened result as ordinary MKMSZ Type-5 frames.

The important compatibility boundary is structural: MKMSZ does not import the incompatible MKT slave-animation ABI merely to display the composite. The donor multi-object presentation can be flattened into a target-native fighter frame when target gameplay timing must remain stock.

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

The established conversion is:

```text
MKT RGBA5551
-> preserve the 5-bit RGB channels
-> reorder into MKMSZ BGR555 source words
-> donor alpha = 0 becomes source word 0
```

For isolated imported-frame work, the native target path is:

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

The generated result is **818 bytes (0.311%) smaller** on identical decoded art. Stream coding differs by only 466 bits across all 341 frames. This establishes that the project encoder is approximately at stock codec efficiency; the major remaining storage opportunities are dictionary/model grouping, cross-animation pattern sharing, dead-stock reclamation, and whole-resource packing rather than a missing radically better Type-5 bitstream algorithm.

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

### Bounded file-size evidence

The Sektor proof line demonstrates that **loaded file footprint alone can break stage initialization**, especially Fortress. These are route-specific proof bounds, not a universal safe-size constant:

| Proof footprint | Bounded result |
|---:|---|
| file `0x87 = 0x52740` | Runtime-confirmed Fortress failure from footprint alone |
| file `0x87 = 0x5100C` | Runtime-confirmed later Fortress failure from footprint alone |
| file `0x87 = 0x4E544` | Runtime-confirmed Fortress gameplay + Inventory in v49 |
| file `0x87 = 0x4E3FC` | v58 remains below the proven v49 working footprint; ordinary Run is Runtime-confirmed |

The practical rule is to treat resource footprint as a guarded runtime constraint, keep proof allocations separate from production ownership, and prefer compaction/reclamation over assuming a larger fighter file will be safe.

## Asset-translation proof chronology

This table is intentionally limited to asset/codec/storage conclusions. Full per-version routes, hashes, animation mapping, and gameplay results remain in the existing MKT/Sektor pages until Audit Task 14 creates `Sektor-Takeover-Proof-History`.

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
| v55 | Adds the `normal_bits >= 1` guard; first PS1 Run import is rejected because its POVBQ output cursor collapsed each row pair into four columns |
| v56 | Cursor-corrected PS1 decode still produces invalid speckled bodies; PS1 POVBQ Run pixels are rejected as the current N64 donor source |
| v57 | Preserved WIMP/MK3 source selected; first extraction is rejected because it ignored `align4(xsize)` source stride |
| v58 | Runtime-confirmed stride-corrected full Run; preserves the WIMP-derived even poses and native Type-5 packing inside the bounded working footprint |

For the exact proof ROM identities and the broader animation/gameplay chronology, see [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) and [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer). Some older sections there intentionally retain pre-test status wording; Task 14 is the planned reconciliation into the dedicated proof-history owner.

## Current compatibility boundaries

- **Supported:** offline decode of known donor fighter formats into indexed pixels, explicit dimension/anchor conversion, palette translation, native Type-5 generation, shared-dictionary packing, and bounded dead-stock reclamation after liveness proof.
- **Supported with scope limits:** WIMP/MK3 robot-source calibration for the checked Sektor Run family; it is not a universal cross-game scaler.
- **Rejected as direct paths:** copying MKT codec streams into MKMSZ, tightly packing rows whose donor storage uses aligned pitch, overwriting the stock palette for isolated imports, unaligned generated shapes, and the current PS1 POVBQ robot Run pixel interpretation.
- **Pending for production:** conflict-free final fighter-resource allocation/composition if Sektor becomes a product feature. Existing proof footprints validate feasibility and failure boundaries only.

## Related pages

- [Data structures and encodings](Data-Structures-and-Encodings) — canonical MKMSZ record and Type-5 format grammar.
- [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer) — current genuine donor-port strategy and existing detailed proof chronology.
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) — slot mapping, current coverage, and existing vNN history pending Task 14.
- [Player actions and special moves](Player-Actions-and-Special-Moves) — target action/control ABI; not asset encoding.
- [PS1 research](PS1-Research) — MKMSZ PS1 platform facts.
- [N64–PS1 comparison](N64-PS1-Comparison) — transfer-safety rules across platforms.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership; proof file-size bounds here are not allocation claims.