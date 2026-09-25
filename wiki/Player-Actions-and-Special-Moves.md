# Player actions and special moves

> **Scope:** This page owns the **MKMSZ host-side action/control ABI**: special-action descriptor and installer semantics, scheduler/context transfer, player movement/animation/strike primitives, callback lifetime and cleanup rules, and durable host-side findings from the Reverse Elbow proof line.
>
> Donor choreography, donor move phases, MKT strike/reaction meanings, no-repel semantics, combo translation, and reusable donor -> MKMSZ mappings are canonical in [MKT adapter primitives](MKT-Adapter-Primitives). The old URL is retained only as a historical supersession stub at [Foreign moves and Reptile](Foreign-Moves-and-Reptile).

## Low Kick descriptor and special-action path

```text
semantic Low Kick 0x80014C60
-> event-4 handler 0x8003C94C
-> descriptor parser 0x8004A0E0
-> matcher 0x80049E60
-> transfer dispatcher 0x80049D14
-> installer 0x80032CD4
```

The Low Kick table is RAM `0x800B0F68` / ROM `0xB1B68`. It has two active `0x2C`-byte records, followed by a zero `u16` sentinel at `0x800B0FC0`. Unrelated data begins eight bytes later, so adding a third record in place is unsafe; an added descriptor must use relocated owned storage.

| Offset | Type | MKMSZ host meaning |
|---:|---|---|
| `+0x00/+0x02` | two `u16` | Legal semantic-button masks |
| `+0x04` | `u32` | Transfer selector; stock implemented values 0 and 1 |
| `+0x08` | pointer | Optional no-argument condition |
| `+0x0C` | pointer | No-argument action/process callback |
| `+0x10` | `u16` | Input-history window |
| `+0x12..+0x1C` | six `u16` | Facing-right tokens, zero-terminated |
| `+0x1E..+0x2A` | seven `u16` | Facing-left tokens, zero-terminated |

Direction tokens are `8=Left` and `9=Right`. The Reverse Elbow proof used the semantic command **Back -> Forward + Low Kick**: facing right `8,9,0`, facing left `9,8,0`, with window `0x10`. The donor reason for that command and the donor move choreography belong to [MKT adapter primitives](MKT-Adapter-Primitives).

## Horizontal locomotion and facing

**Static-confirmed.** The main player process at `0x80028F3C` owns normal directional locomotion. Controller `+0x638` points directly to the remapping-aware semantic input word `0x800BF2EE`. In its normal horizontal state, Right (`0x2000`) and Left (`0x8000`) are copied to controller `+0x68C` as the active direction.

The same input classification derives controller `+0x704` from actor facing bit `+0x8C & 0x10`:

- Right stores the facing bit directly;
- Left stores the facing bit XOR `0x10`.

The result is direction-independent: `+0x704 == 0` means the requested horizontal direction matches current facing, while nonzero means it opposes current facing.

At `0x800293B0`, stock branches on this marker:

```text
+0x704 == 0
    -> 0x8002EAFC run check
    -> 0x80030178 forward locomotion setup
    -> selector 1 / primary slot 0x01 walk_forward

+0x704 != 0
    -> 0x80030208 backward locomotion setup
    -> selector 2 / primary slot 0x02 walk_backward
```

Both setup helpers preserve fighter-specific speed tables and stock movement state. `0x80030178` writes the forward parameters and returns `1`; `0x80030208` writes the backward parameters and returns `2`. The selected value is shadowed in controller `+0x680` before `0x8002FE54` installs the corresponding animation.

The stock facing-flip primitive is `0x8003188C(actor)`. It toggles only actor `+0x8C bit 0x10` and then calls the normal frame/setup path `0x8001BDA0` with actor `+0x74`. Future control work should use this primitive rather than writing the facing bit directly.

### Turn / facing-lock design seam

Semantic Turn/Combine is bit `0x0001`. The player controller is wired to the remapping-aware semantic input word `0x800BF2EE` through controller `+0x638` during player construction. Inventory code at `0x8007764C` separately reads that same semantic word and masks `0x0001` for Combine, so a modern-control implementation must **not** globally clear or remap Turn; inventory Combine behavior must remain context-local and stock.

