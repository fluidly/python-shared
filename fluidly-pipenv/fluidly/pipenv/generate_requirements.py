import json
from contextlib import nullcontext
from typing import Any, ContextManager, Dict, Iterator, TextIO, Union


def get_pypi_dependency(dependency: str, settings: Dict[str, Any]) -> str:
    return f"{dependency}{settings['version']}"


def get_git_dependency(dependency: str, settings: Dict[str, Any]) -> str:
    repository = f"git+{settings['git']}"

    if "ref" in settings:
        repository = f"{repository}@{settings['ref']}"

    if "subdirectory" in settings:
        repository = f"{repository}#subdirectory={settings['subdirectory']}"

    if settings.get("editable") == True:
        repository = f"-e {repository}#egg={dependency}"

    return repository


def get_dependencies(pipfile_lock_file: Union[str, TextIO]) -> Iterator[str]:
    pipfile_lock_context_manager: Union[None, ContextManager[TextIO]] = None
    if isinstance(pipfile_lock_file, str):
        pipfile_lock_context_manager = open(pipfile_lock_file, "r")
    else:
        pipfile_lock_context_manager = nullcontext(pipfile_lock_file)

    with pipfile_lock_context_manager as pipfile_lock:
        lock = json.loads(pipfile_lock.read())

        for dep, settings in lock["default"].items():
            if "version" in settings:
                yield get_pypi_dependency(dep, settings)

            if "git" in settings:
                yield get_git_dependency(dep, settings)


def generate_requirements(
    pipfile_lock_file: Union[str, TextIO] = "Pipfile.lock",
    requirements_file: Union[str, TextIO] = "requirements.txt",
) -> None:
    requirements_context_manager: Union[None, ContextManager[TextIO]] = None
    if isinstance(requirements_file, str):
        requirements_context_manager = open(requirements_file, "w+")
    else:
        requirements_context_manager = nullcontext(requirements_file)

    with requirements_context_manager as requirements:
        for dependency in get_dependencies(pipfile_lock_file):
            requirements.write(f"{dependency}\n")


if __name__ == "__main__":
    generate_requirements()
