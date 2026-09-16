# Troubleshooting

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

## Exit code 2

Exit code `2` means Bluewater could not execute the requested operation. Check repository root detection, `bluewater.yml` validity, required integration paths, and the availability of external runtimes.

## LocaleGuard is enabled but missing

Initialize repository submodules and verify `integrations.locale_guard.path`. Bluewater intentionally does not download LocaleGuard during validation.

## PHP or Node executable not found

Language runtime checks fail only when the corresponding validator is enabled and applicable to the resolved repository profile. Install the runtime or explicitly disable the validator when it is not part of repository policy.

## Generated files are dirty

Run the owning generator, normally `bluewater docs update` for LocaleGuard-managed documentation, review the generated changes, and commit them.

## Hooks cannot find Bluewater

Activate or expose the environment in which `bluewater-scripts` is installed. Blocking hooks fail closed when neither the `bluewater` command nor a usable Python module invocation is available.

## Repository profile looks wrong

Run `bluewater doctor` and inspect `repository.type` in `bluewater.yml`. An explicit profile is authoritative; `auto` uses deterministic repository markers.

## Version compatibility failure

Compare the installed `bluewater --version` value with `repository.required_bluewater_version`. Upgrade/downgrade Bluewater or intentionally revise the repository constraint; do not bypass the check in CI.
