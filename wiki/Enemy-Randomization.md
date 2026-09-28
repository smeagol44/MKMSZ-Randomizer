# Enemy randomization

Enemy randomization is research/proof work, not part of the production patch pipeline.

## Ordinary-enemy architecture

```text
stage stream -> 0x80071500 -> 0x800719F0 -> 0x80071B20 -> 0x8002FCDC
```

The current stage publishes a command-stream pointer at `0x800C11E4`. Process `0x70` interprets it. Spawn records supply coordinates, type, quota, and activation mode; the shared constructor resolves a resource pointer and type-relative descriptor before allocating the fighter. Exact record fields are in [Data structures and encodings](Data-Structures-and-Encodings).

## Stream registry

| Stage/branch | Stream |
|---|---:|
| Temple | `0x800B2D40` |
| Earth | `0x800B2EB8` |
| Water | `0x800B2F9C` |
| Wind ordinary (`state != 9`) | `0x800B30E4` |
| Fortress ordinary (`state < 8`) | `0x800B33A8` |
| Prison | `0x800B361C` |
| Fire ordinary (`state != 5`) | `0x800B3890` |
| Fire alternate/boss-like (`state == 5`) | `0x800B3A54` |
| Bridge | `0x800B3A7C` |
| Fortress alternate (`state >= 8`) | `0x800B3C88` |

Representative ordinary types include Water `0x1A/0x05`, Fire `0x0A/0x09`, and Prison `0x15/0x0E/0x11/0x16/0x14`.

## Constructor resource tables

`0x80071B20` indexes the four-byte resource-pointer-slot table at `0x800B14C0`; `0x8002FCDC` separately indexes descriptor offsets at `0x800B13D0` and stores type at actor `+0x78`.

| Type | Resource-pointer slot | Descriptor offset | Native file |
|---:|---:|---:|---:|
| `0x01` | `0x801AE46C` | `0x22AD8` | `0x89` Temple monk |
| `0x09` | `0x801AE578` | `0x2C084` | `0x25` |
| `0x0A` | `0x800C2560` | `0x20FC8` | `0x20` |

Changing a type is safe only when the expected resource slot is resident and its supporting behavior/presentation is compatible.

## Runtime proofs

The first ordinary Fire type halfword is RAM `0x800B38AA` / ROM `0xB44AA`. Guarded `0x000A -> 0x0009` succeeded: the replacement spawned and normal Fire continued.

The same record changed to type `0x01` originally froze because Fire left slot `0x801AE46C` null. A bounded import proof loaded Temple file `0x89`, populated that slot, and replaced Fire's native type-`0x0A` allocation/file-`0x20` path rather than adding past the arena limit. The imported monk rendered, moved, fought, and was killable. The fighter-only proof lacked normal death/despawn presentation. In a later bounded proof, Temple current-stage resource selector `10` was also materialized in Fire; the user confirmed correct death animation and despawn on the tested route.

This establishes cross-stage fighter residency, construction, and one tested terminal route, not arbitrary roster compatibility.

## Boss and special exclusions

- Wind state 9 directly constructs type `0x08` with fixed coordinates and process ID `0x71`.
- Water boss directly constructs type `0x0B` with fixed coordinates/process ID.
- Earth boss `0x802EDF50` uses custom allocation and explicitly stores type `0x19`.
- Fire state 5 uses dedicated one-spawn stream `0x800B3A54`, type `0x0C`.
- Fortress alternate state uses `0x800B3C88`, types `0x1B/0x1D`, with dedicated resources.

These are not members of an ordinary-enemy pool. Boss randomization needs per-encounter work.

## Rejected candidates

`0x80002DA8/0x80037CD0` are graphics/resource registration; `0x800366B4/0x80036964` and file `0x87` are moving geometry; `0x80064788` is geometry/camera work; `0x8005EF5C` is an effects/render constructor; `0x8002EC78/0x8002ECF4` are player construction.

## Production requirements

A production planner needs deterministic seed integration, stage/branch classification, allowed-type pools, resource-file import/allocation, arena budgets, constructor and auxiliary presentation dependencies, death/despawn validation, and explicit boss exclusion. The current proof is beta feasibility, not a ready patch module.


## Ordinary-enemy compatibility matrix — static pass v01 (2026-09-27)

This pass is **Static-confirmed** from the supported clean N64 USA Rev. 0 ROM plus the already-established constructor/resource model. No ROM was built and no emulator was run.

The purpose of this matrix is narrower than a final randomizer allow-list. It answers two questions first:

1. which fighter types actually occur in each main stage's ordinary branch; and
2. for a foreign type, whether the destination stage already has every required fighter resource resident in the exact constructor slot.

A native/resident cell is **not** automatically a pairwise runtime-substitution approval. Encounter role, auxiliary presentation, death/despawn behavior, and mixed-roster arena pressure remain separate gates.

### Complete ordinary-branch roster

The eight main ordinary streams contain **104 spawn commands and 19 distinct fighter types**:

| Stage | Ordinary-branch spawn records |
|---|---|
| Temple | `0x01` ×3, `0x02` ×5, `0x12` ×1 |
| Earth | `0x00` ×8 |
| Water | `0x05` ×4, `0x1A` ×5 |
| Wind | `0x03` ×17 |
| Fortress | `0x0D` ×1, `0x0E` ×6, `0x0F` ×7, `0x13` ×1, `0x1C` ×1 |
| Prison | `0x0E` ×2, `0x11` ×1, `0x14` ×3, `0x15` ×8, `0x16` ×6 |
| Fire | `0x09` ×5, `0x0A` ×7 |
| Bridge | `0x14` ×7, `0x17` ×6 |

These are stream records, not a count of simultaneously live enemies. Quotas, activation modes, and opcode semantics remain attached to the destination encounter and are not part of the type swap.

Singleton entries (`0x12` in Temple; `0x0D/0x13/0x1C` in Fortress; `0x11` in Prison) must receive an encounter-role audit before they are admitted to a general ordinary pool. Their presence in an ordinary-branch stream is resource-residency evidence, not proof that they are semantically interchangeable with repeated grunts.

All five singleton records use the gated opcode-`6` form, each with quota `1`:

