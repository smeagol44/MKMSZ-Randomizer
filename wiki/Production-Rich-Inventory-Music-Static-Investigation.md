# MKMSZR production rich Inventory: static findings manifest

Investigation date: 2026-10-08. **Root cause remains Pending. No emulator was run, no ROM was built or modified, and PR #156 was not merged.**

## Finding and decision

The supplied state belongs exactly to full-production v02. Its permanent executable, resident HUD, active private font palettes, surviving allocator chain, music streams, audio bank, and sample DMA bookkeeping do not expose a corrupting writer. Current tempo and sequencer/sample clocks are coherent. These are substantial negative findings, not proof that the preceding runtime was healthy.

The maintainer clarified that the symptom is **tempo-only acceleration**, without a pitch increase. A concrete native mechanism can produce that distinction: **an AI enqueue can fail while the caller still advances synthesis and rotates its output buffers**. This path is Static-confirmed; its participation in the reported failure is **Hypothesis**, because the snapshot does not contain the enqueue return history. A full AI FIFO at an arbitrary stopped instruction is insufficient to prove a failed enqueue.

**Single recommended correction, conditional on the causal capture below:** retry the same native PCM enqueue while AI is full, before the producer advances synthesis. Keep the rich renderer, materialized strings, resources, palettes, allocations, and Inventory behavior intact. Do not build this correction until the manual capture establishes discarded PCM as the accelerating mechanism. If that capture is negative, this correction loses its justification; there is no established music fix to build from the present evidence.

This investigation therefore does **not** claim permanent closure. A different claim would require inventing a cause from one frozen state.

## Evidence levels and sources

- **[R] Runtime-confirmed/reported:** supplied maintainer observations; no independent emulator execution here.
- **[S] Snapshot-confirmed:** decoded bytes of this state.
- **[C] Static-confirmed:** existing ROM disassembly, current source, or the verified serializer.
- **[H] Hypothesis:** a causal explanation or proposed correction needing the named observation.
- **[U] Pending:** evidence not present or not established.

