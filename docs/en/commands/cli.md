# CLI Commands

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

## init

`bluewater init` creates a repository-owned `bluewater.yml` using the detected repository profile. It fails if configuration already exists unless `--force` is supplied.

## doctor

`bluewater doctor` reports the repository root, resolved profile, and integration state.

## repo validate

`bluewater repo validate` validates configuration and resolves the repository profile.

## check

`bluewater check --scope changed` is the lightweight developer path used by pre-commit. It discovers staged, unstaged, and untracked files and limits structured-file, Markdown, and Python syntax validation to those files. Repository-wide invariants, including version compatibility, LocaleGuard state, and generated-artifact cleanliness, remain enforced because they can be invalidated indirectly by a local change.

`bluewater check --scope all` evaluates the complete repository and is the contract used by pre-push and CI.

Unknown scopes fail closed rather than falling back to a broader or narrower interpretation.

## ci validate

`bluewater ci validate` runs the full repository governance contract used in CI.

## hooks install

`bluewater hooks install` installs packaged thin launchers into `.git/hooks`. The launchers invoke Bluewater rather than embedding governance policy in each consumer repository.

## docs

`bluewater docs scan`, `bluewater docs update`, `bluewater docs check`, and `bluewater docs validate` delegate to the pinned LocaleGuard dependency. `validate` maps to LocaleGuard's deterministic `check` operation. Bluewater Scripts does not reproduce localization algorithms.
