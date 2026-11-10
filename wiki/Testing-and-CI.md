# Testing and CI

## Local gate

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

The test workflow uses Python 3.11 for pushes to `main`, `refactor/**`, and `feature/**`, and for pull requests.

## Test ownership

| Test module | Contract |
|---|---|
| `test_rom.py` | Clean-ROM normalization/validation and guarded writes |
| `test_checksum.py` | N64 CRC1/CRC2 behavior |
| `test_stage_selector.py` | Menu range/table, mapper, hook, compact/native mapping |
| `test_arena.py` | Both reservation sites and protected range |
| `test_native_payload.py` | File entry, loader stub, hook, capacity |
| `test_pickup_persistence.py` / `test_manager_persistence.py` | State layout, hook code, stage/ordinal mapping |
| `test_pickup_randomization.py` | 84-record catalog, deterministic shuffle, access constraints, 250-seed sweep |
| `test_temple_special_check.py` | Scripted Temple-check allocation, guarded Herbs visual/reward seams, dedicated MKSV persistence flag, re-entry hook targets, and file-`0x1A` composition |
| `test_enemy_planner.py` | 104-record ordinary-enemy catalog, five fixed singleton exclusions, deterministic resource-family profiles, Water payload ceilings/shared-resource accounting, Prison phase paging/auxiliary dependencies, pending-family fail-closed rules |
| `test_fighter_compaction.py` | Accepted 64->16 PRIS body mapping, palette representatives, recovered compact file-size contracts |
| `test_enemy_materializer.py` | Deterministic supported-profile retry, guarded Water HULK/FAST/raw-PRIS17 and compact PRIS15/PRIS16/mixed loader transforms, Prison FAST phase loader + fixed capture anchor, singleton preservation, fail-before-write guards, unsupported-profile rejection |
| `test_global_items.py` | 84-item global logical pool, progression-token IDs, and retained source-location identity |
| `test_resource_materialization.py` | Canonical visual-donor coverage, type-4 encode/decode, deterministic extension selectors/deduplication, and fail-closed stage-bound token handling |
| `test_inventory_boxes.py` | Four boxes, masking, input chord, cave relocation, lifecycle routines |
| `test_flow_bypass.py` | Exact logo branch and selector-only save bypass |
| `test_presentation.py` | Box wrapper/text and boot branding interaction |
| `test_title_branding.py` | Edition-name constraints, embedded art/font rendering, LZW round-trip, and bounded data-only title relocation |
| `test_palette.py` | BGR555 conversion, bounds, deterministic static modes |
| `test_rainbow_palette.py` | Runtime V2 rainbow layout, proof-exact helper/hook bytes, XP-tail composition, and high-ROM bounds |
| `test_xp_progression.py` | Native thresholds/state separation, deterministic nine-reward selection, RNG isolation, Runtime V2 extension bounds, safe stage restore, and guarded XP patch output |
| `test_pipeline.py` | Patch order, default-OFF enemy randomization option, and composed output behavior |
| `test_seed.py` | Seed generation and domain determinism |
| `test_runtime_v1.py` | Historical/compatibility Runtime V1 layout, reference payload, and Fire persistence pipeline contract |
| `test_runtime_v2.py` | Current Runtime V2 0x3B0-code/0x50-state repartition and versioned state-header contract |
| `test_fighter_swap.py` | Fighter option: config/CLI/pipeline guards, classification-table invariants. **ROM-backed**: the Sektor build hash and the CLI reproduction of composition v13 (SHA-256 `e1f83b25…`) |
| `test_mkt_select_screen.py` / `test_web_fighter_swap.py` | Select-screen decoders (PackBits, RGBA5551) and the web wiring of the "Swap character" window. **ROM-backed** (`MKMSZR_MKT_ROM`): grid layout, only Sektor selectable and in colour, render digests |
| `test_fighter_import.py` | Fighter-importer Step 0: script grammar decode/assemble round trip, label relocation, dialect differences, translation rules. **ROM-backed** (skipped unless `MKMSZR_CLEAN_ROM` / `MKMSZR_MKT_ROM` name the supported clean ROMs): stock file-`0x87` byte-identical re-encode, Sektor donor tables and special commands, and donor Run → the Runtime-confirmed v05 live Run script |
| `test_fighter_import_actions.py` | Importer action library (no ROM needed): MIPS assembler encodings, branch/label and segment rules, `%hi/%lo`, jump-calibrated motion, and the teleport action assembling to the Runtime-confirmed Sektor proof v18 payload (pinned SHA-256) |

