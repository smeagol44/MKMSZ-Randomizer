# Complete research synthesis

> **Historical / superseded page.** This URL is retained for old Wiki, archive, and external links. It no longer owns current project status, requirements, technical reference, or proof chronology.
>
> Start with [Home](Home) for current routing, [Project status](Project-Status) for current maturity and priorities, [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) for release requirements, [Runtime validation status](Runtime-Validation-Status) for evidence scope, and [Architecture overview](Architecture-Overview) for the current system model.

## Why this page remains

This page formerly served as the broad cross-domain research synthesis while MKMSZR was moving from Lua-era experimentation and research handoffs into a guarded native ROM-patching architecture.

One historically important decision recorded by the old synthesis was to keep the first production pickup randomizer **stage-local** while cross-stage resource materialization was still proof work. That decision was a bounded implementation step, not the final product goal. Later research established extension selectors, imported-resource materialization, external-to-embedded conversion, and a generalized pure planner; the planner remains outside the normal browser/CLI pipeline pending its production integration gates. Current details belong to [Pickups and stage-local randomization](Pickups-and-Item-Randomization) and [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

The old synthesis also accumulated compact summaries of persistence, enemies, XP, player actions, and PS1 portability. Those subjects now have dedicated canonical owners, so repeating their technical conclusions here would recreate the ownership problem this refactor removed.

## Current canonical owners

| Subject formerly summarized here | Current owner |
|---|---|
| Product architecture and subsystem boundaries | [Architecture overview](Architecture-Overview) |
| Current production / proof / pending state | [Project status](Project-Status) |
| 1.0 requirements and acceptance gates | [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) |
| Runtime evidence scope | [Runtime validation status](Runtime-Validation-Status) |
| Stage-local ordinary pickup behavior | [Pickups and stage-local randomization](Pickups-and-Item-Randomization) |
| Cross-stage materialization, global shuffle, and solvability | [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |
| Pickup persistence, four-box inventory, and lifecycle | [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle) |
| XP / progression behavior and proof history | [XP and progression](XP-and-Progression) |
| Ordinary-enemy architecture and import proof | [Enemy randomization](Enemy-Randomization) |
| MKMSZ player-action host semantics | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| MKT donor compatibility and translation | [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer) and [MKT adapter primitives](MKT-Adapter-Primitives) |
| PS1 findings and transfer limits | [PS1 research](PS1-Research) and [N64–PS1 comparison](N64-PS1-Comparison) |
| Major project chronology | [Milestone timeline](Milestone-Timeline) |
| Rejected / superseded findings | [Experiments, failures and superseded findings](Experiments-Failures-and-Superseded-Findings) |
| Archive provenance | [Historical artifact index](Library-Artifact-Index) |

## Supersession notes

The former synthesis's status statements and decision-boundary table are historical snapshots, not current truth. In particular:

- the old statement that a general cross-stage resource planner did not exist is **superseded**; a pure planner now exists but remains pipeline-disconnected and not production-integrated;
- the old textured-UI boundary predates later Runtime-confirmed gameplay-HUD textured-node and genuine Toasty-pixel proofs;
- proof-only enemy, donor-move, Sektor, and Toasty work has advanced beyond the old one-page summaries and must be read from its current owner;
- exact addresses, allocations, structures, stage records, and evidence limits belong to the current registries/domain pages, not to this historical index.

For research history, use [Milestone timeline](Milestone-Timeline), the owning proof-history pages, [Experiments, failures and superseded findings](Experiments-Failures-and-Superseded-Findings), and [Historical artifact index](Library-Artifact-Index).