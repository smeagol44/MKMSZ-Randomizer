"""Fighter descriptions (Fighter recompiler plan, milestone 1): format, validator, packaging.

Synthetic tests always run; ROM-backed checks run when ``MKMSZR_MKT_ROM`` is set.
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import description as fd


def _raw(fighter: str) -> dict:
    return json.loads(Path(f"src/mkmszr/fighters/{fighter}.json").read_text(encoding="utf-8"))


def test_packaged_descriptions_load() -> None:
    assert fd.available() == ["reptile", "sektor"]
    sektor, reptile = fd.load("sektor"), fd.load("reptile")
    assert (sektor.donor_fighter_id, sektor.donor_name, sektor.title) == (7, "SEKTOR", "SEKTOR")
    assert (reptile.donor_fighter_id, reptile.donor_name, reptile.legacy) == (19, "REPTILE", ())
    assert sektor.body.run_slot == reptile.body.run_slot == 0x4A


def test_sektor_layout_covers_every_body_slot() -> None:
    body = fd.load("sektor").body
    assert body.layout is not None and set(body.layout.slots) == set(body.slots)
    modes = {s: sl.mode for s, sl in body.layout.slots.items()}
    assert {s for s, m in modes.items() if m == "relocated"} == {0x09, 0x12, 0x1A, 0x1B, 0x20}
    assert [s for s, m in modes.items() if m == "packed"] == [0x11]
    assert {s for s, sl in body.layout.slots.items() if sl.hybrid} == {0x0E, 0x0F, 0x14}
    assert fd.load("reptile").body.layout is None  # computed layout (milestone 1, PR 3)


def test_layout_rejects_bad_places_and_overlaps() -> None:
    data = copy.deepcopy(_raw("sektor"))
    data["body"]["layout"]["slots"]["0x09"]["place"] = "0x100"
    with pytest.raises(fd.DescriptionError, match="dead region"):
        fd.validate(data)
    data = copy.deepcopy(_raw("sektor"))
    data["body"]["layout"]["slots"]["0x1B"]["place"] = data["body"]["layout"]["slots"]["0x09"]["place"]
    with pytest.raises(fd.DescriptionError, match="overlap"):
        fd.validate(data)
    data = copy.deepcopy(_raw("sektor"))
    del data["body"]["layout"]["slots"]["0x00"]
    with pytest.raises(fd.DescriptionError, match="missing 0x00"):
        fd.validate(data)


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
