# Toasty audio research

> **Scope:** This page is the canonical owner for Toasty donor-audio identification, source-to-retail MKT mapping, rejected/superseded candidates, Toasty sound proofs v01-v03, and the boundary between a successful disposable proof and production integration.
>
> MKMSZ host audio mechanics are canonical in [Audio system](Sounds-and-Music). Function semantics remain canonical in [Function registry](Function-Registry). Toasty visual research is separate and is linked only for final composition context.

## Current accepted conclusion

**Audibly confirmed donor identity and Runtime-confirmed MKMSZ proof:** the accepted Toasty route is:

```text
preserved/source selector slot 0x1B  (DF: toasty)
  -> retail MKT primary selector slot 0x1B
  -> retail event 0x0160
  -> SN64 patch 65
  -> subpatch 111
  -> waveform 77
  -> retail waveform correction -2253 cents
```

The retail waveform-77 span is ROM `0xB0FBFC..0xB10411`. The user directly auditioned the pitch-corrected slot-`0x1B` candidate on 2026-09-22 and confirmed it as the desired Dan Forden **“Toasty!”** voice. Disposable sound proof `MKMSZR_toasty-sound_common-proof_v03.z64` then played that voice correctly through MKMSZ's native audio path on the tested ordinary-pickup route.

This **supersedes** the earlier branch-first identification. Retail selector slot `0x10` is **Shao Kahn “Fight!”**, not Toasty. The reverse-cymbal waveform-49 route and the later waveform-262/slot-`0x10` route are retained below only as rejected diagnostics.

## Current status

| Claim | Evidence | Current boundary |
|---|---|---|
| Source selector `0x1B` means Toasty | **Static-confirmed** | Preserved `triple_sndtab` plus explicit `MKFX.ASM` `01bH` Toasty call |
| Retail slot `0x1B` maps to event `0x0160` | **Static-confirmed** | Anchored source-to-retail selector-table correlation |
| Event `0x0160` -> patch 65 -> subpatch 111 -> waveform 77 | **Static-confirmed** | Retail MKT SSEQ/SN64 trace |
| Waveform 77 is the intended Toasty voice | **User-audition confirmed** | Pitch-corrected candidate explicitly identified by the user |
| Imported waveform 77 works through MKMSZ | **Runtime-confirmed**, v03 | Tested ordinary-pickup route only |
| Cross-game SN64/N64-ADPCM compatibility | **Runtime-confirmed proof** | v02 establishes one-shot foreign-sample playback; v03 establishes the accepted Toasty voice |
| Final cosmetic trigger + production-safe allocation | **Pending** | v03 replaces a pickup route and is not production architecture |

## Accepted source-to-retail anchor

The reliable identification method is semantic slot anchoring, not the earlier `randper(40)` branch match. Preserved source keeps the Dan Forden trio at selector slots `0x1B..0x1D`, and the retail primary selector table preserves those semantic slot positions in an independently anchored prefix.

| Source semantic | Retail slot | Retail event | Patch | Subpatch | Waveform | Pitch correction |
|---|---:|---:|---:|---:|---:|---:|
| **Toasty — confirmed** | `0x1B` | `0x0160` | 65 | 111 | 77 | `-2253` cents |
| Frosty — adjacent source mapping, not needed for current feature | `0x1C` | `0x018E` | 66 | 112 | 78 | `-2253` cents |
| Crispy — adjacent source mapping, not needed for current feature | `0x1D` | `0x0188` | 67 | 113 | 79 | `-2253` cents |

The adjacent Frosty/Crispy rows are preserved because they are useful controls for the source-to-retail mapping, not because MKMSZR currently intends to integrate those voices.

## Production-integration boundary

### Trigger-source correction: comment family, not uppercut-only

**Static-confirmed in preserved donor source; exact retail Rev. 2 mapping Pending.**

The final cosmetic trigger is broader than a single uppercut. Preserved `src/gamecode/mkreact.c` creates `FX_COMMENT` from `r_uppercut` and from multiple combo reaction paths: `r_combo5`, `r_combo6`, `combo2`, `r_combo3`, and `combo43` (the shared `r_combo4` path). `FX_COMMENT` then performs the delayed commentary/Toasty selection in `mkfx.c`.

The preserved source probability expression is `randper((curback==BKGD_MK2PITSTAR_MOD)?0xA0:0x40)`. The source implementation of `randper` defines its argument as a probability out of 1000, so that source revision is 16% on the special background and 6.4% otherwise.

Earlier supplied-retail tracing recorded a `randper(40)` branch and interpreted it as 4%. That retail/source discrepancy is now explicit Pending work. Final MKMSZR behavior must be chosen from the supplied retail Rev. 2 evidence after reconciliation, not from the earlier 4% shorthand and not from source alone.


v03 proves feasibility, not final product composition. The final feature still needs a dedicated production-safe audio definition/route and final cosmetic trigger; it must not silently reuse the disposable pickup replacement or proof-only allocation. Production composition must remain compatible with the native randomizer, HUD/UI, character-swap work, and the separately tracked Toasty visual path.

The current visual status and its allocations remain canonical in [Toasty visual research](Toasty-Visual-Research); this page does not redefine them.

## Preserved v01 proof-host details

**Rejected / superseded proof allocation.** The original in-place host audit considered MKMSZ patch/raw ID 550 with intermediate record 393 and waveform 383. Exact proof locations preserved from the old MKT compatibility audit:

