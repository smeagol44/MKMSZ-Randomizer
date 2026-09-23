# Sektor takeover proof history

> **Scope:** This page is the canonical owner of the **versioned Sektor takeover proof chronology**. It records vNN artifact identity where preserved, hashes/CRCs/file sizes, the changed variable, proof allocations/conflicts, manual runtime route, final evidence status, positive and negative observations, supersession, and unresolved limits.
>
> Animation-slot tables, mapping policy, current coverage, and current gaps belong to [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping). Stable donor image/codec/palette/Type-5 packing conclusions belong to [MKT fighter asset translation](MKT-Fighter-Asset-Translation). Donor semantic translation belongs to [MKT adapter primitives](MKT-Adapter-Primitives). The MKMSZ host action ABI belongs to [Player actions and special moves](Player-Actions-and-Special-Moves). Literal production/proof allocation ownership belongs to [Memory and allocation map](Memory-and-Allocation-Map).

## Current conclusion

The Sektor takeover line is **Runtime-confirmed as a bounded proof workstream, not a production feature**.

The latest preserved gameplay proof is v62: the tested Sektor MKT combo strings work after translating donor reaction selectors to MKMSZ-native semantics. v58 is the current Runtime-confirmed twelve-pose Run baseline; v59 Runtime-confirms the completed middle Combo visuals; v60 Runtime-confirms the first type-`0x12` alternate Cyrax-style palette. None of those results waive the normal production integration gate.

The strongest current production conflict is v62's standalone 16-byte combo continuation at ROM `[0x9AD90,0x9ADA0)`, which lies inside the production bootstrap composite `[0x9AD84,0x9AF20)`. The proof validates combo semantics, **not** that allocation. The early Sektor helper line also demonstrated the opposite lesson: the zero-filled-looking `[0xA1308,0xA1544)` area was live stock action/dispatch data, and using it caused input-specific hangs.

## Reconciled status rules

A proof entry may preserve its historical **pre-test** status, but the section's final status is always the latest recorded evidence. In particular:

- **v52:** final status is **Runtime-confirmed failure**. Earlier runtime-pending wording is superseded; file-`0x87` footprint `0x5100C` alone reproduces the later Fortress Mission Objective hang with stage music.
- **v53:** final status is **Runtime-confirmed common-takeover baseline**. Fortress, Prison, Inventory, representative common actions, and demo movies passed on the tested routes; the original "runtime pending" heading was pre-test wording.
- **v54:** final status is **partially Runtime-confirmed / superseded**. Its composed strategy exposed wrong Run/Push ownership, a Sweep-Fall hard hang, and Throw palette/timing defects that v55 addressed.
- **v55:** final status is **partially Runtime-confirmed; Run rejected/superseded**. The PS1-derived even-Run import was malformed; the carried-forward repair line continued into v56.
- **v56:** final status is **partially Runtime-confirmed; PS1 Run rejected**. The even poses rendered as speckled/checkerboard bodies, while Sweep Fall/Getup, Throw, Fortress+Inventory, and Prison+Inventory passed on the tested route.
- **v57:** final status is **Runtime-confirmed Run failure** caused by ignoring aligned WIMP source-row pitch; its earlier "in-progress/runtime pending" note is historical context only.
- **v58/v59/v60/v62:** each has an explicit later Runtime-confirmed result within its bounded route. v61 remains **Rejected / failed**.

## Final-status index

| Proof | Final evidence status | Smallest meaningful result / limit |
|---|---|---|
| v01-v07 | **Rejected / failed** | Early helper line used the false zero cave; exact per-version artifact identities are not preserved in the current Task-14 source pages. |
| v08 | **Runtime-confirmed correction** | Restoring the stock action/dispatch bytes removed the input-specific hangs; allocation ownership remains in Memory Map. |
| v09 | **Unresolved historical gap** | No standalone v09 identity/result is preserved in the current canonical sources inspected for Task 14; no reconstruction is invented. |
| v10-v11 | **Runtime-confirmed** | Idle/Sektor baseline, including the destructive replacement line used by many later isolated proofs. |
| v12 | **Rejected / failed** | Expanded locomotion proof failed before gameplay on Mission Objective. |
| v13 | **Rejected / failed** | Type-4 fighter storage reached gameplay but rendered severe ghosting/smear. |
| v14-v19 | **Runtime-confirmed** | Turn, walks, composed locomotion, crouch family, and crouch punch. |
| v20 | **Rejected / failed** | Raw-resource growth crossed the working boundary and catastrophically corrupted the scene before Crouch Low Kick was used. |
| v21-v33 | **Runtime-confirmed** | Crouch/ground/air direct-core expansion through Jump Kick, Flip Punch, and Flip Kick on their documented routes. |
| v34 | **Partial Runtime-confirmed** | Forward/Back Flip and High Hit passed; Low Hit remained unexercised. |
| v35-v37 | **Runtime-confirmed** | Sweep Fall/Getup, Knockdown, and normal Getup. |
| v38 | **Historical reference only** | v39 records file `0x87` as byte-identical to a v38 Stumble resource, but the current mapping chronology preserves no standalone v38 identity/status block. |
| v39 | **Mixed** | Stumble Runtime-confirmed; Prison first-doorway route Runtime-confirmed failure, disproving broad coexistence. |
| v40 | **Runtime-confirmed control** | Smaller idle resource + selector passes Prison doorway. |
| v41 | **Runtime-confirmed failure** | Exact-size inert-tail control reproduces Prison corruption at file `0x87 = 0x578BC`. |
| v42-v43 | **Runtime-confirmed** | Native Type-5 single-frame and full-idle storage/compaction. |
| v44 | **Partial / Rejected packing bug** | Idle/walk/turn pass; Crouch hard-hangs because generated shapes were not word-aligned. |
| v45 | **Runtime-confirmed correction** | Word-aligned Type-5 locomotion composition, including Crouch and Prison doorway. |
| v46 | **Runtime-confirmed mapped animations; route limit remains** | Mapped crouch-combat actions pass; Prison post-door Inventory hard-hangs. |
| v47 | **Runtime-confirmed Prison memory control** | Reclamation restores Prison post-door Inventory; Fortress regression still present. |
| v48 | **Runtime-confirmed failure** | Inert size control proves Fortress can fail from file-`0x87` footprint `0x52740` alone. |
| v49-v50 | **Runtime-confirmed controls** | Both reach Fortress gameplay/music and Inventory; v49 `0x4E544` is the key real-content working footprint. |
| v51 | **Partial Runtime-confirmed** | Prison post-door Inventory passes; Fortress still fails after music before leaving Mission Objective. |
| v52 | **Runtime-confirmed failure** | Inert-tail control at `0x5100C` reproduces v51 Fortress failure. |
| v53 | **Runtime-confirmed baseline** | Sektor-first common takeover with native palette/full stock Type-5 reclamation; tested Fortress, Prison, Inventory, common actions, demos. |
| v54 | **Partial Runtime-confirmed / superseded** | Adds Run/Combo/Throw presentation but exposes Run/Push ownership, Sweep-Fall, and Throw repair issues. |
| v55 | **Partial Runtime-confirmed / Run rejected** | Corrects ownership/guard/Throw path; first PS1 even-Run decode is malformed. |
| v56 | **Partial Runtime-confirmed / Run rejected** | Corrected cursor still yields invalid PS1 full-body Run; non-Run route passes documented regressions. |
| v57 | **Runtime-confirmed failure** | WIMP source extraction ignored `align4(xsize)` row pitch, producing diagonal/slashed frames. |
| v58 | **Runtime-confirmed** | Stride-corrected twelve-pose ordinary Run works on the tested route. |
| v59 | **Runtime-confirmed** | Completed middle Combo visuals work; no new file-`0x87` growth. |
| v60 | **Runtime-confirmed** | First type-`0x12` alternate palette renders as intended yellow/gold Cyrax-style robot. |
| v61 | **Rejected / failed** | Direct donor reaction selector reuse corrupts world/background rendering in the long combo. |
| v62 | **Runtime-confirmed proof; allocation conflict remains** | Three reaction-selector translations fix the tested combo strings; standalone record must be reallocated before integration. |

## v10-v27 — condensed early direct-core chronology

Exact ROM filenames/hashes/CRCs for these early entries are not preserved in the current mapping page, so this history does not invent them. Later proof sections preserve exact identities when they exist.

