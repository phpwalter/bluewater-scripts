import os
from pathlib import Path

import pytest

from bluewater.config import load_config
from bluewater.hooks import HOOKS, install
from bluewater.initialization import initialize
from bluewater.repository import find_root


def test_unicode_and_space_repository_path(tmp_path: Path) -> None:
    root = tmp_path / "Bluewater café repo"
    nested = root / "nested folder" / "deep"
    nested.mkdir(parents=True)
    initialize(root)
    assert find_root(nested) == root.resolve()
    assert load_config(root).repository_type == "documentation"


def test_crlf_configuration_is_accepted(tmp_path: Path) -> None:
    (tmp_path / "bluewater.yml").write_bytes(
        b"version: 1\r\nrepository:\r\n  type: documentation\r\n"
    )
    assert load_config(tmp_path).repository_type == "documentation"


def test_packaged_hook_templates_use_portable_lf_newlines(tmp_path: Path) -> None:
    hooks = tmp_path / ".git" / "hooks"
    hooks.mkdir(parents=True)
    install(tmp_path)
    for name in HOOKS:
        data = (hooks / name).read_bytes()
        assert b"\r\n" not in data
        assert data.startswith(b"#!/usr/bin/env sh\n")


def test_symlinked_start_path_resolves_to_repository_root(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    nested = root / "src"
    nested.mkdir(parents=True)
    (root / "bluewater.yml").write_text(
        "version: 1\nrepository:\n  type: documentation\n",
        encoding="utf-8",
    )
    link = tmp_path / "repo-link"
    try:
        link.symlink_to(root, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable on this platform")
    assert find_root(link / "src") == root.resolve()


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific executable convention")
def test_windows_hook_installation_does_not_require_posix_mode(tmp_path: Path) -> None:
    hooks = tmp_path / ".git" / "hooks"
    hooks.mkdir(parents=True)
    install(tmp_path)
    assert all((hooks / name).is_file() for name in HOOKS)
