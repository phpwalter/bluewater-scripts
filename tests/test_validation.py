from pathlib import Path

from bluewater.config import BluewaterConfig, LocaleGuardConfig
from bluewater.repository import Repository
from bluewater.validation import check_structured_files


def test_invalid_json_fails(tmp_path: Path) -> None:
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    config = BluewaterConfig(version=1, locale_guard=LocaleGuardConfig(enabled=False))
    result = check_structured_files(Repository(tmp_path, "documentation"), config)
    assert not result.ok
