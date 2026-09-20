> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Stage Flow and Selector

## Supported stage mapping

| Compact index | Native ID | Stage |
|---:|---:|---|
| 0 | 0 | Temple |
| 1 | 1 | Wind |
| 2 | 2 | Water |
| 3 | 3 | Earth |
| 4 | 4 | Prison |
| 5 | 5 | Fire |
| 6 | 8 | Bridge |
| 7 | 9 | Fortress |

Native IDs 6/7 are unsafe/non-main entries, so compact 6/7 map to 8/9.

## Selector state

- stock selector contains 11 entries;
- selected index: `0x800C11E0`;
- native stage value: `0x8009A910`;
- title-menu A-route is confirmed;
- experimental controller-Start interception remains intermittent.

## Production mapper + automatic-save bypass

Production mapper:

- RAM `0x8009A2FC`
- ROM `0x0009AEFC`
- 0x20 bytes

Previous mapper:

```text
3C03800C
8C6311E0
2C610006
14200002
00000000
24630002
03E00008
00000000
```

Current mapper:

```text
3C03800C
8C6311E0
2C610006
50200001
24630002
3C028029
03E00008
A0441C0C
```

It preserves compact mapping and stores a nonzero byte at:

`0x80291C0C`

Main-stage entry callbacks already use that byte as a one-shot automatic-save bypass. The generic save entry `FUN_800798A8` is left untouched.

Runtime-confirmed route:

`Safe Stage Select -> Temple -> no entry save -> normal Temple -> completion -> normal later save prompt`

This is not a global save-disable patch. Validation is bounded to the tested route.

## Boot logo bypass

The legal/branding screen stays intact. At ROM `0x0007A3F4` / RAM `0x800797F4`:

```text
original:    0C01F113   jal 0x8007C44C
replacement: 10000003   beq zero,zero,0x80079804
```

Guarded surrounding sequence:

```text
0C01F113 00000000
0C01F143 00000000
0C018576 24040080
```

This skips the two synchronous post-legal splash calls while preserving `FUN_800615D8(0x80)` fade normalization and continuation to the normal title/menu controller `FUN_80078C40`.

Cold-boot legal -> title is runtime-confirmed.
