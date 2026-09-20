# Persistence, inventory, and lifecycle

## Ordinary-pickup persistence

The native game reconstructs stage pickup records, so a per-location runtime bitset is the production authority for randomizer collection state. Production state V2 lives at `0x801AF720..0x801AF81F`, begins with `MKSV`, and assigns one 32-bit word to each main stage. The exact header and word layout are in [Data structures and encodings](Data-Structures-and-Encodings).

Capture hooks the collected-flag store at `0x80039418`; `a1` is the record and `s2` is manager ordinal. Restore hooks `0x80038ACC` before the manager's first `+0x2C` read and walks the current record array using the effective context pointer at `0x802ECE20`, count `+0x6F4`, and base `+0x6F8`.

For seven stages, manager ordinal equals catalog bit. Fire has 19 manager entries for 16 ordinary records, so production uses this explicit translation:

```text
[2, 5, 4, FF, FF, FF, 9, 14, 0, 1, 8, 11, 12, 3, 7, 6, 10, 13, 15]
```

The three `FF` entries are special type-4 records and never enter the ordinary bitset.

Runtime testing collected and restored at least one ordinary pickup in every main stage, multiple Fire items, and completed Temple coverage. That does not equal 84 individual tests.

Progression state is separate: V2 state `+0x40` stores the number of progression rewards acquired and `+0x44` stores persistent XP. Diagnostic B runtime-confirmed XP 258 and two unlocked moves surviving Temple -> Wind and title-menu -> Fire.

At the pickup-manager stage-init boundary, the progression restore helper writes only persistent XP before continuing into the established four-box reconstruction. It does not call the native tier evaluator. Calling that evaluator at this boundary is rejected because it caused the pre-gameplay hang in the first production attempt.

Game Over/new-game reset behavior is still pending.

## Four-box inventory

The game continues to see its stock ten-word live array at `0x800A600C`. Four backing arrays are authoritative:

| Box | Range |
|---:|---:|
| 1 | `0x800A6048..0x800A606F` |
| 2 | `0x800A6070..0x800A6097` |
| 3 | `0x800A6098..0x800A60BF` |
| 4 | `0x800A60C0..0x800A60E7` |

State at `0x800A60E8` stores active index bits `0..1` and input latch `0x100`; magic `MKBX` at `0x800A60EC` distinguishes initialized backing data. The design deliberately has no auto-spill and no global item scan: only the active backing box is copied into the live window.

## Switching input

Outside the inventory menu, hold **Block + Use + Right/Left** to advance or reverse the active box. The hook reads normalized semantic action state at `0x800BF2EE`, so control remapping is respected. A latch prevents repeated switching while the chord remains held.

The native HUD displays `BOX n OF 4` at `(230,210)`. It reads the existing state byte and introduces no new lifecycle state.

## Stage-local key masking

Keys should be usable only in their origin stage. When backing data is copied to live inventory, foreign-stage IDs `0x0D..0x22` are represented as Glass `0x08`; the backing word remains unchanged. Production changes Glass's item-use dispatch from consuming stub `0x80071F58` to inert return-zero stub `0x80071F50`, making the placeholder safe. The Tablet (`0x24`) was rejected because its use path is consumable.

The stage mapping is Temple Map `0x0D`; Wind `0x0E..0x10`; Earth `0x11..0x13`; Water `0x14..0x16`; Fire `0x17..0x19`; Prison `0x1A..0x1C`; Bridge `0x1D..0x1F`; Fortress `0x20..0x22`.

## Lifecycle hooks

- The stock sanitizer at `0x8007AD00` is replaced by a fixed-size mask-copy routine rather than deleting special IDs.
- The stock default loader at `0x8007AD4C` becomes an initialization/reconstruction boundary for live/backing state.
- Transition wrappers commit non-placeholder live items back to the active backing box; Glass slots are skipped so hidden true keys survive.
- Saves serialize the filtered live view through the established game path; loads rebuild live state from authoritative backing data and current-stage masking.
- Title-menu START was the destructive live-window boundary in stock behavior and is explicitly intercepted.

Normal save logic is preserved. Only selector-triggered immediate stage-entry save is suppressed, as documented in [Flow bypasses](Flow-Bypasses).


## Progression lifecycle evidence

**Runtime-confirmed on seed `BCBDBF`:**

- progression acquisition established native move tiers at XP 85 and 258;
- a normal Temple -> Wind transition preserved XP 258 and both unlocked moves;
- quitting to the title menu and directly entering Fire also preserved XP 258 and both moves.

This shows that, on the tested routes, the move-tier state established at acquisition survives without re-running the tier evaluator during stage initialization.
