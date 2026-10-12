# Unread PCM write diagnostic — one bounded capture

Diagnostic only, based on PR #160's pinned RMG v0.9.0 observer. **Do not merge.**
No game ROM changes, rich-render bypass, AI retry, timing correction or automatic
emulator execution. Original RMG and earlier observer installations stay separate.

## Why existing captures cannot answer this

The complete v05 captures contain FIFO events and RSP execution boundaries, but
no actual PCM store events or executed output identity. VI memory hashes sample
other regions. The recovered October 3 v09 state is one endpoint (duplicate
uploads), not an ownership history. None can establish an unread PCM overwrite.
This reuses their documented coverage; no FIFO reconstruction or old tests were
repeated.

## What this measures

ParaLLEl's real `rsp_dma_write()` copies words directly to RDRAM, bypassing the
core's generic SP DMA function. Callbacks surround each **actual DMA write row**.
The opt-in core probe snapshots physical addresses, AI-tail ownership and old
overlapping bytes, then checks committed bytes against the writer's source.
An alert needs all of these:

- the AI tail is accepted and has not been promoted to the active head;
- the real store overlaps that tail's effective physical range (including native
  AI carry, word alignment, SP wrap and 8 MiB RDRAM wrap);
- at least one byte actually changed, and committed bytes match the DMA source;
- the tail identity did not change during the synchronous copy.

Identical rewrites and address reuse after release are reported separately. A
latched OSTask type and task generation come from DMEM at first RSP execution;
an RSP boundary alone is not assumed to be audio. The PC field is RSP/JIT context,
not a proven exact store instruction PC. FIFO enqueue/pop IDs and write records
share **one AI ring**, preserving their ordering. The loaded ROM MD5 is recorded.
No raw PCM, ROM or guest-memory payload is exported.

This deliberately observes **ParaLLEl RSP DMA writes to the unstarted tail**.
CPU/PI/RDP/wild writes and active-head overwrite remain outside coverage. The
probe does not call AI_LEN, update Count, stall synthesis, replace samples or
change FIFO behavior. Enabled observation still adds host work and can shift
timing. A negative run does not certify health. Emulator device ownership is not
by itself proof of the console's precise read schedule; any correction must be
justified in native ROM code and remain portable.

## Install only the verified diagnostic artifact

Use the successful **RMG host observer Flatpak** run on this diagnostic PR.
Download artifact `rmg-pcm-observer-v0.9.0-flatpak`, extract it, then:

```bash
flatpak --user install ./RMG-PCM-Observer-v0.9.0.flatpak
```

The app ID is **org.mkmszr.RMGPCMObserver**. Do not uninstall your other RMG apps.
If the CI compile/export-symbol check failed, stop: there is no validated package
to test. Synthetic checks are not an emulator/gameplay validation.

Use the already failing, rich-enabled prefilled Fortress ROM:
`MKMSZR_inventory-audio-prefill_fortress_proof_v01.z64`, SHA-256
`13346ae68efd99fb9d07929d2d1016eba1fd5d065170d58235522fd9a6e505b1`.
Keep your established Mupen64Plus/ParaLLEl RSP/ParaLLEl RDP, 8 MiB RDRAM,
audio/backend and 100% speed settings. Verify them in this separate installation.
Do not substitute a selector-off/no-rich-render proof or regenerate a ROM.

## Minimum manual route: one cold boot, three-minute cap

Download this directory's Python scripts. In terminal 1, prepare identity and
leave the audible-onset marker waiting. Replace the ROM path if needed:

```bash
python3 prepare_pcm_capture.py \
  --rom "$HOME/Downloads/MKMSZR_inventory-audio-prefill_fortress_proof_v01.z64" \
  --expected-sha256 13346ae68efd99fb9d07929d2d1016eba1fd5d065170d58235522fd9a6e505b1 \
  --output-dir "$HOME/Downloads/mkmszr-pcm-session-1" \
  --mark-onset --uncertainty-seconds 3
```

The helper hashes the ROM, writes `session.json`, and **does not launch RMG**.
The stated three-second uncertainty is your estimate of noticing/reaction delay;
use a larger value if you cannot mark the sound that promptly. The marker is a
human report, not a waveform measurement.

In terminal 2, launch manually:

```bash
flatpak run --user --env=MKMSZR_TRACE=1 --env=MKMSZR_TRACE_PCM=1 org.mkmszr.RMGPCMObserver
```

1. Start **this exact ROM from cold boot**. Do not load a savestate or change speed.
   Leave the memory-hash option disabled; the PCM probe needs no VI hashing.
2. Enter Fortress through the existing Safe Stage Select, open rich Inventory,
   and follow the previously failing short populated-box sweep/idle route.
   Keep rich rows, paper/table/status, portraits and other features enabled.
3. At first audible acceleration, immediately press Enter in terminal 1. Then
   quit RMG **normally**, retaining the startup-to-onset lead-up. No full playthrough.
4. If no acceleration occurs within **three minutes after cold boot**, quit RMG
   normally and cancel the waiting marker with Ctrl+C. Keep `session.json`; do
   not create a fake onset or repeat the run. The result is inconclusive.

After exit, copy the files into the session directory:

```bash
cp "$HOME/.var/app/org.mkmszr.RMGPCMObserver/cache/"mkmszr-*-trace.bin \
   "$HOME/Downloads/mkmszr-pcm-session-1/"
```

Record any deviation, ROM/settings mismatch, elapsed time, pause/save/load use,
and whether the sound accelerated. Optional state capture is only after the
onset has already been marked; it is not required for the byte-write proof.
Send the whole session folder (identity, onset when present, notes and traces).
No ROM file belongs in that folder or on GitHub.

Offline analysis, **not an emulator run**:

```bash
python3 analyze_pcm_trace.py "$HOME/Downloads/mkmszr-pcm-session-1/mkmszr-ai-trace.bin" \
  --session "$HOME/Downloads/mkmszr-pcm-session-1/session.json" \
  --onset "$HOME/Downloads/mkmszr-pcm-session-1/onset.json" \
  --output "$HOME/Downloads/mkmszr-pcm-session-1/result.json"
```

Omit `--onset ...` when no acceleration was reported. Analyzer validation requires
protocol start, normal-exit summary, matching loaded-ROM MD5, audio task coverage,
matched write hooks, no invalid ranges and no overwritten ring. It records exact
changed unread bytes/addresses and distinguishes before/after the reported onset
window. The first FULL-status sample is also listed as a **rejection proxy**, not
an acoustic onset. Close timing remains uncertain; precedence alone is not cause.

## Decision and stop rule

- **Committed changed unread-tail bytes before the symptom:** concrete ownership
  violation to attribute to its native buffer handoff. Inspect that operation for
  a portable ROM buffer-lifetime correction. No FIFO retry or renderer deletion.
- **Violation only after failure:** may be a consequence; do not label it the
  initiator.
- **Acceleration with complete coverage but no mutation:** rules out this
  RSP-DMA/unstarted-tail replacement for this capture. Other writers/head overlap
  are missing evidence; no ownership fix or general memory-safety claim follows.
- **No acceleration, missing identity/marker/coverage, invalid range, overwritten
  ring, or unverified byte proof:** stop and report the missing evidence. Do not
  expand into another audit or request another generic gameplay run.

Actual emulator behavior/runtime parity remains pending until the maintainer's
bounded capture. Nothing in preparation authorizes an automated emulator run or
production integration.
