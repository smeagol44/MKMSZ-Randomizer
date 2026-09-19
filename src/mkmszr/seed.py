"""Seed helpers shared by non-browser frontends."""

from __future__ import annotations

import secrets

SEED_BYTES = 8
SEED_HEX_LENGTH = SEED_BYTES * 2


def generate_seed() -> str:
    """Return a compact 64-bit seed as uppercase hexadecimal."""

    return secrets.token_hex(SEED_BYTES).upper()
