# bluewater.yml

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

`bluewater.yml` is the authoritative project configuration. Invalid required configuration fails closed.

```yaml
version: 1
repository:
  type: auto
  required_bluewater_version: ">=1.0,<2.0"
checks:
  structured_files: true
  locale_guard: true
  generated_files: true
integrations:
  locale_guard:
    enabled: true
    path: tools/locale-guard
    config: .locale-guard.yml
```

Repository type may be `auto`, `python`, `php`, `javascript`, `documentation`, or `mixed`. `auto` derives a profile from well-known project markers.

The JSON Schema at `schemas/bluewater.schema.json` is normative for configuration structure.
