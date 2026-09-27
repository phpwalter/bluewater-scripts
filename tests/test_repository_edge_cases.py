from pathlib import Path

from bluewater.repository import find_root


def test_find_root_accepts_git_worktree_metadata_file(tmp_path: Path) -> None:
    (tmp_path / ".git").write_text("gitdir: ../.git/worktrees/example\n", encoding="utf-8")
    nested = tmp_path / "src" / "deep"
    nested.mkdir(parents=True)
    assert find_root(nested) == tmp_path.resolve()


def test_find_root_prefers_nearest_bluewater_repository(tmp_path: Path) -> None:
    outer = tmp_path / "outer"
    inner = outer / "packages" / "inner"
    nested = inner / "src"
    nested.mkdir(parents=True)
    (outer / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    (inner / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    assert find_root(nested) == inner.resolve()


def test_find_root_prefers_nearest_git_boundary(tmp_path: Path) -> None:
    outer = tmp_path / "outer"
    inner = outer / "vendor" / "nested"
    nested = inner / "src"
    nested.mkdir(parents=True)
    (outer / ".git").mkdir()
    (inner / ".git").mkdir()
    assert find_root(nested) == inner.resolve()


def test_find_root_handles_paths_with_spaces(tmp_path: Path) -> None:
    root = tmp_path / "repo with spaces"
    nested = root / "folder with spaces" / "deep"
    nested.mkdir(parents=True)
    (root / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    assert find_root(nested) == root.resolve()