| Proof | Changed variable | Final evidence | Positive / negative observation | Supersession / limit |
|---|---|---|---|---|
| v10 | First genuine Sektor stance/idle replacement | **Runtime-confirmed** | Correct donor colors, stable normal actions/movement, clean transitions | First proven direct-core member |
| v11 | Destructive idle replacement baseline | **Runtime-confirmed** | Stable baseline reused by later isolated proofs | Later takeover lines supersede its narrow scope |
| v12 | Add Walk F/B, Turn, Duck using expanded raw storage | **Rejected / failed** | Failed before gameplay on Mission Objective | Motivated compact/alternate storage work |
| v13 | Store fighter frames through type 4 | **Rejected / failed** | Reaches gameplay but severe ghosting/smear | Type 4 rejected for fighter sprites |
| v14 | Isolated Turn | **Runtime-confirmed** | Turn works | Raw/type-0 recovery after v13 |
| v15 | Walk Forward/Backward | **Runtime-confirmed** | Shared seven-frame walk set works | — |
| v16 | Compose Idle + Walk F/B + Turn | **Runtime-confirmed** | Stable combined locomotion | — |
| v17 | Crouch | **Runtime-confirmed** | Crouch works | Later used as compact base |
| v18 | Crouch Turn/Block/Hit | **Runtime-confirmed** | Direct crouch-family states work | — |
| v19 | Crouch Punch | **Runtime-confirmed** | Removes observed stock Sub-Zero return frame | — |
| v20 | Crouch Low Kick on accumulated raw branch | **Rejected / failed** | Whole scene corrupts before move use | Resource-footprint failure; v21 isolates same mapping |
| v21 | Crouch Low Kick on smaller v17 base | **Runtime-confirmed** | Low Kick works | Supersedes v20 as mapping evidence |
| v22 | Crouch High Kick + prior Low Kick | **Runtime-confirmed** | Both work | — |
| v23 | Uppercut | **Runtime-confirmed** | Uppercut works | — |
| v24 | Standing Block | **Runtime-confirmed** | Block works | — |
| v25 | High Punch | **Runtime-confirmed** | Imports seven Sektor-owned frames; leaves Low-Punch crossover stock | Post-legal logo bypass becomes proof convenience baseline from here |
| v26 | Low Punch | **Runtime-confirmed** | Punch-chain/crossover behavior works | Completes the paired punch mapping |
| v27 | Standing Low Kick | **Runtime-confirmed** | Appended exact 13-word retail sequence works | Establishes bounded script-relocation pattern reused by v28 |

## Detailed chronology — v28 onward

The entries below retain exact identities, hashes/CRCs, file sizes, packing figures, routes, and negative controls as preserved by the pre-refactor mapping page. Pre-test status wording is retained only when labeled as superseded.

## v28 — Standing High Kick

Disposable proof: `MKMSZR_mkt-sektor-standing-high-kick_isolated-proof_v28.z64`.

Identity:

- SHA-256 `9c01b27c8778fd4a80fd0ccaee45d3b4d4265325a976cc436d6af318d1fc36b4`;
- CRC1/CRC2 `CAACE1C9 / 470098EC`.

v28 returns to the exact runtime-confirmed v11 idle baseline and replaces primary slot `0x11` Standing High Kick with the exact MKT Rev. 2 robot sequence:

```text
RBLOKICK1
RBLOKICK2
RBLOKICK3
RBLOKICK4
RBLOKICK5
RBHIKICK1
0
RBLOKICK5
RBLOKICK4
RBLOKICK3
RBLOKICK2
RBLOKICK1
0
```

The stock MKMSZ High Kick region is only 10 words before Knee, so the exact 13-word donor script is appended and primary table slot `0x11` is redirected to it. Five Low-Kick-family frames plus the unique `RBHIKICK1` apex are materialized through the proven raw/type-0 path. The donor palette is at resource `+0x58870`; file ID `0x87` is `0x588BC`. The runtime-confirmed post-legal logo bypass is included.

**Runtime-confirmed.** The user reported Standing High Kick working perfectly in the tested route. Primary slot `0x11` is therefore a runtime-confirmed direct graphical replacement. The next bounded isolated target is slot `0x13` Knee.


## v29 — Knee

Disposable proof: `MKMSZR_mkt-sektor-knee_isolated-proof_v29.z64`.

Identity:

- SHA-256 `1adffe93fb6a04163896a7738ff74b1f915b0607e3cff1bd82b00b25fab40d71`;
- CRC1/CRC2 `CAACEE79 / 889B6536`.

v29 returns to the exact runtime-confirmed v11 idle baseline and replaces primary slot `0x13` Knee with the exact retail Sektor sequence `RBKNEE1, RBKNEE2, RBKNEE3, 0, RBKNEE2, RBKNEE1, 0`. Retail `RBKNEE1` is the same physical robot stance frame already materialized in v11 as `RBSTANCE7`, so the proof reuses that target shape and imports only the two unique Knee frames. The seven-word target Knee script fits in-place at resource `+0x684`; no script relocation is needed. File ID `0x87` is `0x507E0`. The post-legal logo bypass remains included.

**Runtime-confirmed.** The user reported Knee working perfectly in the tested route. Primary slot `0x13` is therefore a runtime-confirmed direct graphical replacement. The next bounded target is slot `0x14` Sweep.


## v30 — Sweep

Disposable proof: `MKMSZR_mkt-sektor-sweep-kick_isolated-proof_v30.z64`.

Identity:

- SHA-256 `f8a1098706df4fec29580aaf951e5276ac5f193a7d1b073caaee3bc149b80fc8`;
- CRC1/CRC2 `CAACE149 / 5BD11509`.

v30 returns to the exact runtime-confirmed v11 idle baseline and maps primary slot `0x14` Sweep. The retail Sektor script has eight visual frames and the control pair `ani_calla,sweep_sounds`; MKMSZ's native Sweep uses the same 12-word grammar but its own native callback argument. The proof therefore preserves MKMSZ's `6,0` callback pair and replaces only the eight visual pointers with genuine Sektor `RBSWEEPKICK1..8` frames. No donor callback ID is transplanted. File ID `0x87` is `0x56C7C`; the false cave remains stock and the post-legal logo bypass is included.

**Runtime-confirmed.** The user reported Sweep working beautifully in the tested route. Primary slot `0x14` is therefore a runtime-confirmed direct graphical replacement. The next bounded target is slot `0x15` Roundhouse.


## v31 — Roundhouse

Disposable proof: `MKMSZR_mkt-sektor-roundhouse_isolated-proof_v31.z64`.

Identity:

- SHA-256 `21e569d7b32e21062db4eee0ec93e21ad7aa59a74e32027936e25e7e50d0b732`;
- CRC1/CRC2 `CAACE1B9 / 8F6ED860`.

v31 returns to the exact runtime-confirmed v11 idle baseline and maps primary slot `0x15` Roundhouse. The exact MKT Rev. 2 Sektor sequence is `RBSPINKICK1,2,3,4,5,0,6,7,8,0`. MKMSZ's stock Roundhouse region is also exactly ten words and needs no callback/control translation, so all eight visual pointers are replaced in place with genuine Sektor raw/type-0 frames. File ID `0x87` is `0x5B180`, below the already runtime-confirmed v19 size `0x5C15C` and below failed v20. The false cave remains stock and the post-legal logo bypass is included.

**Runtime-confirmed.** The user reported Roundhouse working wonderfully in the tested route. Primary slot `0x15` is therefore a runtime-confirmed direct graphical replacement. The next bounded target is slot `0x16` Jump.


## v32 — Jump

Disposable proof: `MKMSZR_mkt-sektor-jump_isolated-proof_v32.z64`.

Identity:

- SHA-256 `ca8b7e5d473a22ee67dbafd8a707ca8583fc38d2af875eee82734adcee8ce3b0`;
- CRC1/CRC2 `CAACE1D9 / 6D21C0BA`.

v32 returns to the exact runtime-confirmed v11 idle baseline and maps primary slot `0x16` Jump. The exact retail Sektor sequence is `RBJUMP1, RBJUMP2, RBJUMP3, 0`; MKMSZ's stock Jump region is also four words, so the three visual pointers are replaced in place with genuine donor raw/type-0 frames. The imported retail geometries are 65x100, 66x123, and 78x83 in target X:Y order. File ID `0x87` is `0x52D94`; neighboring Roundhouse, Jump Kick, Flip Kick/Punch, Knee, and Sweep scripts remain untouched in this isolated proof.

**Runtime-confirmed.** The user reported Jump working perfectly in the tested route. Primary slot `0x16` is therefore a runtime-confirmed direct graphical replacement.


## v33 — Aerial attacks

Disposable proof: `MKMSZR_mkt-sektor-aerial-attacks_bundle-proof_v33.z64`.

Identity:

- SHA-256 `97b137ecd835d6667143ff3d18aec7b225962d217798cb933b9d29e2294fab37`;
- CRC1/CRC2 `CAACE1C9 / 5DC52FD1`;
- file ID `0x87` size `0x58D9C`.

v33 returns to the exact runtime-confirmed v11 idle baseline and bundles three direct-core aerial attacks:

- slot `0x17` Jump Kick: exact seven-word forward/reverse retail sequence using `RBJUMPKICK1..3`;
- slot `0x18` Flip Punch: exact seven-word forward/reverse retail sequence using `RBFLIPUNCH1..3`;
- slot `0x19` Flip Kick: exact seven-word forward/reverse retail sequence using `RBFLIPKICK1..3`.

All nine unique donor frames use the proven raw/type-0 fighter conversion. Ordinary Jump remains stock in this bundle to keep the resource comfortably below the previously runtime-confirmed v25/v16 size class.

**Runtime-confirmed.** The user reported all three attacks working perfectly in the tested route.


## v34 — Flips and hit reactions

Disposable proof: `MKMSZR_mkt-sektor-flips-hit-reactions_bundle-proof_v34.z64`.

Identity:

- SHA-256 `4fb6517be14fc74febecc35b17d0524147e618a62ede808bd5a5d25104f46dca`;
- CRC1/CRC2 `CAACE149 / 3F3E800D`;
- file ID `0x87` size `0x5BC4C`.

v34 bundles primary slots `0x1A` Forward Flip, `0x1B` Back Flip, `0x1C` High Hit, and `0x1D` Low Hit. The two flip states share the six physical retail Rev. 2 `RBJUMPFLIP` frames in opposite orders and use translated local loop destinations. High Hit and Low Hit each use their exact five-word retail visual sequences.

