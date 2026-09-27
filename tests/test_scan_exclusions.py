from pathlib import Path

from bluewater.repository import Repository
from bluewater.validation import _paths


def test_repository_scan_excludes_dependency_and_build_trees(tmp_path: Path) -> None:
    included = tmp_path / "src" / "app.json"
    included.parent.mkdir()
    included.write_text("{}\n", encoding="utf-8")

    excluded_dirs = [".venv", "venv", "node_modules", "vendor", "dist", "build"]
    for directory in excluded_dirs:
        path = tmp_path / directory / "nested" / "ignored.json"
        path.parent.mkdir(parents=True)
        path.write_text("{broken\n", encoding="utf-8")

    paths = _paths(Repository(tmp_path, "documentation"), (".json",), None)
    assert [path.relative_to(tmp_path).as_posix() for path in paths] == ["src/app.json"]


def test_changed_scope_excludes_dependency_tree_paths(tmp_path: Path) -> None:
    included = tmp_path / "app.json"
    included.write_text("{}\n", encoding="utf-8")
    excluded = tmp_path / "node_modules" / "pkg" / "file.json"
    excluded.parent.mkdir(parents=True)
    excluded.write_text("{}\n", encoding="utf-8")

    paths = _paths(
        Repository(tmp_path, "documentation"),
        (".json",),
        [excluded, included],
    )
    assert paths == [included]
