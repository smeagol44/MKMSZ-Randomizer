# Manager-level Fire persistence

The shared pickup-manager capture/restore architecture from canonical research report
v37 is runtime-confirmed for Fire Temple's starting Potion.

## Confirmed behavior

The Potion's native callback remains untouched at `0x800388FC`.

Collection is captured through the shared pickup-manager commit hook:

- hook: ROM `0x0003A018` / VA `0x80039418`
- original: `sw v0,0x2C(a1)`
- replacement: `jal 0x8009A1E8`
- original next instruction remains the JAL delay slot

The permanent helper reproduces the native collected-flag store and, for Fire manager
ordinal 8, sets V1 Fire bit 0.

Restore remains at manager entry but resolves the record through manager context rather
than the Potion's absolute runtime address. It reads the manager context pointer at
`0x802ECE20`, requires the live Fire record count to equal 19, obtains the record-array
base from context `+0x6F8`, and restores ordinal 8 before actor construction.

## Runtime evidence

The manual BizHawk 2.11.1 / Ares64 test used a cold boot and no savestate.

After collecting the starting Potion:

- V1 header remained valid;
- Fire bit 0 was `1`;
- native Potion flag was `1`;
- the item callback remained vanilla at `0x800388FC`.

After quitting to title and entering Fire again:

- V1 Fire bit 0 was still `1`;
- the reconstructed native flag was restored to `1`;
- the Potion remained absent;
- the native callback was still vanilla.

This confirms that the shared manager-level mechanism, rather than a per-item callback
patch, can maintain the proven Fire pickup state across stage reconstruction.

## Scope boundary

This implementation remains bounded to the already-tested Fire Potion mapping. It is
not yet enabled in the normal browser/CLI pipeline. The next research milestone is
runtime validation of the generalized descriptor/translation design across the eight
catalogued main stages.
