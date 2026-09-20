# Contributor start here

## Repository and safety contract

The supported target is the USA Rev. 0 big-endian `.z64` ROM:

| Hash | Value |
|---|---|
| SHA-256 | `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6` |
| MD5 | `deec4faec416f4e02d934c2e42c0caad` |

ROM bytes are never committed. The patcher rejects an unsupported input, refuses an in-place output, refuses to overwrite an existing output, guards every stock patch site, updates N64 header CRC1/CRC2, writes the new file, and re-reads it for verification.

## Read order

1. Read [Project status](Project-Status) and [Architecture overview](Architecture-Overview).
2. Read the owning domain page for the change.
3. Use [Function registry](Function-Registry), [patch-site registry](Address-and-Patch-Site-Registry), and [data structures](Data-Structures-and-Encodings) for exact facts.
4. For stage data, use the relevant page under [Stage catalogs](Stage-Catalogs).
5. Consult historical artifacts only when a provenance trail or unresolved detail is needed; follow [Research workflow](Research-Workflow).

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
7. selector-only automatic-save bypass;
8. native box indicator;
9. boot branding and deterministic phrase;
10. company/logo bypass;
11. optional palette transform.

Do not reorder modules without checking their guards, cave ownership, and tests. The stage-selector mapper, persistence payload tail, legal-text area, and small executable caves have deliberate shared ownership.

## Evidence and promotion

A useful research result is not automatically production code. Promote it only when the address/structure is reproduced, stock bytes or bounds can be guarded, ownership and conflicts are known, failure behavior is bounded, and tests cover the new contract. Runtime testing should say exactly what was observed; do not generalize one pickup, enemy, stage, or seed into exhaustive coverage.

Never erase a material failed approach. Record why it failed and what later result superseded it. The most important current example is the corrected player-action address family: `0x8004B82C` and `0x8004CC14` are projectile helpers, while the player velocity helper is `0x8002B1EC`.
