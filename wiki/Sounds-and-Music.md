# Audio system

**New v05 selector-only audio origin constraint (2026-10-10):** Complete guest PIF/AI/VI/RSP/phase/SDL capture identifies **299 recurring native PCM enqueue failures**, including **169 before the first Fortress stage-9 sample**; first t36.496, head/tail 1,600/1,472B, promoted tail ends **4,746 Count after** next service. 5,860 SDL fragment pushes all succeed, zero SDL threshold drops. Synth surplus during rejection regime **105,248 = 299 × 352** sample frames, consistent with native producer advancing despite rejected PCM. Frontend initiator still Pending; no descriptor-0x1FC or palette accusation, no production correction. [Audio owner](Production-Rich-Inventory-Music-Static-Investigation#rmg-v05-selector-pre-stage-native-fifo-failure--trace-confirmed-2026-10-10).

**Stress-run v05 audio negative 2026-10-10:** An independently longer ~598s Fortress test with walk/combat/healing/box-switch/rapid cursor never accelerated continuously (maintainer observed occasional brief crunch), despite 612 combined Up/Down press edges. Lossless native AI has only **18 distinct FIFO-rejected PCM submissions**; maximal cluster 5 over 0.266s. Retained SDL host queue has **at least 59 drops** (beginning overwritten; 23 occur >last user input). Three 368-frame-only healthy spans ~44.8s, 40.0s and **38.5s with zero buttons** all show `AI_LEN` lower band 1344→1288. Even `AI_LEN=1216` occurs 29 times and 1,600-byte PCM is accepted 30 times without sustained runaway. This refutes both cursor sweep and `AI_LEN=1216` as **sufficient** causes; they may still affect eventual FIFO phase selection. In complete retained VI tail 32,768/32,768 active audio polls and 32,767/32,767 sample-clock steps match. Enemy Grunt update/aggro cannot be inferred from PIF/RSP/VI/phase streams; no guest actor tracer was run. See [negative control](Production-Rich-Inventory-Music-Static-Investigation#long-rmg-v05-stress-negative-control-and-off-screen-grunt-hypothesis-2026-10-10).\n\n**v05 input-aligned fast PCM dropout (2026-10-10) — user Runtime-observed, numeric trace-confirmed.** The original PIF controller answers for 1,594 input polls prove Up/Down navigation (39 Down + 34 Up before first rejection) preceded the next rapid audio failure. Z response t38.786 probably entered Inventory; repeated navigation starts t39.711; first AI_LEN=1216 t62.093997, first 1,600B synthesis t62.111, first native FIFO FULL t62.544 (1,600B head/1,472B queued tail). Queued tail ends **4,056 Count after next native service** (prior v04 fast −4,126), triggering 86 rejected PCM submissions over 5.734s, accepted interleaved among failures. No SDL host queue-threshold drop occurs; this recording demonstrates clipping with native PCM omission even without host queue overflow. Synth frames +23.54% vs 368-frame target over 345 services. Rejections continue 4.883s **after all inputs release**, so cursor motion is not required for maintenance of the feedback fault. An 8B lower-AI_LEN staircase advances every ~4.804s from 1,256 to 1,216 after Inventory activity, consistent with 15.29 Count/VI phase creep; nearest later Up edge **cannot** have caused the AI_LEN=1216 already sampled. **No specific Inventory-open, cursor renderer/SFX, or producer-state writer is proven as original cause.** See [native event proof](Production-Rich-Inventory-Music-Static-Investigation#rmg-v05-first-input-aligned-rapid-inventory-speedup-2026-10-10).\n\n**Precisely quantified RMG v04 deadline fork (2026-10-10):** With pinned 551 Count/PCM byte and 811,092 Count/VI, 352/368/384-frame DMA durations are 775,808 / **811,072** / 846,336 Count; 368 frames finish only **20 Count before nominal next VI**. Clean and slowdown runs had healthy ~40s 368-only plateaus; observed AI END spacing ~811,077.4/811,077.8 versus 811,092 for audio services naturally drives the 1,344→1,280-byte AI_LEN quantization staircase. Slow onset queued 1,408B finishes **35,580 Count before next service**, leading to ~35,226 median empty-FIFO gap and 352-only generated outputs. Fast onset queued 1,472B finishes **4,126 Count after** next service; counterfactual 1,408B would finish 31,138 Count before. These are timing-conditional native-feedback attractors, **not established initial game bug or proven hardware-portable repair**. The burst's 81 failed *submission events* recur approximately every fourth service, interspersed with accepted output. See [full v04 fork proof](Production-Rich-Inventory-Music-Static-Investigation#quantified-v04-dma-deadline-bifurcation-and-healthy-resonance-2026-10-10).\n\n**New bidirectional audio feedback evidence, 2026-10-10 — three RMG v04 sessions:** The same native AI_LEN-sampled buffer-size rule enters distinct output basins while clock and producer ownership remain intact. Slow audible episode: 2,303 consecutive accepted 352-frame buffers after a rejected service (plus one preceding accepted 352-frame output), spanning 38.4s overall, AI_LEN stays 1,400 bytes and SDL host queue falls to median 504B (threshold 17,637B); one AI END interrupts native FULL read after just **10 CP0 Count** and the following FIFO-only-BUSY regime persists without repeated rejects. Fast audible episode: 81 rejected enqueues over 5.334s, interspersed among ~240 successful services, producer sample clock advances **~23.8% faster** than nominal per-VI target while guest PCM gets skipped, with host queue median 16,600B and four threshold drops. A clean 6m20 run itself contains ~39.77s **all-368-frame output** without perceived acceleration, so that plateau is not a sufficient failure flag. **Observed native sample-time rates do not directly measure audible pitch/tempo.** All 52,316 new phase snapshots retain the same startup DAC/target constants and pointers; 52,313 synth clock increments exactly match prior Info frame sizes. This establishes opposing *downstream* low-/high-supply regimes, not the earliest triggering operation, nor a safe production fix. See [full causal evidence and caveats](Production-Rich-Inventory-Music-Static-Investigation#three-matched-v04-observer-captures-healthy-vs-slowdown-vs-speedup-2026-10-10).\n\n**Native AI closed-loop phase audit (2026-10-09): full captured-event confirmation, root-cause correction Pending.** Across 5 complete RMG traces (7–11), reproduced **59,489/59,489 AI_LEN** reads from DMA head length/duration/CP0 deadline and **58,971/58,971 native PCM buffer sizes** from the preceding AI_LEN; all **513** failed enqueue sizes infer 352 frames from the same native recurrence. Severe first-failure queued tail is ~3,784–4,486 Count *late* at the next audio service; isolated recoveries have >30,500 Count spare. Trace 11's 79th consecutive rejection is followed by audio recovery when AI END occurs **18 Count** after the first FULL-status read, before diagnostic logger's second status read, changing subsequent AI_LEN to 1,464B. This establishes an exact FIFO deadline/feedback bifurcation in the observed pinned emulator, and makes a spontaneous corrupted AI_LEN unlikely as a necessary cause of those traces. It does not prove the earlier guest scheduling trigger or rule out other memory faults; logger timing impacts the exit. The proposed rational-duration observer experiment lengthens 368-frame DMA and could worsen FIFO occupancy, so is not a ready fix. See [audio investigation](Production-Rich-Inventory-Music-Static-Investigation).\n\n**Vanilla ROM audio control (2026-10-09): stock also produces FIFO FULL; repeated failure remains MKMSZR-composition-specific.** Five genuine stock guest FIFO FULLs in ~321s and 40 host SDL queue drops were recorded without audible speed-up. Stock and mod run identical 551 Count/byte emulator DMA duration. One vanilla three-FULL cluster begins with the exact head/tail sizes of MKMSZR's 73-FULL runaway (1600/1472 then 2816/1472), but vanilla's third tail is 1408 rather than 1472 and it recovers. Vanilla has no long all-368-frame output streak (maximum four consecutive) compared to MKMSZR ~40s 368-only precursors. An early-truncated emulator DMA clock likely contributes to shared host clipping, **but is not sufficient by itself** for sustained mod-only runaway. Do not interpret the absence of an audible stock failure as zero stock FIFO rejections or as proof of corrupting guest RAM. See [canonical audio investigation](Production-Rich-Inventory-Music-Static-Investigation).\n\n**RMG v0.9.0 AI DMA timing precision candidate (2026-10-09): emulator-static confirmed, production cause Pending.** `get_dma_duration` uses `AI_LEN*(cpu_counts_per_sec/(4*sample_rate))` with early integer truncation: observed duration 551 Count/byte for all accepted Trace (5)/(6)/(7)/normal-controls, whereas fractional Count/byte is ~551.838 at 22,047Hz. 368-frame DMA consumes 811,072 Count versus nominal VI 811,092; guest AI output rate is ~22,080.54 frames/s but host plays 22,047Hz, predicting ~134 bytes/second SDL queue buildup (~133 B/s observed). Trace (6)/(7) both show nearly 40 seconds of consecutive 368-frame outputs and AI_LEN 1,344→1,280 before the first rejected submission. This explains an RMG host clipping mechanism and strongly implicates slow phase feedback, **but** is not verified as the sole source of guest FIFO bursts or all historical corrupted audio. The ROM's native audio frame builder is byte-identical to clean; emulator-only controlled A/B is staged in [draft PR #161](https://github.com/smeagol44/MKMSZ-Randomizer/pull/161), not a native production fix. See [focused investigation](Production-Rich-Inventory-Music-Static-Investigation).\n\n**Native music upstream investigation (2026-10-09): head/tail FIFO feedback bifurcation reconstructed; initial trigger and permanent correction Pending.** The diagnostic pair has +135 rejected outputs, +4,934 audio and VI services, and +47,616 synthesized samples beyond the nominal target. Native synthesis/WESS advance despite failed enqueue. The new paired host traces establish why the feedback loop sometimes runs away: the queued tail's drain deadline falls just after (Trace 5) or well before (Trace 6) the next service, causing the same 704-frame generation to be queued behind a busy head with AI_LEN=0, or started in an empty FIFO with AI_LEN≈2808. All accepted DMA durations use 551 Count/byte; 368 frames correspond to 811,072 Count against VI=811,092 Count. No responsible Inventory operation or original initial-phase perturbation is recovered. The inspected RMG v0.9.0 source distinguishes emulated AI consumption, ParaLLEl task timing and possible host audio fragment drops; the maintainer's installed build/audio plugin still need pinning. No retry correction is justified. See [native schedule, quantitative limits and minimum observation](Production-Rich-Inventory-Music-Static-Investigation).

> **Scope:** This page is the canonical owner for MKMSZ host audio behavior: native gameplay SFX routing, descriptor and runtime-definition architecture, call-chain behavior, stable host-bank conclusions, audio safety rules, and current music status.
>
> MKT Toasty donor identification, rejected candidates, source-to-retail mapping, and sound-proof v01-v03 chronology are canonical in [Toasty audio research](Toasty-Audio-Research). Function semantics remain canonical in [Function registry](Function-Registry); addresses are named here only to explain the audio call chain.

## Vanilla audio FIFO speed-up — root cause and fix (2026-11-06)

**Root cause Static-confirmed + Hypothesis/strong inference (model); vanilla reproduction and fix Runtime-confirmed bounded.** The long-running music speed-up / crunch is a **stock game defect**, not an MKMSZR composition fault. Each VI, `0x8007D4A8` first submits the previous PCM buffer to the two-slot AI FIFO (`0x8008A500`; full returns `-1` and the buffer is dropped), then reads `AI_LEN` (head remainder only) and sizes the next buffer as `max(352, ((368 - (AI_LEN >> 2) + reserve) & ~15) + 16)`. Target 368 and minimum 352 are derived at audio init from the DAC rate and refresh; the maximum is `target + reserve + 16`. The reserve (320) is written into the boot audio config by one immediate, `addiu v0,zero,0x140` at VA `0x80001354` / ROM `0x1F54` (caller `0x800012EC` → config apply `0x8007DA60`, flags `0x16B` with bit `0x8`, field `+0x10`). That keeps the FIFO nearly full with only about 1–3 ms of headroom: whenever the next submission still finds both slots occupied, the buffer is dropped while the synthesizer and WESS sequence have already advanced, so music runs ahead and effects crackle. Under RMG's integer AI timebase a 368-sample buffer is 20 Count shorter than one VI, so the loop drifts across its 16-sample steps very slowly and lingers near that edge, where tiny jitter tips it into bursts.

An exact closed-loop model of this rule (two-slot AI FIFO, pinned RMG timing of 551 Count/byte and 811,092 Count/VI, measured service jitter of about ±400 Count) reproduces every regime in the existing traces: healthy 368-sample plateaus, the 352-sample "slowdown" lock, isolated rejections roughly every 30 s (as in vanilla Trace 8), and random, minutes-long rejection bursts ("speed-up"). In the same model, reserve 288 or lower removes every burst with no AI starvation, including other AI/VI ratios and ±20,000-Count jitter; an extreme artificial case (1% of services up to a quarter-frame late) still drops some buffers at every reserve, fewer at lower ones.

**Runtime evidence (maintainer, 2026-11-06):** the speed-up reproduced in the **unmodified vanilla USA Rev. 0 ROM** while idling at the password screen. Proof `MKMSZR_audio-reserve-272_all-stages_proof_v01.z64` (production build of `main` `4646a69`, seed `AUDIORESERVE01`, MKT donor, plus reserve 320 → 272; SHA-256 `47da43ef6f3dddf11e7652c60d94fe3ee5c4aa3740ce5f230c0553b4fe077740`) ran the same idle scenario plus the usual triggers without any speed-up. The maintainer heard occasional very short "pops", at worst about every 20 s and sometimes none for minutes, and judged them acceptable; their source (model gap, host audio, or pre-existing) is Pending.

**Production fix:** `AudioFifoReservePatch` (`src/mkmszr/patches/audio_fifo_fix.py`) changes that one guarded immediate to 272 (`0x24020110`), restoring three 16-sample steps of headroom while keeping about 12 ms of queued audio. It is **on by default**; **Debug options → Disable vanilla audio fix** (browser) or `--no-audio-fifo-fix` (CLI) keeps the stock value. Side effects: about 2 ms less audio latency, maximum buffer 704 → 656 samples, and slightly smaller audio-heap PCM records, so hard-coded audio-heap addresses in research tooling (for example AudioInfo `0x8013A780`) shift in builds with the fix. No production MKMSZR code references that heap. History: [rich Inventory music investigation](Production-Rich-Inventory-Music-Static-Investigation).

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
| Vanilla audio FIFO speed-up | **Root cause identified; production fix Runtime-confirmed bounded (2026-11-06)** | Stock reserve 320 leaves ~1–3 ms FIFO headroom; fix lowers it to 272 (ROM `0x1F54`). See the section above |
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

## Isolated sound host chains (2026-11-07)

**Static-confirmed by a conservative clean-ROM audit; one chain Runtime-confirmed as a host (Sektor teleport proof v09).** Imported donor sounds need an event → patch → subpatch → waveform chain that no stock path can reach. The audit establishes these bank facts:

- **SSEQ block:** header at ROM `0x976D40`, with 590 events and 16-byte definitions at `0x976D60`: `u16` track count, then length and offset relative to the track base `0x979240`.
- **Single-track events:** a `0x14`-byte header (initial patch first, stream length at `+0x10`) followed by the stream; most SFX events are exactly `0x20` bytes.
- **Bank tables:** patches at `0x947CB8` (684 × 4 bytes: subpatch count, first subpatch), subpatches at `0x948768` (740 × 20 bytes, waveform at `+0x0A`), waveforms at `0x94C138` (24 bytes) and predictor books at `0x950490` (264 bytes).
- **Descriptor table:** 564 entries (`0x000..0x233`); per-type halfword index tables follow it.

A chain counts as isolated only if all of these hold:
- The event is not the raw ID of any descriptor. The test conservatively reads `0x300` entries, so the following tables count too.
- The event is not an immediate `a0` at any of the 43 `jal 0x80080A88` sites in the ROM.
- It is a single `0x20`-byte track.
- Its initial patch number appears nowhere else in the sequence data as a 16-bit value. This over-approximates in-stream program changes and multi-track headers.
- The patch owns exactly one subpatch, which only that patch owns, and that subpatch's waveform is owned by no other subpatch.
- It is not one of the production hosts (Toasty `52/68/608/533`, Temple `329/486/329/319`) or the stock pickup chain.

Some raw calls take the event from stage resources (`lw a0,(s4)` with `a1 = 1`). As an extra guard, each candidate's event number was counted as a 32-bit word outside the sound bank; the chosen hosts have one stray hit, the same as production host 329.

Isolated chains found (event / patch / subpatch / waveform): `159/316/159/149`, `164/321/164/154`, `168/325/168/158`, `170/327/170/160`, `171/328/171/161`, `172/329/172/162`, `173/330/173/163`, `175/332/175/165`, `177/334/177/167`, `332/489/332/322`, **`335/492/335/325`** (Sektor teleport sound, proof v09/v10), `336/493/336/326`, **`437/594/437/427`** (v09 landing thud only; left stock in v10), `453/610/453/443`, `459/616/459/449`, `478/635/478/468`.

Use by the Sektor proof line through v41 (all Runtime-confirmed as hosts; `fighter_import.sound` installs a chain from the MKT bank and checks every rewritten record against the clean ROM):

| Host event | Donor (MKT USA Rev. 2 event) | Since |
|---|---|---|
| 159, 164, 168, 170, 171, 172 | voice set (v15 rule below) | v12 |
| 335 | teleport `0x104` | v09 |
| 173 / 175 / 177 | rocket chest open `0x108` / launch `0x100` / boom `0x107` (robot ochar `0x0B` / `3` / `0x0A`) | v30 |
| 332 / 336 / 437 / 453 | throw: grab voice `0x67` (voice group 3) / arm OUT `0xFD` / arm THROW `0xFE` / arm IN `0xFF` (robot ochar 0 / 1 / 2) | v41 |

Free: 459, 478. MKT's per-fighter ochar sounds resolve through `0x800A1ED4[fighter]` (a table of `u16` events); the robot table follows the arcade MK3 `st_robo1` order (`MKSOUND.ASM`).

To host a donor sound:
- the donor track replaces the host track, with its patch field set to the host patch;
- the donor subpatch replaces the host subpatch, with its waveform field set to the host waveform;
- the donor waveform record replaces the host's, with its offset rebased to the new sample relative to the TBL base `0x9B0650`;
- the donor predictor book replaces the host's;
- the sample goes in free ROM.

The donor's `−2253`-cent waveform correction is kept as is; MKMSZ honours it, as Toasty already showed. Chains are proof allocations until a production reservation claims them in the [Memory and allocation map](Memory-and-Allocation-Map).

## Imported fighter voice rule (2026-11-07)

**Runtime-confirmed bounded for Sektor (teleport proof v15: "It's fantastic now").** This rule is meant to apply to any MKT donor fighter.

**Donor side.** MKT keeps a voice-group table at `0x800A19D4[group]`: a `u16` count, then `count` entries for each voice group. The fighter's voice group is `0x800A19FC[fighter]`, and `0xFFFF` means no sound. The group meanings follow the arcade MK3 source (`MKSOUND.ASM` `group_table`): 0 attack, 1 jump, 2 wasted, 3 grab, 4 throw voice, 5 tripped, 6 face hit, 7 run, 8 shook, 9 death scream. The reactions that play each group come from `MKREACT.ASM`:
- light hits (`rsnd_react_voice`) play group 6;
- launching hits (high kick, roundhouse, uppercut, launching combos) play group 2;
- sweeps and slides play group 5;
- landing on the back plays only `rsnd_ground` (no voice);
- every quick attack plays group 0 followed by `rsnd_whoosh`.

**Target side.** The player (type 4) voice table `0x800A2EC8` (ROM `0xA3AC8`) maps 12 categories to descriptors `0x20..0x2C`, which play events 30–43. No enemy table and no other descriptor uses them. Category 10 also gets descriptor `0x2A`, which is stock-unreferenced. Each category is matched to a donor group by the reactions that play it:

| Player category | Played by | Donor source |
|---|---|---|
| 0–1 | attack routines **and the somersault jump** (`0x8002FB08`) | group 0 voice, else MKT whoosh #1/#3 (triple slots 6/7) |
| 2–3, 4–5 | stand-up reactions | group 6 face hit |
| 6–7 | launching reactions (uppercut and others) | group 2 wasted |
| 8 | jump `0x80031FB4` | group 1 |
| 9 | sweep-family reactions | group 5 tripped |
| 10 | knockdown landing `0x800546E8` (after its own thud, descriptor `0x10`) and zero-HP death | none (MK3 lands with no voice; a KO has no extra voice) |
| 11 | the grab: the player throw `0x8005BC8C` (`0x8005BCD4`) and the grab paths `0x8003D048` and `0x80040654` are its only callers (earlier labelled "slide/special yell") | group 3 grab. For Sektor, proof v41 plays the grab voice and the arm-OUT sound from a throw wrapper while the table entry stays 0 |

How it is implemented:
- **Empty groups:** a donor group with no sound sets that category's table entry to 0, which `0x80064B00` skips.
- **Re-pointing:** each used Sub-Zero event keeps its slot, and its `0x20`-byte track is replaced by the donor track pointing at an isolated host chain.
- **Random picks:** MKMSZ picks 1 of 2 where MKT picks 1 of `count`. Distinct donor sounds are kept in table order. MKT face-hit entries 62/63 share waveform 158.

Rejected along the way:
- v14 used group 9 for category 10, which played a human pit/fatality scream on knockdown landings.
- v13's run sound (group 7, one shot per Run start through Run-script callback 2 and spare descriptor `0x22`) was correct but annoying in MKMSZ.
- v16 scaled categories 0/1 to 85% volume, which turned down the somersault rather than the attack sounds the user meant.

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
