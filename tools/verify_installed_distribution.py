from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def _wheel_from(path: Path) -> Path:
    if path.is_file() and path.suffix == ".whl":
        return path.resolve()
    if path.is_dir():
        wheels = sorted(path.glob("*.whl"))
        if len(wheels) == 1:
            return wheels[0].resolve()
        if not wheels:
            raise RuntimeError(f"no wheel found in {path}")
        raise RuntimeError(f"expected one wheel in {path}, found {len(wheels)}")
    raise RuntimeError(f"wheel path does not exist: {path}")


def _venv_python(root: Path) -> Path:
    if os.name == "nt":
        return root / "Scripts" / "python.exe"
    return root / "bin" / "python"


def _venv_bluewater(root: Path) -> Path:
    if os.name == "nt":
        return root / "Scripts" / "bluewater.exe"
    return root / "bin" / "bluewater"


def verify_installed_distribution(path: Path) -> int:
    try:
        wheel = _wheel_from(path)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="bluewater-wheel-") as temp:
        temp_root = Path(temp)
        env_root = temp_root / "venv"
        work_root = temp_root / "consumer"
        work_root.mkdir()

        venv.EnvBuilder(with_pip=True).create(env_root)
        python = _venv_python(env_root)
        bluewater = _venv_bluewater(env_root)

        subprocess.run(
            [str(python), "-m", "pip", "install", str(wheel)],
            cwd=work_root,
            check=True,
        )

        version = subprocess.run(
            [str(bluewater), "--version"],
            cwd=work_root,
            check=True,
            capture_output=True,
            text=True,
        )
        if "1.0.0.dev0" not in version.stdout:
            print(
                f"installed CLI reported unexpected version: {version.stdout.strip()}",
                file=sys.stderr,
            )
            return 1

        config_path = work_root / "bluewater.yml"
        config_path.write_text(
            "version: 1\nrepository:\n  type: documentation\n",
            encoding="utf-8",
        )

        probe = """
from importlib.resources import files
from pathlib import Path
from bluewater.config import load_config

root = Path.cwd()
config = load_config(root)
assert config.repository_type == "documentation"
assert config.locale_guard.enabled is True
assert config.locale_guard.path == "tools/locale-guard"
assert config.locale_guard.config == ".locale-guard.yml"

package = files("bluewater")
assert package.joinpath("bluewater.schema.json").is_file()
for name in ("post-checkout", "post-merge", "pre-commit", "pre-push"):
    assert package.joinpath("hook_templates", name).is_file(), name
"""
        subprocess.run(
            [str(python), "-c", probe],
            cwd=work_root,
            check=True,
        )

    print(f"verified installed distribution: {wheel.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: verify_installed_distribution.py <wheel-or-dist-dir>", file=sys.stderr)
        return 2
    return verify_installed_distribution(Path(args[0]))


if __name__ == "__main__":
    raise SystemExit(main())
