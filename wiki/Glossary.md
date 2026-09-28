# Glossary

> **Scope:** This page defines recurring MKMSZR terminology, project shorthand, acronyms, technical vocabulary, evidence labels, and donor/importer language used across the Wiki.
>
> This is a **navigation and definition page**, not the canonical owner of changing addresses, exact structures, current status, or acceptance criteria. When a term has a domain owner, follow the linked page for the authoritative current details.
>
> Terms are grouped by subject rather than alphabetically because many definitions depend on one another.

## Project names, games, platforms, and repositories

- **MKMSZ** — *Mortal Kombat Mythologies: Sub-Zero*, the target game.
- **MKMSZR** — shorthand for the MKMSZ Randomizer project.
- **MKMSZ-Randomizer** — the main GitHub repository containing the shared patch core, tests, tooling, generated-data logic, and version-controlled Wiki sources.
- **Standalone** — the broader MKMSZR working context used for focused reverse engineering, proof builders, documentation, and product work. It does not mean a separate game revision.
- **MKT** — *Mortal Kombat Trilogy*. In this project, the N64 USA Rev. 2 release is the normal donor/reference authority for fighter assets and move semantics.
- **N64** — Nintendo 64, the primary MKMSZ target platform.
- **PS1** — Sony PlayStation. PS1 MKMSZ/MKT material is reference/donor evidence only unless transfer to N64 is separately demonstrated.
- **USA Rev. 0** — the supported N64 MKMSZ ROM revision used by the patcher and reverse-engineering work.
- **Rev. 2** — the N64 MKT revision used as the normal donor authority.
- **Atlas / MKMSZR Project Atlas** — the separate visual/reference site that presents project state, memory maps, patch sites, feature status, and decomp/readiness summaries. The main Wiki remains the technical source of truth.
- **Wiki** — the version-controlled `wiki/` directory and its published GitHub Wiki counterpart. Canonical owner pages define current project knowledge.
- **Library / MKMSZR Research** — the durable evidence/provenance archive for raw exports, Ghidra artifacts, captures, recovered builders, historical reports, and other research evidence. It is not the first source for current status when the Wiki has a canonical owner.

## Stages and stage terminology

- **Main stages** — the eight normal MKMSZ stages used by the randomizer: Temple, Wind, Water, Earth, Prison, Fire, Bridge, and Fortress.
- **Temple / Wind / Water / Earth / Prison / Fire / Bridge / Fortress** — project shorthand for the eight main stage catalogs and their runtime/resource contexts.
- **Stage ID** — the numeric game identifier used by stage-selection and stage-specific code. A displayed selector index is not necessarily the same thing as the native stage ID.
- **Stage selector** — the debug-derived stage-selection frontend used by MKMSZR for fast bounded testing.
- **Safe stage selector** — the compact production/proof selector that exposes only the eight known-safe main destinations and avoids unsafe stock debug entries.
- **Stage-local** — owned by or valid only inside one stage's current resource/overlay/runtime context.
- **Cross-stage** — moving a logical item, fighter, visual resource, or behavior from its native stage into a different stage.
- **Current-stage resource** — the stage presentation/resource package currently loaded for the active stage; some actors switch to this resource for effects or terminal presentation.
- **Stage catalog** — the canonical per-stage record of pickup tables, resource selectors, slot usage, ranges, counts, and stage-specific evidence. See [Stage catalogs](Stage-Catalogs).

## Evidence, maturity, and project-state labels

- **Runtime-confirmed** — observed in game/emulator on a defined build, route, state, and lifecycle boundary. It is always bounded to what was actually tested.
- **Static-confirmed** — established from ROM bytes, disassembly/decompilation, source, tables, or other static analysis without runtime execution.
- **Implementation/CI-confirmed** — established by repository implementation, deterministic generated output, tests, linting, or CI. It is not automatically runtime evidence.
- **Hypothesis / strong inference** — supported by the available evidence but not yet confirmed at the required static or runtime boundary.
- **Rejected / failed** — tested or analyzed and shown unsuitable within the stated scope.
- **Pending** — not yet resolved or validated.
- **Production** — part of the normal browser/CLI product path and accepted at the project's current production boundary.
- **Production beta** — integrated into the product but still missing one or more broader runtime/lifecycle/release gates.
- **Proof-only / proof** — a bounded experiment used to establish feasibility, isolate a mechanism, or reject a hypothesis. Proof allocations and shortcuts are not automatically production-safe.
- **Diagnostic** — an intentionally narrow proof designed to isolate one cause or variable rather than implement final behavior.
- **Negative control** — a deliberately retained failing or unchanged comparison that helps establish why a later result succeeded.
- **Bounded** — qualified to a specific route, stage, seed, build, actor, lifecycle edge, or test condition rather than claimed as universal.
- **Runtime-exhaustive** — tested across every relevant instance/route. The project uses this label sparingly; representative runtime confirmation is not exhaustive coverage.
- **Superseded** — still useful historically, but replaced by newer evidence or a corrected interpretation.
- **Acceptance gate / runtime gate** — the required validation boundary before a new mechanism can be promoted into production composition.
- **Current owner / canonical owner** — the Wiki page responsible for the current truth of a domain. Historical reports may preserve evidence but should not override the owner page.
- **Provenance** — enough information to reproduce or trace a result: ROM identity, seed/config, addresses, bytes, files, scripts, route, observations, and artifact identity where applicable.

