# TEST LAB → Inventory hang: static diagnosis and v20 proof

Date: 2026-10-05. Source baseline: repository `c318ac19a5de8ff697350d6b43aed4314c4150ee` plus exact preserved proof ROMs/builders. No emulator was run. One disposable ROM was built after narrowing the static defect; v20 runtime validation is now Runtime-confirmed on the bounded user test.

## Conclusion and new discriminator

**Runtime-confirmed bounded root cause: the inventory-HUD lazy-data allocator receives an uninitialized size on its first-load branch.** The defect was introduced by v14's compaction of `0x800742F0`, while repairing the independent stale TEST LAB trampoline. It is byte-identical in v16, v18, and v19. The failing owner is the custom HUD allocation helper, not the isolated pickup manager.

**New Runtime-confirmed v16 result:** exact `MKMSZR_test-lab-power-spawn-disable_test-lab_proof_v16.z64` enters TEST LAB normally and immediately hangs when Inventory opens. Thus v18/v19 are reproductions of an older Inventory/HUD composition failure. Their isolated manager, live actor count, and enlarged Fire file `0x3C` are not necessary causes. v16 is startup-safe on this route; it is explicitly **not Inventory-safe**.

The static instruction defect is proven. Attribution of the observed TEST LAB Inventory hang to that defect is now Runtime-confirmed on the bounded v20 user test: the one-word size initialization correction removes the hang. No runtime allocator trace or exact fault address is claimed.

## Exact failing path

Native entry `0x80014FC0` checks process state `0x802ECE18=2`, positive selector, live player/HP, and qualifying player action state, then allocates the Inventory process, callback `0x80073588` (class `0x100`). The draw chain is:

`0x80073588 → 0x800728B0 → 0x800741EC → 0x80074268 → 0x800742C8 → 0xA01B2DAC → 0xA01B28F0 → 0x800742F0 → 0x8006643C`.

Calls originating in the KSEG1 proof module execute the permanent helpers through their KSEG1 aliases (`0xA00742F0`, etc.). These are the same physical instructions.

The row hook saves incoming `a0` but calls the ensure helper at `0xA01B2904` before replacing it. Native `0x80074260` supplied a string pointer from `0x800A633C + item*4`. Initial live slot 0 is the inert masked item `8`; ROM `0x000A6F5C` contains its label pointer `0x800AD80C`, pointing to `SEALED`. The corresponding backing ID is credential `14`, so the later row draw follows the custom credential branch.

The lazy pointer at `0xA01B2DE0` (ROM `0x00F235C0`) initially equals zero. v14/v16/v18/v19 execute:

| VA | ROM | Word | Meaning |
|---|---|---|---|
| `0x80074300` | `0x00074F00` | `8D102DE0` | Read lazy pointer into `s0` |
| `0x80074304` | `0x00074F04` | `12000007` | If null, branch directly to allocator call |
| `0x80074308` | `0x00074F08` | `00000000` | Null-branch delay slot does nothing |
| `0x8007431C` | `0x00074F1C` | `1140000C` | Nonnull path tests whether allocation is still resident |
| `0x80074320` | `0x00074F20` | `24041200` | Set size `a0=0x1200` only on the nonnull path |
| `0x80074324` | `0x00074F24` | `0C01990F` | Call arena allocator `0x8006643C` |

The null path skips `0x80074320`. On the first row, the allocator therefore receives **`0x800AD80C` bytes**, rounded to `0x800AD810`, rather than `0x1200` bytes.

Retail `0x8006643C` has no capacity guard. For cursor `C` at `0x80111ECC`, it returns `C+8`, advances the cursor to `C+8+align8(a0)`, and writes two metadata words at the new cursor. Treating a label pointer as a size sends this write outside the intended RDRAM arena before the subsequent HUD-data DMA. The exact live cursor and resulting bus/fault address were not measured.

v13's earlier ensure helper at `0x800742D8` explicitly sets `a0=0x1200` at the shared `load` label. v14 moved the assignment into the ready-check branch delay slot to fit the restored TEST LAB trampoline in the same permanent span. That transformation did **not** preserve the null path's behavior.

## Reclaimed-region ownership and callers

The audited permanent span is `[0x800742B8,0x800743A8)`, ROM `[0x00074EB8,0x00074FA8)`, exactly `0xF0` bytes. It follows the native row-list return at `0x800742B0`; the native row function does not fall through into it.

