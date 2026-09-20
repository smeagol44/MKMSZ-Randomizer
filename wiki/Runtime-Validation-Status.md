# Runtime validation status

This matrix states the narrowest claim supported by evidence. “Runtime-confirmed” never means exhaustive unless the scope says so.

| Domain | Runtime-confirmed scope | Static/CI scope | Not yet established |
|---|---|---|---|
| Selector | A-button title route; all eight compact destinations | Guards, table, range, mapper | Intermittent Start shortcut is not production |
| Arena/bootstrap | Reserved block loads and executes | Both arena sites, file-table entry, hook/stub bounds | Expansion beyond the 1 KiB contract |
| Pickup persistence | At least one ordinary pickup in every stage; multiple Fire records; Temple completion | All 84 records and bit mappings | Every record individually; Game Over reset |
| Pickup randomization | `TEST153` first Fire location became predicted Shield and behaved normally | All 84 identities; deterministic namespaces; 250-seed access-model tests | Full seeded playthrough; broad arbitrary-layout runtime coverage |
| Four-box inventory | Switching, live/backing copies, transition survival, foreign-key masking | Input/remap hooks and lifecycle routines | Every save/load/Game Over edge |
| Native UI | Arbitrary custom text and persistent box indicator | Node structure, hook, string/cave guards | General textured-image API |
| Flow bypasses | Logos skipped; selector entry avoids only immediate auto-save | Exact owning routine and branch guards | No known open item |
| Palette | Multiple modes visibly recolor clothing | 64-entry source TLUT and BGR555 transform | Dynamic non-Sub-Zero palettes |
| Enemy substitution | Fire `0x0A -> 0x09`; imported Temple monk in Fire | Stream formats, constructor/resource tables | Death presentation; arbitrary mixes; bosses |
| XP progression | Temple proof: three progression pickups plus one vanilla Herbs control, first two tested at `85` and `258`; no combat/kill/combo XP, tier advance, no inventory award, coexistence. Diagnostic B (`BCBDBF`): V2 allocation and XP-only restore, Temple -> Wind and title -> Fire retention of XP 258/two moves | Central award, direct stores, cap table, save field, V2 storage, deterministic nine-reward generation | Final art, full nine-tier run, Game Over/new-run reset |
| Reverse Elbow / MKT port | v6 host-action lifecycle repeats without global hang; v08/A1.7 renders genuine SCCOMBO10; Sektor v01-v03 runtime-confirm the genuine five-frame Sektor stance itself, but v02/v03 hard-hang on the same forward/crouch/air-forward paths; v04 hung before gameplay at Mission Objective and therefore did not test its cursor change | Corrected host scheduler/action paths; exact donor resource closure; codec conversion; Sektor retail 1/3/5/7/9 stance; v05 preserves v04's native-cursor-at-+0x2EC experiment while removing the new diagnostic HUD entirely | Runtime validation of Sektor v05; separate idle-entry palette/shape ordering artifact; full 10→11→12→11→10 donor animation; no-repel shim; translated donor strikes/reactions; completed move port |
| PS1 | No new runtime test in this consolidation | Executable/resource/save/pickup/enemy mappings | Fire type substitution, UI hook, playable Scorpion moves |

## Runtime environment lineage

Historical N64 proof runs used BizHawk `2.11.1`, Ares64, CPU emulation `1`, and P1 controller `2` where explicitly recorded. State-specific observations remain bound to their ROM and save-state identity. The Wiki reproduces conclusions and exact addresses, while hashes and original captures remain historical provenance.

## Production vs proof

“Production” requires current guarded code and tests. “Proof” may intentionally use a temporary cave, a one-off record edit, or a narrow replacement. For example, the Temple XP result is runtime-confirmed but its cave conflicts with production, and the Temple-monk import proves resource residency but lacks the monk's normal death presentation.
