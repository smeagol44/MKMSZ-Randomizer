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
       /        |         \
 stage menu   runtime     palette
               |
        arena reservation
               |
        native payload
               |
        pickup persistence
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
  0x801AF820, reserving the runtime-tested 1 KiB prefix in every patched ROM.
- Native payload bootstrap: reusable infrastructure for the runtime-confirmed
  file-ID 0x1B load-and-execute path.
- Runtime V1 persistence: defines the confirmed 0x200-byte code / 0x200-byte
  persistent-state split.
- Ordinary-pickup persistence: one shared manager capture hook plus manager-context
  restore persists all 84 catalogued ordinary pickup locations across the eight main
  stages. Fire uses the confirmed ordinal translation table that excludes its three
  special manager records.
- Sub-Zero palette: operates only on confirmed clothing entries 0x21..0x3F.
  All currently exposed browser recolor modes have been visually validated in BizHawk.

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

Ordinary-pickup collection is observed at the shared manager commit hook at
0x80039418. Restore runs through the pickup-manager entry path before actor
construction. Stage descriptors select one persistent bitset word per main stage.
Seven stages use manager ordinal directly; Fire translates its 19 manager ordinals
to 16 ordinary-pickup bits while excluding the three special records.

The generalized runtime test succeeded from cold boot with no savestate: at least one
ordinary pickup in each main stage was collected, the corresponding persistent bit
survived quit-to-title/re-entry, and the pickup remained absent after reconstruction.
Several Fire pickups were also exercised, and using Fire's platform-raiser special
record did not change any ordinary-pickup bit.

Reusable payload registration and loading live in patches/native_payload.py.
The V1 layout lives in patches/runtime_v1.py. The active all-stage implementation
lives in patches/pickup_persistence.py.

## User-facing boundary

The safe stage selector, 1 KiB runtime-memory reservation, native runtime payload, and
ordinary-pickup persistence are always installed by the normal CLI/browser patch
pipeline.

Scripted/special mechanisms such as Temple's Map and stage machinery remain outside
the ordinary-pickup bitset unless separately researched and promoted.

## Remaining lifecycle checks

The all-stage ordinary-pickup path is runtime-confirmed for quit-to-title and stage
reconstruction. Normal stage completion, death/game-over, and other lifecycle routes
can still be exercised separately without changing the confirmed pickup identity
design.
