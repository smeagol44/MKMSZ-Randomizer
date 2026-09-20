# Pickups and item randomization

## Native record model

All eight main stages use ordinary `0x30`-byte records. The production catalog contains exactly 84. The movable identity is the seven-word slice `+0x10..+0x2B`: type, callback parameter, callback, two extents, stage-local resource slot, and presentation descriptor. Position/metadata `+0x00..+0x0F` and collected flag `+0x2C` remain attached to the location.

Same-stage Fire Potion-to-Herbs testing established why the entire identity must move: callback changes the award, while type/resource/presentation fields control visible and collision behavior. Copying the complete tuple produced correct Herbs behavior and art at the Potion location.

## Current interim production shuffle

For each stage, the generator uses a stable SHA-256-based Fisher–Yates shuffle with domain:

```text
MKMSZR:PICKUPS:STAGE-LOCAL:V1\0
```

The input includes seed bytes, native stage ID, deterministic attempt number, and counter. RNG is isolated from boot phrases, palettes, and future features. A seedless configuration leaves pickup layout unchanged.

Candidate layouts are rejected, up to 1,000 deterministic attempts, if the known access model cannot obtain stage progression tokens before their required locations. CI exercises 250 seeds and asserts catalog integrity, tuple preservation, determinism, namespace isolation, and constraints.

## Access model

| Stage | Modeled dependencies |
|---|---|
| Temple | Four ordinary locations free; scripted Map excluded |
| Wind | fifth location requires `wind-circle`; sixth requires `wind-triangle` |
| Water | second requires `water-moon`; eighth requires `water-triangle`; ninth requires `water-three-bars` |
| Earth | first three yield Square, Four Squares, Triangle; later locations require Square or Four Squares as listed in the Earth catalog |
| Prison | staged Level 1/2/3 dependencies as listed in the Prison catalog |
| Fire, Bridge, Fortress | Current ordinary locations treated as free by the ported access model |

These are implementation/CI-confirmed rules ported from legacy logic. A complete native runtime playthrough across arbitrary seeds remains pending.

This stage-local mode is an implementation stepping stone, not the final 1.0 randomizer model. 1.0 requires a single cross-stage logical pool and a whole-run validator.

## Progression-reward overlay

After the ordinary layout is accepted, production derives Herbs candidates from that exact assignment and selects exactly nine using a separate SHA-256 Fisher-Yates domain:

```text
MKMSZR:PROGRESSION:HERBS:V1\0
```

Only the callback word of each selected generated Herbs identity is changed. Type, collision, stage-local resource selector and presentation stay Herbs, so the ordinary pickup shuffle is unchanged and no cross-stage resource import is required.

The progression callback advances to the next native XP threshold, evaluates the native tier at pickup acquisition, and does not insert an inventory item. Ordinary pickup persistence still records the physical location as collected. Progression count/XP are stored separately from the 84 ordinary-pickup bits.

Diagnostic A runtime-confirmed the generated Temple pattern for seed `BCBDBF`: first and third Herbs were progression rewards, second Herbs remained normal, XP reached 85 then 258, combat XP stayed disabled, and all three shared ordinary Herbs graphics.

The desired bright-blue Herbs body with bronze/gold-looking handle remains a presentation-only refinement.

## Runtime milestone

