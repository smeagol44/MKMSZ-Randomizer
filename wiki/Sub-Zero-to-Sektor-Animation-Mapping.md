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

The first proven member is slot `0x00` stance/idle: Sektor v10 is **Runtime-confirmed** with correct donor colors, stable normal actions/movement, and clean transitions. Destructive v11 is also **Runtime-confirmed**. Proof v12 implemented slots `0x01..0x04` (walk forward/backward, turn, duck) but **failed before gameplay** on the Mission Objective screen. Compact v13 reaches gameplay but its newly type-4-stored fighter frames render with severe ghosting/smear, so that storage path is rejected for fighter sprites. v14 returns to proven raw/type-0 and is **Runtime-confirmed** for slot `0x03` Turn. v15 is **Runtime-confirmed** for slots `0x01`/`0x02` Walk Forward/Backward using their shared seven-frame raw/type-0 set. v16 is **Runtime-confirmed** for the composed Idle + Walk Forward + Walk Backward + Turn set. v17 is **Runtime-confirmed** for slot `0x04` Crouch. v18 is **Runtime-confirmed** for direct crouch-family slots `0x05..0x07` (Crouch Turn, Crouch Block, Crouch Hit). v19 is **Runtime-confirmed** for slot `0x08` Crouch Punch and removes the observed stock Sub-Zero return frame. v20 mapped slot `0x0A` Crouch Low Kick but crossed the accumulated raw-resource boundary and catastrophically corrupted the whole scene before the move was used. v21 isolates the same slot/mapping on the smaller v17 base (`0x5550C`) and is **Runtime-confirmed** for slot `0x0A` Crouch Low Kick. v22 is **Runtime-confirmed** for slot `0x09` Crouch High Kick and preserves the already-confirmed Low Kick in the same compact build. v23 is **Runtime-confirmed** for slot `0x0B` Uppercut. v24 is **Runtime-confirmed** for slot `0x0C` Standing Block. v25 is **Runtime-confirmed** for slot `0x0E` High Punch on the compact branch. It imports all seven Sektor-owned High Punch frames while deliberately leaving the two Low-Punch crossover references stock until Low Punch is mapped. v26 is **Runtime-confirmed** for slot `0x0F` Low Punch on the small v11 baseline, including its punch-chain/crossover behavior. v27 is **Runtime-confirmed** for slot `0x12` Standing Low Kick. Because the exact retail 13-word sequence does not fit MKMSZ's 10-word stock region before High Kick, the exact sequence is appended and primary slot `0x12` redirected to it; six raw/type-0 donor frames are imported. v28 is **Runtime-confirmed** for slot `0x11` Standing High Kick using the same bounded strategy: the exact 13-word retail sequence is appended, slot `0x11` is redirected to it, and six raw/type-0 donor frames are imported. The user reported both standing kicks working perfectly in their tested routes. v29 is **Runtime-confirmed** for slot `0x13` Knee, reusing the already-proven `RBSTANCE7` frame from the v11 idle set and importing only `RBKNEE2`/`RBKNEE3`. v30 is **Runtime-confirmed** for slot `0x14` Sweep, importing all eight genuine Sektor Sweep frames while preserving MKMSZ's native sweep callback pair. v31 is **Runtime-confirmed** for slot `0x15` Roundhouse, replacing its exact ten-word in-place visual sequence with all eight genuine Sektor spin-kick frames and requiring no callback translation. v32 is **Runtime-confirmed** for slot `0x16` Jump, replacing its exact four-word in-place sequence with the three genuine Sektor jump frames. v33 is **Runtime-confirmed** for slots `0x17` Jump Kick, `0x18` Flip Punch, and `0x19` Flip Kick in one bounded bundle; all nine genuine donor frames worked perfectly in the tested route. From v25 onward the runtime-confirmed post-legal logo bypass is included as a proof convenience baseline.

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


## Latest isolated proof — v29 Knee

Disposable proof: `MKMSZR_mkt-sektor-knee_isolated-proof_v29.z64`.

Identity:

- SHA-256 `1adffe93fb6a04163896a7738ff74b1f915b0607e3cff1bd82b00b25fab40d71`;
- CRC1/CRC2 `CAACEE79 / 889B6536`.

