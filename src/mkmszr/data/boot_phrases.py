"""Seeded boot-screen flavor messages.

Each message is pre-wrapped for the two 19-character native text slots used by
MKMSZR's boot branding. Selection is deterministic for a given seed.
"""

from __future__ import annotations

import hashlib

BOOT_PHRASE_LINE_LIMIT = 19
DEFAULT_BOOT_PHRASE = ("DO PEOPLE EVEN READ", "THESE THINGS?")

BOOT_PHRASES: tuple[tuple[str, str], ...] = (
    ("DO PEOPLE EVEN READ", "THESE THINGS?"),
    ("THERE IS NO KNOWL.", "THAT IS NOT POWER"),
    ("ERR MACRO IS ERMAC", "IS SUB-ZERO SUERO?"),
    ("' OR 1==1 --", ""),
    ("LOREM IPSUM", "DOLOR SIT AMET"),
    ("IT'S OVER 9000!!", ""),
    ("IT'S-A ME, MARIO!", ""),
    ("PRESS F TO PAY", "RESPECTS"),
    ("IT'S MORPHIN' TIME!", ""),
    ("GO GO GADGET", "RANDOMIZER"),
    ("IT'S JUST A THEORY,", "A GAME THEORY"),
    ("1001011011", "0111000101"),
    ("FOLLOW THE WHITE", "RABBIT"),
    ("PLEASE IGNORE", "THE MONK"),
    ("THIS SEED LOOKED", "BETTER ON PAPER"),
    ("WORKS ON MY ROM", ""),
    ("TOTALLY INTENDED", ""),
    ("FEATURE, NOT A BUG", ""),
    ("NO SAVESTATES WERE", "HARMED"),
    ("WHERE'S THE KEY?", ""),
    ("CHECK EVERY CORNER", ""),
    ("TRUST THE SEED", ""),
    ("BLAME THE SEED", ""),
    ("PRAISE THE SEED", ""),
    ("SEED HAPPENS", ""),
    ("RANDOM ENOUGH?", ""),
    ("YOU WANTED RANDOM", ""),
    ("THIS WAS A CHOICE", ""),
    ("GOOD LUCK, HAVE FUN", ""),
    ("HAVE YOU TRIED", "TURNING IT OFF?"),
    ("INSERT COIN", "NOT INCLUDED"),
    ("TOASTY!", ""),
    ("FINISH HIM!", ""),
    ("GET OVER HERE!", ""),
    ("FLAWLESS VICTORY", ""),
    ("ROUND ONE", "FIGHT!"),
    ("TEST YOUR MIGHT", ""),
    ("CHOOSE YOUR DESTINY", ""),
    ("FATALITY? MAYBE.", ""),
    ("KONTINUE?", ""),
    ("NO CONTINUES LEFT", "JUST KIDDING"),
    ("THE ELDER GODS", "DID NOT APPROVE"),
    ("QUAN CHI WAS HERE", ""),
    ("SHINNOK KNOWS", "WHAT YOU DID"),
    ("SUB-ZERO PLEASE", ""),
    ("ICE TO MEET YOU", ""),
    ("STAY FROSTY", ""),
    ("COOL STORY, BRO", ""),
    ("ABSOLUTE ZERO", "ABSOLUTE CHAOS"),
    ("KEY ITEM WITH", "RESPONSIBILITIES"),
    ("TEN SLOTS WEREN'T", "ENOUGH"),
    ("BOXES WITHIN BOXES", ""),
    ("BOX 4 IS REAL", ""),
    ("GLASS IS FINE", "DON'T USE IT"),
    ("THE MAP KNOWS", "TOO MUCH"),
    ("PICKUP PERSISTED", ""),
    ("THIS ONE STICKS", ""),
    ("THE BIT IS SET", ""),
    ("CRC APPROVED", ""),
    ("CHECKSUM SAYS YES", ""),
    ("RDRAM REMEMBERS", ""),
    ("THE HEAP PROVIDES", ""),
    ("RESOURCE RESIDENT", ""),
    ("NULL POINTER?", "NOT TODAY"),
    ("SPAWN RESPONSIBLY", ""),
    ("MONK IMPORTED", ""),
    ("CROSS-STAGE CHAOS", ""),
    ("NO BIZHAWK NEEDED", ""),
    ("MUPEN SAYS HI", ""),
    ("EMULATOR AGNOSTIC", "ISH"),
    ("BIG ENDIAN ENERGY", ""),
    ("MIPS HAPPENS", ""),
    ("JAL AND BE HAPPY", ""),
    ("NOP YOUR WORRIES", ""),
    ("0X800AEE24", "WAS HERE"),
    ("PLEASE HOLD", "LOADING DESTINY"),
    ("RNGESUS TAKE", "THE CONTROLLER"),
    ("THE SEED PROVIDES", ""),
    ("UNEXPECTEDLY VALID", ""),
    ("PROBABLY SAFE", ""),
    ("WHAT COULD GO WRONG", ""),
    ("NOTHING TO SEE HERE", ""),
    ("LOOK BEHIND YOU", ""),
    ("ARE WE THERE YET?", ""),
    ("READ THE MANUAL", "OR DON'T"),
    ("SAVE OFTEN", "OH WAIT"),
    ("NO REFUNDS", ""),
    ("CERTIFIED RANDOM", ""),
    ("HANDCRAFTED CHAOS", ""),
    ("LOCALLY SOURCED RNG", ""),
    ("NOW WITH MORE BOXES", ""),
    ("NOW WITH 100% MORE", "RANDOMIZER"),
    ("SOME ASSEMBLY", "REQUIRED"),
    ("WARRANTY VOID", "IF RANDOMIZED"),
    ("DO NOT TAUNT", "THE RANDOMIZER"),
    ("THE ROM IS AWAKE", ""),
    ("THE ROM HEARS YOU", ""),
    ("YOU SAW NOTHING", ""),
    ("SECRET MESSAGE", "NOT VERY SECRET"),
    ("HELLO FROM SMEAG", ""),
    ("SMEAG WAS HERE", ""),
)


def _validate_pool() -> None:
    for first, second in BOOT_PHRASES:
        for line in (first, second):
            try:
                encoded = line.encode("ascii")
            except UnicodeEncodeError as exc:
                raise AssertionError(f"boot phrase must be ASCII: {line!r}") from exc
            if len(encoded) > BOOT_PHRASE_LINE_LIMIT:
                raise AssertionError(
                    f"boot phrase line exceeds {BOOT_PHRASE_LINE_LIMIT} chars: {line!r}"
                )


_validate_pool()


def select_boot_phrase(seed: str | None) -> tuple[str, str]:
    """Return the deterministic two-line boot phrase for *seed*.

    A missing/blank seed keeps the runtime-confirmed presentation proof phrase.
    Seeded selection uses SHA-256 instead of Python's randomized hash().
    """

    if seed is None or not seed.strip():
        return DEFAULT_BOOT_PHRASE

    digest = hashlib.sha256(
        b"MKMSZR:BOOT-PHRASE:V1\0" + seed.encode("utf-8")
    ).digest()
    index = int.from_bytes(digest[:8], "big") % len(BOOT_PHRASES)
    return BOOT_PHRASES[index]