| Stage | Type | Stream ROM record | Gate mask | Raw XYZ | Activation |
|---|---:|---:|---:|---|---:|
| Temple | `0x12` | `0xB3A94` | `0x08` | `0x1B7F, -0x783, 0` | `1` |
| Fortress | `0x0D` | `0xB3FBC` | `0x01` | `0x97, 0x540, 0` | `0` |
| Fortress | `0x13` | `0xB3FE8` | `0x02` | `-0x145C, 0xA80, 0` | `0` |
| Fortress | `0x1C` | `0xB4014` | `0x04` | `-0x463B, 0xFC0, 0` | `0` |
| Prison | `0x11` | `0xB436C` | `0x20` | `-0x4B00, -0xC0, 0` | `0` |

The follow-up static trace resolves the encounter ownership far enough to remove these five records from the general ordinary pool:

- The clean Test Characters table/name table maps type `0x12` to **SCORPION**, type `0x11` to **UNDEAD SCORP**, and Fortress types `0x0D/0x1C/0x13` to **ASSASSIN1/ASSASSIN2/ASSASSIN3** respectively. The same table also confirms the ordinary grunt family names used below.
- Temple overlay file `0xA0` owns a dedicated progression path that ORs `0x08` into `0x802C1140` at VA `0x802ED01C..24` / ROM `0xCA6FC..704`. That bit exactly matches the singleton SCORPION record's opcode-6 mask `0x08`. This is a dedicated gated Scorpion encounter, not a generic monk slot.
- Prison overlay file `0x9F` has a selector-`5` path that conditionally writes `0x20` to `0x802C1140` at VA `0x802EDEA4` / ROM `0xC5CE4` (otherwise it clears the word). That bit exactly matches the singleton UNDEAD SCORP record's mask `0x20`. The condition comes from save-backed state `0x8009A8CC`; its higher-level gameplay label remains unresolved, but the gate ownership is stage-specific and special.
- Fortress overlay file `0x9E` resolves the three singleton assassins completely. Its three-entry encounter table at VA `0x802F15C4` / ROM `0xC4AC4` selects, by encounter index `s4=0,1,2`, files/slots for type `0x0D` ASSASSIN1, type `0x13` ASSASSIN3, and type `0x1C` ASSASSIN2. The manager seeds `s5=1` and writes `1 << s4` to `0x802C1140` at VA `0x802F03B4..BC`, producing exactly masks `1,2,4`.
- The same Fortress manager computes `s4 * 0x30` and directly updates the first three Fortress pickup records at `0x802F1334 + s4*0x30`: it copies the defeated actor's X coordinate into record `+0x00` and clears bit `0x8000` from record `+0x14` at VA `0x802F043C..046C` / ROM `0xC393C..C396C`. Those records are the already-established Kia, Jataaka, and Sareena defeat-reward locations. Therefore the exact static association is **ASSASSIN1 / type 0x0D -> Kia**, **ASSASSIN3 / type 0x13 -> Jataaka**, and **ASSASSIN2 / type 0x1C -> Sareena**.

These five stream records are mechanically dispatched by the ordinary interpreter, but they are **special encounter records embedded in the ordinary-branch streams**, not general grunt-pool members. They are excluded from the first enemy-randomization pool.

### Static fighter-type names relevant to the ordinary pool

The clean N64 Test Characters records at VA `0x8009AC28` and their adjacent name table provide a direct type/name mapping. Type `0x00` MONK1 is the separately handled Earth entry; the 24 table records then align with names MONK2 through SHINNOK.

For the 19 ordinary-branch types in this matrix:

| Type | Static name | Pool classification |
|---:|---|---|
| `0x00` | MONK1 | repeated ordinary candidate (Earth) |
| `0x01` | MONK2 | repeated ordinary candidate (Temple) |
| `0x02` | MONK3 | repeated ordinary candidate (Temple) |
| `0x03` | MONK4 | repeated ordinary candidate (Wind) |
| `0x05` | MONK6 | repeated ordinary candidate (Water) |
| `0x09` | HULK MONK | repeated ordinary candidate (Fire) |
| `0x0A` | FAST MONK | repeated ordinary candidate (Fire) |
| `0x0D` | ASSASSIN1 / Kia | **special singleton — excluded** |
| `0x0E` | GRUNT1 | repeated ordinary candidate (Fortress/Prison) |
| `0x0F` | GRUNT2 | repeated ordinary candidate (Fortress) |
| `0x11` | UNDEAD SCORP | **special singleton — excluded** |
| `0x12` | SCORPION | **special singleton — excluded** |
| `0x13` | ASSASSIN3 / Jataaka | **special singleton — excluded** |
| `0x14` | PRIS GRUNT1 | repeated ordinary candidate (Prison/Bridge) |
| `0x15` | PRIS GRUNT2 | repeated ordinary candidate (Prison) |
| `0x16` | PRIS GRUNT3 | repeated ordinary candidate (Prison) |
| `0x17` | PRIS GRUNT4 | repeated ordinary candidate (Bridge) |
| `0x1A` | MONK5 | repeated ordinary candidate (Water) |
| `0x1C` | ASSASSIN2 / Sareena | **special singleton — excluded** |

“Repeated ordinary candidate” is a **static pool-candidate classification**, not pairwise runtime approval. Resource residency is native in the listed stage(s), but encounter behavior, death/despawn presentation and every destination-type pairing have not been exhaustively runtime-tested.

### Constructor resource bundles

The constructor's type-indexed slot and descriptor tables, combined with the normal/test-character load records, resolve the following bundles. Type `0x00`, which is outside that debug record block, is independently resolved by the Earth load path: file `0x88` is loaded into slot `0x801AE470`.

