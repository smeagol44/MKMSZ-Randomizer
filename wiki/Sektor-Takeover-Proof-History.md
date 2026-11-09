# Sektor takeover proof history

> **Scope:** This page is the canonical owner of the **versioned Sektor takeover proof chronology**. It records vNN artifact identity where preserved, hashes/CRCs/file sizes, the changed variable, proof allocations/conflicts, manual runtime route, final evidence status, positive and negative observations, supersession, and unresolved limits.
>
> Animation-slot tables, mapping policy, current coverage, and current gaps belong to [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping). Stable donor image/codec/palette/Type-5 packing conclusions belong to [MKT fighter asset translation](MKT-Fighter-Asset-Translation). Donor semantic translation belongs to [MKT adapter primitives](MKT-Adapter-Primitives). The MKMSZ host action ABI belongs to [Player actions and special moves](Player-Actions-and-Special-Moves). Literal production/proof allocation ownership belongs to [Memory and allocation map](Memory-and-Allocation-Map).

## Current conclusion

The Sektor takeover line is **Runtime-confirmed as a bounded proof workstream, not a production feature**.

The stable common-animation/combo baseline remains v62: the tested Sektor MKT combo strings work after translating donor reaction selectors to MKMSZ-native semantics. v58 remains the Runtime-confirmed twelve-pose Run baseline; v59 Runtime-confirms the completed middle Combo visuals; v60 Runtime-confirms the first type-`0x12` alternate Cyrax-style palette.

The straight-missile line has user runtime evidence through **v89**. v75 is the last stable tested flight baseline. v80 constructor-only and v83 raw pre-insertion frame binding retain the Ice-derived first frame and blue missile; v81/v82 and v84 remove that first frame but produce a sparse rocket. The static cause of the controls is the ordinary parent-to-child frame schedule and separate palette ownership, not a missing same-shape texture rebuild. On straight mode zero, `0x8004B028` skips the v75 parent wrapper; `0x8004B584` advances a stock Ice frame after token construction, and the child later advances file-`0x87 +0xD90` to the rocket. v83's early bind is overwritten by that parent advance. v84 moves the controller cursor to rocket loop `+0xD90` before insertion and, under selector zero, the initial Ice-derived frame is no longer visibly recognizable; v88 later proves that descriptor/cursor advance alone does not make the correct rocket texture synchronously ready. v81/v82/v84 force selector zero, which maps to fixed handle `0x80`; the player's Sektor palette has its own dynamic selector. v82 only makes the active handle agree with that same wrong selector. The exact palette words in handle `0x80` during the capture were not read, so pixel-level attribution remains an inference. v85 is **built, runtime untested, and statically rejected** for the ordinary straight route: it suppresses token insertion globally, while its only deferred reinsertion sits in the parent wrapper that this route skips. `0x80024B00` cannot free an actor never linked into the active list. v63–v79 history remains recorded below, with v78/v79 hang causes unresolved. The canonical host trace is [Player actions and special moves](Player-Actions-and-Special-Moves).

The strongest current production conflict remains the proof-code line inside the production bootstrap composite `[0x9AD84,0x9AF20)`. v62's standalone combo continuation uses `[0x9AD90,0x9ADA0)`; v65-v70 helper code begins at `0x9ADA0`, with v70 using the same proof-owned interval up to the bootstrap boundary. These artifacts validate semantics only; none of those offsets are reusable production allocations. The early Sektor helper line demonstrates the same rule from the opposite direction: zero-filled-looking `[0xA1308,0xA1544)` was live stock action/dispatch data, and overwriting it caused input-specific hangs.

## Six-pose Run branch and cadence reconciliation

A separate 2026-09-25 branch tested reducing ordinary Run presentation back to the six retail N64 MKT poses.

- **Run branch v01 — Runtime-confirmed / timing superseded.** `MKMSZR_sektor-run-six-pose_common-proof_v01.z64`, SHA-256 `7f8dc72abb39e5863b64730eb669bed41bb3d308a063905fb6d6aaf9b8a21e1d`. The existing 12 visual entries are `1,1,3,3,5,5,7,7,9,9,11,11`. It was initially preferred relative to v02, but the later clarified observation is that it still feels **too slow**.
- **Run branch v02 — Runtime-confirmed / timing superseded.** `MKMSZR_sektor-run-six-pose-double-loop_common-proof_v02.z64`, SHA-256 `68c4a258eb4d6caf40cb639ea2d7fe36ed2a8b856fbab026188fdccae297bb92`. Sequence `1,3,5,7,9,11,1,3,5,7,9,11` keeps one script entry per pose; the later clarified observation is that it feels **too fast**.
- **Static cadence reconciliation — 2026-09-25.** Retail MKT Sektor slot `0x4A -> +0x1444` contains exactly the six visual poses plus callback/loop control. Ordinary donor Run uses fighter-indexed rate `6` for Sektor and advances once per 60-Hz Run-loop tick, yielding ~100 ms/pose. MKMSZ ordinary Run `+0xEE8` installs rate `2` and advances once per ~30-Hz gameplay scheduler tick, yielding ~66.7 ms per script entry. Thus v01 holds each pose for ~133.3 ms and v02 for ~66.7 ms; they correctly bracket the donor. Rate **3** yields ~100 ms/pose.
- **Run branch v03 — Runtime-confirmed cadence.** `MKMSZR_sektor-run-cadence_common-proof_v03.z64`, SHA-256 `b46b283189b4dfd4d4c144f5405b5b4b165953e6897890b3d2065cb43901847e`, CRC1/CRC2 `A6256DDA / 3EF7DDCE`. Reuses v02's two consecutive six-pose cycles unchanged and changes only ordinary Run setup `ROM 0x2F7A0 / VA 0x8002EBA0: 24040002 -> 24040003`. The user reported the result felt really good. This promotes the rate-3 cadence mapping to Runtime-confirmed on the tested route.
- **Run branch v04 — Runtime-confirmed variable-length script.** `MKMSZR_sektor-run-six-entry_common-proof_v04.z64`, SHA-256 `f805a283180486c144910f9627856a85a5eb633b679d62cdf2dee01e6fd571af`, CRC1/CRC2 `A6256DDA / 3EF7DDCE`. Relative to v03, only the seventh/eighth live Run-script words are changed: the seventh visual pointer becomes loop token `1` and the next word becomes `+0xEE8`. The resulting live script is exactly `RBRUN1,3,5,7,9,11,1,+0xEE8`; the old second six-pose cycle remains physically present but unreachable. The user reported it worked perfectly. This proves MKMSZ ordinary Run does not require the historical twelve visual entries and validates donor-count-length scripts at Sektor scope.
- **Run branch v05 — Runtime-confirmed compact physical repack.** `MKMSZR_sektor-run-compact-six-pose_common-proof_v05.z64`, SHA-256 `3073bd0b77e88a8bb1ea22a5a45ce1fe933512434188e9c578c35adb4f4f5363`, CRC1/CRC2 `A624B5FA / 2240BC7D`; builder `MKMSZR_build_sektor_run_compact_six_pose_v05.py`. v05 preserves the Runtime-confirmed v04 live Run grammar and target rate 3, physically removes the six WIMP-derived even Run poses, and removes all PS1/WIMP Run build dependencies. The generated corpus is 152 frames, 64 models, 40,577 shared patterns, table `0x33289`, padded streams `0x12FA0`, and file `0x87 = 0x4CD68`, exactly reproducing the prior static-removal estimate and leaving `0x17DC` below the bounded v49 comparison footprint. Two clean builds are byte-identical; every generated Type-5 frame passes the builder's independent round-trip verification. The user manually tested v05 and reported that it works perfectly, promoting the compact six-pose resource path to Runtime-confirmed at Sektor scope.
- **Physical-removal repack — Implementation/static-confirmed, Runtime Pending.** Repacking with only the six physical retail Run poses yields file-`0x87 = 0x4CD68` versus `0x4E3FC`, saving `0x1694` / 5,780 bytes and increasing v49-bound headroom from `0x148` to `0x17DC`.

**Integration directive:** future Sektor/importer work should use the donor fighter's actual Run-frame count, emit target loop/control grammar immediately after that sequence, and translate timing through the target animation-rate mechanism independently. Do not pad, duplicate, truncate, or force Run into Sub-Zero's historical 12-entry layout. Physical integration should still remove the six supplemental even Run assets and now-dead PS1/WIMP Run dependencies. Historical v55-v58 evidence remains canonical provenance and should not be erased.

### P28/P29 attachment owner-probe — 2026-09-25

- **Owner-probe common-proof v06 — Runtime-confirmed on the tested rope route.** `MKMSZR_sektor-p28-p29-owner-probe_common-proof_v06.z64`, SHA-256 `b4b098a411ad5712b3574cc96f8667a7684d2927e9c4df900af52792e9ede644`, CRC1/CRC2 `A6256BDA / C01C8AB6`; builder SHA-256 `1820ddae85304699a987ee3ea0e9771a7ad6002f1f1c58b49b89ffc9441cb0eb`. This is a bounded diagnostic derived from the compact common-animation line, not a finished visual mapping. It preserves the stock P28/P29 token-`0x10` grammar, timing, facing flip, attachment logic and narrow companion visual controls, while substituting only the first owner-side descriptor in P28/P29 with genuine retail N64 Sektor art. The user observed the stock Sub-Zero arm companion moving while attached; both Sektor and the arm turned together; the arm vanished on detach and returned on reattach; no duplication, lingering image, corruption or freeze was observed. This Runtime-confirms owner/companion coexistence and normal park/reuse on the tested rope route. It does not establish complete interruption, death-while-attached, stage-exit or old-actor teardown behavior, and the mixed Sektor/stock-arm presentation is not an accepted final fallback pose manifest.

## Build-kit reproduction and takeover change map (2026-11-07)

**Implementation/static-confirmed reproduction; no new runtime evidence.**

**The kit.** The user supplied `MKMSZR_sektor-investigation_build-kit_v01.zip` (SHA-256 `776b29700a7b52312e7dc00d682fcf88b74d7eada25b3250b6dd370180af4b77`). It contains:

- 50 unchanged original builders (takeover v53/v54 legacy, v54–v62, missiles v63–v89, Run v01–v05, the palette and owner probes);
- 14 historical v57 scripts;
- the recovered-source bridge for v53/v54;
- exact XOR-delta replays of 73 earlier artifacts (Sektor v01–v53, Reverse Elbow v1–v8.3, Reptile A1–v08);
- an entry point `build.py` that hash-checks every output.

The kit is research provenance and belongs in the Library. Only its original builders are mirrored in the repository under `Experimental/SektorTransplantBuilders/original_builders/`.

**Reproduced in a cloud session from the clean MKMSZ and MKT inputs.** Targets v55–v62 and v64 onward also need the user-supplied PS1 MKT members `CHARS1/ROBOT.DAT` (`99c5ae8c…bedd0`) and `CODE/ROBOT.BIN` (`d5c2752c…935d6`). Every output below matched its recorded identity; CRC1/CRC2 are read from the rebuilt ROMs.

| Target | Output SHA-256 | CRC1 / CRC2 |
|---|---|---|
| Run v05 | `3073bd0b77e88a8bb1ea22a5a45ce1fe933512434188e9c578c35adb4f4f5363` | `A624B5FA / 2240BC7D` |
| Owner probe v06 | `b4b098a411ad5712b3574cc96f8667a7684d2927e9c4df900af52792e9ede644` | `A6256BDA / C01C8AB6` |
| Takeover v53 (recovered source) | `65181aa5a270ec2ba404d01d02a8054ffba923991408a87465a25515b6b99e7f` | `A6246DD8 / 513DCBF9` |
| Takeover v54 | `7f11e7e462a8e9a5fb028a62e5281989480dd3eb19bdc5d281241113caf1876a` | `A6256DA8 / 9F9B13D5` |
| Takeover v62 (via v59 → v60) | `689862a64ab2cfe04041fae357a19774e335cea39eff6c9d6f5ae143f601e1fd` | `B4234446 / 80A601BE` |
| Missile v75 (via v70 → v72 → v73) | `e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb` | `29C9C3E6 / 61EE1EE8` |
| Missile v89 | `582b255ca3c5ef2cc008444403c1bb5b0379c91c16e6d5f9079da2cdc5ac0d89` | `9F889E81 / 0EDEC067` |
| 16-colour palette proof v01 (from v75) | `e339d75c396b09a10b8c6a4fd1cab76efb5a99dda30d98c6524c029ad6fa3a59` | `29C9C3E6 / 61EE1EE8` |
| Reverse Elbow v8.3 (replay) | `37c58380396eaadd36bd9441a5aac0b0504b0628420cd97adb4a5df204365cc2` | `700C2641 / A5F16487` |
| Reptile v08 (replay) | `1ea40452cdf6e8866b48544fc57f27b065dace75fa0416d52fb4987db61f936d` | `70135E41 / BB4C161F` |