**Runtime-confirmed:** Forward Flip, Back Flip, and High Hit all worked correctly in the tested route.

**Pending:** Low Hit was not exercised. The user could not obtain a practical enemy attack while crouching in the tested route; this is lack of route coverage, not a failure observation.


## v35 — Sweep Fall + Sweep Getup

Disposable proof: `MKMSZR_mkt-sektor-sweep-fall-getup_bundle-proof_v35.z64`.

Identity:

- SHA-256 `9826cc7dba710a9121fe897f1bebc1d8c0f1a732c5c7d426b53787e0f7639c57`;
- CRC1/CRC2 `CAACE1B9 / C178A223`;
- file ID `0x87` size `0x57D00`.

v35 returns to the exact runtime-confirmed v11 idle baseline and bundles primary slot `0x1F` Sweep Fall with slot `0x22` Sweep Getup. The two retail sequences share one genuine robot frame; ten unique donor frames are materialized in total through the proven raw/type-0 fighter conversion. Knockdown, normal Getup, Stumble, and Throw remain stock in this proof.

**Runtime-confirmed.** The user successfully forced the AI sweep route and reported both the fall and sweep-specific recovery working perfectly.


## v36-v37 — Knockdown and normal Getup

### v36 Knockdown

Disposable proof: `MKMSZR_mkt-sektor-knockdown_isolated-proof_v36.z64`.

Identity:

- SHA-256 `054e0bd8fb8807f38c645c5ad9177e0adf0bc6058694a9c8c7eaf3956a2b8e08`;
- CRC1/CRC2 `CAACE5B9 / 0A1A7384`;
- file ID `0x87` size `0x57344`.

v36 maps primary slot `0x1E` Knockdown on the exact runtime-confirmed v11 baseline. The exact retail robot sequence uses seven genuine `RBKNOCKDOWN` frames in a nine-word two-part script and fits the MKMSZ owning region in place.

**Runtime-confirmed.** The user reported the Knockdown sequence working perfectly.

### v37 normal Getup

Disposable proof: `MKMSZR_mkt-sektor-getup_isolated-proof_v37.z64`.

Identity:

- SHA-256 `8178af685d3ffc631a9390d43c7b31d9946ed748acd8ddc2291440148d033533`;
- CRC1/CRC2 `CAACE5C9 / 63053889`;
- file ID `0x87` size `0x54308`.

v37 maps primary slot `0x21` normal Getup on the exact runtime-confirmed v11 baseline. Six genuine retail Sektor Getup frames are materialized through the proven raw/type-0 fighter conversion.

**Runtime-confirmed.** The user reported normal Getup working perfectly.


## v39 — Stumble + Stage Select

Disposable proof: `MKMSZR_mkt-sektor-stumble-stage-select_proof_v39.z64`.

Identity:

- SHA-256 `2ff5eb680c97df2a10bdceaf21da71c30d76ceb9cbae401dfb6c14e0e11831ca`;
- CRC1/CRC2 `BE156481 / 13B6BEC2`;
- file ID `0x87` remains `0x578BC`, byte-identical to the v38 Stumble resource.

The proof composes primary slot `0x20` Stumble with the compact eight-stage selector while keeping the Sektor helper/resource payload unchanged. The Stumble animation uses the exact appended 17-word retail loop and six genuine donor frames.

**Runtime-confirmed for Stumble on the tested route.** The user supplied two runtime screenshots showing the long upright reel-back/stagger reaction and reported that the animation works correctly.

**Runtime-confirmed Prison failure / correction:** the same v39 ROM later entered Prison through the selector and rendered the opening area normally, but crossing the first doorway roughly two seconds from stage start caused catastrophic full-scene/framebuffer corruption exactly as that doorway/encounter boundary activated. Two pre-door screenshots are clean and the post-door screenshot is corrupted. Therefore the earlier broad claim that selector + Sektor transplantation coexist globally is superseded. Stumble remains confirmed; v39's Prison route does not. A bounded control using the smaller v11 file-0x87 resource plus the identical selector composition is the next diagnostic.


## v40 — Prison allocation control

Disposable proof: `MKMSZR_mkt-sektor-idle-stage-select_prison-control_v40.z64`.

Identity:

- SHA-256 `6fa455c174d0d9417549bff5a3a662c9e67c179f5bc4d9842ae416be83b2659d`;
- file ID `0x87` size `0x4D820`.

v40 keeps the same compact stage selector and Sektor proof-helper architecture used by v39, but returns fighter file `0x87` to the exact smaller v11 idle resource. The user repeated the Prison route and crossed the first doorway/encounter boundary without corruption.

**Runtime-confirmed control.** This materially strengthens the hypothesis that v39's Prison corruption is caused by fighter-resource allocation/headroom rather than the selector itself. It does not establish a universal byte threshold; content/layout/load-path interactions remain possible.


## v41 — Prison exact-size allocation control

Disposable proof: `MKMSZR_mkt-sektor-idle-stage-select_prison-size-control_v41.z64`.

Identity:

- SHA-256 `7c54becf79417c10bb188b780967c93bdc3a773fe7898866d6dfeaabce0705ac`;
- CRC1/CRC2 `BE156481 / 13B6BEC2`;
- file ID `0x87` size `0x578BC`, exactly matching failing v39.

v41 starts from runtime-confirmed v40. It does not add any reachable Sektor frame, script, descriptor, or pointer. The only fighter-resource change is extending file ID `0x87` from `0x4D820` to `0x578BC` with `0xA09C` bytes of unreachable `0xFF` tail padding so the loader/allocation footprint exactly matches v39.

**Runtime-confirmed failure.** Prison again renders normally before the first doorway, then catastrophically corrupts the full scene/framebuffer at that same doorway/encounter-activation boundary. This establishes that loaded file-0x87 allocation footprint alone is sufficient to trigger the Prison failure at size `0x578BC`; v39-specific frame content is not required. The exact minimum failing size remains pending.


## v42 — Native Type-5 single-frame proof

Disposable proof: `MKMSZR_mkt-sektor-native-type5-single-frame_proof_v42.z64`.

Identity:

- SHA-256 `b29f6afe1f9c066fa4ff410c1b8fed9befbb11711f870d4c6fc8a15374eeed33`;
- CRC1/CRC2 `BE156571 / 370FC1CC`;
- file ID `0x87` size `0x4D820`.

Stock Sub-Zero fighter images are now static-confirmed to use native codec **type 5**, not the pickup-style type 4 rejected in v13. v42 converts only `RBSTANCE1` from the proven raw Sektor representation to generated native type 5 while leaving its shape offset `+0x459FC`, true descriptor `55x113`, animation script, palette helper, the other four raw idle frames, selector composition, and total fighter-file allocation unchanged.

The generated type-5 image decodes to an aligned `56x114` buffer; the first 113 rows are byte-identical to the already runtime-confirmed raw frame and the final row is transparent padding. Stored bytes for this image/table fall from 6,332 raw bytes to 3,265 bytes with a deliberately simple one-model encoder.

**Runtime-confirmed.** The user inspected the entire idle animation frame-by-frame and could not distinguish the generated native type-5 `RBSTANCE1` frame from the four proven raw Sektor stance frames. The same ROM also passed the Prison first-doorway control without corruption. This confirms the native type-5 fighter-storage path for a genuine imported Sektor frame.


## v43 — Native Type-5 full-idle compaction

Disposable proof: `MKMSZR_mkt-sektor-native-type5-idle_proof_v43.z64`.

Identity:

- SHA-256 `d5d79cf541b70fc61a91c2f360a3e682873bdbdf25400744dbce2d6fe40935e6`;
- CRC1/CRC2 `BE15E281 / 5D345038`;
- file ID `0x87` size `0x49BAC`.

v43 returns to the runtime-confirmed v40 idle-only composition and encodes **all five genuine retail Sektor stance frames** into generated MKMSZ native type-5 blocks. The compact donor payload is repacked from resource `+0x459FC`; the active idle script and its companion loop are updated to the relocated shape offsets, the donor palette moves to `+0x49B60`, and the palette-helper range/pointer immediates are updated accordingly.

The five visible descriptors remain the exact retail Sektor geometries: 55x113, 50x113, 53x113, 58x113, and 57x113. Their type-5 backing buffers use the native 4-pixel / 2-row alignment contract. No new runtime decoder or rendering shim is introduced.

File ID `0x87` shrinks from v40's `0x4D820` to `0x49BAC`, reclaiming `0x3C74` bytes (15,476 bytes) while retaining the same five-frame idle content. This leaves the compact Sektor idle resource only `0x41CC` bytes above the clean stock Sub-Zero file size `0x459E0`.

**Runtime-confirmed.** The user inspected the complete five-frame idle cycle frame-by-frame, observed no visual mismatch or transition artifact, and confirmed Prison's first doorway remains healthy.


## v44 — Native Type-5 locomotion composition

Disposable proof: `MKMSZR_mkt-sektor-native-type5-locomotion_bundle-proof_v44.z64`.

Identity:

- SHA-256 `f1b82589be9cb089a224e09e92a59da25f8bdff531a1418efefe07df66b63cc4`;
- CRC1/CRC2 `BE14EA81 / 1DC5EB0A`;
- file ID `0x87` size `0x5273C`.

v44 extends the runtime-confirmed native type-5 branch to the complete low-risk locomotion set: five-frame Idle, seven physical Walk frames shared by Forward/Backward, two-frame Turn, and three-frame Crouch. The exact retail control grammar is preserved for both walk loops, Turn, and Crouch.

