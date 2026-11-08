"""MKMSZ USA Rev. 0 host action ABI as assembler-level primitives.

These are the engine operations an imported special-move action is composed of.
Every function emits exactly the instruction sequence of the runtime-validated
teleport proofs (v03-v18); the semantics, evidence and rejected alternatives are
documented in the Wiki owner pages ``Player-Actions-and-Special-Moves`` (teleport
host findings) and ``Function-Registry``.

Register convention inside an action: ``s0`` = current controller, ``s1`` = its
actor, ``s4`` = target actor (after :func:`find_target`), ``s2`` = loop counter.
The action keeps a stack frame whose strike record lives at ``strike_offset``; the
collision core only accepts KSEG0 strike records, which a stack copy is.
"""

from __future__ import annotations

from dataclasses import dataclass

from .mips import Assembler

# Globals
CURRENT_CTRL = 0x802ECE20  # current controller (process) pointer
PLAYER_CTRL = 0x802C1AC0  # player controller pointer
SPECIAL_LOCK = 0x800BF308  # native special-action lock (halfword)
SOUND_PARAMS = 0x802C1188  # parameter block used by 0x80064C18

# Functions
F_SPECIAL_BEGIN = 0x80049F90  # stop, face, busy input map (uncancellable)
F_STOP = 0x8002B1C0
F_FIND_NEAREST = 0x80031D00
F_FACE = 0x80031EF0
F_ANIM_ADVANCE = 0x800304C0
F_SLEEP = 0x80028794
F_RATE_INIT = 0x80031724
F_RATE_ADVANCE = 0x8003174C
F_OFFSET = 0x80031208  # (actor, dx, dy) facing-aware, whole world units
F_STRIKE = 0x8002BA04  # (record, 0) -> 0x8000 hit / 0x4000 miss
F_EXIT = 0x800328FC  # exit action / restore control
F_INSTALL = 0x80032CD4  # install controller callback
F_CONTEXT_SWITCH = 0x8007CB84
F_WALL_DISTANCE = 0x80034C8C  # (actor, &left, &right)
F_AUDIO_A = 0x800008D4
F_AUDIO_B = 0x800008DC
F_RAW_SOUND = 0x80080A88  # (event, 0, params)
PLAYER_CONTROL_CALLBACK = 0x80038F3C
F_TRANSFER = 0x8004AA4C  # (selector): install TRANSFER_TABLE[selector] as the action root
TRANSFER_TABLE = 0x800A1050  # stock selectors 0..2; proof selectors 3+ are added by builders
TRANSFER_LIMIT_ROM = 0x4B654  # 'sltiu v0, a2, 3' bound check inside F_TRANSFER

# Sprites: the renderer emits corner offsets as texel offsets << 1 (0x800188F8, 0x8001890C),
# so one sprite pixel spans 2 world units. Donor pixel offsets convert with this factor.
UNITS_PER_TEXEL = 2

# Controller (process) fields
CTRL_ACTOR = 0x6E0
CTRL_SCRIPT_CURSOR = 0x6E4
CTRL_ACTION_ID = 0x6AA
CTRL_AIRBORNE = 0x6B2  # airborne counter; zero while airborne lets 0x80024BA8 install a fall
CTRL_GROUND = 0x6B4
CTRL_CALLBACK = 0x6F0

# Actor fields
ACTOR_GRAVITY = 0x10
ACTOR_XVEL = 0x14
ACTOR_YVEL = 0x18
ACTOR_X = 0x2C
ACTOR_Y = 0x30
ACTOR_Z = 0x34
ACTOR_ZVEL = 0x58
ACTOR_FILE_BASE = 0x98
ACTOR_PATH = 0xDC
ACTOR_PATH_PARAM = 0xE0
ACTOR_NO_GROUND_STICK = 0xF0  # suppresses the integrator's zero-gravity ground stick


