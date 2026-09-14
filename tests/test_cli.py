from pathlib import Path

import pytest

from bluewater.cli import main

CONFIG = """version: 1
repository:
  type: documentation
  required_bluewater_version: \">=1.0.0.dev0,<2.0\"
checks:
  structured_files: false
  markdown: false
  locale_guard: false
  generated_files: false
integrations:
  locale_guard:
    enabled: false
"""

ENABLED_LOCALE_GUARD_CONFIG = """version: 1
repository:
  type: documentation
  required_bluewater_version: \">=1.0.0.dev0,<2.0\"
checks:
  structured_files: false
  markdown: false
  locale_guard: true
  generated_files: false
integrations:
  locale_guard:
    enabled: true
    path: tools/locale-guard
    config: .locale-guard.yml
"""


def _repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / ".git").mkdir()
    (tmp_path / "bluewater.yml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_doctor_reports_actionable_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["doctor"]) == 0
    output = capsys.readouterr().out
    assert "PASS python-runtime" in output
    assert "PASS git" in output
    assert "PASS repository" in output
    assert "PASS bluewater-version" in output
    assert "PASS locale-guard" in output


def test_repo_validate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["repo", "validate"]) == 0
    output = capsys.readouterr().out
    assert "PASS repository" in output
    assert "PASS configuration" in output
    assert "PASS profile" in output
    assert "PASS bluewater-version" in output


def test_docs_disabled_is_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["docs", "validate"]) == 0
    assert "LocaleGuard disabled" in capsys.readouterr().out


def test_check_reports_passes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["check", "--scope", "all"]) == 0
    assert "PASS bluewater-version" in capsys.readouterr().out


def test_missing_configuration_returns_usage_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["doctor"]) == 2
    assert "ERROR:" in capsys.readouterr().out


def test_malformed_configuration_returns_usage_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "bluewater.yml").write_text("version: nope\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert main(["doctor"]) == 2
    output = capsys.readouterr().out
    assert "ERROR:" in output
    assert "invalid bluewater.yml" in output


def test_doctor_without_git_metadata_returns_validation_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "bluewater.yml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    assert main(["doctor"]) == 1
    output = capsys.readouterr().out
    assert "FAIL repository" in output
    assert "missing Git metadata" in output


def test_repo_validate_without_git_metadata_returns_validation_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "bluewater.yml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    assert main(["repo", "validate"]) == 1
    assert "FAIL repository" in capsys.readouterr().out


def test_hooks_install_without_git_worktree_returns_usage_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "bluewater.yml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    assert main(["hooks", "install"]) == 2
    output = capsys.readouterr().out
    assert "ERROR:" in output
    assert ".git/hooks not found" in output


def test_doctor_missing_locale_guard_returns_validation_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text(
        ENABLED_LOCALE_GUARD_CONFIG, encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    assert main(["doctor"]) == 1
    output = capsys.readouterr().out
    assert "FAIL locale-guard" in output
    assert "tools/locale-guard/locale_guard.py" in output
    assert ".locale-guard.yml" in output


def test_docs_missing_locale_guard_returns_usage_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text(
        ENABLED_LOCALE_GUARD_CONFIG, encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    assert main(["docs", "check"]) == 2
    output = capsys.readouterr().out
    assert "ERROR:" in output
    assert "LocaleGuard is enabled but missing" in output


def test_incompatible_version_returns_validation_failure_for_all_validation_surfaces(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    (tmp_path / "bluewater.yml").write_text(
        CONFIG.replace(">=1.0.0.dev0,<2.0", ">=9.0"), encoding="utf-8"
    )

    assert main(["doctor"]) == 1
    assert "FAIL bluewater-version" in capsys.readouterr().out

    assert main(["repo", "validate"]) == 1
    assert "FAIL bluewater-version" in capsys.readouterr().out

    assert main(["check", "--scope", "all"]) == 1
    assert "FAIL bluewater-version" in capsys.readouterr().out

    assert main(["ci", "validate"]) == 1
    assert "FAIL bluewater-version" in capsys.readouterr().out


def test_ci_validate_uses_all_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["ci", "validate"]) == 0
    assert "PASS bluewater-version" in capsys.readouterr().out


def test_printed_failure_returns_one(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _repo(tmp_path, monkeypatch)
    (tmp_path / "bluewater.yml").write_text(
        CONFIG.replace(">=1.0.0.dev0,<2.0", ">=9.0"), encoding="utf-8"
    )
    assert main(["check", "--scope", "all"]) == 1
