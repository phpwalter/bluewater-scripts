from pathlib import Path

import pytest

from bluewater.config import ConfigurationError, load_config

BASE = """version: 1
repository:
  type: documentation
integrations:
  locale_guard:
    path: {path}
    config: {config}
"""


@pytest.mark.parametrize(
    ("path", "config"),
    [
        ("../locale-guard", ".locale-guard.yml"),
        ("tools/../../locale-guard", ".locale-guard.yml"),
        ("/opt/locale-guard", ".locale-guard.yml"),
        ("C:\\\\locale-guard", ".locale-guard.yml"),
        ("tools/locale-guard", "../locale.yml"),
        ("tools/locale-guard", "/tmp/locale.yml"),
        ("tools/locale-guard", "C:\\\\locale.yml"),
    ],
)
def test_integration_paths_cannot_escape_repository(
    tmp_path: Path, path: str, config: str
) -> None:
    (tmp_path / "bluewater.yml").write_text(
        BASE.format(path=path, config=config),
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError, match="repository-relative"):
        load_config(tmp_path)


def test_safe_relative_paths_are_allowed(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text(
        BASE.format(path="vendor/locale-guard", config="config/locale.yml"),
        encoding="utf-8",
    )
    loaded = load_config(tmp_path)
    assert loaded.locale_guard.path == "vendor/locale-guard"
    assert loaded.locale_guard.config == "config/locale.yml"
