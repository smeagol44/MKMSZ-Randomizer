import re

import mkmszr.seed as seed_module


def test_generate_seed_is_64_bit_uppercase_hex(monkeypatch) -> None:
    monkeypatch.setattr(seed_module.secrets, "token_hex", lambda count: "ab" * count)
    value = seed_module.generate_seed()

    assert value == "AB" * 8
    assert re.fullmatch(r"[0-9A-F]{16}", value)
