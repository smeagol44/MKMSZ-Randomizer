# Fighter recompiler — inventory of Sektor-specific items

> **Scope:** milestone 1 inventory for the [Fighter recompiler plan](Fighter-Recompiler-Plan) (progress: [status](Fighter-Recompiler-Status)). It lists every fighter- or move-specific item in the importer and the production fighter patch as of `main` at `8478fdb` (2026-11-10), and says where each one goes. It is the checklist that milestone 1 (generic body builder) and milestone 5 (generic product integration) work through; update an item's **Now** column when it moves.

## Classes

| Class | Meaning | Goes to |
|---|---|---|
| **D** | Fighter data: a choice that differs per fighter | the fighter description (`src/mkmszr/fighters/<id>.json`) |
| **G** | Generic logic, or a host (MKMSZ) fact that holds for every fighter | the generic builder/backend |
| **F** | A donor (MKT) fact | the donor reader (`mkt_fighter.py`) or a registry |
| **L** | Sektor's move code or move assets | frozen legacy (plan rule 4), referenced from Sektor's description |
| **O** | Proof-era or duplicate, not needed by production | removed when the builder is split |

**Generic rule found during the inventory (Static-confirmed, 2026-11-10).** For every mapped body slot `0x00..0x22` except `0x0D` and `0x10`, Sektor's slot table takes the donor script at MKT table 0 index *i* and writes it to the host script at MKMSZ table 0 index *i* (all 33 entries checked against the MKT and clean MKMSZ tables). The per-slot `donor`/`target` offsets in `sektor_build.py` are therefore derived values, not data. MKT idle scripts start with a fighter-ID branch (token 8), already folded by `translate.py`; Sektor's explicit idle words are that folded result.

## `fighter_import/sektor_build.py`

