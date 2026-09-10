# Installation

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

## Development checkout

Bluewater Scripts requires Python 3.12 or later.

```bash
git clone --branch foundation --recurse-submodules https://github.com/phpwalter/bluewater-scripts.git
cd bluewater-scripts
python -m venv .venv
python -m pip install -e ".[dev]"
bluewater doctor
```

## Consumer repository

Pin Bluewater Scripts rather than copying its source:

```bash
git submodule add https://github.com/phpwalter/bluewater-scripts.git tools/bluewater-scripts
git -C tools/bluewater-scripts checkout foundation
git submodule update --init --recursive
python -m pip install -e tools/bluewater-scripts
```

The consumer owns `bluewater.yml`. Shared policy remains immutable inside the submodule. A later stable release should pin a release tag or exact commit rather than the moving `foundation` branch.