## What CI proves

CI proves deterministic generation, guarded source expectations, emitted byte/code layouts, bounds, non-overlap assumptions represented in tests, and product composition. It does not execute the ROM or prove animation, collision, save-device, stage-transition, or full-playthrough behavior.

Game-state-dependent correctness therefore remains unresolved by CI alone. A reproducible runtime record identifies the exact ROM/configuration, stage/route, expected change, observed behavior, negative controls, and lifecycle boundary. A single positive location is representative evidence only.

## Lint version pin (2026-11-06)

**Implementation/CI-confirmed.** CI installed an unbounded `ruff>=0.6`; a newer ruff enabled `EXE001` and `RUF007` by default and `ruff check .` failed on every PR, including docs-only ones. PR #177 marked the two `tools/inventory_audio_*.py` scripts executable, replaced `zip(rows, rows[1:])` with the equivalent `itertools.pairwise(rows)`, and pinned `ruff==0.16.9`. Bump the pin deliberately.

## Real-ROM static composition audit (2026-11-06)

**Static / Implementation-confirmed for the listed builds only; no emulator run.** Inputs: clean USA Rev. 0 (SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`) and MKT Rev. 2 donor (SHA-256 `30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb`), patch code at `main` `f790981`.

- Seven full `patch_rom` configurations built successfully (32 MiB, header unchanged, CRC1/CRC2 valid), covering pickups ON/OFF, vanilla/rainbow/seeded/rgb/red outfits, donor present/absent, enemy randomization, power-order shuffle, debug keys, all Required powers modes, both completion modes, and all GAME SETTINGS bits. A repeated build was byte-identical.
- Per-patch write-overlap audit: only intended overlaps, such as successive owners extending the shared file-`0x1A` end word at ROM `0xA514C`, and the guarded Toasty call trampoline at ROM `0xAFA8C` inside the box-indicator region.
- Hook checks: four-box action hook `0x80015B4C` (stock redefines `v0`/`v1` immediately; no live `a0`/`a1`/temporaries); box-indicator wrapper (displaced callee `0x8001EAE4` takes no stack arguments, following call `0x8002018C` takes no arguments); lifecycle v06 replays (see [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle)).

Gap: no automated test runs the full `patch_rom` composition, because CI has no ROM. A ROM-gated matrix test (skipped unless a ROM path is supplied) remains a candidate; `test_fighter_import.py` (2026-11-07) establishes the `MKMSZR_CLEAN_ROM` / `MKMSZR_MKT_ROM` environment-variable convention for such tests.

## Wiki publication

Changes under `wiki/**` on `main` trigger a mirror job. It clones the `.wiki.git` repository, `rsync --delete`s this directory, commits only if changed, and pushes `master`. Broken internal links will still publish unless caught locally, so documentation validation includes a repository link scan in addition to code tests.


## Seeded Temple intro audio coverage

`tests/test_temple_intro_audio.py` pins the approved Audio-1 and Audio-2 pools, verifies the alternate Friendship take is excluded, exercises deterministic selection for representative seeds in both slots, checks that the shared pipeline omits the feature without donor-derived assets, and verifies that an Audio-1 selection preserves stock Audio-2 while an Audio-2 selection preserves the stock `0x41/0x42` alternation.

`tests/test_mkt_donor.py` also pins the approved donor-profile key set. Runtime claims remain separate from these tests: CI establishes deterministic extraction/composition and byte guards. The `0x20A` production carrier was then manually closed by v06 with seed `TEMPLE-PROD-CARRIER`, which selected Friendship in Audio 1 and produced the expected Friendship-then-stock-laugh sequence. That runtime result is bounded and does not individually validate all 11 donor clips.


## Enemy-randomization product wiring

CI covers the default-OFF shared configuration, conditional `EnemyRandomizationPatch` insertion, CLI `--enemy-randomization`, and browser checkbox -> Pyodide -> `RandomizerConfig.enemy_randomization` wiring. Browser and CLI therefore select the same planner/materializer path for a given seed. Runtime evidence remains separately bounded to the documented representative seeds/routes.
