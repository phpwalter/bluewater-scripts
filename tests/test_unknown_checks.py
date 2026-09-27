from pathlib import Path

import pytest

from bluewater.config import ConfigurationError, load_config


def test_unknown_check_name_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text(
        """version: 1
repository:
  type: documentation
checks:
  markdwon: false
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError, match="invalid bluewater.yml"):
        load_config(tmp_path)


def test_all_version_one_check_names_are_accepted(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text(
        """version: 1
repository:
  type: mixed
checks:
  structured_files: true
  markdown: true
  python_syntax: true
  php_syntax: true
  javascript_syntax: true
  locale_guard: true
  generated_files: true
""",
        encoding="utf-8",
    )
    config = load_config(tmp_path)
    assert set(config.checks) == {
        "structured_files",
        "markdown",
        "python_syntax",
        "php_syntax",
        "javascript_syntax",
        "locale_guard",
        "generated_files",
    }
