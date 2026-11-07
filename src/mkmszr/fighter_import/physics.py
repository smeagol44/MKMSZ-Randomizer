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
