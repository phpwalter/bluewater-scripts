from pathlib import Path

import pytest
import yaml

from bluewater.initialization import initialize


@pytest.mark.parametrize(
    ("marker", "expected"),
    [
        ("pyproject.toml", "python"),
        ("composer.json", "php"),
        ("package.json", "javascript"),
    ],
)
def test_initialize_language_profiles(tmp_path: Path, marker: str, expected: str) -> None:
    (tmp_path / marker).write_text("{}\n", encoding="utf-8")
    config = yaml.safe_load(initialize(tmp_path).read_text(encoding="utf-8"))
    assert config["repository"]["type"] == expected


def test_initialize_documentation_profile(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    config = yaml.safe_load(initialize(tmp_path).read_text(encoding="utf-8"))
    assert config["repository"]["type"] == "documentation"


def test_initialize_mixed_profile(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}\n", encoding="utf-8")
    config = yaml.safe_load(initialize(tmp_path).read_text(encoding="utf-8"))
    assert config["repository"]["type"] == "mixed"


def test_initialized_config_lists_all_supported_checks(tmp_path: Path) -> None:
    config = yaml.safe_load(initialize(tmp_path).read_text(encoding="utf-8"))
    assert config["checks"] == {
        "structured_files": True,
        "markdown": True,
        "python_syntax": True,
        "php_syntax": True,
        "javascript_syntax": True,
        "locale_guard": True,
        "generated_files": True,
    }


def test_force_reinitialization_is_deterministic(tmp_path: Path) -> None:
    first = initialize(tmp_path).read_bytes()
    second = initialize(tmp_path, force=True).read_bytes()
    assert first == second
