# Audio system

**Native AI closed-loop phase audit (2026-10-09): full captured-event confirmation, root-cause correction Pending.** Across 5 complete RMG traces (7–11), reproduced **59,489/59,489 AI_LEN** reads from DMA head length/duration/CP0 deadline and **58,971/58,971 native PCM buffer sizes** from the preceding AI_LEN; all **513** failed enqueue sizes infer 352 frames from the same native recurrence. Severe first-failure queued tail is ~3,784–4,486 Count *late* at the next audio service; isolated recoveries have >30,500 Count spare. Trace 11's 79th consecutive rejection is followed by audio recovery when AI END occurs **18 Count** after the first FULL-status read, before diagnostic logger's second status read, changing subsequent AI_LEN to 1,464B. This establishes an exact FIFO deadline/feedback bifurcation in the observed pinned emulator, and makes a spontaneous corrupted AI_LEN unlikely as a necessary cause of those traces. It does not prove the earlier guest scheduling trigger or rule out other memory faults; logger timing impacts the exit. The proposed rational-duration observer experiment lengthens 368-frame DMA and could worsen FIFO occupancy, so is not a ready fix. See [audio investigation](Production-Rich-Inventory-Music-Static-Investigation).\n\n**Vanilla ROM audio control (2026-10-09): stock also produces FIFO FULL; repeated failure remains MKMSZR-composition-specific.** Five genuine stock guest FIFO FULLs in ~321s and 40 host SDL queue drops were recorded without audible speed-up. Stock and mod run identical 551 Count/byte emulator DMA duration. One vanilla three-FULL cluster begins with the exact head/tail sizes of MKMSZR's 73-FULL runaway (1600/1472 then 2816/1472), but vanilla's third tail is 1408 rather than 1472 and it recovers. Vanilla has no long all-368-frame output streak (maximum four consecutive) compared to MKMSZR ~40s 368-only precursors. An early-truncated emulator DMA clock likely contributes to shared host clipping, **but is not sufficient by itself** for sustained mod-only runaway. Do not interpret the absence of an audible stock failure as zero stock FIFO rejections or as proof of corrupting guest RAM. See [canonical audio investigation](Production-Rich-Inventory-Music-Static-Investigation).\n\n**RMG v0.9.0 AI DMA timing precision candidate (2026-10-09): emulator-static confirmed, production cause Pending.** `get_dma_duration` uses `AI_LEN*(cpu_counts_per_sec/(4*sample_rate))` with early integer truncation: observed duration 551 Count/byte for all accepted Trace (5)/(6)/(7)/normal-controls, whereas fractional Count/byte is ~551.838 at 22,047Hz. 368-frame DMA consumes 811,072 Count versus nominal VI 811,092; guest AI output rate is ~22,080.54 frames/s but host plays 22,047Hz, predicting ~134 bytes/second SDL queue buildup (~133 B/s observed). Trace (6)/(7) both show nearly 40 seconds of consecutive 368-frame outputs and AI_LEN 1,344→1,280 before the first rejected submission. This explains an RMG host clipping mechanism and strongly implicates slow phase feedback, **but** is not verified as the sole source of guest FIFO bursts or all historical corrupted audio. The ROM's native audio frame builder is byte-identical to clean; emulator-only controlled A/B is staged in [draft PR #161](https://github.com/smeagol44/MKMSZ-Randomizer/pull/161), not a native production fix. See [focused investigation](Production-Rich-Inventory-Music-Static-Investigation).\n\n**Native music upstream investigation (2026-10-09): head/tail FIFO feedback bifurcation reconstructed; initial trigger and permanent correction Pending.** The diagnostic pair has +135 rejected outputs, +4,934 audio and VI services, and +47,616 synthesized samples beyond the nominal target. Native synthesis/WESS advance despite failed enqueue. The new paired host traces establish why the feedback loop sometimes runs away: the queued tail's drain deadline falls just after (Trace 5) or well before (Trace 6) the next service, causing the same 704-frame generation to be queued behind a busy head with AI_LEN=0, or started in an empty FIFO with AI_LEN≈2808. All accepted DMA durations use 551 Count/byte; 368 frames correspond to 811,072 Count against VI=811,092 Count. No responsible Inventory operation or original initial-phase perturbation is recovered. The inspected RMG v0.9.0 source distinguishes emulated AI consumption, ParaLLEl task timing and possible host audio fragment drops; the maintainer's installed build/audio plugin still need pinning. No retry correction is justified. See [native schedule, quantitative limits and minimum observation](Production-Rich-Inventory-Music-Static-Investigation).

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
| Production Toasty audio route | **Runtime-confirmed production composition** | Dedicated event `52 -> 68 -> 608 -> 533` is integrated; stock pickup audio remains untouched |

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


