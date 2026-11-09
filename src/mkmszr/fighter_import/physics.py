"""Donor (MKT) to host (MKMSZ) motion units.

The two engines integrate differently: MKT runs at 60 Hz with ``y += vel`` and
``vel += grav`` in 16.16, while MKMSZ runs at 30 Hz with ``vel += 2*grav`` and
``y += (vel >> 8) + (vel >> 7)``. Rather than deriving a pixel scale, velocities and
accelerations are calibrated by the same semantic action in both games: the
standard jump (donor ``0x8006EC50(-0x88000, 0x6CCC)``, host ``0x800321D0(-0xB47AE,
0x7851)``). Teleport proof v01 used an assumed pixel ratio and was rejected.

Converted arcs keep the jump's proportions, which makes them 1.2x longer in real
time than the donor's (the MKMSZ jump is). Where real-time timing matters, scale
an arc with :func:`retime` rather than changing the calibration.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

DONOR_JUMP_VEL = 0x88000
DONOR_JUMP_GRAV = 0x6CCC
HOST_JUMP_VEL = 0xB47AE
HOST_JUMP_GRAV = 0x7851

VEL_RATIO = HOST_JUMP_VEL / DONOR_JUMP_VEL
GRAV_RATIO = HOST_JUMP_GRAV / DONOR_JUMP_GRAV

DONOR_HZ = 60
HOST_HZ = 30


def convert_velocity(donor: int) -> int:
    return int(donor * VEL_RATIO)


def convert_acceleration(donor: int) -> int:
    return int(donor * GRAV_RATIO)


def donor_airtime_seconds(velocity: int, gravity: int) -> float:
    """Up-and-down airtime of a donor arc (``vel += grav`` per 60 Hz tick)."""

    return 2 * velocity / gravity / DONOR_HZ


def host_airtime_seconds(velocity: int, gravity: int) -> float:
    """Up-and-down airtime of a host arc (``vel += 2*grav`` per 30 Hz tick)."""

    return 2 * velocity / (2 * gravity) / HOST_HZ


def retime(velocity: int, gravity: int, scale: float) -> tuple[int, int]:
    """Same apex (``v^2/g``), airtime multiplied by ``scale``."""

    return int(velocity / scale), int(gravity / scale**2)


# ---- Projectile speeds and frame cycles (60 Hz donor -> 30 Hz host) -------------
# Host actor integrator 0x80017F80: fixed8 position += 3 * (velocity >> 8) per host
# update, i.e. 3 * velocity / 65536 world units. A donor 16.16 speed d moves d / 65536
# sprite pixels per donor tick. One host tick covers two donor ticks.
HOST_INTEGRATION_FACTOR = 3


def fold_donor_speeds(
    start: int, cap: int, step: Callable[[int], int], units_per_px: int
) -> list[int]:
    """Host per-tick speed magnitudes for a donor speed recurrence, ending at the cap.

    Host tick k carries donor ticks 2k and 2k+1: ``units_per_px * (d_a + d_b) // 3``.
    The last entry is the steady capped speed.
    """

    seq = []
    d = start
    while True:
        first = d
        d = min(step(d), cap)
        second = d
        d = min(step(d), cap)
        seq.append(units_per_px * (first + second) // HOST_INTEGRATION_FACTOR)
        if first == cap and second == cap:
            return seq


def resample_frame_cycle(frames: Sequence[int], donor_ticks_per_frame: int) -> list[int]:
    """Host per-tick frame list for a looping donor animation (one frame per host tick).

    A host tick spanning two donor frames alternates between them, so each frame keeps
    its donor share of screen time over the returned (whole) cycle.
    """

    donor_period = len(frames) * donor_ticks_per_frame
    host_period = donor_period if donor_period % 2 else donor_period // 2
    out: list[int] = []
    tie = 0
    for k in range(2 * host_period):
        a = frames[(2 * k // donor_ticks_per_frame) % len(frames)]
        b = frames[((2 * k + 1) // donor_ticks_per_frame) % len(frames)]
        if a == b:
            out.append(a)
        else:
            out.append(a if tie % 2 == 0 else b)
            tie += 1
    half = len(out) // 2
    return out[:half] if out[:half] == out[half:] else out
