import tomllib
from pathlib import Path

from packaging.version import Version

from bluewater import __version__


def test_version_metadata_is_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    version_file = (root / "VERSION").read_text(encoding="utf-8").strip()
    assert __version__ == version_file == pyproject["project"]["version"]


def test_release_version_is_valid_and_stable() -> None:
    version = Version(__version__)
    assert version == Version("1.0.0")
    assert not version.is_prerelease
    assert not version.is_devrelease
