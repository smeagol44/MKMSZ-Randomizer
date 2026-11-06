MKMSZR - Standalone Project Instructions

SOURCES
- GitHub `smeagol44/MKMSZ-Randomizer`: implementation/product source of truth.
- Versioned `wiki/` + published Wiki: requirements, status, technical knowledge, registries, catalogs, validation state, pending work.
- Library `MKMSZR Research`: evidence/provenance archive (Ghidra work, exports, captures, manifests, experiments, builders, historical reports).
Wiki pages hold project knowledge, not assistant rules. Old handoffs/Library reports may be superseded; read the current Wiki owner first.
Findings relayed from another assistant/chat are unverified input until checked against code, ROM evidence and the current Wiki.

GHIDRA
- `smeagol44/MKMSZ-Ghidra` is the living ROM-free Ghidra metadata repo; the Wiki stays authoritative.
- Consult it before relevant static RE to avoid duplicate work.
- When findings are verified, update the Wiki owner and, when practical, Ghidra metadata (names, signatures, types, structures, locals, data, comments, bookmarks, references).
- Preserve stage/overlay identity; never flatten overlapping VAs or promote guesses.
- After commits, the user pulls and reruns both import scripts.

CANONICAL ROUTING
Always start with `Project-Status.md`; add `1.0-Requirements-and-Roadmap.md` if product/release behavior is involved.
Owners:
- Project-Status: maturity, blockers, priorities
- 1.0-Requirements-and-Roadmap: requirements, acceptance criteria, release gates
- Runtime-Validation-Status: runtime/evidence matrix
- Architecture-Overview: subsystem boundaries
- Research-Workflow: methodology/evidence conventions only
- Memory-and-Allocation-Map: ROM/RDRAM ownership, reservations, conflicts, proof/candidate/free
- Address-and-Patch-Site-Registry: guarded edit sites/bytes
- Function-Registry: function identities/semantics
- Data-Structures-and-Encodings: structures/codecs
- ROM-Overlay-and-Resource-Map: file/resource/overlay mechanics
- Stage-Catalogs + Stage-Catalog-*: stage records, slots, ranges, counts
- Pickups-and-Item-Randomization: ordinary/stage-local pickups
- Global-Item-Materialization-and-Solvability: global pool, materialization, retries, solver, required powers, Temple Map
- Persistence-Inventory-and-Lifecycle; XP-and-Progression; Native-HUD-and-UI; Presentation-and-Branding
- Player-Actions-and-Special-Moves: host action/control ABI
- MKT-to-MKMSZ-Compatibility-Layer, MKT-Adapter-Primitives, MKT-Fighter-Asset-Translation, Sub-Zero-to-Sektor-Animation-Mapping, Sektor-Takeover-Proof-History: donor port
- Experiments-Failures-and-Superseded-Findings: rejected/superseded index
- Library-Artifact-Index: archive provenance
Use Home/sidebar for other owners; retired/stub pages are not owners.

TASK ALIGNMENT
User requirements and the Roadmap are hard constraints. Never silently change semantics, determinism, progression, scope or goals. Proofs/diagnostic shortcuts do not redefine production behavior.
"Continue" = continue the last agreed task. "What next" = Project Status priority plus latest user direction.
Product/design changes need user approval; routine work within accepted requirements does not.

RESEARCH
Before RE/implementation: read Project-Status; the Roadmap if product behavior is affected; relevant owners; and as relevant Architecture, Memory Map, Patch Registry, Resource/Overlay map, stage catalogs, Runtime Validation and failure history. Use Library evidence only for exact provenance/history/conflicts.
Don't repeat completed research. Prefer focused traces and bounded experiments. Check known failures/open questions first. Rebuild the Ghidra project only if genuinely unusable.
PS1 findings are platform-specific unless transfer is demonstrated; MKT/other games are donor/reference, not compatible binaries.

ROM SAFETY
Keep the clean ROM untouched; verify ROM/revision/hash from current Wiki/repo; use separate disposable outputs; never commit ROM bytes.
Before patching resolve: ROM offset vs VA/RDRAM, stage/overlay scope, endianness/signed immediates, expected bytes, ownership/bounds, pipeline conflicts, failure behavior, CRC1/CRC2.
Zero/FF/padding or empty selectors are not automatically free. Proof caves are not production-safe by default. Memory Map owns ownership; Patch Registry owns guarded edits.
Before reusing a stock region, find all readers AND writers, including features outside normal gameplay (password screen, cheats, debug/options menus). One known reference does not prove exclusive use.
Injected code must not carry state in k0/k1 (interrupts overwrite them); follow the documented execution/cache contract for raw-loaded code and state.

RUNTIME / PRODUCTION
Don't run emulator automation unless explicitly asked; the user validates manually.
For new native paths, allocations, lifecycle hooks, callback composition or materially new production composition: smallest guarded disposable proof -> bounded manual test -> integrate only after user runtime validation, unless the exact behavior and composition are already runtime-confirmed. CI/static success never waives runtime gates.
Before integration verify addresses, guards, bounds, ownership, pipeline interactions, lifecycle, determinism, checksums, tests and failure behavior. Reallocate conflicting proof caves first.

EVIDENCE
Labels: Runtime-confirmed; Static-confirmed; Implementation/CI-confirmed; Hypothesis / strong inference; Rejected / failed; Pending.
No runtime confirmation without user observation or supplied runtime evidence. Never generalize one seed/stage/item/enemy/route to exhaustive coverage. Static analysis of a generated ROM is static/implementation evidence for that exact build config.
Record enough to reproduce: input/output identity, config/seed, addresses, bytes, structures, allocations, route/state/lifecycle, observations, negative controls, ambiguity.
When Wiki and Library conflict, inspect the evidence; preserve useful superseded findings and explain corrections.

DOCUMENTATION / STORAGE
When verified findings change knowledge, update the canonical Wiki owner in the same task when practical; touch registries/catalogs/status/roadmap/failure pages only when their owned facts change.
Edit `wiki/` first; verify published Wiki sync after reaching `main`.
Code/tests/CI/docs live in GitHub; raw durable evidence in Library. Don't upload disposable ROMs, duplicate scripts or regenerable intermediates.

GITHUB WORKFLOW
Repository changes (code, tests, CI, `wiki/`) go through PRs; the user reviews and merges. Prefer one PR per task, with its Wiki update in the same PR.
Other assistants may work on this repo: start from latest `main`, keep PRs focused, avoid editing status pages touched by an open PR unless coordinated.
Be quota-conscious: avoid large GitHub reads (full PR threads, CI logs) and don't watch PRs unless asked.

CI HYGIENE
Compare CI failures against changed files/merge base before attributing them. Don't blame unrelated pre-existing failures on a narrow/docs change, and don't fix unrelated files unless asked; report them separately.

WORK MODE
Prefer normal Sol chats for implementation, Wiki/GitHub work, bounded RE and proof builders. Use Work only when its larger workspace materially helps (hard Ghidra analysis, archive consolidation, broad reconciliation, multi-repo work).

FILE NAMES
Generated ROMs: `MKMSZR_<purpose>_<stage-or-scope>_<proof-or-build>_vNN.z64` (short lowercase-hyphenated descriptors; increment vNN).
