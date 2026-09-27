import subprocess
from pathlib import Path

import pytest

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.repository import Repository
from bluewater.validation import check_javascript_syntax, check_php_syntax, check_python_syntax


def _config(**checks: bool) -> BluewaterConfig:
    return BluewaterConfig(
        version=1,
        locale_guard=LocaleGuardConfig(enabled=False),
        checks=checks,
    )


def test_mixed_profile_runs_python_syntax(tmp_path: Path) -> None:
    src = tmp_path / "src"
    tests = tmp_path / "tests"
    src.mkdir()
    tests.mkdir()
    (src / "ok.py").write_text("value = 1\n", encoding="utf-8")
    result = check_python_syntax(Repository(tmp_path, "mixed"), _config())
    assert result.ok


def test_mixed_profile_runs_php_syntax(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.php"
    path.write_text("<?php echo 'ok';\n", encoding="utf-8")
    monkeypatch.setattr("bluewater.validation.shutil.which", lambda name: "/usr/bin/php" if name == "php" else None)
    monkeypatch.setattr(
        "bluewater.validation.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "No syntax errors", ""),
    )
    result = check_php_syntax(Repository(tmp_path, "mixed"), _config(), [path])
    assert result.ok


def test_mixed_profile_runs_javascript_syntax(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.js"
    path.write_text("const value = 1;\n", encoding="utf-8")
    monkeypatch.setattr("bluewater.validation.shutil.which", lambda name: "/usr/bin/node" if name == "node" else None)
    monkeypatch.setattr(
        "bluewater.validation.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "", ""),
    )
    result = check_javascript_syntax(Repository(tmp_path, "mixed"), _config(), [path])
    assert result.ok


def test_disabled_php_check_does_not_probe_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.php"
    path.write_text("<?php broken\n", encoding="utf-8")

    def fail_if_probed(_: str) -> str | None:
        raise AssertionError("runtime probe should not occur")

    monkeypatch.setattr("bluewater.validation.shutil.which", fail_if_probed)
    result = check_php_syntax(
        Repository(tmp_path, "php"), _config(php_syntax=False), [path]
    )
    assert result.ok


def test_disabled_javascript_check_does_not_probe_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.js"
    path.write_text("const = ;\n", encoding="utf-8")

    def fail_if_probed(_: str) -> str | None:
        raise AssertionError("runtime probe should not occur")

    monkeypatch.setattr("bluewater.validation.shutil.which", fail_if_probed)
    result = check_javascript_syntax(
        Repository(tmp_path, "javascript"), _config(javascript_syntax=False), [path]
    )
    assert result.ok