| v16/v19 range | Owner / target |
|---|---|
| `[0x800742B8,0x800742C8)` | Paper/detail trampoline → `0xA01B2A60` |
| `[0x800742C8,0x800742D8)` | Shared row/preview/HUD trampoline → dispatcher `0xA01B2DAC` |
| `[0x800742D8,0x800742E0)` | Two NOPs; no identified incoming call |
| `[0x800742E0,0x800742F0)` | Restored TEST LAB trampoline → `0xA01AFC20` (signed-low address materialization) |
| `[0x800742F0,0x80074368)` | Lazy `0x1200` HUD-data helper; failing null path |
| `[0x80074368,0x800743A8)` | Display-only backing-ID resolver |

All aligned direct J/JAL targets and raw address words were scanned across exact v08/v09/v13/v14/v16/v19 images. Nearby LUI + ADDIU/ORI address constructions were checked; relative branches were checked in permanent code and the proof module. Results are preserved in `region-callers.json`. This is a bounded static reference audit, not a claim to enumerate every possible computed runtime target.

Exact v16 and v19 incoming direct calls:

| Caller ROM | Caller / role | Target |
|---|---|---|
| `0x00011B00` | Stage setup `0x80010F00`, TEST LAB | `0x800742E0` |
| `0x00073C98` | Inventory preview `0x80073098` | `0x800742C8` |
| `0x00073D24` | Inventory paper/detail `0x80073124` | `0x800742B8` |
| `0x00074E68` | Inventory row `0x80074268` | `0x800742C8` |
| `0x00075B88` | Inventory secondary value/HUD `0x80074F88` | `0x800742C8` |
| `0x00F230E4`, `0x00F23260`, `0x00F23468` | Custom row, paper, HUD | `0x800742F0` canonical / KSEG1 alias when executed |
| `0x00F230F0`, `0x00F23178`, `0x00F2326C` | Custom row, preview, paper | `0x80074368` canonical / KSEG1 alias when executed |

No stale direct call into old ensure `0x800742D8`, old resolve `0x80074364`, or another reclaimed interior address was found in v16/v19. The surviving `0x800742E0` stage call reaches the restored trampoline. The additional failure is **inside** the intended ensure entry.

Exact v08/v09 used different trampolines: detail `0x800742B8`, row `0x800742C0`, preview `0x800742D0`, and TEST LAB `0x800742E0`; their paper trampoline jumped to `0x800742F0`. v13 correctly redirected Inventory's old row/preview callers to the new shared entry, but left the TEST LAB caller at `0x800742E0`, then owned by ensure instructions. v14 fixed that collision and redirected all three ensure/resolve callers, while introducing the size bug. v08 is the last inventory-HUD revision in this line with confirmed TEST LAB entry; exact v08 TEST LAB/Inventory coexistence was not independently established here. Historical TEST LAB v08 is a separate version namespace and did confirm Pause/Inventory; do not conflate these two v08 proofs.

## Exact v16 → v19 runtime-affecting additions

Word-aligned diff spans below are half-open. No HUD permanent/helper/module changes occur between these versions.

| ROM span | v19 addition/change beyond v16 |
|---|---|
| `[0x10,0x18)` | Header checksums |
| `[0xA52E0,0xA52E8)` | File `0x3C` start/end: stock `0x00388260..0x0038A790` → appended `0x01F00000..0x01F026E0` |
| `[0xF2041C,0xF20420)` | NOP → JAL `0x801B1760`, re-enabling explicit pickup setup |
| `[0xF21F6C,0xF21F70)` | Setup resource-base high half `0x8030` → correct `0x802F` |
| `[0xF21FA0,0xF21FA4)` | Child count immediate `9` → `2` |
| `[0xF21FA8,0xF21FEC)` | Record pointer becomes allocated file base `+0x2530`; setup epilogue reshaped |
| `[0xF2205C,0xF220A0)` | Initializer uses current resource base `0x802E82B8 + 0x2530`, initializes two records; code repositioned within owned slot |
| `[0x1F00000,0x1F026E0)` | Stock file body `0x2530` bytes plus all nine `0x30`-byte records (`0x1B0` bytes) |

v18→v19 changes only the two manager/initializer count immediates from 9 to 2 (and required checksums if applicable). All nine resource records remain present. v19 rejected a simple nine-live-actor overload explanation on the tested route. The new v16 result more strongly establishes that none of the above v19 additions is required to trigger the Inventory hang.

## Ownership/lifecycle and historical controls