v29 returns to the exact runtime-confirmed v11 idle baseline and replaces primary slot `0x13` Knee with the exact retail Sektor sequence `RBKNEE1, RBKNEE2, RBKNEE3, 0, RBKNEE2, RBKNEE1, 0`. Retail `RBKNEE1` is the same physical robot stance frame already materialized in v11 as `RBSTANCE7`, so the proof reuses that target shape and imports only the two unique Knee frames. The seven-word target Knee script fits in-place at resource `+0x684`; no script relocation is needed. File ID `0x87` is `0x507E0`. The post-legal logo bypass remains included.

**Runtime-confirmed.** The user reported Knee working perfectly in the tested route. Primary slot `0x13` is therefore a runtime-confirmed direct graphical replacement. The next bounded target is slot `0x14` Sweep.


## Latest isolated proof — v30 Sweep

Disposable proof: `MKMSZR_mkt-sektor-sweep-kick_isolated-proof_v30.z64`.

Identity:

- SHA-256 `f8a1098706df4fec29580aaf951e5276ac5f193a7d1b073caaee3bc149b80fc8`;
- CRC1/CRC2 `CAACE149 / 5BD11509`.

v30 returns to the exact runtime-confirmed v11 idle baseline and maps primary slot `0x14` Sweep. The retail Sektor script has eight visual frames and the control pair `ani_calla,sweep_sounds`; MKMSZ's native Sweep uses the same 12-word grammar but its own native callback argument. The proof therefore preserves MKMSZ's `6,0` callback pair and replaces only the eight visual pointers with genuine Sektor `RBSWEEPKICK1..8` frames. No donor callback ID is transplanted. File ID `0x87` is `0x56C7C`; the false cave remains stock and the post-legal logo bypass is included.

**Runtime-confirmed.** The user reported Sweep working beautifully in the tested route. Primary slot `0x14` is therefore a runtime-confirmed direct graphical replacement. The next bounded target is slot `0x15` Roundhouse.


## Latest isolated proof — v31 Roundhouse

Disposable proof: `MKMSZR_mkt-sektor-roundhouse_isolated-proof_v31.z64`.

Identity:

- SHA-256 `21e569d7b32e21062db4eee0ec93e21ad7aa59a74e32027936e25e7e50d0b732`;
- CRC1/CRC2 `CAACE1B9 / 8F6ED860`.

v31 returns to the exact runtime-confirmed v11 idle baseline and maps primary slot `0x15` Roundhouse. The exact MKT Rev. 2 Sektor sequence is `RBSPINKICK1,2,3,4,5,0,6,7,8,0`. MKMSZ's stock Roundhouse region is also exactly ten words and needs no callback/control translation, so all eight visual pointers are replaced in place with genuine Sektor raw/type-0 frames. File ID `0x87` is `0x5B180`, below the already runtime-confirmed v19 size `0x5C15C` and below failed v20. The false cave remains stock and the post-legal logo bypass is included.

**Runtime-confirmed.** The user reported Roundhouse working wonderfully in the tested route. Primary slot `0x15` is therefore a runtime-confirmed direct graphical replacement. The next bounded target is slot `0x16` Jump.


## Latest isolated proof — v32 Jump

Disposable proof: `MKMSZR_mkt-sektor-jump_isolated-proof_v32.z64`.

Identity:

- SHA-256 `ca8b7e5d473a22ee67dbafd8a707ca8583fc38d2af875eee82734adcee8ce3b0`;
- CRC1/CRC2 `CAACE1D9 / 6D21C0BA`.

v32 returns to the exact runtime-confirmed v11 idle baseline and maps primary slot `0x16` Jump. The exact retail Sektor sequence is `RBJUMP1, RBJUMP2, RBJUMP3, 0`; MKMSZ's stock Jump region is also four words, so the three visual pointers are replaced in place with genuine donor raw/type-0 frames. The imported retail geometries are 65x100, 66x123, and 78x83 in target X:Y order. File ID `0x87` is `0x52D94`; neighboring Roundhouse, Jump Kick, Flip Kick/Punch, Knee, and Sweep scripts remain untouched in this isolated proof.

**Runtime-confirmed.** The user reported Jump working perfectly in the tested route. Primary slot `0x16` is therefore a runtime-confirmed direct graphical replacement.


