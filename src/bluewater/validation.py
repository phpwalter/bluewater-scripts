from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from bluewater.config import BluewaterConfig
from bluewater.locale_guard import LocaleGuardError
from bluewater.locale_guard import run as run_locale_guard
from bluewater.repository import Repository
from bluewater.versioning import satisfies


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def _enabled(config: BluewaterConfig, name: str, default: bool = True) -> bool:
    return config.checks.get(name, default)


def _changed_files(repo: Repository) -> list[Path]:
    commands = (
        ["git", "diff", "--name-only", "--cached"],
        ["git", "diff", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    names: set[str] = set()
    for command in commands:
        proc = subprocess.run(
            command,
            cwd=repo.root,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or f"failed to determine changed files: {command}")
        names.update(line.strip() for line in proc.stdout.splitlines() if line.strip())
    return sorted(
        (repo.root / name for name in names if (repo.root / name).is_file()),
        key=lambda path: path.as_posix(),
    )


def _paths(repo: Repository, suffixes: tuple[str, ...], changed: list[Path] | None) -> list[Path]:
    if changed is not None:
        return [path for path in changed if path.suffix.lower() in suffixes and ".git" not in path.parts]
    paths: list[Path] = []
    for suffix in suffixes:
        paths.extend(path for path in repo.root.rglob(f"*{suffix}") if ".git" not in path.parts)
    return sorted(set(paths), key=lambda path: path.as_posix())


def check_version(config: BluewaterConfig) -> CheckResult:
    ok, detail = satisfies(config.required_version)
    return CheckResult("bluewater-version", ok, detail)


def check_structured_files(
    repo: Repository,
    config: BluewaterConfig,
    changed: list[Path] | None = None,
) -> CheckResult:
    if not _enabled(config, "structured_files"):
        return CheckResult("structured-files", True, "disabled")
    try:
        for path in _paths(repo, (".json",), changed):
            json.loads(path.read_text(encoding="utf-8"))
        for path in _paths(repo, (".yml", ".yaml"), changed):
            yaml.safe_load(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, yaml.YAMLError) as exc:
        return CheckResult("structured-files", False, str(exc))
    return CheckResult("structured-files", True, "JSON/YAML syntax valid")


def check_markdown(
    repo: Repository,
    config: BluewaterConfig,
    changed: list[Path] | None = None,
) -> CheckResult:
    if not _enabled(config, "markdown"):
        return CheckResult("markdown", True, "disabled")
    problems: list[str] = []
    for path in _paths(repo, (".md",), changed):
        if "tools" in path.relative_to(repo.root).parts:
            continue
        text = path.read_text(encoding="utf-8")
        if text and not text.startswith("#"):
            problems.append(f"{path.relative_to(repo.root)}: missing leading heading")
        if "\t" in text:
            problems.append(f"{path.relative_to(repo.root)}: tab character found")
    if problems:
        return CheckResult("markdown", False, "; ".join(problems))
    return CheckResult("markdown", True, "Markdown baseline valid")


def check_python_syntax(
    repo: Repository,
    config: BluewaterConfig,
    changed: list[Path] | None = None,
) -> CheckResult:
    if repo.profile not in {"python", "mixed"} or not _enabled(config, "python_syntax"):
        return CheckResult("python-syntax", True, "not applicable or disabled")
    if changed is not None:
        python_files = [str(path.relative_to(repo.root)) for path in changed if path.suffix == ".py"]
        if not python_files:
            return CheckResult("python-syntax", True, "no changed Python files")
        proc = subprocess.run(
            [sys.executable, "-m", "py_compile", *python_files],
            cwd=repo.root,
            capture_output=True,
            text=True,
            check=False,
        )
    else:
        proc = subprocess.run(
            [sys.executable, "-m", "compileall", "-q", "src", "tests"],
            cwd=repo.root,
            capture_output=True,
            text=True,
            check=False,
        )
    detail = proc.stderr.strip() or "Python syntax valid"
    return CheckResult("python-syntax", proc.returncode == 0, detail)


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
        detail = proc.stderr.strip() or "git status failed"
        return CheckResult("generated-files", False, detail)
    detail = proc.stdout.strip() or "clean"
    return CheckResult("generated-files", not bool(proc.stdout.strip()), detail)


def run_checks(repo: Repository, config: BluewaterConfig, scope: str = "all") -> list[CheckResult]:
    if scope not in {"all", "changed"}:
        raise ValueError(f"unsupported validation scope: {scope}")
    changed = _changed_files(repo) if scope == "changed" else None
    return [
        check_version(config),
        check_structured_files(repo, config, changed),
        check_markdown(repo, config, changed),
        check_python_syntax(repo, config, changed),
        check_locale_guard(repo, config),
        check_git_clean_generated(repo, config),
    ]
