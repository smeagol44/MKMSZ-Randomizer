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


## Native type-5 locomotion composition — v44

Disposable proof: `MKMSZR_mkt-sektor-native-type5-locomotion_bundle-proof_v44.z64`.

Identity:

- SHA-256 `f1b82589be9cb089a224e09e92a59da25f8bdff531a1418efefe07df66b63cc4`;
- CRC1/CRC2 `BE14EA81 / 1DC5EB0A`;
- file ID `0x87` size `0x5273C`.

v44 extends the runtime-confirmed native type-5 branch to the complete low-risk locomotion set: five-frame Idle, seven physical Walk frames shared by Forward/Backward, two-frame Turn, and three-frame Crouch. The exact retail control grammar is preserved for both walk loops, Turn, and Crouch.

The seven Walk frames share one generated type-5 model/dictionary containing 1,456 unique 2x4 patterns with 11-bit pattern indices. Turn/Crouch use private generated dictionaries because shared variants are approximately neutral in size and would add complexity without meaningful gain.

This recreates the same broad locomotion scope that raw v12 expanded to `0x620E0` and failed at stage load, but v44 remains at `0x5273C`, saving `0xF9A4` bytes relative to v12 while retaining the compact stage selector.

**Partial runtime result / rejected packing bug.** Idle, Walk Forward/Backward, and Turn all work correctly. Pressing Crouch hard-hangs immediately before any crouch frame appears. Static audit found Crouch shape offsets `+0x5037E`, `+0x5113A`, and `+0x51D81`; the first and third are not word-aligned. Because the target dereferences shape/descriptor words with ordinary MIPS word loads, this precisely explains the pre-frame hard hang. The type-5 Crouch encoding itself is not rejected by this result.


## Corrected native type-5 locomotion composition — v45

Disposable proof: `MKMSZR_mkt-sektor-native-type5-locomotion_bundle-proof_v45.z64`.

Identity:

- SHA-256 `602664487903c6706a44e2180c5d0e5e8cfe1ad4899dad4fa4d13a3ea876d43b`;
- CRC1/CRC2 `BE14EAF1 / EC2A122C`;
- file ID `0x87` size `0x52740`.

v45 is a corrective rebuild of v44 with the same genuine Sektor Idle, Walk Forward/Backward, Turn, and Crouch content and the same shared seven-frame Walk type-5 dictionary. The packer now aligns every generated shape record to a 4-byte boundary before emitting its descriptor/image wrapper.

Corrected Crouch shape offsets are `+0x50380`, `+0x5113C`, and `+0x51D84`; all are word-aligned. The only resource-size cost versus v44 is four bytes of padding.

**Runtime-confirmed.** Idle, Walk Forward/Backward, Turn, and Crouch all work correctly; repeated transitions among them remain stable, and Prison's first doorway passes. This confirms the corrected word-aligned packer and shared-Walk native type-5 dictionary composition.


## Accelerated native type-5 crouch-combat composition — v46

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


## Dead-stock reclamation / Prison-Inventory control — v47

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


## Fortress exact-size allocation control — v48

Disposable proof: `MKMSZR_mkt-sektor-idle-stage-select_fortress-size-control_v48.z64`.

Identity:

- SHA-256 `c4324831437bd76563f36961f68ab37c604b93e4b42f11e649b4f38fc9cdfbd9`;
- CRC1/CRC2 `BE14EAF1 / EC2A122C`;
- file ID `0x87` size `0x52740`, exactly matching failing v45.

v48 begins from runtime-confirmed v40. It changes no reachable Sektor frame, script, descriptor, palette helper, selector logic, or stage behavior. The only fighter-resource change is extending file ID `0x87` from `0x4D820` to `0x52740` with `0x4F20` bytes (20,256 bytes) of untouched/unreachable `0xFF` tail padding.

This is the Fortress counterpart to the earlier v41 Prison allocation control.

**Runtime-confirmed failure.** Fortress hangs on the Mission Objective screen before stage music/gameplay exactly as v45/v47 do. Since v40 at `0x4D820` loads Fortress normally, loaded file-0x87 allocation footprint alone is sufficient to cause the Fortress failure at `0x52740`. No exact lower threshold is claimed.


## Compact locomotion Fortress controls — v49 / v50

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


## Full crouch-combat merged-reclamation proof — v51

Disposable proof: `MKMSZR_mkt-sektor-type5-full-crouch-combat_merged-reclaim-proof_v51.z64`.

Identity:

- SHA-256 `6a4d07216cf9acbf30aae513a4787eff5c17eaa836171612d612cc5fa729394e`;
- CRC1/CRC2 `BE14F541 / D5784E8A`;
- file ID `0x87` size `0x5100C`.

v51 preserves the exact 34 unique genuine Sektor frames/actions of v46/v47: Idle, Walk F/B, Turn, Crouch, Crouch Turn, Crouch Block, Crouch Hit, Crouch Punch, Crouch Low Kick, Crouch High Kick, and Standing Block. No action is removed and the established encoder-v2 grammar is unchanged.

The storage planner changes only physical placement. The same 42 file-local-unreferenced stock frame intervals proved by v47 are merged only when byte-contiguous, yielding five reclaimed regions. This allows both Type-5 image streams and whole generated Type-5 model/dictionary tables to occupy the dead stock ranges. The planner uses the full `0x5E6C` bytes of already-proved reclaimed storage while keeping every Sektor shape/subdescriptor in the donor append range so the runtime-confirmed palette helper classification remains unchanged.

