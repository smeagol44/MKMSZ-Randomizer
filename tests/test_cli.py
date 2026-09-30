from mkmszr.cli import _build_parser


def test_enemy_randomization_cli_flag_is_exposed():
    args = _build_parser().parse_args(
        ["in.z64", "out.z64", "--enemy-randomization"]
    )
    assert args.enemy_randomization is True
