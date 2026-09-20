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

## Game Over

Game Over is intentionally the full-run reset boundary.

Still pending:

- complete run-state reset implementation/runtime proof;
- HP/EXP/lives/continues lifecycle policy;
- broader normal stage-completion coverage;
- save-file/power-cycle persistence only if later desired.
