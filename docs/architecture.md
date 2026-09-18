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
       /        |        \
 stage menu   arena     palette
                 |
          future runtime patches
                 |
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

- Safe stage selector: the runtime-confirmed compact eight-stage selector is a core
  randomizer feature and is applied to every patched ROM.
- Arena reservation: moves the allocator start from 0x801AF420 to
  0x801AF820, reserving the runtime-tested 1 KiB prefix when enabled.
- Sub-Zero palette: operates only on confirmed clothing entries 0x21..0x3F.
  All currently exposed browser recolor modes have been visually validated in
  BizHawk.
- Native payload bootstrap: reusable infrastructure for the runtime-confirmed
  file-ID 0x1B load-and-execute path.
- Runtime V1 persistence: defines the confirmed 0x200-byte code / 0x200-byte
  persistent-state split.
- Manager-level Fire persistence: runtime-confirmed shared capture at the pickup
  manager's native commit point and manager-context restore for Fire Temple's starting
  Potion while leaving its item callback untouched.

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

The first persistence proof used a per-item callback. The follow-up proof confirmed
the better shared architecture: collection can be observed at the manager commit hook
at 0x80039418 and restored through manager context before actor construction. Fire
Temple's starting Potion remains the bounded runtime-confirmed mapping.

Reusable payload registration and loading live in patches/native_payload.py.
The V1 layout lives in patches/runtime_v1.py. The confirmed shared-manager Fire path
lives in patches/manager_persistence.py.

## User-facing boundary

The safe stage selector is always installed by the normal CLI/browser patch pipeline.

Manager-level persistent pickup handling is not yet installed by the normal pipeline.
Its mechanism is runtime-confirmed for the Fire starting Potion, but all-stage
descriptor/translation handling still needs runtime validation before it becomes a
normal randomizer feature.

## Next research checkpoint

Generalize stable pickup identities and collected-bitset capture/restore across
all eight catalogued main stages, without adding expanded inventory, seed logic,
or item randomization in the same research step.
