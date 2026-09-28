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

**Water MONK5/MONK6 → GRUNT1/GRUNT2 sizing.** Native Water files `8C` (`0x1E160`) and `8D` (`0xA370`) total `0x284D0`. Replacement files `22` (`0x255E0`) and `23` (`0x1C7C0`) total `0x41DA0`: net `0x198D0` (104,656 bytes) after removing *both* native fighters, before auxiliary presentation and allocator overhead. The Water overlay loader at ROM `0xB58B4..0xB58F8` normally allocates/loads `8C` into `0x801114C0`, then `8D` into `0x802E7268`; the grunt constructor expects `22` at `0x802E7DC4` and `23` at `0x802E83E4`. Both new files and slots must be composed together. The `0x75A8` (30,120-byte) global bounded headroom observation is **not a Water-specific measurement**; using it conservatively for the archived profiler route caps the combined replacement payload at `0x2FA78` and leaves `0x12328` (74,536 bytes) to save or relocate. The normal terminal branches need no *new* stage resource in Water (details below); other death variants and different compositions remain unbounded. The complete raw-pair replacement is unsupported by the available arena bound.

A candidate compact composition replaces the two Water fighter allocations as a pair, repacks/rebases the reachable `22`/`23` content and all terminal frames, and materializes any auxiliary closure found by callback tracing. Raw Type-5 image chunks differ in their file-relative pointers; a later normalized comparison identified one six-frame duplicate set, detailed below. Even sharing those frames and their model-1 pattern block is insufficient for the conservative Water ceiling. No *safe minimum* compact size is established yet. Resolve reachable animation/AI/death roots, base-file references, other readers of the Water native slots, exact Water peak cursor, and relocation closure before choosing a packed footprint or preparing a ROM.

### Water pair: normal terminal path and conservative footprint (2026-09-28, static only)

The permanent terminal dispatcher at `0x80056F80..0x80057060` examines actor `+0x78` and, outside native stage IDs `7`/`9`, sends `0x05 MONK6`, `0x1A MONK5`, and `0x0F GRUNT2` through `0x80053DA8`. On Water (stage ID `2`), that routine replaces actor `+0x98` with the current stage resource base from `0x802F82B8`, sets its animation cursor to `base + *(base + 0x28)` (outer selector **10**), runs the six-frame sequence, decrements the encounter count, releases the actor, and exits the process. Water file `0x75` already has selector `10` at relative `0x4508` and its entire `0x1F6C` embedded list/image closure at `0x4508..0x6473`. Therefore this **normal terminal branch** of imported GRUNT2 requires no additional stage-resource allocation in Water: it can consume the same resident selector-10 payload as both native Water monks. This is a static dispatch/data proof, not a Water × GRUNT2 runtime result or an all-death-variants claim.

Type `0x0E GRUNT1` takes the other dispatcher branch, `0x80053E8C`. It acquires the type-indexed source at `0x800B1538 + 0x0E*4 = 0x2555C` relative to file `0x22`, selects fighter animation index `0x32` through `0x8002FE54`, then performs the same count/release/process exit. File `0x22` root word `+0xC8` points to script `+0x1D0`: six frame descriptors `+0x24DFC, +0x24F30, +0x25060, +0x25180, +0x252A8, +0x25394`, followed by zero. The palette source and all six descriptors/images remain inside file `0x22` (end `+0x255E0`). This normal branch does **not** read Water selector `10`. GRUNT2 has a separate reachable type-morph route at `0x8005765C..0x800577BC`: it replaces actor `+0x98` with the file-`0x22` slot `0x802E7DC4`, stores type `0x0E`, and selects root `0`; thus `0x22` must coexist with `0x23` even when both ordinary types are imported together. Other hit/death variants and all fighter-script roots still need a complete liveness audit before any frame can be deleted.

The stock files contain 177 valid Type-5 images in `0x22` and 115 in `0x23`, each referring to its file's own two-model table (`+0x740` and `+0x474`). The second model's **3,000-byte** pattern block is byte-identical in the two files (500 six-byte patterns, in the same order). A rebased combined representation can store that block once while retaining each file's distinct first model, table metadata, script roots, palettes, and image streams; all affected model-relative and image-relative offsets must be regenerated. This is a **static deduplication candidate**, not a validated native loader format. A direct scan finds one image in `0x22` and six in `0x23` without a direct 32-bit descriptor reference before the image area (332 and 1,624 bytes respectively); computed references/other consumers remain unruled out, so none of these bytes count as safely removable yet.

For a **two-allocation** replacement, native `8C+8D` use `0x284D0` payload bytes and `22+23` use `0x41DA0`; all four sizes are eight-byte aligned, and the allocator's two eight-byte bookkeeping charges cancel. Water's normal setup loads resource file `0x75` at `0x800B47C0..0x800B47E0` before the fighter loads at `0x800B4CB4..0x800B4CF8`. In the historical Water capture where file `0x75` began at `0x802504A8`, **even ignoring every other allocation**, two later fighter payloads must end at or beyond `0x802504A8 + 0x64E0 + 0x10 + payload_sum`. The raw grunt pair's resulting lower cursor bound is `0x80298738`, **`0x7DA8` above** `0x80290990`. This is a useful Water-qualified *lower bound*, not the exact peak of the present production configuration; changes in the stage-file base/route require recalculation.

