from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

HOOKS = ("pre-commit", "pre-push", "post-checkout", "post-merge")


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


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _expected_version() -> str:
    root = Path(__file__).resolve().parents[1]
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def verify_installed_distribution(path: Path) -> int:
    try:
        wheel = _wheel_from(path)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    expected_version = _expected_version()
    with tempfile.TemporaryDirectory(prefix="bluewater-wheel-") as temp:
        temp_root = Path(temp)
        env_root = temp_root / "venv"
        work_root = temp_root / "consumer"
        work_root.mkdir()

        venv.EnvBuilder(with_pip=True).create(env_root)
        python = _venv_python(env_root)
        bluewater = _venv_bluewater(env_root)

        _run([str(python), "-m", "pip", "install", str(wheel)], cwd=work_root)

        version = _run([str(bluewater), "--version"], cwd=work_root)
        if version.stdout.strip() != expected_version:
            print(
                "installed CLI reported unexpected version: "
                f"{version.stdout.strip()} (expected {expected_version})",
                file=sys.stderr,
            )
            return 1

        _run(["git", "init", "-q"], cwd=work_root)

        first_init = _run([str(bluewater), "init"], cwd=work_root)
        config_path = work_root / "bluewater.yml"
        if not config_path.is_file() or "created" not in first_init.stdout:
            print("bluewater init did not create bluewater.yml", file=sys.stderr)
            return 1

        first_config = config_path.read_bytes()
        _run([str(bluewater), "init", "--force"], cwd=work_root)
        if config_path.read_bytes() != first_config:
            print("bluewater init --force is not deterministic", file=sys.stderr)
            return 1

        second_init = subprocess.run(
            [str(bluewater), "init"],
            cwd=work_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if second_init.returncode != 2 or "already exists" not in second_init.stdout:
            print("bluewater init did not protect existing configuration", file=sys.stderr)
            return 1

        _run([str(bluewater), "hooks", "install"], cwd=work_root)

        probe = """
import os
from importlib.resources import files
from pathlib import Path
from bluewater.config import load_config

root = Path.cwd()
config = load_config(root)
assert config.repository_type == "documentation"
assert config.required_version == ">=1.0.0.dev0,<2.0"
assert config.locale_guard.enabled is True
assert config.locale_guard.path == "tools/locale-guard"
assert config.locale_guard.config == ".locale-guard.yml"
assert config.checks == {
    "structured_files": True,
    "markdown": True,
    "locale_guard": True,
    "generated_files": True,
}

package = files("bluewater")
assert package.joinpath("bluewater.schema.json").is_file()
hooks = ("pre-commit", "pre-push", "post-checkout", "post-merge")
for name in hooks:
    resource = package.joinpath("hook_templates", name)
    assert resource.is_file(), name
    installed = root / ".git" / "hooks" / name
    assert installed.is_file(), name
    assert installed.read_bytes() == resource.read_bytes(), name
    if os.name != "nt":
        assert os.access(installed, os.X_OK), name
"""
        _run([str(python), "-c", probe], cwd=work_root)

        hook_snapshot = {
            name: (work_root / ".git" / "hooks" / name).read_bytes() for name in HOOKS
        }
        _run([str(bluewater), "hooks", "install"], cwd=work_root)
        for name, expected in hook_snapshot.items():
            if (work_root / ".git" / "hooks" / name).read_bytes() != expected:
                print(f"hook installation is not deterministic: {name}", file=sys.stderr)
                return 1

    print(f"verified installed distribution and consumer initialization: {wheel.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: verify_installed_distribution.py <wheel-or-dist-dir>", file=sys.stderr)
        return 2
    return verify_installed_distribution(Path(args[0]))


if __name__ == "__main__":
    raise SystemExit(main())
