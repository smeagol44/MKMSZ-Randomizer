# Pickups and item randomization

> **Scope:** This page is the canonical owner for the **ordinary-pickup behavior and historical stage-local seeded randomization**. It deliberately does not own the 1.0 cross-stage materializer, global logical shuffle, deterministic global retry contract, whole-run solver, required-Power-Upgrades policy, or Temple Map 85th-check question; those belong to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

## Current conclusion

PR #137 replaces the stage-local product shuffle with a deterministic **85-check global pool**, including the scripted Temple special check. The global generator, destination materializer, fixed-point solver, retry policy, and independent required-power settings belong to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability). The stage-local details below document the superseded `STAGE-LOCAL:V1` implementation and its bounded proofs.

The former stage-local product mode was an interim implementation. Its complete-tuple semantics must not be read as the global materializer contract: resource selectors are stage-local, while reward identity and destination-owned stage actions are composed separately by the current global path.

**Known Wind ownership risk (Static-confirmed, 2026-09-30):** the historical stage-local implementation moves the complete `+0x10..+0x2B` tuple, so Wind callback `0x802F2CB4` and its parameter move with the shuffled reward. The focused Wind trace now shows that callback parameters 0/1 also inject physical stage/checkpoint selector steps `3/5`, and parameter 2 writes live Wind-local state `0x802F60A0`. Therefore the complete tuple is not purely logical reward identity in Wind. A different reward placed at a stock Wind key location can remove that location's native stage-state action, while a Wind key moved elsewhere can carry that action to the wrong physical location. This is an architectural risk established by static code/implementation comparison; no claim is made that a particular production seed has runtime-failed from it. The historical stage-local system is superseded and must not be used as the template for 1.0 global award semantics.

## Ordinary pickup behavior and identity semantics

All eight main stages use ordinary `0x30`-byte records. The catalog contains exactly 84 ordinary records.

The canonical byte grammar is owned by [Data structures and encodings](Data-Structures-and-Encodings). In summary, the randomizable identity is the contiguous seven-word slice `+0x10..+0x2B`:

- type / behavior;
- callback parameter;
- native award callback;
- two collision extents;
- stage-local resource selector;
- presentation descriptor.

Position and location metadata `+0x00..+0x0F` stay attached to the destination, and the collected flag at `+0x2C` stays attached to that physical check and is persisted separately.

Same-stage Fire Potion-to-Herbs testing established why the complete identity has to move. Changing only the callback changes the award but does not fully carry presentation/collision identity. Copying the complete seven-word tuple produced correct Herbs behavior and art at the Potion location.

The concrete records, selectors, and resource instances remain canonical in the eight [stage catalogs](Stage-Catalogs); this page does not duplicate their raw tables.

### Hand-authored pickup placement probe

A bounded 2026-10-02 placement experiment established a reusable authoring workflow for intentionally placing ordinary pickups at new coordinates. The Runtime-confirmed probe reads the live player actor's raw fixed8 X/Y/Z directly from actor `+0x2C/+0x30/+0x34`. For hand-authored ordinary pickup placement, the accepted visual convention is **X = displayed player X, Z = displayed player Z, Y = displayed player Y + 28 world units = +0x1C00 fixed8**. Direct player Y put Herbs around head height; a later Wind revision was too low, so +28 is the project baseline. This is an authoring convention rather than an engine-coordinate rule and should be rechecked for models with materially different anchors.

The reusable diagnostic is `tools/build_pickup_placement_probe.py`. Full proof mechanics, rejected probe variants, and the separate post-1.0 Ice Blast -> Pickup cancel are recorded in [Pickup placement and Ice-Blast cancel proofs](Pickup-Placement-and-Action-Cancel-Proofs).

## Historical stage-local production shuffle

For each stage, the generator uses a stable SHA-256-based Fisher-Yates shuffle with domain:

```text
MKMSZR:PICKUPS:STAGE-LOCAL:V1\0
```

The deterministic input includes the user seed bytes, native stage ID, attempt number, and counter. This namespace is isolated from boot phrases, palettes, progression-reward selection, and future features. A seedless configuration leaves the pickup layout unchanged.

Candidate layouts are rejected, up to **1,000 deterministic attempts**, if the current stage-local access model cannot obtain required progression tokens before their dependent locations. This 1,000-attempt ceiling belongs only to the interim stage-local implementation; it is not the 1.0 global retry policy.

CI exercises 250 seeds and checks catalog integrity, tuple preservation, determinism, namespace isolation, and the modeled access constraints.

## Current stage-local access model

