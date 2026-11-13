"""The web "Swap character" window is wired to the fighter option and the worker."""

from pathlib import Path


def test_fighter_swap_is_wired() -> None:
    html = Path("web/index.html").read_text(encoding="utf-8")
    app = Path("web/app.js").read_text(encoding="utf-8")
    worker = Path("web/patch-worker.js").read_text(encoding="utf-8")

    for control_id in ("swapFighterButton", "fighterName", "fighterDialog", "fighterCanvas"):
        assert f'id="{control_id}"' in html
        assert f'querySelector("#{control_id}")' in app
    # Disabled until a validated MKT donor exists.
    assert 'id="swapFighterButton" class="secondary-action compact-action" type="button" disabled' in html
    assert 'donorValidation.state === "valid"' in app
    # The chosen fighter reaches RandomizerConfig and the donor bytes reach patch_rom.
    assert "fighter: selectedFighter" in app
    assert "fighter=str(web_fighter)" in worker
    assert "fighter_donor=_mkt_bytes if _config.fighter != 'sub-zero' else None" in worker
    # The select screen is decoded from the user's donor in the worker.
    assert '"select-screen"' in app and '"select-screen"' in worker
    assert "from mkmszr.donors.mkt_select_screen import render" in worker
    # The title character follows the fighter unless the user typed their own.
    assert 'const FIGHTER_TITLES = { "sub-zero": "SUB-ZERO", sektor: "SEKTOR", reptile: "REPTILE" };' in app
    # Every fighter offered has an outfit recolour; one without would lock it to Vanilla.
    assert 'const OUTFIT_FIGHTERS = ["sub-zero", "sektor", "reptile"];' in app
    assert "outfitMode.disabled = outfitLocked" in app
    # Imported fighters lock SPECIALS to CLASSIC.
    assert "specialsModern.disabled = imported" in app
