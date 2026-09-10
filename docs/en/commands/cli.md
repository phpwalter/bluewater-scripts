# CLI Commands

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

## doctor

`bluewater doctor` reports the repository root, resolved profile, and integration state.

## repo

`bluewater repo` validates configuration and resolves the repository profile.

## check

`bluewater check --scope changed` is intended for pre-commit use. `bluewater check --scope all` is the full governance contract used by pre-push and CI. The foundation preserves both scopes even where a check still evaluates the complete repository so later optimization does not change the public command contract.

## hooks install

`bluewater hooks install` installs thin launchers into `.git/hooks`.

## docs

`bluewater docs scan`, `bluewater docs update`, and `bluewater docs check` delegate directly to the pinned LocaleGuard dependency. Bluewater Scripts does not reproduce localization algorithms.
