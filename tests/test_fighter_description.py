"""Fighter descriptions (Fighter recompiler plan, milestone 1): format, validator, packaging.

Synthetic tests always run; ROM-backed checks run when ``MKMSZR_MKT_ROM`` is set.
"""

from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path

import pytest

from mkmszr.fighter_import import description as fd

BUILD = Path("src/mkmszr/fighter_import/sektor_build.py").read_text(encoding="utf-8")


def _raw(fighter: str) -> dict:
    return json.loads(Path(f"src/mkmszr/fighters/{fighter}.json").read_text(encoding="utf-8"))


def test_packaged_descriptions_load() -> None:
    assert fd.available() == ["reptile", "sektor"]
    sektor, reptile = fd.load("sektor"), fd.load("reptile")
    assert (sektor.donor_fighter_id, sektor.donor_name, sektor.title) == (7, "SEKTOR", "SEKTOR")
    assert (reptile.donor_fighter_id, reptile.donor_name, reptile.legacy) == (19, "REPTILE", ())
    assert sektor.body.run_slot == reptile.body.run_slot == 0x4A


def test_sektor_description_matches_the_build_constants() -> None:
    """Until milestone 1 moves them, the description must equal sektor_build.py's literals."""

    body = fd.load("sektor").body
    block = BUILD[BUILD.index("slot_cfg = {") : BUILD.index("    for cfg in slot_cfg.values()")]
    assert list(body.slots) == [int(x, 16) for x in re.findall(r"^\s+(0x[0-9A-F]+): dict", block, re.MULTILINE)]
    index_map = re.search(r"MAP32TO16=\[([0-9,]+)\]", BUILD).group(1)
    assert list(body.colour.index_map) == [int(x) for x in index_map.split(",")]
    p16 = re.search(r"SEKTOR_PALETTE16=bytes\.fromhex\('([0-9a-f]+)'\)", BUILD).group(1)
    p32 = "".join(re.findall(r"'([0-9a-f]{64})'", BUILD[BUILD.index("SEKTOR_PALETTE32") :])[:2])
    assert body.colour.palette == bytes.fromhex(p16) + bytes.fromhex(p32)[32:]
    assert re.search(r"RUN_RATE_ROM\+4\] = bytes\.fromhex\('24040003'\)", BUILD)  # host Run rate 3


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda d: d.pop("donor"), "donor"),
        (lambda d: d.update(id="Sektor"), "id"),
        (lambda d: d.update(title="SEKTOR-THE-ROBOT"), "title"),
        (lambda d: d["donor"].update(fighter_id=40), "fighter_id"),
        (lambda d: d["body"]["slots"].append("0x00"), "duplicate"),
        (lambda d: d["body"]["slots"].append("zz"), "hex"),
        (lambda d: d["body"]["run"].update(host_rate=0), "host_rate"),
        (lambda d: d["body"]["colour"].update(index_map_32_to_16=[1] * 32), "transparent"),
        (lambda d: d["body"]["colour"].update(palette_bgr555="00"), "palette_bgr555"),
        (lambda d: d["body"]["colour"].update(method="guess"), "method"),
        (lambda d: d["body"]["common_animations"].append("fly"), "fly"),
        (lambda d: d["legacy"].append("reptile-acid"), "legacy"),
        (lambda d: d.update(moves=[]), "unknown keys"),
    ],
)
def test_validator_rejects(change, message) -> None:
    data = copy.deepcopy(_raw("sektor"))
    change(data)
    with pytest.raises(fd.DescriptionError, match=message):
        fd.validate(data)


def test_validator_reports_every_problem_at_once() -> None:
    data = copy.deepcopy(_raw("sektor"))
    data["title"] = ""
    data["body"]["run"]["host_rate"] = 99
    with pytest.raises(fd.DescriptionError) as err:
        fd.validate(data)
    assert "title" in str(err.value) and "host_rate" in str(err.value)


MKT = os.environ.get("MKMSZR_MKT_ROM")


@pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")
def test_donors_and_the_same_index_slot_rule() -> None:
    from mkmszr.fighter_import.mkt_fighter import MktRom

    mkt = Path(MKT).read_bytes()
    reader = MktRom(mkt)
    for fighter in fd.available():
        description = fd.load(fighter)
        fd.check_donor(description, mkt)
        table0 = reader.table0(description.donor_fighter_id)
        assert all(table0[slot] for slot in description.body.slots), fighter  # a donor script per slot
        assert table0[description.body.run_slot]
    wrong = fd.validate({**_raw("sektor"), "donor": {**_raw("sektor")["donor"], "fighter_id": 6}})
    with pytest.raises(fd.DescriptionError, match="SINDEL"):
        fd.check_donor(wrong, mkt)
