from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from bluewater.config import LocaleGuardConfig


class LocaleGuardError(RuntimeError):
    pass


def command(root: Path, config: LocaleGuardConfig, action: str) -> list[str]:
    script = root / config.path / "locale_guard.py"
    if not script.is_file():
        raise LocaleGuardError(
            f"LocaleGuard is enabled but missing at {script}; initialize submodules first"
        )
    return [sys.executable, "-B", str(script), "--config", config.config, action]


def run(root: Path, config: LocaleGuardConfig, action: str = "check") -> int:
    cmd = command(root, config, action)
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(cmd, cwd=root, check=False, env=env).returncode
