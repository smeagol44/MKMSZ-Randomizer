# Audio system

> **Scope:** This page is the canonical owner for MKMSZ host audio behavior: native gameplay SFX routing, descriptor and runtime-definition architecture, call-chain behavior, stable host-bank conclusions, audio safety rules, and current music status.
>
> MKT Toasty donor identification, rejected candidates, source-to-retail mapping, and sound-proof v01-v03 chronology are canonical in [Toasty audio research](Toasty-Audio-Research). Function semantics remain canonical in [Function registry](Function-Registry); addresses are named here only to explain the audio call chain.

## Current conclusion

MKMSZ has a statically mapped native gameplay SFX path from a compact descriptor index through an event/raw-ID entry into runtime sound definitions and the lower voice allocator. The stock ordinary-pickup path is the best current control because its caller, descriptor, event namespace, and downstream patch/subpatch/waveform routing have all been traced.

The Toasty work additionally established a stable host-side compatibility result: MKMSZ can play imported MKT N64 ADPCM data with transplanted predictor metadata through the native audio engine when the event/patch/subpatch/waveform namespaces and pitch correction are translated correctly. That is a **Runtime-confirmed proof**, not a production allocation or final cosmetic trigger. See [Toasty audio research](Toasty-Audio-Research).

Music remains **Pending** as a general subsystem: the project has not mapped the complete MKMSZ music sequence/control API. The Toasty proofs exposed SSEQ/event and instrument-liveness behavior relevant to safe SFX work, but they do not constitute a full music-engine map.

## Current status

| Area | Status | Evidence and limit |
|---|---|---|
| Gameplay SFX wrapper | **Static-confirmed** | `0x80064C18` is widely called by stock gameplay code and resolves a descriptor before native playback |
| SFX descriptor table | **Static-confirmed** | 10-byte entries begin at VA `0x800A1730` / ROM `0x000A2330` |
| Raw/event playback entry | **Static-confirmed** | `0x80080A88` receives the resolved ID and selects a 16-byte runtime sound definition |
| Low-level voice allocation/start | **Static-confirmed** | `0x8007EC4C` consumes the resolved runtime definition |
| Ordinary-pickup control | **Static-confirmed** | descriptor `0x3B` resolves to event/raw ID `0x020C`; its SSEQ route reaches patch 681 / subpatch 524 / waveform 133 |
| Main MKMSZ SN64 bank grammar | **Static-confirmed** | control bank and waveform-table structure are parsed; exact host counts and bases are recorded below |
| Foreign MKT N64-ADPCM compatibility | **Runtime-confirmed proof** | Toasty v02 proves one-shot imported donor-sample playback; v03 proves the accepted Toasty voice and pitch metadata |
| Music engine / complete sequence-control API | **Pending** | only the bounded SSEQ/event behavior needed by the audio proofs is mapped |
| Production Toasty audio route | **Pending** | final trigger and production-safe allocation/composition are not integrated |

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

## Runtime definition and bank architecture

**Static-confirmed host facts established during the Toasty investigation:**

- MKMSZ main SN64 control bank: ROM `0x947C80`, control payload at `0x947CB8`, size `0x2F088`.
- MKMSZ waveform-data/TBL base: ROM `0x9B0650`.
- Parsed host bank: 683 event/raw IDs, 740 intermediate/subpatch records, and 598 waveform records.
- The runtime sound-definition records selected by `0x80080A88` are 16 bytes each before the lower voice path consumes them.
- For the stock ordinary-pickup control, descriptor `0x3B` selects event/SSEQ entry `0x020C` (524), whose single track starts on patch 681; patch 681 owns subpatch 524, which selects waveform 133.

The proof history also established an important namespace/liveness rule: an event/SSEQ index is not the same namespace as an SN64 patch number. Safe liveness analysis must include gameplay event references, every SSEQ track-header initial patch ID, in-stream program changes, and patch -> subpatch -> waveform sharing. A patch or waveform is not disposable merely because it is absent from descriptor tables or explicit in-stream program changes.

These are host-side architectural conclusions. Donor-specific selectors, MKT bank addresses, waveform identities, and v01-v03 chronology belong to [Toasty audio research](Toasty-Audio-Research).

## Function-semantics ownership

The audio chain above names `0x80064C18`, `0x80080A88`, `0x8007EC4C`, and `0x80015FD8` because their composition matters to the audio explanation. Their canonical meanings, evidence labels, and future semantic corrections are maintained only in [Function registry](Function-Registry); this page intentionally does not maintain a competing function table.

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

## Related canonical owners

- [Function registry](Function-Registry) — canonical function semantics.
- [Data structures and encodings](Data-Structures-and-Encodings) — stable shared record/codec grammar when promoted there.
- [Memory and allocation map](Memory-and-Allocation-Map) — production/proof ROM and RDRAM ownership.
- [Toasty audio research](Toasty-Audio-Research) — MKT donor identity, rejected traces, and v01-v03 proof chronology.
- [Toasty visual research](Toasty-Visual-Research) — visual-only Toasty diagnostics and current visual boundary.
- [Runtime validation status](Runtime-Validation-Status) — concise cross-domain evidence scope.
