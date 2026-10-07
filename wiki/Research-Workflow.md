# Research methodology and evidence

This page describes MKMSZR's research methods, evidence records, and technical validation limits. Its existing URL is retained for links. Assistant operating rules are maintained separately in Project Instructions.

## Sources and provenance

| Source | Role |
|---|---|
| Repository implementation and tests | What the product currently implements and checks |
| Versioned `wiki/` and published Wiki | Current technical knowledge, requirements, status, registries, and decoded catalogs |
| `MKMSZR Research` archive | Original evidence, preserved Ghidra work, captures, experiments, and historical interpretations |
| [`MKMSZ-Ghidra`](https://github.com/smeagol44/MKMSZ-Ghidra) | Living, reproducible Ghidra-facing analysis metadata: function/global names, comments, scripts, and later shared types/labels |
| Bounded static or runtime investigation | Evidence for an unresolved question |

The archive is a provenance trail rather than a second current manual. An older report can contain a superseded interpretation; the owning Wiki topic records the current conclusion and the history needed to explain it.

## Living Ghidra analysis workspace

The preserved Ghidra project in `MKMSZR Research` remains exact historical/static-analysis provenance. Active analysis is additionally mirrored through the public [`MKMSZ-Ghidra`](https://github.com/smeagol44/MKMSZ-Ghidra) repository so the same partially-understood program can be inspected and progressively named by multiple researchers without distributing ROM bytes.

The shared repository currently targets the clean **MKMSZ USA Rev. 0** N64 image and stores reviewable text metadata plus Ghidra scripts rather than treating an opaque local Ghidra database as the sole source of analysis state. A researcher imports their own clean ROM with the established N64 loader, runs normal analysis, and applies the shared metadata locally. Unknown functions deliberately remain available as unknown functions; the repository is an evolving analysis workspace, not a claim that the binary is fully decompiled.

When a static investigation establishes a durable function/global identity, signature, type, label, or comment, update the appropriate canonical Wiki/registry and the Ghidra-facing metadata in the same task when practical. Stage-overlay symbols must retain explicit stage/overlay scope rather than being flattened into one global address namespace.

## Types of investigation

- **Static analysis** establishes code, data, address, and control-flow relationships without executing the game.
- **Implementation checks** establish guarded output, allocation bounds, deterministic generation, and patch composition represented in code/tests.
- **Runtime validation** observes behavior on a defined ROM, configuration, route, and game state.

These answer different questions. A diagnostic shortcut can isolate one mechanism without satisfying the product requirements in [Project status](Project-Status). An implementation stepping stone and the requested final behavior can therefore have different scopes.

## Bounded experiment model

A bounded experiment connects one hypothesis to a small guarded change and an observable outcome. Changing one runtime-critical variable at a time helps distinguish competing explanations; combining allocation and lifecycle changes made the first XP production failure harder to isolate.

| Experiment information | Technical purpose |
|---|---|
| Clean ROM/revision and verified hash | Identifies the binary to which offsets and guards apply |
| Static, implementation, or runtime scope | Identifies what kind of conclusion the experiment can support |
| Hypothesis, expected behavior, and negative controls | Distinguishes the proposed mechanism from alternatives |
| Expected bytes, replacements, and structure offsets | Makes the patch and interpretation reproducible |
| ROM offset versus VA/RDRAM, overlay/stage, endianness, signed immediates | Prevents address and encoding ambiguity |
| Cave ownership, bounds, and pipeline interactions | Identifies conflicts with the [patch-site registry](Address-and-Patch-Site-Registry) |
| Disposable output identity, configuration/seed, route/state, and lifecycle boundary | Binds observations to the actual test |
| Positive and negative observations, remaining ambiguity | Defines the supported result and its limits |

## Evidence and corrections

[Home](Home#evidence-labels) defines the evidence vocabulary. Confirmation is scoped to the evidence available; one seed, stage, or pickup is not exhaustive coverage.

Examples of established corrections:

- `lui 0x802F` plus signed low `0xCE20` resolves to `0x802ECE20`.
- Projectile callbacks at `0x8004B82C/0x8004CC14` are not player movement evidence; player velocity is `0x8002B1EC`.
- A top-level special callback returning through its entry `$ra` self-reenters.

The earlier interpretation, evidence that changed it, and corrected mechanism remain useful historical knowledge. Material examples are collected in [Experiments, failures, and superseded findings](Experiments-Failures-and-Superseded-Findings).

## Proof and production compatibility

A working disposable ROM demonstrates a bounded behavior. It does not establish that its temporary caves are compatible with the production layout. Production compatibility includes guarded stock bytes, explicit allocation/bounds, pipeline order, deterministic seeded behavior, tests, checksum handling, and relevant runtime coverage.

New native paths, allocation changes, lifecycle hooks, and callback compositions can have failures visible only in the relevant game state. The XP stage-init hang demonstrated that successful static/CI composition alone cannot establish that safety. Runtime results from an old proof layout do not establish the behavior of a changed production composition.

## Knowledge organization

| Information | Wiki location |
|---|---|
| Subsystem mechanism, findings, and constraints | Owning domain page |
| Exact function/address/structure facts | Shared registries |
| Product maturity and bounded runtime coverage | Project and runtime status pages |
| Stage records/resources | Stage catalogs |
| Material failed or superseded approaches | Failure history and relevant owning topic |
| Durable topic navigation | Home and sidebar |

This structure keeps current explanations and decoded facts available together while retaining links to exact historical evidence when needed.
