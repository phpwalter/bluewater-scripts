from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REQUIRED_FILES = {
    "bluewater/bluewater.schema.json",
    "bluewater/hook_templates/post-checkout",
    "bluewater/hook_templates/post-merge",
    "bluewater/hook_templates/pre-commit",
    "bluewater/hook_templates/pre-push",
}


def resolve_wheel(path: Path) -> Path:
    if path.is_file():
        return path
    if path.is_dir():
        wheels = sorted(path.glob("*.whl"))
        if len(wheels) == 1:
            return wheels[0]
        if not wheels:
            raise ValueError(f"no wheel found in distribution directory: {path}")
        raise ValueError(f"expected exactly one wheel in {path}, found {len(wheels)}")
    raise ValueError(f"distribution artifact not found: {path}")


def verify_wheel(path: Path) -> int:
    try:
        wheel = resolve_wheel(path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())

    missing = sorted(REQUIRED_FILES - names)
    if missing:
        print("wheel is missing required runtime files:", file=sys.stderr)
        for name in missing:
            print(f"- {name}", file=sys.stderr)
        return 1

    print(f"verified distribution contents: {wheel.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: verify_distribution.py <wheel-path-or-directory>", file=sys.stderr)
        return 2
    return verify_wheel(Path(args[0]))


if __name__ == "__main__":
    raise SystemExit(main())
