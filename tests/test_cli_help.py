import pytest

from bluewater.cli import _parser


def test_top_level_help_is_stable(capsys: pytest.CaptureFixture[str]) -> None:
    parser = _parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    for command in ("init", "doctor", "check", "hooks", "docs", "repo", "ci"):
        assert command in output


def test_invalid_format_is_rejected() -> None:
    parser = _parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["doctor", "--format", "xml"])
    assert exc.value.code == 2


def test_unknown_command_is_rejected() -> None:
    parser = _parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["unknown"])
    assert exc.value.code == 2
