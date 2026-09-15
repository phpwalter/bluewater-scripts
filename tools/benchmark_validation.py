from __future__ import annotations

import argparse
import statistics
import subprocess
import time
from pathlib import Path


def _run(root: Path, scope: str) -> float:
    start = time.perf_counter()
    proc = subprocess.run(
        ["python", "-m", "bluewater", "check", "--scope", scope],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed = time.perf_counter() - start
    if proc.returncode not in {0, 1}:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "benchmark execution failed")
    return elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Bluewater validation scopes")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--iterations", type=int, default=5)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.iterations < 1:
        parser.error("--iterations must be >= 1")

    for scope in ("changed", "all"):
        samples = [_run(root, scope) for _ in range(args.iterations)]
        print(
            f"{scope}: min={min(samples):.4f}s "
            f"median={statistics.median(samples):.4f}s max={max(samples):.4f}s"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