The stock gameplay turn-action routine at `0x8003D86C` selects primary animation slot `0x03`, the canonical `turn` animation, and runs the native turn-action sequence. Because the routine operates through the current controller rather than being intrinsically player-only, a control-assist proof should suppress the standalone turn only when current controller `+0x638 == 0x800BF2EE`; this preserves non-player/native users while making held Turn available as the player-facing modifier.

The accepted control-assist direction is gameplay-local:

```text
requested direction matches facing
    -> vanilla forward path

requested direction opposes facing
    + Turn held
        -> vanilla backward path
    + Turn not held
        -> stock facing flip
        -> stock forward/run path
```

This preserves the native backward-walk implementation as an intentional **Facing Lock / Backpedal** modifier instead of recreating it. The ordinary stock turn-action state is distinct from inventory handling and must be suppressed or bypassed for this mode so holding Turn can function as a modifier rather than immediately consuming the press as a standalone turn.

While a walk is already active, stock polls `controller+0x68C & semantic_input`. Releasing/changing the active direction exits through the normal stop/cleanup path and the next locomotion entry recomputes direction/facing. A first proof may therefore tolerate a one-tick re-entry on reversal, but release of Turn during an already-active backward walk needs an explicit check if the desired modifier semantics are to switch immediately back to auto-facing without requiring a direction repress.

### Smallest proof contract

A bounded proof can stay almost entirely inside stock locomotion semantics:

```text
after stock computes controller +0x704:
    if +0x704 == 0:
        leave stock forward path unchanged
    else if Turn/Combine bit 0x0001 is held:
        leave stock backward path unchanged
    else if nearest opponent has +0x6BC & 0x0200:
        leave stock forced-facing behavior unchanged
    else:
        0x8003188C(player_actor)
        controller +0x704 = 0
        resume stock forward/run selection
```

The same proof must player-gate the standalone `0x8003D86C` turn action so a held Turn press does not itself consume control before horizontal locomotion sees it. Inventory Combine is outside that gameplay action path and remains vanilla. Earth boss behavior is an explicit manual test item because the generic `0x0200` policy is not statically universal.

### Stock forced-facing exception

Shared host routines use opponent-controller `+0x6BC bit 0x0200` as a gate for automatic `0x80031EF0` face-opponent behavior. The stock fighter-characteristics table sets this bit for several special/boss fighter types, including the documented Wind `0x08`, Water `0x0B`, Fire `0x0C`, and Fortress `0x1B/0x1D` encounters. This is a **face-policy flag**, not a proven universal "boss bit"; other special types also carry it.

Earth type `0x19` is a separate unresolved exception. Its stock characteristics-table word is zero, and the Earth custom boss constructor at overlay VA `0x802EDF50` (Earth overlay file `0x9C`) bypasses the generic fighter-characteristics initialization: it manually installs type `0x19` at actor `+0x78`. A direct audit of the Earth overlay finds neither a `+0x6BC` write nor a direct call to `0x80031EF0` in that boss constructor/overlay. Therefore `+0x6BC & 0x0200` is **not yet proven to detect the Earth boss**, and it must not be documented or implemented as a universal boss bit.

For the first modern-facing proof, the safe static rule is: defer completely to stock when the nearest opponent carries `+0x6BC & 0x0200`; test Earth separately. If Earth runtime behavior still auto-faces as expected, capture that route and trace its distinct mechanism before production integration instead of hard-coding a stage ID.

### Direction-facing proof v01/v02

The first expansion-loaded control proof uses a proof-only file-`0x1A` module in the 15 KiB expansion pool and enters freshly loaded code only through uncached KSEG1 trampolines.

- **v01 — Rejected / failed.** Pressing the first opposite horizontal direction immediately hard-hung. The proof used current-controller global `0x802FCE20`, repeating the already-rejected unsigned-low-immediate interpretation. The actual address is `0x802ECE20`: `lui 0x802F` paired with signed low immediate `0xCE20` subtracts `0x31E0`.
- **v02 — Runtime-confirmed on the tested route.** Changing only that global to `0x802ECE20` made the control behavior work as intended: opposite horizontal input flips Sub-Zero and proceeds through stock forward locomotion; holding Turn preserves vanilla backward walking / facing lock. The user reported the corrected behavior worked perfectly and matched the requested control model.

