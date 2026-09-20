> **Mirror notice:** This Wiki is a navigation-friendly adaptation of MKMSZR documentation. The ChatGPT Library folder `MKMSZR Research` remains the reverse-engineering/research source of truth; this repository remains the implementation/product source of truth. If the Wiki conflicts with an owning source, the owning source wins.

# Enemy Randomization

## Ordinary enemy flow

`command stream -> FUN_80071500 -> FUN_800719F0 -> FUN_80071B20 -> FUN_8002FCDC`

Bosses/minibosses/scripted encounters are separate.

## Ordinary command streams

| Stage/branch | Stream |
|---|---:|
| Temple | `0x800B2D40` |
| Earth | `0x800B2EB8` |
| Water | `0x800B2F9C` |
| Wind ordinary | `0x800B30E4` |
| Fortress ordinary | `0x800B33A8` |
| Prison | `0x800B361C` |
| Fire ordinary | `0x800B3890` |
| Fire alternate | `0x800B3A54` |
| Bridge | `0x800B3A7C` |
| Fortress alternate | `0x800B3C88` |

## Resource residency

Changing fighter type alone is not sufficient; the expected fighter resource slot must be populated.

Runtime evidence:

- Fire `0x0A -> 0x09` succeeds;
- Fire `0x0A -> 0x01` originally froze because type `0x01`'s slot was null;
- a bounded proof loaded Temple file `0x89`, populated type `0x01`'s resource slot and spawned a functional Temple monk in Fire.

The imported monk rendered, moved, fought and was killable.

Known issue: normal death/despawn presentation is missing.

## Still needed

- production mixed-roster planner;
- compatibility matrix;
- memory/resource budgeting;
- death/despawn auxiliary behavior;
- explicit boss/miniboss policy;
- deterministic seed integration.
