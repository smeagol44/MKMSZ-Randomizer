# Pickup placement and Ice-Blast cancel proofs

> **Scope:** This page records two bounded post-1.0 research tools/results from 2026-10-02: hand-authored ordinary-pickup placement from live Sub-Zero coordinates, and the Runtime-confirmed normal **Ice Blast -> Pickup** action cancel. Neither behavior is part of the 1.0 requirements or normal production pipeline.

## Evidence status

| Result | Evidence | Scope |
|---|---|---|
| Live pickup-placement coordinate probe | **Runtime-confirmed diagnostic** | The accepted v03 probe reached gameplay and printed readable native stage/selector plus live player X/Y/Z. |
| Hand-authored pickup placement | **Runtime-confirmed bounded authoring method** | Two Wind Herbs were relocated using player-position captures and visually iterated. The project authoring convention is now **pickup Y = player Y + 28 world units**. |
| Normal Ice Blast -> Pickup cancel | **Runtime-confirmed bounded proof** | The user reported the v01 proof worked perfectly on the tested Wind route: while standing on an ordinary pickup, Pickup can interrupt normal ground Ice Blast and immediately enter the native pickup transition. |
| Product integration | **Post-1.0 / 4Fun; not integrated** | Keep separate from 1.0 controls and ordinary pickup production behavior unless explicitly promoted later. |

## Coordinate probe and placement convention

Ordinary pickup records store destination position in their first words:

- record +0x00 = X;
- record +0x04 = Y;
- record +0x08 = Z;
- record +0x0C = location-owned metadata.

The accepted diagnostic reads the live player controller pointer at 0x802C1AC0, then controller +0x6E0 for the player actor. Actor +0x2C/+0x30/+0x34 are printed directly as raw fixed8 X/Y/Z. These values are already in the coordinate family used by ordinary pickup records; do not convert them to decimal world units before writing a record.

The accepted hand-authored placement rule is:

    pickup X = displayed player X
    pickup Z = displayed player Z
    pickup Y = displayed player Y + (28 << 8)
             = displayed player Y + 0x1C00

The +28 Y correction is a **visual authoring convention**, not an engine requirement. Directly copying Sub-Zero's Y put the pickup around head height. A later Wind test was moved too far downward, so the project settled on **+28 world units** as the preferred chest-area placement offset for future hand-authored pickup locations.

This convention should be validated if a different pickup model has a materially different visual anchor.

### Probe implementation

Repository tool:

- tools/build_pickup_placement_probe.py

The distilled tool composes Safe Stage Select, selector-only save bypass, arena reservation/native payload transport, post-legal logo bypass, a gameplay-only HUD coordinate overlay, and HP/resource refill for safe placement work.

The overlay is gated by gameplay-enable 0x802C1A04, preserving Mission Objective/front-end execution. The HUD hook is ROM 0x0005D9CC; the displaced stock submit 0x8001EAE4 runs first. Native text is drawn through 0x80073E74 with font pointer 0x800B1E20.

The original proof lineage found two important rejected mistakes:

1. running gameplay-only probe logic before the gameplay-enable gate could hang during Mission Objective;
2. the native text routine requires the fifth stack argument to be the font pointer, and 0x802ECE20 is the **current process pointer**, not a globally stable pickup-manager pointer. Treating HUD-process fields as pickup-manager count/base caused the rejected first-live-frame path.

The accepted v03 therefore prints only stable player/stage owners and does not scan pickup-manager state from the HUD process.

## Ice Blast -> Pickup cancel

### Requested behavior

When the player is already standing on an ordinary pickup:

    normal ground Ice Blast
        -> press Pickup while the pickup is spatially valid
        -> cancel the Ice Blast player animation/lifecycle
        -> enter the game's normal pickup transition immediately

The proof deliberately does **not** create a new pickup animation, bypass proximity, or award the item directly.

### Stock authority preserved

The ordinary pickup manager remains authoritative for Pickup input, spatial/proximity/facing checks, ordinary pickup action/state installation, and native callback/award behavior.

The proof only broadens the manager's action-eligibility gate so that normal ground Ice Blast is temporarily treated like the stock accepted pickup state.

### Exact proof seam

Proof builder:

- tools/build_iceblast_pickup_cancel_proof.py

Accepted proof artifact:

- MKMSZR_iceblast-pickup-cancel_wind_proof_v01.z64
- SHA-256 c95a0a6cdbfcf09b7352de1b4559f7d2623050f63d50269f8a67b8531cdc160d
- CRC1/CRC2 68BA01B6 / 0BAA6E9A
- exact base proof SHA-256 5a431c048f6cbaefa4337357e7fede6ae9b9ce013b16cbcd5ea6040f5678286a

The action-gate hook is at ROM 0x00039AF8 / VA 0x80038EF8. Stock loads player action controller+0x6AA and accepts its ordinary pickup state 0x303. The proof additionally accepts only when:

    controller +0x6F0 == 0x8004AB84   # normal Ice-projectile action root
    0x80111F98 == 0                   # native Ice mode zero

The mode-zero guard is important: Directional Ice uses modes 1/2, so those variants are excluded. Air Ice Blast uses a different action root and is also excluded.

After the normal pickup input/spatial gates have already passed, a second hook at ROM 0x00039BA4 / VA 0x80038FA4 rechecks that the player is still in normal ground Ice Blast and clears the native special-action lock:

    0x800BF308 = 0

Control then returns to the stock pickup manager, which performs its existing pickup transition. The proof does not directly force the reward callback or inventory insertion.

### Why the lock clear is delayed

Native Ice action 0x8004AB84 owns special-action lock 0x800BF308; its normal exit at 0x8004B524 clears that lock during recovery. Clearing it at the initial eligibility test would change Ice behavior even when no pickup interaction succeeds.

The accepted proof therefore clears the lock **only after** the stock manager has confirmed that a pickup interaction is actually going to commit. This preserves normal Ice Blast behavior when the player is not on a valid pickup or does not press Pickup.

### Runtime result and limits

**Runtime-confirmed bounded result:** the user reported the requested Ice Blast -> Pickup cancel behavior worked perfectly on the tested Wind proof.

This establishes the tested normal ground Ice Blast cancellation seam. It does **not** establish Directional Ice cancellation, Air Ice Blast cancellation, generalized cancel-any-action behavior, production compatibility of the proof helper cave, or exact behavior of every already-spawned Ice helper/projectile at every possible cancel frame.

## Product status

This experiment is intentionally classified as:

- **Atlas track:** 4Fun
- **scope:** Post-1.0 / optional
- **1.0 release blocker:** No
- **current product integration:** None

The result is retained because it establishes a useful native action-cancel technique and may support future optional movement/combat/pickup ideas without changing the 1.0 control contract.

## Related owners

- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — ordinary pickup record semantics and current product behavior.
- [Player actions and special moves](Player-Actions-and-Special-Moves) — player action lifecycle, Ice special lock, and native control/action primitives.
- [Data structures and encodings](Data-Structures-and-Encodings) — canonical ordinary pickup record grammar.
- [Function registry](Function-Registry) — function/field identities.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded proof hook sites.
- [Runtime validation status](Runtime-Validation-Status) — bounded runtime evidence.
