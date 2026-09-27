# Version and Compatibility Governance

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Bluewater Scripts uses Semantic Versioning for the package and independently versions durable machine-readable contracts when necessary.

## Package version

The package version is authoritative only when these three locations agree:

- `VERSION`
- `project.version` in `pyproject.toml`
- `bluewater.__version__`

CI tests fail on any drift.

## Prereleases

Development builds use a PEP 440 prerelease/development suffix such as `1.0.0.dev0`. The suffix is removed only as part of the release branch/tranche after the complete release-readiness suite succeeds.

## Configuration schema

`bluewater.yml` has its own integer schema version. A breaking configuration change requires a new configuration schema version and an explicit migration path. Package minor releases must not silently reinterpret an existing configuration version.

## Diagnostic protocol

Machine-readable diagnostic output is a public automation contract. Breaking changes require a new diagnostic format version; check identifiers within a format version are stable protocol names.

## Deprecation

Behavior scheduled for removal must first be documented as deprecated in a non-breaking release. Deprecation notices must identify the replacement behavior and the earliest package version in which removal may occur.

## Release criteria

A stable release requires synchronized version metadata, a clean changelog entry, complete CI on every supported platform/Python pair, package build/install verification, LocaleGuard validation, and a clean repository after all generated artifacts are refreshed.
