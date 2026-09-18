# Native payload bootstrap

The research workspace has runtime-confirmed the complete bounded path:

~~~text
ROM payload
  -> file-table ID 0x1B
  -> FUN_80065D64
  -> reserved RDRAM at 0x801AF420
  -> uncached KSEG1 execution at 0xA01AF420
  -> normal return
~~~

The harmless execution proof wrote marker MKEX to 0x801AF440 and then continued
normal emulation. The raw loader was also statically confirmed to wait for DMA
completion before returning.

## Promoted implementation pieces

NativePayloadPatch owns the reusable low-level mechanics:

- guard and populate file-table entry 0x1B;
- place a raw payload in the confirmed trailing-ROM region beginning at
  0x00F10000;
- install the confirmed arena-reset hook at ROM 0x00066FE0;
- install the loader/call stub at ROM 0x0009AD84;
- call the loaded routine through its KSEG1 alias so the bootstrap does not depend
  on unknown I-cache state;
- return normally to the original caller.

The MIPS encoding helpers used to construct the stub live in mkmszr.mips.

Runtime layout V1 now builds on this bootstrap with a 0x200-byte code image and
a separate 0x200-byte persistent state region. See docs/runtime-v1.md.

## User-facing boundary

The native bootstrap and V1 persistence modules remain **disabled in the normal
CLI/browser pipeline**. The current persistence proof covers only Fire Temple's
starting Potion. Multi-stage identity/capture/restore must be generalized before
the native runtime becomes a normal randomizer feature.

## Confirmed addresses

| Purpose | Address |
| --- | --- |
| Reserved block | 0x801AF420..0x801AF81F |
| File-table entry 0x1B | ROM 0x000A5154 |
| Raw loader | VA 0x80065D64 |
| Payload ROM start | 0x00F10000 |
| Payload RDRAM start | 0x801AF420 |
| Uncached execution alias | 0xA01AF420 |
| Arena-reset hook | ROM 0x00066FE0 / VA 0x800663E0 |
| Bootstrap stub | ROM 0x0009AD84 / VA 0x8009A184 |
