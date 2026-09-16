# Diagnostic Output Contract

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Bluewater exposes machine-readable diagnostics through `--format json` on `doctor`, `repo validate`, `check`, and `ci validate`.

## Format version

Every JSON document includes `"format_version": 1`. Consumers must inspect this field before interpreting the payload. A future incompatible representation requires a new format version rather than silently changing version 1.

## Result envelope

Successful execution returns a `checks` array and an aggregate `ok` value. Each check has three stable fields: `name`, `ok`, and `detail`.

Check names are protocol identifiers. Within format version 1, an existing check name must not be repurposed to mean a different invariant. New checks may be added only when their ordering and compatibility implications are documented.

## Execution-error envelope

When Bluewater cannot execute a requested validation because repository context, configuration, or a required prerequisite is invalid, JSON mode emits an `error` object and returns exit code `2`. Version 1 defines `error.kind` as `execution` and includes a human-readable `detail` string.

## Exit codes

- `0`: execution succeeded and all requested checks passed.
- `1`: execution succeeded and at least one governance check failed.
- `2`: Bluewater could not execute the requested operation.

## Determinism

For identical inputs and check results, Bluewater emits identical compact JSON bytes. Object keys are sorted and check ordering is fixed by the command contract.

## Schema

The normative schema is `schemas/diagnostics.schema.json`. Tests validate both result and execution-error envelopes against this schema.
