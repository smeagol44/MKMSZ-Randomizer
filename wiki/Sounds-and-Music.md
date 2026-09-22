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

This completes the donor-side `0x0244` → CTL/TBL waveform trace. No MKMSZ transplant compatibility is claimed by this section.

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
