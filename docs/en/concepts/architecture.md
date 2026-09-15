# Architecture

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

Bluewater Scripts follows a kernel-and-adapter model. Python modules own policy and orchestration. Git hooks and CI workflows are thin adapters over the same command surface.

```text
consumer repository
       |
       +-- bluewater.yml
       |
       +-- Bluewater Scripts
               |
               +-- configuration/schema validation
               +-- repository profile detection
               +-- governance checks
               +-- Git hook orchestration
               +-- integration adapters
                         |
                         +-- LocaleGuard
```

The governing invariant is that the same repository state and configuration produce the same validation outcome. CI must not contain hidden policy that local validation cannot execute.

Bluewater Scripts does not implement application-specific checks. Specialized systems such as LocaleGuard or Polaris-AGOS remain separate components and are invoked through explicit integration boundaries.
