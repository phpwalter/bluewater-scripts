# Bluewater Scripts

Deterministic repository automation and governance for the Bluewater ecosystem.

<!-- locale-guard:summary:start -->
<!-- locale-guard:summary:end -->

Bluewater Scripts centralizes repository policy behind one Python command surface. Git hooks and CI call the same engine, consumer repositories configure behavior through `bluewater.yml`, and documentation localization governance is delegated to LocaleGuard.

## Responsibilities

Bluewater Scripts owns repository automation, configuration validation, repository profile detection, Git hook orchestration, CI parity, and integration with specialist governance tools. It deliberately does not contain application business logic or duplicate LocaleGuard localization logic.

## Foundation status

The active implementation branch is `foundation`. The current package version is `1.0.0.dev0` and the first milestone is the Bluewater Scripts 1.0 foundation.

## Install for development

```bash
git clone --recurse-submodules https://github.com/phpwalter/bluewater-scripts.git
cd bluewater-scripts
git checkout foundation
python -m venv .venv
python -m pip install -e ".[dev]"
bluewater doctor
bluewater hooks install
```

## Core commands

```bash
bluewater --version
bluewater doctor
bluewater repo
bluewater check --scope changed
bluewater check --scope all
bluewater hooks install
bluewater docs scan
bluewater docs update
bluewater docs check
```

## Consumer model

A consuming repository pins Bluewater Scripts as a submodule and owns its configuration. Bluewater Scripts in turn delegates localization governance to LocaleGuard. Policy code is never copied into consumer repositories.

See [`docs/en/getting-started/installation.md`](docs/en/getting-started/installation.md) and [`docs/en/concepts/architecture.md`](docs/en/concepts/architecture.md).

## License

MIT. See [LICENSE](LICENSE).
