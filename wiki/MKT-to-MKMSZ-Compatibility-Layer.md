# MKT compatibility overview

> **Scope:** This page owns the accepted **MKT -> MKMSZ porting strategy and current compatibility contract**. It is the architectural entry point, not a proof diary.
>
> Donor semantic translation belongs to [MKT adapter primitives](MKT-Adapter-Primitives). Fighter image/codec/palette/storage translation belongs to [MKT fighter asset translation](MKT-Fighter-Asset-Translation). The MKMSZ host action ABI belongs to [Player actions and special moves](Player-Actions-and-Special-Moves). Sektor slot mapping/current coverage belongs to [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping), while the canonical vNN chronology belongs to [Sektor takeover proof history](Sektor-Takeover-Proof-History).

## Current conclusion

The accepted direction is a **faithful source-level port through an MKMSZ compatibility adapter**.

The goal is not to imitate an MKT move with vaguely similar MKMSZ parts, and it is not to relocate MKT retail instructions directly. Preserve donor control flow and donor data wherever practical, then translate only the engine-facing interfaces that are not binary-compatible.

That means preserving, where established:

- donor phase ordering and loop counts;
- donor movement intent/constants;
- donor animation scripts and frame resources;
- donor strike geometry, damage, block behavior, and reaction meaning;
- donor no-repel behavior;
- donor hit/block/timeout/recovery branches;
- donor combo graph structure where the record grammar is proven compatible.

Translate:

- MKT PROCESS/OBJECT field accesses to MKMSZ controller/actor layouts;
- MKT scheduler/action entry and exit to the proven MKMSZ action lifecycle;
- MKT helper calls to semantically equivalent MKMSZ helpers;
- donor strike/reaction selectors to MKMSZ-native semantics;
- donor animation callbacks/control tokens when they are engine-local;
- donor fighter image formats/palettes/storage into target-consumable MKMSZ assets.

Direct relocation of donor retail instructions remains rejected as the general strategy. The games differ in process/object layouts, globals, scheduler ABI, strike/reaction tables, heap/resource bases, callback semantics, and texture codecs; a safe binary rewrite would require the same semantic knowledge as a source-level adapter while being more fragile.

## Evidence boundary

The primary N64 donor/target pair is:

