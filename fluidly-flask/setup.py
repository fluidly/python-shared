#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = "fluidly-flask"
DESCRIPTION = "Flask helpers."
URL = "https://github.com/fluidly/python-shared"
EMAIL = "tech@fluidly.com"
AUTHOR = "Fluidly"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "0.1.0"

# What packages are required for this module to be executed?
REQUIRED = [
    "flask",
    "marshmallow",
    "uwsgi",
    "fluidly-structlog @ git+ssh://git@github.com/fluidly/python-shared.git#subdirectory=fluidly-structlog",
    "fluidly-auth @ git+ssh://git@github.com/fluidly/python-shared.git#subdirectory=fluidly-auth",
]


# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# Setup boilerplate below this line.

try:
    package_root = os.path.abspath(os.path.dirname(__file__))

    readme_filename = os.path.join(package_root, "README.md")
    with io.open(readme_filename, encoding="utf-8") as readme_file:
        readme = readme_file.read()
except FileNotFoundError:
    readme = DESCRIPTION

packages = [
    package
    for package in find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"])
    if package.startswith("fluidly")
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=packages,
    package_data={"fluidly.flask": ["py.typed"]},
    namespace_packages=["fluidly"],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
)
