# Governance Boundaries

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Bluewater Scripts is intentionally narrow.

**Bluewater Scripts** governs repository automation, developer workflow, configuration, checks, hooks, and CI orchestration.

**LocaleGuard** governs documentation localization state and generated localization presentation artifacts.

**Polaris-AGOS** may govern broader architectural invariants and cross-repository policy. Bluewater Scripts may invoke such a system in the future, but it should not absorb its policy language or architecture kernel.

Consumer repositories own application logic and project-specific policy. Shared Bluewater tooling must remain reusable and must not encode assumptions about a particular application.
