import os

import nox

DEFAULT_PYTHON_VERSION = "3.7"
FORMAT_DEPENDENCIES = ["autoflake", "black", "isort"]

PACKAGES = [f for f in os.listdir(".") if os.path.isdir(f) and f.startswith("fluidly-")]

nox.options.sessions = ["format", "lint", "type_check", "test"]


def install_local_packages_as_editable(session, packages):
    for package in packages:
        session.install("-e", package, env={"INSTALL_EDITABLE": "1"})


@nox.session(python=DEFAULT_PYTHON_VERSION)
def setup(session):
    session.install("pre-commit")

    session.run("cp", ".env.template", ".env", external=True)
    session.run("pre-commit", "install")


@nox.session(python=DEFAULT_PYTHON_VERSION)
def test(session):
    session.install("pytest", "responses", "freezegun")

    install_local_packages_as_editable(session, PACKAGES)

    session.run(
        "pytest",
        *session.posargs,
    )


@nox.session(python=DEFAULT_PYTHON_VERSION)
def lint(session):
    session.install("flake8", "yamllint")

    session.run("flake8", *PACKAGES)
    session.run("yamllint", ".")


@nox.session(python=DEFAULT_PYTHON_VERSION)
def format(session):
    session.install(*FORMAT_DEPENDENCIES)

    session.run("autoflake", "--remove-all-unused-imports", "-i", "-r", ".")
    session.run("isort", ".")
    session.run("black", ".")


@nox.session(python=DEFAULT_PYTHON_VERSION)
def format_check(session):
    session.install(*FORMAT_DEPENDENCIES)

    session.run("autoflake", "--remove-all-unused-imports", "-c", "-r", ".")
    session.run("isort", "-c", ".")
    session.run("black", "--check", "--diff", ".")


@nox.session(python=DEFAULT_PYTHON_VERSION)
def type_check(session):
    session.install("mypy", "types-requests", "types-setuptools")

    install_local_packages_as_editable(session, PACKAGES)

    for package in PACKAGES:
        if "-generic-" in package:
            continue

        session.run("mypy", f"{package}/fluidly/", "--strict")
