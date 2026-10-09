# MKMSZR rich Inventory music — upstream investigation

2026-10-08. **Root cause and permanent correction: Pending. PR #156 remains draft and unmerged.** No emulator automation, additional ROM, AI retry, or production integration was performed.

The new pair proves 135 additional rejected PCM submissions. Audio work and VI callbacks both advance by 4,934, while synthesis advances **47,616 sample frames beyond the 368-per-service target**. This is close to the **47,520-sample minimum** represented by those rejected buffers. Omission of synthesized musical time is therefore a strong explanation for accumulated tempo drift. The pair does not identify the Inventory operation that causes the imbalance or establish that guest rejection explains the entire audible symptom.

The earliest verified unsuccessful operation is native full-FIFO enqueue `0x8008A500`; its caller ignores failure and advances synthesis. This establishes the downstream loss path. **No upstream operation X or condition Y has yet been causally identified.** Closure needs service/AI/task chronology immediately before rejection, followed by a matched rendering control.

ROM `0x0008B158`, `1440000A → 1440FFFD`, is explicitly rejected for this investigation. It remains an untested mitigation. Retrying can change scheduler timing and hang if AI stops draining. Nothing in the new counter evidence promotes it to a root-cause fix.

## RMG host observer: bounded smoke validation (2026-10-08)

