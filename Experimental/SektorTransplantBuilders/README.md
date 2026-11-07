# Sektor transplant builders

Experimental Python builders for the MKMSZ Sub-Zero -> MKT Sektor transplant proof lineage.

These scripts are preserved so disposable proof ROMs can be reproduced without depending on chat attachments. They are not production randomizer builders unless explicitly promoted elsewhere.

ROM inputs and generated ROM bytes must not be committed. Builders must keep clean-ROM hash guards, donor identity guards, bounded allocation checks, output CRC updates, and any version-specific static assertions used by the proof.

From v57 onward, preserve each generated `.py` builder here when a new proof ROM is issued.

## `original_builders/` (added 2026-11-07)

The 50 original builder scripts from the user-supplied `MKMSZR_sektor-investigation_build-kit_v01.zip` (SHA-256 `776b29700a7b52312e7dc00d682fcf88b74d7eada25b3250b6dd370180af4b77`), copied byte-for-byte; each file matches the kit's `SHA256SUMS.txt`. They cover takeover v53/v54 legacy, v54–v62, missiles v63–v89 (both v80 variants), Run v01–v05, the 16-colour palette proof, the P28/P29 owner probe and frame helpers.

They are preserved for provenance and are excluded from `ruff`. Most builders take a previous proof ROM as input, and several need the PS1 MKT members `CHARS1/ROBOT.DAT` and `CODE/ROBOT.BIN`. The kit's `build.py`, its `recipes.json` dependency chain, the v53/v54 recovery bridge and the 73 archival XOR replays are **not** copied here; the full kit stays in the Library. Reproduced identities and the takeover change map are recorded in the Wiki under [Sektor takeover proof history](../../wiki/Sektor-Takeover-Proof-History.md#build-kit-reproduction-and-takeover-change-map-2026-11-07).

These are disposable investigation builders, not production code. Do not apply their proof caves or allocations to production compositions.
