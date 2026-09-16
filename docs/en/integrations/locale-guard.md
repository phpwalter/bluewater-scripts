# LocaleGuard Integration

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

LocaleGuard owns documentation localization governance. Bluewater Scripts treats it as an immutable Git submodule at `tools/locale-guard` and delegates commands to its documented CLI.

The current foundation pins LocaleGuard commit `7c885d8fdc9128f855f25e6d760d4283300532e2` from LocaleGuard's `foundation` branch. The path and integration can be configured in `bluewater.yml`; the exact Git commit remains controlled by the parent repository's submodule pointer.

LocaleGuard owns:

- canonical/localized documentation tree comparison;
- translation coverage;
- missing-document reporting;
- README localization summaries;
- per-document language navigation;
- generated localization reports and flag assets.

Bluewater Scripts owns when those checks run and how their exit status participates in repository governance.

## Delegated commands

- `bluewater docs scan` delegates LocaleGuard `scan`.
- `bluewater docs update` delegates LocaleGuard `update`.
- `bluewater docs check` delegates LocaleGuard `check`.
- `bluewater docs validate` is an alias for the deterministic LocaleGuard `check` operation.

Bluewater passes the project-owned `.locale-guard.yml` path to LocaleGuard and propagates LocaleGuard's process exit code rather than reinterpreting localization results.

## Precedence

LocaleGuard runs only when both the integration and the Bluewater check are enabled. `integrations.locale_guard.enabled: false` prevents delegation regardless of the check switch. `checks.locale_guard: false` also suppresses validation even when the integration is available.

## Failure behavior

If LocaleGuard is enabled but the pinned script is unavailable, Bluewater fails closed. `doctor` reports the missing integration as a validation failure, while a direct `docs` command returns an execution/setup error. Non-zero LocaleGuard check results remain governance failures.

## Consumer setup

Consumers using the default path must initialize repository submodules before running documentation governance. Bluewater does not download, replace, or dynamically update LocaleGuard; dependency revision control remains a Git responsibility.
