from mkmszr.cli import _build_parser


def test_enemy_randomization_cli_flag_is_exposed():
    args = _build_parser().parse_args(
        ["in.z64", "out.z64", "--enemy-randomization"]
    )
    assert args.enemy_randomization is True


def test_run_settings_cli_defaults_and_overrides():
    parser = _build_parser()
    defaults = parser.parse_args(["in.z64", "out.z64"])
    assert defaults.difficulty == "very_hard"
    assert defaults.lives == 5
    assert defaults.continues == 3
    assert defaults.no_persist_hp is False

    custom = parser.parse_args(
        [
            "in.z64", "out.z64",
            "--difficulty", "hard",
            "--lives", "10",
            "--continues", "5",
            "--no-persist-hp",
        ]
    )
    assert custom.difficulty == "hard"
    assert custom.lives == 10
    assert custom.continues == 5
    assert custom.no_persist_hp is True
