# Persistence, inventory, and lifecycle

**Inventory-HUD TEST LAB closure (2026-10-05):** exact v16 enters TEST LAB but immediately hangs on Inventory, before v18/v19 isolated pickup additions. Static review identified the independent v14 first-load HUD size bug; **v20 Runtime-confirms its one-word correction removes the hang on the bounded TEST LAB route.** The pickup-manager parent-field preservation and Fire resource composition were not required causes. See [TEST LAB Inventory diagnosis](Test-Lab-Inventory-Hang-Static-Diagnosis).

## Ordinary-pickup persistence

The native game reconstructs stage pickup records, so a per-location runtime bitset is the production authority for randomizer collection state. Production state V2 lives at `0x801AF7D0..0x801AF81F`, begins with `MKSV`, and assigns one 32-bit word to each main stage. The exact header and word layout are in [Data structures and encodings](Data-Structures-and-Encodings).

Capture hooks the collected-flag store at `0x80039418`; `a1` is the record and `s2` is manager ordinal. Restore hooks `0x80038ACC` before the manager's first `+0x2C` read and walks the current record array using the effective context pointer at `0x802ECE20`, count `+0x6F4`, and base `+0x6F8`.

For seven stages, manager ordinal equals catalog bit. Fire has 19 manager entries for 16 ordinary records, so production uses this explicit translation:

```text
[2, 5, 4, FF, FF, FF, 9, 14, 0, 1, 8, 11, 12, 3, 7, 6, 10, 13, 15]
```

The three `FF` entries are special type-4 records and never enter the ordinary bitset.

Runtime testing collected and restored at least one ordinary pickup in every main stage, multiple Fire items, and completed Temple coverage. That does not equal 84 individual tests.

Progression state is separate: V2 state `+0x40` stores the number of progression rewards acquired and `+0x44` stores persistent XP. Diagnostic B runtime-confirmed XP 258 and two unlocked moves surviving Temple -> Wind and title-menu -> Fire.

At the pickup-manager stage-init boundary, the progression restore helper writes only persistent XP before continuing into the established four-box reconstruction. It does not call the native tier evaluator. Calling that evaluator at this boundary is rejected because it caused the pre-gameplay hang in the first production attempt.

Game Over/new-game reset behavior is Runtime-confirmed in lifecycle v06 on the accepted bounded route: classified final Game Over clears MKMSZR run state and inventory/progression authority while preserving all five GAME SETTINGS preferences; the next run returns to Very Hard, nine total lives, five continues, full HP, and starter inventory.

## Four-box inventory

The game continues to see its stock ten-word live array at `0x800A600C`. Four backing arrays are authoritative:

| Box | Range |
|---:|---:|
| 1 | `0x800A6048..0x800A606F` |
| 2 | `0x800A6070..0x800A6097` |
| 3 | `0x800A6098..0x800A60BF` |
| 4 | `0x800A60C0..0x800A60E7` |

State at `0x800A60E8` stores active index bits `0..1`, input latch `0x100`, and durable GAME SETTINGS bits: `0x0200` TURN=LOCK, `0x0400` COMBOS=ASSIST, `0x0800` SPECIALS=MODERN, and `0x1000` JUMP=BUTTON. Box switching preserves all owned settings bits. JUMP=BUTTON is only user-editable while COMBOS=ASSIST and SPECIALS=MODERN; disabling either prerequisite clears the JUMP button bit back to DPAD. Magic `MKBX` at `0x800A60EC` distinguishes initialized backing data. The design deliberately has no auto-spill. General game inventory behavior still receives only the active backing box through the ten-word LIVE window; the explicit exception is the Fire/Bridge native **all-three credential ownership test**, whose four-box correction searches the contiguous 40-word authoritative backing region while preserving the stock physical use-site gate and completion action.

## Switching input

Outside the inventory menu, hold **Block + Use + Right/Left** to advance or reverse the active box. The hook reads normalized semantic action state at `0x800BF2EE`, so control remapping is respected. A latch prevents repeated switching while the chord remains held.

The native HUD displays `BOX n OF 4` at `(230,210)`. It reads the existing state byte and introduces no new lifecycle state.

## Stage-local key masking