See [Research methodology and evidence](Research-Workflow) and [Runtime validation status](Runtime-Validation-Status).

## ROM, files, and resource terminology

- **ROM** — the cartridge image being analyzed or patched.
- **Clean ROM** — the unmodified supported ROM used as input and never overwritten.
- **Patched ROM / output ROM** — a separate generated ROM containing MKMSZR changes.
- **ROM offset** — a byte offset inside the ROM file, such as `0x0003A018`. It is not automatically the same as a runtime virtual address.
- **File ID** — the game's numeric identifier for a resource/file in its internal global file table.
- **Global file table** — the ROM table mapping file IDs to ROM start/end ranges and flags.
- **Raw file** — a resource loaded as raw bytes without an overlay relocation model. The exact flag/loader semantics remain owned by [Resource and overlay system](ROM-Overlay-and-Resource-Map).
- **Overlay** — code/data loaded into a reusable runtime address range for a particular stage or subsystem. The same virtual address can contain different code in different overlays.
- **Overlay qualification** — identifying not just a virtual address but which overlay/file owns that address at the time. This is essential because overlay VAs are reused.
- **Resource file** — a file containing actor, presentation, image, palette, animation, stage, or other game data.
- **Fighter file / fighter resource** — the resource bundle used by the fighter constructor for a particular fighter type.
- **Stage resource file** — the current stage presentation/resource package containing outer selectors and stage-local presentation data.
- **Outer selector / resource selector** — an index in a stage/resource file's top-level selector table. A zero selector is a missing logical resource, not proof of physically free bytes.
- **Slot** — a numbered position in a table, registry, palette allocator, animation table, resource selector table, or runtime pointer table. Meaning depends on the owning structure.
- **Resource-pointer slot** — a runtime pointer location expected by the shared fighter constructor for a specific fighter type.
- **Descriptor offset** — the fighter-type-relative offset used by the constructor to find the fighter descriptor within the resident resource.
- **Primary file** — the main file required by a fighter/resource family.
- **Secondary dependency** — another resource file/slot required by the primary fighter path, often shared by a related fighter family.
- **Bundle / resource bundle** — the complete set of files/slots needed to make a fighter or item resource usable in a destination.
- **Full raw bundle** — the total uncompressed/raw allocation footprint of the files identified as required for a fighter family in the current analysis.
- **Embedded resource** — data stored inside a parent stage/resource file and addressed relative to that file.
- **External resource** — a separately loaded file/resource referenced by the active structure.
- **Resident** — currently loaded at the expected runtime location/slot and available to the code that dereferences it.
- **Materialize / materialization** — make the exact visual/resource representation needed by a randomized logical item or fighter physically resident in the destination stage.
- **Import** — bring a resource or behavior from another stage/game into the target context.
- **Relocate** — move a file/resource/code block to a different ROM or runtime location while preserving/rebuilding every reference required for it to function.
- **Rebase** — adjust file-relative pointers/offsets after moving or repacking a structure so references point at the corresponding new locations.
- **Closure / dependency closure** — the complete reachable set of resources, callbacks, data, and supporting state required for a behavior to work correctly.
- **Reachable closure** — the subset of a larger file/resource graph actually reachable from the roots used by the tested behavior.
- **Presentation resource** — art/animation/effect data used to display an action or state, distinct from the logic that causes the state.
- **Terminal presentation** — the visual sequence used at the end of an enemy's life, such as a death/despawn animation before actor removal.
- **Logical capacity** — an unused selector/table entry that can represent another resource.
- **Physical capacity** — actual owned bytes where new data may safely be stored. A zero selector can provide logical capacity without physical capacity.
- **Padding** — bytes between structures or files for alignment/layout. Padding is not automatically free storage.
- **`FF` / zero-filled-looking region** — bytes that visually resemble unused space. They are not considered free unless ownership and references are proven.
- **ROM ownership** — the project rule that every generated or edited ROM interval must have a documented owner/guard rather than being assumed free.
- **RDRAM ownership** — the corresponding rule for runtime memory.
- **File-local offset** — an offset measured from the start of one resource file rather than from ROM or RDRAM.
- **ROM expansion / high ROM** — generated-data regions near the high end of the 16 MiB ROM used by MKMSZR for owned output resources. “High ROM” is location shorthand, not a separate memory type.

