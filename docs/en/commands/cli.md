# CLI Commands

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

## Exit codes

Bluewater commands use a stable process contract:

- `0` means the command completed successfully and all requested governance checks passed.
- `1` means the command executed correctly but one or more governance or repository validation checks failed.
- `2` means Bluewater could not execute the requested operation because configuration, repository context, a required integration, or another prerequisite was missing or invalid.

This distinction is intentional. CI systems can treat exit code `1` as a policy failure and exit code `2` as an execution or repository-setup failure rather than collapsing both cases into the same condition.

## Machine-readable output

`doctor`, `repo validate`, `check`, and `ci validate` accept `--format text` or `--format json`. Text remains the default for interactive use.

JSON mode emits one deterministic JSON object on standard output:

```json
{"checks":[{"detail":"...","name":"repository","ok":true}],"ok":true}
```

The top-level `ok` value is `true` only when every emitted check passed. `checks` preserves the documented execution order. Each check object contains exactly the stable fields `name`, `ok`, and `detail`.

JSON serialization is compact and key-sorted so repeated executions with identical check results produce identical output bytes. Exit-code semantics do not change in JSON mode: `0` is success, `1` is a completed validation with one or more failed checks, and `2` remains an execution/configuration failure.

Check names are part of the automation contract. Current repository diagnostics use `repository`, `configuration`, `profile`, and `bluewater-version`. `doctor` prepends `python-runtime` and `git` and appends `locale-guard`. Full governance validation emits `bluewater-version`, `structured-files`, `markdown`, `python-syntax`, `php-syntax`, `javascript-syntax`, `locale-guard`, and `generated-files` in that order.

## init

`bluewater init` creates a repository-owned `bluewater.yml` using the detected repository profile. It fails with exit code `2` if configuration already exists unless `--force` is supplied.

## doctor

`bluewater doctor` reports Python and Git availability, repository metadata, configuration state, resolved profile, Bluewater version compatibility, and LocaleGuard state. A failed diagnostic check returns `1`; an unreadable or invalid Bluewater configuration returns `2`.

Use `bluewater doctor --format json` when another tool needs structured diagnostics.

## repo validate

`bluewater repo validate` validates repository metadata, configuration presence, the resolved repository profile, and Bluewater version compatibility. Validation failures return `1`; configuration or context errors that prevent validation return `2`.

Use `bluewater repo validate --format json` for deterministic repository-validation output.

## check

`bluewater check --scope changed` is the lightweight developer path used by pre-commit. It discovers staged, unstaged, and untracked files and limits structured-file, Markdown, and language syntax validation to those files. Repository-wide invariants, including version compatibility, LocaleGuard state, and generated-artifact cleanliness, remain enforced because they can be invalidated indirectly by a local change.

`bluewater check --scope all` evaluates the complete repository and is the contract used by pre-push and CI.

Both scopes support `--format json` without changing validation behavior or exit codes.

Unknown scopes fail closed rather than falling back to a broader or narrower interpretation. A completed check set with one or more failed checks returns `1`; configuration or prerequisite failures return `2`.

## ci validate

`bluewater ci validate` runs the full repository governance contract using `all` scope. It follows the same exit-code contract as `bluewater check --scope all` and supports `--format json` for CI integrations that consume structured results.

## hooks install

`bluewater hooks install` installs packaged thin launchers into `.git/hooks`. The launchers invoke Bluewater rather than embedding governance policy in each consumer repository. Running the command outside a Git worktree, or when `.git/hooks` is unavailable, returns `2`.

## docs

`bluewater docs scan`, `bluewater docs update`, `bluewater docs check`, and `bluewater docs validate` delegate to the pinned LocaleGuard dependency. `validate` maps to LocaleGuard's deterministic `check` operation. Bluewater Scripts does not reproduce localization algorithms.

If LocaleGuard integration is explicitly disabled, documentation commands return success without delegation. If LocaleGuard is enabled but the pinned checkout or required script is missing, Bluewater returns `2` rather than silently skipping documentation governance.
