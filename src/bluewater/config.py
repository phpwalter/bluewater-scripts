from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
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
    return BluewaterConfig(
        version=int(data["version"]),
        repository_type=str(repo.get("type", "auto")),
        required_version=repo.get("required_bluewater_version"),
        locale_guard=LocaleGuardConfig(
            enabled=bool(locale_guard.get("enabled", True)),
            path=str(locale_guard.get("path", "tools/locale-guard")),
            config=str(locale_guard.get("config", ".locale-guard.yml")),
        ),
        checks={str(key): bool(value) for key, value in data.get("checks", {}).items()},
    )
