# python-shared

One repo to share them all

This repository is slightly different to our other python repositories, in that it uses [Nox](https://nox.thea.codes/en/stable/index.html) rather than Pipenv.
Due to the special configuration of sub-packages and how some depend on each other, Pipenv (and Pip) resolve any `fluidly-*` packages to that hosted on Github instead of local directories.

Luckily, dependencies for python-shared are simple so we manage this ourselves with Nox.

## Setup

```
pip install --user --upgrade nox
nox -s setup
```

The usual commands for linting and testing are provided (see `noxfile.py` or run `nox -l`).

## Local workflow

Nox recreates the virtual environment every time. You can use `nox -r` to reuse a previous virtual environment,
but any packages installed in editable mode will always be reinstalled. This takes quite a long time.

Instead, activate the test virtual environment and execute commands within there e.g.

```
# On first run...
nox -s test

# On subsequent runs...
source .nox/test/bin/activate
pytest
```
