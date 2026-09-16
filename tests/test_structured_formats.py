from pathlib import Path

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.repository import Repository
from bluewater.validation import check_structured_files


def _config() -> BluewaterConfig:
    return BluewaterConfig(version=1, locale_guard=LocaleGuardConfig(enabled=False))


def test_valid_toml_passes(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "example"\n', encoding="utf-8")
    result = check_structured_files(Repository(tmp_path, "python"), _config())
    assert result.ok
    assert "TOML" in result.detail


def test_invalid_toml_fails(tmp_path: Path) -> None:
    (tmp_path / "broken.toml").write_text("[project\n", encoding="utf-8")
    result = check_structured_files(Repository(tmp_path, "documentation"), _config())
    assert not result.ok


def test_empty_yaml_is_valid(tmp_path: Path) -> None:
    (tmp_path / "empty.yml").write_text("", encoding="utf-8")
    assert check_structured_files(Repository(tmp_path, "documentation"), _config()).ok


def test_multi_document_yaml_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "multi.yml").write_text("a: 1\n---\nb: 2\n", encoding="utf-8")
    result = check_structured_files(Repository(tmp_path, "documentation"), _config())
    assert not result.ok


def test_json_utf8_bom_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "bom.json").write_bytes(b"\xef\xbb\xbf{}\n")
    result = check_structured_files(Repository(tmp_path, "documentation"), _config())
    assert not result.ok
