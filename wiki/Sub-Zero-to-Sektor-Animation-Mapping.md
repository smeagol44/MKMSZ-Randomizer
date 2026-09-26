# Sub-Zero ↔ Sektor animation mapping

> **Scope:** This page is the canonical reference for **Sub-Zero primary/secondary animation slots, MKT Sektor/robot slots, accepted mapping policy, current mapping coverage, and current remaining gaps**.
>
> It does **not** own version-by-version proof chronology. Exact vNN identities, hashes/CRCs/file sizes where preserved, changed variables, proof allocations/conflicts, manual routes, observations, supersession, and unresolved limits are canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).
## Evidence boundary

- **MKMSZ target:** USA Rev. 0, SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`.
- **MKT donor:** USA Rev. 2, SHA-256 `30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb`.
- MKMSZ Sub-Zero resource: global file ID `0x87`, clean ROM `0x748920..0x78E2FF`, size `0x459E0`.
- MKMSZ animation selector `0x8002FE54`: table 0 at resource `+0x000`; table 1 at `+0x104`.
- The first script after MKMSZ table 1 is at `+0x1B0`, making table 1 exactly **43 entries**.
- MKT robot heap base: donor ROM `0x8881C0`; `robo_anitab1` is heap `+0x000` (**90 entries**) and `robo_anitab2` is heap `+0x168` (**27 entries**).
- MKT names are source-lineage labels; the table offsets below are verified against the supplied retail Rev. 2 ROM.

## Main conclusion

**Static-confirmed:** much of the inherited primary animation layout is shared through the ordinary fighter core, but numeric table position is **not** by itself a MKMSZ product requirement. Ordinary common states in the early table remain the strongest direct graphical-replacement candidates; later reachability tracing shows that MKMSZ repurposes some inherited positions for Mythologies-only control/special data.

Do **not** infer semantic equivalence for secondary tables or for inherited labels whose MKMSZ call sites disagree with the old Midway name. MKMSZ's 43-entry table 1 is Mythologies-specific, while the MKT robot family's 27-entry table 2 contains robot specials and family-shared entries. Secondary mapping must be semantic and reachability-driven.

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
| `0x0D` | inherited `victory` label; MKMSZ selector path has no caller; `+0xD90` is reused by the stock Ice projectile loop | `+0x00D90` | `+0x01148` | **NOT A PLAYER-VICTORY IMPORT REQUIREMENT** |
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
| `0x24` | inherited zap/projectile slot; live MKMSZ Ice-family player-special script | `+0x00DA0` | `+0x001D4` | **HOST-SPECIAL / EXTENSION** |
| `0x25` | inherited dizzy label; no current Sub-Zero/player caller established | `+0x0084C` | `+0x00778` | **NO CURRENT IMPORT REQUIREMENT** |


The detailed runtime progression that originally followed this table has moved to [Sektor takeover proof history](Sektor-Takeover-Proof-History). The table below remains a semantic slot reference; its `DIRECT candidate` labels describe inherited layout compatibility, not an assertion that every row has been individually runtime-tested.

**Reachability rule:** inherited Midway slot names are not requirements by themselves. Primary `0x0D` is the clearest example: its inherited name is `victory`, but no static caller was found for the MKMSZ selector routine that requests `0x0D`. The underlying `+0xD90` script is nevertheless physically live through the stock Ice projectile child, so "not a player Victory requirement" does **not** mean "free storage." Importer semantics and physical-script liveness must be audited separately.

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
| `0x0D` | inherited `victory` label; no MKMSZ Victory requirement established | `+0x00D90` |
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

- **Common direct body:** ordinary primary states with demonstrated shared semantics; use donor-equivalent art first, but do not promote an inherited label into a requirement without MKMSZ reachability evidence.
- **Live host-only state / fallback:** MKMSZ player states that are demonstrably reached but have no established direct donor semantic; preserve host control grammar and choose/compose a donor fallback only after the target state is identified.
- **Character-specific / extension:** MKMSZ powers/projectiles and donor-specific specials, actors, palettes, effects, reactions, and multipart art. These do not belong in the generic body budget.
- **No current import requirement:** inherited/legacy slots with no Sub-Zero/player reachability evidence. Preserve physical data if another alias/reference is live, but do not manufacture donor art merely to fill the slot.
- **Sektor extra donor primary:** donor `0x41..0x59` may supply semantic substitutes only when an actual live MKMSZ state needs one; numeric position is never sufficient.

## MKMSZ player-state reachability audit — 2026-09-25

**Static-confirmed; no ROM built.** The audit used the clean USA Rev. 0 executable and the preserved Ghidra function map, then followed direct calls to `0x8002FE54` plus the stock select/play wrappers used by the player/action machinery.

A critical layout rule is now explicit:

```text
table 0 base = file 0x87 + 0x000
65 table-0 entries -> last entry at +0x100
table 1 base = file 0x87 + 0x104

