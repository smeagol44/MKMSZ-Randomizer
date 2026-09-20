# ROM, overlay, and resource map

## Global file mechanism

The global file table begins at ROM `0x000A5010` / VA `0x800A4410`. Entries are 12 bytes. Production claims file ID `0x1B` at ROM `0x000A5154` for the MKMSZR native payload, stored at ROM `0x00F10000`. The raw loader at `0x80065D64` is synchronous in the proven bootstrap path.

## Main stage resource files

| Stage | ID | File-table entry ROM | Resource ROM range | Size | Verified runtime base | Slots | Pickups |
|---|---:|---:|---:|---:|---:|---:|---:|
| Temple | `0` | `0xA5490` | `0x513710..0x52336F` | `0xFC60` | `0x80226E28` | 17 | 4 |
| Wind | `1` | `0xA561C` | `0x698680..0x69A81F` | `0x21A0` | `0x80264FC8` | 12 | 6 |
| Water | `2` | `0xA558C` | `0x611780..0x617C5F` | `0x64E0` | `0x802504A8` | 29 | 9 |
| Earth | `3` | `0xA5670` | `0x6BAEC0..0x6DD46F` | `0x225B0` | `0x802434B8` | 65 | 20 |
| Prison | `4` | `0xA537C` | `0x41C680..0x420F6F` | `0x48F0` | `0x801FB798` | 12 | 10 |
| Fire | `5` | `0xA52E0` | `0x388260..0x38A78F` | `0x2530` | `0x80224C88` | 27 | 16 |
| Bridge | `8` | `0xA51E4` | `0x296140..0x29A46F` | `0x4330` | `0x80243000` | 25 | 10 |
| Fortress | `9` | `0xA5334` | `0x3B9700..0x3BCD1F` | `0x3620` | `0x801F4E20` | 7 | 9 |

Every slot, pickup record, and recognized embedded/external resource record is reproduced under [Stage catalogs](Stage-Catalogs).

## Resource-table rules

The first words of a stage resource file form a stage-local outer selector table. A pickup's `+0x24` word indexes this table; it is not a global resource ID. Occupied entries can point to embedded-data bundles, external-resource-ID bundles, zero-terminated lists, aliases, or still-unresolved valid structures.

A zero entry gives selector capacity only. It does not reserve or reveal physical bytes in the file. Safe foreign import requires storage with explicit bounds, relocation/expansion or other proven ownership, updated file-table size/location, descriptor integrity, arena headroom, and runtime validation.

## Proven Fire expansion

The foreign Prison-key pickup proof relocated Fire's `0x2530`-byte file to ROM `0x00F00000`, expanded it through `0x00F02BE7` (`0x2BE8` bytes), made logical slot 5 point to an appended descriptor at file offset `0x2530`, stored resource records at `0x2558..0x25F7`, and appended data through `0x2BE7`. A dedicated callback at VA `0x8008EAEC` / ROM `0x0008F6EC` awarded inventory ID `0x1A`. This proves the architecture; those exact locations now overlap production cave planning and are not a reusable allocation promise.

## Overlay identity warning

Addresses at or above the stage-overlay base describe the currently loaded stage overlay. Always name the stage and source artifact when recording an overlay function. Do not promote an overlay address to a global function merely because it appeared stable in one stage.


## Global-randomizer materialization split

The runtime-confirmed foreign Prison-key import proves that exact foreign world art can be imported by relocating/expanding a stage resource file and rebasing a bundle. That remains the path for exact cross-stage visuals.

For 1.0 logic, however, a lighter strategy is now under test: preserve each destination's native world-actor resource shell and change only the logical award callback/parameter. If runtime-confirmed, the global randomizer will not require resource-file expansion for every cross-stage placement. Resource importing then becomes optional per-item presentation work rather than the core logical-randomization dependency.

Fortress and Prison still have no immediate free logical selectors, so this distinction materially reduces 1.0 allocation risk.
