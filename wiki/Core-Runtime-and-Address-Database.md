# Core runtime and native payload

> **Scope:** This page is the canonical owner for MKMSZR's **native runtime architecture**: arena-reservation mechanism, file-`0x1B` payload loading/bootstrap, Runtime V2 composition, pickup-persistence hook architecture, and stage-init composition.
>
> It does **not** own continuous ROM/RDRAM allocation intervals, exact guarded ROM edits, or function semantics. Those belong respectively to [Memory and allocation map](Memory-and-Allocation-Map), [Address and patch-site registry](Address-and-Patch-Site-Registry), and [Function registry](Function-Registry). The stable `Core-Runtime-and-Address-Database` slug is retained for existing links.

## Clean target and invariants

Only the 16 MiB USA Rev. 0 big-endian ROM is supported: SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`. Every stock edit uses an expected-byte guard. A patch failure stops the build before output, and the clean input is never modified in place.

## Arena reservation mechanism

Production reserves one 16 KiB block immediately below the game's shifted main-arena start. Architecturally, stock construction begins the arena at KSEG0 `0x801AF420`; production moves the floor to `0x801B3420`. The established Runtime V2 code/state contract remains byte-for-byte in the first 1 KiB, `0x801AF420..0x801AF820`, while `0x801AF820..0x801B3420` is a 15 KiB build-time expansion pool. Both guarded arena-address constructions must move together.

The **exact continuous reservation and every current sub-owner** are canonical in [Memory and allocation map](Memory-and-Allocation-Map). The two guarded ROM instructions that move the arena start, including expected and replacement words, are canonical in the [patch-site registry](Address-and-Patch-Site-Registry).

After relocation, the bootstrap establishes the shifted arena floor `0x801B3420` in persistent/reset base global `0x800EECD0` and uses `0x80066390` to copy that floor into the live bump cursor at `0x80111ECC`. The two globals therefore have distinct roles: `0x800EECD0` is the reset/base floor, while `0x80111ECC` is the transient allocation cursor. [Function registry](Function-Registry) owns the helper/allocator semantics. The expansion pool below `0x801B3420` is production-reserved MKMSZR ownership; memory above that anchor remains allocator-owned rather than generically free.

## Arena allocator model

Static tracing of the clean USA Rev. 0 image establishes the stock arena as an 8-byte-aligned stack/bump allocator family:

- persistent/reset base: `0x800EECD0`;
- live bump cursor: `0x80111ECC`;
- bump boundary: `0x80290990`;
- main allocator: `0x8006643C`;
- rewind: `0x80066478`;
- remaining-capacity query: `0x80066420`.

The main allocator returns `old_cursor + 8`, aligns requested payload size to 8 bytes, advances the live cursor, and writes 8 bytes of bookkeeping at the new cursor. It contains no internal bounds check. The capacity helper computes `(0x80290990 - cursor) >> 3`; immediately adjacent fixed runtime state begins at `0x80290998`, so a cursor at `0x80290990` consumes the final bookkeeping word and any further allocation would enter fixed state.

Rewind is stack-like: `0x80066478(pointer)` sets the cursor to `pointer - 8`. `0x80066410` returns `cursor + 8` without allocating, allowing callers to save a reversible checkpoint. This explains stage-lifetime reconstruction paths that save a checkpoint, allocate resources, and later rewind/rebuild them.

These allocator findings are **Static-confirmed**. The 16 KiB production floor is separately **Runtime-confirmed** to the bounded profiler and full-production routes documented in [Runtime validation status](Runtime-Validation-Status). Headroom remains workload-dependent; the measured margin is not a guarantee for arbitrary future feature composition.

## Runtime V2 composition

Core Runtime owns how the reserved block is composed; the Memory Map owns its absolute intervals, aliases, lifecycle, and availability.

| Runtime-relative slice | Architectural role | Canonical Memory Map owner |
|---|---|---|
| `[+0x000,+0x1D4)` | Runtime V2 initialization plus pickup-persistence core | `rdram.production.runtime_core` |
| `[+0x1D4,+0x200)` | Four-box filtered-save helper | `rdram.production.inventory_payload` |
| `[+0x200,+0x2E0)` | XP callback, threshold table, XP-only restore helper, and bounded padding | `rdram.production.xp_payload` |
| `[+0x2E0,+0x3B0)` | Optional runtime feature tail; `rainbow` owns `[+0x2E0,+0x3AC)`, final 4 bytes remain reserved | `rdram.production.optional_runtime_tail` |
| `[+0x3B0,+0x3D0)` | `MKSV` V2 state header | `rdram.production.state_header` |
| `[+0x3D0,+0x3F0)` | Eight ordinary-pickup persistence bitsets | `rdram.production.pickup_state` |
| `[+0x3F0,+0x3F8)` | Progression acquired-count and persistent-XP words | `rdram.production.xp_state` |
| `[+0x3F8,+0x3FC)` | Optional rainbow phase word | `rdram.production.rainbow_phase` |
| `[+0x3FC,+0x400)` | Reserved persistent-state tail | `rdram.production.state_reserved_tail` |

These offsets are composition contracts, not a second allocation registry. New code/state owners must fit the versioned layout and pass the same composition/bounds checks before production use.

### Expansion pool

The remaining reserved range `0x801AF820..0x801B3420` is managed by the build-time `ExpansionPoolAllocator`. It is a monotonic aligned allocator used while constructing a ROM; it does **not** replace or consume the stock runtime arena allocator. No production feature owns a subrange yet. Requests receive named, aligned slices, duplicate names are rejected, and a build fails before output if the pool would overflow. The Memory Map remains canonical for any sub-owner once a feature actually claims bytes.

## Payload registration and bootstrap

Global file ID `0x1B` is the production transport for the reloadable native payload. Its file-table semantics belong to [Resource and overlay system](ROM-Overlay-and-Resource-Map), while exact ownership of the patched file entry, generated ROM payload source, runtime destination, and bootstrap composite belongs to [Memory and allocation map](Memory-and-Allocation-Map).

The stage-load bootstrap is called from the guarded production hook and:

1. loads file `0x1B` synchronously through raw loader `0x80065D64` into the reserved runtime base, using the uncached alias where required;
2. synchronizes the relocated arena pointer;
3. enters the Runtime V2 initialization/persistence path; and
4. returns to the stock stage-load flow with the arena boundary and runtime state composed.

The bootstrap stub itself lives inside Memory Map region `rom.production.bootstrap_composite`. The generated payload source is `rom.production.payload_source`. Exact bootstrap-hook bytes remain in the patch-site registry, and function meanings for the loader/synchronization helper remain in Function Registry.

## Pickup-persistence hook architecture

Persistence is composed around the stock pickup manager rather than replacing the manager wholesale.

- **Capture:** after the stock collected flag is stored, the helper records the stage/manager ordinal in the persistent bitset while preserving the displaced store. At that point `a1` is the pickup record and `s2` is the manager ordinal.
- **Restore:** before the manager's first collected-flag read, the restore path reconstructs collected state from the persistent bitset and then resumes the stock manager.
- **Context:** the live manager/process pointer is at effective address `0x802ECE20`; context `+0x6F4` is record count and `+0x6F8` is the record base. This corrects the superseded `0x802FCE20` reading.

The exact capture/restore ROM edits are canonical in the patch-site registry. The manager's function meaning is canonical in Function Registry. Absolute persistent-state ranges are canonical in the Memory Map.

## Production allocation boundary

This page no longer maintains a competing flat cave/allocation table. Current production cave and runtime ownership is canonical in [Memory and allocation map](Memory-and-Allocation-Map), including:

- `rom.production.inventory_action_cave`;
- `rom.production.inventory_helper_cave`;
- `rom.production.bootstrap_composite`;
- `rom.production.box_indicator`;
- `rom.production.payload_source`; and
- all `rdram.production.*` Runtime V2 code/state sub-owners.

Historical proof use does not make any of those ranges reusable. The Memory Map also owns the required negative example `rom.stock.false_zero_cave`: the zero-filled action/dispatch records around ROM `0xA1308` are live stock data, not padding.

## Preserved analysis project

The canonical N64 Ghidra program was reconstructed from the clean ROM rather than an old RDRAM dump. The archived project hash is SHA-256 `fbe071…`; it is provenance, not needed to use the address tables in this Wiki.


## Stage-init composition and XP rule

Diagnostic B established the production-safe stage-load composition. The stage-init restore path writes persistent XP back to `0x8011200C` and then performs the existing four-box reconstruction. It does **not** call native tier evaluator `0x80074FBC` there.

Calling the evaluator at this pickup-manager initialization point is **Rejected / failed**: the earlier build hung before gameplay became visible. The evaluator remains Runtime-confirmed on the progression-pickup acquisition path.

This page owns that composition rule. Exact XP patch sites belong to the patch-site registry, `0x80074FBC` semantics belong to Function Registry, and persistent XP/state intervals belong to the Memory Map.
