# Upgrading Bluewater Scripts

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Treat a Bluewater upgrade as a governance change rather than a routine dependency bump.

## Before upgrading

- review `CHANGELOG.md`;
- confirm the target package version satisfies repository policy;
- review configuration-schema and diagnostic-format changes;
- update the pinned LocaleGuard revision separately when needed.

## Upgrade procedure

1. update Bluewater Scripts in a dedicated branch;
2. run `bluewater --version`;
3. run `bluewater doctor`;
4. run `bluewater repo validate`;
5. run the complete project test suite;
6. run `bluewater check --scope all`;
7. run LocaleGuard validation;
8. rebuild and verify distribution artifacts where applicable;
9. commit generated documentation changes separately from policy changes when practical.

## Breaking changes

A package major version may introduce a breaking CLI or policy contract. Configuration and machine-readable diagnostic formats have independent version identifiers; consumers should migrate those contracts explicitly rather than assuming package-version equivalence.

## Rollback

If an upgrade changes repository behavior unexpectedly, restore the previous package revision and configuration constraint together. Do not suppress failing governance checks merely to complete the upgrade.