The seven Walk frames share one generated type-5 model/dictionary containing 1,456 unique 2x4 patterns with 11-bit pattern indices. Turn/Crouch use private generated dictionaries because shared variants are approximately neutral in size and would add complexity without meaningful gain.

This recreates the same broad locomotion scope that raw v12 expanded to `0x620E0` and failed at stage load, but v44 remains at `0x5273C`, saving `0xF9A4` bytes relative to v12 while retaining the compact stage selector.

**Partial runtime result / rejected packing bug.** Idle, Walk Forward/Backward, and Turn all work correctly. Pressing Crouch hard-hangs immediately before any crouch frame appears. Static audit found Crouch shape offsets `+0x5037E`, `+0x5113A`, and `+0x51D81`; the first and third are not word-aligned. Because the target dereferences shape/descriptor words with ordinary MIPS word loads, this precisely explains the pre-frame hard hang. The type-5 Crouch encoding itself is not rejected by this result.


## v45 — Corrected native Type-5 locomotion composition

Disposable proof: `MKMSZR_mkt-sektor-native-type5-locomotion_bundle-proof_v45.z64`.

Identity:

- SHA-256 `602664487903c6706a44e2180c5d0e5e8cfe1ad4899dad4fa4d13a3ea876d43b`;
- CRC1/CRC2 `BE14EAF1 / EC2A122C`;
- file ID `0x87` size `0x52740`.

v45 is a corrective rebuild of v44 with the same genuine Sektor Idle, Walk Forward/Backward, Turn, and Crouch content and the same shared seven-frame Walk type-5 dictionary. The packer now aligns every generated shape record to a 4-byte boundary before emitting its descriptor/image wrapper.

Corrected Crouch shape offsets are `+0x50380`, `+0x5113C`, and `+0x51D84`; all are word-aligned. The only resource-size cost versus v44 is four bytes of padding.

**Runtime-confirmed.** Idle, Walk Forward/Backward, Turn, and Crouch all work correctly; repeated transitions among them remain stable, and Prison's first doorway passes. This confirms the corrected word-aligned packer and shared-Walk native type-5 dictionary composition.


## v46 — Native Type-5 crouch-combat composition

Disposable proof: `MKMSZR_mkt-sektor-native-type5-crouch-combat_bundle-proof_v46.z64`.

Identity:

- SHA-256 `de53faf74aa651f56bb23b38c3952e8db9e8c5fe680bcb48b84333cc306ba89b`;
- CRC1/CRC2 `BE156481 / 757D90E7`;
- file ID `0x87` size `0x56E78`.

v46 deliberately accelerates coverage. It rebuilds the already runtime-confirmed compressed locomotion set and adds primary slots `0x05..0x0A` plus `0x0C`: Crouch Turn, Crouch Block, Crouch Hit, Crouch Punch, Crouch High Kick, Crouch Low Kick, and Standing Block. Together with Idle, Walk Forward/Backward, Turn, and Crouch, the resource contains 34 unique genuine Sektor fighter frames.

The offline type-5 encoder is upgraded beyond the v42-v45 flat-index proof form. v46 uses stock-compatible normal pattern-index classes and symbols `13..15` for transparent 2x4-block runs. Every generated stream is independently decoded during the build and checked byte-for-byte against the exact MKT-decoded aligned Sektor pixel buffer.

The long Crouch High Kick sequence is appended at resource `+0x56E04` and primary slot `0x09` redirects to it, matching the already runtime-confirmed raw-v22 strategy. All generated shape records are 4-byte aligned.

Despite the much larger animation scope, file `0x87` is only `0x56E78`: `0xB268` bytes smaller than raw v12's `0x620E0`, and `0xA44` bytes below the exact v41 size `0x578BC` that is runtime-confirmed to break Prison.

**Runtime-confirmed for all mapped animations; Prison post-door Inventory failure remains.** The user confirmed every v46 animation works, including Crouch Hit. Prison's first doorway no longer corrupts gameplay, but opening Inventory after crossing that doorway hard-hangs. Inventory works before the doorway, and this failure has not been observed in other stages so far. The evidence therefore points to a tighter Prison-specific post-door memory high-water boundary rather than an animation/codec failure.


## v47 — Dead-stock reclamation / Prison-Inventory control

Disposable proof: `MKMSZR_mkt-sektor-native-type5-repacked_prison-inventory-proof_v47.z64`.

Identity:

- SHA-256 `4eb68d30f64c67be8a669b11452c87f9ca0fd4bad5c12d616feadffa8a2276ad`;
- CRC1/CRC2 `BE14E2F1 / A10378F8`;
- file ID `0x87` size `0x52BC0`.

v47 preserves the exact v46 34-frame/action composition and exact type-5 codec grammar. It changes only physical storage placement.

A conservative stock-file liveness pass derived shape references from all 65 primary and 43 secondary animation-table script starts, then performed a whole-file aligned-word reference scan. Of the stock shapes referenced by the primary slots already replaced in v46, 42 frame blocks have no remaining pointer outside those replaced scripts. Their shape-to-next-shape intervals total `0x5E6C` bytes and are treated as disposable proof storage.

To preserve the already-runtime-confirmed palette helper, every generated Sektor shape/subdescriptor remains in the donor append range. Only type-5 image wrappers/streams are placed into the proven-dead stock frame holes. 17,080 bytes (`0x42B8`) of generated image storage fit there; the three oversized/fragmentation-fallback images remain in the donor tail.

The result reduces file `0x87` from v46's `0x56E78` to `0x52BC0` without dropping any animation. This is only `0x480` bytes above runtime-confirmed v45 while retaining the full v46 crouch-combat set.

**Runtime-confirmed for the Prison memory control; Fortress regression pending attribution.** Prison -> first doorway -> Inventory works normally, while the exact v46 composition at the larger 0x56E78 footprint hangs when Inventory is opened after that doorway. This confirms the reclaimed-storage size reduction is sufficient to restore that route. However, Fortress testing now shows the same pre-music Mission Objective hang in v45 (0x52740) as in v47 (0x52BC0), while v40 (0x4D820) loads Fortress normally. This means v47 reclamation is not the onset of the Fortress regression. The reclaimed stock intervals remain conservatively described as file-local-unreferenced rather than globally dead.


## v48 — Fortress exact-size allocation control

Disposable proof: `MKMSZR_mkt-sektor-idle-stage-select_fortress-size-control_v48.z64`.

Identity:

- SHA-256 `c4324831437bd76563f36961f68ab37c604b93e4b42f11e649b4f38fc9cdfbd9`;
- CRC1/CRC2 `BE14EAF1 / EC2A122C`;
- file ID `0x87` size `0x52740`, exactly matching failing v45.

v48 begins from runtime-confirmed v40. It changes no reachable Sektor frame, script, descriptor, palette helper, selector logic, or stage behavior. The only fighter-resource change is extending file ID `0x87` from `0x4D820` to `0x52740` with `0x4F20` bytes (20,256 bytes) of untouched/unreachable `0xFF` tail padding.

This is the Fortress counterpart to the earlier v41 Prison allocation control.

**Runtime-confirmed failure.** Fortress hangs on the Mission Objective screen before stage music/gameplay exactly as v45/v47 do. Since v40 at `0x4D820` loads Fortress normally, loaded file-0x87 allocation footprint alone is sufficient to cause the Fortress failure at `0x52740`. No exact lower threshold is claimed.


## v49-v50 — Compact locomotion Fortress controls

Two disposable proofs preserve the same genuine Sektor Idle + Walk Forward/Backward + Turn + Crouch behavior while using encoder-v2.

`MKMSZR_mkt-sektor-type5_compact-locomotion_proof_v49.z64`:
- SHA-256 `fab888febf806a84119b773ffe01a23c1c6d37efc25aae250e93d1d1b1a740ff`;
- CRC1/CRC2 `BE1556F1 / 31A9C4B4`;
- file ID `0x87` size `0x4E544`;
- no stock-frame-hole reuse.

`MKMSZR_mkt-sektor-type5_reclaimed-locomotion_proof_v50.z64`:
- SHA-256 `adb737edd95a012a8675f36d5c0cafeb368cc8c29f0bd6f62c43db5c1181acf6`;
- CRC1/CRC2 `BE159571 / 6193CBE7`;
- file ID `0x87` size `0x4C320`;
- uses `0x2224` bytes of file-local-unreferenced stock locomotion-frame intervals.

v49 is `0xD24` bytes above the known-good v40 Fortress footprint. v50 is `0x1500` bytes below it. These are real-content controls rather than inert padding threshold probes.

**Runtime-confirmed.** Both v49 and v50 load Fortress normally, reach gameplay/music, and allow Inventory to open without a hang. This establishes that the generated Type-5 locomotion itself is Fortress-safe at v49's `0x4E544` footprint and that v50's conservative stock locomotion-hole reclamation is also Fortress-safe on the tested route.


## v51 — Full crouch-combat merged reclamation

Disposable proof: `MKMSZR_mkt-sektor-type5-full-crouch-combat_merged-reclaim-proof_v51.z64`.

Identity:

- SHA-256 `6a4d07216cf9acbf30aae513a4787eff5c17eaa836171612d612cc5fa729394e`;
- CRC1/CRC2 `BE14F541 / D5784E8A`;
- file ID `0x87` size `0x5100C`.