See [Resource and overlay system](ROM-Overlay-and-Resource-Map), [Memory and allocation map](Memory-and-Allocation-Map), and [Data structures and encodings](Data-Structures-and-Encodings).

## Addressing and N64 memory terminology

- **RDRAM** — the Nintendo 64's main system RAM.
- **RAM address** — generic runtime memory address. In this Wiki, use the more specific VA/KSEG form when known.
- **VA / virtual address** — the CPU-visible runtime address used by code, for example `0x80039418`.
- **Physical address / physical offset** — the underlying RAM offset before the KSEG alias bits are applied.
- **KSEG0** — cached N64/MIPS virtual address region beginning at `0x80000000`.
- **KSEG1** — uncached alias of physical memory beginning at `0xA0000000`.
- **Cached alias** — the KSEG0 address for a physical RAM location.
- **Uncached alias** — the KSEG1 address for the same physical RAM location.
- **Alias** — two virtual addresses referring to the same physical memory through different cache behavior.
- **Arena** — the game's main runtime allocation region used by the bump allocator.
- **Arena floor / arena start** — the low address from which the game's main allocations begin.
- **Arena boundary / bump boundary** — the upper limit that the bump allocator must not cross.
- **Bump allocator** — an allocator that advances a cursor upward for each allocation rather than searching arbitrary free blocks.
- **Live cursor / arena cursor** — the current next-allocation pointer of the bump allocator.
- **Peak / high-water mark** — the largest cursor value observed in a bounded run.
- **Headroom** — distance between an observed peak allocation and the known arena boundary. It is not automatically confirmed-free production memory.
- **Reservation** — an explicitly owned runtime interval removed from the game's normal allocation space for MKMSZR.
- **16 KiB reservation** — the current MKMSZR production block `0x801AF420..0x801B3420`, containing Runtime V2 plus the expansion pool.
- **Runtime V2** — the established first 1 KiB MKMSZR native runtime layout inside the 16 KiB reservation: reloadable code plus persistent state.
- **Native payload** — MKMSZR MIPS code loaded into reserved RDRAM and called by patched game hooks.
- **Persistent state** — MKMSZR runtime data intentionally retained independently of transient stage actors/resources.
- **Expansion pool** — the 15 KiB production-managed subrange after Runtime V2 used for composed native feature allocations.
- **Build-time allocator** — the repository allocator that assigns non-overlapping expansion-pool slices to production features before ROM generation.
- **Code cave** — an existing ROM/code interval intentionally reused for injected instructions after ownership and liveness are proven.
- **Proof cave** — a code cave used only by a disposable proof. Runtime success does not make it production-safe.
- **Overlap / allocation conflict** — two features claiming any of the same bytes/addresses.
- **Alignment** — placing data or code at address boundaries required by the target representation or CPU access width.
- **`align4(x)`** — round a value up to a 4-byte boundary.
- **Stride / row pitch** — stored byte distance between rows of image data; it can be larger than visible width because of padding.

See [Core runtime and native payload](Core-Runtime-and-Address-Database) and [Memory and allocation map](Memory-and-Allocation-Map).

## MIPS, patching, and binary-edit terminology

