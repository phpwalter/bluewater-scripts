from pathlib import Path

import pytest

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.repository import Repository
from bluewater.validation import (
    check_git_clean_generated,
    check_locale_guard,
    check_markdown,
    check_python_syntax,
    check_structured_files,
    run_checks,
)


def _config(**checks: bool) -> BluewaterConfig:
    return BluewaterConfig(
        version=1,
        required_version=">=1.0.0.dev0,<2.0",
        locale_guard=LocaleGuardConfig(enabled=False),
        checks=checks,
    )


def test_structured_files_reports_invalid_json(tmp_path: Path) -> None:
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    result = check_structured_files(Repository(tmp_path, "documentation"), _config())
    assert not result.ok


def test_structured_files_can_be_disabled(tmp_path: Path) -> None:
    result = check_structured_files(
        Repository(tmp_path, "documentation"), _config(structured_files=False)
    )
    assert result.ok
    assert result.detail == "disabled"


def test_markdown_detects_missing_heading_and_tabs(tmp_path: Path) -> None:
    (tmp_path / "bad.md").write_text("plain\ttext", encoding="utf-8")
    result = check_markdown(Repository(tmp_path, "documentation"), _config())
    assert not result.ok
    assert "missing leading heading" in result.detail
    assert "tab character" in result.detail


def test_python_syntax_not_applicable_to_documentation(tmp_path: Path) -> None:
    result = check_python_syntax(Repository(tmp_path, "documentation"), _config())
    assert result.ok
    assert "not applicable" in result.detail


def test_python_syntax_detects_compile_failure(tmp_path: Path) -> None:
    src = tmp_path / "src"
    tests = tmp_path / "tests"
    src.mkdir()
    tests.mkdir()
    (src / "bad.py").write_text("def broken(:\n", encoding="utf-8")
    result = check_python_syntax(Repository(tmp_path, "python"), _config())
    assert not result.ok


def test_locale_guard_disabled(tmp_path: Path) -> None:
    result = check_locale_guard(Repository(tmp_path, "documentation"), _config())
    assert result.ok
    assert result.detail == "disabled"


def test_generated_files_reports_non_git_directory(tmp_path: Path) -> None:
    result = check_git_clean_generated(Repository(tmp_path, "documentation"), _config())
    assert not result.ok


def test_run_checks_rejects_unknown_scope(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="scope"):
        run_checks(Repository(tmp_path, "documentation"), _config(), "bogus")
