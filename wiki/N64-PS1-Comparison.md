# N64–PS1 comparison

The ports share strong source/data lineage, but they do not share executable addresses, overlay placement, file containers, patch sites, free-memory claims, or checksum behavior.

| Concept | N64 USA Rev. 0 | PS1 `SLUS_004.76` | Transfer status |
|---|---|---|---|
| Executable base | Cartridge segments/overlays; main overlay base `0x802ECE30` | Payload `0x80010000`, overlay base near `0x80130FF8` | Concept only |
| Stage selector | `0x8000D0B8`, index `0x800C11E0` | `0x8002A688`, index `0x800D8150` | Same label order; separate activation |
| Ordinary pickups | 84 records, manager `0x80038ACC` | 84 records, manager `0x8005499C` | Record grammar strongly shared |
| Pickup record | `0x30` bytes; identity `+0x10..+0x2B` | Same structure | Field semantics transferable; addresses are not |
| Inventory | `0x800A600C`, insertion `0x80075448` | `0x800ACE28`, insertion `0x8004C0B0` | Ten-word design shared |
| Enemy chain | `71500 -> 719F0 -> 71B20 -> 2FCDC` | `3955C -> 39A3C -> 39B50 -> 41BF0` | Architecture shared |
| Enemy streams | Global table region `0x800B...` | Overlay/start region `0x80010000...` | Grammar/ordering shared; bytes endian/platform-specific |
| Type 1 descriptor | `0x22AD8`, file `0x89` | `0x22AD8`, file `0x92 MONK2` | Descriptor offset conserved, resource ID differs |
| Type 9 descriptor | `0x2C084`, file `0x25` | `0x2C084`, file `0x28 HULK` | Same caveat |
| Type A descriptor | `0x20FC8`, file `0x20` | `0x20FC8`, file `0x20 FAST` | Strong shared lineage |
| Text | `0x80073E74`, width `0x80074084` | `0x8004ACD4`, width `0x8004AEEC` | Similar service, different implementation |
| Save | Native cartridge save paths; N64 research fields differ | `0x900` memory-card image, `0x78` records, XOR checksum | Platform-specific |
| Output checksum | N64 header CRC1/CRC2 | PS1 file/disc layout and save checksum | Never reuse |

## Shared type-specific AI/control data

A particularly strong cross-port data match exists in the Test Scorpion/type-`0x12` synthetic-control system:

| Data | PS1 | N64 |
|---|---:|---:|
| per-type AI/control table | `0x80010FC8` | `0x800AF340` |
| type-`0x12` list | `0x800114E8` | `0x800AF860` |
| first type-`0x12` condition | `0x80011554` | `0x800AF8CC` |
| common sentinel | `0x80012B08` | `0x800B0E80` |

The descriptor bytes match after endian conversion. This is direct shared game-data lineage, not merely similar high-level behavior. It still does not make the PS1 and N64 evaluator code addresses interchangeable.

## Safe conclusions

- The `0x30` pickup grammar, 84-location boundary, item-ID family, ordinary-enemy stream concept, and several fighter descriptor offsets are common lineage.
- PS1 can use N64 discoveries as search signatures and semantic hypotheses.
- Each port still requires its own guarded patch sites, resource residency proof, runtime allocation plan, and validation.

## Unsafe conclusions

- An N64 virtual address cannot be transplanted to PS1.
- N64 stage-local resource slot numbers are not PS1 global file IDs.
- A matching descriptor offset does not prove identical surrounding binary data.
- Apparent space between PS1 overlay end and stack is not automatically free.
- N64 CRC logic, KSEG alias rules, and MIPS instruction patches do not define PS1 disc/save handling.

## First PS1 runtime sequence

The bounded order is: guarded selector activation, runtime overlay/memory observation, safe eight-stage mapping, one same-stage Fire enemy substitution, one stage pickup/resource mapping, then a port estimate. Jumping directly to a full randomizer would conflate platform and gameplay unknowns.