- **MIPS** — the CPU instruction set used by the Nintendo 64's main CPU.
- **Instruction** — one 32-bit MIPS operation.
- **Word** — normally a 32-bit value in this project.
- **Halfword** — a 16-bit value.
- **Byte** — an 8-bit value.
- **u16 / u32** — unsigned 16-bit / 32-bit integer.
- **Signed immediate** — a small integer encoded in an instruction whose high bit changes its signed interpretation.
- **Endianness** — byte order. The supported N64 ROM is big-endian `.z64`; multi-byte reads/writes must preserve target byte order.
- **JAL** — MIPS “jump and link”; calls a function and stores a return address.
- **JALR** — “jump and link register”; indirect function call through a register.
- **JR** — jump register, commonly used for function return via `ra`.
- **NOP** — no-operation instruction, encoded as zero in the normal MIPS form used here.
- **Delay slot** — the instruction immediately after a MIPS branch/jump that still executes before control transfers.
- **Immediate** — a constant encoded directly in an instruction.
- **Guard / guarded edit** — verify exact expected bytes/words before changing them. A guard prevents silently patching the wrong ROM/revision/composition.
- **Expected bytes** — the stock or previously established bytes a patch requires before writing replacements.
- **Patch site** — a specific ROM instruction/data location intentionally modified.
- **Hook** — redirect execution from stock code into MKMSZR code, usually returning to a known continuation point.
- **Continuation / resume address** — the stock address execution returns to after an injected helper has replayed/replaced the required original behavior.
- **Trampoline / stub** — a small injected routine that redirects or adapts a call before transferring to another function.
- **Wrapper** — a routine that surrounds a stock operation with extra behavior while attempting to preserve the stock call contract.
- **Leaf helper** — a helper that does not make nested calls, useful at fragile call sites with strict register/lifecycle assumptions.
- **Register contract** — which CPU registers a caller expects to remain preserved or contain specific return values.
- **ABI** — Application Binary Interface: calling convention and runtime structure expectations between routines.
- **Host ABI** — the MKMSZ-specific calling/layout/lifecycle contract that donor code cannot assume is identical.
- **Patch composition** — the combined effect of multiple patches in one generated ROM.
- **Guarded composition** — a composition whose addresses, expected bytes, ranges, conflicts, and capacities are checked before emission.
- **CRC1 / CRC2** — N64 cartridge-header checksums updated after ROM modification.
- **SHA-256** — cryptographic hash used to identify exact input/output artifacts.
- **Deterministic build** — the same supported ROM, configuration, seed, donor inputs, and code produce byte-identical output.

See [Address and patch-site registry](Address-and-Patch-Site-Registry), [Function registry](Function-Registry), and [Testing and CI](Testing-and-CI).

## Reverse-engineering and tooling terminology

- **RE / reverse engineering** — recovering game structures, code semantics, resource formats, and runtime behavior from the compiled game.
- **Static analysis** — analysis without executing the game, such as disassembly, decompilation, table parsing, and file inspection.
- **Dynamic/runtime analysis** — observing the game while it runs, normally through manual emulator validation in this project.
- **Ghidra** — the primary static reverse-engineering suite used for N64 MKMSZ analysis.
- **Ghidra project** — the preserved analyzed program database containing auto-functions, labels, references, and decompilation state.
- **N64LoaderWV** — the Ghidra loader extension used to import/interpret the N64 ROM.
- **Disassembly** — machine instructions decoded into assembly.
- **Decompilation** — a higher-level C-like reconstruction generated from machine code. It is evidence to interpret, not original source.
- **Function registry** — the Wiki owner that records resolved function identities/semantics.
- **Call site** — an instruction/address that invokes another routine.
- **Caller / callee** — the routine making a call / the routine being called.
- **Inbound reference** — a call, pointer, table entry, or other reference leading to a routine/data structure.
- **Reachability** — whether a function/state/resource can actually be reached from live code, not merely whether its bytes exist.
- **Liveness** — whether data/code is still used by any reachable path. Zero or apparently unused bytes are not reclaimable until liveness is understood.
- **Trace** — follow control flow, data flow, resource references, or lifecycle edges until the relevant dependency/predicate is resolved.
- **Static trace** — such a trace performed without running the emulator.
- **Bounded experiment** — deliberately small proof changing as few variables as possible.
- **BizHawk** — the emulator frontend historically used for manual MKMSZR runtime validation.
- **Ares64** — the N64 core used in the documented BizHawk validation environment.
- **Lua randomizer** — the older BizHawk Lua implementation used before the current native-ROM patcher architecture. It is historical/reference behavior, not the current product core.

## Randomizer, seed, solver, and lifecycle terminology