**Runtime-observed diagnostic operation, not root-cause confirmation.** The maintainer used the separate RMG v0.9.0 diagnostic Flatpak from draft [PR #157](https://github.com/smeagol44/MKMSZ-Randomizer/pull/157) and uploaded four Trace v02 event files from a roughly 33-second manual smoke run. Read-only binary decoding validated `MZRHST1` magic, version 1, 56-byte records, exact byte counts, consecutive sequence numbers, and monotonic timestamps:

| Source | Total/retained events | Overwritten | Observation |
|---|---:|---:|---|
| AI | 10,043/10,043 | 0 | 1,674 enqueue attempts, 1,674 status reads; zero FULL in either sampled position |
| VI | 3,938/3,938 | 0 | 1,969 callback+due pairs |
| RSP | 10,881/10,881 | 0 | 2,511 task-boundary entries; zero recorded RSP cycles at all 5,022 post-run points (consistent with pinned ParaLLEl RSP source, not independently a failure) |
| Host audio | 6,694/6,694 | 0 | 3,347 SDL push results, all successful; zero host drops |

The host SDL queue sampled **0..7,396 bytes**, below the **17,637-byte threshold**. These results are healthy-path reference measurements, not a reproduction of accelerated music.

At the measured event rates, the v02 rings retain about **12.2 minutes AI, 18.3 minutes VI, 12.8 minutes RSP, and 9.1 minutes host audio**. The canonical eight-minute filled→empty→filled test can fit at similar rates, but host-audio margin is modest; quit normally promptly after its final 30-second closed phase, and always inspect overwritten counters before claiming a complete timeline. Backend rate or stage changes could reduce retention.

This v02 logger observes guest AI register accesses, VI/RSP task boundaries, and host audio submission/drop decisions. It **does not itself record full WESS synthesis generations, task PCM record identity, or native audio-service call provenance**; further discriminating evidence may still be necessary. No game correction, AI retry, merge, or emulator automation was performed.

## Trace v02 accelerated-music capture — first FIFO failure chronology (2026-10-08)

**R:** maintainer heard accelerated music during phase 2, within the first minute of the occupied-box Inventory-open test, and saved `accelerated.state` while the music was accelerated. The file belongs to diagnostic ROM MD5 `62CB2C88A25B622998400CFE8C904188`. **S:** its diagnostic helper at `801B3408` holds **75 native PCM enqueue rejections** (`AIF1`, version `20261008`), first/last WESS ticks `0x6174/0x6452`, current WESS tick `0x645E`, audio frame `0x31E5`, and VI callback `0x32FC`. The saved state is a **during-failure** capture, not a post-hoc attribution of the entire musical symptom.

Read-only Trace v02 event files (signature `MZRHST1`, record size 56 bytes) were structurally validated with the checked-in `diagnostics/rmg-host-observer/decode_host_trace.py` and a focused host-timestamp/CP0-count alignment. All files cover one observer execution with total timestamp span ~741.82 host seconds; no emulator was run for analysis:

| Trace | Saved/total records | Lost | SHA-256 |
|---|---:|---:|---|
| `mkmszr-ai-trace(2).bin` | 247,213/247,213 | 0 | `cc9d4f20ce8b0c9cbb97ecd30772f48f6412e5874d72416e57a46060d587513c` |
| `mkmszr-vi-trace(2).bin` | 83,132/83,132 | 0 | `cdb1c448eb797128ddd3e0441177bd732105c1e696133664160a9e36e2b13514` |
| `mkmszr-rsp-trace(2).bin` | 246,414/246,414 | 0 | `0df39f1170b3e7505b688406b90e8db79a27fdd81fa338f6d32203f26fc9f116` |
| `mkmszr-host-audio-trace(2).bin` | 131,072/164,664 | **33,592** | `99e87ea54e46440c8c0d1b4b76eca018944dfc848055d9c28e402753118c6ba7` |
| `accelerated.state` | gzip M64+SAVE v2; diagnostic counter 75 | n/a | `696e173549a7a51cb1fa1fb2e1d1051130a4b033f80096e4dc60c784e4daa30d` |

Host timestamps are monotonic but **not emulated time**, and the first 146 seconds of *host-audio* samples were overwritten. Its first **retained** SDL drop is at ~421.65s, not provably the first in the whole session. No host drop is retained for ~146–421s, including the recorded 305s onset. A total 45 retained host drop records discard 42,200 bytes later. This supports a distinct later playback-queue contribution, **not** the first guest FIFO-full event.

**First captured native failure chain (relative to first VI log event; measured, not a guess about absolute Inventory-opening time):**

1. Previously healthy cadence near 300–304s was ~60 VI callbacks, ~60 accepted AI writes and ~60 AI DMA-end deliveries per host second. At ~305.2447s and 305.2606s, successive **1,600-byte / 400-sample** PCM buffers were submitted, exceeding normal 1,408–1,536-byte / 352–384-sample buffers. The upstream native feedback (`8007D4F0` AI head-only remaining-length formula) had just observed 1,216-byte head remainders. This is a precursor, not an independently established original Inventory defect.
2. At ~305.2777s, native audio submitted a 1,472-byte tail behind an active 1,600-byte AI head. At **305.29473s**, the next native AI_STATUS reads saw `0xC0000000` (BUSY+FULL) before that active DMA completed, with **4,204 emulated Count units** still until its observed AI-end Count `1780803589` (first status read Count `1780799385`). The read of AI_LEN at Count `1780799463` returned **zero**: ~7.5 head bytes remaining truncate to zero under RMG's eight-byte alignment. It does **not** mean both guest AI slots were empty.
3. The established native PCM-size feedback therefore generated a **704-sample** maximum-sized buffer next, observed as an accepted **2,816-byte AI submission at ~305.31063s**, while the prior failure's PCM had not been enqueued. Subsequent long buffers and FIFO-full status reads form a self-amplifying workload/queue-feedback episode.
4. From ~306–309s, **~60 VI callbacks/s** continued but only **~45 accepted AI submissions and ~45 AI DMA ends/s** occurred, with **30 FULL status reads/s** (two native status reads per rejected attempt). `AI_STATUS.FULL` appeared 288 times in 144 close read-pairs across the entire capture: **140 read-pairs** clustered ~305.295–323.885s (interrupted by a ~9-second wall-time idle gap), then four sporadic pairs later.
5. The **75th** FIFO-full read-pair is at ~310.228s; the native savestate contains a matching 75-failure cumulative counter and a subsequent host-time gap of ~9 seconds precedes read-pair 76 at ~319.575s. This is unusually strong alignment of uploaded guest state and host chronology, but the exact GUI/save timestamp is not embedded as a direct marker.
6. On-time AI drain evidence: matching head-start and DMA-end Count records around ~305–324s differ from their scheduled DMA durations by only **0–178 Count units**, ordinarily 0–10. There is **no gross guest AI-end deadline miss** during the initial failure episode. The RSP logger retains stable first-run/task/interrupt patterns around the burst (~80 RSP starts/s during active rendering, reported zero emulated cycles in the pinned ParaLLEl model), without evidence of a missing RSP completion. It lacks native task/PCM *generation identities*, so cannot prove all task ownership conditions safe.

**Causal status:** The first *observed* violated condition is a VI/audio-service enqueue arriving **shortly before** a still-active FIFO DMA has completed while the tail is also queued. Head-only AI_LEN feedback returning zero and subsequent maximum PCM generation **amplify** the collision into repeated lost submissions, while sequencing continues. This discriminates against the previously suspected *large AI consumer deadline delay* as the immediate trigger, but still does **not** identify the first rich Inventory rendering/resource/scheduler operation that shifts the producer/consumer phase to this boundary. Host SDL drops occur later in the retained interval and are not required for the onset. A correction to PCM enqueue retry is still rejected; no upstream correction is authorized or implemented.

**Remaining discriminators:** establish the first renderer/Inventory-operation timing shift relative to guest VI/audio release and AI head+tail occupancy on an otherwise matched control. This logger lacks explicit native WESS audio-service/generation IDs and Inventory phase markers; event timing alone cannot attribute the first phase crossing to a particular glyph/palette, rendering, scheduler or resource operation. Ask whether empty-box and closed-Inventory phases suppressed *new FIFO rejections* (do not equate persisted audible offset with ongoing rejection), and ideally compare the existing occupied-versus-empty segment boundaries to the complete AI history. Savestate loading can reset emulated Count/AI FIFO state; never interpret huge cross-load Count differences as late DMA without excluding load boundaries.

### Complete five-phase route: occupied → empty → occupied and closure

**R:** The maintainer confirms completing *all five* phases, performing the specified action **before** timing each waiting interval. Phase 2: entered Inventory with occupied box 1 and left selection unchanged for approximately three minutes; `accelerated.state` was saved during the first 40–60 seconds. Phase 3: navigated to empty box 3 and waited ~2 minutes. Phase 4: **two D-pad Right presses**, box 3→4→1, then waited ~2 minutes on occupied box 1. Phase 5: closed Inventory and waited ~30 seconds. No post-Kia phase restart or savestate reload is reported during these five phases.

The host/RSP trace independently changes from approximately **90 RSP first-run task starts/s** with Inventory closed to **80/s** at t~266.2, returning to ~90/s at t~702.0; VI cadence remains ~60/s throughout active emulation. This supports the Inventory opening/closing boundaries. Internal box transitions are **not instrumented**: t~456 and t~576 are estimates inferred from stated ~180/120/120-second waits plus a ~9-second host-time pause around the in-Inventory savestate. The following windows are therefore descriptive comparisons, **not exact input-event timestamps**; timestamps are seconds from the first logged VI callback:

| Approximate window | Maintainer-controlled state | Native FIFO-full enqueue attempts (two FULL status reads per attempt) | Host SDL drop events | AI writes of PCM size >1,600 bytes |
|---|---|---:|---:|---:|
| 240–266s (sampled) | Phase 1: closed | **0** | **0** | **0** |
| 266–456s | Phase 2: occupied box 1 | **141** | **5** | **213** |
| 456–576s | Phase 3: empty box 3 | **1** | **12** | **1** |
| 576–702s | Phase 4: returned to occupied box 1 | **2** | **16** | **2** |
| 702–742s | Phase 5: closed | **0** | **12** | **0** |

The **140 initial rejections** in phase 2 are concentrated at **t305.295–323.885s**, starting ~39 seconds after the Inventory-open RSP-cadence transition. A ~9-second wall-time gap within this period is consistent with user-reported state saving; exact save timestamp remains unmarked. The *only* subsequent phase-2 rejection is at **t421.852s**, with none from t~324–421s even though box 1 stayed occupied and Inventory remained open. There is then one sporadic failure at **t555.853s** (estimated empty-box phase) and two at **t598.871/598.987s** (restored occupied-box phase). **No new guest FIFO-full attempts** occur in the final closed interval.

The host-audio ring's first 146s were overwritten, but all five analysis windows lie beyond the retained boundary. The **first retained host drop is at t421.652s**, after the major guest failure episode. Phase 3, phase 4 and even the closed phase 5 contain host SDL drops (12, 16 and 12 respectively), whereas no SDL submission calls returned false. Such subsequent host drops are **not specific to the continuously rendered occupied-box rows**. They may add audible omission but cannot explain the initial guest FIFO-full episode. Total retained host drops across the route = **45 events / 42,200 bytes**.

**Interpretation and limits:** Severe native audio loss is **episodic**, not a constant condition throughout occupation of the rich Inventory. The occupied-box state remained unchanged during the initial burst *and* a long rejection-free continuation. Restoring the same occupied box later did not reproduce a sustained burst. This weakens a simple continuous row-rendering-overload claim; it does **not** rule out a rare phase-collision, accumulated workload-dependent event, entrance/lifetime transition, resource behavior or timing-sensitive composition. Empty-box mode did not eliminate *all* rejections. The observed 80 versus 90 RSP-task-start cadence identifies a change in RSP activity associated with Inventory state, not by itself a proved cost/latency or a specific glyph operation. Audio sequencer state already advanced past lost PCM may remain audible as accelerated even after new native rejections cease; no exact audible recovery timeline is encoded here.

**Follow-up audible-course clarification (R, 2026-10-08):** The maintainer reports the acceleration is **transient**, roughly 10–15 seconds (uncertain), and music then audibly returns to normal. Further acceleration was not heard for several minutes; whether subsequent box/navigation inputs retrigger a new episode is unknown. This is consistent with the ~19-second dominant rejection burst followed by long rejection-free intervals, but is not timestamp-locked to the first audible onset/recovery. Revise earlier suggestions that the symptom necessarily remains accelerated after the loss event: accumulated omitted PCM can alter sequence phase, but does not establish an indefinitely fast audible tempo. The next proposed *manual* discriminating test enters Fortress directly, holds Inventory open with **no input** for three minutes, then switches to empty box 3 for one minute and returns via box 4 to box 1 for another minute (30 seconds closed before and after). Trace files are primary; an accelerated savestate is optional and may perturb timing. This test differs from the post-Kia route, so a negative result alone does not dismiss the existing reproduction.

**Remaining gate:** a matched instrumentation/production proof that marks Inventory open/box-switch/close and native audio generation/service dispatch in guest Count, allowing the earliest timing-phase shift to be attributed to a concrete operation without changing visual behavior. Do not apply AI enqueue retry or promote PR #156 on this evidence alone.

## Sources, scope and identities

Evidence labels: **C** checked native code or primary source; **S** decoded snapshot; **R** maintainer runtime report; **H** inference; **U** unavailable. Inputs were read-only. Project Status was read first, followed by the Roadmap, previous static owner, Native HUD/UI, Persistence/Inventory/Lifecycle, Memory/Allocation, Patch Registry, Runtime Validation and relevant audio/resource/scheduling/failure records. Living Ghidra metadata was consulted before adding verified entries.

[MKMSZR main baseline](https://github.com/smeagol44/MKMSZ-Randomizer/tree/52a1df98defaa1fedd2986cba291375d41ae1ccc): `52a1df98defaa1fedd2986cba291375d41ae1ccc`. [Draft PR #156](https://github.com/smeagol44/MKMSZ-Randomizer/pull/156): head `47a395ba16c7e4cecc0ba9d6de91b8a4310db32e`, base `0421f7b3eab54e3c484a19834e3f2230b6adbb05`. Later independent main changes do not alter these existing ROM identities. Ghidra baseline: `e86bc8ba2fcc20aedaeb7b725905018b72a2f90f`.

| Input | SHA-256 |
|---|---|
| Clean USA Rev.0 | `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6` |
| Accepted `MKMSZR_inventory-rich-materialized_fortress_proof_v01.z64` | `b73a9cba8c8a2ff0f6b96d9057dd30f36dc5b1e6e0b713d2f9d0eafb3b335c03` |
| Failing `MKMSZR_inventory-materialized_full-production_build_v02.z64` | `f44e3724a8c883b720d727936cb7f4204f19acc5569ca4b0fc581007ee2b7313` |
| Existing `MKMSZR_inventory-audio-trace_fortress_proof_v01.z64` | `9b7c47758be500535ef10a4c0a063667e50cded66ab28a1b101f0182d4be3152` |
| Normal state, supplied locally as `test_musicnormal(1).state` | `43383279333a8820f0faf73a487c710dadd14c4b3b07b9af3f9b0470ef6271cc` |
| Accelerated state, supplied as `test_musicspeedup(1).state` | `db2f9358c9373c9d0079003ff91d5c18afddf99a44ea60c0d6d9994d18f5a66d` |

Both states record diagnostic MD5 `62cb2c88a25b622998400cfe8c904188`. Format is M64+SAVE v2, decompressed size 16,793,412 bytes; 8 MiB RDRAM at offset `0x1BC` with bytes reversed within each host word. Its AI block preserves FIFO lengths/durations, **not both addresses**; loading reconstructs both from the last AI_DRAM register. No state was executed here.

**C:** v02→diagnostic differs in 115 bytes in five runs: header CRC `[0x10,0x18)`, fail-branch byte `0x8B15B`, trampoline `[0x8B198,0x8B19C)`, resource-end descriptor `[0xA514E,0xA5150)`, and appended `[0x1819B9C,0x1819C00)`. Permanent executable changes total five bytes. Entire rich module `[0x801B28F0,0x801B2DF0)` (size **0x500 = 1,280 bytes**, ROM `[0x18190D0,0x18195D0)`) is identical between v02 and diagnostic. Proof matches its row/preview/table portion through `0x801B2C80`; the final status region differs in 268 bytes for Custom/Seed versus Vanilla. It is incorrect to call the whole proof/v02 module identical.

Existing failure-only helper: `[0x801B33BC,0x801B3408)`; six-word log: `[0x801B3408,0x801B3420)` = count, first tick, last tick, AI status, `AIF1`, version `0x20261008`. Diagnostic file 1A maps ROM `[0x1816000,0x1819C00)` to runtime `[0x801AF820,0x801B3420)`. Arena floor is unchanged. Logging adds CPU work on failures; it is not perfectly timing-neutral, and could affect later failures. No free guest tail is assumed.

The [historical initial manifest](https://github.com/smeagol44/MKMSZ-Randomizer/blob/main/wiki/Production-Rich-Inventory-Music-Initial-Static-Manifest.md) preserves the prior `musicspeedup3.state` teardown, lifetime counterexample, Vanilla correction and superseded retry proposal. Its verified negatives remain valid for those inputs. This investigation uses them without repeating the broad teardown.

## Native producer/consumer and scheduling reconstruction

### VI and task release

**C:** setup `0x8000060C` creates scheduler queue `0x802C1970`, backing `0x801AE4C8`, capacity 32. Event registrations: SP→message 1 at `0x80000734`, DP→2 at `0x80000744`, pre-NMI→5 at `0x80000724`; `osViSetEvent` at `0x8000075C` sets VI→3 at rate **one**. Message 4 is software task dispatch. Scheduler thread `0x800B6048`, entry `0x80000A70`, priority 90; game thread `0x800B46F8` priority 10, PI worker 50, VI manager 150.

| Address | Native operation |
|---|---|
| `80000A70` | Blocking message receive and dispatch |
| `80000E24` | VI: promote prior fresh audio task, dispatch, framebuffer service, build next audio task |
| `80000E3C / E44` | Fresh `8009A534`→queued `8009A538`; clear fresh |
| `80000EF4 / F00` | Call `8007D3FC` if audio-enable `8009A530`; publish next fresh task |
| `80000F24` | Call input/VI callback from `800B43C0` if `80000300` is nonzero |
| `80015950 / 15998` | Input/VI callback; increments `802E7DC0` |
| `80000F4C` | Audio-first task dispatch; defer while active audio exists |
| `80000B6C` | SP completion/yield handling |
| `80000C5C` | DP completion/graphics bookkeeping |
| `800011F0` | Cache writeback, task load, RSP start |

Both endpoints have `80000300=1`, callback `80015950` and the above game/scheduler priorities. Inventory suspends cooperative gameplay lists, not this OS audio scheduler. Cached glyph drawing neither schedules another audio frame nor registers a VI callback. Higher audio priority weakens simple CPU starvation; it does not exclude a blocked operation, delayed interrupt, or service burst. In this configuration the input callback runs on the scheduler after audio service; no traced glyph path enters it. Both endpoint scheduler queues have validCount zero. Prior maximum/backlog is **U**.

### PCM feedback and sequenced time

`8007D3FC → 8007D4A8` first cleans sample DMA (`8007D860`; audio frame counter `800A7F60` increments at `8007D98C`), then submits previous `lastInfo` at `8007D4E8 → 8008A500`. Enqueue checks full at `8008A550 → 80092E90`; full returns `-1` without AI writes, accepted writes AI_DRAM/AI_LEN at `8008A57C/580`, returns zero. The diagnostic logs the failure and returns through the original epilogue.

At `8007D4F0`, enqueue's result is overwritten by a call to AI_LEN getter `8008A3C0`. New sample count follows the observed native constants:

`max(352, ((368 - (AI_LEN >> 2) + 320) & ~15) + 16)`

Assembly uses 16-bit masking/storage. Minimum/target globals are `800BA450/454`, reserve `800A8004`; configured maximum PCM capacity `800BA458=704`. An empty head produces 704. **The feedback reads remaining head bytes, not total head+tail occupancy.** A late service and subsequent adjacent services can change produced sample counts without increasing aggregate service frequency. This is a competing mechanism, not recovered chronology.

| Ownership structure | Verified layout |
|---|---|
| AudioInfo pointer globals `800BA3E8..3F0` | `8013A780`, `8013B2D0`, `8013BE20` |
| Record stride | `B50`: 80-byte header + `B00` PCM capacity |
| Record `+0 / +4` | PCM=`record+50`; signed 16-bit sample-frame count |
| Record `+8` | 64-byte OSTask, type 2 |
| Record `+38 / +3C` | Command pointer/byte count, OSTask `+30/+34` |
| Command globals `800BA3E0/3E4` | `8012A780`, `80132780`, each capacity `8000` |
| `800A7F6C / 7F70` | Three-buffer index / previous lastInfo |
| `8009A534 / 538 / 53C` | Fresh / queued / active audio task |

Wrapper publishes new lastInfo, rotates three records and alternates two command lists despite previous enqueue failure. Synthesis `8008910C` advances ALSynth `+20` at `80089270` during command construction, before RSP completion or AI acceptance. ALSynth global is **800A8210**, pointing to `800BA3F4` (signed-low-address instructions must not be misread as `800B8210`).

Callback `8007DA34 → 80083D38 → 80085C8C` advances WESS/sequence and returns 8,333 microseconds, yielding **184 player samples/tick**. Tick global `800A8038`; ms/fraction `800A803C/8044`; increment `85555` in 16.16. Sequence time can advance for synthesized PCM that never reaches AI. Omitting these musical intervals can accelerate progression through the score while leaving sample pitch/DAC unchanged. **C** establishes the permitted path; the complete audible contribution remains **H**.

### Shared RSP and task lifetime

The VI handler queues the prior generated task before producing the next. Dispatcher refuses while active `8009A53C` is nonzero, otherwise transfers queued→active at `80000F80`, clears queued at `F88`. Running graphics (`800FEC24 >= 0`) causes yield flags `800C11E8/800BF35E` and request `8008A7E0`; audio starts after SP/yield handoff. Completion handler `80000B6C` checks `osSpTaskYielded` (`8008A800`), clears/completes the appropriate owner, dispatches or resumes graphics.

**Conditional static hazards:** queued is one pointer. Promotion `80000E3C` can replace it if it has not been consumed. Continued synthesis can reuse a PCM record or command list before a delayed generation completes. These conditions are **not observed** in the pair. Both endpoints have fresh=`lastInfo+8`, queued=active=0, SP status `243` (halt/broke), and no queued SP/DP task event. That excludes an unfinished task at capture, not a previous replaced generation. Rotating addresses require generation IDs to establish ownership.

## Paired timeline and quantitative constraints

**R:** same session/stage/post-Kia door route. Normal music first; accelerated without pitch rise after Inventory remains open. No wall-time recording or measured tempo factor accompanies the states.

| Measurement | Normal | Accelerated | Change |
|---|---:|---:|---|
| Rejected submissions | 1 | 136 | **135** |
| WESS ticks | 49,754 | 59,881 | 10,127 |
| Audio frames | 24,873 | 29,807 | **4,934** |
| VI callbacks | 25,152 | 30,086 | **4,934** |
| VI minus audio | 279 | 279 | Unchanged |
| Player sample time | 9,154,736 | 11,018,104 | 1,863,368 = ticks × 184 |
| Synth sample time | 9,154,656 | 11,017,984 | 1,863,328 |
| WESS ms / fraction | 414,616 / 27,106 | 499,008 / 1,885 | Exact tick × `85555` |
| CP0 Count | `C19E9D50` | `B0273056` | Modulo delta 4,001,927,942 |
| Next VI deadline | `C1AAFDA2` | `B033909A` | Modulo delta **4,001,927,928** |
| Saved VI period | 811,092 | 811,092 | Delta exactly **4,934 periods** |
| AI status | `40000000` | `40000000` | BUSY; FULL clear |
| Last-written AI_LEN / head length | `580 / 580` | `680 / 680` | 352 / 416 stereo frames |
| Head duration | 775,808 | 916,864 | Length × 551 Count units |
| Counts to next AI event | 708,126 | 854,354 | Unexpired head |
| AI DAC / bit rate | `89F / F` | `89F / F` | No endpoint rate change |

FIFO tail length/duration fields are stale when FULL is clear. Do not count them as live occupancy. The saved AI_LEN register is its last write, not an observed current remaining-length read.

First rejection is tick **35,580 in both states**, preceding healthy capture 49,754; normal's last rejection is also 35,580. Accelerated's last is **59,874**, seven ticks before capture. Thus one rejection is not sufficient for audible acceleration. Assuming no log reset, 135 additional failures occurred during the paired interval, but their distribution/onset is unknown.

At nominal 60 Hz, 4,934 VI periods represent **82.2333 emulated seconds**, not wall time. Count/deadlines are modulo 2^32; two endpoints cannot recover additional whole wraps or prove unchanged settings throughout. Independent VI/counter agreement strongly opposes sustained callback multiplication but cannot exclude stalls followed by bursts, compensating extra/lost messages or wall-time pacing changes.

Nominal synthesis: `4934 × 368 = 1,815,712`. Actual surplus: **47,616 (2.6224%)**. WESS advances **259 ticks beyond two/audio frame**. This is more sequenced synthesis per service, not more services. Under fixed native 352..704 frame sizes and one attempt per frame, rejected buffers represent **47,520..95,040 samples = 2.1554..4.3108 seconds** at integer DAC 22,047 Hz. Surplus exceeds that minimum by **96 samples**.

**H:** the close relationship strongly supports a PCM omission contribution. It is not complete conservation accounting: accepted lengths, initial/final live occupancy, underruns, task completion and host drops are unrecorded. Exact rejected sizes, instantaneous audible tempo, clustering and total loss cannot be reconstructed. The aggregate 2.6% does not quantify how dramatic the perceived onset was.

**S:** both permanent executables match diagnostic `[80000400,8009A000)` exactly. The existing static audit was reused to verify all eight complete active Fortress streams, bank/predictors, native ADPCM rounding, DMA lists and populated sample buffers. The earlier broad negatives survive. Active music waves are clean-identical, not the substituted donor Temple/Toasty carriers.

## Rich rendering, palettes and resources

| Rich operation | Entry/shared helper | Repeated work |
|---|---|---|
| Item/credential rows | `80074268 → A01B28F0` | Native labels/colored true-stage credentials |
| Selected preview | `80073098 → A01B2980` | Sprite; portrait ROM DMA on selection/stage change |
| Paper title/stage/check table | `800742B8 → A01B2A60` | Width/title and cached table-row draws |
| Required Powers / checks | `800742C8 → A01B2C80` | Vanilla XP or Custom/Seed text and cached checks |
| Legend/box indicator | Promoted native legend module | Accepted dynamic box indicator/legend glyphs |
| Inventory loop | `80073588 → 800728B0`, sleep `80028794` | Repeated panel draw; no repeated open prologue |

Materialization removes repeated changing-data computation, not native glyph rendering. New pair has identical LIVE/40 backing words, process state `16`, Powers count zero, and byte-identical `1200`-byte HUD (SHA `239c4d2d44c1f6b236b11fdce11b26059f241321bf3a91b491c47773aedc5ca8`). Box 2 contains one `04`; boxes 3/4 are empty. No selection/box change is evident between endpoints.

**C:** strings `80073E74 → 80073CEC`; each non-space glyph calls palette acquire `8001C528(font+4,256,0)` then render builder `8001E578`, submitting `58`-byte nodes through `8001EBB8`. Cache hit at `8001C628` increments u16 refs and returns existing handle without conversion/upload. Miss: allocate `8001C81C`, convert `8001C6D0`, upload `8001D6EC`, synchronous flush `8001D7F0`. Traced cached paths have no audio calls or interrupt-mask changes; this does not certify all graphics paths.

Release `8001C64C` decrements the original owned handle; zero frees via `8001C898`. Glyph acquisition has no matching release. Stock text behaves similarly. Acquire wrap does not itself free, and hit validity depends on active/source identity. Retrofitting releases could free a palette still consumed by queued graphics. Full 256-color source spans remain required despite 16 visible colors.

**S:** 17 active dynamic entries `C0..D0`, same sources/handles in both; both private palettes convert correctly across all 256 colors. Private source `A01FF3B4` refs **6125→17129** (+11004); `A01FEBA4` **4375→12235** (+7860). These match 1,572 seven/five-glyph repetitions if no releases/rebindings intervened. They support cached repeated rendering, not churn. Stock source `800B1D84` wraps refs **64658→43648**, but no failing release/private corruption or exhausted cache is shown.

Graphics builder `8001EC20` traverses buckets; glyph/textured kind 2 dispatches `8001ED00`; pipe-sync emitter `80020108` is in this chain. More glyphs mean real CPU command and graphics work. They do not by themselves prove audio/RSP deadline failure.

| Resource | Normal / accelerated |
|---|---|
| Arena floor / cursor | `801B3420 / 8028C538` both; 74 links, nominal headroom 17,496 bytes |
| HUD / Fortress anchor | `801FEBA0 / 801FFDA8` both; HUD end `801FFDA0` |
| Graphics cursor / texture boundary | `803D9F38 / 803FEEC0` both; gap `24F88` |
| Upload queue | `FFFFFFFF` both |
| Partial current-frame nodes | 180 / 377 |
| Node cursor | `800C6730 / 800CAAE8` = `800C2950 + count × 58` |
| Both completed display-list sizes | `B538` = 46,392 bytes both; per-buffer capacity `17800` |

Partial node counts capture different phases; **377/180 is not a workload ratio**. Earlier audit hardcoded second-bank base `800D8110`, valid for its older state. Native setup `8001BA80/84` establishes `800C2950 + bank × 157C0` (1,000 nodes). Both new states use first bank; their older `cursor_consistent=false` is a decoder assumption. The new decoder accepts both banks. No current node threshold (`3E7`) overflow, allocation collision or upload backlog appears. Earlier peaks remain unknown.

The independent stale-HUD bug remains: open wrapper `[A01B3210,A01B324C)` clears `P+1198/+119C` **before** ensure validates ownership; ensure's `cursor >= P+1200` cannot reject rewind/refill by another owner. The captured resident HUD/anchor protects these Fortress endpoints. No first stale write/audio victim is shown. A lifecycle fix must invalidate at discard before flag writes and account for pointer-keyed palette/queued render consumers; it remains separate from music attribution.

## Accepted proof versus production

The accepted proof's extensive bounded **R** result remains valid. It passed pickups, consumables, Combine, empty boxes, Kia/crystal, doors/elevators and Inventory stress. It is not a matched control for full-production v02.

Exact comparison: **125,946 bytes, 4,580 runs**. Proof uses Custom/Seed Required Powers, production Vanilla `REQ. XP 5100`; assignments/power order/enemies and donor Temple sample differ, lives/continues 6/4 versus 5/3. Exact seed strings were not inferred from bytes. Common row/preview/table code and active Fortress score match; status code and resource composition do not. Different text/resource workload can alter timing even with the same algorithm. Endpoint headroom is not a peak-memory comparison.

v01→v02 changes only bytes `1819A9F:5C→38`, `1819AC7:F4→D0`, correcting Vanilla cached/preparation targets to `A01B2D38/A01B2CD0`. Vanilla is `24` bytes shorter than Custom/Seed. Earlier targets skipped initialized setup, a concrete stray-glyph defect. Corrected v02 materialization is coherent in both new states. Neither that repair nor unmatched proof success establishes audio causation.

**Existing matched workload control:** same diagnostic ROM/backend/stage/seed/checks/settings, occupied first Items box versus empty box 3/4. Rich table/status/legend stay present; rows and selected preview change. Exclude transition DMA from steady-state analysis. This isolates a row/preview workload bundle, not an individual glyph/palette function. Closing Inventory controls the entire panel. No new matched ROM should be built unless chronology specifically justifies a narrower status/resource intervention.

## RMG-specific source findings

**R:** RMG Flatpak installed through Bazaar, ParaLLEl RDP + ParaLLEl RSP. Exact RMG/core/plugin/Flatpak versions, audio plugin, CPU mode, audio synchronization/latency, speed limiter and per-game settings are **U**. A compatible state format does not identify those binaries.

Inspected primary implementation: [RMG v0.9.0, commit `453f6639734537908c4c2ca35244255bc5424e3d`](https://github.com/Rosalie241/RMG/tree/453f6639734537908c4c2ca35244255bc5424e3d), 2026-06-14. Conclusions below are limited to it until the installed build is pinned.

- [Core AI controller](https://github.com/Rosalie241/RMG/blob/453f6639734537908c4c2ca35244255bc5424e3d/Source/3rdParty/mupen64plus-core/src/device/rcp/ai/ai_controller.c): head/tail FIFO, FULL on tail fill; AI-end promotes/clears FULL or clears BUSY. Consumption is CP0 Count/event scheduled. Duration uses `AI_LEN × floor((VI_delay × refresh)/(4 × DAC_Hz)) × dma_modifier`. Saved NTSC delay/DAC give integer 22,047 Hz and **551 Count units/byte**, matching both live durations with default 100% modifier. No historical settings proof follows.
- `get_remaining_dma_length` returns **head** remainder from its deadline. `read_ai_regs(AI_LEN)` also sends consumed fragments to the host audio plugin; AI-end sends the remainder. Extra AI_LEN reads change host delivery. Record already computed values rather than adding reads.
- [Core RSP](https://github.com/Rosalie241/RMG/blob/453f6639734537908c4c2ca35244255bc5424e3d/Source/3rdParty/mupen64plus-core/src/device/rcp/rsp/rsp_core.c) calls `rsp.doRspCycles(first_run)/2`, schedules SP/DP events and gates on pending/wait state. [ParaLLEl RSP `DoRspCycles`](https://github.com/Rosalie241/RMG/blob/453f6639734537908c4c2ca35244255bc5424e3d/Source/3rdParty/mupen64plus-rsp-parallel/parallel.cpp) runs to break/IRQ/exit and returns **input cycles** (core supplies 1 or 0), giving zero added duration after division. It does not derive task time from command/instruction workload. This weakens a blanket extra-glyphs→longer guest RSP duration claim.
- [ParaLLEl RDP SyncFull](https://github.com/Rosalie241/RMG/blob/453f6639734537908c4c2ca35244255bc5424e3d/Source/3rdParty/mupen64plus-video-parallel/parallel_imp.cpp) sets DPC_CLOCK=`viewport width × height × 2`, waits for a GPU timeline and raises DP. Its guest timing estimate is viewport-based, not glyph-count-based. GPU wait costs wall time without automatically advancing guest Count. Guest CPU construction/yield/interrupt timing can still matter.
- [RMG-Audio `sdl_push_samples`](https://github.com/Rosalie241/RMG/blob/453f6639734537908c4c2ca35244255bc5424e3d/Source/RMG-Audio/sdl_backend.cpp) drops a host fragment when queued bytes reach `frequency × 0.2 × 4`. This is independent of guest FIFO rejection. If active, its dropped bytes must be measured; plugin identity/SDL queue are not in the states. It is not assumed to be the user's selected plugin.
- [Serializer](https://github.com/Rosalie241/RMG/blob/453f6639734537908c4c2ca35244255bc5424e3d/Source/3rdParty/mupen64plus-core/src/main/savestates.c) omits both FIFO addresses and reconstructs them on load. Matched runtime controls require cold boot, not cross-plugin state reloads.

Guest AI rejection, guest task scheduling and host playback are distinct. Wall-time graphics slowness alone does not prove virtual AI consumes late: both AI and VI are Count-scheduled. Healthy guest accounting does not prove every host fragment was played. No backend bug is confirmed from these source differences.

## Competing hypotheses

| Hypothesis | Support | Contrary evidence / missing discriminator |
|---|---|---|
| Sustained duplicate/excess callbacks | Queue-driven release exists | Audio=VI delta, deadlines exactly 4934 periods; no aggregate runaway. Need service intervals for brief bursts. |
| Service phase/bursts cause feedback overproduction | +47616 synthesis, 135 failures; head-only feedback | AI_LEN/service chronology absent. Need long gap/adjacent release and occupancy before rejection. |
| Guest AI consumption delayed | FULL proven at failures | Endpoints have normal duration/live deadlines. Need scheduled versus delivered AI-end Count. |
| Graphics yield/task replacement/reuse | Shared RSP, single queued slot, rotating buffers | No current pending task; inspected ParaLLEl returns zero work-derived guest delay. Need generations/start/completion/reuse. |
| Palette misses/synchronous upload | Every glyph acquires; miss flush exists | Same 17 entries, intact palettes, stable allocator, idle uploads; hits do not upload. Need actual miss before violation. |
| Ref wrap corrupts ownership | Stock source wraps | Acquire wrap does not free; no failing release/cache/audio victim. Need first invalid consumer. |
| Stale HUD write | Static lifetime counterexample | Resident captured HUD/anchor intact; no audio victim. Independent defect. |
| Vanilla status defect | v01 bad continuation confirmed | v02 targets/strings coherent; proof comparison unmatched. Need otherwise matched status control if chronology points here. |
| Changed music/DAC | Would alter score or rate | Eight streams/bank/active waves exact; DAC/clock relations unchanged. Strongly weakened. |
| Host drop/pacing contribution | Inspected RMG-Audio has fragment omission | Active plugin/settings/queue unknown. Need accepted/dropped host bytes and audio timing. |

## Correction decision, ownership and risks

**No upstream code correction is justified yet.** Preserve rich presentation/gameplay while observing the first broken invariant. Select the target from chronology, not survival of another ROM:

| First observed violation | Earliest justified correction target | Required control/invariant |
|---|---|---|
| Blocking render/resource operation→late/bunched service→surplus synthesis | That operation or verified task-release policy before surplus generation | Eliminate measured bursts while preserving input/sequence cadence and all rich text. Text removal alone is not the permanent fix. |
| Queued generation replaced or record/list reused unfinished | Scheduler promotion/reuse ownership fence | No uncompleted replacement, premature AI consumption or AI-owned PCM reuse; normal cadence unchanged. Do not spin/stall the scheduler. |
| AI-end late in Count while VI timely | Pinned core/backend event scheduling | Same ROM/backend settings; correct guest register/deadline behavior and host accounting. No enqueue retry. |
| Host drops explain remaining audible loss | Active backend's measured pacing/drop condition | Bounded latency/queue policy; preserve DAC/resampling semantics; compare unchanged guest behavior. |
| Palette/lifetime failure precedes timing/audio failure | Proven offending resource owner | Balance original handles, retain 256 colors, invalidate at discard, drain queued consumers before reuse. |

The stale-HUD owner defect warrants a separate lifecycle repair, but combining it with this test loses attribution. A future guest modification must guard ROM SHA, original instructions/delay slots, ABI/stack forwarding, file-1A extent, occupied intervals, allocation discard and palette/render lifetimes. Current helper/log ends **exactly** at floor `801B3420`; no free guest instrumentation space is claimed. There is no justified upstream patch address/replacement instruction until the responsible operation is observed.

## Minimum measurement and bounded manual experiment

More endpoint states cannot recover the missing producer/consumer chronology. The minimum useful event sequence spans a healthy period and first recurring rejection:

1. VI due/delivery Count; audio service Count and its already computed AI_LEN; frame/WESS/synth counters and rejection-counter change.
2. Accepted AI address/length; live FIFO status/head/tail and scheduled versus delivered AI-end Count.
3. Audio generation (frame number + rotating record/list), RSP start/yield/return and SP completion Count. Verify PCM completion before AI consumes it and before record/list reuse. Enqueue into a waiting AI tail can overlap RSP work; submission alone is not a violation. Addresses alone are insufficient.
4. Active host plugin accepted/dropped byte totals plus short wall-time audio recording/onset markers, to measure the audible loss budget.

Prefer observation-only **host hooks in the original RMG build** at existing AI_STATUS/AI_LEN accesses, AI writes/end, VI delivery and RSP task/event boundaries. This is a specific diagnostic design, not an implemented build. First pin actual Flatpak/RMG/core/RSP/RDP/audio identities and settings, then verify corresponding source. Gate on exact diagnostic ROM SHA/MD5/code, log signature/version and validated guest pointer ranges/offsets.

Use a fixed host ring, e.g. **32,768 × 64-byte records = 2 MiB**, outside guest RAM. Read guest globals using existing host endian helpers. Record already computed register values and hook-local Count; no extra emulated AI_LEN reads, logging-only `cp0_update_count`, per-instruction breakpoints, glyph tracing or event-time console/file I/O. Count overflow/lost records; incomplete chronology cannot close cause. Export after pause/stop. Host logging still costs wall time: repeat the matched route with observer disabled to check that it did not create/remove failure. No guest ROM patch/allocation or borrowed PCM/task buffer is needed.

**One eight-minute manually operated experiment**, same existing diagnostic ROM, original ParaLLEl RDP/RSP and audio/settings, cold boot and same post-Kia/door route:

1. Inventory closed, 30 seconds: whole-panel baseline.
2. Occupied first Items box, fixed selection, 180 seconds; record audible onset if it occurs.
3. Empty box 3/4, Inventory still open, 120 seconds; exclude first two seconds after switching (transition resource work).
4. Original occupied box and selection, 120 seconds: restoration control against session age alone.
5. Close, 30 seconds; stop/export the rolling records and onset audio. Stop early on hang/gameplay regression. Never cross-load another ROM/backend's state.

Compare new rejection **rate per VI**, service intervals, AI deadline delivery and generation ownership, not merely cumulative counts or immediate musical-position recovery. Accumulated offset can persist after its trigger stops. Empty box preserves table/status/legend and exact seed/composition while changing row/preview workload through accepted gameplay inputs.

On-time AI drain plus late/bunched service supports upstream scheduling; late AI-end in Count supports consumer timing; incomplete/replaced generation identifies ownership; host drops identify additional audible omission. Filled→empty→filled changes in the **same first violation** and rejection rate link the row/preview bundle to it. They do not individually prove glyph or palette causation. If only closing helps, attribution stays broader. Unchanged rates weaken row/preview cost as a target. A later same-ROM backend A/B can narrow portability, but cannot replace chronology.

Without host observation, this route with boundary states/audio can narrow workload by rejection rates, **not close task/deadline cause**. No additional diagnostic ROM is recommended until a lower-overhead guest alternative has a specific justified need and exact allocation/patch guards.

## Verification and disposition

[Read-only paired decoder](https://github.com/smeagol44/MKMSZ-Randomizer/blob/main/tools/inventory_audio_pair_audit.py), stdlib-only: normal state, accelerated state, pinned existing diagnostic ROM, `--output JSON`. It emits identities, clocks/events, live FIFO interpretation, AudioInfo/pointer records, memory/render endpoints and limitations; it never launches an emulator or writes ROMs. The existing broad audit was reused for established data/code/DMA negatives. Its second-bank render assumption is superseded only for these new states.

Verified scheduler/audio names/globals/comments are mirrored in [living Ghidra metadata](https://github.com/smeagol44/MKMSZ-Ghidra); hypothetical causal names are excluded. Validation is supplied-state decoding, native disassembly, exact existing-ROM comparison, primary backend/serializer source checks and metadata schema checks. No copyrighted ROM/RAM/PCM payload is published.

**Defensible conclusion:** recurring native rejection and extra synthesized musical time coexist with steady aggregate VI/audio service. The ignored failure permits PCM loss. The upstream Inventory trigger and complete audible loss budget remain unobserved. Permanent closure requires the first service/consumer/task ownership violation plus a matched rendering control. PR #156 stays draft/unmerged; no mitigation or production integration follows from these findings.