The proof line continued through v10/v06 and has now been promoted into the shared browser/CLI patch core. **Runtime-confirmed production composition:** `TURN: TOGGLE` preserves vanilla controls; `TURN: LOCK` uses the accepted v10 world-direction/facing-lock model, while v06 makes the fragile release/action-install hooks leaf-only and temporarily defers to stock semantics when the bounded controller-list scan finds opponent `+0x6BC & 0x0200`. The full production build passed both former Temple hang regressions and the first Scorpion forced-facing route. Earth type `0x19` remains Pending and is not generalized from Scorpion.

## Host action primitives

| Address | Correct MKMSZ meaning |
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
| `0x800328FC` | Exit action / restore control |
| `0x8004AA4C` | Scheduler context-transfer shim using table `0x800A1050` |
| `0x8004AB84` | Complete ice-projectile action root |
| `0x80030974` | Animation token-`0x0B` secondary-resource actor handler |
| `0x80031208` | Facing-aware actor-relative XY adjustment |
| `0x8004CBC4` | Projectile child-process bridge; binds staged secondary actor into a new child controller/process |
| `0x8004CC50` | Generic projectile flight/collision loop |
| `0x8004CE6C` | Projectile strike-record resolver |
| `0x800BF308` | Special-action lock; native action roots set it |

`0x8004B82C` is the ice-projectile flight callback. `0x8004CC14` is projectile setup that writes a projectile actor's `+0x14` and initializes projectile animation timing through `0x80031724`. Neither is the player propulsion helper. The older recommendation to use `0x8004CC14` for player movement is **Rejected / failed**.

### Projectile secondary-actor staging

The stock Zap/Ice path uses two controller fields that alias the same secondary actor at the projectile handoff but serve different lifecycle roles:

- animation token `0x0B -> 0x80030974 -> 0x80034510` creates a resource-backed actor and temporarily installs it at current controller `+0x6E0`;
- `0x80030974` stores that actor at `+0x714`, restores the owner to `+0x6E0`, then copies `+0x714 -> +0x648`;
- stock straight-Ice placement at `0x8004AFF8` passes `+0x648` to `0x80031208`;
- the same action later uses `+0x714` as the temporary current actor for animation;
- `0x8004CBC4` gives parent `+0x714` to child controller `+0x6E0`, tags the actor `0x700`, and clears parent `+0x648`.

Therefore `+0x648` is the stable secondary-actor working/staging pointer in this setup, while `+0x714` is the active/transfer pointer and may be temporarily repurposed before being restored. The v71 postmortem statically rejects the hypothesis that the stock `0x80031208` call positions a different helper actor from the one handed to the projectile child.

### Projectile flight callback and velocity seam

The complete v75 host transaction has three independent actors/process lifetimes. The parent `0x8004AB84` saves owner `+0x6E4/+0x714`, temporarily sets `+0x714` to the **value loaded from** `0x80291C10` (file-`0x87` resource base), `+0x6E4` to offset `0xF88`, and `+0x718` to `6`, and starts class-`0x100` companion and tint processes. `0x8002830C` copies this helper context to its child. Helper `0x80060A3C` uses script `resource+0xFA0` to construct a **new primary and mirror actor**; it allocates texture slot `0x200..0x2FF` and the stock Ice palette, inserts both actors, advances the primary through `0x800304C0`, and copies its body to the mirror with mirror `+0xFA=0`. It removes both through `0x80024B00`, sleeps two ticks, releases the texture through `0x8001C424`, and exits. Its traced cleanup does **not** release the acquired palette handle. `0x8004AB0C` calls the blue screen tint and exits without creating an actor. The parent restores its saved `+0x714` during its sleep. These helper actors are not the subsequently created projectile.

