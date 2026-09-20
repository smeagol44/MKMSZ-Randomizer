> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Native UI and Presentation

## Gameplay HUD

Runtime-confirmed chain:

`FUN_8005BFB0 -> FUN_8001EAE4`

MKMSZR can preserve the stock HUD and append native nodes.

Confirmed:

- one custom rectangle;
- multiple custom rectangles in one frame;
- rendering from file-ID `0x1B` loaded code;
- arbitrary custom gameplay ASCII text.

## Native text

- renderer: `FUN_80073E74`
- width routine: `FUN_80074084`
- typical font descriptor: `0x800B1E20`

Runtime proofs include `PAUSED`, `MKMSZR UI TEST`, and `TOASTY!`.

## Production box indicator

Current production text:

`BOX n OF 4`

The old `BOX n / 4` idea is obsolete because plain `/` produced an unexpected custom-font glyph.

## Boot/legal branding

The legal screen remains and is reused for MKMSZR branding.

Production content includes title/subtitle, `RANDOMIZER`, Midway attribution, a deterministic two-line seed message, `BY SMEAG`, and `LICENSED BY NINTENDO`.

Native font codes:

- `^` -> ®
- `[` -> ™
- `~` -> ©
- plain `/` does not produce a normal slash

The boot phrase RNG domain is:

`MKMSZR:BOOT-PHRASE:V1`

### Punctuation runtime result

Seed `TEST153` selects:

`' OR 1==1 --`

Manual testing confirmed that this message rendered correctly at boot. This materially improves confidence in apostrophe, equals-sign and hyphen usage in the phrase pool.

## Post-legal logo bypass

ROM `0x0007A3F4` is changed from `jal 0x8007C44C` to an unconditional branch to `0x80079804`, skipping both fixed company/logo presentations while preserving the legal screen, fade normalization and title initialization.

Cold boot is runtime-confirmed.

## Unresolved

Recognizable custom textured-image rendering remains unsolved. Solid geometry and native text are the supported production UI path.
