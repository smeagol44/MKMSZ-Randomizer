"""A donor fighter's MKT voice set on the MKMSZ player's voice slots (reusable component).

The rule is Sektor's accepted voice rule (proofs v12-v17, ``sektor_build`` v14 comment; Wiki
``Sounds-and-Music``) with the donor fighter as a parameter:

* MKT voice groups (arcade MK3 ``group_table``): 0 attack, 1 jump, 2 wasted, 3 grab, 4 throw voice,
  5 tripped, 6 face hit, 7 run, 8 shook, 9 death scream. ``0x800A19D4[group]`` -> ``{u16 count,
  count entries per voice group}``; the fighter's voice group is ``0x800A19FC[fighter]``.
* MKMSZ player voice table ``0x800A2EC8`` (ROM ``0xA3AC8``): 12 categories -> descriptors
  ``0x20..0x2C`` -> events 30..43. Category -> donor group: 0-1 attack effort (group 0, else the
  MKT whooshes), 2-5 stand-up hits (group 6), 6-7 launching hits (group 2), 8 jump (group 1), 9
  sweep family (group 5), 10 knockdown landing and 11 slide/special yell silent.
* MKMSZ plays one of two events for paired categories, so a group keeps every distinct donor
  sound (distinct by sample bytes; MKT has duplicate entries pointing at one waveform).

Each distinct donor sound is hosted in an isolated chain (:mod:`.sound`); the player's events
then take that donor track. Sektor's frozen build keeps its own copy of this code.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import sound

MKT_GROUP_TABLE, MKT_VOICE_GROUP = 0x800A19D4, 0x800A19FC
MKT_TRIPLE_TABLE = 0x800A1AA8  # triple 6/7: whoosh #1 / #3
PLAYER_VOICE_TABLE_ROM = 0xA3AC8
STOCK_TABLE = bytes.fromhex("00200021002700280025002600230024002c00290026002b")
CAT_EVENT = {0: 31, 1: 32, 2: 38, 3: 39, 4: 36, 5: 37, 6: 34, 7: 35, 8: 43, 9: 40, 10: 41, 11: 42}
CAT_DESC = {
    0: 0x20,
    1: 0x21,
    2: 0x27,
    3: 0x28,
    4: 0x25,
    5: 0x26,
    6: 0x23,
    7: 0x24,
    8: 0x2C,
    9: 0x29,
    10: 0x2A,
    11: 0x2B,
}


def _u16(mkt: bytes, va: int) -> int:
    return int.from_bytes(mkt[va - 0x80000000 : va - 0x80000000 + 2], "big")


def _u32(mkt: bytes, va: int) -> int:
    return int.from_bytes(mkt[va - 0x80000000 : va - 0x80000000 + 4], "big")


def groups(mkt: bytes, fighter: int) -> dict[int, list[int]]:
    """The fighter's MKT voice groups: group -> donor events (0xFFFF entries dropped)."""

    vg = _u16(mkt, MKT_VOICE_GROUP + 2 * fighter)
    out = {}
    for g in range(10):
        t = _u32(mkt, MKT_GROUP_TABLE + 4 * g)
        n = _u16(mkt, t)
        events = [_u16(mkt, t + 2 + 2 * (vg * n + k)) for k in range(n)]
        out[g] = [e & 0x7FFF for e in events if e != 0xFFFF]
    return out


@dataclass(frozen=True)
class VoiceSet:
    category: dict[int, int | None]  # MKMSZ voice category -> donor event (None: silent)
    run: int | None  # donor run voice (group 7)


def voice_set(mkt: bytes, fighter: int) -> VoiceSet:
    bank = sound.MktSoundBank(mkt)
    g = groups(mkt, fighter)

    def distinct(events: list[int]) -> list[int]:
        seen, out = set(), []
        for e in events:
            key = bank.event(e).sample
            if key not in seen:
                seen.add(key)
                out.append(e)
        return out

    def pair(events: list[int]) -> list[int | None]:
        d = distinct(events)
        return (d * 2)[:2] if d else [None, None]

    whoosh = [
        _u16(mkt, MKT_TRIPLE_TABLE + 2 * 6) & 0x7FFF,
        _u16(mkt, MKT_TRIPLE_TABLE + 2 * 7) & 0x7FFF,
    ]
    attack = distinct(g[0]) or whoosh
    face, wasted = pair(g[6]), pair(g[2])
    return VoiceSet(
        {
            0: attack[0],
            1: attack[1 % len(attack)],
            2: face[0],
            3: face[1],
            4: face[0],
            5: face[1],
            6: wasted[0],
            7: wasted[1],
            8: (g[1] or [None])[0],
            9: (g[5] or [None])[0],
            10: None,
            11: None,
        },
        (g[7] or [None])[0],
    )