Let `P_W` be Water's measured peak cursor on the *same* profiler composition and route. With unchanged later allocations and no new auxiliary allocation, the exact payload ceiling is `0x284D0 + (0x80290990 - P_W)`. The archived all-stage profiler records only global peak `0x802893E8`, **not** `P_W`; its route therefore supplies the conservative ceiling `0x2FA78` (`0x75A8` headroom). The raw pair exceeds that ceiling by `0x12328` (74,536 bytes); even after the one proven byte-identical 3,000-byte pattern-block reuse, `0x411E8` exceeds it by `0x11770` (71,536 bytes), before any rebasing metadata cost. This ceiling is bounded only for the archived profiler composition/route; it is not a current-production worst-case guarantee. The exact Water peak and a minimum reachable compact file closure are **not established**. A Water-qualified cursor trace or a complete static allocation/liveness proof is needed before asserting a viable footprint; do not describe the global peak as a Water measurement or build a ROM from this estimate.

### GRUNT1/GRUNT2 reachable-closure follow-up (2026-09-28, Static-confirmed; compaction Pending)

**Exact required source islands on the normal Water routes.** File `22` root slot `+0xC8` (primary index `0x32`) leads to the seven-word list `[+0x1D0,+0x1EC)`: six pointers to frame records `+0x24DFC`, `+0x24F30`, `+0x25060`, `+0x25180`, `+0x252A8`, `+0x25394`, then zero. The six aligned descriptor/image extents form `[+0x24DFC,+0x25454)` (`0x658` bytes), and each image chooses model 1 in the table at `+0x740`. The terminal palette source is `[+0x2555C,+0x255E0)` (`0x84` bytes: count word and 64 halfword colors). Constructor palette/descriptor records also begin at file `22 +0x25454` and file `23 +0x1C6AC`; both must remain accessible through the type-indexed tables. GRUNT2 normal terminal presentation in Water uses existing stage-file `75` selector 10, not file `23`'s terminal frames. Its `0x000F` type-morph branch at `0x80057740..0x800577BC` replaces actor `+0x98` with the contents of slot `0x802E7DC4` (file `22`), changes actor type to `0x0E`, and selects root 0. The ordinary GRUNT2 route therefore requires file `22` resident concurrently with file `23`, even if the two pair members share stored subresources.

**One exact duplicate family, conditional on pointer rebasing.** In file `22`, model-1 pattern bytes `[+0xF14E,+0xFD06)` (`0xBB8`) equal file `23 [+0xBFFC,+0xCBB4)` byte for byte. Both model-1 records have identical remaining 100 bytes; their four-byte pattern offsets differ. File `23`'s six terminal-looking descriptors/images `[+0x1C054,+0x1C6AC)` (`0x658`) match file `22 [+0x24DFC,+0x25454)` in order, geometry, compressed bitstreams, decoded pixels, and alignment padding. Each descriptor and image carries different file-relative pointers, explaining why raw whole-chunk equality missed the match. All **six** file-`23` images use model 1; file `22`'s six listed terminal images are likewise its only model-1 images. A single rebuilt dictionary and single six-frame body could save at most `0xBB8 + 0x658 = 0x1210` compared with both raw files if *every* inbound pointer and any computed entry are safely rebased. Separate model-0 dictionaries, model tables, root tables and palettes are not thereby shared. The near-matching constructor palettes at `22+0x25454` and `23+0x1C6AC` differ at their last byte and are **not** byte-identical resources.

**Precise unresolved indirect dependency (blocks an exact live-range map).** `0x8002FE54` computes `actor+0x98 + 4*animation_index` (or `+0x104 + 4*animation_index` for secondary roots) and uses the loaded file-relative offset as an animation cursor. Shared combat code can supply an index through `0x800321D0` at `0x80032214..0x80032298` (and its sibling `0x80032580` at `0x800325C0..0x80032630`): the **fifth stack argument** becomes `$s4`, whose low 12 bits or signed low halfword select the fighter root; its high halfword selects the secondary bank. Callers demonstrably pass different values (for example `0x8004E260` passes `4`, `0x80053D6C` passes `5`); which caller routes apply to each imported ordinary GRUNT is Pending. The interpreter at `0x800304C0` also follows file-relative script jumps at `0x8003058C..0x800305A4` and conditional type-selected jumps at `0x80030710..0x8003074C`; its ordinary frame reader `0x8001BDA0` makes a *second* relative dereference from each selected frame record. The type-specific combat record selector `0x8002E978` additionally indexes table `0x800AF340 + type*4`: GRUNT1 -> `0x800B0430`, GRUNT2 -> `0x800B0508`, using a caller-supplied action index before `0x8002BA04` dispatches the record. The Water ordinary encounter's reachable fifth-argument/action-index values and the corresponding complete jump/frame closure have **not** been exhaustively bounded. In particular, the six duplicates in `23` lack direct earlier-word references, and `22+0x18B3C` also lacks one; this is no proof that a computed pointer cannot reach them. No animation, model-0 dictionary, palette or image range is certified dead.

Consequently the *conditional* duplicated-data-only pair would be `0x41DA0 - 0x1210 = 0x40B90` before metadata and alignment, still `0x11118` (69,912 bytes) over the conservative `0x2FA78` Water ceiling. This figure is **not** the smallest reachable representation or a safe patch footprint. An exact compact pair and exact Water-specific peak remain Pending until the specific shared reaction/action indices and computed script-entry paths above are closed, followed by Water-qualified allocation accounting. No ROM build or emulator run was performed for this follow-up.
