# Configuration Reference

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

## version

Required integer. Foundation schema accepts version `1`.

## repository.type

Required. One of `auto`, `python`, `php`, `javascript`, `documentation`, or `mixed`.

## repository.required_bluewater_version

Optional version constraint declared by a consumer. Foundation records the field; semantic constraint enforcement is part of the next hardening increment.

## checks

Boolean feature switches. Foundation defines `structured_files`, `locale_guard`, and `generated_files`.

## integrations.locale_guard

`enabled` controls delegation. `path` locates the immutable LocaleGuard checkout. `config` identifies the project-owned LocaleGuard configuration file.

Unknown top-level, repository, or integration keys are rejected by schema validation. Check names are intentionally extensible so new deterministic checks do not require a schema revision solely to add a boolean switch.
