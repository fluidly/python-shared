# python-shared

One repo to share them all

This repository is slightly different to our other python repositories, in that it uses [Nox](https://nox.thea.codes/en/stable/index.html) rather than Pipenv.
Due to the special configuration of sub-packages and how some depend on each other, Pipenv (and Pip) resolve any `fluidly-*` packages to that hosted on Github instead of local directories.

Luckily, dependencies for python-shared are simple so we manage this ourselves with Nox.

## Prerequisites
You will need to have `pyenv` and `pyenv-virtualenv` installed.

## Setup

```
pip install --user --upgrade nox
nox -s setup
```

**Note:** If you get a `command not found: nox` error, it's likely that you're installing packages into your system version of python, which you shouldn't do (you can confirm this by running `which python`). See [configuring pyenv](#set-up-pyenv) below if you wish to use pyenv.

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

### Set up pyenv

```bash
curl https://pyenv.run | bash

pyenv install -v 3.7.4 # or whatever version you'd like to use by default
pyenv global 3.7.4
pyenv which python
```

You should now see `/home/.pyenv/versions/3.7.4/bin/python`. Add the following to your `~/.bashrc` or equivalent:

```bash
export PATH="$HOME/.pyenv/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Open a new terminal, you should now be able to run `nox -s setup`.
