# Lifecycle Pause-Quit proof v03

This proof supersedes lifecycle v02 for the user-reported **Pause -> Quit -> YES** route.

## Runtime result that motivated v03

v02 was partially successful: four-box inventory remained persistent, but XP/powers, HP, and lives reset after quitting to title and entering a stage. Continues were not tested. This establishes that the inventory lifecycle was still healthy and isolates the new lifecycle proof as the owner of the regression.

## Static correction

- Native Pause callback: `0x80016300`.
- QUIT confirmation path: `s3=1`, YES is selection `s0=0`.
- Exact pre-teardown call: VA `0x800166CC` / ROM `0x000172CC`, stock `jal 0x80028488`; the delay slot at `0x000172D0` supplies `a1=0`.
- v02's stage-entry wrapper at ROM `0x0007B94C` was the wrong place to *save* HP/lives/continues because title/stage startup can already have reset those live values.
- v02 also replaced the already Runtime-confirmed progression restore call at ROM `0x00F101BC`; v03 restores that production call verbatim.

## v03 composition

The proof uses the already-loaded file-`0x1A` gap ROM `[0x00F69150,0x00F697E0)` / runtime `[0x801B0970,0x801B1000)`.

Only two helpers are emitted:

1. **QUIT save helper** at runtime `0x801B0970`: saves exact live lives `0x8010BCFC`, continues `0x801AE45C`, XP `0x8011200C`, and player HP `controller+0x654` into proof-only MKSV words, seeds native HP carrier `0x801AE4C0` / validity `0x800C11F8`, then calls the displaced stock teardown `0x80028488`.
2. **Post-inventory restore helper** at runtime `0x801B0A20`: production progression restore writes persistent XP exactly as before, then calls this helper instead of directly calling the production inventory load/mask wrapper. The helper calls that exact wrapper first (`0xA00A9B14`), then restores lives/continues and re-seeds the native HP carrier.

v03 deliberately does **not** own death, Continue spending, stage-completion save, or Game Over reset. Those remain separate gates.

Artifact: `MKMSZR_lifecycle_pause-quit_proof_v03.z64`
SHA-256: `6b82c6782c23cd526b36a8df8166269474af6a34ab7c33d7e9a527e3778f66fb`
CRC1/CRC2: `120311ED / 933CE9BF`

Evidence: **Implementation/static-confirmed; Runtime Pending.**
