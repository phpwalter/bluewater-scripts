from pathlib import Path

import pytest

from bluewater.initialization import initialize


def test_initialize_detects_python_repository(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='consumer'\n", encoding="utf-8")
    path = initialize(tmp_path)
    assert path.is_file()
    assert "type: python" in path.read_text(encoding="utf-8")


def test_initialize_refuses_overwrite_without_force(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_text("existing", encoding="utf-8")
    with pytest.raises(RuntimeError):
        initialize(tmp_path)
