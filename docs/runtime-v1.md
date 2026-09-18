# Runtime layout V1

The first persistent native MKMSZR state layout is now runtime-confirmed.

## Memory map

| Region | Cached range | KSEG1 alias | Size |
| --- | --- | --- | ---: |
| Reloadable code | `0x801AF420..0x801AF61F` | `0xA01AF420..0xA01AF61F` | `0x200` |
| Persistent state | `0x801AF620..0x801AF81F` | `0xA01AF620..0xA01AF81F` | `0x200` |

The file-ID `0x1B` payload is exactly `0x200` bytes, so subsequent native loads
replace only the code half and leave the state half untouched.

The V1 state header is:

| Offset | Meaning |
| ---: | --- |
| `+0x00` | magic `MKSV` / `0x4D4B5356` |
| `+0x04` | layout version `1` |
| `+0x08` | state-region size `0x200` |
| `+0x0C` | header size `0x20` |
| `+0x10` | flags |
| `+0x14..+0x1F` | reserved |
| `+0x20` | Fire pickup bitset in the current bounded proof |

Valid V1 state is preserved. Cleared, invalid, or incompatible state is zeroed
and initialized deterministically.

## Confirmed Fire persistence proof

The current promoted proof assigns Fire Temple's starting Potion to bit 0 at
`0x801AF640`.

- the native Potion callback pointer is redirected to the capture wrapper at
  `0xA01AF4C0`;
- the wrapper calls the original Potion callback, then sets Fire bit 0;
- the pickup-manager entry at ROM `0x000396CC` jumps through the permanent
  trampoline at `0x8009A1D8`;
- the restore wrapper at `0xA01AF520` validates V1, requires stage 5 and bit 0,
  restores the native collected flag at `0x802F14F4`, reproduces the two
  overwritten manager instructions, and resumes at `0x80038AD4`.

The decisive runtime test cold-booted the patched ROM, collected the Potion
normally, quit to title, reconstructed Fire, and re-entered. The V1 header and
bit survived; the native flag was restored before actor construction; the
Potion stayed absent; and another 600 frames ran normally.

The confirmed experiment output was:

- SHA-256:
  `5a9565bf16eecb4d3944eed0db7e60130b5efd96e8f879a1cb2ff02dd12da264`
- CRC1 / CRC2:
  `943F8EC7 / 6CA46758`

## Implementation boundary

This module is reusable implementation infrastructure, but it is **not enabled
by the normal CLI/browser pipeline yet**. The confirmed scope is one pickup in
one stage. The next research milestone is to generalize stable pickup identity
and capture/restore across all eight catalogued main stages before exposing
persistent pickup state as a normal randomizer feature.

The implementation entry point for reproducing the exact confirmed patch
sequence is `runtime_v1_fire_patches()`.
