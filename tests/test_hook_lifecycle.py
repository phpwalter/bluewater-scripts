import subprocess
from pathlib import Path

import pytest

from bluewater.hooks import HOOKS, install, status, uninstall


def _git_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


def test_status_reports_missing_then_bluewater(tmp_path: Path) -> None:
    root = _git_repo(tmp_path)
    assert {item.state for item in status(root)} == {"missing"}
    install(root)
    assert {item.state for item in status(root)} == {"bluewater"}


def test_install_refuses_custom_hook_without_force(tmp_path: Path) -> None:
    root = _git_repo(tmp_path)
    hooks = root / ".git" / "hooks"
    custom = hooks / "pre-commit"
    custom.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="refusing to overwrite custom Git hook"):
        install(root)
    assert "echo custom" in custom.read_text(encoding="utf-8")


def test_force_replaces_custom_hook(tmp_path: Path) -> None:
    root = _git_repo(tmp_path)
    custom = root / ".git" / "hooks" / "pre-commit"
    custom.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")
    install(root, force=True)
    assert "command -v bluewater" in custom.read_text(encoding="utf-8")


def test_uninstall_removes_only_bluewater_hooks(tmp_path: Path) -> None:
    root = _git_repo(tmp_path)
    install(root)
    custom = root / ".git" / "hooks" / "pre-commit"
    custom.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")
    uninstall(root)
    assert custom.exists()
    for name in HOOKS:
        if name != "pre-commit":
            assert not (root / ".git" / "hooks" / name).exists()


def test_hook_installation_is_idempotent(tmp_path: Path) -> None:
    root = _git_repo(tmp_path)
    install(root)
    before = {
        name: (root / ".git" / "hooks" / name).read_bytes()
        for name in HOOKS
    }
    install(root)
    after = {
        name: (root / ".git" / "hooks" / name).read_bytes()
        for name in HOOKS
    }
    assert before == after