| Type | Native ordinary branch(es) | Resource-pointer slot | Descriptor offset | Primary file | Secondary dependency | Full raw bundle |
|---:|---|---:|---:|---:|---:|---:|
| `0x00` | Earth | `0x801AE470` | `0x2239C` | `0x88` / `0x225B0` | — | `0x225B0` (137.4 KiB) |
| `0x01` | Temple | `0x801AE46C` | `0x22AD8` | `0x89` / `0x22BF0` | — | `0x22BF0` (139.0 KiB) |
| `0x02` | Temple | `0x800C11B8` | `0xB3F8` | `0x8A` / `0xB510` | `0x89` → `0x801AE46C` | `0x2E100` (184.2 KiB) |
| `0x03` | Wind | `0x802E7DF0` | `0x14DCC` | `0x8B` / `0x14EE0` | — | `0x14EE0` (83.7 KiB) |
| `0x05` | Water | `0x802E7268` | `0xA264` | `0x8D` / `0xA370` | `0x8C` → `0x801114C0` | `0x284D0` (161.2 KiB) |
| `0x09` | Fire | `0x801AE578` | `0x2C084` | `0x25` / `0x2C210` | — | `0x2C210` (176.5 KiB) |
| `0x0A` | Fire | `0x800C2560` | `0x20FC8` | `0x20` / `0x21160` | — | `0x21160` (132.3 KiB) |
| `0x0D` | Fortress | `0x800C25B8` | `0x33EDC` | `0x1F` / `0x34030` | — | `0x34030` (208.0 KiB) |
| `0x0E` | Fortress, Prison | `0x802E7DC4` | `0x25454` | `0x22` / `0x255E0` | — | `0x255E0` (149.5 KiB) |
| `0x0F` | Fortress | `0x802E83E4` | `0x1C6AC` | `0x23` / `0x1C7C0` | `0x22` → `0x802E7DC4` | `0x41DA0` (263.4 KiB) |
| `0x11` | Prison | `0x802C1998` | `0x3F92C` | `0x95` / `0x3FB10` | — | `0x3FB10` (254.8 KiB) |
| `0x12` | Temple | `0x802E6E48` | `0x458CC` | `0x87` / `0x459E0` | — | `0x459E0` (278.5 KiB) |
| `0x13` | Fortress | `0x800C255C` | `0x3AE00` | `0x1D` / `0x3AFD0` | — | `0x3AFD0` (236.0 KiB) |
| `0x14` | Prison, Bridge | `0x80111528` | `0x1FA7C` | `0x8E` / `0x1FC10` | — | `0x1FC10` (127.0 KiB) |
| `0x15` | Prison | `0x80112008` | `0x1B7DC` | `0x8F` / `0x1B910` | `0x8E` → `0x80111528` | `0x3B520` (237.3 KiB) |
| `0x16` | Prison | `0x802C0FA0` | `0x1C418` | `0x90` / `0x1C550` | `0x8E` → `0x80111528` | `0x3C160` (240.3 KiB) |
| `0x17` | Bridge | `0x80111ED0` | `0x1306C` | `0x91` / `0x131A0` | `0x8E` → `0x80111528` | `0x32DB0` (203.4 KiB) |
| `0x1A` | Water | `0x801114C0` | `0x1E050` | `0x8C` / `0x1E160` | — | `0x1E160` (120.3 KiB) |
| `0x1C` | Fortress | `0x801AE714` | `0x372F8` | `0x1C` / `0x37400` | — | `0x37400` (221.0 KiB) |

The secondary dependencies explain the stock paired families already visible in the streams: `0x02 -> 0x01`'s file `0x89`, `0x05 -> 0x1A`'s file `0x8C`, `0x0F -> 0x0E`'s file `0x22`, and `0x15/0x16/0x17 -> 0x14`'s file `0x8E`.

### Stage × type residency matrix

Legend:

- **N** — native in the destination ordinary branch; exact constructor resource slot(s) are stock-resident there.
- **P** — cross-stage import is Runtime-confirmed for construction/combat and, after separate selector-`10` materialization, normal death/despawn on the tested route. Other routes remain untested.
- **I** — at least one required resource/slot is absent from the destination's native ordinary bundle; explicit import/materialization is required and compatibility is still Pending.

| Stage | `00` | `01` | `02` | `03` | `05` | `09` | `0A` | `0D` | `0E` | `0F` | `11` | `12` | `13` | `14` | `15` | `16` | `17` | `1A` | `1C` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Temple | I | N | N | I | I | I | I | I | I | I | I | N | I | I | I | I | I | I | I |
| Earth | N | I | I | I | I | I | I | I | I | I | I | I | I | I | I | I | I | I | I |
| Water | I | I | I | I | N | I | I | I | I | I | I | I | I | I | I | I | I | N | I |
| Wind | I | I | I | N | I | I | I | I | I | I | I | I | I | I | I | I | I | I | I |
| Fortress | I | I | I | I | I | I | I | N | N | N | I | I | N | I | I | I | I | I | N |
| Prison | I | I | I | I | I | I | I | I | N | I | N | I | I | N | N | N | I | I | I |
| Fire | I | **P** | I | I | I | N | N | I | I | I | I | I | I | I | I | I | I | I | I |
| Bridge | I | I | I | I | I | I | I | I | I | I | I | I | I | N | I | I | N | I | I |

There are **no non-native N cells** in this first pass: every foreign type is missing at least one exact resource-file/slot pair in the destination's native ordinary bundle. The only cross-stage exception with runtime evidence is Fire × `0x01`: file `0x89` at `0x801AE46C` proved construction/combat, and a subsequent proof also materializing Temple stage-resource selector `10` proved normal death/despawn on the tested route.

### Immediate planner consequence

A production enemy planner cannot treat the current arena tail as a generic additive fighter cache. The smallest foreign raw bundle in this matrix is type `0x03` at `0x14EE0` (83.7 KiB), while the current 16 KiB-reservation profiler's strongest global bounded headroom observation is only `0x75A8` (29.41 KiB). The historical Fire proof already demonstrated the same failure mode concretely: appending type-`0x01` file `0x89` crossed the arena boundary by `0x3098`.

Therefore the production compatibility problem splits cleanly into:

1. **same-stage/native-resource substitutions** — no new fighter-file allocation;
2. **cross-stage imports** — require replacement, compact/rebased storage, deduplicated composition, or an independently proven load/unload policy; simple additive full-file loading is not a production-safe general strategy;
3. **lifecycle compatibility** — death/despawn and auxiliary presentation must still be proven even after construction/resource residency succeeds.

The recently reclaimed high-ROM space from compact Rainbow helps ROM packaging, but it does not change this RDRAM arena constraint.

### Excluded special routes

This matrix intentionally excludes the existing special/boss paths: auxiliary hardcoded type `0x07`, Wind boss type `0x08`, Water boss type `0x0B`, Fire state-5 type `0x0C`, Earth custom boss type `0x19`, and Fortress alternate types `0x1B/0x1D`. Those remain per-encounter work and are not ordinary-pool candidates.

### Conservative first ordinary pool

With the singleton trace resolved, the static first-pool candidates are:

