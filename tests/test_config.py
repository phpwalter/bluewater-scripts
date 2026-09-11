from pathlib import Path

import pytest

from bluewater.config import ConfigurationError, load_config


def test_missing_config_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        load_config(tmp_path)


def test_non_mapping_config_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text("- invalid\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="YAML mapping"):
        load_config(tmp_path)


def test_schema_invalid_config_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text("version: nope\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="invalid bluewater.yml"):
        load_config(tmp_path)


def test_minimal_config(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text(
        "version: 1\nrepository:\n  type: auto\n", encoding="utf-8"
    )
    config = load_config(tmp_path)
    assert config.version == 1
    assert config.repository_type == "auto"
    assert config.locale_guard.enabled


def test_full_config_mapping(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text(
        """version: 1
repository:
  type: php
  required_bluewater_version: \">=1.0.0.dev0,<2.0\"
checks:
  markdown: false
integrations:
  locale_guard:
    enabled: false
    path: vendor/locale-guard
    config: config/locale.yml
""",
        encoding="utf-8",
    )
    config = load_config(tmp_path)
    assert config.repository_type == "php"
    assert config.required_version == ">=1.0.0.dev0,<2.0"
    assert not config.locale_guard.enabled
    assert config.locale_guard.path == "vendor/locale-guard"
    assert config.locale_guard.config == "config/locale.yml"
    assert config.checks == {"markdown": False}
