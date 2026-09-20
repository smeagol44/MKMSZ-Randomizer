# Player actions and special moves

This page owns the MKMSZ-side action architecture and the Reverse Elbow proof history. It corrects several earlier address interpretations.

## Low Kick descriptor path

```text
semantic Low Kick 0x80014C60
-> event-4 handler 0x8003C94C
-> descriptor parser 0x8004A0E0
-> matcher 0x80049E60
-> transfer dispatcher 0x80049D14
-> installer 0x80032CD4
```

The Low Kick table is RAM `0x800B0F68` / ROM `0xB1B68`. It has two active `0x2C`-byte records, followed by a zero `u16` sentinel at `0x800B0FC0`. Unrelated data begins eight bytes later, so adding a third record in place is unsafe; the table must be relocated.

| Offset | Type | Meaning |
|---:|---|---|
| `+0x00/+0x02` | two `u16` | Legal semantic-button masks |
| `+0x04` | `u32` | Transfer selector; implemented values 0 and 1 |
| `+0x08` | pointer | Optional no-argument condition |
| `+0x0C` | pointer | No-argument action/process callback |
| `+0x10` | `u16` | Input-history window |
| `+0x12..+0x1C` | six `u16` | Facing-right tokens, zero-terminated |
| `+0x1E..+0x2A` | seven `u16` | Facing-left tokens, zero-terminated |

Direction tokens are 8=Left and 9=Right. Reverse Elbow's semantic command is **Back → Forward + Low Kick**: facing right `8,9,0`, facing left `9,8,0`, within window `0x10`.

## Corrected action primitives

| Address | Correct meaning |
|---:|---|
| `0x8002B1EC` | Player velocity helper; writes player actor `+0x14` and `+0x58` |
| `0x8002B1C0` | Stop/clear linear motion |
| `0x80031D00` | Find nearest opponent controller |
| `0x80031EF0` | Face opponent |
| `0x8002FE54` | Select animation `(table,index)` |
| `0x800304C0` | Advance animation |
| `0x8004CF3C` | Fighter strike dispatch |
| `0x8002BA04` | Collision/damage/reaction core |
| `0x80028794` | Process sleep |
| `0x800328FC` | Exit action/restore control |
| `0x8004AA4C` | Scheduler context-transfer shim using table `0x800A1050` |
| `0x8004AB84` | Complete ice-projectile action root |
| `0x800BF308` | Special-action lock; native action roots set it |

`0x8004B82C` is the ice-projectile flight callback. `0x8004CC14` is projectile setup that writes a projectile actor's `+0x14` and selects animation. Neither is the player propulsion helper. This supersedes older notes that recommended `0x8004CC14` for Reverse Elbow movement.

The current process/controller pointer is at effective address `0x802ECE20`, not `0x802FCE20`.

## Callback lifetime rule

`0x80032CD4` installs a top-level special-action callback with `$ra` equal to the callback entry. A normal `jr ra` therefore re-enters itself. The callback must transfer into the scheduler/native cleanup path or otherwise not return normally. The v3 immediate hang is explained by this self-reentry.

`0x8004AA4C` is not a generic action initializer: it transfers scheduler context according to selector table `0x800A1050`. Stock selectors 0–2 are defined. The successful proof extends selector 3 as a controlled bridge.

## Reverse Elbow proof history

| Version | Result |
|---|---|
| v1–v2 | Command dispatch reached; motion minimal; facing corrected in v2; experimental victim callback could hard-hang on contact |
| v3 | Immediate hang with or without enemy; later explained by top-level `jr ra` self-reentry |
| v4–v5 | Additional lifecycle attempts; v5 omitted native special lock `0x800BF308`, a strong hang cause; used incomplete action assumptions |
| v6 | First stable lifecycle: selector-3 scheduler bridge, lock=1, player velocity `0x8002B1EC`, bounded loops, native control restore; repeatable without whole-game hang |
| v7 | Strike `0x14`, Y-distance gate, attempted pass-through, diagnostic HUD; jumping-enemy test showed no abnormal contact |
| v8 | Intended 4x velocity `0xD0000`, locomotion index `controller+0x6E6`, per-tick reapply, forced X crossover `+0x3800`, expanded HUD |

Latest runtime testing did not confirm the v8 improvements: no enemy pass-through, attacks cancel forward motion while diagnostic `L 1` stays unchanged, direction/jump/crouch are locked but attacks remain possible, speed remains very slow, and expanded HUD text is absent. The Y gate behaved as intended against a jumping enemy. Durable result: v6 lifecycle stability. v8 speed, pass-through, interaction, and diagnostics remain unresolved.

## Pending proof questions

v6 is the established lifecycle baseline. The next proof design needs a conflict-free production-adjacent allocation and observable states. Direct player-velocity measurements would separate the unresolved movement problem from later pass-through, victim-hold, and strike behavior. A stale `L 1` byte alone does not establish that an action remains active. Bounded loops and native cleanup at every exit are part of the successful lifecycle design.