v51 preserves the exact 34 unique genuine Sektor frames/actions of v46/v47: Idle, Walk F/B, Turn, Crouch, Crouch Turn, Crouch Block, Crouch Hit, Crouch Punch, Crouch Low Kick, Crouch High Kick, and Standing Block. No action is removed and the established encoder-v2 grammar is unchanged.

The storage planner changes only physical placement. The same 42 file-local-unreferenced stock frame intervals proved by v47 are merged only when byte-contiguous, yielding five reclaimed regions. This allows both Type-5 image streams and whole generated Type-5 model/dictionary tables to occupy the dead stock ranges. The planner uses the full `0x5E6C` bytes of already-proved reclaimed storage while keeping every Sektor shape/subdescriptor in the donor append range so the runtime-confirmed palette helper classification remains unchanged.

File `0x87` drops from v47's `0x52BC0` to `0x5100C`, a further `0x1BB4`-byte reduction with identical mapped content. This is `0x1734` bytes below the exact v48 Fortress allocation footprint that is runtime-confirmed to fail, although the exact Fortress threshold remains unknown.

**Final status: Partially Runtime-confirmed / superseded by v52 as the decisive size control.** v51 passed Prison -> first doorway -> Inventory, but Fortress reached stage music and still failed to leave the Mission Objective screen.

_Pre-test status (superseded): Static/implementation-confirmed; runtime pending. Primary gate was Fortress stage load + Inventory; secondary gate was Prison first doorway + Inventory and quick animation regression._


## v51-v52 — Later Fortress allocation boundary

v51 (`0x5100C`) preserves the complete 34-frame crouch-combat composition and passes the previously failing Prison doorway -> Inventory route. Fortress progresses farther than the earlier `0x52740` failure: stage music begins, but gameplay still does not leave the Mission Objective screen.

v52 is the decisive control: `MKMSZR_mkt-sektor-type5-locomotion_v51-size-control_v52.z64`.

- SHA-256 `02745e4dff4e4a4beaacb928d62915da4fff702c9bfae48fd3154835d59480ef`;
- CRC1/CRC2 `BE14F541 / D5784E8A`;
- file ID `0x87` size `0x5100C`.

v52 starts from fully runtime-confirmed Fortress-working v49 and changes no reachable fighter content. It adds only `0x2AC8` bytes of inert `0xFF` allocation tail so file `0x87` exactly matches v51's footprint.

**Final status: Runtime-confirmed failure.** Fortress reproduces v51's later Mission Objective hang with stage music playing. Therefore the `0x5100C` allocation footprint alone is sufficient to cause this later Fortress failure; the additional 17 combat frames present in v51 are not required. Historical pre-test/runtime-pending wording for v52 is superseded by this observed result.

Production-relevant implication: keep optimizing physical file-0x87 footprint. The known real-content working point is v49 at `0x4E544`; v51/v52 at `0x5100C` fail, a gap of only `0x2AC8` (10,952 bytes).


## v53 — common-animation Sektor takeover / native palette

Disposable proof: `MKMSZR_mkt-sektor-common-takeover_native-palette-proof_v53.z64`.

Identity:
- SHA-256 `65181aa5a270ec2ba404d01d02a8054ffba923991408a87465a25515b6b99e7f`;
- CRC1/CRC2 `A6246DD8 / 513DCBF9`;
- file ID `0x87` size `0x473D8`.

**Final status: Runtime-confirmed common-takeover baseline.** Later manual validation recorded Fortress, Prison, Inventory, representative common actions, and demo movies passing on the tested routes.

_Pre-test status (superseded): Static/implementation-confirmed; runtime pending._

This proof changes strategy from mixed Sub-Zero/Sektor coexistence to a Sektor-first takeover.

### Common mapped scope

33 common primary states through `0x22` are mapped to genuine Sektor visuals: all slots in that range except Victory `0x0D` and Elbow/Combo `0x10`. This includes the previously proven locomotion/crouch/ground attacks plus Uppercut, High/Low Punch, both standing kicks, Knee, Sweep, Roundhouse, Jump, Jump Kick, Flip Punch/Kick, Forward/Back Flip, High/Low Hit, Knockdown, Sweep Fall, Stumble, normal Getup, and Sweep Getup. Low Hit remains semantically the same direct mapping that lacked a practical runtime trigger in v34.

The build contains 129 unique genuine retail Sektor frames.

### Native palette; helper removed

The frame-setup-time donor-palette helper is removed completely. v53 begins from the clean ROM for the runtime path and restores:
- stock frame setup at `0x8001BDA0`;
- stock shared-arena start `0x801AF420`;
- zero/unclaimed file-ID `0x1B`;
- no helper bootstrap and no `0xF10000` helper payload load.

The stock 64-entry Sub-Zero player TLUT is retained structurally. Its lower 32 entries are replaced with the exact runtime-proven converted Sektor palette; the upper 32 stock entries remain valid. All Sektor images are 5-bpp and therefore address only the lower 32 entries.

### Full stock Type-5 reclamation

Because rare/unported animations are allowed to look wrong temporarily, v53 redirects every remaining direct stock Type-5 shape reference in the clean primary/secondary script corpus to the first Sektor stance shape. Those states retain their stock control grammar but display a safe placeholder Sektor frame instead of depending on Sub-Zero art.

This makes the entire stock 341-frame Type-5 corpus disposable. The old `+0x14AC..+0x41683` region is rebuilt for Sektor.

Two shared generated 5-bpp models use the exact stock model-0 class geometry:
- model 0: 69 frames, 19,939 patterns;
- model 1: 60 frames, 15,869 patterns.

118 Sektor frames fit in the reclaimed stock Type-5 region; 11 overflow into the relocated file tail. Independent software decode checks require every generated frame to reproduce the exact MKT-decoded padded pixels.

The resulting file `0x87 = 0x473D8`, which is `0x716C` bytes smaller than the runtime-confirmed Fortress-working v49 footprint `0x4E544` and far below v51/v52's failing `0x5100C`.

Unported primary states intentionally left as placeholder visuals are Victory `0x0D`, Elbow/Combo `0x10`, Throw `0x23`, generic projectile/Zap `0x24`, Dizzy `0x25`, plus later primary/secondary rare/special states not yet individually mapped.


## v54 — Run + Elbow/Combo + Throw/Grab

Disposable proof: `MKMSZR_mkt-sektor-run-combo-throw_common-proof_v54.z64`.

Identity:
- SHA-256 `7f11e7e462a8e9a5fb028a62e5281989480dd3eb19bdc5d281241113caf1876a`;
- CRC1/CRC2 `A6256DA8 / 9F9B13D5`;
- file ID `0x87` size `0x4E154`;
- `0x3F0` (1,008 bytes) below the runtime-confirmed Fortress-working v49 footprint `0x4E544`.

**Partially runtime-tested; the Run ownership, Sweep-Fall encoding, and Throw palette/timing are superseded by v55.**

v54 keeps the runtime-confirmed v53 native-Sektor-palette/helper-free architecture and extends it with Run, Elbow/Combo, and Grab/Throw visuals. A clean rebuild is deterministic, and an optional builder cross-check confirms all 129 inherited v53 frames are byte-for-byte identical in decoded pixels, geometry, and anchors to the runtime-confirmed v53 ROM.

### Running

MKMSZ secondary slot `0x27` still targets script `+0x1B0`. v54 preserves the native seven-visual loop plus `1 -> +0x1B4` control grammar and replaces only the visuals with genuine Sektor `RBRUN1,3,5,7,9,11,1` donor poses at `+0x2708,+0x271C,+0x2730,+0x2744,+0x2758,+0x276C,+0x2708`. MKT's footstep callback is not transplanted.

### Elbow / full combo

Primary slot `0x10` remains at MKMSZ target `+0x5E0`. The exact native 17-word, four-segment structure is preserved, including its zero separators. Its 13 visual positions use the ten genuine Sektor `RBELBOCOMBO1..10` shapes in sequence:

`1,2,3 / 2,1 / 4,5,6 / 7,8,9,10,9`.

No MKT gameplay callback or donor movement/control ABI is introduced.

### Grab / throw

A corrected static audit shows that MKMSZ's attacker-side Throw body at `+0x8F8` is exactly **12 words with nine visual positions**:

`[0,1,3,4,5,6,7,9,10]`.

The later shape references previously counted as part of a 15-position throw belong to the adjacent reaction/flip block beginning at `+0x928`; they are not attacker Throw frames and are not rewritten by v54. This agrees with the nine-frame MKMSZ Throwing presentation visible in external sprite references.

MKT Sektor's throw is substantially longer and uses `RBSHOLDER4` plus a slave mechanical arm. v54 does **not** import the incompatible slave-animation ABI. Instead it decodes MKT codec 15 offline, composites `RBSHOLDER4` with selected arm poses using donor anchors, and re-encodes the exact flattened pixels as ordinary MKMSZ Type-5 frames.

The nine MKMSZ attacker slots are downsampled to:

`RBSTANCE7 -> arm +0x2318 -> +0x2340 -> +0x237C -> +0x2390 -> +0x23B8 -> +0x23CC -> +0x2408 -> RBSTANCE7`.

Thus the throw uses seven distinct genuine mechanical-arm composites spanning emergence, forward extension, vertical sweep, upper-left transition, long sweep, downward return, and near-retraction, with genuine Sektor stance at entry/exit. Every MKMSZ zero separator and non-shape control word remains stock.

### Storage / Type-5 packing

