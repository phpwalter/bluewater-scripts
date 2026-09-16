from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

OWNED_TOOL_PATHS = (
    "tools/verify_distribution.py",
    "tools/verify_installed_distribution.py",
    "tools/benchmark_validation.py",
    "tools/release_check.py",
)


def _run(root: Path, *command: str) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=root, check=True)


def _clean_dist(root: Path) -> None:
    for name in ("build", "dist"):
        path = root / name
        if path.exists():
            shutil.rmtree(path)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    python = sys.executable
    _clean_dist(root)

    _run(root, python, "-m", "ruff", "check", "src", "tests", *OWNED_TOOL_PATHS)
    _run(
        root,
        python,
        "-m",
        "mypy",
        "src/bluewater",
        "tools/verify_distribution.py",
        "tools/verify_installed_distribution.py",
    )
    _run(
        root,
        python,
        "-m",
        "pytest",
        "--cov=bluewater",
        "--cov-branch",
        "--cov-report=term-missing",
    )
    _run(root, python, "-m", "bluewater", "doctor")
    _run(root, python, "-m", "bluewater", "repo", "validate")
    _run(root, python, "-m", "bluewater", "check", "--scope", "all")
    _run(root, python, "-m", "bluewater", "ci", "validate", "--format", "json")
    _run(root, python, "-m", "bluewater", "docs", "check")
    _run(root, python, "-m", "build")

    distributions = sorted((root / "dist").iterdir())
    if not distributions:
        raise RuntimeError("build produced no distribution artifacts")
    _run(root, python, "-m", "twine", "check", *(str(path) for path in distributions))

    _run(root, python, "tools/verify_distribution.py", "dist")
    _run(root, python, "tools/verify_installed_distribution.py", "dist")

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    if status.stdout.strip():
        print("release readiness left the repository dirty:", file=sys.stderr)
        print(status.stdout, file=sys.stderr)
        return 1

    print("Bluewater release-readiness checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
