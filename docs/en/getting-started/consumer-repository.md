# Consumer Repository Guide

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

A consumer repository owns its Bluewater configuration and consumes Bluewater Scripts as tooling rather than copying policy code.

## Bootstrap

1. Install the supported Bluewater Scripts version.
2. Run `bluewater init` from the repository root.
3. Review `bluewater.yml`, especially the resolved repository profile and required Bluewater version constraint.
4. Initialize/pin LocaleGuard when documentation localization governance is enabled.
5. Create/review `.locale-guard.yml`.
6. Run `bluewater hooks install` if local Git-hook enforcement is desired.
7. Run `bluewater doctor` and `bluewater repo validate`.
8. Add `bluewater ci validate` to CI.

## Ownership model

The consumer owns `bluewater.yml`, `.locale-guard.yml`, generated documentation output, and the exact dependency revisions it adopts. Bluewater Scripts owns validator implementation and deterministic CLI behavior. LocaleGuard owns localization analysis and generated localization content.

## Recommended CI command

Use `bluewater ci validate` for the complete repository contract. Automation that needs structured results can use `bluewater ci validate --format json`.
