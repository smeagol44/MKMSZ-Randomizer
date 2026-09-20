# Research workflow

## Source-of-truth order

1. Current repository implementation and tests.
2. Versioned `wiki/` owning page, registries, and stage catalogs.
3. Historical research reports and exact artifacts for provenance or unresolved detail.
4. New bounded static or runtime investigation.

The research archive is not a second current manual. When archive evidence changes a conclusion, update the owning Wiki page and preserve the superseded statement where it explains a failure or safety rule.

## Before an experiment

- Name the clean ROM/revision and verify its hash.
- State whether the task is static analysis, implementation, or runtime validation.
- Define one hypothesis and the smallest guarded change that can distinguish it.
- Resolve ROM versus VA/RDRAM addressing, overlay scope, endianness, signed-immediate effects, and cave ownership.
- Check [Address and patch-site registry](Address-and-Patch-Site-Registry) for production conflicts.
- Keep the clean ROM immutable and write a disposable output.

## Evidence recording

Use the narrow evidence labels defined on [Home](Home). Record expected bytes, replacements, addresses, relevant structure offsets, configuration/seed, exact route/state, positive observations, negative controls, and remaining ambiguity. If a result contradicts a prior interpretation, explain the mechanism of correction.

Examples of good corrections:

- `lui 0x802F` plus signed low `0xCE20` resolves to `0x802ECE20`.
- Projectile callbacks at `0x8004B82C/0x8004CC14` cannot be used as player movement evidence; player velocity is `0x8002B1EC`.
- A top-level special callback returning through its entry `$ra` self-reenters.

## Promotion to production

Promotion requires guarded stock bytes, explicit allocation/bounds, interaction with existing pipeline order, deterministic behavior where seeded, unit tests, clean-output checksum handling, documentation updates, and runtime coverage proportional to gameplay risk. Temporary proof caves must be reallocated; runtime success does not waive ownership conflicts.

## Documentation update checklist

- Owning domain page.
- Function/address/data registry if an exact fact changed.
- Project and runtime status if maturity changed.
- Relevant stage catalog if a record/resource changed.
- Failures/superseded page for a material rejected path.
- Sidebar only when a new durable domain page is added.


## Runtime-sensitive implementation gate

For a new native code path, allocation change, lifecycle hook, or callback composition that has not already been runtime-confirmed in its production layout:

1. build a disposable ROM directly from the clean supported ROM;
2. give the user the smallest bounded manual test;
3. record the observed result;
4. only after successful runtime validation, integrate that behavior into the normal browser/CLI pipeline.

Implementation/CI confirmation alone is not sufficient to promote a new runtime-sensitive path to the web patcher.
