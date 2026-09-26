# Historical artifact index

> **Scope:** This page routes preserved research/archive material to its current Wiki owner. It is a provenance index, not a second technical manual or current-status page.

Current technical facts are reproduced in this Wiki. The external `MKMSZR Research` collection remains the audit trail for original reports, captures, scripts, patchers, archived analysis projects, and preserved Ghidra work.

| Historical collection | What it preserves | Current Wiki owner |
|---|---|---|
| Start-here and synthesis reports | Former routing, broad cross-domain summaries, and historical decision framing | [Home](Home), [Architecture overview](Architecture-Overview), and the retired [Complete research synthesis](Complete-Research-Synthesis) |
| Core runtime/address database | Disassembly traces, bootstrap experiments, address provenance | [Core runtime and native payload](Core-Runtime-and-Address-Database), [Function registry](Function-Registry), [Address and patch-site registry](Address-and-Patch-Site-Registry), [Memory and allocation map](Memory-and-Allocation-Map) |
| Pickup/resource reports | Original callback tests, cross-stage import proofs, parser outputs, resource-materialization experiments | [Pickups and stage-local randomization](Pickups-and-Item-Randomization), [Global item materialization and solvability](Global-Item-Materialization-and-Solvability), [Stage catalogs](Stage-Catalogs) |
| Persistence/inventory handoffs | Bitset, lifecycle, key-mask, and four-box proof history | [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle) |
| UI/presentation reports | Native text/node experiments, boot/title work, screenshots, and presentation diagnostics | [Native HUD and UI](Native-HUD-and-UI), [Presentation and branding](Presentation-and-Branding), [Toasty visual research](Toasty-Visual-Research) |
| ATTACK: MODERN proof builders and ROMs | Common proof v01–v04, the SHA-verified full-composition check v01 ROM and its reproducible builder | [Player actions and special moves](Player-Actions-and-Special-Moves), [Runtime validation status](Runtime-Validation-Status) |
| Audio/Toasty reports | MKMSZ audio traces, donor selector/event mapping, waveform candidates, and disposable sound proofs | [Audio system](Sounds-and-Music), [Toasty audio research](Toasty-Audio-Research) |
| Enemy reports | Stream decompilation, constructor/resource traces, and foreign fighter import | [Enemy randomization](Enemy-Randomization) |
| Stage-flow reports | Selector, logo-bypass, and save-bypass traces | [Stage flow and selector](Stage-Flow-and-Selector) |
| MKT/Sektor reports and recovered builders | Donor asset/codec work, adapter research, animation mapping, versioned takeover proofs, exact proof identities where preserved | [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer), [MKT adapter primitives](MKT-Adapter-Primitives), [MKT fighter asset translation](MKT-Fighter-Asset-Translation), [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping), [Sektor takeover proof history](Sektor-Takeover-Proof-History) |
| PS1 reports/filesystem inventory | Executable, files, save, structure, and donor/reference analysis | [PS1 research](PS1-Research), [N64–PS1 comparison](N64-PS1-Comparison) |
| Specialist handoffs | Narrow chronological experiment detail, exact artifacts, failed branches, and supersession evidence | Owning domain plus [Experiments, failures and superseded findings](Experiments-Failures-and-Superseded-Findings) |
| Ghidra N64 archive | Reconstructed clean-ROM analysis project and exact static-analysis provenance | Relevant function/address/structure owner; preserved project remains archive evidence rather than a substitute for current Wiki conclusions |

## Provenance and supersession rule

The archive may contain older claims that are deliberately superseded by later evidence. Preserve those artifacts because they show how a conclusion was reached or corrected, but read the current Wiki owner first.

Examples:

- the corrected process/context pointer is `0x802ECE20`; older handoffs using the superseded interpretation remain provenance only;
- the player velocity helper is `0x8002B1EC`; older Reverse Elbow notes that treated projectile setup as player propulsion are historical evidence of the correction;
- older Toasty traces that identified selector slot `0x10` are superseded by the audibly confirmed slot-`0x1B` route;
- proof-only ROM/RDRAM caves and standalone footprints remain evidence of bounded experiments and do not become current production allocations merely because they worked in a disposable build.

For major chronology, use [Milestone timeline](Milestone-Timeline). For current project state use [Project status](Project-Status); for current evidence scope use [Runtime validation status](Runtime-Validation-Status).
