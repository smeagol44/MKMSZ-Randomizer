> **Mirror notice:** This Wiki is a navigation-friendly adaptation of MKMSZR documentation. The ChatGPT Library folder `MKMSZR Research` remains the reverse-engineering/research source of truth; this repository remains the implementation/product source of truth. If the Wiki conflicts with an owning source, the owning source wins.

# Pickups and Item Randomization

## Native ordinary pickup record

Ordinary pickups use 0x30-byte stage records.

| Offset | Meaning |
|---:|---|
| `+0x00..+0x0F` | world position / destination metadata |
| `+0x10` | behavior/type |
| `+0x14` | callback parameter / flags |
| `+0x18` | native award callback |
| `+0x1C` | extent A |
| `+0x20` | extent B |
| `+0x24` | **stage-local resource selector** |
| `+0x28` | presentation descriptor |
| `+0x2C` | collected flag |

The complete movable native item identity is `+0x10..+0x2B`.

## Ordinary catalog

| Stage | Locations |
|---|---:|
| Temple | 4 |
| Wind | 6 |
| Water | 9 |
| Earth | 20 |
| Prison | 10 |
| Fire | 16 |
| Bridge | 10 |
| Fortress | 9 |
| **Total** | **84** |

The scripted Temple Map and other scripted/special mechanisms are outside this catalog.

## Runtime-confirmed resource facts

- Native callback substitution changes the actual awarded item.
- Same-stage Fire Potion -> Herbs works when compatible native fields move together.
- Cross-stage item import is possible when the foreign resource is explicitly resident.
- Empty logical selectors do not imply physical storage.
- `+0x24` is stage-local.

## v0.18 seeded native randomization

PR #16 introduced the first production native item randomizer.

It:

- processes all 84 ordinary locations;
- preserves each destination's position/metadata and collected flag;
- shuffles the complete `+0x10..+0x2B` tuple;
- keeps each stage's native resource pool within that stage;
- uses domain `MKMSZR:PICKUPS:STAGE-LOCAL:V1`;
- guards all researched clean tuples before writing;
- preserves stage item-pool multisets.

The generator ports the legacy Lua access model for Wind, Earth, Water and Prison. Candidate layouts that fail the model are rejected deterministically. CI checks 250 generated seeds across all eight stages.

## First generated-layout runtime proof

Seed:

`TEST153`

Expected Fire first ordinary location:

`Shield`

Manual result:

- Fire's first ordinary pickup was visibly a Shield;
- collecting/encountering the generated location behaved as expected;
- the same seed also produced the expected boot phrase `' OR 1==1 --`;
- that punctuation-heavy phrase rendered correctly in the native boot font.

This is the first runtime confirmation that the production seeded pickup generator changes a real native pickup as designed.

**Validation boundary:** one generated Fire location is confirmed. A complete seeded run and broader arbitrary-layout coverage remain pending.

## Native-vs-Lua difference

The old Lua randomizer substituted Herbs for some native mana pickups. The native ROM randomizer preserves real native mana tuples.

## Next frontier

Global cross-stage placement needs a production resource planner that can load/reuse foreign presentation resources safely and deterministically.