The initial slot-`0x24` runner stops at file-`0x87 +0xDB4` **before** the projectile token. Following the companion sleep, parent advance `0x8004AEDC` consumes token `+0xDB8` and operand `+0xDBC`, creating the projectile through `0x80030974 -> 0x80034510 -> 0x800281A0/0x80028128`. The token sets `+0x714=+0x648` to the new actor, gives it owner `+0x98`, render record `+0x7C`, fixed texture slot `+0x9C=0x24`, stock Ice palette selector `+0x9E`, owner position and flags, and inserts it at `0x80030AC8`. The parent places `+0x648` with native `0x80031208(+5,+38)`. **On the ordinary straight branch (`0x80111F98=0`), `0x8004B020` invokes `0x8004B584` and `0x8004B028` jumps over the proof wrapper at `0x8004B040`: the wrapper does not bind the normal v75 rocket.** `0x8004B584` temporarily makes `+0x714` current at `+0x6E0` and runs stock `0x800304C0` at `0x8004B5A0`, consuming the next Ice entry `+0xDC4`; then it restores the owner, checks strike, and normally hands `+0x714` to class-`0x700` child through `0x8004CBC4` (which clears parent `+0x648`). Other mode/contact branches have separate behavior.

The straight child `0x8004B82C` reads `file-0x87 +0xFD0 = +0xD90`, sets `+0x6E4` to the **rocket-loop cursor**, calls `0x8004CC14` once to set facing velocity and the `0x80031724` rate (`+0x6A6=3`, `+0x6A8=1`), and v75's later wrapper sets initial velocity `0x46666` and child callback `+0x70C`. The generic `0x8004CC50` loop sleeps one tick; `0x8003174C` first consumes the countdown and then calls `0x800304C0` on `+0xD90`, binding the genuine rocket **after the earlier Ice frame has been published**. The callback changes velocity, not image or palette. This is the observed late, well-formed v75 rocket's actual path. The parent wrapper at `0x8009A210` is reachable from the nonzero-mode branch, so results from the normal straight shot cannot validate its palette store or frame transaction.

`0x8001BDA0` stores actor `+0x74` (entry), constructs `+0x7C`'s image pointer, dimensions, facing and anchors from `+0x98`, and with `+0x8C bit 0x40` set increments `+0xFA` to request a texture decode. It refreshes `+0x68/+0x80/+0x6A/+0x6C/+0x6E/+0x70` from texture slot `+0x9C` and palette selector `+0x9E`. Constructor `0x800281A0` calls it before the token has finalized slot/selector/owner flags, so its first call is not a complete ready-to-render transaction. `0x800185B8` later consumes `+0xFA`, decodes record `+0x7C` with `0x8000322C`, and queues slot-`0x24` upload through `0x8001D6EC`; the frame scheduler drains the queue with `0x8001D7F0`. `0x80024650` links the actor into the active **movement and render** list sorted by `+0x5C/+0x30`; it neither builds the record nor uploads pixels. Both the Ice entry `+0x34A58` and rocket entry `+0x4E6E4` have a zero preceding descriptor word. On the `+0x8C bit 0x40` path, a same-entry bind and a changed-entry bind with that zero word both increment `+0xFA` and use `+0x9C`; the earlier claim that same-shape binding skips a necessary rocket rebuild is false for these entries.

In v83 the raw pre-insertion `0x8001BDA0` changes actor `+0x74` but leaves controller `+0x6E4` on the Ice script, so `0x8004B5A0` replaces that early bind with Ice. v84 redirects `+0x6E4` to `+0xD90` and advances the rocket before insertion, but also forces selector zero. v88 repeats the early rocket descriptor/cursor advance while preserving the correct dynamic ROCKET_P selector and still shows one frame of corrupted Sektor-like texture. Therefore descriptor/cursor state alone is not enough to guarantee first-published pixel data. The render path makes the distinction explicit: `0x8001BDA0/0x800304C0` marks actor `+0xFA` dirty, while the active pass at `0x800185B8` later decodes `+0x7C`, queues the texture-slot upload through `0x8001D6EC`, and only the separate queue drain commits it. v89 **Runtime-confirms** pre-publication texture-slot readiness as the missing seam: native synchronous `0x8001BF70` prepares finalized slot `+0x9C` before stock list insertion, `0x8001BDA0` refreshes the actor fields, and the user observes immediate correct rocket presentation with no one-frame corrupted Sektor. This establishes that actor descriptor/palette correctness is insufficient until the slot's pixel data is resident before publication.

