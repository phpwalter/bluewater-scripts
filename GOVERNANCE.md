# Governance

Bluewater Scripts owns repository automation policy for the Bluewater ecosystem. Application behavior, product policy, localization implementation, and enterprise architecture governance remain outside this repository.

## Boundaries

- Bluewater Scripts: repository automation, validation, developer workflow, hook and CI orchestration.
- LocaleGuard: documentation localization structure, coverage, navigation, and generated localization artifacts.
- Polaris-AGOS: higher-order architecture policy and cross-repository architectural invariants.

Policy logic should live in Python modules, not shell hooks or CI YAML. Hooks and CI are adapters over the same command surface.