- Temple: `0x01 MONK2`, `0x02 MONK3`
- Earth: `0x00 MONK1`
- Water: `0x05 MONK6`, `0x1A MONK5`
- Wind: `0x03 MONK4`
- Fortress: `0x0E GRUNT1`, `0x0F GRUNT2`
- Prison: `0x0E GRUNT1`, `0x14 PRIS GRUNT1`, `0x15 PRIS GRUNT2`, `0x16 PRIS GRUNT3`
- Fire: `0x09 HULK MONK`, `0x0A FAST MONK`
- Bridge: `0x14 PRIS GRUNT1`, `0x17 PRIS GRUNT4`

This is the smallest conservative **same-stage** roster because every listed type is repeated in its native ordinary branch and its complete constructor resource bundle is already resident there. It does not yet authorize arbitrary pairwise substitution; Fire `0x0A -> 0x09` remains the only direct type-swap Runtime confirmation.

### Next matrix pass

The next gate is a per-type terminal-presentation and callback trace, followed by bounded composition proofs. Do not generalize the Fire × MONK2 result to other types or assume the stage-local selector number itself is portable.

## Auxiliary presentation pass — bounded evidence (2026-09-27)

The user reports **Runtime-confirmed, bounded** Fire × MONK2 normal death animation/despawn after materializing Temple current-stage selector `10` alongside fighter file `0x89` in slot `0x801AE46C`. The earlier fighter-only proof is its negative control. The exact new proof file, selector repointing, and route hash were not supplied with this report.

The clean-ROM stage files establish an asset relationship. Temple resource file (ROM `0x513710`, relative `0xADF4..0xCD5F`) and Water resource file (ROM `0x611780`, relative `0x4508..0x6473`) each have a six-record selector-`10` list. Their six contiguous compressed image payloads (`0x1ED8` bytes) are **byte-identical**; the preceding `0x94` bytes of list/record pointers differ and must be rebased. The full embedded closure spans `0x1F6C` bytes before destination placement. Wind selector `10` has six external IDs `0x37A..0x37F` with matching dimensions/anchors; pixel identity and destination cache availability remain unproved. Earth selector `10` aliases other selectors, Prison selector `10` is a different eight-frame bundle, and Fire/Bridge selector `10` are empty. Thus **selector number 10 is not a globally portable death resource**. Temple/Water payloads can be deduplicated byte for byte if both are needed in one destination and their relative pointers are rebuilt. Identical data alone does not prove a fighter's terminal callback consumes it.

The table records confirmed dependencies and distinguishes candidate assets from traced callbacks. A dash means **unresolved**, not no auxiliary dependency. Constructor slots, descriptor offsets, and full file sizes remain in the matrix above.

| Fighter type | Native ordinary stage | Fighter bundle | Terminal-presentation dependency | Shared/family/stage-specific | Evidence |
|---|---|---|---|---|---|
| `00` MONK1 | Earth | `88` | —; Earth selector `10` differs | unresolved | Static stage table; callback pending |
| `01` MONK2 | Temple | `89` | Temple selector `10` six-frame closure in tested Fire import | monk-family candidate, stage-local selector | Runtime-confirmed bounded Fire route; static Temple/Water payload |
| `02` MONK3 | Temple | `8A` + `89` | —; Temple selector `10` native | monk-family candidate | Static residency; callback pending |
| `03` MONK4 | Wind | `8B` | —; Wind selector `10` six external records | monk-family candidate, cache-dependent | Static form/geometry; callback/pixels pending |
| `05` MONK6 | Water | `8D` + `8C` | Water selector `10` on the normal terminal branch | stage-local selector, same payload as Temple | Static terminal dispatcher `0x80056F80..0x80057060` / `0x80053DA8`; runtime pending |
| `09` HULK MONK | Fire | `25` | —; Fire selector `10` empty | Fire native route | Static stage table; callback pending |
| `0A` FAST MONK | Fire | `20` | —; Fire selector `10` empty | Fire native route | Static stage table; callback pending |
| `0E` GRUNT1 | Fortress, Prison | `22` | File `22` palette source `+0x2555C`, animation root `0x32` / six frames inside `22` on the normal terminal branch | fighter-specific, no selector `10` on this branch | Static `0x80053E8C`; runtime pending |
| `0F` GRUNT2 | Fortress | `23` + `22` | **In Water:** resident Water selector `10` on the normal terminal branch; native Fortress stage-ID-`9` branch differs | stage-specific dispatcher; Water shares monk terminal payload | Static `0x80056F80..0x80057060` / `0x80053DA8`; runtime pending |
| `14` PRIS GRUNT1 | Prison, Bridge | `8E` | —; Bridge selector `10` empty | family/stage-specific unresolved | Static dual-stage residency; callback pending |
| `15` PRIS GRUNT2 | Prison | `8F` + `8E` | — | prison-grunt family candidate | Static bundle; callback pending |
| `16` PRIS GRUNT3 | Prison | `90` + `8E` | — | prison-grunt family candidate | Static bundle; callback pending |
| `17` PRIS GRUNT4 | Bridge | `91` + `8E` | —; Bridge selector `10` empty | prison-grunt family candidate | Static bundle; callback pending |
| `1A` MONK5 | Water | `8C` | Water selector `10` on the normal terminal branch | stage-local selector, same payload as Temple | Static terminal dispatcher `0x80056F80..0x80057060` / `0x80053DA8`; runtime pending |

**Water MONK5/MONK6 → GRUNT1/GRUNT2 sizing.** Native Water files `8C` (`0x1E160`) and `8D` (`0xA370`) total `0x284D0`. Replacement files `22` (`0x255E0`) and `23` (`0x1C7C0`) total `0x41DA0`: net `0x198D0` (104,656 bytes) after removing *both* native fighters, before auxiliary presentation and allocator overhead. The Water overlay loader at ROM `0xB58B4..0xB58F8` normally allocates/loads `8C` into `0x801114C0`, then `8D` into `0x802E7268`; the grunt constructor expects `22` at `0x802E7DC4` and `23` at `0x802E83E4`. Both new files and slots must be composed together. The archived global `0x75A8` headroom observation supplied an earlier conservative `0x2FA78` pair ceiling; the subsequently supplied Water-specific peak `0x80284940` raises the *observed-route* pair ceiling to `0x34520` (details below). The normal terminal branches need no *new* stage resource in Water (details below); other death variants and different compositions remain unbounded. The complete raw-pair replacement is unsupported by either bound.

