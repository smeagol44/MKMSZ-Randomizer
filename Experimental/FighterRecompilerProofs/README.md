# Fighter recompiler proofs

Disposable proof builders for the [Fighter recompiler plan](../../wiki/Fighter-Recompiler-Plan.md). Each builder takes clean ROMs only, hash-guards its inputs and every patched site, and writes a separate output ROM; ROM bytes are never committed. Proof caves and allocations here (the Reverse Elbow v6 / teleport payload arena, file `0x1B`, selector 3) are proof-only, not production allocations.

| Builder | Output | Tests |
|---|---|---|
| `MKMSZR_build_generic-projectile_proof_v01.py` | `MKMSZR_generic-projectile_common_proof_v01.z64` | Generic projectile on the native enemy-projectile path (class `0x700` child, `0x80047160` with type 4, `0x8002BA04` collision), no Ice patching; Sub-Zero `F,F + LK` throws the stock Ice-ball art ([components](../../wiki/Fighter-Recompiler-Components.md#generic-projectile-lowering-planned)) |
| `MKMSZR_build_generic-projectile_proof_v02.py` | `MKMSZR_generic-projectile_common_proof_v02.z64` (default), `…_v03.z64` (`--reaction toward`) | Same path with Reptile's MKT forceball: flight loop and impact frames (type 4, 64-colour palette) in an enlarged file `0x87` at ROM `0xF20000`, speed `0x77776`, MKT strike box; victim arc away (host reaction `0x1A`, v02) or toward the attacker (mirror `0x25`, v03) |
| `MKMSZR_build_generic-projectile_proof_v04.py` | `MKMSZR_generic-projectile_common_proof_v04.z64` | v03 plus: the forceball's own flight palette `0x800BECE4` (from save states), no z shift, a calibrated spawn offset (−20, +72 world units), and the MKT launch arc (lifted host reaction `0x25` with converted constants in dummy reaction slot `0x2B`) |