Palette selection is a distinct resource transaction: token `0x80030974` calls `0x8001C528(0x800B1A24,0x100,0)` and stores the returned **handle minus `0x80`** at actor `+0x9E`. The player type-4 constructor instead acquires its source via `0x800B13D0[type]`: v75 file-`0x87 +0x4584C` (table entry `+0x45848`) contains the resident Sektor colors, but its runtime selector is dynamically allocated, ordinarily in `0xC0..0x1BF`. Selector **zero** maps to handle `0x80`; it does not mean “the owner's Sektor palette.” `0x8001BDA0` resolves active `+0x80` through `0x80290A02 + selector*8`; render upload uses `0x802E73E0 + selector*4`. Matching `+0x80` to selector zero alone preserves the wrong palette source. `0x8001C64C` releases an explicitly owned palette handle when called; neither the traced companion cleanup nor the normal projectile `0x8004CDF8` calls it. The exact contents of slot zero in the runtime captures, and an end-to-end per-shot palette release, are unverified.

**Static-confirmed cleanup split:** `0x8004CC50` calls `0x8004CDF8` for offscreen/lifetime exit; this removes the projectile actor and terminates the child process. On normal loop return, the Ice child switches scheduler callback to `0x8004BB64`. Separately, the parent finishes seven postlaunch animation advances and six sleeps, calls `0x8004B524` to clear `0x800BF308`, then `0x800328FC`. The companion helper removes its own pair of actors; tint process exits on its own. New donor actions must model each termination path explicitly. The full donor/host map and evidence limits are in [MKT adapter primitives](MKT-Adapter-Primitives).

`0x80031394` is **not a proven safe drop-in `match_ani_points`** at this seam. Besides copying owner position, its child `+0x64` branch can flip facing through `0x8003188C`; its other branch dereferences child render record `+0x7C` and uses anchor offsets. v78 called it on the staged Ice actor before the genuine rocket first descriptor and hard-hung. The exact failing precondition or register state is unresolved, so a generic origin adapter must first establish the actor/descriptor state it requires.

**Static-confirmed.** The generic projectile flight loop at `0x8004CC50` provides a reusable per-tick callback seam:

```text
loop entry:
    child +0x680 = child +0x70C

each flight iteration:
    sleep 1
    target animation/update work
    offscreen/lifetime checks
    if child +0x680 != 0:
        call child +0x680
    resolve strike record
    run projectile strike/contact path
```

For the stock Ice/Sektor proof actor, horizontal projectile velocity is actor `+0x14`. `0x8004CC14(actor, magnitude, rate)` is the one-time facing-aware setup helper used by the stock path and also initializes animation timing through `0x80031724`. The flight loop itself does not rewrite actor `+0x14` between callback invocations. A translated per-tick acceleration callback can therefore mutate only actor `+0x14` while preserving the stock lifecycle and animation-rate state.

This distinction explains the v71 failure mode: repeatedly calling `0x8004CC14` from the tick callback also reinitialized animation timing every tick. Direct per-tick `+0x14` mutation is the narrower target operation for the current acceleration proof.

### Projectile local-position units

`0x80031208` consumes signed local whole-coordinate offsets. On the normal freshly-created projectile path (`actor +0xDC == 0`), it mirrors local X for actor flip, rotates vector `(x,y,0)` through the actor-local orientation, and adds the resulting integer components to actor world position `+0x2C/+0x30/+0x34` after `<< 8`. Target actor positions are therefore 8-fractional-bit fixed-point while this helper's placement arguments are whole local units. Its matrix normalization is unity; there is no additional target scale factor.

For the current Sektor straight-missile case, the donor's already-N64-scaled retail displacement is definitively semantic `X=+5, Y=+38`: MKT source `multi_adjust_xy` applies its second argument to `oxpos` and third to `oypos`, and retail `make_rocket` passes `a1=5,a2=38` to the same operation. The X/Y-swap hypothesis is therefore **Rejected / failed**.

