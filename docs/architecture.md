# Architecture

The implementation repository is intentionally separate from the reverse-engineering
Library. Research establishes addresses and behavior; this codebase promotes only
runtime/static findings that are strong enough to become guarded patch modules.

## Core flow

~~~text
CLI / browser frontend / future GUI
                 |
                 v
          RandomizerConfig
                 |
                 v
           PatchPipeline
          /      |       \
      arena   palette   future runtime patches
          \      |       /
                 v
              RomImage
                 |
           CIC-6102 CRC
                 |
                 v
          disposable ROM
~~~

RomImage owns clean-ROM validation, guarded endian reads/writes, output hashing,
and changed-range reporting. Patch modules do not open files directly.

The pipeline is frontend-agnostic: CLI, browser, and future desktop UI construct the
same configuration and call the same Python core.

## Current promoted modules

- Arena reservation: moves the allocator start from 0x801AF420 to
  0x801AF820, reserving the runtime-tested 1 KiB prefix.
- Sub-Zero palette: operates only on confirmed clothing entries 0x21..0x3F.
  All currently exposed browser recolor modes have been visually validated in
  BizHawk.
- Native payload bootstrap: low-level infrastructure for the runtime-confirmed
  file-ID 0x1B load-and-execute path. It is not enabled by the default
  user-facing build until the versioned 1 KiB code/state layout is defined.

## Native payload path

Research has runtime-confirmed:

~~~text
trailing ROM
  -> file-table ID 0x1B
  -> FUN_80065D64
  -> 0x801AF420
  -> execute through KSEG1 0xA01AF420
  -> normal return
~~~

The harmless proof wrote MKEX to the separate reserved word 0x801AF440 and
continued normally. Static analysis confirmed the raw loader waits for DMA completion
before returning, and KSEG1 instruction fetch avoids requiring explicit cache
maintenance for this bounded bootstrap.

Reusable file-table registration, payload placement, MIPS stub construction, hook
guards, and uncached execution are now implemented in patches/native_payload.py.
See docs/native-payload.md.

## Next research checkpoint

Before enabling a real runtime payload by default:

1. define a versioned layout for the reserved 1 KiB block;
2. separate executable code from persistent state explicitly;
3. prove a one-stage collected-pickup bitset using that layout;
4. only then generalize persistent pickup identity/state across stages.

## Migration order

After the runtime layout and first persistent-state proof, migrate the next known-good
native systems such as the compact safe stage selector and two-box inventory proof.
Each migration should reproduce its established behavior before the old one-off
patcher is considered superseded.
