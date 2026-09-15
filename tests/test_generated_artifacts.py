import subprocess
from pathlib import Path

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.repository import Repository
from bluewater.validation import check_git_clean_generated


def _config() -> BluewaterConfig:
    return BluewaterConfig(version=1, locale_guard=LocaleGuardConfig(enabled=False))


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _repo(tmp_path: Path) -> Repository:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "bluewater@example.invalid")
    _git(tmp_path, "config", "user.name", "Bluewater Tests")
    generated = tmp_path / "docs" / "_generated"
    generated.mkdir(parents=True)
    (generated / "status.md").write_text("# Status\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("baseline\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "baseline")
    return Repository(tmp_path, "documentation")


def test_generated_artifacts_clean_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result = check_git_clean_generated(repo, _config())
    assert result.ok
    assert result.detail == "clean"


def test_dirty_generated_document_fails(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (tmp_path / "docs" / "_generated" / "status.md").write_text("# Changed\n", encoding="utf-8")
    result = check_git_clean_generated(repo, _config())
    assert not result.ok
    assert "docs/_generated/status.md" in result.detail.replace("\\", "/")


def test_dirty_readme_fails(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (tmp_path / "README.md").write_text("# Changed\n", encoding="utf-8")
    result = check_git_clean_generated(repo, _config())
    assert not result.ok
    assert "README.md" in result.detail


def test_unrelated_dirty_file_does_not_fail_generated_check(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (tmp_path / "notes.txt").write_text("changed\n", encoding="utf-8")
    result = check_git_clean_generated(repo, _config())
    assert result.ok
