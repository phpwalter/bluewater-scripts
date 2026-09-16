from pathlib import Path
from types import SimpleNamespace

import pytest

from bluewater.config import LocaleGuardConfig
from bluewater.locale_guard import LocaleGuardError, command, run


def test_missing_locale_guard_is_error(tmp_path: Path) -> None:
    with pytest.raises(LocaleGuardError):
        command(tmp_path, LocaleGuardConfig(), "check")


def test_locale_guard_runs_with_utf8_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool_dir = tmp_path / "tools" / "locale-guard"
    tool_dir.mkdir(parents=True)
    (tool_dir / "locale_guard.py").write_text("", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        captured.update(kwargs)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("bluewater.locale_guard.subprocess.run", fake_run)

    result = run(tmp_path, LocaleGuardConfig(), "check")

    assert result == 0
    env = captured["env"]
    assert isinstance(env, dict)
    assert env["PYTHONUTF8"] == "1"
    assert env["PYTHONIOENCODING"] == "utf-8"
