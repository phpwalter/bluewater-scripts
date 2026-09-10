from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

from bluewater.config import BluewaterConfig
from bluewater.locale_guard import LocaleGuardError, run as run_locale_guard
from bluewater.repository import Repository


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def _enabled(config: BluewaterConfig, name: str, default: bool = True) -> bool:
    return config.checks.get(name, default)


def check_structured_files(repo: Repository, config: BluewaterConfig) -> CheckResult:
    if not _enabled(config, "structured_files"):
        return CheckResult("structured-files", True, "disabled")
    try:
        for path in repo.root.rglob("*.json"):
            if ".git" not in path.parts:
                json.loads(path.read_text(encoding="utf-8"))
        for path in list(repo.root.rglob("*.yml")) + list(repo.root.rglob("*.yaml")):
            if ".git" not in path.parts:
                yaml.safe_load(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, yaml.YAMLError) as exc:
        return CheckResult("structured-files", False, str(exc))
    return CheckResult("structured-files", True, "JSON/YAML syntax valid")


def check_locale_guard(repo: Repository, config: BluewaterConfig) -> CheckResult:
    if not config.locale_guard.enabled or not _enabled(config, "locale_guard"):
        return CheckResult("locale-guard", True, "disabled")
    try:
        rc = run_locale_guard(repo.root, config.locale_guard, "check")
    except LocaleGuardError as exc:
        return CheckResult("locale-guard", False, str(exc))
    return CheckResult("locale-guard", rc == 0, f"exit code {rc}")


def check_git_clean_generated(repo: Repository, config: BluewaterConfig) -> CheckResult:
    if not _enabled(config, "generated_files"):
        return CheckResult("generated-files", True, "disabled")
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--", "docs/_generated", "README.md"],
        cwd=repo.root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return CheckResult("generated-files", False, proc.stderr.strip() or "git status failed")
    return CheckResult("generated-files", not bool(proc.stdout.strip()), proc.stdout.strip() or "clean")


def run_checks(repo: Repository, config: BluewaterConfig, scope: str = "all") -> list[CheckResult]:
    _ = scope  # reserved for changed-file optimization; contract is stable from v1
    return [
        check_structured_files(repo, config),
        check_locale_guard(repo, config),
        check_git_clean_generated(repo, config),
    ]