therefore:
table0 index (0x41 + n) == table1 index n
```

`0x8002FE54` performs no bounds check before indexing. Stock code intentionally uses both forms; for example the main player process requests table-0 index `0x46`, which resolves to secondary slot `0x05`. A generic importer must normalize these aliases before deciding whether a physical script/state is live.

### Current player/importer classification

| Target state | Reachability evidence | Classification / importer consequence |
|---|---|---|
| ordinary mapped primary body states through attacker Throw `0x23` | Existing mapping/proof line; many bounded Runtime-confirmed routes | **COMMON / DIRECT or already-resolved host mapping.** Low Hit `0x1D` remains runtime-unexercised but its direct donor mapping is already present; this is a validation gap, not a missing asset family. |
| primary `0x0D -> +0xD90` | The selector routine at `0x80030064` has no static inbound call/pointer in the clean ROM. Separately, stock Ice child `0x8004B82C` obtains `+0xD90` through file-`0x87 +0xFD0` and uses it as the projectile loop. | **Not a player Victory requirement.** Do not import MKT Victory. The `+0xD90` bytes/art remain physically live while stock Ice compatibility exists, so they are not reclaimable merely because the inherited slot label is unused. |
| primary `0x24 -> +0xDA0`, `0x2C -> +0xDE8`, `0x2D -> +0xE30` | Complete stock Ice action root `0x8004AB84` selects `0x2C`, `0x2D`, and `0x24`; special selector-1 path `0x8004BD28` also selects `0x24`. | **CHARACTER-SPECIFIC / HOST-SPECIAL EXTENSION.** Real MKMSZ states, but not generic fighter-body requirements. Preserve/translate them only for the selected special-move policy. |
| primary `0x25 -> +0x84C` | Only selector found is inside `0x8005578C`; no static inbound call/pointer found for that routine. Primary `0x30` aliases the same script and has no selector access found. | **NO CURRENT PLAYER IMPORT REQUIREMENT.** Do not import donor Dizzy merely because of the inherited name. Keep physical liveness separate if a later caller is discovered. |
| primary `0x28 -> +0x31C` | Player attachment branch at `0x8002A9AC`, following the Turn-triggered `P29` facing transition; token `0x10` drives a second actor with paired visual descriptors. | **HOST-ONLY attachment/turn presentation.** No direct retail Sektor equivalent established; preserve dual-actor grammar or prove a safe single-actor substitute. |
| primary `0x29 -> +0x394` | Player attachment branch calls `0x80030484(0x29)` at `0x8002A970` when semantic Turn/Combine bit `0x0001` is held, then flips actor facing. | **HOST-ONLY attached-turn transition.** No direct retail Sektor equivalent established; a deterministic donor-pose fallback requires a visual/actor proof. |
| primary `0x2A -> +0x244` | Selected at `0x800290A8` when controller health `+0x654` is zero (and attachment `+0x6B0` is clear); leads to terminal state `0x502`. | **COMMON / FALLBACK candidate for player death.** The donor's generic fall/knockdown body may provide art; target death/terminal lifecycle must be retained. No exact donor sequence accepted. |
| primary `0x2B -> +0xEE8` | Ordinary Run setup `0x8002EB38` | **LIVE / SOLVED.** v03–v05 establish donor-count Run scripts, translated cadence, and compact physical storage. |
| primary `0x26` | No static selector request found; script `+0x974` is shared with secondary `0x20`. | **NO PRIMARY-SEMANTIC REQUIREMENT ESTABLISHED.** Shared physical script cannot be reclaimed until secondary ownership is resolved. |
| primary `0x27` | One selector exists inside unreferenced `0x8004CEA4`; slot aliases stance `+0x2EC`. | **No extra fighter art required.** No player requirement established by this audit. |
| primary `0x2E -> +0xD78` | Selector exists in `0x800361E4`, but no static inbound call/pointer was found; the same script is secondary `0x24`. | **NO PRIMARY-SEMANTIC REQUIREMENT ESTABLISHED; physical alias remains conditional.** |
| primary `0x2F -> +0x85C` | Selector exists in `0x80069730`, but no static inbound call/pointer was found. | **NO CURRENT PLAYER IMPORT REQUIREMENT.** |
| primary `0x31 -> +0x1E8` | Selected by `0x80059070`; that routine is present as global reaction callback `0x3A`. | **CONDITIONAL REACTION.** Keep a safe fallback until it is proven whether any stock enemy/route can apply reaction `0x3A` to the Sub-Zero/player actor; do not treat inherited `fb_sheevagoro` as semantics. |
| primary `0x32..0x40` | Stock Sub-Zero table entries are zero. | **No physical fighter-art requirement** unless a future product path deliberately adds one. |

### Secondary-table result

The secondary table is **not** a list of 43 donor poses to fill.

- **Secondary `0x03 -> +0xE84` is live in the main player process** at `0x80029D5C` after global `0x800C2558 == 0x30C`; known producers at `0x80038FC4` (proximity plus interaction bit `0x0002`) and `0x800491CC` install the scripted player callback. The separate standalone Turn helper `0x8003D86C` selects **this same secondary slot**. Although its inbound indirect dispatch is not resolved by direct JAL/J or literal-pointer search, the TURN: LOCK v02 player-gated suppression at this entry is Runtime-confirmed on its tested route. Primary Turn `0x03` is a different script and cannot be silently substituted for both uses.
- **Secondary `0x05 -> +0x290` is live in the main player process** through table-0 alias `0x46` at `0x8002ADDC/0x8002ADE4`. This route changes controller/actor movement flags, enters state `0x30F`, and waits on directional input during attachment/release.
- **Secondary `0x27 -> +0x1B0` is live Push** and is already Runtime-confirmed with the documented Sektor fallback.
- **Secondary `0x0B -> +0xF58` and `0x0C -> +0xE9C` are reachable stock-special states** through special roots `0x8004BD28` and `0x8004B1D0` referenced by dispatch table `0x800A1050`. They belong to the host-special extension budget, not the generic body.
- Secondary `0x00..0x0A` appear in generic fighter/action code, but except for the player-owned cases above this audit does **not** establish Sub-Zero/player ownership for each numeric slot. Do not import donor art merely because generic fighter code can request that index for some actor.
- The many aliases to `+0x928` (secondary `0x0E/0x0F/0x10/0x11/0x13/0x14/0x15/0x18/0x19/0x1F/0x28`) remain **semantic/reachability Pending** for the player. The few constant-selector routines found for that family have no static inbound references; this does not prove the physical block dead because victim/reaction code may reach it by another route.
- Zero secondary entries `0x0D`, `0x12`, `0x25`, and `0x26` require no physical image merely to satisfy the table.

**Audit boundary:** "no static caller found" means no direct JAL/J, literal function pointer, or traced wrapper call was found in the clean base executable for the checked path. It is not a proof that overlays or data-driven indirect dispatch can never reach the bytes. Therefore such states are excluded from the **current importer requirement**, not declared free storage.

### Immediate consequence

The earlier reachability audit isolated `P28, P29, P2A, S03, S05` as its five unresolved player states. The following semantic trace resolves their **host roles** while keeping exact cross-fighter visual policy pending. Victory/Dizzy are not the next common import requirement. Stock Ice-family states stay on the separate special-extension track, and the `+0x928` victim/reaction family remains a later focused reachability trace.

### Five live player states — semantic trace (2026-09-25)

**Static-confirmed in the clean ROM and the preserved Ghidra function map.** Script offsets below are relative to global fighter file `0x87` (`ROM 0x748920`). The script words and decoded stock Type-5 frame silhouettes were checked against the clean ROM; the supplied retail N64 MKT Rev. 2 robot table and scripts were compared separately. These are source/visual inspections, **not** runtime tests or accepted donor-frame mappings. `HOST-ONLY` means the host owns a distinct action/actor lifecycle; a later importer can still reuse donor art after a bounded visual and lifecycle proof.

| State | Selecting condition and player ownership | Script/control grammar and lifecycle | Retail N64 Sektor comparison / decision |
|---|---|---|---|
| **P28** `+0x31C` | Main player `0x8002A9AC`, reached from the attached movement loop after `P29`. Attachment was installed at `0x80025D50..0x80025E10`: reciprocal controller `+0x644`, position/step `+0x668`, attachment flag `+0x6B0=1`, callback `0x80025E48`. The branch initially checks whether the current script cursor matches one of the first eight `P28` words using `0x8002FE90`; this is *not* a collision or donor-slot lookup. | Starts with zero delimiters and two identical frame words; the live body at `+0x32C..+0x38B` repeats token `0x10` plus **two distinct image descriptors** eight times, then loops with `1,+0x32C` at `+0x38C`. Token `0x10 -> 0x80030B6C` creates/reuses controller `+0x650` companion actor, copies pose/flags/palette, synchronizes positions through `0x80031394`, and binds one descriptor to the companion and one to the owner; this cannot be replaced with a plain one-frame script by numeric substitution. `0x8002A9B4..0x8002A9F4` deliberately skips two zero-terminated runs before advancing. | Sektor primary `0x28 -> +0xDA0` is an inherited fatality/reaction sequence with token `0x0A`, not this paired traversal presentation. **HOST-ONLY;** no direct equivalent. Exact support/companion disposal on every detach path remains to be tested. |
| **P29** `+0x394` | In the same player attachment loop, semantic Turn bit `0x0001` with `s3==0` selects `P29` at `0x8002A954..0x8002A970`; the control then flips owner facing at `0x8002A9A0` (`0x8003188C`) and selects `P28`. Ground Turn is a separate action. | Three token-`0x10` pairs (`+0x394..+0x3B7`) continue the same two-actor presentation; token `2,0` at `+0x3B8` ends it. The caller sleeps `4` ticks between two manual `0x800304C0` advances, then `4` more before facing flip. The exact first-frame priming is governed by `0x80030484` and its initial immediate advance. | Sektor primary `0x29 -> +0xDEC` is another inherited reaction, not attached turning. **HOST-ONLY;** a reusable donor-facing interpolation remains a visual candidate, not an approved direct mapping. |
| **P2A** `+0x244` | Main player death branch `0x80029034..0x80029138`: `+0x654` is health (damage subtraction/clamp at `0x8002E28C..0x8002E2B0`); when zero and attachment `+0x6B0` is clear, it selects `P2A`, sets `+0x6AA=0x502`, and never resumes ordinary input. Existing `0x509` state is excluded. | `0x8002B1C0` zeros actor velocity; two `0x80031070(5)` calls play the selected script. It begins with body frames at `+0x244..+0x254`, includes control words `6,1` at `+0x258` and `+0x268`, and proceeds into a descending/kneeling terminal pose; sound/action helpers execute before `0x8002912C`'s sleep loop. Intervening `0x800572C4/0x80057478` conditionally transform *other* fighter types and do not redefine the player death entry. | Sektor primary `0x2A -> +0xE38` is an inherited reaction. Ordinary donor knockdown `0x1E -> +0x808` is a plausible **COMMON / FALLBACK art source**, but its return/getup grammar is unsuitable as the terminal death script. Preserve MKMSZ death timing and lifecycle; visual acceptance is Pending. |
| **S03** `+0xE84` | Main player state dispatch `+0x6DC=0x16` enters `0x80029D0C`; only global `0x800C2558==0x30C` selects it. The flag/state are installed by at least `0x80038FA4..0x80038FCC` (position/facing proximity plus interaction bit `0x0002`) and `0x800491A0..0x800491E8` (scripted event with item `0x23`). Separately, the Runtime-confirmed TURN: LOCK v02 gate at `0x8003D86C` supports a standalone Turn use of S03, with its indirect inbound dispatch unresolved. | Five body frames `+0xE84..+0xE94` ending in zero at `+0xE98`; the decoded pose extends an arm. The scripted player path manually advances through `0x800304C0`, sleeping `6` ticks while the global flag is set; after the flag clears, it rewinds cursor `8` bytes and replays the tail every `6` ticks until terminator `2`, then exits the player process. `0x8003D86C` instead has its own movement and `0x80031070(2)` runner; these are two lifecycles for the same art. | Sektor robot secondary `0x03 -> +0x1494` is telepunch, not this host turn/gesture. **HOST-ONLY** presentation, with a possible common donor reaching/turn-pose fallback **unproven**; no generic direct animation established across both uses. |
| **S05** `+0x290` | Main player transition at `0x80029148..0x8002916C` checks negative actor `+0xE8` and the non-default collision/attachment callback before entering `0x8002ADB0`. It selects table-0 index `0x46`, which aliases **secondary 5**, and installs state `0x30F`. The stock decoded body frames show raised arms, consistent with an overhead attachment/release presentation. | Eight frames `+0x290..+0x2AC`, zero at `+0x2B0`, then six frames `+0x2B4..+0x2C8` looping with `1,+0x2B4`. The caller resets attachment-related actor flags, waits `4` ticks, runs `0x80031070(4)`, installs rate `4` through `0x80031724`, sleeps/advances with `0x8003174C`, then branches on Up `0x1000`/Down `0x4000` and actor facing/motion. Release continues through `0x8002AEF8..0x8002AF68`; attachment cleanup is not just an animation terminator. | Sektor robot secondary `0x05 -> +0x13A0` is a robot target/special entry, not this host traversal state. **HOST-ONLY;** no direct donor equivalent established. A generic raised-arm donor fallback would require a bounded pose and state-transition proof. |

#### P28/P29 companion ownership and teardown (2026-09-25)

**Static-confirmed in clean NMYE Rev. 0 ROM disassembly; no runtime test.** Token `0x10` enters shared `0x800304C0 -> 0x80030B6C`. Its eight P28 and three P29 entries are `[0x10, companion descriptor, owner descriptor]`. The first P28 pair is file-`0x87 +0x330/+0x334` (ROM `0x748C50/0x748C54`); the first P29 pair is `+0x398/+0x39C` (ROM `0x748CB8/0x748CBC`). The companion entries are narrow secondary images (first P28 visible geometry `12x32`, owner `32x132`), so assigning a complete donor body to both entries would duplicate art.

| Boundary | Established ownership and effect |
|---|---|
| Create/reuse `0x80030B6C..0x80030C68` | If current controller `+0x650` is null **or** global `0x8009F744` is nonzero, acquire a `0x118`-byte actor from `0x800245A4`, save it at `+0x650`, initialize actor-local render record `+0x7C = actor+0x108`, copy owner color bytes `+0xA0/+0xA4/+0xA8`, `+0xD8`, ordering `+0x5C`, flags `+0x8C/+0x64`, then insert it once with `0x80024650` into actor list `0x80111C98`. The creation branch clears `0x8009F744`; clean ROM data initializes it to `1`. With an existing pointer and zero flag, the insertion/allocation branch is skipped. No direct non-token writer of this flag was found in the scanned clean executable; broader initialization/indirect writes remain unresolved. |
| Every token `0x10`, `0x80030C68..0x80030E44` | Refresh color bytes and copy owner palette selector `+0x9E`, resource base `+0x98`, frame/position `+0x34`, and flags; clear companion `+0x64` bits `0x20` and `0x10`; copy controller texture slot `+0x6E8` into actor `+0x9C`; adjust scale/facing; align via `0x80031394`; bind the **next** descriptor to companion and the following one to owner with `0x8001BDA0`. Neither descriptor word acquires a separate resource handle. Companion has no independent controller/process. |
| Leave token / park `0x800304C0+0x30524..+0x30548` | When the current controller equals player `0x802C1AC0`, the token differs from `0x10`, `+0x650` exists, and `0x8009F744 == 0`, set companion actor `+0x64` bit `0x20`. The actor render/update path `0x80018784..0x80018788` skips its visible draw branch when that bit is set. This path does **not** unlink/free it or clear `+0x650`. Next token `0x10` clears bit `0x20`, refreshes its bindings and reuses it. The P29 terminator `2,0` parks it before the owner facing flip at `0x8002A9A0`; P28 resumes via `0x8002A9AC..0x8002A9F4`. |
| Detach/interruption | Normal player detach `0x8002A850..0x8002A8E0` clears reciprocal controller `+0x644`, `+0x69C`, and attachment `+0x6B0`, then `0x8002FF50` selects ordinary slot 0 and `0x800304C0` advances its non-`0x10` script, parking the companion. Shared `0x80032AF8` also severs reciprocal attachment links and `+0x6B0` on interruption, but has **no** direct companion operation; a later non-`0x10` advance is required for visual parking. The timing and completeness of every interrupted callback remain unresolved. |
| Death / reinitialization | Main player death `0x80029044..0x800290A8` requires `+0x6B0 == 0`; while attached, main process enters `0x8002A6A0` instead of directly selecting P2A. `0x8002ECF4..0x8002ED80` creates a fresh player controller and zeros `+0x638..+0x6D7`, including `+0x650`. This does not itself prove actor-list teardown at stage exit, title return, Game Over, or death while an attachment callback is active. |

**Strong inference:** Repeated normal attach/detach/reattach within one live player instance uses one listed, parked/reused companion and requires no new texture or palette allocation per cycle. Companion `+0x9E` and `+0x9C` copy the owner's existing palette selector and texture slot; the trace contains no per-companion palette acquisition, texture allocation, release, or `0x80024B00` unlink. The owner resource/palette/texture must therefore remain valid while either actor can render. Stage-wide actor-list reset and unusual interruption timing are **unresolved**, not a proven release contract. `0x800304C0` and token `0x10` are shared fighter machinery; modifying the token handler or global flag for a player-only donor visual is unsafe without separate cross-fighter coverage.

The safest bounded visual seam is the paired **file-`0x87` descriptor operands** in P28/P29, preserving token words, cursor grammar, original owner/companion actor creation and parking, rate, reciprocal attachment links, and `0x8003188C` facing flip. Translate retail N64 MKT donor art into target-native Type-5 descriptors under current file/storage and palette ownership rules; account for the companion's separate, narrow visual layer instead of drawing two complete bodies. Do not allocate an extra actor, texture slot, or palette merely to substitute poses. The first disposable proof should change just the first paired entry of P28 and first paired entry of P29, keeping other entries stock as diagnostic controls, then validate attachment, attached Turn, Up/Down motion, detach, and reattach before broadening the manifest. Such a proof only validates the changed frames and tested route, not the stage/death teardown.

**Limits:** The attachment geometry suggests overhead traversal, supported by arm-raised stock silhouettes and the Up/Down controlled step counter, but the exact stage object name and every stage-wide teardown edge have not been established. A safe generic visual fallback cannot be declared from one still pose. The static scan alone does not resolve the standalone Turn's indirect dispatch to `0x8003D86C`; its bounded v02 runtime gate evidence and the separate scripted S03 use must both be retained. No PS1/WIMP/arcade poses were used to close donor gaps.

#### Direct selector inventory and ownership boundary

The clean base executable has additional **direct** selector sites. They are listed here so the main-player path is not mistaken for exclusive ownership. Sites inside a shared fighter routine select for the **current controller**; without its inbound actor route, the site alone does not prove that the player or an enemy takes that branch. This inventory excludes computed indices and data-driven/indirect script entry.

| State | Direct selector sites beyond the main player route | Scope finding |
|---|---|---|
| `P28` / `P29` | No second constant selector established beyond `0x8002A9AC` / `0x8002A970 -> 0x80030484` | The observed owner is the player attachment branch; its companion is an actor, **not** a second fighter controller selecting P28/P29. |
| `P2A` | `0x80056B40` selects primary `0x2A`, after writing current controller state `0x502` at `0x80056B20`; its own script runner advances every `6` ticks at `0x80056B48..0x80056B8C`. | Additional scripted death/terminal presentation through the current controller; this does not make donor primary `0x2A` a direct semantic match. Actor/overlay-specific reachability still needs a separate route trace. |
| `S03` | Secondary `3`: `0x8003D878`, `0x8003E1FC`, `0x80040870`, `0x80040A14`, `0x800414F0`, `0x80045010`, `0x80045488`, `0x80047E74`; main-player `0x80029D5C` above. | Shared action/reaction routines can select the same art for other current controllers. `0x8003D86C` has separately Runtime-confirmed Turn-gate impact; the scripted `0x30C` route remains independently live. Primary `3` selectors are **not** S03. |
| `S05` | Secondary `5`: `0x8003D8E8`, `0x8003F348`, `0x8003F8CC`, `0x8003FAC8`, `0x80040F90`, `0x80042724`, `0x8004573C`, `0x80045ACC`, `0x800486D8`, `0x800495A0`; main-player alias `0x8002ADDC` above. | Several shared fight/reaction routines select S05 and some attach another actor at controller `+0x648`; this does not establish that *their* motion lifecycle is the same as the main player's `0x30F` route. Primary `5` selectors are **not** S05. |

The read-only P28/P29 companion audit resolved the safe visual seam: preserve stock token-`0x10` actor ownership and narrow companion descriptors, and substitute only the owner descriptor operands. Disposable proof `MKMSZR_sektor-p28-p29-owner-probe_common-proof_v06.z64` (SHA-256 `b4b098a411ad5712b3574cc96f8667a7684d2927e9c4df900af52792e9ede644`, CRC1/CRC2 `A6256BDA / C01C8AB6`) uses genuine retail N64 Sektor owner art in the first P28/P29 pair while keeping the companion side stock-derived. **Runtime-confirmed on the tested rope path:** the stock Sub-Zero arm companion animates while attached; Sektor and the arm both turn together through P29; detaching parks/removes the visible arm; reattaching restores it; no duplication, lingering image, corruption, or freeze was observed. This proves imported owner art can coexist with the host-owned token-`0x10` companion grammar on this bounded route. The intentionally mixed visual is diagnostic, not an accepted final fallback manifest. Interruption timing and complete stage/state teardown remain untested limits.

## Current mapping coverage

The takeover remains **proof-only**, but the current slot mapping is much broader than the original direct-core candidate table:

| Area | Current mapping/evidence |
|---|---|
| Primary direct core `0x00..0x22` | Broad genuine-Sektor coverage exists. Many individual locomotion, crouch, ground-combat, airborne, hit/getup, and reaction states were Runtime-confirmed in isolated/bundled proofs. v53 then established the Sektor-first common-animation takeover baseline. |
| Low Hit `0x1D` | Exact direct mapping is present, but v34 did not obtain a practical runtime trigger. Treat the mapping as established but that exact state as **runtime-unexercised**. |
| Elbow / Combo `0x10` | Genuine Sektor visuals are mapped; v59 Runtime-confirms the repaired middle Combo visuals on the tested route. |
| Throw attacker `0x23` | The attacker-side Sektor/mechanical-arm presentation is mapped through the flattened target representation; later takeover routes carried the Grab/Throw repair successfully. Victim-side grabbed/thrown reactions remain a separate gap. |
| Ordinary Run | **Runtime-confirmed accepted design:** use only the six retail N64 MKT Run poses `RBRUN1,3,5,7,9,11`, at target Run rate **3** (~100 ms/pose), followed immediately by loop control back to the Run root. v03 Runtime-confirms the translated cadence; v04 Runtime-confirms that the live MKMSZ Run script can contain exactly six visual entries rather than preserving Sub-Zero's historical 12-entry layout. Donor frame count and target cadence are therefore independent importer properties. |
| Gameplay combo graph | v62 Runtime-confirms the tested Sektor MKT combo strings after translating donor reaction selectors to MKMSZ-native semantics. This is semantic/gameplay proof coverage, not production integration. |
| Straight-missile presentation | v69 Runtime-confirms the genuine chest-open pose can be installed safely on the player for one frame through the resolved animation cursor. v70 Runtime-confirms a genuine horizontal rocket frame can reach and travel as the projectile. The helper-clone/palette/spawn/flight behavior is still wrong, so this is **partial presentation coverage**, not an accepted special-move mapping. |
| Alternate Scorpion/type-`0x12` palette | v60 Runtime-confirms the first yellow/gold Cyrax-style alternate palette on its tested route. This is proof-history evidence rather than an animation-slot mapping rule. |

Coverage statements are deliberately bounded. A later takeover proof can demonstrate that a composition works without proving every mapped slot individually, and a static mapping does not become Runtime-confirmed merely because neighboring states were exercised.

### Accepted six-pose Run integration and cadence

The accepted Sektor integration/repack removes the six supplemental even Run poses from the physical resource and keeps only the six retail N64 MKT poses:

`RBRUN1, RBRUN3, RBRUN5, RBRUN7, RBRUN9, RBRUN11`

**Static-confirmed donor script:** retail MKT Sektor primary slot `0x4A` points to heap `+0x1444`, whose words are:

`+2708, +271C, +2730, 6, 8, +2744, +2758, +276C, 1, +1444, 0`

The six frame words are `RBRUN1,3,5,7,9,11`. Control pair `6,8` is the donor animation callback/footstep event and consumes no independent frame hold; `1,+0x1444` jumps back to the Run root.

**Static-confirmed cadence:** ordinary retail MKT Run setup selects slot `0x4A`, indexes rate table `0x800A7E08` by fighter ID, and passes the selected byte to donor rate initializer `0x8000E13C`. Retail Sektor is fighter index `7`, whose table byte is `6`. Its ordinary Run loop performs `process_sleep(1)` then donor rate advance `0x8000E184` once per iteration. On the 60-Hz donor scheduler, one pose therefore lasts `6/60 = 100 ms` after the initial primed advance.

MKMSZ ordinary Run setup `0x8002EB38` selects primary slot `0x2B -> file 0x87 +0xEE8` and calls `0x80031724(2)`. The active Run loop sleeps with `0x80028794(1)`, then calls `0x8003174C` once per gameplay scheduler iteration. That scheduler runs once per main gameplay iteration, while the loop waits for two retrace increments before the next iteration, so the target Run advance call is approximately 30 Hz. Native rate 2 therefore makes one script entry last about `2/30 = 66.7 ms`.

This resolves the two manual tests:
- `1,3,5,7,9,11,1,3,5,7,9,11` at native rate 2 gives ~66.7 ms/pose and a ~400 ms six-pose cycle: **too fast** versus MKT's ~600 ms cycle.
- `1,1,3,3,5,5,7,7,9,9,11,11` at native rate 2 gives ~133.3 ms/pose and an ~800 ms cycle: **too slow**.
- target Run rate **3** gives `3/30 = 100 ms` per script entry, matching MKT's `6/60 = 100 ms` steady-state dwell exactly without inventing intermediate poses.

**Runtime-confirmed proof sequence:** v03 (`MKMSZR_sektor-run-cadence_common-proof_v03.z64`, SHA-256 `b46b283189b4dfd4d4c144f5405b5b4b165953e6897890b3d2065cb43901847e`) changed only the Run-rate immediate at `ROM 0x2F7A0 / VA 0x8002EBA0` from `24040002` to `24040003`; the user reported that cadence felt correct. v04 (`MKMSZR_sektor-run-six-entry_common-proof_v04.z64`, SHA-256 `f805a283180486c144910f9627856a85a5eb633b679d62cdf2dee01e6fd571af`) then changed only the live Run script control flow so the loop token `1,+0xEE8` follows immediately after the sixth genuine pose; the user reported it worked perfectly. The old second six-pose copy remains physically present but unreachable in v04, intentionally separating script-length semantics from physical repacking.

Because the accepted six-pose Run no longer needs the rejected PS1-derived Run path or the later WIMP-derived even-pose repair assets, future Sektor builders should remove those Run-only inputs/decoders/dependencies rather than carry them forward as dead build requirements. Historical v55-v58 provenance remains documented in proof history and asset translation.

**Generic importer rule (Runtime-confirmed at Sektor scope):** do not normalize Run to a fixed MKMSZ visual-entry count. Emit exactly the donor Run frame sequence that exists for that fighter, then append the target loop/control grammar and translate donor time to the target animation-rate mechanism independently. A donor fighter with 7 Run frames should therefore receive a 7-frame target Run script, not padding, truncation, duplication, or a forced 12-entry container.

The physical-removal repack is **Runtime-confirmed** as v05: `MKMSZR_sektor-run-compact-six-pose_common-proof_v05.z64`, SHA-256 `3073bd0b77e88a8bb1ea22a5a45ce1fe933512434188e9c578c35adb4f4f5363`. It contains 152 generated frames and 40,577 shared patterns; file `0x87 = 0x4CD68`, saving `0x1694` = **5,780 bytes** versus the `0x4E3FC` v58-style resource and increasing v49-bound headroom from `0x148` to `0x17DC`. The builder no longer accepts or references PS1/WIMP Run inputs. The user manually tested v05 and reported that it works perfectly, closing the compact Run storage gate at Sektor scope.

## Current remaining gaps

The current canonical gaps are:

- finalize and runtime-prove the donor fallback/presentation policies for the five Static-confirmed live main-player host states `P28`, `P29`, `P2A`, `S03`, and `S05`; their host semantics are now identified, and inherited `fb_*` names are explicitly not accepted as MKMSZ semantics;
- Low Hit `0x1D` still lacks a practical direct runtime trigger despite its exact mapping; this is a validation gap, not a missing donor asset;
- victim-side Grab/Throw/reaction ownership, especially the shared `+0x928` family, remains a focused reachability/semantic gap;
- stock Ice-family presentation (`P24/P2C/P2D`, indirect `+0xD90`, `S0B/S0C`) is a **character-specific host-special extension**, not common body coverage; donor special-move behavior belongs to [MKT adapter primitives](MKT-Adapter-Primitives) and the host ABI to [Player actions and special moves](Player-Actions-and-Special-Moves);
- primary reaction callback `P31` remains conditional until reaction `0x3A` is tied to or excluded from player-victim routes;
- inherited slots with no player reachability evidence are not importer TODOs merely because the table contains a pointer;
- imported fighter asset/codec/palette/storage rules belong to [MKT fighter asset translation](MKT-Fighter-Asset-Translation);
- proof allocations do not become production-safe through successful testing. Literal ownership and the v62 bootstrap conflict remain canonical in [Memory and allocation map](Memory-and-Allocation-Map).

## Evidence and production boundary

The accepted design is a genuine donor-to-target translation, not a behavioral approximation. Numeric slot equality is used only where semantics are actually shared; secondary/special tables remain semantic mappings.

The Sektor line is not a normal browser/CLI feature. Current proof success establishes mapping and translation feasibility on bounded routes. Production integration would still require conflict-free allocation/composition, guarded build integration, and the project's normal runtime validation gate.

## Related pages

- [Sektor takeover proof history](Sektor-Takeover-Proof-History) — canonical vNN chronology, proof identities, routes, results, supersession, and proof allocation conflicts.
- [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer) — accepted cross-game porting strategy and compatibility contract.
- [MKT adapter primitives](MKT-Adapter-Primitives) — donor semantic translation.
- [MKT fighter asset translation](MKT-Fighter-Asset-Translation) — donor image/codec/palette conversion and stable Type-5 packing conclusions.
- [Player actions and special moves](Player-Actions-and-Special-Moves) — MKMSZ host action ABI.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and production/proof conflicts.
