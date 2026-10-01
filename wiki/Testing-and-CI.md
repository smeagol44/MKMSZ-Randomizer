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

## What CI proves

CI proves deterministic generation, guarded source expectations, emitted byte/code layouts, bounds, non-overlap assumptions represented in tests, and product composition. It does not execute the ROM or prove animation, collision, save-device, stage-transition, or full-playthrough behavior.

Game-state-dependent correctness therefore remains unresolved by CI alone. A reproducible runtime record identifies the exact ROM/configuration, stage/route, expected change, observed behavior, negative controls, and lifecycle boundary. A single positive location is representative evidence only.

## Wiki publication

Changes under `wiki/**` on `main` trigger a mirror job. It clones the `.wiki.git` repository, `rsync --delete`s this directory, commits only if changed, and pushes `master`. Broken internal links will still publish unless caught locally, so documentation validation includes a repository link scan in addition to code tests.


## Seeded Temple intro audio coverage

`tests/test_temple_intro_audio.py` pins the approved Audio-1 and Audio-2 pools, verifies the alternate Friendship take is excluded, exercises deterministic selection for representative seeds in both slots, checks that the shared pipeline omits the feature without donor-derived assets, and verifies that an Audio-1 selection preserves stock Audio-2 while an Audio-2 selection preserves the stock `0x41/0x42` alternation.

`tests/test_mkt_donor.py` also pins the approved donor-profile key set. Runtime claims remain separate from these tests: CI establishes deterministic extraction/composition and byte guards. The `0x20A` production carrier was then manually closed by v06 with seed `TEMPLE-PROD-CARRIER`, which selected Friendship in Audio 1 and produced the expected Friendship-then-stock-laugh sequence. That runtime result is bounded and does not individually validate all 11 donor clips.


## Enemy-randomization product wiring

CI covers the default-OFF shared configuration, conditional `EnemyRandomizationPatch` insertion, CLI `--enemy-randomization`, and browser checkbox -> Pyodide -> `RandomizerConfig.enemy_randomization` wiring. Browser and CLI therefore select the same planner/materializer path for a given seed. Runtime evidence remains separately bounded to the documented representative seeds/routes.
