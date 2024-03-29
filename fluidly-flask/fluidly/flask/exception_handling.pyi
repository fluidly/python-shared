from typing import Any, TypeVar

from fluidly.flask.api_exception import APIException as APIException
from fluidly.flask.rest_logger import rest_log_entrypoint as rest_log_entrypoint

T = TypeVar("T")

def handle_exceptions(func: T) -> T: ...
def log_safely(func: T) -> T: ...
