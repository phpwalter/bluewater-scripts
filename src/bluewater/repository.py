from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Repository:
    root: Path
    profile: str


def find_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / "bluewater.yml").exists():
            return candidate
    raise RuntimeError("not inside a Bluewater repository")


def detect_profile(root: Path) -> str:
    markers: list[tuple[str, tuple[str, ...]]] = [
        ("python", ("pyproject.toml", "requirements.txt")),
        ("php", ("composer.json",)),
        ("javascript", ("package.json",)),
    ]
    matches = [name for name, files in markers if any((root / f).exists() for f in files)]
    if (root / "docs").is_dir() and not matches:
        return "documentation"
    if len(matches) > 1:
        return "mixed"
    return matches[0] if matches else "documentation"


def inspect_repository(root: Path, configured_profile: str = "auto") -> Repository:
    profile = detect_profile(root) if configured_profile == "auto" else configured_profile
    return Repository(root=root, profile=profile)