`0x802ECE20` is the **current running process/controller pointer**, not a permanent pointer dedicated to the pickup manager. The scheduler publishes each running controller at `0x8002867C` and clears it on exit at `0x8002877C`. Generic allocator `0x8002830C` reads the current parent, links the child into the process list, and copies parent fields including `+0x6F4/+0x6F8`; it does not publish the child into `0x802ECE20` as a lasting replacement.

v19 setup saves parent `+0x6F4/+0x6F8`, temporarily installs count 2 and record pointer, allocates class `0x19` with callback `0x80038ACC`, and restores the parent fields synchronously. Child construction thereafter owns the child's fields, including its actor linkage. No late overwrite of the parent's saved fields was established.

Native Inventory calls `0x80028870` at `0x80073688` to suspend the gameplay process list. With current Inventory process `I`, original head `H`, and `N=I+0`, it saves `H` to `0x80111FC0`, sets head `0x80111EAC=I`, clears `I+0`, and saves `N` to `0x802C0F98`. Inventory changes process state to `0x16` and temporarily detaches actor-list head `0x80111C98`. Exit calls `0x800288A8` at `0x80073BC8` to restore the saved process links; actor-list state is separately restored. This suspension does not interpret a pickup child's `+0x6F4/+0x6F8` as Inventory resources or traverse its records.

Later historical TEST LAB manager proofs v15/v16 and native Fire-file v26/v27/v38 use the same essential parent-field preservation, explicit resource load/publication, and isolated manager strategy. v38's inherited builder also preserves the later manager chronology. Exact historical v21 binary was not recovered; no exact-v21 binary comparison is claimed. None of the inspected accepted setup paths restores `0x802ECE20` after allocator creation, because allocator creation does not replace it. They also leave their stage resource base published. No extra restoration absent from v19 was found.

Exact Power-Herbs TEST LAB v01/v02 publish file `0x3C`, install a two-record manager during startup, and save/restore parent `+0x6F4/+0x6F8` in the same way. Their pickups are active before user input. v02 adds the accepted white-pulse presentation. Their accepted pickup/presentation results alone do **not** prove the user opened Inventory in those exact proofs. Historical room proofs establish bounded Inventory support; later pickup screenshots/evidence establish bounded coexistence, not exhaustive coverage of every proof.

The correct resource-base slot is **`0x802E82B8`**: `0x802F0000 + sign_extend(0x82B8) = 0x802F0000 - 0x7D48`. Historical code using `lui 0x802F; sw ...,0x82B8(...)` was correct despite earlier wiki labels. v17 incorrectly used a high half corresponding to effective `0x802F82B8`; v18 corrected the two affected high halves.

Custom row/paper/preview/HUD code reads inventory backing IDs, stage ID `0x8009A910`, progression state `0xA01AF7D0`, lazy HUD pointer `0xA01B2DE0`, preview cache `0xA01B2DE4`, and portrait backing `0x800EEAF0` (sprite `0x46C`). Its lazy allocator does not resolve through the stage resource global, file `0x3C`, or current process pointer. No newly triggered file-`0x3C` registration conflict at Inventory entry was established. The direct malformed allocation outranks generic arena pressure; reducing pickup memory cannot correct its argument.

## Smallest guarded proof and allocation ownership

Fix category: **custom HUD control-flow / allocation-argument initialization**. No TEST LAB redesign, manager ownership change, stage resource scoping change, or memory reduction is needed for this candidate.

One code word changes on exact v19:

| Address | Expected bytes | Replacement bytes |
|---|---|---|
| VA `0x80074308`, alias `0xA0074308`, ROM `0x00074F08` | `00 00 00 00` | `24 04 12 00` (`addiu a0,zero,0x1200`) |

The null branch always executes this delay slot, so both first-load and reload paths request `0x1200`. The nonnull resident path still performs no allocation. The existing second size assignment remains; retaining it makes the proof one-word-only. Header CRC bytes are regenerated.

The permanent span and all module boundaries remain unchanged. The same lazy data allocation is owned by the HUD: ROM source `[0x01814000,0x01815200)`, payload size `0x1200`, pointer slot `0xA01B2DE0`; allocator consumes `0x1208` cursor bytes including bookkeeping and returns payload at original cursor `+8`. No new fixed RAM cave, controller field, process slot, file-table range, resource registration, or ROM payload allocation is introduced. Existing v19 setup slots remain ROM `[0xF21F40,0xF22040)` / VA `[0xA01B1760,0xA01B1860)` and initializer `[0xF22040,0xF220C0)` / `[0xA01B1860,0xA01B18E0)`.

