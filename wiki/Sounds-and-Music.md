# Sounds & Music

This page owns MKMSZR research on the N64 game's sound-effect and music systems. The current scope is intentionally narrow: native gameplay SFX playback is partially mapped; music sequencing, sound-bank structure, sample compression/encoding, and foreign-sound import are still pending.

## Current status

| Area | Status | Evidence and limit |
|---|---|---|
| Gameplay SFX wrapper | **Static-confirmed** | `0x80064C18` is called widely by stock gameplay code and resolves a table entry before native playback |
| SFX descriptor table | **Static-confirmed** | 10-byte entries beginning at VA `0x800A1730` / ROM `0x000A2330` |
| Raw sound-ID playback | **Static-confirmed** | `0x80080A88` receives the resolved raw sound/sample ID and selects a runtime sound definition |
| Low-level voice allocation/start | **Static-confirmed** | `0x8007EC4C` consumes the resolved runtime definition |
| Ordinary-pickup SFX example | **Static-confirmed** | stock pickup callbacks use descriptor index `0x3B`, resolving to raw sound ID `0x020C` |
| Music engine / sequence format | **Pending** | not yet mapped |
| ROM sound-bank/sample format | **Pending** | not yet decoded |
| Importing an MKT sound into MKMSZ | **Pending** | no compatibility claim yet |
| Runtime custom-sound proof | **Pending** | no MKMSZR-authored sound call has yet been runtime-tested |

## Native gameplay SFX path

The currently mapped host path is:

```text
gameplay caller
    |
    | descriptor index
    v
0x80064C18  native gameplay SFX wrapper
    |
    | 10-byte descriptor from 0x800A1730
    v
0x80080A88  raw sound-ID playback entry
    |
    | resolved 16-byte runtime sound definition
    v
0x8007EC4C  low-level definition / voice allocator
```

The wrapper at `0x80064C18` is a general gameplay facility rather than a one-off effect path. Static call-site scanning finds hundreds of direct uses in the clean USA Rev. 0 ROM, including ordinary pickup callbacks.

## SFX descriptor table

The descriptor table begins at:

- VA `0x800A1730`
- ROM `0x000A2330`

Each entry is exactly 10 bytes:

| Offset | Size | Meaning | Status |
|---:|---:|---|---|
| `+0x00` | 2 | native raw sound/sample ID | **Static-confirmed** |
| `+0x02` | 1 | high byte not consumed by the mapped wrapper path | **Static-confirmed observation; semantic meaning pending** |
| `+0x03` | 1 | base primary sound parameter | **Static-confirmed** |
| `+0x04` | 2 | random variation magnitude for the primary parameter | **Static-confirmed** |
| `+0x06` | 2 | base secondary parameter | **Static-confirmed** |
| `+0x08` | 2 | random variation magnitude for the secondary parameter | **Static-confirmed** |

The random-variation helper used by this path is `0x80015FD8`. Static analysis shows it produces a roughly symmetric signed variation around the supplied base value. Exact gameplay semantics for the two parameters are not yet named; do not label them as volume, pitch, pan, or another conventional audio property until caller/runtime evidence establishes that meaning.

## Worked stock example: ordinary pickup sound

Several stock pickup callbacks call:

```text
a0 = 0x3B
a1 = 0
a2 = 0x40
jal 0x80064C18
```

Descriptor `0x3B` is located at ROM `0x000A257E` and contains:

```text
02 0C 00 7F 00 00 00 00 00 00
```

Decoded through the currently mapped structure:

- raw sound ID: `0x020C`
- primary base parameter: `0x7F`
- primary variation: `0`
- secondary base parameter: `0`
- secondary variation: `0`

This is the current reference control for future custom-SFX experiments because the full stock route from gameplay event to native playback is known.

## Function registry

Canonical function entries are maintained in [Function registry](Function-Registry):

| Address | Meaning |
|---:|---|
| `0x80064C18` | native gameplay SFX wrapper |
| `0x80080A88` | raw sound-ID playback entry |
| `0x8007EC4C` | low-level sound-definition / voice allocator |
| `0x80015FD8` | random-variation helper used by the SFX wrapper |

This page owns the audio-system explanation; the registry remains the compact address index.

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

Therefore the **retail MKT Toasty sound-table index is `0x10`**, not source identifier `0x1095`.

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

## Music

**Pending.** No current MKMSZR research establishes the N64 music sequence format, track table, streaming model, bank ownership, or runtime music-control API. Sound effects and music should therefore remain separate research tracks until evidence shows which lower-level components they share.

## Safety and implementation boundary

For a future custom-sound proof:

- keep the clean ROM untouched and build a separate guarded output;
- guard all edited table entries and storage ranges;
- do not overwrite an existing sound/sample solely because its numeric ID looks unused;
- resolve ROM offsets versus runtime pointers and any bank-relative addressing before patching;
- preserve existing voice/channel behavior unless the experiment specifically targets it;
- treat donor IDs and definitions as semantic references, not binary-compatible records;
- perform a bounded manual runtime test before integrating any new audio path into the normal pipeline.

A successful call to an existing MKMSZ sound does **not** by itself prove that foreign-sample import is safe; the sample/bank format and lifetime must be validated separately.


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