- target waveform ROM `0xB84FEC..0xB87A3F`;
- target intermediate record ROM `0x94A61C`;
- target waveform record ROM `0x94E520`;
- target predictor book ROM `0x968F88`.

The allocation was later shown to be live because stock SSEQ entry 393 starts on patch 550. It is retained only as a diagnostic lesson and is not reusable production space.

## Rejected and superseded investigation chronology

> The material below intentionally preserves the chronological intermediate claims, exact traces, and failed candidates that led to the accepted result above. **Any identification below that conflicts with the Current accepted conclusion is superseded and is not current Toasty identity.**


## MKT donor evidence relevant to Toasty

Midway's preserved MKT/MK3 source identifies the Toasty voice through donor sound-table entry `0x1B`, which resolves to donor sound call/sample identifier `0x1095` and is described as Dan Forden's “Toasty”.

This is **donor-side static evidence only**. Numeric sound IDs are game-local unless compatibility is demonstrated. The project must not assume that donor `0x1095` can be passed directly to MKMSZ, just as donor strike/reaction indices cannot be assumed to retain their numeric meaning across games.

Retail N64 tracing supersedes the old source-level numeric identifier for implementation purposes.

**Static-confirmed in the supplied MKT USA Rev. 2 ROM:** the retail probability helper is at `0x8006E50C`. There is exactly one `randper(40)` call in the executable, at ROM `0x00039BF4`; this matches the preserved source Toasty/comment branch, which also uses `40/1000`.

On the successful branch, the retail routine reaches MKT's native sound-table wrapper at `0x800054A8` with:

```text
a0 = 0x10
a1 = 0
```

**Superseded interpretation at this stage:** this branch was initially treated as proving retail Toasty selector slot `0x10`. Later source-to-retail anchor work and direct listening established that slot `0x10` is **Fight!**, while Toasty is slot `0x1B`.

For `a1 = 0`, `0x800054A8` indexes the 16-bit table at `0x800A1AA8`. Entry `0x10` is at ROM `0x000A1AC8` and contains `0x0244`. Further bank tracing corrects the earlier terminology: `0x0244` is a retail MKT sound-definition/event value, **not** the final SN64 patch/waveform ID.

### Retail MKT Toasty CTL/TBL trace

**Static-confirmed in the supplied MKT USA Rev. 2 ROM.** The retail event value `0x0244` ultimately selects SN64 patch `7`. The donor control bank is:

- SN64 header ROM `0xA8F550`;
- compressed control payload ROM `0xA8F588`;
- raw-DEFLATE compressed size `0x17AE0`;
- decompressed control payload size `0x1F720`.

Within that decompressed control payload:

1. patch `7` is at relative offset `0x001C`, bytes `01 00 00 4F`: one subpatch, starting at subpatch index `79`;
2. subpatch `79` is at relative offset `0x0D0C`, bytes `69 7C 40 00 3C 00 00 7F 00 00 00 31 00 02 7D 00 00 0A 7F 7F`; its waveform/SFX ID is `49`;
3. waveform record `49` is at relative offset `0x2CC0`, bytes `0003882A 00002A54 00000000 00000000 FFFFFFFF 00000000`.

Waveform record `49` therefore specifies:

- TBL-relative start `0x3882A`;
- encoded length `0x2A54` bytes;
- no loop (`0xFFFFFFFF`);
- predictor book `49`, stored in the decompressed CTL at relative offset `0x81D0`;
- predictor order `2`, predictor count `8`.

The MKT waveform-data/TBL base is ROM `0xAB4370`. Therefore the genuine encoded Toasty voice occupies:

- ROM start `0xAECB9A`;
- ROM end-exclusive `0xAEF5EE`;
- inclusive last byte `0xAEF5ED`;
- length `0x2A54` bytes;
- SHA-256 `bbc594750c7cd6fe9e14f161abe762af6f905801469af28659489493f90f33a2`.

The length is exactly 1,204 nine-byte N64 ADPCM frames, or 19,264 decoded PCM samples. At the bank's nominal 22.05 kHz rate this is about 0.874 seconds.

**Rejected / corrected by direct audio validation.** The waveform at ROM `0xAECB9A..0xAEF5ED` decodes cleanly as N64 ADPCM, but the user listened to the extracted WAV and identified it as a **reverse-cymbal effect**, not Dan Forden saying “Toasty!”. Therefore the prior conclusion that retail event value `0x0244` ultimately selects patch 7 / subpatch 79 / waveform 49 for Toasty is wrong.

The useful surviving evidence is:
- retail Toasty/comment code reaches sound wrapper `0x800054A8` with table index `0x10`;
- table entry `0x10` at ROM `0xA1AC8` contains `0x0244`;
- waveform `0xAECB9A..0xAEF5ED` is a valid SN64 ADPCM sample with the documented predictor book, but it is **not Toasty**.

The next bounded task is to re-trace how retail MKT interprets `0x0244` at runtime before any SN64 patch/waveform lookup, rather than assuming the prior patch-7 mapping. No further Toasty import proof should be built until the correct donor waveform is positively identified by decoded-audio validation.

## Detailed proof and identification chronology

### Toasty sound proof v01 — rejected routing assumption

Disposable proof: `MKMSZR_toasty-sound_common-proof_v01.z64`.

**Runtime-confirmed failure / diagnostic result.** The imported donor waveform did not play as a normal pickup SFX. Instead, gameplay produced a very faint recurring “ghost/howl” sound at changing pitches. The effect followed the game's **Music** toggle rather than the expected SFX behavior; with music disabled the pickup produced no Toasty voice.