- **Seed** — user-visible deterministic input used to derive randomized choices.
- **RNG** — random-number generator. In MKMSZR it must be deterministic for a given seed/configuration.
- **RNG namespace** — a separated deterministic random stream for one feature, used so changing presentation or another option does not silently perturb gameplay placement.
- **Determinism** — identical inputs produce identical logical layout and generated ROM.
- **Retry attempt** — a deterministic next attempt when a generated global layout fails the solver or another validity condition.
- **Solver** — logic that evaluates whether the generated run is completable under the project's access/progression model.
- **Access rule** — condition required to reach a location, stage, item, or objective.
- **Completion predicate** — the condition the solver uses to decide that the run can be finished.
- **Logical item** — the gameplay identity being awarded/owned, independent of how the item is visually/materially represented in a destination stage.
- **Location** — a randomized check/reward position or event that receives an assigned logical item.
- **Assignment** — mapping of a logical item to a location.
- **Global pool** — one run-wide set of logical items/locations rather than separate stage-local shuffle pools.
- **Stage-local pool** — the current interim randomizer model where each stage shuffles its own ordinary pickups independently.
- **Materializer / resource planner** — code that decides which destination resources must be added/reused/rebased so the assigned logical item or fighter has the correct physical representation.
- **Solvable / winnable seed** — a deterministic seed whose generated layout satisfies the current solver/completion requirements.
- **Required Power-Ups target** — the deterministic per-seed count/policy governing how much progression is required by the final global solver design.
- **Lifecycle** — creation, stage entry, gameplay, transitions, menu/title returns, death, Game Over, save/load, teardown, and new-run boundaries that may affect state/resources.
- **Persistence** — state intentionally retained across one or more lifecycle boundaries.
- **Reconstruction** — rebuilding native game state from MKMSZR persistent state after reload/re-entry.
- **Collected flag** — native or reconstructed state indicating an ordinary pickup has already been taken.
- **Checkpoint** — game state used as a death/respawn return point.
- **Checkpoint side effect** — an unwanted checkpoint relocation caused by acquiring certain key items; this is distinct from their inventory award or visual banner.
- **New-run reset** — clearing state that must not survive into a fresh game.
- **Game Over reset** — lifecycle handling when continues/lives are exhausted.
- **Very Hard invariant** — the 1.0 requirement that final gameplay difficulty be locked to Very Hard.
- **Temple Map** — the special Map item whose inventory identity and Temple elevator/progression trigger must be separated correctly in the global randomizer.
- **XP** — experience points used by MKMSZ progression.
- **Tier / power tier** — progression threshold that unlocks a Power Upgrade/move.
- **Power order / Shuffle Power Progression** — optional deterministic reassignment of the nine Power Upgrade rewards to the nine XP gates, subject to approved ordering constraints.

See [Global item materialization and solvability](Global-Item-Materialization-and-Solvability), [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle), and [XP and progression](XP-and-Progression).

## Pickup and inventory terminology

- **Ordinary pickup** — a normal stage pickup managed by the shared ordinary-pickup system rather than a one-off scripted reward.
- **Pickup record** — the stage data record defining an ordinary pickup's position, identity, resource selector, callback, and related fields.
- **Stable pickup identity** — the persistent bit/index assigned to one ordinary pickup location independent of randomized item identity.
- **Pickup manager order** — the runtime order in which ordinary pickups are managed; it is checked against stage-catalog order when assigning persistence bits.
- **Complete identity slice** — the group of pickup-record fields that must move together so art, award, callback, and resource identity remain coherent.
- **Foreign item** — an item whose native resource does not exist in the destination stage and therefore needs materialization.
- **Key item** — an item that changes stage progression/access rather than being only a consumable/stat pickup.
- **Boss-defeat reward location** — a reward record activated by defeating a specific encounter. The trigger/location identity is separate from the logical item placed there.
- **Four-box inventory** — MKMSZR's four backing inventory boxes with explicit user switching.
- **Live box** — the inventory currently copied into the game's active native inventory state.
- **Backing box** — one of the stored MKMSZR inventory snapshots not currently live.
- **Foreign-key masking** — temporarily hide stage-inappropriate foreign key identities from native game logic while preserving their stored ownership.
- **Glass** — the inert inventory identity used as the masking placeholder because it avoids the consumable behavior of earlier candidates.
- **BOX n OF 4** — the native HUD indicator showing which MKMSZR inventory box is active.

See [Pickups and stage-local randomization](Pickups-and-Item-Randomization) and [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle).

## Enemy-randomization terminology

