from __future__ import annotations

import os
import shutil
from pathlib import Path


HOOKS = ("pre-commit", "pre-push", "post-checkout", "post-merge")


def install(root: Path) -> None:
    source = root / "hooks"
    target = root / ".git" / "hooks"
    if not target.is_dir():
        raise RuntimeError(".git/hooks not found; hooks can only be installed in a Git worktree")
    for name in HOOKS:
        src = source / name
        if not src.is_file():
            raise RuntimeError(f"hook template missing: {src}")
        dst = target / name
        shutil.copyfile(src, dst)
        try:
            os.chmod(dst, 0o755)
        except OSError:
            pass
