from pathlib import Path

from bluewater.repository import detect_profile


def test_detect_python_profile(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    assert detect_profile(tmp_path) == "python"


def test_detect_mixed_profile(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    assert detect_profile(tmp_path) == "mixed"
