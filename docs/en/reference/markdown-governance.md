# Markdown Governance

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Bluewater Scripts 1.0 deliberately applies a small deterministic Markdown baseline rather than attempting to become a general Markdown linter.

## Enforced rules

For Markdown files in scope, Bluewater requires:

- non-empty files to begin with a Markdown heading marker (`#`), and
- tab characters to be absent.

Files under a repository-relative `tools/` path are excluded because tool checkouts and vendored integrations are governed by their owning projects.

## Deferred rules

Bluewater Scripts 1.0 does not enforce relative-link validity, duplicate anchors, prose style, trailing whitespace, heading-depth progression, or final-newline policy. Those rules can be introduced later only if they can be made deterministic across supported Markdown renderers and repositories.

Documentation localization remains the responsibility of LocaleGuard. Markdown validation must not duplicate LocaleGuard language, translation, or generated-language-bar policy.