Static postmortem identified two namespace/routing mistakes in the proof design:

1. the prior liveness audit for MKMSZ patch `550` was incomplete. It checked explicit SSEQ instrument-change commands but did **not** check each SSEQ track header's initial patch ID. Stock SSEQ entry `393` is a one-track entry whose initial patch ID is exactly `550`. Therefore patch `550` / subpatch `393` / waveform `383` is live and must not be treated as unused;
2. redirecting gameplay descriptor `0x3B` from raw/event ID `0x020C` to `0x0226` selects **SSEQ entry 550**, not “patch 550 directly.” SSEQ entry `550` is a five-track looping/music-style entry whose initial patches are `37, 38, 39, 41, 41`. Thus the pickup redirection and the patched waveform were in different namespaces.

The stock pickup route is now more precisely understood:

```text
descriptor 0x3B
  -> event/SSEQ entry 0x020C (524)
  -> entry 524 initial patch 681
  -> patch 681
  -> subpatch 524
  -> waveform 133
```

This explains why v01 could alter background/sequenced audio without producing the intended pickup Toasty voice.

The pitch-varying runtime symptom is consistent with the transplanted Toasty ADPCM waveform being decoded and used as a pitched SN64 instrument, but this is **not yet sufficient to label the foreign waveform import itself runtime-confirmed**; the routing was wrong and no clean one-shot Toasty playback occurred.

**Rejected / superseded conclusion:** patch/raw ID `550` is not an unused proof host. Future liveness checks must include both SSEQ track-header initial patch IDs and in-stream instrument changes.

The next bounded sound task is to design a proof around the known stock pickup event `524` / patch `681` without modifying any patch or waveform reachable by unrelated sequenced audio.


### Clean Toasty pickup proof v02 design

**Static-confirmed design; runtime pending.** This supersedes the rejected v01 routing/allocation approach.

A complete parse of all 590 stock MKMSZ SSEQ entries / 882 tracks, including both each track header's initial patch ID and every in-stream `0x07` program change, establishes:

- gameplay descriptor `0x3B` is the only descriptor-table entry selecting event/SSEQ entry `0x020C` (524);
- SSEQ entry 524 has one track and starts on patch `681`;
- patch `681` is referenced by exactly that one SSEQ track and by no in-stream program change;
- patch `681` owns only subpatch `524`;
- subpatch `524` owns stock waveform `133`;
- waveform `133` has only `0x1EFA` bytes of physical TBL storage, too small for the donor Toasty stream (`0x2A54`), so it must not be expanded into following live waveform allocations.

The corrected liveness audit finds waveform record `533` genuinely unreachable from all stock SSEQ tracks. Its only patch owner is patch `68`, and patch 68 is absent from every initial track patch ID and every in-stream program change. Waveform 533's existing physical TBL allocation is only `0x1750` bytes, so the proof will use its **record and predictor slot only**, not overwrite or extend its original stock sample interval.

Proposed v02 proof layout:

```text
stock routing kept intact:
descriptor 0x3B
  -> event 524
  -> patch 681
  -> subpatch 524

proof-only change:
subpatch 524
  -> unused waveform record 533
  -> new Toasty sample at ROM 0xF20000
```

Exact proof edits:

- leave descriptor `0x3B`, SSEQ entry 524, and patch 681 unchanged;
- replace isolated subpatch 524 at ROM `0x94B058` with the donor Toasty subpatch semantics, changing only its waveform ID from donor 49 to target waveform `533` (`0x0215`);
- replace unused waveform record 533 at ROM `0x94F330` with:
  - start offset `0x0056F9B0` relative to the MKMSZ waveform base `0x9B0650`, resolving to ROM `0xF20000`;
  - encoded length `0x2A54`;
  - no loop;
  - donor pitch/correction field `0`;
- replace unused predictor book 533 at ROM `0x972A38` with the donor Toasty order-2 / 8-predictor book;
- copy the exact donor `0x2A54`-byte ADPCM stream to ROM `0xF20000..0xF22A53`.

The clean ROM's global file table has no file claiming `0xF20000`; the highest stock file-table end is `0xEF6B60`, which is also the start of the ROM's trailing `0xFF` region. Thus `0xF20000..0xF22A53` is stock-unclaimed and byte-empty in the supported clean ROM. This is a **disposable proof allocation**, not yet a production allocation promise.

This design deliberately touches no stock waveform sample interval used by any sequenced audio. The old waveform 133 bytes remain stock, and waveform 533's old `0x1750`-byte sample interval also remains untouched; only its unreachable metadata/predictor record is repointed.

Expected runtime test: collecting an ordinary pickup should play the genuine MKT Toasty voice once, while background music remains unchanged. Music should no longer acquire pitched Toasty/ghost notes.


### Toasty sound proof v02 — runtime result

**Runtime-confirmed for foreign-sample playback; rejected as Toasty identification.** The v02 routing fix produced a normal one-shot sound effect on ordinary pickup, with no recurrence as background music. The heard effect matched the separately decoded donor WAV: a short reverse-cymbal sound.

v02 therefore runtime-confirms the important lower-level result that MKMSZ can play an imported MKT N64 ADPCM sample using transplanted predictor-book metadata through the stock pickup SSEQ route. It does **not** confirm the sample as Toasty. The remaining blocker is donor identification/routing inside MKT, not basic cross-game SN64 waveform compatibility.


### Corrected retail Toasty event trace

