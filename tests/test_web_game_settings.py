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
        "enemyRandomization",
        "powersAsPickups",
        "requiredPowersMode",
        "customRequiredPowers",
        "difficulty",
        "startingLives",
        "startingContinues",
        "persistHp",
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
    assert "web_enemy_randomization" in app
    assert "enemy_randomization=bool(web_enemy_randomization)" in app
    assert 'id="enemyRandomization" type="checkbox"' in html
    assert 'id="powersAsPickups" type="checkbox" checked' in html
    assert "powers_as_pickups=bool(web_powers_as_pickups)" in app
    assert "required_powers_mode=str(web_required_powers_mode)" in app
    assert "custom_required_powers=int(web_custom_required_powers)" in app
    assert "resultRequiredPowers.textContent" in app
    assert 'id="difficulty"' in html
    assert '<option value="very_hard" selected>Very Hard</option>' in html
    assert 'id="startingLives" type="number" min="1" max="10" step="1" value="5"' in html
    assert 'id="startingContinues" type="number" min="0" max="5" step="1" value="3"' in html
    assert 'id="persistHp" type="checkbox" checked' in html
    assert "difficulty=str(web_difficulty)" in app
    assert "lives=int(web_lives)" in app
    assert "continues=int(web_continues)" in app
    assert "persist_hp=bool(web_persist_hp)" in app


def test_web_jump_button_dependency_is_enforced_in_ui() -> None:
    app = Path("web/app.js").read_text(encoding="utf-8")
    assert "attackModern.checked && specialsModern.checked" in app
    assert "jumpButton.disabled = !jumpAvailable" in app