Those values map directly to the target helper's **offset arguments** `(+5,+38)`, with facing remaining the helper's responsibility. However, complete visible spawn equivalence also depends on the projectile's position **before** that adjustment. MKT performs `setup_proj_obj -> get_proj_obj_m -> match_ani_points(owner, projectile)` before applying the offset, while the current target proof inherits stock Ice secondary-actor creation/alignment. Equivalence of those pre-adjust base origins is **Pending** and is the next relevant placement seam; v72 proves stable mirrored offset application, not full donor-equivalent origin setup.

### Projectile velocity integration

**Static-confirmed.** `0x80017F80` is the actor update/integration loop used by the gameplay main loop. For a normal projectile with actor `+0xDC == 0`, it reads local velocity fields `+0x14/+0x18`, arithmetic-shifts them by 8, rotates the resulting local vector through actor orientation, and adds three times the transformed integer components into fixed8 world position `+0x2C/+0x30/+0x34`.

Therefore, at neutral orientation:

```text
delta_world_x_per_actor_update =
    3 * (actor_xvel >> 8) / 256
```

in world-coordinate units. The low eight velocity bits do not contribute to that update.

The gameplay loop invokes the actor integrator at `0x80014258` and gates the next iteration on the retrace/tick counter at `0x802FCD44`; the resulting ordinary rendering/movement cadence is approximately 30 Hz. This is distinct from MKT's 16.16 `oxpos += oxvel` motion at nominal 60 Hz. The donor-to-target projectile adapter must therefore translate both **numeric velocity units** and **update cadence**, not merely copy MKT `oxvel.pos` values into target actor `+0x14`.

The exact Sektor resampling policy is owned by [MKT adapter primitives](MKT-Adapter-Primitives). v73 Runtime-confirms that direct per-tick writes to `+0x14` are stable, but its raw donor constants are not the final calibrated translation.

The current process/controller pointer is at effective address `0x802ECE20`, not `0x802FCE20`.

Function-level semantics are indexed in [Function registry](Function-Registry); this page owns how the helpers compose into the host action lifecycle.

## Projectile actor/process host ABI

The v63-v70 Sektor missile work and follow-up static trace expose a target-native projectile split that should be reused by donor adapters rather than treating Ice Blast as one monolithic move.

**Static-confirmed target composition:**

```text
animation token 0x0B
-> 0x80030974
-> 0x80034510
-> 0x800281A0 -> 0x80028128   ; resource-backed secondary actor
-> stage actor in controller +0x714/+0x648
-> 0x80024650                  ; insert actor

0x80031208(actor, dx, dy)      ; facing-aware relative placement

0x8004CBC4(callback)
-> 0x8002830C(class 0x700, callback)
-> copy parent/opponent context
-> child +0x6E0 = parent staged actor +0x714
-> tag/clear staging state
```

This establishes distinct host primitives for **resource actor creation**, **relative placement**, and **child projectile process creation**. The exact function meanings remain indexed in [Function registry](Function-Registry); donor-side semantics and the reusable adapter vocabulary remain in [MKT adapter primitives](MKT-Adapter-Primitives).

The projectile collision/strike path is likewise separate from Ice freeze presentation: `0x8004CC50` drives the generic projectile loop, `0x8004CE6C` resolves a fighter-local strike record from the supplied selector, and `0x8004CF3C -> 0x8002BA04` reaches the normal target strike/collision core. A donor strike index is still **not** portable numerically.

### Resolved player animation cursor

The current controller/process animation cursor is `+0x6E4`. v69 is **Runtime-confirmed** for one narrow use: after the stock special helper completes, temporarily redirecting `+0x6E4` to the imported chest script, advancing once through `0x800304C0`, and restoring the cursor displays the genuine chest-open frame on the player without hanging.

That runtime result proves the host cursor/update mechanism only. It does not make a one-frame post-helper injection the final donor-animation runner.


## Installer, scheduler, and context-transfer semantics

`0x80032CD4` installs a top-level special-action callback. In the observed installed context, the callback begins with `$ra` equal to the callback entry. A normal `jr ra` therefore re-enters the callback instead of returning to an ordinary caller.

`0x8004AA4C` is not a generic action initializer. It transfers scheduler context according to selector table `0x800A1050`. Stock selectors `0..2` are defined. The stable Reverse Elbow v6 proof used a deliberately added selector-3 bridge as a **proof-specific controlled extension**; that does not make selector 3 a stock ABI entry or a production allocation.