The final corpus contains **152 generated Sektor frames**:
- 129 inherited v53 frames;
- 6 Run frames;
- 10 Elbow/Combo frames;
- 7 flattened Throw keyframes.

All artwork uses one physical shared 5-bpp Type-5 pattern dictionary. Sixteen entropy-model records point into that same dictionary with independent normal-class windows; the 6-bit native model selector makes this representation format-compatible. This changes only compression/model selection, not decoded pixels.

Final storage figures:
- 40,594 unique 2x4 patterns;
- shared table/dictionary size `0x31F5E`;
- compressed stream bytes `0x156B8`;
- file `0x87 = 0x4E154`.

Five former appended scripts are repacked into now-dead pre-Type-5 script regions; only the exact 13-word Standing High Kick script remains a separately packed script item. The stock 341-frame Sub-Zero Type-5 corpus remains fully reclaimed.

Independent software decode verifies every emitted Type-5 frame against its exact donor-decoded padded pixel buffer. Every generated shape is word-aligned. The helper remains absent, file ID `0x1B` remains unclaimed, the stock arena start remains restored, and the native Sektor palette architecture from v53 is unchanged.

Runtime gates: Run; full Elbow/Combo; Grab/Throw; Fortress -> gameplay -> Inventory; Prison first doorway -> Inventory.



## v55 — true 12-frame Run + Sweep-Fall decoder guard + Throw repair

Disposable proof: `MKMSZR_sektor-run-sweep-throw_common-proof_v55.z64`.

Identity:
- SHA-256 `13dd4c9247bf4b1154d3b7563412333c6e21f68569155f742e683fbc29635ebc`;
- CRC1/CRC2 `A624ABE8 / 48D2A010`;
- file ID `0x87 = 0x4D0A4`;
- `0x14A0` (5,280 bytes) below runtime-confirmed Fortress-working v49 `0x4E544`.

**Partially runtime-confirmed; v55 Run import failed visually and is superseded by v56.**

### Run / Push ownership correction

v54 runtime testing exposed the earlier semantic mistake. MKMSZ `+0x1B0` is the **Push** animation: seven visual ticks followed by `1 -> +0x1B4`. That is why the v54 Sektor run poses appeared while pushing. The actual ordinary **Run** loop is at `+0xEE8` and contains **twelve visual positions**, followed by `1 -> +0xEE8`.

v55 leaves Push as a seven-tick Sektor approximation using the six N64-retained run poses, but maps ordinary Run to twelve distinct Sektor poses:

`RBRUN1, RBRUN2, RBRUN3, RBRUN4, RBRUN5, RBRUN6, RBRUN7, RBRUN8, RBRUN9, RBRUN10, RBRUN11, RBRUN12`.

The odd poses `1/3/5/7/9/11` come from the supplied MKT N64 Rev. 2 donor. PS1 MKT preserves the full Run at `CODE/ROBOT.BIN +0x140C`, whose twelve image references resolve consecutively to `CHARS1/ROBOT.DAT` headers 222..233. The even poses `2/4/6/8/10/12`, deliberately cut from MKT N64, are decoded from those PS1 resources and converted into the native MKMSZ Type-5/Sektor-palette representation.

The PS1/N64 common odd poses differ only modestly in port crop/geometry, so v55 did not apply a destructive global resize. **Runtime correction:** the v55 PS1 POVBQ emitter was wrong: after writing each 2x4 vector it did not advance the destination pointer by four pixels, so every vector overwrote the same four-column strip. The prior “18 supplemental patterns / lossless” result only proved equality against those malformed target buffers and is **Rejected / superseded**.

### Sweep Fall

v54 hard-hung immediately after its second visible Sweep-Fall pose. Static audit places the next pose in the first generated model on that path containing a **0-bit normal Type-5 class**. Stock/runtime-confirmed generated layouts had not established such a class as native-decoder-safe. v55 therefore forbids zero-bit normal classes globally: all 52 generated model records have normal widths `>= 1` bit. This is a **strong inference / guarded repair** until runtime re-test confirms the former Sweep-Fall route no longer hangs.

### Throw color and timing

v54 established that the flattened mechanical-arm geometry is viable, but its codec-15 arm indices were interpreted through Sektor's body palette, producing a red arm. The donor source identifies a dedicated eight-entry `MECARM_P` palette. v55 converts that actual metal ramp into the resident Sektor TLUT using:

`1->17, 2->19, 3->20, 4->22, 5->24, 6->25, 7->26`.

The user also observed the visual arm choreography roughly one native tick ahead of the actual grab. v55 preserves MKMSZ gameplay/victim timing and changes only the nine attacker visual slots from v54's `stance, arm1..arm7, stance` to:

`stance, stance, arm1, arm2, arm3, arm4, arm5, arm6, arm7`.

The same seven genuine flattened arm phases remain in order: `+0x2318,+0x2340,+0x237C,+0x2390,+0x23B8,+0x23CC,+0x2408`.

### v55 storage and verification

The generated corpus contains **158 frames**: 129 inherited v53 frames + 12 Run poses + 10 Combo poses + 7 Throw composites. One physical 5-bpp dictionary contains **40,595** unique 2x4 patterns and is addressed by **52** entropy-model records. The table/dictionary occupies `0x32E03`; padded frame streams total `0x136A4`.

Five former append scripts remain repacked into proven-dead pre-Type-5 script regions, while Standing High Kick remains the one packed script item. The stock 341-frame Sub-Zero Type-5 corpus remains fully reclaimed.

Two clean v55 builds are byte-identical. The builder independently decodes every emitted Type-5 frame and requires exact equality with its selected target buffer; with the optional runtime-confirmed v53 ROM it also verifies all 129 inherited frames exactly. A separate finished-ROM audit confirms twelve distinct Run roots at `+0xEE8`, the independent seven-visual Push loop at `+0x1B0`, the one-slot Throw delay with stock separators untouched, and minimum normal-class width 1 across all 52 models.

Runtime gates: Run; Push; Sweep Fall + Sweep Getup; Throw color/timing; full Combo regression; Fortress -> gameplay -> Inventory; Prison first doorway -> Inventory.


## v56 — corrected full-body PS1 Run decode

Disposable proof: `MKMSZR_sektor-run-decode_common-proof_v56.z64`.

Identity:
- SHA-256 `eea8d47b4ed2fb94be891724097a97c74c94bff4703cd6f66a5bc5da25d892c0`;
- CRC1/CRC2 `A6256A28 / 73BE34AB`;
- file ID `0x87 = 0x4E414`;
- `0x130` (304 bytes) below runtime-confirmed Fortress-working v49 `0x4E544`.

**Final status: Partially Runtime-confirmed; PS1-derived Run path Rejected / failed.** The later manual test in this same proof showed the six even Run poses as speckled/checkerboard bodies, while Sweep Fall/Getup, Throw, Fortress+Inventory, and Prison+Inventory passed on the tested route.

_Pre-test status (superseded): Static/implementation-confirmed; runtime pending._

v56 is intentionally narrow: it keeps v55's already-working Throw, existing Combo mapping, Sweep-Fall safety guard, Push mapping, and all inherited v53 content. Only the six PS1-derived even Run poses are rebuilt.

The corrected PS1 POVBQ emitter follows the native 2-row/4-column vector layout exactly: after the second four-pixel row of a vector it advances the output cursor by four pixels before returning to the first row. Independent comparison against the separate PS1 decoder matches byte-for-byte for `RBRUN2/4/6/8/10/12`; every source frame also spans more than 30 nonzero columns, directly excluding the v55 four-column overwrite failure.

The corrected six full-body frames contain substantially more unique pattern data than the malformed v55 strips. Lossless inclusion would cross the known Fortress allocation boundary, so v56 uses a bounded codebook approximation: 256 supplemental PS1 2x4 patterns, exact transparency masks/silhouettes, and 64 Type-5 entropy models. The resulting six converted even poses have color-space RMSE about 4.504 in 5-bit RGB units and 36.3% exact opaque indices. This is deliberately documented as **lossy color/pattern approximation with exact silhouette**, not as lossless conversion.

Final storage: 158 generated frames, 40,833 shared dictionary patterns, table `0x33789`, padded streams `0x1408C`, file `0x87 = 0x4E414`. Two clean builds are byte-identical and every emitted Type-5 frame round-trips against its selected v56 target buffer.

Runtime gate: ordinary Run must show all twelve full-body poses; v55's tiny-artifact even frames must be absent. Push, Throw, Combo, Sweep Fall, Fortress/Inventory and Prison/Inventory are regressions.

Additional v55 runtime observation: the Sub-Zero combo still reaches six gameplay hits, but at least one middle impact displays an incorrect/neutral Sektor visual. The victim-side “being grabbed/thrown” presentation remains a separate pending mapping family; inherited primary `fb_*` slots `0x26+` are the first static candidates and must be tied to actual MKMSZ call sites before replacement.


**v56 runtime correction:** the six PS1-derived even Run poses still render badly, now as speckled/checkerboard full bodies rather than four-column artifacts. The six N64 odd poses remain clean. Native-palette renders of PS1 odd poses show the same bad internal structure, so this is an upstream PS1 POVBQ interpretation failure, not a Type-5/VQ packing failure. The v56 PS1 Run path is **Rejected**. Sweep Fall/Getup, Throw, Fortress+Inventory, and Prison+Inventory all pass on the tested v56 route.