Builder guards exact v19 SHA, 32 MiB size, the entire ensure-helper hash, branch/call/size words, zero initial pointer, two-pickup counts, corrected resource-base high halves, file-table span, Very Hard halfword `0x000A6BA8=0004`, and input checksums. Full-image verification permits only this code word and CRC header changes. Three audited branch cases check null first-load, stale reload, and resident reuse. All shared module/data, file-`0x3C` bytes, nine records, and other appended resources are byte-identical to v19.

Artifact: `MKMSZR_inventory-hud-alloc_test-lab_proof_v20.z64`, 32 MiB.

- Base v19 SHA-256: `aafcc7e26ecd77b04a3882cee9569161f8059d92af1fce003ac3e68e08406277`.
- v20 SHA-256: `3461ed86540d51881f5f7d1b45c17dee9113484889370c8af750b819a11b1daa`.
- v20 CRC1 / CRC2: `479EDF13 / E1BE6C34`.
- Evidence: static/implementation verification passed; **Runtime-confirmed bounded user test**. The builder itself ran no emulator.

## One bounded manual test

Cold-boot exact v20 with a fresh run, using the established title A → Safe Stage Select → TEST LAB Start route. Do not use a savestate from another proof. Confirm the room enters and exactly two pickups appear. **Before collecting either pickup, open Inventory.** Expected: Inventory draws its first page and remains responsive; close it, confirm normal movement/music, and reopen once. This single route tests first allocation and reuse with the unchanged active v19 manager/resources. Record whether the hang occurs before any Inventory pixels, during the draw, or on close/reopen. The user reports this v20 route is fixed, confirming the candidate on that bounded route. Broader stage/preview/box/lifecycle acceptance remains separate.

## Separate follow-up defect and preserved findings

The v13 row rewrite also dropped forwarding of the caller's fifth font/palette argument for ordinary items. Current helper pushes `0x30`; the original argument is at new `sp+0x40`, but ordinary path `0xA01B2958` only reloads `a0` and does not populate outgoing `sp+0x10`. Native `0x80073E74` consumes that fifth argument. v08 forwarded it correctly. Initial TEST LAB backing slots are all credentials, whose branch initializes the outgoing font explicitly, so this is not the initial-row failure explained above. It is a separate unsafe ordinary-item path and a release blocker for broader HUD coverage. It is deliberately excluded from the one-word v20 proof to keep attribution bounded.

Preserved chronology (inventory-HUD namespace):

- v08: last confirmed TEST LAB entry before startup regression; Inventory coexistence in this exact revision is not assumed.
- v09: synchronous Power Upgrade bootstrap caused original Mission Objective/startup regression.
- v13: additionally reclaimed `0x800742E0` while TEST LAB still called it; independent stale-trampoline regression.
- v14: restored that trampoline, advanced to music, but retained v09's startup problem; its compaction also introduced the independent HUD null-allocation defect identified here.
- v16: disabled only the v09 startup call; **Runtime-confirmed TEST LAB entry and immediate Inventory hang**, including the new exact-file manual result.
- v17: later isolated-manager attempt hung at Mission Objective; stage-base interpretation `0x802F82B8` was wrong due to signed `0x82B8`.
- v18: corrected only two affected high halves; **Runtime-confirmed entry, all nine Power Upgrade pickups, and immediate Inventory hang**.
- v19: two live pickups with all nine records/file composition retained; **Runtime-confirmed entry, two pickups, and immediate Inventory hang**. Rejects 9→2 live-count reduction as a remedy on this route; v16 shows the manager addition is unnecessary for the failure.
- Earth horizontal wall spikes were not broken: they are difficulty-gated. Earlier HUD proofs unintentionally used difficulty 2, rather than the project's Very Hard baseline. v14 onward retains difficulty halfword 4.

Exact comparison identities: v16 SHA `82a13bf95eae36ec5fed0c828a631b99d19178a53ba06833c1bb8bf204b0f994`; v18 SHA `6832f1c0db523d4ef55ccdec90251b924aaff004e71601648bff8637677586f5`; v14 SHA `27a2a5f14e20cf632eec4243dfa1bf6bdf42823c05858c5f6b629db926723bae`; v13 SHA `bb2114b195ba5d5eb83b81347e2af5e6045a3a19e5f7de4b3aff980245741d15`.