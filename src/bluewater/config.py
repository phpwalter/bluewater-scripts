from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import cast

import yaml
from jsonschema import Draft202012Validator


class ConfigurationError(ValueError):
    """Raised when bluewater.yml is missing or invalid."""


@dataclass(frozen=True)
class LocaleGuardConfig:
    enabled: bool = True
    path: str = "tools/locale-guard"
    config: str = ".locale-guard.yml"


@dataclass(frozen=True)
class BluewaterConfig:
    version: int
    repository_type: str = "auto"
    required_version: str | None = None
    locale_guard: LocaleGuardConfig = field(default_factory=LocaleGuardConfig)
    checks: dict[str, bool] = field(default_factory=dict)


def _schema() -> dict[str, object]:
    resource = files("bluewater").joinpath("bluewater.schema.json")
    return cast(dict[str, object], json.loads(resource.read_text(encoding="utf-8")))


def _repository_relative(value: str, field_name: str) -> str:
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    parts = {*posix.parts, *windows.parts}
    if posix.is_absolute() or windows.is_absolute() or ".." in parts:
        raise ConfigurationError(f"{field_name} must be a repository-relative path without '..'")
    return value


def load_config(root: Path) -> BluewaterConfig:
    path = root / "bluewater.yml"
    if not path.is_file():
        raise ConfigurationError(f"required configuration not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigurationError("bluewater.yml must contain a YAML mapping")

    errors = sorted(Draft202012Validator(_schema()).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ConfigurationError(f"invalid bluewater.yml: {details}")

    repo = data.get("repository", {})
    integrations = data.get("integrations", {})
    locale_guard = integrations.get("locale_guard", {})
    locale_path = _repository_relative(
        str(locale_guard.get("path", "tools/locale-guard")),
        "integrations.locale_guard.path",
    )
    locale_config = _repository_relative(
        str(locale_guard.get("config", ".locale-guard.yml")),
        "integrations.locale_guard.config",
    )
    return BluewaterConfig(
        version=int(data["version"]),
        repository_type=str(repo.get("type", "auto")),
        required_version=repo.get("required_bluewater_version"),
        locale_guard=LocaleGuardConfig(
            enabled=bool(locale_guard.get("enabled", True)),
            path=locale_path,
            config=locale_config,
        ),
        checks={str(key): bool(value) for key, value in data.get("checks", {}).items()},
    )
