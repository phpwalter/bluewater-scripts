from __future__ import annotations

import argparse
from pathlib import Path

from bluewater import __version__
from bluewater.config import BluewaterConfig, ConfigurationError, load_config
from bluewater.hooks import install as install_hooks
from bluewater.initialization import initialize
from bluewater.locale_guard import LocaleGuardError
from bluewater.locale_guard import run as run_locale_guard
from bluewater.repository import Repository, find_root, inspect_repository
from bluewater.validation import CheckResult, run_checks


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bluewater")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a project-owned bluewater.yml")
    init.add_argument("--force", action="store_true")
    sub.add_parser("doctor", help="inspect repository and dependencies")

    check = sub.add_parser("check", help="run deterministic governance checks")
    check.add_argument("--scope", choices=("changed", "all"), default="all")

    hooks = sub.add_parser("hooks", help="manage Git hooks")
    hooks.add_argument("action", choices=("install",))

    docs = sub.add_parser("docs", help="delegate documentation localization governance")
    docs.add_argument("action", choices=("check", "update", "scan", "validate"), default="check")

    repo = sub.add_parser("repo", help="repository operations")
    repo.add_argument("action", choices=("validate",))

    ci = sub.add_parser("ci", help="CI operations")
    ci.add_argument("action", choices=("validate",))
    return parser


def _context() -> tuple[Path, BluewaterConfig, Repository]:
    root = find_root()
    config = load_config(root)
    repo = inspect_repository(root, config.repository_type)
    return root, config, repo


def _print_results(results: list[CheckResult]) -> int:
    ok = True
    for result in results:
        print(f"{'PASS' if result.ok else 'FAIL'} {result.name}: {result.detail}")
        ok = ok and result.ok
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "init":
            path = initialize(Path.cwd().resolve(), force=args.force)
            print(f"created {path}")
            return 0

        root, config, repo = _context()
        if args.command == "doctor":
            print(f"root: {root}")
            print(f"profile: {repo.profile}")
            print(f"LocaleGuard: {'enabled' if config.locale_guard.enabled else 'disabled'}")
            return 0
        if args.command == "repo":
            print(f"repository valid: {repo.profile}")
            return 0
        if args.command == "hooks":
            install_hooks(root)
            print("Git hooks installed")
            return 0
        if args.command == "docs":
            if not config.locale_guard.enabled:
                print("LocaleGuard disabled")
                return 0
            action = "check" if args.action == "validate" else args.action
            return run_locale_guard(root, config.locale_guard, action)
        if args.command == "ci":
            return _print_results(run_checks(repo, config, "all"))
        if args.command == "check":
            return _print_results(run_checks(repo, config, args.scope))
    except (ConfigurationError, LocaleGuardError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    return 2