def _track_rom(clean: bytes, event: int) -> int:
    return sound.host_track_rom(clean, event)


def install(
    rom: bytearray, clean: bytes, mkt: bytes, fighter: int,
    chains: tuple[sound.HostChain, ...], sample_rom: int,
) -> tuple[VoiceSet, int]:  # fmt: skip
    """Host the donor voice set and point the player's voice events at it. Returns the set and
    the next free sample address."""

    vs = voice_set(mkt, fighter)
    needed = list(dict.fromkeys(e for e in vs.category.values() if e is not None))
    if len(needed) > len(chains):
        raise ValueError(f"{len(needed)} voices need more than {len(chains)} host chains")
    bank = sound.MktSoundBank(mkt)
    donor_track: dict[int, bytes] = {}
    for event, chain in zip(needed, chains, strict=False):
        sample_rom = sound.install(rom, clean, bank.event(event), chain, sample_rom)
        t = _track_rom(clean, chain.event)
        donor_track[event] = bytes(rom[t : t + 0x20])  # the donor track, patch = the chain's
    table = b"".join(
        (CAT_DESC[c] if vs.category[c] is not None else 0).to_bytes(2, "big") for c in range(12)
    )
    if (
        bytes(rom[PLAYER_VOICE_TABLE_ROM : PLAYER_VOICE_TABLE_ROM + len(STOCK_TABLE)])
        != STOCK_TABLE
    ):
        raise ValueError("player voice table is not stock")
    rom[PLAYER_VOICE_TABLE_ROM : PLAYER_VOICE_TABLE_ROM + len(table)] = table
    for c, event in vs.category.items():
        if event is None:
            continue
        t = _track_rom(clean, CAT_EVENT[c])
        if bytes(rom[t : t + 0x20]) != clean[t : t + 0x20]:
            raise ValueError(f"player voice event {CAT_EVENT[c]} already modified")
        rom[t : t + 0x20] = donor_track[event]
    return vs, sample_rom


# One donor sound played from the body scripts (``body.script_sounds``): host callback 2 plays a
# gameplay SFX descriptor. Descriptor 0x2A (event 41) is the player voice category 10, which the
# voice rule leaves silent for MKT donors; no stock code or other descriptor plays it
# (Static-confirmed: Wiki Sounds-and-Music; descriptor scan, 2026-11-13).
SCRIPT_SOUND_DESCRIPTOR = CAT_DESC[10]
SCRIPT_SOUND_EVENT = CAT_EVENT[10]


def install_script_sound(
    rom: bytearray, clean: bytes, mkt: bytes, fighter: int, index: int,
    chain: sound.HostChain, sample_rom: int, voice_set: VoiceSet,
) -> int:  # fmt: skip
    """Host the donor fighter's ``ft_sound(index)`` in ``chain`` and point the spare descriptor's
    event at it. Returns the next free sample address."""

    if voice_set.category[10] is not None:
        raise ValueError("voice category 10 is in use; its descriptor is not spare")
    bank = sound.MktSoundBank(mkt)
    sample_rom = sound.install(rom, clean, bank.event(bank.fighter_event(fighter, index)), chain, sample_rom)
    src = _track_rom(clean, chain.event)
    dst = _track_rom(clean, SCRIPT_SOUND_EVENT)
    if bytes(rom[dst : dst + 0x20]) != clean[dst : dst + 0x20]:
        raise ValueError(f"event {SCRIPT_SOUND_EVENT} already modified")
    rom[dst : dst + 0x20] = rom[src : src + 0x20]
    return sample_rom