**Replacement donor path (Static-confirmed):** preserved Midway MK3 `ROBO8.IMG` contains complete raw 8-bit `RBRUN1..RBRUN12` full-body images and `ROBO_P`. N64 MKT source explicitly lists the six even Run poses as cut. Future Run work must first calibrate raw MK3 odd poses against their exact N64 odd counterparts before transferring the even poses.

## v57 — Full-Run reconstruction and row-pitch failure (2026-09-21)

> **Historical recovery note (superseded as a current status):** this section was written before the v57 runtime test. It is retained because it records the recovered builder/source path; the final v57 Run result is the Runtime-confirmed failure documented below.

### Baseline and rejected path

- **Runtime-confirmed baseline remains v53** for the common Sektor takeover architecture.
- The later v55/v56 line retains the already user-confirmed Throw/Grab, Sweep Getup, Fortress, Prison, and Inventory fixes from the current takeover branch.
- **Rejected / failed for Run:** the v56 PS1 POVBQ-derived even Run frames. The alternating bad frames were already malformed in the decoded donor buffers, so another ROM built from that decode would only reproduce the visual corruption.
- The actual recovered builder `MKMSZR_build_sektor_takeover_v56.py` is available again and is the immediate code baseline for v57. It preserves the existing Type-5 encoder, donor/native corpus packing, guards, CRC path, and the already-confirmed non-Run fixes.

### Clean Midway source for the cut even Run poses

**Static-confirmed:** Midway's preserved WIMP library `video/supermk3/ROBO8.IMG` contains full-body source images `RBRUN1..RBRUN12`, including all six even poses cut from the retail N64 MKT robot data. It also contains the robot palette `ROBO_P`.

The WIMP headers parse consistently with the preserved WIMP structures. `ROBO_P` is a 64-color RGB555 source palette. Its colors can be reduced deterministically to the already runtime-proven 32-color N64 Sektor TLUT used by the takeover branch; this avoids introducing a new runtime palette path.

### N64 conversion calibration

**Static-confirmed for retained source/N64 pairs:** the Midway source art was reduced for N64 with an approximately fixed geometry transform:

- target width = `round(source_width * 0.80)`;
- target height = `round(source_height * 0.85)`;
- target X anchor follows the same 0.80 reduction exactly on the checked retained frames;
- target Y anchors are calibrated from the retained N64 robot descriptors and are applied explicitly below rather than guessed from the rejected PS1 pixel path.

This relationship was cross-checked against retained N64 robot Run, Stance, and Air-Punch descriptors. Pixel-mask comparison of retained Run frames also shows very close agreement for source/N64 pairs where the preserved source art revision matches the retail N64 pose. Some retained poses differ artistically between the preserved development source and final retail N64 art, so the calibration is being used as a conversion rule, not as a claim of universal pixel identity.

### Derived even-frame target descriptors

The six missing even Run poses now have bounded N64-style target geometry:

| Pose | Midway source | Derived target | Target anchor |
|---|---:|---:|---:|
| `RBRUN2` | 96x131 | **77x111** | **(+43,-8)** |
| `RBRUN4` | 63x127 | **50x108** | **(+17,-12)** |
| `RBRUN6` | 89x131 | **71x111** | **(+29,-8)** |
| `RBRUN8` | 108x135 | **86x115** | **(+46,-8)** |
| `RBRUN10` | 74x131 | **59x111** | **(+26,-9)** |
| `RBRUN12` | 81x137 | **65x116** | **(+24,-4)** |

**Implementation/static-confirmed, not runtime-confirmed:** all six clean `ROBO8.IMG` even poses have now been converted into target-sized indexed buffers using the calibrated reduction and deterministic `ROBO_P` -> proven N64 Sektor-TLUT color mapping. They are no longer dependent on the rejected PS1 POVBQ decoder.

### Role of PS1 MKT

The PS1 MKT material remains useful as an **independent descriptor/sequence reference**, especially because it preserves all 12 Run poses. It must not be treated as an N64 byte/layout oracle, and the rejected POVBQ pixel decode is not being revived. PS1 addresses and compressed-texture semantics remain platform-specific.

### v57 static build checkpoint

Disposable proof built from the clean supported MKMSZ ROM:

`MKMSZR_sektor-full-run_common-proof_v57.z64`

Identity:

- SHA-256 `2938fb45efbe0a81679054f820e1ddfbea4b2174d7227d1454f54e0558e8269b`;
- CRC1/CRC2 `A6256BE8 / 2791B9F0`;
- file ID `0x87 = 0x4E4A0`;
- `0xA4` bytes below the runtime-confirmed Fortress-working v49 footprint `0x4E544`.

_Pre-test status (superseded): **Implementation/static-confirmed; runtime pending.** The final v57 Run result is the Runtime-confirmed row-pitch failure recorded below._

A fully lossless inclusion of all six clean ROBO8 even frames was also built analytically, but it reached approximately `0x50200`, above the last runtime-confirmed Fortress-safe footprint. That lossless allocation was therefore not selected as the first runtime proof.

v57 instead keeps the clean ROBO8-derived geometry and exact transparency/silhouette masks, while using the already-established bounded Type-5 codebook strategy only for opaque palette-pattern approximation. The selected bound is **160 supplemental ROBO8 2x4 patterns**. Resulting quality is approximately **2.427 RGB RMSE** in 5-bit channel space with **47.346% exact opaque indices**, materially better than rejected v56's approximately 4.504 RMSE / 36.3% exact opaque indices. The final shared dictionary contains 40,737 patterns, the Type-5 table is `0x335A9`, and padded frame streams total `0x142F8`.

All six ROBO8 even-frame source buffers are hash-guarded in the recovered builder, all twelve Run roots at `+0xEE8` are distinct, generated Type-5 frames round-trip against their selected target buffers, normal class widths remain nonzero, all referenced shapes are word-aligned, and two clean v57 builds are byte-identical.

The v56 non-Run line is preserved: Throw/Grab composition, Sweep-Fall safety fix, Push approximation, existing Combo mapping, native v53 palette architecture, and the existing Fortress/Prison allocation strategy are unchanged in intent.

**Pending runtime gate:** ordinary Run must show a coherent twelve-pose Sektor cycle with the six formerly bad alternating frames corrected. Regressions: Push, Sweep Fall + Sweep Getup, Throw, full Combo, Fortress -> gameplay -> Inventory, and Prison first doorway -> Inventory.

### v57 runtime correction — ROBO8 source row pitch

**Runtime-confirmed failure:** the first v57 Run test shows several Run frames as heavily diagonal/slashed horizontal bands rather than coherent fighter sprites.

**Static-confirmed root defect:** Midway's preserved WIMP processing code treats image `xsize` as the **unpadded** visible width and advances every source row by `zero_pad = (4 - xsize) & 3`. Therefore raw WIMP image storage uses a 4-byte-aligned source-row pitch. The v57 ROBO8 extraction instead read each source as tightly packed `width * height`, so non-4-aligned source widths progressively consume row-padding bytes as pixels and shift every following row.

This also resolves the earlier odd-frame calibration anomaly: the ROBO8 odd Run frames that matched the N64 silhouettes extremely closely were source widths 100, 104 and 64 (already 4-byte aligned), while the three apparent source-art mismatches were widths 81, 71 and 97 (all requiring row padding). The earlier suggestion of an art-revision difference for those mismatches is superseded.

For the six even source poses, `RBRUN2` width 96 and `RBRUN8` width 108 are natural unchanged controls; `RBRUN4` width 63, `RBRUN6` width 89, `RBRUN10` width 74 and `RBRUN12` width 81 require corrected source pitch. The v57 Run path is therefore **Rejected / failed** for this concrete extraction bug. Non-Run v57 regressions remain pending the user's current test pass.

**Next Run fix:** recapture ROBO8 pixels row-by-row with `source_stride = align4(source_width)`, re-run the retained-odd calibration, regenerate only the six clean even target buffers, then repeat the Type-5 footprint/round-trip/CRC gates before the next disposable proof.




## v58 — stride-corrected full Run

Disposable proof: `MKMSZR_sektor-run-stride_common-proof_v58.z64`.

Identity:
- SHA-256 `bc15eed845b9d97c785acf828e593d5683d6a8f905bfb475b751160774d973e2`;
- CRC1/CRC2 `A6256DD8 / DB8E6E81`;
- file ID `0x87 = 0x4E3FC`;
- `0x148` bytes below the runtime-confirmed Fortress-working v49 footprint `0x4E544`.

**Runtime-confirmed on 2026-09-21 for ordinary Run.** The user reported that the completed Run animation “works perfectly.”

v58 is deliberately narrow. It keeps the v57/v56 non-Run architecture and changes only the six supplemental even Run source buffers. The v57 diagonal/slashed-frame failure was traced to a source-row-stride mistake: Midway WIMP stores each 8-bit source row at `align4(xsize)`, while v57 had consumed `xsize` bytes per row. Midway's own WIMP compression code explicitly computes `zero_pad = (4 - xsize) & 3`.

This also resolves the misleading v57 calibration anomaly. The retained odd ROBO8 frames whose source widths were already 4-byte aligned matched N64 closely, while the apparent mismatches all required source-row padding. v58 therefore reads every ROBO8 row using the aligned source pitch before scaling/palette conversion. `RBRUN2` (width 96) and `RBRUN8` (108) remain natural controls; `RBRUN4` (63), `RBRUN6` (89), `RBRUN10` (74), and `RBRUN12` (81) are the four even poses materially corrected by the stride fix.

