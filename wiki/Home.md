# MKMSZR technical knowledge base

MKMSZR is a native-ROM randomizer project for **Mortal Kombat Mythologies: Sub-Zero** on Nintendo 64. The supported game target is the **USA Rev. 0** release; exact ROM identity and low-level validation details live on the owning technical pages rather than here.

This Wiki is the current technical and product knowledge base for the project. Use it to find current project state, 1.0 requirements, runtime evidence, implementation/reference material, stage catalogs, donor research, and preserved failure/history records.

## Start here

- [Project status](Project-Status) — current production, proof-only, pending, and priority state.
- [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) — canonical 1.0 scope, acceptance criteria, blockers, and dependency order.
- [Runtime validation status](Runtime-Validation-Status) — current evidence matrix and runtime-validation scope.
- [Contributor start here](Contributor-Start-Here) — repository workflow, build/test entry points, and contribution routing.
- [Architecture overview](Architecture-Overview) — high-level system boundaries and patch/runtime architecture.
- [Research methodology and evidence](Research-Workflow) — evidence labels, bounded-experiment method, and research provenance.

## Find the right owner

### Core technical reference

Use [Core runtime and native payload](Core-Runtime-and-Address-Database) for bootstrap/runtime mechanisms, [Memory and allocation map](Memory-and-Allocation-Map) for literal ROM/RDRAM ownership, [Function registry](Function-Registry) for function semantics, [Address and patch-site registry](Address-and-Patch-Site-Registry) for guarded edit sites, [Data structures and encodings](Data-Structures-and-Encodings) for stable structure/codec grammar, and [Resource and overlay system](ROM-Overlay-and-Resource-Map) for file/overlay/resource-loading rules. [Address quick reference](Address-Quick-Reference) is a convenience subset, and [Testing and CI](Testing-and-CI) owns automated validation/publication mechanics.

### Randomizer and product systems

Current system owners are [Stage flow and selector](Stage-Flow-and-Selector), [Pickups and stage-local randomization](Pickups-and-Item-Randomization), [Global item materialization and solvability](Global-Item-Materialization-and-Solvability), [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle), [XP and progression](XP-and-Progression), [Native HUD and UI](Native-HUD-and-UI), [Presentation and branding](Presentation-and-Branding), [Audio system](Sounds-and-Music), [Palette and recoloring](Palette-and-Recoloring), and [Web patcher and product](Web-Patcher-and-Product).

### Stage reference

[Stage catalogs](Stage-Catalogs) is the shared index/legend for the eight main-stage catalogs and links to Temple, Wind, Water, Earth, Prison, Fire, Bridge, and Fortress.

### Gameplay, enemies, and donor research

Start with [Enemy randomization](Enemy-Randomization) or [Player actions and special moves](Player-Actions-and-Special-Moves) for MKMSZ gameplay research. For donor work, use the [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer), then its focused owners: [MKT adapter primitives](MKT-Adapter-Primitives), [MKT fighter asset translation](MKT-Fighter-Asset-Translation), [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping), and [Sektor takeover proof history](Sektor-Takeover-Proof-History). Toasty work is split between [Toasty audio research](Toasty-Audio-Research) and [Toasty visual research](Toasty-Visual-Research). Platform-specific donor/reference material lives in [PS1 research](PS1-Research) and [N64–PS1 comparison](N64-PS1-Comparison).

### History, failures, and provenance

Use [Experiments, failures and superseded findings](Experiments-Failures-and-Superseded-Findings) for the cross-domain rejected/superseded index, [Milestone timeline](Milestone-Timeline) for major chronology, and [Library artifact index](Library-Artifact-Index) for preserved research/archive provenance.

## Canonical ownership

Prefer the current canonical owner pages linked from this Home page and the sidebar. Older pages may remain at stable URLs as supersession stubs for historical or external links; when a stub points to a current owner, the current owner is authoritative. Do not treat a retired or superseded page as current technical truth merely because its URL still resolves.
