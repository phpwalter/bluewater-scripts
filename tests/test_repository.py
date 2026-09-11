from pathlib import Path

import pytest

from bluewater.repository import detect_profile, find_root, inspect_repository


def test_detect_python_profile(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    assert detect_profile(tmp_path) == "python"


def test_detect_php_profile(tmp_path: Path) -> None:
    (tmp_path / "composer.json").write_text("{}", encoding="utf-8")
    assert detect_profile(tmp_path) == "php"


def test_detect_javascript_profile(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    assert detect_profile(tmp_path) == "javascript"


def test_detect_documentation_profile(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    assert detect_profile(tmp_path) == "documentation"


def test_detect_mixed_profile(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    assert detect_profile(tmp_path) == "mixed"


def test_find_root_walks_parents(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text("version: 1\n", encoding="utf-8")
    child = tmp_path / "a" / "b"
    child.mkdir(parents=True)
    assert find_root(child) == tmp_path.resolve()


def test_find_root_fails_outside_repository(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="not inside"):
        find_root(tmp_path)


def test_inspect_repository_honors_explicit_profile(tmp_path: Path) -> None:
    repo = inspect_repository(tmp_path, "php")
    assert repo.root == tmp_path
    assert repo.profile == "php"
