from pathlib import Path

import pytest

from bluewater.hooks import HOOKS, install


def test_install_uses_packaged_hook_templates(tmp_path: Path) -> None:
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    install(tmp_path)
    for name in HOOKS:
        installed = hooks_dir / name
        assert installed.is_file()
        text = installed.read_text(encoding="utf-8")
        assert "command -v bluewater" in text
        assert "python -m bluewater" in text
        assert "python3 -m bluewater" in text


def test_blocking_hooks_fail_closed_when_bluewater_is_unavailable(tmp_path: Path) -> None:
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    install(tmp_path)
    for name in ("pre-commit", "pre-push"):
        text = (hooks_dir / name).read_text(encoding="utf-8")
        assert "exit 127" in text
        assert "Bluewater is not available on PATH" in text


def test_post_hooks_remain_non_blocking(tmp_path: Path) -> None:
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    install(tmp_path)
    for name in ("post-checkout", "post-merge"):
        text = (hooks_dir / name).read_text(encoding="utf-8")
        assert "doctor" in text
        assert text.rstrip().endswith("exit 0")


def test_install_requires_git_hooks_directory(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match=r"\.git/hooks"):
        install(tmp_path)
