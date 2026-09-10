# Contributing

Development targets the `foundation` branch until the 1.0 foundation is accepted.

## Setup

```bash
git clone --branch foundation --recurse-submodules https://github.com/phpwalter/bluewater-scripts.git
cd bluewater-scripts
python -m venv .venv
python -m pip install -e ".[dev]"
bluewater hooks install
```

Before opening a pull request run:

```bash
python -m ruff check src tests
python -m mypy src/bluewater
python -m pytest
python -m bluewater check --scope all
```

Do not modify `tools/locale-guard` in this repository. It is an immutable dependency pinned by Git submodule commit.
