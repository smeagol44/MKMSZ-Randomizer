from pathlib import Path


def test_web_game_settings_toggles_are_wired_to_patch_config() -> None:
    html = Path("web/index.html").read_text(encoding="utf-8")
    app = Path("web/app.js").read_text(encoding="utf-8")
    worker = Path("web/patch-worker.js").read_text(encoding="utf-8")

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
        "globalCompletionMode",
        "customRequiredPowers",
        "difficulty",
        "startingLives",
        "startingContinues",
        "persistHp",
    ):
        assert f'id="{control_id}"' in html
        assert f'querySelector("#{control_id}")' in app

    # The main thread collects UI values and posts a plain config object to the
    # patch worker; the worker owns the Pyodide/Python RandomizerConfig wiring.
    for config_key in (
        "turnLock",
        "attackModern",
        "specialsModern",
        "jumpButton",
        "runAuto",
        "shufflePowerProgression",
        "enemyRandomization",
        "powersAsPickups",
        "requiredPowersMode",
        "globalCompletionMode",
        "customRequiredPowers",
        "difficulty",
        "lives",
        "continues",
        "persistHp",
    ):
        assert config_key in app
        assert config_key in worker

    assert "GameSettingsConfig" in worker
    assert "web_turn_lock" in worker
    assert "web_attack_modern" in worker
    assert "web_specials_modern" in worker
    assert "web_jump_button" in worker
    assert "web_run_auto" in worker
    assert "web_shuffle_power_progression" in worker
    assert "shuffle_power_progression=bool(web_shuffle_power_progression)" in worker
    assert "web_enemy_randomization" in worker
    assert "enemy_randomization=bool(web_enemy_randomization)" in worker
    assert 'id="enemyRandomization" type="checkbox" checked' in html
    assert 'id="shufflePowerProgression" type="checkbox" checked' in html
    assert 'id="powersAsPickups" type="checkbox" checked' in html
    assert '<option value="seeded" selected>Random from seed</option>' in html
    assert '<option value="seed" selected>Seed</option>' in html
    assert '<option value="vanilla">Vanilla</option>' in html
    assert '<option value="custom">Custom</option>' in html
    assert "powers_as_pickups=bool(web_powers_as_pickups)" in worker
    assert "required_powers_mode=str(web_required_powers_mode)" in worker
    assert "global_completion_mode=str(web_global_completion_mode)" in worker
    assert '<option value="all_85" selected>All 85 available</option>' in html
    assert '<option value="game_beatable">Game beatable</option>' in html
    assert "custom_required_powers=int(web_custom_required_powers)" in worker
    assert "resultRequiredPowers.textContent" in app
    assert 'id="difficulty"' in html
    assert '<option value="very_hard" selected>Very Hard</option>' in html
    assert 'id="startingLives" type="number" min="1" max="10" step="1" value="5"' in html
    assert 'id="startingContinues" type="number" min="0" max="5" step="1" value="3"' in html
    assert 'id="persistHp" type="checkbox" checked' in html
    assert "difficulty=str(web_difficulty)" in worker
    assert "lives=int(web_lives)" in worker
    assert "continues=int(web_continues)" in worker
    assert "persist_hp=bool(web_persist_hp)" in worker


def test_web_jump_button_dependency_is_enforced_in_ui() -> None:
    app = Path("web/app.js").read_text(encoding="utf-8")
    assert "attackModern.checked && specialsModern.checked" in app
    assert "jumpButton.disabled = !jumpAvailable" in app


def test_web_progress_flavor_uses_full_deck_before_repeating() -> None:
    app = Path("web/app.js").read_text(encoding="utf-8")

    assert app.count('..."') >= 80
    assert "let sillyDeck = [];" in app
    assert "function refillSillyDeck()" in app
    assert "function nextSillyMessage()" in app
    assert "sillyDeck = shuffleMessages(SILLY_MESSAGES)" in app
    assert "lastSillyMessage" in app
    assert "}, 3600);" in app
    assert "chooseSillyMessages(6)" not in app
