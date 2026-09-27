# Configuration Evolution

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Bluewater configuration is intentionally strict. Version 1 rejects unknown top-level keys, repository keys, integration keys, and check names. This prevents typographical errors from silently disabling or inventing governance behavior.

## Adding a check

A new check added within configuration version 1 must be introduced as a known optional boolean with a deterministic default that does not reinterpret existing keys. If adding the check would change the meaning of an existing configuration, a new configuration version is required instead.

## Breaking changes

A new configuration version is required when Bluewater needs to rename/remove a key, change the meaning of an existing value, or require new information that older configuration cannot represent safely.

## Migration

Configuration-version changes must ship with an explicit migration guide and fail with an actionable error when an unsupported version is encountered. Bluewater must not guess how to migrate policy.

## Paths and validator-specific options

Version 1 keeps validator configuration deliberately small. Include/exclude lists and tool-specific arguments are deferred until they can be represented consistently across repository profiles without weakening deterministic defaults.