| # | Item (lines as of `8478fdb`) | Class | Note |
|---|---|---|---|
| 1 | Clean and MKT ROM hash asserts | G | Validation already in `RomImage` / `validate_mkt_n64_rev2` |
| 2 | `MB` robot heap `0x8881C0`, `ROBO_DICT` `0x906A90` | F | `MktRom.heap/dictionary(fighter_id)` |
| 3 | `ORIG_FILE87_ROM`, `CLEAN_SIZE`, `TYPE_START`/`TYPE_END`, `PALETTE_OFF` | G | Host file-`0x87` layout |
| 4 | Staging addresses `RR 0xF40000`, `PAYLOAD_ROM 0xF10000`, `SOUND_ROM 0xF20000` | G / O | Build-internal staging in the 16 MiB image, moved by the v49 placement; the generic builder writes the final layout directly |
| 5 | `SAFE_V49` budget | G | Fighter-file budget limit |
| 6 | `SEKTOR_PALETTE32`, `SEKTOR_PALETTE16`, `MAP32TO16` | D | Colour policy (16-colour palette and index map) |
| 7 | `BitReader`/`BitWriter`, `dec_15`, `dec_22_24` (codec 23 branch untested), `make_blocks`, `donor_frame`, `visible_rows` | G | Donor decoding; codec 23 is milestone 1 work |
| 8 | `MECARM_RGBA5551`, `ARM_TO_SEKTOR`, `composite()` | L (D for parameters) | Robot throw arm flattened onto the body; the flattening itself is reusable for multi-part frames |
| 9 | `slot_cfg` slots `0x00..0x22`: `donor`, `target`, `n`, `mode` | G (+D) | Derived by the rule above; `n` from the donor script, `mode` from host capacity. Slot exclusions (`0x0D`, `0x10`) are generic |
| 10 | Idle `words` override | G | Folded token-8 branch |
| 11 | `RUN_RELS` | G (+D) | MKT table 0 slot `0x4A` frames for every fighter; Run rate (3) is a rule from the cadence calibration |
| 12 | `COMBO_RELS` (`RBELBOCOMBO1..10`) and the elbow-combo script (`COMBO_TARGET`, `combo_visual_pos`, `combo_seq`) | D | Per-fighter combo presentation |
| 13 | `KNEE_LATE_MAP` | D | Sektor's combo-selector parts 3–5 |
| 14 | `BODY_REL`, `ARM_RELS`, throw script (`THROW_TARGET`, `throw_visual_pos`, `throw_sequence`) | L | Robot arm throw; other fighters use MKT slot `0x23` (milestone 1 decides the generic throw rule) |
| 15 | `TELE_RELS`, `CHEST_RELS`, `EMPTY_KEY` | L | Teleport and rocket assets |
| 16 | `FLIP_RELS` | G | MKT slot `0x47` phase 1 (generic grabbed recipe) |
| 17 | Entropy groups (58 inherited + 4 Run + Throw + Combo = 64) and the pattern order priority | G (+D) | Mechanism generic; Sektor's grouping is kept as description data where byte identity needs it |
| 18 | `best_partition`, `zero_plan`, stream and table encoding, `decode_generated` verifier | G | Type-5 encoder and checker |
| 19 | Debug stage-menu mapper/table, selection load, boot-logo skip, max-EXP caps, file `0x1B`, arena prefix and loader hook | O | Proof infrastructure, dropped by `fighter_swap.py` |
| 20 | Stock-shape scan, stock reference positions, fallback redirect to stance | G | |
| 21 | `dead_regions`, `redirect_slots`, `script_targets`, `capacity`, `hybrid_slots` | G | Script placement and capacity; to be computed, not listed (hybrid rule to be confirmed in milestone 1) |
| 22 | Item packer (knapsack) and append area | G | |
| 23 | Push script from Run poses | G | Generic fallback recipe (MKT has no push) |
| 24 | Run script and Run-rate edit `0x2F7A0` (`2 → 3`) | G | |
| 25 | `v53_path` cross-check | O | Disabled |
| 26 | Teleport scripts, aliases, depths, `TeleportParams`, strike words, `TELE_EVENT` | L | |
| 27 | Rocket art (`ROCKETD1/D2`, `ROCKET_P`), flight loop, smoke and explosion, tracker direction art and crosshair | L | Uses generic `projectile.py` and `effects.py` |
| 28 | `DEFAULT_CACHED_CALLS = True` | G | Code-generation policy for imported code |
| 29 | `knee_rec` combo record and the combo graph edit `0xB1CB0`, knee root `0xA1CE8` | D | Combo strings |
| 30 | Ice re-host (lifted callback and root with patches), trap stumble, hit child, straight helper, speed table, strike record, zap script words `+0xD90…`, chest words | L | |
| 31 | Selector bound `0x4B654`, transfer table `0xA1C5C/60` | G (+L values) | Move dispatch backend; entries point at legacy code today |
| 32 | Command records: LK teleport, LP straight, LP double, HP homing | L | Become move-program commands later |
| 33 | `sektor_tiers.stock_edits` | D (+G) | Progression decisions; mechanism generic |
| 34 | Donor sound install for the teleport event (`SOUNDS`) | L | |
| 35 | Voice rule (MKT voice groups → MKMSZ categories), `HOST_POOL`, `CAT_EVENT`, `CAT_DESC`, `SZ_TABLE_ROM` | G | Already data-driven by fighter id; Sektor asserts become tests |
| 36 | `WHOOSH` triples | F | |
| 37 | Rocket, tracker and throw sounds | L | |
| 38 | Strike selector `0x13` repoint, reaction `0x23` repoint | L | |
| 39 | v48 relocation link passes, stock references, jal sites, fixed loader | G | |
| 40 | `common_moves.apply`, companion frame (`attachment`) | G | |
| 41 | v49 placement (`0x01820000`, samples) and manifest | G | Placement owned by the [memory map](Memory-and-Allocation-Map) |
| 42 | Inline CIC-6102 CRC | O | Duplicate of `checksum.py` |

## Other modules

| Module | Item | Class | Note |
|---|---|---|---|
| `patches/fighter_swap.py` | `TRANSPLANT_SITES`, `TRANSPLANT_RANGES`, `DERIVED_SITES`, `DROP_SITES`, `DROP_RANGES` | G (lists D) | Milestone 5: generated from the build manifest |
| `patches/fighter_swap.py` | `FIXED_VA`, pool and tail bounds | G | Host allocation facts |
| `patches/fighter_swap.py` | Calls to help, icons, outfit | D | Driven by the description |
| `fighter_import/power_help.py` | `SEKTOR_HELP` | D | Mechanism generic |
| `fighter_import/power_icons.py` | `_sektor_icons` recipe, Sektor/rocket/target palette addresses, `EMERGE_2` | D | Icon recipe per fighter; mechanism generic |
| `fighter_import/outfit.py` | `RED_ENTRIES` | D | Recolour entries per fighter |
| `fighter_import/actions/sektor_tiers.py` | Costs, slot mapping, condition emitters | D (+G) | |
| `fighter_import/actions/robo_*.py` | Teleport, rockets, tracker, throw sounds | L | |
| `fighter_import/mkt_fighter.py` | `ROBOT_HEAP_ROM`, `SEKTOR` | F | Convenience constants |
| Others (`script`, `translate`, `mkmsz_fighter`, `host`, `mips`, `lifter`, `relocate`, `physics`, `projectile`, `effects`, `sound`, `attachment`, `common_moves`) | — | G | No fighter-specific data found |
