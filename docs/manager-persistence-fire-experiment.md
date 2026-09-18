# Manager-level persistence Fire experiment

This branch implements the smallest runtime experiment recommended by canonical
research report v37. It is **not runtime-confirmed yet** and must not be merged
until manual BizHawk validation succeeds.

## What changes from the confirmed V1 proof

The Fire starting Potion callback remains the clean native value:

`0x800388FC`

Collection is captured only through the shared pickup-manager commit hook:

- hook: ROM `0x0003A018` / VA `0x80039418`
- original: `sw v0,0x2C(a1)`
- experimental replacement: `jal 0x8009A1E8`
- original next instruction remains the JAL delay slot

The permanent helper reproduces the native collected-flag store and, only for
Fire manager ordinal 8, sets V1 Fire bit 0.

Restore remains at manager entry, but no longer writes the absolute Fire record
address. It reads the manager context pointer at `0x802ECE20`, requires the
live record count to equal 19, obtains the record-array base from context
`+0x6F8`, and restores ordinal 8 before actor construction.

## Code placement

- V1 initialization: `0xA01AF420`
- manager-context restore scanner: `0xA01AF4C0`
- permanent restore trampoline: `0x8009A1D8`
- permanent capture helper: `0x8009A1E8`

The payload remains exactly `0x200` bytes and persistent state remains the
existing V1 `0x200`-byte state half.

## Manual validation target

Use a fresh cold boot with no savestate load.

1. Verify the V1 header initializes and Fire bit 0 is clear.
2. Enter Fire.
3. Confirm the Potion callback is still `0x800388FC`.
4. Collect the starting Potion normally.
5. Confirm the native flag becomes 1 and Fire bit 0 becomes 1.
6. Quit to title without loading a savestate.
7. Re-enter/reconstruct Fire.
8. Confirm the native flag is restored and the Potion remains absent.
9. Continue normal emulation long enough to establish safe return/stability.

Use `tools/verify_manager_persistence_fire_experiment.lua` for the address
checks. The experiment should be promoted only after this lifecycle passes.