def hi(address: int) -> int:
    """``%hi``: upper half adjusted for a sign-extended ``%lo``."""

    return ((address + 0x8000) >> 16) & 0xFFFF


def lo(address: int) -> int:
    """``%lo``: signed lower half."""

    low = address & 0xFFFF
    return low - 0x10000 if low & 0x8000 else low


@dataclass(frozen=True)
class Frame:
    size: int = 0x40
    strike_offset: int = 0x30


def enter_action(a: Assembler, frame: Frame, strike_words: tuple[int, ...]) -> None:
    """Allocate the action's stack frame and copy the strike record into it."""

    a.addiu("sp", "sp", -frame.size)
    for index, word in enumerate(strike_words):
        a.li("t0", word)
        a.sw("t0", frame.strike_offset + 4 * index, "sp")


def load_controller(a: Assembler) -> None:
    """``s0`` = current controller, ``s1`` = its actor."""

    a.lui("t0", hi(CURRENT_CTRL))
    a.lw("s0", lo(CURRENT_CTRL), "t0")
    a.lw("s1", CTRL_ACTOR, "s0")


def set_special_lock(a: Assembler) -> None:
    a.lui("t0", hi(SPECIAL_LOCK))
    a.li("t1", 1)
    a.sh("t1", lo(SPECIAL_LOCK), "t0")


def set_action_id(a: Assembler, action_id: int) -> None:
    a.li("t0", action_id)
    a.sh("t0", CTRL_ACTION_ID, "s0")


def special_begin(a: Assembler) -> None:
    """Native special begin: busy input map, so the action cannot be cancelled."""

    a.move("a0", "s1")
    a.jal(F_SPECIAL_BEGIN)


def set_cursor(a: Assembler, script_offset: int) -> None:
    """Point the controller's animation cursor at a fighter-file script offset."""

    a.lw("t0", ACTOR_FILE_BASE, "s1")
    a.li("t1", script_offset)
    a.addu("t0", "t0", "t1")
    a.sw("t0", CTRL_SCRIPT_CURSOR, "s0")


def start_animation(a: Assembler, script_offset: int, rate: int) -> None:
    """Cursor to the script, initialise the frame rate and show the first frame."""

    set_cursor(a, script_offset)
    a.li("a0", rate)
    a.jal(F_RATE_INIT)
    advance_animation(a)


def advance_animation(a: Assembler) -> None:
    a.move("a0", "s1")
    a.jal(F_ANIM_ADVANCE)


def sleep_tick(a: Assembler) -> None:
    a.li("a0", 1)
    a.jal(F_SLEEP)


def rate_step(a: Assembler) -> None:
    a.jal(F_RATE_ADVANCE)


def sleep_ticks(a: Assembler, count: int, label: str) -> None:
    """Sleep ``count`` ticks one at a time (counter in ``s2``)."""

    a.li("s2", count)
    a.label(label)
    sleep_tick(a)
    a.addiu("s2", "s2", -1)
    a.bnez("s2", label)


def stop(a: Assembler, actor: str = "s1") -> None:
    a.move("a0", actor)
    a.jal(F_STOP)


def face_opponent(a: Assembler) -> None:
    a.move("a0", "s1")
    a.jal(F_FACE)


def offset_actor(a: Assembler, actor: str, dx: str) -> None:
    """``0x80031208(actor, dx, 0)``: facing-aware move in whole world units."""

    a.move("a0", actor)
    a.move("a1", dx)
    a.move("a2", "zero")
    a.jal(F_OFFSET)


def in_square_range(a: Assembler, fail: str, range_units: int) -> None:
    """Fail unless |dx| and |dy| between ``s1`` and target ``s4`` are within range."""

    for field in (ACTOR_X, ACTOR_Y):
        a.lw("t0", field, "s4")
        a.lw("t1", field, "s1")
        a.subu("t0", "t0", "t1")
        a.sra("t9", "t0", 31)
        a.xor("t0", "t0", "t9")
        a.subu("t0", "t0", "t9")
        a.li("t1", range_units << 8)
        a.slt("t2", "t1", "t0")
        a.bnez("t2", fail)