A native special action also needs the target action-lock/cleanup conventions. The successful host-side proof set `0x800BF308`, kept its loops bounded, and exited through native scheduler/control restoration.

## Callback lifetime and cleanup rules

These are durable host-side safety constraints:

- an installed top-level action callback must not simply return normally;
- every movement/contact wait loop must be bounded;
- action exit must transfer through the native scheduler/cleanup path or an equivalently proven target-native path;
- the native special-action lock must be established/preserved where the action path requires it;
- interruption/contact branches are lifecycle paths and must reach cleanup, not just switch animation;
- one observed state byte is not enough to prove an action is still active after interruption.

These rules come from both successful and failed bounded proofs and are applicable to later donor-adapter work regardless of the specific move choreography.

## Durable Reverse Elbow host-side findings

The Reverse Elbow experiments are useful here only for what they established about MKMSZ's host action system.

| Finding | Evidence / implication |
|---|---|
| Early movement interpretation used projectile setup as propulsion | **Rejected / failed.** `0x8004CC14` is projectile setup; `0x8002B1EC` is the player velocity helper. |
| Experimental victim callback could hard-hang on contact | **Rejected / failed.** Victim/contact work must not be added before its callback/lifetime semantics are understood. |
| v3 hung immediately with or without an enemy | **Rejected / failed.** Later analysis explains this as installed-callback `jr ra` self-reentry. |
| v5 omitted native special lock `0x800BF308` | **Rejected / failed** as a complete lifecycle model; omission is a strong host-side hang risk. |
| v6 used selector-3 bridge + lock + player velocity + bounded loops + native restore | **Runtime-confirmed** stable lifecycle baseline; repeatable without whole-game hang on the tested route. |
| v7 added strike `0x14` and a Y-distance gate | The Y gate behaved as intended against a jumping enemy; no abnormal jumping-enemy contact was observed on that bounded test. |
| v8 attempted velocity `0xD0000`, locomotion index `controller+0x6E6`, per-tick reapply, forced-X crossover `+0x3800`, and expanded diagnostics | **Not confirmed as an improvement.** Runtime testing still showed slow movement/no pass-through; attacks could cancel forward motion while the displayed `L 1` state stayed unchanged; expanded HUD diagnostics were absent. These parameters are preserved as failed-proof reproduction data, not accepted movement values. |

The durable conclusion is the **v6 lifecycle model**, not the v8 movement behavior. Direct player-velocity measurement remains the clean way to separate movement calibration from pass-through, victim-hold, and strike behavior.

The old forced-X crossover attempt is not a reusable host primitive and is not accepted donor behavior. Donor-side pass-through/no-repel semantics are documented in [MKT adapter primitives](MKT-Adapter-Primitives).

## Current host-side boundaries

Established:

- descriptor parsing/matching and special-action installation path;
- bounded scheduler sleep/context transfer primitives;
- player velocity/stop/facing helpers;
- animation select/advance helpers and the resolved controller animation cursor at `+0x6E4`;
- resource-backed secondary-actor construction, facing-aware relative actor placement, and projectile child-process binding;
- generic projectile collision/strike resolution path;
- strike dispatch and collision/reaction entry points;
- native action lock and exit/control restoration;
- callback self-reentry hazard and bounded cleanup requirement.

Not established here:

- a production-ready generic donor action runner;
- generic donor velocity-unit conversion;
- a generic no-repel shim;
- arbitrary donor victim-reaction translation;
- donor animation control-token translation;
- a production-ready generic wrapper that composes the identified projectile actor/process primitives with donor callback/state/effect semantics.

Those translation-layer gaps are tracked in [MKT adapter primitives](MKT-Adapter-Primitives).

## Related pages

- [MKT adapter primitives](MKT-Adapter-Primitives) — canonical donor choreography and donor -> MKMSZ semantic translation.
- [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer) — accepted genuine-port strategy and compatibility contract.
- [Foreign moves and Reptile](Foreign-Moves-and-Reptile) — historical supersession stub for the retired behavioral-recreation page.
- [Function registry](Function-Registry) — flat canonical function semantics.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded patch sites.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ownership/allocation and proof-vs-production boundaries.
