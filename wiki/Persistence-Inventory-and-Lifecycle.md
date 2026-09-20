> **Documentation status:** This page is part of the living/current MKMSZR Wiki. The Library folder `MKMSZR Research` preserves underlying evidence, historical canonical reports, and specialist artifacts. If a current Wiki conclusion conflicts with Library evidence, inspect the evidence and preserve superseded conclusions where relevant.

# Persistence, Inventory and Lifecycle

## Runtime Layout V1

Persistent state:

`0x801AF620..0x801AF81F`

Header identifies `MKSV`, version 1, 0x200-byte state region and 0x20-byte header.

## Ordinary-pickup persistence

Production capture/restore operates at the shared pickup-manager path.

- all 84 ordinary locations are represented;
- at least one pickup in every main stage has been tested through the persistence architecture;
- scripted/special mechanisms remain separate.

## Four native inventory boxes

| Storage | RDRAM |
|---|---|
| LIVE | `0x800A600C..0x800A6033` |
| Box 1 | `0x800A6048..0x800A606F` |
| Box 2 | `0x800A6070..0x800A6097` |
| Box 3 | `0x800A6098..0x800A60BF` |
| Box 4 | `0x800A60C0..0x800A60E7` |
| state | `0x800A60E8` |
| magic | `0x800A60EC` |

The backing box is authoritative; LIVE is a window.

Switching uses the remapping-aware Block + Use + Left/Right semantic chord and is rejected while the inventory UI is open.

## Stage-local foreign-key masking

Foreign-stage keys remain as their true IDs in backing storage but are represented in LIVE as reserved placeholder ID `0x08`.

Vanilla Glass `0x08` was consumable, so MKMSZR patches its USE dispatch to the no-consume return. Repeated USE was runtime-confirmed inert.

## XP and move progression

Focused static analysis has now mapped the native XP/move-progression path sufficiently for a pickup-driven randomizer design.

Static-confirmed:

- current XP is the 32-bit word at `0x8011200C`;
- the central ordinary XP-award helper is `0x8002E104` / ROM `0x0002ED04`;
- three additional direct XP award stores exist at `0x800540E8`, `0x80057160`, and `0x8005722C`;
- the native tier evaluator/stage clamp is `0x80074FBC` / ROM `0x00075BBC`;
- the signed-halfword per-stage XP-cap table is `0x800A63FC` / ROM `0x000A6FFC`;
- the exact first XP values for native power tiers 1..9 are `85, 258, 834, 1410, 2323, 3315, 4503, 5911, 7354`.

The legacy Lua used the same hexadecimal tier constants but rewrote current XP every frame according to Power Upgrade count and rewrote all main-stage caps to 9999 at startup. Its comment for `0x1CBA` says 7345; native static analysis confirms the actual value is **7354**.

Planned native design, not yet runtime-confirmed:

- disable ordinary/direct combat XP awards at their native award paths;
- replace nine randomized Herbs with a synthetic progression pickup;
- each progression pickup advances current XP once to the next native tier threshold and records that XP in MKMSZR persistent state;
- restore the persistent XP once at stage reconstruction rather than continuously overwriting the game's XP value;
- statically raise main-stage XP caps so any normal move tier can remain active in every selected stage.

The save-slot/state loader at `0x80078A18` restores XP as part of a 0x7C-byte record; it is not the ordinary combat-award path. Title/new-game lifecycle resets still mean the production randomizer should keep its own persistent progression value and restore it at the existing stage-init reconstruction boundary.

## Game Over

Game Over is intentionally the full-run reset boundary.

Still pending:

- complete run-state reset implementation/runtime proof;
- HP/lives/continues lifecycle policy and runtime validation of the new XP-progression design;
- broader normal stage-completion coverage;
- save-file/power-cycle persistence only if later desired.
