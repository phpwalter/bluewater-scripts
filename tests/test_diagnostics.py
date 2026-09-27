from pathlib import Path

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.diagnostics import doctor_checks, repository_checks
from bluewater.repository import Repository


def _config(locale_guard: bool = False) -> BluewaterConfig:
    return BluewaterConfig(
        version=1,
        required_version=">=1.0.0.dev0,<2.0",
        locale_guard=LocaleGuardConfig(enabled=locale_guard),
    )


def test_repository_checks_pass_for_documentation_repo(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    results = repository_checks(Repository(tmp_path, "documentation"), _config())
    assert all(result.ok for result in results)


def test_repository_check_order_and_names_are_stable(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    results = repository_checks(Repository(tmp_path, "documentation"), _config())
    names = [result.name for result in results]
    assert names == ["repository", "configuration", "profile", "bluewater-version"]
    assert len(names) == len(set(names))


def test_repository_checks_fail_without_git_metadata(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    results = repository_checks(Repository(tmp_path, "documentation"), _config())
    repository = next(result for result in results if result.name == "repository")
    assert not repository.ok


def test_repository_checks_fail_when_profile_marker_missing(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    results = repository_checks(Repository(tmp_path, "python"), _config())
    profile = next(result for result in results if result.name == "profile")
    assert not profile.ok


def test_doctor_check_order_and_names_are_stable(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    results = doctor_checks(Repository(tmp_path, "documentation"), _config())
    names = [result.name for result in results]
    assert names == [
        "python-runtime",
        "git",
        "repository",
        "configuration",
        "profile",
        "bluewater-version",
        "locale-guard",
    ]
    assert len(names) == len(set(names))


def test_doctor_reports_disabled_locale_guard_as_pass(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    results = doctor_checks(Repository(tmp_path, "documentation"), _config())
    locale_guard = next(result for result in results if result.name == "locale-guard")
    assert locale_guard.ok
    assert locale_guard.detail == "disabled"


def test_doctor_fails_when_enabled_locale_guard_files_are_missing(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    results = doctor_checks(Repository(tmp_path, "documentation"), _config(locale_guard=True))
    locale_guard = next(result for result in results if result.name == "locale-guard")
    assert not locale_guard.ok
    assert "missing:" in locale_guard.detail
