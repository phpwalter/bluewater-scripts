from pathlib import Path

import pytest

from bluewater.repository import detect_profile, inspect_repository


@pytest.mark.parametrize(
    ("markers", "expected"),
    [
        (("pyproject.toml",), "python"),
        (("requirements.txt",), "python"),
        (("composer.json",), "php"),
        (("package.json",), "javascript"),
        (("pyproject.toml", "composer.json"), "mixed"),
        (("pyproject.toml", "package.json"), "mixed"),
        (("composer.json", "package.json"), "mixed"),
        (("pyproject.toml", "composer.json", "package.json"), "mixed"),
    ],
)
def test_language_marker_matrix(tmp_path: Path, markers: tuple[str, ...], expected: str) -> None:
    for marker in markers:
        (tmp_path / marker).write_text("{}\n", encoding="utf-8")
    assert detect_profile(tmp_path) == expected


def test_documentation_only_repository(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    assert detect_profile(tmp_path) == "documentation"


def test_empty_repository_defaults_to_documentation(tmp_path: Path) -> None:
    assert detect_profile(tmp_path) == "documentation"


def test_documentation_directory_does_not_override_language_profile(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "composer.json").write_text("{}\n", encoding="utf-8")
    assert detect_profile(tmp_path) == "php"


def test_documentation_directory_does_not_hide_mixed_profile(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='example'\n", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}\n", encoding="utf-8")
    assert detect_profile(tmp_path) == "mixed"


def test_explicit_profile_is_authoritative_over_detected_markers(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{}\n", encoding="utf-8")
    repo = inspect_repository(tmp_path, "php")
    assert repo.profile == "php"
    assert detect_profile(tmp_path) == "javascript"


def test_auto_profile_uses_detection(tmp_path: Path) -> None:
    (tmp_path / "composer.json").write_text("{}\n", encoding="utf-8")
    assert inspect_repository(tmp_path, "auto").profile == "php"
