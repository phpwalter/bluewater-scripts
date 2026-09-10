from __future__ import annotations

import argparse
from pathlib import Path

from bluewater import __version__
from bluewater.config import ConfigurationError, load_config
from bluewater.hooks import install as install_hooks
from bluewater.locale_guard import LocaleGuardError, run as run_locale_guard
from bluewater.repository import find_root, inspect_repository
from bluewater.validation import run_checks


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bluewater")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="inspect repository and dependencies")
    check = sub.add_parser("check", help="run deterministic governance checks")
    check.add_argument("--scope", choices=("changed", "all"), default="all")
    hooks = sub.add_parser("hooks", help="manage Git hooks")
    hooks.add_argument("action", choices=("install",))
    docs = sub.add_parser("docs", help="delegate documentation localization governance")
    docs.add_argument("action", choices=("check", "update", "scan"), default="check")
    sub.add_parser("repo", help="validate repository configuration and profile")
    return parser


def _context() -> tuple[Path, object, object]:
    root = find_root()
    config = load_config(root)
    repo = inspect_repository(root, config.repository_type)
    return root, config, repo


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
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
            return run_locale_guard(root, config.locale_guard, args.action)
        if args.command == "check":
            results = run_checks(repo, config, args.scope)
            for result in results:
                print(f"{'PASS' if result.ok else 'FAIL'} {result.name}: {result.detail}")
            return 0 if all(result.ok for result in results) else 1
    except (ConfigurationError, LocaleGuardError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    return 2
