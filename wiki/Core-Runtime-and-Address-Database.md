# Core runtime and address database

This page explains the production native foundation. For flat lookups use [Function registry](Function-Registry), [patch-site registry](Address-and-Patch-Site-Registry), and [runtime map](Runtime-and-Memory-Map).

## Clean target and invariants

Only the 16 MiB USA Rev. 0 big-endian ROM is supported: SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`. Every stock edit uses an expected-byte guard. A patch failure stops the build before output, and the clean input is never modified in place.

## Arena reservation

Two independent arena-start constructions must agree. At ROM `0x00066F64` and `0x00066FE8`, `addiu v0,v0,0xF420` (`0x2442F420`) becomes `addiu v0,v0,0xF820` (`0x2442F820`). The protected interval is `0x801AF420..0x801AF81F`; the game arena starts at `0x801AF820`.

The runtime code/state split is versioned, not generic free space. Production V2 uses code `0x801AF420..0x801AF71F` (0x300) and persistent state `0x801AF720..0x801AF81F` (0x100). V1's former 0x200/0x200 split is retained only as historical proof context. Inventory still owns payload `+0x1D4..+0x1FF`; XP progression owns the new payload extension `+0x200..+0x2FF`.

## Payload registration and bootstrap

| Component | ROM | VA/RDRAM | Limit |
|---|---:|---:|---:|
| Global file table | `0xA5010` | `0x800A4410` | 12-byte entries |
| MKMSZR file ID `0x1B` entry | `0xA5154` | — | guarded stock entry |
| Payload bytes | `0xF10000` | `0x801AF420` / uncached `0xA01AF420` | production V2 code `0x300` |
| Bootstrap hook | `0x66FE0` | `0x800663E0` | stage-load path |
| Bootstrap stub | `0x9AD84` | `0x8009A184` | capacity `0x19C` |
| Raw loader | — | `0x80065D64` | synchronous in proven path |
| Arena pointer global | — | `0x800EECD0` | synchronized by bootstrap |
| Arena sync helper | — | `0x80066390` | native routine |

The bootstrap loads file `0x1B`, synchronizes the arena pointer, and transfers to the payload through the uncached alias where required. Tests assert file-table contents, emitted MIPS words, hook/stub capacity, and arena consistency.

## Pickup persistence integration

Capture at VA `0x80039418` / ROM `0x3A018` preserves the displaced `sw v0,0x2C(a1)`, with `a1` as the record and `s2` as manager ordinal. Restore hooks the manager at VA `0x80038ACC` / ROM `0x396CC`, before the first collected-flag read, then resumes at `0x80038AD4`.

The manager context pointer is at effective address `0x802ECE20`; context `+0x6F4` is record count and `+0x6F8` is base. This corrects the superseded `0x802FCE20` reading.

## Cave ownership

| ROM/VA | Current production owner |
|---|---|
| `0x9AD84` / `0x8009A184` | Bootstrap stub and relocated selector mapper tail |
| `0x9A6C8` / `0x80099AC8` | Four-box switch/mask helper |
| `0x8F6E8` / `0x8008EAE8` | Four-box action routine |
| `0xAFA24..0xAFA97` / `0x800AEE24..` | Box-indicator wrapper and string |
| `0xAF9BE..0xAFA23`, `0xAFA98..0xAFABB` | Boot branding/license strings |
| payload `+0x1D4..+0x1FF` | Inventory filtered-save helper |
| payload `+0x200..+0x2FF` | XP progression callback, threshold table, restore helper |

Historical proof patches used some of these areas before production assigned them. Archive offsets are therefore not automatically safe in a current build.

## Preserved analysis project

The canonical N64 Ghidra program was reconstructed from the clean ROM rather than an old RDRAM dump. The archived project hash is SHA-256 `fbe071…`; it is provenance, not needed to use the address tables in this Wiki.