def find_target(a: Assembler, fail: str, range_units: int) -> None:
    """``s4`` = nearest opponent actor on the same path and within range, else ``fail``."""

    a.jal(F_FIND_NEAREST)
    a.beqz("v0", fail)
    a.lw("s4", CTRL_ACTOR, "v0")
    a.beqz("s4", fail)
    a.lw("t0", ACTOR_PATH, "s4")
    a.lw("t1", ACTOR_PATH, "s1")
    a.bne("t0", "t1", fail)
    in_square_range(a, fail, range_units)


def strike(a: Assembler, frame: Frame, miss: str) -> None:
    """Resolve the stack strike record; branch to ``miss`` unless it connected."""

    a.addiu("a0", "sp", frame.strike_offset)
    a.move("a1", "zero")
    a.jal(F_STRIKE)
    a.andi("v0", "v0", 0xFFFF)
    a.li("t0", 0x4000)
    a.beq("v0", "t0", miss)


def play_sound(a: Assembler, event: int, player: str = "play") -> None:
    a.li("a0", event)
    a.jal_label(player)


def emit_sound_player(a: Assembler, label: str = "play") -> None:
    """Subroutine ``play(event)``: the tail of stock 0x80064C18 for {event, 0x7F, ...}, a2 0x40."""

    a.label(label)
    a.addiu("sp", "sp", -0x18)
    a.sw("ra", 0x14, "sp")
    a.sw("s0", 0x10, "sp")
    a.move("s0", "a0")
    a.li("t0", SOUND_PARAMS)
    a.li("t1", 0xB)
    a.sw("t1", 0, "t0")
    a.li("t1", 0x7F)
    a.sb("t1", 4, "t0")
    a.li("t1", 0x40)
    a.sb("t1", 5, "t0")
    a.sh("zero", 8, "t0")
    a.jal(F_AUDIO_A)
    a.jal(F_AUDIO_B)
    a.move("a0", "s0")
    a.move("a1", "zero")
    a.li("a2", SOUND_PARAMS)
    a.jal(F_RAW_SOUND)
    a.jal(F_AUDIO_A)
    a.jal(F_AUDIO_B)
    a.lw("ra", 0x14, "sp")
    a.lw("s0", 0x10, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x18)


def exit_action(a: Assembler, hang: str = "hang") -> None:
    """Leave through the native restore, then the proven v6 fallback (never returns)."""

    a.sh("zero", CTRL_AIRBORNE, "s0")  # never exit through the airborne fall reaction
    a.move("a0", "s1")
    a.jal(F_EXIT)
    a.lui("t0", hi(CURRENT_CTRL))
    a.lw("s0", lo(CURRENT_CTRL), "t0")
    a.lui("t1", hi(PLAYER_CONTROL_CALLBACK))
    a.addiu("t1", "t1", lo(PLAYER_CONTROL_CALLBACK))
    a.sw("t1", CTRL_CALLBACK, "s0")
    a.move("a0", "s0")
    a.move("a1", "t1")
    a.jal(F_INSTALL)
    a.addiu("a0", "s0", 8)
    a.jal(F_CONTEXT_SWITCH)
    a.label(hang)
    a.beq("zero", "zero", hang)


def emit_transfer_thunk(a: Assembler, label: str, selector: int) -> None:
    """Descriptor action: ``F_TRANSFER(selector)``, entered at its KSEG0 address.

    A plain ``j`` from a KSEG1 payload would reach the uncached alias of the shim;
    ``jr`` keeps the stock KSEG0 entry.
    """

    a.label(label)
    a.lui("t9", hi(F_TRANSFER))
    a.addiu("t9", "t9", lo(F_TRANSFER))
    a.jr("t9")
    a.addiu("a0", "zero", selector)
