# Wind portraits, stage XP limits and debug starting keys

Implementation/static-confirmed candidate, 2026-10-27. Runtime validation is
Pending. Do not merge/deploy until the bounded manual check below passes.
No emulator was run by the assistant.

## Changes

- Wind file-`0x7E` portrait order is circle / three bars / triangle for
  `WIND1/2/3` (item IDs `0x0E/0x0F/0x10`). Water order is preserved.
- Powers-as-pickups OFF now removes stage-specific XP limits using the same
  guarded cap-table edits as ON. All ten native stage entries read `20000`,
  the existing overall maximum. Combat XP stores, combo XP display, progression
  thresholds, earned-XP persistence and the independent Fortress gate remain
  unchanged in OFF mode.
- The final browser settings group is **Debug options**, with an unchecked
  **Start with all stage keys** checkbox. It adds all 21 stage credentials,
  including Fortress crystals, alongside Herbs/Herbs/Potion. Temple Map is
  excluded. CLI equivalent: `--debug-all-keys`.
- Slots 0..2 are supplies, 3..23 are keys `0x0E..0x22`, 24..39 are empty.
  Debug OFF retains normal starter contents. The debug setting does not change
  world rewards, checks collected, powers, checkpoint state or seed acceptance.
- The pre-stage LIVE view uses inert placeholders for box-1 debug key slots;
  filtered commits therefore cannot erase keys before stage reconstruction.
  Normal stage masking and box switching apply after entry.
- Genuine final Game Over restores the configured starter set. Debug reset
  replaces only lifecycle module `+0x500..+0x53F`, within its existing allocation.
  The early source at ROM `0xF69740..0xF6977F` is also copied by the existing
  Inventory-menu transport to final ROM `0x1817740..0x181777F`.
  Runtime VA is `0x801B0F60..0x801B0F9F` (uncached execution alias).
  No new hook, callback, stack frame or allocation is introduced.

## Reproduction

Base: main `65ca8f5838bc86f0af564b7a87f2aaa64e256af2` plus this change.
Use the supported clean 16 MiB USA Rev. 0 ROM, SHA-256
`9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`.
Keep that input untouched and build to a separate path:

```bash
PYTHONPATH=src python -m mkmszr.cli clean.z64 \
  MKMSZR_keys-xp-debug_all-stages_proof_v01.z64 \
  --seed ICONXPDEBUG01 --no-powers-as-pickups --debug-all-keys \
  --lives 1 --continues 0
```

Other proof settings: Very Hard, Persistent HP ON, vanilla outfit and power
order, stock Fortress requirement, enemies vanilla, all controls classic,
All 85 available completion, no MKT donor. One life and zero continues make
the final-reset check short; they are proof configuration, not new defaults.

Proof identity (32 MiB generated output):

- SHA-256: `7129c455a29f736c77bb06b6a34d5695326f6eae48981b2a82a8739e47bc8465`
- CRC1 / CRC2: `4D2B66FA / 89A89E6C`
- Accepted global attempt index: `2` (zero-based).
- Source/output SHA checks, re-read equality, N64 CRC verification, all ten
  cap-table values and unchanged OFF combat XP/combo render instructions pass.

## Bounded manual check

Use a fresh boot of this ROM, without an older savestate.

1. Enter Wind. Open Inventory and confirm `WIND2` shows Three Bars and `WIND3`
   shows Triangle. Switch through all four boxes: 24 occupied backing slots
   total (three supplies plus 21 keys/crystals), with foreign-stage keys SEALED
   and box 4 empty. Do not expect all foreign key portraits to be visible in Wind.
2. Re-enter another stage, such as Water or Fortress. Its three credentials
   should become real items; Wind keys should become SEALED. Switching boxes
   and Pause → Quit → re-entry must retain them.
3. In Temple, earn combat XP beyond its former **260** cap. Confirm it continues
   increasing and earned XP/powers survive Pause → Quit → re-entry. Other main
   stages have the same common-maximum table values, statically checked.
4. Trigger genuine final Game Over (the proof has one life, no continues).
   Start again: keys/crystals and normal supplies must be restored across the
   same boxes, while XP and collected-check progress reset normally. It must
   not re-grant keys on an ordinary stage transition or Pause → Quit.

Existing unresolved audio behavior remains a separate release gate; this
candidate makes no audio correction or new audio claim.

## Static checks

The full existing suite plus focused regression tests cover portrait mapping,
default-OFF config/worker wiring, starter layout, title-time filtered-save
protection, both modes' cap guards, and normal/debug reset instruction semantics
(including branch delay slots, termination and stores restricted to 40 backing
words). Python compile and browser JavaScript syntax checks pass.

Whole-repository Ruff reports three existing findings already present at the
base commit: EXE001 in `tools/inventory_audio_pair_audit.py`, and EXE001/RUF007
in `tools/inventory_audio_phase_compare.py`. Changed Python source/tests pass
Ruff. These unrelated scripts were left unchanged.

An otherwise-identical debug-OFF build has the same accepted attempt and world
layout. An exhaustive 32 MiB byte comparison finds exactly **202 differing
bytes**, all within header CRC `[0x10,0x18)`, LIVE initializer
`[0xA6C0C,0xA6C34)`, backing inventory `[0xA6C48,0xA6CE8)`, the early reset
block `[0xF69740,0xF69780)` and its final transport copy
`[0x1817740,0x1817780)`. **Zero unexplained differences.** Settings/magic,
all resource allocations, pickups, solver/layout, HUD data and hooks are
byte-identical between these debug ON/OFF controls.