File `0x87` drops from v47's `0x52BC0` to `0x5100C`, a further `0x1BB4`-byte reduction with identical mapped content. This is `0x1734` bytes below the exact v48 Fortress allocation footprint that is runtime-confirmed to fail, although the exact Fortress threshold remains unknown.

**Static/implementation-confirmed; runtime pending.** Primary gate: Fortress stage load + Inventory. Secondary gate: Prison first doorway + Inventory and quick animation regression.


## Fortress later allocation boundary — v51 / v52

v51 (`0x5100C`) preserves the complete 34-frame crouch-combat composition and passes the previously failing Prison doorway -> Inventory route. Fortress progresses farther than the earlier `0x52740` failure: stage music begins, but gameplay still does not leave the Mission Objective screen.

v52 is the decisive control: `MKMSZR_mkt-sektor-type5-locomotion_v51-size-control_v52.z64`.

- SHA-256 `02745e4dff4e4a4beaacb928d62915da4fff702c9bfae48fd3154835d59480ef`;
- CRC1/CRC2 `BE14F541 / D5784E8A`;
- file ID `0x87` size `0x5100C`.

v52 starts from fully runtime-confirmed Fortress-working v49 and changes no reachable fighter content. It adds only `0x2AC8` bytes of inert `0xFF` allocation tail so file `0x87` exactly matches v51's footprint.

**Runtime-confirmed failure.** Fortress reproduces v51's later Mission Objective hang with stage music playing. Therefore the `0x5100C` allocation footprint alone is sufficient to cause this later Fortress failure; the additional 17 combat frames present in v51 are not required.

Production-relevant implication: keep optimizing physical file-0x87 footprint. The known real-content working point is v49 at `0x4E544`; v51/v52 at `0x5100C` fail, a gap of only `0x2AC8` (10,952 bytes).


## v53 — common-animation Sektor takeover / native palette

Disposable proof: `MKMSZR_mkt-sektor-common-takeover_native-palette-proof_v53.z64`.

Identity:
- SHA-256 `65181aa5a270ec2ba404d01d02a8054ffba923991408a87465a25515b6b99e7f`;
- CRC1/CRC2 `A6246DD8 / 513DCBF9`;
- file ID `0x87` size `0x473D8`.

**Static/implementation-confirmed; runtime pending.**

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

**Static/implementation-confirmed; runtime pending.**

v56 is intentionally narrow: it keeps v55's already-working Throw, existing Combo mapping, Sweep-Fall safety guard, Push mapping, and all inherited v53 content. Only the six PS1-derived even Run poses are rebuilt.

The corrected PS1 POVBQ emitter follows the native 2-row/4-column vector layout exactly: after the second four-pixel row of a vector it advances the output cursor by four pixels before returning to the first row. Independent comparison against the separate PS1 decoder matches byte-for-byte for `RBRUN2/4/6/8/10/12`; every source frame also spans more than 30 nonzero columns, directly excluding the v55 four-column overwrite failure.

The corrected six full-body frames contain substantially more unique pattern data than the malformed v55 strips. Lossless inclusion would cross the known Fortress allocation boundary, so v56 uses a bounded codebook approximation: 256 supplemental PS1 2x4 patterns, exact transparency masks/silhouettes, and 64 Type-5 entropy models. The resulting six converted even poses have color-space RMSE about 4.504 in 5-bit RGB units and 36.3% exact opaque indices. This is deliberately documented as **lossy color/pattern approximation with exact silhouette**, not as lossless conversion.

Final storage: 158 generated frames, 40,833 shared dictionary patterns, table `0x33789`, padded streams `0x1408C`, file `0x87 = 0x4E414`. Two clean builds are byte-identical and every emitted Type-5 frame round-trips against its selected v56 target buffer.

Runtime gate: ordinary Run must show all twelve full-body poses; v55's tiny-artifact even frames must be absent. Push, Throw, Combo, Sweep Fall, Fortress/Inventory and Prison/Inventory are regressions.

Additional v55 runtime observation: the Sub-Zero combo still reaches six gameplay hits, but at least one middle impact displays an incorrect/neutral Sektor visual. The victim-side “being grabbed/thrown” presentation remains a separate pending mapping family; inherited primary `fb_*` slots `0x26+` are the first static candidates and must be tied to actual MKMSZ call sites before replacement.


**v56 runtime correction:** the six PS1-derived even Run poses still render badly, now as speckled/checkerboard full bodies rather than four-column artifacts. The six N64 odd poses remain clean. Native-palette renders of PS1 odd poses show the same bad internal structure, so this is an upstream PS1 POVBQ interpretation failure, not a Type-5/VQ packing failure. The v56 PS1 Run path is **Rejected**. Sweep Fall/Getup, Throw, Fortress+Inventory, and Prison+Inventory all pass on the tested v56 route.

**Replacement donor path (Static-confirmed):** preserved Midway MK3 `ROBO8.IMG` contains complete raw 8-bit `RBRUN1..RBRUN12` full-body images and `ROBO_P`. N64 MKT source explicitly lists the six even Run poses as cut. Future Run work must first calibrate raw MK3 odd poses against their exact N64 odd counterparts before transferring the even poses.