**Static-confirmed; decoded-audio identity pending direct listening confirmation.** The prior `0x0244 -> patch 7` interpretation was wrong because `0x0244` is not an SN64 patch number. The retail call path is:

```text
forden/comment path
  -> 0x800054A8(a0=0x10, a1=0)
  -> table 0x800A1AA8[0x10] = 0x0244
  -> 0x80005590
  -> 0x8008AA50(sound/event id 0x0244)
  -> ZLIB-SSEQ entry 580
```

`0x8008AA50` multiplies the event ID by `0x10` and indexes the runtime sequence/event-definition array before entering the low-level audio path. This establishes that retail value `0x0244` names **SSEQ event 580**, not SN64 patch 7.

Retail MKT's ZLIB-SSEQ bank is at ROM `0xAA7070`. Its compressed 627-entry table expands to `0x2730` bytes. Entry 580 contains:
- one track;
- decompressed length `0x30`;
- data offset `0x4E94`;
- compressed track stream beginning at ROM `0xAAC6CA`.

The decompressed track is:

```text
initial patch 0x00F9 (249)
program change -> 0x31 (49)
(no note is played)
program change -> 0xF9 (249)
play note 0x3C, velocity 0x7F
stop note 0x3C
end
```

Therefore the audible Toasty event note uses **SN64 patch 249**. Patch 49 is selected transiently but no note is emitted while it is active.

Parsing patch 249 through the retail MKT SN64 bank gives:

```text
patch 249
  -> intermediate record 263
  -> waveform record 262
```

Waveform 262 metadata:
- TBL-relative start `0xD9E7E`;
- encoded length `0x0E22`;
- no loop;
- predictor book order 2, 8 predictors;
- MKT waveform/TBL base `0xAB4370`;
- physical donor ROM span `0xB8E1EE..0xB8F00F`;
- raw ADPCM SHA-256 `7b2324798718047a1fc563b6aefeb62060e0056600d47de1a641653dcf0212b2`.

The patch root key is `0x3C`, exactly matching the SSEQ note `0x3C`, so this event requests the sample at its natural key rather than intentionally pitch-shifting it.

Direct SN64 ADPCM decoding yields 6,432 PCM samples, about 0.292 s at the bank's nominal 22.05 kHz rate. The generated WAV SHA-256 is `c2113d64bf843af167af000001ccf22824e042f1c39d4cacd12ba6074941ab04`.

This waveform is the **correct static retail candidate reached by the Toasty event path**. Do not mark its audible identity runtime-confirmed until the extracted WAV is directly listened to and confirmed as Dan Forden's “Toasty!” voice.


### Second Toasty donor candidate — rejected

A follow-up trace treated retail table value `0x0244` as ZLIB-SSEQ event 580 and followed its apparent audible note to patch `249` -> intermediate `263` -> waveform `262` at MKT ROM `0xB8E1EE..0xB8F00F`.

**Rejected by direct audio validation.** The extracted/decoded waveform is not a recognizable Toasty voice; the user reported that the candidate effectively produces no audible sound. Although the decoded PCM is not numerically all-zero, it is not a valid Toasty identification.

Therefore the prior conclusion that `0x0244 -> event 580 -> patch 249 -> waveform 262` is the complete Toasty audio path is **Rejected / superseded**.

The next bounded audit must return to the retail MIPS call sequence around the unique `randper(40)` path and decode the actual `triple_sound` helper ABI/alternate entry semantics instruction-by-instruction before mapping any value into SSEQ/SN64 resources again.


### Retail MKT `triple_sound` ABI

**Static-confirmed from retail MKT USA Rev. 2 MIPS disassembly.** This audit corrects the interpretation boundary before any further Toasty sample extraction.

The main executable is loaded with ROM offset equal to low VA offset (ROM `0x1000` is entry VA `0x80001000`). Therefore retail helper VA `0x800054A8` is at ROM `0x54A8`; earlier analysis that applied MKMSZ's `+0xC00` mapping to MKT was incorrect.

The unique `randper(40)` Toasty/comment branch at ROM/VA `0x39BF4 / 0x80039BF4` reaches:

```text
0x80039C28  addiu a0,zero,0x10
0x80039C2C  jal   0x800054A8
0x80039C30  move  a1,zero
```

Retail `0x800054A8` is the N64 selector wrapper corresponding to the source-level `triple_sound` role. Its observed ABI is:

```text
a0 = 16-bit selector-table index
a1 = selector-table bank
     0     -> primary table at 0x800A1AA8
     nonzero -> secondary table at 0x800A1C20
```

The helper computes `entry_ptr = table_base + index*2` and reads a signed 16-bit selector entry.

For primary-table slot `0x10`:

```text
0x800A1AA8 + 0x10*2 = 0x800A1AC8
entry = 0x0244
```

The selector-entry high bit is metadata rather than part of the downstream audio-definition ID:

- bit 15 clear: use fixed pan `0x40` (center);
- bit 15 set: call `0x8000590C`, which derives a position-dependent pan value from gameplay X position;
- low 15 bits: downstream audio-definition/event ID.

Thus Toasty's retail selector entry `0x0244` is unflagged and centered.

The wrapper then calls `0x80005590(entry_ptr, pan)`. That helper masks the selected halfword with `0x7FFF` and passes the result to `0x8008AA50`.

For Toasty:

```text
triple_sound selector 0x10
  -> primary selector entry 0x0244
  -> pan 0x40
  -> audio-definition ID 0x0244 (decimal 580)
```

