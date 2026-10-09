# MKMSZR host observer — experimental RMG v0.9.0

**Status: unverified diagnostic**, not a fix or production release. Lives only in draft PR #157; PR #156 remains draft.

The GitHub Actions job attempts to build `org.mkmszr.RMGObserver` using Flathub's pinned RMG v0.9.0 source (`453f6639734537908c4c2ca35244255bc5424e3d`) and KDE 6.11 runtime, leaving `com.github.Rosalie241.RMG` installed through Bazaar alone.

## Use only after CI build verification

Install the resulting Flatpak artifact manually, **without uninstalling** your original RMG:

```bash
flatpak --user install ./RMG-Host-Observer-v0.9.0.flatpak
flatpak run --user --env=MKMSZR_TRACE=1 org.mkmszr.RMGObserver
```

The observer reads `MKMSZR_TRACE` once, before its first recorded event. Omitting `MKMSZR_TRACE=1` leaves the observation hot path disabled.

On clean emulator exit, independent binary traces are written to the app's `XDG_CACHE_HOME` as `mkmszr-ai-trace.bin`, `mkmszr-vi-trace.bin`, `mkmszr-rsp-trace.bin`, `mkmszr-host-audio-trace.bin`, when their event-producing libraries ran and files could be created. The file format starts with the ASCII magic `MZRHST1` (padded to eight bytes), version, record size, saved/total/overwritten counts, and timestamped event records. The ring holds 32,768 recent entries **per compilation unit**; earlier records overwritten at wrap are unavailable, and all analyses must honor their lost-record counts. Do not interpret gaps across independent rings as an ordered guest/host trace without monotonic-time matching.

This instrumentation collects no raw ROM, guest memory contents, screenshots or PCM. It logs event metadata only. It is **not yet verified against the specific user's live timing failure**; even opt-in observation can perturb wall-time scheduling, and an observer-disabled negative control is mandatory.

Do not run the eight-minute workload until the observer passes compile, install, trace-extraction and disabled-mode parity checks. Never compare this app's implicit per-ROM settings to the original without verifying them.

## v02 RDRAM observation: separate, opt-in follow-on

The draft v02 observer is based on the already separate v01 host observer; it is **not a game ROM patch, not a mitigation**, and is not production approved. It adds two records to the existing **VI trace ring**, in addition to existing AI/VI/RSP/SDL events, only when **both** `MKMSZR_TRACE=1` and `MKMSZR_TRACE_MEM=1`. Omitting the latter preserves v01-only event collection and avoids the RDRAM hash loop. Do not launch it for testing until this branch's actual pinned Flatpak build and opt-out parity are verified.

Manual v02 launch (side-by-side; original Bazaar RMG is unaffected):

```bash
flatpak run --user --env=MKMSZR_TRACE=1 --env=MKMSZR_TRACE_MEM=1 org.mkmszr.RMGObserver
```

Event `0x40` (once per VI) records `arena_cursor 0x80111ECC`, `arena_reset_base 0x800EECD0`, HUD dynamic arena pointer `0x801B2DE0`, stage index `0x8009A910`, MKSV state magic `0x801AF7D0`, native audio-frame count `0x800A7F60`, maximum sampled cursor in this emulator process, and flags. Bits 0–4 of flags mean (0) expected arena base, (1) cursor between base and `0x80290990`, (2) HUD pointer in the bounded arena region, (3) cursor covers the HUD block end, (4) MKSV magic present. Outside gameplay/load lifecycle, unset bits are not necessarily corruption.

Event `0x41` (same VI Count) records FNV-derived word hashes of fixed rich HUD code `[0x801B28F0,0x801B2DE0)`, Inventory legend `[0x801B2F50,0x801B30E4)`, and optional materialized helper code `[0x801B30F0,0x801B33BC)`; then HUD selected-preview cache, box flags, native audio-work gate, output-record index and second cursor sample. Fixed-region hashes are *change detectors*, not confirmed corruption: transitions, load/clear and absent optional modules can legitimately alter them.

The observer reads **physical RDRAM words directly** through `vi->mi->r4300->rdram->dram`; it performs no guest MMIO reads/writes, no AI sampling beyond v01, no game control changes and no ROM modification. Every VI sample uses ~550 word-hash iterations. Event records are metadata only; no ROM bytes or full RDRAM are exported. VI sampling cannot see a transient writer and its repair between VIs or reconstruct true allocation-call stacks/peak. High-water is a **sampled** high-water, not a hardware/allocator alarm or guaranteed historical maximum.

Offline decoder:

```bash
python3 analyze_memory_trace.py mkmszr-vi-trace.bin --ai mkmszr-ai-trace.bin
```

It refuses overwritten trace rings and reports arena bounds, HUD pointer validity, code-hash changes during stable stage, and guest rejection counts. A positive alert requires manual lifecycle attribution; zero alerts do *not* certify memory safety.

**Shortest useful manual route, after CI/installation and parity:** cold-boot prefilled Fortress diagnostic v01 through Safe Stage Select, open rich Inventory, move selection through both ordinary and key entries for 30 seconds and leave idle until 90–120 seconds after entry. End earlier if an audio symptom occurs; exit normally, preserving all VI/AI/RSP/host-audio traces. An ordinary-items-only variant is optional if the first capture contains informative violations. No combat or stage progression is required. Record host time of audible symptom and whether a savestate or pause was used. This is a first-pass observation, not exhaustive validation. The existing severe Trace (5) cannot be retrospectively given new memory events.

**Release gate:** this tool does not authorize changing 16 KiB arena floor, deleting Toasty/controls/HUD, installing native AI retry, declaring an emulator defect, or merging diagnostic PRs. The first offending write/allocation/owner must still be identified by reproducible evidence before proposing a guarded native change.
