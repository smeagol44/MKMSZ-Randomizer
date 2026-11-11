# Fighter recompiler proofs

Disposable proof builders for the [Fighter recompiler plan](../../wiki/Fighter-Recompiler-Plan.md). Each builder takes clean ROMs only, hash-guards its inputs and every patched site, and writes a separate output ROM; ROM bytes are never committed. Proof caves and allocations here (the Reverse Elbow v6 / teleport payload arena, file `0x1B`, selector 3) are proof-only, not production allocations.

| Builder | Output | Tests |
|---|---|---|
| `MKMSZR_build_generic-projectile_proof_v01.py` | `MKMSZR_generic-projectile_common_proof_v01.z64` | Generic projectile on the native enemy-projectile path (class `0x700` child, `0x80047160` with type 4, `0x8002BA04` collision), no Ice patching; Sub-Zero `F,F + LK` throws the stock Ice-ball art ([components](../../wiki/Fighter-Recompiler-Components.md#generic-projectile-lowering-planned)) |
