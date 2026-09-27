import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from bluewater.cli import FORMAT_VERSION, main

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
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text(CONFIG, encoding="utf-8")
    monkeypatch.chdir(tmp_path)


def _schema() -> dict[str, object]:
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / "schemas" / "diagnostics.schema.json").read_text(encoding="utf-8"))


def test_json_results_include_format_version(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _repo(tmp_path, monkeypatch)
    assert main(["repo", "validate", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["format_version"] == FORMAT_VERSION == 1
    assert not list(Draft202012Validator(_schema()).iter_errors(payload))


def test_json_execution_error_uses_versioned_error_envelope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["doctor", "--format", "json"]) == 2
    raw = capsys.readouterr().out.strip()
    payload = json.loads(raw)
    assert payload == {
        "error": {"detail": "not inside a Bluewater repository", "kind": "execution"},
        "format_version": 1,
        "ok": False,
    }
    assert raw == json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert not list(Draft202012Validator(_schema()).iter_errors(payload))


def test_schema_rejects_unversioned_payload() -> None:
    payload = {"ok": True, "checks": []}
    assert list(Draft202012Validator(_schema()).iter_errors(payload))
