# Contributor start here

## Supported target and patcher safety

The supported target is the USA Rev. 0 big-endian `.z64` ROM:

| Hash | Value |
|---|---|
| SHA-256 | `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6` |
| MD5 | `deec4faec416f4e02d934c2e42c0caad` |

The repository distributes patch code without ROM bytes. The patcher rejects an unsupported input, refuses an in-place output, refuses to overwrite an existing output, guards every stock patch site, updates N64 header CRC1/CRC2, writes the new file, and re-reads it for verification.

## Documentation map

| Information | Location |
|---|---|
| Current maturity, production/proof/pending state, and priorities | [Project status](Project-Status) |
| 1.0 product requirements, acceptance criteria, and release gates | [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) |
| Product layers and composition | [Architecture overview](Architecture-Overview) |
| Subsystem mechanisms and findings | Owning domain pages linked from [Home](Home) |
| Exact functions, patch sites, and structures | [Function registry](Function-Registry), [patch-site registry](Address-and-Patch-Site-Registry), [data structures](Data-Structures-and-Encodings) |
| Decoded stage data | [Stage catalogs](Stage-Catalogs) |
| Research methods and evidence provenance | [Research methodology](Research-Workflow), [artifact index](Library-Artifact-Index) |

## Requirements, proofs, and implementation scope

Current maturity and priority order are summarized in [Project status](Project-Status). Canonical 1.0 product requirements, acceptance criteria, and release gates are owned by [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap). Assistant behavior and task-selection rules live in Project Instructions.

Three distinct scopes appear throughout the documentation:

- a diagnostic shortcut used to isolate one mechanism;
- an implementation stepping stone;
- the actual requested 1.0 behavior.

A diagnostic result establishes its tested mechanism. It does not by itself establish final 1.0 behavior or compatibility with the production allocation. Static design, disposable proof, manual runtime observations, and production integration provide different kinds of evidence.

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
pytest
```

Developer CLI:

```bash
mkmszr clean-usa-rev0.z64 output.z64 --seed TEST153 --outfit seeded
```

`--outfit` supports `vanilla`, presets, `seeded`, `hue --hue DEGREES`, and `rgb --rgb RRGGBB`. If `--seed` is omitted, the CLI generates a random 64-bit hexadecimal seed.

## Patch-pipeline order

Order is a contract because later patches intentionally reuse or relocate earlier caves:

1. safe stage selector;
2. arena reservation;
3. native payload/bootstrap;
4. ordinary-pickup persistence;
5. seeded pickup randomization;
6. four-box inventory and lifecycle hooks;
7. pickup-driven XP progression and runtime V2 composition;
8. selector-only automatic-save bypass;
9. native box indicator;
10. boot branding and deterministic phrase;
11. company/logo bypass;
12. title branding (`TitleBrandingPatch`);
13. optional palette transform.

The stage-selector mapper, persistence payload tail, legal-text area, and small executable caves have deliberate shared ownership. Reordering modules can invalidate expected-byte guards or overwrite another owner's code; the pipeline tests cover the composed order.

## Evidence and compatibility limits

A useful research result is not automatically production code. Production compatibility depends on reproducible addresses/structures, guarded stock bytes or bounds, known ownership and conflicts, bounded failure behavior, and tests of the new contract. Runtime evidence is limited to the observed pickup, enemy, stage, seed, and route; it is not inherently exhaustive.

The [failure history](Experiments-Failures-and-Superseded-Findings) explains rejected approaches and their corrections. One important example is the corrected player-action address family: `0x8004B82C` and `0x8004CC14` are projectile helpers, while the player velocity helper is `0x8002B1EC`.
