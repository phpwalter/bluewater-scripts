from __future__ import annotations

import os
from importlib.resources import as_file, files
from pathlib import Path

HOOKS = ("pre-commit", "pre-push", "post-checkout", "post-merge")


def install(root: Path) -> None:
    target = root / ".git" / "hooks"
    if not target.is_dir():
        raise RuntimeError(".git/hooks not found; hooks can only be installed in a Git worktree")

    templates = files("bluewater").joinpath("hook_templates")
    for name in HOOKS:
        resource = templates.joinpath(name)
        if not resource.is_file():
            raise RuntimeError(f"packaged hook template missing: {name}")
        with as_file(resource) as src:
            dst = target / name
            dst.write_bytes(src.read_bytes())
        try:
            os.chmod(dst, 0o755)
        except OSError:
            pass
