from pathlib import Path


def test_web_game_settings_toggles_are_wired_to_patch_config() -> None:
    html = Path("web/index.html").read_text(encoding="utf-8")
    app = Path("web/app.js").read_text(encoding="utf-8")

    for control_id in (
        "turnLock",
        "attackModern",
        "specialsModern",
        "jumpButton",
        "runAuto",
        "shufflePowerProgression",
    ):
        assert f'id="{control_id}"' in html
        assert f'querySelector("#{control_id}")' in app

    assert "GameSettingsConfig" in app
    assert "web_turn_lock" in app
    assert "web_attack_modern" in app
    assert "web_specials_modern" in app
    assert "web_jump_button" in app
    assert "web_run_auto" in app
    assert "web_shuffle_power_progression" in app
    assert "shuffle_power_progression=bool(web_shuffle_power_progression)" in app


def test_web_jump_button_dependency_is_enforced_in_ui() -> None:
    app = Path("web/app.js").read_text(encoding="utf-8")
    assert "attackModern.checked && specialsModern.checked" in app
    assert "jumpButton.disabled = !jumpAvailable" in app