## Runtime-confirmed bundle — v33 aerial attacks

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


## Partial runtime validation — v34 flips and hit reactions

Disposable proof: `MKMSZR_mkt-sektor-flips-hit-reactions_bundle-proof_v34.z64`.

Identity:

- SHA-256 `4fb6517be14fc74febecc35b17d0524147e618a62ede808bd5a5d25104f46dca`;
- CRC1/CRC2 `CAACE149 / 3F3E800D`;
- file ID `0x87` size `0x5BC4C`.

v34 bundles primary slots `0x1A` Forward Flip, `0x1B` Back Flip, `0x1C` High Hit, and `0x1D` Low Hit. The two flip states share the six physical retail Rev. 2 `RBJUMPFLIP` frames in opposite orders and use translated local loop destinations. High Hit and Low Hit each use their exact five-word retail visual sequences.

**Runtime-confirmed:** Forward Flip, Back Flip, and High Hit all worked correctly in the tested route.

**Pending:** Low Hit was not exercised. The user could not obtain a practical enemy attack while crouching in the tested route; this is lack of route coverage, not a failure observation.


## Runtime-confirmed bundle — v35 Sweep Fall + Sweep Getup

Disposable proof: `MKMSZR_mkt-sektor-sweep-fall-getup_bundle-proof_v35.z64`.

Identity:

- SHA-256 `9826cc7dba710a9121fe897f1bebc1d8c0f1a732c5c7d426b53787e0f7639c57`;
- CRC1/CRC2 `CAACE1B9 / C178A223`;
- file ID `0x87` size `0x57D00`.

v35 returns to the exact runtime-confirmed v11 idle baseline and bundles primary slot `0x1F` Sweep Fall with slot `0x22` Sweep Getup. The two retail sequences share one genuine robot frame; ten unique donor frames are materialized in total through the proven raw/type-0 fighter conversion. Knockdown, normal Getup, Stumble, and Throw remain stock in this proof.

**Runtime-confirmed.** The user successfully forced the AI sweep route and reported both the fall and sweep-specific recovery working perfectly.


## Runtime-confirmed isolated proofs — v36 Knockdown and v37 Getup

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


## Runtime-confirmed composition — v39 Stumble + Stage Select

Disposable proof: `MKMSZR_mkt-sektor-stumble-stage-select_proof_v39.z64`.

Identity:

- SHA-256 `2ff5eb680c97df2a10bdceaf21da71c30d76ceb9cbae401dfb6c14e0e11831ca`;
- CRC1/CRC2 `BE156481 / 13B6BEC2`;
- file ID `0x87` remains `0x578BC`, byte-identical to the v38 Stumble resource.

The proof composes primary slot `0x20` Stumble with the compact eight-stage selector while keeping the Sektor helper/resource payload unchanged. The Stumble animation uses the exact appended 17-word retail loop and six genuine donor frames.

**Runtime-confirmed for Stumble on the tested route.** The user supplied two runtime screenshots showing the long upright reel-back/stagger reaction and reported that the animation works correctly.

**Runtime-confirmed Prison failure / correction:** the same v39 ROM later entered Prison through the selector and rendered the opening area normally, but crossing the first doorway roughly two seconds from stage start caused catastrophic full-scene/framebuffer corruption exactly as that doorway/encounter boundary activated. Two pre-door screenshots are clean and the post-door screenshot is corrupted. Therefore the earlier broad claim that selector + Sektor transplantation coexist globally is superseded. Stumble remains confirmed; v39's Prison route does not. A bounded control using the smaller v11 file-0x87 resource plus the identical selector composition is the next diagnostic.


## Prison allocation control — v40

Disposable proof: `MKMSZR_mkt-sektor-idle-stage-select_prison-control_v40.z64`.

Identity:

- SHA-256 `6fa455c174d0d9417549bff5a3a662c9e67c179f5bc4d9842ae416be83b2659d`;
- file ID `0x87` size `0x4D820`.

v40 keeps the same compact stage selector and Sektor proof-helper architecture used by v39, but returns fighter file `0x87` to the exact smaller v11 idle resource. The user repeated the Prison route and crossed the first doorway/encounter boundary without corruption.