A candidate compact composition replaces the two Water fighter allocations as a pair, repacks/rebases the reachable `22`/`23` content and all terminal frames, and materializes any auxiliary closure found by callback tracing. Raw Type-5 image chunks differ in their file-relative pointers; a later normalized comparison identified one six-frame duplicate set, detailed below. Even sharing those frames and their model-1 pattern block is insufficient for the Water-observed ceiling. No *safe minimum* compact size is established yet. Resolve reachable animation/AI/death roots, base-file references, other readers of the Water native slots, composition-specific peak validity, and relocation closure before choosing a packed footprint or preparing a ROM.

### Water pair: normal terminal path and conservative footprint (2026-09-28, static only)

The permanent terminal dispatcher at `0x80056F80..0x80057060` examines actor `+0x78` and, outside native stage IDs `7`/`9`, sends `0x05 MONK6`, `0x1A MONK5`, and `0x0F GRUNT2` through `0x80053DA8`. On Water (stage ID `2`), that routine replaces actor `+0x98` with the current stage resource base from `0x802F82B8`, sets its animation cursor to `base + *(base + 0x28)` (outer selector **10**), runs the six-frame sequence, decrements the encounter count, releases the actor, and exits the process. Water file `0x75` already has selector `10` at relative `0x4508` and its entire `0x1F6C` embedded list/image closure at `0x4508..0x6473`. Therefore this **normal terminal branch** of imported GRUNT2 requires no additional stage-resource allocation in Water: it can consume the same resident selector-10 payload as both native Water monks. This is a static dispatch/data proof, not a Water × GRUNT2 runtime result or an all-death-variants claim.

Type `0x0E GRUNT1` takes the other dispatcher branch, `0x80053E8C`. It acquires the type-indexed source at `0x800B1538 + 0x0E*4 = 0x2555C` relative to file `0x22`, selects fighter animation index `0x32` through `0x8002FE54`, then performs the same count/release/process exit. File `0x22` root word `+0xC8` points to script `+0x1D0`: six frame descriptors `+0x24DFC, +0x24F30, +0x25060, +0x25180, +0x252A8, +0x25394`, followed by zero. The palette source and all six descriptors/images remain inside file `0x22` (end `+0x255E0`). This normal branch does **not** read Water selector `10`. GRUNT2 has a separate reachable type-morph route at `0x8005765C..0x800577BC`: it replaces actor `+0x98` with the file-`0x22` slot `0x802E7DC4`, stores type `0x0E`, and selects root `0`; thus `0x22` must coexist with `0x23` even when both ordinary types are imported together. Other hit/death variants and all fighter-script roots still need a complete liveness audit before any frame can be deleted.

The stock files contain 177 valid Type-5 images in `0x22` and 115 in `0x23`, each referring to its file's own two-model table (`+0x740` and `+0x474`). The second model's **3,000-byte** pattern block is byte-identical in the two files (500 six-byte patterns, in the same order). A rebased combined representation can store that block once while retaining each file's distinct first model, table metadata, script roots, palettes, and image streams; all affected model-relative and image-relative offsets must be regenerated. This is a **static deduplication candidate**, not a validated native loader format. A direct scan finds one image in `0x22` and six in `0x23` without a direct 32-bit descriptor reference before the image area (332 and 1,624 bytes respectively); computed references/other consumers remain unruled out, so none of these bytes count as safely removable yet.

For a **two-allocation** replacement, native `8C+8D` use `0x284D0` payload bytes and `22+23` use `0x41DA0`; all four sizes are eight-byte aligned, and the allocator's two eight-byte bookkeeping charges cancel. Water's normal setup loads resource file `0x75` at `0x800B47C0..0x800B47E0` before the fighter loads at `0x800B4CB4..0x800B4CF8`. In the historical Water capture where file `0x75` began at `0x802504A8`, **even ignoring every other allocation**, two later fighter payloads must end at or beyond `0x802504A8 + 0x64E0 + 0x10 + payload_sum`. The raw grunt pair's resulting lower cursor bound is `0x80298738`, **`0x7DA8` above** `0x80290990`. This is a useful Water-qualified *lower bound*, not the exact peak of the present production configuration; changes in the stage-file base/route require recalculation.

Let `P_W` be Water's peak cursor on the *same* profiler composition and route. With unchanged later allocations and no new auxiliary allocation, the payload ceiling is `0x284D0 + (0x80290990 - P_W)`. The archived all-stage profiler's global peak `0x802893E8` supplied an earlier conservative `0x2FA78` ceiling, but was **not** a Water measurement. The user subsequently supplied Water's observed peak `P_W = 0x80284940`; its `0xC050` headroom yields the Water-observed `0x34520` ceiling. The raw pair exceeds this by `0xD880`; the conditional `0x1210` duplicate saving leaves a `0x40B90` pair, still `0xC670` (50,800 bytes) too large, before rebasing metadata. The Water peak is a user-supplied runtime observation, not a new run in this static trace or a current-production worst-case guarantee. A minimum reachable compact closure remains unproved.

### GRUNT1/GRUNT2 reachable-closure follow-up (2026-09-28, Static-confirmed; compaction Pending)

**Exact required source islands on the normal Water routes.** File `22` root slot `+0xC8` (primary index `0x32`) leads to the seven-word list `[+0x1D0,+0x1EC)`: six pointers to frame records `+0x24DFC`, `+0x24F30`, `+0x25060`, `+0x25180`, `+0x252A8`, `+0x25394`, then zero. The six aligned descriptor/image extents form `[+0x24DFC,+0x25454)` (`0x658` bytes), and each image chooses model 1 in the table at `+0x740`. The terminal palette source is `[+0x2555C,+0x255E0)` (`0x84` bytes: count word and 64 halfword colors). Constructor palette/descriptor records also begin at file `22 +0x25454` and file `23 +0x1C6AC`; both must remain accessible through the type-indexed tables. GRUNT2 normal terminal presentation in Water uses existing stage-file `75` selector 10, not file `23`'s terminal frames. Its `0x000F` type-morph branch at `0x80057740..0x800577BC` replaces actor `+0x98` with the contents of slot `0x802E7DC4` (file `22`), changes actor type to `0x0E`, and selects root 0. The ordinary GRUNT2 route therefore requires file `22` resident concurrently with file `23`, even if the two pair members share stored subresources.

