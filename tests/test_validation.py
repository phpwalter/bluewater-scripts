import subprocess
from pathlib import Path

import pytest

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.repository import Repository
from bluewater.validation import (
    check_git_clean_generated,
    check_javascript_syntax,
    check_locale_guard,
    check_markdown,
    check_php_syntax,
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


def test_php_syntax_not_applicable_to_python(tmp_path: Path) -> None:
    result = check_php_syntax(Repository(tmp_path, "python"), _config())
    assert result.ok
    assert "not applicable" in result.detail


def test_php_changed_scope_without_php_files_is_success(tmp_path: Path) -> None:
    result = check_php_syntax(Repository(tmp_path, "php"), _config(), [])
    assert result.ok
    assert result.detail == "no changed PHP files"


def test_php_syntax_requires_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.php"
    path.write_text("<?php echo 'ok';", encoding="utf-8")
    monkeypatch.setattr("bluewater.validation.shutil.which", lambda _: None)
    result = check_php_syntax(Repository(tmp_path, "php"), _config(), [path])
    assert not result.ok
    assert "php executable not found" in result.detail


def test_php_syntax_reports_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.php"
    path.write_text("<?php echo 'ok';", encoding="utf-8")
    monkeypatch.setattr("bluewater.validation.shutil.which", lambda _: "php")
    monkeypatch.setattr(
        "bluewater.validation.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "No syntax errors", ""),
    )
    result = check_php_syntax(Repository(tmp_path, "php"), _config(), [path])
    assert result.ok
    assert "1 files" in result.detail


def test_php_syntax_reports_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.php"
    path.write_text("<?php broken", encoding="utf-8")
    monkeypatch.setattr("bluewater.validation.shutil.which", lambda _: "php")
    monkeypatch.setattr(
        "bluewater.validation.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 255, "", "Parse error"),
    )
    result = check_php_syntax(Repository(tmp_path, "php"), _config(), [path])
    assert not result.ok
    assert "Parse error" in result.detail


def test_javascript_changed_scope_without_js_files_is_success(tmp_path: Path) -> None:
    result = check_javascript_syntax(Repository(tmp_path, "javascript"), _config(), [])
    assert result.ok
    assert result.detail == "no changed JavaScript files"


def test_javascript_syntax_requires_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.js"
    path.write_text("const value = 1;", encoding="utf-8")
    monkeypatch.setattr("bluewater.validation.shutil.which", lambda _: None)
    result = check_javascript_syntax(Repository(tmp_path, "javascript"), _config(), [path])
    assert not result.ok
    assert "node executable not found" in result.detail


def test_javascript_syntax_reports_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.js"
    path.write_text("const value = 1;", encoding="utf-8")
    monkeypatch.setattr("bluewater.validation.shutil.which", lambda _: "node")
    monkeypatch.setattr(
        "bluewater.validation.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "", ""),
    )
    result = check_javascript_syntax(Repository(tmp_path, "javascript"), _config(), [path])
    assert result.ok
    assert "1 files" in result.detail


def test_javascript_syntax_reports_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "index.js"
    path.write_text("const = ;", encoding="utf-8")
    monkeypatch.setattr("bluewater.validation.shutil.which", lambda _: "node")
    monkeypatch.setattr(
        "bluewater.validation.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 1, "", "SyntaxError"),
    )
    result = check_javascript_syntax(Repository(tmp_path, "javascript"), _config(), [path])
    assert not result.ok
    assert "SyntaxError" in result.detail


def test_locale_guard_disabled(tmp_path: Path) -> None:
    result = check_locale_guard(Repository(tmp_path, "documentation"), _config())
    assert result.ok
    assert result.detail == "disabled"


def test_generated_files_reports_non_git_directory(tmp_path: Path) -> None:
    result = check_git_clean_generated(Repository(tmp_path, "documentation"), _config())
    assert not result.ok


def test_changed_scope_validates_untracked_files(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    config = _config(markdown=False, generated_files=False)
    results = run_checks(Repository(tmp_path, "documentation"), config, "changed")
    structured = next(result for result in results if result.name == "structured-files")
    assert not structured.ok


def test_run_checks_rejects_unknown_scope(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="scope"):
        run_checks(Repository(tmp_path, "documentation"), _config(), "bogus")