Keys should be usable only in their origin stage. When backing data is copied to live inventory, foreign-stage IDs `0x0D..0x22` are represented by stock item ID `0x08`, displayed as **SEALED**; the backing word remains unchanged. Production changes stock item `0x08`'s item-use dispatch from consuming stub `0x80071F58` to inert return-zero stub `0x80071F50`, making the placeholder safe. The Tablet (`0x24`) was rejected because its use path is consumable.

The stage mapping is Temple Map `0x0D`; Wind `0x0E..0x10`; Earth `0x11..0x13`; Water `0x14..0x16`; Fire `0x17..0x19`; Prison `0x1A..0x1C`; Bridge `0x1D..0x1F`; Fortress `0x20..0x22`.

### Foreign-key acquisition masking boundary — Runtime-confirmed closure (2026-09-30)

Fire -> Wind Circle v01 confirmed the existing reconstruction behavior but exposed an immediate-acquisition gap: directly after the foreign Circle was awarded in Fire, LIVE still showed real item ID `0x0E` until the next box/stage reconstruction. The authoritative backing identity itself was already correct.

Disposable v02 added one bounded ordinary-pickup post-callback composition: filtered LIVE -> active backing save, followed immediately by active backing -> stage-masked LIVE reconstruction. Runtime validation confirmed that the newly acquired Wind Circle appears as inert **SEALED** (stock item `0x08`) **immediately** in Fire, without requiring a box switch or stage transition. Entering Wind restores the real Circle, and normal Wind use succeeds while retaining the key.

This Runtime-confirms the tested foreign-key masking round trip across both acquisition and reconstruction boundaries. Production integration still requires the normal guarded code/allocation path; the proof hook itself is not silently promoted to product ownership.

Native key items are **not consumed by normal use**. They remain in inventory after use; any cleanup/removal associated with completing a stage is a separate lifecycle boundary and is not part of ordinary key-use semantics.

## Lifecycle hooks

- The stock sanitizer at `0x8007AD00` is replaced by a fixed-size mask-copy routine rather than deleting special IDs.
- The stock default loader at `0x8007AD4C` is replaced by the filtered **LIVE -> active backing save** wrapper. LIVE reconstruction is `0x80099B14 -> 0x8007AD00`, with the ten-word LIVE store at `0x8007AD34`. Keep this inventory ownership unchanged; see the [static lifecycle closure](Lifecycle-Static-Closure-v05).
- Transition wrappers commit non-placeholder live items back to the active backing box; SEALED/stock-Glass placeholder slots are skipped so hidden true keys survive.
- Saves serialize the filtered live view through the established game path; loads rebuild live state from authoritative backing data and current-stage masking.
- Title-menu START was the destructive live-window boundary in stock behavior and is explicitly intercepted.

Normal save logic is preserved. Only selector-triggered immediate stage-entry save is suppressed, as documented in [Stage flow and selector](Stage-Flow-and-Selector).


## Progression lifecycle evidence

**Runtime-confirmed on seed `BCBDBF`:**

- progression acquisition established native move tiers at XP 85 and 258;
- a normal Temple -> Wind transition preserved XP 258 and both unlocked moves;
- quitting to the title menu and directly entering Fire also preserved XP 258 and both moves.

This shows that, on the tested routes, the move-tier state established at acquisition survives without re-running the tier evaluator during stage initialization.


## HP / lives / continues lifecycle implications

The canonical 1.0 requirement and acceptance criteria are owned by [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap). This section records only the lifecycle evidence and implementation implications needed to satisfy that requirement.

The legacy Lua is only a clue here, not a solution. It writes startup configuration values once:

- difficulty RDRAM offset `0x0A5FA9` = `0x04` (Very Hard);
- lives RDRAM offset `0x0A5FAB` = `0x06`;
- continues RDRAM offset `0x0A5FAD` = `0x04`.

It also names `0x0F1057` as a life-related address, but does not use it for stage-transition preservation. There is no Lua logic that carries current HP, current lives, or current continues between stages.