`0x8008AA50` does **not** treat `0x0244` as an SN64 patch or waveform number. It obtains the active audio manager through global `0x802AFEEC`, loads the current definition-array base from `manager->+0x0C -> +0x20`, computes:

```text
definition_ptr = definition_base + (0x0244 * 0x10)
```

and calls low-level `0x8008A74C(definition_ptr, 0x0244, 0, 0, params)`.

Therefore `0x0244` is **flat runtime audio-definition index 580 into a 16-byte-record array**. The exact ROM resource/bank record backing that runtime definition must be established from the manager/load path before mapping it to SSEQ, SN64 patch, subpatch, or waveform data.

**Rejected / superseded shortcut:** do not equate `0x0244` directly with ZLIB-SSEQ entry 580 solely because both use 16-byte records. That association requires an explicit loader/base trace.

This closes the requested ABI question. No further donor waveform should be extracted until the runtime definition-array base for the Toasty call is tied to its exact loaded ROM resource.


### Runtime definition-array ownership

**Static-confirmed from retail MKT USA Rev. 2 loader disassembly.** This closes the ownership gap left by the `triple_sound` ABI audit.

The active definition table used by `0x8008AA50` is not part of the SN64 patch/waveform table itself. It is the decompressed **ZLIB-SSEQ definition table** loaded from ROM resource `0xAA7070`.

#### Startup ownership chain

The retail audio startup caller at `0x80082D94` first initializes the SN64 sample/control bank:

```text
0x80082DA8  a0 = 0x00A8F550
0x80082DAC  jal 0x80089B50
```

It then explicitly initializes the sequence/event resource:

```text
0x80082DF0  a1 = 0x00AA7070
0x80082DF8  jal 0x80093550
```

`0x80093550` reads the 0x20-byte SSEQ header from ROM `0xAA7070`. The header reports:

- magic: `SSEQ`;
- version/game ID: `2`;
- entry count: `0x273` = 627;
- compression flag/type byte at header `+0x10`: nonzero;
- compressed definition-table size: `0x7A6`;
- decompressed definition-table size: `0x2730`.

The caller allocates exactly the returned `0x2730` bytes, obtains the active audio-manager pointer through `0x80089854`, and calls:

```text
0x80093614(manager, 0x00AA7070, 0, allocated_buffer, 0x2730)
```

Inside `0x80093614`, the decisive write is:

```text
0x800936E8  lw   t2,0x0C(t1)     ; manager->+0x0C
0x800936F0  sw   t9,0x20(t2)     ; manager->+0x0C->+0x20 = allocated_buffer
```

That is the exact same pointer chain later consumed by `0x8008AA50`:

```text
0x8008AA68  lw   t7,0x0C(t6)
0x8008AA70  lw   t8,0x20(t7)
0x8008AA78  sll  t9,a0,4
0x8008AA8C  addu a0,t8,t9
```

Therefore the runtime definition base used for `audio-definition ID * 16` is the heap buffer installed by the SSEQ loader.

#### Exact ROM resource and definition 0x0244

The SSEQ resource layout is:

```text
ROM 0xAA7070..0xAA708F   0x20-byte SSEQ header
ROM 0xAA7090..0xAA7835   0x7A6-byte raw-DEFLATE definition table
ROM 0xAA7836..           per-entry track streams
```

The compressed table at `0xAA7090` raw-DEFLATE-decompresses to exactly `0x2730` bytes, SHA-256:

`6cdfcf946ba78f492aa731ee542aeca6faf34d9c61d51871565f23f87e59ef7e`

There are 627 16-byte records. Audio-definition ID `0x0244` is decimal 580, so its record begins at decompressed-table offset:

```text
580 * 0x10 = 0x2440
```

Definition 580 is:

```text
00010100 00000030 00004E94 00000000
```

Interpreted with the retail SSEQ definition layout already used by the loader:

- `+0x00`: one track;
- `+0x04`: track-data length `0x30`;
- `+0x08`: track-data offset `0x4E94` from the start of the track-data area;
- `+0x0C`: runtime pointer/cache field, initially zero.

The track-data area begins immediately after the compressed table at ROM `0xAA7836`, so definition 580 resolves to:

```text
0xAA7836 + 0x4E94 = 0xAAC6CA
```

Thus the exact ROM resource supplying `triple_sound` selector slot `0x10`'s downstream definition `0x0244` is:

```text
MKT ZLIB-SSEQ resource at ROM 0xAA7070
  -> decompressed definition table
  -> record 580 at raw offset 0x2440
  -> track stream at ROM 0xAAC6CA, length 0x30
```

This now **confirms** the association `0x0244 -> SSEQ definition 580` through the actual retail loader and runtime pointer installation. The previously rejected shortcut was the unsupported leap from numeric equality alone; the relationship itself is now established by loader evidence.

This does **not** rehabilitate the rejected waveform-262 Toasty candidate. The remaining error must be downstream in interpretation of SSEQ entry 580's track/program/patch behavior or later SN64 selection semantics.

### Definition 580 retail command execution

**Static-confirmed from retail MKT USA Rev. 2 MIPS disassembly.** This replaces reliance on the generic SSEQ parser for the program/patch selected by Toasty's note-on event.

Definition `0x0244` / decimal 580 resolves through the proven SSEQ loader to compressed track stream ROM `0xAAC6CA`, compressed length `0x30`. Raw-DEFLATE decompression yields 48 bytes. The first `0x18` bytes are the retail track header; the final `0x18` bytes are the command stream:

