from pathlib import Path

import pytest

from bluewater.config import ConfigurationError, load_config


def test_missing_config_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        load_config(tmp_path)


def test_minimal_config(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text("version: 1\nrepository:\n  type: auto\n", encoding="utf-8")
    config = load_config(tmp_path)
    assert config.version == 1
    assert config.repository_type == "auto"
