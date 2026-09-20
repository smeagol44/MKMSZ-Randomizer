# Stage flow and selector

## Production title route

The title-screen A-button route originally calls `0x8002830C`; production changes the JAL at ROM `0xE028` to the native debug selector at `0x8000D0B8`. The normal stage-loader path remains stock, preserving cinematics, overlay initialization, and progression behavior after a stage is chosen.

The selector's wrap/count instructions at ROM `0xDD60` and `0xDD64` are bounded to eight entries. The pointer table at ROM `0x9B7DC` / VA `0x8009ABDC` is rewritten to retain only:

| Compact index | Label | Native stage |
|---:|---|---:|
| 0 | Temple | 0 |
| 1 | Wind | 1 |
| 2 | Water | 2 |
| 3 | Earth | 3 |
| 4 | Prison | 4 |
| 5 | Fire | 5 |
| 6 | Bridge | 8 |
| 7 | Fortress | 9 |

Stock entries excluded from production are Unused, Fire God Room, and Test Characters. The original eleven-label order was Temple, Wind, Water, Earth, Prison, Fire, Unused, Fire God Room, Bridge, Fortress, Test Characters.

## Selection mapping

The debug menu writes selection at `0x800C11E0`. The transition path at `0x80015088` ultimately stores the native stage at `0x8009A910`. Production replaces the stock selection load at ROM `0x15CD0` with a JAL to a small mapper: compact values below 6 pass through; values 6 and 7 gain 2.

The initial mapper occupied ROM `0x9A700` / VA `0x80099B00`. Four-box integration relocates it to ROM `0x9AEFC` / VA `0x8009A2FC`, because the former selector cave is repurposed for inventory code. Tests enforce this relocation and the selection hook.

## Runtime evidence

The A-button route is runtime-confirmed for all eight safe stages. An attempted Start-button shortcut behaved intermittently and is rejected from production; no documentation should imply that Start is an alternate supported selector entry.

## Selector-specific save bypass

The relocated mapper also writes nonzero byte `0x15` to `0x80291C0C`, the game's native one-shot stage-entry bypass. This suppresses only the immediate automatic save prompt caused by jumping directly into a stage. It does not patch the save routine at `0x800798A8`, and manual/later/post-stage saves remain normal.

See [Flow bypasses](Flow-Bypasses) for the exact bytes and boot-flow branch.