- **Ordinary enemy** — a fighter spawned through the shared ordinary-enemy command-stream interpreter rather than a dedicated boss/script path.
- **Ordinary branch / ordinary stream** — the stage command stream or branch used by normal enemy spawns.
- **Spawn command / spawn record** — one command describing an enemy spawn's type, coordinates, quota, activation mode, and related fields.
- **Fighter type** — the numeric actor/fighter identity stored at actor `+0x78` and used to index shared constructor tables.
- **Constructor** — the shared routine that resolves fighter resource pointer + descriptor and creates the actor.
- **Compatibility matrix** — the stage × fighter-type research table classifying native residency, import requirements, bounded runtime evidence, and unresolved dependencies.
- **Native / N cell** — matrix state meaning the fighter is already native/resource-resident in that stage. It is not automatically pairwise runtime approval.
- **Import-required / I cell** — matrix state meaning one or more exact resources/slots are absent and must be materialized.
- **Bounded runtime import / P cell** — historical/current matrix shorthand for a cross-stage import with bounded runtime evidence; always read the legend because the exact maturity represented by the letter can evolve with evidence.
- **Special singleton** — a one-shot gated enemy record embedded in an ordinary stream but owned by a special encounter, such as Scorpion, Undead Scorpion, Kia, Jataaka, or Sareena. These are excluded from the first general pool.
- **Conservative first pool** — repeated native-resource fighter types considered the safest initial ordinary-randomization candidates before broad cross-stage imports.
- **Terminal dependency** — any auxiliary resource/callback required after combat reaches death/despawn handling.
- **Auxiliary presentation dependency** — presentation data not contained in the main fighter file but needed for a complete imported fighter lifecycle.
- **Selector 10** — a current-stage resource selector used by the Runtime-confirmed Fire × MONK2 terminal/death proof. It is **not** a universal death-resource slot: other stages may use selector 10 differently or leave it empty.
- **MONK1…MONK6 / HULK MONK / FAST MONK / GRUNT1 / GRUNT2 / PRIS GRUNT1…4** — static fighter names used by the ordinary-enemy compatibility work. Their type IDs and current resource bundles are owned by [Enemy randomization](Enemy-Randomization).
- **Kia / Jataaka / Sareena assassin records** — special Fortress singleton encounters that activate the corresponding boss-defeat reward records; they are not general ordinary-pool enemies.
- **Death/despawn** — the terminal fighter lifecycle: death state/presentation followed by active-enemy accounting cleanup and actor removal.
- **Arena pressure** — increase in RDRAM allocation caused by imported fighter/resource bundles.
- **Replacement composition** — replace native destination allocations with imported resources instead of simply appending additional full files.
- **Compact/rebased composition** — keep only the reachable resource closure, rebuild relative references, and repack it to fit the destination budget.
- **Mixed roster** — a stage containing multiple randomized fighter types at once.

See [Enemy randomization](Enemy-Randomization).

## Graphics, image, palette, and animation terminology

- **Palette** — indexed color table used by an image/resource.
- **TLUT** — Texture Look-Up Table; the palette used by indexed N64 textures.
- **BGR555** — 16-bit source-color representation used by MKMSZ palette data: five bits each for blue, green, and red plus the project-documented control/high-bit semantics.
- **RGB555** — 15-bit RGB-style color representation used by some preserved donor assets.
- **RGBA5551** — N64 MKT donor palette representation with five bits each of red/green/blue plus one alpha bit.
- **CI4** — 4-bit color-index texture representation, normally selecting among 16 palette entries.
- **CI8** — 8-bit color-index texture representation, normally selecting among up to 256 palette entries.
- **bpp** — bits per pixel.
- **Indexed image** — image whose pixels store palette indices rather than direct RGB colors.
- **Palette binding** — associating an actor/image with the correct runtime palette selector/handle.
- **Palette handle** — native runtime identifier returned by the palette allocator and stored on actors.
- **Palette refcount / release** — native lifetime accounting for shared/allocated palette state.
- **Texture slot** — native runtime slot holding/identifying prepared texture image data.
- **Texture publication / actor publication** — making an actor visible to the renderer after descriptor, palette, and texture-slot state are ready.
- **First-visible frame** — the first rendered frame after actor publication; important in the Sektor missile work because stale texture state could appear for one frame.
- **Frame** — one visual image/pose entry used by an animation.
- **Pose** — visual fighter stance/frame; often used when discussing donor animation mapping.
- **Shape** — descriptor/geometry/image unit referenced by an animation frame.
- **Animation script** — sequence of frame pointers plus control tokens/callback directives.
- **Token / control word** — non-frame entry inside an animation script that changes timing, looping, callbacks, flips, or other behavior.
- **Primary / secondary animation table** — the two major fighter animation tables used by MKMSZ/MKT mapping work.
- **Pxx / Sxx** — project shorthand for MKMSZ primary/secondary animation slots, for example `P28`, `P2A`, or `S03`.
- **COMMON / DIRECT** — importer classification: MKMSZ requires the state and a normal MKT fighter has a semantically equivalent donor animation.
- **COMMON / FALLBACK** — MKMSZ requires the state but the donor has no directly equivalent exposed animation; use an approved donor fallback while preserving MKMSZ control/lifecycle semantics.
- **HOST-ONLY** — a live MKMSZ state whose semantics belong to MKMSZ and do not have an established direct donor equivalent.
- **CHARACTER-SPECIFIC / HOST-SPECIAL EXTENSION** — state/resource tied to Sub-Zero/MKMSZ powers or other character-specific behavior rather than the generic fighter-body importer.
- **Cut frame** — art/animation present in another source/reference but omitted from the retail donor build.
- **Multipart art** — one displayed pose/effect assembled from multiple image pieces/actors.
- **Companion actor** — secondary actor owned by another action/actor, such as attachment presentation or helper effects.
- **Anchor** — image placement origin/offset used to position a frame relative to an actor.
- **Geometry** — width, height, anchor, crop, and related placement data.
- **Codec** — encoding/compression format used to store image data.
- **Type-5** — project name for the MKMSZ-native fighter image/stream format generated for imported donor art. Donor codecs are decoded offline and re-emitted as valid target-native Type-5 data.
- **VQ** — vector quantization; image compression using reusable small pixel patterns/codebook entries.
- **Codebook / dictionary** — collection of reusable image patterns referenced by encoded image streams.
- **Pattern** — one reusable small pixel block in the target Type-5/VQ representation.
- **Model / entropy model** — encoding model used by the generated Type-5 stream.
- **Compression stream** — encoded payload that references patterns/models rather than storing every pixel directly.
- **Transparency mask** — which pixels are transparent; preserved separately from ordinary color error metrics in donor conversion.
- **RMSE** — root-mean-square error, used as one numeric image/palette approximation metric. It does not by itself establish visual correctness.
- **WIMP** — the name used by preserved Midway raw-image tooling/files in this project. The Wiki treats it as a source-format/tooling label; it does not currently expand the acronym.
- **ROBO8.IMG** — preserved Midway robot image source used as supplemental Sektor art evidence after the PS1 pixel path was rejected.
- **POVBQ** — project/source label for the PS1 MKT vector-quantized representation investigated during supplemental asset research; the current PS1 pixel interpretation is rejected for N64 fighter import.
- **Row pitch / source stride** — stored bytes between source image rows. WIMP rows use `align4(xsize)`, not simply visible width.
- **Palette normalization** — deterministic reduction/remapping of donor colors into the target palette budget.
- **16-color importer direction** — accepted generic MKT→MKMSZ policy to normalize imported fighter art to a 16-color indexed palette unless evidence shows a real incompatibility.

