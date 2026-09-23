# Pickups and stage-local randomization

> **Scope:** This page is the canonical owner for the **current production ordinary-pickup behavior and stage-local seeded randomization**. It deliberately does not own the 1.0 cross-stage materializer, global logical shuffle, deterministic global retry contract, whole-run solver, required-Power-Upgrades policy, or Temple Map 85th-check question; those belong to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

## Current conclusion

MKMSZR currently randomizes the 84 ordinary pickup records **within each stage**. The production mode is deterministic, preserves each destination location and collected flag, moves the complete ordinary-item identity slice, and rejects stage-local layouts that violate the current modeled access requirements.

This is a real production system, but it is intentionally an **interim 1.0 mode**. The final 1.0 design requires one cross-stage logical pool plus a destination resource materializer and whole-run solvability verifier. Those are separate systems because a resource selector that is valid in one stage is not automatically meaningful in another.

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

## Current stage-local production shuffle

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

After the ordinary stage-local layout is accepted, production derives Herbs candidates from that accepted assignment and selects exactly nine using a separate SHA-256 Fisher-Yates domain:

```text
MKMSZR:PROGRESSION:HERBS:V1\0
```

Only the callback word of each selected generated Herbs identity is changed. Type, collision, stage-local resource selector, and presentation remain Herbs, so this current overlay does not require cross-stage resource import.

The progression callback advances to the next native XP threshold, evaluates the native tier at pickup acquisition, and does not insert an inventory item. Ordinary pickup persistence still records the physical location as collected. Progression count/XP are stored separately from the 84 ordinary-pickup bits.

Diagnostic A Runtime-confirmed the generated Temple pattern for seed `BCBDBF`: the first and third Herbs were progression rewards, the second Herbs remained normal, XP reached 85 then 258, combat XP stayed disabled, and all three shared ordinary Herbs graphics.

The complete progression mechanism and lifecycle evidence belong to [XP and progression](XP-and-Progression). The future seed-specific **required** Power-Upgrades target and its solver role belong to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

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
| `0x80038770` | Key/crystal | stage and parameter dependent |
| `0x800490CC` | Shinnok Amulet | `0x23`; separate special path |

This table is a pickup-domain convenience summary, not a replacement for the canonical function registry or item/key structure tables.

## Current exclusions

The current stage-local ordinary-pickup system deliberately excludes:

- the Temple Map and other scripted/special actors;
- boss or cutscene rewards;
- cross-stage resource imports/materialization;
- Shinnok's Amulet special pickup path;
- legacy Lua substitutions such as representing native Mana as Herbs;
- treating empty logical resource selectors as physical storage.

## Why global materialization is a separate system

Within one stage, the complete ordinary identity tuple can be shuffled because its resource selector remains meaningful against the same destination stage resource file. Across stages, that assumption breaks: `+0x24` is stage-local, resource bundles may be embedded or externally backed, and key/crystal award semantics may need a destination-safe path.

Therefore the current stage-local shuffle owns **which same-stage identity goes to which ordinary location**. The 1.0 global system must separately own **which logical item goes to which stage and how that item is physically materialized there**, including resource import, extension selectors, deduplication, destination-safe awards, deterministic global retries, and whole-run solvability.

See [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) for that canonical design/proof history. Underlying loader/resource grammar remains in [ROM, overlay, and resource map](ROM-Overlay-and-Resource-Map), and concrete stage resource records remain in the [stage catalogs](Stage-Catalogs).

## Related pages

- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — 1.0 cross-stage logical pool, materializer, proofs, deterministic retry, solver, required powers, and Map question.
- [Data structures and encodings](Data-Structures-and-Encodings) — canonical ordinary-pickup record grammar.
- [Stage catalogs](Stage-Catalogs) — all 84 concrete ordinary records and stage-local resources.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence and inventory behavior.
- [XP and progression](XP-and-Progression) — current progression callback, thresholds, persistence, and runtime evidence.
- [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap) — normative release requirements and acceptance gates.