```text
00 07 31 00
00 0C 67
00 0D 40
00 07 F9 00
01 11 3C 7F
85 7F 12 3C
00 22
```

The runtime track initializer at `0x8008A40C` sets track-state `+0x10 = 1`, selecting command-dispatch table `0x800F7CE0` via pointer table `0x800F7B10`.

For this dispatch table:

- opcode `0x07` -> handler `0x80091D28`;
- opcode `0x11` -> handler `0x80092D68`;
- opcode `0x12` -> handler `0x80092EE8`.

#### Program change 0x07

The retail `0x07` handler at `0x80091D28` reads the two bytes following the command and stores the resulting 16-bit program number directly at track-state `+0x04`.

Therefore the two program changes in definition 580 execute exactly as:

```text
07 31 00 -> current patch = 0x0031 (49)
...
07 F9 00 -> current patch = 0x00F9 (249)
```

The second write occurs before the note-on event.

#### Note-on 0x11

The retail note-on handler at `0x80092D68` reads the current patch directly from track-state `+0x04`:

```text
0x80092DA4  lh   t8,0x04(a0)   ; current patch/program
0x80092DAC  sll  t9,t8,2
0x80092DB4  addu t1,t9,t0     ; patch table base + patch*4
```

At the Toasty note-on command `11 3C 7F`, the current patch value is therefore **249 / `0x00F9`**.

The handler then reads patch 249's one-subpatch record from the active SN64 bank. In the decompressed MKT SN64 control bank:

```text
patch 249 record: 01 00 01 07
```

This means one subpatch beginning at index `0x0107` = 263.

Subpatch 263 is:

```text
64 7F 40 00 3C 00 00 7F 00 00 01 06 00 02 7D 00 00 0A 7F 7F
```

Its note range is `0x00..0x7F`, so note `0x3C` selects it. The subpatch's waveform field is `0x0106` = 262.

Therefore the exact retail command-selection chain is now:

```text
definition 580
  -> program 49
  -> volume/pan commands
  -> program 249
  -> note-on 0x3C
  -> retail note-on handler reads current patch 249
  -> subpatch 263
  -> waveform record 262
```

**Key conclusion:** patch **249** is retail-code-confirmed as the exact SN64 patch selected by definition 580's note-on event. This is not inferred from generic tooling.

The user's prior audition still rejects the standalone waveform-262 WAV as a valid audible Toasty reconstruction. Since retail execution really does select patch 249/subpatch 263/waveform 262, the remaining discrepancy is downstream: the standalone extraction/decoding/playback reconstruction is missing some retail runtime behavior (for example waveform pitch/correction, envelope or another voice-start transform), rather than selecting the wrong program before note-on.


### Retail Toasty voice-start transform

**Static-confirmed from retail MKT USA Rev. 2 MIPS disassembly; audible identity still pending a pitch-corrected listening check.**

The note-on path for definition 580 reaches:

```text
0x80092D68  note-on handler
  -> 0x80092B2C  voice-slot allocator / arbiter
  -> 0x80092674  voice-record initializer
  -> 0x800913A4  pitch / volume / envelope parameter builder
  -> 0x80097010  synth voice-start API
```

`0x80092B2C` is therefore not itself the pitch calculator. It selects/reuses a voice slot and delegates initialization.

#### Waveform correction relocation during SN64 bank initialization

A critical runtime conversion occurs in the SN64 waveform-record initialization loop around `0x800918C8`:

```text
0x800918C8  lw   t6,0x0C(a1)
0x800918D0  sw   t6,0x14(a1)
```

The loader copies the on-disk waveform field at `+0x0C` to runtime field `+0x14`, then repurposes the runtime `+0x0C` slot for a live ADPCM wave-info pointer.

For waveform 262, the original 24-byte disk record is:

```text
000D9E7E 00000E22 00000000 FFFFF733 FFFFFFFF 00000000
```

Thus the preserved runtime correction is:

```text
0xFFFFF733 = -2253 cents
```

The earlier standalone WAV reconstruction ignored this field and decoded the ADPCM stream directly at 22.05 kHz.

#### Retail pitch calculation

`0x800913A4` builds the pitch value in cents from the live voice, subpatch and waveform metadata. Its effective formula for this path is:

```text
pitch_cents =
    waveform_correction
  + pitch_bend_offset
  + 100 * (note - root_key)
  - detune
```

It then calls `0x80091340`, whose constants and loop implement the cents-to-ratio conversion:

```text
pitch_ratio = 2^(pitch_cents / 1200)
```

For the Toasty event:

- note = `0x3C`;
- root key = `0x3C`;
- detune = 0;
- subpatch pitch-wheel range bytes are both 0, so the pitch-bend contribution is 0;
- waveform correction = `-2253` cents.

Therefore:

```text
pitch_cents = -2253
pitch_ratio = 2^(-2253/1200)
            ~= 0.272154916
```

At the bank's nominal 22.05 kHz rate, the ADPCM stream is therefore consumed at an effective rate of approximately:

```text
22050 * 0.272154916 ~= 6001 samples/sec
```

Waveform 262 decodes to 6,432 PCM samples, so retail-speed playback lasts approximately:

```text
6432 / 6001 ~= 1.072 seconds
```

This is radically different from the rejected naive standalone reconstruction, which wrote the same 6,432 samples at 22.05 kHz and therefore lasted only about 0.292 seconds.

#### Envelope and voice-start parameters

Subpatch 263 contains:

```text
64 7F 40 00 3C 00 00 7F 00 00 01 06 00 02 7D 00 00 0A 7F 7F
```

