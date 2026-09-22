# Sounds & Music

This page owns MKMSZR research on the N64 game's sound-effect and music systems. The current scope is intentionally narrow: native gameplay SFX playback is partially mapped; music sequencing, sound-bank structure, sample compression/encoding, and foreign-sound import are still pending.

## Current status

| Area | Status | Evidence and limit |
|---|---|---|
| Gameplay SFX wrapper | **Static-confirmed** | `0x80064C18` is called widely by stock gameplay code and resolves a table entry before native playback |
| SFX descriptor table | **Static-confirmed** | 10-byte entries beginning at VA `0x800A1730` / ROM `0x000A2330` |
| Raw sound-ID playback | **Static-confirmed** | `0x80080A88` receives the resolved raw sound/sample ID and selects a runtime sound definition |
| Low-level voice allocation/start | **Static-confirmed** | `0x8007EC4C` consumes the resolved runtime definition |
| Ordinary-pickup SFX example | **Static-confirmed** | stock pickup callbacks use descriptor index `0x3B`, resolving to raw sound ID `0x020C` |
| Music engine / sequence format | **Pending** | not yet mapped |
| ROM sound-bank/sample format | **Pending** | not yet decoded |
| Importing an MKT sound into MKMSZ | **Pending** | no compatibility claim yet |
| Runtime custom-sound proof | **Pending** | no MKMSZR-authored sound call has yet been runtime-tested |

## Native gameplay SFX path

The currently mapped host path is:

```text
gameplay caller
    |
    | descriptor index
    v
0x80064C18  native gameplay SFX wrapper
    |
    | 10-byte descriptor from 0x800A1730
    v
0x80080A88  raw sound-ID playback entry
    |
    | resolved 16-byte runtime sound definition
    v
0x8007EC4C  low-level definition / voice allocator
```

The wrapper at `0x80064C18` is a general gameplay facility rather than a one-off effect path. Static call-site scanning finds hundreds of direct uses in the clean USA Rev. 0 ROM, including ordinary pickup callbacks.

## SFX descriptor table

The descriptor table begins at:

- VA `0x800A1730`
- ROM `0x000A2330`

Each entry is exactly 10 bytes:

| Offset | Size | Meaning | Status |
|---:|---:|---|---|
| `+0x00` | 2 | native raw sound/sample ID | **Static-confirmed** |
| `+0x02` | 1 | high byte not consumed by the mapped wrapper path | **Static-confirmed observation; semantic meaning pending** |
| `+0x03` | 1 | base primary sound parameter | **Static-confirmed** |
| `+0x04` | 2 | random variation magnitude for the primary parameter | **Static-confirmed** |
| `+0x06` | 2 | base secondary parameter | **Static-confirmed** |
| `+0x08` | 2 | random variation magnitude for the secondary parameter | **Static-confirmed** |

The random-variation helper used by this path is `0x80015FD8`. Static analysis shows it produces a roughly symmetric signed variation around the supplied base value. Exact gameplay semantics for the two parameters are not yet named; do not label them as volume, pitch, pan, or another conventional audio property until caller/runtime evidence establishes that meaning.

## Worked stock example: ordinary pickup sound

Several stock pickup callbacks call:

```text
a0 = 0x3B
a1 = 0
a2 = 0x40
jal 0x80064C18
```

Descriptor `0x3B` is located at ROM `0x000A257E` and contains:

```text
02 0C 00 7F 00 00 00 00 00 00
```

Decoded through the currently mapped structure:

- raw sound ID: `0x020C`
- primary base parameter: `0x7F`
- primary variation: `0`
- secondary base parameter: `0`
- secondary variation: `0`

This is the current reference control for future custom-SFX experiments because the full stock route from gameplay event to native playback is known.

## Function registry

Canonical function entries are maintained in [Function registry](Function-Registry):

| Address | Meaning |
|---:|---|
| `0x80064C18` | native gameplay SFX wrapper |
| `0x80080A88` | raw sound-ID playback entry |
| `0x8007EC4C` | low-level sound-definition / voice allocator |
| `0x80015FD8` | random-variation helper used by the SFX wrapper |

This page owns the audio-system explanation; the registry remains the compact address index.

## MKT donor evidence relevant to Toasty

Midway's preserved MKT/MK3 source identifies the Toasty voice through donor sound-table entry `0x1B`, which resolves to donor sound call/sample identifier `0x1095` and is described as Dan Forden's “Toasty”.

This is **donor-side static evidence only**. Numeric sound IDs are game-local unless compatibility is demonstrated. The project must not assume that donor `0x1095` can be passed directly to MKMSZ, just as donor strike/reaction indices cannot be assumed to retain their numeric meaning across games.

The next bounded Toasty-audio task is therefore:

1. locate the retail MKT N64 sample/bank data behind donor identifier `0x1095`;
2. determine the MKT N64 sound-definition and sample-storage grammar used by that entry;
3. compare it with MKMSZ's `0x80080A88 -> 0x8007EC4C` runtime definition path;
4. decide whether the voice can be copied directly, repacked into an MKMSZ-native definition/bank, or requires sample conversion;
5. identify conflict-free ROM/RAM ownership for a disposable proof.

No direct-import compatibility is claimed until that comparison is complete.

## Music

**Pending.** No current MKMSZR research establishes the N64 music sequence format, track table, streaming model, bank ownership, or runtime music-control API. Sound effects and music should therefore remain separate research tracks until evidence shows which lower-level components they share.

## Safety and implementation boundary

For a future custom-sound proof:

- keep the clean ROM untouched and build a separate guarded output;
- guard all edited table entries and storage ranges;
- do not overwrite an existing sound/sample solely because its numeric ID looks unused;
- resolve ROM offsets versus runtime pointers and any bank-relative addressing before patching;
- preserve existing voice/channel behavior unless the experiment specifically targets it;
- treat donor IDs and definitions as semantic references, not binary-compatible records;
- perform a bounded manual runtime test before integrating any new audio path into the normal pipeline.

A successful call to an existing MKMSZ sound does **not** by itself prove that foreign-sample import is safe; the sample/bank format and lifetime must be validated separately.
