from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from importlib.resources import as_file, files
from pathlib import Path

HOOKS = ("pre-commit", "pre-push", "post-checkout", "post-merge")


@dataclass(frozen=True)
class HookStatus:
    name: str
    state: str


def hooks_directory(root: Path) -> Path:
    proc = subprocess.run(
        ["git", "rev-parse", "--git-path", "hooks"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("hooks can only be managed in a Git worktree")
    path = Path(proc.stdout.strip())
    if not path.is_absolute():
        path = root / path
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _template_bytes(name: str) -> bytes:
    resource = files("bluewater").joinpath("hook_templates", name)
    if not resource.is_file():
        raise RuntimeError(f"packaged hook template missing: {name}")
    with as_file(resource) as src:
        return src.read_bytes()


def status(root: Path) -> list[HookStatus]:
    target = hooks_directory(root)
    results: list[HookStatus] = []
    for name in HOOKS:
        dst = target / name
        if not dst.exists():
            state = "missing"
        elif dst.read_bytes() == _template_bytes(name):
            state = "bluewater"
        else:
            state = "custom"
        results.append(HookStatus(name, state))
    return results


def install(root: Path, *, force: bool = False) -> None:
    target = hooks_directory(root)
    for name in HOOKS:
        dst = target / name
        expected = _template_bytes(name)
        if dst.exists() and dst.read_bytes() != expected and not force:
            raise RuntimeError(
                f"refusing to overwrite custom Git hook: {dst}; rerun with --force to replace it"
            )
        dst.write_bytes(expected)
        try:
            os.chmod(dst, 0o755)
        except OSError:
            pass


def uninstall(root: Path) -> None:
    target = hooks_directory(root)
    for name in HOOKS:
        dst = target / name
        if dst.exists() and dst.read_bytes() == _template_bytes(name):
            dst.unlink()
