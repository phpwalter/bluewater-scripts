from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    destination = root / "bluewater-diagnostics.json"
    proc = subprocess.run(
        [sys.executable, "-m", "bluewater", "ci", "validate", "--format", "json"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    payload_line = next((line for line in reversed(lines) if line.lstrip().startswith("{")), "")
    if payload_line:
        try:
            payload = json.loads(payload_line)
        except json.JSONDecodeError:
            payload = None
        if payload is not None:
            destination.write_text(
                json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )

    for line in lines:
        if line != payload_line:
            print(line)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")

    if not payload_line or not destination.is_file():
        print("Bluewater did not emit a valid JSON diagnostics envelope", file=sys.stderr)
        return 2
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