Seed `TEST153` predicted a Shield at Fire's first ordinary location. Runtime testing showed the Shield model and award behaving normally. The boot phrase for that build was `' OR 1==1 --`, independently selected from the phrase namespace. This confirms one generated location, not the full 84-location run.

## Callbacks and fixed IDs

| Callback | Decoded item | Native ID where fixed |
|---:|---|---:|
| `0x800388FC` | Potion | `0x01` |
| `0x8003898C` | Formula | `0x02` |
| `0x8003895C` | Eye | `0x03` |
| `0x800389BC` | Herbs | `0x04` |
| `0x800389EC` | Health urn | `0x05` |
| `0x8003892C` | Shield | `0x06` |
| `0x80038A1C` | Extra life | non-inventory lifecycle effect |
| `0x80038A58` | Mana | native mana behavior |
| `0x80038A90` | Strength urn | `0x0B` |
| `0x80038770` | Key/crystal | stage and parameter dependent |
| `0x800490CC` | Shinnok Amulet | `0x23`; separate special path |

## Cross-stage import proof

A pickup's `+0x24` is stage-local, so copying a Prison identity into Fire initially produced no usable item. The successful proof relocated and expanded Fire's resource file, appended a Prison-key bundle under Fire slot 5, and used a dedicated callback to award item `0x1A`. It rendered and awarded correctly. This proves that cross-stage items are feasible only as a coordinated resource, callback, file-table, storage, and arena operation.

Production does not yet have a resource-import planner. Global item pooling remains disabled. See [ROM and resource map](ROM-Overlay-and-Resource-Map) and the per-stage catalogs.

## Explicit exclusions

- Temple Map and other scripted/special actors.
- Boss or cutscene rewards.
- Cross-stage resource imports.
- Legacy Lua substitutions such as replacing native mana with Herbs.
- Treating empty logical slots as storage.


## Legacy Lua global-randomizer reference

The legacy `MKMSZR - 1.1.lua` already contained a true global shuffle design:

1. build one flat list of locations across all eight stages;
2. collect one flat item multiset;
3. replace nine Herbs entries with progression Power Upgrades;
4. Fisher-Yates shuffle the full item list;
5. assign it back across stages;
6. repeatedly collect every currently accessible location until no new location opens;
7. accept the seed only if the resulting simulated inventory satisfies the final win condition.

That is the correct high-level shape for 1.0, but it must **not** be ported literally. The Lua location-access rules differ from the current researched catalogs, some stock Mana entries were intentionally represented as Herbs, and the Lua's final beatability check was intentionally narrow. Current Wiki catalogs/requirements own the native 1.0 logic.

The current SHA-256 deterministic RNG is preferable to Lua `math.random`; the global implementation should preserve deterministic namespace isolation while changing from stage-local to global assignment.

## 1.0 cross-stage materialization requirement

A logical item cannot be represented globally by blindly copying its native 28-byte tuple. The tuple may contain a stage-local resource selector and, for keys/crystals, an overlay-local callback.

The global generator therefore needs a destination-stage materializer:

- logical item identity and award semantics;
- destination-safe callback;
- destination-local resource slot;
- presentation descriptor/collision data;
- imported resource bundle when the destination does not already contain it.

The runtime-confirmed Fire foreign Prison-key proof establishes that this architecture is feasible. A production planner must generalize it with guarded storage, relocation/expansion, file-table updates, deduplication, and allocation bounds.


## 1.0 deterministic retry requirement

The legacy Lua had a retry/reseeding bug: when an attempted global layout was rejected as unwinnable, later attempts were not guaranteed to regenerate identically from the same displayed seed.

The native 1.0 generator must make retry state explicit and deterministic. A recommended contract is:

```text
candidate = H(namespace || user_seed || attempt_index || counter)
```

The solver tests attempt 0, then 1, then 2, and so on until one is accepted. The accepted attempt number is therefore a pure function of the user seed and game rules. Regenerating the same seed under the same randomizer version/rules must reproduce the identical final layout even when multiple rejected candidates precede it.

The attempt index must not be advanced by unrelated RNG namespaces such as boot phrases, palette selection, HUD flavor text, or required-Power-Upgrades generation.

## Required Power Upgrades

1.0 retains the legacy concept of a seed-specific required number of progression rewards. This value must be generated deterministically from its own RNG namespace and displayed by the randomizer HUD.
2. The value must be incorporated into whole-run solvability validation: the accepted global layout must make at least that many progression rewards reachable before the completion condition.
3. The exact allowed range/policy should be finalized with the global solver, but it must not depend on how many candidate layouts were rejected.

## Temple Map as a possible 85th check

The Map is not one of the 84 ordinary records and currently couples several native behaviors. Before including it in the global pool, resolve two separate concerns:

- **reward versus trigger:** determine whether the Map inventory award can be decoupled from the Temple elevator/exit-opening event, so shuffling the logical Map item does not make Temple incompletable;
- **cross-stage persistence:** stock behavior removes the Map on Temple -> Wind. If the Map becomes a true randomized inventory item, that removal must be suppressed or replaced by explicit randomizer lifecycle handling.

Until those are proven, the global solver should model the Map separately rather than pretending it is an ordinary 0x30-byte pickup.


## Exact cross-stage visual materialization requirement

**Required for 1.0.**

A randomized pickup must visually represent the item it actually awards. A Fire Potion location that contains a Prison key must look like the Prison key, not like a Potion.

The logical-item catalog remains useful for global shuffle/solver semantics, but physical materialization must carry the randomized item's actual visual identity into the destination stage:

- source item type/behavior where required for correct pickup presentation;
- source extents/collision dimensions;
- source presentation descriptor;
- the source item's resource/model bundle, remapped into a destination-local selector;
- destination-safe award callback/parameter semantics.

Because `+0x24` is stage-local, the source selector cannot simply be copied. The destination stage must already contain an equivalent resource or receive an imported copy of the source bundle under a safe destination-local selector.

The runtime-confirmed Fire foreign Prison-key proof is the architectural precedent: Fire's resource file was relocated/expanded, the Prison-key bundle was appended and assigned to a Fire selector, and the pickup then rendered as the Prison key and awarded the Prison key.

For 1.0, that mechanism must be generalized across the complete randomized item pool with explicit allocation, deduplication, file-table updates, bounds checks, destination selector planning, and runtime validation.

A temporary experiment that keeps the destination graphics while awarding a different logical item is **Rejected for 1.0** because it violates the randomizer's visual-identity requirement. It should not be used as the production materialization path.
