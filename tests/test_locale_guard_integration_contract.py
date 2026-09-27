from pathlib import Path

import pytest

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.locale_guard import LocaleGuardError, command, run
from bluewater.repository import Repository
from bluewater.validation import check_locale_guard


def _install_fake_locale_guard(root: Path, exit_code: int = 0) -> LocaleGuardConfig:
    tool = root / "tools" / "locale-guard"
    tool.mkdir(parents=True)
    script = tool / "locale_guard.py"
    script.write_text(
        "import sys\nraise SystemExit(" + str(exit_code) + ")\n",
        encoding="utf-8",
    )
    (root / ".locale-guard.yml").write_text("version: 1\n", encoding="utf-8")
    return LocaleGuardConfig(enabled=True)


@pytest.mark.parametrize("action", ["scan", "update", "check"])
def test_command_delegates_supported_actions(tmp_path: Path, action: str) -> None:
    config = _install_fake_locale_guard(tmp_path)
    cmd = command(tmp_path, config, action)
    assert cmd[-1] == action
    assert "locale_guard.py" in cmd[2]
    assert cmd[-3:-1] == ["--config", ".locale-guard.yml"]


def test_run_propagates_locale_guard_exit_code(tmp_path: Path) -> None:
    config = _install_fake_locale_guard(tmp_path, exit_code=7)
    assert run(tmp_path, config, "check") == 7


def test_missing_locale_guard_script_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(LocaleGuardError, match="enabled but missing"):
        command(tmp_path, LocaleGuardConfig(enabled=True), "check")


def test_validation_maps_nonzero_locale_guard_to_failure(tmp_path: Path) -> None:
    config = _install_fake_locale_guard(tmp_path, exit_code=4)
    result = check_locale_guard(
        Repository(tmp_path, "documentation"),
        BluewaterConfig(version=1, locale_guard=config, checks={"locale_guard": True}),
    )
    assert not result.ok
    assert result.detail == "exit code 4"


def test_integration_disable_wins_over_check_enable(tmp_path: Path) -> None:
    config = BluewaterConfig(
        version=1,
        locale_guard=LocaleGuardConfig(enabled=False),
        checks={"locale_guard": True},
    )
    result = check_locale_guard(Repository(tmp_path, "documentation"), config)
    assert result.ok
    assert result.detail == "disabled"


def test_check_disable_wins_over_integration_enable(tmp_path: Path) -> None:
    config = BluewaterConfig(
        version=1,
        locale_guard=LocaleGuardConfig(enabled=True),
        checks={"locale_guard": False},
    )
    result = check_locale_guard(Repository(tmp_path, "documentation"), config)
    assert result.ok
    assert result.detail == "disabled"