See [Data structures and encodings](Data-Structures-and-Encodings), [Palette and recoloring](Palette-and-Recoloring), and [MKT fighter asset translation](MKT-Fighter-Asset-Translation).

## Donor, compatibility-layer, and Sektor terminology

- **Donor** — another game/build/resource used as the semantic or asset source. For normal fighter importing, N64 MKT is the primary donor authority.
- **Host / target** — MKMSZ, the game whose engine, ABI, lifecycle, resources, and native semantics must ultimately be respected.
- **Compatibility layer** — the translation strategy that maps donor semantics/assets into target-native MKMSZ behavior rather than relocating donor code blindly.
- **Adapter** — code/data translation that converts one donor concept into target-native primitives/structures.
- **Adapter primitive** — a reusable MKMSZ operation corresponding to a donor semantic, such as movement intent, facing, projectile spawn, collision, animation selection, or cleanup.
- **Semantic translation** — preserve what a donor operation means while implementing it with target-native routines/data.
- **Binary transplantation** — copying donor machine code directly. This is not the accepted general strategy because layouts, scheduler/process ABI, tables, heaps, and callbacks differ.
- **Source-level port** — reconstruct donor control flow/meaning using MKMSZ-native primitives.
- **Takeover** — replace Sub-Zero's visible fighter assets/states with a donor fighter while retaining the MKMSZ host engine.
- **Sektor takeover** — the project proof line using MKT Sektor as the guinea pig for a future generic N64 MKT fighter importer.
- **Importer** — tooling that converts donor fighter assets/semantics into MKMSZ-native assets/data.
- **Generic fighter importer** — intended reusable MKT fighter→MKMSZ translation path rather than Sektor-specific patching.
- **Mapping** — association between a required MKMSZ state/animation and a donor animation/fallback.
- **Donor-equivalent cadence** — target timing chosen to reproduce donor animation timing despite different script formats/frame lists.
- **Host lifecycle** — MKMSZ's process/action setup, scheduling, actor ownership, callbacks, teardown, and state transitions.
- **Donor lifecycle** — the equivalent behavior in MKT, used as semantic reference rather than assumed ABI-compatible code.
- **Rocket / straight missile** — Sektor special-move proof line used to develop projectile adapter primitives and asset/palette/texture readiness handling.
- **Reverse Elbow** — donor-move research case used to develop host action/adapter semantics; not itself a 1.0 blocker.
- **No-repel / repulsion suppression** — donor behavior temporarily disabling ordinary fighter separation so an action can pass through/cross the opponent.

See [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer), [MKT adapter primitives](MKT-Adapter-Primitives), [MKT fighter asset translation](MKT-Fighter-Asset-Translation), [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping), and [Sektor takeover proof history](Sektor-Takeover-Proof-History).

## Product/UI feature names

