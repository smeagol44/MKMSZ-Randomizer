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

The same record changed to type `0x01` originally froze because Fire left slot `0x801AE46C` null. A bounded import proof loaded Temple file `0x89`, populated that slot, and replaced Fire's native type-`0x0A` allocation/file-`0x20` path rather than adding past the arena limit. The imported monk rendered, moved, fought, and was killable. Its normal death/despawn presentation was missing.

A 2026-09-27 static follow-up resolves that missing presentation. The generic death continuation does **not** remain inside fighter file `0x89`: for type `0x01`, it switches the dying actor to current-stage presentation **slot 10** through `0x80053DA8`. Temple's current-stage resource file `0x60` supplies a six-frame embedded bundle at slot 10; Fire's current-stage resource file `0x3C` leaves slot 10 exactly zero because Fire's native types `0x09/0x0A` are explicitly excluded from this generic terminal-presentation path. The imported MONK2 therefore reaches a valid generic death chain but binds an absent Fire stage-local presentation resource.

This establishes cross-stage fighter resource residency and construction and statically identifies the first auxiliary lifecycle dependency. Arbitrary roster compatibility remains Pending until such stage-local dependencies are planned/materialized and runtime-tested.

## MONK2 death/despawn presentation trace — static closure (2026-09-27)

**Static-confirmed.** The imported Fire type-`0x01` proof reaches the normal generic enemy terminal chain. The missing visuals are not caused by fighter file `0x89`, a separate MONK2 constructor file, or a special MONK2-only death callback.

The relevant permanent-code chain is:

```text
terminal/reaction path
  -> 0x800328FC
       health +0x654 == 0
  -> 0x80057098
       common terminal bookkeeping / type-family transforms
       schedules 0x80056D50
  -> 0x80056D50
       type/stage exclusions
       type 0x01 is NOT excluded
  -> 0x80053DA8
       sleep 60
       actor +0x98 = current stage resource base 0x802E82B8
       animation/resource pointer = base + *(base + 0x28)
       ; +0x28 is outer selector 10
       run terminal presentation
       decrement active accounting / remove actor
```

### Why stock Temple works and imported Fire does not

The current-stage presentation base at `0x802E82B8` is populated independently from the fighter resource:

| Stage | Current-stage file | Size | Outer slot 10 |
|---|---:|---:|---:|
| Temple | `0x60` | `0xFC60` | `0xADF4`, six-frame embedded bundle |
| Fire | `0x3C` | `0x2530` | **`0x00000000`** |

Temple slot 10 occupies a self-contained file-relative presentation region `0xADF4..0xCE8C` (size `0x2098`). Its six records begin at `0xAE10, 0xAE24, 0xAE38, 0xAE4C, 0xAE60, 0xAE74`. Water and Wind also expose six-record slot-10 bundles with the same presentation dimensions, independently supporting a shared stage-local terminal/death semantic.

Fire can leave this selector empty in stock gameplay because `0x80056D50` explicitly excludes native Fire types `0x09` and `0x0A` from `0x80053DA8`. Importing type `0x01` changes that assumption: MONK2 is not excluded, so its death path reads Fire slot 10 and obtains zero.

This matches the prior Runtime-confirmed observation: the fighter can be fought and killed, while its normal death/despawn presentation is absent.

### Correction: `0x8005E1FC`

Earlier notes described `0x8005E1FC` as a special type-`0x01` sound dispatch. The deeper trace corrects that interpretation. `0x800572C4` transforms particular source fighter families such as type `0x02` onto their secondary type-`0x01`/file-`0x89` resource before spawning `0x8005E1FC`; a parallel transform exists for another paired family. Therefore `0x8005E1FC` belongs to transformed secondary-resource-family behavior and is **not** evidence that native MONK2 requires another constructor/death resource.

### Smallest bounded proof

The next proof should retain the already-working Fire MONK2 fighter import and materialize **only Temple slot 10** into Fire:

1. relocate/expand Fire current-stage resource file `0x3C` in a disposable proof;
2. append a pointer-rebased copy of Temple's `0xADF4..0xCE8C` slot-10 bundle;
3. write Fire outer selector 10 (`file +0x28`) to the appended descriptor;
4. leave fighter file `0x89`, enemy stream records, and all other Fire resources unchanged;
5. manually kill imported MONK2s and verify the six-frame terminal presentation and clean actor disappearance.

This is approximately `0x2098` (8.15 KiB) of auxiliary stage-resource data rather than importing the whole Temple stage resource. Fire's selector 10 is logically empty, but that does **not** make physical storage free; the proof must use explicit relocated/expanded file ownership.

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
- **P** — cross-stage import is Runtime-confirmed for construction/combat but still has a known lifecycle/presentation defect.
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

There are **no non-native N cells** in this first pass: every foreign type is missing at least one exact resource-file/slot pair in the destination's native ordinary bundle. The only cross-stage exception with runtime evidence is Fire × `0x01`, where the explicit file-`0x89` import proved construction, rendering, AI, movement, collision, combat and killability, while normal death/despawn presentation remained missing.

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

The imported type-`0x01` death/despawn defect is now Static-confirmed as a missing destination stage-local slot-10 presentation bundle. The next bounded runtime gate is a Fire proof that materializes only Temple slot 10 while preserving the already-working fighter import. In parallel, a future disposable all-stage proof can exercise the conservative same-stage pools above without introducing foreign fighter allocations.
