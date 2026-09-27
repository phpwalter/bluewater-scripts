# Generated Artifact Governance

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Bluewater Scripts treats two repository surfaces as generated-governance outputs in 1.0:

- `docs/_generated/`
- `README.md`

The README is included because LocaleGuard owns generated localization summary regions within it. Bluewater does not attempt to parse or regenerate those regions itself; it verifies that the repository is clean after the owning generator has run.

Unrelated modified files do not fail the generated-artifact check.

## Remediation

When this check fails, run the owning documentation generator (`bluewater docs update` for LocaleGuard-managed documentation), review the resulting changes, and commit the generated output. The governance check is intentionally read-only and never repairs generated files during validation.
