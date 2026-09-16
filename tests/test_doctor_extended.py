import json
import subprocess
from pathlib import Path

import pytest

from bluewater.cli import main
from bluewater.hooks import install

CONFIG = """version: 1
repository:
  type: documentation
checks:
  structured_files: false
  markdown: false
  locale_guard: false
  generated_files: false
integrations:
  locale_guard:
    enabled: false
"""


def _repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text(CONFIG, encoding="utf-8")
    install(tmp_path)
    monkeypatch.chdir(tmp_path)


def test_extended_doctor_adds_operational_diagnostics(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["doctor", "--extended", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    names = [item["name"] for item in payload["checks"]]
    assert names[-4:] == [
        "resolved-profile",
        "active-checks",
        "hooks",
        "locale-guard-revision",
    ]
    resolved = next(item for item in payload["checks"] if item["name"] == "resolved-profile")
    assert "configured/resolved=documentation" in resolved["detail"]
    hooks = next(item for item in payload["checks"] if item["name"] == "hooks")
    assert hooks["ok"] is True
    assert "pre-commit=bluewater" in hooks["detail"]


def test_default_doctor_order_is_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["doctor", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert [item["name"] for item in payload["checks"]] == [
        "python-runtime",
        "git",
        "repository",
        "configuration",
        "profile",
        "bluewater-version",
        "locale-guard",
    ]