**One exact duplicate family, conditional on pointer rebasing.** In file `22`, model-1 pattern bytes `[+0xF14E,+0xFD06)` (`0xBB8`) equal file `23 [+0xBFFC,+0xCBB4)` byte for byte. Both model-1 records have identical remaining 100 bytes; their four-byte pattern offsets differ. File `23`'s six terminal-looking descriptors/images `[+0x1C054,+0x1C6AC)` (`0x658`) match file `22 [+0x24DFC,+0x25454)` in order, geometry, compressed bitstreams, decoded pixels, and alignment padding. Each descriptor and image carries different file-relative pointers, explaining why raw whole-chunk equality missed the match. All **six** file-`23` images use model 1; file `22`'s six listed terminal images are likewise its only model-1 images. A single rebuilt dictionary and single six-frame body could save at most `0xBB8 + 0x658 = 0x1210` compared with both raw files if *every* inbound pointer and any computed entry are safely rebased. Separate model-0 dictionaries, model tables, root tables and palettes are not thereby shared. The near-matching constructor palettes at `22+0x25454` and `23+0x1C6AC` differ at their last byte and are **not** byte-identical resources.

**Precise unresolved indirect dependency (blocks an exact live-range map).** `0x8002FE54` computes `actor+0x98 + 4*animation_index` (or `+0x104 + 4*animation_index` for secondary roots) and uses the loaded file-relative offset as an animation cursor. At `0x800321D0` / `0x80032580`, it is the **sixth** caller stack argument, not the fifth, that becomes `$s4` and selects/skips the root. The fifth argument controls rate; the earlier attribution of `0x8004E260`'s `4` and `0x80053D6C`'s `5` to fighter roots was wrong: both sites supply root `0x1E` as their sixth argument. The interpreter at `0x800304C0` follows file-relative script jumps at `0x8003058C..0x800305A4` and conditional type-selected jumps at `0x80030710..0x8003074C`; its ordinary frame reader `0x8001BDA0` makes a *second* relative dereference from each selected frame record. `0x8002E978` similarly takes the **sixth** argument for its type-specific record index at `0x800AF340 + type*4` (GRUNT1 -> `0x800B0430`, GRUNT2 -> `0x800B0508`); `$a3` controls a separate animation choice. In particular, the six duplicates in `23` lack direct earlier-word references, and `22+0x18B3C` also lacks one; this is no proof that a computed pointer cannot reach them. No animation, model-0 dictionary, palette or image range is certified dead.

Consequently the *conditional* duplicated-data-only pair would be `0x41DA0 - 0x1210 = 0x40B90` before metadata and alignment, still `0xC670` (50,800 bytes) over the Water-observed `0x34520` ceiling. This figure is **not** the smallest reachable representation or a safe patch footprint. An exact compact pair remains Pending until the specific shared reaction/action roots and computed script-entry paths are closed. No ROM build or emulator run was performed for this follow-up.

### Water GRUNT action and reaction correction (2026-09-28, static only)

