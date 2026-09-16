from __future__ import annotations

import shutil
import subprocess
import sys

from bluewater.config import BluewaterConfig
from bluewater.hooks import status as hook_status
from bluewater.repository import Repository, detect_profile
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


def _relative_display(repo: Repository, path: object) -> str:
    return str(path).replace("\\", "/").replace(str(repo.root).replace("\\", "/") + "/", "")


def _locale_guard(repo: Repository, config: BluewaterConfig) -> CheckResult:
    if not config.locale_guard.enabled:
        return CheckResult("locale-guard", True, "disabled")
    script = repo.root / config.locale_guard.path / "locale_guard.py"
    cfg = repo.root / config.locale_guard.config
    missing: list[str] = []
    if not script.is_file():
        missing.append(_relative_display(repo, script))
    if not cfg.is_file():
        missing.append(_relative_display(repo, cfg))
    if missing:
        return CheckResult("locale-guard", False, f"missing: {', '.join(missing)}")
    return CheckResult(
        "locale-guard",
        True,
        f"{_relative_display(repo, script)} using {_relative_display(repo, cfg)}",
    )


def _resolved_profile(repo: Repository) -> CheckResult:
    detected = detect_profile(repo.root)
    detail = f"configured/resolved={repo.profile}; detected={detected}"
    return CheckResult("resolved-profile", True, detail)


def _active_checks(config: BluewaterConfig) -> CheckResult:
    known = (
        "structured_files",
        "markdown",
        "python_syntax",
        "php_syntax",
        "javascript_syntax",
        "locale_guard",
        "generated_files",
    )
    enabled = [name for name in known if config.checks.get(name, True)]
    disabled = [name for name in known if not config.checks.get(name, True)]
    detail = f"enabled={','.join(enabled) or 'none'}; disabled={','.join(disabled) or 'none'}"
    return CheckResult("active-checks", True, detail)


def _hook_state(repo: Repository) -> CheckResult:
    try:
        states = hook_status(repo.root)
    except RuntimeError as exc:
        return CheckResult("hooks", False, str(exc))
    custom = [item.name for item in states if item.state == "custom"]
    missing = [item.name for item in states if item.state == "missing"]
    ok = not custom and not missing
    detail = ", ".join(f"{item.name}={item.state}" for item in states)
    return CheckResult("hooks", ok, detail)


def _locale_guard_revision(repo: Repository, config: BluewaterConfig) -> CheckResult:
    if not config.locale_guard.enabled:
        return CheckResult("locale-guard-revision", True, "disabled")
    proc = subprocess.run(
        ["git", "submodule", "status", "--", config.locale_guard.path],
        cwd=repo.root,
        capture_output=True,
        text=True,
        check=False,
    )
    detail = proc.stdout.strip() or proc.stderr.strip() or "submodule status unavailable"
    ok = proc.returncode == 0 and bool(proc.stdout.strip()) and not proc.stdout.startswith("-")
    return CheckResult("locale-guard-revision", ok, detail)


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
                _hook_state(repo),
                _locale_guard(repo, config),
                _locale_guard_revision(repo, config),
            ]
        )
    return results


def doctor_checks(
    repo: Repository,
    config: BluewaterConfig,
    *,
    extended: bool = False,
) -> list[CheckResult]:
    results = [
        _python_runtime(),
        _git_available(),
        *repository_checks(repo, config),
        _locale_guard(repo, config),
    ]
    if extended:
        results.extend(
            [
                _resolved_profile(repo),
                _active_checks(config),
                _hook_state(repo),
                _locale_guard_revision(repo, config),
            ]
        )
    return results
