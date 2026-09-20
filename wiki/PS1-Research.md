# PlayStation research

Unless stated otherwise, PS1 results are **static-confirmed**, not runtime-confirmed. Target executable: `SLUS_004.76`.

## Executable and memory layout

| Property | Value |
|---|---:|
| Payload load | `0x80010000` |
| Entry point | `0x80090E70` |
| Declared payload end | `0x800D8000` |
| Initial stack | `0x801FFFF0` |
| Startup clear end / supported overlay base | `0x80130FF8` |

The large apparent interval below the stack is not certified free memory. A PS1 port needs runtime allocation/overlay validation before reserving anything.

## Resource directory

The executable has a 207-entry directory: location table `0x80012F28`, size table `0x80013264`. IDs `0x00..0x1B` are 28 movie references with size zero in this directory; IDs `0x1C..0xCE` are 179 files whose declared sizes match the extracted resources.

| ID | File | Size |
|---:|---|---:|
| `0x20` | `FAST.BIN` | 135,508 |
| `0x28` | `HULK.BIN` | 180,748 |
| `0x90` | `MKSZ.BIN` | 235,144 |
| `0x92` | `MONK2.BIN` | 142,308 |
| `0x9C` | `QUANCHI.BIN` | 323,092 |
| `0x9E` | `SCORPION.BIN` | 260,872 |
| `0x9F` | `SHINNOK.BIN` | 190,192 |
| `0xA1` | `WATERGOD.BIN` | 221,112 |
| `0xA2` | `WINDGOD.BIN` | 218,756 |

## Stage selector

| Component | Address |
|---|---:|
| Selector | `0x8002A688` |
| `SELECT LEVEL` string | `0x800136F4` |
| 11 label pointers | `0x800AC40C` |
| Selected index | `0x800D8150` |
| Confirm handler | `0x80031E98` |
| Normal title START call | `0x8002A9E0` |

The label order matches N64. Activation and a safe eight-stage mapping remain runtime-untested.

## Pickups and inventory

PS1 pickup manager `0x8005499C` uses the same `0x30`-byte record architecture and the same 84 ordinary-location boundary. The stage-local resource-table root is `0x800D82F4`.

| Callback | Meaning |
|---:|---|
| `0x800547CC` | Potion |
| `0x800547FC` | Shield |
| `0x8005482C` | Eye |
| `0x8005485C` | Formula |
| `0x8005488C` | Herbs |
| `0x800548BC` | Health urn |
| `0x800548EC` | Extra-life family |
| `0x80054960` | Strength urn |
| around `0x800545A4/0x80054654` | Generic key/special paths |

The ten-word inventory is at `0x800ACE28`; insertion is `0x8004C0B0`. IDs `0x00..0x24` correspond closely to N64; `0x25` Power Upgrade is not a stock item.

## Enemy streams and resources

PS1 flow is `0x8003955C -> 0x80039A3C -> 0x80039B50 -> 0x80041BF0`; current stream pointer `0x800D7E80`; opcode table `0x80013940`.

| Stage/branch | Stream |
|---|---:|
| Temple | `0x80010000` |
| Earth | `0x80010178` |
| Water | `0x8001025C` |
| Wind | `0x800103A4` |
| Fortress ordinary | `0x80010684` |
| Prison | `0x800108F8` |
| Fire ordinary | `0x80010B6C` |
| Fire special | `0x80010D30` |
| Bridge | `0x80010D58` |
| Fortress special | `0x80010F64` |

The key fighter descriptor offsets match N64: type 1 `0x22AD8`, type 9 `0x2C084`, type A `0x20FC8`. PS1 slots/files are type 1 slot `0x800D7F98` -> file `0x92 MONK2`; type 9 slot `0x800D8200` -> `0x28 HULK`; type A slot `0x800D81EC` -> `0x20 FAST`.

A smallest future proof would change the first normal-Fire type at VA `0x80010B84` / extracted-file offset `0x1384` from `0A00` to `0900`, with a clean guarded build and runtime test.

## Save format

Memory-card file: `BASLUS-00476SUBZERO`, image size `0x900`. Checksum routine `0x80090B94` zeros the checksum field, adds `0x258`, then XORs `0x240` words; initialization is `0x80090BCC`.

Each save record is `0x78` bytes:

| Offset | Meaning |
|---:|---|
| `+0x04` | Stage (`0x800D76A8`) |
| `+0x08` | Starting lives |
| `+0x0C` | XP (`0x800D7DC4`) |
| `+0x10..+0x37` | Ten inventory words |
| `+0x38..+0x57` | Eight progression values |
| `+0x70` | Lives (`0x800D7D48`) |
| `+0x74` | Continues (`0x800E8184`) |

Current HP is in the player structure at `+0x354`, not in the stable global save fields.

## UI and test-character findings

Text renderer `0x8004ACD4`, glyph renderer `0x8004A920`, width `0x8004AEEC`. Candidate UI function `0x80049530` is only partially mapped and is not certified as an always-on HUD hook.

The Test Characters table is `0x800AC43C`, 25 records of `0x1C`; names start `0x800AC6F8`; selection is `0x800D7E48`. Index 13 `SCORPION` is type `0x12` and uses `MKSZ.BIN`, indicating an AI/test system rather than a live player. Index 14 `UNDEAD SCORP` is type `0x11` and uses genuine `SCORPION.BIN`, making it the stronger resource candidate. Fields `+0x14/+0x18` are audio setup, not move-command pointers. No player-reachable spear or teleport has been confirmed.

See [N64–PS1 comparison](N64-PS1-Comparison) for safe transfer rules.
