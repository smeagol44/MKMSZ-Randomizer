# Runtime and memory map

## Stable global regions

| Range/address | Owner | Status and rule |
|---|---|---|
| `0x800A4410` | Global 12-byte file-table entries | Static-confirmed |
| `0x800A5FE4..0x800A600B` | Production key-to-stage table, reusing the obsolete default-inventory template | Implementation/CI-confirmed |
| `0x800A600C..0x800A6033` | Stock live inventory window, ten words | Runtime-confirmed |
| `0x800A6048..0x800A60E7` | Four authoritative ten-word boxes | Runtime-confirmed |
| `0x800A60E8` | Box state: active index bits `0..1`, latch bit `0x100` | Runtime-confirmed |
| `0x800A60EC` | `MKBX` magic `0x4D4B4258` | Implementation/CI-confirmed |
| `0x800A63FC` | Signed XP cap halfword table | Static-confirmed |
| `0x8009A910` | Current native stage word | Static/runtime-confirmed |
| `0x800C11E0` | Debug-menu selection index | Static/runtime-confirmed |
| `0x800BF2EE` | Remapping-aware normalized action input | Static/runtime-confirmed |
| `0x8011200C` | Current XP | Static/runtime-confirmed |

## Reserved MKMSZR runtime block

The game originally begins its main arena at `0x801AF420`. Production changes both construction sites at ROM `0x66F64` and `0x66FE8` from low immediate `0xF420` to `0xF820`, protecting exactly `0x400` bytes.

| Offset | Address | Size | Meaning |
|---:|---:|---:|---|
| `+0x000` | `0x801AF420` | `0x300` | Native runtime V2 code payload |
| `+0x300` | `0x801AF720` | `0x100` | `MKSV` V2 state block |
| end | `0x801AF820` | — | New arena start |

The superseded V1 split was `0x200` bytes of code at `0x801AF420..0x801AF61F` plus `0x200` bytes of state at `0x801AF620..0x801AF81F`. V2 retains the same total reservation; its code/state split is documented in [Core runtime](Core-Runtime-and-Address-Database).

Cached code addresses use `0x801A...`; the loader/bootstrap uses the uncached alias `0xA01AF420` where required. This entire interval belongs to the versioned production layout. A proof cave placed inside it would conflict with existing code or state unless those owners were explicitly relocated.

## Overlay and process context

Main stage overlays load at `0x802ECE30`; their functions and data are mutually exclusive across stages even when the same virtual address appears in different stages. The live process/context pointer used by pickup restoration is stored at effective address `0x802ECE20`. This address was previously misreported as `0x802FCE20` by treating the low immediate as unsigned. In MIPS address construction, `lui 0x802F` plus signed `0xCE20` equals `0x802ECE20`.

The pickup manager context exposes the ordinary-record count at `+0x6F4` and record base at `+0x6F8`. These offsets are implementation-critical and guarded through hook bytes, not a promise that the entire context structure is decoded.

## Arena-sensitive enemy imports

The original high-water endpoint is `0x80290990`. In the Fire cross-stage enemy proof, adding Temple fighter file `0x89` after stock allocations would exceed this by `0x3098`. Replacing Fire file `0x20` instead leaves about `0x1E0D0` bytes. This is proof-specific allocation math, not a general allocator guarantee.
