import tomllib
from pathlib import Path

from bluewater import __version__


def test_version_metadata_is_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    version_file = (root / "VERSION").read_text(encoding="utf-8").strip()
    assert __version__ == version_file == pyproject["project"]["version"]


def test_development_version_remains_prerelease_until_release() -> None:
    assert __version__.endswith(".dev0")
