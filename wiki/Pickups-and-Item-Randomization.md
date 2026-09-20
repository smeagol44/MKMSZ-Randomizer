# Pickups and item randomization

## Native record model

All eight main stages use ordinary `0x30`-byte records. The production catalog contains exactly 84. The movable identity is the seven-word slice `+0x10..+0x2B`: type, callback parameter, callback, two extents, stage-local resource slot, and presentation descriptor. Position/metadata `+0x00..+0x0F` and collected flag `+0x2C` remain attached to the location.

Same-stage Fire Potion-to-Herbs testing established why the entire identity must move: callback changes the award, while type/resource/presentation fields control visible and collision behavior. Copying the complete tuple produced correct Herbs behavior and art at the Potion location.

## Production shuffle

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

## Progression-reward overlay

After the ordinary layout is accepted, production derives Herbs candidates from that exact generated assignment and selects exactly nine with a separate SHA-256 Fisher–Yates domain:

```text
MKMSZR:PROGRESSION:HERBS:V1\0
```

Only the callback word of each chosen generated Herbs identity is changed. Type, collision, stage-local resource selector and presentation remain Herbs. This keeps the ordinary shuffle byte-for-byte independent and avoids foreign-resource imports. Progression acquisition state is also separate from the 84 ordinary-pickup persistence bits.

The initial production visual is therefore ordinary Herbs. Bright-blue-with-bronze-handle presentation is a pending visual-only refinement.

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
