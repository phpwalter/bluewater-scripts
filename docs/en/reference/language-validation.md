# Language Validation

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Bluewater Scripts 1.0 provides syntax validation for Python, PHP, and JavaScript repositories.

## Python

Python validation applies to `python` and `mixed` repository profiles. Full-scope validation compiles `src` and `tests`; changed-scope validation compiles changed `.py` files with the running Python interpreter.

## PHP

PHP validation applies to `php` and `mixed` profiles and requires a `php` executable on `PATH` when the check is enabled and applicable. Files are validated with `php -l`.

## JavaScript

JavaScript validation applies to `javascript` and `mixed` profiles and requires a `node` executable on `PATH` when the check is enabled and applicable. Files with `.js`, `.mjs`, and `.cjs` extensions are validated with `node --check`.

## Runtime probing

Disabled language checks do not probe for their corresponding runtimes. A missing runtime fails only when that validator is both enabled and applicable to the resolved repository profile.

## TypeScript and JSX

TypeScript, TSX, and JSX validation are explicitly outside the Bluewater Scripts 1.0 syntax-validation contract. They require compiler/transpiler-specific project semantics that cannot be represented safely by `node --check`. Support may be introduced in a later configuration-schema version with an explicit toolchain contract.
