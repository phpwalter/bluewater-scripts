from pathlib import Path

from bluewater.hooks import HOOKS, install


def test_install_uses_packaged_hook_templates(tmp_path: Path) -> None:
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    install(tmp_path)
    for name in HOOKS:
        installed = hooks_dir / name
        assert installed.is_file()
        assert "bluewater" in installed.read_text(encoding="utf-8")
