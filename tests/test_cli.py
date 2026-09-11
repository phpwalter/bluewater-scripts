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


def _repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "bluewater.yml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_doctor_reports_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["doctor"]) == 0
    output = capsys.readouterr().out
    assert "profile: documentation" in output
    assert "LocaleGuard: disabled" in output


def test_repo_validate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["repo", "validate"]) == 0
    assert "repository valid: documentation" in capsys.readouterr().out


def test_docs_disabled_is_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["docs", "validate"]) == 0
    assert "LocaleGuard disabled" in capsys.readouterr().out


def test_check_reports_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
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


def test_printed_failure_returns_one(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _repo(tmp_path, monkeypatch)
    (tmp_path / "bluewater.yml").write_text(
        CONFIG.replace(">=1.0.0.dev0,<2.0", ">=9.0"), encoding="utf-8"
    )
    assert main(["check", "--scope", "all"]) == 1
