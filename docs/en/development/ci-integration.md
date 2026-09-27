# CI Integration

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

CI should execute the same governance engine used locally rather than reimplementing checks in workflow YAML.

## Required sequence

A release-quality pipeline should:

1. check out the repository and pinned submodules;
2. install the supported Python version and Bluewater Scripts dependencies;
3. run repository tests/static analysis owned by the project;
4. run `bluewater ci validate`;
5. build distribution artifacts when applicable;
6. verify installation from the built artifact rather than only the source tree.

## Machine-readable output

`bluewater ci validate --format json` is intended for CI integrations and produces stable check identifiers and aggregate status. Process exit codes remain authoritative: `0` pass, `1` governance failure, `2` execution/setup failure.

## Local parity

`bluewater check --scope all` and `bluewater ci validate` use the complete repository validation scope. Pre-push should use the same complete scope; pre-commit may use `--scope changed` for developer feedback while repository-wide invariants remain active.