Initial GitHub main was `dc2e41dc4dadfb3742f7fa516a03e2d9346de01d`. Before documentation work, main was refreshed to `594c0877f4446eabc1dc9b93860ff54ccefe133a`; intervening changes concern Ghidra/documentation classification and do not change this Inventory implementation. Draft [PR #156](https://github.com/smeagol44/MKMSZ-Randomizer/pull/156) was inspected at `47a395ba16c7e4cecc0ba9d6de91b8a4310db32e`, base `0421f7b3eab54e3c484a19834e3f2230b6adbb05`.

`Project-Status.md` was read first. The Roadmap, Native HUD/UI, Persistence/Inventory/Lifecycle, Memory/Allocation, Address/Patch Registry, Runtime Validation, audio owner, and relevant failure records were then consulted. Previous Fortress-preload and Inventory snapshot/empty-box manifests were used as historical controls, not inherited causal conclusions. Prepared-glyph renderer experiments remain rejected.

Primary format source: [RMG v0.9.0 Mupen64Plus serializer](https://github.com/Rosalie241/RMG/blob/v0.9.0/Source/3rdParty/mupen64plus-core/src/main/savestates.c). Comparative WESS structure names came from [DOOM64-RE wessarc.h](https://github.com/Erick194/DOOM64-RE/blob/6931e678a0b2958be1b49598f2fe60712c6596e1/doom64/wessarc.h) and [audio.c](https://github.com/Erick194/DOOM64-RE/blob/6931e678a0b2958be1b49598f2fe60712c6596e1/doom64/audio.c). All addresses and operative behavior below were checked against MKMSZ's native instructions and this snapshot. DOOM64 names alone are not evidence of MKMSZ behavior.

### Input identities

| Input | Bytes | SHA-256 |
|---|---:|---|
| Clean USA Rev. 0 ROM | 16,777,216 | `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6` |
| Accepted rich-materialized Fortress proof v01 | 33,554,432 | `b73a9cba8c8a2ff0f6b96d9057dd30f36dc5b1e6e0b713d2f9d0eafb3b335c03` |
| Full-production v01 | 33,554,432 | `2bb4f2f77d187c763a74df9c223216a8195c20627e3f1aeec85be4fbff63fa95` |
| Full-production v02 | 33,554,432 | `f44e3724a8c883b720d727936cb7f4204f19acc5569ca4b0fc581007ee2b7313` |
| `musicspeedup3.state`, compressed | 1,778,782 | `b53f99327087b65e8f68193989d6b05224871ce4b7a13b3ffc76ded50471b435` |
| Decompressed state | 16,793,412 | `04b4b7ef4fcb17ba9acb33bb7d37b5b5975100c3149c81bb9cb68a4eac7b5c86` |
| Reconstructed 8 MiB RDRAM | 8,388,608 | `c82e6520194688e9b1d1f91682bce5469a216fc5bb82dfbda74a7cc3ad2f6e51` |

## 1. Savestate format, CPU position, and limits

**[C/S]** The attachment is gzip containing `M64+SAVE`, version `0x00020000`, followed by the ASCII ROM MD5. The embedded MD5 `6E2BF0F102EBE987D093C9554967E464` matches production v02 exactly. This identifies the Mupen64Plus serialization family; it does not establish the frontend/version that created it. It is not an Ares-native layout, irrespective of the attachment's conversational label.

RDRAM begins at decompressed offset `0x1BC`. Reverse each serialized 32-bit word's byte order to recover canonical big-endian N64 memory. The large state also contains TLB lookup arrays: its total file length is not the RAM size. K0 and K1 aliases map to the same recovered physical memory.

**[S]** Every byte in permanent executable `[0x80000400,0x8009A000)` matches existing v02 ROM `[0x1000,0x9AC00)`. This includes patched Inventory sites, native audio code, and the corrected ensure helper. The shared runtime also matches its source except its explicit state words and the established mutable Power-order remap. No executable damage is visible in either comparison.

Saved CPU PC is `0x80000180`, normal exception-vector entry, with EPC `0x8001C548`, Cause `0x10000400`. The interrupted operation is native palette-cache lookup, reached through glyph rendering at `0x80073CEC`; return address `0x80073D24`, SP `0x800FC828`, and source font/palette context `0x800B1D84`. **[S/C] This is an interrupt during rendering, not evidence of an exception crash.** The current controller at `0x800FC340` has its initialized stack top at `+0x628 = 0x800FC968`; the frozen SP is within that controller stack. This does not prove every earlier call path's maximum depth.

**[U]** The snapshot has no first-onset instruction, previous maximum allocation, failed enqueue count, healthy before-state, or wall-time measurement. Its format's older AI core block reconstructs both FIFO addresses from the saved DRAM register; do not infer exact per-buffer address chronology from those fields. Audio plug-in pacing and frontend settings are not fully recoverable here.

## 2. Proof versus production, including Vanilla

**[C] Production v01 → v02 changes exactly two bytes.**

| ROM byte | v01 → v02 | Instruction / purpose |
|---:|---|---|
| `0x01819A9F` | `5C → 38` | `37392D5C → 37392D38`; cached-check continuation `A01B2D5C → A01B2D38` |
| `0x01819AC7` | `F4 → D0` | `37392CF4 → 37392CD0`; preparation continuation `A01B2CF4 → A01B2CD0` |

Vanilla's immutable requirement path is `0x24` bytes shorter than Custom/Seed's mutable Powers path. The correct Vanilla prepare target initializes `t3=0` at `A01B2CD0`, then reads/counts all eight check-bit words. v01 instead entered at `A01B2CF4`, skipped the first word, and retained an unspecified caller-clobbered count register. Its cached draw target also skipped pointer/width/coordinate setup and entered at `a3=1`, using unestablished arguments. This is a concrete presentation/control-flow defect consistent with the reported stray glyph. **Its relation to later audio acceleration is not established.**

v02 reaches correct preparation and width/draw setup. Both saved validity words and digits agree with the corrected path. The two changes are outside the N64 header-CRC coverage region, so identical header CRC words between these two supplied ROMs are not evidence of a missing repair.

| Aspect | Accepted proof v01 | Production v02 | Consequence |
|---|---|---|---|
| Required Powers presentation | Custom/Seed exact-Powers family | Vanilla `REQ. XP 5100` | Different continuation layout; now correctly selected |
| Seeded assignments / Power order / enemies | Proof composition | Different generated composition | Success is not a matched seed/resource negative control |
| Configured lives / continues | 6 / 4 | 5 / 3 | Run settings differ |
| Materialized table/open/preload architecture | Accepted | Same architecture | No new glyph renderer introduced |
| Active Fortress music streams | Same bytes | Same bytes | Direct changed music-stream theory contradicted |
| Donor audio metadata | One selected Temple sample | Another selection | Difference is real, but active Fortress music waves remain clean-identical |

Proof and v02 differ in **125,946 bytes across 4,580 contiguous runs**. Exact seed text is not recoverable merely from those generated bytes; do not invent it. The accepted proof passed pickups, consumables, Combine, empty boxes, Kia/crystal, doors/elevators, and repeated Inventory use **[R]**. Its result remains valid within that composition. It does not isolate materialization as a universal speedup cure.

## 3. Resident resources and allocator reconstruction

| Meaning | Storage | Saved value |
|---|---:|---:|
| Stage | `8009A910` | `9`, Fortress |
| Arena floor | `800EECD0` | `801B3420` |
| Arena cursor | `80111ECC` | `8028C538` |
| HUD pointer | `A01B2DE0` | `801FEBA0` |
| HUD end | derived | `801FFDA0` |
| Fortress rewind argument | `802E822C` | `801FFDA8` |
| Stage resource file `43` pointer | `802E82B8` | `801F8E20` |
| Current GRUNT file `22` | `802E7DC4` | `8024A790` |
| Current GRUNT file `23` | `802E83E4` | `8026FD78` |
| Preview cache | `A01B2DE4` | `122` hex |

**[C/S]** Native allocator `8006643C` returns old cursor+8, advances by aligned size+8, and writes `FFFFFFFF / previous-boundary` at the new boundary. It has no maximum check. Native rewind `80066478` sets cursor to its argument minus eight. The nominal limit is the literal `80290990`, not a word loaded there.

The **74 surviving links** are aligned and strictly decreasing to the initialized floor. Relevant sequence:

`801B3420 → 801B3430 → 801F8E18 → 801FEB98 → 801FFDA0 → … → 8024A788 → 8026FD70 → 8028C538`.

The respective early payload sizes include `459E0` stock file `87`, `5D78` generated Fortress file `43`, and `1200` HUD; final fighter payloads are `255E0` / `1C7C0`, exactly files `22` / `23`. These three raw resources match their existing ROM files byte-for-byte. Many intermediate blocks belong to decoded packages/models and are not assigned semantic names from size alone.

At HUD end, metadata is `FFFFFFFF 801FEB98`. Anchor equals `P+1208`, so warm rewind leaves cursor at `P+1200`; the next allocation begins after the HUD. **[S] The intended Fortress preload lifetime survives in this state.** Margin to nominal ceiling is `0x4458 = 17,496` bytes. This is current margin, not a peak guarantee.

Shared file `1A` is ROM `[01816000,01819B9C)` and runtime `[801AF820,801B33BC)`, below the unchanged arena floor `801B3420`. The original rich runtime remains exactly `500` bytes at `[801B28F0,801B2DF0)`. The transport capacity ends at ROM `01819C00`; trailing capacity is reserved, not generally free.

### Static lifetime defect, separate from audio attribution

**[C]** `build_open_wrapper`, runtime `[A01B3210,A01B324C)`, loads the cached pointer and, if nonzero, stores zero to `P+1198` and `P+119C` **before** ensure-data validates/reloads it. The ensure helper only tests nonzero and `cursor >= P+1200`. Rewind-and-refill can satisfy that inequality while another owner occupies P. Native rewind does not itself invalidate the HUD cache.

A deterministic abstract counterexample: cache `P=80210008`; rewind to cursor `80200000`; another allocation covers through `80220000`. Ensure's comparison accepts P; open writes `802111A0/802111A4` through it. Neither numerical headroom nor the new session flags establish ownership. Null-pointer open and the captured resident Fortress P are negative controls: this unsafe path does not fire as a stale write there.

**[U] No such stale write is present in the supplied Fortress state, and its first failing consumer/audio path has not been identified.** Do not call this discovered invariant violation the speedup root cause. Any eventual lifecycle repair must invalidate on discard and account for native pointer-keyed palette identities; substituting another cursor-range predicate is insufficient.

## 4. Inventory hooks, rendering, and materialization

| Path | Native hook ROM / VA | Shared destination / frame | Contract checked |
|---|---|---|---|
| Inventory open | `74310 / 80073710` | `A01B3210`, leaf | Replays s4/fp/s5 setup; resumes `80073720` |
| Inventory loop | `74324 / 80073724` | `A01B3128` → switch `A01B2DF0` | Empty-Powers special case; normal switch transaction retained |
| Credential row | `74E68 / 80074268` | `A01B28F0`, frame `30` | Real backing identity; ordinary fifth font argument forwarded from new SP+40 |
| Selected preview | `73C98 / 80073098` | `A01B2980`, frame `30` | One carrier sprite `46C`; ROM portrait DMA only when stage/item selection changes |
| Paper/title/table | permanent trampoline `800742B8` | `A01B2A60`, frame `60` | Native title/width, prepare rows once, native draw every frame |
| Requirement/check status | permanent dispatcher `800742C8` | `A01B2C80`, frame `28` | Vanilla immutable XP text; check preparation and cached continuation correctly selected |
| Fortress preload | `1315C / 8001255C` | `A01B30F0`, frame `18` | Clears pointer, ensures exact 1200-byte block, publishes getter cursor+8 |

Original native Inventory `80073588` uses frame `78`, suspends/restores gameplay lists through `80028870/800288A8`, draws through `800728B0`, and sleeps one tick through `80028794`. The empty-box path does not re-enter the entire open/lifecycle prologue each frame. Overwritten instructions, delay slots, return continuations, callee-saved registers, and fifth-argument forwarding were inspected. No new concrete ABI violation was found on these traced paths; historical maximum stack depth remains unmeasured.

**[S]** LIVE slots are `[8,4,1,FFFFFFFF,FFFFFFFF,FFFFFFFF,5,8,FFFFFFFF,FFFFFFFF]`. Backing box 1 retains true IDs `10,4,1,5,1B` hex at the corresponding occupied positions; the remaining three boxes are empty. Glass placeholder `8` versus true foreign credentials is expected masking. Power count is 1; derived backing/state are not overwritten by the display materialization flags.

All `1200` HUD bytes were compared with v02's ROM template. Differences are exactly:

| HUD offset | Saved change |
|---:|---|
| `10ED` | Temple checks `0→5` |
| `10FD / 1102` | Wind checks/keys `0→1 / 0→1` |
| `111D / 112D` | Earth/Fire checks `0→4 / 0→1` |
| `1142 / 115D` | Prison keys/Fortress checks `0→1 / 0→1` |
| `1185 / 1186` | `CHKS 12-85` digits |
| `119B / 119F` | Status/table words become `2 / 1` |

Descriptors, offset tables, titles, other strings, and unused tail are unchanged. Materialization eliminates repeated changing-data writes/scans; it does **not** eliminate per-glyph native draw/palette acquisition. That distinction is central to interpreting the accepted proof.

## 5. Render nodes and palette-cache bookkeeping

**[C]** Text `80073E74` (frame `38`) parses characters and calls glyph routine `80073CEC` (frame `78`). The glyph calls `8001C528` with source `font+4`, count `100` hex, mode zero, then submits through `8001E578` (frame `88`). Seven custom 516-byte descriptors safely retain the full 256-color source span even though their visible colors use only the first 16 entries. A smaller descriptor is not authorized by a 16-color header: `8001C6D0` may force 256 colors under mode-global zero.

Native source cache: `800B7A50`, 8-byte entries = source pointer, u16 references, s16 handle. Active flags: `800B75D0`, 2-byte entries. Handle mapping: `80290600+handle*8`; converted backing: `802E71E0+handle*4`. Dynamic handles range `140..23F`. Acquire increments a 16-bit reference count. Release `8001C64C` decrements; zero calls free `8001C898`. Repeated stock glyphs also accumulate references, so large/wrapped counters alone are not causal evidence.

**[S]** Eighteen dynamic cache entries are active, indices `C0..D1`, handles `140..151`; no exhaustion is present. All 256 converted colors match for the two active private HUD sources:

| Cache / handle | Source | Backing | References |
|---|---:|---:|---:|
| `CB / 14B` | `A01FEBA4` | `803D9338` | `3098` |
| `CC / 14C` | `A01FF3B4` | `803D9538` | `4408` |

Native font entries `C1..C5`, `C7..CA`, `CD`, `D1` also match their current source across 256 colors. `CE` matches its first 16 colors but not its unused trailing source span. `CF/D0` retain old paged-resource palette copies while their source pointers now identify replaced fighter bytes. The older Fortress manifest observed the same native lifetime phenomenon. **[H/U] A retained converted copy is not automatically wrong; a failing reacquisition/consumer must be demonstrated.** No such consumer-to-audio write was recovered.

Render count `802E8234=B4` (180); cursor `802C1BB8=800DBEF0` equals `800D8110+180*58`. It is below the native `3E7` submission threshold. Upload queue top `802C16C0=FFFFFFFF` is idle. Graphics allocation cursor `801AE478=803DA138`, opposing texture boundary `800BF2FC=803FEEC0`, gap `24D88`. No current node overflow or graphics collision is visible. None of these measurements preserves earlier maxima.

## 6. Audio reconstruction and the concrete pending mechanism

**[C/S]** Native manager at `800BA528`, referenced by `800BA54C`, points to sequence slots `8016FDA8`, tracks `80170018`, and voices `80170C98`. Track stride is `50` hex, voice stride `14` hex. There is one active sequence, eight active music tracks, and nine active voices out of 32.

Sequence slot 1 (`8016FDC0`) owns event `23E` (574). Active track slots `0,2,3,4,5,6,7,9` all have PPQ `1E0` (480), QPM `7E` (126), and parts/tick `00086666` (8.4 in 16.16), consistent with the native 120 Hz callback. Their command pointers are within their resident stream bounds. All eight complete streams match v02, proof, and clean ROM bytes at `9A2FC8,9A318C,9A3894,9A39B8,9A4BB0,9A4D54,9A5040,9A5F4C`.

Entire loaded tables match v02: 683 patch records at `80140D20` ↔ ROM `947CB8`, 740 subpatch records at `801417D0` ↔ ROM `948768`, and 598 predictors at `801494F8` ↔ ROM `950490`. All 598 waveform records at `801451A0` conform to source base rebasing by `9B0650`, native flags, loop-pointer relocation, predictor pointer `801494F8+id*108` hex, and source pitch.

67 waveform lengths are shortened by one byte. **[C/S] This is native ADPCM initialization, not corruption:** `80090BF0..80090C18` computes `9*floor(len/9)` and writes the wave length. Every shortening conforms; the remaining records retain the source length. Active music waves `572,576,577,578` and their relevant subpatches/predictors are clean-identical, not the substituted Temple/Toasty carriers.

Audio sample-cache descriptor base `801123C0`, 48 entries of `14` hex bytes, each with an `800`-byte buffer. Used/free heads at `800BA444/800BA448` form consistent lists of 9 / 39 entries, covering all 48 once, with valid backward links. Every populated buffer (30) matches its recorded ROM source across all `800` bytes. Pending DMA count `800A7F64=2` is a captured in-flight count, not inherently an overflow.

| Clock/state | Saved value | Interpretation |
|---|---:|---|
| AI DAC / bit rate | `89F / F` | Normal saved DAC setting; no raised sample rate visible |
| AI status | `C0000000` | Busy and FIFO full at this instant |
| AI DRAM / length register | `0013BE70 / 680` | Last saved register pair; FIFO address history limited by format |
| FIFO lengths | `680 / 700` | 416 / 448 stereo sample frames |
| Frame/min/max sample counts | `170 / 160 / 2C0` | 368 / 352 / 704 |
| Extra samples | `140` | Native configured replenishment reserve |
| WESS ticks `800A8038` | `173FD` = 95,229 | Native callbacks |
| WESS ms `800A803C`, fraction `800A8044` | 793,574 / `8401` | Exactly `ticks * 85555` in 16.16 |
| AL player sample time `800BA4D0` | 17,522,136 | Exactly `ticks * 184` |
| Audio frames `800A7F60` | 47,461 | About two sequencer ticks/frame, with startup/loading differences |
| VI callback counter `802E7DC0` | 47,740 | Independent count; no obvious factor-of-two runaway |

### Static call path

`80000E24` VI-side service → `80000EF4` calls `8007D3FC` audio-work → `8007D4A8` frame builder → `8007D4E8` calls `8008A500` AI enqueue → **return at `8007D4F0` is ignored** → `8008910C` synthesizes another frame → callback `8007DA34` → `80083D38` WESS tick → `80085C8C` sequence engine.

`8008A500` calls full-FIFO predicate `80092E90` at `8008A550`. If full, it returns `FFFFFFFF`; if accepted, it writes AI address/length and returns zero. Caller next calls AI length getter, calculates a new sample count, invokes synthesis at `8007D55C`, and the work wrapper publishes the new `lastInfo` / rotates the three output buffers regardless of that prior enqueue result.

**[C] Deterministic contract counterexample:** input full-FIFO → enqueue returns -1 and writes no AI buffer → caller still invokes synthesis and overwrites producer bookkeeping. Not-full input → zero return and actual AI writes is the negative control. This confirms the code permits a discarded-audio path.

**[H] Tempo-only acceleration could result from sequenced time being synthesized but omitted from audible output.** Ordinary frame cost alone does not prove this path was used. The same native contract exists in clean ROM and the accepted proof, so production's provoking condition must also be identified. RSP task replacement/completion or repeated producer service are competing scheduling mechanisms; they require pending-task chronology, not guesswork. Current full FIFO may simply follow a successful enqueue.

## 7. Single conditional correction and exact guards

**Proposal [H], not built or implemented:** keep the same PCM buffer pending while AI is full. Change the enqueue routine's full-FIFO branch into a retry of its existing capacity check, before returning to the frame builder. This prevents that caller from advancing synthesis or rotating away from rejected PCM. It needs one instruction change, no new helper, no transport growth, and no reservation change.

The diagnostic must first show that failed AI enqueue/producer advance coincides with the accelerating route and differs from a matched healthy control. If failures do not occur, or pending RSP completion is the actual defect, do not apply this retry as a speculative fix.

| Guard / change | Exact contract |
|---|---|
| Existing-ROM input | SHA-256 must equal the supplied v02 hash above |
| Native edit | ROM `[0008B158,0008B15C)` / VA `[8008A558,8008A55C)` must be `1440000A`: `bnez v0,8008A584` |
| Replacement | `1440FFFD`: `bnez v0,8008A550`, retry existing `jal 80092E90` full predicate |
| Delay slot | ROM `[0008B15C,0008B160)` must remain `2402FFFF` (`v0=-1`); predicate overwrites v0 on every retry |
| Surrounding guard | ROM `[0008B150,0008B168)` must be `0C024BA4 00000000 1440000A 2402FFFF 0C023EB0 02002021` |
| Stack/calling convention | Existing `20`-byte frame and saved RA/S0/S1 unchanged; retries do not re-run the prologue, grow the stack, or change S0/S1 buffer/length |
| Address alignment bookkeeping | Native setup before `8008A550` executes once; retry does not re-apply the N64 AI address-adjustment workaround |
| Coverage | Full-ROM aligned-word census of clean, proof, and v02 finds exactly one direct call at ROM `7E0E8` / VA `8007D4E8`, and no literal `8008A500` pointer words; computed indirect targets are not excluded. Refresh the census for the exact later build |
| Reservation guards | File-1A start/end/raw, arena floor, `500`-byte rich runtime, and `1200`-byte HUD request remain byte-identical |
| Unchanged-byte audit | Only this four-byte instruction and required header CRC words may differ from supplied v02 |
| Configuration guards | Vanilla and Custom/Seed status layouts/continuations remain their respective PR156 targets; no default configuration substitution |

**Cost requiring manual validation:** this changes full-FIFO behavior from immediate failure to a short wait in the native audio service. AI must continue draining while the CPU polls. One maximum native 704-sample buffer takes about 32 ms at the configured DAC rate; this bounds an expected running-hardware wait, not a guarantee for every emulator implementation. Capture the actual wait and reject hangs, repeated timing disturbance, or input/progression regressions. This tradeoff is why the proposal must stay gated on demonstrated discarded PCM.

The branch now repeats the existing capacity predicate until space exists, then writes the original buffer once and returns zero. The caller's synthesis/publication path is unchanged, but cannot pass a full-FIFO rejection. No working text renderer, palette contract, Inventory behavior, allocation, helper placement, or pre-stage bootstrap path is replaced.

**[U]** The missing evidence is actual failed submission plus chronology. These exact guards make a future correction reviewable; they do not promote it to a verified fix. Correcting the separate stale-HUD-pointer invariant would require a different justified change and is not bundled into this recommendation.

## 8. Bounded manual causal test, then acceptance test

### Phase A: existing v02 only, no new ROM

Use an emulator/debugger that exposes native CPU breakpoints. Keep v02's configuration unchanged. The saved bad runtime may be inspected, but a healthy cold-start state before the original route is needed for first-onset attribution. Loading the bad state into another ROM is not a valid control.

1. Bound the run to **ten minutes after Fortress entry**. Save a healthy state immediately before the Inventory/Kia/door route. Hold the same selected item for 60 seconds, perform ten open/close cycles and one tour of the four boxes including an empty box, then repeat the original Kia/crystal → door/elevator Inventory sequence within the remaining time. Record selection, wall time, and first audible tempo change.
2. Set a conditional breakpoint at **`8007D4F0` when v0=`FFFFFFFF`**, the immediate return from AI enqueue. Record lastInfo pointer `800A7F70`, its buffer address and sample count, buffer index `800A7F6C`, sequencer ticks/ms, and AI status. Observe whether synthesis at `8007D55C` and publication/rotation in `8007D3FC` advance without that PCM being submitted.
3. Inspect pending RSP audio tasks at `8009A534/8009A538/8009A53C`, and the three AudioInfo records referenced by `800BA3E8..800BA3F0`. Establish whether an unfinished task/output is replaced. Capture a healthy comparator at the same selection/route and an immediate event state. A breakpoint changes wall time; use the instruction and pointer chronology for the causal decision, not stopwatch tempo while paused.
4. **Positive causal gate:** repeated rejected submissions discard sequenced intervals and occur on the tempo-change route, while the matched healthy control accepts the corresponding buffers. **Negative:** no failed enqueue, or acceleration persists while all relevant PCM is accepted; then reject the proposed gate and continue from task/clock chronology. Mere full-FIFO reads are neither result.

If the backend cannot expose this breakpoint, paired healthy/event states plus a recording of tempo-only onset are the next evidence, but do not justify pretending the return history has been recovered. A ten-minute non-reproduction does not certify a fix.

### Phase B: only after Phase A establishes the cause

After a separately reviewed correction satisfying section 7, repeat the **same bounded ten-minute route** and preserve the native renderer. During a full-FIFO retry, lastInfo/buffer index/WESS sample time must hold until the original buffer is accepted; normal frames must retain native behavior. Measure the retry duration and reject hangs or visible control/scheduling regressions. Test pickups, one consumable, Combine, Items/Powers, empty-box recovery, Kia/crystal, the door and elevator, and repeated open/close. Require normal music tempo without new gaps, preserved progression, and identical Inventory presentation. Repeat the status portion under Vanilla and Custom/Seed. Bounded success plus the observed producer invariant closes the tested mechanism; it still does not establish all-seed peak memory safety.

## 9. Hypotheses and negative controls retained

| Candidate | Evidence / disposition |
|---|---|
| Wrong Vanilla continuations | Static-confirmed in v01; corrected in v02; current digits/flags correct. Not a remaining direct v02 target bug. |
| Current resident HUD overwritten / displaced anchor | Contradicted by full payload, metadata, and 74-link chain. Prior transient histories remain unavailable. |
| Current private-palette damage / exhaustion | Contradicted by all 256 active custom colors, valid mappings, and 18 dynamic entries. Refcount-wrap history remains unmeasured. |
| Modified permanent executable / music streams / current audio bank | Contradicted by full executable match, eight exact streams, full bank/predictor checks, and all populated DMA buffers. |
| Changed sample rate / explicit bad tempo fields | Saved DAC, QPM/PPQ/PPI and clock relationships do not show it. Wall-time callback rate is not recoverable from one state. |
| Transient arena overrun | Native allocator is unchecked; current margin and chain do not measure prior peaks. No specific overrun writer recovered. |
| Stale HUD pointer through rewind/refill | Static invariant defect; no captured stale writes or music consumer. Retained as an independent Pending lifetime issue. |
| Dropped PCM / producer outruns output | Concrete permitted native call path, consistent with tempo-only symptom; failed return history missing. Sole conditional correction target. |
| Unfinished RSP task/output replacement | Native asynchronous ownership requires chronology; current task pointers alone are insufficient. Distinguish from AI queue rejection before a correction. |

Historical selector/menu/lifecycle music failures are valid rejection history, not a universal corruption signature. Earlier no-rich-render control implicates rendering participation within its own preload composition, but does not distinguish submission pressure from memory/resource ownership. Accepted materialization proof and failing production differ too broadly to make that causal choice.

## Reproduction and handoff

The companion `MKMSZR_inventory_static_audit.py` takes the state, clean ROM, accepted proof, v01, and v02 as **read-only inputs** and emits `MKMSZR_inventory_static_measurements.json`. It validates identities, serializer layout, permanent-code equality, allocator links, HUD byte differences, palette conversion, all active music streams, audio-bank rebasing/native length rounding, DMA list integrity/buffer bytes, and exact clock relationships. It has no ROM-write or emulator API. No private ROM/RDRAM payload is included in the deliverables or public documentation.

Keep PR #156 draft/unmerged. Preserve the accepted rich renderer and materialization architecture. **Current disposition: verified static negatives plus a reviewable conditional audio correction; accelerated-music root cause and permanent fix remain Pending until the causal gate is met.**