**Runtime-confirmed control.** This materially strengthens the hypothesis that v39's Prison corruption is caused by fighter-resource allocation/headroom rather than the selector itself. It does not establish a universal byte threshold; content/layout/load-path interactions remain possible.


## Prison exact-size allocation control — v41

Disposable proof: `MKMSZR_mkt-sektor-idle-stage-select_prison-size-control_v41.z64`.

Identity:

- SHA-256 `7c54becf79417c10bb188b780967c93bdc3a773fe7898866d6dfeaabce0705ac`;
- CRC1/CRC2 `BE156481 / 13B6BEC2`;
- file ID `0x87` size `0x578BC`, exactly matching failing v39.

v41 starts from runtime-confirmed v40. It does not add any reachable Sektor frame, script, descriptor, or pointer. The only fighter-resource change is extending file ID `0x87` from `0x4D820` to `0x578BC` with `0xA09C` bytes of unreachable `0xFF` tail padding so the loader/allocation footprint exactly matches v39.

**Runtime-confirmed failure.** Prison again renders normally before the first doorway, then catastrophically corrupts the full scene/framebuffer at that same doorway/encounter-activation boundary. This establishes that loaded file-0x87 allocation footprint alone is sufficient to trigger the Prison failure at size `0x578BC`; v39-specific frame content is not required. The exact minimum failing size remains pending.


## Native type-5 storage proof — v42

Disposable proof: `MKMSZR_mkt-sektor-native-type5-single-frame_proof_v42.z64`.

Identity:

- SHA-256 `b29f6afe1f9c066fa4ff410c1b8fed9befbb11711f870d4c6fc8a15374eeed33`;
- CRC1/CRC2 `BE156571 / 370FC1CC`;
- file ID `0x87` size `0x4D820`.

Stock Sub-Zero fighter images are now static-confirmed to use native codec **type 5**, not the pickup-style type 4 rejected in v13. v42 converts only `RBSTANCE1` from the proven raw Sektor representation to generated native type 5 while leaving its shape offset `+0x459FC`, true descriptor `55x113`, animation script, palette helper, the other four raw idle frames, selector composition, and total fighter-file allocation unchanged.

The generated type-5 image decodes to an aligned `56x114` buffer; the first 113 rows are byte-identical to the already runtime-confirmed raw frame and the final row is transparent padding. Stored bytes for this image/table fall from 6,332 raw bytes to 3,265 bytes with a deliberately simple one-model encoder.

**Runtime-confirmed.** The user inspected the entire idle animation frame-by-frame and could not distinguish the generated native type-5 `RBSTANCE1` frame from the four proven raw Sektor stance frames. The same ROM also passed the Prison first-doorway control without corruption. This confirms the native type-5 fighter-storage path for a genuine imported Sektor frame.


## Native type-5 full-idle compaction proof — v43

Disposable proof: `MKMSZR_mkt-sektor-native-type5-idle_proof_v43.z64`.

Identity:

- SHA-256 `d5d79cf541b70fc61a91c2f360a3e682873bdbdf25400744dbce2d6fe40935e6`;
- CRC1/CRC2 `BE15E281 / 5D345038`;
- file ID `0x87` size `0x49BAC`.

v43 returns to the runtime-confirmed v40 idle-only composition and encodes **all five genuine retail Sektor stance frames** into generated MKMSZ native type-5 blocks. The compact donor payload is repacked from resource `+0x459FC`; the active idle script and its companion loop are updated to the relocated shape offsets, the donor palette moves to `+0x49B60`, and the palette-helper range/pointer immediates are updated accordingly.

The five visible descriptors remain the exact retail Sektor geometries: 55x113, 50x113, 53x113, 58x113, and 57x113. Their type-5 backing buffers use the native 4-pixel / 2-row alignment contract. No new runtime decoder or rendering shim is introduced.

File ID `0x87` shrinks from v40's `0x4D820` to `0x49BAC`, reclaiming `0x3C74` bytes (15,476 bytes) while retaining the same five-frame idle content. This leaves the compact Sektor idle resource only `0x41CC` bytes above the clean stock Sub-Zero file size `0x459E0`.

**Runtime-confirmed.** The user inspected the complete five-frame idle cycle frame-by-frame, observed no visual mismatch or transition artifact, and confirmed Prison's first doorway remains healthy.
