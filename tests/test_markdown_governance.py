from pathlib import Path

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.repository import Repository
from bluewater.validation import check_markdown


def _config() -> BluewaterConfig:
    return BluewaterConfig(version=1, locale_guard=LocaleGuardConfig(enabled=False))


def test_heading_and_spaces_pass(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Heading\n\nBody text.\n", encoding="utf-8")
    result = check_markdown(Repository(tmp_path, "documentation"), _config())
    assert result.ok


def test_missing_leading_heading_fails(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Body text.\n", encoding="utf-8")
    result = check_markdown(Repository(tmp_path, "documentation"), _config())
    assert not result.ok
    assert "missing leading heading" in result.detail


def test_tab_character_fails(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Heading\n\tBody\n", encoding="utf-8")
    result = check_markdown(Repository(tmp_path, "documentation"), _config())
    assert not result.ok
    assert "tab character" in result.detail


def test_tools_markdown_is_excluded(tmp_path: Path) -> None:
    tools = tmp_path / "tools" / "vendor"
    tools.mkdir(parents=True)
    (tools / "README.md").write_text("not governed\tcontent", encoding="utf-8")
    result = check_markdown(Repository(tmp_path, "documentation"), _config())
    assert result.ok
