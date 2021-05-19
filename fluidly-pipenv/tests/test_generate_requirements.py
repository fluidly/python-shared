import io
import json

import pytest

from fluidly.pipenv.generate_requirements import generate_requirements


@pytest.fixture
def mock_pipfile_lock():
    def _wrapper(_meta=None, default=None, develop=None):
        pipfile_lock = {
            "_meta": _meta or {},
            "default": default or {},
            "develop": develop or {},
        }

        return io.StringIO(json.dumps(pipfile_lock))

    return _wrapper


def test_generates_pypi_dependency(mock_pipfile_lock):
    pipfile_lock_file = mock_pipfile_lock(
        default={
            "flask": {"version": "==2.0.0"},
        }
    )

    requirements_file = io.StringIO()
    generate_requirements(pipfile_lock_file, requirements_file)

    requirements_file.seek(0)
    assert requirements_file.read() == "flask==2.0.0\n"


def test_generates_git_dependency(mock_pipfile_lock):
    pipfile_lock_file = mock_pipfile_lock(
        default={
            "fluidly-auth": {
                "git": "git@github.com/fluidly/python-shared.git",
                "ref": "d1bfd94894fff06f0580d9c780c99d0d6eb32a46",
                "subdirectory": "fluidly-auth",
            },
        }
    )

    requirements_file = io.StringIO()
    generate_requirements(pipfile_lock_file, requirements_file)

    requirements_file.seek(0)
    assert (
        requirements_file.read()
        == "git+git@github.com/fluidly/python-shared.git@d1bfd94894fff06f0580d9c780c99d0d6eb32a46#subdirectory=fluidly-auth\n"
    )


def test_generates_editable_dependency(mock_pipfile_lock):
    pipfile_lock_file = mock_pipfile_lock(
        default={
            "marshmallow": {
                "editable": True,
                "git": "https://github.com/marshmallow-code/marshmallow.git",
                "ref": "01837167ef1758df1f2decb819e7294200ec9f67",
            },
        }
    )

    requirements_file = io.StringIO()
    generate_requirements(pipfile_lock_file, requirements_file)

    requirements_file.seek(0)
    assert (
        requirements_file.read()
        == "-e git+https://github.com/marshmallow-code/marshmallow.git@01837167ef1758df1f2decb819e7294200ec9f67#egg=marshmallow\n"
    )