The 16-colour proof is `MKMSZR_sektor-16color_common-proof_v01.z64`, built by `MKMSZR_build_sektor_16color_v01.py` (SHA-256 `73fa9318a757989847cc6e7a9e9e439fd6099ce43f12c69d415e9ff129a9b305`). It was previously recorded only as the visually accepted policy proof in [MKT fighter asset translation](MKT-Fighter-Asset-Translation#accepted-generic-16-color-normalization-direction). Its CRCs equal v75's because it changes only data beyond the first MiB.

**Takeover change map (word diff against the clean ROM, outside the relocated file).** Static-confirmed for these exact builds.

| Region | Present in | Meaning |
|---|---|---|
| `0xA5664/0xA5668` | all | File-`0x87` table entry relocated to `0xF40000` (end `+0x4CD68` in v05, `+0x4E154` in v54) |
| `0xDD60`, `0xE028`, `0x15CD0` → `0x9A700` cave, `0x7A3F4`, `0x9B7F4` | all | Early randomizer test harness, not fighter code: stage clamp, Safe Stage Select callback, stage-selector mapper, logo bypass and the selector list. See [Stage flow and selector](Stage-Flow-and-Selector) |
| `0x2F7A0` | Run v03–v05 | Run rate `2 → 3` |
| `0xA1CE8`, `0xB1CB4..0xB1D10` | v62 line | Combo-table data |
| `0x4AFAC..0x4C48C`, `0x9AD90..0x9AF1C`, `0xB1B4C` | v75 / v89 | Ice-action hooks, proof code in the bootstrap-conflict interval, and Ice-path data |
| `0x315C8`, `0x316C8` | v89 only | Token-`0x0B` palette-call and actor-insertion call sites |

The fighter-body takeover itself is therefore **data only**: a replacement file `0x87`.

**Script structure.** v54, v62, v05 and v89 keep the stock Sub-Zero script control structure across `+0x1B0..+0x1000`:

- **Unchanged:** the counts of tokens `2, 3, 5, 6, 10, 11, 16` and the callbacks.
- **Frame references:** most of the roughly 500 changed words are frame references.
- **Redirected roots:** five slot roots point elsewhere (`0x09`, `0x11`, `0x12`, `0x1A`, `0x20`).
- **Shortened loops:** six looping scripts are cut to donor length by a new loop jump right after the donor frames. These are `+0x300→+0x2EC` (Idle), `+0x3DC→+0x3C0` and `+0x408→+0x3EC` (Walk), plus `+0x4F8→+0x4E4`, `+0x670→+0x654` and `+0x7D8→+0x7C4`. Some stock jumps become unreachable as a result.
- **Run (v05):** the Run script is exactly the donor robot Run sequence with donor callback `6,8` removed and the loop jump retained, adding `+0xF00→+0xEE8`. This directly evidences the importer rule that donor scripts must be fitted into the host phase layout except where the layouts already match; see [MKT adapter primitives](MKT-Adapter-Primitives#animation-script-grammar-translation).

## Reconciled status rules

A proof entry may preserve its historical **pre-test** status, but the section's final status is always the latest recorded evidence. In particular:

- **v52:** final status is **Runtime-confirmed failure**. Earlier runtime-pending wording is superseded; file-`0x87` footprint `0x5100C` alone reproduces the later Fortress Mission Objective hang with stage music.
- **v53:** final status is **Runtime-confirmed common-takeover baseline**. Fortress, Prison, Inventory, representative common actions, and demo movies passed on the tested routes; the original "runtime pending" heading was pre-test wording.
- **v54:** final status is **partially Runtime-confirmed / superseded**. Its composed strategy exposed wrong Run/Push ownership, a Sweep-Fall hard hang, and Throw palette/timing defects that v55 addressed.
- **v55:** final status is **partially Runtime-confirmed; Run rejected/superseded**. The PS1-derived even-Run import was malformed; the carried-forward repair line continued into v56.
- **v56:** final status is **partially Runtime-confirmed; PS1 Run rejected**. The even poses rendered as speckled/checkerboard bodies, while Sweep Fall/Getup, Throw, Fortress+Inventory, and Prison+Inventory passed on the tested route.
- **v57:** final status is **Runtime-confirmed Run failure** caused by ignoring aligned WIMP source-row pitch; its earlier "in-progress/runtime pending" note is historical context only.
- **v58/v59/v60/v62:** each has an explicit later Runtime-confirmed result within its bounded route. v61 remains **Rejected / failed**.
- **v63:** **Rejected / failed.** The special itself was still XP-gated, and normal hit testing exposed a hard hang plus blood/effect corruption after the proof reused an incorrectly classified file-`0x87` bank.
- **v64:** **Partially Runtime-confirmed / presentation rejected.** The special path executes with the compact chest/missile assets, but the player does not enter the chest pose; duplicate frozen/blue helper actors appear, the projectile flashes a Sektor fallback, and flight remains Ice-like.
- **v65-v67:** **Rejected / failed.** All three hang immediately after the correct chest visual appears or the special begins; restoring only the first Ice helper process in v67 changes the extra visual but not the hang.
- **v68:** **Runtime-confirmed stable negative control.** Full stock Ice lifecycle no longer hangs, but the attempted temporary animation-table substitution does not display the chest frame.
- **v69:** **Runtime-confirmed narrow chest-pose hook.** Post-helper substitution through current process `+0x6E4` plus one stock frame advance displays the genuine chest-open frame for one frame and continues safely.
- **v70:** **Partially Runtime-confirmed / implementation strategy superseded.** Chest presentation and a genuine rocket frame execute and travel, but the Ice helper clones/palette remain and the user reports spawn far from Sektor, slow motion, and no visible donor-style acceleration.
- **v71:** **Rejected / failed.** Hard hang 1-3 frames after `F,F+LP`. Post-test static trace rejects the wrong-actor placement hypothesis and identifies per-tick reuse of `0x8004CC14` as a semantic mismatch; sole hang cause remains Pending.
- **v72:** **Runtime-confirmed placement proof.** Direct `(+5,+38)` native placement launches close to Sektor and mirrors correctly in both facings; visible Y may still be slightly high, while constant-speed flight and blue Ice tint remain unchanged controls.
- **v73:** **Runtime-confirmed acceleration behavior / calibration Pending.** Missile visibly accelerates and remains stable; exact donor-equivalent start speed/rate/cap in MKMSZ physical units are not yet established.
- **v74:** **Runtime-confirmed stable cadence resampler / magnitude under-scaled.** Comparative donor/target video shows similar ~0.3 s ramp timing but about half the donor's late normalized on-screen speed on the tested route; a separate donor-local -> target-world scale remains Pending.

## Final-status index

| Proof | Final evidence status | Smallest meaningful result / limit |
|---|---|---|
| v01 | **Partial Runtime-confirmed / failed lifecycle proof** | Genuine Sektor idle rendered, but transition corruption and input-specific hangs remained; the active-palette-handle omission was Static-confirmed as a defect, not proven as the sole cause. |
| v02-v07 | **Rejected / failed isolation line** | Successive palette, cursor, rate-hook, and wrapper controls narrowed the failure without fixing it; exact identities and negative-control details are restored below. |
| v08 | **Runtime-confirmed correction** | Restoring the exact stock action/dispatch records removed the input-specific hangs; this causally rejected the false zero-cave allocation. |
| v09 | **Runtime-confirmed except one transition artifact** | Re-homed palette helper/state in owned proof memory restored correct colors and stability; one frame-transition artifact remained until v10. |
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
| v63 | **Rejected / failed** | Four-frame missile/chest proof reused a falsely classified file-`0x87` bank; normal hit/blood presentation hard-hangs before the XP-gated missile can be meaningfully tested. |
| v64 | **Partial Runtime-confirmed / presentation rejected** | Compact one-chest/one-missile composition executes, but the reused Ice presentation produces duplicate/fallback Sektor actors, distant spawn, and constant Ice-like flight. |
| v65 | **Rejected / failed** | Correct chest art appears on the player, then the game immediately hangs after replacing stock lifecycle behavior and suppressing both Ice helper-process spawns. |
| v66 | **Rejected / failed** | Mirroring the stock animation runner inside the replacement wrapper does not change the immediate hang. |
| v67 | **Rejected / failed** | Restoring the first Ice helper-process spawn changes the visible extra object but the move still hangs immediately. |
| v68 | **Runtime-confirmed stable negative control** | Stock Ice lifecycle/processes/projectile run without hanging; temporary table substitution does not reach the real player-animation cursor, so no chest pose appears. |
| v69 | **Runtime-confirmed narrow hook** | Post-helper process-`+0x6E4` cursor substitution plus one native frame advance displays the chest-open pose for one frame and returns safely. |
| v70 | **Partial Runtime-confirmed / strategy superseded** | Genuine chest and rocket visuals execute and the rocket travels, but Ice clones/tint remain and spawn/velocity/acceleration do not match the intended donor behavior. |
| v71 | **Rejected / failed** | Combined placement/setup-helper experiment hard-hangs; per-tick `0x8004CC14` reuse is a static semantic mismatch, but the sole hang cause is unresolved. |
| v72 | **Runtime-confirmed** | Direct donor-retail local `(+5,+38)` placement is stable and mirrors correctly. |
| v73 | **Runtime-confirmed behavior / calibration Pending** | Direct per-tick projectile `+0x14` acceleration is stable. |
| v74 | **Runtime-confirmed** | Folded donor cadence is stable; tested visible magnitude remained roughly 2x low. |
| v75 | **Runtime-confirmed baseline** | Doubled host magnitude on the folded cadence feels correct on the tested route; current stable missile-flight baseline. |
| v76 | **Rejected / ineffective** | Presentation hold/Y changes do not materially solve presentation. |
| v77 | **Stable negative result** | Owner-Y/rocket-anchor reset does not materially change the head-height spawn. |
| v78 | **Rejected / failed** | Direct `0x80031394` origin/facing alignment shim hard-hangs at this lifecycle seam. |
| v79 | **Rejected / failed composition** | Five simultaneous presentation/contact changes hard-hang; no individual edit is causally isolated. |
| v80 | **Runtime-confirmed stable negative presentation result** | Correct live constructor operand alone does not remove the Ice-blue first projectile presentation or companion actors. |
| v81 | **Partial Runtime-confirmed** | Removes the one-frame blue projectile fallback, but selector zero selects a different palette source; the exact captured TLUT contents are unknown. |
| v82 | **Runtime-confirmed stable negative control** | Explicit selector-0 active-handle rebind makes no visible difference from v81; stale `+0x80` alone is rejected. |
| v83 | **Runtime-confirmed stable negative result** | Raw post-init/pre-insertion `0x8001BDA0` rocket bind leaves the same first Ice/Sektor projectile frame and Ice-blue missile. |
| v84 | **Partial Runtime-confirmed** | Early contextual bind removes the one-frame Ice/Sektor fallback, but the missile remains glitched; first-visible timing is proven, early rocket state is not viable. |
| v85 | **Built; Runtime untested; statically rejected on straight mode zero** | Built, **runtime untested**; static control flow bypasses its sole deferred insertion on ordinary straight shots, leaving an unlisted actor and unbalanced removal. Do not advance this candidate. |
| v86 | **Partial Runtime-confirmed** | Correct dynamic palette-source ownership materially improves the rocket, but the resident Sektor TLUT remap is grayscale/quantized and cannot reproduce donor-faithful rocket colors. |
| v87 | **Runtime-confirmed asset/palette success; first-frame mismatch remains** | Exact retail ROCKETD1 + ROCKET_P renders the flying missile with correct donor-like colors. The earlier one-frame Ice-derived projectile still appears, now visibly corrupted because it is rendered through the rocket palette. |
| v88 | **Partial Runtime-confirmed / first-frame texture still stale** | Flying missile remains correct, but the one-frame corrupted Sektor-like texture still appears. Early descriptor/cursor binding is therefore not sufficient to make the finalized projectile texture slot ready before publication. |
| v89 | **Runtime-confirmed first-visible rocket success** | Synchronous native texture-slot preparation before actor publication removes the one-frame corrupted Sektor while preserving the donor-faithful ROCKETD1/ROCKET_P missile and v75 flight machinery. |

## Detailed chronology — v01-v27

These entries restore the exact pre-Task-11 proof detail from commit `986cc631e6f2dc9a242540567c73da3b00f648d5`. Each entry begins with the **current reconciled final status**; any older hypothesis or intermediate wording below is subordinate to that status. All entries remain disposable proof evidence, not production allocation or integration.

## v01 — genuine Sektor rendering confirmed, transition cleanup failed

**Final status: Partial Runtime-confirmed / failed transition-lifecycle proof.** Genuine five-frame Sektor idle rendering worked, but the one-frame transition corruption and crouch/forward hard hangs remained; the missing active-handle restoration was a Static-confirmed defect and only a strong inference as the complete cause.

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v01.z64`

Runtime result reported by the user:

- standing neutral visibly renders Sektor "in all its glory";
- the genuine five-frame Sektor stance is therefore **Runtime-confirmed** in MKMSZ;
- leaving idle can show a single corrupted/weird transition frame;
- attempting to crouch from Sektor idle caused a whole-emulator/game hard hang immediately after Down was pressed.

The donor decoding, dimensions, row stride, palette choice, and idle-script resource are therefore not the current failure. The failure is at the idle-exit ownership/lifecycle boundary.

Static re-audit found a concrete v01 defect:

1. v01 saved/restored actor palette selector `+0x9E`;
2. it did **not** save/restore the resolved active palette handle at actor `+0x80`;
3. on a non-idle selection it restored `+0x9E` and released the temporary Sektor palette immediately;
4. until native frame setup rebound a stock palette, actor `+0x80` could still refer to the released donor palette slot.

That is a real use-after-release window and is consistent with both the one-frame corruption and crouch hang. The structural defect is **Static-confirmed**; it remains a **strong inference** that this is the complete runtime cause until the corrected proof is tested.

## v02 — active-handle restoration fix

**Final status: Rejected / failed as a complete fix; donor rendering remains Runtime-confirmed.**

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v02.z64`

Identity:

- SHA-256 `d5df6193d6b942664ff02367037e55f58683a439d11f4926646c71ddd46a182c`;
- CRC1/CRC2 `35B9266E / F0DB463F`.

v02 is built from the clean supported target ROM. The imported Sektor resource block is byte-for-byte identical to v01. The isolated change is palette-transition bookkeeping:

- save stock selector `actor+0x9E`;
- save stock active palette handle `actor+0x80`;
- on idle exit restore **both** fields;
- only then release the temporary donor palette;
- retain donor idle speed 8 only while the Sektor idle binding is active.

**Rejected / failed as a complete fix; donor rendering remains runtime-confirmed.**

Further user runtime testing showed the same single-frame corruption and hard hangs. The trigger is selective rather than simply "any animation change": block, punches, kicks, turning, walking backward, and ordinary jumping can work, while crouching, walking forward, and adding forward drift during an already-running jump can hard-hang immediately. The supplied 12.7-second capture is especially constraining because the final failure occurs after a stock jump is already visibly underway; adding forward movement freezes the game without a visible animation change first.

The capture also shows the transient corrupt frame when returning from stock actions to Sektor idle (approximately 4.5 s and 7.0 s in that recording). This narrows that artifact separately to the idle-entry presentation boundary.

## v03 — restore the stock resource table; redirect only the idle cursor

**Final status: Rejected / failed as a hang fix; donor rendering remains Runtime-confirmed.**

Static re-audit found a stronger structural problem in v01/v02. The relocated Sub-Zero resource was copied intact except that its actual table-0/index-0 word was permanently changed from stock `+0x2EC` to appended Sektor script `+0x459E0`. This means the proof globally replaced the resource's stance entry, rather than limiting the foreign animation to the `select_animation(0,0)` call. Static target code contains resource-table reads outside `0x8002FE54`, so a permanent table mutation can affect stock state/locomotion code even when no visibly new animation has been selected.

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v03.z64`

Identity:

- SHA-256 `222fb08985f30f78b2628e74ea24b21c2ac26701f4bc81450be574a21be908ca`;
- CRC1/CRC2 `40543A98 / EE1442F8`.

v03 is built from the clean supported ROM and keeps the donor frames/palette/timing identical to v02. Its isolated change is:

- the relocated first `0x459E0` bytes of Sub-Zero's resource are byte-for-byte identical to the clean stock file, including table-0/index-0 = `+0x2EC`;
- the appended Sektor data remains outside that stock range;
- only an exact Sub-Zero idle request `(table 0,index 0)`, while the isolated donor palette is owned by the same actor, writes controller `+0x6E4 = resource_base + 0x459E0`;
- all non-idle calls continue through the stock `select_animation` tail and all other resource-table consumers see stock data.

**Rejected / failed as a hang fix; donor rendering remains runtime-confirmed.**

The user repeated the same forward, airborne-forward, crouch, safe-action, and transition tests. v03 behaved **exactly like v02**, including hard hangs at the same failing inputs and the same transient corrupt frame. Therefore permanently replacing the table-0/index-0 word was not the cause of the hang.

This negative result materially narrows the failure: the common foreign state that remains during Sektor idle is the **live animation cursor itself**, which v03 still redirected from the native Sub-Zero stance region into the appended Sektor script. Static target code snapshots, compares, and advances controller `+0x6E4` directly in several helpers outside simple `select_animation` calls, so cursor locality/lifecycle is now the leading hypothesis.

## v04 — native cursor location with foreign frame pointers + diagnostic HUD

**Final status: Rejected / failed before gameplay; the native-cursor hypothesis was not tested cleanly because the added diagnostic HUD confounded the build.**

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v04.z64`

Identity:

- SHA-256 `295480a5596dd9c6a09be3dbc7899c3d6c2b6a1e0c2193c0624834a7ef3ee385`;
- CRC1/CRC2 `36AD42FB / 615A2E42`.

v04 keeps the relocated Sub-Zero resource table unchanged and no longer redirects `controller+0x6E4` to appended script `+0x459E0`. Instead, it preserves the native table-0/index-0 target and native cursor location at resource `+0x2EC`, replacing only the first seven words of that native idle script with:

```text
Sektor RBSTANCE1 shape
Sektor RBSTANCE3 shape
Sektor RBSTANCE5 shape
Sektor RBSTANCE7 shape
Sektor RBSTANCE9 shape
command 1
self +0x2EC
```

All other bytes in the original `0x459E0`-byte Sub-Zero resource are unchanged. The appended donor shapes, raw CI buffers, converted Sektor palette, and donor idle rate 8 remain the same as the earlier proofs.

v04 also adds proof-only native HUD instrumentation through the already runtime-confirmed gameplay text path. The bottom readout is:

`P# C# L# X#`

where the digits encode donor-palette ownership, whether the live animation cursor is inside the native idle-script range, the low nibble of controller locomotion state, and the low nibble of normalized action input. This instrumentation is diagnostic only and is not a product UI design.

**Rejected / failed before gameplay; cursor hypothesis not tested.**

The user reported that v04 reached the Mission Objective display, stage music began, and then the game/emulator hung before gameplay appeared. Because v04 introduced both the native-cursor experiment and a new diagnostic HUD wrapper at the same time, this result is confounded and does **not** establish whether the native-cursor strategy is valid.

Static re-audit found that the v04 diagnostic wrapper read controller/actor state from the gameplay HUD path without first proving that a live player context existed. The Mission Objective flow can execute that HUD path before normal gameplay control is established, so the diagnostic code is a **strong candidate** for the pre-game hang. This is not runtime-confirmed as the sole cause until an otherwise-identical no-HUD build is tested.

Historical context from the earlier Reverse Elbow/Reptile proof is important here: a separate diagnostic path was already runtime-confirmed during gameplay, displaying forms such as `IN XXXXXXXX L0 P0 A00` through the native HUD/text path and surviving repeated special activations. Future instrumentation should reuse that proven pattern rather than the unguarded v04 wrapper.

## v05 — v04 cursor experiment with diagnostic HUD removed

**Final status: Rejected / failed as a hang fix; stage-start isolation succeeded and identified the v04 diagnostic HUD as the pre-game confound.**

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v05.z64`

Identity:

- SHA-256 `8be8bf1e1aa066483043c528623c8f7ff08c40042d786a5d62ef97a2ac1dd5e9`;
- CRC1/CRC2 `BFDA3A1F / 1142C1A6`.

v05 is byte-for-byte v04 except for removal of the proof-only diagnostic HUD hook/wrapper/string and the resulting header CRC change. It therefore preserves the intended v04 animation experiment unchanged:

- native Sub-Zero table-0/index-0 still points to resource `+0x2EC`;
- the live animation cursor remains in that native idle-script region;
- only the first five idle-frame pointers plus the native loop command/self-offset are replaced to render the genuine Sektor stance;
- donor palette ownership and idle rate remain as in the earlier proofs.

**Rejected / failed as a hang fix; stage-start isolation succeeded.**

The user confirmed that v05 enters gameplay normally, proving the v04 pre-game Mission Objective hang came from the added diagnostic HUD rather than the native-cursor experiment. Once gameplay begins, however, v05 behaves like v02/v03: Sektor idle renders, but forward movement, crouch, and airborne forward drift still hard-hang at the same points. The native-cursor-at-`+0x2EC` hypothesis is therefore **Rejected / failed** as the cause of the gameplay hang.

This result leaves a smaller set of implementation pieces common to all failing Sektor builds: resource relocation/foreign shape use, temporary palette ownership/select-animation wrapper, proof state storage, and the donor-rate hook.

## v06 — remove only the donor animation-rate hook

**Final status: Rejected / failed as a hang fix.** Removing only the donor animation-rate hook did not remove the input-specific hangs.

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v06.z64`

Identity:

- SHA-256 `06b1eb0d3a964d2b42f4ba8006a646c700fde08ab97700a3082001c8471e06da`;
- CRC1/CRC2 `4753AA06 / DACEC518`.

v06 is byte-for-byte v05 except for restoring the clean stock bytes at ROM `0x32324..0x3232B` / VA `0x80031724..0x8003172B`, removing the proof's animation-rate interception entirely. Sektor therefore runs at MKMSZ's stock cadence rather than donor rate 8. No imported frame, resource, palette, select-animation, or state-storage bytes changed.

**Rejected / failed as a hang fix.**

The user reported that v06 still hard-hangs on the same forward movement, crouch, and airborne-forward inputs. Therefore the donor animation-rate hook is **not** the cause of the gameplay hang.

At this point the persistent one-frame corruption on animation transitions can no longer be treated as confidently cosmetic. The strongest common remaining suspect is the temporary donor-palette/select-animation wrapper and its render-state transition, which is also the code path most directly associated with the visible corrupt transition frame.

## v07 — remove dynamic donor palette handling entirely

**Final status: Rejected / failed as a hang fix; palette presentation was separated from the hang cause.**

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v07.z64`

Identity:

- SHA-256 `aa989a2dc74fa577245c3d9895d2471035ad7cb9544b62487e4a8f8d85c2a8f8`;
- CRC1/CRC2 `3884563E / AF3FDC3B`.

v07 is byte-for-byte v06 except for restoring the clean stock first two instructions of target `select_animation` at ROM `0x30A54..0x30A5B` / VA `0x8002FE54..0x8002FE5B`. This completely bypasses the Sektor proof's dynamic palette wrapper and temporary owner/selector state while preserving the native-cursor idle script and imported Sektor frame resources.

Expected presentation: the genuine Sektor stance geometry/animation should still render, but with Sub-Zero's stock palette, so colors may be wrong. That visual degradation is intentional.

**Rejected / failed as a hang fix; palette presentation cause separated from hang cause.**

The user confirmed that v07 still hard-hangs on the same forward movement, crouch, and airborne-forward inputs. The visible result changed substantially: all five Sektor stance frames now render with wrong/corrupted colors under Sub-Zero's stock palette. This establishes that the dynamic donor-palette path is required for correct Sektor presentation, but it is **not** the cause of the hard hang.

This also separates the symptoms: the transition/frame color corruption is palette/render-state related, while the input-specific hard hang persists without any Sektor palette wrapper execution.

### Corrected false-cave finding

Static re-audit found a more fundamental proof error common to v01-v07. The helper was placed at ROM `0xA1308..0xA1543` / VA `0x800A0708..0x800A0943` because the clean bytes were zero. That region is **not unowned free space**.

A live pointer table begins at ROM `0xA15C4` / VA `0x800A09C4` and points to twelve 0x78-byte records:

```text
0  0x800A049C  callback +0x10 = 0x8003C870
1  0x800A0514  callback +0x10 = 0x8003C9B4
2  0x800A058C  callback +0x10 = 0x8003C984
3  0x800A0604  callback +0x10 = 0x8003C848
4  0x800A067C  callback +0x10 = 0x8003C94C
5  0x800A0424  callback +0x10 = 0x8003C7E8
6  0x800A06F4  callback +0x10 = 0x8003C7F0
7  0x800A076C  stock record is all zero
8  0x800A07E4  stock record is all zero
9  0x800A085C  stock record is all zero
10 0x800A08D4  stock record is all zero
11 0x800A094C  stock record is all zero
```

The Sektor helper overwrote most of zero records 7-10 and part of the surrounding record area with executable instructions. Zero bytes here are therefore **semantic data, not a code cave**. An input/action scan that expects those records to remain zero can observe nonzero garbage fields or bogus callback values. This is a strong static explanation for why only selected inputs hard-hang.

This supersedes every earlier statement treating `0x800A0708..` as free proof storage.

## v08 — restore the false cave to exact stock data

**Final status: Runtime-confirmed correction.** Restoring the false cave to exact stock action/dispatch data removed the input-specific hard hangs on the tested route; donor colors were intentionally not restored in this control.

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v08.z64`

Identity:

- SHA-256 `d842c51bf1253ccd0fece0f255e804a4077907aa55fc759fb54b61dde6b1d9be`;
- CRC1/CRC2 `C2435AAC / EBC131C0`.

v08 is byte-for-byte v07 except for restoring ROM `0xA1308..0xA1543` to the clean ROM's exact stock zero-filled record data and recalculating the header CRC. Because v07 already restored the stock `select_animation` entry and removed the rate hook, no Sektor helper code is needed for this test.

Active Sektor changes remaining in v08 are therefore only:

- relocated/expanded file ID `0x87`;
- native idle script frame pointers changed to the five appended genuine Sektor shapes;
- appended donor frame/texture data.

The palette remains intentionally stock Sub-Zero, so Sektor is expected to look color-corrupted exactly as in v07.

**Runtime-confirmed.**

The user confirmed that v08 no longer hard-hangs: forward movement, crouch, and airborne forward drift all work. The Sektor stance still renders with intentionally wrong colors because the donor palette wrapper remains disabled.

Because v08 differs from v07 only by restoring the falsely claimed cave to its exact stock zero-filled dispatch records (plus header CRC), this establishes the root cause of the input-specific hard hangs as the overwritten live action/dispatch data. The failure is therefore **Runtime-confirmed**, not merely inferred.

The durable safety rule is: ROM `0xA1308..` / VA `0x800A0708..` is not generic free space. In particular, the zero-filled 0x78-byte records referenced by the live table at VA `0x800A09C4` are semantic dispatch data and must remain stock unless deliberately decoded and modified.

## v09 — re-home palette helper into owned reserved runtime memory

**Final status: Runtime-confirmed safe proof architecture except for one transition-frame artifact.** The helper/state were re-homed into explicitly owned proof memory.

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v09.z64`

Identity:

- SHA-256 `8d702002ef5b5ac8b8a9289e7b4f059ad92fd28c64a425bb240d86a6b6bf0829`;
- CRC1/CRC2 `2A920945 / 02213D28`.

v09 is built from the runtime-confirmed v08 behavior and reintroduces only the corrected dynamic Sektor palette path in explicitly owned proof memory:

- the existing 1 KiB arena reservation `0x801AF420..0x801AF81F` is enabled through the current proven two-site reservation;
- file ID `0x1B` loads a bounded 0x300-byte proof payload from ROM `0xF10000` to RDRAM `0x801AF420`;
- the existing runtime-confirmed stage-load bootstrap loads that payload before gameplay;
- the palette helper is at `0x801AF440`;
- its temporary state is at `0x801AF700`, inside the same explicitly reserved proof payload;
- target `select_animation` redirects only its first two instructions to that owned helper, which then resumes at stock `0x8002FE5C`;
- the false cave `0x800A0708..` remains byte-for-byte stock;
- the donor animation-rate hook remains disabled, so this proof uses MKMSZ's stock idle cadence.

The helper retains the corrected v02 palette bookkeeping: save stock selector and active palette handle, allocate/bind the genuine Sektor palette for exact idle selection, restore both stock fields before release on exit.

**Runtime-confirmed except for one transition-frame artifact.**

The user confirmed that v09 restores Sektor's correct donor colors while preserving the v08 hang fix: forward movement, crouch, airborne forward drift, attacks, blocking, turning, and jumping all work. The falsely claimed global cave remains stock and the re-homed helper in the reserved runtime block is therefore **Runtime-confirmed** as a safe proof architecture.

One defect remains: a single visibly corrupted frame still appears at animation transitions. Static trace of target `select_animation` explains the timing: `0x8002FE54` only changes controller animation cursor `+0x6E4`; it does not install the first new shape immediately. v09 changes palette ownership during `select_animation`, so one render interval can briefly combine the previous shape with the new palette (and vice versa on exit).

## v10 — bind palette atomically inside native frame setup

**Final status: Runtime-confirmed.** Frame-setup-time palette binding removed the transition artifact on the tested route.

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v10.z64`

Identity:

- SHA-256 `a4890654d3266346ea5d44775f44c3f2be515e5928adbd141e949ebf0e3d87fa`;
- CRC1/CRC2 `DAAD01D9 / BED5AF87`.

v10 preserves the runtime-confirmed v09 resource relocation, genuine five-frame Sektor idle, owned 1 KiB runtime allocation, and stock locomotion behavior, but restores target `select_animation` completely to stock.

Instead, v10 hooks native frame setup `0x8001BDA0` through the owned helper at `0x801AF440`. The helper identifies a Sektor frame only when the incoming shape pointer lies inside the appended Sektor-shape/resource range of relocated file ID `0x87`.

On Sektor frame installation:

1. allocate/reuse the genuine donor palette;
2. set actor `+0x9E` to the donor selector;
3. call the original frame-setup body;
4. native frame setup resolves that selector and writes the matching active handle to actor `+0x80` in the same synchronous call.

On the first stock frame after Sektor:

1. restore the saved stock selector;
2. call the original frame-setup body so native code installs the stock shape and active palette together;
3. release the donor palette only after stock frame setup has completed.

This removes the v09 interval in which palette ownership changed before the new shape was installed. The false cave remains exact stock data; the donor-rate hook remains disabled so cadence is still the MKMSZ stock rate for this proof.

**Runtime-confirmed.**

The user reported v10 as fully correct: genuine Sektor idle renders with the proper donor palette, normal movement/actions remain stable, and the last one-frame transition corruption is gone. This runtime-confirms frame-setup-time palette switching as the correct boundary for the tested Sektor idle replacement.

The current strongest bounded claim is therefore:

> **Runtime-confirmed:** a genuine five-frame MKT Rev. 2 Sektor idle animation can cleanly replace MKMSZ Sub-Zero's ordinary idle state, with correct donor colors, both stock action transitions and locomotion remaining stable, and no visible transition corruption in the user's tested route.

## v11 — destructive idle replacement proof

**Final status: Runtime-confirmed.** Destructive idle replacement behaved like the proven v10 baseline.

Disposable proof:

`MKMSZR_mkt-sektor-idle_destructive-swap_proof_v11.z64`

Identity:

- SHA-256 `37faf7fe07cd6dfe84cd65f39cdd67482a601135ad9342f6dd927a49cf98b128`;
- CRC1/CRC2 `DAAD01D9 / BED5AF87`.

v11 starts from runtime-confirmed v10 but deliberately discards the replaced Sub-Zero idle assets instead of keeping a recoverable in-ROM backup. The active relocated resource's unreachable old idle-script tail and stock idle-frame bundles that are no longer referenced are zeroed; the inactive original ROM copy's complete stock idle script/frame region is also zeroed. One stock frame that is still referenced elsewhere is retained.

The donor conversion still uses relocated/extra physical storage because the decoded row-aligned type-0 Sektor frames are substantially larger than the original compressed Sub-Zero idle bundle. This is a storage-format constraint, not an attempt to preserve runtime switching.

**Runtime-confirmed.** The user tested v11 and reported behavior identical to the perfect v10 result. This confirms that preserving a recoverable in-ROM copy of the replaced idle animation is unnecessary for the current build-time graphics-swap goal.

## v12 — destructive idle + locomotion replacement

**Final status: Rejected / failed at stage load.** The large raw file-`0x87` expansion is the leading allocation/resource-pressure explanation, not a proven animation-semantic fault.

Disposable proof:

`MKMSZR_mkt-sektor-locomotion_destructive-swap_proof_v12.z64`

Identity:

- SHA-256 `bf02b4ba3fca25a9e6a2362ec6e84e18a2550d9a2f54182fe5b3fe94ad693094`;
- CRC1/CRC2 `DAA12659 / 3F399A9B`.

v12 extends the runtime-confirmed destructive v11 architecture to the next direct primary-table block:

- slot `0x00`: Sektor stance/idle, unchanged from v11;
- slot `0x01`: Sektor walk forward;
- slot `0x02`: Sektor walk backward;
- slot `0x03`: Sektor turn;
- slot `0x04`: Sektor duck/crouch.

Exact retail donor scripts used:

```text
walk forward: RBWALK1,2,3,5,7,8,9, ANI_JUMP, self
walk backward: RBWALK9,8,7,5,3,2,1, ANI_JUMP, self
turn: RBTURN1, RB2VICTORY2, ANI_FLIP, RBTURN1, 0
duck: RBDUCK1, RBDUCK2, RBDUCK3, 0
```

The N64 retail CUT_FRAME branch is therefore preserved. Twelve unique Sektor frames are decoded from donor codecs 22/24 with the exact robot dictionary, converted to MKMSZ type-0 row-aligned indexed buffers, and appended to the relocated Sub-Zero file.

The expanded target resource is now:

- ROM `0xF40000..0xFA20DF`;
- size `0x620E0`;
- donor frame materialization begins at resource `+0x4D7D0`;
- the converted Sektor palette moved to resource color pointer `+0x6209C`;
- the runtime-confirmed frame-setup helper's donor upper bound and palette pointer were updated to that new value.

The old false cave remains stock. No donor-rate hook is enabled.

Destructive policy is retained:

- the inactive original-ROM copies of the replaced walk/turn/duck scripts and frame bundles are erased;
- in the active relocated file, the old walk and turn bundles plus duck frames 1/2 are erased after their scripts are replaced;
- stock duck frame 3 remains because unswapped crouch-derived actions still reference it. It is shared live data, not a backup.

The 0x148C0-byte ROM extension beyond v11's resource end was verified to occupy the existing all-`0xFF` disposable tail and does not overlap another global-file-table entry. File ID `0x1B` remains the proof runtime payload and file ID `0x87` alone owns the expanded fighter resource.

**Rejected / failed at stage load.**

The user reported that v12 hangs on the Mission Objective screen before stage music begins. Gameplay is never reached, so this result does not test the imported walk/turn/duck animation behavior itself.

The primary structural difference from runtime-confirmed v11 is resource growth: materializing the twelve new locomotion frames as MKMSZ type-0/raw buffers expanded file ID `0x87` from `0x4D820` to `0x620E0`, an additional `0x148C0` bytes (~82 KiB). Because the failure occurs before gameplay and before music, resource-load/allocation pressure is the leading hypothesis rather than a frame-transition fault. This is **Hypothesis / strong inference**, not yet proven.

## v13 — compact native type-4 locomotion materialization

**Final status: Rejected / failed for fighter-frame storage.** Type-4 storage reached gameplay but produced severe ghosting/smear.

Disposable proof:

`MKMSZR_mkt-sektor-locomotion_compact-swap_proof_v13.z64`

Identity:

- SHA-256 `30170bed6011c1ba98c57e69b8a3b2532f56a57a4bf9f12652a041cbf5e19cad`;
- CRC1/CRC2 `DAA36F59 / 4CB3375F`.

v13 preserves the same direct animation mapping as v12:

- slot `0x00` Sektor idle;
- slot `0x01` Sektor walk forward;
- slot `0x02` Sektor walk backward;
- slot `0x03` Sektor turn;
- slot `0x04` Sektor duck/crouch.

The difference is storage only. The twelve added locomotion frames are decoded from the exact MKT Rev. 2 robot streams and then re-encoded into MKMSZ's native type-4 embedded-image format rather than stored as type-0/raw buffers. Software decode verification proves every v13 type-4 block reproduces the exact donor-decoded row-aligned pixel buffer used by v12.

Resulting file ID `0x87`:

- ROM `0xF40000..0xF9473F`;
- size `0x54740`;
- only `0x6F20` bytes larger than runtime-confirmed v11, versus v12's `0x148C0`-byte growth;
- false cave remains exact stock;
- donor palette/frame-setup helper remains in the proven owned runtime block;
- no donor-rate hook.

**Rejected for fighter presentation; resource-load goal succeeded.**

The user confirmed that v13 reaches gameplay, so compacting the resource removes v12's pre-stage-load failure. However, every newly type-4-stored locomotion animation shows severe visual corruption: repeated/dragged Sektor silhouettes and rectangular smear patterns. The original raw/type-0 Sektor idle remains the established clean presentation path.

The screenshots also rule out the previously known 4-byte row-padding error as a complete explanation: the retail Sektor walk frames are 68 pixels wide, already naturally 4-byte aligned, yet still show the same ghosting. Therefore native type-4 materialization is **Rejected / failed for this fighter-frame path** in the tested form, even though type-4 remains runtime-confirmed for ordinary pickup visuals.

## v14 — raw/type-0 single-animation size isolation: Turn

**Final status: Runtime-confirmed.** Isolated Turn works on the tested route.

Disposable proof:

`MKMSZR_mkt-sektor-turn_destructive-swap_proof_v14.z64`

Identity:

- SHA-256 `0136742245361c23c962dfb47d61609dc3b4726736b2c768a24f08113a0a6234`;
- CRC1/CRC2 `DAACEFD9 / 6DF36782`.

v14 returns to runtime-confirmed v11 as its base and adds only primary slot `0x03`, Sektor's exact retail turn:

```text
RBTURN1
RB2VICTORY2
ANI_FLIP
RBTURN1
0
```

Both donor frames use the already runtime-confirmed fighter conversion:

- MKT Y:X -> MKMSZ X:Y;
- 4-byte-aligned CI rows;
- raw/type-0 wrapper `00000000`;
- the v10 frame-setup-time donor palette switch;
- false cave untouched.

The two frames add `0x2D94` bytes of raw donor material. File ID `0x87` is now ROM `0xF40000..0xF905B3`, size `0x505B4`, only about 11.4 KiB larger than runtime-confirmed v11. The donor palette is moved to resource `+0x50568` so the proven helper's donor-range test still covers all foreign shapes.

The active and inactive old Sub-Zero turn scripts are no longer callable; their shape/sub-descriptor stubs are cleared. Old compressed image bytes may remain orphaned but are not retained as an intentional runtime backup.

**Runtime-confirmed.**

The user reported v14 as perfect. The stage loads normally; the genuine two-frame Sektor turn renders cleanly with the established donor palette; transitions remain stable; no ghosting, smear, palette artifact, or hang was observed in the tested route.

This reconfirms the raw/type-0 fighter materialization path beyond idle and confirms primary slot `0x03` Turn as a direct graphical replacement.

## v15 — raw/type-0 shared walk-frame proof

**Final status: Runtime-confirmed.** Walk Forward/Backward work on the tested route.

Disposable proof:

`MKMSZR_mkt-sektor-walk_destructive-swap_proof_v15.z64`

Identity:

- SHA-256 `cd6d83c0d2ec1ae3e33f5ae1cd73bec383c7e3cb411caa930eb4337c5e9453ab`;
- CRC1/CRC2 `DAA31E49 / 780D580B`.

v15 returns to runtime-confirmed destructive v11 as its base and adds only primary slots `0x01` and `0x02`:

- Sektor walk forward: `RBWALK1,2,3,5,7,8,9, ANI_JUMP, self`;
- Sektor walk backward: the exact same seven frames in reverse order.

Because forward/backward share the same seven retail frames, they require only one physical donor frame set. The materialized raw/type-0 frame block is copied exactly from the previously decoded v12 donor data, preserving:

- MKT Y:X -> MKMSZ X:Y descriptor conversion;
- 4-byte-aligned rows;
- raw/type-0 wrapper;
- v10 frame-setup-time palette switching;
- false cave untouched;
- no donor-rate hook.

The donor walk block occupies resource `+0x4D7D0..+0x5AD7F`. The Sektor palette follows at color pointer `+0x5AD80`. File ID `0x87` is now ROM `0xF40000..0xF9ADCB`, size `0x5ADCC`, about 54 KiB larger than v11.

This proof intentionally leaves Turn stock so that the seven-frame walk set is isolated from the already-confirmed v14 Turn composition.

**Runtime-confirmed.**

The user reported v15 as perfect: stage load is normal; both forward and backward walking remain genuine Sektor throughout; the walk graphics look correct; and no transition, palette, smear, or hang regression was observed in the tested route.

This runtime-confirms primary slots `0x01` Walk Forward and `0x02` Walk Backward as direct graphical replacements using one shared seven-frame raw/type-0 donor set.

## v16 — compose confirmed Idle + Walk + Turn

**Final status: Runtime-confirmed.** Idle + Walk Forward + Walk Backward + Turn work as a composed set.

Disposable proof:

`MKMSZR_mkt-sektor-idle-walk-turn_destructive-swap_proof_v16.z64`

Identity:

- SHA-256 `c9f68e965c6e6cdcc716ea11944829d61d09fda28d3adc5c896200ea9782771a`;
- CRC1/CRC2 `DAA30759 / 664C0B43`.

v16 is a composition proof only. It begins from runtime-confirmed v15 and adds the already runtime-confirmed v14 Sektor Turn block without introducing a new decoder, palette strategy, or animation semantic:

- `0x00` Idle — runtime-confirmed v10/v11;
- `0x01` Walk Forward — runtime-confirmed v15;
- `0x02` Walk Backward — runtime-confirmed v15;
- `0x03` Turn — runtime-confirmed v14;
- `0x04` Crouch remains stock.

The shared seven-frame walk block remains resource `+0x4D7D0..+0x5AD7F`. The exact v12 raw/type-0 Turn materialization, whose isolated behavior was proven in v14, is placed at `+0x5AD80..+0x5DB13`. The donor palette moves immediately after it to `+0x5DB14`, and the frame-setup helper's donor upper bound / palette pointer are updated accordingly.

File ID `0x87` is ROM `0xF40000..0xF9DB5F`, size `0x5DB60`, which is `0x10340` bytes (~64.8 KiB) larger than runtime-confirmed v11. This remains substantially below rejected v12's `0x620E0` size.

The false cave remains exact stock; no donor-rate hook is enabled. The already runtime-confirmed destructive Turn cleanup is also retained.

**Runtime-confirmed.**

The user reported v16 as perfect. Idle, Walk Forward, Walk Backward, and Turn all coexist in the same session with correct Sektor graphics, correct donor palette, clean transitions, and no hang or smear regression. This is the first runtime-confirmed multi-animation Sektor composition beyond idle.

## v17 — isolate raw/type-0 Crouch

**Final status: Runtime-confirmed.** Crouch works on the compact raw/type-0 branch.

Disposable proof:

`MKMSZR_mkt-sektor-crouch_destructive-swap_proof_v17.z64`

Identity:

- SHA-256 `d28cc5705357503fcb1629e538ad48a569ff5ce55f8e4f878a67408cef3fd8e7`;
- CRC1/CRC2 `DAA31FD9 / 17C86690`.

v17 intentionally returns to the runtime-confirmed destructive v11 idle base rather than appending Crouch onto v16. Adding all three raw Crouch frames to v16 would recreate the rejected v12 file-ID-`0x87` size `0x620E0`, so repeating that known-bad composition is avoided.

Primary slot `0x04` now uses the exact retail Sektor crouch sequence:

```text
RBDUCK1
RBDUCK2
RBDUCK3
0
```

The three raw/type-0 frames are compactly relocated immediately after the v11 donor-idle region:

- RBDUCK1 shape `+0x4D7D0`;
- RBDUCK2 shape `+0x4F498`;
- RBDUCK3 shape `+0x50D08`;
- donor palette `+0x51D58`.

File ID `0x87` becomes ROM `0xF40000..0xF91DA3`, size `0x51DA4`, keeping this proof far below the rejected v12 size while preserving the already-proven raw fighter format and frame-setup-time palette switching.

**Runtime-confirmed.**

The user reported v17 as perfect. The stage loads normally; the genuine three-frame Sektor crouch renders cleanly with the donor palette; crouch transitions are stable; and no ghosting, palette artifact, or hang was observed in the tested route. Primary slot `0x04` Crouch is therefore a runtime-confirmed direct graphical replacement.

## v18 — crouch-family direct-core batch

**Final status: Runtime-confirmed.** The direct crouch-family states work on the tested route.

Disposable proof:

`MKMSZR_mkt-sektor-crouch-family_destructive-swap_proof_v18.z64`

Identity:

- SHA-256 `aec6c96c315496b3665f433243e03b6fd305f61b8774bde337978a168b060f82`;
- CRC1/CRC2 `DAA301D9 / 97D70477`.

v18 starts from runtime-confirmed v17 and expands the crouching family through primary slots `0x05..0x07`:

- `0x05` Crouch Turn: `RBDUCKTURN1, RBDUCKTURN2, ANI_FLIP, RBDUCKTURN1, RBDUCK3, 0`;
- `0x06` Crouch Block: `RBDUCKBLOCK1, RBDUCKBLOCK2, RBDUCKBLOCK3, 0`;
- `0x07` Crouch Hit: retail CUT_FRAME sequence `RBDUCKBLOCK1, RBDUCKHIT2, RBDUCKHIT3, 0`.

The batch reuses v17's already-confirmed `RBDUCK3` frame and shares `RBDUCKBLOCK1` between block and hit, so only seven new physical donor frames are required. All seven use the proven raw/type-0 fighter conversion and exact supplied MKT Rev. 2 robot streams.

New donor shapes begin at resource `+0x51D58`; the donor palette moves to `+0x59854`. File ID `0x87` is now size `0x598A0`, still below the already runtime-confirmed v15/v16 resource sizes.

The false cave remains stock; palette switching remains on the runtime-confirmed native frame-setup boundary; no donor-rate hook is enabled.

**Runtime-confirmed.**

The user confirmed that v18 works perfectly: Crouch, Crouch Turn, Crouch Block, and Crouch Hit all render as Sektor and transition correctly without hangs, palette faults, smear, or other visible corruption in the tested route.

One expected mixed-state artifact remained outside v18's scope: using stock MKMSZ Crouch Punch and allowing it to return to crouch can show a stock Sub-Zero crouch frame, because the unswapped slot-0x08 script contains explicit stock return frames rather than merely reselecting slot 0x04.

## v19 — Crouch Punch direct replacement

**Final status: Runtime-confirmed.** Crouch Punch works and removes the observed stock return frame.

Disposable proof:

`MKMSZR_mkt-sektor-crouch-punch_destructive-swap_proof_v19.z64`

Identity:

- SHA-256 `73e16ae4d6c2941834caa68c7227d75a99865f4483430f07e9123d971741e199`;
- CRC1/CRC2 `DAA36769 / 1A41D433`.

v19 starts from runtime-confirmed v18 and replaces primary slot `0x08` with the exact MKT Rev. 2 robot CUT_FRAME crouch-punch script:

```text
RBDUCKBLOCK1
RBDUCKPUNCH2
RBDUCKPUNCH3
0
RBDUCKPUNCH2
RBDUCKBLOCK1
RBDUCK3
0
```

This directly addresses the observed stock-frame return. `RBDUCKBLOCK1` and `RBDUCK3` are already resident from v18/v17, so only two new physical donor frames are added:

- `RBDUCKPUNCH2` at resource `+0x59854`;
- `RBDUCKPUNCH3` at resource `+0x5AA78`.

Both use the proven raw/type-0 fighter conversion. The donor palette moves to `+0x5C110`, and file ID `0x87` becomes size `0x5C15C`, still slightly below the already runtime-confirmed v16 size `0x5DB60`.

The ROM extension target was verified to be untouched `0xFF` tail space before writing. The false cave remains stock; palette switching remains on the runtime-confirmed frame-setup boundary; no donor-rate hook is enabled.

**Runtime-confirmed.**

The user reported v19 as clean. Crouch Punch remains Sektor throughout, returns through imported `RBDUCK3` rather than the former stock Sub-Zero crouch frame, and transitions remain stable. Primary slot `0x08` is therefore runtime-confirmed as a direct graphical replacement.

## v20 — Crouch Low Kick

**Final status: Rejected / failed.** Whole-scene corruption occurs before the new Crouch Low Kick is used; the file-`0x87` footprint remains the strongest allocation-boundary inference.

Disposable proof:

`MKMSZR_mkt-sektor-crouch-low-kick_destructive-swap_proof_v20.z64`

Identity:

- SHA-256 `a41a73cc2d37b371aeeae9bdc4c761100b94c44106697101f8689ab7ca77b687`;
- CRC1/CRC2 `DAA30659 / FE85A85E`.

v20 starts from runtime-confirmed v19 and replaces primary slot `0x0A` with the exact retail CUT_FRAME Sektor crouch-low-kick sequence:

```text
RBDUCKHIKICK1
RBDUCKLOKICK2
RBDUCKLOKICK3
0
RBDUCKLOKICK2
RBDUCKHIKICK1
RBDUCK3
0
```

The final `RBDUCK3` reuses the already runtime-confirmed crouch frame from v17. Only three new physical donor frames are added:

- `RBDUCKHIKICK1` at resource `+0x5C110`;
- `RBDUCKLOKICK2` at `+0x5CE48`;
- `RBDUCKLOKICK3` at `+0x5DF60`.

All three are decoded from the supplied MKT Rev. 2 robot resource, verified against the retail descriptors, and materialized using the runtime-confirmed raw/type-0 fighter format. The donor palette moves to `+0x5F878`.

File ID `0x87` becomes size `0x5F8C4`, still below the rejected v12 size `0x620E0`. The false cave remains untouched; palette switching remains on the v10 frame-setup boundary; no donor-rate hook is enabled.

**Rejected / failed due to whole-scene runtime corruption before the new animation is used.**

The user reported that the stage itself appears, but approximately one second later—just as the player is about to appear—the entire scene becomes severely corrupted. The screenshot shows broad renderer/framebuffer-style corruption across the stage and HUD, not merely a malformed fighter frame. The new Crouch Low Kick was not activated before the failure.

This materially tightens the raw fighter-resource size boundary:

- v19 file ID `0x87` size `0x5C15C`: normal gameplay is runtime-confirmed clean;
- v20 size `0x5F8C4`: catastrophic scene corruption occurs during player instantiation;
- delta: only `0x3768` bytes (~13.8 KiB).

The strongest current explanation is **Hypothesis / strong inference:** file ID `0x87` has crossed a practical load/allocation boundary and is colliding with later runtime memory or render-state allocation. The failure is not attributed to the Crouch Low Kick animation semantics because the animation is never selected.

## v21 — isolated Crouch Low Kick below the raw-size boundary

**Final status: Runtime-confirmed.** Crouch Low Kick works when isolated on the smaller v17 base.

Disposable proof:

`MKMSZR_mkt-sektor-crouch-low-kick_isolated-proof_v21.z64`

Identity:

- SHA-256 `f6169f6d2a82b0165ff5a96ef609a60ef0f95546288c8978ddd8aa35983a161b`;
- CRC1/CRC2 `DAA30FC9 / 88373F03`.

v21 returns to runtime-confirmed v17 (Idle + Crouch) and adds only the exact same retail Crouch Low Kick mapping used by v20:

```text
RBDUCKHIKICK1
RBDUCKLOKICK2
RBDUCKLOKICK3
0
RBDUCKLOKICK2
RBDUCKHIKICK1
RBDUCK3
0
```

The three donor frames use the same verified raw/type-0 conversion, but are placed immediately after v17's compact donor block:

- `RBDUCKHIKICK1` at `+0x51D58`;
- `RBDUCKLOKICK2` at `+0x52A90`;
- `RBDUCKLOKICK3` at `+0x53BA8`;
- donor palette at `+0x554C0`.

File ID `0x87` is only `0x5550C`, safely below runtime-confirmed v18/v19/v16 sizes. This isolates animation correctness from the accumulation/size failure seen in v20.

**Runtime-confirmed.**

The user confirmed normal stage load and a clean genuine Sektor crouch low kick, including the full return to the imported Sektor crouch state. This establishes primary slot `0x0A` Crouch Low Kick as a correct direct graphical replacement. It also confirms that v20's catastrophic corruption was caused by accumulated composition/resource pressure rather than by the low-kick mapping itself.

Primary test: normal stage load, Sektor Crouch Low Kick, clean return to Sektor crouch, and no broad scene corruption. If v21 succeeds, slot `0x0A` is a valid direct mapping and the remaining blocker is storage/composition, not animation semantics.

A separate instrumentation note remains: the earlier Reverse Elbow/Reptile branch already runtime-confirmed a gameplay-safe diagnostic HUD through the native gameplay HUD/text path. Future Sektor instrumentation should reuse that proven pattern rather than the rejected v04 unguarded wrapper.

## v22 — isolated Crouch High Kick composed with confirmed Low Kick

**Final status: Runtime-confirmed.** Crouch High Kick and the carried-forward Low Kick both work on the tested route.

Disposable proof:

`MKMSZR_mkt-sektor-crouch-kicks_isolated-proof_v22.z64`

Identity:

- SHA-256 `a73a4a9b5cf5a822fd9f504962cbbd8716fd154954e7a6e5cdf35b53abd4c176`;
- CRC1/CRC2 `DAA30659 / 739BE7D0`.

v22 builds from runtime-confirmed v21. It retains the confirmed Crouch Low Kick and adds primary slot `0x09` Crouch High Kick.

The exact retail Sektor high-kick sequence is:

```text
RBDUCKHIKICK1
RBDUCKHIKICK2
RBDUCKHIKICK3
RBDUCKHIKICK4
0
RBDUCKHIKICK3
RBDUCKHIKICK2
RBDUCKHIKICK1
RBDUCK3
0
```

`RBDUCKHIKICK1` and `RBDUCK3` were already resident in v21, so only three new physical frames are added.

Because the exact retail sequence is 10 words long while MKMSZ's original slot-`0x09` script area has only 9 words before the next stock script, v22 does **not** overwrite the neighboring High Punch script. Instead it stores the exact 10-word Sektor high-kick script at appended resource `+0x554C0` and redirects primary table slot `0x09` there.

New donor shapes:

- `RBDUCKHIKICK2` at `+0x554E8`;
- `RBDUCKHIKICK3` at `+0x56090`;
- `RBDUCKHIKICK4` at `+0x571E8`;
- donor palette at `+0x59098`.

File ID `0x87` becomes size `0x590E4`, below the already runtime-confirmed v19 size `0x5C15C` and well below failed v20 `0x5F8C4`.

**Runtime-confirmed.**

The user confirmed that v22 works cleanly: Crouch High Kick plays correctly through its forward/reverse sequence, returns to the imported Sektor crouch, and the previously confirmed Crouch Low Kick remains correct in the same build.

This runtime-confirms primary slot `0x09` Crouch High Kick as a direct graphical replacement and confirms coexistence of both crouching kick slots on the compact branch.

## v23 — isolated Uppercut

**Final status: Runtime-confirmed.** Uppercut works on the tested route.

Disposable proof:

`MKMSZR_mkt-sektor-uppercut_isolated-proof_v23.z64`

Identity:

- SHA-256 `bcece5ddf4f7994c04776309c0f35158a1a3fcb1404a7e405194dd24150c10c7`;
- CRC1/CRC2 `DAA31FC9 / 2BFDE43C`.

v23 returns to the runtime-confirmed v17 crouch base and isolates primary slot `0x0B` Uppercut so the test remains below the known raw resource failure boundary.

The exact MKT Rev. 2 Sektor uppercut sequence is:

```text
RBUPPERCUT1
RBUPPERCUT3
RBUPPERCUT4
RBUPPERCUT5
ANI_NOSLEEP
RBUPPERCUT7
0
RBUPPERCUT5
0
```

Static comparison with MKMSZ's stock Sub-Zero uppercut shows the same nine-word animation grammar and the same command value `5` for `ANI_NOSLEEP` in the same position. Therefore v23 replaces the stock script in place at resource `+0x49C`; no script relocation or neighboring overwrite is required.

Five exact retail donor frames are materialized through the proven raw/type-0 fighter path:

- `RBUPPERCUT1` at `+0x51D58`, 46x78, anchor (+20,-42);
- `RBUPPERCUT3` at `+0x52C10`, 57x94, anchor (+20,-28);
- `RBUPPERCUT4` at `+0x54230`, 82x98, anchor (+30,-25);
- `RBUPPERCUT5` at `+0x56270`, 78x108, anchor (+32,-16);
- `RBUPPERCUT7` at `+0x58448`, 46x130, anchor (+21,+6);
- donor palette moves to `+0x59CC0`.

File ID `0x87` becomes size `0x59D0C`, below the runtime-confirmed v19 size `0x5C15C` and well below failed v20 `0x5F8C4`.

**Runtime-confirmed.**

The user reported the uppercut working exactly as expected, including the tall apex frame and clean transition afterward.

Primary validation: stage load, Sektor Uppercut animation, correct tall apex frame, and clean transition afterward. The proof intentionally does not compose the crouching kicks so Uppercut itself remains isolated from the known accumulation boundary.

## v24 — isolated Standing Block

**Final status: Runtime-confirmed.** Standing Block works on the tested route.

Disposable proof:

`MKMSZR_mkt-sektor-standing-block_isolated-proof_v24.z64`

Identity:

- SHA-256 `61dcf4fc9d6ace56cf06c565233c944bb3530405466fc89f1ca239b49409fad9`;
- CRC1/CRC2 `DAACE659 / 489383DE`.

v24 starts from runtime-confirmed destructive v11 and replaces only primary slot `0x0C` Standing Block with the exact MKT Rev. 2 Sektor CUT_FRAME sequence:

```text
RBHIBLOCK1
RBHIBLOCK3
RBHIBLOCK3
0
```

Only two physical donor frames are required. They use the proven raw/type-0 fighter conversion and exact robot dictionary/descriptor rules. The donor palette is moved after the new block frames; the frame-setup-time palette helper remains otherwise unchanged.

File ID `0x87` is only `0x503E0` bytes in this proof, well below every observed raw-resource failure boundary.

**Runtime-confirmed.**

The user reported v24 as perfect. Standing Block renders as genuine Sektor, transitions cleanly, and showed no stock Sub-Zero block frame, palette artifact, or stability regression in the tested route.

## v25 — isolated High Punch core + post-legal logo skip

**Final status: Runtime-confirmed.** High Punch works on its bounded route; the post-legal logo bypass remains only a proof convenience baseline.

Disposable proof:

`MKMSZR_mkt-sektor-high-punch_isolated-proof_v25.z64`

Identity:

- SHA-256 `b26f5eb73d72354c66a336d992d9cca2bbc3daf36545147124c898176e7a7167`;
- CRC1/CRC2 `CAACE5C9 / 637009C7`.

v25 starts from runtime-confirmed v24 and adds the seven genuine Sektor High Punch frames `RBHIPUNCH1..7`. MKMSZ's stock High Punch script has the same 28-word control/segment grammar as MKT's retail robot script, so the existing target command words and jump targets are preserved while every High-Punch-owned frame pointer is redirected to imported Sektor shapes.

Two late crossover frame references belong semantically to Low Punch (`RBLOPUNCH5` and `RBLOPUNCH2`). Those remain stock Sub-Zero in v25 by design rather than being approximated; they will be addressed when Low Punch is mapped. A simple High Punch and all High-Punch-owned frames are therefore the primary validation scope.

Seven raw/type-0 frames are appended. File ID `0x87` becomes `0x5DA0C`, essentially the same size class as runtime-confirmed v16 (`0x5DB60`) and below the v19/v20 failure bracket.

Starting with v25, these disposable animation proofs also include the already runtime-confirmed **post-legal logo bypass** at ROM `0x7A3F4`: only the first guarded word changes to `0x10000003`, skipping the two fixed company/logo presentations while preserving the legal screen, fade normalization, and title handoff.

**Runtime-confirmed.**

The user reported High Punch working perfectly in the tested route. The post-legal logo bypass also remains part of the convenience baseline from this proof onward.

Primary test: ordinary High Punch, repeated High Punch, transitions back to idle/block, and watch for any stock frame only on the known Low-Punch crossover branches.

## v26 — isolated Low Punch

**Final status: Runtime-confirmed.** Ordinary and chained Low Punch behavior works on the tested route.

Disposable proof: `MKMSZR_mkt-sektor-low-punch_isolated-proof_v26.z64`.

Identity:

- SHA-256 `46de0dbfb1217d9d19b8af5221771597e23bfed78248b64090a2eb131c28510d`;
- CRC1/CRC2 `CAAC9DC9 / 4FC0CC34`.

v26 returns to the small runtime-confirmed v11 idle baseline and isolates primary slot `0x0F` Low Punch. The exact CUT_FRAME branch needs five Low-Punch-owned frames (`RBLOPUNCH2..6`, excluding the cut `RBLOPUNCH1`) plus the three High-Punch crossover frames `RBHIPUNCH1`, `RBHIPUNCH5`, and `RBHIPUNCH7`. MKMSZ's inherited 27-word punch-chain control structure is preserved; only the corresponding visual frame pointers are replaced. File ID `0x87` is `0x5BF88`. The runtime-confirmed post-legal logo bypass is included.

**Runtime-confirmed.** The user reported the ordinary and chained Low Punch behavior working perfectly in the tested route.

## v27 — isolated Standing Low Kick

**Final status: Runtime-confirmed.** Standing Low Kick works with the exact relocated 13-word donor sequence.

Disposable proof: `MKMSZR_mkt-sektor-standing-low-kick_isolated-proof_v27.z64`.

Identity:

- SHA-256 `548dc3b1e07528c5863e20cfcbd52f7cdf632b85c409a80d37d15916a798bb7f`;
- CRC1/CRC2 `CAACE1B9 / 6BA95942`.

v27 returns to the runtime-confirmed v11 idle base and imports the exact MKT Rev. 2 Sektor Standing Low Kick. The donor sequence is `RBLOKICK1,2,3,4,5,6,0,5,4,3,2,1,0`. MKMSZ's stock slot-0x12 script region is only 10 words before the neighboring High Kick script, so the exact 13-word donor sequence is appended at resource `+0x4D7D4` and primary table slot `0x12` is redirected there rather than overwriting slot `0x11` data. Six donor frames use the proven raw/type-0 conversion, the Sektor palette moves to `+0x588F8`, and file 0x87 is `0x58944` bytes. The runtime-confirmed post-legal logo bypass is included as a convenience baseline. **Runtime-confirmed.** The user reported Standing Low Kick working perfectly in the tested route.

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


## v75-v85 — calibrated flight and first-render reconciliation

- **v75 — Runtime-confirmed.** Comparative donor/v74 video showed the target late-flight magnitude at about half donor speed while the temporal ramp was already close. v75 keeps the folded two-donor-tick resampler and doubles only the calibrated host velocity magnitude. The user reported the result “feels really good now”; no hang was observed. v75 is the current stable missile-flight baseline.
- **v76 — Rejected / failed for its intended presentation changes.** A small Y correction barely moved the visible rocket and sleeping the parent after the v69 one-frame chest injection did not hold the chest pose. The player returned immediately because the stock animation cursor had already been restored.
- **v77 — Stable negative placement result.** Resetting projectile Y to owner Y plus the donor rocket anchor produced essentially the same head-height visible spawn. This rejected another guessed base-origin correction without affecting the v75 flight result.
- **v78 — Rejected / failed.** Directly composing target helper `0x80031394(owner, projectile)` before `0x80031208(+5,+38)` hard-hung the game. Static similarity to donor `match_ani_points` is therefore insufficient to treat `0x80031394` as a safe projectile adapter primitive at this lifecycle seam.
- **v79 — Rejected / failed as a composition.** Built from exact v75, not v76-v78. It changed (1) the chest cursor/script to eight repeated frames, (2) six post-launch sleeps to `0x20` total ticks, (3) projectile palette selector binding, (4) the Ice screen-tint call, and (5) fighter-type-4 selector-`0x13` strike reaction/damage (`0x2C -> 0x04`, `0/0 -> 20/2`) simultaneously. The user observed another hard hang. No individual change is identified as its cause; neither palette nor strike translation is runtime validated. v75 flight and `(+5,+38)` placement were byte-preserved. Clone-helper actors, smoke, impact explosion, and imported donor audio remain Pending.
- **v80 — Runtime-confirmed stable negative presentation result.** The latest constructor proof is `MKMSZR_sektor-missile-constructor_common-proof_v80.z64`, SHA-256 `2e3e14367ec074f866d0d4825331d9b13d15492710e7880ced94b77baae3a9e3`. Built from exact v75, it changes only relocated file-`0x87` operand `0xF40DBC: 0x00034A58 -> 0x0004E6E4`, i.e. the live primary-slot-`0x24` token-`0x0B` constructor entry. The move remains stable but the visible result is materially unchanged: the projectile is still Ice-blue around Sektor's head and the two blue companion actors remain. This proves the constructor operand alone is insufficient; it does not invalidate the constructor seam or helper lifecycle.
- **v81 — Partial Runtime-confirmed first-render seam.** Disposable proof `MKMSZR_sektor-missile-first-render_common-proof_v81.z64`, SHA-256 `424b6ddb229f9c3f7e775212357ca3e862ed75c343fb14b8f44de233b4c0f607`, CRC1/CRC2 `29C9C3E6 / E9E88C41`. It keeps exact v75 placement, child ownership, cadence/acceleration, companion/tint processes, collision and cleanup. Relative to v75 it applies the validated v80 constructor operand and changes token-handler VA `0x800309E8` / ROM `0x315E8` from `sh v0,0x9E(s0)` to `sh zero,0x9E(s0)`, forcing selector 0 before insertion while preserving the preceding `0x8001C528` allocation/refcount call. Runtime video `MKMSZR_SEKTOR_MISSILE_V81_RUNTIME_2026-09-24.webm` shows the prior one-frame blue Sektor-like projectile fallback is gone, but the missile itself is visibly corrupted into a sparse horizontal pixel/bar form. This is consistent with selector zero changing first presentation; the paired constructor edit means it does not isolate selector-only first-frame behavior. Slot zero is not the dynamically acquired Sektor source.
- **v82 — Runtime-confirmed stable negative control.** Disposable proof `MKMSZR_sektor-missile-palette-bind_common-proof_v82.z64`, SHA-256 `becf7a1e6bc1276976d844105fda42d07bc5af54d3be4fca92324811092c442c`, CRC1/CRC2 `0A70C1B2 / 72AEDC2B`. The user reports no visible change from v81: the one-frame blue projectile fallback remains gone, but the missile remains identically glitched. This rejects stale active handle `+0x80` by itself as the cause; selector zero still maps to the wrong palette source. The selector-0 store and explicit `+0x80` rebind are therefore superseded as the next implementation direction.
- **v83 — Runtime-confirmed stable negative presentation result.** Disposable proof `MKMSZR_sektor-missile-postinit-bind_common-proof_v83.z64`, SHA-256 `e15a48d019a868ac542c41c82558ff7270aea0666eebc007d53a5a4bdafdb23d`, CRC1/CRC2 `9DEC7AB0 / D63748B1`. The user reports the same visible sequence as the stock-constructor line: first an Ice/Sektor-like projectile frame, then an Ice-blue missile. Screenshots are archived as `MKMSZR_SEKTOR_MISSILE_V83_RUNTIME_ICE_ACTORS_2026-09-25.png` and `..._ICE_MISSILE_2026-09-25.png`. Therefore a raw `0x8001BDA0` ROCKETD1 bind immediately before actor-list insertion is **not sufficient** to control first presentation, even after token actor initialization. Placement, flight and helper lifecycles remain stable.
- **v84 — Partial Runtime-confirmed first-visible ownership result.** Disposable proof `MKMSZR_sektor-missile-context-bind_common-proof_v84.z64`, SHA-256 `0d51810737fdf04e73b27dd0b00a1c082588349d6cf907aef6c09d0a57aed90b`, CRC1/CRC2 `9CF5BA48 / 98A4A465`. Runtime screenshot shows the initial one-frame Ice/Sektor projectile fallback is gone, proving the contextual pre-insertion bind is early enough to control first visibility. The following missile remains the same sparse/glitched rocket texture as v81. On the normal straight branch the parent wrapper is bypassed; the parent stock advance now reads the rocket cursor because v84 moved controller `+0x6E4` to `+0xD90`; the wrong selector-zero palette still matters. The same-shape-rebuild explanation is disproved by the descriptor and dirty-flag path. Evidence screenshot is archived as `MKMSZR_SEKTOR_MISSILE_V84_RUNTIME_GLITCHED_ROCKET_2026-09-25.png`.
- **v85 — Built; Runtime untested; statically rejected for straight mode zero.** Disposable proof `MKMSZR_sektor-missile-deferred-insert_common-proof_v85.z64`, SHA-256 `23bc0cd6d677fc99805cdb6bdeebe160073b18ac1f71b8855d87fbf3562f30ea`, CRC1/CRC2 `B52962D5 / 07C23284`. Built from exact v75. It does **not** bind the rocket early. Instead it suppresses only token handler `0x80030AC8`'s call to `0x80024650` while preserving the delay-slot `actor+0xAE` store and all staging pointers. The actor remains stock-Ice and unlisted through placement. On the ordinary straight route, control skips that wrapper entirely: its proposed transition/insertion never runs. `0x80024650` is only a sorted list link; to preserve its stock sort key, v85 temporarily substitutes owner Y during insertion and restores the projectile's final placed Y immediately afterward. Child code, flight, helper/tint processes, collision and cleanup remain byte-preserved. The token-call suppression is proof-global and not production-safe; the mode-zero control-flow fault statically rejects this candidate.
- **v86 — Partial Runtime-confirmed palette-source result.** Disposable proof `MKMSZR_sektor-missile-palette-source_common-proof_v86.z64`, SHA-256 `fe6f8b91d1d12d587e64080acb24e039399d9ed15faacb21e64486ced5d6a58c`, CRC1/CRC2 `4C35DEC0 / E02BF951`. Built from exact v75. It changes only the guarded straight-shot token palette source from stock Ice `0x800B1A24` to file-`0x87 +0x4584C` through stock `0x8001C528`, preserving the returned dynamic selector and all frame/insertion/helper/child/flight machinery. Runtime screenshots show a materially more coherent full rocket shape than v81/v84, but the missile remains visually wrong relative to the donor reference. Static asset audit explains the limit: the imported ROCKETD1 pixels in v70/v75 were deliberately remapped from donor indices `0..15` into resident Sektor TLUT entries `16..31`; the actual used set collapses into grayscale Sektor entries `18,19,21,22,23,24,25`. v86 therefore validates projectile-local palette-source ownership, but also proves that the resident-Sektor remap is not donor-faithful enough for final rocket presentation. Evidence archived as `MKMSZR_SEKTOR_MISSILE_V86_RUNTIME_PALETTE_SOURCE_2026-09-25.png` and `..._CROP_2026-09-25.png`.

- **v87 — Runtime-confirmed donor-faithful rocket asset/palette pair; first-frame mismatch remains.** Disposable proof `MKMSZR_sektor-missile-rocket-palette_common-proof_v87.z64`, SHA-256 `2137de34fc34b29a0d9c0f62164a6961714cb27b464824d5e354756655885b9e`, CRC1/CRC2 `4C35F4F0 / DCDBD00C`. Built from exact v75 plus exact MKT Rev. 2 donor. The flying missile now renders with the expected gray body and red/orange/yellow exhaust, validating the exact retail ROCKETD1 indices and dynamically acquired converted ROCKET_P source. The initial one-frame Ice/Sektor projectile still occurs, but because that earlier Ice-derived descriptor now uses ROCKET_P it appears as a glitched/corrupted Sektor. This sharply separates correct palette/content ownership from the still-Ice first-frame schedule. Evidence screenshots are archived as `MKMSZR_SEKTOR_MISSILE_V87_RUNTIME_GOOD_ROCKET_2026-09-25.png` and `MKMSZR_SEKTOR_MISSILE_V87_RUNTIME_GLITCHED_FIRST_FRAME_2026-09-25.png`.
- **v88 — Partial Runtime-confirmed; first-frame texture publication still wrong.** Disposable proof `MKMSZR_sektor-missile-first-frame-rocket_common-proof_v88.z64`, SHA-256 `196899276ef9cbc494714dc60862437402a7a22d7e2af1100f584e653c5dfed0`, CRC1/CRC2 `5F0CC13B / 97B0B76C`. The flying rocket remains donor-faithful, but the one-frame corrupted Sektor-like texture is still visible. This disproves the assumption that v84's contextual descriptor/cursor advance had made the rocket texture synchronously ready before first publication; with the correct palette present, the stale slot becomes visible instead of sparse. Evidence screenshot is archived as `MKMSZR_SEKTOR_MISSILE_V88_RUNTIME_STALE_SLOT_FIRST_FRAME_2026-09-25.png`.
- **v89 — Runtime-confirmed first-visible rocket success.** Disposable proof `MKMSZR_sektor-missile-preupload_common-proof_v89.z64`, SHA-256 `582b255ca3c5ef2cc008444403c1bb5b0379c91c16e6d5f9079da2cdc5ac0d89`, CRC1/CRC2 `9F889E81 / 0EDEC067`. It keeps v87's exact retail ROCKETD1/ROCKET_P asset pair and dynamic selector, applies the v80-proven rocket constructor operand and keeps the ordinary parent next frame on ROCKETD1, then uses native `0x8001BF70` on the finalized projectile slot before stock `0x80024650` insertion. `0x8001BF70` installs slot metadata, queues the raw rocket pixels through `0x8001D6EC`, and immediately drains the queue via `0x8001D7F0(1)`; v89 then calls `0x8001BDA0` to refresh actor slot/palette/frame fields before publication. The user reports the corrupted one-frame Sektor is completely gone while the correct donor-colored missile remains. This Runtime-confirms texture-slot readiness as the missing first-publication seam. The proof remains one-shot/diagnostic because texture-storage advancement and balanced palette/texture release are not yet modeled.

### Post-v78 static composition findings

The stock Ice action itself provides a safer reduced-animation runner than the failed “inject then sleep” model. After the v69 hook there is one pre-launch and six post-launch calls to `0x800304C0`; the post-launch sleeps are `2+2+3+4+5+5 = 21` ticks. A reduced chest script can therefore repeat the one available genuine chest shape across those existing advances, while the post-launch sleep budget can be resampled to donor `process_sleep(0x20)` without introducing a new top-level callback.

The blue presentation has two distinct inherited sources. The v79 proposal changed the parent wrapper from selector zero to the owner selector, but that wrapper is bypassed on ordinary straight mode zero. Its hard hang cannot establish a palette fix. On nonzero modes, frame setup resolves the active palette handle from the chosen selector. Separately, the second stock Ice helper callback at `0x8004AB0C` is presentation-only around `0x80044964(128,128,192,128,...)` followed by native process exit; v79 suppresses only that tint call. The two visible Ice/Sektor clone actors come from the separate `0x80060A3C` helper path and are not removed in v79.

For contact, fighter type 4 uses strike-pointer table `0x800AF484`; selector `0x13` resolves to record `0x800AF634`, whose stock bytes encode the Ice projectile hitbox, unblocked reaction `0x2C`, blocked reaction `0x05`, zero normal/block damage, and flags. v79 changed reaction/damage semantics while retaining the target hitbox and generic `0x8004CC50 -> 0x8004CE6C/0x8004CF3C -> 0x8002BA04` collision path. Reaction `0x04` was chosen from the v62 tested combo route; exact equivalence to donor `r_rocket` and the v79 contact path are unvalidated after its hard hang. One wrapper advance plus one prelaunch and seven postlaunch advances reach the terminator on the ninth advance after eight repeated chest shapes. At zero `0x800304C0` returns completion `0x4002`, which this parent does not inspect; this count alone does not identify the v79 hang.

### Post-v80 ownership reconciliation

Exact v75 identity: SHA-256 `e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb`. Its builder derives from exact v73, folds two donor 60 Hz steps into each ~30 Hz target callback, uses initial host field `0x46666` and cap `0xEEEEE`, and leaves stock Ice helpers, Ice SFX/tint/collision and `(+5,+38)` placement unchanged. This is the immutable tested baseline.

Clean donor/target plus v75 disassembly resolves the key process distinction: Ice parent starts class-`0x100` companion constructor `0x80060A3C` and tint callback `0x8004AB0C`; the former allocates texture/palette, constructs/inserts and later removes two actors, while the latter calls screen tint and exits. The separate class-`0x700` projectile child is created through `0x8004CBC4`. The parent stores temporary actor/script/coordinate state before the helpers, restores its staged projectile pointer, then hands that actor to the projectile child. The initial Ice-derived projectile frame is a third source: the token inserts the actor after the helper phase; the normal parent then advances another Ice entry, and the child later installs the rocket cursor `+0xD90`. Full donor/host semantics are in [MKT adapter primitives](MKT-Adapter-Primitives).

v65-v67 suppressed one or two process spawns **and** altered parent animation/setup/movement. Restoring one companion in v67 changed visuals but did not restore the complete transaction. v78's direct `0x80031394` shim altered position/anchor/facing at a pre-rocket-descriptor seam and hard-hung. v79 changed five independent concerns and hard-hung. None identifies a single causal instruction. v80 then resolved and changed the exact live constructor operand at file-`0x87 +0xDBC`, but the visible Ice-derived projectile presentation remained. Static reconciliation explains why: after `0x80034510` constructs the actor, token handler `0x80030974` separately calls `0x8001C528(0x800B1A24,0x100,0)`, stores `return-0x80` to actor `+0x9E`, and only then inserts the actor. Exact v75 also has `+0xFD0 -> +0xD90`, where `+0xD90` is already the genuine rocket loop, so the child cursor is not the remaining Ice-descriptor seam. That v81 proposal is superseded by its observed corrupted result and the handle-source trace. If a further ROM is authorized later, the bounded source-only proof is a guarded token `0x8001C528` call that acquires the already resident player type-4 Sektor source, keeps its returned selector, and otherwise preserves exact v75 timing and helpers. This tests palette-source identity only; it does not resolve the first Ice frame. No ROM is built here.

## v63-v70 — Sektor straight-missile proof line

This line begins after the Runtime-confirmed v62 combo proof and targets Sektor's MKT straight missile. The durable asset-format conclusions belong to [MKT fighter asset translation](MKT-Fighter-Asset-Translation); the donor move semantics and accepted compatibility direction belong to [MKT adapter primitives](MKT-Adapter-Primitives). The entries here own only the proof chronology, artifact identities, changed variables, runtime observations, and supersession.

### Pre-v63 donor/storage audit

**Static-confirmed before the first build:**

- the authentic Sektor command is **Forward, Forward + Low Punch**, mirrored by facing;
- the launch presentation uses the robot chest-open family;
- straight missile flight selects the horizontal rocket sub-animation;
- the two horizontal retail rocket shapes are MKT robot-relative `+0x2668` and `+0x267C`, using donor codec 16;
- the first chest shapes audited were `+0x29A0` and `+0x29B4`, using donor codec 22;
- the dedicated donor `ROCKET_P` palette exists independently of Ice colors.

The codec-16 blocker was resolved losslessly before the proof. The two horizontal rocket frames decode to `39x9` / 360 stored pixels and `42x10` / 440 stored pixels respectively, using four-bit indices `0..15`.

An exact four-frame Type-5 dry pack (two chest + two missile frames) against the v59/v62 takeover corpus projected file `0x87 = 0x4F5A8`: `0x11AC` larger than v59 and `0x1064` above the Runtime-confirmed v49 Fortress-working footprint `0x4E544`. This did **not** prove that `0x4F5A8` would fail; it established that blindly appending all four frames would leave the known working envelope.

The later compact proof therefore reduced the initial visible requirement to one fully-open chest pose plus one horizontal rocket pose and reused the existing Sektor Type-5 dictionary/model structure rather than treating every donor pose as mandatory for the first runtime gate.

### v63 — four-frame in-place-bank experiment

Disposable proof: `MKMSZR_sektor-missile-flight_common-proof_v63.z64`.

Builder: `MKMSZR_build_sektor_missile_flight_v63.py`.

Identity:
- SHA-256 `f45135d640195d20d2a0b47eb0fdde66e091be004c576f799cea9b9143515686`;
- CRC1/CRC2 `B4274446 / 49F03C85`;
- file `0x87 = 0x4E3FC`, unchanged from v59/v62.

v63 reconstructed the v60 palette and v62-safe combo graph on top of v59, decoded/imported two chest frames plus the two horizontal rocket frames, and packed them into file-`0x87` range `+0x41984..+0x43190`, which had been classified by the proof audit as a closed/unreachable stock special-animation bank. The used content ended at `+0x42D44`. The proof then redirected the stock Ice launch secondary script to the chest sequence, redirected the basic Ice projectile loop to the two rocket frames, and changed the Low-Punch special command to `F,F+LP`.

**Rejected / failed at runtime.** The missile itself could not initially be exercised because the normal XP unlock was still active. While farming XP, the user found that being hit hard-hung the game and the normal blood presentation was replaced by a visible artifact/glitch. The missile was still locked at that point, so this failure is independent of missile contact behavior.

The durable conclusion is negative: `+0x41984..+0x43190` was **not** safe replacement storage merely because the first reference audit made it look closed. v63 is the direct file-local equivalent of the project's broader “zero/unreferenced-looking bytes are not automatically free” rule.

### v64 — compact one-chest/one-missile expansion

Disposable proof: `MKMSZR_sektor-missile-expanded_common-proof_v64.z64`.

Builder: `MKMSZR_build_sektor_missile_expanded_v64.py`.

Identity:
- SHA-256 `e0a4a58169f2f3a0d93e1ec717a8f631a8c449e24f2fcf7fc60d834c026d19cc`;
- CRC1/CRC2 `6D28457F / A48A0CA9`;
- file `0x87 = 0x4E788`;
- `0x244` bytes above the Runtime-confirmed v49 footprint `0x4E544`;
- `0x38C` bytes above v59/v62 `0x4E3FC`.

v64 abandoned the v63 “dead bank” reuse and rebuilt from the clean ROM using the compact takeover packer. It added exactly two proof frames to the 158-frame corpus:
- fully-open chest source `RBCHEST2` / donor `+0x29B4`;
- horizontal rocket source `ROCKETD1` / donor `+0x2668`.

Both were quantized only against already-resident Sektor Type-5 patterns with exact transparency masks and folded into existing model group 56, avoiding a new model record. Measured proof-frame quality was approximately:
- chest: RGB RMSE `2.004059`, `53.727%` exact opaque indices;
- rocket: RGB RMSE `2.275750`, `50.218%` exact opaque indices.

The proof also added a **test-only max-tier gate** by feeding XP `7354` to the existing special condition so `F,F+LP` could be exercised immediately. This is proof convenience only and is not progression design.

**Partial Runtime-confirmed / presentation rejected.** The game reached and executed the special path. The player did **not** use the chest-open pose. Instead, two frozen blue/fallback Sektor-like helper actors appeared below the player. The projectile itself appeared first as another frozen Sektor-like frame, then changed into the missile. The missile spawned much too far from Sektor and travelled at an essentially constant Ice-Blast-like speed rather than the intended accelerating rocket behavior.

v64 therefore established that the compact asset composition could reach the move path on the tested route, but it disproved the assumption that the reused Ice secondary slot was the player's chest-animation path. It did not establish `0x4E788` as a general Fortress/Prison-safe allocation ceiling.

### v65 — direct player chest wrapper + suppressed Ice helper processes

Disposable proof: `MKMSZR_sektor-missile-corrected_common-proof_v65.z64`.

Builder: `MKMSZR_build_sektor_missile_corrected_v65.py`.

Identity:
- SHA-256 `7c0bb60a76f7dd6db513d5b62799f1c06f0eecce4312e106112143f39583e943`;
- CRC1/CRC2 `26D042AF / 7B8C4C36`;
- file `0x87 = 0x4E788`.

v65 kept the compact two-frame asset pack, installed the chest art on the real player through a proof-only wrapper at the straight-Ice animation call, suppressed both stock Ice helper-process spawns at ROM `0x4BA68` and `0x4BA84`, initialized the missile presentation earlier, requested the normal Sektor palette, shifted the inherited Ice spawn by a hardcoded 96 pixels toward Sektor, and added a proof-only per-tick acceleration callback (`v += v >> 4`, cap `0xE0000`) over an initial `0x40000` speed.

**Rejected / failed.** Runtime showed the correct chest-open Sektor frame, but the game immediately hard-hung. This proves the chest asset itself can be rendered on the player; it does **not** validate the v65 lifecycle wrapper, helper-process suppression, hardcoded placement, or flight graft.

### v66 — lifecycle-wrapper correction attempt

Disposable proof: `MKMSZR_sektor-missile-lifecycle_common-proof_v66.z64`.

Builder: `MKMSZR_build_sektor_missile_lifecycle_v66.py`.

Identity:
- SHA-256 `4c3ad9f0330f6422920374495324324d5baf0ad009071e45eb78916981248c32`;
- CRC1/CRC2 `626C2EB2 / 4F3966EE`;
- file `0x87 = 0x4E788`.

Relative to v65, v66 changed only the player-animation lifecycle wrapper (plus resulting header CRC). Chest art, missile setup, hardcoded spawn adjustment, acceleration code, test-only max-XP gate, and v62 combo behavior were intentionally unchanged. The wrapper attempted to mirror stock `0x80030E98`: select the primary animation through `0x8002FE54`, redirect the current animation cursor to the dedicated chest script, then let stock `0x80031070` run it.

**Rejected / failed.** The user reported the exact same immediate hang as v65. The “manual sleep versus stock runner” hypothesis is therefore rejected as the sole explanation.

### v67 — restore first Ice helper process only

Disposable proof: `MKMSZR_sektor-missile-process1_common-proof_v67.z64`.

Builder: `MKMSZR_build_sektor_missile_process1_v67.py`.

Identity:
- SHA-256 `216faa071a8685f19423c29a251901eb372c1a79749c3219d974cffa2c6e45ae`;
- CRC1/CRC2 `626C6D34 / AF24ACE8`;
- file `0x87 = 0x4E788`.

v67 is a one-variable diagnostic over v66. The first stock Ice helper-process creation at ROM `0x4BA68` is restored exactly (callback `0x80060A3C`); the second process at `0x4BA84` remains suppressed. All other v66 chest/missile code remains unchanged.

**Rejected / failed.** Entering the special still hard-hung immediately. A different/extra spawned visual became visible before the hang, proving that restoring the first process changed presentation state, but it did not repair the core action lifecycle. The first helper process was therefore not the sole missing requirement.

### v68 — stock-lifecycle chest-only negative control

Disposable proof: `MKMSZR_sektor-chest-stock-lifecycle_common-proof_v68.z64`.

Builder: `MKMSZR_build_sektor_chest_stock_lifecycle_v68.py`.

Identity:
- SHA-256 `cce10a4a8762f429730e74d62f4da3029a22d16b11d72cd2d7e9b7b88563bfc0`;
- CRC1/CRC2 `D9D0A7C9 / 5D4FC053`;
- file `0x87 = 0x4E728`.

v68 deliberately removed the missile experiment from the diagnostic:
- only the single chest frame remains as a new asset;
- both stock Ice helper-process spawns are restored;
- stock Ice projectile setup/flight is untouched;
- the stock player-animation helper `0x80030E98` is left intact;
- a wrapper temporarily redirects the presumed resource-table entry for the straight-Ice player-animation call, calls the stock helper, then immediately restores the entry.

**Runtime-confirmed stable negative control.** The game no longer hangs. The chest frame never appears. The familiar blue/frozen Sektor helper/projectile presentation remains.

This establishes two things: the broad stock Ice lifecycle itself is stable in the takeover composition, and the v68 temporary table substitution did not reach the actual resolved player-animation source consumed by the move.

### v69 — post-helper resolved-cursor chest proof

Disposable proof: `MKMSZR_sektor-chest-postcursor_common-proof_v69.z64`.

Builder: `MKMSZR_build_sektor_chest_postcursor_v69.py`.

Identity:
- SHA-256 `386bd9e7263da5101ec9727ff0de072ffc666493510f4efe0b827c5cf29e373d`;
- CRC1/CRC2 `39F6CA1C / AB5D2C9F`;
- file `0x87 = 0x4E71C`.

v69 keeps the entire stock Ice action, helper-process, projectile, collision, and cleanup machinery intact. At the single straight-Ice player-animation call it:
1. lets stock `0x80030E98` finish normally;
2. reads the current process at `0x802ECE20`;
3. saves process/controller animation cursor `+0x6E4`;
4. temporarily points `+0x6E4` at the dedicated chest script inside file `0x87`;
5. calls one stock `0x800304C0` animation advance to install the chest frame;
6. restores the original cursor immediately.

**Runtime-confirmed.** The genuine chest-open frame appears on Sektor and the game continues normally. It lasts only one frame, which is expected for this diagnostic; hold/recovery timing was intentionally not implemented.

This is the narrowest durable player-animation result from the missile line: **current process/controller `+0x6E4` is the live resolved animation cursor, and a one-frame post-helper substitution through the normal advance path is safe on the tested route.**

### v70 — first genuine missile-flight presentation proof

Disposable proof: `MKMSZR_sektor-missile-flight_common-proof_v70.z64`.

Builder: `MKMSZR_build_sektor_missile_flight_v70.py`.

Identity:
- SHA-256 `5fe374e8702e99c6e5361b2637dcdd5bd4e743f58abbbbbdba2ad63aa283d8ae`;
- CRC1/CRC2 `99A3FF57 / 916A810F`;
- file `0x87 = 0x4E790`;
- `0x24C` bytes above the v49 working footprint.

v70 preserves the Runtime-confirmed v69 chest-marker mechanism and the complete stock Ice parent/helper lifecycle. It adds the single horizontal rocket frame back to the compact resource, points the basic projectile animation loop at that rocket, attempts to bind the projectile to the normal/native Sektor palette, installs the first missile frame earlier in the projectile path, applies the same proof-only 96-pixel spawn correction used by the earlier line, sets initial speed `0x40000` and animation rate 3, and attaches the proof-only `v += v >> 4` / `0xE0000` acceleration callback. Stock Ice collision/freeze semantics remain intentionally unchanged.

**Partially Runtime-confirmed.** The observed frame sequence is:
- Sektor displays the chest-open pose;
- two blue Ice helper/fallback Sektor actors appear below;
- a third blue Sektor-like projectile frame flashes for one frame;
- that projectile becomes the genuine missile;
- the first two helper actors disappear and the missile continues travelling.

Both the helper actors and missile retain a blue/ice tint. The user also reports that the missile spawns far too far from Sektor, moves slowly, and does not visibly accelerate as the intended Sektor rocket should.

The positive result is narrow: the imported horizontal rocket asset reaches the live projectile and travels without the v65-v67 immediate hang. The negative result is more important architecturally: mutating the existing Ice projectile path with hardcoded target offsets/velocity callbacks is **not** a faithful donor-move adapter. v70 is therefore superseded as the implementation strategy by the source-level compatibility approach in [MKT adapter primitives](MKT-Adapter-Primitives), where donor projectile creation, owner-relative placement, process ownership, flight callback, collision/strike meaning, palette/effect semantics, and cleanup are translated explicitly.

### v71 — native-placement / setup-helper acceleration experiment

Disposable proof: `MKMSZR_sektor-missile-flight_common-proof_v71.z64`.

Builder: `MKMSZR_build_sektor_missile_flight_v71_delta.py`.

Identity:
- baseline v70 SHA-256 `5fe374e8702e99c6e5361b2637dcdd5bd4e743f58abbbbbdba2ad63aa283d8ae`;
- output SHA-256 `8fbae98e3a66cf74c6e631069993451930de2f0febe58626be3eb78dfe809c6b`;
- CRC1/CRC2 `BCFB8436 / C965E1C4`.

v71 changed two variables relative to v70. It replaced the post-creation 96-pixel X correction with direct arguments at the stock `0x80031208` placement seam, using retail-MKT-derived `(+5,+38)`, and changed the projectile movement path to use retail initial/cap constants with the target setup helper `0x8004CC14`.

**Rejected / failed at runtime.** Approximately 1-3 frames after entering `F,F+LP`, emulation hard-hung. Before the freeze, the inherited blue/frozen Ice helper actors were visible around Sektor. This is a bounded runtime failure; it does not establish which of the two v71 changes caused the hang.

Post-test static tracing resolves one ambiguity. The actor at controller `+0x648` passed to the stock `0x80031208` call is the same secondary actor also held at `+0x714` and later promoted by `0x8004CBC4` into child `+0x6E0`. Therefore the hypothesis that v71 positioned an unrelated Ice helper actor is **Rejected / failed**.

A separate static defect remains in v71's movement graft: `0x8004CC14` is a projectile setup helper that writes facing-aware X velocity and calls `0x80031724` to initialize animation timing. v71 reused it from the per-tick acceleration callback and supplied a rate derived from the velocity calculation, so it mutated animation-rate state every flight tick rather than merely updating velocity. This is **Static-confirmed as a semantic mismatch**, but it is not yet proven to be the sole cause of the runtime hard hang.

Post-v71 coordinate tracing also closes the placement-unit question. On a fresh token-`0x0B` projectile, `0x80031208` takes signed whole local X/Y offsets, mirrors X for actor facing, rotates the local vector into MKMSZ world XYZ, and adds the result to the actor's 8-fractional-bit position fields with `<<8`; there is no hidden target scale. MKT's source `SCX(7),SCY(45)` becomes retail N64 `(+5,+38)`, so the direct target placement arguments are also `(+5,+38)`. This is **Static-confirmed** and means v71's placement values themselves were semantically well-formed even though the combined v71 build failed.

The stable runtime baseline for further work remains v70. The next proof should be placement-only: retain v70 movement/lifecycle unchanged and replace only the stock Ice local spawn displacement with `(+5,+38)`.

### v72 — placement-only proof

Disposable proof: `MKMSZR_sektor-missile-placement_common-proof_v72.z64`.

Builder: `MKMSZR_build_sektor_missile_placement_v72.py`.

Identity:
- SHA-256 `355c4bfbb9d2c0f0d21f6e8bc628defa530f79bc0f322fae3ca48bb1ce088fca`;
- CRC1/CRC2 `64A77F51 / D38D06E4`.

v72 is a strict single-variable delta from the Runtime-stable v70 missile proof. It leaves v70's projectile child code, movement callback, collision path, helper-process composition, imported rocket asset, chest marker, and `F,F+LP` binding unchanged. The only behavioral change is placement:
- stock Ice placement arguments at `0x80031208` are replaced with translated donor-retail local displacement `(+5,+38)`;
- v70's later proof-only `+/-96`-pixel X correction is removed.

**Runtime-confirmed placement proof.** The move no longer hangs. The genuine rocket appears close to Sektor at launch, and the placement mirrors correctly when Sektor faces the opposite direction. User observation suggests the visible rocket may sit somewhat high, while X may be correct or slightly close; this is not sufficient to reject the engine-coordinate translation because imported-image anchor/origin remains a separate presentation variable.

The missile still travels at the inherited essentially constant v70 pace and retains the blue Ice tint/helper presentation. Those are expected negative controls because v72 intentionally leaves v70 movement and palette/effect behavior unchanged.

Durable conclusion: the generic donor-retail placement mapping `place_relative(projectile, +5, +38)` is now **Runtime-confirmed on the tested route**. The next isolated gate is movement/acceleration translation; do not perturb the placement result while testing it.

### v73 — movement-only acceleration proof

Disposable proof: `MKMSZR_sektor-missile-movement_common-proof_v73.z64`.

Builder: `MKMSZR_build_sektor_missile_movement_v73.py`.

Identity:
- SHA-256 `a6cbf8c061df46c5a85668680ba268153a55ea2f293e3bd87db6b148abcfd36b`;
- CRC1/CRC2 `53EF29D9 / FDB4C45C`.

v73 starts from the Runtime-confirmed v72 placement proof and changes only the projectile child movement program. Placement remains direct native local `(+5,+38)`; stock Ice helper-process composition, chest marker, collision path, imported rocket art, blue Ice presentation, and `F,F+LP` input remain controls.

The movement proof uses the donor-retail normal branch:
- initial magnitude `0x33333`;
- each flight callback computes `abs(v + (v >> 4))`;
- magnitude caps at `0xB3333`;
- direction sign is preserved;
- only projectile actor `+0x14` is mutated per tick;
- `0x8004CC14` is **not** called from the per-tick callback;
- donor reacting-target initial speed `0x59999` remains Pending because a target `target_is_reacting()` semantic has not yet been established.

**Runtime-confirmed acceleration behavior / calibration Pending.** The user reports that the missile definitely accelerates, never hangs, and retains the successful v72 placement. The exact perceived start speed, acceleration rate, and cap are not yet confirmed as donor-faithful in target physical units; the user notes that the inherited Ice sound/tint, missing rocket smoke trail, and MKMSZ camera tracking make visual speed judgment difficult.

Durable conclusion: direct per-tick mutation of projectile actor `+0x14` is a viable stable host seam for translated acceleration at v73 scope.

#### Post-v73 velocity calibration

The requested static calibration closes the main numeric ambiguity:

- MKT uses 16.16 `oxpos/oxvel` and directly performs `oxpos += oxvel` each nominal 60 Hz loop.
- MKMSZ `0x80017F80` reads projectile `+0x14`, shifts it `>>8`, rotates the local velocity, then adds **three times** the transformed integer into fixed8 world position.
- MKMSZ ordinary movement/render cadence is approximately 30 Hz, consistent with its main-loop retrace gate and independent frame-step observations.

Under the v72 local-unit mapping, a constant donor velocity therefore maps to approximately `2/3` of the donor numeric field on MKMSZ. The steady-state straight-rocket equivalents are `0x33333 -> 0x22222`, `0x59999 -> ~0x3BBBB`, and `0xB3333 -> 0x77777`.

However, v73 also applies the donor `+1/16` recurrence only once per 30 Hz target callback, whereas donor MKT applies it once per 60 Hz tick. Thus v73 combines an over-large raw host velocity field with a too-slow temporal acceleration recurrence. This reconciles the runtime report that acceleration is obvious but the overall motion still does not confidently feel donor-correct.

The faithful next proof should not merely replace the three constants. It should preserve donor-space velocity state and pair two donor 60 Hz motion intervals into one MKMSZ 30 Hz interval. For normal launch `d0=0x33333`, `d1=0x36666`, the first host interval is approximately `(d0+d1)/3 = 0x23333`; later callbacks advance two donor recurrence steps, use the pair displacement divided by three as host `+0x14`, and retain the later donor state. This **Static-derived resampler remains runtime Pending**.

### v74 — cadence-resampled movement proof + donor-video comparison

Disposable proof: `MKMSZR_sektor-missile-resampler_common-proof_v74.z64`.

Builder: `MKMSZR_build_sektor_missile_resampler_v74.py`.

Identity:
- SHA-256 `1b51e8f0ae2226137a8cfb88ad182f50d0d739c46c7ad7a4cacb88f7ec2328e3`;
- CRC1/CRC2 `29CA7A70 / 1E35BD21`.

v74 keeps the Runtime-confirmed v72 placement `(+5,+38)`, the stock Ice helper-process scaffold, collision/lifecycle path, imported rocket art, blue Ice presentation, and `F,F+LP` binding. It changes only movement magnitude/timing relative to v73:
- initial host field `0x23333`;
- per-target-tick folded recurrence `h += (h >> 3) + (h >> 8)`, equivalent to two unclamped donor `17/16` substeps;
- host cap `0x77777`;
- no per-tick call to `0x8004CC14`.

**Runtime-confirmed stable, fidelity still incomplete.** The user reported v74 feels slower than MKT and supplied side-by-side 60-fps recordings. Frame-by-frame analysis measured seven clean MKT flights and five clean v74 flights. The repositioning jumps/somersaults were excluded.

Quantitative comparison:
- median 30%-to-85% normalized screen transit: MKT about `0.296 s`; v74 about `0.532 s`; v74 takes about `1.80x` as long;
- median late 70%-to-85% normalized screen speed: MKT about `2.13` screen-widths/s; v74 about `1.08` screen-widths/s;
- in the supplied recording dimensions, late motion is about `2032 px/s` for MKT versus `994 px/s` for v74, a ratio of about `2.04x`;
- MKT visibly advances the projectile on each captured 60-fps frame; v74 usually holds each position for two captured frames, corroborating the 60-Hz donor versus ~30-Hz target cadence;
- both trajectories reach their late-speed plateau in roughly `0.3-0.35 s`, so the folded temporal resampling is substantially closer even though the absolute target velocity is too small.

Durable correction: the earlier `2/3` target-field derivation was conditional on an unproven **one donor local position unit = one MKMSZ world unit** assumption. v74 comparative runtime evidence rejects that assumption as a complete fidelity conversion. The target integrator and cadence derivation remain valid, but the adapter still needs a donor-local-to-target-world spatial scale. On this tested camera/route the missing projected-motion factor is very close to `2x`; this is a bounded calibration candidate, **not yet a universal cross-engine constant**.

The supplied donor video also shows the genuine two-frame rocket presentation and recurring smoke trail, while v74 retains the blue Ice tint/SFX, two inherited helper actors, and no donor smoke. Those presentation differences affect perceived energy but do not explain the measured ~2x coordinate-speed gap.

Raw evidence archived in Library:
- `06 - Screenshots and Evidence/MKMSZR_SEKTOR_MISSILE_V74_RUNTIME_2026-09-24.webm`;
- `06 - Screenshots and Evidence/MKT_SEKTOR_STRAIGHT_MISSILE_DONOR_2026-09-24.webm`;
- quantitative report `07 - RAM Diffs and Experiment Data/MKMSZR_Sektor_Missile_v74_Video_Comparison_2026-09-24.md`.

The next bounded movement proof should retain v74's cadence folding but test the missing spatial magnitude separately; do not combine it with placement, smoke, palette, audio, or helper-process cleanup.

## Teleport-uppercut proof line v01–v08 (2026-11-07)

**Runtime-confirmed bounded: the move in v08 (user report "Everything looks and works really good") and Sektor's MKT teleport sound in v09 ("just perfect"); v10 is v09 without the landing thud (built, quick check pending); shadow behaviour unchanged.** This is the first end-to-end imported Sektor special: MKT `F,F + LK` teleport uppercut (`do_body_propell(8)` → `0x80048368`) on the Sektor takeover body. It ships as one disposable ROM per iteration (body repack + move). The donor-side analysis is in [MKT adapter primitives](MKT-Adapter-Primitives#sektor-teleport-uppercut-translation) and the host findings are in [Player actions and special moves](Player-Actions-and-Special-Moves#teleport-uppercut-host-findings-2026-11-07). Builders: `Experimental/SektorTransplantBuilders/teleport/MKMSZR_build_sektor_teleport_vNN.py`, run as `python3 <builder> <clean MKMSZ> <MKT Rev. 2> -o <out>`. All eight reproduce their ROMs byte-for-byte from the two clean inputs.

User decisions that define the target behaviour:
- classic controls only;
- silent at first; then (after v08) Sektor's own MKT sounds rather than MKMSZ ones, because Sektor replaces Sub-Zero completely. The donor landing thud is not wanted, since the stock landing sound already plays;
- the move can start airborne and cannot be cancelled;
- range is a distance square (same limit horizontally and vertically) of roughly 90–95% of the starting camera's visible ground width on Temple/Fire/Water/Earth, ignoring zoom;
- the hop is about a normal jump, using the user's MKT capture as reference;
- Sektor falls on the last uppercut frame;
- sink and emerge read as leaving and entering the screen;
- the shadow may stay as it is if fixing it is costly.

### Identities

| Proof | SHA-256 | CRC1 / CRC2 | Runtime result (user) |
|---|---|---|---|
| v01 | `135659ebf18455435ab8b6eb354949d41af546ed82716bebe24d678ef98d4769` | `A9E75D9E / FF64623D` | 16c/4bpp body works; animation correct but no sink; target never hit; Sektor invisible in Wind; teleports to off-camera targets |
| v02 | `587a657e9d40208bd47e8728c1cd5e7271d5c7febb63d0eb4a98b9dc91b216e4` | `A9E75D9E / FF64623D` | Hit lands and visibility fixed; no sink; sweep-type reaction; range too long; cannot start airborne |
| v03 | `5826eb8e5a04b1e6fe270e3330bda5de991c218d8179180897c6e7140afa5918` | `A9E76426 / B4E3CBFC` | Sink looks good but reads as going through the floor; punch-type reaction; no hop after the hit (stops and is grounded at once) |
| v04 | `3a0cba0b232626fcace49f4534e2aad5d7522336cfab2050b78be69a33ce397b` | `A9E7661E / FEDE07EC` | Uppercut reaction and distance range accepted. Problems: an airborne start pauses at ground level; shadow stays; hop too strong (camera rises); an airborne start with no target falls as if hit; no last-frame descent; cancellable by any action |
| v05 | `455bf5c3195049fd3bc29be64277c41c461b6ffe15c5adce484ff07ad63f5319` | `A983662E / C9C25F79` | Shadow still visible; after the hit, stock jump-fall animation; still cancellable by every button and special |
| v06 | `17b878cbfc472bb5e9f6c0841f09dc6036a8f3ec720b554228d0715e72dba271` | `A983662E / A9CA554A` | **Not cancellable (confirmed).** Move still ends as soon as it hits |
| v07 | `3864fc3ad5733dd01ae39ac6dbeebce5b80d24d55cdd78cc0c1bf9b8cce50f74` | `A983662E / 0466CE32` | **Hop, arc, last-frame descent and landing work.** Against a cornered enemy, Sektor falls back as if hit mid-air |
| v08 | `85f09d8a99d9f5aa2c4aba631e3d042922ed24915c0213da99cb6305cf5edebd` | `A983665E / 36E3F2EF` | **Accepted:** everything works; only sound (deliberately silent) and the shadow remain |
| v09 | `51007a411ef9ed2646e28a8eba50bc9bc077b120de3cd5a6c5cabb60ff4afdf3` | `A983623E / B90F3AC2` | **Teleport sound "just perfect".** The added landing thud was too loud and redundant with the stock landing sound |
| v10 | `913ebc2b02ed935515848d1615bc81538620e2f7cd4c678c4ea11bfbd882f56b` | `A983622E / 64626E81` | v09 without the landing thud; built and statically checked, quick runtime check pending |
| v11 | `1682507985ce89199e5844442a750577dec97fbf64d74d4f2119ab70d21cde5a` | `A983622E / 64626E81` | **Worked perfectly:** post-hit timing matched to MKT, so the standing-LK juggle connects |
| v12 | `12e15eb39a92456f5025700fe81794ef5bc613e575320864ae50268134535733` | `A9CB6252 / E3A446C6` | **"Everything sounds perfect"** (a bit loud): Sektor's MKT voice set replaces Sub-Zero's |
| v13 | `af951e47789ff58942feb0b8a3b5a532ad72cd4619178a8b033e814536dbbcfb` | `A9CB6252 / E3A446C6` | Adds the robot run sound. Correct, but repetitive and annoying in MKMSZ, so dropped |
| v14 | `c62dc1a9baad3fc3e4cac884587300d38ff4d7183d7c8983dd5a242583a82ebf` | `A9CB6580 / AF5E62DB` | Voice from MKT's voice-group table. **Rejected:** the group-9 "death scream" is a human pit/fatality scream and played on knockdown landings |
| v15 | `06e3d306f89c7c5b4e6cc3bfabcfd4f805a1865630c7c012756368d8db1b0918` | `A93F6580 / E79F491A` | **"It's fantastic now":** knockdown landing and death silent; run sound removed |
| v16 | `7e6b15597d838c299f91804f6f5900881151b90db44a4d0e523a599ecbcf27bc` | `EF26B815 / 7A9A1448` | Adds Sektor's MKT combos (v62 graph). **Rejected volume change:** player categories 0/1 also play the somersault jump, so the "attack whoosh" ×0.85 lowered the somersault instead |
| v17 | `104e13ff9d92592b803d926b96470b66e7be6fd200781c1cbe4106a0421f4574` | `EF26B815 / 7A9A1448` | v16 with the volume change reverted. Combos work, but the kick endings lack their animation |
| v18 | `4335e1ad03c7c6a06a761cd34e7c92a071064a12a533d184b8ab5bedd875ea02` | `EF26B815 / 7A9A1448` | Adds v59's late-Knee frames (`KNEE_LATE_MAP`); runtime check pending |
| v19 | `4335e1ad03c7c6a06a761cd34e7c92a071064a12a533d184b8ab5bedd875ea02` | `EF26B815 / 7A9A1448` | Importer refactor (R1): the action comes from the `fighter_import` primitive library. The ROM is byte-identical to v18, so no runtime test is needed |
| v20 | `669424a1e5aa5f5ee7666405f01a4fc89458ad09dbeea4377eca3c4e0c179f9e` | `2FF93E88 / C088FDC8` | **Runtime-confirmed:** stock Ice Blast re-hosted as a lifted copy (selector 4) behaves exactly as before |
| v21 | `3b7695ddce69526acb69f963d90a4aa3a1b4d3655ece583515011150cbafecb7` | `3F8F746B / F4E1AD85` | Rocket art and palette correct from the first frame. One unreproduced inventory glyph corruption (per-shot texture-storage growth) |
| v22 | `3771cc920ed0768d9c12152fe6966f8a04efcdc14dc28db5930b9ebca50c0ca6` | `03B8BECA / 16310335` | **Rejected / failed:** hangs on D,F+LP then D,F+HK (the up-shot's 56×113 stance frame overran the fixed 368-byte slot buffer) |
| v23 | `06e46044da64fa5aa3b2822a436ee4916d4a5844c22f3251ba83848eba3b8b89` | `C8DC78F2 / 288B36F3` | **Runtime-confirmed:** no hang, no allocation; first frame still correct |
| v24 | `3bae3da809045d7327a6995364bfaa616c8f9d4d4ffc8ca3199089a52eecde24` | `C8DC78F2 / 288B36F3` | MKT placement passed unscaled: rocket too high, slightly inward, drawn over Sektor |
| v25 | `8f419a02ea315355763cb2e957ac416120257dc6329a57d159e5c8dc5f8b3b05` | `3E3C6526 / AF74FA90` | Height and draw order accepted; teleport reappears on the target's floor |
| v26 | `bf195177e8388119b3e87b1d9189dad96c6349c52ef5bfcf6a6bc1fbe8ddfd13` | `3E3C6526 / AF74FA90` | **Runtime-confirmed:** MKT chest open/hold/close animation |
| v27 | `0a0f44b7f09e4b24c9ae9915aa4547e41ededf79903bf32b7ff051ee17151905` | `D9436343 / AF11EC0E` | **Runtime-confirmed:** MKT flight (two frames, speeds, reacting start, acceleration, cap). Flame still visible behind Sektor at launch; ending lag reported short |
| v28 | `383aca9481a757bbae217883c612fa2f0f716aa3587b53ca33d97e914b49ae74` | `D9436343 / AF11EC0E` | Spawn +4 px outward (runtime-observed correction); confirmed through v29 |
| v29 | `a158c19faf62b84ddf68e3d7736cec3c88f848959b78b1c1000746c67ddf5e98` | `2FFA6768 / DC6270B5` | **Runtime-confirmed:** same behaviour as v28 ("works as before"); code moved out of the graphics-microcode area, 16 KiB arena |
| v30 | `e9e19fab8d5897526ad8cd27a9be06cbd7071896991e0a67742ff8eca16baf6a` | `2FFB9768 / 7FF1DA86` | **Runtime-confirmed:** MKT rocket sounds (chest open, launch, boom) |
| v31 | `2be04433df354e83684579603a2c761937664fdedf860fe6886e314f17151e1a` | `2F9A7F88 / B63590D5` | MKT rocket strike. Airborne reaction accepted; grounded stumble (stock reaction `0x24`) far too weak; a point-blank shot still froze the target |
| v32 | `d7922053eeea6e48261bbd97975458483055338e0252c61116f8dbe2c8d24d59` | `2F9A7F88 / B63590D5` | Point-blank hit through the rocket record; teleport damage back to MKT `0x10/2`. Superseded by v34 without a separate report |
| v33 | `6d729a55de78f1c0a4806b4dc408fb479cfda87cbdab470bab1fcbcd94000ad4` | `2F9FB368 / 429E7533` | Lifted reaction `0x24` with MKT-converted push. **Superseded** by the user's direction to use the Fire spiked-rod trap reaction |
| v34 | `e125a89be93d05dfc5e586c0f6810e8f63912a981f45ea8865efb6508329f1da` | `2F9A5388 / BD26076F` | Fire trap stumble works, but the hit felt delayed (the trap's own 8-tick hit pause; MKT has none) |
| v35 | `35120e43b73c5dc9f699c8b9fec137bf531920d30b46ff57539eec0c0230f4d0` | `2F9F4F70 / 4EB3F719` | Smoke trail and explosion render. **Hangs** near the end of the explosion; smoke disappears too quickly |
| v36a / v36b | `1e5e9c494ca44f5941dbaaa4b4c30160defe3360e52cc060d79cba7344ac4384` / `f1cdea66b17c9602834930c81848d3b0c559f3ace5a370b8955bf19e572d9195` | `2F9AD7B0 / 2587C05C` / `2F9F4F80 / AE6BB45D` | Diagnostics: a (trap pause restored) hangs, b (no explosion) does not |
| v37a / v37b | `0f62222d8b829e646589283793614b09b0749eead01301bd8d7c0051581ce728` / `0a41e52a3ae3f14381063fb5d7273464794ae19080aa7eac875d78de981a25d3` | `2F9F4F70 / 4EB3F719` / `2F9F46F8 / 4779E0F1` | Diagnostics: both hang (a: widths padded, stops on frame 7; b: frame 7 dropped, stops one frame earlier). Odd frame width **Rejected** as the cause |
| v38c / v38d / v38e | `1d25696713f5f3fd1bc5abca3837cb94d15eaba986a6f66b7cf2cd41c4648ffe` / `157b6fed45da1c2d31396ebe77208f213004ff366003dad87aa16955f31ef58b` / `51b21c9bb8fd0bef7eeeab12c9f1a8f3b874d3c5b38536bfbf074f183e271a83` | `2F9F4AF0 / D4E2186F` / `2F9F49F8 / 575D86D9` / `2F9F4F70 / 4EB3F719` | Diagnostics: c (raw six-frame explosion, no smoke) does not hang; d (no smoke) and e (Ice hit visuals kept) hang |
| v39 | `ccc0eb8d4a52eba7287f20c144627a4326c090c2547b84321e553466dcd63417` | `2F9F4EF8 / 37E07300` | **Runtime-confirmed ("it works fantastic"):** hang fixed (zero word before each effect descriptor). The launch-time Ice clones are still there |
| v40 | `670fe45a3e4b9bc3f9238051413b6acf5f16aaf2ad5b13289891a2f7ef63a5c1` | `2F9F48C8 / AD5C2BFB` | **Runtime-confirmed:** no Ice clones or tint at launch; teleport rises from the floor against an airborne target. The user marked the rocket done |
| v41 | `55a29201f738b8fadd7d83914f694adb46ae33e530cab66197708e29ac71f3a1` | `2FA8B4DC / E17A95A1` | **Runtime-confirmed ("working as expected"):** Sektor's MKT throw sounds |
| v42 | `87154a9d205661ec5bde32fdcf9070fd141df77f514fd7ef7fd80f05252913ae` | `6FA520CA / B7719F66` | Heat-seeking rocket on `F,D,B + HP` (R3). Works ("it works! Perfectly!"), but the rocket sometimes passed through enemies and the crosshair had a purple border |
| v43 | `05c20276e76c842bc627dcb0427be11a52c6f6e7112bf8dd8f2096400e76ac39` | `6FA52E76 / 00ED8E0C` | Effect palettes bound past the record's count word (crosshair, smoke and explosion colours had been two entries off since v35); donor 6-px proximity test. Superseded by v44 before its own test |
| v44 | `0ea931bb9f39f708f51be7c4de802547f55e6e18c37899269fefa466ba50c189` | `68512E76 / AB0F8B94` | Straight rocket on MKT's `F,F + LP`. After a kill, the homing rocket and crosshair chased the dead enemy (user video, Wind) |
| v45 | `4f5d3257f12adf99cb8fca0b0e1600d9807f3b3dee0de063da1b4248993198aa` | `6854727E / 956FB0C4` | **Runtime-confirmed ("all working wonderfully"):** homing target = nearest living enemy in the teleport's range; v43's colours, proximity and v44's command included |
| v46 | `12f13ce451d672e2686a10e45a12264a80751f670096c9fe77ce9e1d2bd62db5` | `A8261389 / B7CE9896` | **Runtime-confirmed ("really good"):** Double Missile on `B,B,F + LP` in place of Ice Clone. The user marked Sektor complete |

Builders import the importer library (`src/mkmszr/fighter_import`). Each builder reproduces its ROM byte-for-byte at the commit that added it: v30 `eb6022a`, v31 `7205271`, v32 `56e42f3`, v33 `c528392`, v34 `e955be3`, v35 `13f3859`, v36 `c06daa8`, v37 `6a940a0`, v38 `b01f9e6`, v39 `6488cca`, v40 `73a77d3`, v41 `d49a089` (checked for v31, v33, v35 and v36a), v42 `80e7c33`, v43 `aa2218f`, v44 `e9f9cad`, v45 `959c155`, v46 `df52ccf` (all five checked). At `d49a089`, v30, v34 and v39–v41 still reproduce; the others build differently because later library fixes change their output (for example v35's builder now produces v39). At `df52ccf` only v46 reproduces: v42–v44 no longer link and v45 differs, because the R3 library gained the target picker and the double-launch state.

### Version changes

- **v01:**
  - Body: the v05-equivalent Sektor body repacked as a 16-colour 4-bpp Type-5 (file `0x87` end `0x45BE0`, under the Fortress-safe `0x4E544`).
  - Move: the teleport adapter on the exact Reverse Elbow v6 host infrastructure.
  - Failures: it hid Sektor with actor `+0x64` bit `0x20` and added gravity in its own loop, which together with the engine's gravity gave 3× effective gravity. Its strike record lay in the KSEG1 payload.
- **v02:**
  - The strike record moved to the stack, giving a KSEG0 pointer (the collision core checks the top nibble is `8`).
  - The hide bit was removed.
  - The engine applies gravity; velocities are calibrated by matching the two stock jumps (donor `-0x88000/0x6CCC`, host `-0xB47AE/0x7851`).
  - Targets must be on screen via `0x80035260`.
- **v03:**
  - Range: a 90% viewport projection test.
  - Sink: frames cropped at the feet line.
  - Airborne start: falls to the ground first.
  - Payload arena widened to `0x800` bytes.
  - Hit selector changed to crouch-punch.
- **v04:**
  - The strike record is the stock uppercut's reaction, aux and trailer (reaction `0x08`).
  - Range: a 592-unit square on `|Δx|`, `|Δy|`. That is 0.925 × the 640-unit visible ground width at camera depth `0x200`.
  - Sink and emerge use descriptor-only anchor-shift aliases, so the image moves below the screen without any cropping.
  - Emerge velocity is anchored on the donor curve.
- **v05:**
  - Hop velocity × 0.9: from the user's apex captures, v04 peaked at about 1.04 enemy heights against MKT's ≈ 0.92.
  - A custom descriptor condition rejects the move before it starts when there is no target.
  - Action ID `0x603`.
  - An airborne start continues the sink from the donor-curve index already reached.
  - Its own ground reference replaces `+0x6B4`.
  - Shadow attempt: detach and hide actors flagged `+0x8C & 0x2000`. It had no effect (Rejected).
- **v06:**
  - Native special-action begin `0x80049F90` (busy input map) → not cancellable.
  - The adapter drives the hop itself, using engine-equivalent integration with `+0xF0` re-set each tick.
  - The shadow attempt was removed.
- **v07:**
  - Root cause of "ends on hit": the per-tick floor check installs the stock fall routine `0x80025230` when no floor region is found and the ctrl `+0x6B0` word is zero.
  - Fix: maintain the airborne counter `+0x6B2` every air tick, as the stock jump does, and clear it on landing and before exit.
- **v08:**
  - Placement follows the donor: Sektor appears past the target on the far side and turns to face it.
    - Distance is `min(40, wall room − 4)`.
    - If that leaves less than 16 units, the target is nudged out of the corner to 16 units of separation.
  - This keeps the uppercut from knocking a cornered target into the wall, which triggers the stock corner pushback.
  - Damage `0x10 → 0x18` and chip `2 → 3` (1.5×, user request).
- **v09:**
  - Adds the donor sounds of the move ([translation](MKT-Adapter-Primitives#sektor-teleport-uppercut-translation)).
  - Teleport sound: MKT event `0x104`, played at the move start. It goes through MKMSZ event 335 → patch 492 → subpatch 335 → waveform 325.
  - Landing thud: MKT event `0x92`, played on touchdown. It goes through MKMSZ event 437 → patch 594 → subpatch 437 → waveform 427.
  - Both hosts are fully isolated stock chains ([Audio system](Sounds-and-Music#isolated-sound-host-chains-2026-11-07)).
  - Playback copies the stock `0x80064C18` sequence: parameter block `0x802C1188` = `{0xB, volume 0x7F, 0x40, 0}`, then `0x80080A88(event, 0, block)` between the `0x800008D4/0x800008DC` pairs.
- **v10:** the landing thud is removed and its host chain left stock.
- **v11:** the post-hit arc keeps the accepted apex but matches MKT's real-time airtime. Launch velocity is ÷0.924 and gravity ÷0.924² (donor 0.602 s; v10 0.633 s). The landing hold drops from 4 to 3 ticks, matching the donor `0x80076E48` hold of 2×3 ticks at 60 Hz. Sektor can act 2 frames sooner.
- **v12–v15 (voice):** Sub-Zero's player-only voice events are re-pointed at isolated host chains carrying Sektor's MKT sounds. The final v15 rule is in [Audio system](Sounds-and-Music#imported-fighter-voice-rule-2026-11-07).
- **v16–v18 (combos):** v62's six Sektor combo records at `0xB1CB0` (byte-identical to v62). The standalone `HK,HK` record moves from `0x9AD90`, which is now this line's loader stub, into the payload arena (KSEG1 `0xA01AFB38`), with knee root `0xA1CE8` pointing at it. The combo walker `0x8004D4C0` follows any negative `+0x0C` pointer and fetches strike records from its own table `0x800B0D48`, so KSEG1 is accepted. v18 adds v59's late-Knee shape ownership, which this lineage had never received, so the knee's parts 3–5 show Sektor frames instead of the stance fallback.

### Straight rocket (R2) v20–v29

Sektor's MKT straight rocket is built by re-hosting stock Ice Blast and swapping donor behaviour in one piece per proof. The recipe is `fighter_import.actions.robo_zap`; every edit to the lifted Ice root is a declared word patch checked against the stock word it replaces.

- **v20:** the LP Ice Blast callback and root (`0x80049C34`, `0x8004AB84..0x8004B1D0`) are lifted into the payload; the callback transfers to selector 4 (the lifted root). Runtime-identical to stock.
- **v21:** ROCKETD1 (robot `+0x2668`, 39×9, anchor (26,3)) and ROCKET_P appended to file `0x87`; token-`0x0B` palette and pre-upload hooks (v87/v89 design). The pre-upload's `0x8001BF70` allocates from the texture bump pointer `0x801AE478` on every shot (no bounds check, reset only at stage setup), which can grow into the top-down dynamic textures (`0x8001C2B4`).
- **v22:** fixed 368-byte slot buffer. **Rejected:** the render pass's deferred upload (`0x800185B8`) copies each new frame into the slot's current storage with that frame's size; the still-stock up-shot script builds its projectile on the 56×113 stance frame and overran the buffer (hang).
- **v23:** no allocation: frame refresh (`0x8001BDA0`) plus the stock deferred copy done early (`0x8001D6EC` mode 1, `0x8001D7F0`) into slot `0x24`'s stock storage.
- **v24–v25:** sprite pixels are 2 world units (renderer `sll 1` at `0x800188F8`/`0x8001890C`), so MKT (+5,+38) px = (+10,+76). Draw order: sprite layer = `+0x5C×32 + +0xEC`, ordering table drawn from high to low; behind-owner idiom `+0xEC = owner + 1` (`0x80030D18`). Teleport: reappear at the target controller's floor `+0x6B4`.
- **v26:** chest open/hold/close (MKZAP.ASM `robo_open_chest_fast`, `sleep 0x20`, `robo_close_chest`): RBCHEST1/RBCHEST2 in the Zap script phases, closing frame 2 ticks.
- **v27:** flight: ROCKETD1/ROCKETD2 resampled to one frame per host tick (D1 D1 D2 D1 D2 D2); host speed per tick = 2 × (two donor speeds) / 3 from MKT's integer recurrence (start `0x46666`, reacting `0x7B332`, cap `0xEEEEE`; v75's accepted values, now derived); reacting = opponent `+0x6BE` bit `0x04`; flight child replaces `0x8004B82C`.
- **v28:** +4 px outward from the user's frame-by-frame MKT captures (not explained by anchor arithmetic).
- **v29:** see [RSP microcode text](Memory-and-Allocation-Map#rsp-microcode-text-inside-the-main-segment-2026-11-08). The token hooks are removed and the rocket setup runs from the lifted root after its token advance (`0x8004AEE4`); arena 16 KiB.

### Straight rocket (R2) v30–v41 and the throw sounds

- **v30 (sounds):** Sektor's MKT ochar sounds through isolated host chains (`fighter_import.sound`): chest open `0x0B` → MKT event `0x108` → host 173, launch `3` → `0x100` → host 175, boom `0x0A` → `0x107` → host 177. The chest sound wraps the root's open-phase call `0x8004AD38`; the Ice launch-sound block `0x8004AD58..0x8004AD98` is skipped and the launch sound plays at creation; the boom replaces the Ice hit sound (`0x8004BB94`) in a lifted copy of the hit child `0x8004BB64`.
- **v31–v32 (strike):** the rocket's own strike record (MKT `stk_ro_zap`: box `(16,−15,35,31)`, damage `0x14`, chip 2; host reaction and block selectors) in the payload; player type-4 strike-pointer entry `0x13` (ROM `0xB00D0`) points at it, because its stock record `0x800AF634` is shared with type 2. v32: the lifted straight helper's point-blank test (`0x8004B5D4`) reads entry `0x13` instead of the Ice freeze record `0x18`; teleport damage back to MKT `0x10/2`.
- **v33–v35 (reaction):** MKT `r_rocket` is a strong stumble back (airborne: knocked down). v33's lifted `0x24` with a converted push is superseded. v34 reaches the Fire spiked-rod trap stumble `0x80051280` through reaction index `0x23`, whose stock entry `0x8004E0C0` is an endless sleep that no strike table uses (reaction table `0x800A1190`, ROM `0xA1D90`). v35 points `0x23` at a lifted copy without the trap's 8-tick hit pause (`jal 0x80028794` at `0x80051318`).
- **v35 (effects):** MKT smoke puffs and explosion as native effect processes (`fighter_import.effects`, modelled on the stock Ice helper; see [Player actions](Player-Actions-and-Special-Moves#effect-actors-2026-11-09)). One puff per flight tick, 19 px behind the rocket along its heading, one sub-layer behind it. The explosion starts from the boom wrapper at the contact position, in front. The hit child no longer starts the Ice helper/tint processes (`0x8004BCB4`, `0x8004BCD0`). Art in file `0x87`: puffs raw (`0x110C` bytes), explosion type 4 (`0x2C24` bytes).
- **v36–v38 (hang bisection):** the hang always came 10–14 ticks after the explosion started, on varying frames; only builds with type-4 explosion frames 8 (or 7 in v37b) hung. See v39.
- **v39 (fix):** `0x8001BDA0` reads the word before a frame descriptor as a texture-slot override ([Data structures](Data-Structures-and-Encodings#frame-descriptor-and-the-preceding-word)). v35 put each descriptor straight after its type-4 image; frames 2 and 8 were preceded by token bytes (`0xA3000000`, `0x86000000`). Frame 8's value became a store at slot-table index `0x86000000`, i.e. into TLB-mapped space. Raw images end in transparent zeros, which is why the smoke and v38c never hung. The layout now writes a zero word before every descriptor.
- **v40:** the lifted root no longer starts the launch-time Ice helper pair (`0x8004AE68`) or blue tint (`0x8004AE84`). The tint call goes to a payload stub returning `scratch − 0x6F4`, because the three stores after it (`0x8004AEBC..C4`) would otherwise land in the player's own controller. Teleport: if the target's floor `+0x6B4` is unusable (`0x7FBC00` "no floor below", set while it flies high, or more than 512 units below it), Sektor reappears on his own floor before falling back to the target's height (v25–v39 reappeared in mid-air beside an airborne target).
- **v41 (throw sounds):** MKT `robo1_slam` sounds on the player throw `0x8005BC8C`: grab voice (voice group 3, event `0x67`) plus arm OUT (robot ochar 0, `0xFD`) at the grab, arm THROW (ochar 1, `0xFE`) before the throw phase, arm IN (ochar 2, `0xFF`) at the finish, through isolated hosts 332, 336, 437 and 453. Three stock call sites (`0x8005BCD4`, `0x8005BDC8`, `0x8005BDF8`) go to payload wrappers that play the sounds only when the thrower is the player, then continue to the stock call. Player voice category 11 (silent since v12) is the grab slot: its only callers are grab/throw paths ([Audio](Sounds-and-Music#imported-fighter-voice-rule-2026-11-07)).

Open details (the user marked the rocket done with these pending):
- smoke timing: MKT puffs grow about twice as slowly as v35–v41's (user observation, same spacing); the MKT/MKMSZ process-tick ratio needs a frame-count measurement and also governs the chest timing and the rocket speed check;
- explosion alpha: effect slots get the per-frame default render mode (alpha `0x80`); the stock Ice helper selects mode 1 (`0xC0`) through `0x8009A5F0` before taking its slot;
- smoke uses one process per puff and refuses to spawn while fewer than 16 processes/objects are free, which caps the trail on busy screens;
- MKT's faster chest open when the opponent is reacting; one rocket at a time (resolved: the stock root already refuses while a rocket process lives, see R3 below).

**Correction (v43).** The v35–v42 effects bound their palettes at the record start, so every smoke, explosion and crosshair colour was two palette entries off and the two lowest indices read the count word ([host findings](Player-Actions-and-Special-Moves#effect-actors-2026-11-09)). The "smoke disappears too quickly" and explosion-alpha observations above were made on those colours and have not been re-checked since.

### Heat-seeking rocket (R3), command fixes and the Double Missile, v42–v46

All four MKT Sektor specials now run on the Sektor body: the `F,F + LK` teleport uppercut, the `F,F + LP` straight rocket, the `B,B,F + LP` Double Missile and the `F,D,B + HP` heat-seeking rocket. Runtime-confirmed bounded in v45/v46; the user marked Sektor complete on v46.

- **v42 (R3):** MKT `do_robo_zap2` / `rocket2_proc` on the straight rocket's launch (`fighter_import.actions.robo_tracker`). Freeze on Contact's HP record (ROM `0xB1C80`) carries `F,D,B + HP` (user choice). A payload flag set by each record's action stub selects the homing creation (donor start speed `0x4CCCC`, cruise sound) and, in the flight child, the homing flight: per host tick two donor ticks of the phase table (8 straight, 16 climbing with `vy −= 0x8800`, then `rocket_hunt`: aim 54 px below the target's reference, steer `0x33333`, `v = v + u − v/16`, renormalise to 5 px/tick, MKT's rough hypotenuse), eight direction loops (parts 1–3, 5–7 of robot animation `0x1300`; level reuses the straight loop), facing flip `0x8003188C`, direction-dependent smoke and a 0x41-call timeout that explodes. The crosshair (robot heap descriptor `0x2C64`, codec 15, palette `0x800BC3D0`, (−12, +27) px) is a follower effect process that tracks its target and removes itself when the rocket's heartbeat stops. Sounds: target ochar `0x0C` → `0x109` → host 459 at the command, cruise ochar 4 → `0x101` → host 478 at creation. File `0x87` grew to `+0x4C340` (12 direction frames, loops, crosshair).
- **v43:** effect palettes bound at record + 4 (see the correction above). MKT's proximity test: each donor hunt step measures from that step's own position (actor position plus the earlier steps of the host tick); within 6 px (rough distance) the rocket is placed on the aim point and stopped, so the stock strike right after the callback resolves there. If that strike does not connect, the next call explodes the rocket without a strike through the loop's own exit `0x8004CDF8`. v42 had no proximity test, so a rocket whose box missed circled through the target.
- **v44:** the LP Ice Blast record (ROM `0xB1B38`) carries MKT's `F,F + LP` instead of the stock `D,F + LP`, with the teleport's `0x18` window (the R2 plan always said `F,F + LP`; v20–v43 kept the stock command).
- **v45:** the homing target. v42–v44 used the controller's last-opponent link `+0x640`, which after a kill still names the dead enemy: the user's Wind video shows rocket and crosshair following a body into a pit while a live enemy stood on a platform. The target is now the nearest (x) living enemy (classes 2–4 through `0x80028510`, health `+0x654` non-zero) on Sektor's path within the teleport's 592-unit square range. The HP condition (stock LP Ice condition, then the picker) refuses the move when there is none. Each flight tick keeps the target while it is present and alive, otherwise picks again, or flies on unguided and removes the crosshair.
- **v46 (Double Missile):** MKT special 51 (`0x8007BFC8`) is the straight launcher `rzap3 0x8007C068` in mode 1: create a rocket, sleep `0x0A`, create a second, recovery, sleep `0x30` (mode 0: `0x20`), close the chest. Ice Clone's LP record (ROM `0xB1B0C`, `D,B + LP`) carries `B,B,F + LP` with the straight rocket's condition (user choice). Right after the first rocket's flight child is created, the lifted root (`0x8004B0E8`) jumps to `zap_again`, which waits one tick, rewinds the parent's script to the creation token `+0xDB8` and replays the root's own mode-0 creation path from `0x8004AD40` (offset globals, staging, sleep 2, token, placement, straight helper, child). The second rocket follows 2 + 1 + 2 = 5 host ticks (10 donor) after the first; back at the site the chest holds 8 more ticks. A point-blank first hit takes the straight helper's hit path and fires no second rocket (MKT would).

Host facts used: the stock Ice root refuses to start while a class-`0x700` process (a live rocket) exists (`0x80028510(0x700)` at `0x8004ABB0`), so both straight commands and the homing rocket are one-at-a-time and block each other (MKT allows three homing rockets). A double puts two smoke trails on screen (about 22 live puffs); the pool reserve still holds, and the texture storage per puff is the one unguarded budget (user choice: leave it, no live-puff cap).

Open details, all deferred by the user: smoke timing and the tick ratio (and the rocket speed re-check), explosion alpha after the v43 colour fix, MKT's faster chest open against a reacting opponent, and the unexplained teleport fall. Tier gating, the remaining Sub-Zero specials and MODERN controls belong to R4.

### Proof-only footprint (v08)

All of these are the Reverse Elbow v6 proof infrastructure plus the takeover storage, guarded against clean bytes. **None is a production allocation.**

| Site | Content |
|---|---|
| Payload | ROM `0xF10000..0xF107FF` → RDRAM `0x801AF420..0x801AFC1F`. Executed and read through the KSEG1 alias `0xA01AF420`. File `0x1B` table entry at `0xA5154`; the arena prefix is widened through `0x66F64` (`2442f420 → 2442fc20`) and the loader hook at `0x66FE0`; loader stub at `0x9AD84` (overlaps the production bootstrap, as in v6). |
| Dispatch | Selector-3 permit `0x4B654` and the table[3] thunk at `0xA1C5C` (Reverse Elbow v6 bridge); proof EXP caps at `0xA6FFC..0xA700F`. |
| Descriptor | The stock Low Kick descriptor at `0xB1B68` (`D,B + LK`) is replaced by `F,F + LK`: mask `0x40`, selector 1, the adapter condition, action `0x800A1060`, window `0x18`. Selector 1 is needed because selector 0 refuses an airborne start. |
| Sound (v10) | Donor ADPCM sample at ROM `0xF20000..0xF20BE1`. In the sound bank, MKMSZ event 335's track (`0x97BCB8`, patch kept 492), subpatch 335 (`0x94A194`), waveform 325 (`0x94DFB0`, offset → `0xF20000`) and predictor 325 (`0x9653B8`) hold the donor records. |
| Body | Repacked file `0x87` at ROM `0xF40000`, end pointer `0xA5668`. Teleport scripts SINK/DROP/LANDA/LANDB occupy the file tail up to `+0x45BE0`. |

### Known limits after v08

- Only the teleport sound is imported; Sektor's other sounds (voice, footsteps and so on) are still Sub-Zero's.
- The drop shadow stays visible during sink and emerge: the shadow renderer is not yet located.
- MKT's 16-tick velocity lead on placement is omitted.
- Facing uses the stock nearest-opponent helper, so with two close enemies Sektor could face the nearer one.
- A target standing at a drop-off edge could place Sektor over the drop. A single unreproduced report after v40 matches this (Sektor appeared at floor level and fell to the floor below); cause unconfirmed. A fix would probe for a floor at the placement before committing to it.
- Only bounded manual routes were tested; this is not exhaustive coverage.

## Canonical ownership and remaining limits

- Slot tables/current coverage: [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping).
- Stable codec/palette/Type-5/storage conclusions: [MKT fighter asset translation](MKT-Fighter-Asset-Translation).
- Donor semantic translation: [MKT adapter primitives](MKT-Adapter-Primitives).
- MKMSZ host action ABI: [Player actions and special moves](Player-Actions-and-Special-Moves).
- Literal current allocation ownership/conflicts: [Memory and allocation map](Memory-and-Allocation-Map).

The current proof line still does not establish production readiness, arbitrary Sektor specials, exhaustive rare-state coverage, victim-side grab/throw presentation, or a conflict-free production allocation for the v62 combo continuation. Historical successful proof footprints remain proof evidence only.
