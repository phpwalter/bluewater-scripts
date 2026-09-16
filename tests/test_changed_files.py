import subprocess
from pathlib import Path

from bluewater.repository import Repository
from bluewater.validation import _changed_files


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path) -> Repository:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "bluewater@example.invalid")
    _git(tmp_path, "config", "user.name", "Bluewater Tests")
    return Repository(tmp_path, "documentation")


def _relative(repo: Repository) -> list[str]:
    return [path.relative_to(repo.root).as_posix() for path in _changed_files(repo)]


def test_changed_files_include_untracked_paths_with_spaces_and_unicode(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (tmp_path / "with spaces.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "café.json").write_text("{}\n", encoding="utf-8")
    assert _relative(repo) == ["café.json", "with spaces.json"]


def test_changed_files_include_staged_and_unstaged_files(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    staged = tmp_path / "staged.json"
    unstaged = tmp_path / "unstaged.json"
    staged.write_text("{}\n", encoding="utf-8")
    unstaged.write_text("{}\n", encoding="utf-8")
    _git(tmp_path, "add", "staged.json", "unstaged.json")
    _git(tmp_path, "commit", "-qm", "baseline")

    staged.write_text('{"changed": true}\n', encoding="utf-8")
    unstaged.write_text('{"changed": true}\n', encoding="utf-8")
    _git(tmp_path, "add", "staged.json")

    assert _relative(repo) == ["staged.json", "unstaged.json"]


def test_changed_files_report_renamed_destination_only(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    original = tmp_path / "old name.json"
    original.write_text("{}\n", encoding="utf-8")
    _git(tmp_path, "add", "old name.json")
    _git(tmp_path, "commit", "-qm", "baseline")
    _git(tmp_path, "mv", "old name.json", "new name.json")

    assert _relative(repo) == ["new name.json"]


def test_changed_files_exclude_deleted_paths(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    path = tmp_path / "deleted.json"
    path.write_text("{}\n", encoding="utf-8")
    _git(tmp_path, "add", "deleted.json")
    _git(tmp_path, "commit", "-qm", "baseline")
    path.unlink()

    assert _relative(repo) == []


def test_changed_files_work_in_repository_without_commits(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (tmp_path / "first.json").write_text("{}\n", encoding="utf-8")
    assert _relative(repo) == ["first.json"]
