# Frontend and save-flow bypasses

Production contains two narrowly scoped flow changes. Both are runtime-confirmed and guarded.

## Post-legal logo bypass

Owning frontend routine `0x80079510` performs:

1. first fixed splash via `0x8007C44C` using resources `0x3B4/0x3B5`;
2. second fixed splash via `0x8007C50C` using `0x3B2/0x3B3`;
3. fade/normalization `0x800615D8(0x80)`;
4. title handoff through `0x80078C40`.

At VA `0x800797F4` / ROM `0x7A3F4`, the guarded sequence is:

```text
0C01F113 00000000 0C01F143 00000000 0C018576 24040080
```

Production changes only the first word to `0x10000003`, an unconditional branch over both splash calls. The legal/MKMSZR branding screen remains visible, and fade normalization/title initialization execute unchanged.

## Selector auto-save bypass

The compact mapper writes a nonzero byte to `0x80291C0C` only when returning a selector choice. Stock stage-entry code recognizes this as a one-shot skip. The generic auto-save function `0x800798A8` is not replaced, so later/manual/post-stage save flows are preserved.

## Rejected broad approaches

- Removing the owning frontend routine would also skip required normalization/title state.
- Patching generic save code would suppress unrelated saves and expand lifecycle risk.
- A global “never save on entry” flag is unnecessary; the game already owns a scoped byte.

The accepted implementation therefore modifies only one guarded boot branch and the existing selector mapper.
