> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# PS1 Research

## Status

PS1 work currently has a strong **static** baseline. Unless explicitly stated otherwise, PS1 findings are not runtime-confirmed.

Target executable: `SLUS_004.76`

- payload load: `0x80010000`
- entry point: `0x80090E70`
- declared payload end: `0x800D8000`
- initial stack: `0x801FFFF0`
- startup clear end / strongly supported overlay base: `0x80130FF8`

The large interval above the largest overlay is not certified free memory.

## Surviving stage selector

| Component | Address |
|---|---:|
| selector | `0x8002A688` |
| `SELECT LEVEL` | `0x800136F4` |
| 11-entry labels | `0x800AC40C` |
| selected index | `0x800D8150` |
| confirm handler | `0x80031E98` |
| normal title START call | `0x8002A9E0` |

The label order matches N64. Activation is runtime-untested.

## Porting implications

The PS1 and N64 versions share substantial source/data lineage, but addresses, overlay layout, resources, native patches, CRC behavior and free-memory conclusions are platform-specific.

## If PS1 work resumes

1. guarded selector activation;
2. runtime overlay/memory validation;
3. safe eight-stage mapping;
4. one-stage pickup/resource map;
5. only then estimate full randomizer port effort.
