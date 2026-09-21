# Sub-Zero ↔ Sektor animation mapping

This page owns the current static animation-slot catalog for the experimental **MKMSZ Sub-Zero graphics → MKT Sektor graphics** replacement work.

## Evidence boundary

- **MKMSZ target:** USA Rev. 0, SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`.
- **MKT donor:** USA Rev. 2, SHA-256 `30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb`.
- MKMSZ Sub-Zero resource: global file ID `0x87`, clean ROM `0x748920..0x78E2FF`, size `0x459E0`.
- MKMSZ animation selector `0x8002FE54`: table 0 at resource `+0x000`; table 1 at `+0x104`.
- The first script after MKMSZ table 1 is at `+0x1B0`, making table 1 exactly **43 entries**.
- MKT robot heap base: donor ROM `0x8881C0`; `robo_anitab1` is heap `+0x000` (**90 entries**) and `robo_anitab2` is heap `+0x168` (**27 entries**).
- MKT names are source-lineage labels; the table offsets below are verified against the supplied retail Rev. 2 ROM.

## Main conclusion

**Static-confirmed:** the inherited primary animation layout is shared through the ordinary fighter core. MKMSZ table-0 slots `0x00..0x25` and MKT Sektor primary slots `0x00..0x25` carry the same generic fighter meanings. These are the strongest first direct graphical-replacement candidates.

Do **not** infer the same for secondary tables. MKMSZ's 43-entry table 1 is Mythologies-specific, while the MKT robot family's 27-entry table 2 contains robot specials and family-shared entries. Secondary mapping must be semantic.

## Direct core mapping

| Slot | MKMSZ Sub-Zero | MKMSZ script | MKT Sektor script | Status |
|---:|---|---:|---:|---|
| `0x00` | stance | `+0x002EC` | `+0x001D4` | **DIRECT candidate** |
| `0x01` | walk_forward | `+0x003C0` | `+0x00230` | **DIRECT candidate** |
| `0x02` | walk_backward | `+0x003EC` | `+0x00254` | **DIRECT candidate** |
| `0x03` | turn | `+0x00418` | `+0x0021C` | **DIRECT candidate** |
| `0x04` | duck | `+0x0042C` | `+0x00278` | **DIRECT candidate** |
| `0x05` | duck_turn | `+0x0043C` | `+0x002FC` | **DIRECT candidate** |
| `0x06` | duck_block | `+0x00458` | `+0x00288` | **DIRECT candidate** |
| `0x07` | duck_hit | `+0x00468` | `+0x00298` | **DIRECT candidate** |
| `0x08` | duck_punch | `+0x0047C` | `+0x00314` | **DIRECT candidate** |
| `0x09` | duck_high_kick | `+0x004E0` | `+0x00354` | **DIRECT candidate** |
| `0x0A` | duck_low_kick | `+0x004C0` | `+0x00334` | **DIRECT candidate** |
| `0x0B` | uppercut | `+0x0049C` | `+0x0037C` | **DIRECT candidate** |
| `0x0C` | block | `+0x00624` | `+0x0050C` | **DIRECT candidate** |
| `0x0D` | victory | `+0x00D90` | `+0x01148` | **DIRECT candidate** |
| `0x0E` | high_punch | `+0x00504` | `+0x003A0` | **DIRECT candidate** |
| `0x0F` | low_punch | `+0x00574` | `+0x00410` | **DIRECT candidate** |
| `0x10` | elbow/combo | `+0x005E0` | `+0x0047C` | **DIRECT candidate** |
| `0x11` | high_kick | `+0x0065C` | `+0x005EC` | **DIRECT candidate** |
| `0x12` | low_kick | `+0x00634` | `+0x0051C` | **DIRECT candidate** |
| `0x13` | knee | `+0x00684` | `+0x00550` | **DIRECT candidate** |
| `0x14` | sweep_kick | `+0x00704` | `+0x00594` | **DIRECT candidate** |
| `0x15` | roundhouse | `+0x006DC` | `+0x005C4` | **DIRECT candidate** |
| `0x16` | jump | `+0x00734` | `+0x00620` | **DIRECT candidate** |
| `0x17` | jump_kick | `+0x00744` | `+0x00630` | **DIRECT candidate** |
| `0x18` | flip_punch | `+0x0077C` | `+0x00668` | **DIRECT candidate** |
| `0x19` | flip_kick | `+0x00760` | `+0x0064C` | **DIRECT candidate** |
| `0x1A` | forward_flip | `+0x00798` | `+0x00684` | **DIRECT candidate** |
| `0x1B` | back_flip | `+0x007C0` | `+0x006A4` | **DIRECT candidate** |
| `0x1C` | hit_high | `+0x007E8` | `+0x0070C` | **DIRECT candidate** |
| `0x1D` | hit_low | `+0x007FC` | `+0x00720` | **DIRECT candidate** |
| `0x1E` | knockdown | `+0x00874` | `+0x00808` | **DIRECT candidate** |
| `0x1F` | sweep_fall | `+0x008B4` | `+0x01100` | **DIRECT candidate** |
| `0x20` | stumble | `+0x00810` | `+0x00734` | **DIRECT candidate** |
| `0x21` | getup | `+0x00898` | `+0x0082C` | **DIRECT candidate** |
| `0x22` | sweep_getup | `+0x008D8` | `+0x01124` | **DIRECT candidate** |
| `0x23` | throw | `+0x008F8` | `+0x01180` | **DIRECT candidate** |
| `0x24` | zap/projectile_generic | `+0x00DA0` | `+0x001D4` | **DIRECT candidate** |
| `0x25` | dizzy | `+0x0084C` | `+0x00778` | **DIRECT candidate** |

The first proven member is slot `0x00` stance/idle: Sektor v10 is **Runtime-confirmed** with correct donor colors, stable normal actions/movement, and clean transitions. Destructive v11 is also **Runtime-confirmed**. Proof v12 implemented slots `0x01..0x04` (walk forward/backward, turn, duck) but **failed before gameplay** on the Mission Objective screen. Compact v13 reaches gameplay but its newly type-4-stored fighter frames render with severe ghosting/smear, so that storage path is rejected for fighter sprites. v14 returns to proven raw/type-0 and is **Runtime-confirmed** for slot `0x03` Turn. v15 is **Runtime-confirmed** for slots `0x01`/`0x02` Walk Forward/Backward using their shared seven-frame raw/type-0 set. v16 is **Runtime-confirmed** for the composed Idle + Walk Forward + Walk Backward + Turn set. v17 is **Runtime-confirmed** for slot `0x04` Crouch. v18 is **Runtime-confirmed** for direct crouch-family slots `0x05..0x07` (Crouch Turn, Crouch Block, Crouch Hit). v19 is **Runtime-confirmed** for slot `0x08` Crouch Punch and removes the observed stock Sub-Zero return frame. v20 mapped slot `0x0A` Crouch Low Kick but crossed the accumulated raw-resource boundary and catastrophically corrupted the whole scene before the move was used. v21 isolates the same slot/mapping on the smaller v17 base (`0x5550C`) and is **Runtime-confirmed** for slot `0x0A` Crouch Low Kick. v22 is **Runtime-confirmed** for slot `0x09` Crouch High Kick and preserves the already-confirmed Low Kick in the same compact build. v23 is **Runtime-confirmed** for slot `0x0B` Uppercut. v24 is **Runtime-confirmed** for slot `0x0C` Standing Block. v25 is **Runtime-confirmed** for slot `0x0E` High Punch on the compact branch. It imports all seven Sektor-owned High Punch frames while deliberately leaving the two Low-Punch crossover references stock until Low Punch is mapped. v26 is **Runtime-confirmed** for slot `0x0F` Low Punch on the small v11 baseline, including its punch-chain/crossover behavior. v27 is **Runtime-confirmed** for slot `0x12` Standing Low Kick. Because the exact retail 13-word sequence does not fit MKMSZ's 10-word stock region before High Kick, the exact sequence is appended and primary slot `0x12` redirected to it; six raw/type-0 donor frames are imported. v28 is **Runtime-confirmed** for slot `0x11` Standing High Kick using the same bounded strategy: the exact 13-word retail sequence is appended, slot `0x11` is redirected to it, and six raw/type-0 donor frames are imported. The user reported both standing kicks working perfectly in their tested routes. From v25 onward the runtime-confirmed post-legal logo bypass is included as a proof convenience baseline.

## MKMSZ Sub-Zero primary table — all 65 slots

| Slot | Inherited semantic | Script offset |
|---:|---|---:|
| `0x00` | stance | `+0x002EC` |
| `0x01` | walk_forward | `+0x003C0` |
| `0x02` | walk_backward | `+0x003EC` |
| `0x03` | turn | `+0x00418` |
| `0x04` | duck | `+0x0042C` |
| `0x05` | duck_turn | `+0x0043C` |
| `0x06` | duck_block | `+0x00458` |
| `0x07` | duck_hit | `+0x00468` |
| `0x08` | duck_punch | `+0x0047C` |
| `0x09` | duck_high_kick | `+0x004E0` |
| `0x0A` | duck_low_kick | `+0x004C0` |
| `0x0B` | uppercut | `+0x0049C` |
| `0x0C` | block | `+0x00624` |
| `0x0D` | victory | `+0x00D90` |
| `0x0E` | high_punch | `+0x00504` |
| `0x0F` | low_punch | `+0x00574` |
| `0x10` | elbow/combo | `+0x005E0` |
| `0x11` | high_kick | `+0x0065C` |
| `0x12` | low_kick | `+0x00634` |
| `0x13` | knee | `+0x00684` |
| `0x14` | sweep_kick | `+0x00704` |
| `0x15` | roundhouse | `+0x006DC` |
| `0x16` | jump | `+0x00734` |
| `0x17` | jump_kick | `+0x00744` |
| `0x18` | flip_punch | `+0x0077C` |
| `0x19` | flip_kick | `+0x00760` |
| `0x1A` | forward_flip | `+0x00798` |
| `0x1B` | back_flip | `+0x007C0` |
| `0x1C` | hit_high | `+0x007E8` |
| `0x1D` | hit_low | `+0x007FC` |
| `0x1E` | knockdown | `+0x00874` |
| `0x1F` | sweep_fall | `+0x008B4` |
| `0x20` | stumble | `+0x00810` |
| `0x21` | getup | `+0x00898` |
| `0x22` | sweep_getup | `+0x008D8` |
| `0x23` | throw | `+0x008F8` |
| `0x24` | zap/projectile_generic | `+0x00DA0` |
| `0x25` | dizzy | `+0x0084C` |
| `0x26` | fb_kano | `+0x00974` |
| `0x27` | fb_sonya | `+0x002EC` |
| `0x28` | fb_jax | `+0x0031C` |
| `0x29` | fb_indian | `+0x00394` |
| `0x2A` | fb_johnny_cage | `+0x00244` |
| `0x2B` | fb_swat | `+0x00EE8` |
| `0x2C` | fb_lia | `+0x00DE8` |
| `0x2D` | fb_robo1 | `+0x00E30` |
| `0x2E` | fb_robo2 | `+0x00D78` |
| `0x2F` | fb_kung_lao | `+0x0085C` |
| `0x30` | fb_tusk | `+0x0084C` |
| `0x31` | fb_sheevagoro | `+0x001E8` |
| `0x32` | fb_shang_tsung | `0` |
| `0x33` | fb_liu_kang | `0` |
| `0x34` | fb_smoke | `0` |
| `0x35` | fb_kitana | `0` |
| `0x36` | fb_jade | `0` |
| `0x37` | fb_mileena | `0` |
| `0x38` | fb_ninja_1 | `0` |
| `0x39` | fb_ninja_2 | `0` |
| `0x3A` | fb_ninja_3 | `0` |
| `0x3B` | fb_ninja_4 | `0` |
| `0x3C` | fb_ninja_5 | `0` |
| `0x3D` | fb_ninja_6 | `0` |
| `0x3E` | fb_ninja_7 | `0` |
| `0x3F` | fb_raiden | `0` |
| `0x40` | fb_shao_kahn | `0` |

Slots `0x26..` retain inherited Midway table positions, but actual MKMSZ call-site use is not implied by the inherited labels. Many later slots are aliases or zero.

## MKMSZ Sub-Zero secondary table — all 43 raw slots

Semantic naming is **Pending**. These entries must be labeled from MKMSZ call sites and runtime behavior before donor mapping.

| Slot | Script offset |
|---:|---:|
| `0x00` | `+0x00ED4` |
| `0x01` | `+0x00ED8` |
| `0x02` | `+0x00ED8` |
| `0x03` | `+0x00E84` |
| `0x04` | `+0x002EC` |
| `0x05` | `+0x00290` |
| `0x06` | `+0x002D8` |
| `0x07` | `+0x00F28` |
| `0x08` | `+0x0021C` |
| `0x09` | `+0x00890` |
| `0x0A` | `+0x00C90` |
| `0x0B` | `+0x00F58` |
| `0x0C` | `+0x00E9C` |
| `0x0D` | `0` |
| `0x0E` | `+0x00928` |
| `0x0F` | `+0x00928` |
| `0x10` | `+0x00928` |
| `0x11` | `+0x00928` |
| `0x12` | `0` |
| `0x13` | `+0x00928` |
| `0x14` | `+0x00928` |
| `0x15` | `+0x00928` |
| `0x16` | `+0x00B4C` |
| `0x17` | `+0x00BB0` |
| `0x18` | `+0x00928` |
| `0x19` | `+0x00928` |
| `0x1A` | `+0x00B64` |
| `0x1B` | `+0x00A4C` |
| `0x1C` | `+0x00AC0` |
| `0x1D` | `+0x00B18` |
| `0x1E` | `+0x00B18` |
| `0x1F` | `+0x00928` |
| `0x20` | `+0x00974` |
| `0x21` | `+0x009B4` |
| `0x22` | `+0x00A00` |
| `0x23` | `+0x00D14` |
| `0x24` | `+0x00D78` |
| `0x25` | `0` |
| `0x26` | `0` |
| `0x27` | `+0x001B0` |
| `0x28` | `+0x00928` |
| `0x29` | `+0x00CAC` |
| `0x2A` | `+0x001D4` |

## MKT Sektor / robot primary table — all 90 slots

Slots `0x00..0x40` use the inherited generic labels above. Sektor then continues with additional Trilogy states.

| Slot | Animation | Retail script offset |
|---:|---|---:|
| `0x00` | stance | `+0x001D4` |
| `0x01` | walk_forward | `+0x00230` |
| `0x02` | walk_backward | `+0x00254` |
| `0x03` | turn | `+0x0021C` |
| `0x04` | duck | `+0x00278` |
| `0x05` | duck_turn | `+0x002FC` |
| `0x06` | duck_block | `+0x00288` |
| `0x07` | duck_hit | `+0x00298` |
| `0x08` | duck_punch | `+0x00314` |
| `0x09` | duck_high_kick | `+0x00354` |
| `0x0A` | duck_low_kick | `+0x00334` |
| `0x0B` | uppercut | `+0x0037C` |
| `0x0C` | block | `+0x0050C` |
| `0x0D` | victory | `+0x01148` |
| `0x0E` | high_punch | `+0x003A0` |
| `0x0F` | low_punch | `+0x00410` |
| `0x10` | elbow/combo | `+0x0047C` |
| `0x11` | high_kick | `+0x005EC` |
| `0x12` | low_kick | `+0x0051C` |
| `0x13` | knee | `+0x00550` |
| `0x14` | sweep_kick | `+0x00594` |
| `0x15` | roundhouse | `+0x005C4` |
| `0x16` | jump | `+0x00620` |
| `0x17` | jump_kick | `+0x00630` |
| `0x18` | flip_punch | `+0x00668` |
| `0x19` | flip_kick | `+0x0064C` |
| `0x1A` | forward_flip | `+0x00684` |
| `0x1B` | back_flip | `+0x006A4` |
| `0x1C` | hit_high | `+0x0070C` |
| `0x1D` | hit_low | `+0x00720` |
| `0x1E` | knockdown | `+0x00808` |
| `0x1F` | sweep_fall | `+0x01100` |
| `0x20` | stumble | `+0x00734` |
| `0x21` | getup | `+0x0082C` |
| `0x22` | sweep_getup | `+0x01124` |
| `0x23` | throw | `+0x01180` |
| `0x24` | zap/projectile_generic | `+0x001D4` |
| `0x25` | dizzy | `+0x00778` |
| `0x26` | fb_kano | `+0x00D14` |
| `0x27` | fb_sonya | `+0x00D50` |
| `0x28` | fb_jax | `+0x00DA0` |
| `0x29` | fb_indian | `+0x00DEC` |
| `0x2A` | fb_johnny_cage | `+0x00E38` |
| `0x2B` | fb_swat | `+0x00E84` |
| `0x2C` | fb_lia | `+0x00EC4` |
| `0x2D` | fb_robo1 | `+0x00F28` |
| `0x2E` | fb_robo2 | `+0x00F8C` |
| `0x2F` | fb_kung_lao | `+0x00AA4` |
| `0x30` | fb_tusk | `+0x00B24` |
| `0x31` | fb_sheevagoro | `+0x00BB8` |
| `0x32` | fb_shang_tsung | `+0x00C08` |
| `0x33` | fb_liu_kang | `+0x00CB4` |
| `0x34` | fb_smoke | `+0x008FC` |
| `0x35` | fb_kitana | `+0x0099C` |
| `0x36` | fb_jade | `+0x009E0` |
| `0x37` | fb_mileena | `+0x00948` |
| `0x38` | fb_ninja_1 | `+0x00A48` |
| `0x39` | fb_ninja_2 | `+0x00A48` |
| `0x3A` | fb_ninja_3 | `+0x00A48` |
| `0x3B` | fb_ninja_4 | `+0x00A48` |
| `0x3C` | fb_ninja_5 | `+0x00A48` |
| `0x3D` | fb_ninja_6 | `+0x00A48` |
| `0x3E` | fb_ninja_7 | `+0x00A48` |
| `0x3F` | fb_raiden | `+0x00870` |
| `0x40` | fb_shao_kahn | `+0x00848` |
| `0x41` | air_fb_kano | `+0x008C0` |
| `0x42` | legged | `+0x00FE4` |
| `0x43` | projectile | `+0x01300` |
| `0x44` | shook | `+0x010A4` |
| `0x45` | air_fb_robo2 | `+0x008FC` |
| `0x46` | zoomed | `+0x0103C` |
| `0x47` | orb_banged | `+0x01024` |
| `0x48` | jade_shook | `+0x01644` |
| `0x49` | impaled | `+0x002A8` |
| `0x4A` | run | `+0x01444` |
| `0x4B` | thudd | `+0x015E8` |
| `0x4C` | scared | `+0x015E0` |
| `0x4D` | back_break | `+0x0167C` |
| `0x4E` | baby | `+0x01684` |
| `0x4F` | big_head | `+0x0168C` |
| `0x50` | half_cutup | `+0x016A4` |
| `0x51` | cutup | `+0x016A8` |
| `0x52` | float | `+0x016BC` |
| `0x53` | pounded | `+0x016C4` |
| `0x54` | reach | `+0x016CC` |
| `0x55` | skin_rip | `+0x016EC` |
| `0x56` | stretch | `+0x016F4` |
| `0x57` | sucked | `+0x01704` |
| `0x58` | shocked | `+0x0171C` |
| `0x59` | shredded | `+0x01730` |

## MKT robot-family secondary table — all 27 slots

This table is shared across the robot family. A nonzero resource entry is not proof that the move is legal for Sektor.

| Slot | Animation | Retail script offset |
|---:|---|---:|
| `0x00` | chest_open | `+0x0113C` |
| `0x01` | net | `+0x013F4` |
| `0x02` | bolt | `+0x01470` |
| `0x03` | robo_telepunch | `+0x01494` |
| `0x04` | bomb | `+0x013AC` |
| `0x05` | target | `+0x013A0` |
| `0x06` | air_slam | `+0x006E0` |
| `0x07` | tele_explode | `+0x014F4` |
| `0x08` | crush_arms (unused) | `0` |
| `0x09` | throw_spear | `+0x015FC` |
| `0x0A` | flame_on (unused) | `0` |
| `0x0B` | invisibility | `+0x01154` |
| `0x0C` | spear | `+0x01628` |
| `0x0D` | self_destruct (unused) | `0` |
| `0x0E` | helicopter (unused) | `0` |
| `0x0F` | arm_bomb (unused) | `0` |
| `0x10` | crush_blood (unused) | `0` |
| `0x11` | 4bar (unused) | `0` |
| `0x12` | earth (unused) | `0` |
| `0x13` | small_bomb (unused) | `0` |
| `0x14` | shark (unused) | `0` |
| `0x15` | bat (unused) | `0` |
| `0x16` | robo1_friend (unused) | `0` |
| `0x17` | dinger (unused) | `0` |
| `0x18` | robo2_friend (unused) | `0` |
| `0x19` | bull (unused) | `0` |
| `0x1A` | smoke_friend (unused) | `0` |

## Mapping policy

For the experimental graphics swap, "replacement" means the generated ROM may discard the corresponding Sub-Zero animation assets. The clean input ROM is the rollback source. There is no current requirement to preserve both characters for runtime switching.

Physical relocation is still allowed when donor data does not fit in the original compressed storage. The current Sektor converter materializes decoded, row-aligned type-0 image data, so donor storage can be substantially larger than the replaced stock compressed bundle.

Current buckets:

- **Direct core:** primary `0x00..0x25`; map same semantic slot first.
- **Legacy reaction slots:** MKMSZ `0x26..0x40`; only map if MKMSZ actually calls them.
- **Sektor extra primary:** donor `0x41..0x59`; use as semantic substitutes when a Mythologies-only state needs one.
- **Secondary/special:** no numeric mapping assumption.
- **Mythologies-only traversal/specials:** choose the closest Sektor pose/sequence or compose donor frames after the MKMSZ slot is positively identified.

## Recommended implementation order

1. Low-risk locomotion bundle: walk forward, walk backward, turn, duck.
2. Ground combat bundle: crouch attacks, uppercut, block, punches, elbow, kicks, knee, sweep, roundhouse.
3. Airborne bundle: jump, jump kick, flip punch/kick, forward/back flip.
4. Reactions/getups.
5. Decode and label all 43 MKMSZ secondary slots from call sites.
6. Map Mythologies-specific secondary states semantically to Sektor assets.


## Latest isolated proof — v28 Standing High Kick

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