- **GAME SETTINGS** — native in-game frontend used by MKMSZR for configurable control behavior.
- **TURN: TOGGLE / LOCK** — facing/turn behavior options.
- **ATTACK: CLASSIC / MODERN** — attack-input mode.
- **SPECIALS: CLASSIC / MODERN** — special-move input mode.
- **JUMP: DPAD / BUTTON** — jump-input mode.
- **RUN: HOLD / AUTO** — run-input mode.
- **Modern controls** — collective shorthand for ATTACK/SPECIALS/JUMP/RUN alternatives implemented through MKMSZ-native control/action semantics.
- **Native HUD** — UI rendered through the game's own text/sprite systems rather than direct framebuffer drawing.
- **Randomizer HUD** — planned run-state display for checks/progression/key/pickup information; broader than the already-produced box indicator.
- **Boot branding** — legal/boot presentation modified by MKMSZR.
- **Seeded phrase** — deterministic boot phrase generated from its own RNG namespace.
- **Title branding / edition text** — rebranded title screen and configurable `<NAME> EDITION` text.
- **Rainbow** — runtime outfit mode that cycles 64 generated palettes while preserving the native palette allocator/release path.
- **Compact-tail Rainbow** — production optimization that leaves stock Sub-Zero file `0x87` in place and loads only the extra 8 KiB rainbow palette bank into an appended runtime tail.
- **Toasty** — MK-style visual/audio easter egg imported from MKT and integrated as an optional MKMSZR feature.
- **CI4 Toasty** — compact production Toasty visual representation using 4-bit indexed slices plus a 16-entry palette.
- **Selector-only save bypass** — suppress only the unwanted immediate save associated with entering the debug stage selector, not normal saving globally.
- **Post-legal logo bypass** — skips selected post-legal logo flow while retaining required title/fade initialization.
- **Safe Stage Select / compact selector** — current supported eight-stage debug selector path.
- **Shuffle Power Progression** — optional deterministic shuffle of Power Upgrade order, constrained by the accepted Ice Shatter prerequisite.

## Development, Git, and CI terminology

- **CLI** — command-line interface.
- **Browser patcher / web patcher** — browser UI using the same shared patch core as the CLI.
- **Shared patch core** — one implementation path used by both browser and CLI generation.
- **Builder** — script/module that constructs a proof or production ROM from guarded inputs.
- **Proof builder** — disposable/reproducible builder for one bounded experiment.
- **Pipeline** — ordered composition of patch modules and generation steps.
- **CI** — Continuous Integration: automated linting, tests, build/parity checks, and related repository validation.
- **Ruff** — Python linter/formatter check used by repository CI.
- **pytest** — Python test framework used by the repository.
- **PR** — GitHub Pull Request.
- **Branch** — Git branch containing a proposed set of changes.
- **Merge** — integrate an approved PR into `main`.
- **`main`** — canonical repository branch.
- **Wiki sync** — repository automation that publishes version-controlled `wiki/` changes to the GitHub Wiki.
- **Pages deployment** — publication of the Atlas/site through GitHub Pages where applicable.
- **Byte parity / byte-identical** — independently generated output exactly matches a previously accepted artifact.
- **Reproducible build** — builder and inputs are sufficient to recreate the documented output/hash.

## Common notation

- **`0x...`** — hexadecimal number.
- **`[start,end)`** — half-open range including `start` and excluding `end`.
- **`+0xNN`** — offset relative to the base of the current object/file/structure.
- **`A -> B`** — depending on context, “changes/maps from A to B” or a call/data-flow edge; read the surrounding owner page for exact semantics.
- **`type 0xNN`** — fighter/actor type number.
- **`file 0xNN`** — internal game file ID.
- **`slot N` / `selector N`** — indexed position in the currently discussed table.
- **`vNN`** — proof/build revision number within one experiment line, not a product version.
- **KiB** — kibibyte, 1024 bytes.
- **MiB** — mebibyte, 1024 KiB.
- **Hz / fps** — frequency / frames per second where timing/video comparisons are discussed.
- **`ROM ... / VA ...`** — paired file offset and runtime virtual address for the same instruction/data when a stable mapping is known.

## Terms deliberately not duplicated here

The glossary intentionally does **not** list every individual function address, patch address, pickup record, animation slot, file ID, stage selector, enemy type, or proof hash. Those are registries/catalog data rather than vocabulary and change more often.

Use these owners for exact values:

- [Address and patch-site registry](Address-and-Patch-Site-Registry)
- [Function registry](Function-Registry)
- [Data structures and encodings](Data-Structures-and-Encodings)
- [Memory and allocation map](Memory-and-Allocation-Map)
- [Stage catalogs](Stage-Catalogs)
- [Enemy randomization](Enemy-Randomization)
- [Runtime validation status](Runtime-Validation-Status)

If a recurring term appears in project discussion but is missing here, add it to this page when its meaning is stable enough to define without duplicating a changing registry.
