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