The final twelve-pose Run at `+0xEE8` remains:
`RBRUN1..RBRUN12`,
with odd poses from retail N64 MKT and the six cut even poses reconstructed from stride-corrected `ROBO8.IMG`.

The bounded Type-5 composition remains inside the proven Fortress allocation envelope: 158 generated frames, 64 entropy models, 40,737 shared dictionary patterns, table `0x335A9`, and padded streams `0x14254`. The six ROBO8 even poses use 160 selected supplemental patterns with color-space RMSE `1.895317` and `54.115%` exact opaque indices, while preserving the selected target silhouettes. Every emitted Type-5 frame round-trips through the software decoder and two clean v58 builds are byte-identical.

Only Run was newly runtime-validated in v58; the already-confirmed Sweep Fall/Getup, Grab/Throw, Fortress/Inventory, and Prison/Inventory results come from the preceding repair line and are not re-labeled here as fresh v58 observations.


## v59 — complete middle Combo visuals

Disposable proof: `MKMSZR_sektor-full-combo_common-proof_v59.z64`.

Identity:
- SHA-256 `b8b1ddfa964de4da86dc9598f99139f4c50ac066deaaf4ab5cd91fda63baf1cc`;
- CRC1/CRC2 `A6256DD8 / DB8E6E81`;
- file ID `0x87 = 0x4E3FC`;
- `0x148` bytes below runtime-confirmed Fortress-working v49 `0x4E544`.

**Runtime-confirmed on 2026-09-21 for the completed Combo visuals.** The user reported that v59 “works perfectly.”

The earlier missing middle Combo visual(s) were not caused by the primary `0x10` Elbow/Combo script. That script already preserved MKMSZ's exact 17-word / four-segment grammar and mapped its 13 visual positions to:
`RBELBOCOMBO 1,2,3 / 2,1 / 4,5,6 / 7,8,9,10,9`.

The remaining neutral/missing visuals came from later portions of MKMSZ's **Knee** animation reused by the six-hit gameplay combo. v59 leaves the six gameplay combo records at ROM `0xB1CB0..0xB1D0F` byte-identical, including animation selectors:
`1003, 1004, 1305, 1501, 1303, 1501`.
Only six late Knee visual shape references are redirected:

| MKMSZ script position | v59 Sektor visual |
|---:|---|
| `+0x6A0` | `RBSPINKICK4` (`+0x1DD8`) |
| `+0x6A4` | `RBSPINKICK5` (`+0x1DC4`) |
| `+0x6AC` | `RBKNEE3` (`+0x1D74`) |
| `+0x6C4` | `RBKNEE1` (`+0x17A8`) |
| `+0x6D0` | `RBKNEE2` (`+0x1D60`) |
| `+0x6D4` | `RBKNEE3` (`+0x1D74`) |

All intervening controls/separators in those Knee segments remain byte-identical to clean MKMSZ. v59 adds no new frame assets and does not enlarge file `0x87`: it reuses already-resident Sektor shapes, so the v58 storage/model/Run composition remains unchanged. The count of remaining fallback stock-shape references falls from 323 to 317. Two independent clean v59 builds are byte-identical.

v58's twelve-pose Run remains the runtime-confirmed Run baseline. v59 changes only the six late Knee visual references needed by the existing combo chain; no independent v59 re-validation of unrelated gameplay routes is implied.


## v60 — First Scorpion alternate palette

**Final status: Runtime-confirmed on 2026-09-21.**

The first visible `SCORPION` / fighter type `0x12` is a Sub-Zero-family actor using an alternate palette, not the separate genuine Undead Scorpion/type-`0x11` resource. Under the v59 Sektor takeover, the transplanted fighter images are 5-bpp and therefore use only palette indices `0..31`. The normal player palette had already been replaced with Sektor's native lower-32 TLUT, but the type-`0x12` alternate palette still contained the stock ninja colors, so the same Sektor pixels were interpreted through the wrong colors.

v60 (`MKMSZR_scorpion-cyrax-palette_common-proof_v60.z64`) is an in-place palette-only proof built directly from the runtime-confirmed v59 ROM. In the relocated file-`0x87` image used by this proof, the alternate palette's lower 32 entries are at file-relative `+0x458D0`, ROM `0xF858D0`. v60 replaces that 64-byte lower-half TLUT with a Cyrax-style Sektor palette: armor entries `1..15` use a yellow/gold ramp derived from MKMSZ's Scorpion yellow family, while Sektor's gray/black metal entries `16..31` are preserved exactly in the target palette.

Static scope verification:
- input v59 SHA-256: `b8b1ddfa964de4da86dc9598f99139f4c50ac066deaaf4ab5cd91fda63baf1cc`;
- output v60 SHA-256: `caebb133e7ea759e5f115d169fe84f00d4120caa6545373b28983fd8efde048b`;
- exactly 62 bytes differ, all inside the single 64-byte alternate-palette window;
- file `0x87` size is unchanged at `0x4E3FC`;
- recalculated CRC1/CRC2 remain `A6256DD8 / DB8E6E81` because this proof patch lies outside the CIC-6102 CRC-covered ROM range.

Runtime result: the user reported the first Scorpion renders correctly as the intended yellow/gold Cyrax-style robot. This confirms only that first type-`0x12` alternate-palette route; no claim is made here for Undead Scorpion/type-`0x11` or arbitrary enemy palettes.


## v61/v62 — Sektor MKT combo-string transplant

The combo-string work is separate from v59's visual repair. v59 kept MKMSZ's original six Sub-Zero gameplay combo records and only fixed the Sektor visuals used by that chain. v61/v62 instead replace the gameplay combo graph itself with Sektor's MKT button/animation structure while keeping the already-runtime-confirmed Sektor art resident in file `0x87`.

### v61 — direct donor reaction-selector transplant

Disposable proof: `MKMSZR_sektor-mkt-combos_common-proof_v61.z64`.

Identity:
- SHA-256 `aecd40a9a8ba5c8a96195cf9f18ebe5b0c53b67d40d88fc33fb1c55b5d930111`;
- CRC1/CRC2 `A8234446 / EB410032`;
- file `0x87 = 0x4E3FC`, byte-identical to v60.

The proof replaces the six native combo records at ROM `0xB1CB0..0xB1D0F`, redirects the native knee/high-kick combo root pointer at ROM `0xA1CE8`, and adds one proof-only 16-byte standalone `HK -> HK` continuation record at ROM `0x9AD90` / VA `0x8009A190`. The normal HP/elbow root remains `0x800B10B0`.

The resulting Sektor strings are:
- `HK, HK`;
- `HP, HP, D+LP`;
- `HP, HP, HK, B+HK`;
- `HP, HP, HK, HK, B+HK`.

**Rejected / failed.** Runtime testing showed `HP, HP, D+LP` produced the intended uppercut-style victim launch, but the long combo caused catastrophic world/background rendering corruption while Sektor/HUD remained alive. v61 had copied MKT combo reaction selector `0x02` numerically into MKMSZ for the knockback finishers.

### v62 — MKMSZ-safe reaction translation

Disposable proof: `MKMSZR_sektor-mkt-combos-safe_common-proof_v62.z64`.

Identity:
- SHA-256 `689862a64ab2cfe04041fae357a19774e335cea39eff6c9d6f5ae143f601e1fd`;
- CRC1/CRC2 `B4234446 / 80A601BE`;
- file `0x87 = 0x4E3FC`, unchanged from v60/v61.

v62 preserves v61's Sektor button graph, attacker animation selectors, internal combo pointers, uppercut record, and proof-only `HK,HK` root. It changes only three gameplay reaction-selector bytes relative to v61, plus the resulting header CRC:
- ROM `0x9AD98`: standalone `HK,HK` finisher selector `0x02 -> 0x04`;
- ROM `0xB1CE8`: four-hit `B+HK` finisher selector `0x02 -> 0x04`;
- ROM `0xB1D08`: five-hit `B+HK` finisher selector `0x02 -> 0x04`.

The low-byte input requirements remain semantically appropriate: `0x0400` for the standalone `HK,HK` finisher and `0x0401` for the stick-away `B+HK` finishers. The already-working uppercut entry remains `0x0504` (`stk_5`-family launch plus stick-down requirement).

**Runtime-confirmed on 2026-09-21.** After the three selector translations, the user reported v62 “working perfectly.” This closes the v61 long-combo corruption on the tested route while preserving the uppercut launch behavior.

Evidence limit: v62 is still a disposable proof. Its extra 16-byte combo record uses `0x9AD90`, inside the randomizer bootstrap's production-owned `0x9AD84..` region. Production integration must relocate that standalone record to conflict-free owned storage; the runtime result validates the combo semantics, not that proof allocation.


## Canonical ownership and remaining limits

- Slot tables/current coverage: [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping).
- Stable codec/palette/Type-5/storage conclusions: [MKT fighter asset translation](MKT-Fighter-Asset-Translation).
- Donor semantic translation: [MKT adapter primitives](MKT-Adapter-Primitives).
- MKMSZ host action ABI: [Player actions and special moves](Player-Actions-and-Special-Moves).
- Literal current allocation ownership/conflicts: [Memory and allocation map](Memory-and-Allocation-Map).

The current proof line still does not establish production readiness, arbitrary Sektor specials, exhaustive rare-state coverage, victim-side grab/throw presentation, or a conflict-free production allocation for the v62 combo continuation. Historical successful proof footprints remain proof evidence only.
