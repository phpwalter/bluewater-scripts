from __future__ import annotations

import shutil
import subprocess
import sys

from bluewater.config import BluewaterConfig
from bluewater.hooks import HOOKS
from bluewater.repository import Repository
from bluewater.validation import CheckResult, check_version

MINIMUM_PYTHON = (3, 12)


def _python_runtime() -> CheckResult:
    current = sys.version_info[:3]
    ok = current >= MINIMUM_PYTHON
    detail = f"Python {current[0]}.{current[1]}.{current[2]}"
    if not ok:
        detail += f"; requires >= {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}"
    return CheckResult("python-runtime", ok, detail)


def _git_available() -> CheckResult:
    executable = shutil.which("git")
    if executable is None:
        return CheckResult("git", False, "git executable not found on PATH")
    proc = subprocess.run(
        [executable, "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    detail = proc.stdout.strip() or proc.stderr.strip() or executable
    return CheckResult("git", proc.returncode == 0, detail)


def _repository_metadata(repo: Repository) -> CheckResult:
    marker = repo.root / ".git"
    if not marker.exists():
        return CheckResult("repository", False, f"missing Git metadata: {marker}")
    return CheckResult("repository", True, str(repo.root))


def _configuration(repo: Repository) -> CheckResult:
    path = repo.root / "bluewater.yml"
    return CheckResult(
        "configuration",
        path.is_file(),
        str(path) if path.is_file() else f"missing required configuration: {path}",
    )


def _profile(repo: Repository) -> CheckResult:
    expected: dict[str, tuple[str, ...]] = {
        "python": ("pyproject.toml", "requirements.txt"),
        "php": ("composer.json",),
        "javascript": ("package.json",),
        "documentation": ("docs",),
    }
    if repo.profile == "mixed":
        return CheckResult("profile", True, "mixed repository profile")
    markers = expected.get(repo.profile)
    if markers is None:
        return CheckResult("profile", False, f"unsupported repository profile: {repo.profile}")
    present = [name for name in markers if (repo.root / name).exists()]
    if present:
        return CheckResult("profile", True, f"{repo.profile}: {', '.join(present)}")
    return CheckResult(
        "profile",
        False,
        f"{repo.profile} profile has none of its expected markers: {', '.join(markers)}",
    )


def _locale_guard(repo: Repository, config: BluewaterConfig) -> CheckResult:
    if not config.locale_guard.enabled:
        return CheckResult("locale-guard", True, "disabled")
    script = repo.root / config.locale_guard.path / "locale_guard.py"
    cfg = repo.root / config.locale_guard.config
    missing: list[str] = []
    if not script.is_file():
        missing.append(str(script))
    if not cfg.is_file():
        missing.append(str(cfg))
    if missing:
        return CheckResult("locale-guard", False, f"missing: {', '.join(missing)}")
    return CheckResult("locale-guard", True, f"{script} using {cfg}")


def _hook_installation(repo: Repository) -> CheckResult:
    hooks_dir = repo.root / ".git" / "hooks"
    missing = [name for name in HOOKS if not (hooks_dir / name).is_file()]
    if missing:
        return CheckResult("hooks", False, f"missing Bluewater hook paths: {', '.join(missing)}")
    return CheckResult("hooks", True, f"installed: {', '.join(HOOKS)}")


def _locale_guard_submodule(repo: Repository, config: BluewaterConfig) -> CheckResult:
    if not config.locale_guard.enabled:
        return CheckResult("locale-guard-submodule", True, "disabled")
    proc = subprocess.run(
        ["git", "submodule", "status", "--", config.locale_guard.path],
        cwd=repo.root,
        capture_output=True,
        text=True,
        check=False,
    )
    detail = proc.stdout.strip() or proc.stderr.strip() or "submodule not registered"
    ok = proc.returncode == 0 and bool(proc.stdout.strip()) and not proc.stdout.startswith("-")
    return CheckResult("locale-guard-submodule", ok, detail)


def repository_checks(
    repo: Repository,
    config: BluewaterConfig,
    *,
    extended: bool = False,
) -> list[CheckResult]:
    results = [
        _repository_metadata(repo),
        _configuration(repo),
        _profile(repo),
        check_version(config),
    ]
    if extended:
        results.extend(
            [
                _hook_installation(repo),
                _locale_guard(repo, config),
                _locale_guard_submodule(repo, config),
            ]
        )
    return results


def doctor_checks(repo: Repository, config: BluewaterConfig) -> list[CheckResult]:
    return [
        _python_runtime(),
        _git_available(),
        *repository_checks(repo, config),
        _locale_guard(repo, config),
    ]