| Stage | Modeled dependencies |
|---|---|
| Temple | Four ordinary locations free; scripted Map excluded |
| Wind | fifth location requires `wind-circle`; sixth requires `wind-triangle` |
| Water | second requires `water-moon`; eighth requires `water-triangle`; ninth requires `water-three-bars` |
| Earth | first three yield Square, Four Squares, Triangle; later locations require Square or Four Squares as listed in the Earth catalog |
| Prison | staged Level 1/2/3 dependencies as listed in the Prison catalog |
| Fire, Bridge, Fortress | Current ordinary locations treated as free by the ported access model |

These rules are **Implementation/CI-confirmed** as the current stage-local model. They were ported from legacy logic and reconciled with the current catalogs, but they are not yet a complete whole-run progression graph. A representative arbitrary-seed full native playthrough remains pending.

## Progression-reward overlay in the current product

When Powers as pickups is ON, after the ordinary stage-local layout is accepted, production derives Herbs candidates from that accepted assignment and selects exactly nine using a separate SHA-256 Fisher-Yates domain. When OFF, no callbacks are converted:

```text
MKMSZR:PROGRESSION:HERBS:V1\0
```

Only the callback word of each selected generated Herbs identity is changed. Type, collision, stage-local resource selector, and presentation remain Herbs, so this current overlay does not require cross-stage resource import.

The progression callback advances to the next native XP threshold, evaluates the native tier at pickup acquisition, and does not insert an inventory item. Ordinary pickup persistence still records the physical location as collected. Progression count/XP are stored separately from the 84 ordinary-pickup bits.

Diagnostic A Runtime-confirmed the generated Temple pattern for seed `BCBDBF`: the first and third Herbs were progression rewards, the second Herbs remained normal, XP reached 85 then 258, combat XP stayed disabled, and all three shared ordinary Herbs graphics.

The complete progression mechanism and lifecycle evidence, including the build-time Powers-as-pickups choice, belong to [XP and progression](XP-and-Progression). The future mode-aware **required** Power-Upgrades target and its solver role belong to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

## Runtime evidence for the current shuffle

Seed `TEST153` predicted a Shield at Fire's first ordinary location. Runtime testing showed the Shield model and award behaving normally. The boot phrase for that build was `' OR 1==1 --`, independently selected from its own namespace.

This confirms one generated stage-local location on that build; it does **not** establish exhaustive runtime coverage for all 84 records or arbitrary layouts.

## Callback reference for current item identities

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
| `0x80038770` | Key/crystal stock award | stage and parameter dependent; key-triggered checkpoint side effect still Pending trace |
| `0x800490CC` | Shinnok Amulet | `0x23`; separate special path |

This table is a pickup-domain convenience summary, not a replacement for the canonical function registry or item/key structure tables.

## Fortress boss-reward caveat

The three Fortress crystal records correspond to rewards produced after defeating Kia, Jataaka, and Sareena. Their stock records/catalog entries describe the spawned reward, not a requirement that the global randomizer permanently bind each boss to its crystal. The 1.0 model treats the boss defeat as the reward-location trigger and the crystal as the stock logical reward; generalized spawn/materialization belongs to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

## Current exclusions

The current stage-local ordinary-pickup system deliberately excludes:

- the Temple Map and other scripted/special actors;
- boss or cutscene rewards;
- cross-stage resource imports/materialization;
- Shinnok's Amulet special pickup path;
- legacy Lua substitutions such as representing native Mana as Herbs;
- treating empty logical resource selectors as physical storage.

## Why global materialization is a separate system

Within one stage, the complete ordinary identity tuple keeps its resource selector meaningful against the same stage resource file, which is why the interim implementation can render same-stage identities. **Wind now proves that resource validity is not enough to establish behavioral ownership:** its callback/parameter words also carry stage/checkpoint state that belongs to physical Wind progression. Across stages—and for the final 1.0 same-stage semantics as well—the materializer must separate logical reward award/visual identity from destination-location state effects rather than assuming the whole tuple is movable.

Therefore the current stage-local shuffle owns **which same-stage identity goes to which ordinary location**. The 1.0 global system must separately own **which logical item goes to which stage and how that item is physically materialized there**, including resource import, extension selectors, deduplication, destination-safe awards, deterministic global retries, and whole-run solvability.

See [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) for that canonical design/proof history. Underlying loader/resource grammar remains in [ROM, overlay, and resource map](ROM-Overlay-and-Resource-Map), and concrete stage resource records remain in the [stage catalogs](Stage-Catalogs).

## Related pages

- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — 1.0 cross-stage logical pool, materializer, proofs, deterministic retry, solver, required powers, and Map question.
- [Data structures and encodings](Data-Structures-and-Encodings) — canonical ordinary-pickup record grammar.
- [Stage catalogs](Stage-Catalogs) — all 84 concrete ordinary records and stage-local resources.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and inventory behavior.
- [XP and progression](XP-and-Progression) — current progression callback, thresholds, persistence, and runtime evidence.
- [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) — normative release requirements and acceptance gates.
