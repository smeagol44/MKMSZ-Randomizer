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
- Native payload bootstrap: reusable infrastructure for the runtime-confirmed
  file-ID 0x1B load-and-execute path.
- Runtime V1 persistence: defines the confirmed 0x200-byte code / 0x200-byte
  state split and reproduces the first native Fire-Potion collected-state proof.

## Native runtime path

Research has runtime-confirmed:

~~~text
trailing ROM
  -> file-table ID 0x1B
  -> FUN_80065D64
  -> reloadable code at 0x801AF420..0x801AF61F
  -> execute through KSEG1
  -> persistent V1 state at 0x801AF620..0x801AF81F
~~~

The V1 header is MKSV / version 1 / state size 0x200 / header size 0x20.
Fire Temple's starting Potion is the first proven persistent pickup: collection
sets bit 0 at 0x801AF640, and the pickup-manager restore hook reapplies the
native collected flag before actor construction after stage reconstruction.

Reusable payload registration and loading live in patches/native_payload.py.
The V1 layout and bounded Fire persistence path live in patches/runtime_v1.py.
See docs/native-payload.md and docs/runtime-v1.md.

## User-facing boundary

The browser and CLI do not install runtime V1 persistence yet. The confirmed
scope is one pickup in one stage; exposing it as a normal randomizer feature
would imply broader support than has been proven.

## Next research checkpoint

Generalize stable pickup identities and collected-bitset capture/restore across
all eight catalogued main stages, without adding expanded inventory, seed logic,
or item randomization in the same research step.

## Migration order

After generalized pickup persistence is proven, promote that result into the
runtime module and then continue migrating other known-good native systems such
as the compact safe stage selector and two-box inventory proof.