## Seeded Temple intro audio

The Temple intro has two independently validated audio positions. The opening spoken position chooses stock descriptor `0x41` (“You will fail”) or `0x42` (“I will succeed”) through the stock persistent alternation at `0x800AA8A4`; the later position uses descriptor `0x43` for Scorpion's laugh. The relevant Temple-overlay immediates are ROM `0xCB274`, `0xCB280`, and `0xCB2F8`.

Bounded manual proofs established both replacement seams:

- **Audio 2:** v02 replaced only the Temple `0x43` call with an imported MKT Shao Kahn laugh while forcing a known stock first line; runtime playback was accepted. Later Raiden and robot-run donor clips were auditioned and the same Audio-2 route was accepted.
- **Audio 1:** v05 redirected both stock first-line branches to an imported Raiden BBB clip while leaving `0x43` completely stock; runtime playback was accepted.

The production contract is seed/build-time deterministic rather than runtime-random. When a valid MKT USA Rev. 2 N64 donor is supplied, the isolated domain `MKMSZR:TEMPLE-INTRO-AUDIO:V1\0` chooses exactly one position and then one clip from that position's pool. The other position stays stock. With no MKT donor, the Temple-audio patch is omitted entirely.

Approved **Audio 1** pool:

- Shao Kahn “Friendship!” (`TS_SK_FRIEND`; the alternate Friendship take is intentionally excluded)
- Shao Kahn “Choose Your Destiny” (`TS_SK_CHOOSE`)
- Shao Kahn “Excellent” (`TS_SK_EXCELLENT`)
- Shao Kahn “Superb” (`TS_SK_SUBERB`)
- Shao Kahn “Well Done” (`TS_SK_WELL_DONE`)
- Liu Kang bicycle-kick vocal (`ST_LK_BIKE`)

Approved **Audio 2** pool:

- Raiden torpedo BBB / SSS / TTT (`ST_RD_BBB`, `ST_RD_SSS`, `ST_RD_TTT`)
- robot run (`GS_RUN_ROBO`)
- Shao Kahn laugh

Only the selected encoded sample is materialized into the output ROM; the complete pool is never copied into one build.

### Production carrier and proof-carrier correction

The early Temple proofs used descriptor `0x220 -> event 0x1B8 -> patch 597 -> subpatch 440 -> wave 430`. That route is **proof-only**: a later whole-ROM audit found live stock callers loading descriptor `0x220` around ROM `0xBE744/0xBE750/0xBFACC`, including calls into `0x80064C18`. Reusing it in production could therefore alter unrelated stock audio.

Production instead uses the statically isolated chain:

`descriptor 0x20A -> event 0x1A6 -> patch 579 -> subpatch 422 -> wave 412`.

Clean-ROM analysis found no direct descriptor/event immediates for `0x20A/0x1A6`, and the event -> patch -> subpatch -> waveform ownership is unique. The selected donor event/subpatch/wave/predictor metadata is rebased into that chain. The selected ADPCM sample owns conditional high-ROM reservation `[0xF6BDF0,0xF6D810)`, immediately after the production Toasty sample region. **v06 Runtime-confirms this production carrier/allocation composition:** seed `TEMPLE-PROD-CARRIER` selected Audio 1 / Friendship and the user observed the expected **“Friendship!” followed by the untouched stock Scorpion laugh**. Proof ROM SHA-256 is `9460d923b9c1cecf2d481e36719f7249231944eeecc7e2c300dd95a4809085c6`; builder SHA-256 is `d529e212f667ebd6f4724b03d7cb828e726b4f9c9d4ab897856db46ae5f6a102`. This is bounded confirmation of the production carrier and one Audio-1 pool member, not exhaustive runtime coverage of all 11 approved clips.

The attempted MKT retail `TS_SK_ITS_OFFICIAL` / `skyousuk` lookup is excluded from the pool. User audition showed the retail waveform reached through that surviving identity is an unrelated short impact-like sound. Older Midway sources show the complete phrase was assembled from separate `skofficl` then `skyousuk` material; recovering that phrase remains optional future pool work.

## Music

**Partially mapped, broader behavior Pending.** The [2026-10-08 production Inventory investigation](Production-Rich-Inventory-Music-Static-Investigation) statically/snapshot-confirms bounded WESS track/voice structures, current Fortress sequence data, bank/sample-cache ownership, and the synthesis-to-AI call path. It does not establish the complete sequence/control API, all sequence command semantics, or the accelerated-music cause. Preserve the distinction between bounded native evidence and a general subsystem closure.

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
