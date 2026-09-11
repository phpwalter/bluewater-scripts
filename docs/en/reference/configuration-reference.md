# Configuration Reference

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

## version

Required integer. The current schema accepts version `1`.

## repository.type

Required. One of `auto`, `python`, `php`, `javascript`, `documentation`, or `mixed`.

When `repository.type` is `auto`, Bluewater derives the profile from repository markers. An explicit configured profile takes precedence over detected markers. This makes repository configuration authoritative while keeping `auto` deterministic for consumers that prefer convention-based detection.

## repository.required_bluewater_version

Optional semantic version constraint declared by a consumer. The validation engine evaluates the running Bluewater Scripts version against this constraint and fails the governance check when the requirement is not satisfied.

## checks

Boolean feature switches. Supported checks currently include:

- `structured_files`
- `markdown`
- `python_syntax`
- `php_syntax`
- `javascript_syntax`
- `locale_guard`
- `generated_files`

An explicit `false` disables that check. Language-specific syntax checks also require an applicable repository profile: Python runs for `python` and `mixed`, PHP for `php` and `mixed`, and JavaScript for `javascript` and `mixed`.

Unknown check names remain schema-valid by design so deterministic checks can be introduced without requiring a schema revision solely to add a boolean switch.

## integrations.locale_guard

`enabled` controls delegation. `path` locates the pinned LocaleGuard checkout. `config` identifies the project-owned LocaleGuard configuration file.

When LocaleGuard integration is disabled, Bluewater does not invoke LocaleGuard. When enabled, documentation governance remains delegated to LocaleGuard rather than reimplemented inside Bluewater Scripts.

## Precedence summary

Configuration is authoritative where the user has made an explicit choice:

1. An explicit `repository.type` overrides repository marker detection.
2. `repository.type: auto` delegates profile selection to deterministic marker detection.
3. An explicit check value of `false` disables that check even when the repository profile would otherwise make it applicable.
4. Integration-level `enabled: false` disables the corresponding integration before delegation occurs.

Unknown top-level, repository, or integration keys are rejected by schema validation.