The retail voice-start path converts the `+0x0C` attack value using exact integer arithmetic equivalent to multiplying by 1000 before passing it to the synth start call. For Toasty:

```text
attack = 2 -> 2000 microseconds = 2 ms
```

The note-off/release path at `0x800928FC` similarly converts the subpatch `+0x10` value:

```text
release/decay = 10 -> 10000 microseconds = 10 ms
```

and schedules a volume ramp to zero.

Definition 580's track explicitly sets:

- track volume `0x67` = 103;
- track pan `0x40` = center.

Subpatch 263 also has centered pan `0x40`, full-range note velocity/volume bytes `0x7F`, and the note-on itself uses velocity `0x7F`. The retail start path combines these values and passes the resulting volume/pan with the calculated pitch ratio and waveform pointer to `0x80097010`.

The argument layout and behavior of `0x80097010` match the standard N64 `alSynStartVoiceParams` / `n_alSynStartVoiceParams` role: wavetable, floating-point pitch ratio, volume, pan, effects mix, and attack time are queued to the synth/mixer. External libultra source is used only to name/corroborate the API semantics; the MKT-specific values above come from retail disassembly.

**Consequence:** the user's rejection of the prior waveform-262 WAV does not contradict the retail selection trace. That WAV omitted the required `-2253`-cent runtime correction and played the stream about 3.67× too fast. The next bounded validation is to generate a pitch-corrected waveform-262 WAV using the retail ratio `0.272154916` and have it auditioned before any further MKMSZ proof is built.


### Source-to-retail selector anchor map

**Static-confirmed mapping evidence; individual Dan Forden waveform identities remain pending direct listening confirmation.**

A content-first comparison of the preserved Midway `triple_sndtab` against the retail MKT USA Rev. 2 primary selector table at `0x800A1AA8` shows that the early selector-slot layout is preserved even though the underlying sound/event IDs were rebuilt for N64.

Useful anchors:

| Selector slot | Preserved source meaning | Retail selector value | Evidence |
|---:|---|---:|---|
| `0x08` | subway approaching | `0x01B1` | contiguous source semantic group maps to contiguous retail SSEQ IDs |
| `0x09` | subway steady state | `0x01B2` | same group |
| `0x0A` | subway going away | `0x01B3` | same group |
| `0x0C` | P1 cursor | `0x016F` | four-slot cursor/pick group remains contiguous |
| `0x0D` | P2 cursor | `0x0170` | same group |
| `0x0E` | P1 picked | `0x0171` | same group |
| `0x0F` | P2 picked | `0x0172` | same group |
| `0x10` | Shao Kahn: Fight! #3 | `0x0244` | **direct audio validation:** user identified the correctly pitch-reconstructed retail event as “Fight!” |
| `0x11` | Round One | `0x0240` | five-entry Fight/Round cluster |
| `0x12` | Round Two | `0x0241` | same cluster |
| `0x13` | Round Three | `0x0242` | same cluster |
| `0x14` | Round Four | `0x0243` | same cluster |
| `0x15` | Finish Him! | `0x0164` | paired retail IDs |
| `0x16` | Finish Her! | `0x0165` | paired retail IDs |

This establishes a much safer rule for this prefix of the table: **the semantic selector slot is preserved, while the numeric sound/SSEQ ID stored in that slot is platform-specific.**

The earlier attempt to identify Toasty from a retail `randper(40)` branch is therefore **Rejected as an identification method**. Its downstream selector `0x10` is the preserved Fight slot, and the user directly identified the resulting pitch-corrected waveform as “Fight!”. The branch match was wrong even though the downstream audio trace was internally correct.

#### Dan Forden selector trio

The preserved source table contains:

```text
slot 0x1B -> DF: toasty
slot 0x1C -> DF: frosty
slot 0x1D -> DF: crispy
```

More strongly, preserved `MKFX.ASM` explicitly sets:

```text
movi 01bH,a11    ; sound: toasty
...
move a9,a0
calla triple_sound
```

so source Toasty’s selector slot is unambiguous.

The corresponding retail primary-table entries are:

```text
slot 0x1B -> event 0x0160
slot 0x1C -> event 0x018E
slot 0x1D -> event 0x0188
```

Tracing those three retail SSEQ definitions:

| Source semantic | Retail slot | Retail event | Initial/current patch | Subpatch | Waveform | Pitch correction |
|---|---:|---:|---:|---:|---:|---:|
| Toasty candidate | `0x1B` | `0x0160` | 65 | 111 | 77 | `-2253` cents |
| Frosty candidate | `0x1C` | `0x018E` | 66 | 112 | 78 | `-2253` cents |
| Crispy candidate | `0x1D` | `0x0188` | 67 | 113 | 79 | `-2253` cents |

All three definitions are simple one-track, one-note events with note/root key `0x3C`; no intermediate program-change ambiguity exists. Their retail waveform spans are:

- waveform 77: ROM `0xB0FBFC..0xB10411`;
- waveform 78: ROM `0xB10412..0xB10D1B`;
- waveform 79: ROM `0xB10D1C..0xB11891`.

Pitch-corrected WAV candidates were generated for direct listening. Do not promote the semantic waveform identities to Runtime-confirmed until the user auditions them. The selector/event mapping itself is substantially stronger than the discarded branch-first method because it is anchored by preserved slot semantics plus the user-confirmed retail `0x10 = Fight!` control.


### Audibly confirmed retail Toasty voice

