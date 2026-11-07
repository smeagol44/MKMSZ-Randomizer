# Sektor transplant builders

Experimental Python builders for the MKMSZ Sub-Zero -> MKT Sektor transplant proof lineage.

These scripts are preserved so disposable proof ROMs can be reproduced without depending on chat attachments. They are not production randomizer builders unless explicitly promoted elsewhere.

ROM inputs and generated ROM bytes must not be committed. Builders must keep clean-ROM hash guards, donor identity guards, bounded allocation checks, output CRC updates, and any version-specific static assertions used by the proof.

From v57 onward, preserve each generated `.py` builder here when a new proof ROM is issued.

## `original_builders/` (added 2026-11-07)

The 50 original builder scripts from the user-supplied `MKMSZR_sektor-investigation_build-kit_v01.zip` (SHA-256 `776b29700a7b52312e7dc00d682fcf88b74d7eada25b3250b6dd370180af4b77`), copied byte-for-byte; each file matches the kit's `SHA256SUMS.txt`. They cover takeover v53/v54 legacy, v54–v62, missiles v63–v89 (both v80 variants), Run v01–v05, the 16-colour palette proof, the P28/P29 owner probe and frame helpers.

They are preserved for provenance and are excluded from `ruff`. Most builders take a previous proof ROM as input, and several need the PS1 MKT members `CHARS1/ROBOT.DAT` and `CODE/ROBOT.BIN`. The kit's `build.py`, its `recipes.json` dependency chain, the v53/v54 recovery bridge and the 73 archival XOR replays are **not** copied here; the full kit stays in the Library. Reproduced identities and the takeover change map are recorded in the Wiki under [Sektor takeover proof history](../../wiki/Sektor-Takeover-Proof-History.md#build-kit-reproduction-and-takeover-change-map-2026-11-07).

These are disposable investigation builders, not production code. Do not apply their proof caves or allocations to production compositions.

## `teleport/` (added 2026-11-07)

Builders `MKMSZR_build_sektor_teleport_v01.py` … `v18.py` for the Sektor teleport-uppercut proof line, the first imported MKT special (`F,F + LK`). Each one is self-contained and takes only the two clean ROMs:

```bash
python3 MKMSZR_build_sektor_teleport_v08.py <clean MKMSZ USA Rev. 0 .z64> <MKT USA Rev. 2 .z64> -o MKMSZR_sektor-teleport_common-proof_v08.z64
```

They hash-guard both inputs and every patched site. All of them reproduce their issued ROMs byte-for-byte. v08 is the Runtime-confirmed bounded move. v09 adds Sektor's MKT teleport sound, which is Runtime-confirmed. v10 drops the landing thud. v11 matches MKT's juggle timing. v12–v15 import Sektor's MKT voice set (v15 accepted). v16–v18 add Sektor's MKT combos (v18 restores the late-knee frames). Identities, version changes, the proof-only footprint and known limits are in the Wiki under [Sektor takeover proof history](../../wiki/Sektor-Takeover-Proof-History.md#teleport-uppercut-proof-line-v01v08-2026-11-07). They are excluded from `ruff` like `original_builders/`. The payload arena, loader stub and descriptor replacement are Reverse Elbow v6 proof infrastructure, not production allocations.
