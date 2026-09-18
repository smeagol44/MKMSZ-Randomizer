# Architecture

The implementation repository is intentionally separate from the reverse-engineering
Library. Research establishes addresses and behavior; this codebase promotes only
runtime/static findings that are strong enough to become guarded patch modules.

## Core flow

```text
CLI / future GUI / future web frontend
                 |
                 v
          RandomizerConfig
                 |
                 v
           PatchPipeline
          /      |       \
      arena   palette   future native patches
          \      |       /
                 v
              RomImage
                 |
           CIC-6102 CRC
                 |
                 v
          disposable ROM
```

`RomImage` owns clean-ROM validation, guarded endian reads/writes, output hashing,
and changed-range reporting. Patch modules do not open files directly.

The pipeline is frontend-agnostic: CLI, desktop UI, and a future browser frontend
should construct the same configuration and call the same core.

## Current promoted modules

- Arena reservation: moves the allocator start from `0x801AF420` to
  `0x801AF820`, reserving the runtime-tested 1 KiB prefix.
- Sub-Zero palette: operates only on confirmed clothing entries `0x21..0x3F`.
  Exact red and green preserve the runtime-tested transforms; hue/RGB/seeded modes
  generalize the same source palette.

## Payload direction

Research has runtime-confirmed:

```text
trailing ROM -> file-table ID 0x1B -> FUN_80065D64 -> 0x801AF420
```

Loaded-code execution is deliberately not promoted into a production patch yet.
After the harmless execution proof, payload allocation, file-table registration,
and runtime-state layout should become dedicated modules.

## Migration order

Next known-good native systems to migrate are the compact safe stage selector and
the two-box inventory proof. Each migration should reproduce its established output
bytes/hash before the old one-off patcher is considered superseded.