The clean Rev. 0 ROM (SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`) and preserved permanent-image function inventory were read without modifying the ROM. The argument correction above follows the actual MIPS stack offsets after each callee prologue, including call delay slots.

**Action `0xE/0xF` ownership.** `0x8004D280` supplies sixth argument `0xE` to `0x8002E978` at `0x8004D2C4`; `0x8004D3A8` supplies `0xF` at `0x8004D420`. Their ordinary calls are `0x8002A510` and `0x8002A0A4` inside the class-1 player-controller dispatch `0x80028F3C`, whose actor is its controller `+0x6E0`. The other permanent calls at `0x80006634` / `0x80006588` enter through special controller setups, not the `0x80071500 -> 0x80071B20` ordinary-enemy constructor. Thus these two sites **cannot be reached by an ordinary type `0x0E/0x0F` actor on the stock Water spawn route**. This rejects `0xE/0xF` as grunt action requirements from these callers; it does not certify every other action index or an artificial actor-type override on a player process. The ten direct permanent `0x8002E978` sites include `0xE/0xF`, while `0x80033880` passes `0/1`; call-site constants alone are not a grunt reachability set.

**Shared reaction call-site inventory.** The 77 direct permanent-image calls to `0x800321D0` divide by their **sixth** argument: 32 pass `-1` and skip root selection at `0x80032270`; 37 pass root `0x1E`; and eight singleton sites pass `0` (`0x800252DC`), `0x16` (`0x8002AF4C`), `2` (`0x8002B538`), `0x1A` (`0x80041180`), `0x41` (`0x80041B4C`), `0x31` (`0x80051000`), `0x4A` (`0x80058A18`), or `0x2E` (`0x80058F74`). `0x80069968` reuses `$s0=-1` from `0x80069850` and belongs to the first group. These are syntactic call-site classifications, **not** ordinary-GRUNT reachability claims. The fifth argument is a rate, not a root: e.g. `0x8004E260` passes fifth `4`, sixth `0x1E`; `0x80053D6C` passes fifth `5`, sixth `0x1E`. `0x80032580` has no direct permanent-image call; the previously identified raw-overlay `0xA2` call (stage-ID-1 path, ROM `0xD45A8`) has fifth `2`, but its sixth argument and Water reachability must not be inferred from that value. Thirteen raw-overlay calls to `0x800321D0` also remain outside this permanent-image inventory.

**Root-alias normalization.** Clean file-table entries `0x22` and `0x23` at ROM `0xA51A8` / `0xA51B4` identify uncompressed `[0x20F900,0x234EE0)` and `[0x234EE0,0x2516A0)`. Primary root words are file-relative; identical offsets denote aliases, not independent script storage. Both files alias `0=0x27`, `1=0x28`, and `9=0xA=0xE`. File `0x22` additionally aliases `0xD=0x24`, `0x11..0x16`, `0x17=0x19`, and `0x1E=0x2A`; file `0x23` aliases `0xC=0x10`, `0x13..0x15`, and `0x16..0x1C`. File `0x22` root `0x32` points to the proven terminal list `+0x1D0`; the file `0x23` word at index `0x1E` is `+0x474`, its **model table**, not a certified playable script. Therefore the 37 shared root-`0x1E` calls cannot simply be assigned to GRUNT2. File `0x22` root `0` begins at `+0x2A8` with frame-record offsets `+0x1DA38,+0x1DCA0,+0x1DF10`; file `0x23` root `0` begins at `+0x188` with `+0x18130,+0x183AC,+0x18644`. File `0x22` root `0x1E` begins at `+0x618` with `+0x19EC8,+0x1A0EC,+0x1A2F8`. These initial words establish real two-level frame/image reads via `0x800304C0 -> 0x8001BDA0`; they do **not** close the scripts after control tokens and conditional jumps.

### `0x800328FC → 0x80053D28` process-state trace (2026-09-28, static only)

**Construction and writers.** The ordinary spawn path `0x80071500 → 0x800719F0 → 0x80071B20` creates a `0x71..0x74` process, normalizes its class to **`2..5`** (`addiu -0x6F` at `0x80071B64`; the earlier `0x6F..0x72` result was an arithmetic error), and zero-fills `process+0x638..+0x6D7` with `0x80070710` before actor construction and transfer to `0x800039AC`. This includes `+0x6B2`; the more general freelist constructor `0x8002830C` does not itself clear that field. A clean-ROM permanent-image halfword-store census at exact offset `0x6B2` found 35 direct sites. Current-process action/physics writers are `0x8002663C/26874/26AD0`, `0x80032210/32318/3254C`, `0x800325BC/32704`, `0x80033BD4/33C48/33C80`, `0x80034134/341C8/342FC`, `0x80036670`, `0x80040B4C`, `0x8004285C/42970`, `0x800435B8/43698`, `0x80044450`, `0x8004872C`, `0x800488FC`, `0x80048E44`, and `0x80059164/591DC`. The other direct sites address a specified player controller or linked process: `0x800182BC`, `0x80037618` (`current+0x644`), `0x80038640`, `0x8003D180/3D47C/3D694`, `0x80041890`, `0x8005BB54` (`current+0x640`), and `0x80069BE8`. This is a direct-store inventory, not proof that every generic callback is an ordinary-GRUNT action. The Water raw overlay is file `0xA1`, ROM `[0xB4FC0,0xBAF60)` (its fighter loader is at ROM `0xB58B4`); it has **zero** direct calls to `0x800321D0` and zero direct halfword stores to `+0x6B2`. The 13 identified raw-overlay `0x800321D0` calls instead split across Earth `0x9C` (4), Prison `0x9F` (2), Temple `0xA0` (3), and stage-ID-1 `0xA2` (4). File `0x9B`, Fire `0x9D`, and Fortress `0x9E` also have none. These are raw-file assignments, not imports into Water.

**Live flag and transfer.** `0x800321D0` explicitly clears `+0x6B2` at entry (`0x80032210`), increments it before the one-frame sleep at `0x80032318`, and clears it on return (`0x8003254C`). `0x80033BB4` and `0x800341AC` also set it to one across timed loops and clear it on ordinary exit. `0x800341AC`'s direct `0x800328FC` edge at `0x800342B4` follows a call to `0x800321D0` (which clears the flag), so that edge alone is **not** a nonzero-state proof. `0x8002B690` returns `0x8000` iff the *current process* `+0x6B2` is nonzero; `0x800328FC` then calls `0x80053D28` at `0x80032920`. Unblocked collision resolves the high byte of strike record `+0x08` through reaction table `0x800A1190` at `0x8002DF10..28`; `0x8002E078 → 0x80032CD4` replaces the victim's callback and marks reaction bit `+0x6BE:0x04` without clearing `+0x6B2`. Reaction-table entry `0` is `0x8004E530`, which calls `0x800328FC` at `0x8004E68C`. The separate callback `0x80059070` occupies reaction indices `0x3A/0x5A` and directly calls `0x80053D28` at `0x800591E0`, after clearing its own `+0x6B2`; its strike-selector availability to ordinary Water play is not established.

The raw-overlay direct `sh +0x6B2` census adds 22 sites outside Water: Earth file `0x9C` ROM `0xDCDF8,0xDDD50,0xDEC30,0xDEEA4,0xDF1B0,0xDF380,0xDF8EC,0xE0468`; Temple `0xA0` ROM `0xCB668,0xCB94C,0xCB9A0`; stage-ID-1 `0xA2` ROM `0xD51F8,0xD5B64,0xD6A68,0xD6B88,0xD6B8C,0xD6BEC,0xD6BF4,0xD7408,0xD79EC,0xD7A38,0xD7EF0`. The other stage-overlay files `0x9B/0x9D/0x9E/0x9F/0xA1` have no direct `sh +0x6B2` site. Raw opcode matches in other overlays do not establish an ordinary Water process writer.

**Morph and root.** `0x80053D28` first calls `0x80057478`; for current type `0x0F`, that helper rebinds actor `+0x98` to file `0x22`, changes type to `0x0E`, and selects root 0 before returning. The subsequent `0x800321D0` call has fifth argument `5` (rate) and sixth `0x1E` (primary root). On file `0x22`, root `0x1E` aliases root `0x2A` at script `+0x618`; its first three frame-record offsets are `+0x19EC8,+0x1A0EC,+0x1A2F8`. The earlier file-`0x23` word `0x1E=+0x474` is a model table, but it is **not** the root used by this callback after the `0x0F` morph. The focused root-`0x1E` script/frame closure below supersedes this remaining script-specific task; other roots and computed consumers remain unclosed.

**Prior stopping dependency, narrowed below.** Callback replacement can preserve victim `+0x6B2`, but a normal return from `0x800321D0` clears it. The specific `0x800328FC → 0x80053D28` handoff still needs an eligible second strike and callback schedule during the nonzero interval. The independent Slide reaction below already certifies file-`0x22` root `0x1E` as live; the handoff is no longer its sole liveness route. No further dead bytes follow from the collision trace.

### Ordinary GRUNT collision and root-`0x1E` closure (2026-09-28, static only)

**Victim ownership and gates.** The `0x8002BADC` collision core enters its ordinary-victim scan at `0x8002CAE4..0x8002CB84` after the player-target check. `0x80028510` finds a process whose `+0x6D8` class is `2`, `3`, or `4` (excluding the current attacker); ordinary spawn slots `0x71..0x73` become exactly those classes. Slot `0x74` becomes class `5` and is not selected by this three-slot scan. The victim is `$fp`, the attacker is the current `0x802ECE20` process, and global `0x802C1AC0` is the player controller. The code requires victim action `+0x6AA` other than `0x502/0x619`, nonzero health `+0x654`, actor `+0x64:0x100` clear, facing and hit geometry, and a zero result from `0x80025370`'s obstacle/zone check. Special cases at `0x8002DBB8..0x8002DCA0` concern other actor types/actions and state `0x50B` only when the player is action `0x215`; `0x8002DE48..0x8002DF0C` excludes types `0x1D`, `8`, and `0x0C`, not `0x0E/0x0F`. `0x80034964` sends guard states `0x700/0x701` to the blocked table `0x800A1290` when the guard global is clear. An ordinary alive, facing, unguarded GRUNT in a valid hitbox takes the unblocked `0x800A1190` table. Neither the tested victim gates nor `0x80025370` reads `+0x6B2` or reaction bit `+0x6BE:0x04`. At `0x8002DF28`, `0x8002E078 → 0x80032CD4` installs the selected callback and resets victim stack pointers to `victim+0x620`, leaving its `+0x6B2` intact. The next scheduler invocation of that process runs the replacement callback with the victim as current process. This is the mechanical handoff, not proof that every strike can overlap a nonzero interval.

**Concrete live reaction.** Normal type-`4` player Slide is reached through its stock action callback `0x80059FF0` (recognized at `0x8003C9F8 → 0x8003CFAC`, tier at least `2`). At `0x8005A0B8` it passes type-`4` strike-table slot `0x10`, `0x800AF614`, to `0x8002BA04`; that record's `+0x08` high byte is `0x2D`. On an unblocked hit against ordinary class-`2..4` type `0x0E/0x0F`, `0x800A1190[0x2D]=0x8004E2D4`. This callback calls `0x80057478`, so type `0x0F` morphs to `0x0E` and file `0x22` before `0x800321D0` receives sixth argument root `0x1E` at `0x8004E3CC`. It sets victim action `+0x6AA=0x50B`, but does not set actor `+0x64:0x100`; `0x800321D0` clears then increments that *victim* `+0x6B2` immediately before its sleep. Thus root `0x1E` is an ordinary Water GRUNT requirement independently of `0x80053D28`. The normal player type-`4` record at slot `0`, `0x800AF504`, separately has reaction byte `0`: `0x800A1190[0]=0x8004E530`; table index `0x19` is the same callback. Slide repeatedly presents slot `0x10`, so its own later hits do not select entry `0`.

**Exact root-`0x1E` file-`0x22` reads.** Root slots `0x1E` (`[+0x78,+0x7C)`) and alias `0x2A` (`[+0xA8,+0xAC)`) both contain `+0x618`. The script `[+0x618,+0x638)` holds seven frame-relative offsets followed by zero; it contains no control token, relative jump, or type branch. `0x800304C0` reads each offset, `0x8001BDA0` reads its frame record's second relative image offset at `frame+8`, and then the Type-5 image's relative model-table offset. All seven images resolve model `0` in file `0x22` table `+0x740` (table/header `[+0x740,+0x814)` and stock model-0 pattern region beginning `+0x814`; model `1` begins `+0xF14E`). Exact four-byte-aligned frame/descriptor/image extents, from the stock Type-5 bitstream decoder, are:

| Script word | Frame and image extent in file `0x22` | Image start | Model |
|---|---|---|---|
| `+0x618` | `[+0x19EC8,+0x1A0EC)` | `+0x19EDC` | 0 |
| `+0x61C` | `[+0x1A0EC,+0x1A2F8)` | `+0x1A100` | 0 |
| `+0x620` | `[+0x1A2F8,+0x1A4DC)` | `+0x1A30C` | 0 |
| `+0x624` | `[+0x1A4DC,+0x1A670)` | `+0x1A4F0` | 0 |
| `+0x628` | `[+0x1A670,+0x1A7E0)` | `+0x1A684` | 0 |
| `+0x62C` | `[+0x1A7E0,+0x1A968)` | `+0x1A7F4` | 0 |
| `+0x630` | `[+0x1678C,+0x16910)` | `+0x167A0` | 0 |

The six consecutive records total `0xAA0`, the seventh `0x184`, and the script `0x20`. The decoder consumed 1,165 distinct six-byte model-0 patterns (`0x1B4E` referenced bytes) scattered across the stock model-0 dictionary, with index span `0..9925`; those references cannot be dropped merely because frame bytes are retained. `0x8001BDA0` uses the actor's already acquired palette selector `+0x9E → +0x80`; this root has no separate palette-acquisition token. Constructor palette ownership, especially after a GRUNT2 morph, remains a separate existing resource requirement. The stock extents are certified live, not a proposed packed size or a certificate that unused dictionary entries can be deleted.

**Remaining `0x800328FC` edge.** A Slide hit can start `0x8004E2D4` and produce a hittable nonzero victim interval (`+0x6AA=0x50B`, actor `+0x64:0x100` clear). A subsequent eligible type-`4` strike slot `0` would install `0x8004E530`; that callback has sleeps but no flag clear before `0x8004E68C → 0x800328FC`, which would take `0x80053D28` if the inherited victim flag remained nonzero. Static code does not yet establish an ordinary Water schedule that overlaps slot `0` with the Slide-produced interval: the same player's Slide callback continues to use slot `0x10`, and normal `0x800321D0` completion clears the flag. An independent ordinary-GRUNT AI/action writer of `+0x6B2` concurrent with a player slot-`0` hit is the other specific candidate; its type-`0x0E/0x0F` dispatch and hit window remain unproved. Therefore the `0x800328FC → 0x80053D28` handoff is **Pending**, while root `0x1E` itself is **Static-confirmed live** via Slide. No further range is certified dead. The raw pair `0x41DA0` is a source-payload upper bound (and exceeds the ceiling by `0xD880`); `0x1210` sharing would *conditionally* lower that to `0x40B90`, still `0xC670` (50,800 bytes) above the Water observed-route ceiling `0x34520`, before rebasing/metadata. No tighter byte-saving bound is certified: the new seven-frame/model-0 set is live, and other roots, computed readers and safe repacking are unclosed. There is no exact minimum compact footprint. The smallest next static check is to trace ordinary type-`0x0E/0x0F` AI dispatch into one concrete nonzero `+0x6B2` writer (or bound Slide recovery against its victim loop), then prove whether a player slot-`0` collision can be scheduled before that victim clears the flag. A guarded runtime proof is premature. No ROM build or emulator was run.
