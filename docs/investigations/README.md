# Rich Inventory audio pair, 2026-10-08

Canonical report: [upstream investigation](../../wiki/Production-Rich-Inventory-Music-Static-Investigation.md).
Earlier evidence and superseded retry: [initial static manifest](../../wiki/Production-Rich-Inventory-Music-Initial-Static-Manifest.md).

`inventory_audio_pair_measurements_v01.json` contains ROM-free decoded measurements from the two maintainer-supplied states. No ROM, raw RAM or PCM is included.

Reproduce with local legally obtained copies of the exact existing diagnostic ROM and states:

```bash
python3 tools/inventory_audio_pair_audit.py \
  test_musicnormal.state test_musicspeedup.state \
  MKMSZR_inventory-audio-trace_fortress_proof_v01.z64 \
  --output inventory_audio_pair_measurements_v01.json
```

The stdlib-only script reads inputs, verifies the diagnostic SHA/embedded state MD5/code/log/clock/layout guards, and writes measurements. It never runs an emulator or writes a ROM. Actual uploaded filenames have `(1)` suffixes; the JSON preserves them. The normal/accelerated ordering is required. Endpoint values do not establish event chronology; output limitations are part of the result.