**User-audition confirmed on 2026-09-22.** The source-slot correlation method successfully identified the actual retail MKT Toasty voice without relying on the previously misleading `randper(40)` branch.

Preserved source `triple_sndtab` identifies:

```text
slot 0x1B -> DF: toasty
slot 0x1C -> DF: frosty
slot 0x1D -> DF: crispy
```

The retail primary selector table preserves those slot positions in this anchored region. The user listened to the pitch-corrected retail candidate from source slot `0x1B` and explicitly confirmed that it is the desired Dan Forden **“Toasty!”** voice.

Confirmed retail chain:

```text
source selector slot 0x1B
  -> retail primary selector slot 0x1B
  -> retail event 0x0160
  -> SN64 patch 65
  -> subpatch 111
  -> waveform 77
```

Waveform 77 uses the same `-2253`-cent retail correction that must be applied at playback. The user-confirmed standalone WAV is:

`MKT_slot-1b_toasty-candidate_wave77_pitch-corrected.wav`

This supersedes the rejected candidates:
- reverse-cymbal waveform from the earlier incorrect patch-7 route;
- `Fight!` waveform 262 reached from retail selector slot `0x10`.

**Implementation consequence:** future MKMSZR Toasty sound proofs should use only the confirmed slot-`0x1B` / event-`0x0160` / patch-65 / subpatch-111 / waveform-77 voice. Frosty and Crispy are not required for the current feature.


### Toasty sound proof v03 — runtime confirmed

Disposable proof: `MKMSZR_toasty-sound_common-proof_v03.z64`.

**Runtime-confirmed on 2026-09-22.** The user reported that the proof worked perfectly: collecting the tested ordinary pickup produced the correct audibly confirmed MKT Dan Forden “Toasty!” voice.

The proof keeps MKMSZ's stock pickup event/SSEQ route and isolated patch ownership, but replaces the proof-only subpatch/waveform host with the confirmed donor Toasty data:

```text
MKT source selector 0x1B
  -> retail event 0x0160
  -> patch 65
  -> subpatch 111
  -> waveform 77
  -> retail correction -2253 cents
```

This runtime-confirms:
- MKT waveform 77 and its predictor metadata are binary-compatible with MKMSZ's SN64 audio path when transplanted correctly;
- the `-2253`-cent waveform correction is required and plays correctly through MKMSZ's native pitch path;
- a genuine MKT speech sample can coexist with normal MKMSZ gameplay audio on the tested route.

The v03 pickup replacement is still a disposable routing proof, not final Toasty product behavior. Production should allocate a dedicated safe audio definition/route and invoke it from the final cosmetic Toasty trigger rather than replacing the ordinary-pickup sound.

## Related canonical owners

- [Audio system](Sounds-and-Music) — MKMSZ host SFX/definition architecture and music status.
- [Function registry](Function-Registry) — canonical function semantics.
- [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer) — donor compatibility strategy; Toasty chronology no longer lives there.
- [Runtime validation status](Runtime-Validation-Status) — concise evidence summary.
- [Project status](Project-Status) — current maturity only.
- [Toasty visual research](Toasty-Visual-Research) — visual proof chronology and final visual composition boundary.

### v41 feature-core composition

**Implementation/static-confirmed; runtime pending.**

v41 composes the Runtime-confirmed v03 voice with the compact Toasty visual state machine. The voice is invoked once when the six-tick slide-in completes and the 32-tick hold begins.

This does **not** yet solve production audio routing. The disposable proof deliberately reuses v03's event-524/subpatch host, so ordinary pickup playback is also redirected to Toasty in v41. The purpose is only to validate audio/visual timing and lifecycle together before the final trigger work. A dedicated production-safe audio definition/route is still Pending.


### Toasty dedicated-audio proof v46 — runtime confirmed

**Runtime-confirmed on 2026-09-25.** The user reported v46 works perfectly. The proof removes the disposable pickup-audio hijack and preserves the ordinary pickup chain byte-for-byte:

`descriptor 0x3B -> event 524 -> patch 681 -> subpatch 524 -> waveform 133`.

Toasty instead uses the isolated dedicated host:

`event 52 -> patch 68 -> subpatch 608 -> waveform 533`.

Waveform 533 carries the confirmed donor waveform-77 metadata/predictor/sample, including the required `-2253`-cent correction. This runtime result establishes both sides of the production audio boundary on the tested route: the genuine Toasty voice still plays correctly, and ordinary pickup sound is restored to vanilla behavior.

### v47 production-composition audio gate

**Runtime-confirmed on 2026-09-25.** The user reported the full current production-composition v47 ROM works perfectly. The v46 dedicated route remains intact, ordinary pickup audio remains stock, and no regression was reported in the exercised production systems. v47 used 500/1000 only to make this composition gate fast to validate. The merged production module changes only that tuning to the selected **80/1000 (8%)**; the dedicated event/patch/subpatch/waveform route and donor audio bytes are otherwise unchanged.


### Browser donor extraction

**Implementation/CI-confirmed.** The browser/CLI donor extractor validates the exact MKT USA Rev. 2 N64 ROM and derives the confirmed Toasty audio chain locally: deflated CTL at `0xA8F588`, subpatch-111 offset `0x0F8C`, waveform-77 offset `0x2F60`, predictor offset `0x9EB0`, and encoded sample `0xB0FBFC..0xB10411`. The extracted records are guarded against the Runtime-confirmed v46/v47 hashes before being translated into the dedicated MKMSZ host chain. No MKT audio bytes are stored in GitHub or the deployed site.
