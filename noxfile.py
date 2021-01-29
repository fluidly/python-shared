import nox

DEFAULT_PYTHON_VERSION = "3.7"

PACKAGES = [
    "fluidly-generic-delete",
    "fluidly-generic-query",
    "fluidly-structlog",
    "fluidly-pubsub",
    "fluidly-sqlalchemy",
    "fluidly-flask",
    "fluidly-auth",
    "fluidly-fastapi",
]


@nox.session(python=DEFAULT_PYTHON_VERSION)
def setup(session):
    session.install("pre-commit")

    session.run("cp", ".env.template", ".env", external=True)
    session.run("pre-commit", "install")


@nox.session(python=DEFAULT_PYTHON_VERSION)
def test(session):
    session.install("pytest", "responses", "freezegun")

    for package in PACKAGES:
        session.install("-e", package)

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
    session.install("autoflake", "black", "isort")

    session.run("autoflake", "--remove-all-unused-imports", "-i", "-r", ".")
    session.run("isort", ".")
    session.run("black", ".")


@nox.session(python=DEFAULT_PYTHON_VERSION)
def format_check(session):
    session.install("autoflake", "black", "isort")

    session.run("autoflake", "--remove-all-unused-imports", "-c", "-r", ".")
    session.run("isort", "-c", ".")
    session.run("black", "--check", "--diff", ".")


@nox.session(python=DEFAULT_PYTHON_VERSION)
def type_check(session):
    session.install("mypy")

    for package in PACKAGES:
        session.install("-e", package)

    for package in PACKAGES:
        if "-generic-" in package:
            continue

        session.run("mypy", f"{package}/fluidly/", "--strict")
