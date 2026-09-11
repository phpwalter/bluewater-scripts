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


def verify_wheel(path: Path) -> int:
    if not path.is_file():
        print(f"distribution artifact not found: {path}", file=sys.stderr)
        return 2

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())

    missing = sorted(REQUIRED_FILES - names)
    if missing:
        print("wheel is missing required runtime files:", file=sys.stderr)
        for name in missing:
            print(f"- {name}", file=sys.stderr)
        return 1

    print(f"verified distribution contents: {path.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: verify_distribution.py <wheel-path>", file=sys.stderr)
        return 2
    return verify_wheel(Path(args[0]))


if __name__ == "__main__":
    raise SystemExit(main())
