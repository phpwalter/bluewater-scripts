from __future__ import annotations

from pathlib import Path

from bluewater.repository import detect_profile

CONFIG_TEMPLATE = """version: 1

repository:
  type: {profile}
  required_bluewater_version: \">=1.0,<2.0\"

checks:
  structured_files: true
  markdown: true
  locale_guard: true
  generated_files: true

integrations:
  locale_guard:
    enabled: true
    path: tools/locale-guard
    config: .locale-guard.yml
"""


def initialize(root: Path, *, force: bool = False) -> Path:
    path = root / "bluewater.yml"
    if path.exists() and not force:
        raise RuntimeError(f"configuration already exists: {path}")
    profile = detect_profile(root)
    path.write_text(CONFIG_TEMPLATE.format(profile=profile), encoding="utf-8")
    return path
