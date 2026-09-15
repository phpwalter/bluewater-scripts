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
