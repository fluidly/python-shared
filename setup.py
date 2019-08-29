from setuptools import setup

# Package meta-data.
NAME = "python-shared"
DESCRIPTION = "Shared and reusable python modules."
URL = "https://github.com/fluidly/python-shared"
EMAIL = "tech@fluidly.com"
AUTHOR = "Fluidly"
REQUIRES_PYTHON = ">=3.7.0"
VERSION = "0.1.0"

about = {"__version__": VERSION}

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    # packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    py_modules=["fluidly"],
)