The focused 2026-10-01 [static lifecycle closure](Lifecycle-Static-Closure-v05) established the death/Continue/constructor/terminal chains used by v05/v06. The user then Runtime-confirmed v05 for lives/continues/XP/powers/inventory/death/Continue/final-reset behavior; HP alone was still overwritten to 166 by the later stock constructor store at VA `0x8002EE44`. v06 NOPs only that redundant second full-HP store, and the user reported the complete lifecycle worked perfectly, including damaged-HP persistence across Pause -> Quit -> re-entry.

| Lifecycle proof | Evidence / disposition |
|---|---|
| v01 | **Rejected.** Supposed reset at ROM `0x364EC` cleared run state on stage entry. Never reuse that reset composition. |
| v02 | Inventory survived Pause -> Quit; XP/powers, HP and lives did not. Partial evidence only. |
| v03 | **Rejected.** Bad stage-entry composition hung at Mission Objective. |
| v04 | **Rejected / unsafe composition** because music sometimes sped up. **XP/powers persistence across Pause -> Quit is Runtime-confirmed in v04**, but does not accept its composition. |
| v04 lives floor | Static inspection shows its repeated restore writes saved lives after the stock death decrement, undoing it. The roughly ×7 / eight-total floor is a proof bug, not stock minimum-life behavior. |
| v04 HP | Restore runs after player construction; constructor has already selected/stored HP. Carrier priming at that late boundary does not restore the current player. Corrected constructor-local restoration remains runtime Pending. |
| v04 death inventory | Exact late writer is backing -> LIVE mask copy. No death-time LIVE commit is present. Stale backing explains lost uncommitted items; actual all-four-box overwrite is not runtime-established. |
| v05 | **Runtime-confirmed except HP.** Lives/continues decremented and persisted correctly, XP/powers and all inventory behavior remained correct, ordinary death used full replacement HP, and final Game Over reset run progress/defaults correctly. Living HP restoration was overwritten later by stock `0x8002EE44: sh v0,0x654(a1)`. |
| v06 | **Runtime-confirmed accepted lifecycle baseline.** Same v05 composition plus NOP at ROM `0x2FA44` / VA `0x8002EE44`. Damaged HP now persists across living exit/re-entry while fresh run/death/Continue still get full HP from the earlier stock constructor branch. User: “worked perfectly, like a charm.” |

Production lifecycle v06 preserves production XP restoration byte-for-byte, commits inventory before death teardown, and uses a one-shot living re-entry token in the player constructor. Ordinary death/Continue invalidates damaged-HP eligibility and leaves stock resource mutation intact. The final reset is guarded at ROM `0x367B4` by zero current lives, nonpositive signed continues and a real-run terminal context, with demo protection latched before its indicators are cleared. The shared patch now parameterizes difficulty, configured lives and continues in the same validated helper: defaults are Very Hard / 5 / 3, ranges are lives 1..10 and continues 0..5. HP persistence defaults ON; OFF intentionally retains stock `0x8002EE44` so living re-entry returns to full HP. All five user GAME SETTINGS preference bits (`0x3E00`) survive either policy. The exact Very Hard / 9 / 5 / HP-ON v06 artifact remains the Runtime-confirmed reference case.


## Temple scripted-check lifecycle

The canonical 1.0 policy is resolved in [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap): logical Map item `0x0D` is excluded from the randomizer pool, while the scripted Temple Map location remains a special check.

v01 Runtime-confirmed that replacing only the scripted location's inventory award with Herbs leaves the Temple elevator/platform progression intact. v02 then closes the special-check lifecycle: collection sets **MKSV header flags bit `0x0001`**; on title -> Temple re-entry the helper sees that bit, reconstructs the stock Temple-local collected word at `0x8026E9A4 = 0x00000100`, and resumes the stock post-award loop at `0x802EEE94` without respawning or re-awarding the check. The user confirmed the check remained absent, elevator/rope progression remained correct, and Temple -> Wind completed normally.

This state is intentionally independent of the 84 ordinary manager-backed persistence bits. No cross-stage logical-Map retention or Temple -> Wind Map-removal workaround exists in 1.0 because Map `0x0D` is not a randomized logical item.

Lifecycle v06 now owns the accepted Game Over/new-run reset and clears the Temple special-check persistence bit together with the rest of run-scoped MKMSZR state.