| Role | Image | Identity |
|---|---|---|
| Donor | MKT USA Rev. 2 N64 | `0xC00000` bytes; SHA-256 `30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb` |
| Target | MKMSZ USA Rev. 0 N64 | SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6` |

The public MKT source tree is a symbolic guide. Exact donor addresses/tables are retail-binary findings unless a page explicitly labels them otherwise.

Supplemental PS1 MKT and preserved Midway source assets are donor/reference evidence only. Their addresses, storage formats, and runtime behavior do not transfer to MKMSZ N64 without demonstrated translation.

Runtime-confirmed proofs establish only their documented routes. They demonstrate compatibility patterns; they do not imply arbitrary MKT moves or fighter data are already portable.

## What transfers conceptually

Current evidence supports these **conceptual** transfers:

| Donor concept | Current compatibility conclusion | Canonical detail |
|---|---|---|
| Action phase ordering, bounded sleeps, movement/contact/recovery phases | Transfer as semantic control flow | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Movement intent: move, stop, face opponent | Target-native primitives exist; donor constants still need target calibration | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Animation selection and frame progression | Target-native primitives exist | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Fighter frame/shape structure | Conceptually compatible after pointer-base and dimension translation | [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| Donor indexed pixels/palettes | Transfer after deterministic decode/format and palette translation | [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| Normal-combo record structure | Compatible at the tested Sektor v62 scope | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Strike geometry/damage/reaction **meaning** | Transfer semantically, not by raw numeric IDs | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Three-tick no-repel behavior | Donor semantic is Static-confirmed; target shim is Pending | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Projectile actor/process split | Target-native resource-actor creation, facing-aware placement, and child-process binding are Static-confirmed; generic adapter wrappers remain Pending | [MKT adapter primitives](MKT-Adapter-Primitives), [Player actions and special moves](Player-Actions-and-Special-Moves) |

## What requires translation

The following are **not** assumed byte- or number-compatible:

- PROCESS/OBJECT/controller/actor field offsets;
- scheduler/action entry, callback lifetime, and cleanup;
- action locks and interruption rules;
- raw movement constants until target units/facing behavior are validated;
- strike-table indices;
- victim-reaction selectors;
- animation callback/control tokens;
- donor heap-relative pointers and resource bases;
- MKT N64 codecs 16/22/24/15;
- donor palette representation/binding;
- proof allocations or file-size envelopes.

A core rule from both Reverse Elbow and Sektor combo work is:

> **Numeric equality is not semantic compatibility.**

Donor table indices and selectors must be identified by meaning and mapped to MKMSZ-native semantics. The v61 -> v62 Sektor combo correction is the clearest Runtime-confirmed example: preserving the donor combo graph while translating only the incompatible reaction selector fixed the tested corruption without recreating the move.

## Current compatibility boundaries

### Established

- **Source-level adapter direction:** accepted architecture.
- **MKMSZ action lifecycle primitives:** sufficient for a stable bounded host-side proof path; exact ABI remains in [Player actions and special moves](Player-Actions-and-Special-Moves).
- **Movement / stop / face / animation selection / animation advance:** target primitives identified.
- **Fighter asset translation:** donor descriptors/pixels/palettes can be converted into MKMSZ-native target assets for proven formats; generated Type-5 is the accepted target storage direction.
- **Normal-combo grammar:** transferable at the bounded Sektor v62 scope when game-local reaction semantics are translated.
- **Projectile host primitives:** resource-backed secondary-actor creation, facing-aware relative placement, child projectile-process binding, and the generic projectile collision/strike path are statically identified. v69 Runtime-confirms the resolved player-animation cursor path; v70 Runtime-confirms a genuine donor rocket frame can reach the live projectile.
- **Rejected-path lessons:** forced crossover, raw selector reuse, blind callback-token reuse, unsafe callback returns, and direct donor codec consumption all remain reusable architectural constraints.

### Translation-required or incomplete

- generic donor action-phase runner;
- generic donor movement-unit conversion policy;
- generic three-tick no-repel shim in MKMSZ;
- general donor strike/reaction semantic map;
- generic donor animation-control-token translator;
- generic projectile actor/process wrapper and donor projectile callback/state/effect translation;
- arbitrary donor special-move command/action integration;
- production-safe allocation/composition for imported fighters or moves.

### Not implied by current proofs

Current work does **not** establish:

- binary compatibility between MKT and MKMSZ executables;
- a universal MKT PROCESS/OBJECT ABI;
- direct donor-code relocation;
- arbitrary strike/reaction selector reuse;
- arbitrary donor animation-script token reuse;
- arbitrary MKT fighter-resource import without format translation;
- production readiness of Sektor takeover or donor special moves;
- a general PS1 -> N64 binary compatibility layer.

## Architecture boundaries and canonical owners

The compatibility work is intentionally split by information type:

- [MKT adapter primitives](MKT-Adapter-Primitives) owns donor -> MKMSZ semantic translation: scheduler/yield/control transfer, movement, animation operations, strike/reaction translation, no-repel, combo semantics, cleanup, coverage, and missing generic shims.
- [MKT fighter asset translation](MKT-Fighter-Asset-Translation) owns donor fighter descriptors, dimensions/anchors, codecs, palettes, MKMSZ Type-5 generation, storage/packing, and asset compatibility limits.
- [Player actions and special moves](Player-Actions-and-Special-Moves) owns the **host-side MKMSZ action ABI**, helper meanings, scheduler bridge, callback lifetime, action lock, cleanup, and Reverse Elbow host proof history.
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) owns the slot mapping, mapping policy, current coverage, and current gaps.
- [Sektor takeover proof history](Sektor-Takeover-Proof-History) owns the vNN proof/build chronology, final evidence statuses, artifact identities, routes, supersession, and proof-specific allocation conflicts.
- [Toasty audio research](Toasty-Audio-Research) owns Toasty donor-audio identity, rejected candidates, and audio proof chronology.
- [Toasty visual research](Toasty-Visual-Research) owns Toasty visual diagnostics and image/render proof chronology.
- [Audio system](Sounds-and-Music) owns generic MKMSZ host audio mechanics.
- [Function registry](Function-Registry) owns canonical target function semantics.

## Sektor proof-history boundary

[Sektor takeover proof history](Sektor-Takeover-Proof-History) is now the canonical version chronology. This overview keeps only the accepted cross-game strategy and compatibility contract.

[Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) retains the four slot tables, mapping policy, current coverage, and current gaps. [MKT fighter asset translation](MKT-Fighter-Asset-Translation) retains stable codec/palette/Type-5/storage conclusions and bounded packing evidence, but defers exact vNN identities/routes/status reconciliation to Proof History.

## Reusable rejected/superseded lessons

The architectural lessons are preserved here without keeping a second proof diary:

- behavioral recreation was a useful early experiment but is **not** the accepted final porting direction;
- forced-X crossover is not MKT pass-through; donor behavior uses normal movement plus temporary repulsion suppression;
- MKT strike/reaction numbers are game-local table semantics;
- donor animation callbacks/control words are not automatically MKMSZ-compatible;
- returning normally from an installed MKMSZ special-action callback can self-reenter;
- projectile setup is not the player-propulsion primitive;
- omitting native action lifecycle state can destabilize the action;
- imported fighter bytes must be translated into the target asset representation rather than copied as donor codecs.
- v70's hardcoded Ice-path spawn/acceleration tuning is superseded as the implementation strategy; donor projectile choreography should run through generic target actor/process primitives instead.

Detailed Reverse Elbow failures remain on [Player actions and special moves](Player-Actions-and-Special-Moves). Detailed donor semantic consequences are on [MKT adapter primitives](MKT-Adapter-Primitives). Sektor vNN failure/supersession chronology is canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).

## Current research direction

The compatibility layer should become more generic by filling semantic gaps, **not** by hardcoding additional donor choreography.

Useful next adapter research, after current project priorities permit it, is:

- a minimal generic projectile adapter over the now-identified MKMSZ resource-actor, relative-placement, and child-process primitives, validated first with Sektor `do_robo_zap -> rocket1_proc`;
- donor projectile callback/state/effect/palette translation without inheriting Ice presentation;
- a reusable donor phase/action runner over the proven MKMSZ lifecycle;
- a narrow MKMSZ no-repel hook implementing the donor three-tick semantics;
- one exact victim-reaction translation that preserves target interruption/cleanup;
- semantic expansion of normal-combo translation beyond the currently proven selectors;
- explicit translation of donor animation control tokens when needed.

These are proof/research goals, not current 1.0 product blockers.

## Related pages

- [MKT adapter primitives](MKT-Adapter-Primitives)
- [MKT fighter asset translation](MKT-Fighter-Asset-Translation)
- [Player actions and special moves](Player-Actions-and-Special-Moves)
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping)
- [Sektor takeover proof history](Sektor-Takeover-Proof-History)
- [Toasty audio research](Toasty-Audio-Research)
- [Toasty visual research](Toasty-Visual-Research)
- [Audio system](Sounds-and-Music)
- [Function registry](Function-Registry)
- [N64-PS1 comparison](N64-PS1-Comparison)
